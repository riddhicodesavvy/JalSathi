"""Deterministic audit fixtures. Synthetic rows have no assigned potability labels."""

import json

import numpy as np
import pandas as pd

from ml.data import FEATURES, ROOT, load_dataset

OUT = ROOT / "tests/fixtures"
CSV = OUT / "csv"
REFERENCE = dict(
    ph=7.2,
    Hardness=180.0,
    Solids=15000.0,
    Chloramines=7.0,
    Sulfate=300.0,
    Conductivity=400.0,
    Organic_carbon=12.0,
    Trihalomethanes=65.0,
    Turbidity=3.0,
)


def generate():
    CSV.mkdir(parents=True, exist_ok=True)
    frame, fingerprint = load_dataset()
    registry = json.loads((ROOT / "ml/artifacts/registry.json").read_text())
    held = frame.loc[registry["test_indices"]].dropna()
    positive = held[held.Potability == 1].sample(50, random_state=2026)
    negative = held[held.Potability == 0].sample(50, random_state=2026)
    manifest, specs = [], {}

    def save(name, rows, source, status=200, invalid=0):
        rows.to_csv(CSV / name, index=False)
        specs[name] = dict(
            rows=len(rows), source=source, expected_status=status, invalid=invalid, columns=list(rows.columns)
        )

    for name, rows in [
        ("potable_labeled_25.csv", positive.head(25)),
        ("nonpotable_labeled_25.csv", negative.head(25)),
        ("balanced_labeled_100.csv", pd.concat([positive, negative]).sample(frac=1, random_state=2026)),
    ]:
        save(name, rows[FEATURES], "Original complete held-out dataset records")
        manifest.extend(
            dict(
                file=name,
                csv_row=i + 2,
                dataset_index=int(idx),
                Potability=int(row.Potability),
                partition="held-out test",
            )
            for i, (idx, row) in enumerate(rows.iterrows())
        )
    rng = np.random.default_rng(2026)
    lo, hi = frame[FEATURES].min(), frame[FEATURES].max()
    random = pd.DataFrame(rng.uniform(lo, hi, (100, 9)), columns=FEATURES)
    save("diverse_valid_100.csv", random, "Synthetic uniform observed-range functional inputs; unlabeled")
    edge = pd.DataFrame([REFERENCE] * 30)
    for i in range(30):
        c = FEATURES[i % 9]
        edge.loc[i, c] = [0.0, float(hi[c]), 14.0 if c == "ph" else 1e9][i % 3]
    save("edge_cases_30.csv", edge, "Synthetic schema boundary inputs; unlabeled")
    ood = pd.DataFrame([REFERENCE] * 20)
    for i in range(20):
        c = FEATURES[1 + i % 8]
        ood.loc[i, c] = max(float(hi[c]) * 2, 100.0) + i
    save("out_of_distribution_20.csv", ood, "Synthetic outside training ranges; unlabeled")
    sample = pd.DataFrame([REFERENCE])
    save("invalid_missing_columns.csv", sample.drop(columns=["Sulfate"]), "Modified reference", 422)
    text = sample.astype(object)
    text.loc[0, "ph"] = "=1+1"
    save("invalid_non_numeric.csv", text, "Formula/text injection attempt", invalid=1)
    blank = sample.copy()
    blank.loc[0, "Sulfate"] = np.nan
    save("invalid_empty_cells.csv", blank, "Modified reference; missing measurement", invalid=1)
    save("invalid_extra_columns.csv", sample.assign(unexpected="payload"), "Modified reference", 422)
    save("invalid_large_file.csv", pd.DataFrame([REFERENCE] * 1001), "Synthetic over row limit", 413)
    (CSV / "invalid_empty_file.csv").write_bytes(b"")
    specs["invalid_empty_file.csv"] = dict(rows=0, source="Empty file", expected_status=422, invalid=0)
    save(
        "invalid_duplicate_rows.csv",
        pd.DataFrame([REFERENCE] * 3),
        "Duplicate reference measurements; duplicates intentionally retained independently",
    )
    save("single_sample.csv", sample, "Specified numerical reference; no claimed true label")
    save(
        "maximum_supported_batch.csv",
        pd.concat([random] * 10, ignore_index=True),
        "1,000 synthetic valid rows; repeated measurements retained",
    )
    groups = []
    for name, count, feature, lower, upper in [
        ("A typical", 20, None, 0, 0),
        ("B acidic", 10, "ph", 1, 4),
        ("C alkaline", 10, "ph", 10, 14),
        ("D high turbidity", 10, "Turbidity", 6, 15),
        ("E high solids", 10, "Solids", 45000, 85000),
        ("F high hardness", 10, "Hardness", 300, 650),
        ("G high sulfate", 10, "Sulfate", 450, 800),
        ("H high chloramines", 10, "Chloramines", 12, 25),
        ("I combined extremes", 10, "all", 0, 0),
    ]:
        data = pd.DataFrame(
            rng.uniform(frame[FEATURES].quantile(0.25), frame[FEATURES].quantile(0.75), (count, 9)),
            columns=FEATURES,
        )
        if feature == "all":
            data = pd.DataFrame(rng.uniform(hi * 0.8, hi * 1.6, (count, 9)), columns=FEATURES)
            data.ph = data.ph.clip(0, 14)
        elif feature:
            data[feature] = rng.uniform(lower, upper, count)
        groups.extend(dict(group=name, **r) for r in data.to_dict("records"))
    groups.extend(dict(group="J random valid", **r) for r in random.to_dict("records"))
    groups.extend(dict(group="K out of distribution", **r) for r in ood.to_dict("records"))
    pd.DataFrame(groups).to_csv(OUT / "diverse_groups.csv", index=False)
    pd.DataFrame(manifest).to_csv(OUT / "ground_truth_manifest.csv", index=False)
    browser = []
    for label, rows in [(1, positive.head(25)), (0, negative.head(25))]:
        for idx, row in rows.iterrows():
            browser.append(
                dict(
                    dataset_index=int(idx),
                    true_label=label,
                    measurements={c: float(row[c]) for c in FEATURES},
                )
            )
    (OUT / "browser_samples.json").write_text(json.dumps(browser, indent=2))
    (OUT / "specifications.json").write_text(json.dumps(specs, indent=2))
    readme = "# Reproducible QA CSV fixtures\n\nRun `python -m tests.generate_test_csvs`. Seed 2026. "
    readme += "Original source: root water_potability.csv; expected upstream https://www.kaggle.com/datasets/adityakadiwal/water-potability. "
    readme += f"SHA-256: {fingerprint}. No production training data is changed.\n\n"
    readme += "Labeled records are complete, distinct held-out records; labels/indexes are stored separately in ../ground_truth_manifest.csv. "
    readme += "Synthetic measurements have no invented labels and are not drinking-water safety examples. "
    readme += (
        "Duplicate rows are permitted and retained in input order; each receives its own analysis ID.\n\n"
    )
    readme += "| File | Rows | Source/purpose | Expected HTTP | Invalid rows |\n|---|---:|---|---:|---:|\n"
    for name, spec in specs.items():
        readme += f"| {name} | {spec['rows']} | {spec['source']} | {spec['expected_status']} | {spec['invalid']} |\n"
    (CSV / "README.md").write_text(readme, encoding="utf-8")
    print(
        f"Generated {len(specs)} CSV fixtures, {len(groups)} diverse-group measurements, and labeled manifests."
    )


if __name__ == "__main__":
    generate()
