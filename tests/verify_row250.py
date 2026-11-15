"""Verify the user's rounded row-250 measurements against the deployed RF and API."""

import csv
import hashlib
import json
from datetime import datetime, timezone

import httpx
import numpy as np
import pandas as pd

from backend.app.inference import Registry
from ml.data import FEATURES, ROOT

SUPPLIED = dict(
    ph=9.445130,
    Hardness=145.805402,
    Solids=13168.529156,
    Chloramines=9.444471,
    Sulfate=310.583374,
    Conductivity=592.659021,
    Organic_carbon=8.606397,
    Trihalomethanes=77.577460,
    Turbidity=3.875165,
)


def run():
    registry = Registry()
    registry.require()
    assert registry.metadata["primary"] == "rf"
    with (ROOT / "water_potability.csv").open(newline="", encoding="utf-8-sig") as stream:
        original = list(csv.DictReader(stream))[250]
    assert int(original["Potability"]) == 1
    full_precision = {c: float(original[c]) for c in FEATURES}
    assert all(abs(full_precision[c] - SUPPLIED[c]) <= 0.0000005 for c in FEATURES)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in registry.directory.glob("*.joblib")}
    evidence = dict(
        checked_at=datetime.now(timezone.utc).isoformat(),
        dataset_index=250,
        csv_line=252,
        original_label=1,
        primary_model="rf",
        version=registry.metadata["version"],
        threshold=0.5,
        original_csv_values={c: original[c] for c in FEATURES},
        artifact_hashes=hashes,
        cases={},
    )
    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=30) as client:
        active = client.get("/models")
        active.raise_for_status()
        assert active.json()["primary"] == "rf" and active.json()["version"] == evidence["version"]
        for name, values in [("supplied_rounded", SUPPLIED), ("original_full_precision", full_precision)]:
            frame = pd.DataFrame([values], columns=FEATURES)
            model = registry.models["rf"]
            probability = float(model.predict_proba(frame)[0, 1])
            prediction = int(model.predict(frame)[0])
            response = client.post("/predict", json=values)
            response.raise_for_status()
            api = response.json()
            rf = next(item for item in api["models"] if item["id"] == "rf")
            assert api["measurements"] == values
            assert api["primary_model"] == "rf" and api["predicted_class"] == prediction
            assert rf["predicted_class"] == prediction
            assert np.isclose(rf["potable_probability"], probability, rtol=0, atol=1e-12)
            assert api["agreement_count"] == sum(m["predicted_class"] == prediction for m in api["models"])
            evidence["cases"][name] = dict(
                measurements=values,
                direct_class=prediction,
                direct_potable_probability=probability,
                api_verified=True,
                api=api,
            )
            print(
                name,
                "class",
                prediction,
                "P(class 1)",
                repr(probability),
                "agreement",
                api["agreement_count"],
            )
        # Revalidate the existing genuine five-example upload fixture using this live deployment.
        path = ROOT / "tests/fixtures/verified_potable_samples.csv"
        response = client.post("/predict/batch", files={"file": (path.name, path.read_bytes(), "text/csv")})
        response.raise_for_status()
        batch = response.json()
        assert batch["valid"] == batch["potable"] == 5 and batch["invalid"] == 0
        entries = []
        for item in batch["results"]:
            frame = pd.DataFrame([item["measurements"]], columns=FEATURES)
            p = float(registry.models["rf"].predict_proba(frame)[0, 1])
            assert p >= 0.5 and np.isclose(
                next(m["potable_probability"] for m in item["models"] if m["id"] == "rf"),
                p,
                rtol=0,
                atol=1e-12,
            )
            entries.append(dict(measurements=item["measurements"], potable_probability=p))
        evidence["additional_five_verified"] = entries
    assert all(
        hashlib.sha256((registry.directory / name).read_bytes()).hexdigest() == digest
        for name, digest in hashes.items()
    )
    (ROOT / "reports/testing/ROW_250_VERIFICATION.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    print("Row 250 API checks and existing five-example CSV checks passed. No model changes.")


if __name__ == "__main__":
    run()
