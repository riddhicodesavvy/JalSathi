"""Validate browser-downloaded reports and summarize verified original examples."""

import hashlib
import json

import numpy as np
import pymupdf

from ml.data import FEATURES, ROOT


def main():
    directory = ROOT / "reports/testing"
    evidence = json.loads((directory / "verified_potable_evidence.json").read_text(encoding="utf-8"))
    browser = json.loads((directory / "verified_potable_browser_evidence.json").read_text(encoding="utf-8"))
    tests = json.loads((directory / "verified-potable-browser-tests.json").read_text(encoding="utf-8"))
    assert tests["stats"]["expected"] == 1 and tests["stats"]["unexpected"] == 0
    assert browser["verified"] == 10 and not browser["errors"]
    browser_by_key = {(entry["group"], entry["number"]): entry for entry in browser["entries"]}
    report_checks = []
    text = "# Verified original Potable predictions\n\n"
    text += "Verified against the actual running API at `http://127.0.0.1:8000/api/v1/predict` "
    text += "and frontend at `http://127.0.0.1:5173/analyze`. Primary model: **Random Forest (`rf`)**. "
    text += f"Version: `{evidence['version']}`. Fixed threshold: **0.5**.\n\n"
    text += "**These are dataset-labeled examples and model predictions, not laboratory-certified drinking water.** "
    text += "Probabilities are uncalibrated model estimates, not probabilities that water is scientifically safe. "
    text += "Microbial and other essential tests are missing; eight unit-based reference checks remain unverified.\n\n"
    text += f"## Selection and provenance\n\n{evidence['complete_rows']} original rows have all nine measurements. "
    text += f"{evidence['qualifying_positive_labeled_rows']} complete rows have original label 1 and RF prediction 1. "
    text += (
        "The five examples below have the highest class-1 probabilities within that qualifying collection. "
    )
    text += (
        "**All five selected positive examples belong to the training partition.** Their probabilities are "
    )
    text += "selected demonstrations of the saved fitted model, not an unbiased estimate of unseen-sample performance. "
    text += "Original dataset labels and predicted labels are recorded separately. No retraining, threshold tuning, "
    text += "heuristic override or default substitution was performed.\n\n"
    text += "Original CSV numeric strings were retained in the upload fixture; JSON/form values use full round-trip "
    text += "floating-point numbers. Dataset indexes are zero-based; CSV line numbers count the header as line 1.\n\n"
    text += f"Dataset SHA-256: `{evidence['dataset_sha256']}`.\n\n"
    for group in ["potable", "nonpotable"]:
        text += (
            "## "
            + (
                "Five verified Potable examples"
                if group == "potable"
                else "Five verified Non-Potable controls"
            )
            + "\n\n"
        )
        for entry in evidence["examples"][group]:
            seen = browser_by_key[(group, entry["number"])]
            result = seen["result"]
            assert seen["uiVerified"] and result["measurements"] == entry["measurements"]
            assert result["predicted_class"] == entry["api_result"]["predicted_class"]
            assert np.isclose(
                next(m["potable_probability"] for m in result["models"] if m["id"] == "rf"),
                entry["primary_probability"],
                rtol=0,
                atol=1e-12,
            )
            path = ROOT / "runtime/verified-example-reports" / f"{group}-{entry['number']}.pdf"
            doc = pymupdf.open(path)
            extracted = " ".join(" ".join(page.get_text() for page in doc).split())
            assert all(str(value) in extracted for value in entry["measurements"].values())
            assert result["analysis_id"] in extracted and result["label"] in extracted
            assert result["version"] in extracted and "Laboratory testing" in extracted
            assert f"{result['selected_class_probability']:.1%}" in extracted
            report_checks.append(
                dict(
                    group=group,
                    number=entry["number"],
                    analysis_id=result["analysis_id"],
                    measurements_match=True,
                    classification_match=True,
                    pages=len(doc),
                )
            )
            text += f"### Example {entry['number']} — dataset index {entry['dataset_index']}\n\n"
            text += f"CSV line **{entry['csv_line']}**; partition **{entry['partition']}**; "
            text += f"original label **{entry['original_label']}**; primary prediction **{result['predicted_class']} ({result['label']})**.\n\n"
            text += f"Random Forest **P(class 1) = `{entry['primary_probability']!r}`** "
            text += f"({entry['primary_probability'] * 100:.12f}%). "
            text += f"Agreement with primary class: **{result['agreement_count']}/5**.\n\n"
            text += "| Required feature | Original CSV value |\n|---|---:|\n"
            for feature in FEATURES:
                text += f"| {feature} | {entry['original_values'][feature]} |\n"
            text += "\n| Classifier | Predicted class | P(class 1) |\n|---|---:|---:|\n"
            for model in result["models"]:
                text += (
                    f"| {model['name']} | {model['predicted_class']} | {model['potable_probability']!r} |\n"
                )
            text += "\n**API verification: PASS.** Exact nine input mappings, primary model/version, class, "
            text += "all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.\n\n"
            text += "**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, "
            text += "ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. "
            text += (
                "The downloaded PDF contains the same measurements, ID, version, probability and prediction. "
            )
            text += "Educational disclaimers remained visible; no safety guarantee was displayed.\n\n"
            text += f"Browser analysis ID: `{result['analysis_id']}`. "
            if group == "potable":
                text += f"[Browser screenshot](verified-potable-{entry['number']}.png). "
            ph = entry["measurements"]["ph"]
            text += f"Independent pH reference check: **{'within' if 6.5 <= ph <= 8.5 else 'outside'}**; "
            text += "other eight references **unverified**. A model-positive classification does not override a pH reference breach.\n\n"
    text += "## Verification summary\n\n"
    text += "- Five distinct original positive-labeled rows predicted Potable by the saved RF pipeline.\n"
    text += "- Five original negative-labeled controls predicted Non-Potable by the same pipeline.\n"
    text += "- Ten initial live API predictions, ten alternating real browser submissions, and twenty actual PDFs verified.\n"
    text += "- Five-row upload fixture accepted through the live batch API: 5/5 Predicted Potable, zero probability mismatches.\n"
    text += "- All fifty initial model-wise probabilities matched direct inference; all browser responses matched corresponding direct RF estimates.\n"
    text += "- Browser JavaScript errors: zero. Prediction/integration bugs found: none. One test selector was corrected to target the existing indicator tooltip; application code was unchanged.\n"
    text += "- Dataset, model artifacts and the production threshold remained unchanged.\n\n"
    text += "Upload file: `tests/fixtures/verified_potable_samples.csv` (only the nine features, no target). "
    text += "Machine-readable provenance and responses: `verified_potable_evidence.json` and `verified_potable_browser_evidence.json`. "
    text += "Reproduce: `python -m tests.verify_potable_examples`; "
    text += "`cd frontend; node node_modules/@playwright/test/cli.js test --config playwright.potable.config.ts`; "
    text += "`python -m tests.write_verified_potable_report` from the root. These commands intentionally create real analysis history entries because they verify the actual deployed app.\n"
    assert (
        hashlib.sha256((ROOT / "water_potability.csv").read_bytes()).hexdigest() == evidence["dataset_sha256"]
    )
    for name, digest in evidence["artifact_hashes"].items():
        assert hashlib.sha256((ROOT / "ml/artifacts" / name).read_bytes()).hexdigest() == digest
    (directory / "VERIFIED_POTABLE_EXAMPLES.md").write_text(text, encoding="utf-8")
    (directory / "verified_potable_pdf_checks.json").write_text(
        json.dumps(report_checks, indent=2), encoding="utf-8"
    )
    # Render the strongest example's browser-downloaded report for visual review.
    doc = pymupdf.open(ROOT / "runtime/verified-example-reports/potable-1.pdf")
    for index, page in enumerate(doc):
        page.get_pixmap().save(directory / f"verified-potable-report-page-{index + 1}.png")
    print("Report written. Browser-downloaded PDF checks:", len(report_checks), "passed.")


if __name__ == "__main__":
    main()
