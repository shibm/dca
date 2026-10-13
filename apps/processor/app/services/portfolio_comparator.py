import os
import glob
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.schemas.financials import (
    NormalizedFinancialReport,
    EntityBenchmarkItem,
    MultiEntityComparisonReport
)
from app.ai.financial_normalizer import FinancialNormalizer
from app.parsers.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class PortfolioComparator:
    """Pillar 2: Normalizes and benchmarks financial performance across 30+ portfolio companies."""

    def __init__(self, max_workers: int = 4):
        self.normalizer = FinancialNormalizer()
        self.parser = PDFParser(extract_tables=True)
        self.max_workers = max_workers

    def process_financial_pdf(self, pdf_path: str) -> EntityBenchmarkItem:
        """Parse single financial statement and extract normalized benchmark item."""
        parsed = self.parser.parse(pdf_path)
        report = self.normalizer.normalize(pdf_path, parsed.full_text)

        inc = report.income_statement
        bs = report.balance_sheet
        cf = report.cash_flow

        debt_to_equity = round(bs.total_debt / bs.total_shareholder_equity, 2) if bs.total_shareholder_equity > 0 else None

        return EntityBenchmarkItem(
            entity_name=report.entity_name,
            fiscal_period=report.fiscal_period,
            currency=report.currency,
            revenue=inc.revenue,
            yoy_revenue_growth_pct=report.yoy_revenue_growth_pct,
            gross_margin_pct=inc.gross_margin_pct,
            ebitda=inc.ebitda or 0.0,
            ebitda_margin_pct=inc.ebitda_margin_pct,
            net_income=inc.net_income,
            cash_and_equivalents=bs.cash_and_equivalents,
            total_debt=bs.total_debt,
            free_cash_flow=cf.free_cash_flow,
            debt_to_equity=debt_to_equity,
            health_status=report.health_status,
            health_flags=report.health_notes
        )

    def compare_portfolio(self, directory_or_files: Any) -> MultiEntityComparisonReport:
        """Benchmark all financial statements across portfolio companies."""
        if isinstance(directory_or_files, str) and os.path.isdir(directory_or_files):
            pdf_files = glob.glob(os.path.join(directory_or_files, "*.pdf"))
        elif isinstance(directory_or_files, list):
            pdf_files = directory_or_files
        else:
            pdf_files = []

        if not pdf_files:
            return MultiEntityComparisonReport(
                total_entities_analyzed=0,
                reporting_period="FY2025",
                total_portfolio_revenue=0.0,
                average_gross_margin_pct=0.0,
                average_ebitda_margin_pct=0.0,
                median_revenue_growth_pct=0.0,
                distressed_entities_count=0,
                watchlist_entities_count=0,
                companies=[]
            )

        items: List[EntityBenchmarkItem] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.process_financial_pdf, f): f for f in pdf_files}
            for future in as_completed(future_to_file):
                try:
                    res = future.result()
                    items.append(res)
                except Exception as e:
                    logger.error(f"Error processing financial statement {future_to_file[future]}: {e}")

        # Compute portfolio aggregations
        total_rev = sum(i.revenue for i in items)
        avg_gross_margin = round(sum(i.gross_margin_pct or 0.0 for i in items) / len(items), 2) if items else 0.0
        avg_ebitda_margin = round(sum(i.ebitda_margin_pct or 0.0 for i in items) / len(items), 2) if items else 0.0

        growth_rates = sorted([i.yoy_revenue_growth_pct for i in items if i.yoy_revenue_growth_pct is not None])
        median_growth = growth_rates[len(growth_rates) // 2] if growth_rates else 0.0

        distressed_cnt = sum(1 for i in items if i.health_status == "DISTRESSED")
        watchlist_cnt = sum(1 for i in items if i.health_status == "WATCHLIST")

        period = items[0].fiscal_period if items else "FY2025"

        return MultiEntityComparisonReport(
            total_entities_analyzed=len(items),
            reporting_period=period,
            total_portfolio_revenue=round(total_rev, 2),
            average_gross_margin_pct=avg_gross_margin,
            average_ebitda_margin_pct=avg_ebitda_margin,
            median_revenue_growth_pct=round(median_growth, 2),
            distressed_entities_count=distressed_cnt,
            watchlist_entities_count=watchlist_cnt,
            companies=sorted(items, key=lambda x: x.revenue, reverse=True)
        )

