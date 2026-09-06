from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_PATH = Path(
    "sample-data/quotes/synthetic-painting-proposal-canyon-view.pdf"
)


def money(value: int) -> str:
    return f"${value:,.2f}"


def build_estimate() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=LETTER,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title="Canyon View Coatings Painting Proposal",
        author="Canyon View Coatings",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ProposalTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=25,
        textColor=colors.HexColor("#17352b"),
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#66736d"),
        uppercase=True,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#263c34"),
    )
    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#5f6e68"),
    )
    right_style = ParagraphStyle("Right", parent=body_style, alignment=TA_RIGHT)

    story = []
    story.append(Paragraph("CANYON VIEW COATINGS", title_style))
    story.append(Paragraph("Interior repaint proposal | Licensed and insured", body_style))
    story.append(Spacer(1, 12))

    summary = Table(
        [
            [Paragraph("PROPOSAL", label_style), Paragraph("PROJECT", label_style), Paragraph("DATE", label_style)],
            [Paragraph("CV-1048", body_style), Paragraph("Unit 214 Turnover", body_style), Paragraph("August 28, 2026", body_style)],
            [Paragraph("PREPARED FOR", label_style), Paragraph("SERVICE ADDRESS", label_style), Paragraph("VALID THROUGH", label_style)],
            [Paragraph("Riverside Residential Partners", body_style), Paragraph("4550 Magnolia Ave, Riverside, CA", body_style), Paragraph("September 11, 2026", body_style)],
        ],
        colWidths=[1.35 * inch, 3.55 * inch, 1.7 * inch],
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f2")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#ccd8d2")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dce4e0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary, Spacer(1, 18)])

    story.append(Paragraph("WORK BREAKDOWN", title_style))
    items = [
        ("Surface preparation", "Protect floors and fixed furnishings. Patch ordinary nail holes and minor wall blemishes. Sand repaired areas.", 620),
        ("Walls", "Spot-prime repaired areas, then apply two finish coats of premium acrylic eggshell to walls in living room, kitchen, hall, two bedrooms, and bath.", 2480),
        ("Trim and doors", "Apply one finish coat to baseboards, door casings, and six interior doors using semi-gloss enamel.", 870),
        ("Ceiling allowance", "Paint the bathroom ceiling only. All other ceilings are excluded from this proposal.", 260),
        ("Project closeout", "Daily housekeeping, final cleanup, and removal of painting debris from the property are included.", 340),
    ]
    rows = [[Paragraph("ITEM", label_style), Paragraph("DESCRIPTION", label_style), Paragraph("AMOUNT", label_style)]]
    for name, description, amount in items:
        rows.append([Paragraph(name, body_style), Paragraph(description, body_style), Paragraph(money(amount), right_style)])

    work_table = Table(rows, colWidths=[1.35 * inch, 4.35 * inch, 0.9 * inch], repeatRows=1)
    work_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17352b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5ded9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([work_table, Spacer(1, 16)])

    subtotal = sum(item[2] for item in items)
    totals = Table(
        [
            [Paragraph("Subtotal", body_style), Paragraph(money(subtotal), right_style)],
            [Paragraph("Customer loyalty discount", body_style), Paragraph("-$170.00", right_style)],
            [Paragraph("PROPOSAL TOTAL", label_style), Paragraph(money(subtotal - 170), right_style)],
        ],
        colWidths=[2.2 * inch, 1.1 * inch],
        hAlign="RIGHT",
    )
    totals.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 2), (-1, 2), 1.2, colors.HexColor("#17352b")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([totals, Spacer(1, 18)])

    story.append(Paragraph("CLARIFICATIONS AND TERMS", title_style))
    terms = [
        "Pricing assumes the unit will be vacant and utilities will be active during the work.",
        "Water-damaged drywall, texture matching, cabinet finishing, and removal of hazardous coatings are not included.",
        "Colors are limited to one wall color and one trim color. Additional colors require a written change order.",
        "Labor is warranted for one year against peeling or blistering caused by workmanship. Moisture intrusion and substrate failure are excluded.",
        "A 30% scheduling deposit is due upon approval; the remaining balance is due after final walkthrough.",
    ]
    for term in terms:
        story.append(Paragraph(f"- {term}", small_style))
        story.append(Spacer(1, 3))

    def draw_footer(canvas, _document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#ccd8d2"))
        canvas.setLineWidth(0.5)
        canvas.line(0.7 * inch, 0.42 * inch, 7.8 * inch, 0.42 * inch)
        canvas.setFillColor(colors.HexColor("#5f6e68"))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(
            0.7 * inch,
            0.25 * inch,
            "Canyon View Coatings | (951) 555-0184 | proposals@canyonview.example",
        )
        canvas.drawRightString(7.8 * inch, 0.25 * inch, "Page 1 of 1")
        canvas.restoreState()

    document.build(story, onFirstPage=draw_footer)


if __name__ == "__main__":
    build_estimate()
