# Modelo Power BI (especificação)

Este diretório ainda não contém um arquivo `.pbix`. Ele documenta o modelo proposto, a consulta Power Query, as medidas DAX e as páginas planejadas para implementação posterior no Power BI Desktop.

`ctps_emissoes` tem uma linha para cada registro publicado nos arquivos oficiais. O modelo não afirma que cada linha represente uma pessoa única.

Para a primeira versão, a tabela fato é `ctps_emissoes`. As dimensões podem ser derivadas no Power Query ou no modelo: `DimPeriodo` (período, ano e mês), `DimUF` (UF e município do órgão), `DimProtocolo` e `DimPerfil` (sexo, escolaridade, raça/cor, estado civil e cidadania).

Use relações unidirecionais de dimensões para a fato e medidas explícitas em DAX. A escolha segue a orientação oficial sobre modelo em estrela: [Microsoft Learn](https://learn.microsoft.com/power-bi/guidance/star-schema).

Páginas sugeridas: visão geral, demanda regional, perfil dos registros e qualidade/cobertura. O painel deve deixar claro que os números descrevem a publicação administrativa, não contratação ou impacto causal.
