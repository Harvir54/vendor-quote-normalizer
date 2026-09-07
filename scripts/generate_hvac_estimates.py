"""Generate synthetic HVAC estimate PDFs for the demo."""

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
        Paragraph("HVAC system replacement", styles["BodyText"]),
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
        "synthetic-hvac-estimate-summit.pdf", "Summit Comfort Systems", "SC-4102", "$14,800.00",
        [
            ("Install 4-ton heat pump and air handler; Manufacturer: Carrier; 18 SEER2 / 9 HSPF2", "$11,900.00"),
            ("Outdoor model 25VNA848A003; indoor model FE4ANF005", "$0.00"),
            ("Modify ducts; install refrigerant line set and electrical disconnect", "$1,650.00"),
            ("Permit, startup, airflow testing and charge verification", "$750.00"),
            ("Old equipment removal, thermostat and cleanup", "$500.00"),
        ],
        ["Manual J load calculation and AHRI matched-system certificate included.", "Install condensate drain and float switch. Two-year labor warranty included."],
    )
    build(
        "synthetic-hvac-estimate-inland.pdf", "Inland Air Solutions", "IA-7725", "$11,900.00",
        [
            ("Install 3.5-ton heat pump and air handler; 15.2 SEER2 / 7.8 HSPF2", "$10,850.00"),
            ("Reuse existing ductwork and refrigerant line set", "$0.00"),
            ("Install thermostat; permit, startup and system testing included", "$650.00"),
            ("Old equipment disposal and cleanup", "$400.00"),
        ],
        ["Manual J load calculation and AHRI certificate are not included.", "Electrical work excluded. One-year labor warranty included."],
    )


if __name__ == "__main__":
    main()
