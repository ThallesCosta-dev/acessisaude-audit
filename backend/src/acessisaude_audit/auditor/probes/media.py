"""Sondas de mídia temporal e de conteúdo em movimento.

Cobrem barreiras que o axe-core não avalia porque dependem de inspecionar o
conteúdo embarcado e o comportamento temporal da página:

- **1.2.2 / 1.2.3** — vídeo sem legenda ou alternativa acessível.
- **1.4.2 / 2.2.2** — mídia que inicia sozinha e não pode ser interrompida.
- **2.2.1** — atualização automática de página por ``meta refresh``.

Peso jurídico específico: conteúdo audiovisual em portal de saúde costuma
veicular orientação clínica e campanha sanitária. Sua inacessibilidade aciona,
além do art. 63 da LBI, o art. 26 do Decreto 5.626/2005, que impõe ao poder
público garantir acesso à informação às pessoas surdas.
"""

from __future__ import annotations

from typing import Any

from acessisaude_audit.auditor.probes._js import CSS_PATH_FN, wrap
from acessisaude_audit.auditor.probes.base import (
    Confidence,
    Probe,
    ProbeContext,
    affected_groups,
    help_url_for,
    remediation_for,
)
from acessisaude_audit.domain.models import (
    EvidenceNode,
    Finding,
    FindingSource,
    Impact,
    Outcome,
)

__all__ = ["AutoplayProbe", "CaptionsProbe", "MetaRefreshProbe"]


_MEDIA_SCRIPT = wrap(
    """
    const describe = (el) => ({
      selector: cssPath(el),
      html: el.outerHTML.slice(0, 300),
      tag: el.tagName.toLowerCase(),
      autoplay: el.hasAttribute('autoplay'),
      muted: el.muted === true || el.hasAttribute('muted'),
      controls: el.hasAttribute('controls'),
      loop: el.hasAttribute('loop'),
      ariaLabel: el.getAttribute('aria-label'),
      tracks: Array.from(el.querySelectorAll('track')).map(t => ({
        kind: (t.getAttribute('kind') || '').toLowerCase(),
        srclang: t.getAttribute('srclang'),
        label: t.getAttribute('label'),
      })),
    });

    const videos = Array.from(document.querySelectorAll('video')).map(describe);
    const audios = Array.from(document.querySelectorAll('audio')).map(describe);

    // Players de terceiros embutidos: não é possível inspecionar suas legendas
    // a partir do documento hospedeiro (política de mesma origem).
    const embedded = Array.from(document.querySelectorAll('iframe'))
      .filter(f => /youtube|vimeo|dailymotion|player|video/i.test(f.src || ''))
      .slice(0, 10)
      .map(f => ({
        selector: cssPath(f),
        html: f.outerHTML.slice(0, 300),
        src: f.src,
        title: f.getAttribute('title'),
      }));

    return { videos, audios, embedded };
    """,
    CSS_PATH_FN,
)


def _has_captions(item: dict[str, Any]) -> bool:
    """Se o elemento declara faixa de legenda ou de legenda oculta."""
    return any((t.get("kind") or "") in {"captions", "subtitles"} for t in item.get("tracks") or [])


class CaptionsProbe(Probe):
    """Detecta mídia temporal sem alternativa acessível (WCAG 1.2.2, 1.2.3).

    Vereditos:

    - ``<video>`` **sem** nenhuma faixa ``track kind="captions"`` ou
      ``"subtitles"`` → ``FAIL``. A ausência é objetiva e verificável no DOM.
    - ``<video>`` **com** faixa declarada → nenhum achado. A ferramenta não
      julga a qualidade da legenda: legendas automáticas incorretas são um
      problema real, mas sua avaliação exige revisão humana e está fora do que
      um método automático pode afirmar.
    - ``<audio>`` sem transcrição identificável → ``INCOMPLETE``. A transcrição
      pode existir como texto adjacente na página, o que a máquina não sabe
      associar com segurança.
    - Player de terceiro em ``iframe`` → ``INCOMPLETE``, com registro explícito
      de que a região é opaca à auditoria. Declarar o ponto cego é parte do
      método.
    """

    id = "probe.captions"
    criteria = ("1.2.2", "1.2.3")
    confidence = Confidence.DETERMINISTIC
    description = "Verifica faixas de legenda em vídeo e alternativas em áudio."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_MEDIA_SCRIPT)
        if not data:
            return []

        findings: list[Finding] = []

        uncaptioned = [v for v in data.get("videos", []) if not _has_captions(v)]
        if uncaptioned:
            findings.append(
                Finding(
                    rule_id="probe.captions.video-without-track",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=["1.2.2"],
                    summary=f"{len(uncaptioned)} vídeo(s) sem faixa de legenda declarada.",
                    description=(
                        "Elementos <video> não declaram nenhuma faixa <track> de legenda "
                        "ou legenda oculta. Em portal de saúde, o conteúdo audiovisual "
                        "costuma veicular orientação clínica e campanha sanitária: sua "
                        "inacessibilidade retira da pessoa surda informação diretamente "
                        "ligada ao cuidado da própria saúde."
                    ),
                    remediation=remediation_for("1.2.2"),
                    help_url=help_url_for("1.2.2"),
                    affects=affected_groups("1.2.2"),
                    extra_provisions=["dec5626.art26"],
                    nodes=[
                        EvidenceNode(
                            selector=str(v.get("selector", "")),
                            html=str(v.get("html", "")),
                            failure_summary=(
                                'Elemento <video> sem <track kind="captions"> nem '
                                '<track kind="subtitles">.'
                            ),
                            measured={"tracks": v.get("tracks"), "controls": v.get("controls")},
                        )
                        for v in uncaptioned[:10]
                    ],
                )
            )

        audios = data.get("audios", [])
        if audios:
            findings.append(
                Finding(
                    rule_id="probe.captions.audio-transcript",
                    source=FindingSource.PROBE,
                    outcome=Outcome.INCOMPLETE,
                    criteria=["1.2.1"],
                    summary=(
                        f"{len(audios)} elemento(s) de áudio requerem verificação de transcrição."
                    ),
                    description=(
                        "Foram encontrados elementos <audio>. O critério exige alternativa "
                        "textual equivalente, que pode estar publicada como texto adjacente "
                        "— associação que a verificação automática não consegue confirmar. "
                        "Requer conferência humana."
                    ),
                    remediation=remediation_for("1.2.1"),
                    help_url=help_url_for("1.2.1"),
                    affects=affected_groups("1.2.1"),
                    nodes=[
                        EvidenceNode(
                            selector=str(a.get("selector", "")),
                            html=str(a.get("html", "")),
                            failure_summary="Verificar existência de transcrição textual.",
                        )
                        for a in audios[:10]
                    ],
                )
            )

        embedded = data.get("embedded", [])
        if embedded:
            findings.append(
                Finding(
                    rule_id="probe.captions.embedded-player",
                    source=FindingSource.PROBE,
                    outcome=Outcome.INCOMPLETE,
                    criteria=["1.2.2"],
                    summary=(
                        f"{len(embedded)} player(s) de terceiros embutidos — região opaca "
                        "à auditoria automática."
                    ),
                    description=(
                        "Players hospedados em outro domínio não podem ser inspecionados "
                        "a partir da página, por restrição de mesma origem do navegador. "
                        "A existência de legendas precisa ser verificada manualmente. "
                        "Este achado é registrado para que a lacuna conste do relatório: "
                        "ausência de detecção não é evidência de conformidade."
                    ),
                    remediation=(
                        "Verificar manualmente as legendas no player e garantir que o "
                        "iframe tenha atributo title descritivo."
                    ),
                    help_url=help_url_for("1.2.2"),
                    affects=affected_groups("1.2.2"),
                    nodes=[
                        EvidenceNode(
                            selector=str(e.get("selector", "")),
                            html=str(e.get("html", "")),
                            failure_summary=f"Player embutido de {e.get('src', '')[:120]}",
                            measured={"title": e.get("title")},
                        )
                        for e in embedded
                    ],
                )
            )

        return findings


class AutoplayProbe(Probe):
    """Detecta mídia com reprodução automática e sem controles (WCAG 1.4.2, 2.2.2).

    Áudio que inicia sozinho compete com a voz sintetizada do leitor de tela e
    torna a página inutilizável para quem depende dele. A verificação exclui
    mídia silenciada (``muted``), que não produz esse conflito.
    """

    id = "probe.autoplay"
    criteria = ("1.4.2", "2.2.2")
    confidence = Confidence.DETERMINISTIC
    description = "Detecta áudio/vídeo com autoplay audível ou sem controles."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_MEDIA_SCRIPT)
        if not data:
            return []

        offenders = [
            m
            for m in [*data.get("videos", []), *data.get("audios", [])]
            if m.get("autoplay") and not m.get("muted")
        ]
        if not offenders:
            return []

        no_controls = [m for m in offenders if not m.get("controls")]
        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.SERIOUS if no_controls else Impact.MODERATE,
                criteria=list(self.criteria),
                summary=(
                    f"{len(offenders)} mídia(s) com reprodução automática audível"
                    + (f", das quais {len(no_controls)} sem controles." if no_controls else ".")
                ),
                description=(
                    "Mídia que inicia sozinha com som sobrepõe-se à voz do leitor de tela "
                    "e impede a leitura da página. Quando não há controle de pausa "
                    "acessível, o usuário não tem como interromper — a única saída é "
                    "abandonar o serviço."
                ),
                remediation=remediation_for("1.4.2"),
                help_url=help_url_for("1.4.2"),
                affects=affected_groups("1.4.2"),
                nodes=[
                    EvidenceNode(
                        selector=str(m.get("selector", "")),
                        html=str(m.get("html", "")),
                        failure_summary=(
                            f"<{m.get('tag')}> com autoplay, muted={m.get('muted')}, "
                            f"controls={m.get('controls')}."
                        ),
                        measured={
                            "autoplay": m.get("autoplay"),
                            "muted": m.get("muted"),
                            "controls": m.get("controls"),
                            "loop": m.get("loop"),
                        },
                    )
                    for m in offenders[:10]
                ],
            )
        ]


_REFRESH_SCRIPT = wrap(
    """
    const metas = Array.from(document.querySelectorAll('meta[http-equiv="refresh" i]'));
    return metas.map(m => {
      const content = m.getAttribute('content') || '';
      const seconds = parseFloat(content.split(';')[0]);
      return {
        selector: cssPath(m),
        html: m.outerHTML.slice(0, 200),
        content,
        seconds: Number.isFinite(seconds) ? seconds : null,
        redirects: /url\\s*=/i.test(content),
      };
    });
    """,
    CSS_PATH_FN,
)


class MetaRefreshProbe(Probe):
    """Detecta atualização ou redirecionamento automático por ``meta refresh`` (WCAG 2.2.1).

    O recarregamento automático descarta o que o usuário estava lendo ou
    digitando e devolve o foco ao topo. Para quem preenche um formulário
    lentamente — por deficiência motora, por baixa visão ou por conexão instável
    — o efeito é a perda repetida do trabalho já feito, sem qualquer aviso.

    A norma admite atraso superior a 20 horas (equivalente a não recarregar);
    valores abaixo disso caracterizam violação.
    """

    id = "probe.meta-refresh"
    criteria = ("2.2.1",)
    confidence = Confidence.DETERMINISTIC
    description = "Detecta meta refresh com atraso inferior a 20 horas."

    #: Limiar da norma, em segundos (20 horas).
    _THRESHOLD_SECONDS = 72_000

    async def _run(self, context: ProbeContext) -> list[Finding]:
        metas: list[dict[str, Any]] | None = await context.evaluate(_REFRESH_SCRIPT)
        if not metas:
            return []

        offenders = [
            m
            for m in metas
            if m.get("seconds") is not None and float(m["seconds"]) < self._THRESHOLD_SECONDS
        ]
        if not offenders:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.SERIOUS,
                criteria=list(self.criteria),
                summary="A página se atualiza ou redireciona automaticamente.",
                description=(
                    "Há declaração de meta refresh com atraso curto. O recarregamento "
                    "automático interrompe a leitura, devolve o foco ao início do "
                    "documento e descarta dados já digitados, sem que o usuário possa "
                    "adiar, estender ou desativar o comportamento."
                ),
                remediation=remediation_for("2.2.1"),
                help_url=help_url_for("2.2.1"),
                affects=affected_groups("2.2.1"),
                nodes=[
                    EvidenceNode(
                        selector=str(m.get("selector", "")),
                        html=str(m.get("html", "")),
                        failure_summary=(
                            f"Atualização automática em {m.get('seconds')} s"
                            + (" com redirecionamento." if m.get("redirects") else ".")
                        ),
                        measured={
                            "seconds": m.get("seconds"),
                            "redirects": m.get("redirects"),
                            "content": m.get("content"),
                        },
                    )
                    for m in offenders
                ],
            )
        ]
