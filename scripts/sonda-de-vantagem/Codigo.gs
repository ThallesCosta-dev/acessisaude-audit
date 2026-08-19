/**
 * Sonda de vantagem — controle de rede para a auditoria contínua
 * =============================================================
 *
 * NÃO é uma auditoria de acessibilidade. É um controle.
 *
 * A auditoria mede o documento renderizado por um navegador real, porque o
 * axe-core precisa de DOM e porque parte dos alvos é aplicação de página única
 * que serve casca vazia sem JavaScript. Esta sonda faz outra coisa, muito mais
 * simples: pergunta a cada endereço "você responde?" a partir de uma posição de
 * rede diferente da do coletor.
 *
 * POR QUE EXISTE
 * --------------
 * A coleta contínua roda em runner do GitHub, com IP de datacenter nos EUA. Em
 * quatro janelas consecutivas, o Meu SUS Digital devolveu HTTP 403 e duas
 * páginas da SES-RJ nunca carregaram — enquanto os mesmos endereços respondem
 * HTTP 200 de um IP residencial brasileiro.
 *
 * De um único ponto de observação é impossível separar duas explicações:
 *
 *   (a) o portal está indisponível;
 *   (b) o portal recusa aquele IP.
 *
 * A distinção não é técnica, é jurídica. (a) é barreira de disponibilidade, que
 * o artigo sustenta ser precondição da acessibilidade. (b) é artefato do
 * instrumento — a mesma classe de erro do User-Agent HeadlessChrome, registrada
 * no ADR 0008. Confundir as duas contamina o resultado.
 *
 * Com três posições — runner nos EUA, a máquina do pesquisador no Brasil, e o
 * Google via Apps Script — a divergência entre elas deixa de ser ruído e passa
 * a ser medida da política de rede do portal.
 *
 * O QUE ELA NÃO RESOLVE
 * ---------------------
 * O Apps Script executa de IPs do Google, majoritariamente nos EUA. Não
 * substitui um ponto de observação brasileiro: acrescenta um segundo ponto
 * estrangeiro, independente do primeiro. Se ambos falharem onde o IP brasileiro
 * tem sucesso, a hipótese (b) ganha força; se o Google tiver sucesso onde o
 * runner falha, a causa é específica daquele IP ou da renderização.
 *
 * CONDUTA DE COLETA
 * -----------------
 * Vale aqui a mesma conduta do restante do projeto: identificação no
 * User-Agent, intervalo entre requisições, e nenhuma tentativa de autenticação
 * ou de envio de dados. São requisições GET a páginas públicas.
 *
 * Implantação: ver README.md nesta pasta.
 */

// ---------------------------------------------------------------------------
// Configuração
// ---------------------------------------------------------------------------

/**
 * Identificação da pesquisa. Preencha antes de instalar o gatilho.
 *
 * Não é formalidade: um portal público precisa poder saber quem o acessa e a
 * quem reclamar. A sonda recusa executar enquanto o marcador estiver presente.
 */
var CONTATO = "AcessiSaude-Audit/0.1 (sonda de vantagem; +PREENCHA@SEU-EMAIL)";

/** Intervalo entre requisições, em milissegundos. */
var INTERVALO_MS = 2000;

/** Tempo máximo de espera por resposta, em milissegundos. */
var TIMEOUT_MS = 30000;

/**
 * Endereços observados.
 *
 * Espelham as sementes do catálogo do projeto. Se o catálogo mudar, este bloco
 * precisa mudar junto — a duplicação é deliberada, porque o Apps Script não tem
 * como ler o YAML do repositório, e uma sonda que observe endereços diferentes
 * dos auditados não serve de controle.
 */
var ALVOS = [
  ["conecte-sus-web",   "https://meususdigital.saude.gov.br/"],
  ["gov-br-saude",      "https://www.gov.br/saude/pt-br"],
  ["gov-br-saude",      "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z"],
  ["gov-br-saude",      "https://www.gov.br/saude/pt-br/composicao/saes"],
  ["ses-rj",            "https://www.rj.gov.br/saude/"],
  ["ses-rj",            "https://www.saude.rj.gov.br/ouvidoria/participe"],
  ["ses-rj",            "https://www.saude.rj.gov.br/laudos"],
  ["sms-rio",           "https://prefeitura.rio/saude/"],
  ["carioca-rio-saude", "https://carioca.rio/tema/saude/"],
  ["carioca-rio-saude", "https://carioca.rio/servicos/atendimento-em-unidades-de-pronto-atendimento-upa-24-horas/"]
];

var CABECALHO = [
  "observado_em", "alvo", "url", "status_http", "bytes", "duracao_ms",
  "url_final", "erro"
];

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

/**
 * Observa todos os alvos e grava uma linha por endereço.
 *
 * É a função que o gatilho temporal chama.
 */
function observar() {
  if (CONTATO.indexOf("PREENCHA") !== -1) {
    throw new Error(
      "Preencha a constante CONTATO com a identificacao da pesquisa antes de " +
      "executar. Coleta automatizada nao identificada e conduta que este " +
      "projeto recusa."
    );
  }

  var aba = _aba();
  var registros = [];

  for (var i = 0; i < ALVOS.length; i++) {
    if (i > 0) {
      Utilities.sleep(INTERVALO_MS);
    }
    registros.push(_observarUm(ALVOS[i][0], ALVOS[i][1]));
  }

  aba.getRange(aba.getLastRow() + 1, 1, registros.length, CABECALHO.length)
     .setValues(registros);

  Logger.log("Observados %s enderecos.", registros.length);
}

/**
 * Observa um endereço e devolve a linha correspondente.
 *
 * Uma falha de rede não interrompe a rodada: vira registro com a coluna erro
 * preenchida. Interromper produziria lacuna silenciosa na série — exatamente o
 * que o coletor evita ao tratar perda de página como dado, e não como
 * interrupção da coleta.
 */
function _observarUm(alvo, url) {
  var inicio = Date.now();
  var carimbo = new Date();

  try {
    var resposta = UrlFetchApp.fetch(url, {
      method: "get",
      headers: { "User-Agent": CONTATO },
      muteHttpExceptions: true,   // 4xx e 5xx sao DADO, nao excecao
      followRedirects: true,
      validateHttpsCertificates: true,
      timeout: TIMEOUT_MS
    });

    var duracao = Date.now() - inicio;
    var corpo = resposta.getContentText();

    return [
      carimbo, alvo, url, resposta.getResponseCode(), corpo.length, duracao, "", ""
    ];

  } catch (e) {
    return [
      carimbo, alvo, url, "", "", Date.now() - inicio, "", String(e).slice(0, 250)
    ];
  }
}

/** Devolve a aba de registro, criando-a com cabeçalho na primeira execução. */
function _aba() {
  var planilha = SpreadsheetApp.getActiveSpreadsheet();
  var aba = planilha.getSheetByName("observacoes");

  if (aba === null) {
    aba = planilha.insertSheet("observacoes");
    aba.getRange(1, 1, 1, CABECALHO.length).setValues([CABECALHO]).setFontWeight("bold");
    aba.setFrozenRows(1);
  }
  return aba;
}

// ---------------------------------------------------------------------------
// Gatilho
// ---------------------------------------------------------------------------

/**
 * Instala o gatilho temporal. Executar UMA vez, à mão.
 *
 * A cada 6 horas, e não em horários fixos, porque o Apps Script não permite
 * escolher o minuto — gatilhos horários disparam em janela aproximada. Para um
 * controle isso basta: o que importa é haver observação independente próxima de
 * cada janela do coletor, não coincidência exata.
 */
function instalarGatilho() {
  removerGatilhos();
  ScriptApp.newTrigger("observar").timeBased().everyHours(6).create();
  Logger.log("Gatilho instalado: a cada 6 horas.");
}

/** Remove todos os gatilhos deste projeto. */
function removerGatilhos() {
  var gatilhos = ScriptApp.getProjectTriggers();
  for (var i = 0; i < gatilhos.length; i++) {
    ScriptApp.deleteTrigger(gatilhos[i]);
  }
  Logger.log("Gatilhos removidos: %s", gatilhos.length);
}
