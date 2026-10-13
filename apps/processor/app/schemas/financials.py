from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IncomeStatement(BaseModel):
    """Normalized Profit & Loss (P&L) statement."""
    revenue: float = Field(..., description="Total Gross/Net Revenue")
    cogs: Optional[float] = Field(None, description="Cost of Goods Sold / Cost of Revenue")
    gross_profit: Optional[float] = Field(None, description="Revenue minus COGS")
    operating_expenses: Optional[float] = Field(None, description="Total OPEX (R&D, SG&A, etc.)")
    ebitda: Optional[float] = Field(None, description="Earnings Before Interest, Taxes, Depreciation, & Amortization")
    operating_income: Optional[float] = Field(None, description="Operating Income (EBIT)")
    net_income: float = Field(..., description="Bottom-line Net Profit / Loss")
    
    # Computed Margins (as percentages, e.g. 68.5)
    gross_margin_pct: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None


class BalanceSheet(BaseModel):
    """Normalized Assets, Liabilities & Equity statement."""
    cash_and_equivalents: float = Field(..., description="Liquid cash and short-term deposits")
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    total_current_assets: Optional[float] = None
    total_assets: float = Field(..., description="Total Assets on balance sheet")
    
    accounts_payable: Optional[float] = None
    short_term_debt: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    total_debt: float = Field(default=0.0, description="Short-term plus Long-term Debt")
    total_liabilities: float = Field(..., description="Total Liabilities")
    
    total_shareholder_equity: float = Field(..., description="Net Worth / Shareholder Equity")


class CashFlowStatement(BaseModel):
    """Normalized Cash Flow metrics."""
    operating_cash_flow: float = Field(..., description="Cash generated from operating activities")
    capital_expenditures: Optional[float] = Field(None, description="CapEx")
    free_cash_flow: float = Field(..., description="Operating Cash Flow minus CapEx")
    financing_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None


class NormalizedFinancialReport(BaseModel):
    """Standardized financial performance model for a single portfolio entity."""
    entity_name: str = Field(..., description="Name of portfolio company or reporting entity")
    fiscal_period: str = Field(..., description="e.g. 'FY2025', 'FY2024', 'Q3-2026'")
    currency: str = Field("USD", description="3-letter reporting currency code")
    reporting_standard: str = Field("US-GAAP", description="US-GAAP, IFRS, or Local GAAP")
    
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow: CashFlowStatement
    
    # Growth metrics
    yoy_revenue_growth_pct: Optional[float] = Field(None, description="Year-on-year revenue growth %")
    yoy_ebitda_growth_pct: Optional[float] = Field(None, description="Year-on-year EBITDA growth %")
    
    # Health Assessment
    health_status: str = Field("SOLID", description="'EXCELLENT', 'SOLID', 'WATCHLIST', 'DISTRESSED'")
    health_notes: List[str] = Field(default_factory=list)
    confidence_score: float = Field(0.95, ge=0.0, le=1.0)


class EntityBenchmarkItem(BaseModel):
    """Flattened summary representation for multi-entity comparative matrix."""
    entity_name: str
    fiscal_period: str
    currency: str
    revenue: float
    yoy_revenue_growth_pct: Optional[float]
    gross_margin_pct: Optional[float]
    ebitda: float
    ebitda_margin_pct: Optional[float]
    net_income: float
    cash_and_equivalents: float
    total_debt: float
    free_cash_flow: float
    debt_to_equity: Optional[float]
    health_status: str
    health_flags: List[str] = Field(default_factory=list)


class MultiEntityComparisonReport(BaseModel):
    """Pillar 2: Complete 30-Company Comparative Benchmarking Matrix."""
    total_entities_analyzed: int
    reporting_period: str
    total_portfolio_revenue: float
    average_gross_margin_pct: float
    average_ebitda_margin_pct: float
    median_revenue_growth_pct: float
    distressed_entities_count: int
    watchlist_entities_count: int
    companies: List[EntityBenchmarkItem] = Field(default_factory=list)

