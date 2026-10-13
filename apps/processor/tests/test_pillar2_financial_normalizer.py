import os
import pytest
from app.parsers.pdf_parser import PDFParser
from app.ai.financial_normalizer import FinancialNormalizer
from app.services.portfolio_comparator import PortfolioComparator

FINANCIALS_DIR = "apps/processor/tests/portfolio_financials"


def test_pillar2_financial_statement_normalization():
    """Verify standard extraction and normalization for a high-growth SaaS portfolio company."""
    pdf_path = os.path.join(FINANCIALS_DIR, "01_CloudVanguard_SaaS_FY2025.pdf")
    parser = PDFParser(extract_tables=True)
    parsed = parser.parse(pdf_path)

    normalizer = FinancialNormalizer()
    report = normalizer.normalize(pdf_path, parsed.full_text)

    assert "CloudVanguard Technologies" in report.entity_name
    assert report.fiscal_period == "FY2025"
    assert report.currency == "USD"

    # Verify P&L
    inc = report.income_statement
    assert inc.revenue == 42_500_000.0
    assert inc.cogs == 9_200_000.0
    assert inc.gross_profit == 33_300_000.0
    assert inc.gross_margin_pct == 78.35
    assert inc.ebitda == 11_900_000.0
    assert inc.ebitda_margin_pct == 28.0
    assert inc.net_income == 8_250_000.0

    # Verify Balance Sheet & Cash Flow
    bs = report.balance_sheet
    assert bs.cash_and_equivalents == 18_400_000.0
    assert bs.total_debt == 6_000_000.0
    assert report.cash_flow.free_cash_flow == 11_400_000.0

    # Verify Financial Health
    assert report.health_status == "EXCELLENT"
    assert report.yoy_revenue_growth_pct == 28.4


def test_pillar2_distressed_financial_evaluation():
    """Verify identification of negative burn and distressed health status."""
    pdf_path = os.path.join(FINANCIALS_DIR, "04_NexTherapeutics_Bio_FY2025.pdf")
    parser = PDFParser(extract_tables=True)
    parsed = parser.parse(pdf_path)

    normalizer = FinancialNormalizer()
    report = normalizer.normalize(pdf_path, parsed.full_text)

    assert "NexTherapeutics Bio" in report.entity_name
    assert report.income_statement.ebitda == -8_500_000.0
    assert report.cash_flow.free_cash_flow == -8_500_000.0
    assert report.health_status == "DISTRESSED"
    assert any("burn" in note.lower() for note in report.health_notes)


def test_pillar2_multi_entity_portfolio_comparator():
    """Verify benchmarking across multiple portfolio entities."""
    comparator = PortfolioComparator(max_workers=2)
    report = comparator.compare_portfolio(FINANCIALS_DIR)

    assert report.total_entities_analyzed == 4
    assert report.total_portfolio_revenue > 180_000_000.0
    assert report.distressed_entities_count == 1
    assert len(report.companies) == 4

    # Verify sorted by revenue descending
    revenues = [c.revenue for c in report.companies]
    assert revenues == sorted(revenues, reverse=True)

