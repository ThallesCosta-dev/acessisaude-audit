# PDF único com os artigos baixados: entrega de 09 a 11/09/2026

**Relação dos artigos reunidos em um único PDF a partir da pasta de referências do projeto, com a origem de cada um e sua situação no manuscrito**

**Resultado (15/09/2026):** `2026-09-11-artigos-compilados.pdf`, com capa, sumário e marcador por
artigo, montado a partir dos **16 PDF da pasta [`docs/referencias/`](../referencias/)**, em ordem
alfabética de autoria. Há também uma cópia `.zip`. Os dois arquivos não são versionados
(`.gitignore`), por serem obras de terceiros.

## 1. Como refazer

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\compilar_pdfs.py docs
eferencias docs\entregas6-09-11-artigos-compilados.pdf
```

O script junta os PDF da pasta em ordem alfabética do nome do arquivo, cria um marcador por
arquivo e comprime os fluxos de conteúdo. A capa com as referências completas foi gerada à
parte, a partir do sumário abaixo. Para incluir um artigo novo, basta salvá-lo na pasta e
rodar o comando de novo.

## 2. Artigos da pasta e como estão citados

| # | Arquivo em `docs/referencias/` | Referência (autor-data) | No manuscrito |
|---|---|---|---|
| 1 | Acosta-Vargas-et-al-2022-IJERPH.pdf | Acosta-Vargas *et al.* (2022), IJERPH | Não citado |
| 2 | Alajarmeh-2021-UAIS.pdf | Alajarmeh (2021), UAIS | Citado |
| 3 | Alismail-Chipidza-2021-JAMIA.pdf | Alismail e Chipidza (2021), JAMIA | Não citado |
| 4 | Barros-et-al-2024-WCGE.pdf | Barros *et al.* (2024), SBC | Citado |
| 5 | Belli-2017-JCP-preprint-FGV.pdf | Belli (2017), Journal of Cyber Policy | Não citado |
| 6 | Brajnik-2009-ASSETS-author-version.pdf | Brajnik (2009), ASSETS | Citado |
| 7 | 3371300.3383346.pdf | Frazão e Duarte (2020), W4A | Não citado |
| 8 | Freire-Castro-Fortes-2009-RAP.pdf | Freire, Castro e Fortes (2009), RAP | Citado |
| 9 | Ismailova-Inal-2022-IEEE-Access.pdf | Ismailova e Inal (2022), IEEE Access | Não citado |
| 10 | Petrie-Kheir-2007-CHI.pdf | Petrie e Kheir (2007), CHI | Não citado |
| 11 | 2207676.2207736.pdf | Power *et al.* (2012), CHI | Citado |
| 12 | Silva-LaRue-2015-RAP.pdf | Silva e La Rue (2015), RAP | Citado |
| 13 | Simao-Rodrigues-2005-CiInf.pdf | Simão e Rodrigues (2005), Ci. Inf. | Citado |
| 14 | Vieira-Caniato-Yonemotu-2017-Reciis.pdf | Vieira, Caniato e Yonemotu (2017), Reciis | Citado |
| 15 | 2461121.2461124.pdf | Vigo, Brown e Conway (2013), W4A | Citado |
| 16 | Yi-2020-UAIS.pdf | Yi (2020), UAIS | Não citado |

Sete artigos da pasta não entraram na lista de referências do manuscrito. São leitura de
apoio e podem voltar ao texto se a Discussão precisar deles (Belli, para o custo de dados e
*zero-rating*; Yi, Alismail e Acosta-Vargas, para saúde pública em outros países; Frazão,
Ismailova e Petrie, para a comparação entre ferramentas e a relação acessibilidade-usabilidade).

## 3. Citados no manuscrito e ausentes da pasta

Dois artigos citados não estão em `docs/referencias/`: **Torres, Mazzoni e Alves (2002)** e
**Moraes e González de Gómez (2007)**, ambos na SciELO em acesso aberto
(DOI 10.1590/S0100-19652002000300009 e 10.1590/S1413-81232007000300002). Ao salvá-los na pasta,
rodar o comando da seção 1 para que entrem no PDF.

## 4. Documentos normativos e relatórios

Constam nas referências, mas não são artigos: Constituição Federal; Decretos 5.296/2004 e
6.949/2009; Leis 12.527/2011, 12.965/2014, 13.146/2015 e 14.129/2021; eMAG 3.1; WCAG 2.1;
Caplovitz (1963, livro); TIC Domicílios 2024; Censo 2022; Web Almanac 2025; Panorama da Anatel.
