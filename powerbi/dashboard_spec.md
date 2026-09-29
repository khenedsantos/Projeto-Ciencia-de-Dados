# Dashboard entregue e reconciliação das páginas

O [PBIX](dashboard_ctps_2020_2022.pbix) foi construído manualmente no Power BI Desktop e contém quatro páginas. Este documento descreve a entrega existente. As capturas e o binário não foram editados na integração.

| Página | Conteúdo | Contexto observado |
|---|---|---|
| [Visão Geral](01_visao_geral.png) | Cartões, Top 10 UFs, protocolo e evolução mensal | Ano = 2020, 2021 e 2022; protocolo e UF = Todos |
| [Perfil dos Registros](02_perfil_registros.png) | Escolaridade, sexo, raça/cor e cidadania | Ano = 2020, 2021 e 2022; protocolo e UF = Todos |
| [Qualidade e Metodologia](03_qualidade_metodologia.png) | Processados, removidos, datas inválidas, fora do período e limitações | Base completa para controle de qualidade |
| [Revisão Analítica](04_revisao_analitica.png) | Síntese temporal, regional, protocolo e perfil | Texto descritivo da análise; não deve ser tratado como medida dinâmica |

## Diferença entre os totais

A base processada mantém **485.430** linhas. Uma delas tem `Data CTPS Gerada = 2023-01`, na fonte oficial `dados_ctps_2022.xlsx`. As tabelas analíticas do pipeline e a view SQL usam **485.429** linhas em 2020–2022.

| Indicador | Base completa preservada | Recorte analítico do dashboard: 2020–2022 |
|---|---:|---:|
| Registros | 485.430 | 485.429 |
| 1ª via | 351.527 | 351.527 |
| 2ª via | 133.903 | 133.902 |
| Masculino | 251.310 | 251.309 |
| Feminino | 234.120 | 234.120 |
| Pardo | 303.673 | 303.672 |
| Brasileiro Nato | 478.833 | 478.832 |
| 1º GRAU INCOMP. 5ª A 8ª SÉRIE INCOMP. | 68.133 | 68.132 |
| AC | 2.135 | 2.134 |

A captura de **Perfil dos Registros** mostra **485.429 registros**, sendo **251.309 masculinos (51,77%)** e **234.120 femininos (48,23%)**, com subtítulo 2020–2022. O layout do PBIX confirma a seleção de 2020, 2021 e 2022 nessa página e em Visão Geral. As duas páginas analíticas estão visualmente e numericamente alinhadas ao recorte das tabelas e do SQL.

Os 485.430 exibidos na página de qualidade são intencionais: ela controla a preservação da base, com **0 removidos**, **0 datas inválidas** e **1 registro fora do período**. Já o recorte analítico exclui esse registro somente das agregações.

## Uso e interpretação

Visão Geral e Perfil permitem explorar ano, tipo de protocolo e UF. O ranking usa a UF do órgão emissor. Não representa residência, população ou desempenho do mercado de trabalho. Categorias históricas são mantidas conforme a fonte, inclusive `IG`, sem significado presumido.

A página Revisão Analítica contém uma narrativa fixa sobre os dados; seu texto não deve ser tomado como atualização automática após mudanças em filtros ou na base.

[modelo.md](modelo.md) documenta carregamento, definição de repetições e limites da inspeção. [medidas.dax](medidas.dax) e [PowerQuery.m](PowerQuery.m) são referências técnicas de apoio; não foram usadas para sobrescrever o modelo manual.
