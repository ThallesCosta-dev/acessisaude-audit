/**
 * Cliente HTTP da API.
 *
 * Deliberadamente sem biblioteca de dados (React Query, SWR): o painel faz
 * poucas requisições, todas disparadas por navegação explícita, e a camada de
 * cache traria complexidade sem benefício. `useRecurso` cobre o caso e mantém a
 * superfície pequena o bastante para ser lida inteira.
 *
 * Erro de rede é tratado como estado de primeira classe, não como exceção
 * silenciosa: `useRecurso` devolve `erro`, e cada tela é obrigada a renderizá-lo
 * em uma região `role="alert"`. Um painel que falha em branco é, para o usuário
 * de leitor de tela, indistinguível de um painel vazio.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type {
  Alvo,
  Criterio,
  Dispositivo,
  Pagina,
  RespostaIndices,
  ResumoVarredura,
  Trabalho,
  Varredura,
} from './types';

/** Prefixo da API. Em desenvolvimento, o proxy do Vite reescreve para o backend. */
const BASE = '/api';

/** Erro de API com o código HTTP preservado, para tratamento diferenciado. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly detail?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
      ...init,
    });
  } catch (cause) {
    throw new ApiError(
      'Não foi possível contactar o servidor. Verifique se a API está em execução ' +
        '(acessisaude servir).',
      0,
      String(cause),
    );
  }

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail;
    } catch {
      detail = undefined;
    }
    throw new ApiError(
      detail ?? `A requisição falhou com código ${response.status}.`,
      response.status,
      detail,
    );
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  /** Estado do serviço e das dependências que a coleta exige. */
  saude: () =>
    request<{
      status: string;
      versao: string;
      axe_core_disponivel: boolean;
      navegador: string;
      respeita_robots_txt: boolean;
    }>('/saude'),

  /** Catálogo de alvos — o desenho amostral do estudo. */
  alvos: (apenasHabilitados = false) =>
    request<Alvo[]>(`/alvos${apenasHabilitados ? '?apenas_habilitados=true' : ''}`),

  alvo: (id: string) => request<Alvo>(`/alvos/${encodeURIComponent(id)}`),

  /** Sementes do alvo, separando auditáveis de lacunas declaradas. */
  paginasDoAlvo: (id: string) =>
    request<{
      auditaveis: Array<{ url: string; label: string; fluxo_essencial: boolean }>;
      lacunas_declaradas: Array<{ url: string; label: string; motivo: string }>;
    }>(`/alvos/${encodeURIComponent(id)}/paginas`),

  varreduras: (params: { targetId?: string; limit?: number; offset?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.targetId) q.set('target_id', params.targetId);
    q.set('limit', String(params.limit ?? 50));
    q.set('offset', String(params.offset ?? 0));
    return request<Pagina<ResumoVarredura>>(`/varreduras?${q}`);
  },

  varredura: (id: string) => request<Varredura>(`/varreduras/${encodeURIComponent(id)}`),

  indices: (id: string) =>
    request<RespostaIndices>(`/varreduras/${encodeURIComponent(id)}/indices`),

  /** URL do relatório HTML estático — abre fora do painel, sem JavaScript. */
  urlRelatorio: (id: string) => `${BASE}/varreduras/${encodeURIComponent(id)}/relatorio`,

  urlCsv: (id: string) => `${BASE}/varreduras/${encodeURIComponent(id)}/achados.csv`,

  iniciarVarredura: (targetId: string, discover = false) =>
    request<{ job_id: string; status: string; alvo: string }>('/varreduras', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_id: targetId, discover }),
    }),

  trabalho: (jobId: string) =>
    request<Trabalho>(`/varreduras/trabalhos/${encodeURIComponent(jobId)}`),

  /** Frequência de critérios violados em todas as varreduras. */
  frequenciaDeCriterios: () =>
    request<
      Array<{
        criterio: string;
        titulo: string | null;
        nivel?: string;
        principio?: string;
        achados: number;
      }>
    >('/varreduras/agregados/criterios'),

  criterios: (apenasAutomatizaveis = false) =>
    request<Criterio[]>(
      `/referencia/criterios${apenasAutomatizaveis ? '?apenas_automatizaveis=true' : ''}`,
    ),

  dispositivos: () => request<Dispositivo[]>('/referencia/dispositivos'),

  integridadeDaMatriz: () =>
    request<{
      criterios_no_escopo: number;
      criterios_sem_mapeamento: string[];
      matriz_completa: boolean;
      dispositivos_registrados: number;
    }>('/referencia/integridade-da-matriz'),
};

/** Estado de um recurso remoto. */
export interface EstadoRecurso<T> {
  dados: T | null;
  carregando: boolean;
  erro: ApiError | null;
  recarregar: () => void;
}

/**
 * Carrega um recurso da API, expondo carregamento e erro como estados explícitos.
 *
 * Cancelamento: uma requisição cuja tela já foi desmontada não atualiza estado.
 * Sem isso, navegar rapidamente entre varreduras faria a resposta antiga
 * sobrescrever a nova — o usuário veria dados de outra varredura sob o título
 * correto, que é pior do que não ver nada.
 *
 * @param carregar Função que busca o recurso.
 * @param deps Dependências que disparam nova busca.
 */
export function useRecurso<T>(
  carregar: () => Promise<T>,
  deps: readonly unknown[],
): EstadoRecurso<T> {
  const [dados, setDados] = useState<T | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<ApiError | null>(null);
  const [gatilho, setGatilho] = useState(0);
  const geracao = useRef(0);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const carregarMemo = useCallback(carregar, deps);

  useEffect(() => {
    const atual = ++geracao.current;
    setCarregando(true);
    setErro(null);

    carregarMemo()
      .then((resultado) => {
        if (geracao.current === atual) {
          setDados(resultado);
          setCarregando(false);
        }
      })
      .catch((causa: unknown) => {
        if (geracao.current !== atual) return;
        setErro(
          causa instanceof ApiError
            ? causa
            : new ApiError('Erro inesperado ao carregar os dados.', 0, String(causa)),
        );
        setCarregando(false);
      });
  }, [carregarMemo, gatilho]);

  const recarregar = useCallback(() => setGatilho((n) => n + 1), []);
  return { dados, carregando, erro, recarregar };
}
