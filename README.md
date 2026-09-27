# Emissões de CTPS no Brasil — 2020 a 2022

Análise exploratória das emissões de Carteira de Trabalho e Previdência Social (CTPS) disponibilizadas pelo Ministério do Trabalho e Emprego (MTE).

O projeto foi reconstruído para responder perguntas descritivas sobre volume de emissões, distribuição regional, tipo de protocolo e perfil informado no atendimento. O foco é demonstrar um fluxo reproduzível com Python, pandas, SQL e Power BI.

## Contexto e limites

As bases públicas registram atendimentos e emissões de CTPS física em arquivos mensais e anuais do MTE. Elas permitem observar a distribuição dos registros publicados na fonte, mas não representam diretamente contratações, desemprego ou toda a força de trabalho brasileira.

As perguntas do projeto são: como os registros se distribuem por mês de geração; quais estados e órgãos concentram mais registros; qual é a composição por primeira e segunda via; e como aparecem sexo, escolaridade e cidadania.

Fonte oficial: [página de estatísticas da CTPS do MTE](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/estatisticas).

Os arquivos brutos não são versionados. O download é reproduzível e os checksums ficam registrados em `data/source_manifest.json`. O pipeline preserva as 485.430 linhas publicadas nos cinco arquivos. Linhas com o mesmo conjunto de atributos não são removidas automaticamente: sem identificador de atendimento não é possível afirmar que sejam duplicatas indevidas.

O escopo temporal da série principal usa `Data CTPS Gerada` entre 2020-01 e 2022-12. A fonte `dados_ctps_2022.xlsx` contém uma linha com `Data CTPS Gerada = 2023-01` (linha 552 no arquivo oficial); ela foi preservada, sinalizada no relatório de qualidade e incluída em `reports/tables/emissoes_fora_intervalo.csv`. A linha registra protocolo e emissão em 2022-12, protocolo `2ª Via`, órgão `SRTE/AC - Rio Branco` e UF `AC`. Além disso, 15.017 registros têm `Data Protocolo` anterior a 2020, informação histórica do atendimento que não é usada para recortar a série de geração.

## Estrutura

```text
data/raw/                 # arquivos baixados; ignorados pelo Git
data/processed/           # CSV, SQLite e relatório de qualidade gerados
reports/figures/          # gráficos gerados
reports/tables/           # tabelas agregadas geradas
powerbi/                  # Power Query, medidas DAX e modelo
scripts/download_source.py
sql/analises.sql
src/ctps_pipeline.py
tests/test_pipeline.py       # testes unitários
tests/test_integration.py    # teste opcional com fontes locais
```

## Como executar

Use Python 3.11 ou superior.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/download_source.py
python -m src.ctps_pipeline --source-dir data/raw --output-dir data/processed
pytest
```

O pipeline gera `data/processed/ctps_emissoes.csv`, `data/processed/ctps_emissoes.sqlite`, `data/processed/quality_report.json`, tabelas agregadas, gráficos e `reports/insights.md`.

## SQL e Power BI

As consultas em `sql/analises.sql` usam SQLite e partem da tabela `ctps_emissoes`. O diretório `powerbi/` contém a especificação do modelo proposto, o script de Power Query, as medidas DAX e a especificação das páginas do dashboard. Ainda não existe um arquivo `.pbix`: o dashboard real será montado posteriormente no Power BI Desktop. Portanto, esses arquivos descrevem uma entrega planejada e reproduzível, não um painel já publicado.

## Interpretação

As conclusões descrevem os registros publicados pelo MTE. A base não contém um identificador de pessoa ou de atendimento que permita medir pessoas únicas, reincidência, conversão em emprego ou causalidade. Datas são mensais; há categorias históricas e mudanças de preenchimento entre arquivos. Recomendações devem ser apresentadas como uso potencial para acompanhamento da demanda registrada, sem alegar economia de recursos ou melhoria de empregabilidade.

Status: pipeline reconstruído e validado com os arquivos oficiais disponíveis na página do MTE em 27/09/2026.
