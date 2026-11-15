import os
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ml.data import ROOT


def generate_report(result):
    default_directory = (
        Path(tempfile.gettempdir()) / "jalsathi-reports"
        if os.getenv("VERCEL") == "1"
        else ROOT / "runtime/reports"
    )
    directory = Path(os.getenv("JALSATHI_REPORTS", default_directory))
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{result['analysis_id']}.pdf"
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#0864a0")
    styles["BodyText"].leading = 15
    story = []

    def para(text, style="BodyText"):
        # Helvetica does not contain mathematical symbols used by the web UI.
        safe = str(text).replace("≤", "<=").replace("–", "-").replace("≥", ">=")
        story.append(Paragraph(escape(safe), styles[style]))
        gap = Spacer(1, 3 * mm)
        if style.startswith("Heading"):
            gap.keepWithNext = True
        story.append(gap)

    def table(rows, widths):
        rows = [
            [
                Paragraph(escape(str(cell).replace("–", "-").replace("≤", "<=")), styles["BodyText"])
                for cell in row
            ]
            for row in rows
        ]
        caption = None
        if (
            len(story) >= 2
            and isinstance(story[-2], Paragraph)
            and story[-2].style.name.startswith("Heading")
        ):
            caption = story[-2]
            del story[-2:]
            rows.insert(0, [caption] + [""] * (len(widths) - 1))
        header = 1 if caption else 0
        t = Table(rows, colWidths=widths, repeatRows=header + 1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, header), (-1, header), colors.HexColor("#ddf4fb")),
                    ("ROWBACKGROUNDS", (0, header + 1), (-1, -1), [colors.white, colors.HexColor("#f3faff")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("LINEBELOW", (0, header), (-1, header), 1, colors.HexColor("#9bd9e6")),
                ]
            )
        )
        if caption:
            t.setStyle(TableStyle([("SPAN", (0, 0), (-1, 0)), ("BACKGROUND", (0, 0), (-1, 0), colors.white)]))
        story.append(t)
        story.append(Spacer(1, 5 * mm))

    para("JalSathi", "Title")
    para("WATER QUALITY INTELLIGENCE | Educational analysis report", "Heading2")
    para(f"Report ID: {result['analysis_id']}")
    para(f"Analysis time (UTC): {result['created_at']} | Source: {result['source']}")
    para(result["label"], "Heading1")
    para(f"Primary model: {result['primary_model']} | Version: {result['version']}")
    para(
        f"Selected-class model estimate: {result['selected_class_probability']:.1%} (uncalibrated). "
        f"Agreement: {result['agreement_count']}/5 models."
    )
    para(result["disclaimer"])
    para("Measured parameters and reference checks", "Heading2")
    table(
        [["Parameter", "Value / units", "Reference / status"]]
        + [
            [p["feature"], f"{p['value']} / {p['unit']}", f"{p['reference']} / {p['status']}"]
            for p in result["parameters"]
        ],
        [42 * mm, 54 * mm, 78 * mm],
    )
    para("Model comparison", "Heading2")
    table(
        [["Classifier", "Prediction", "P(potable)"]]
        + [[p["name"], p["label"], f"{p['potable_probability']:.1%}"] for p in result["models"]],
        [55 * mm, 79 * mm, 40 * mm],
    )
    para("Warnings and limitations", "Heading2")
    for warning in result["warnings"]:
        para(warning)
    para("CART decision path (model explanation, not a causal claim)", "Heading2")
    para("; ".join(result["decision_path"]))
    para(
        "Dataset: Aditya Kadiwal, Water Potability, Kaggle. Sampling locations, measurement units, "
        "and label validation are not independently established. Missing training values use training-only "
        "median imputation. This model does not test for microbes, heavy metals, pesticides or radioactivity."
    )
    para(
        "Reference: US EPA secondary guidance (aesthetic/corrosion; not certification). "
        "https://www.epa.gov/sdwa/secondary-drinking-water-standards-guidance-nuisance-chemicals"
    )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#61748c"))
        canvas.drawString(18 * mm, 12 * mm, "JalSathi | Educational screening only")
        canvas.drawRightString(192 * mm, 12 * mm, f"Page {doc.page}")

    SimpleDocTemplate(
        str(path),
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=20 * mm,
        title="JalSathi Water Analysis",
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    return path
