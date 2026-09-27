# Observações calculadas

Os números abaixo foram gerados pelo pipeline; são descrições do conjunto publicado e não evidenciam causalidade ou impacto.

- Registros preservados: **485,430**.
- Registros com o mesmo perfil em todas as colunas de negócio: **25,844**; eles foram preservados por falta de identificador de atendimento.
- UF com maior volume no conjunto: **MG**, com **81,791** registros (16.8% do total).
- As cinco UFs com mais registros concentram **299,077** linhas (61.6% do total). Isso descreve a distribuição da publicação, sem indicar causa para a concentração.
- Tipo de protocolo mais frequente: **1ª Via**, com **351,527** registros.
- **1ª Via** representa **351,527** registros (72.4%).
- **2ª Via** representa **133,903** registros (27.6%).
- No período de análise, o volume observado foi de **227,013** em **2020-01** e **62** em **2022-12**; o pico mensal foi **2020-01**, com **227,013** registros.
- Há **1** registro fora do intervalo de geração 2020-01 a 2022-12: `Data CTPS Gerada = 2023-01`, originado de `dados_ctps_2022.xlsx`. Ele foi preservado e está detalhado em `reports/tables/emissoes_fora_intervalo.csv`.

## Limitações

As variações mensais e regionais são descritivas dos registros administrativos publicados. Não permitem inferir emprego, tamanho do mercado de trabalho, demanda causal ou desempenho de atendimento. `Data Protocolo` tem 15.017 registros anteriores a 2020, enquanto `Data CTPS Gerada` tem um registro em 2023-01; esses valores são preservados e reportados separadamente.
