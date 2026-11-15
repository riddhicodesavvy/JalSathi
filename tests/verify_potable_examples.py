"""Find original rows using the trusted deployed RF pipeline, then verify the live API."""

import csv
import hashlib
import io
import json
from datetime import datetime, timezone

import httpx
import numpy as np
import pandas as pd

from backend.app.inference import Registry
from backend.app.standards import check_parameters
from ml.data import FEATURES, ROOT

OUT = ROOT / "reports/testing"
FIXTURE = ROOT / "tests/fixtures/verified_potable_samples.csv"


def run():
    registry = Registry()
    registry.require()
    assert registry.metadata["primary"] == "rf"
    original_bytes = (ROOT / "water_potability.csv").read_bytes()
    digest = hashlib.sha256(original_bytes).hexdigest()
    assert digest == registry.metadata["dataset"]["sha256"]
    artifact_hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in registry.directory.glob("*.joblib")
    }
    # Keep original CSV lexemes for the upload fixture and report; use full round-trip
    # floating-point values for direct inference and the JSON API.
    with (ROOT / "water_potability.csv").open(newline="", encoding="utf-8-sig") as stream:
        original = list(csv.DictReader(stream))
    complete = [(index, row) for index, row in enumerate(original) if all(row[c].strip() for c in FEATURES)]
    values = pd.DataFrame([{c: float(row[c]) for c in FEATURES} for _, row in complete], columns=FEATURES)
    rf = registry.models["rf"]
    assert rf.feature_names_in_.tolist() == FEATURES and rf.classes_.tolist() == [0, 1]
    probabilities = rf.predict_proba(values)[:, 1]
    candidates = [
        i for i, (_, row) in enumerate(complete) if row["Potability"] == "1" and probabilities[i] >= 0.5
    ]
    negatives = [
        i for i, (_, row) in enumerate(complete) if row["Potability"] == "0" and probabilities[i] < 0.5
    ]
    positive_order = sorted(candidates, key=lambda i: (-probabilities[i], complete[i][0]))[:5]
    negative_order = sorted(negatives, key=lambda i: (probabilities[i], complete[i][0]))[:5]
    assert len(positive_order) == len(negative_order) == 5, (len(candidates), len(negatives))
    groups = {"potable": positive_order, "nonpotable": negative_order}
    result = dict(
        generated_at=datetime.now(timezone.utc).isoformat(),
        dataset_sha256=digest,
        artifact_hashes=artifact_hashes,
        primary_model="rf",
        version=registry.metadata["version"],
        threshold=0.5,
        complete_rows=len(complete),
        qualifying_positive_labeled_rows=len(candidates),
        qualifying_negative_labeled_rows=len(negatives),
        selection="Top five class-1 probabilities among complete original label-1 rows; "
        "five lowest probabilities among complete original label-0 rows. "
        "These are selected demonstrations, not unbiased evaluation.",
        examples={},
    )
    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=60) as client:
        health = client.get("/health")
        health.raise_for_status()
        assert health.json()["models_available"]
        deployed = client.get("/models").json()
        assert deployed["primary"] == "rf" and deployed["version"] == registry.metadata["version"]
        for group, indices in groups.items():
            entries = []
            for number, position in enumerate(indices, 1):
                index, original_row = complete[position]
                sample = {c: float(original_row[c]) for c in FEATURES}
                direct = {
                    key: float(model.predict_proba(pd.DataFrame([sample], columns=FEATURES))[0, 1])
                    for key, model in registry.models.items()
                }
                response = client.post("/predict", json=sample)
                response.raise_for_status()
                api = response.json()
                expected_class = 1 if group == "potable" else 0
                assert api["primary_model"] == "rf" and api["predicted_class"] == expected_class
                assert api["version"] == registry.metadata["version"] and api["measurements"] == sample
                for model in api["models"]:
                    assert np.isclose(model["potable_probability"], direct[model["id"]], rtol=0, atol=1e-12)
                    assert model["predicted_class"] == int(direct[model["id"]] >= 0.5)
                primary = next(model for model in api["models"] if model["id"] == "rf")
                assert primary["predicted_class"] == expected_class
                agreement = sum(model["predicted_class"] == expected_class for model in api["models"])
                assert (
                    api["agreement_count"] == agreement and api["agreement_percentage"] == agreement / 5 * 100
                )
                assert api["parameters"] == check_parameters(sample)
                saved = client.get("/analyses/" + api["analysis_id"]).json()
                assert saved == api
                report = client.get(f"/reports/{api['analysis_id']}/pdf")
                report.raise_for_status()
                import pymupdf

                doc = pymupdf.open(stream=report.content, filetype="pdf")
                text = " ".join(" ".join(page.get_text() for page in doc).split())
                assert api["analysis_id"] in text and api["label"] in text
                assert all(str(value) in text for value in sample.values())
                assert "Laboratory testing" in text and "uncalibrated" in text
                entries.append(
                    dict(
                        number=number,
                        dataset_index=index,
                        csv_line=index + 2,
                        partition="test" if index in registry.metadata["test_indices"] else "training",
                        original_label=int(original_row["Potability"]),
                        original_values={c: original_row[c] for c in FEATURES},
                        measurements=sample,
                        direct_probabilities=direct,
                        primary_probability=direct["rf"],
                        api_verified=True,
                        report_verified=True,
                        api_result=api,
                    )
                )
                print(group, number, "index", index, "P(class 1)", repr(direct["rf"]), "agreement", agreement)
            result["examples"][group] = entries
        # The exported fixture is validated by the actual batch endpoint as well.
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=FEATURES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(entry["original_values"] for entry in result["examples"]["potable"])
        FIXTURE.write_text(stream.getvalue(), encoding="utf-8", newline="")
        batch_response = client.post(
            "/predict/batch", files={"file": (FIXTURE.name, FIXTURE.read_bytes(), "text/csv")}
        )
        batch_response.raise_for_status()
        batch = batch_response.json()
        assert batch["valid"] == batch["potable"] == 5 and batch["invalid"] == 0
        for entry, item in zip(result["examples"]["potable"], batch["results"]):
            rf_result = next(m for m in item["models"] if m["id"] == "rf")
            assert np.isclose(
                rf_result["potable_probability"], entry["primary_probability"], rtol=0, atol=1e-12
            )
        result["batch_verified"] = dict(id=batch["batch_id"], potable=5, valid=5, mismatches=0)
    assert hashlib.sha256((ROOT / "water_potability.csv").read_bytes()).hexdigest() == digest
    for name, fingerprint in artifact_hashes.items():
        assert hashlib.sha256((registry.directory / name).read_bytes()).hexdigest() == fingerprint
    (OUT / "verified_potable_evidence.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )
    print("Verified 5 positive and 5 negative examples against live API and reports. Models unchanged.")


if __name__ == "__main__":
    run()
