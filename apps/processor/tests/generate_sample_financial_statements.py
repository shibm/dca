import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_financial_pdf(
    output_path: str,
    company_name: str,
    period: str,
    income_rows: list,
    balance_rows: list,
    growth_note: str = ""
):
    """Generates a realistic financial statement PDF with income statement and balance sheet tables."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    note_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )

    story = [
        Paragraph(f"{company_name} – Financial Statements", title_style),
        Paragraph(f"Reporting Period: {period} (Amounts in USD)", subtitle_style)
    ]

    if growth_note:
        story.append(Paragraph(growth_note, note_style))
        story.append(Spacer(1, 5))

    # Income Statement Table
    story.append(Paragraph("Consolidated Statement of Operations (P&L)", h2_style))
    t1 = Table(income_rows, colWidths=[320, 180])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    # Balance Sheet Table
    story.append(Paragraph("Consolidated Balance Sheet", h2_style))
    t2 = Table(balance_rows, colWidths=[320, 180])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t2)

    doc.build(story)
    print(f"Financial statement created: {output_path}")


def generate_all_sample_financial_statements(out_dir: str = "apps/processor/tests/portfolio_financials"):
    """Generates 4 diverse portfolio company financial statements for Pillar 2 benchmarking."""

    # 1. High Growth Tech SaaS (Excellent health: High margin, rapid YoY growth)
    create_financial_pdf(
        os.path.join(out_dir, "01_CloudVanguard_SaaS_FY2025.pdf"),
        "CloudVanguard Technologies Inc.",
        "FY2025",
        [
            ["Line Item", "Amount (USD)"],
            ["Total Revenue", "$42,500,000"],
            ["Cost of Revenue", "$9,200,000"],
            ["Gross Profit", "$33,300,000"],
            ["Total Operating Expenses", "$21,400,000"],
            ["EBITDA", "$11,900,000"],
            ["Operating Income", "$10,100,000"],
            ["Net Income", "$8,250,000"],
        ],
        [
            ["Balance Sheet Item", "Amount (USD)"],
            ["Cash and cash equivalents", "$18,400,000"],
            ["Total Assets", "$54,000,000"],
            ["Total Debt", "$6,000,000"],
            ["Total Liabilities", "$12,500,000"],
            ["Stockholders' Equity", "$41,500,000"],
            ["Cash Flow from Operating Activities", "$12,800,000"],
            ["Capital Expenditures", "$1,400,000"],
            ["Free Cash Flow", "$11,400,000"],
        ],
        "Revenue grew by 28.4% YoY driven by enterprise subscription expansion."
    )

    # 2. Mature Manufacturing / Logistics (Solid health: Moderate margin, stable cash)
    create_financial_pdf(
        os.path.join(out_dir, "02_ApexLogistics_Global_FY2025.pdf"),
        "Apex Logistics Global Corp.",
        "FY2025",
        [
            ["Line Item", "Amount (USD)"],
            ["Turnover", "$88,000,000"],
            ["Cost of Sales", "$62,000,000"],
            ["Gross Margin", "$26,000,000"],
            ["Operating Costs", "$16,500,000"],
            ["Operating Profit before Depreciation (EBITDA)", "$9,500,000"],
            ["Operating Profit", "$6,800,000"],
            ["Profit for the year", "$4,900,000"],
        ],
        [
            ["Balance Sheet Item", "Amount (USD)"],
            ["Cash at bank", "$12,000,000"],
            ["Total Assets", "$92,000,000"],
            ["Total Borrowings", "$22,000,000"],
            ["Total Liabilities", "$38,000,000"],
            ["Total Equity", "$54,000,000"],
            ["Operating Cash Flow", "$8,900,000"],
            ["Purchase of property, plant (CapEx)", "$3,500,000"],
            ["Free Cash Flow", "$5,400,000"],
        ],
        "Net sales increased by 7.5% year-on-year."
    )

    # 3. Retail / Direct-to-Consumer (Watchlist: Low margin, high debt, low FCF)
    create_financial_pdf(
        os.path.join(out_dir, "03_OmniRetail_Holdings_FY2025.pdf"),
        "OmniRetail Brands Holdings LLC",
        "FY2025",
        [
            ["Line Item", "Amount (USD)"],
            ["Total Billings", "$56,000,000"],
            ["Cost of Goods Sold", "$41,000,000"],
            ["Gross Profit", "$15,000,000"],
            ["Total OPEX", "$13,800,000"],
            ["Adjusted EBITDA", "$1,200,000"],
            ["EBIT", "$350,000"],
            ["Net Profit", "$180,000"],
        ],
        [
            ["Balance Sheet Item", "Amount (USD)"],
            ["Cash and cash equivalents", "$3,100,000"],
            ["Total Assets", "$68,000,000"],
            ["Total Loans and Borrowings", "$29,000,000"],
            ["Total Liabilities", "$48,000,000"],
            ["Shareholders' Equity", "$20,000,000"],
            ["Cash Flow from Operating Activities", "$1,400,000"],
            ["Capital Expenditures", "$1,200,000"],
            ["Free Cash Flow", "$200,000"],
        ],
        "Sales grew by 3.2% amidst margin compression."
    )

    # 4. Biotechnology / Early Stage (Distressed: High cash burn, negative EBITDA)
    create_financial_pdf(
        os.path.join(out_dir, "04_NexTherapeutics_Bio_FY2025.pdf"),
        "NexTherapeutics Bio Corp.",
        "FY2025",
        [
            ["Line Item", "Amount (USD)"],
            ["Operating Revenues", "$6,500,000"],
            ["Direct Operating Costs", "$3,800,000"],
            ["Gross Profit", "$2,700,000"],
            ["Total Operating Expenses", "$11,200,000"],
            ["EBITDA", "($8,500,000)"],
            ["Operating Loss", "($9,100,000)"],
            ["Net Loss", "($9,800,000)"],
        ],
        [
            ["Balance Sheet Item", "Amount (USD)"],
            ["Cash and cash equivalents", "$4,200,000"],
            ["Total Assets", "$18,000,000"],
            ["Total Debt", "$15,000,000"],
            ["Total Liabilities", "$19,500,000"],
            ["Total Equity", "($1,500,000)"],
            ["Operating Cash Flow", "($7,900,000)"],
            ["Capital Expenditures", "$600,000"],
            ["Free Cash Flow", "($8,500,000)"],
        ],
        "Operating revenues decreased 12.0% during clinical trial ramp."
    )


if __name__ == "__main__":
    generate_all_sample_financial_statements()

