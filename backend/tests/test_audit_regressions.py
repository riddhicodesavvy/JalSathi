import csv
import io

import numpy as np
import pandas as pd
import pytest

from backend.app.csv_export import safe_csv_cell
from ml.data import FEATURES, ROOT


@pytest.mark.parametrize("value", ["=1+1", "+SUM(A1)", "-CMD()", "@IMPORT()", "\t=1", "\r=1", "  =1+2"])
def test_csv_text_escaped(value):
    assert safe_csv_cell(value).startswith("'")


def test_csv_numeric_cells_unchanged():
    assert safe_csv_cell(123.45) == 123.45
    assert safe_csv_cell("Predicted Potable") == "Predicted Potable"


def test_report_retains_nine_full_precision_values(client):
    import pymupdf

    frame = pd.read_csv(ROOT / "tests/fixtures/csv/balanced_labeled_100.csv")
    sample = frame.iloc[0].to_dict()
    result = client.post("/api/v1/predict", json=sample).json()
    response = client.get(f"/api/v1/reports/{result['analysis_id']}/pdf")
    doc = pymupdf.open(stream=response.content, filetype="pdf")
    text = " ".join(" ".join(page.get_text() for page in doc).split())
    for value in sample.values():
        assert str(value) in text


def test_50_labeled_rows_single_batch_parity(client):
    frame = pd.read_csv(ROOT / "tests/fixtures/csv/balanced_labeled_100.csv").head(50)
    batch = client.post(
        "/api/v1/predict/batch", files={"file": ("parity.csv", frame.to_csv(index=False).encode())}
    ).json()
    assert batch["valid"] == 50
    for i, (_, row) in enumerate(frame.iterrows()):
        single = client.post("/api/v1/predict", json=row.to_dict()).json()
        other = batch["results"][i]
        assert single["version"] == other["version"]
        assert single["primary_model"] == other["primary_model"]
        assert single["decision_path"] == other["decision_path"]
        assert all(
            np.isclose(single["measurements"][c], other["measurements"][c], rtol=0, atol=1e-10)
            for c in FEATURES
        )
        for left, right in zip(single["models"], other["models"]):
            assert left["id"] == right["id"]
            assert left["predicted_class"] == right["predicted_class"]
            assert np.isclose(left["potable_probability"], right["potable_probability"], rtol=0, atol=1e-12)


def test_duplicate_rows_retained_in_order(client, sample):
    response = client.post(
        "/api/v1/predict/batch",
        files={"file": ("duplicates.csv", pd.DataFrame([sample] * 3).to_csv(index=False).encode())},
    )
    payload = response.json()
    assert payload["valid"] == 3 and payload["invalid"] == 0
    assert [r["row"] for r in payload["results"]] == [2, 3, 4]
    assert len({r["analysis_id"] for r in payload["results"]}) == 3
    export = client.get(f"/api/v1/batches/{payload['batch_id']}/csv")
    rows = list(csv.DictReader(io.StringIO(export.text)))
    assert len(rows) == 3
