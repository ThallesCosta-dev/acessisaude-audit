/**
 * Componentes de interface compartilhados.
 *
 * Cada um resolve um problema de acessibilidade que, resolvido caso a caso nas
 * telas, seria resolvido de forma inconsistente:
 *
 * - `Selo` garante que toda escala cromática venha com rótulo textual (1.4.1).
 * - `Erro` e `Carregando` publicam mudanças de estado em regiões `aria-live`,
 *   sem as quais o usuário de leitor de tela não sabe que algo aconteceu (4.1.3).
 * - `Indicador` impede que um número apareça sem escala e sem sentido de leitura.
 * - `Tabela` força `<caption>` e confina a rolagem ao bloco (1.3.1, 1.4.10).
 */

import type { ReactNode } from 'react';
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import type { ApiError } from '../lib/api';
import type { RiscoJuridico } from '../lib/types';
import { EXPLICACAO_RISCO, ROTULO_RISCO } from '../lib/format';

/** Variantes visuais do selo. Cada uma tem rótulo textual obrigatório. */
type VarianteSelo = 'critico' | 'alto' | 'moderado' | 'baixo' | 'ok' | 'neutro';

interface SeloProps {
  variante: VarianteSelo;
  children: ReactNode;
  /** Texto adicional lido por tecnologia assistiva, quando o rótulo é abreviado. */
  descricao?: string;
}

/**
 * Etiqueta com cor de reforço e texto obrigatório.
 *
 * O texto é o portador do sentido; a cor apenas o acompanha. Um usuário com
 * deficiência na visão de cores lê exatamente a mesma informação.
 */
export function Selo({ variante, children, descricao }: SeloProps) {
  return (
    <span className={`selo selo--${variante}`}>
      {children}
      {descricao ? <span className="apenas-leitor-de-tela"> — {descricao}</span> : null}
    </span>
  );
}

/** Selo de risco jurídico, com a explicação da consequência prática. */
export function SeloDeRisco({ risco }: { risco: RiscoJuridico | null }) {
  if (!risco) return <Selo variante="neutro">Risco não classificado</Selo>;
  return (
    <Selo variante={risco} descricao={EXPLICACAO_RISCO[risco]}>
      {ROTULO_RISCO[risco]}
    </Selo>
  );
}

interface IndicadorProps {
  valor: string;
  rotulo: string;
  /** Escala e sentido de leitura. Obrigatório: número sem escala não informa. */
  nota: string;
}

/**
 * Cartão de índice.
 *
 * `nota` é obrigatória por decisão de projeto. Um "72" isolado não diz se é bom
 * ou ruim, nem em que escala — e um painel que exibe números assim transfere ao
 * leitor um trabalho de interpretação que ele não tem como fazer.
 */
export function Indicador({ valor, rotulo, nota }: IndicadorProps) {
  return (
    <li className="cartao">
      <span className="indicador__valor">{valor}</span>
      <span className="indicador__rotulo">{rotulo}</span>
      <span className="indicador__nota">{nota}</span>
    </li>
  );
}

/**
 * Estado de carregamento, anunciado por tecnologia assistiva.
 *
 * `role="status"` com `aria-live="polite"`: o leitor de tela anuncia sem
 * interromper o que estiver sendo lido. Sem isso, a tela permanece em silêncio
 * e o usuário não distingue "carregando" de "vazio".
 */
export function Carregando({ children = 'Carregando…' }: { children?: ReactNode }) {
  return (
    <p role="status" aria-live="polite" className="texto-suave">
      {children}
    </p>
  );
}

/**
 * Estado de erro, anunciado com prioridade.
 *
 * `role="alert"` já implica `aria-live="assertive"`: o leitor de tela anuncia a
 * mensagem assim que ela entra no documento, sem que seja preciso mover o foco.
 *
 * **O foco não é movido de propósito.** Roubar o foco no carregamento da tela
 * arrancaria o usuário de teclado de onde ele estava — em particular, tornaria
 * o link de salto inalcançável na primeira tabulação, que é justamente o
 * mecanismo de bypass exigido pelo critério 2.4.1. O comportamento foi
 * detectado pela própria suíte de acessibilidade deste painel
 * (`tests/acessibilidade.spec.ts`), que falhou por não conseguir alcançar o
 * link de salto quando a API estava fora do ar.
 *
 * `tabIndex={-1}` é mantido para que a mensagem possa receber foco
 * programaticamente quando o erro decorrer de uma ação explícita do usuário —
 * caso em que mover o foco é apropriado, porque ele já está aguardando resposta.
 */
export function Erro({
  erro,
  aoTentarNovamente,
}: {
  erro: ApiError;
  aoTentarNovamente?: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  return (
    <div ref={ref} tabIndex={-1} role="alert" className="aviso aviso--erro">
      <h2>Não foi possível carregar os dados</h2>
      <p>{erro.message}</p>
      {erro.status > 0 ? (
        <p className="texto-suave">Código HTTP {erro.status}.</p>
      ) : null}
      {aoTentarNovamente ? (
        <button type="button" className="botao botao--secundario" onClick={aoTentarNovamente}>
          Tentar novamente
        </button>
      ) : null}
    </div>
  );
}

/** Aviso de barreira absoluta — a informação mais importante de toda a tela. */
export function AvisoDeBarreiraAbsoluta() {
  return (
    <div role="alert" className="aviso aviso--erro">
      <h2>Barreira absoluta identificada</h2>
      <p>
        Foram detectadas violações de risco jurídico <strong>crítico</strong>:
        barreiras que impedem completamente o uso do serviço por um grupo
        identificável de pessoas, sem rota alternativa. Nessa condição, os
        demais índices desta página descrevem o grau de dificuldade de um
        serviço que, para essas pessoas, está simplesmente indisponível.
      </p>
    </div>
  );
}

/**
 * Aviso permanente sobre o alcance da verificação automática.
 *
 * Aparece em toda tela de resultado, e não apenas na documentação. A tentação
 * de exibir só o número é grande, e é exatamente ela que produz a leitura
 * indevida de "o portal tem 78% de acessibilidade".
 */
export function AvisoDeCobertura({
  criteriosAvaliados,
  cobertura,
}: {
  criteriosAvaliados: number;
  cobertura: number;
}) {
  return (
    <div className="aviso aviso--info">
      <h3>Alcance desta verificação</h3>
      <p>
        A verificação automática cobre{' '}
        <strong>
          {criteriosAvaliados} dos 50 critérios de sucesso WCAG 2.1 de níveis A e
          AA
        </strong>{' '}
        ({Math.round(cobertura * 100)}%), e apenas para os modos de falha que
        admitem veredito determinístico. Os demais dependem de julgamento humano
        — por exemplo, se uma alternativa textual <em>descreve</em> a imagem, e
        não apenas se ela existe.
      </p>
      <p>
        <strong>Ausência de achado não equivale a conformidade.</strong> Este
        painel estabelece um piso de não conformidade, nunca um atestado de
        acessibilidade.
      </p>
    </div>
  );
}

interface TabelaProps {
  /** Descrição do conteúdo. Obrigatória: tabela sem legenda desorienta (1.3.1). */
  legenda: string;
  cabecalhos: ReactNode;
  children: ReactNode;
}

/**
 * Tabela de dados com legenda e rolagem confinada.
 *
 * O contêiner recebe `tabindex={0}` e `role="region"` para que a rolagem
 * horizontal seja alcançável por teclado — sem isso, o conteúdo à direita da
 * borda ficaria inacessível a quem não usa mouse.
 */
export function Tabela({ legenda, cabecalhos, children }: TabelaProps) {
  return (
    <div className="tabela-rolavel" tabIndex={0} role="region" aria-label={legenda}>
      <table>
        <caption>{legenda}</caption>
        <thead>
          <tr>{cabecalhos}</tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

/**
 * Título de página que move o foco **apenas em troca de rota**.
 *
 * Em aplicações de página única, navegar não recarrega o documento: o foco
 * permanece no link clicado e o leitor de tela não anuncia nada. Mover o foco
 * para o título é a técnica recomendada pelo W3C para restaurar o
 * comportamento que o usuário espera de uma navegação.
 *
 * **Na carga inicial, porém, mover o foco é incorreto.** O navegador já
 * posiciona o usuário no início do documento, e adiantá-lo até o `h1` pula o
 * link de salto — anulando o mecanismo de bypass do critério 2.4.1 logo na
 * primeira tabulação. A distinção usa `useLocation().key`, que o react-router
 * define como `'default'` exatamente na entrada inicial do histórico.
 *
 * Este comportamento foi descoberto pela suíte de acessibilidade do próprio
 * painel, e não por revisão manual — o que é, em si, um argumento a favor de
 * auditar continuamente em vez de auditar uma vez.
 */
export function TituloDePagina({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLHeadingElement>(null);
  const { key } = useLocation();

  useEffect(() => {
    if (key !== 'default') {
      ref.current?.focus();
    }
  }, [key]);

  return (
    <h1 ref={ref} tabIndex={-1}>
      {children}
    </h1>
  );
}

/**
 * Barra proporcional acessível.
 *
 * Não usa `<progress>`: seu estilo é difícil de controlar entre navegadores e
 * seu valor nem sempre é anunciado. Aqui o valor está no texto adjacente, e a
 * barra é `aria-hidden` — decoração pura, sem informação exclusiva.
 */
export function Barra({ fracao }: { fracao: number }) {
  const largura = Math.max(0, Math.min(1, fracao)) * 100;
  return (
    <span
      aria-hidden="true"
      style={{
        display: 'block',
        height: '0.4rem',
        background: 'var(--papel-alt)',
        borderRadius: '999px',
        overflow: 'hidden',
        marginTop: '0.3rem',
      }}
    >
      <span
        style={{
          display: 'block',
          width: `${largura}%`,
          height: '100%',
          background: 'var(--acento)',
        }}
      />
    </span>
  );
}
