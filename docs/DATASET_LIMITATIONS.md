# Scientific and dataset limitations

The local file matches the commonly distributed 3,276-row Water Potability schema, but matching structure does not authenticate upstream provenance, collection locations, measurement methods, sampling dates, units, label validity or population representativeness. Kaggle is the expected source, not a laboratory certification.

pH, Sulfate and Trihalomethanes contain missing values. Pipelines fit median imputation on training rows only; this can hide missingness structure and introduce uncertainty. Real sample requests require all nine finite measurements and do not silently fill blanks or zeros. IQR flags describe distributional extremes, not proven errors or guideline violations.

No microbial/pathogen, comprehensive heavy metal, pesticide, organic micropollutant or radiological screening is established by these nine columns. A label prediction cannot certify drinking-water safety. Geographic and temporal transfer, distribution shift and uncalibrated probabilities are material limitations. Out-of-range indicators compare to observed training minima/maxima and are a simple screening heuristic, not a formal multivariate out-of-distribution detector.

US EPA secondary guidance lists pH 6.5–8.5, sulfate 250 mg/L and TDS 500 mg/L. Only dimensionless pH is actively compared. Sulfate units and the Solids-to-TDS mapping/units are unverified, so these checks remain unavailable; other parameters also remain unverified. No invented WHO/BIS thresholds, mass units, borderline bands or regulatory approvals are displayed. These US secondary guidelines address aesthetic/corrosion issues and do not establish Indian compliance. A positive ML label never removes a documented pH breach warning.

References:

- https://www.kaggle.com/datasets/adityakadiwal/water-potability
- https://www.epa.gov/sdwa/secondary-drinking-water-standards-guidance-nuisance-chemicals
- https://www.who.int/publications/i/item/9789240045064
- https://www.who.int/publications/i/item/9789240121225 (2026 third addendum)
- https://www.bis.org.in/other/DrinWatIS10500.pdf (BIS IS 10500:2012)
- https://scikit-learn.org/stable/modules/model_evaluation.html

The accessible BIS standard distinguishes acceptable limits from permissible limits in the absence of an alternate source. Those categories are not interchangeable. Neither BIS mass-unit limits nor WHO chemical thresholds are automatically applied to unverified CSV units. The WHO 2026 third-addendum edition was also located during reference review; no new numeric thresholds from it are claimed by the application.
