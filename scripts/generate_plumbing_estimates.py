"""Generate synthetic plumbing estimate PDFs for the demo."""

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


def build(filename: str, vendor: str, number: str, total: str, rows: list[tuple[str, str]], notes: list[str]) -> None:
    path = QUOTES / filename
    styles = getSampleStyleSheet()
    table_style = TableStyle([
        ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#c9ceca")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#245c45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef4f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 8),
    ])
    story = [
        Paragraph(vendor.upper(), styles["Title"]), Paragraph("ESTIMATE", styles["Heading2"]),
        Paragraph("Plumbing fixture replacement", styles["BodyText"]),
        Paragraph(f"Estimate {number} &nbsp;&nbsp; | &nbsp;&nbsp; Valid for 30 days", styles["BodyText"]),
        Spacer(1, 18), Paragraph("SCOPE AND PRICING", styles["Heading3"]),
        Table([["Description", "Amount"], *rows, ["ESTIMATE TOTAL", total]], colWidths=[5.85 * inch, 1.2 * inch], style=table_style),
        Spacer(1, 18), Paragraph("PROJECT NOTES", styles["Heading3"]),
        *[Paragraph(f"• {note}", styles["BodyText"]) for note in notes],
        Spacer(1, 18), Paragraph("Synthetic document created for software testing. No real contractor or customer data.", styles["Italic"]),
    ]
    SimpleDocTemplate(str(path), pagesize=LETTER, rightMargin=.65 * inch, leftMargin=.65 * inch, topMargin=.55 * inch, bottomMargin=.55 * inch).build(story)
    copyfile(path, PUBLIC / filename)


def main() -> None:
    build(
        "synthetic-plumbing-estimate-clearflow.pdf", "ClearFlow Plumbing", "CF-3184", "$4,980.00",
        [
            ("Install 4 customer-supplied plumbing fixtures", "$2,600.00"),
            ("Replace supply lines and shutoff valves", "$880.00"),
            ("Drain line modifications included", "$600.00"),
            ("Materials, permit and inspection fees included", "$700.00"),
            ("Pressure and leak testing; final cleanup included", "$200.00"),
        ],
        ["Two-year labor warranty included."],
    )
    build(
        "synthetic-plumbing-estimate-rapid.pdf", "Rapid Rooter Services", "RR-8810", "$3,900.00",
        [
            ("Install 3 customer-supplied plumbing fixtures", "$2,550.00"),
            ("Supply lines and materials included", "$850.00"),
            ("Leak testing and cleanup included", "$500.00"),
        ],
        [
            "Drain line modifications are not included.", "Shutoff valves, if needed, cost extra.",
            "Permit and inspection fees are not included.", "One-year labor warranty included.",
        ],
    )


if __name__ == "__main__":
    main()
