"""Matriz de correspondência WCAG 2.1 ↔ ordenamento jurídico brasileiro.

Este é o módulo que sustenta a tese interdisciplinar do projeto: converter um
achado técnico ("contraste 2.9:1 no botão de agendamento") em uma proposição
jurídica ("violação do art. 63, caput, da LBI c/c art. 47 do Decreto 5.296/2004,
exigível pela via da ação civil pública").

Arquitetura da matriz
---------------------
A vinculação se dá em duas camadas:

1. **Camada geral** (:data:`BASE_PROVISIONS`) — dispositivos que incidem sobre
   *qualquer* falha de acessibilidade em sítio de órgão público de saúde. A
   incidência decorre do próprio art. 63, caput, da LBI, que não distingue entre
   tipos de barreira.
2. **Camada específica** (:data:`CRITERION_MAPPINGS`) — dispositivos adicionais
   que só incidem quando o critério violado tem natureza particular (ex.: falhas
   de legenda acionam o Decreto 5.626/2005, sobre Libras).

Essa separação evita o vício metodológico mais comum em trabalhos da área:
citar o mesmo bloco de leis para toda e qualquer falha, o que dilui a força
argumentativa e impede graduar a gravidade.

Rastreabilidade
---------------
Cada :class:`CriterionMapping` carrega uma ``thesis`` — a proposição jurídica em
uma frase — e uma ``legal_risk``. A tese é o que aparece no relatório entregue ao
gestor e o que alimenta a seção de Resultados do artigo. Ver
``docs/juridico/matriz-wcag-lbi.md`` para a versão discursiva e revisável desta
mesma matriz.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from functools import cache

from acessisaude_audit.domain.lbi import LegalProvision, provision
from acessisaude_audit.domain.wcag import WCAG_CRITERIA, SuccessCriterion, criterion

__all__ = [
    "BASE_PROVISIONS",
    "CRITERION_MAPPINGS",
    "CriterionMapping",
    "LegalRisk",
    "mapping_for",
    "provisions_for",
    "unmapped_criteria",
]


class LegalRisk(StrEnum):
    """Gravidade jurídica da violação, graduada por três vetores combinados.

    Os vetores são: (i) essencialidade do serviço obstruído; (ii) existência ou
    não de rota alternativa acessível; (iii) reversibilidade do dano. A escala
    **não** é a mesma do ``impact`` do axe-core, que mede gravidade técnica —
    são dimensões independentes e ambas são reportadas.
    """

    BAIXO = "baixo"
    """Dificulta o uso, mas não impede a conclusão da tarefa por rota alternativa."""

    MODERADO = "moderado"
    """Exige esforço desproporcional ou auxílio de terceiro, ferindo a autonomia
    protegida pelo art. 3º, I da LBI."""

    ALTO = "alto"
    """Impede a conclusão da tarefa por parte de um grupo identificável."""

    CRITICO = "critico"
    """Impede o acesso a serviço de saúde essencial, com risco de dano à saúde ou
    perda de prazo/vaga não recuperável."""

    @property
    def weight(self) -> float:
        """Peso usado nos índices agregados de :mod:`~acessisaude_audit.domain.scoring`."""
        return {
            LegalRisk.BAIXO: 1.0,
            LegalRisk.MODERADO: 3.0,
            LegalRisk.ALTO: 7.0,
            LegalRisk.CRITICO: 12.0,
        }[self]


#: Dispositivos que incidem sobre qualquer barreira digital em portal público de saúde.
BASE_PROVISIONS: tuple[str, ...] = (
    "lbi.art63.caput",
    "lbi.art3.iv.d",
    "lbi.art4",
    "dec5296.art47",
    "emag.3.1",
)

#: Dispositivos acrescidos quando o portal é de saúde (todos os alvos deste projeto).
HEALTH_PROVISIONS: tuple[str, ...] = (
    "lbi.art18",
    "cf.art196",
    "onu.art25",
)


@dataclass(frozen=True, slots=True)
class CriterionMapping:
    """Vinculação de um critério WCAG a dispositivos normativos.

    Attributes:
        criterion_id: Critério WCAG 2.1, ex. ``"1.4.3"``.
        extra_provisions: Chaves de dispositivos que se somam a
            :data:`BASE_PROVISIONS` e :data:`HEALTH_PROVISIONS`.
        legal_risk: Gravidade jurídica presumida da violação deste critério em
            um portal público de saúde. É um *default* — o motor pode elevá-la
            quando a falha ocorre em página de fluxo crítico (ver
            ``catalog/targets.yaml``, campo ``critical_paths``).
        thesis: A proposição jurídica, em uma frase, ligando falha e norma.
        remediation: Conduta corretiva esperada do gestor, em linguagem de ação.
    """

    criterion_id: str
    legal_risk: LegalRisk
    thesis: str
    remediation: str
    extra_provisions: tuple[str, ...] = field(default_factory=tuple)

    @property
    def criterion(self) -> SuccessCriterion:
        """O critério WCAG correspondente."""
        return criterion(self.criterion_id)

    @property
    def provision_keys(self) -> tuple[str, ...]:
        """Todas as chaves de dispositivos aplicáveis, sem duplicatas e em ordem."""
        seen: dict[str, None] = {}
        for key in (*BASE_PROVISIONS, *HEALTH_PROVISIONS, *self.extra_provisions):
            seen.setdefault(key, None)
        return tuple(seen)

    @property
    def provisions(self) -> tuple[LegalProvision, ...]:
        """Os dispositivos aplicáveis já resolvidos."""
        return tuple(provision(k) for k in self.provision_keys)


def _m(
    criterion_id: str,
    legal_risk: LegalRisk,
    thesis: str,
    remediation: str,
    extra: tuple[str, ...] = (),
) -> CriterionMapping:
    return CriterionMapping(
        criterion_id=criterion_id,
        legal_risk=legal_risk,
        thesis=thesis,
        remediation=remediation,
        extra_provisions=extra,
    )


_BAIXO = LegalRisk.BAIXO
_MOD = LegalRisk.MODERADO
_ALTO = LegalRisk.ALTO
_CRIT = LegalRisk.CRITICO

_TA = ("lbi.art74",)  # tecnologia assistiva
_INFO = ("cf.art5.xiv", "lai.art8.par3.viii")  # acesso à informação
_LIBRAS = ("dec5626.art26",)
_USUARIO = ("lei13460.art5",)
_AUTONOMIA = ("lbi.art3.i",)
_PRIORIDADE = ("lbi.art9.v",)


#: Matriz completa: um mapeamento por critério WCAG 2.1 A/AA.
CRITERION_MAPPINGS: tuple[CriterionMapping, ...] = (
    # ------------------------------------------------------------- Perceptível
    _m(
        "1.1.1",
        _ALTO,
        "A ausência de alternativa textual configura barreira na comunicação e na "
        "informação (art. 3º, IV, 'd', LBI): o conteúdo existe juridicamente como "
        "informação pública, mas não é recebível pelo usuário cego, esvaziando o "
        "dever de transparência ativa do art. 8º, § 3º, VIII da LAI.",
        "Prover atributo alt descritivo em imagens informativas e alt vazio em "
        "imagens decorativas; descrever gráficos e infográficos em texto adjacente.",
        _TA + _INFO,
    ),
    _m(
        "1.2.1",
        _MOD,
        "Conteúdo audiovisual sem alternativa acessível descumpre o dever de oferta "
        "de comunicação e informação adequadas do art. 18, § 4º da LBI.",
        "Publicar transcrição textual completa junto ao player.",
        _LIBRAS + _INFO,
    ),
    _m(
        "1.2.2",
        _ALTO,
        "Vídeo de orientação em saúde sem legenda nega à pessoa surda o acesso à "
        "informação sanitária, violando o art. 26 do Decreto 5.626/2005 e o direito "
        "à atenção integral do art. 18 da LBI.",
        "Adicionar legendas sincronizadas (não automáticas) e, quando o conteúdo "
        "for orientação clínica, janela de Libras.",
        _LIBRAS,
    ),
    _m(
        "1.2.3",
        _MOD,
        "A informação transmitida apenas por canal visual não alcança o usuário "
        "cego, contrariando o art. 63, caput, da LBI.",
        "Fornecer audiodescrição ou alternativa textual equivalente ao conteúdo visual.",
        _TA,
    ),
    _m(
        "1.2.4",
        _ALTO,
        "Transmissões ao vivo de conteúdo sanitário sem legenda em tempo real "
        "excluem a pessoa surda em contexto de urgência informacional — hipótese "
        "agravada de discriminação por omissão (art. 4º, § 1º, LBI).",
        "Contratar legendagem em tempo real (CART) para transmissões oficiais.",
        _LIBRAS,
    ),
    _m(
        "1.2.5",
        _MOD,
        "Reforça o dever do art. 63 quanto à equivalência da informação em canal não visual.",
        "Produzir faixa de audiodescrição para o conteúdo pré-gravado.",
        _TA,
    ),
    _m(
        "1.3.1",
        _ALTO,
        "Sem estrutura semântica, a tecnologia assistiva não consegue reconstruir a "
        "relação entre rótulo e dado; o art. 74 da LBI assegura o acesso a "
        "tecnologias assistivas, o que pressupõe conteúdo com elas compatível.",
        "Usar HTML semântico (label/for, th/scope, fieldset/legend, listas e "
        "cabeçalhos reais) em lugar de formatação puramente visual.",
        _TA,
    ),
    _m(
        "1.3.2",
        _MOD,
        "Sequência de leitura incoerente compromete a compreensão autônoma do "
        "serviço, ferindo o conceito legal de acessibilidade do art. 3º, I da LBI.",
        "Garantir que a ordem no DOM corresponda à ordem visual de leitura.",
        _AUTONOMIA,
    ),
    _m(
        "1.3.3",
        _MOD,
        "Instruções dependentes de percepção sensorial específica presumem um "
        "usuário-padrão, prática vedada pelo art. 4º da LBI.",
        "Reescrever instruções combinando referência textual e posicional "
        "(ex.: 'no botão Confirmar, ao final do formulário').",
    ),
    _m(
        "1.3.4",
        _MOD,
        "O travamento de orientação de tela desconsidera usuários com aparelho "
        "fixado a suporte ou cadeira, restringindo o uso com autonomia (art. 3º, I).",
        "Remover restrições de orientação, salvo quando essencial e justificado.",
        _AUTONOMIA,
    ),
    _m(
        "1.3.5",
        _BAIXO,
        "A ausência de identificação de propósito de campo aumenta o custo de uso "
        "sem impedi-lo; incide o dever de adequação do art. 5º da Lei 13.460/2017.",
        "Declarar atributos autocomplete nos campos de identificação pessoal.",
        _USUARIO,
    ),
    _m(
        "1.4.1",
        _ALTO,
        "Informação veiculada exclusivamente por cor é inacessível a pessoas com "
        "deficiência na visão de cores; quando indica status de consulta ou exame, "
        "a omissão compromete o direito à informação em saúde (art. 18, LBI).",
        "Acrescentar rótulo textual, ícone ou padrão gráfico redundante à cor.",
        _INFO,
    ),
    _m(
        "1.4.2",
        _MOD,
        "Áudio automático interfere na tecnologia assistiva, obstruindo o acesso "
        "garantido pelo art. 74 da LBI.",
        "Não iniciar áudio automaticamente; se necessário, oferecer controle de "
        "pausa imediatamente acessível por teclado.",
        _TA,
    ),
    _m(
        "1.4.3",
        _ALTO,
        "O contraste insuficiente é a barreira de comunicação mais prevalente e "
        "atinge diretamente a população idosa usuária do SUS; sua persistência em "
        "portal público caracteriza descumprimento continuado do art. 63, caput, "
        "da LBI e do art. 47 do Decreto 5.296/2004.",
        "Ajustar a paleta para razão mínima de 4.5:1 (texto normal) e 3:1 (texto "
        "grande), validando os tokens de design, não apenas as telas.",
        _INFO,
    ),
    _m(
        "1.4.4",
        _ALTO,
        "O bloqueio de ampliação nega adaptação razoável, conduta equiparada a "
        "discriminação pelo art. 4º, § 1º da LBI.",
        "Usar unidades relativas e remover 'user-scalable=no' da meta viewport.",
    ),
    _m(
        "1.4.5",
        _MOD,
        "Texto embutido em imagem é simultaneamente inacessível à tecnologia "
        "assistiva e oneroso em dados móveis, somando barreira de comunicação e "
        "barreira socioeconômica de acesso.",
        "Substituir cartazes em imagem por texto HTML estilizado; reservar imagem "
        "de texto apenas para logotipos.",
        _TA + _INFO,
    ),
    _m(
        "1.4.10",
        _ALTO,
        "O acesso majoritário aos serviços públicos de saúde no Brasil se dá por "
        "telefone celular; a exigência de rolagem bidirecional em telas estreitas "
        "inviabiliza o uso e frustra o acesso universal do art. 196 da CF/88.",
        "Adotar layout responsivo que preserve conteúdo e função em viewport de "
        "320 CSS px sem rolagem horizontal.",
        _USUARIO,
    ),
    _m(
        "1.4.11",
        _MOD,
        "Controles sem contraste suficiente são imperceptíveis para baixa visão, "
        "barreira vedada pelo art. 3º, IV, 'd' da LBI.",
        "Garantir 3:1 entre componentes de interface/indicadores gráficos e o fundo.",
    ),
    _m(
        "1.4.12",
        _BAIXO,
        "Impedir o ajuste tipográfico bloqueia adaptação individual, contrariando "
        "o princípio do desenho universal (art. 3º, II, LBI).",
        "Evitar alturas fixas e '!important' que impeçam sobrescrita de espaçamento.",
    ),
    _m(
        "1.4.13",
        _MOD,
        "Conteúdo que desaparece impede a leitura por quem usa ampliação, "
        "restringindo o uso com segurança e autonomia (art. 3º, I, LBI).",
        "Tornar o conteúdo sobreposto dispensável por Esc, apontável e persistente.",
        _AUTONOMIA,
    ),
    # ---------------------------------------------------------------- Operável
    _m(
        "2.1.1",
        _CRIT,
        "A impossibilidade de operar o serviço por teclado exclui integralmente "
        "usuários com deficiência motora e usuários de leitor de tela: não há rota "
        "alternativa. Configura barreira absoluta e violação frontal do art. 63, "
        "caput, da LBI c/c art. 9 da Convenção da ONU (status constitucional).",
        "Assegurar que todo controle seja alcançável e acionável por teclado, "
        "preferindo elementos nativos (button, a, input) a divs com handler.",
        (*_TA, "onu.art9"),
    ),
    _m(
        "2.1.2",
        _CRIT,
        "A armadilha de foco aprisiona o usuário e impede tanto concluir quanto "
        "abandonar a tarefa — impedimento total de acesso ao serviço de saúde.",
        "Implementar gestão de foco em modais com retorno ao elemento de origem e "
        "fechamento por Esc.",
        _TA,
    ),
    _m(
        "2.1.4",
        _BAIXO,
        "Atalhos de tecla única geram acionamento acidental em usuários de "
        "reconhecimento de voz; incide o dever de adequação do serviço público.",
        "Permitir desativar ou remapear atalhos de caractere único.",
        _USUARIO,
    ),
    _m(
        "2.2.1",
        _ALTO,
        "Prazos de sessão não ajustáveis penalizam quem opera mais lentamente por "
        "deficiência ou por conexão precária, produzindo discriminação indireta "
        "(art. 4º, § 1º, LBI).",
        "Oferecer aviso e extensão de sessão; ampliar o tempo-limite em fluxos de "
        "agendamento e preenchimento longo.",
        _PRIORIDADE,
    ),
    _m(
        "2.2.2",
        _MOD,
        "Movimento automático não interrompível compete com a leitura e consome "
        "dados móveis, combinando barreira cognitiva e socioeconômica.",
        "Prover controle de pausa/parada para carrosséis, animações e atualizações "
        "automáticas com duração superior a cinco segundos.",
    ),
    _m(
        "2.3.1",
        _CRIT,
        "Conteúdo intermitente acima do limiar pode desencadear crise epiléptica: "
        "o dano é à integridade física, e não apenas ao acesso, elevando o dever de "
        "cuidado do art. 8º da LBI.",
        "Eliminar conteúdo que pisque mais de três vezes por segundo.",
    ),
    _m(
        "2.4.1",
        _MOD,
        "A ausência de mecanismo de salto obriga a percorrer repetidamente blocos "
        "idênticos, esforço desproporcional vedado pelo conceito de acessibilidade "
        "com autonomia do art. 3º, I da LBI.",
        "Incluir link 'pular para o conteúdo principal' e marcos ARIA (landmarks).",
        _AUTONOMIA,
    ),
    _m(
        "2.4.2",
        _BAIXO,
        "Título ausente ou genérico degrada a orientação do usuário, ferindo o "
        "dever de adequação do art. 5º da Lei 13.460/2017.",
        "Definir title único e descritivo por página, do específico ao geral.",
        _USUARIO,
    ),
    _m(
        "2.4.3",
        _ALTO,
        "Ordem de foco incoerente induz erro na submissão de dados de saúde, com "
        "risco de agendamento equivocado — dano ao acesso ao serviço.",
        "Alinhar a ordem de tabulação à ordem visual; evitar tabindex positivo.",
    ),
    _m(
        "2.4.4",
        _MOD,
        "Links sem finalidade discernível fora de contexto impedem a navegação "
        "eficiente por tecnologia assistiva (art. 74, LBI).",
        "Reescrever textos de link para que descrevam o destino sem depender do "
        "parágrafo circundante.",
        _TA,
    ),
    _m(
        "2.4.5",
        _BAIXO,
        "A existência de uma única rota de localização de conteúdo aumenta o custo "
        "de acesso ao serviço público (art. 5º, Lei 13.460/2017).",
        "Oferecer ao menos dois mecanismos: busca interna e mapa do site ou índice.",
        _USUARIO,
    ),
    _m(
        "2.4.6",
        _ALTO,
        "Cabeçalhos e rótulos não descritivos inutilizam o principal mecanismo de "
        "navegação de usuários de leitor de tela, obstruindo o acesso à informação.",
        "Escrever cabeçalhos que descrevam o conteúdo da seção e rótulos que "
        "descrevam o dado solicitado.",
        _TA + _INFO,
    ),
    _m(
        "2.4.7",
        _ALTO,
        "A supressão do indicador de foco cega o usuário de teclado quanto à sua "
        "posição, impedindo o uso com segurança (art. 3º, I, LBI).",
        "Manter indicador de foco visível com contraste mínimo de 3:1; nunca usar "
        "'outline: none' sem substituto equivalente.",
        _AUTONOMIA,
    ),
    _m(
        "2.5.1",
        _MOD,
        "Gestos complexos pressupõem destreza específica, excluindo pessoas com "
        "limitação motora sem adaptação razoável.",
        "Prover alternativa de ponteiro simples para toda função baseada em gesto.",
    ),
    _m(
        "2.5.2",
        _MOD,
        "A ação irrevogável no toque inicial impede desfazer acionamento acidental, "
        "relevante em fluxos de cancelamento de consulta.",
        "Disparar ações no evento de soltura (up) e permitir aborto do gesto.",
    ),
    _m(
        "2.5.3",
        _MOD,
        "A divergência entre nome acessível e rótulo visível quebra o comando por "
        "voz, tecnologia assistiva protegida pelo art. 74 da LBI.",
        "Garantir que o nome acessível contenha o texto visível do controle.",
        _TA,
    ),
    _m(
        "2.5.4",
        _BAIXO,
        "Funções acionadas por movimento do dispositivo excluem usuários que o "
        "mantêm fixo, sem alternativa equivalente.",
        "Oferecer controle na interface para toda função por movimento e permitir desativá-la.",
    ),
    # ----------------------------------------------------------- Compreensível
    _m(
        "3.1.1",
        _ALTO,
        "Sem declaração de idioma, o sintetizador de voz pronuncia o português com "
        "fonética estrangeira e a informação em saúde se torna ininteligível — a "
        "informação é publicada, mas não é comunicada (art. 3º, IV, 'd', LBI).",
        "Declarar lang='pt-BR' no elemento html de todas as páginas.",
        _TA + _INFO,
    ),
    _m(
        "3.1.2",
        _BAIXO,
        "Trechos em idioma estrangeiro sem marcação degradam a síntese de voz de forma pontual.",
        "Marcar com atributo lang os trechos em outro idioma.",
        _TA,
    ),
    _m(
        "3.2.1",
        _MOD,
        "Mudança de contexto ao receber foco desorienta o usuário de teclado, "
        "comprometendo o uso com segurança (art. 3º, I, LBI).",
        "Não disparar navegação ou submissão no evento de foco.",
        _AUTONOMIA,
    ),
    _m(
        "3.2.2",
        _ALTO,
        "A submissão automática ao alterar um campo impede a revisão de dados de "
        "saúde antes do envio, com risco de agendamento incorreto.",
        "Exigir ação explícita de confirmação para mudanças de contexto.",
    ),
    _m(
        "3.2.3",
        _BAIXO,
        "A inconsistência de navegação entre páginas do mesmo portal eleva a carga "
        "cognitiva e o tempo de atendimento.",
        "Padronizar posição e ordem dos mecanismos de navegação repetidos.",
        _USUARIO,
    ),
    _m(
        "3.2.4",
        _MOD,
        "Componentes com mesma função identificados de modo distinto induzem erro "
        "em fluxo assistencial.",
        "Padronizar rótulos, ícones e nomes acessíveis de componentes equivalentes.",
    ),
    _m(
        "3.3.1",
        _ALTO,
        "Erro não identificado de forma programática impede a conclusão do "
        "cadastro ou agendamento por usuário de leitor de tela: a tarefa falha em "
        "silêncio, o que equivale à negativa de atendimento.",
        "Identificar o erro em texto, associá-lo ao campo (aria-describedby) e "
        "anunciá-lo em região aria-live.",
        _TA + _PRIORIDADE,
    ),
    _m(
        "3.3.2",
        _ALTO,
        "Campo sem rótulo programático torna indeterminável o dado solicitado, "
        "inviabilizando o preenchimento autônomo (art. 3º, I, LBI).",
        "Associar label a todo campo; placeholder não substitui rótulo.",
        _TA + _AUTONOMIA,
    ),
    _m(
        "3.3.3",
        _MOD,
        "Informar o erro sem indicar a correção prolonga indefinidamente a "
        "tentativa de acesso ao serviço.",
        "Descrever o formato esperado e sugerir a correção quando conhecida.",
        _USUARIO,
    ),
    _m(
        "3.3.4",
        _ALTO,
        "Ações irreversíveis sobre agendamento ou dados de saúde sem confirmação "
        "podem gerar perda de vaga não recuperável, dano concreto ao acesso à "
        "saúde (art. 196, CF/88).",
        "Prover confirmação, revisão ou reversibilidade em ações críticas.",
        _PRIORIDADE,
    ),
    # ------------------------------------------------------------------ Robusto
    _m(
        "4.1.1",
        _BAIXO,
        "Marcação malformada produz comportamento imprevisível em tecnologia "
        "assistiva, comprometendo a interoperabilidade pressuposta pelo art. 74.",
        "Eliminar IDs duplicados e aninhamento inválido; validar o HTML no build.",
        _TA,
    ),
    _m(
        "4.1.2",
        _CRIT,
        "Controle sem nome, função ou valor expostos simplesmente não existe para "
        "a tecnologia assistiva: o serviço é, para o usuário cego, inexistente. "
        "É a forma mais severa de barreira na informação do art. 3º, IV, 'd'.",
        "Usar elementos nativos ou, quando inevitável, ARIA completo (role, nome "
        "acessível, estado) com teclado equivalente.",
        (*_TA, "onu.art9"),
    ),
    _m(
        "4.1.3",
        _ALTO,
        "Confirmações e alertas não anunciados fazem o usuário desconhecer o "
        "resultado da própria solicitação de consulta ou exame.",
        "Publicar mensagens de status em regiões aria-live com papel adequado "
        "(status, alert) sem mover o foco.",
        _TA,
    ),
)


@cache
def _index() -> dict[str, CriterionMapping]:
    return {m.criterion_id: m for m in CRITERION_MAPPINGS}


def mapping_for(criterion_id: str) -> CriterionMapping | None:
    """Mapeamento jurídico do critério, ou ``None`` se ainda não modelado."""
    return _index().get(criterion_id)


def provisions_for(criterion_id: str) -> tuple[LegalProvision, ...]:
    """Dispositivos normativos aplicáveis à violação de um critério.

    Retorna tupla vazia se o critério não tiver mapeamento — situação que
    :func:`unmapped_criteria` permite detectar em teste de completude.
    """
    m = mapping_for(criterion_id)
    return m.provisions if m else ()


def unmapped_criteria() -> tuple[str, ...]:
    """Critérios WCAG A/AA sem mapeamento jurídico correspondente.

    Usado pelo teste de completude da matriz (``tests/unit/test_mapping.py``):
    a suíte falha se qualquer critério do escopo ficar órfão, impedindo que a
    ferramenta reporte falhas tecnicamente detectadas mas juridicamente mudas.
    """
    idx = _index()
    return tuple(c.id for c in WCAG_CRITERIA if c.id not in idx)
