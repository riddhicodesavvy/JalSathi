"""Run from repository root: python -m ml.train. Never called by inference."""

import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    log_loss,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree

from ml.data import FEATURES, ROOT, SEED, load_dataset, summarize


def metrics(y, p):
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return dict(
        accuracy=accuracy_score(y, pred),
        precision=precision_score(y, pred, zero_division=0),
        recall=recall_score(y, pred),
        f1=f1_score(y, pred),
        balanced_accuracy=balanced_accuracy_score(y, pred),
        roc_auc=roc_auc_score(y, p),
        pr_auc=average_precision_score(y, p),
        brier=brier_score_loss(y, p),
        log_loss=log_loss(y, p),
        confusion_matrix=[[int(tn), int(fp)], [int(fn), int(tp)]],
        false_potable_rate=float(fp / (tn + fp)),
        classification_report=classification_report(y, pred, output_dict=True, zero_division=0),
    )


def train():
    out = Path(os.getenv("JALSATHI_ARTIFACTS", ROOT / "ml/artifacts"))
    out.mkdir(parents=True, exist_ok=True)
    plots = out / "plots"
    plots.mkdir(exist_ok=True)
    frame, fingerprint = load_dataset()
    X, y = frame[FEATURES], frame.Potability
    xtr, xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    specs = {
        "cart": (
            "CART",
            DecisionTreeClassifier(random_state=SEED, class_weight="balanced"),
            {"model__max_depth": [3, 6, 10], "model__min_samples_leaf": [8, 20]},
        ),
        "rf": (
            "Random Forest",
            RandomForestClassifier(
                n_estimators=160,
                random_state=SEED,
                n_jobs=1,
                oob_score=True,
                class_weight="balanced_subsample",
            ),
            {"model__max_depth": [8, None], "model__min_samples_leaf": [2, 6]},
        ),
        "ada": (
            "AdaBoost",
            AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1), random_state=SEED),
            {"model__n_estimators": [60, 120], "model__learning_rate": [0.1, 0.5]},
        ),
        "gb": (
            "Gradient Boosting",
            GradientBoostingClassifier(random_state=SEED),
            {
                "model__n_estimators": [80, 140],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [2, 3],
            },
        ),
    }
    models, metadata = {}, []
    for key, (name, estimator, grid) in specs.items():
        print(f"Tuning {name}...", flush=True)
        pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", estimator)])
        # Every imputer is fitted inside each CV fold. Selection uses training CV only.
        search = GridSearchCV(
            pipe,
            grid,
            cv=cv,
            scoring={
                "balanced_accuracy": "balanced_accuracy",
                "roc_auc": "roc_auc",
                "neg_brier": "neg_brier_score",
            },
            refit="balanced_accuracy",
            n_jobs=2,
            error_score="raise",
        )
        search.fit(xtr, ytr)
        models[key] = search.best_estimator_
        idx = search.best_index_
        metadata.append(
            dict(
                id=key,
                name=name,
                cv_balanced_accuracy=float(search.best_score_),
                cv_roc_auc=float(search.cv_results_["mean_test_roc_auc"][idx]),
                cv_brier=float(-search.cv_results_["mean_test_neg_brier"][idx]),
                hyperparameters=search.best_params_,
            )
        )
    print("Cross-validating independent soft-voting ensemble...", flush=True)
    voting = VotingClassifier(estimators=[(k, clone(v)) for k, v in models.items()], voting="soft")
    from sklearn.model_selection import cross_validate

    scores = cross_validate(
        voting,
        xtr,
        ytr,
        cv=cv,
        scoring={"ba": "balanced_accuracy", "auc": "roc_auc", "brier": "neg_brier_score"},
    )
    voting.fit(xtr, ytr)
    models["voting"] = voting
    metadata.append(
        dict(
            id="voting",
            name="Voting Ensemble",
            cv_balanced_accuracy=float(scores["test_ba"].mean()),
            cv_roc_auc=float(scores["test_auc"].mean()),
            cv_brier=float(-scores["test_brier"].mean()),
            hyperparameters={"voting": "soft", "members": list(specs), "weights": "equal"},
        )
    )
    # Predeclared CV selection criterion: balanced accuracy, tie-break with Brier.
    primary = max(metadata, key=lambda m: (m["cv_balanced_accuracy"], -m["cv_brier"]))["id"]
    stamp = datetime.now(timezone.utc).isoformat()
    version = fingerprint[:10] + "-seed42-v1"
    for item in metadata:
        key = item["id"]
        model = models[key]
        p = model.predict_proba(xte)[:, 1]
        item.update(
            metrics=metrics(yte, p),
            version=version,
            trained_at=stamp,
            calibration="Uncalibrated model probabilities",
            features=FEATURES,
            dataset_sha256=fingerprint,
            positive_class=1,
        )
        fpr, tpr, _ = roc_curve(yte, p)
        prec, rec, _ = precision_recall_curve(yte, p)
        item["roc"] = [{"x": float(a), "y": float(b)} for a, b in zip(fpr, tpr)]
        item["pr"] = [{"x": float(a), "y": float(b)} for a, b in zip(rec, prec)]
        perm = permutation_importance(
            model, xte, yte, n_repeats=3, random_state=SEED, scoring="balanced_accuracy", n_jobs=2
        )
        item["permutation_importance"] = dict(zip(FEATURES, perm.importances_mean.tolist()))
        estimator = model.named_steps["model"] if key != "voting" else None
        if estimator is not None:
            item["feature_importance"] = dict(zip(FEATURES, estimator.feature_importances_.tolist()))
        if key == "rf":
            item["oob_score"] = float(estimator.oob_score_)
        item["threshold_analysis"] = [
            dict(
                threshold=t,
                false_potable_rate=float(((p >= t) & (yte == 0)).sum() / (yte == 0).sum()),
                potable_recall=float(((p >= t) & (yte == 1)).sum() / (yte == 1).sum()),
            )
            for t in [0.3, 0.5, 0.7, 0.9]
        ]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
        axes[0].imshow(item["metrics"]["confusion_matrix"], cmap="Blues")
        for i in range(2):
            for j in range(2):
                axes[0].text(j, i, item["metrics"]["confusion_matrix"][i][j], ha="center", va="center")
        axes[0].set(
            xlabel="Predicted", ylabel="Actual", title="Confusion matrix", xticks=[0, 1], yticks=[0, 1]
        )
        axes[1].plot(fpr, tpr)
        axes[1].plot([0, 1], [0, 1], "--", color="gray")
        axes[1].set(xlabel="False positive rate", ylabel="True positive rate", title="ROC")
        axes[2].plot(rec, prec)
        axes[2].set(xlabel="Recall", ylabel="Precision", title="Precision-recall")
        fig.suptitle(item["name"])
        fig.tight_layout()
        fig.savefig(plots / f"{key}-evaluation.png", dpi=140)
        plt.close(fig)
        joblib.dump(model, out / f"{key}.joblib")
        print(f"{key}: {item['metrics']['balanced_accuracy']:.3f} balanced accuracy", flush=True)
    fig, ax = plt.subplots(figsize=(23, 10))
    plot_tree(
        models["cart"].named_steps["model"],
        feature_names=FEATURES,
        class_names=["Non-potable", "Potable"],
        max_depth=3,
        filled=True,
        rounded=True,
        ax=ax,
        fontsize=9,
    )
    fig.savefig(plots / "cart-tree.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    summary = summarize(frame, fingerprint)
    registry = dict(
        primary=primary,
        models=metadata,
        version=version,
        seed=SEED,
        split="80/20 stratified",
        train_indices=xtr.index.tolist(),
        test_indices=xte.index.tolist(),
        versions=dict(python=platform.python_version(), sklearn=sklearn.__version__, numpy=np.__version__),
        training_ranges={c: [float(xtr[c].min()), float(xtr[c].max())] for c in FEATURES},
        selection="Maximum training CV balanced accuracy; Brier score breaks ties. Threshold 0.5.",
        dataset=summary,
    )
    (out / "registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    samples = ROOT / "data/samples"
    samples.mkdir(parents=True, exist_ok=True)
    frame.dropna().groupby("Potability", group_keys=False).head(3)[FEATURES].to_csv(
        samples / "demo.csv", index=False
    )
    print(f"Saved five models. Primary: {primary}.", flush=True)


if __name__ == "__main__":
    train()
