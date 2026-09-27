import hashlib
import json
import sqlite3
import shutil
from pathlib import Path
from uuid import uuid4

import pandas as pd
import pytest

import src.ctps_pipeline as pipeline
from src.ctps_pipeline import EXPECTED_COLUMNS, EXPECTED_PERIOD_END, EXPECTED_PERIOD_START


@pytest.fixture
def workdir():
    path = Path.cwd() / ".pytest-local" / uuid4().hex
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def sample_frame(rows: int = 5) -> pd.DataFrame:
    return pd.DataFrame({
        column: ["2020-01" if column.startswith("Data") else "valor"] * rows
        for column in EXPECTED_COLUMNS
    })


def with_source(frame: pd.DataFrame, source: str = "sample.xlsx") -> pd.DataFrame:
    result = frame.copy()
    result["arquivo_fonte"] = source
    return result


def test_transform_creates_month_and_preserves_rows():
    clean = pipeline.transform(with_source(sample_frame()))
    assert len(clean) == 5
    assert clean["periodo_emissao"].eq("2020-01").all()
    assert clean["registro_id"].notna().all()


def test_quality_report_does_not_delete_equal_profiles():
    raw = with_source(sample_frame())
    report = pipeline.quality_report(raw, pipeline.transform(raw))
    assert report["rows_removed"] == 0
    assert report["duplicate_full_rows"] == 4


def test_invalid_date_is_coerced_and_reported():
    raw = with_source(sample_frame(1))
    raw.loc[0, "Data CTPS Gerada"] = "data-invalida"
    clean = pipeline.transform(raw)
    report = pipeline.quality_report(raw, clean)
    assert pd.isna(clean.loc[0, "data_ctps_gerada_date"])
    assert report["invalid_dates_by_column"]["Data CTPS Gerada"] == 1


def test_out_of_range_generation_is_detected_and_preserved():
    raw = with_source(sample_frame(2))
    raw.loc[1, "Data CTPS Gerada"] = "2023-01"
    clean = pipeline.transform(raw)
    report = pipeline.quality_report(raw, clean)
    assert len(clean) == 2
    assert pipeline.out_of_range_mask(clean).sum() == 1
    assert report["out_of_range_emission_records"] == 1
    assert report["out_of_range_by_date_column"]["Data CTPS Gerada"]["periods"] == {"2023-01": 1}
    assert report["out_of_range_emission_details"][0]["Data CTPS Gerada"] == "2023-01"


def test_load_sources_rejects_unexpected_column(monkeypatch, workdir):
    monkeypatch.setattr(pipeline, "SOURCE_FILES", {"sample.xlsx": "https://example.invalid/sample.xlsx"})
    monkeypatch.setattr(pipeline.pd, "read_excel", lambda *args, **kwargs: sample_frame(1).assign(coluna_nova="x"))
    (workdir / "sample.xlsx").touch()
    with pytest.raises(ValueError, match="Colunas não documentadas"):
        pipeline.load_sources(workdir)


def test_load_sources_rejects_missing_required_file(monkeypatch, workdir):
    monkeypatch.setattr(pipeline, "SOURCE_FILES", {"obrigatorio.xlsx": "https://example.invalid/obrigatorio.xlsx"})
    with pytest.raises(FileNotFoundError, match="Fonte ausente"):
        pipeline.load_sources(workdir)


def test_load_sources_rejects_missing_expected_column(monkeypatch, workdir):
    monkeypatch.setattr(pipeline, "SOURCE_FILES", {"sample.xlsx": "https://example.invalid/sample.xlsx"})
    incomplete = sample_frame(1).drop(columns=["Sigla UF Nascimento"])
    monkeypatch.setattr(pipeline.pd, "read_excel", lambda *args, **kwargs: incomplete)
    (workdir / "sample.xlsx").touch()
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        pipeline.load_sources(workdir)


def test_make_outputs_generates_aggregations_figures_and_insights(workdir):
    raw = with_source(sample_frame(3))
    raw.loc[1, "Tipo Protocolo"] = "1ª Via"
    raw.loc[2, "Tipo Protocolo"] = "2ª Via"
    raw.loc[0, "Sigla UF Órgão"] = "MG"
    raw.loc[1, "Sigla UF Órgão"] = "SP"
    clean = pipeline.transform(raw)
    output_dir = workdir / "data" / "processed"
    pipeline.make_outputs(clean, output_dir)
    reports = workdir / "reports"
    assert (reports / "tables" / "emissoes_por_mes.csv").exists()
    assert (reports / "tables" / "emissoes_por_uf.csv").exists()
    assert (reports / "tables" / "emissoes_por_protocolo.csv").exists()
    assert (reports / "tables" / "emissoes_fora_intervalo.csv").exists()
    assert (reports / "figures" / "emissoes_por_mes.png").exists()
    assert "Registros preservados" in (reports / "insights.md").read_text(encoding="utf-8")


def test_sqlite_row_count_matches_dataframe(workdir):
    clean = pipeline.transform(with_source(sample_frame(4)))
    output_dir = workdir / "processed"
    pipeline.write_sqlite(clean, output_dir)
    with sqlite3.connect(output_dir / "ctps_emissoes.sqlite") as connection:
        count = connection.execute("SELECT COUNT(*) FROM ctps_emissoes").fetchone()[0]
    assert count == len(clean)


def test_manifest_validation_is_local_and_hash_based(workdir):
    source_dir = workdir / "raw"
    source_dir.mkdir()
    source = source_dir / "source.xlsx"
    source.write_bytes(b"conteudo de teste")
    manifest = [{
        "file": source.name,
        "url": "https://example.invalid/source.xlsx",
        "bytes": source.stat().st_size,
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }]
    manifest_path = workdir / "source_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = pipeline.validate_manifest(manifest_path, source_dir)
    assert result[source.name]["sha256"] == manifest[0]["sha256"]
    source.write_bytes(b"alterado")
    with pytest.raises(ValueError, match="Checksum divergente"):
        pipeline.validate_manifest(manifest_path, source_dir)


def test_documented_period_bounds_are_explicit():
    assert str(EXPECTED_PERIOD_START) == "2020-01"
    assert str(EXPECTED_PERIOD_END) == "2022-12"
