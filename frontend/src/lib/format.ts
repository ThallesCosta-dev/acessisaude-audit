/**
 * Formatação e rótulos em português.
 *
 * Regra que atravessa todo este módulo: **nenhuma informação é transmitida
 * apenas por cor** (WCAG 1.4.1). Toda escala cromática do painel tem aqui um
 * rótulo textual correspondente, e é ele que os componentes renderizam — a cor
 * entra como reforço, nunca como portadora única de sentido.
 */

import type { Esfera, GravidadeTecnica, RiscoJuridico, Veredito } from './types';

const NUM = new Intl.NumberFormat('pt-BR');
const DEC1 = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const DEC2 = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const BRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const DATA = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
});

/** Inteiro com separador de milhar. */
export const inteiro = (valor: number): string => NUM.format(valor);

/**
 * Índice em escala 0–100, com uma casa decimal.
 *
 * Aceita nulo e devolve travessão. Nulo significa que nenhuma página foi
 * auditada: não há veredito, o que difere tanto de conformidade quanto de não
 * conformidade. Exibir 0 ou 100 nesse caso inventaria um resultado.
 */
export const indice = (valor: number | null | undefined): string =>
  valor === null || valor === undefined ? '—' : DEC1.format(valor);

/** Rótulo textual para o estado "sem observação", usado por leitor de tela. */
export const SEM_VEREDITO =
  'sem veredito — nenhuma página foi auditada; não é conformidade nem não conformidade';

/** Megabytes com duas casas. */
export const megabytes = (valor: number): string => `${DEC2.format(valor)} MB`;

/**
 * Valor monetário com precisão adaptativa.
 *
 * Duas casas decimais são a convenção para preços e são inadequadas aqui: com o
 * preço de referência coletado (R$ 3,00 por GiB), o custo de um único acesso
 * fica na casa dos milésimos, e a formatação monetária usual exibiria
 * "R$ 0,00" para praticamente toda página — apagando justamente o indicador que
 * se quer comunicar.
 *
 * Abaixo de R$ 0,01, o valor é expresso em **centavos**, que é a unidade em que
 * a grandeza é inteligível ("0,7 centavo por acesso").
 */
export const reais = (valor: number): string => {
  if (valor > 0 && valor < 0.01) {
    const centavos = valor * 100;
    const texto = new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(centavos);
    // Em português a flexão acompanha a grandeza, não a parte inteira: abaixo
    // de dois, singular ("0,7 centavo"); de dois em diante, plural.
    return `${texto} centavo${centavos >= 2 ? 's' : ''}`;
  }
  return BRL.format(valor);
};

/** Fração em [0,1] formatada como percentual. */
export const percentual = (fracao: number, casas = 1): string =>
  `${new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(fracao * 100)}%`;

/** Data e hora local a partir de um instante ISO em UTC. */
export const dataHora = (iso: string): string => DATA.format(new Date(iso));

/** Rótulo textual do risco jurídico. */
export const ROTULO_RISCO: Record<RiscoJuridico, string> = {
  baixo: 'Risco baixo',
  moderado: 'Risco moderado',
  alto: 'Risco alto',
  critico: 'Risco crítico',
};

/** Explicação do que cada nível de risco significa em consequência prática. */
export const EXPLICACAO_RISCO: Record<RiscoJuridico, string> = {
  baixo: 'Dificulta o uso, mas há rota alternativa para concluir a tarefa.',
  moderado: 'Exige esforço desproporcional ou auxílio de terceiro, ferindo a autonomia.',
  alto: 'Impede a conclusão da tarefa por um grupo identificável de pessoas.',
  critico:
    'Impede o acesso a serviço de saúde essencial, sem rota alternativa, com risco de ' +
    'dano à saúde ou perda de vaga não recuperável.',
};

/** Rótulo textual da gravidade técnica. */
export const ROTULO_GRAVIDADE: Record<GravidadeTecnica, string> = {
  minor: 'Gravidade técnica menor',
  moderate: 'Gravidade técnica moderada',
  serious: 'Gravidade técnica séria',
  critical: 'Gravidade técnica crítica',
};

/** Rótulo textual do veredito. */
export const ROTULO_VEREDITO: Record<Veredito, string> = {
  pass: 'Conforme',
  fail: 'Violação confirmada',
  incomplete: 'Requer revisão humana',
  inapplicable: 'Não aplicável',
};

/** Rótulo da esfera federativa. */
export const ROTULO_ESFERA: Record<Esfera, string> = {
  federal: 'Federal',
  estadual: 'Estadual',
  municipal: 'Municipal',
  consorcio: 'Consórcio intermunicipal',
  privado_conveniado: 'Privado conveniado',
};

/** Rótulo do princípio POUR. */
export const ROTULO_PRINCIPIO: Record<string, string> = {
  perceptivel: 'Perceptível',
  operavel: 'Operável',
  compreensivel: 'Compreensível',
  robusto: 'Robusto',
};

/** Rótulo do grupo de pessoas afetado pela barreira. */
export const ROTULO_GRUPO: Record<string, string> = {
  cegueira: 'Pessoas cegas (leitor de tela)',
  baixa_visao: 'Pessoas com baixa visão',
  visao_de_cores: 'Deficiência na visão de cores',
  surdez: 'Pessoas surdas',
  motora: 'Deficiência motora (sem mouse)',
  cognitiva_neurodivergencia: 'Deficiência intelectual / neurodivergência',
  fala: 'Usuários de comando por voz',
  fotossensibilidade: 'Epilepsia fotossensível',
  baixa_conectividade: 'Plano de dados limitado',
};

/** Rótulo da origem da verificação. */
export const ROTULO_ORIGEM: Record<string, string> = {
  'axe-core': 'axe-core',
  probe: 'sonda própria',
  heuristic: 'heurística',
  manual: 'avaliação humana',
};

/**
 * Interpreta um índice de conformidade em linguagem de gestor.
 *
 * As faixas são convenção de apresentação deste painel, e não classificação
 * normativa: a WCAG não gradua conformidade, ela é binária por critério. O
 * texto diz isso explicitamente para não induzir a leitura de que "78 é
 * aprovado".
 */
export function faixaDeConformidade(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return SEM_VEREDITO;
  if (valor >= 90) return 'poucas violações detectadas entre os critérios verificáveis';
  if (valor >= 70) return 'violações relevantes entre os critérios verificáveis';
  if (valor >= 40) return 'violações extensas entre os critérios verificáveis';
  return 'violações generalizadas entre os critérios verificáveis';
}

/** Interpreta o índice de atrito. */
export function faixaDeAtrito(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return SEM_VEREDITO;
  if (valor < 20) return 'atrito baixo';
  if (valor < 50) return 'atrito moderado';
  if (valor < 80) return 'atrito alto';
  return 'atrito muito alto';
}

/** Encurta uma URL para exibição, preservando o início e o fim do caminho. */
export function urlCurta(url: string, max = 60): string {
  if (url.length <= max) return url;
  const sem = url.replace(/^https?:\/\//, '');
  if (sem.length <= max) return sem;
  return `${sem.slice(0, max - 12)}…${sem.slice(-10)}`;
}
