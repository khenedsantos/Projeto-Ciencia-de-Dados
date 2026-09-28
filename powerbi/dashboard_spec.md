# Especificação do dashboard

Esta é uma especificação para implementação posterior no Power BI Desktop. Não há um arquivo `.pbix` neste repositório.

## Página 1 — Visão Geral

**Objetivo:** mostrar o volume publicado e sua evolução. Por padrão, incluir todos os registros para conciliar com o README; oferecer o recorte 2020–2022 e identificar a exceção de 2023.

- **Cartões:** `[Registros publicados]`, `[Primeira via]`, `[Segunda via]`, `[Percentual primeira via]`.
- **Linha temporal:** eixo `periodo_emissao`, valor `[Registros publicados]`.
- **Composição:** coluna ou barra empilhada por `Tipo Protocolo`, usando `[Registros publicados]`.
- **Filtros:** `ano_emissao`, `mes_emissao` e `Tipo Protocolo`.
- **Observação:** destacar o registro `2023-01` como fora do período principal, sem removê-lo da tabela fato.

## Página 2 — Análise Regional

**Objetivo:** comparar a distribuição dos registros por UF e órgão.

- **Cartões:** `[Registros publicados]` e `[UFs com registros]`.
- **Barras horizontais:** `Sigla UF Órgão`, valor `[Registros publicados]`, ordenadas de forma decrescente.
- **Detalhamento:** `Nome Órgão` e `Nome Município Órgão` em uma tabela ou drill-through, com `[Registros publicados]`.
- **Filtros:** `Sigla UF Órgão`, `Nome Órgão` e período.
- **Leitura:** a concentração regional é descritiva da publicação administrativa; não indica causa ou desempenho.

## Página 3 — Perfil dos Registros

**Objetivo:** explorar os atributos informados no atendimento sem tratar categorias como características de pessoas únicas.

- **Cartões:** `[Registros publicados]`, `[Primeira via]`, `[Segunda via]` e `[Repeticoes de registros]`.
- **Barras:** `Sexo`, `Nível Escolaridade`, `Raça e Cor`, `Estado Civil` e `Tipo Cidadania`, sempre com `[Registros publicados]`.
- **Tabela agregada de contexto:** dimensões `Tipo CTPS` e `Descrição Nacionalidade`, com `[Registros publicados]`.
- **Filtros:** `Tipo Protocolo`, `Sigla UF Órgão`, ano e mês.
- **Leitura:** os campos descrevem o preenchimento dos registros publicados e podem refletir categorias históricas da fonte.

## Medidas

As medidas usadas nas páginas estão em [`medidas.dax`](medidas.dax). A tabela fato é `ctps_emissoes`; as dimensões podem ser derivadas no Power Query ou no próprio modelo. Recomenda-se relacionamento unidirecional das dimensões para a fato e nenhum relacionamento bidirecional sem necessidade analítica explícita.
