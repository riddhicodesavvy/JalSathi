"""Reference checks are independent of ML. Unknown units block mass-unit checks."""

from ml.data import FEATURES

EPA = "https://www.epa.gov/sdwa/secondary-drinking-water-standards-guidance-nuisance-chemicals"
REFERENCES = {
    "ph": dict(
        lower=6.5,
        upper=8.5,
        unit="dimensionless",
        reference="6.5–8.5",
        source=EPA,
        jurisdiction="US EPA secondary (aesthetic/corrosion) guidance; not an Indian certification",
    ),
    "Sulfate": dict(
        upper=250,
        unit="mg/L",
        reference="≤250 mg/L (units unverified)",
        source=EPA,
        jurisdiction="US EPA secondary (aesthetic) guidance",
    ),
    "Solids": dict(
        upper=500,
        unit="mg/L",
        reference="TDS ≤500 mg/L (mapping/units unverified)",
        source=EPA,
        jurisdiction="US EPA secondary (aesthetic) guidance",
    ),
}


def check_parameters(values):
    checks = []
    for c in FEATURES:
        ref = REFERENCES.get(c)
        status = "unknown"
        if c == "ph":
            status = "within" if ref["lower"] <= values[c] <= ref["upper"] else "outside"
        checks.append(
            dict(
                feature=c,
                value=values[c],
                status=status,
                unit="dimensionless" if c == "ph" else "dataset units unverified",
                reference=ref["reference"] if ref else "No verified applicable reference",
                source=ref["source"] if ref else None,
                jurisdiction=ref["jurisdiction"] if ref else None,
                reason=None
                if c == "ph"
                else "Comparison unavailable: units or applicable threshold unverified.",
            )
        )
    return checks
