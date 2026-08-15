/**
 * Detalhe de uma varredura: índices, perfil de exclusão e achados.
 *
 * Os achados são agrupados por **risco jurídico**, não por gravidade técnica
 * nem por página. A escolha é a tese do projeto em forma de interface: para o
 * gestor público, a pergunta operante não é "quantos elementos estão errados",
 * é "o que me expõe e o que impede o cidadão de ser atendido".
 *
 * Achados indeterminados aparecem em seção própria, claramente separada, e
 * nunca somados às violações.
 */

import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, useRecurso } from '../lib/api';
import type { Achado, RiscoJuridico } from '../lib/types';
import {
  dataHora,
  faixaDeAtrito,
  faixaDeConformidade,
  indice,
  inteiro,
  megabytes,
  percentual,
  reais,
  ROTULO_GRAVIDADE,
  ROTULO_GRUPO,
  ROTULO_ORIGEM,
  urlCurta,
} from '../lib/format';
import {
  AvisoDeBarreiraAbsoluta,
  AvisoDeCobertura,
  Barra,
  Carregando,
  Erro,
  Indicador,
  Selo,
  SeloDeRisco,
  Tabela,
  TituloDePagina,
} from '../components/ui';

/** Ordem de apresentação: do mais grave ao menos grave. */
const ORDEM_DE_RISCO: RiscoJuridico[] = ['critico', 'alto', 'moderado', 'baixo'];

export function DetalheDaVarredura() {
  const { id = '' } = useParams();
  const varredura = useRecurso(() => api.varredura(id), [id]);
  const indices = useRecurso(() => api.indices(id), [id]);

  const { violacoes, indeterminados } = useMemo(() => {
    const todos = varredura.dados?.pages.flatMap((p) => p.findings) ?? [];
    return {
      violacoes: todos.filter((f) => f.outcome === 'fail'),
      indeterminados: todos.filter((f) => f.outcome === 'incomplete'),
    };
  }, [varredura.dados]);

  const porRisco = useMemo(() => {
    const grupos = new Map<RiscoJuridico | 'nao_classificado', Achado[]>();
    for (const achado of violacoes) {
      const chave = achado.legal_risk ?? 'nao_classificado';
      const atual = grupos.get(chave) ?? [];
      atual.push(achado);
      grupos.set(chave, atual);
    }
    for (const lista of grupos.values()) {
      lista.sort((a, b) => b.occurrences - a.occurrences);
    }
    return grupos;
  }, [violacoes]);

  if (varredura.carregando || indices.carregando) {
    return <Carregando>Carregando a varredura…</Carregando>;
  }
  if (varredura.erro) {
    return <Erro erro={varredura.erro} aoTentarNovamente={varredura.recarregar} />;
  }
  if (indices.erro) {
    return <Erro erro={indices.erro} aoTentarNovamente={indices.recarregar} />;
  }
  if (!varredura.dados || !indices.dados) {
    return <Carregando />;
  }

  const v = varredura.dados;
  const s = indices.dados.indices;
  const custo = s.data_cost;

  return (
    <>
      <p>
        <Link to="/">← Voltar ao painel</Link>
      </p>

      <TituloDePagina>{v.target_name || v.target_id}</TituloDePagina>
      <p className="texto-suave">
        Varredura de {dataHora(v.started_at)} · {v.base_url}
      </p>

      {s.absolute_barrier ? <AvisoDeBarreiraAbsoluta /> : null}

      {/* -------------------------------------------------------- índices */}
      <h2 id="indices">Índices agregados</h2>
      <ul className="grade lista-limpa">
        <Indicador
          valor={indice(s.conformance_index)}
          rotulo="ICA — Conformidade"
          nota={`0 a 100, maior é melhor. ${faixaDeConformidade(s.conformance_index)}.`}
        />
        <Indicador
          valor={indice(s.friction_index)}
          rotulo="IAN — Atrito de navegação"
          nota={`0 a 100, menor é melhor. Quanto custa usar apesar das barreiras: ${faixaDeAtrito(
            s.friction_index,
          )}.`}
        />
        <Indicador
          valor={indice(s.legal_exposure_index)}
          rotulo="IEJ — Exposição jurídica"
          nota="0 a 100, menor é melhor. Concentra-se nas violações de risco moderado ou superior."
        />
        <Indicador
          valor={inteiro(s.violations)}
          rotulo="Violações confirmadas"
          nota={`${inteiro(s.occurrences)} ocorrências em elementos distintos. ${inteiro(
            s.incomplete,
          )} achados requerem revisão humana.`}
        />
        {custo ? (
          <Indicador
            valor={megabytes(custo.total_mb)}
            rotulo="Peso médio por página"
            nota={`${reais(custo.cost_brl)} por acesso — ${custo.franchise_share_pct.toFixed(
              2,
            )}% da franquia mensal de referência. ${custo.third_party_share_pct.toFixed(
              0,
            )}% do tráfego vai a domínios de terceiros.`}
          />
        ) : null}
      </ul>

      <AvisoDeCobertura criteriosAvaliados={s.criteria_evaluated} cobertura={s.coverage} />

      <p className="linha">
        <a className="botao" href={api.urlRelatorio(v.id)} target="_blank" rel="noreferrer">
          Abrir relatório completo em HTML
          <span className="apenas-leitor-de-tela"> (abre em nova aba)</span>
        </a>
        <a className="botao botao--secundario" href={api.urlCsv(v.id)}>
          Exportar achados em CSV
        </a>
      </p>

      {/* ---------------------------------------------- perfil de exclusão */}
      <h2 id="exclusao">Quem é excluído</h2>
      <p>
        Converte a contagem de defeitos em população impactada. É a leitura que
        importa para a decisão de gestão e para o argumento jurídico: o dano
        juridicamente relevante é o da pessoa excluída, não o do elemento HTML
        malformado.
      </p>

      {indices.dados.grupos_excluidos.length > 0 ? (
        <Tabela
          legenda="Ocorrências de barreira por grupo de pessoas afetado"
          cabecalhos={
            <>
              <th scope="col">Grupo</th>
              <th scope="col" className="num">
                Ocorrências
              </th>
            </>
          }
        >
          {indices.dados.grupos_excluidos.map((g) => {
            const maximo = indices.dados!.grupos_excluidos[0]?.ocorrencias ?? 1;
            return (
              <tr key={g.grupo}>
                <th scope="row">
                  {ROTULO_GRUPO[g.grupo] ?? g.grupo}
                  <Barra fracao={g.ocorrencias / maximo} />
                </th>
                <td className="num">{inteiro(g.ocorrencias)}</td>
              </tr>
            );
          })}
        </Tabela>
      ) : (
        <p className="texto-suave">
          Nenhuma barreira atribuída a grupo específico nesta varredura.
        </p>
      )}

      {/* ------------------------------------------------------- achados */}
      <h2 id="achados">Achados, por gravidade jurídica</h2>

      {violacoes.length === 0 ? (
        <p>
          Nenhuma violação confirmada pelas verificações automáticas executadas.
          Isso não atesta conformidade — ver o alcance declarado acima.
        </p>
      ) : null}

      {ORDEM_DE_RISCO.map((risco) => {
        const itens = porRisco.get(risco);
        if (!itens || itens.length === 0) return null;
        return (
          <section key={risco} aria-labelledby={`risco-${risco}`}>
            <h3 id={`risco-${risco}`}>
              <SeloDeRisco risco={risco} />{' '}
              <span>
                {itens.length} {itens.length === 1 ? 'achado' : 'achados'}
              </span>
            </h3>
            {itens.map((achado) => (
              <CartaoDeAchado key={achado.id} achado={achado} />
            ))}
          </section>
        );
      })}

      {/* --------------------------------------------------- indeterminados */}
      <h2 id="revisao">Achados que exigem revisão humana</h2>
      <p>
        Os itens abaixo <strong>não</strong> são violações declaradas. São
        situações em que a verificação automática identificou indício, mas o
        veredito depende de julgamento que nenhum algoritmo substitui — por
        exemplo, se uma alternativa textual descreve corretamente a imagem.
      </p>

      {indeterminados.length > 0 ? (
        <Tabela
          legenda="Achados com veredito indeterminado, pendentes de revisão humana"
          cabecalhos={
            <>
              <th scope="col">Situação</th>
              <th scope="col">Regra</th>
              <th scope="col" className="num">
                Ocorrências
              </th>
            </>
          }
        >
          {indeterminados.map((f) => (
            <tr key={f.id}>
              <th scope="row">{f.summary}</th>
              <td>
                <code>{f.rule_id}</code>
              </td>
              <td className="num">{inteiro(f.occurrences)}</td>
            </tr>
          ))}
        </Tabela>
      ) : (
        <p className="texto-suave">Nenhum item pendente de revisão.</p>
      )}

      {/* ------------------------------------------------------ procedência */}
      <h2 id="procedencia">Procedência do dado</h2>
      <dl className="meta">
        <dt>Identificador</dt>
        <dd>
          <code>{v.id}</code>
        </dd>
        <dt>Esquema de dados</dt>
        <dd>{v.schema_version}</dd>
        <dt>Versão da ferramenta</dt>
        <dd>{v.engine_version}</dd>
        <dt>Motor de regras</dt>
        <dd>axe-core {v.axe_version ?? 'não registrado'}</dd>
        <dt>Navegador</dt>
        <dd>{v.browser}</dd>
        <dt>Páginas auditadas</dt>
        <dd>{inteiro(v.page_count)}</dd>
        <dt>Taxa de perda</dt>
        <dd>{percentual(indices.dados.taxa_de_perda)} das páginas em erro</dd>
      </dl>

      <h3>Parâmetros usados no cálculo dos índices</h3>
      <p className="texto-suave">
        Nenhum índice deste projeto circula dissociado das constantes que o
        produziram — sem elas, nenhum número seria reexecutável.
      </p>
      <Tabela
        legenda="Constantes de cálculo desta varredura"
        cabecalhos={
          <>
            <th scope="col">Parâmetro</th>
            <th scope="col" className="num">
              Valor
            </th>
          </>
        }
      >
        {Object.entries(indices.dados.parametros).map(([chave, valor]) => (
          <tr key={chave}>
            <th scope="row">
              <code>{chave}</code>
            </th>
            <td className="num">{valor}</td>
          </tr>
        ))}
      </Tabela>

      {indices.dados.lacunas_declaradas.length > 0 ? (
        <>
          <h3>Lacunas declaradas da amostra</h3>
          <div className="aviso aviso--atencao">
            <p>
              As páginas a seguir integram o serviço mas <strong>não foram
              auditadas</strong>, por exigirem autenticação. Como essas telas
              concentram parte relevante do fluxo assistencial, os índices desta
              varredura podem estar otimistas.
            </p>
            <ul>
              {indices.dados.lacunas_declaradas.map((g) => (
                <li key={g.url}>
                  <code>{urlCurta(g.url)}</code> — {g.label} ({g.motivo})
                </li>
              ))}
            </ul>
          </div>
        </>
      ) : null}

      {v.errors.length > 0 ? (
        <>
          <h3>Erros durante a coleta</h3>
          <ul>
            {v.errors.map((e) => (
              <li key={e}>
                <code>{e}</code>
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </>
  );
}

/** Um achado, com suas três camadas: técnica, normativa e jurídica. */
function CartaoDeAchado({ achado }: { achado: Achado }) {
  return (
    <details className="achado">
      <summary>
        <span>{achado.summary}</span>
        <Selo variante="neutro">
          {inteiro(achado.occurrences)}{' '}
          {achado.occurrences === 1 ? 'ocorrência' : 'ocorrências'}
        </Selo>
      </summary>
      <div>
        <dl className="meta">
          <dt>Regra</dt>
          <dd>
            <code>{achado.rule_id}</code> ({ROTULO_ORIGEM[achado.source] ?? achado.source})
          </dd>

          <dt>Critérios WCAG</dt>
          <dd>
            {achado.criteria.length > 0
              ? achado.criteria.join(', ')
              : 'Não corresponde a critério WCAG — barreira de direitos digitais.'}
          </dd>

          <dt>Gravidade técnica</dt>
          <dd>
            {achado.impact ? ROTULO_GRAVIDADE[achado.impact] : 'não classificada'}
          </dd>

          <dt>Grupos afetados</dt>
          <dd>
            {achado.affects.length > 0
              ? achado.affects.map((g) => ROTULO_GRUPO[g] ?? g).join('; ')
              : '—'}
          </dd>

          <dt>Página</dt>
          <dd>
            <a href={achado.page_url}>{urlCurta(achado.page_url)}</a> ({achado.viewport})
          </dd>
        </dl>

        {achado.description ? <p>{achado.description}</p> : null}

        {achado.legal_thesis ? (
          <div className="tese">
            <p>
              <strong>Fundamentação jurídica.</strong> {achado.legal_thesis}
            </p>
          </div>
        ) : null}

        {achado.legal_provisions.length > 0 ? (
          <p>
            <strong>Dispositivos invocáveis:</strong>{' '}
            {achado.legal_provisions.join('; ')}.
          </p>
        ) : null}

        {achado.remediation ? (
          <p>
            <strong>Conduta corretiva esperada.</strong> {achado.remediation}
          </p>
        ) : null}

        {achado.nodes.length > 0 ? (
          <>
            <h4>Evidência</h4>
            {achado.nodes.slice(0, 3).map((no, i) => (
              <div key={`${no.selector}-${i}`}>
                <p>
                  <code>{no.selector}</code>
                </p>
                {no.failure_summary ? <p>{no.failure_summary}</p> : null}
                {no.html ? (
                  <pre>
                    <code>{no.html}</code>
                  </pre>
                ) : null}
              </div>
            ))}
            {achado.nodes.length > 3 ? (
              <p className="texto-suave">
                … e mais {achado.nodes.length - 3} ocorrência(s). Lista completa no
                relatório HTML e no JSON da varredura.
              </p>
            ) : null}
          </>
        ) : null}

        {achado.help_url ? (
          <p>
            <a href={achado.help_url} target="_blank" rel="noreferrer">
              Documentação técnica do critério
              <span className="apenas-leitor-de-tela"> (abre em nova aba)</span>
            </a>
          </p>
        ) : null}
      </div>
    </details>
  );
}
