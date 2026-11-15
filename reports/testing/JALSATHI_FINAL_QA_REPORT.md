# JalSathi final QA report

**Verdict: PASS WITH LIMITATIONS**

Final verification: **52/52 automated tests** (36 backend, 4 component, 12 browser), plus **2305/2305 isolated audit assertions**. Backend application coverage: 97%. Ruff, ESLint, TypeScript and production build pass. Initial failures and fixes are documented in BUG_FIX_LOG.md.

## A — Environment and isolation

Python 3.12.14, Windows-11-10.0.26200-SP0, FastAPI 0.163.1, scikit-learn 1.8.0, pandas 2.3.3, pytest 9.2.0. Node 22.16.0; React/Vite/TypeScript/Playwright versions are locked in frontend/package-lock.json.

The existing frontend/API were checked, and isolated QA services were started on ports 5175/8001. Audit services use runtime/qa-audit.sqlite and runtime/qa-browser.sqlite. Existing history was backed up privately before testing; no user-created analysis was deleted or uploaded. Original file/model hashes were checked before and after. The full source CSV remains byte-for-byte unchanged.

## B — Model health and methodology

| Model | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | TN / FP / FN / TP | Predicted 0 / 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CART | 0.6128 | 0.5841 | 0.5043 | 0.4531 | 0.4774 | 0.6104 | 0.5230 | 286 / 114 / 140 / 116 | 426 / 230 |
| Random Forest | 0.6524 | 0.6102 | 0.5753 | 0.4180 | 0.4842 | 0.6653 | 0.6028 | 321 / 79 / 149 / 107 | 470 / 186 |
| AdaBoost | 0.6204 | 0.5179 | 0.6842 | 0.0508 | 0.0945 | 0.5656 | 0.4471 | 394 / 6 / 243 / 13 | 637 / 19 |
| Gradient Boosting | 0.6570 | 0.5894 | 0.6372 | 0.2812 | 0.3902 | 0.6545 | 0.5841 | 359 / 41 / 184 / 72 | 543 / 113 |
| Voting Ensemble | 0.6662 | 0.5976 | 0.6697 | 0.2852 | 0.4000 | 0.6518 | 0.5905 | 364 / 36 / 183 / 73 | 547 / 109 |

Actual target distribution is 400 non-potable/256 potable. All five pipelines pass feature order, finite probability, class encoding, training-only imputation, deterministic prediction and saved-metric/curve checks. Voting equals the arithmetic mean of its independently fitted member probabilities and the separately saved base predictions. RF remains the correct CV-selected primary. See MODEL_DIVERSITY_ANALYSIS.md for AdaBoost diagnosis and training-only threshold experiments. No model was retrained and the 0.5 threshold is unchanged. Hyperparameter-selected CV scores have selection optimism; final test data was reserved for reporting.

## C — Potable-class tests

50 complete held-out Potability=1 rows were tested directly and through single and batch API paths. A separately selected 25 positive-labeled rows were submitted using all nine browser form fields. Missing original measurements were tested separately through fitted preprocessing, while live form/API requests reject blanks.

## D — Non-potable-class tests

50 complete held-out Potability=0 rows received the same direct/API/batch checks; 25 negative-labeled rows also went through the browser. The subset results are:

| Model | Positive rows predicted potable / 50 | Subset recall | Negative rows predicted potable / 50 | Subset false-potable rate |
|---|---:|---:|---:|---:|
| cart | 26 | 52.0% | 18 | 36.0% |
| rf | 26 | 52.0% | 11 | 22.0% |
| ada | 5 | 10.0% | 2 | 4.0% |
| gb | 18 | 36.0% | 5 | 10.0% |
| voting | 19 | 38.0% | 6 | 12.0% |

Full held-out false-potable counts are CART 114, RF 79, AdaBoost 6, GB 41, Voting 36. Corresponding false-nonpotable counts are 140,149,243,184,183.

## E — Diversified inputs and sensitivity

| Model | Inputs | Potable | Non-potable | Unique probabilities | Minimum | Maximum | Mean | Std. dev. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cart | 220 | 93 | 127 | 33 | 0.000000 | 1.000000 | 0.520990 | 0.248784 |
| rf | 220 | 101 | 119 | 201 | 0.085971 | 0.840246 | 0.481843 | 0.138352 |
| ada | 220 | 32 | 188 | 42 | 0.193319 | 0.775663 | 0.356682 | 0.141649 |
| gb | 220 | 112 | 108 | 207 | 0.075541 | 0.993276 | 0.521385 | 0.258156 |
| voting | 220 | 90 | 130 | 207 | 0.103531 | 0.877771 | 0.470225 | 0.162270 |

All requested groups A–K were exercised: representative measurements, acidic/alkaline pH, high turbidity, solids, hardness, sulfate and chloramines, combined extremes, 100 random observed-range inputs and 20 out-of-training-range inputs. Every OOD fixture row receives a warning. No labels were assigned to synthetic cases. Nine features were each varied over seven observed quantiles for each model (315 comparisons). No pathological fixed-probability behavior was found.

## F — CSV handling

All 15 generated fixtures were executed through API and UI, including all malformed inputs and the 1,000-row limit. Expected status/row/error behavior and export parity pass. See CSV_TEST_RESULTS.md and the separate provenance manifest; target labels are never submitted as features.

## G — Direct, individual, form and batch parity

100 labeled samples × five models = **500** direct/single/batch model comparisons with zero class, probability, feature-mapping or version mismatches (probability tolerance 1e-12). Single/batch CART decision paths also match in regression tests. The browser independently verified all nine edited payload values, saved history, primary label, displayed estimate and agreement for **50** original records (25 per label). It observed RF potable **18** times and non-potable **32** times. Another three mobile submissions pass the same checks. Browser single/batch parity covers 265 model comparisons with zero mismatches. No defaults replaced edited inputs.

## H — Frontend, history, reports, scientific/security checks

All six pages load on desktop/mobile without JavaScript page errors or tested page overflow. Tests cover navigation, sliders, numeric values, both genuine result banners, loading, disabled duplicate submits, reset/focus, server errors, details, PDF and CSV downloads, all model visualization tabs, metric sorting, report preview/history pagination, new-batch control reset and all CSV fixtures. The dashboard and model metadata match original artifacts. Probability labels remain uncalibrated estimates, eight unit-based checks remain unverified, and microbial-testing limitations remain visible.

20 saved analyses were retrieved and matched to original inputs/API results; PDF IDs, timestamps, model identity, version, labels, rounded display probabilities and **all nine full-precision measurements** match. Final rendered PDF pages were visually reviewed; repeated table headers avoid orphaned titles.

Malformed JSON, invalid IDs, traversal, file extension/byte/row limits, NaN/infinity, oversized numbers, script/formula text, allowed/disallowed CORS and generic errors were exercised. No stack traces are disclosed to clients. Formula strings cannot enter numeric data and export text has defensive escaping.

## I — Repairs and performance

See BUG_FIX_LOG.md for reproduced root causes, files and regressions. No redesign was performed. The batch tree-path preprocessing was vectorized after identifying repeated per-row transforms. Recorded application-level timings (one local run, not a benchmark guarantee):

| Operation | Seconds |
|---|---:|
| Model loading | 0.140 |
| API TestClient startup | 0.711 |
| Median single prediction | 0.174 |
| Batch 10 | 0.364 |
| Batch 100 | 0.299 |
| Batch 500 | 0.751 |
| Batch 1000 | 1.221 |

Previous 1,000-row time: 5.013s. Metadata JSON is 161,602 bytes. Frontend bundle sizes are recorded by the production build; charts remain lazy-loaded. Timings include persistence/JSON and vary with local load.

## J — Final verdict and limitations

Core workflows pass. AdaBoost severely under-detects potable labels, RF misses some positive records, probabilities are uncalibrated, measurement units/provenance are incompletely verified and the dataset lacks essential microbial/contaminant tests. Predictions cannot certify drinking safety. Bayesian-style averaging is an approximation, GAM is genuinely implemented, and MARS/SHAP remain honestly marked absent. No metric or threshold was changed to manufacture improvement. One upstream Starlette/httpx deprecation and harmless Zod build annotations remain; no failing core tests remain.

Artifacts: FINAL_TEST_SUMMARY.json, MODEL_DIVERSITY_ANALYSIS.md, POTABLE_NONPOTABLE_TEST_RESULTS.csv, INDIVIDUAL_BATCH_PARITY.csv, CSV_TEST_RESULTS.md, BUG_FIX_LOG.md, TRAINING_OOF_THRESHOLDS.csv, SENSITIVITY_ANALYSIS.csv, model-distributions.png, confusion-matrices.png, sensitivity-analysis.png, actual-class browser screenshots and rendered PDF page PNGs. Reproduce with python -m tests.generate_test_csvs and python -m tests.run_audit; browser setup is documented in README.md.
