/**
 * Matriz WCAG ↔ ordenamento jurídico brasileiro, como interface consultável.
 *
 * Esta é a contribuição interdisciplinar do projeto exposta de forma
 * inspecionável: para cada um dos 50 critérios de sucesso A/AA, qual é o risco
 * jurídico, qual a proposição que liga a falha técnica à norma e quais
 * dispositivos são invocáveis.
 *
 * Os dados vêm inteiramente do endpoint `/referencia`. Nenhuma regra é
 * reimplementada em TypeScript — do contrário a matriz existiria em duas
 * versões, e elas divergiriam.
 */

import { useMemo, useState } from 'react';
import { api, useRecurso } from '../lib/api';
import type { Criterio } from '../lib/types';
import { ROTULO_GRUPO, ROTULO_PRINCIPIO } from '../lib/format';
import {
  Carregando,
  Erro,
  Selo,
  SeloDeRisco,
  TituloDePagina,
} from '../components/ui';

type Filtro = 'todos' | 'automatizaveis' | 'manuais';

export function Referencia() {
  const criterios = useRecurso(() => api.criterios(), []);
  const dispositivos = useRecurso(() => api.dispositivos(), []);
  const integridade = useRecurso(() => api.integridadeDaMatriz(), []);
  const [filtro, setFiltro] = useState<Filtro>('todos');

  const visiveis = useMemo(() => {
    const lista = criterios.dados ?? [];
    if (filtro === 'automatizaveis') return lista.filter((c) => c.automatable);
    if (filtro === 'manuais') return lista.filter((c) => !c.automatable);
    return lista;
  }, [criterios.dados, filtro]);

  const porPrincipio = useMemo(() => {
    const grupos = new Map<string, Criterio[]>();
    for (const c of visiveis) {
      const atual = grupos.get(c.principle) ?? [];
      atual.push(c);
      grupos.set(c.principle, atual);
    }
    return grupos;
  }, [visiveis]);

  if (criterios.carregando) return <Carregando>Carregando a matriz…</Carregando>;
  if (criterios.erro) {
    return <Erro erro={criterios.erro} aoTentarNovamente={criterios.recarregar} />;
  }

  const total = criterios.dados?.length ?? 0;
  const automatizaveis = criterios.dados?.filter((c) => c.automatable).length ?? 0;

  return (
    <>
      <TituloDePagina>Matriz WCAG 2.1 e legislação brasileira</TituloDePagina>
      <p>
        Correspondência entre cada critério de sucesso da WCAG 2.1 (níveis A e
        AA) e o ordenamento jurídico brasileiro — Lei 13.146/2015 (LBI),
        Constituição Federal, Convenção da ONU sobre os Direitos das Pessoas com
        Deficiência, Lei de Acesso à Informação, Decreto 5.296/2004 e eMAG 3.1.
      </p>

      {integridade.dados ? (
        <div
          className={`aviso ${
            integridade.dados.matriz_completa ? 'aviso--info' : 'aviso--erro'
          }`}
        >
          <h2>Integridade da matriz</h2>
          {integridade.dados.matriz_completa ? (
            <p>
              Todos os {integridade.dados.criterios_no_escopo} critérios do
              escopo possuem fundamentação jurídica mapeada, sobre{' '}
              {integridade.dados.dispositivos_registrados} dispositivos
              normativos registrados. A completude é verificada em teste
              automatizado: nenhuma falha detectada pode ficar juridicamente
              muda.
            </p>
          ) : (
            <p>
              Critérios sem mapeamento jurídico:{' '}
              {integridade.dados.criterios_sem_mapeamento.join(', ')}.
            </p>
          )}
        </div>
      ) : null}

      <div className="aviso aviso--info">
        <h2>Cobertura da verificação automática</h2>
        <p>
          <strong>
            {automatizaveis} dos {total} critérios
          </strong>{' '}
          admitem veredito determinístico para ao menos um modo de falha. A
          leitura precisa importa: 1.1.1 é marcado como automatizável porque a{' '}
          <em>ausência</em> de <code>alt</code> é detectável — não porque a
          adequação da descrição o seja. Um portal com todos os <code>alt</code>{' '}
          preenchidos com &ldquo;imagem&rdquo; passa na verificação e continua
          inacessível.
        </p>
      </div>

      {/* ------------------------------------------------------------ filtro */}
      <fieldset style={{ border: 0, padding: 0, margin: '1.5rem 0' }}>
        <legend style={{ fontWeight: 600, padding: 0 }}>
          Filtrar por tipo de verificação
        </legend>
        <div className="linha" role="group">
          {(
            [
              ['todos', `Todos (${total})`],
              ['automatizaveis', `Automatizáveis (${automatizaveis})`],
              ['manuais', `Exigem avaliação humana (${total - automatizaveis})`],
            ] as const
          ).map(([valor, rotulo]) => (
            <label key={valor} className="linha" style={{ gap: '0.35rem' }}>
              <input
                type="radio"
                name="filtro-criterios"
                value={valor}
                checked={filtro === valor}
                onChange={() => setFiltro(valor)}
              />
              {rotulo}
            </label>
          ))}
        </div>
      </fieldset>

      {/* -------------------------------------------------------- critérios */}
      {['perceptivel', 'operavel', 'compreensivel', 'robusto'].map((principio) => {
        const itens = porPrincipio.get(principio);
        if (!itens || itens.length === 0) return null;
        return (
          <section key={principio} aria-labelledby={`principio-${principio}`}>
            <h2 id={`principio-${principio}`}>
              {ROTULO_PRINCIPIO[principio] ?? principio} ({itens.length})
            </h2>
            {itens.map((c) => (
              <CartaoDeCriterio key={c.id} criterio={c} />
            ))}
          </section>
        );
      })}

      {/* ------------------------------------------------------ dispositivos */}
      <h2 id="dispositivos">Dispositivos normativos registrados</h2>
      <p>
        Base legal invocada pelos achados, com a referência completa em formato
        ABNT para citação.
      </p>

      {dispositivos.carregando ? <Carregando /> : null}
      {dispositivos.erro ? (
        <Erro erro={dispositivos.erro} aoTentarNovamente={dispositivos.recarregar} />
      ) : null}

      {(dispositivos.dados ?? []).map((d) => (
        <details key={d.key} className="achado">
          <summary>
            <span>{d.label}</span>
            <Selo variante="neutro">{d.strength.replace(/_/g, ' ')}</Selo>
          </summary>
          <div>
            <p>{d.summary}</p>
            <dl className="meta">
              <dt>Sujeito obrigado</dt>
              <dd>{d.addressee}</dd>
              <dt>Vias de exigibilidade</dt>
              <dd>{d.routes.map((r) => r.replace(/_/g, ' ')).join('; ') || '—'}</dd>
              <dt>Chave no sistema</dt>
              <dd>
                <code>{d.key}</code>
              </dd>
            </dl>
            <p>
              <strong>Referência:</strong> {d.citation}
            </p>
            <p>
              <a href={d.url} target="_blank" rel="noreferrer">
                Texto oficial
                <span className="apenas-leitor-de-tela"> (abre em nova aba)</span>
              </a>
            </p>
          </div>
        </details>
      ))}
    </>
  );
}

function CartaoDeCriterio({ criterio }: { criterio: Criterio }) {
  return (
    <details className="achado">
      <summary>
        <span>
          {criterio.id} — {criterio.title_pt}
        </span>
        <Selo variante="neutro">Nível {criterio.level}</Selo>
        <SeloDeRisco risco={criterio.legal_risk} />
        {criterio.automatable ? (
          <Selo variante="ok" descricao="Admite veredito determinístico automático.">
            Automatizável
          </Selo>
        ) : (
          <Selo variante="moderado" descricao="Depende de julgamento humano.">
            Avaliação humana
          </Selo>
        )}
      </summary>
      <div>
        <h4>Por que este critério existe</h4>
        <p>{criterio.rationale}</p>

        {criterio.legal_thesis ? (
          <div className="tese">
            <p>
              <strong>Fundamentação jurídica.</strong> {criterio.legal_thesis}
            </p>
          </div>
        ) : null}

        <dl className="meta">
          <dt>Grupos afetados</dt>
          <dd>{criterio.affects.map((g) => ROTULO_GRUPO[g] ?? g).join('; ')}</dd>
          <dt>Dispositivos invocáveis</dt>
          <dd>{criterio.provisions.join('; ')}</dd>
          <dt>Título original</dt>
          <dd>{criterio.title_en}</dd>
        </dl>

        {criterio.remediation ? (
          <p>
            <strong>Conduta corretiva esperada.</strong> {criterio.remediation}
          </p>
        ) : null}

        <p>
          <a href={criterio.url} target="_blank" rel="noreferrer">
            Understanding WCAG 2.1 — critério {criterio.id}
            <span className="apenas-leitor-de-tela"> (abre em nova aba)</span>
          </a>
        </p>
      </div>
    </details>
  );
}
