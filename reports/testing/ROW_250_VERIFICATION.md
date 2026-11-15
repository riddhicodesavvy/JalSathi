# Original dataset row 250 verification

Original dataset index: **250 (zero-based; CSV line 252)**. Original Potability label: **1**.

The supplied six-decimal measurements and the original full-precision measurements both produce **Predicted Potable (class 1)** with saved primary Random Forest **P(class 1) = 0.6263747470354587**. The real FastAPI endpoint matches direct inference within 1e-12. The live browser form submitted exactly the supplied values and displayed **Predicted Potable**, **62.6% Model Estimate**, and **3/5 agreement**. Browser page errors: zero.

| Feature | Supplied value | Original CSV value |
|---|---:|---:|
| ph | 9.44513 | 9.445129837868656 |
| Hardness | 145.805402 | 145.80540244684383 |
| Solids | 13168.529156 | 13168.529155675998 |
| Chloramines | 9.444471 | 9.44447108562294 |
| Sulfate | 310.583374 | 310.583373858597 |
| Conductivity | 592.659021 | 592.6590209759507 |
| Organic_carbon | 8.606397 | 8.606396746986945 |
| Trihalomethanes | 77.57746 | 77.57745951035697 |
| Turbidity | 3.875165 | 3.8751652466165467 |

| Model | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 0.5381138897258213 |
| Random Forest | 1 | 0.6263747470354587 |
| AdaBoost | 0 | 0.2398309013423312 |
| Gradient Boosting | 1 | 0.5156198358380972 |
| Voting Ensemble | 0 | 0.47998484348542714 |

No direct/API/UI mismatch was found and no application fix was required. Models, artifact hashes and the fixed 0.5 threshold are unchanged. The independent pH reference check remains outside range; a positive ML classification does not override it. Probabilities are uncalibrated educational estimates, not safety guarantees.

The existing tests/fixtures/verified_potable_samples.csv was re-uploaded to the actual batch endpoint: all five original examples were again predicted Potable, with probabilities matching direct inference. Exact nine-value combinations and row provenance remain in VERIFIED_POTABLE_EXAMPLES.md; the evidence JSON records their current API verification.

Browser screenshot: [row250-frontend.png](row250-frontend.png). Machine-readable evidence: ROW_250_VERIFICATION.json and ROW_250_BROWSER_VERIFICATION.json.
