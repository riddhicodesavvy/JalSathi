# Model diversity and AdaBoost diagnosis

| Model | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | TN / FP / FN / TP | Predicted 0 / 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CART | 0.6128 | 0.5841 | 0.5043 | 0.4531 | 0.4774 | 0.6104 | 0.5230 | 286 / 114 / 140 / 116 | 426 / 230 |
| Random Forest | 0.6524 | 0.6102 | 0.5753 | 0.4180 | 0.4842 | 0.6653 | 0.6028 | 321 / 79 / 149 / 107 | 470 / 186 |
| AdaBoost | 0.6204 | 0.5179 | 0.6842 | 0.0508 | 0.0945 | 0.5656 | 0.4471 | 394 / 6 / 243 / 13 | 637 / 19 |
| Gradient Boosting | 0.6570 | 0.5894 | 0.6372 | 0.2812 | 0.3902 | 0.6545 | 0.5841 | 359 / 41 / 184 / 72 | 543 / 113 |
| Voting Ensemble | 0.6662 | 0.5976 | 0.6697 | 0.2852 | 0.4000 | 0.6518 | 0.5905 | 364 / 36 / 183 / 73 | 547 / 109 |

All metrics were independently recomputed from all 656 held-out rows, including original missing values passed through fitted imputation. Every saved scalar, confusion matrix, ROC and PR curve matches. Positive class is Potability=1. All probabilities are uncalibrated.

## AdaBoost: low recall, not a broken input path

The fitted 60-stump model predicts potable only 19/656 times (2.90%): TP=13, FP=6, FN=243, TN=394. Potable recall is 5.08%, precision 68.42%, and F1 9.45%. Its average P(potable) is 0.303588 with 28 unique held-out probabilities spanning 0.193319–0.695570. The model is fitted and input-dependent but severely biased toward the majority non-potable class at the fixed 0.5 threshold.

Training labels contain 1,598 non-potable and 1,022 potable rows (61%/39%); held-out labels contain 400/256 with essentially the same proportions. Feature order, training-only median statistics, class ordering, raw predictions and probability thresholding all pass. All 60 estimators are present; their later weighted errors approach 0.498 and weights are small. This is consistent with limited stump discrimination plus class imbalance and the threshold, rather than a preprocessing/default-submission defect. No causal claim about one isolated cause is warranted.

The same poor recall appears in training out-of-fold predictions (about 5.19% at 0.5). Threshold sensitivity uses training rows only, not test labels. Hyperparameters were already selected on those training rows, so this is a diagnostic with selection optimism, not a new unbiased validation study.

| Threshold | Precision | Recall | Specificity | Balanced accuracy | False-potable rate |
|---|---:|---:|---:|---:|---:|
| 0.30 | 0.4072 | 0.7231 | 0.3267 | 0.5249 | 0.6733 |
| 0.35 | 0.4801 | 0.2710 | 0.8123 | 0.5417 | 0.1877 |
| 0.40 | 0.5061 | 0.2035 | 0.8730 | 0.5382 | 0.1270 |
| 0.45 | 0.5376 | 0.0910 | 0.9499 | 0.5205 | 0.0501 |
| 0.50 | 0.6625 | 0.0519 | 0.9831 | 0.5175 | 0.0169 |
| 0.55 | 0.7069 | 0.0401 | 0.9894 | 0.5147 | 0.0106 |
| 0.60 | 0.6939 | 0.0333 | 0.9906 | 0.5119 | 0.0094 |
| 0.65 | 0.6552 | 0.0186 | 0.9937 | 0.5062 | 0.0063 |
| 0.70 | 0.6250 | 0.0049 | 0.9981 | 0.5015 | 0.0019 |

A lower threshold can recover recall while creating many more false-potable predictions: at 0.30 the false-potable rate reaches about 67.3%. No production threshold or artifact was changed to force both classes or improve screenshots. Further model improvement requires a separate, prespecified training-only study.

## Random Forest and diverse inputs

RF produces 186 potable and 470 non-potable classifications on the full held-out set, 656 unique probabilities from 0.149059 to 0.868813. Repeated non-potable results for medians or nearby inputs are legitimate; the model is not collapsed or cached. Primary selection reproduces the stored training-CV rule: RF balanced accuracy 0.6164 versus Voting 0.5914; test accuracy is not the selection rule.

| Model | Inputs | Potable | Non-potable | Unique probabilities | Minimum | Maximum | Mean | Std. dev. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cart | 220 | 93 | 127 | 33 | 0.000000 | 1.000000 | 0.520990 | 0.248784 |
| rf | 220 | 101 | 119 | 201 | 0.085971 | 0.840246 | 0.481843 | 0.138352 |
| ada | 220 | 32 | 188 | 42 | 0.193319 | 0.775663 | 0.356682 | 0.141649 |
| gb | 220 | 112 | 108 | 207 | 0.075541 | 0.993276 | 0.521385 | 0.258156 |
| voting | 220 | 90 | 130 | 207 | 0.103531 | 0.877771 | 0.470225 | 0.162270 |

The 220 generated cases cover all requested groups A–K, with no synthetic labels. See DIVERSITY_BY_GROUP.csv for every group and model. All five models naturally produce both classes across this diverse collection. Trees are piecewise constant, so individual parameter changes need not change probabilities. The sensitivity CSV records all 315 feature/model/value comparisons; the plot preserves unchanged plateaus. Correct submission of all nine features does not imply every fitted model uses every feature at every point.

| Model | Positive rows predicted potable / 50 | Subset recall | Negative rows predicted potable / 50 | Subset false-potable rate |
|---|---:|---:|---:|---:|
| cart | 26 | 52.0% | 18 | 36.0% |
| rf | 26 | 52.0% | 11 | 22.0% |
| ada | 5 | 10.0% | 2 | 4.0% |
| gb | 18 | 36.0% | 5 | 10.0% |
| voting | 19 | 38.0% | 6 | 12.0% |

These selected complete-row subset rates are descriptive and differ from the full held-out recall; use the 656-row evaluation for overall performance. See model_health.json for probability quantiles, calibration labels and complete classification reports.
