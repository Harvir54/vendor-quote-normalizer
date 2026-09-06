"""Generate synthetic flooring estimate PDFs for the demo and tests."""

from pathlib import Path
from shutil import copyfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"
PUBLIC = ROOT / "frontend" / "public" / "samples"


def build_quote(filename: str, vendor: str, estimate_no: str, total: str, rows: list[tuple[str, str]], notes: list[str]) -> None:
    path = QUOTES / filename
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER, rightMargin=.65 * inch, leftMargin=.65 * inch,
        topMargin=.55 * inch, bottomMargin=.55 * inch,
        title=f"Synthetic flooring estimate - {vendor}", author="Vendor Quote Normalizer",
    )
    table_style = TableStyle([
        ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#c9ceca")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#245c45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef4f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 8),
    ])
    story = [
        Paragraph(vendor.upper(), styles["Title"]),
        Paragraph("ESTIMATE", styles["Heading2"]),
        Paragraph("Flooring installation", styles["BodyText"]),
        Paragraph(f"Estimate {estimate_no} &nbsp;&nbsp; | &nbsp;&nbsp; Residential flooring replacement", styles["BodyText"]),
        Spacer(1, 18),
        Paragraph("SCOPE AND PRICING", styles["Heading3"]),
        Table([["Description", "Amount"], *rows, ["ESTIMATE TOTAL", total]], colWidths=[5.85 * inch, 1.2 * inch], style=table_style),
        Spacer(1, 18),
        Paragraph("PROJECT NOTES", styles["Heading3"]),
        *[Paragraph(f"• {note}", styles["BodyText"]) for note in notes],
        Spacer(1, 18),
        Paragraph("Synthetic document created for software testing. No real contractor or customer data.", styles["Italic"]),
    ]
    doc.build(story)
    copyfile(path, PUBLIC / filename)


def main() -> None:
    QUOTES.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    build_quote(
        "synthetic-flooring-estimate-pacific.pdf", "Pacific Floorworks", "PF-2048", "$8,640.00",
        [
            ("Remove and dispose of existing carpet and pad", "$1,050.00"),
            ("Minor subfloor preparation and leveling included", "$690.00"),
            ("Install 1,200 sq ft luxury vinyl plank, 6.5 mm thickness, 20 mil wear layer, with attached pad", "$6,300.00"),
            ("Moisture barrier and transition strips included", "$420.00"),
            ("Final cleanup included", "$180.00"),
        ],
        ["Baseboards are excluded; existing baseboards remain in place.", "Two-year labor warranty included."],
    )
    build_quote(
        "synthetic-flooring-estimate-valley.pdf", "Valley Flooring Group", "VF-7721", "$7,150.00",
        [
            ("Install 1,100 sq ft LVP flooring with 12 mil wear layer", "$6,350.00"),
            ("Transition strips included", "$350.00"),
            ("Final cleanup included", "$450.00"),
        ],
        [
            "Existing flooring removal is not included.",
            "Subfloor repair or leveling, if needed, will be priced separately.",
            "Underlayment is not stated. Moisture barrier is not stated.",
            "Baseboard work is not stated.",
            "One-year labor warranty included.",
        ],
    )


if __name__ == "__main__":
    main()
