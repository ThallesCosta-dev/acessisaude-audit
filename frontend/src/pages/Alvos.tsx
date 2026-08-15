/**
 * Catálogo de alvos — o desenho amostral do estudo, exposto como interface.
 *
 * Esta tela existe para um propósito metodológico, não operacional: tornar
 * inspecionável **por que cada plataforma integra a amostra** e **o que ficou
 * de fora**. Um estudo cujo desenho amostral só existe em um YAML no repositório
 * é, na prática, um estudo cujo desenho amostral ninguém confere.
 */

import { api, useRecurso } from '../lib/api';
import { inteiro, ROTULO_ESFERA } from '../lib/format';
import { Carregando, Erro, Selo, TituloDePagina } from '../components/ui';
import type { Esfera } from '../lib/types';

export function Alvos() {
  const alvos = useRecurso(() => api.alvos(), []);

  if (alvos.carregando) return <Carregando>Carregando o catálogo…</Carregando>;
  if (alvos.erro) return <Erro erro={alvos.erro} aoTentarNovamente={alvos.recarregar} />;

  const lista = alvos.dados ?? [];
  const habilitados = lista.filter((a) => a.enabled);
  const desabilitados = lista.filter((a) => !a.enabled);
  const totalLacunas = lista.reduce((soma, a) => soma + a.declared_gaps, 0);

  return (
    <>
      <TituloDePagina>Plataformas do estudo</TituloDePagina>
      <p>
        Catálogo das plataformas digitais de saúde pública sob auditoria, com a
        justificativa de inclusão de cada uma e as lacunas declaradas da amostra.
      </p>

      <div className="aviso aviso--info">
        <h2>Conduta de coleta</h2>
        <p>
          Plataformas em produção nascem <strong>desabilitadas</strong> no
          catálogo. Habilitar uma delas é decisão consciente do pesquisador, que
          assume: respeito ao <code>robots.txt</code>, intervalo mínimo entre
          requisições, identificação no <code>User-Agent</code> e ausência de
          qualquer interação com formulários ou autenticação.
        </p>
        <p>
          A ferramenta <strong>nunca</strong> preenche formulários, nunca
          autentica e nunca envia dados. Ela lê o DOM renderizado de páginas
          públicas — nada além disso.
        </p>
      </div>

      {totalLacunas > 0 ? (
        <div className="aviso aviso--atencao">
          <h2>Limitação declarada da amostra</h2>
          <p>
            {inteiro(totalLacunas)} página(s) do conjunto exigem autenticação e{' '}
            <strong>não são auditadas</strong>. Auditar área autenticada de
            sistema público sem autorização formal seria conduta inadmissível em
            pesquisa. Como essas telas concentram parte relevante do fluxo
            assistencial — resultado de exame, carteira de vacinação,
            agendamento confirmado —, os resultados do estudo podem estar
            otimistas em relação à experiência real do usuário.
          </p>
        </div>
      ) : null}

      <h2>Habilitadas para varredura ({habilitados.length})</h2>
      {habilitados.length === 0 ? (
        <p className="texto-suave">Nenhuma plataforma habilitada no momento.</p>
      ) : (
        <ul className="grade lista-limpa">
          {habilitados.map((a) => (
            <CartaoDeAlvo key={a.id} alvo={a} />
          ))}
        </ul>
      )}

      <h2>Documentadas, ainda não habilitadas ({desabilitados.length})</h2>
      <p className="texto-suave">
        Permanecem no catálogo com sua justificativa de seleção, o que mantém o
        desenho amostral do estudo completo e auditável mesmo antes da coleta.
      </p>
      <ul className="grade lista-limpa">
        {desabilitados.map((a) => (
          <CartaoDeAlvo key={a.id} alvo={a} />
        ))}
      </ul>
    </>
  );
}

function CartaoDeAlvo({
  alvo,
}: {
  alvo: {
    id: string;
    name: string;
    organization: string;
    sphere: Esfera;
    base_url: string;
    territory: string;
    enabled: boolean;
    population_served: number | null;
    selection_rationale: string;
    auditable_pages: number;
    declared_gaps: number;
    categories: string[];
  };
}) {
  return (
    <li className="cartao">
      <h3>{alvo.name}</h3>
      <p className="texto-suave">
        {alvo.organization}
        {alvo.territory ? ` · ${alvo.territory}` : ''}
      </p>

      <p className="linha">
        <Selo variante="neutro">{ROTULO_ESFERA[alvo.sphere]}</Selo>
        {alvo.enabled ? (
          <Selo variante="ok">Habilitada</Selo>
        ) : (
          <Selo
            variante="moderado"
            descricao="Alvos de produção nascem desabilitados por conduta de coleta."
          >
            Não habilitada
          </Selo>
        )}
        {alvo.declared_gaps > 0 ? (
          <Selo
            variante="alto"
            descricao="Páginas que exigem autenticação e não são auditadas."
          >
            {inteiro(alvo.declared_gaps)} lacuna(s)
          </Selo>
        ) : null}
      </p>

      <dl className="meta">
        <dt>Endereço</dt>
        <dd>
          <a href={alvo.base_url}>{alvo.base_url}</a>
        </dd>
        <dt>Páginas auditáveis</dt>
        <dd>{inteiro(alvo.auditable_pages)}</dd>
        {alvo.population_served ? (
          <>
            <dt>População de referência</dt>
            <dd>{inteiro(alvo.population_served)} pessoas</dd>
          </>
        ) : null}
        {alvo.categories.length > 0 ? (
          <>
            <dt>Serviços</dt>
            <dd>{alvo.categories.join(', ')}</dd>
          </>
        ) : null}
      </dl>

      {alvo.selection_rationale ? (
        <>
          <h4>Por que integra a amostra</h4>
          <p>{alvo.selection_rationale}</p>
        </>
      ) : null}
    </li>
  );
}
