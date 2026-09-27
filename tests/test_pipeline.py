import pandas as pd

from src.ctps_pipeline import EXPECTED_COLUMNS, transform, quality_report


def sample_frame(rows: int = 5) -> pd.DataFrame:
    return pd.DataFrame({column: ["2020-01" if column.startswith("Data") else "valor"] * rows for column in EXPECTED_COLUMNS})


def test_transform_creates_month_and_preserves_rows():
    raw = sample_frame()
    raw["arquivo_fonte"] = "sample.xlsx"
    clean = transform(raw)
    assert len(clean) == 5
    assert clean["periodo_emissao"].eq("2020-01").all()
    assert clean["registro_id"].notna().all()


def test_quality_report_does_not_delete_equal_profiles():
    raw = sample_frame()
    raw["arquivo_fonte"] = "sample.xlsx"
    clean = transform(raw)
    report = quality_report(raw, clean)
    assert report["rows_removed"] == 0
    assert report["duplicate_full_rows"] == 4
