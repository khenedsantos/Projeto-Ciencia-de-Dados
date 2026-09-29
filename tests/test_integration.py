import os
import shutil
import sqlite3
import struct
from pathlib import Path
from uuid import uuid4

import pytest
import pandas as pd

from src.ctps_pipeline import DATE_COLUMNS, EXPECTED_COLUMNS, PROFILE_COLUMNS, date_column_name, run


@pytest.mark.integration
def test_pipeline_with_local_official_sources():
    source_dir_value = os.environ.get("CTPS_SOURCE_DIR")
    if not source_dir_value:
        pytest.skip("Defina CTPS_SOURCE_DIR para executar o teste de integração com as fontes baixadas.")
    source_dir = Path(source_dir_value)
    # run validates the versioned manifest, including URLs, sizes and SHA-256.
    output_dir = Path.cwd() / ".pytest-local" / uuid4().hex / "data" / "processed"
    try:
        report = run(source_dir, output_dir)
        assert report["input_rows"] == report["output_rows"] == 485430
        assert report["rows_removed"] == 0
        assert report["analysis_rows"] == 485429
        assert report["duplicate_full_rows"] == 25844
        assert not any(report["invalid_dates_by_column"].values())
        assert report["out_of_range_emission_records"] == 1
        assert sum(item["registros"] for item in report["nonstandard_uf_details"]) == 12
        csv = pd.read_csv(output_dir / "ctps_emissoes.csv", dtype="string", keep_default_na=False)
        with sqlite3.connect(output_dir / "ctps_emissoes.sqlite") as connection:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            db = pd.read_sql_query("SELECT * FROM ctps_emissoes", connection).astype("string").fillna("")
            for column in DATE_COLUMNS:
                name = date_column_name(column)
                csv[name] = pd.to_datetime(csv[name])
                db[name] = pd.to_datetime(db[name])
            pd.testing.assert_frame_equal(csv, db)
            sql = (Path(__file__).parents[1] / "sql/analises.sql").read_text(encoding="utf-8")
            queries = [q.strip() for q in sql.split(";") if q.strip()]
            connection.execute(queries[0])
            slugs = ["mes", "uf", "protocolo", *PROFILE_COLUMNS]
            for slug, query in zip(slugs, queries[1:8], strict=True):
                results = connection.execute(query).fetchall()
                actual_counts = {row[0]: row[1] for row in results}
                table = pd.read_csv(output_dir.parent.parent / "reports/tables" / f"emissoes_por_{slug}.csv")
                assert dict(zip(table.iloc[:, 0], table["registros"])) == actual_counts
                assert table["registros"].sum() == 485429
            assert connection.execute(queries[-1]).fetchone()[0] == csv.duplicated(EXPECTED_COLUMNS).sum() == 25844
        reports = output_dir.parent.parent / "reports"
        # Compare text with normalized newlines. PNG bytes can vary by matplotlib version.
        project_reports = Path(__file__).parents[1] / "reports"
        for generated in [*reports.glob("tables/*.csv"), reports / "insights.md"]:
            assert generated.read_text(encoding="utf-8") == (project_reports / generated.relative_to(reports)).read_text(encoding="utf-8")
        for name in ("emissoes_por_mes.png", "top_10_ufs.png"):
            data = (reports / "figures" / name).read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            width, height = struct.unpack(">II", data[16:24])
            assert width > 0 and height > 0
    finally:
        shutil.rmtree(output_dir.parent.parent, ignore_errors=True)
