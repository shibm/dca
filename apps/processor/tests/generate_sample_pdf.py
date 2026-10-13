import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_contract_pdf(output_path: str, title: str, paragraphs_p1: list, paragraphs_p2: list):
    """Utility to generate a 2-page test contract PDF."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = [Paragraph(title, title_style), Spacer(1, 10)]
    for p in paragraphs_p1:
        story.append(Paragraph(p, body_style))

    story.append(PageBreak())

    for p in paragraphs_p2:
        story.append(Paragraph(p, body_style))

    doc.build(story)
    print(f"Contract generated: {output_path}")


def generate_all_sample_contracts(batch_dir: str = "apps/processor/tests/contracts_batch"):
    """Generates 3 realistic contracts for Pillar 1 M&A and SLA testing."""

    # 1. Vendor SLA Agreement (Moderate Risk, Uptime 99.95%, Consent required on Change of Control)
    create_contract_pdf(
        os.path.join(batch_dir, "01_CloudCore_Vendor_SLA.pdf"),
        "CLOUD INFRASTRUCTURE SERVICE LEVEL AGREEMENT",
        [
            "This Service Level Agreement is effective as of <b>November 1, 2026</b> between "
            "<b>Acme Global Technologies Inc.</b> (\"Customer\") and <b>CloudCore Systems Ltd.</b> (\"Provider\").",
            "Provider guarantees <b>99.95% uptime</b> across all production clusters. In the event uptime falls below 99.95%, "
            "Customer is entitled to a <b>15% service credit</b> applied to the next billing cycle.",
            "Total annual contract commitment is <b>$240,000.00</b> USD payable monthly within Net 30 days."
        ],
        [
            "<b>Section 7: Change of Control & Assignment</b><br/>"
            "Customer shall not assign this Agreement without Provider's prior written consent. "
            "Any change of control, merger, or acquisition of Customer shall require prior written consent of Provider.",
            "<b>Section 8: Auto-Renewal</b><br/>"
            "This agreement automatically renews for successive 1-year terms unless notice of non-renewal is provided at least 60 days prior to expiration."
        ]
    )

    # 2. Critical M&A Risk Agreement (Vendor Termination Right upon Acquisition + $50,000 termination fee)
    create_contract_pdf(
        os.path.join(batch_dir, "02_DataStream_Critical_Risk.pdf"),
        "ENTERPRISE DATA FEED MASTER AGREEMENT",
        [
            "This Agreement is made effective <b>December 1, 2026</b> by and between "
            "<b>Acme Global Technologies Inc.</b> (\"Client\") and <b>DataStream Analytics Corp.</b> (\"Vendor\").",
            "Total contract value is <b>$480,000.00</b> USD over a 24-month term.",
            "Vendor provides real-time market data subject to a 99.9% uptime commitment with a 10% service credit for downtime."
        ],
        [
            "<b>Section 11: Change of Control & Immediate Termination</b><br/>"
            "In the event of a change of control, corporate acquisition, or transfer of substantially all assets of Client, "
            "Vendor reserves the exclusive right to terminate this agreement upon immediate notice.",
            "<b>Section 12: Early Termination Liquidated Damages</b><br/>"
            "In the event of early termination, an early termination fee of $50,000.00 shall be immediately due and payable to Vendor."
        ]
    )

    # 3. Standard NDA / Software License (Low Risk)
    create_contract_pdf(
        os.path.join(batch_dir, "03_SecureDesk_Standard_License.pdf"),
        "SOFTWARE LICENSE AND SUPPORT AGREEMENT",
        [
            "This Software License Agreement is made effective <b>January 15, 2026</b> by and between "
            "<b>Acme Global Technologies Inc.</b> and <b>SecureDesk Software Inc.</b>",
            "Total annual subscription value is <b>$35,000.00</b> USD.",
            "Standard support hours apply with a 4-hour response time guarantee."
        ],
        [
            "<b>Section 5: Governing Law & Assignment</b><br/>"
            "Governed by the laws of the State of Delaware. Either party may assign this agreement in connection with a merger or acquisition without prior consent.",
            "Either party may terminate for convenience upon 30 days written notice without penalty."
        ]
    )


if __name__ == "__main__":
    generate_all_sample_contracts()
