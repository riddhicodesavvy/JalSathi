"""Produce reproducible dataset, evaluation and delivery evidence from saved artifacts."""

import json
import math

import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from ml.data import FEATURES, ROOT, SEED, load_dataset


def main():
    directory = ROOT / "ml/artifacts"
    registry = json.loads((directory / "registry.json").read_text())
    frame, fingerprint = load_dataset()
    report_dir = ROOT / "reports/evaluations"
    report_dir.mkdir(parents=True, exist_ok=True)
    versions = {}
    from importlib.metadata import version

    for package in ["scikit-learn", "pandas", "numpy", "joblib", "matplotlib", "fastapi", "pydantic"]:
        versions[package] = version(package)
    for item in registry["models"]:
        model = joblib.load(directory / f"{item['id']}.joblib")
        params = model.get_params(deep=True)
        item["full_parameters"] = {
            key: (
                repr(value)
                if isinstance(value, float) and not math.isfinite(value)
                else value
                if isinstance(value, (int, float, str, bool, type(None)))
                else repr(value)
            )
            for key, value in params.items()
        }
        item["library_versions"] = versions
    registry["versions"].update(versions)
    (directory / "registry.json").write_text(
        json.dumps(registry, indent=2, allow_nan=False), encoding="utf-8"
    )
    rows = []
    for model in registry["models"]:
        rows.append(
            {
                "model": model["name"],
                **{
                    key: model["metrics"][key]
                    for key in [
                        "accuracy",
                        "precision",
                        "recall",
                        "f1",
                        "balanced_accuracy",
                        "roc_auc",
                        "pr_auc",
                        "false_potable_rate",
                    ]
                },
            }
        )
    pd.DataFrame(rows).to_csv(report_dir / "model_metrics.csv", index=False)
    table = "| Model | Accuracy | Precision | Recall | F1 | Balanced accuracy | ROC-AUC | PR-AUC | False-potable rate |\n"
    table += "|---|" + "---:|" * 8 + "\n"
    for row in rows:
        table += (
            "| "
            + row["model"]
            + " | "
            + " | ".join(f"{v:.4f}" for k, v in row.items() if k != "model")
            + " |\n"
        )
    (report_dir / "MODEL_EVALUATION.md").write_text(
        "# Saved held-out evaluation\n\n"
        + table
        + "\nPrimary model: "
        + registry["primary"]
        + ". Selection: "
        + registry["selection"]
        + "\n\n656 held-out observations: 400 non-potable and 256 potable. Positive class is 1. "
        "False-potable rate is FP/(TN+FP). PR-AUC is average precision. Probabilities are uncalibrated. "
        "Higher thresholds reduce false-potable mistakes while losing potable recall; inspect the saved per-model "
        "threshold analysis. These test curves are descriptive and were not used for selection.\n",
        encoding="utf-8",
    )
    summary = registry["dataset"]
    content = "# JalSathi dataset verification\n\nOriginal CSV preserved at `water_potability.csv`. "
    content += f"SHA-256: `{fingerprint}`.\n\nVerified {len(frame)} rows, {len(FEATURES)} inputs, binary Potability target. "
    content += f"Labels: {summary['classes']}. Duplicates: {summary['duplicates']}.\n\n"
    content += "Prior analytical work remains in `reports/eda/`; no previous master analysis markdown was present.\n\n"
    content += "| Feature | Missing | IQR outlier flags | Negative values |\n|---|---:|---:|---:|\n"
    for c in FEATURES:
        content += f"| {c} | {summary['missing'][c]} | {summary['outliers_iqr'][c]} | {summary['negative_values'][c]} |\n"
    content += (
        "\nNo outlier rows removed. Statistical outliers are not regulatory violations. Units, sampling "
    )
    content += "locations, laboratory method and label validity are not independently authenticated. "
    content += "Expected upstream source: https://www.kaggle.com/datasets/adityakadiwal/water-potability\n"
    (ROOT / "reports/JALSATHI_DATASET_ANALYSIS.md").write_text(content, encoding="utf-8")
    train = frame.loc[registry["train_indices"]]
    comparison = []
    for strategy in ["median", "mean"]:
        pipe = Pipeline(
            [
                ("imputer", SimpleImputer(strategy=strategy)),
                ("model", DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, random_state=SEED)),
            ]
        )
        scores = cross_val_score(
            pipe,
            train[FEATURES],
            train.Potability,
            cv=StratifiedKFold(3, shuffle=True, random_state=SEED),
            scoring="balanced_accuracy",
        )
        comparison.append(dict(strategy=strategy, cv_balanced_accuracy=float(scores.mean())))
    (report_dir / "imputation_comparison.json").write_text(json.dumps(comparison, indent=2))
    print(table)


if __name__ == "__main__":
    main()
