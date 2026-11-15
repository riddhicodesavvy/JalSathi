"""Run an evidence-producing audit on a separate SQLite database, never user history."""

import csv
import hashlib
import io
import json
import logging
import os
import platform
import time
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
    precision_recall_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from ml.data import FEATURES, ROOT, load_dataset
from ml.train import metrics
from tests.generate_test_csvs import CSV, OUT, REFERENCE, generate

REPORTS = ROOT / "reports/testing"
os.environ["JALSATHI_DATABASE"] = f"sqlite:///{(ROOT / 'runtime/qa-audit.sqlite').as_posix()}"
os.environ["JALSATHI_REPORTS"] = str(ROOT / "runtime/qa-audit-reports")


def dump(name, value):
    (REPORTS / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def probability_stats(p):
    return dict(
        count=len(p),
        predicted_potable=int((p >= 0.5).sum()),
        predicted_nonpotable=int((p < 0.5).sum()),
        unique_probabilities=int(len(np.unique(p))),
        min=float(p.min()),
        max=float(p.max()),
        mean=float(p.mean()),
        std=float(p.std()),
        quantiles=np.quantile(p, [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]).tolist(),
    )


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not (REPORTS / "baseline_hashes.json").exists():
        files = [
            ROOT / "water_potability.csv",
            ROOT / "ml/artifacts/registry.json",
            *(ROOT / "ml/artifacts").glob("*.joblib"),
        ]
        dump(
            "baseline_hashes.json",
            {
                file.relative_to(ROOT).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
                for file in files
            },
        )
    generate()
    checks, failures = [], []

    def check(name, condition, detail=""):
        checks.append(dict(name=name, passed=bool(condition), detail=detail))
        if not condition:
            failures.append(name)
        return bool(condition)

    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.schemas import Sample
    from backend.app.inference import Registry

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("jalsathi").setLevel(logging.WARNING)
    frame, fingerprint = load_dataset()
    metadata = json.loads((ROOT / "ml/artifacts/registry.json").read_text())
    start = time.perf_counter()
    registry = Registry()
    loading = time.perf_counter() - start
    train = frame.loc[metadata["train_indices"]]
    test = frame.loc[metadata["test_indices"]]
    x, y = test[FEATURES], test.Potability
    check("split indices disjoint", set(train.index).isdisjoint(test.index))
    check(
        "reproduce original stratified split",
        set(train_test_split(frame.index, test_size=0.2, stratify=frame.Potability, random_state=42)[1])
        == set(test.index),
    )
    check(
        "primary chosen by training CV",
        max(metadata["models"], key=lambda m: (m["cv_balanced_accuracy"], -m["cv_brier"]))["id"]
        == metadata["primary"],
    )
    check("five distinct loaded objects", len({id(m) for m in registry.models.values()}) == 5)
    health = {}
    probabilities = {}
    for item in metadata["models"]:
        key = item["id"]
        model = registry.models[key]
        p = model.predict_proba(x)[:, 1]
        probabilities[key] = p
        actual = metrics(y, p)
        tn, fp, fn, tp = np.array(actual["confusion_matrix"]).ravel()
        for metric in [
            "accuracy",
            "precision",
            "recall",
            "f1",
            "balanced_accuracy",
            "roc_auc",
            "pr_auc",
            "brier",
            "false_potable_rate",
        ]:
            check(
                f"{key} stored {metric} reproduces",
                np.isclose(actual[metric], item["metrics"][metric], atol=1e-12),
            )
        check(f"{key} class ordering", model.classes_.tolist() == [0, 1])
        check(f"{key} feature order", model.feature_names_in_.tolist() == FEATURES)
        check(f"{key} valid probabilities", np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all())
        check(
            f"{key} raw predict matches threshold", np.array_equal(model.predict(x), (p >= 0.5).astype(int))
        )
        for curve, computed in [
            ("roc", roc_curve(y, p)[:2]),
            ("pr", (precision_recall_curve(y, p)[1], precision_recall_curve(y, p)[0])),
        ]:
            saved = np.array([[v["x"], v["y"]] for v in item[curve]])
            check(f"{key} saved {curve} curve reproduces", np.allclose(saved, np.array(computed).T))
        if key != "voting":
            check(
                f"{key} training-only imputation",
                np.allclose(model.named_steps["imputer"].statistics_, train[FEATURES].median()),
            )
            check(
                f"{key} missing training/test input handled",
                np.isfinite(model.predict_proba(x.iloc[:3].assign(Sulfate=np.nan))).all(),
            )
        health[key] = dict(
            name=item["name"],
            metrics=actual,
            probabilities=probability_stats(p),
            actual_distribution={"nonpotable": int((y == 0).sum()), "potable": int((y == 1).sum())},
            false_potable=int(fp),
            false_nonpotable=int(fn),
            calibration=item["calibration"],
        )
    voting = registry.models["voting"]
    independent = np.mean([m.predict_proba(x)[:, 1] for m in voting.estimators_], axis=0)
    check(
        "voting equals actual independent member average",
        np.allclose(independent, probabilities["voting"], atol=1e-14),
    )
    check(
        "voting equals standalone base average",
        np.allclose(
            np.mean([probabilities[k] for k in ["cart", "rf", "ada", "gb"]], axis=0),
            probabilities["voting"],
            atol=1e-14,
        ),
    )
    dump("model_health.json", health)
    partition = {
        str(label): dict(train=int((train.Potability == label).sum()), test=int((y == label).sum()))
        for label in [0, 1]
    }
    dump("partition_distributions.json", partition)
    print("Recomputed every model metric and verified fitted pipelines.", flush=True)
    # OOF probabilities on training only. Hyperparameters were previously selected on these rows;
    # this is a descriptive sensitivity check, not a fresh unbiased validation estimate.
    reuse = os.getenv("JALSATHI_REUSE_TRAINING_DIAGNOSTICS") == "1"
    if reuse:
        hashes = json.loads((REPORTS / "baseline_hashes.json").read_text())
        if not all(
            hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
            for name, digest in hashes.items()
        ):
            raise RuntimeError("Cannot reuse diagnostics after a model or dataset change.")
    threshold_rows = pd.read_csv(REPORTS / "TRAINING_OOF_THRESHOLDS.csv").to_dict("records") if reuse else []
    for key, model in [] if reuse else registry.models.items():
        print("Training-fold threshold diagnostic:", key, flush=True)
        p = cross_val_predict(
            clone(model),
            train[FEATURES],
            train.Potability,
            cv=StratifiedKFold(3, shuffle=True, random_state=314),
            method="predict_proba",
            n_jobs=2,
        )[:, 1]
        for threshold in np.arange(0.3, 0.701, 0.05):
            pred = (p >= threshold).astype(int)
            tn, fp, fn, tp = confusion_matrix(train.Potability, pred).ravel()
            threshold_rows.append(
                dict(
                    model=key,
                    threshold=round(float(threshold), 2),
                    precision=precision_score(train.Potability, pred, zero_division=0),
                    recall=recall_score(train.Potability, pred),
                    specificity=tn / (tn + fp),
                    balanced_accuracy=balanced_accuracy_score(train.Potability, pred),
                    false_potable_rate=fp / (tn + fp),
                    f1=f1_score(train.Potability, pred, zero_division=0),
                    predicted_potable=int(pred.sum()),
                )
            )
    pd.DataFrame(threshold_rows).to_csv(REPORTS / "TRAINING_OOF_THRESHOLDS.csv", index=False)
    # Labeled held-out samples and explicitly unlabeled generated measurements.
    labeled = pd.read_csv(CSV / "balanced_labeled_100.csv")
    manifest = pd.read_csv(OUT / "ground_truth_manifest.csv").query("file == 'balanced_labeled_100.csv'")
    group_data = pd.read_csv(OUT / "diverse_groups.csv")
    diversity = []
    sensitivity = []
    labeled_rows = []
    for key, model in registry.models.items():
        p = model.predict_proba(labeled)[:, 1]
        for i, (value, (_, truth)) in enumerate(zip(p, manifest.iterrows())):
            labeled_rows.append(
                dict(
                    model=key,
                    dataset_index=int(truth.dataset_index),
                    true_label=int(truth.Potability),
                    predicted_class=int(value >= 0.5),
                    potable_probability=float(value),
                    csv_row=i + 2,
                )
            )
        for group, data in group_data.groupby("group", sort=False):
            diversity.append(
                dict(model=key, group=group, **probability_stats(model.predict_proba(data[FEATURES])[:, 1]))
            )
        before = float(model.predict_proba(pd.DataFrame([REFERENCE], columns=FEATURES))[0, 1])
        for feature in FEATURES:
            for value in frame[feature].quantile([0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]):
                sample = {**REFERENCE, feature: float(value)}
                after = float(model.predict_proba(pd.DataFrame([sample], columns=FEATURES))[0, 1])
                sensitivity.append(
                    dict(
                        model=key,
                        feature=feature,
                        old_value=REFERENCE[feature],
                        new_value=float(value),
                        class_before=int(before >= 0.5),
                        class_after=int(after >= 0.5),
                        probability_before=before,
                        probability_after=after,
                    )
                )
        allp = model.predict_proba(group_data[FEATURES])[:, 1]
        check(f"{key} varied inputs change probabilities", len(np.unique(allp)) > 1)
    pd.DataFrame(labeled_rows).to_csv(REPORTS / "POTABLE_NONPOTABLE_TEST_RESULTS.csv", index=False)
    pd.DataFrame(diversity).to_csv(REPORTS / "DIVERSITY_BY_GROUP.csv", index=False)
    pd.DataFrame(sensitivity).to_csv(REPORTS / "SENSITIVITY_ANALYSIS.csv", index=False)
    # Tests live on a dedicated DB. Existing QA records are not deleted either.
    batch_results = []
    parity = []
    latencies = []
    report_checks = []
    start = time.perf_counter()
    with TestClient(app) as client:
        startup = time.perf_counter() - start
        check("health models ready", client.get("/api/v1/health").json()["models_available"])
        check("dataset API count", client.get("/api/v1/dataset/summary").json()["rows"] == len(frame))
        check("model API matches disk", client.get("/api/v1/models").json()["models"] == metadata["models"])
        # Submit every generated fixture, including the maximum row count and malformed files.
        specs = json.loads((OUT / "specifications.json").read_text())
        balanced_batch = None
        for name, spec in specs.items():
            start = time.perf_counter()
            response = client.post(
                "/api/v1/predict/batch", files={"file": (name, (CSV / name).read_bytes(), "text/csv")}
            )
            elapsed = time.perf_counter() - start
            body = response.json()
            ok = check(f"CSV {name} status", response.status_code == spec["expected_status"])
            exported = False
            if response.status_code == 200:
                check(
                    f"CSV {name} row counts",
                    body["total"] == spec["rows"]
                    and body["invalid"] == spec["invalid"]
                    and body["valid"] == spec["rows"] - spec["invalid"],
                )
                export = client.get(f"/api/v1/batches/{body['batch_id']}/csv")
                exported = export.status_code == 200
                rows = list(csv.DictReader(io.StringIO(export.text)))
                check(f"CSV {name} export count", exported and len(rows) == body["valid"])
                for row, result in zip(rows, body["results"]):
                    check(
                        f"CSV {name} export row {row['row']}",
                        all(
                            np.isclose(float(row[c]), result["measurements"][c], rtol=0, atol=1e-10)
                            for c in FEATURES
                        )
                        and row["prediction"] == result["label"]
                        and float(row["model_probability"]) == result["selected_class_probability"],
                    )
                if name == "balanced_labeled_100.csv":
                    balanced_batch = body
                if name == "out_of_distribution_20.csv":
                    check(
                        "every OOD row warns",
                        all(
                            any("outside observed training range" in w for w in r["warnings"])
                            for r in body["results"]
                        ),
                    )
            batch_results.append(
                dict(
                    file=name,
                    status=response.status_code,
                    submitted_rows=spec["rows"],
                    accepted=body.get("valid", 0),
                    rejected=body.get("invalid", spec["rows"]),
                    seconds=elapsed,
                    potable=body.get("potable"),
                    nonpotable=body.get("non_potable"),
                    validation=body.get("errors", body.get("error")),
                    export_verified=exported,
                    passed=ok,
                )
            )
        # All 100 labeled samples: direct model vs single API vs batch, all five classifiers.
        for i, row in labeled.iterrows():
            sample = {c: float(row[c]) for c in FEATURES}
            start = time.perf_counter()
            response = client.post("/api/v1/predict", json=sample)
            latencies.append(time.perf_counter() - start)
            check(f"single labeled row {i} status", response.status_code == 200)
            single = response.json()
            batch = balanced_batch["results"][i]
            check(f"single row {i} stored values", single["measurements"] == sample)
            saved = client.get("/api/v1/analyses/" + single["analysis_id"]).json()
            check(f"single row {i} history matches", saved == single)
            direct = registry.predict_many([Sample(**sample)])[0]
            for a, b, d in zip(single["models"], batch["models"], direct["models"]):
                same = (
                    a["id"] == b["id"] == d["id"]
                    and a["predicted_class"] == b["predicted_class"] == d["predicted_class"]
                    and np.isclose(a["potable_probability"], b["potable_probability"], rtol=0, atol=1e-12)
                    and np.isclose(a["potable_probability"], d["potable_probability"], rtol=0, atol=1e-12)
                )
                check(f"parity row {i} {a['id']}", same)
                parity.append(
                    dict(
                        csv_row=i + 2,
                        model=a["id"],
                        single_class=a["predicted_class"],
                        batch_class=b["predicted_class"],
                        direct_class=d["predicted_class"],
                        single_probability=a["potable_probability"],
                        batch_probability=b["potable_probability"],
                        version=single["version"],
                        class_match=a["predicted_class"] == b["predicted_class"],
                        probability_match=bool(
                            np.isclose(a["potable_probability"], b["potable_probability"], rtol=0, atol=1e-12)
                        ),
                        version_match=single["version"] == batch["version"],
                        mapping_match=all(
                            np.isclose(sample[c], batch["measurements"][c], rtol=0, atol=1e-10)
                            for c in FEATURES
                        ),
                    )
                )
            if i < 20:
                import pymupdf

                pdf = client.get(f"/api/v1/reports/{single['analysis_id']}/pdf")
                doc = pymupdf.open(stream=pdf.content, filetype="pdf")
                text = " ".join(" ".join(p.get_text() for p in doc).split())
                required = [
                    single["analysis_id"],
                    single["created_at"],
                    single["label"],
                    single["version"],
                    f"{single['selected_class_probability']:.1%}",
                ]
                exact_values = {c: str(value) in text for c, value in sample.items()}
                check(
                    f"PDF {i} identity/class/probability",
                    pdf.status_code == 200 and all(v in text for v in required),
                )
                check(f"PDF {i} every measurement retained", all(exact_values.values()), str(exact_values))
                report_checks.append(
                    dict(
                        id=single["analysis_id"],
                        values=exact_values,
                        measurements=sample,
                        matches=all(exact_values.values()),
                        pages=len(doc),
                    )
                )
        reference = client.post("/api/v1/predict", json=REFERENCE).json()
        dump("reference_sample_result.json", reference)
        for count in [10, 100, 500, 1000]:
            payload = labeled.iloc[np.arange(count) % 100].to_csv(index=False).encode()
            start = time.perf_counter()
            r = client.post("/api/v1/predict/batch", files={"file": ("performance.csv", payload)})
            latencies.append(dict(batch_rows=count, seconds=time.perf_counter() - start))
            check(f"performance batch {count}", r.status_code == 200 and r.json()["valid"] == count)
        # Explicit malformed/security cases; numeric-only exported values cannot carry formulas.
        cases = [
            (
                "malformed JSON",
                lambda: client.post(
                    "/api/v1/predict", content=b"{", headers={"Content-Type": "application/json"}
                ),
                422,
            ),
            ("invalid report UUID", lambda: client.get("/api/v1/reports/not-a-uuid/pdf"), 422),
            ("traversal plot", lambda: client.get("/api/v1/plots/%2e%2e%2fregistry.json"), 404),
            (
                "unexpected file type",
                lambda: client.post("/api/v1/predict/batch", files={"file": ("bad.exe", b"abc")}),
                415,
            ),
            (
                "oversized bytes",
                lambda: client.post("/api/v1/predict/batch", files={"file": ("big.csv", b"x" * 2_000_001)}),
                413,
            ),
        ]
        security = []
        for name, call, status in cases:
            r = call()
            check(name, r.status_code == status)
            security.append(dict(name=name, status=r.status_code))
        for value in ["NaN", "Infinity", -1, 1e10, "<script>alert(1)</script>", '=HYPERLINK("bad")']:
            r = client.post("/api/v1/predict", json={**REFERENCE, "Hardness": value})
            check(f"reject invalid number {value}", r.status_code == 422 and "Traceback" not in r.text)
        for origin, allowed in [("http://localhost:5173", True), ("https://untrusted.example", False)]:
            r = client.options(
                "/api/v1/predict", headers={"Origin": origin, "Access-Control-Request-Method": "POST"}
            )
            check(f"CORS {origin}", (r.headers.get("access-control-allow-origin") == origin) == allowed)
        dump("security_results.json", security)
    # Do not remove user history or the isolated evidence; mark scope explicitly.
    dump("CSV_TEST_RESULTS.json", batch_results)
    pd.DataFrame(parity).to_csv(REPORTS / "INDIVIDUAL_BATCH_PARITY.csv", index=False)
    dump("report_consistency.json", report_checks)
    dump(
        "performance.json",
        dict(
            model_loading_seconds=loading,
            api_startup_seconds=startup,
            single_latency_median_seconds=float(np.median([v for v in latencies if isinstance(v, float)])),
            batches=[v for v in latencies if isinstance(v, dict)],
            metadata_json_bytes=len(json.dumps(metadata)),
            isolation="runtime/qa-audit.sqlite; existing user history untouched",
        ),
    )
    # Baseline artifacts and data must be unchanged throughout diagnosis.
    hashes = json.loads((REPORTS / "baseline_hashes.json").read_text())
    for name, digest in hashes.items():
        check(
            f"baseline file unchanged {name}",
            hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
        )
    dump("audit_checks.json", checks)
    dump(
        "audit_summary.json",
        dict(
            total=len(checks),
            passed=len(checks) - len(failures),
            failed=failures,
            labeled_samples=100,
            positive=50,
            negative=50,
            diverse_samples=len(group_data),
            parity_samples=100,
            parity_model_comparisons=len(parity),
            csv_fixtures=len(specs),
            models_unchanged=True,
            generated_at=datetime.now(timezone.utc).isoformat(),
            python=platform.python_version(),
            os=platform.platform(),
        ),
    )
    plot(health, probabilities, diversity, sensitivity)
    print(
        f"Audit checks: {len(checks) - len(failures)}/{len(checks)} passed. Failures: {failures}", flush=True
    )


def plot(health, probabilities, diversity, sensitivity):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    keys = list(health)
    axes[0].bar(keys, [health[k]["probabilities"]["predicted_nonpotable"] for k in keys], label="Non-potable")
    axes[0].bar(
        keys,
        [health[k]["probabilities"]["predicted_potable"] for k in keys],
        bottom=[health[k]["probabilities"]["predicted_nonpotable"] for k in keys],
        label="Potable",
    )
    axes[0].legend()
    axes[0].set_title("Held-out predicted class counts")
    for key, p in probabilities.items():
        axes[1].hist(p, bins=25, alpha=0.45, label=key)
    axes[1].axvline(0.5, linestyle="--", color="black")
    axes[1].legend()
    axes[1].set_title("P(potable), uncalibrated")
    fig.tight_layout()
    fig.savefig(REPORTS / "model-distributions.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 5, figsize=(15, 3))
    for ax, key in zip(axes, keys):
        cm = health[key]["metrics"]["confusion_matrix"]
        ax.imshow(cm, cmap="Blues")
        ax.set(title=key, xlabel="Predicted", ylabel="Actual", xticks=[0, 1], yticks=[0, 1])
        for i in range(2):
            for j in range(2):
                ax.text(j, i, cm[i][j], ha="center", va="center")
    fig.tight_layout()
    fig.savefig(REPORTS / "confusion-matrices.png", dpi=150)
    plt.close(fig)
    df = pd.DataFrame(sensitivity)
    fig, axes = plt.subplots(3, 3, figsize=(12, 9))
    for feature, ax in zip(FEATURES, axes.flat):
        for key in keys:
            data = df[(df.feature == feature) & (df.model == key)]
            ax.plot(data.new_value, data.probability_after, marker=".", label=key)
        ax.set(title=feature, ylim=(0, 1), ylabel="P(potable)")
    axes.flat[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(REPORTS / "sensitivity-analysis.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    run()
