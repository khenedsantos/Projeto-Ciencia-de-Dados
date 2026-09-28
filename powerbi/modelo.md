# Modelo Power BI (especificação)

Este diretório ainda não contém um arquivo `.pbix`. Ele documenta o modelo proposto, a consulta Power Query, as medidas DAX e as páginas planejadas para implementação posterior no Power BI Desktop.

No Desktop, crie o parâmetro de texto `CaminhoCSV` apontando para o CSV processado e importe `PowerQuery.m` como a consulta `ctps_emissoes`. As datas convertidas usam o dia 1 como representação técnica do mês, sem precisão diária. Crie cada medida de `medidas.dax` separadamente; formate a participação como percentual. Power Query e DAX foram revisados estaticamente e ainda precisam ser executados no Desktop.

Sem filtros, os cartões devem mostrar 485.430 registros, 351.527 de primeira via e 133.903 de segunda via. A medida `Repeticoes de registros` conta as linhas excedentes após a primeira ocorrência de cada combinação das 18 colunas de negócio, como o relatório Python: 25.844 sem filtros. Não conta pessoas nem combinações únicas. `registro_id` é um hash de atributos, não uma chave única de atendimento.

`ctps_emissoes` tem uma linha para cada registro publicado nos arquivos oficiais. O modelo não afirma que cada linha represente uma pessoa única.

Para a primeira versão, a tabela fato é `ctps_emissoes`. As dimensões podem ser derivadas no Power Query ou no modelo: `DimPeriodo` (período, ano e mês), `DimUF` (UF e município do órgão), `DimProtocolo` e `DimPerfil` (sexo, escolaridade, raça/cor, estado civil e cidadania).

Use relações unidirecionais de dimensões para a fato e medidas explícitas em DAX. A escolha segue a orientação oficial sobre modelo em estrela: [Microsoft Learn](https://learn.microsoft.com/power-bi/guidance/star-schema).

As páginas propostas estão detalhadas em [`dashboard_spec.md`](dashboard_spec.md): Visão Geral, Análise Regional e Perfil dos Registros. O painel deve deixar claro que os números descrevem a publicação administrativa, não contratação ou impacto causal.
