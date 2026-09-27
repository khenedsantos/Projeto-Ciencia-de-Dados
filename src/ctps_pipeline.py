from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

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


def load_sources(source_dir: Path) -> pd.DataFrame:
    frames = []
    for filename in SOURCE_FILES:
        path = source_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fonte ausente: {path}. Execute scripts/download_source.py.")
        frame = pd.read_excel(path, dtype="string", keep_default_na=False)
        frame = frame.drop(columns=[column for column in frame if column.startswith("Unnamed:")], errors="ignore")
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


def quality_report(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    return {
        "input_rows": int(len(raw)), "output_rows": int(len(clean)),
        "input_columns": int(len(raw.columns) - 1), "output_columns": int(len(clean.columns)),
        "rows_removed": int(len(raw) - len(clean)),
        "duplicate_full_rows": int(raw.duplicated(subset=EXPECTED_COLUMNS).sum()),
        "empty_values_by_column": {column: int(clean[column].eq("").sum()) for column in EXPECTED_COLUMNS},
        "invalid_dates_by_column": {column: int(clean[date_column_name(column)].isna().sum()) for column in DATE_COLUMNS},
        "source_rows": {str(key): int(value) for key, value in clean["arquivo_fonte"].value_counts().items()},
    }


def make_outputs(clean: pd.DataFrame, output_dir: Path) -> None:
    reports = output_dir.parent.parent / "reports"
    tables, figures = reports / "tables", reports / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    monthly = clean.groupby("periodo_emissao", dropna=False).size().rename("registros").reset_index()
    by_state = clean.groupby("Sigla UF Órgão").size().sort_values(ascending=False).rename("registros").reset_index()
    by_protocol = clean.groupby("Tipo Protocolo").size().sort_values(ascending=False).rename("registros").reset_index()
    monthly.to_csv(tables / "emissoes_por_mes.csv", index=False)
    by_state.to_csv(tables / "emissoes_por_uf.csv", index=False)
    by_protocol.to_csv(tables / "emissoes_por_protocolo.csv", index=False)
    chart_specs = [
        (monthly, "emissoes_por_mes.png", "Registros por mês de geração da CTPS", "periodo_emissao"),
        (by_state.head(10), "top_10_ufs.png", "10 UFs com mais registros", "Sigla UF Órgão"),
    ]
    for data, filename, title, x in chart_specs:
        plt.figure(figsize=(11, 5))
        plt.bar(data[x].astype(str), data["registros"])
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel("Registros publicados")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(figures / filename, dpi=160)
        plt.close()
    lines = ["# Observações calculadas", "", "Os números abaixo foram gerados pelo pipeline; não são metas nem impactos causais.", ""]
    lines.append(f"- Registros preservados: **{len(clean):,}**.")
    lines.append(f"- Registros com o mesmo perfil em todas as colunas de negócio: **{int(clean.duplicated(subset=EXPECTED_COLUMNS).sum()):,}**; eles foram preservados por falta de identificador de atendimento.")
    if not by_state.empty:
        lines.append(f"- UF com maior volume no conjunto: **{by_state.iloc[0]['Sigla UF Órgão']}**, com **{int(by_state.iloc[0]['registros']):,}** registros.")
    if not by_protocol.empty:
        lines.append(f"- Tipo de protocolo mais frequente: **{by_protocol.iloc[0]['Tipo Protocolo']}**, com **{int(by_protocol.iloc[0]['registros']):,}** registros.")
    (reports / "insights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sqlite(clean: pd.DataFrame, output_dir: Path) -> None:
    with sqlite3.connect(output_dir / "ctps_emissoes.sqlite") as connection:
        clean.to_sql("ctps_emissoes", connection, if_exists="replace", index=False)


def run(source_dir: Path, output_dir: Path) -> dict:
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
