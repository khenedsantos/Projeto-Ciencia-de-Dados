import os
import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from src.ctps_pipeline import run, validate_manifest


@pytest.mark.integration
def test_pipeline_with_local_official_sources():
    source_dir_value = os.environ.get("CTPS_SOURCE_DIR")
    if not source_dir_value:
        pytest.skip("Defina CTPS_SOURCE_DIR para executar o teste de integração com as fontes baixadas.")
    source_dir = Path(source_dir_value)
    manifest_candidates = [
        source_dir / "source_manifest.json",
        source_dir.parent / "source_manifest.json",
        source_dir / "download-manifest.json",
    ]
    manifest_path = next((path for path in manifest_candidates if path.exists()), None)
    if manifest_path is None:
        pytest.fail("Manifest local não encontrado ao lado das fontes oficiais.")
    validate_manifest(manifest_path, source_dir)
    output_dir = Path.cwd() / ".pytest-local" / uuid4().hex / "processed"
    try:
        report = run(source_dir, output_dir)
        assert report["input_rows"] == report["output_rows"]
        assert report["out_of_range_emission_records"] == 1
    finally:
        shutil.rmtree(output_dir.parent, ignore_errors=True)
