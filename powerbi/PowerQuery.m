let
    // Crie o parâmetro de texto CaminhoCSV no Desktop com o caminho do CSV gerado.
    Source = Csv.Document(File.Contents(CaminhoCSV), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {{"data_protocolo_date", type date}, {"data_ctps_gerada_date", type date}, {"data_emissão_date", type date}, {"data_nascimento_date", type date}, {"ano_emissao", Int64.Type}, {"mes_emissao", Int64.Type}, {"registro_id", type text}}, "en-US")
in
    Types
