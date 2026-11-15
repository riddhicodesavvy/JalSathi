# JalSathi implementation delivery

Verified on 15 November 2026, Windows, Python 3.12.14 and Node 22.16.0.

## Delivery checklist

- [x] Preserved original `water_potability.csv` and every pre-existing file in `reports/eda`.
- [x] Verified 3,276 records, nine measurements and binary labels; generated dataset analysis and fingerprint.
- [x] Trained, tuned, saved and evaluated CART, Random Forest, AdaBoost, Gradient Boosting and independent soft Voting pipelines.
- [x] Selected primary Random Forest using training CV balanced accuracy and Brier tie-break; no final-test-driven model selection.
- [x] Implemented FastAPI, validated inference, reference separation, SQLite persistence, UUID history, generated PDF reports and CSV batch export.
- [x] Completed all six React pages: Dashboard, Analyze Sample, Model Comparison, Batch Analysis, Reports and About.
- [x] Implemented Aqua Glass sidebar, original droplet/leaf logo, original wave and laboratory SVG decoration, rounded glass cards, synchronized controls, model ring/indicators, reference table, accessible Radix detail dialogs, error/loading/empty states and notifications.
- [x] Implemented actual metric comparisons, confusion matrices, ROC/PR curves, per-model permutation influence, threshold safety analysis, fitted CART visualization and per-sample decision paths.
- [x] Implemented genuine additive logistic spline GAM, actual effect plots and tested additivity.
- [x] Implemented validation-likelihood weighted Bayesian-style demonstration, explicitly labeled a plug-in approximation.
- [x] Documented architecture, API, scientific limitations, reproducibility and complete Unit 5/practical mapping.
- [x] Added PowerShell setup/start scripts, npm lockfile and exact installed Python dependency snapshot.
- [x] Verified responsive desktop and 390px mobile real browser workflows, navigation, reports, batch processing and no page overflow in tested views.
- [ ] Adaptive MARS: not implemented; no reliable compatible Windows dependency included. Fixed splines and forests are not falsely labeled MARS.
- [ ] SHAP: not implemented; actual CART and permutation explanations are supplied instead.
- [ ] Rigorous BMA: not implemented; parameter-integrating Bayesian inference is beyond the fitted sklearn model family. Approximation status remains visible.
- [ ] Probability calibration and full laboratory/BIS/WHO certification: not claimed. Percentages remain uncalibrated model estimates; eight mass-unit reference checks remain unavailable until units are independently verified.

## Actual held-out metrics

| Classifier | Accuracy | F1 | Balanced accuracy | ROC-AUC | False-potable rate |
|---|---:|---:|---:|---:|---:|
| CART | 61.28% | 0.4774 | 58.41% | 0.6104 | 28.50% |
| Random Forest | 65.24% | 0.4842 | 61.02% | 0.6653 | 19.75% |
| AdaBoost | 62.04% | 0.0945 | 51.79% | 0.5656 | 1.50% |
| Gradient Boosting | 65.70% | 0.3902 | 58.94% | 0.6545 | 10.25% |
| Voting Ensemble | 66.62% | 0.4000 | 59.76% | 0.6518 | 9.00% |

656 untouched test rows, including 400 non-potable and 256 potable. False-potable rate is FP/(TN+FP), not 1-precision. AdaBoost's low false-potable rate accompanies very poor potable recall; it is not evidence of a superior safety classifier. Voting has the highest test accuracy, while Random Forest was selected by the declared training criterion. Full precision, recall, PR-AUC, classification reports and Brier/log loss are stored in the registry and evaluation reports. No model is sufficiently validated to certify water safety.

## API and storage

`GET /api/v1/health`, `/models`, `/models/metrics`, `/models/{id}`, `/dataset/summary`, `/features`, `/analyses`, `/analyses/{uuid}`, `/reports/{uuid}/pdf`, `/batches/{uuid}/csv`, `/plots/{filename}`, `/samples/csv`, `/extensions`; `POST /api/v1/predict` and `/predict/batch`. OpenAPI: `/docs`.

The code resides in `backend/app`, `frontend/src`, `ml` and `scripts`; reusable UI modules split form/result components, branding, charts, history, dialogs, status/error states, formatting, validation and API access. Original data stays at the root; trained trusted artifacts are in `ml/artifacts`; derived evidence is in `reports/evaluations`. Runtime history and generated reports are in ignored `runtime` storage. No public deployment or cloud configuration is required.

## Executed checks

| Check | Result |
|---|---|
| Core training and held-out evaluation | Five actual fitted models saved and evaluated |
| Optional extension training | Actual GAM and plug-in averaging artifacts/results saved |
| pytest | 25 tests passed; backend application coverage 97% |
| Targeted extension/report recheck | 3 tests passed |
| Frontend component tests | 4 tests passed |
| ESLint | Passed without lint warnings after cleanup |
| TypeScript + Vite production build | Passed |
| Ruff | Passed |
| Playwright | Desktop and mobile real workflows plus invalid-form/API-error scenarios passed |
| Visual inspection | Desktop/mobile analyzer screenshots and both generated PDF pages reviewed; orphaned PDF heading fixed |

Browser tests initially encountered local socket restrictions; they passed with permitted loopback access. A Starlette/httpx deprecation warning remains in the test harness. Vite reports harmless upstream Zod PURE-comment annotations; they do not fail the build. Production application data is never mocked. The API-error simulation is confined to one browser test.

## Exact startup

From the repository root in PowerShell:

```powershell
./scripts/start.ps1
```

Then open http://127.0.0.1:5173. API documentation: http://127.0.0.1:8000/docs.

Separate terminals, if preferred:

```powershell
./.venv/Scripts/python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm run dev
```

Clean-environment setup: `./scripts/setup.ps1`. Retraining: `./.venv/Scripts/python.exe -m ml.train`; optional demonstrations: `./.venv/Scripts/python.exe -m ml.extensions`; evidence refresh: `./.venv/Scripts/python.exe -m scripts.verify_artifacts`.

All core application features run locally without API keys. External permissions only affected installing dependencies and allowing test loopback sockets. Future public deployment needs authentication, rate/request limits, HTTPS, backups and domain review. The launch script requires available ports and the installed virtual environment. Additional sample measurements must use the dataset's scale; verified scientific units and essential laboratory tests remain prerequisites for real-world interpretation.
