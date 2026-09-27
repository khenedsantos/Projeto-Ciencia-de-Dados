-- SQLite. Uma linha representa um registro publicado na fonte.
SELECT periodo_emissao, COUNT(*) AS registros FROM ctps_emissoes GROUP BY periodo_emissao ORDER BY periodo_emissao;
SELECT "Sigla UF Órgão" AS uf, COUNT(*) AS registros, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ctps_emissoes), 2) AS percentual FROM ctps_emissoes GROUP BY "Sigla UF Órgão" ORDER BY registros DESC;
SELECT "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_emissoes GROUP BY "Tipo Protocolo" ORDER BY registros DESC;
SELECT Sexo, "Tipo Protocolo" AS tipo_protocolo, COUNT(*) AS registros FROM ctps_emissoes GROUP BY Sexo, "Tipo Protocolo" ORDER BY Sexo, registros DESC;

-- Perfis repetidos são reportados, não eliminados: não há identificador de atendimento.
SELECT COUNT(*) AS grupos_com_repeticao FROM (
  SELECT "Tipo Protocolo", "Tipo CTPS", "Nome Órgão", "Nome Município Órgão", "Sigla UF Órgão", Sexo, "Nível Escolaridade", "Raça e Cor", "Estado Civil", "Tipo Cidadania", "Nome do País", "Descrição Nacionalidade", "Nome Município Nascimento", "Sigla UF Nascimento", COUNT(*) AS n
  FROM ctps_emissoes
  GROUP BY "Tipo Protocolo", "Tipo CTPS", "Nome Órgão", "Nome Município Órgão", "Sigla UF Órgão", Sexo, "Nível Escolaridade", "Raça e Cor", "Estado Civil", "Tipo Cidadania", "Nome do País", "Descrição Nacionalidade", "Nome Município Nascimento", "Sigla UF Nascimento"
  HAVING n > 1
);
