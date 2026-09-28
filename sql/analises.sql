-- SQLite. Base completa preservada. Análises abaixo usam Data CTPS Gerada em 2020–2022.
-- A view é temporária: não apaga nem altera linhas da tabela processada.
CREATE TEMP VIEW IF NOT EXISTS ctps_2020_2022 AS
SELECT * FROM ctps_emissoes
WHERE data_ctps_gerada_date >= '2020-01-01' AND data_ctps_gerada_date < '2023-01-01';

-- emissoes_por_mes.csv
SELECT periodo_emissao, COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY periodo_emissao ORDER BY periodo_emissao;
-- emissoes_por_uf.csv (IG permanece como categoria original, não como UF reconhecida)
SELECT "Sigla UF Órgão" AS uf, COUNT(*) AS registros, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ctps_2020_2022), 4) AS percentual FROM ctps_2020_2022 GROUP BY "Sigla UF Órgão" ORDER BY registros DESC;
-- emissoes_por_protocolo.csv
SELECT "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY "Tipo Protocolo" ORDER BY registros DESC;
-- emissoes_por_sexo.csv
SELECT Sexo, COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY Sexo ORDER BY registros DESC;
-- emissoes_por_escolaridade.csv
SELECT "Nível Escolaridade", COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY "Nível Escolaridade" ORDER BY registros DESC;
-- emissoes_por_raca_cor.csv
SELECT "Raça e Cor", COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY "Raça e Cor" ORDER BY registros DESC;
-- emissoes_por_cidadania.csv
SELECT "Tipo Cidadania", COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY "Tipo Cidadania" ORDER BY registros DESC;
-- Cruzamento sexo × protocolo no mesmo recorte.
SELECT Sexo, "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_2020_2022 GROUP BY Sexo, "Tipo Protocolo" ORDER BY Sexo, registros DESC;

-- Qualidade: base COMPLETA. Linhas excedentes após a primeira ocorrência
-- por combinação das 18 colunas de negócio, após remoção de espaços nas extremidades.
-- Não são pessoas nem combinações únicas. Nenhuma linha é removida.
SELECT COALESCE(SUM(n - 1), 0) AS repeticoes_de_registros FROM (
  SELECT COUNT(*) AS n
  FROM ctps_emissoes
  GROUP BY "Tipo Protocolo", "Data Protocolo", "Tipo CTPS", "Data CTPS Gerada", "Nome Órgão", "Nome Município Órgão", "Sigla UF Órgão", "Data Emissão", Sexo, "Nível Escolaridade", "Raça e Cor", "Estado Civil", "Data Nascimento", "Tipo Cidadania", "Nome do País", "Descrição Nacionalidade", "Nome Município Nascimento", "Sigla UF Nascimento"
  HAVING n > 1
);
