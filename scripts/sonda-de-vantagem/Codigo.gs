/**
 * Sonda de vantagem — controle de rede para a auditoria contínua
 * =============================================================
 *
 * NÃO é uma auditoria de acessibilidade. É um controle.
 *
 * A auditoria mede o documento renderizado por um navegador real, porque o
 * axe-core precisa da árvore de acessibilidade, das cores computadas depois da
 * cascata de CSS e do layout em largura declarada. Nada disso existe no HTML
 * servido. Esta sonda faz outra coisa, muito mais simples: pergunta a cada
 * endereço "você responde?" a partir de uma posição de rede diferente da do
 * coletor.
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
 * O QUE ELA NÃO RESOLVE
 * ---------------------
 * O Apps Script executa de IPs do Google, majoritariamente nos EUA. Não
 * substitui um ponto de observação brasileiro: acrescenta um segundo ponto
 * estrangeiro, independente do primeiro.
 *
 * E não move a auditoria para cá. Repassar o HTML ao coletor não ajudaria: para
 * renderizar a página, o navegador precisa buscar CSS, JavaScript, fontes e
 * imagens no mesmo portal, a partir do mesmo IP que leva 403. A sonda move o
 * primeiro pedido, não os cinquenta de que a renderização depende.
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

/**
 * Rótulo desta posição de rede, gravado em cada observação.
 *
 * Sem ele, duas fontes com o mesmo carimbo de tempo seriam indistinguíveis na
 * análise — e a comparação entre pontos de observação é a única razão de a
 * sonda existir.
 */
var VANTAGEM = "apps-script-google-eua";

/** Intervalo entre requisições, em milissegundos. */
var INTERVALO_MS = 2000;

/** Tempo máximo de espera por resposta, em milissegundos. */
var TIMEOUT_MS = 30000;

/** Repositório e ramo onde as observações são publicadas. */
var GITHUB_REPO = "ThallesCosta-dev/acessisaude-audit";
var GITHUB_RAMO = "serie-temporal";
var GITHUB_PASTA = "observacoes";

/**
 * Endereços observados.
 *
 * Espelham as sementes do catálogo do projeto. Se o catálogo mudar, este bloco
 * precisa mudar junto — a duplicação é deliberada, porque o Apps Script não tem
 * como ler o YAML do repositório, e uma sonda que observe endereços diferentes
 * dos auditados não serve de controle. Confira com conferir_alvos.py.
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
  "observado_em", "vantagem", "alvo", "url", "status_http", "bytes",
  "duracao_ms", "url_final", "erro"
];

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

/**
 * Observa todos os alvos, grava na planilha e publica no repositório.
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

  var carimbo = new Date();
  var observacoes = [];

  for (var i = 0; i < ALVOS.length; i++) {
    if (i > 0) {
      Utilities.sleep(INTERVALO_MS);
    }
    observacoes.push(_observarUm(ALVOS[i][0], ALVOS[i][1], carimbo));
  }

  _gravarNaPlanilha(observacoes);
  _publicarNoGitHub(observacoes, carimbo);

  Logger.log("Observados %s enderecos.", observacoes.length);
}

/**
 * Observa um endereço e devolve o registro correspondente.
 *
 * Uma falha de rede não interrompe a rodada: vira registro com o campo erro
 * preenchido. Interromper produziria lacuna silenciosa na série — exatamente o
 * que o coletor evita ao tratar perda de página como dado, e não como
 * interrupção da coleta.
 */
function _observarUm(alvo, url, carimbo) {
  var inicio = Date.now();

  try {
    var resposta = UrlFetchApp.fetch(url, {
      method: "get",
      headers: { "User-Agent": CONTATO },
      muteHttpExceptions: true,   // 4xx e 5xx sao DADO, nao excecao
      followRedirects: true,
      validateHttpsCertificates: true,
      timeout: TIMEOUT_MS
    });

    return {
      observado_em: carimbo.toISOString(),
      vantagem: VANTAGEM,
      alvo: alvo,
      url: url,
      status_http: resposta.getResponseCode(),
      bytes: resposta.getContentText().length,
      duracao_ms: Date.now() - inicio,
      url_final: "",
      erro: ""
    };

  } catch (e) {
    return {
      observado_em: carimbo.toISOString(),
      vantagem: VANTAGEM,
      alvo: alvo,
      url: url,
      status_http: "",
      bytes: "",
      duracao_ms: Date.now() - inicio,
      url_final: "",
      erro: String(e).slice(0, 250)
    };
  }
}

// ---------------------------------------------------------------------------
// Destinos
// ---------------------------------------------------------------------------

/** Acrescenta as observações à aba de registro. */
function _gravarNaPlanilha(observacoes) {
  var aba = _aba();
  var linhas = observacoes.map(function (o) {
    return CABECALHO.map(function (coluna) { return o[coluna]; });
  });
  aba.getRange(aba.getLastRow() + 1, 1, linhas.length, CABECALHO.length)
     .setValues(linhas);
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

/**
 * Publica as observações no ramo da série temporal, como arquivo novo.
 *
 * Um arquivo por execução, e não um CSV atualizado, por uma razão de
 * concorrência: o coletor também empurra para este ramo, três vezes ao dia.
 * Criar arquivo novo dispensa ler o SHA anterior e elimina a janela em que
 * duas escritas se sobrepõem — se as duas fontes colidissem, a perdedora
 * sumiria em silêncio, que é o modo de falhar que este projeto mais evita.
 *
 * Sem token configurado, apenas registra e segue: a planilha continua sendo o
 * destino primário, e uma falha de publicação não pode custar a observação.
 */
function _publicarNoGitHub(observacoes, carimbo) {
  var token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  if (!token) {
    Logger.log("GITHUB_TOKEN ausente nas propriedades do script — publicacao ignorada.");
    return;
  }

  var documento = {
    vantagem: VANTAGEM,
    observado_em: carimbo.toISOString(),
    agente: CONTATO,
    instrumento: "sonda-de-vantagem/apps-script",
    nota: "Controle de rede. Nao e auditoria de acessibilidade: mede apenas se o endereco responde.",
    observacoes: observacoes
  };

  var caminho = GITHUB_PASTA + "/" + VANTAGEM + "__" + _carimboCompacto(carimbo) + ".json";
  var url = "https://api.github.com/repos/" + GITHUB_REPO + "/contents/" + caminho;

  var corpo = {
    message: "Sonda de vantagem (" + VANTAGEM + ") — " + _carimboCompacto(carimbo),
    content: Utilities.base64Encode(
      JSON.stringify(documento, null, 2), Utilities.Charset.UTF_8
    ),
    branch: GITHUB_RAMO
  };

  var resposta = UrlFetchApp.fetch(url, {
    method: "put",
    contentType: "application/json",
    headers: {
      "Authorization": "Bearer " + token,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    payload: JSON.stringify(corpo),
    muteHttpExceptions: true
  });

  var codigo = resposta.getResponseCode();
  if (codigo === 201) {
    Logger.log("Publicado em %s (%s).", caminho, GITHUB_RAMO);
  } else {
    Logger.log(
      "Falha ao publicar (HTTP %s): %s", codigo, resposta.getContentText().slice(0, 300)
    );
  }
}

/** Carimbo no formato AAAAMMDD-HHMMSS, em UTC, como no nome das varreduras. */
function _carimboCompacto(data) {
  return Utilities.formatDate(data, "UTC", "yyyyMMdd-HHmmss");
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

/**
 * Confere se o token está configurado e se alcança o repositório.
 *
 * Executar à mão depois de cadastrar o token, antes de confiar no gatilho: uma
 * publicação que falha só aparece no registro de execução, e ninguém lê registro
 * de execução de um gatilho que roda de madrugada.
 */
function conferirAcessoAoGitHub() {
  var token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  if (!token) {
    throw new Error(
      "GITHUB_TOKEN ausente. Cadastre em Configuracoes do projeto > Propriedades do script."
    );
  }

  var resposta = UrlFetchApp.fetch(
    "https://api.github.com/repos/" + GITHUB_REPO + "/branches/" + GITHUB_RAMO,
    {
      method: "get",
      headers: {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
      },
      muteHttpExceptions: true
    }
  );

  var codigo = resposta.getResponseCode();
  if (codigo === 200) {
    Logger.log("Acesso confirmado: %s, ramo %s.", GITHUB_REPO, GITHUB_RAMO);
  } else if (codigo === 404) {
    Logger.log(
      "HTTP 404. O ramo %s existe? O token tem permissao de Contents neste repositorio? " +
      "Em repositorio privado, token sem permissao devolve 404, e nao 403.",
      GITHUB_RAMO
    );
  } else {
    Logger.log("HTTP %s: %s", codigo, resposta.getContentText().slice(0, 300));
  }
}
