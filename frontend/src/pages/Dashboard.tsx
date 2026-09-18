/**
 * Painel: visão geral das varreduras registradas.
 *
 * Ordem de leitura deliberada — a mesma de um relatório de auditoria:
 *
 * 1. Estado do serviço (a coleta é possível agora?).
 * 2. Barreiras absolutas (existe portal inutilizável?).
 * 3. Resumo do conjunto, em números com escala declarada.
 * 4. Varreduras, com índices comparáveis.
 * 5. Critérios mais violados no conjunto (o que é estrutural, não acidental).
 *
 * Barreira absoluta vem antes de qualquer índice porque nenhum número
 * contínuo captura a diferença entre "difícil" e "impossível", e é essa a
 * informação que muda a decisão do gestor.
 */

import { Link } from 'react-router-dom';
import { api, useRecurso } from '../lib/api';
import {
  dataHora,
  faixaDeAtrito,
  faixaDeConformidade,
  SEM_VEREDITO,
  indice,
  inteiro,
  megabytes,
  percentual,
  reais,
} from '../lib/format';
import {
  Carregando,
  Erro,
  Indicador,
  Selo,
  Tabela,
  TituloDePagina,
} from '../components/ui';

export function Dashboard() {
  const saude = useRecurso(() => api.saude(), []);
  const varreduras = useRecurso(() => api.varreduras({ limit: 50 }), []);
  const criterios = useRecurso(() => api.frequenciaDeCriterios(), []);

  const lista = varreduras.dados?.items ?? [];
  const observadas = lista.filter((v) => v.observed);
  const comBarreiraAbsoluta = observadas.filter((v) => v.absolute_barrier);
  const plataformas = new Set(lista.map((v) => v.target_id)).size;
  const totalDeViolacoes = lista.reduce((soma, v) => soma + v.violation_count, 0);
  const totalDeOcorrencias = lista.reduce((soma, v) => soma + v.occurrence_count, 0);

  return (
    <>
      <div className="pagina-cabecalho">
        <span className="rotulo-alto">Auditoria contínua</span>
        <TituloDePagina>Painel de auditorias</TituloDePagina>
        <p>
          Varreduras de acessibilidade em plataformas digitais de saúde pública,
          avaliadas contra a WCAG 2.1 (níveis A e AA) e vinculadas à Lei
          Brasileira de Inclusão.
        </p>
      </div>

      {/* --------------------------------------------------- estado do serviço */}
      {saude.dados && !saude.dados.axe_core_disponivel ? (
        <div role="alert" className="aviso aviso--atencao">
          <h2>Serviço em estado degradado</h2>
          <p>
            O motor de regras axe-core não está disponível no servidor. Novas
            varreduras seriam executadas sem a verificação determinística e
            produziriam resultados incompletos — o que é pior do que não
            executá-las. Consulte <code>backend/vendor/README.md</code>.
          </p>
        </div>
      ) : null}

      {/* ------------------------------------------------- barreiras absolutas */}
      {comBarreiraAbsoluta.length > 0 ? (
        <div role="alert" className="aviso aviso--erro">
          <h2>
            {comBarreiraAbsoluta.length === 1
              ? '1 plataforma com barreira absoluta'
              : `${comBarreiraAbsoluta.length} plataformas com barreira absoluta`}
          </h2>
          <p>
            Nestas plataformas há violações de risco jurídico <strong>crítico</strong>:
            barreiras sem rota alternativa, que impedem completamente o uso do
            serviço por um grupo identificável de pessoas.
          </p>
          <ul>
            {comBarreiraAbsoluta.map((v) => (
              <li key={v.id}>
                <Link to={`/varreduras/${v.id}`}>{v.target_name || v.target_id}</Link>{' '}
                — varredura de {dataHora(v.started_at)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {/* ------------------------------------------------------- resumo */}
      {lista.length > 0 ? (
        <ul className="grade grade--indicadores lista-limpa" aria-label="Resumo do conjunto">
          <Indicador
            valor={inteiro(lista.length)}
            rotulo="Varreduras"
            nota={`${inteiro(plataformas)} ${
              plataformas === 1 ? 'plataforma auditada' : 'plataformas auditadas'
            }, ${inteiro(observadas.length)} com páginas observadas.`}
          />
          <Indicador
            valor={inteiro(comBarreiraAbsoluta.length)}
            rotulo="Com barreira absoluta"
            nota="Varreduras em que há violação crítica sem rota alternativa. Zero é o único valor aceitável."
            variante={comBarreiraAbsoluta.length > 0 ? 'critico' : 'ok'}
          />
          <Indicador
            valor={inteiro(totalDeViolacoes)}
            rotulo="Violações confirmadas"
            nota={`${inteiro(totalDeOcorrencias)} ocorrências em elementos distintos, somadas em todas as varreduras.`}
            variante="alto"
          />
          <Indicador
            valor={
              observadas.length > 0
                ? indice(
                    observadas.reduce((s, v) => s + (v.conformance_index ?? 0), 0) /
                      observadas.length,
                  )
                : '—'
            }
            rotulo="ICA médio"
            nota="Conformidade, 0 a 100, maior é melhor. Média simples entre varreduras observadas; não é atestado."
            variante="neutro"
          />
        </ul>
      ) : null}

      {/* ------------------------------------------------------- varreduras */}
      <h2>Varreduras registradas</h2>

      {varreduras.carregando ? <Carregando>Carregando varreduras…</Carregando> : null}
      {varreduras.erro ? (
        <Erro erro={varreduras.erro} aoTentarNovamente={varreduras.recarregar} />
      ) : null}

      {!varreduras.carregando && !varreduras.erro && lista.length === 0 ? (
        <div className="vazio">
          <h3>Nenhuma varredura registrada</h3>
          <p>
            Execute uma auditoria pela linha de comando — a via principal da
            coleta, porque produz um comando registrável e citável no trabalho:
          </p>
          <pre>
            <code>
              python scripts/servidor_fixtures.py{'\n'}
              acessisaude varrer fixtures-local
            </code>
          </pre>
        </div>
      ) : null}

      {lista.length > 0 ? (
        <Tabela
          larga
          legenda="Varreduras registradas, da mais recente à mais antiga"
          explicacao="ICA: conformidade, 0 a 100, maior é melhor. IAN: atrito de navegação, 0 a 100, menor é melhor."
          cabecalhos={
            <>
              <th scope="col">Plataforma</th>
              <th scope="col">Coletada em</th>
              <th scope="col" className="num">
                ICA
              </th>
              <th scope="col" className="num">
                IAN
              </th>
              <th scope="col" className="num">
                Violações
              </th>
              <th scope="col" className="num">
                Peso médio
              </th>
              <th scope="col">Situação</th>
            </>
          }
        >
          {lista.map((v) => (
            <tr key={v.id}>
              <th scope="row">
                <Link to={`/varreduras/${v.id}`}>{v.target_name || v.target_id}</Link>
                {v.sphere ? <span className="celula-secundaria">{v.sphere}</span> : null}
              </th>
              <td>{dataHora(v.started_at)}</td>
              <td className="num">
                {indice(v.conformance_index)}
                <span className="apenas-leitor-de-tela">
                  {' '}
                  de 100 — {faixaDeConformidade(v.conformance_index)}
                </span>
              </td>
              <td className="num">
                {indice(v.friction_index)}
                <span className="apenas-leitor-de-tela">
                  {' '}
                  de 100 — {faixaDeAtrito(v.friction_index)}
                </span>
              </td>
              <td className="num">
                {inteiro(v.violation_count)}
                <span className="celula-secundaria">
                  {inteiro(v.occurrence_count)} ocorr.
                </span>
              </td>
              <td className="num">
                {megabytes(v.mean_page_mb)}
                <span className="celula-secundaria">{reais(v.mean_cost_brl)}</span>
              </td>
              <td>
                {/* Três estados, e não dois: `null` significa que nada foi
                    observado. Tratá-lo como falso faria o painel anunciar
                    "sem barreira absoluta" para uma varredura em que nenhuma
                    página carregou — a leitura mais enganosa possível. */}
                {!v.observed ? (
                  <Selo variante="moderado" descricao={SEM_VEREDITO}>
                    Sem veredito
                  </Selo>
                ) : v.absolute_barrier ? (
                  <Selo
                    variante="critico"
                    descricao="Há barreira que impede completamente o uso por um grupo identificável."
                  >
                    Barreira absoluta
                  </Selo>
                ) : (
                  <Selo variante="neutro">Sem barreira absoluta</Selo>
                )}
                {v.loss_rate > 0 ? (
                  <span className="celula-secundaria">
                    {percentual(v.loss_rate)} das páginas em erro
                  </span>
                ) : null}
              </td>
            </tr>
          ))}
        </Tabela>
      ) : null}

      {/* --------------------------------------------- critérios mais violados */}
      <h2>Barreiras mais frequentes no conjunto</h2>
      <p className="secao-intro">
        Agregado de todas as varreduras registradas. Responde à pergunta que
        interessa à política pública: quais barreiras são <em>estruturais</em> no
        ecossistema de saúde digital, e não acidentes de um portal isolado.
      </p>

      {criterios.carregando ? <Carregando /> : null}
      {criterios.erro ? (
        <Erro erro={criterios.erro} aoTentarNovamente={criterios.recarregar} />
      ) : null}

      {criterios.dados && criterios.dados.length > 0 ? (
        <Tabela
          legenda="Critérios WCAG 2.1 violados"
          explicacao="Por número de achados no conjunto de varreduras; os 15 mais frequentes."
          cabecalhos={
            <>
              <th scope="col">Critério</th>
              <th scope="col">Nível</th>
              <th scope="col" className="num">
                Achados
              </th>
            </>
          }
        >
          {criterios.dados.slice(0, 15).map((c) => (
            <tr key={c.criterio}>
              <th scope="row">
                {c.criterio} {c.titulo ?? ''}
              </th>
              <td>{c.nivel ?? '—'}</td>
              <td className="num">{inteiro(c.achados)}</td>
            </tr>
          ))}
        </Tabela>
      ) : null}

      {criterios.dados && criterios.dados.length === 0 && !criterios.carregando ? (
        <p className="texto-suave">
          Nenhum achado agregado ainda. Execute ao menos uma varredura.
        </p>
      ) : null}
    </>
  );
}
