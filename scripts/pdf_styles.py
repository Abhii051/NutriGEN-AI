"""
PDF Styling and Flowable Helper Module for NutriGEN-AI Master Notes
Provides a clean, academic, publication-grade layout with two-pass page numbering,
custom typography, callout panels, monospace code blocks, and structured Q&A boxes.
"""

import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Palette
PRIMARY = colors.HexColor("#1E3A8A")        # Deep Corporate Navy
SECONDARY = colors.HexColor("#0D9488")      # Clinical Teal
ACCENT = colors.HexColor("#B45309")         # Deep Amber
DARK_TEXT = colors.HexColor("#0F172A")      # Slate 900
BODY_TEXT = colors.HexColor("#1E293B")      # Slate 800
LIGHT_BG = colors.HexColor("#F8FAFC")       # Slate 50
BORDER_COLOR = colors.HexColor("#CBD5E1")   # Slate 300
CODE_BG = colors.HexColor("#F1F5F9")        # Monospace Box BG
CALLOUT_INFO_BG = colors.HexColor("#EFF6FF")
CALLOUT_INFO_BORDER = colors.HexColor("#3B82F6")
CALLOUT_SUCCESS_BG = colors.HexColor("#ECFDF5")
CALLOUT_SUCCESS_BORDER = colors.HexColor("#10B981")
CALLOUT_WARN_BG = colors.HexColor("#FFFBEB")
CALLOUT_WARN_BORDER = colors.HexColor("#F59E0B")


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that computes total pages dynamically
    and draws running headers and footers on every page except the cover.
    """
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

    def draw_page_decorations(self, total_pages):
        if self._pageNumber > 1:
            self.saveState()
            
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY)
            self.drawString(54, letter[1] - 36, "NutriGEN-AI: Comprehensive Engineering Master Notes & Viva Guide")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(letter[0] - 54, letter[1] - 36, "Commit: 9df7ad1 | Production Architecture")
            
            # Header line
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.75)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
            # Running Footer line
            self.line(54, 46, letter[0] - 54, 46)
            
            # Running Footer Text
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 32, "Confidential & Academic Master Reference · Final Year Engineering Defense")
            self.drawRightString(letter[0] - 54, 32, f"Page {self._pageNumber} of {total_pages}")
            
            self.restoreState()


def get_styles():
    """Builds and returns our customized typographic stylesheet."""
    base = getSampleStyleSheet()
    styles = {}

    styles["CoverTitle"] = ParagraphStyle(
        "CoverTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=12
    )

    styles["CoverSubtitle"] = ParagraphStyle(
        "CoverSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=SECONDARY,
        alignment=TA_LEFT,
        spaceAfter=20
    )

    styles["CoverMeta"] = ParagraphStyle(
        "CoverMeta",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    styles["ChapterHeading"] = ParagraphStyle(
        "ChapterHeading",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    styles["SectionHeading"] = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    styles["SubSectionHeading"] = ParagraphStyle(
        "SubSectionHeading",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=DARK_TEXT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=BODY_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    styles["BodyBold"] = ParagraphStyle(
        "BodyBold",
        parent=styles["Body"],
        fontName="Helvetica-Bold"
    )

    styles["BulletItem"] = ParagraphStyle(
        "BulletItem",
        parent=styles["Body"],
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    styles["CodeText"] = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    styles["CalloutHeader"] = ParagraphStyle(
        "CalloutHeader",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=PRIMARY,
        spaceAfter=3
    )

    styles["CalloutBody"] = ParagraphStyle(
        "CalloutBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=DARK_TEXT
    )

    styles["QAQuestion"] = ParagraphStyle(
        "QAQuestion",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    styles["QAAnswer"] = ParagraphStyle(
        "QAAnswer",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=BODY_TEXT,
        leftIndent=10,
        spaceAfter=6
    )

    styles["TableHeader"] = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    styles["TableCell"] = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=DARK_TEXT
    )

    styles["TableCellBold"] = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=DARK_TEXT
    )

    return styles


_STYLES = get_styles()


def sanitize_xml(text):
    """
    Safely escapes arbitrary text for ReportLab XML rendering while
    preserving intentional styling tags: <b>, <i>, <code>, <font>, <small>.
    """
    if text is None:
        return ""
    text = str(text)
    
    # Temporarily protect allowed tags
    placeholders = []
    allowed_pattern = r"(</?(?:b|i|u|font|code|small)(?:\s+[^>]+)?>)"
    
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__SAFE_TAG_{idx}__"
    
    protected = re.sub(allowed_pattern, repl, text, flags=re.IGNORECASE)
    
    # Escape bare XML entities
    protected = protected.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Restore protected tags
    for i, tag in enumerate(placeholders):
        safe_tag = tag.replace("<code>", "<font face='Courier' color='#1E293B'>").replace("</code>", "</font>")
        protected = protected.replace(f"__SAFE_TAG_{i}__", safe_tag)
        
    return protected


def P(text, style_name="Body"):
    """Convenience helper to create a Paragraph with XML escaping."""
    return Paragraph(sanitize_xml(text), _STYLES[style_name])


def CodeBlock(code_text):
    """Creates a beautifully styled monospace code block flowable."""
    lines = code_text.strip().split("\n")
    p_lines = [sanitize_xml(line).replace(" ", "&nbsp;") for line in lines]
    content = "<br/>".join(p_lines)
    p = Paragraph(f"<font face='Courier' size=7.5 color='#0F172A'>{content}</font>", _STYLES["CodeText"])
    
    t = Table([[p]], colWidths=[letter[0] - 108])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def Callout(title, text, kind="info"):
    """Creates a visually distinct callout box for notes, warnings, or highlights."""
    if kind == "success":
        bg, border = CALLOUT_SUCCESS_BG, CALLOUT_SUCCESS_BORDER
        badge = "✓ VERIFIED CLINICAL AUDIT"
    elif kind == "warn":
        bg, border = CALLOUT_WARN_BG, CALLOUT_WARN_BORDER
        badge = "⚠ IMPORTANT VIVA NOTE"
    else:
        bg, border = CALLOUT_INFO_BG, CALLOUT_INFO_BORDER
        badge = "✦ KEY ARCHITECTURAL PRINCIPLE"

    header_html = f"<b><font color='{border.hexval()}'>{badge}:</font> {sanitize_xml(title)}</b>"
    p_head = Paragraph(header_html, _STYLES["CalloutHeader"])
    p_body = Paragraph(sanitize_xml(text), _STYLES["CalloutBody"])

    t = Table([[p_head], [p_body]], colWidths=[letter[0] - 108])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.75, border),
        ('LINELEFT', (0, 0), (0, -1), 3.0, border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def QA(q_num, category, question, answer):
    """Creates an examiner Q&A entry with category pill and highlighted question."""
    q_html = f"<b>Q{q_num} [{category}]:</b> {sanitize_xml(question)}"
    p_q = Paragraph(q_html, _STYLES["QAQuestion"])
    a_html = f"<b>Examiner Answer:</b> {sanitize_xml(answer)}"
    p_a = Paragraph(a_html, _STYLES["QAAnswer"])
    return KeepTogether([p_q, p_a])


def StyledTable(header_row, data_rows, col_widths=None):
    """Creates a clean, styled table with alternating row colors."""
    total_w = letter[0] - 108
    if not col_widths:
        ncols = len(header_row)
        col_widths = [total_w / ncols] * ncols

    head_p = [Paragraph(f"<b>{sanitize_xml(h)}</b>", _STYLES["TableHeader"]) for h in header_row]
    body_p = []
    for row in data_rows:
        row_cells = []
        for cell in row:
            if str(cell).startswith("<b>"):
                row_cells.append(Paragraph(sanitize_xml(cell), _STYLES["TableCellBold"]))
            else:
                row_cells.append(Paragraph(sanitize_xml(str(cell)), _STYLES["TableCell"]))
        body_p.append(row_cells)

    table_data = [head_p] + body_p
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
    ]))
    return t
