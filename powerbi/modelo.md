# Modelo e carregamento no Power BI

O [dashboard_ctps_2020_2022.pbix](dashboard_ctps_2020_2022.pbix) é a entrega manual do dashboard. Ele e suas quatro capturas são preservados integralmente. [dashboard_spec.md](dashboard_spec.md) descreve as páginas e os contextos de filtro observados.

## Dados e escopo

A tabela `ctps_emissoes` preserva 485.430 linhas dos cinco arquivos oficiais. Cada linha é um registro administrativo, não uma pessoa única. As datas convertidas usam o dia 1 como representação técnica do mês; não existe precisão diária na fonte.

O layout do PBIX referencia `ctps_emissoes` nos visuais e `Calendario.Ano` / `Calendario.Date` nas segmentações e na série temporal. A leitura do layout não valida cardinalidades, relações nem fórmulas internas do modelo tabular. Para inspecioná-las, abra o PBIX no Power BI Desktop.

O recorte principal é baseado em `data_ctps_gerada_date` desde 2020-01-01, inclusive, até 2023-01-01, exclusive. Tem 485.429 registros, 351.527 de 1ª via e 133.902 de 2ª via. Sem filtro de período, são 485.430, 351.527 e 133.903, respectivamente.

## Portabilidade

1. Execute o pipeline na raiz do projeto para gerar `data/processed/ctps_emissoes.csv`.
2. Abra o PBIX no Desktop. Para atualizar a origem, use **Transformar dados** e examine a etapa **Fonte** da consulta `ctps_emissoes`.
3. Aponte a origem para o CSV gerado no seu computador. Caso a consulta utilize parâmetro, altere-o em **Gerenciar parâmetros**; se utilizar caminho literal, ajuste a etapa Fonte na sua cópia de trabalho.
4. Confira o total processado de 485.430 e os filtros de ano antes de comparar resultados. Não remova o registro de 2023 na importação.

[PowerQuery.m](PowerQuery.m) é uma consulta de apoio portátil por parametrização: crie no Desktop um parâmetro de **texto** chamado `CaminhoCSV` contendo o caminho absoluto local do CSV. Cole a consulta em uma consulta em branco chamada `ctps_emissoes`, apenas se estiver reconstruindo o carregamento. Caminhos relativos dependem do contexto do Desktop e não são assumidos aqui. A consulta mantém as 18 colunas de negócio como texto e tipa somente os campos derivados.

O arquivo M não modifica automaticamente o PBIX e não é apresentado como uma exportação da consulta interna do artefato.

## Medidas e repetições

[medidas.dax](medidas.dax) contém fórmulas de apoio revisadas estaticamente, não uma extração certificada de todas as medidas do PBIX. `Registros publicados` conta linhas no contexto atual; as medidas com sufixo `2020-2022` explicitam o recorte e mantêm a interseção com os filtros do usuário. A inspeção do layout confirma os nomes das medidas usadas nos visuais, mas não executa o motor DAX.

**Repetições de registros** contam as linhas excedentes após a primeira ocorrência de cada combinação das colunas abaixo, após a remoção de espaços nas extremidades:

```text
Tipo Protocolo; Data Protocolo; Tipo CTPS; Data CTPS Gerada;
Nome Órgão; Nome Município Órgão; Sigla UF Órgão; Data Emissão;
Sexo; Nível Escolaridade; Raça e Cor; Estado Civil; Data Nascimento;
Tipo Cidadania; Nome do País; Descrição Nacionalidade;
Nome Município Nascimento; Sigla UF Nascimento
```

Python usa `duplicated(EXPECTED_COLUMNS).sum()`; SQL agrupa as mesmas 18 colunas e soma `n - 1`; o DAX de apoio usa o mesmo agrupamento. Na base completa sem filtros: **25.844**. O campo legado `duplicate_full_rows` do JSON de qualidade mantém esse significado, sem afirmar duplicidade indevida. No DAX, filtros alteram o universo do cálculo; SQL e relatório de qualidade usam a base completa.

`arquivo_fonte`, campos derivados e `registro_id` não participam desse agrupamento. `registro_id` é um hash de atributos e origem, não uma chave única de pessoa ou atendimento. Não há uma segunda métrica de “perfis recorrentes” definida por subconjunto de atributos, nem identificação de recorrência de uma mesma pessoa. Nenhuma linha é descartada por repetição.

`Categorias UF com registros` inclui `IG` como categoria original. Não deve ser interpretada como quantidade de unidades federativas reconhecidas.

## Validação e limites

As contagens do Python, das tabelas e do SQL são confrontadas automaticamente. A equivalência semântica do DAX de apoio é revisada estaticamente; as capturas comprovam o estado visual fornecido pelo autor. Não houve alteração nem regravação do PBIX nesta integração.
