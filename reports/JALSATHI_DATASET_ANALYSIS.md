# JalSathi dataset verification

Original CSV preserved at `water_potability.csv`. SHA-256: `904004bde729bfe3d2e195f46343bceead09e32a0eb95bb8184e7e20e029b2bf`.

Verified 3276 rows, 9 inputs, binary Potability target. Labels: {'0': 1998, '1': 1278}. Duplicates: 0.

Prior analytical work remains in `reports/eda/`; no previous master analysis markdown was present.

| Feature | Missing | IQR outlier flags | Negative values |
|---|---:|---:|---:|
| ph | 491 | 46 | 0 |
| Hardness | 0 | 83 | 0 |
| Solids | 0 | 47 | 0 |
| Chloramines | 0 | 61 | 0 |
| Sulfate | 781 | 41 | 0 |
| Conductivity | 0 | 11 | 0 |
| Organic_carbon | 0 | 25 | 0 |
| Trihalomethanes | 162 | 33 | 0 |
| Turbidity | 0 | 19 | 0 |

No outlier rows removed. Statistical outliers are not regulatory violations. Units, sampling locations, laboratory method and label validity are not independently authenticated. Expected upstream source: https://www.kaggle.com/datasets/adityakadiwal/water-potability
