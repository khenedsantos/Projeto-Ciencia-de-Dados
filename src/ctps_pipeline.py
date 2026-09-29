from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import urllib.request
from pathlib import Path

import matplotlib

# Os gráficos são exportados para arquivos, sem dependência de interface gráfica.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

SOURCE_FILES = {
    "dados_ctps_2020-jan.xlsx": "https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/ctps-arquivos/dados_ctps_2020-jan.xlsx",
    "dados_ctps_2020-fev.xlsx": "https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/ctps-arquivos/dados_ctps_2020-fev.xlsx",
    "dados_ctps_2020-mar-a-dez.xlsx": "https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/ctps-arquivos/dados_ctps_2020-mar-a-dez.xlsx",
    "dados_ctps_2021.xlsx": "https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/ctps-arquivos/dados_ctps_2021.xlsx",
    "dados_ctps_2022.xlsx": "https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/ctps-arquivos/dados_ctps_2022.xlsx",
}
EXPECTED_COLUMNS = [
    "Tipo Protocolo", "Data Protocolo", "Tipo CTPS", "Data CTPS Gerada",
    "Nome Órgão", "Nome Município Órgão", "Sigla UF Órgão", "Data Emissão",
    "Sexo", "Nível Escolaridade", "Raça e Cor", "Estado Civil", "Data Nascimento",
    "Tipo Cidadania", "Nome do País", "Descrição Nacionalidade",
    "Nome Município Nascimento", "Sigla UF Nascimento",
]
DATE_COLUMNS = ["Data Protocolo", "Data CTPS Gerada", "Data Emissão", "Data Nascimento"]
SCOPE_DATE_COLUMNS = ["Data Protocolo", "Data CTPS Gerada", "Data Emissão"]
EXPECTED_PERIOD_START = pd.Period("2020-01", freq="M")
EXPECTED_PERIOD_END = pd.Period("2022-12", freq="M")
VALID_UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
PROFILE_COLUMNS = {
    "sexo": "Sexo", "escolaridade": "Nível Escolaridade",
    "raca_cor": "Raça e Cor", "cidadania": "Tipo Cidadania",
}


def date_column_name(column: str) -> str:
    return f"{column.lower().replace(' ', '_')}_date"


def download_sources(raw_dir: Path) -> list[dict[str, str | int]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for filename, url in SOURCE_FILES.items():
        destination = raw_dir / filename
        if not destination.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "ctps-portfolio/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                destination.write_bytes(response.read())
        manifest.append({"file": filename, "url": url, "bytes": destination.stat().st_size,
                         "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
    (raw_dir.parent / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def validate_manifest(manifest_path: Path, source_dir: Path, expected_sources: dict | None = None) -> dict[str, dict[str, int | str]]:
    """Validate the local files listed in a manifest without accessing the network."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    filenames = [entry["file"] for entry in manifest]
    if len(filenames) != len(set(filenames)):
        raise ValueError("Manifest contém arquivos repetidos.")
    if expected_sources is not None and (
        set(filenames) != set(expected_sources)
        or any(entry["url"] != expected_sources.get(entry["file"]) for entry in manifest)
    ):
        raise ValueError("Manifest não corresponde aos arquivos e URLs esperados.")
    validation = {}
    for entry in manifest:
        path = source_dir / entry["file"]
        if not path.exists():
            raise FileNotFoundError(f"Fonte do manifest ausente: {path}")
        content = path.read_bytes()
        bytes_count = len(content)
        sha256 = hashlib.sha256(content).hexdigest()
        if bytes_count != entry["bytes"] or sha256 != entry["sha256"]:
            raise ValueError(
                f"Checksum divergente para {path.name}: "
                f"bytes={bytes_count}/{entry['bytes']}, sha256={sha256}/{entry['sha256']}"
            )
        validation[entry["file"]] = {"bytes": bytes_count, "sha256": sha256}
    return validation


def load_sources(source_dir: Path) -> pd.DataFrame:
    frames = []
    for filename in SOURCE_FILES:
        path = source_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fonte ausente: {path}. Execute scripts/download_source.py.")
        frame = pd.read_excel(path, dtype="string", keep_default_na=False)
        frame = frame.drop(columns=[column for column in frame if column.startswith("Unnamed:")], errors="ignore")
        missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
        extra = sorted(set(frame.columns) - set(EXPECTED_COLUMNS))
        if missing:
            raise ValueError(f"{filename}: Colunas obrigatórias ausentes: {missing}")
        if extra:
            raise ValueError(f"{filename}: Colunas não documentadas encontradas: {extra}")
        frame["arquivo_fonte"] = filename
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    missing = sorted(set(EXPECTED_COLUMNS) - set(combined.columns))
    extra = sorted(set(combined.columns) - set(EXPECTED_COLUMNS) - {"arquivo_fonte"})
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    if extra:
        raise ValueError(f"Colunas não documentadas encontradas: {extra}")
    return combined[EXPECTED_COLUMNS + ["arquivo_fonte"]]


def transform(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in EXPECTED_COLUMNS:
        result[column] = result[column].astype("string").str.strip()
    for column in DATE_COLUMNS:
        result[date_column_name(column)] = pd.to_datetime(
            result[column].replace("", pd.NA), format="%Y-%m", errors="coerce"
        )
    result["periodo_emissao"] = result[date_column_name("Data CTPS Gerada")].dt.to_period("M").astype("string")
    result["ano_emissao"] = result[date_column_name("Data CTPS Gerada")].dt.year.astype("Int64")
    result["mes_emissao"] = result[date_column_name("Data CTPS Gerada")].dt.month.astype("Int64")
    result["registro_id"] = pd.util.hash_pandas_object(
        result[EXPECTED_COLUMNS + ["arquivo_fonte"]], index=False
    ).astype("uint64").astype("string")
    return result


def out_of_range_mask(clean: pd.DataFrame, column: str = "Data CTPS Gerada") -> pd.Series:
    """Return valid parsed dates outside the documented analysis period."""
    parsed = clean[date_column_name(column)]
    periods = parsed.dt.to_period("M")
    return parsed.notna() & ((periods < EXPECTED_PERIOD_START) | (periods > EXPECTED_PERIOD_END))


def analysis_scope(clean: pd.DataFrame) -> pd.DataFrame:
    """Select valid generation months in 2020–2022; never mutate the full base."""
    periods = clean[date_column_name("Data CTPS Gerada")].dt.to_period("M")
    return clean.loc[periods.between(EXPECTED_PERIOD_START, EXPECTED_PERIOD_END)].copy()


def nonstandard_uf_counts(clean: pd.DataFrame) -> pd.DataFrame:
    """Keep source categories unchanged; do not infer a state for unknown codes."""
    return (
        clean.loc[~clean["Sigla UF Órgão"].isin(VALID_UFS)]
        .groupby(["arquivo_fonte", "Sigla UF Órgão", "Nome Órgão", "Nome Município Órgão"], dropna=False)
        .size().rename("registros").reset_index()
    )


def _scope_details(clean: pd.DataFrame) -> dict[str, dict[str, object]]:
    details = {}
    for column in SCOPE_DATE_COLUMNS:
        mask = out_of_range_mask(clean, column)
        periods = clean.loc[mask, date_column_name(column)].dt.to_period("M").astype("string")
        details[column] = {
            "records": int(mask.sum()),
            "periods": {str(key): int(value) for key, value in periods.value_counts().sort_index().items()},
            "sources": {str(key): int(value) for key, value in clean.loc[mask, "arquivo_fonte"].value_counts().items()},
        }
    return details


def quality_report(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    scope_details = _scope_details(clean)
    emission_out_of_range = clean.loc[
        out_of_range_mask(clean),
        [
            "arquivo_fonte", "Tipo Protocolo", "Data Protocolo", "Tipo CTPS",
            "Data CTPS Gerada", "Nome Órgão", "Nome Município Órgão",
            "Sigla UF Órgão", "Data Emissão", "Data Nascimento",
            "Sigla UF Nascimento",
        ],
    ].to_dict(orient="records")
    return {
        "input_rows": int(len(raw)), "output_rows": int(len(clean)),
        "input_columns": int(len(set(raw.columns) - {"arquivo_fonte"})), "output_columns": int(len(clean.columns)),
        "rows_removed": int(len(raw) - len(clean)),
        "duplicate_full_rows": int(clean.duplicated(subset=EXPECTED_COLUMNS).sum()),
        "repetition_columns": EXPECTED_COLUMNS,
        "analysis_rows": int(len(analysis_scope(clean))),
        "nonstandard_uf_details": nonstandard_uf_counts(clean).to_dict(orient="records"),
        "empty_values_by_column": {column: int(clean[column].eq("").sum()) for column in EXPECTED_COLUMNS},
        "invalid_dates_by_column": {column: int(clean[date_column_name(column)].isna().sum()) for column in DATE_COLUMNS},
        "source_rows": {str(key): int(value) for key, value in clean["arquivo_fonte"].value_counts().items()},
        "analysis_period": {"start": str(EXPECTED_PERIOD_START), "end": str(EXPECTED_PERIOD_END)},
        "out_of_range_by_date_column": scope_details,
        "out_of_range_emission_records": scope_details["Data CTPS Gerada"]["records"],
        "out_of_range_emission_details": emission_out_of_range,
    }


def make_outputs(clean: pd.DataFrame, output_dir: Path) -> None:
    reports = output_dir.parent.parent / "reports"
    tables, figures = reports / "tables", reports / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    analytical = analysis_scope(clean)
    monthly = analytical.groupby("periodo_emissao", dropna=False).size().rename("registros").reset_index()
    by_state = analytical.groupby("Sigla UF Órgão").size().sort_values(ascending=False).rename("registros").reset_index()
    by_protocol = analytical.groupby("Tipo Protocolo").size().sort_values(ascending=False).rename("registros").reset_index()
    monthly.to_csv(tables / "emissoes_por_mes.csv", index=False)
    by_state.to_csv(tables / "emissoes_por_uf.csv", index=False)
    by_protocol.to_csv(tables / "emissoes_por_protocolo.csv", index=False)
    for slug, column in PROFILE_COLUMNS.items():
        counts = analytical.groupby(column, dropna=False).size().sort_values(ascending=False).rename("registros").reset_index()
        counts["percentual"] = (counts["registros"] / len(analytical) * 100).round(4)
        counts.to_csv(tables / f"emissoes_por_{slug}.csv", index=False)
    nonstandard_uf_counts(clean).to_csv(tables / "ufs_nao_padronizadas.csv", index=False)
    out_of_scope = clean.loc[out_of_range_mask(clean), ["arquivo_fonte"] + EXPECTED_COLUMNS].copy()
    out_of_scope.to_csv(tables / "emissoes_fora_intervalo.csv", index=False)
    number_formatter = FuncFormatter(lambda value, _: f"{int(value):,}".replace(",", "."))
    plt.style.use("default")

    monthly_periods = pd.to_datetime(monthly["periodo_emissao"], format="%Y-%m", errors="coerce").dt.to_period("M")
    monthly_x = list(range(len(monthly)))
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(monthly_x, monthly["registros"], color="#2563eb", marker="o", linewidth=2, markersize=4)
    out_of_scope_months = ~monthly_periods.between(EXPECTED_PERIOD_START, EXPECTED_PERIOD_END)
    if out_of_scope_months.any():
        ax.scatter(
            [monthly_x[index] for index, value in enumerate(out_of_scope_months) if value],
            monthly.loc[out_of_scope_months, "registros"],
            color="#dc2626", zorder=3, label="Fora do período principal",
        )
    tick_positions = list(range(0, len(monthly), 3))
    if monthly_x and monthly_x[-1] not in tick_positions:
        tick_positions.append(monthly_x[-1])
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(monthly.iloc[tick_positions]["periodo_emissao"], rotation=45, ha="right")
    ax.set_title("Registros por mês de geração da CTPS — 2020–2022")
    ax.set_xlabel("Período de geração")
    ax.set_ylabel("Registros publicados")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(number_formatter)
    ax.grid(axis="y", alpha=0.25)
    ax.grid(axis="x", visible=False)
    if out_of_scope_months.any():
        ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(figures / "emissoes_por_mes.png", dpi=180)
    plt.close(fig)

    top_states = by_state.head(10).sort_values("registros")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(top_states["Sigla UF Órgão"], top_states["registros"], color="#2563eb")
    ax.bar_label(bars, labels=[f"{int(value):,}".replace(",", ".") for value in top_states["registros"]], padding=4, fontsize=8)
    ax.set_title("10 UFs com mais registros — 2020–2022")
    ax.set_xlabel("Registros publicados")
    ax.set_ylabel("UF do órgão")
    ax.xaxis.set_major_formatter(number_formatter)
    ax.set_xlim(0, top_states["registros"].max() * 1.18 if not top_states.empty else 1)
    ax.grid(axis="x", alpha=0.25)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(figures / "top_10_ufs.png", dpi=180)
    plt.close(fig)

    lines = ["# Observações calculadas", "", "Os números abaixo foram gerados pelo pipeline. São achados descritivos do conjunto publicado; não evidenciam causalidade ou impacto.", "", "## Achados", ""]
    total = len(analytical)
    lines.append(f"- Registros preservados na base completa: **{len(clean):,}**.")
    lines.append(f"- Recorte analítico de 2020–2022: **{total:,}** registros. Todas as distribuições e participações abaixo usam esse recorte; qualidade e repetições são verificadas na base completa.")
    lines.append(f"- Repetições de registros: **{int(clean.duplicated(subset=EXPECTED_COLUMNS).sum()):,}** linhas excedentes após a primeira ocorrência de cada combinação das 18 colunas de negócio. Todas foram preservadas; a contagem não representa pessoas nem combinações únicas.")
    if not by_state.empty:
        top_uf = by_state.iloc[0]
        top_five_share = by_state.head(5)["registros"].sum() / total
        lines.append(f"- **Distribuição regional:** {top_uf['Sigla UF Órgão']} concentra **{int(top_uf['registros']):,}** registros ({int(top_uf['registros']) / total:.1%} do total). As cinco UFs com mais registros somam **{int(by_state.head(5)['registros'].sum()):,}** linhas ({top_five_share:.1%}).")
    if not by_protocol.empty:
        lines.append(f"- **Tipo de protocolo:** {by_protocol.iloc[0]['Tipo Protocolo']} é o tipo mais frequente, com **{int(by_protocol.iloc[0]['registros']):,}** registros.")
        for protocol in ["1ª Via", "2ª Via"]:
            match = by_protocol.loc[by_protocol["Tipo Protocolo"].eq(protocol), "registros"]
            if not match.empty:
                count = int(match.iloc[0])
                lines.append(f"  - {protocol}: **{count:,}** registros ({count / total:.1%}).")
    in_scope_monthly = monthly.loc[monthly_periods.between(EXPECTED_PERIOD_START, EXPECTED_PERIOD_END)].copy()
    if not in_scope_monthly.empty:
        first = in_scope_monthly.iloc[0]
        last = in_scope_monthly.iloc[-1]
        peak = in_scope_monthly.loc[in_scope_monthly["registros"].idxmax()]
        lines.append(f"- **Evolução observada:** o volume foi de **{int(first['registros']):,}** registros em **{first['periodo_emissao']}** e **{int(last['registros']):,}** em **{last['periodo_emissao']}**; o pico mensal foi **{peak['periodo_emissao']}**, com **{int(peak['registros']):,}** registros.")
        yearly = in_scope_monthly.groupby(in_scope_monthly["periodo_emissao"].str[:4])["registros"].sum()
        lines.append("- **Comparação anual por mês de geração:** " + "; ".join(
            f"{year}: **{int(count):,}** registros" for year, count in yearly.items()
        ) + ". O registro fora do período principal não entra nesta comparação.")
        if len(yearly) > 1 and yearly.iloc[0]:
            change = (yearly.iloc[-1] / yearly.iloc[0] - 1) * 100
            lines.append(f"- A variação de volume entre {yearly.index[0]} e {yearly.index[-1]} foi de **{change:.2f}%**. É uma comparação dos registros publicados, sem atribuição de causa.")
    if not out_of_scope.empty:
        occurrences = out_of_scope.groupby(["Data CTPS Gerada", "arquivo_fonte"]).size()
        detail = "; ".join(f"`{period}` em `{source}`: {count}" for (period, source), count in occurrences.items())
        lines.append(f"- **Qualidade de escopo:** **{len(out_of_scope):,}** registro(s) fora de {EXPECTED_PERIOD_START} a {EXPECTED_PERIOD_END}: {detail}. Preservados em [emissoes_fora_intervalo.csv](tables/emissoes_fora_intervalo.csv).")
    for slug, column in PROFILE_COLUMNS.items():
        counts = analytical[column].value_counts()
        if not counts.empty:
            lines.append(f"- **{column}:** a categoria mais frequente é **{counts.index[0]}**, com **{int(counts.iloc[0]):,}** registros ({counts.iloc[0] / total:.2%}). Distribuição completa em [emissoes_por_{slug}.csv](tables/emissoes_por_{slug}.csv).")
    unusual = nonstandard_uf_counts(clean)
    if not unusual.empty:
        lines.append(f"- **UF não padronizada:** **{int(unusual['registros'].sum()):,}** registros na base completa. Valores originais e origem em [ufs_nao_padronizadas.csv](tables/ufs_nao_padronizadas.csv); nenhum código foi substituído.")
    protocol_before = int((clean[date_column_name("Data Protocolo")].dt.to_period("M") < EXPECTED_PERIOD_START).sum())
    lines.extend(["", "## Possíveis interpretações e limites", "", "- Os resultados mostram como os registros administrativos publicados se distribuem por tempo, UF e protocolo. Não permitem explicar as causas das variações.", "- As mudanças mensais não devem ser interpretadas como evolução do emprego, do mercado de trabalho ou de demanda causal.", f"- `Data Protocolo` tem {protocol_before:,} registros anteriores ao período principal. Essa data histórica é distinta do mês de geração; as ocorrências foram preservadas e reportadas separadamente.", "- A UF é a do órgão emissor, não necessariamente a residência do titular. A categoria IG é mantida sem atribuição de significado.", "- As capturas de Visão Geral e Perfil dos Registros usam 2020–2022 (485.429), em concordância com estas tabelas. O controle de qualidade mantém a base completa de 485.430. Consulte a [documentação do dashboard](../powerbi/dashboard_spec.md)."])
    (reports / "insights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sqlite(clean: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output_dir / "ctps_emissoes.sqlite") as connection:
        clean.to_sql("ctps_emissoes", connection, if_exists="replace", index=False)


def run(source_dir: Path, output_dir: Path) -> dict:
    validate_manifest(Path(__file__).resolve().parents[1] / "data/source_manifest.json", source_dir, SOURCE_FILES)
    raw = load_sources(source_dir)
    clean = transform(raw)
    report = quality_report(raw, clean)
    if report["rows_removed"] != 0 or any(report["invalid_dates_by_column"].values()):
        raise ValueError(f"Falha de qualidade: {report}")
    output_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_dir / "ctps_emissoes.csv", index=False)
    (output_dir / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_sqlite(clean, output_dir)
    make_outputs(clean, output_dir)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    print(json.dumps(run(args.source_dir, args.output_dir), ensure_ascii=False, indent=2))
