"""Repositórios: tradução entre modelos de domínio e linhas do banco.

O domínio nunca sabe que existe banco. Toda conversão acontece aqui, em um só
lugar, o que torna verificável a afirmação de que o índice relacional é
derivável integralmente do documento JSON — propriedade explorada por
:meth:`ScanRepository.reindex`.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from acessisaude_audit.domain.models import Finding, Outcome, ScanResult
from acessisaude_audit.domain.scoring import (
    DEFAULT_PARAMETERS,
    AccessibilityScore,
    ScoringParameters,
    score_scan,
)
from acessisaude_audit.domain.wcag import criterion
from acessisaude_audit.logging_setup import get_logger
from acessisaude_audit.persistence.orm import FindingRow, ScanRow

__all__ = ["JsonScanStore", "ScanRepository"]

logger = get_logger(__name__)


class JsonScanStore:
    """Armazena varreduras como arquivos JSON — o artefato primário de pesquisa.

    Convenção de nome: ``{target_id}__{AAAAMMDD-HHMMSS}__{id-curto}.json``.
    Ordena cronologicamente por padrão no listador do sistema de arquivos e
    torna o alvo legível sem abrir o arquivo.
    """

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, scan: ScanResult) -> Path:
        """Caminho canônico do arquivo desta varredura."""
        stamp = scan.started_at.strftime("%Y%m%d-%H%M%S")
        return self._dir / f"{scan.target_id}__{stamp}__{str(scan.id)[:8]}.json"

    def save(self, scan: ScanResult) -> Path:
        """Grava a varredura em disco e devolve o caminho.

        Serializa com ``by_alias=False`` e indentação de 2 espaços: o arquivo
        precisa ser legível e diffável, porque é ele que acompanha o artigo
        como material suplementar.
        """
        path = self.path_for(scan)
        path.write_text(
            scan.model_dump_json(indent=2, exclude_none=False),
            encoding="utf-8",
        )
        logger.info(
            "varredura gravada em disco",
            extra={"arquivo": str(path), "bytes": path.stat().st_size},
        )
        return path

    def load(self, path: Path) -> ScanResult:
        """Lê uma varredura do disco, validando contra o modelo atual.

        Raises:
            pydantic.ValidationError: Se o arquivo não corresponder ao esquema
                corrente — sinal de que o dataset é de uma versão anterior e
                exige migração explícita, e não leitura tolerante.
        """
        return ScanResult.model_validate_json(path.read_text(encoding="utf-8"))

    def list_files(self) -> list[Path]:
        """Arquivos de varredura disponíveis, do mais recente ao mais antigo."""
        return sorted(self._dir.glob("*.json"), reverse=True)


class ScanRepository:
    """Leitura e escrita de varreduras no banco relacional."""

    def __init__(self, session: Session, *, params: ScoringParameters = DEFAULT_PARAMETERS) -> None:
        self._session = session
        self._params = params

    # ---------------------------------------------------------------- escrita

    def save(
        self, scan: ScanResult, *, json_path: Path | None = None, sphere: str | None = None
    ) -> ScanRow:
        """Persiste a varredura: documento + índice achatado.

        Substitui integralmente qualquer registro anterior de mesmo ``id``
        (varreduras são imutáveis; reescrever significa reprocessar).

        Args:
            scan: Resultado a persistir.
            json_path: Caminho do arquivo JSON correspondente, se houver.
            sphere: Esfera federativa do alvo, copiada do catálogo.
        """
        self._session.execute(delete(ScanRow).where(ScanRow.id == str(scan.id)))

        score = score_scan(scan, self._params)
        row = self._to_row(scan, score, json_path=json_path, sphere=sphere)
        self._session.add(row)

        for finding_row in self._flatten(scan):
            self._session.add(finding_row)

        logger.info(
            "varredura indexada",
            extra={
                "scan": str(scan.id),
                "alvo": scan.target_id,
                "ica": score.conformance_index,
                "ian": score.friction_index,
            },
        )
        return row

    def reindex(self, scan_id: str) -> ScanRow | None:
        """Reconstrói o índice achatado a partir do documento JSON armazenado.

        Existe para tornar operacional a promessa de que o documento é a fonte
        da verdade: se o cálculo de índices mudar, ou se uma coluna nova for
        acrescentada, não é preciso revarrer nenhum portal.
        """
        row = self._session.get(ScanRow, scan_id)
        if row is None:
            return None
        scan = ScanResult.model_validate(row.document)
        return self.save(
            scan,
            json_path=Path(row.json_path) if row.json_path else None,
            sphere=row.sphere,
        )

    # ---------------------------------------------------------------- leitura

    def get(self, scan_id: str) -> ScanResult | None:
        """Recupera a varredura completa pelo identificador."""
        row = self._session.get(ScanRow, scan_id)
        return ScanResult.model_validate(row.document) if row else None

    def get_row(self, scan_id: str) -> ScanRow | None:
        """Recupera apenas a linha de índice (sem materializar o domínio)."""
        return self._session.get(ScanRow, scan_id)

    def list_rows(
        self,
        *,
        target_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[ScanRow]:
        """Lista varreduras, da mais recente à mais antiga."""
        stmt = select(ScanRow).order_by(ScanRow.started_at.desc())
        if target_id:
            stmt = stmt.where(ScanRow.target_id == target_id)
        return self._session.execute(stmt.limit(limit).offset(offset)).scalars().all()

    def latest_for_target(self, target_id: str) -> ScanRow | None:
        """Varredura mais recente de um alvo."""
        stmt = (
            select(ScanRow)
            .where(ScanRow.target_id == target_id)
            .order_by(ScanRow.started_at.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalars().first()

    def count(self, *, target_id: str | None = None) -> int:
        """Total de varreduras registradas."""
        stmt = select(func.count()).select_from(ScanRow)
        if target_id:
            stmt = stmt.where(ScanRow.target_id == target_id)
        return int(self._session.execute(stmt).scalar_one())

    def criterion_frequency(self, *, only_violations: bool = True) -> list[tuple[str, int]]:
        """Frequência de cada critério violado no conjunto de varreduras.

        É a consulta que alimenta a figura principal do artigo — quais barreiras
        são estruturais no ecossistema, e não acidentes de um portal isolado.
        """
        stmt = (
            select(FindingRow.primary_criterion, func.count(FindingRow.id))
            .where(FindingRow.primary_criterion.is_not(None))
            .group_by(FindingRow.primary_criterion)
            .order_by(func.count(FindingRow.id).desc())
        )
        if only_violations:
            stmt = stmt.where(FindingRow.outcome == Outcome.FAIL.value)
        return [(str(c), int(n)) for c, n in self._session.execute(stmt).all()]

    def delete(self, scan_id: str) -> bool:
        """Remove uma varredura e seus achados. Retorna se algo foi removido."""
        result = self._session.execute(delete(ScanRow).where(ScanRow.id == scan_id))
        return bool(result.rowcount)

    # ---------------------------------------------------------------- interno

    def _to_row(
        self,
        scan: ScanResult,
        score: AccessibilityScore,
        *,
        json_path: Path | None,
        sphere: str | None,
    ) -> ScanRow:
        cost = score.data_cost
        return ScanRow(
            id=str(scan.id),
            schema_version=scan.schema_version,
            target_id=scan.target_id,
            target_name=scan.target_name,
            base_url=scan.base_url,
            sphere=sphere,
            status=scan.status.value,
            started_at=scan.started_at,
            finished_at=scan.finished_at,
            engine_version=scan.engine_version,
            axe_version=scan.axe_version,
            browser=scan.browser,
            page_count=scan.page_count,
            violation_count=scan.violation_count,
            occurrence_count=scan.occurrence_count,
            incomplete_count=score.incomplete,
            loss_rate=scan.loss_rate,
            conformance_index=score.conformance_index,
            friction_index=score.friction_index,
            legal_exposure_index=score.legal_exposure_index,
            absolute_barrier=score.absolute_barrier,
            coverage=score.coverage,
            mean_page_mb=cost.total_mb if cost else 0.0,
            mean_cost_brl=cost.cost_brl if cost else 0.0,
            document=scan.model_dump(mode="json"),
            json_path=str(json_path) if json_path else None,
        )

    def _flatten(self, scan: ScanResult) -> list[FindingRow]:
        """Achata todos os achados da varredura em linhas indexáveis."""
        rows: list[FindingRow] = []
        for page in scan.pages:
            for finding in page.findings:
                rows.append(
                    self._finding_row(
                        finding,
                        scan_id=str(scan.id),
                        is_critical_path=page.is_critical_path,
                    )
                )
        return rows

    @staticmethod
    def _finding_row(finding: Finding, *, scan_id: str, is_critical_path: bool) -> FindingRow:
        primary = finding.criteria[0] if finding.criteria else None
        principle: str | None = None
        level: str | None = None
        if primary:
            try:
                sc = criterion(primary)
                principle = sc.principle.value
                level = sc.level.value
            except KeyError:  # pragma: no cover - critério fora do escopo
                pass

        risk = finding.legal_risk
        return FindingRow(
            id=str(finding.id),
            scan_id=scan_id,
            rule_id=finding.rule_id,
            source=finding.source.value,
            outcome=finding.outcome.value,
            impact=finding.impact.value if finding.impact else None,
            legal_risk=risk.value if risk else None,
            criteria=list(finding.criteria),
            primary_criterion=primary,
            principle=principle,
            level=level,
            affects=[g.value for g in finding.affects],
            legal_provisions=list(finding.legal_provisions),
            occurrences=finding.occurrences,
            summary=finding.summary,
            legal_thesis=finding.legal_thesis,
            page_url=finding.page_url,
            viewport=finding.viewport,
            is_critical_path=is_critical_path,
        )
