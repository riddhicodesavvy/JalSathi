# Machine learning methodology

The original dataset has nine measurements and binary Potability. Class 1 is potable; class 0 is non-potable. `ml/data.py` verifies the exact schema, finite-or-missing features, numeric data and binary labels. It fingerprints the original file. Duplicates, missingness, negative values and IQR outliers are reported; no arbitrary row removal occurs.

`python -m ml.train` splits 80% training (2,620 rows), 20% test (656), stratified at random seed 42. It fits median imputation within each pipeline and CV fold. Trees do not require scaling. The optional GAM fits imputation, separate B-spline bases and scaling inside its training folds. A bounded three-fold stratified grid search evaluates CART depth/leaf size, forest depth/leaf size, AdaBoost stage count/rate, and Gradient Boosting stages/rate/depth. All search candidates use only training rows.

Median imputation is robust to the flagged extremes and preserves all observed records. `scripts/verify_artifacts.py` also compares median against mean imputation on a prespecified CART using only training CV; both produced 0.5596 balanced accuracy in this diagnostic. Results are in `reports/evaluations/imputation_comparison.json`. This is a sensitivity diagnostic, not a test-set-driven pipeline alteration. Raw extremes are retained because their laboratory validity is unknown.

Soft Voting clones the four tuned pipelines into independently fitted members and averages their probabilities equally. No nested voting member duplicates a base model. Voting receives the same CV protocol. Because hyperparameters were selected on these training folds, reported selection CV scores have model-selection optimism; they are not nested-CV generalization estimates. The final held-out partition remains untouched until evaluation.

Primary selection maximizes CV balanced accuracy, using CV Brier score as tie-break. Balanced accuracy weighs the minority potable class and majority non-potable class equally. Brier scores assess raw probabilistic error. Forest OOB accuracy is supplementary, not primary selection. Probabilities are not calibrated; the app says so explicitly. Calibration is deferred until an independently designed calibration study can justify an improvement and its interpretation. The 0.5 classification threshold is fixed, never tuned on the final test.

The registry records accuracy, potable precision/recall/F1, balanced accuracy, ROC-AUC, average precision (the PR-AUC convention used here), Brier score, log loss, confusion matrix and classification report. It reports the safety-relevant false-potable rate FP/(TN+FP): actual non-potable samples incorrectly predicted potable. Stored threshold analyses at 0.3, 0.5, 0.7 and 0.9 describe tradeoffs, not deployment recommendations. Raising a threshold may reduce false-potable predictions at the cost of potable recall. No tested threshold certifies water safety.

CART paths and tree diagrams use actual fitted splits. Tree-based impurity importance and test permutation importance are saved separately. Permutation importance measures mean test balanced-accuracy change over three random permutations. It is descriptive, may be negative, and is never used for feature selection or test-based model selection. These explanations are not SHAP and do not establish causal effects. SHAP is not installed or claimed.

## Advanced demonstrations

`python -m ml.extensions` trains a genuine generalized additive binary model: logit(p) = intercept + sum_j f_j(x_j). Each f_j is a cubic B-spline expansion; L2 regularization controls coefficient size. It uses scikit-learn rather than a separate pyGAM dependency. Knot count and regularization are selected by training-only CV. `gam-effects.png` shows feature contributions centered at training medians on the log-odds scale. No feature interactions are present; additivity is tested.

The Bayesian-style demonstration uses four **fixed** classifier configurations. It partitions the core training rows into 75% fitting and 25% validation. Each candidate pipeline is fitted on the former, then equal-prior plug-in model weights satisfy:

`w_m ∝ exp(sum_i log p_m(y_i | x_i))`

Validation weights normalize by a log-sum-exp stabilization, and predictions average the fixed candidates' probabilities. The final test labels never determine weights. This conditions on fitted parameter estimates and does not integrate parameter uncertainty or compute a Bayesian marginal likelihood. It is explicitly **not rigorous BMA**, and concentrated weights reveal model dominance rather than guaranteed superior averaging. The four weighted candidates remain fitted on the internal fitting partition so their evaluated meaning does not change after weighting.

Adaptive MARS is not implemented. It needs learned hinge placement, interaction selection and pruning; a fixed-knot GAM must not be called MARS. There is no included reliable Windows MARS dependency. The five core models remain fully functional without it.

All fitted artifacts are local trusted outputs. The registry includes model IDs, version, feature order, fingerprint, seed, split indices, CV results, hyperparameters, timestamps and package versions. Exact Python dependencies are recorded separately. Never unpickle untrusted external files.
