# Reproducible QA CSV fixtures

Run `python -m tests.generate_test_csvs`. Seed 2026. Original source: root water_potability.csv; expected upstream https://www.kaggle.com/datasets/adityakadiwal/water-potability. SHA-256: 904004bde729bfe3d2e195f46343bceead09e32a0eb95bb8184e7e20e029b2bf. No production training data is changed.

Labeled records are complete, distinct held-out records; labels/indexes are stored separately in ../ground_truth_manifest.csv. Synthetic measurements have no invented labels and are not drinking-water safety examples. Duplicate rows are permitted and retained in input order; each receives its own analysis ID.

| File | Rows | Source/purpose | Expected HTTP | Invalid rows |
|---|---:|---|---:|---:|
| potable_labeled_25.csv | 25 | Original complete held-out dataset records | 200 | 0 |
| nonpotable_labeled_25.csv | 25 | Original complete held-out dataset records | 200 | 0 |
| balanced_labeled_100.csv | 100 | Original complete held-out dataset records | 200 | 0 |
| diverse_valid_100.csv | 100 | Synthetic uniform observed-range functional inputs; unlabeled | 200 | 0 |
| edge_cases_30.csv | 30 | Synthetic schema boundary inputs; unlabeled | 200 | 0 |
| out_of_distribution_20.csv | 20 | Synthetic outside training ranges; unlabeled | 200 | 0 |
| invalid_missing_columns.csv | 1 | Modified reference | 422 | 0 |
| invalid_non_numeric.csv | 1 | Formula/text injection attempt | 200 | 1 |
| invalid_empty_cells.csv | 1 | Modified reference; missing measurement | 200 | 1 |
| invalid_extra_columns.csv | 1 | Modified reference | 422 | 0 |
| invalid_large_file.csv | 1001 | Synthetic over row limit | 413 | 0 |
| invalid_empty_file.csv | 0 | Empty file | 422 | 0 |
| invalid_duplicate_rows.csv | 3 | Duplicate reference measurements; duplicates intentionally retained independently | 200 | 0 |
| single_sample.csv | 1 | Specified numerical reference; no claimed true label | 200 | 0 |
| maximum_supported_batch.csv | 1000 | 1,000 synthetic valid rows; repeated measurements retained | 200 | 0 |
