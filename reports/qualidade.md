# Qualidade e reconciliação da entrega Power BI

## Escopo e origem dos números

A base processada tem **485.430 registros**; o recorte de geração de CTPS em **2020–2022 tem 485.429**. A integração passou a aplicar esse recorte em todas as agregações analíticas de Python e SQL. Antes, totais por protocolo/UF e participações incluíam 2023, enquanto a comparação anual já recortava o período. Os arquivos processados continuam completos.

As tabelas `emissoes_por_mes`, `emissoes_por_uf`, `emissoes_por_protocolo`, `emissoes_por_sexo`, `emissoes_por_escolaridade`, `emissoes_por_raca_cor` e `emissoes_por_cidadania` descrevem o recorte. `emissoes_fora_intervalo` e `ufs_nao_padronizadas` são controles de qualidade sobre a base completa.

## Registro oficial de janeiro de 2023

A linha está em `dados_ctps_2022.xlsx` com os valores originais:

| Campo | Valor |
|---|---|
| Tipo Protocolo | 2ª Via |
| Data Protocolo | 2022-12 |
| Data CTPS Gerada | 2023-01 |
| Data Emissão | 2022-12 |
| Nome Órgão | SRTE/AC - Rio Branco |
| Nome Município Órgão | RIO BRANCO |
| Sigla UF Órgão | AC |

O mês de 2023 existe na fonte: não foi produzido pela conversão. A linha foi preservada por rastreabilidade e está em [emissoes_fora_intervalo.csv](tables/emissoes_fora_intervalo.csv). O recorte usa a data de geração, não a data do protocolo ou da emissão. Há também 15.017 datas de protocolo anteriores a 2020, preservadas como histórico do atendimento.

## Categoria original IG

Há **12 registros** com `Sigla UF Órgão = IG` nos XLSX oficiais, com `Nome Município Órgão = IGNORADO`.

| Arquivo | Quantidade | Linhas na planilha, incluindo o cabeçalho |
|---|---:|---|
| dados_ctps_2020-jan.xlsx | 10 | 46334, 57119, 61424, 77863, 113586, 121946, 123621, 124026, 166180, 184721 |
| dados_ctps_2020-fev.xlsx | 2 | 22434, 105250 |

Os órgãos informados são `AA/DF - Gama - Gama` (5), `AA/DF - Ceilândia - Ceilândia` (6) e `SEC - Gama` (1). Esses nomes não justificam substituir IG por DF: o significado do código não foi confirmado. IG é mantido como categoria não padronizada, sem representar uma unidade federativa adicional. A distribuição reproduzível por fonte e órgão está em [ufs_nao_padronizadas.csv](tables/ufs_nao_padronizadas.csv).

## Repetições, tipos e integridade

- **25.844 repetições** são linhas excedentes por combinação das 18 colunas de negócio após remoção de espaços nas extremidades. A [definição completa](../powerbi/modelo.md) é compartilhada por Python, SQL e DAX de apoio. Não há deduplicação nem contagem de pessoas/perfis únicos.
- CSV e SQLite armazenam as mesmas linhas e atributos. As datas derivadas aparecem como `AAAA-MM-01` no CSV e `AAAA-MM-01 00:00:00` no SQLite; a comparação normaliza os tipos de data, sem alterar valores.
- O [manifesto versionado](../data/source_manifest.json) registra URL, tamanho e SHA-256 dos cinco XLSX. A execução valida cada arquivo antes do processamento, sem necessidade de internet se as fontes já estiverem disponíveis.
- O relatório gerado `data/processed/quality_report.json` registra entradas/saídas, remoções, datas inválidas, repetições, recorte e categorias de UF não padronizadas.
- As capturas e o PBIX foram copiados byte a byte e conferidos por SHA-256. A validação automatizada do pipeline não executa o motor DAX nem regrava o PBIX.

## Contexto das capturas

Visão Geral e Perfil dos Registros estão salvos com 2020, 2021 e 2022 selecionados e mostram 485.429 registros. A captura de Perfil confirma 251.309 masculinos (51,77%) e 234.120 femininos (48,23%). Os números analíticos do dashboard, README, SQL e tabelas usam o mesmo recorte; o controle de qualidade mantém a base completa de 485.430, incluindo o registro oficial de janeiro de 2023. Veja a [reconciliação por indicador](../powerbi/dashboard_spec.md).

## Limites

A fonte não permite identificar indivíduos únicos, provar duplicidades indevidas nem explicar causas da redução dos registros. As categorias são preservadas conforme publicadas. Emissões de CTPS não medem emprego, contratação, desemprego, formalização ou impacto econômico.
