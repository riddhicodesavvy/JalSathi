# Verified original Potable predictions

Verified against the actual running API at `http://127.0.0.1:8000/api/v1/predict` and frontend at `http://127.0.0.1:5173/analyze`. Primary model: **Random Forest (`rf`)**. Version: `904004bde7-seed42-v1`. Fixed threshold: **0.5**.

**These are dataset-labeled examples and model predictions, not laboratory-certified drinking water.** Probabilities are uncalibrated model estimates, not probabilities that water is scientifically safe. Microbial and other essential tests are missing; eight unit-based reference checks remain unverified.

## Selection and provenance

2011 original rows have all nine measurements. 698 complete rows have original label 1 and RF prediction 1. The five examples below have the highest class-1 probabilities within that qualifying collection. **All five selected positive examples belong to the training partition.** Their probabilities are selected demonstrations of the saved fitted model, not an unbiased estimate of unseen-sample performance. Original dataset labels and predicted labels are recorded separately. No retraining, threshold tuning, heuristic override or default substitution was performed.

Original CSV numeric strings were retained in the upload fixture; JSON/form values use full round-trip floating-point numbers. Dataset indexes are zero-based; CSV line numbers count the header as line 1.

Dataset SHA-256: `904004bde729bfe3d2e195f46343bceead09e32a0eb95bb8184e7e20e029b2bf`.

## Five verified Potable examples

### Example 1 — dataset index 1527

CSV line **1529**; partition **training**; original label **1**; primary prediction **1 (Predicted Potable)**.

Random Forest **P(class 1) = `0.9249881844042929`** (92.498818440429%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 7.301444654287731 |
| Hardness | 143.43135025761057 |
| Solids | 46718.55596534806 |
| Chloramines | 4.768780800964818 |
| Sulfate | 252.46648472775968 |
| Conductivity | 446.83967260296896 |
| Organic_carbon | 12.575416892102169 |
| Trihalomethanes | 60.64840389938017 |
| Turbidity | 3.1600748401136087 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 1 |
| Random Forest | 1 | 0.9249881844042929 |
| AdaBoost | 1 | 0.6955696078335103 |
| Gradient Boosting | 1 | 0.8936282281728675 |
| Voting Ensemble | 1 | 0.8785465051026676 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `62a815e7-ec28-4821-836e-a505f3b6a6a5`. [Browser screenshot](verified-potable-1.png). Independent pH reference check: **within**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 2 — dataset index 2851

CSV line **2853**; partition **training**; original label **1**; primary prediction **1 (Predicted Potable)**.

Random Forest **P(class 1) = `0.9123171762080672`** (91.231717620807%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 8.163999617620284 |
| Hardness | 195.21249526095846 |
| Solids | 27414.899122937924 |
| Chloramines | 5.4124813846444635 |
| Sulfate | 231.72422478606262 |
| Conductivity | 529.6818065825521 |
| Organic_carbon | 12.425426010087335 |
| Trihalomethanes | 69.99012794495474 |
| Turbidity | 3.67308809381557 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 0.808492298467189 |
| Random Forest | 1 | 0.9123171762080672 |
| AdaBoost | 1 | 0.6955696078335103 |
| Gradient Boosting | 1 | 0.8680236326858107 |
| Voting Ensemble | 1 | 0.8211006787986442 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `7db25e49-cc6a-4985-8031-a0849037e581`. [Browser screenshot](verified-potable-2.png). Independent pH reference check: **within**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 3 — dataset index 1181

CSV line **1183**; partition **training**; original label **1**; primary prediction **1 (Predicted Potable)**.

Random Forest **P(class 1) = `0.9089332505057248`** (90.893325050572%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 9.792727768555453 |
| Hardness | 161.05788144753413 |
| Solids | 30249.170845011024 |
| Chloramines | 5.214315143188376 |
| Sulfate | 258.03885201408383 |
| Conductivity | 413.1554659517622 |
| Organic_carbon | 12.493388330953849 |
| Trihalomethanes | 76.2255797341665 |
| Turbidity | 3.729120401580513 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 1 |
| Random Forest | 1 | 0.9089332505057248 |
| AdaBoost | 1 | 0.6585870578104859 |
| Gradient Boosting | 1 | 0.8986475162678549 |
| Voting Ensemble | 1 | 0.8665419561460164 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `321c4635-e9cb-40e2-80d6-c395d3dadca6`. [Browser screenshot](verified-potable-3.png). Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 4 — dataset index 1189

CSV line **1191**; partition **training**; original label **1**; primary prediction **1 (Predicted Potable)**.

Random Forest **P(class 1) = `0.9017430785767819`** (90.174307857678%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 6.859323725529028 |
| Hardness | 179.0688054957262 |
| Solids | 27567.375669680983 |
| Chloramines | 5.885557479524616 |
| Sulfate | 227.3484603094109 |
| Conductivity | 391.59970804108104 |
| Organic_carbon | 14.670554903689094 |
| Trihalomethanes | 83.46993430779078 |
| Turbidity | 4.501980014505442 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 1 |
| Random Forest | 1 | 0.9017430785767819 |
| AdaBoost | 1 | 0.6955696078335103 |
| Gradient Boosting | 1 | 0.8792671706408384 |
| Voting Ensemble | 1 | 0.8691449642627826 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `28499945-bdab-4eb5-be76-6a64b6db5ade`. [Browser screenshot](verified-potable-4.png). Independent pH reference check: **within**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 5 — dataset index 1137

CSV line **1139**; partition **training**; original label **1**; primary prediction **1 (Predicted Potable)**.

Random Forest **P(class 1) = `0.887730767807966`** (88.773076780797%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 8.722143776841188 |
| Hardness | 151.6211320112265 |
| Solids | 28301.516948548786 |
| Chloramines | 3.651961339353696 |
| Sulfate | 248.09475894507978 |
| Conductivity | 468.36745137041055 |
| Organic_carbon | 15.15117258217083 |
| Trihalomethanes | 79.53836757802165 |
| Turbidity | 3.2746286418408777 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 1 | 1 |
| Random Forest | 1 | 0.887730767807966 |
| AdaBoost | 1 | 0.6585870578104859 |
| Gradient Boosting | 1 | 0.8732163189865675 |
| Voting Ensemble | 1 | 0.8548835361512549 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `7de09703-7744-4338-a02f-3bd21d15a3ad`. [Browser screenshot](verified-potable-5.png). Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

## Five verified Non-Potable controls

### Example 1 — dataset index 468

CSV line **470**; partition **training**; original label **0**; primary prediction **0 (Predicted Non-Potable)**.

Random Forest **P(class 1) = `0.039993588253182236`** (3.999358825318%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 4.370476580258797 |
| Hardness | 188.6540372531146 |
| Solids | 29542.338165335546 |
| Chloramines | 8.117114132677262 |
| Sulfate | 301.02218217666064 |
| Conductivity | 456.3084538577487 |
| Organic_carbon | 16.34683847675535 |
| Trihalomethanes | 46.69694092362607 |
| Turbidity | 4.64938203413864 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 0 | 0.14801778436457944 |
| Random Forest | 0 | 0.039993588253182236 |
| AdaBoost | 0 | 0.19331944311597457 |
| Gradient Boosting | 0 | 0.11510055367496795 |
| Voting Ensemble | 0 | 0.12410784235217606 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `efea2ec0-7be9-439c-b654-ccd2a2d55d40`. Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 2 — dataset index 1851

CSV line **1853**; partition **training**; original label **0**; primary prediction **0 (Predicted Non-Potable)**.

Random Forest **P(class 1) = `0.0469560644038207`** (4.695606440382%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 3.8788793890688 |
| Hardness | 177.71284092836623 |
| Solids | 21937.47156902812 |
| Chloramines | 7.369768571309858 |
| Sulfate | 299.2416239048493 |
| Conductivity | 447.30375575365935 |
| Organic_carbon | 12.451911879217278 |
| Trihalomethanes | 63.16311345592596 |
| Turbidity | 4.927711075497064 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 0 | 0 |
| Random Forest | 0 | 0.0469560644038207 |
| AdaBoost | 0 | 0.19331944311597457 |
| Gradient Boosting | 0 | 0.13003671525509838 |
| Voting Ensemble | 0 | 0.0925780556937234 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `7ffc8a6c-5b84-4855-8deb-234be2489cc6`. Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 3 — dataset index 100

CSV line **102**; partition **training**; original label **0**; primary prediction **0 (Predicted Non-Potable)**.

Random Forest **P(class 1) = `0.05385089909607964`** (5.385089909608%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 4.270716194733736 |
| Hardness | 166.83770854028538 |
| Solids | 24405.250534952756 |
| Chloramines | 7.3915101384206565 |
| Sulfate | 297.20673916830356 |
| Conductivity | 349.5189103676489 |
| Organic_carbon | 13.478526445498858 |
| Trihalomethanes | 54.47483954440166 |
| Turbidity | 3.763905902952325 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 0 | 0 |
| Random Forest | 0 | 0.05385089909607964 |
| AdaBoost | 0 | 0.19331944311597457 |
| Gradient Boosting | 0 | 0.1269960188708271 |
| Voting Ensemble | 0 | 0.09354159027072032 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `91e76917-a879-4148-83e0-a146240a5826`. Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 4 — dataset index 2993

CSV line **2995**; partition **training**; original label **0**; primary prediction **0 (Predicted Non-Potable)**.

Random Forest **P(class 1) = `0.06121238291765132`** (6.121238291765%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 3.1020755653395566 |
| Hardness | 198.48865056001767 |
| Solids | 45148.80811766023 |
| Chloramines | 7.821650422876534 |
| Sulfate | 324.64407957923544 |
| Conductivity | 427.2167644660192 |
| Organic_carbon | 15.53012277971635 |
| Trihalomethanes | 54.574254304233314 |
| Turbidity | 4.2480753693420485 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 0 | 0.14801778436457944 |
| Random Forest | 0 | 0.06121238291765132 |
| AdaBoost | 0 | 0.19331944311597457 |
| Gradient Boosting | 0 | 0.06188747005620765 |
| Voting Ensemble | 0 | 0.11610927011360325 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `4ec3b5c9-4075-4849-959b-7d47e65a683b`. Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

### Example 5 — dataset index 2161

CSV line **2163**; partition **training**; original label **0**; primary prediction **0 (Predicted Non-Potable)**.

Random Forest **P(class 1) = `0.06467804029241937`** (6.467804029242%). Agreement with primary class: **5/5**.

| Required feature | Original CSV value |
|---|---:|
| ph | 4.16111196816975 |
| Hardness | 181.73638869560602 |
| Solids | 25815.389206539712 |
| Chloramines | 8.53462900071612 |
| Sulfate | 297.23921899210234 |
| Conductivity | 399.2921708958753 |
| Organic_carbon | 9.343333976076622 |
| Trihalomethanes | 46.63808080379271 |
| Turbidity | 4.16824218857341 |

| Classifier | Predicted class | P(class 1) |
|---|---:|---:|
| CART | 0 | 0.14801778436457944 |
| Random Forest | 0 | 0.06467804029241937 |
| AdaBoost | 0 | 0.19331944311597457 |
| Gradient Boosting | 0 | 0.12200713075264855 |
| Voting Ensemble | 0 | 0.13200559963140548 |

**API verification: PASS.** Exact nine input mappings, primary model/version, class, all five probabilities (absolute tolerance 1e-12), computed agreement, saved history and API-generated PDF match direct inference.

**Browser verification: PASS.** Exact edited inputs reached the live API. The banner, ring text and arc length, individual classifier indicators and independent guideline statuses matched the response. The downloaded PDF contains the same measurements, ID, version, probability and prediction. Educational disclaimers remained visible; no safety guarantee was displayed.

Browser analysis ID: `85b7b44c-f9f5-4c13-94de-be983599446a`. Independent pH reference check: **outside**; other eight references **unverified**. A model-positive classification does not override a pH reference breach.

## Verification summary

- Five distinct original positive-labeled rows predicted Potable by the saved RF pipeline.
- Five original negative-labeled controls predicted Non-Potable by the same pipeline.
- Ten initial live API predictions, ten alternating real browser submissions, and twenty actual PDFs verified.
- Five-row upload fixture accepted through the live batch API: 5/5 Predicted Potable, zero probability mismatches.
- All fifty initial model-wise probabilities matched direct inference; all browser responses matched corresponding direct RF estimates.
- Browser JavaScript errors: zero. Prediction/integration bugs found: none. One test selector was corrected to target the existing indicator tooltip; application code was unchanged.
- Dataset, model artifacts and the production threshold remained unchanged.

Upload file: `tests/fixtures/verified_potable_samples.csv` (only the nine features, no target). Machine-readable provenance and responses: `verified_potable_evidence.json` and `verified_potable_browser_evidence.json`. Reproduce: `python -m tests.verify_potable_examples`; `cd frontend; node node_modules/@playwright/test/cli.js test --config playwright.potable.config.ts`; `python -m tests.write_verified_potable_report` from the root. These commands intentionally create real analysis history entries because they verify the actual deployed app.
