"""Exercise the unauthenticated public deployment, never bypassing deployment protection."""

import argparse
import csv
import io
import json
import time

import httpx
import numpy as np
import pymupdf

from ml.data import ROOT
from tests.verify_row250 import SUPPLIED


def run(url):
    out = ROOT / "reports/testing/PRODUCTION_API_RESULTS.json"
    previous = json.loads(out.read_text()) if out.exists() else None
    checks = []

    def check(name, passed):
        checks.append({"name": name, "passed": bool(passed)})
        assert passed, name

    started = time.perf_counter()
    with httpx.Client(base_url=url, timeout=90, follow_redirects=True) as client:
        for route in ["/", "/dashboard", "/analyze", "/models", "/batch", "/reports", "/about"]:
            response = client.get(route)
            check("public SPA " + route, response.status_code == 200 and 'id="root"' in response.text)
        health = client.get("/api/v1/health")
        check("health HTTP 200", health.status_code == 200)
        health = health.json()
        check("five fitted models loaded", health["models_available"] and len(health["loaded_models"]) == 5)
        check(
            "durable PostgreSQL persistence",
            health["database"] == "postgresql" and health["persistent_history"],
        )
        metadata = client.get("/api/v1/models").json()
        registry = json.loads((ROOT / "ml/artifacts/registry.json").read_text())
        check(
            "primary and saved metrics match",
            metadata["primary"] == "rf" and metadata["models"] == registry["models"],
        )
        dataset = client.get("/api/v1/dataset/summary").json()
        check(
            "genuine dataset statistics",
            dataset["rows"] == 3276 and dataset["sha256"] == registry["dataset"]["sha256"],
        )
        positive = client.post("/api/v1/predict", json=SUPPLIED)
        check("row250 HTTP 200", positive.status_code == 200)
        positive = positive.json()
        check("row250 potable", positive["predicted_class"] == 1 and positive["primary_model"] == "rf")
        check(
            "row250 probability unchanged",
            np.isclose(positive["selected_class_probability"], 0.6263747470354587, rtol=0, atol=1e-12),
        )
        check("row250 agreement", positive["agreement_count"] == 3)
        check("row250 exact values", positive["measurements"] == SUPPLIED)
        negative_source = json.loads((ROOT / "reports/testing/verified_potable_evidence.json").read_text())[
            "examples"
        ]["nonpotable"][0]
        negative = client.post("/api/v1/predict", json=negative_source["measurements"])
        check("negative HTTP 200", negative.status_code == 200)
        negative = negative.json()
        check("genuine nonpotable", negative["predicted_class"] == 0)
        negative_rf = next(item for item in negative["models"] if item["id"] == "rf")
        check(
            "negative probability unchanged",
            np.isclose(
                negative_rf["potable_probability"], negative_source["primary_probability"], rtol=0, atol=1e-12
            ),
        )
        samples = ROOT / "tests/fixtures/verified_potable_samples.csv"
        batch = client.post(
            "/api/v1/predict/batch", files={"file": (samples.name, samples.read_bytes(), "text/csv")}
        )
        check("batch HTTP 200", batch.status_code == 200)
        batch = batch.json()
        check("five positive CSV samples", batch["valid"] == batch["potable"] == 5 and batch["invalid"] == 0)
        expected = json.loads((ROOT / "reports/testing/verified_potable_evidence.json").read_text())[
            "examples"
        ]["potable"]
        check(
            "batch probabilities unchanged",
            all(
                np.isclose(
                    item["selected_class_probability"], sample["primary_probability"], rtol=0, atol=1e-12
                )
                for item, sample in zip(batch["results"], expected)
            ),
        )
        export = client.get("/api/v1/batches/" + batch["batch_id"] + "/csv")
        check(
            "CSV export matches",
            export.status_code == 200 and len(list(csv.DictReader(io.StringIO(export.text)))) == 5,
        )
        malformed = client.post(
            "/api/v1/predict/batch", files={"file": ("malformed.csv", b"ph\n7", "text/csv")}
        )
        check("malformed CSV safely rejected", malformed.status_code == 422)
        pdf = client.get("/api/v1/reports/" + positive["analysis_id"] + "/pdf")
        check("PDF HTTP 200", pdf.status_code == 200 and pdf.content.startswith(b"%PDF-"))
        doc = pymupdf.open(stream=pdf.content, filetype="pdf")
        text = " ".join(" ".join(page.get_text() for page in doc).split())
        check(
            "PDF correct values and identity",
            all(str(value) in text for value in SUPPLIED.values())
            and positive["analysis_id"] in text
            and positive["label"] in text
            and positive["version"] in text,
        )
        check("PDF scientific limitations", "Laboratory testing" in text and "uncalibrated" in text)
        for plot in ["cart-tree.png", "gam-effects.png", "rf-evaluation.png"]:
            response = client.get("/api/v1/plots/" + plot)
            check(
                "real plot " + plot, response.status_code == 200 and response.content.startswith(b"\x89PNG")
            )
        for uuid in [positive["analysis_id"], negative["analysis_id"]]:
            response = client.get("/api/v1/analyses/" + uuid)
            check(
                "saved history " + uuid,
                response.status_code == 200 and response.json()["analysis_id"] == uuid,
            )
        if previous and previous["url"] == url:
            response = client.get("/api/v1/analyses/" + previous["positive_analysis_id"])
            check("history survives later verification/deployment", response.status_code == 200)
    # A fresh network client retrieves the same persisted record.
    with httpx.Client(timeout=60) as fresh:
        result = fresh.get(url + "/api/v1/analyses/" + positive["analysis_id"])
        check("fresh client persistent snapshot", result.status_code == 200 and result.json() == positive)
    evidence = dict(
        url=url,
        passed=len(checks),
        total=len(checks),
        checks=checks,
        health=health,
        positive_analysis_id=positive["analysis_id"],
        positive_probability=positive["selected_class_probability"],
        negative_analysis_id=negative["analysis_id"],
        batch_id=batch["batch_id"],
        elapsed_seconds=time.perf_counter() - started,
        persistence="Neon PostgreSQL",
    )
    out.write_text(json.dumps(evidence, indent=2))
    print(json.dumps({key: value for key, value in evidence.items() if key != "checks"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    run(parser.parse_args().url.rstrip("/"))
