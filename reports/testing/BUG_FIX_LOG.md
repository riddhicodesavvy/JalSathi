# Reproduced bugs and fixes

| Priority | Finding and root cause | Correction | Regression/evidence |
|---|---|---|---|
| P1 | A failed re-analysis left the previous success visible because mutation errors did not clear result state | Clear result on mutation start | Desktop/mobile before-fix tests failed; after-fix tests pass |
| P1 | Numeric fields and reset remained editable during an in-flight request, allowing results to reappear after reset or mismatch current inputs | Disable the form fieldset until the request settles | Desktop/mobile delayed-request tests pass; Analyze Another clears and focuses pH |
| P1 | PDF measurements used .4g, losing original submitted precision in all 20 checked reports | Retain round-trip decimal representations and paginate titled tables with repeated headers | Initial 20 report precision checks failed; final 20 pass; API regression and rendered pages inspected |
| P2 | New batch uploads retained old search/filter/sort, which could hide new results | Reset all batch view controls on successful upload | Browser filters then uploads a new one-row CSV and verifies it is visible |
| Hardening | Numeric-only exports were safe today, but future text fields could introduce formula injection | Escape executable spreadsheet-text prefixes without changing numeric cells | Seven injection-prefix tests and unchanged-number regression pass |
| Performance | CART local explanation preprocessing ran separately for every batch row | Transform the batch and calculate tree decision paths once | Single/batch classifications, probabilities and paths remain identical; timing recorded |

No trained model or production decision threshold was changed. Low AdaBoost recall is a measured model limitation, not fixed by fabricating positive predictions. The original dataset and pre-existing 61 user analyses were preserved. Baseline failures are recorded rather than hidden; final verification reruns pass.
