"""Optional, explicitly limited Unit 5 demonstrations. No change to core selection."""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

from ml.data import FEATURES, ROOT, SEED, load_dataset
from ml.train import metrics


def run(directory: Path | None = None):
    directory = directory or ROOT / "ml/artifacts"
    registry = json.loads((directory / "registry.json").read_text())
    frame, _ = load_dataset()
    xtr = frame.loc[registry["train_indices"], FEATURES]
    ytr = frame.loc[registry["train_indices"], "Potability"]
    xte = frame.loc[registry["test_indices"], FEATURES]
    yte = frame.loc[registry["test_indices"], "Potability"]
    # No interactions: logit p = intercept + sum_j f_j(x_j).
    gam = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("spline", SplineTransformer(n_knots=5, degree=3, include_bias=False)),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000)),
        ]
    )
    search = GridSearchCV(
        gam,
        {"spline__n_knots": [4, 6], "model__C": [0.1, 1]},
        cv=StratifiedKFold(3, shuffle=True, random_state=SEED),
        scoring="balanced_accuracy",
        n_jobs=2,
    )
    search.fit(xtr, ytr)
    model = search.best_estimator_
    joblib.dump(model, directory / "gam.joblib")
    gam_metrics = metrics(yte, model.predict_proba(xte)[:, 1])
    fig, axes = plt.subplots(3, 3, figsize=(12, 9))
    baseline = xtr.median()
    for ax, feature in zip(axes.flat, FEATURES):
        grid = np.linspace(xtr[feature].quantile(0.01), xtr[feature].quantile(0.99), 100)
        from pandas import DataFrame

        samples = DataFrame([baseline.to_dict()] * 100)
        samples[feature] = grid
        effect = model.decision_function(samples)
        effect -= model.decision_function(DataFrame([baseline.to_dict()]))[0]
        ax.plot(grid, effect, color="#079eac")
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.6)
        ax.set(title=feature, ylabel="Centered log-odds effect")
    fig.suptitle("Additive logistic spline GAM: fitted feature effects, not causal effects")
    fig.tight_layout()
    fig.savefig(directory / "plots/gam-effects.png", dpi=140)
    plt.close(fig)
    # Validation likelihood weights on fixed fitted candidates, equal model priors.
    # This is a plug-in pseudo-posterior, NOT Bayesian marginal-likelihood integration.
    xa, xv, ya, yv = train_test_split(xtr, ytr, test_size=0.25, stratify=ytr, random_state=SEED)
    keys = ["cart", "rf", "ada", "gb"]
    # Fixed, prespecified candidate settings; validation labels never tune these.
    estimators = [
        DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, random_state=SEED),
        RandomForestClassifier(n_estimators=160, min_samples_leaf=2, random_state=SEED),
        AdaBoostClassifier(n_estimators=60, learning_rate=0.1, random_state=SEED),
        GradientBoostingClassifier(n_estimators=80, learning_rate=0.05, max_depth=2, random_state=SEED),
    ]
    candidates, log_weights = [], []
    for estimator in estimators:
        candidate = Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", estimator)])
        candidate.fit(xa, ya)
        log_weights.append(-len(yv) * log_loss(yv, candidate.predict_proba(xv)[:, 1]))
        candidates.append(candidate)
    log_weights = np.asarray(log_weights)
    weights = np.exp(log_weights - log_weights.max())
    weights /= weights.sum()
    p = sum(w * m.predict_proba(xte)[:, 1] for w, m in zip(weights, candidates))
    joblib.dump({"models": candidates, "weights": weights}, directory / "likelihood-average.joblib")
    result = dict(
        gam=dict(
            status="Implemented",
            method="Penalized additive logistic B-spline GAM",
            cv_balanced_accuracy=float(search.best_score_),
            hyperparameters=search.best_params_,
            metrics=gam_metrics,
            plot="gam-effects.png",
        ),
        bayesian_style_average=dict(
            status="Approximation only",
            method="Validation-likelihood weighted plug-in averaging, equal priors",
            formula="w_m = exp(sum_i log p_m(y_i|x_i)) / sum_k exp(sum_i log p_k(y_i|x_i))",
            limitations="No parameter integration or marginal likelihood; not rigorous BMA. "
            "Fixed candidate settings; 75% of training rows fit candidates, 25% determine weights. "
            "Weights condition on fitted parameters. Final test remains untouched.",
            weights=dict(zip(keys, weights.tolist())),
            metrics=metrics(yte, p),
        ),
        adaptive_basis=dict(
            status="Not implemented",
            reason="MARS requires adaptive hinge selection and pruning. No reliable Windows MARS dependency "
            "is included; fixed spline GAM must not be mislabeled as MARS.",
        ),
    )
    (directory / "extensions.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
