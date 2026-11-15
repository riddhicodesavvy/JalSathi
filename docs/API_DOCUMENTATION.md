# API guide

Base: `/api/v1`. Interactive OpenAPI documentation: `/docs`.

| Method | Route | Behavior |
|---|---|---|
| GET | `/health` | API status and five-model availability |
| GET | `/models`, `/models/metrics` | Primary selection, actual per-model CV/test metrics and curves |
| GET | `/models/{id}` | Actual metadata for cart, rf, ada, gb or voting |
| POST | `/predict` | Validate, infer, explain and persist one sample |
| POST | `/predict/batch` | Multipart CSV; valid results, row errors, aggregate counts |
| GET | `/batches/{uuid}/csv` | Download persisted valid predictions |
| GET | `/dataset/summary` | Original file statistics and fingerprint |
| GET | `/features` | Required feature names, control ranges, defaults and reference context |
| GET | `/analyses?limit=10&offset=0` | Paginated history, maximum 100 per request |
| GET | `/analyses/{uuid}` | Saved measurements and prediction snapshot |
| GET | `/reports/{uuid}/pdf` | Generate a real analysis-specific PDF and record its path |
| GET | `/plots/{filename}` | Allowlisted fitted tree, GAM effects or model evaluation PNG |
| GET | `/samples/csv` | Genuine complete rows selected from the source dataset |
| GET | `/extensions` | Actual optional extension results and honest implementation statuses |

`POST /predict` accepts exactly `ph`, `Hardness`, `Solids`, `Chloramines`, `Sulfate`, `Conductivity`, `Organic_carbon`, `Trihalomethanes`, `Turbidity`. All must be finite numbers: pH 0–14, other features 0–1e9. Broad non-pH bounds are technical validation limits, **not scientific safety ranges**. Feature sliders use observed dataset scale for exploration; values outside training range generate warnings. Extra request fields are rejected.

Responses include UUID, UTC timestamp, measurements, model/version, all five classifications and probabilities, selected-class estimate, agreement count/percentage, reference checks, warnings, fitted CART path and disclaimer. Probabilities are explicitly uncalibrated. Reference statuses are independent of classifications.

Batch uploads require UTF-8 `.csv` files with exact unique headers. Optional `Potability` is ignored. Maximum 2 MB and 1,000 rows. Blank/malformed numeric rows are reported by original CSV line number. Structural/encoding problems reject the file; valid rows from mixed files are analyzed and persisted atomically with batch metadata. Inference never trains.

Errors use `{"error":{"message":"...","details":[...]}}` where details are present for request validation. Codes: 413 size/row limit, 415 file extension, 422 schema/value error, 404 unknown resources, 503 missing models, 500 generic internal error. Health still reports model unavailability honestly. Model files are loaded only from the configured trusted local directory.
