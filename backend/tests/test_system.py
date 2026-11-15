import csv
import io
import json

import joblib
import numpy as np
import pytest
from fastapi import HTTPException

from backend.app.inference import Registry
from ml.data import FEATURES, ROOT, load_dataset


def test_dataset_and_preserved_eda():
    frame, fingerprint = load_dataset()
    assert frame.shape == (3276, 10)
    assert len(fingerprint) == 64
    assert frame.Potability.value_counts().to_dict() == {0: 1998, 1: 1278}
    assert frame.ph.isna().sum() == 491
    assert (ROOT / "reports/eda/generate_eda.py").is_file()


def test_invalid_schema(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("ph,Potability\n7,1\n")
    with pytest.raises(ValueError, match="columns"):
        load_dataset(bad)


def test_training_isolation_and_artifacts():
    metadata = json.loads((ROOT / "ml/artifacts/registry.json").read_text())
    json.dumps(metadata, allow_nan=False)
    assert set(metadata["train_indices"]).isdisjoint(metadata["test_indices"])
    assert len(metadata["train_indices"]) + len(metadata["test_indices"]) == 3276
    frame, _ = load_dataset()
    train = frame.loc[metadata["train_indices"], FEATURES]
    for key in ["cart", "rf", "ada", "gb"]:
        model = joblib.load(ROOT / f"ml/artifacts/{key}.joblib")
        assert model.feature_names_in_.tolist() == FEATURES
        assert np.allclose(model.named_steps["imputer"].statistics_, train.median().to_numpy())
        p = model.predict_proba(frame[FEATURES].iloc[:5])
        assert p.shape == (5, 2)
        assert np.isfinite(p).all() and np.allclose(p.sum(axis=1), 1)


def test_health_and_metadata(client):
    assert client.get("/api/v1/health").json()["models_available"]
    response = client.get("/api/v1/models")
    assert response.status_code == 200, response.text
    models = response.json()
    assert len(models["models"]) == 5
    for item in models["models"]:
        assert 0 <= item["metrics"]["balanced_accuracy"] <= 1
    assert client.get("/api/v1/models/metrics").status_code == 200
    assert client.get("/api/v1/models/cart").status_code == 200
    assert client.get("/api/v1/models/absent").status_code == 404
    assert client.get("/api/v1/dataset/summary").json()["rows"] == 3276
    assert len(client.get("/api/v1/features").json()) == 9


def test_prediction_history_and_report(client, sample):
    response = client.post("/api/v1/predict", json=sample)
    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result["models"]) == 5
    assert 0 <= result["selected_class_probability"] <= 1
    assert result["agreement_count"] == sum(
        m["predicted_class"] == result["predicted_class"] for m in result["models"]
    )
    assert result["decision_path"]
    assert sum(p["status"] == "unknown" for p in result["parameters"]) == 8
    identifier = result["analysis_id"]
    assert client.get("/api/v1/analyses").json()["total"] == 1
    assert client.get(f"/api/v1/analyses/{identifier}").json()["measurements"] == sample
    report = client.get(f"/api/v1/reports/{identifier}/pdf")
    assert report.status_code == 200
    assert report.content.startswith(b"%PDF-")
    import pymupdf

    pdf = pymupdf.open(stream=report.content, filetype="pdf")
    text = "".join(p.get_text() for p in pdf)
    assert identifier in text and result["label"] in text
    assert "Laboratory testing" in " ".join(text.split())
    for page in pdf:
        if "Model comparison" in page.get_text():
            assert "Classifier" in page.get_text() and "CART" in page.get_text()


@pytest.mark.parametrize(
    "patch",
    [
        {"ph": -1},
        {"ph": 15},
        {"Hardness": -1},
        {"Solids": "NaN"},
        {"ph": None},
        {"Turbidity": "Infinity"},
        {"Potability": 1},
    ],
)
def test_invalid_inputs(client, sample, patch):
    sample.update(patch)
    r = client.post("/api/v1/predict", json=sample)
    assert r.status_code == 422
    assert "error" in r.json()


def test_missing_fields(client):
    assert client.post("/api/v1/predict", json={}).status_code == 422


def csv_bytes(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FEATURES)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def test_batch_valid_invalid_and_export(client, sample):
    bad = {**sample, "ph": "NaN"}
    response = client.post(
        "/api/v1/predict/batch", files={"file": ("measurements.csv", csv_bytes([sample, bad]), "text/csv")}
    )
    assert response.status_code == 200, response.text
    result = response.json()
    assert (result["valid"], result["invalid"], result["total"]) == (1, 1, 2)
    assert result["errors"][0]["row"] == 3
    single = client.post("/api/v1/predict", json=sample).json()
    assert single["models"] == result["results"][0]["models"]
    export = client.get(f"/api/v1/batches/{result['batch_id']}/csv")
    assert export.status_code == 200 and "model_probability" in export.text


@pytest.mark.parametrize(
    "name,body,status",
    [
        ("bad.txt", b"a", 415),
        ("bad.csv", b"ph\n7", 422),
        ("empty.csv", ",".join(FEATURES).encode(), 422),
        ("bad.csv", b"\xff", 422),
        ("large.csv", b"x" * 2_000_001, 413),
        ("dup.csv", b"ph,ph\n7,7", 422),
    ],
)
def test_batch_rejection(client, name, body, status):
    assert client.post("/api/v1/predict/batch", files={"file": (name, body)}).status_code == status


def test_missing_registry(tmp_path, client, sample):
    registry = Registry(tmp_path)
    with pytest.raises(HTTPException) as exc:
        registry.require()
    assert exc.value.status_code == 503
    client.app.state.registry = registry
    assert client.get("/api/v1/health").json()["models_available"] is False
    assert client.post("/api/v1/predict", json=sample).status_code == 503


def test_guideline_breach_and_distribution(client, sample):
    result = client.post("/api/v1/predict", json={**sample, "ph": 0, "Solids": 1e8}).json()
    assert result["parameters"][0]["status"] == "outside"
    assert any("outside observed training range" in w for w in result["warnings"])


def test_unavailable_resources(client):
    assert "error" in client.get("/api/v1/unknown").json()
    assert client.get("/api/v1/plots/not-allowed.png").status_code == 404
    assert client.get("/api/v1/plots/cart-tree.png").status_code == 200
    assert client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/api/v1/analyses?limit=500").status_code == 422
