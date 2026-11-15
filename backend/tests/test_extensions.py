import json

import joblib
import numpy as np

from ml.data import FEATURES, ROOT, load_dataset


def test_extensions_are_fitted_and_honestly_labeled():
    directory = ROOT / "ml/artifacts"
    result = json.loads((directory / "extensions.json").read_text())
    assert result["bayesian_style_average"]["status"] == "Approximation only"
    assert result["adaptive_basis"]["status"] == "Not implemented"
    weights = result["bayesian_style_average"]["weights"]
    assert np.isclose(sum(weights.values()), 1)
    frame, _ = load_dataset()
    model = joblib.load(directory / "gam.joblib")
    assert model.predict_proba(frame[FEATURES].iloc[:3]).shape == (3, 2)
    # Additivity in the logit: changing two coordinates equals the sum of single changes.
    baseline = frame[FEATURES].median().to_frame().T
    a, b, both = baseline.copy(), baseline.copy(), baseline.copy()
    a["ph"] = both["ph"] = 6.0
    b["Hardness"] = both["Hardness"] = 150.0

    def f(x):
        return model.decision_function(x)[0]

    assert np.isclose(f(both) - f(baseline), f(a) + f(b) - 2 * f(baseline))


def test_extensions_endpoint(client):
    assert client.get("/api/v1/extensions").status_code == 200
    assert client.get("/api/v1/plots/gam-effects.png").status_code == 200
