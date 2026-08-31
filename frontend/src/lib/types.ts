/**
 * Tipos do contrato com a API.
 *
 * Espelham os esquemas Pydantic de `backend/src/acessisaude_audit/api/schemas.py`.
 * A duplicação é consciente e limitada: os tipos ficam aqui, mas **nenhuma regra
 * de negócio é reimplementada em TypeScript**. Rótulos, teses jurídicas, risco
 * por critério e a matriz WCAG↔LBI vêm do endpoint `/referencia`, justamente
 * para que a matriz não exista em duas versões que divergem com o tempo.
 *
 * A referência normativa do contrato é o OpenAPI publicado em `/openapi.json`.
 */

/** Risco jurídico da violação, em ordem crescente de gravidade. */
export type RiscoJuridico = 'baixo' | 'moderado' | 'alto' | 'critico';

/** Gravidade técnica, na escala do axe-core. */
export type GravidadeTecnica = 'minor' | 'moderate' | 'serious' | 'critical';

/** Veredito de uma verificação, no vocabulário EARL do W3C. */
export type Veredito = 'pass' | 'fail' | 'incomplete' | 'inapplicable';

/** Origem da verificação. */
export type Origem = 'axe-core' | 'probe' | 'heuristic' | 'manual';

/** Esfera federativa responsável pelo serviço. */
export type Esfera =
  | 'federal'
  | 'estadual'
  | 'municipal'
  | 'consorcio'
  | 'privado_conveniado';

/** Envelope de paginação. */
export interface Pagina<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

/** Alvo do catálogo, na forma consumida pelo dashboard. */
export interface Alvo {
  id: string;
  name: string;
  organization: string;
  sphere: Esfera;
  categories: string[];
  base_url: string;
  territory: string;
  enabled: boolean;
  population_served: number | null;
  selection_rationale: string;
  /** Sementes efetivamente varríveis. */
  auditable_pages: number;
  /** Sementes excluídas por exigirem autenticação — lacunas declaradas. */
  declared_gaps: number;
  tags: string[];
}

/** Varredura em forma de resumo. */
export interface ResumoVarredura {
  id: string;
  target_id: string;
  target_name: string;
  sphere: string | null;
  status: string;
  started_at: string;
  finished_at: string | null;

  page_count: number;
  violation_count: number;
  occurrence_count: number;
  incomplete_count: number;
  loss_rate: number;

  /**
   * Nulos quando `observed` é falso: nenhuma página foi auditada, e não há
   * veredito. Distinto de conformidade e de não conformidade — a interface
   * precisa exibir traço, nunca zero nem cem.
   */
  observed: boolean;
  conformance_index: number | null;
  friction_index: number | null;
  legal_exposure_index: number | null;
  absolute_barrier: boolean | null;
  coverage: number;

  mean_page_mb: number;
  mean_cost_brl: number;

  engine_version: string;
  axe_version: string | null;
}

/** Elemento do DOM em que a falha foi observada — a prova material do achado. */
export interface NoDeEvidencia {
  selector: string;
  html: string;
  failure_summary: string;
  measured: Record<string, unknown>;
}

/** Um achado de auditoria, com suas três camadas. */
export interface Achado {
  id: string;
  rule_id: string;
  source: Origem;
  outcome: Veredito;
  impact: GravidadeTecnica | null;
  criteria: string[];
  summary: string;
  description: string;
  remediation: string;
  help_url: string | null;
  affects: string[];
  nodes: NoDeEvidencia[];
  page_url: string;
  viewport: string;
  occurrences: number;
  legal_risk: RiscoJuridico | null;
  legal_provisions: string[];
  legal_thesis: string | null;
}

/** Métricas de rede — a dimensão do usuário periférico. */
export interface MetricasDeRede {
  total_bytes: number;
  request_count: number;
  bytes_by_type: Record<string, number>;
  third_party_bytes: number;
  third_party_domains: string[];
  total_mb: number;
  third_party_share: number;
  largest_contentful_paint_ms: number | null;
}

/** Resultado da auditoria de uma página em um viewport. */
export interface AuditoriaDePagina {
  url: string;
  final_url: string;
  status: string;
  http_status: number | null;
  title: string | null;
  lang: string | null;
  viewport: { name: string; width: number; height: number; is_mobile: boolean };
  findings: Achado[];
  network: MetricasDeRede;
  error: string | null;
  is_critical_path: boolean;
}

/** Varredura completa — o artefato primário de pesquisa. */
export interface Varredura {
  id: string;
  schema_version: string;
  target_id: string;
  target_name: string;
  base_url: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  pages: AuditoriaDePagina[];
  engine_version: string;
  axe_version: string | null;
  browser: string;
  config_snapshot: Record<string, unknown>;
  errors: string[];
  page_count: number;
  violation_count: number;
  occurrence_count: number;
}

/** Índices agregados de uma varredura. */
export interface Indices {
  /**
   * Nulos quando `observed` é falso: nenhuma página foi auditada, e não há
   * veredito. Distinto de conformidade e de não conformidade — a interface
   * precisa exibir traço, nunca zero nem cem.
   */
  observed: boolean;
  conformance_index: number | null;
  friction_index: number | null;
  legal_exposure_index: number | null;
  absolute_barrier: boolean | null;
  coverage: number;
  criteria_evaluated: number;
  criteria_violated: number;
  violations: number;
  occurrences: number;
  incomplete: number;
  violations_by_impact: Record<string, number>;
  violations_by_legal_risk: Record<string, number>;
  violations_by_principle: Record<string, number>;
  violations_by_level: Record<string, number>;
  excluded_groups: Record<string, number>;
  violated_criteria: string[];
  data_cost: {
    total_mb: number;
    cost_brl: number;
    franchise_share_pct: number;
    third_party_share_pct: number;
    is_heavy: boolean;
    monthly_cost_brl_at_4_visits: number;
  } | null;
}

/**
 * Resposta de `/varreduras/{id}/indices`.
 *
 * `parametros` acompanha sempre os índices: nenhum número deste projeto deve
 * circular dissociado das constantes que o produziram.
 */
export interface RespostaIndices {
  indices: Indices;
  grupos_excluidos: Array<{ grupo: string; ocorrencias: number }>;
  parametros: Record<string, number>;
  taxa_de_perda: number;
  lacunas_declaradas: Array<{ url: string; label: string; motivo: string }>;
}

/** Critério WCAG com seu vínculo jurídico. */
export interface Criterio {
  id: string;
  title_pt: string;
  title_en: string;
  level: 'A' | 'AA' | 'AAA';
  principle: string;
  rationale: string;
  automatable: boolean;
  affects: string[];
  url: string;
  legal_risk: RiscoJuridico | null;
  legal_thesis: string | null;
  remediation: string | null;
  provisions: string[];
}

/** Dispositivo normativo brasileiro. */
export interface Dispositivo {
  key: string;
  source: string;
  label: string;
  summary: string;
  strength: string;
  addressee: string;
  citation: string;
  url: string;
  routes: string[];
}

/** Estado de um trabalho de varredura em segundo plano. */
export interface Trabalho {
  id: string;
  target_id: string;
  status: 'pendente' | 'executando' | 'concluida' | 'falhou' | 'cancelada';
  concluidas: number;
  total: number;
  url_corrente: string | null;
  scan_id: string | null;
  erro: string | null;
}
