# Saved held-out evaluation

| Model | Accuracy | Precision | Recall | F1 | Balanced accuracy | ROC-AUC | PR-AUC | False-potable rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CART | 0.6128 | 0.5043 | 0.4531 | 0.4774 | 0.5841 | 0.6104 | 0.5230 | 0.2850 |
| Random Forest | 0.6524 | 0.5753 | 0.4180 | 0.4842 | 0.6102 | 0.6653 | 0.6028 | 0.1975 |
| AdaBoost | 0.6204 | 0.6842 | 0.0508 | 0.0945 | 0.5179 | 0.5656 | 0.4471 | 0.0150 |
| Gradient Boosting | 0.6570 | 0.6372 | 0.2812 | 0.3902 | 0.5894 | 0.6545 | 0.5841 | 0.1025 |
| Voting Ensemble | 0.6662 | 0.6697 | 0.2852 | 0.4000 | 0.5976 | 0.6518 | 0.5905 | 0.0900 |

Primary model: rf. Selection: Maximum training CV balanced accuracy; Brier score breaks ties. Threshold 0.5.

656 held-out observations: 400 non-potable and 256 potable. Positive class is 1. False-potable rate is FP/(TN+FP). PR-AUC is average precision. Probabilities are uncalibrated. Higher thresholds reduce false-potable mistakes while losing potable recall; inspect the saved per-model threshold analysis. These test curves are descriptive and were not used for selection.
