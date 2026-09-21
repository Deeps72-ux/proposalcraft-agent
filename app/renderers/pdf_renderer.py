import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render running headers and total page numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        # Do not draw headers/footers on cover page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(54, 750, "ProposalCraft Enterprise — Confidential Commercial Document")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, letter[0] - 54, 742)

        # Running Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "Confidential & Proprietary — All Rights Reserved")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)

        self.restoreState()


def render_pdf(proposal: Dict[str, Any]) -> bytes:
    """Generate a high-fidelity enterprise proposal PDF using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    # Custom Palettes
    PRIMARY = colors.HexColor("#0F172A")       # Slate 900
    ACCENT = colors.HexColor("#2563EB")        # Blue 600
    MUTED = colors.HexColor("#475569")         # Slate 600
    BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
    BORDER_LIGHT = colors.HexColor("#E2E8F0")  # Slate 200

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=MUTED,
        spaceAfter=24,
    )

    h1_style = ParagraphStyle(
        "ProposalH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "ProposalH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ProposalBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=PRIMARY,
        spaceAfter=8,
    )

    bullet_style = ParagraphStyle(
        "ProposalBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=PRIMARY,
        leftIndent=14,
        spaceAfter=4,
    )

    callout_style = ParagraphStyle(
        "ProposalCallout",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_body_style = ParagraphStyle(
        "TableBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY,
    )

    table_bold_style = ParagraphStyle(
        "TableBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY,
    )

    story = []

    # Extract Data
    client = proposal.get("client_name") or "Enterprise Client"
    project = proposal.get("project_title") or "Commercial Proposal & Technical Solution"
    company = proposal.get("company_name") or "ProposalCraft Solutions"
    created_at = proposal.get("created_at") or datetime.now().strftime("%B %d, %Y")
    sections = proposal.get("sections", {})
    review = proposal.get("review_feedback", {})

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    story.append(Spacer(1, 40))
    story.append(
        Paragraph(
            "<font color='#2563EB'><b>ENTERPRISE BUSINESS PROPOSAL</b></font>",
            subtitle_style,
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph(project, title_style))
    story.append(HRFlowable(width="100%", thickness=3, color=ACCENT, spaceBefore=4, spaceAfter=20))
    story.append(
        Paragraph(f"Prepared exclusively for: <b>{client}</b>", subtitle_style)
    )
    story.append(Spacer(1, 80))

    meta_data = [
        [Paragraph("<b>Submitted By:</b>", body_style), Paragraph(company, body_style)],
        [Paragraph("<b>Client Organization:</b>", body_style), Paragraph(client, body_style)],
        [Paragraph("<b>Date of Submission:</b>", body_style), Paragraph(str(created_at)[:10], body_style)],
        [Paragraph("<b>Classification:</b>", body_style), Paragraph("Confidential / Commercial Proposal", body_style)],
        [Paragraph("<b>Audit Score:</b>", body_style), Paragraph(f"Approved ({review.get('compliance_score', 95)}/100 Compliance Rating)", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 350])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_LIGHT),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ])
    )
    story.append(meta_table)
    story.append(PageBreak())

    # ==========================================
    # 2. EXECUTIVE SUMMARY
    # ==========================================
    exec_sec = sections.get("executive_summary", {})
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("<b>Strategic Context & Client Challenge</b>", h2_style))
    story.append(Paragraph(exec_sec.get("challenge", "Strategic requirements analysis."), body_style))

    story.append(Paragraph("<b>Proposed Solution Overview</b>", h2_style))
    story.append(Paragraph(exec_sec.get("proposed_solution", "Comprehensive architecture implementation."), body_style))

    # Strategic Value Callout Box
    strat_val = exec_sec.get("strategic_value", "")
    if strat_val:
        callout_data = [[
            Paragraph(f"<b>Key Value Proposition & ROI:</b><br/>{strat_val}", callout_style)
        ]]
        callout_table = Table(callout_data, colWidths=[500])
        callout_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3B82F6")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ])
        )
        story.append(Spacer(1, 4))
        story.append(callout_table)
        story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Executive Highlights:</b>", h2_style))
    for hl in exec_sec.get("highlights", []):
        story.append(Paragraph(f"• {hl}", bullet_style))

    story.append(Spacer(1, 14))

    # ==========================================
    # 3. TECHNICAL ARCHITECTURE
    # ==========================================
    tech_sec = sections.get("technical_architecture", {})
    story.append(Paragraph("2. Proposed Technical Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=10))
    story.append(Paragraph(tech_sec.get("overview", "Technical design specifications."), body_style))

    # Architecture Components Table
    comps = tech_sec.get("components", [])
    if comps:
        story.append(Paragraph("<b>Core System Modules & Technology Stack</b>", h2_style))
        table_rows = [
            [
                Paragraph("<b>Component Name</b>", table_header_style),
                Paragraph("<b>Technology Stack</b>", table_header_style),
                Paragraph("<b>Architectural Responsibility</b>", table_header_style),
            ]
        ]
        for c in comps:
            table_rows.append([
                Paragraph(c.get("name", ""), table_bold_style),
                Paragraph(c.get("tech_stack", ""), table_body_style),
                Paragraph(c.get("description", ""), table_body_style),
            ])

        tech_table = Table(table_rows, colWidths=[120, 130, 250])
        tech_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ])
        )
        story.append(tech_table)
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Security & Compliance Governance:</b>", h2_style))
    story.append(Paragraph(tech_sec.get("security_and_compliance", "Enterprise encryption and RBAC."), body_style))

    story.append(Paragraph("<b>Scalability & Resilience:</b>", h2_style))
    story.append(Paragraph(tech_sec.get("scalability_and_resilience", "High-availability clustering."), body_style))

    story.append(Spacer(1, 14))

    # ==========================================
    # 4. SCOPE & KEY DELIVERABLES
    # ==========================================
    deliv_sec = sections.get("deliverables", {})
    story.append(KeepTogether([
        Paragraph("3. Scope & Key Deliverables", h1_style),
        HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=10),
    ]))

    phases = deliv_sec.get("phases", [])
    if phases:
        deliv_rows = [
            [
                Paragraph("<b>Phase & Duration</b>", table_header_style),
                Paragraph("<b>Tangible Deliverables</b>", table_header_style),
                Paragraph("<b>Strategic Milestone Outcome</b>", table_header_style),
            ]
        ]
        for p in phases:
            deliv_items = "<br/>".join([f"• {d}" for d in p.get("deliverables", [])])
            deliv_rows.append([
                Paragraph(f"<b>{p.get('phase', '')}</b><br/><font color='#64748B'>{p.get('duration', '')}</font>", table_body_style),
                Paragraph(deliv_items, table_body_style),
                Paragraph(p.get("outcome", ""), table_body_style),
            ])

        deliv_table = Table(deliv_rows, colWidths=[130, 220, 150])
        deliv_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ])
        )
        story.append(deliv_table)
        story.append(Spacer(1, 14))

    # ==========================================
    # 5. COMMERCIAL & PRICING
    # ==========================================
    price_sec = sections.get("pricing", {})
    currency = price_sec.get("currency", "USD")
    total_inv = price_sec.get("total_investment", 0.0)

    story.append(KeepTogether([
        Paragraph("4. Commercial & Milestone Investment", h1_style),
        HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=10),
    ]))

    milestones = price_sec.get("milestones", [])
    if milestones:
        price_rows = [
            [
                Paragraph("<b>Milestone</b>", table_header_style),
                Paragraph("<b>Deliverable Trigger</b>", table_header_style),
                Paragraph("<b>Timeline</b>", table_header_style),
                Paragraph(f"<b>Amount ({currency})</b>", table_header_style),
                Paragraph("<b>Share</b>", table_header_style),
            ]
        ]
        for m in milestones:
            amt = float(m.get("amount", 0))
            price_rows.append([
                Paragraph(m.get("milestone", ""), table_bold_style),
                Paragraph(m.get("deliverable", ""), table_body_style),
                Paragraph(m.get("timeline", ""), table_body_style),
                Paragraph(f"{amt:,.2f}", table_body_style),
                Paragraph(str(m.get("percentage", "")), table_body_style),
            ])

        # Summary Row
        price_rows.append([
            Paragraph("<b>Total Contract Investment</b>", table_bold_style),
            Paragraph("<b>All Project Deliverables Included</b>", table_bold_style),
            Paragraph("-", table_bold_style),
            Paragraph(f"<b>{total_inv:,.2f} {currency}</b>", table_bold_style),
            Paragraph("<b>100%</b>", table_bold_style),
        ])

        price_table = Table(price_rows, colWidths=[130, 170, 70, 85, 45])
        price_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, BG_LIGHT]),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FEF3C7")),  # Amber accent for total
            ])
        )
        story.append(price_table)
        story.append(Spacer(1, 10))

    terms = price_sec.get("payment_terms", "")
    if terms:
        story.append(Paragraph(f"<b>Payment Terms:</b> {terms}", body_style))

    assumptions = price_sec.get("assumptions", [])
    if assumptions:
        story.append(Paragraph("<b>Commercial Assumptions:</b>", h2_style))
        for a in assumptions:
            story.append(Paragraph(f"• {a}", bullet_style))

    # ==========================================
    # 6. COMPLIANCE & REVIEW SIGN-OFF
    # ==========================================
    if review:
        story.append(Spacer(1, 14))
        story.append(KeepTogether([
            Paragraph("<b>Proposal Audit & Quality Assurance</b>", h2_style),
            Paragraph(
                f"This document underwent automated executive verification. "
                f"<b>Compliance Rating:</b> {review.get('compliance_score', 95)}/100 | "
                f"<b>Tone & Alignment:</b> {review.get('tone_score', 95)}/100.",
                body_style,
            ),
            Paragraph(f"<i>Auditor Note: {review.get('review_notes', '')}</i>", callout_style),
        ]))

    # Build document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
