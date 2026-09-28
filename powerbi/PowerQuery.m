let
    // Consulta de apoio. O PBIX existente não é modificado por este arquivo.
    // Crie o parâmetro de texto CaminhoCSV com o caminho absoluto do CSV gerado
    // no seu computador (data/processed/ctps_emissoes.csv). Ver modelo.md.
    Source = Csv.Document(File.Contents(CaminhoCSV), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {{"data_protocolo_date", type date}, {"data_ctps_gerada_date", type date}, {"data_emissão_date", type date}, {"data_nascimento_date", type date}, {"ano_emissao", Int64.Type}, {"mes_emissao", Int64.Type}, {"registro_id", type text}}, "en-US")
in
    Types
