# CSV matrix: actual API and browser results

All 15 fixtures were uploaded through both the real API and browser UI. Duplicate measurements are intentionally retained with unique analysis IDs and input order. Invalid numeric rows return structured row errors; structural failures reject the upload.

| File | Submitted | Accepted | Rejected | HTTP | Seconds | Export verified | Browser handled |
|---|---:|---:|---:|---:|---:|---|---|
| potable_labeled_25.csv | 25 | 25 | 0 | 200 | 0.269 | True | True |
| nonpotable_labeled_25.csv | 25 | 25 | 0 | 200 | 0.190 | True | True |
| balanced_labeled_100.csv | 100 | 100 | 0 | 200 | 0.267 | True | True |
| diverse_valid_100.csv | 100 | 100 | 0 | 200 | 0.358 | True | True |
| edge_cases_30.csv | 30 | 30 | 0 | 200 | 0.220 | True | True |
| out_of_distribution_20.csv | 20 | 20 | 0 | 200 | 0.258 | True | True |
| invalid_missing_columns.csv | 1 | 0 | 1 | 422 | 0.015 | False | True |
| invalid_non_numeric.csv | 1 | 0 | 1 | 200 | 0.040 | True | True |
| invalid_empty_cells.csv | 1 | 0 | 1 | 200 | 0.038 | True | True |
| invalid_extra_columns.csv | 1 | 0 | 1 | 422 | 0.038 | False | True |
| invalid_large_file.csv | 1001 | 0 | 1001 | 413 | 0.067 | False | True |
| invalid_empty_file.csv | 0 | 0 | 0 | 422 | 0.016 | False | True |
| invalid_duplicate_rows.csv | 3 | 3 | 0 | 200 | 0.238 | True | True |
| single_sample.csv | 1 | 1 | 0 | 200 | 0.213 | True | True |
| maximum_supported_batch.csv | 1000 | 1000 | 0 | 200 | 1.415 | True | True |

See CSV_TEST_RESULTS.json for class counts and exact validation messages. Every successful export row was compared with its stored measurements, label and model estimate; invalid numeric rows are excluded from exports. The maximum 1,000-row batch succeeds; 1,001 rows and uploads over 2 MB reject with HTTP 413. Formula/text values in numeric fields are rejected; safe_csv_cell also prefixes potentially executable exported text.
