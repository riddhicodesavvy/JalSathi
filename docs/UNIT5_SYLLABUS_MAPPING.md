# Machine Learning Unit 5 — Topic Implementation Mapping

| Unit 5 topic | Implementation | File/module | UI demonstration | Status |
|---|---|---|---|---|
| CART | Gini DecisionTreeClassifier, bounded depth/leaf search | `ml/train.py`, `backend/app/inference.py` | Model Comparison tree; Analyze Model Details path | Trained; artifact/prediction tests pass |
| Ensemble Learning | Bootstrap RandomForestClassifier with OOB evaluation | `ml/train.py` | Model Comparison and agreement indicators | Trained; evaluated and tested |
| Boosting | AdaBoostClassifier with stump weak learners | `ml/train.py` | Model Comparison and predictions | Trained; evaluated and tested |
| Boosting | GradientBoostingClassifier | `ml/train.py` | Model Comparison and predictions | Trained; evaluated and tested |
| Ensemble Learning | Equal-weight independent soft VotingClassifier | `ml/train.py` | Model Agreement and comparison | Trained; evaluated and tested |
| Bayesian Model Averaging | Validation-likelihood plug-in model averaging | `ml/extensions.py` | About advanced demonstrations | Tested approximation only, not rigorous BMA |
| Generalized Additive Models | Penalized additive logistic B-spline GAM | `ml/extensions.py` | About fitted feature effects | Trained; probability/additivity tests pass |
| Adaptive Basis Function Models | MARS investigation and limitation | `ml/extensions.py`, `docs/ML_METHODOLOGY.md` | About syllabus and limitation | Not implemented; no false substitution |

## CART and Practical 1

**Practical 1: Implement CART learning algorithms to perform categorization.** CART recursively partitions feature space to reduce Gini impurity, categorizing binary Potability. JalSathi tunes maximum depth and minimum leaf size on training folds. `cart.joblib` stores the fitted imputation/tree pipeline. The Model Comparison diagram is the actual tree displayed through depth 3; Analyze Model Details traverses the actual nodes for a supplied sample. The observed held-out confusion matrix and nonempty decision path demonstrate implementation. Viva: explain the split rule, impurity reduction, leaf class probabilities, pruning/complexity control and overfitting.

## Random Forest and Practical 2

**Practical 2: Implement Ensemble learning models to perform classification.** Random Forest combines 160 bootstrap trees with random feature subsets. Averaging reduces individual-tree variance. `ml/train.py` tunes depth and leaf complexity, saves OOB and test results, and exposes measured feature importance. Compare its actual confusion matrix against CART in Model Comparison. Viva: distinguish bootstrap bagging, random feature selection, OOB validation and a final held-out test. Primary selection came from training CV, not an assumed ensemble advantage.

## AdaBoost

AdaBoost sequentially fits weak decision stumps and increases emphasis on misclassified training observations. Stage count and learning rate are tuned. The saved model, actual metrics and API predictions demonstrate the Unit 5 boosting topic. Open its View Details card and inspect stage/rate hyperparameters. Viva: explain sample reweighting, weak learners and sensitivity to noisy labels.

## Gradient Boosting

Gradient Boosting fits trees to negative gradients of classification loss, iteratively reducing residual error. JalSathi tunes stage count, rate and depth. Compare test performance and influence against AdaBoost in Model Comparison. Viva: contrast sample reweighting with gradient-based function fitting; explain shrinkage and tree complexity.

## Voting / combining models

Soft Voting averages four independent member probabilities equally, with no nested voting model or duplicate member. Agreement indicators display each actual model's classification, while the voting result itself comes from the fitted VotingClassifier. It need not outperform every member. Viva: contrast voting with bagging and boosting, probability averaging with majority voting, and correlated errors with complementary models. Inspect `hyperparameters.members` and the actual metric table.

## Bayesian-style model averaging demonstration

Rigorous BMA integrates predictions over model and parameter posteriors. These fitted sklearn trees do not supply Bayesian marginal likelihoods. The extension uses fixed candidates, an internal training-only holdout and equal-prior validation log-likelihood weights. About shows actual weights and held-out balanced accuracy. Artifact tests check normalization and explicit approximation labels. Viva: derive the normalized weight formula, explain concentration, and state that conditioning on fitted parameters omits parameter integration. Never describe ordinary accuracy weights or equal voting as BMA.

## Generalized additive model

An additive logistic model has logit(p) = intercept + sum of nonlinear feature effects. The extension fits separate cubic spline bases and a regularized logistic link, with knot/penalty CV inside training. About displays genuine centered log-odds effects. Tests verify probability shape and additive superposition in logit space. Viva: explain the link function, nonlinear univariate effects, regularization, centering and the absence of interactions. Actual results are in `ml/artifacts/extensions.json`.

## Adaptive basis models

MARS learns and prunes hinge-function bases, potentially including interactions. It could model nonlinear thresholds, but this project does not include a reliable compatible MARS implementation. The fixed-knot spline GAM and Random Forest must not be called MARS. The UI and extension metadata consistently mark this not implemented. Viva: explain the methodological distinction and the dependency limitation honestly.

Core numerical evidence is in `reports/evaluations/MODEL_EVALUATION.md`; optional results are in `ml/artifacts/extensions.json`. Dataset and scientific limitations remain part of every demonstration.
