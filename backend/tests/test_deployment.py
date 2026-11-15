import json

import numpy as np
import pandas as pd
import pytest

from backend.app import database
from ml.data import ROOT
from tests.verify_row250 import SUPPLIED


def test_row250_positive_release_regression(client):
    response = client.post("/api/v1/predict", json=SUPPLIED)
    assert response.status_code == 200
    result = response.json()
    assert result["primary_model"] == "rf"
    assert result["predicted_class"] == 1
    assert result["agreement_count"] == 3
    rf = next(item for item in result["models"] if item["id"] == "rf")
    assert np.isclose(rf["potable_probability"], 0.6263747470354587, rtol=0, atol=1e-12)


def test_production_rejects_ephemeral_database(monkeypatch):
    monkeypatch.setattr(database, "PRODUCTION", True)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JALSATHI_DATABASE", raising=False)
    with pytest.raises(RuntimeError, match="durable"):
        database.database_url()
    monkeypatch.setenv("JALSATHI_DATABASE", "sqlite:////tmp/demo.sqlite")
    with pytest.raises(RuntimeError, match="ephemeral"):
        database.database_url()


@pytest.mark.parametrize("scheme", ["postgres://", "postgresql://", "postgresql+psycopg://"])
def test_postgres_url_normalization(monkeypatch, scheme):
    monkeypatch.setattr(database, "PRODUCTION", True)
    monkeypatch.delenv("JALSATHI_DATABASE", raising=False)
    monkeypatch.setenv("DATABASE_URL", scheme + "example:placeholder@db.example/test?sslmode=require")
    assert (
        database.database_url() == "postgresql+psycopg://example:placeholder@db.example/test?sslmode=require"
    )


def test_maximum_batch_fits_serverless_response_limit(client):
    path = ROOT / "tests/fixtures/csv/maximum_supported_batch.csv"
    response = client.post("/api/v1/predict/batch", files={"file": ("maximum.csv", path.read_bytes())})
    assert response.status_code == 200
    assert len(response.content) < 4_500_000
    result = response.json()
    assert result["valid"] == 1000
    first = result["results"][0]
    assert len(first["models"]) == 5 and len(first["measurements"]) == 9
    detail = client.get(first["details_url"]).json()
    assert len(detail["parameters"]) == 9 and detail["decision_path"]
    assert detail["models"] == first["models"]
    assert detail["measurements"] == first["measurements"]


def test_model_and_dataset_fingerprints_unchanged():
    import hashlib

    registry = json.loads((ROOT / "ml/artifacts/registry.json").read_text())
    assert (
        hashlib.sha256((ROOT / "water_potability.csv").read_bytes()).hexdigest()
        == registry["dataset"]["sha256"]
    )
    original = pd.read_csv(ROOT / "water_potability.csv")
    assert original.iloc[250].Potability == 1
