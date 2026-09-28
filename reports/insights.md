# Observações calculadas

Os números abaixo foram gerados pelo pipeline. São achados descritivos do conjunto publicado; não evidenciam causalidade ou impacto.

## Achados

- Registros preservados na base completa: **485,430**.
- Recorte analítico de 2020–2022: **485,429** registros. Todas as distribuições e participações abaixo usam esse recorte; qualidade e repetições são verificadas na base completa.
- Repetições de registros: **25,844** linhas excedentes após a primeira ocorrência de cada combinação das 18 colunas de negócio. Todas foram preservadas; a contagem não representa pessoas nem combinações únicas.
- **Distribuição regional:** MG concentra **81,791** registros (16.8% do total). As cinco UFs com mais registros somam **299,077** linhas (61.6%).
- **Tipo de protocolo:** 1ª Via é o tipo mais frequente, com **351,527** registros.
  - 1ª Via: **351,527** registros (72.4%).
  - 2ª Via: **133,902** registros (27.6%).
- **Evolução observada:** o volume foi de **227,013** registros em **2020-01** e **62** em **2022-12**; o pico mensal foi **2020-01**, com **227,013** registros.
- **Comparação anual por mês de geração:** 2020: **470,560** registros; 2021: **11,707** registros; 2022: **3,162** registros. O registro fora do período principal não entra nesta comparação.
- A variação de volume entre 2020 e 2022 foi de **-99.33%**. É uma comparação dos registros publicados, sem atribuição de causa.
- **Qualidade de escopo:** **1** registro(s) fora de 2020-01 a 2022-12: `2023-01` em `dados_ctps_2022.xlsx`: 1. Preservados em [emissoes_fora_intervalo.csv](tables/emissoes_fora_intervalo.csv).
- **Sexo:** a categoria mais frequente é **MASCULINO**, com **251,309** registros (51.77%). Distribuição completa em [emissoes_por_sexo.csv](tables/emissoes_por_sexo.csv).
- **Nível Escolaridade:** a categoria mais frequente é **2º GRAU COMPLETO OU TEC. PROFISSIONAL**, com **159,537** registros (32.87%). Distribuição completa em [emissoes_por_escolaridade.csv](tables/emissoes_por_escolaridade.csv).
- **Raça e Cor:** a categoria mais frequente é **Pardo**, com **303,672** registros (62.56%). Distribuição completa em [emissoes_por_raca_cor.csv](tables/emissoes_por_raca_cor.csv).
- **Tipo Cidadania:** a categoria mais frequente é **Brasileiro Nato**, com **478,832** registros (98.64%). Distribuição completa em [emissoes_por_cidadania.csv](tables/emissoes_por_cidadania.csv).
- **UF não padronizada:** **12** registros na base completa. Valores originais e origem em [ufs_nao_padronizadas.csv](tables/ufs_nao_padronizadas.csv); nenhum código foi substituído.

## Possíveis interpretações e limites

- Os resultados mostram como os registros administrativos publicados se distribuem por tempo, UF e protocolo. Não permitem explicar as causas das variações.
- As mudanças mensais não devem ser interpretadas como evolução do emprego, do mercado de trabalho ou de demanda causal.
- `Data Protocolo` tem 15,017 registros anteriores ao período principal. Essa data histórica é distinta do mês de geração; as ocorrências foram preservadas e reportadas separadamente.
- A UF é a do órgão emissor, não necessariamente a residência do titular. A categoria IG é mantida sem atribuição de significado.
- A captura da página Perfil dos Registros do PBIX usa Ano = Todos (485.430). As tabelas deste relatório usam 2020–2022 (485.429). Consulte a [reconciliação do dashboard](../powerbi/dashboard_spec.md).
