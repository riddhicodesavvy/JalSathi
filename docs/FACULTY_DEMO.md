# Reproducible faculty demonstration

1. Run `./scripts/setup.ps1` once if dependencies or artifacts are missing; run `./scripts/start.ps1` from the root.
2. Open http://127.0.0.1:5173/dashboard. Show the verified 3,276 rows, nine features, class distribution and actual held-out model performance.
3. Open Analyze Sample. Explain that initial values are dataset medians for exploration, not a real collected water sample. Replace them with a complete row from `data/samples/demo.csv`.
4. Analyze. Explain primary Random Forest selection, actual five-model disagreement/agreement, selected-class uncalibrated probability, pH reference check, eight unverified unit-based checks, and visible limitations.
5. Open Model Details to trace actual CART decisions. Feature splits explain the fitted tree and do not prove causation.
6. Change pH to 0, analyze again, and show the pH breach and out-of-training-range warning. Neither the model label nor its percentage overrides missing essential safety testing.
7. Download the real PDF. Match its UUID, measurements, classifications and warnings to the saved analysis.
8. Open Model Comparison. Sort balanced accuracy, inspect the confusion matrices and false-potable rate, ROC/PR curves, permutation importance and fitted CART diagram. Show threshold tradeoffs in View Details.
9. Open Batch Analysis. Download and upload the genuine source-row CSV. Inspect real results and counts; filter, sort and export predictions. Introduce a missing/negative value in a copy to demonstrate row-level errors.
10. Open Reports and preview/download the saved result. History persists across API restarts in SQLite.
11. Open About. Show the complete core Unit 5 topics, actual additive GAM effect plots and the Bayesian-style approximation caveat. MARS remains clearly marked not implemented.
12. Review `docs/UNIT5_SYLLABUS_MAPPING.md` and `reports/evaluations/MODEL_EVALUATION.md` during viva.

The demonstration CSV contains genuine complete source measurements. Predictions are always computed from fitted artifacts; no expected labels or model results are hardcoded. Demo defaults, source records and real collected samples must be described distinctly.
