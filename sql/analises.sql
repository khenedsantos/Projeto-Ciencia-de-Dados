-- SQLite. Uma linha representa um registro publicado na fonte.
SELECT periodo_emissao, COUNT(*) AS registros FROM ctps_emissoes GROUP BY periodo_emissao ORDER BY periodo_emissao;
SELECT "Sigla UF Órgão" AS uf, COUNT(*) AS registros, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ctps_emissoes), 2) AS percentual FROM ctps_emissoes GROUP BY "Sigla UF Órgão" ORDER BY registros DESC;
SELECT "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_emissoes GROUP BY "Tipo Protocolo" ORDER BY registros DESC;
SELECT Sexo, "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_emissoes GROUP BY Sexo, "Tipo Protocolo" ORDER BY Sexo, registros DESC;

-- Linhas excedentes após a primeira ocorrência por combinação das 18 colunas.
-- Não são pessoas nem combinações únicas; todas as linhas são preservadas.
SELECT COALESCE(SUM(n - 1), 0) AS repeticoes_de_registros FROM (
  SELECT COUNT(*) AS n
  FROM ctps_emissoes
  GROUP BY "Tipo Protocolo", "Data Protocolo", "Tipo CTPS", "Data CTPS Gerada", "Nome Órgão", "Nome Município Órgão", "Sigla UF Órgão", "Data Emissão", Sexo, "Nível Escolaridade", "Raça e Cor", "Estado Civil", "Data Nascimento", "Tipo Cidadania", "Nome do País", "Descrição Nacionalidade", "Nome Município Nascimento", "Sigla UF Nascimento"
  HAVING n > 1
);
