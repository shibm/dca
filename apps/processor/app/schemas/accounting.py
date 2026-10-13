from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AccountingStandard(str, Enum):
    ASC_606 = "ASC_606_REVENUE"
    ASC_842 = "ASC_842_LEASES"
    IFRS_15 = "IFRS_15_REVENUE"
    IFRS_16 = "IFRS_16_LEASES"


class PerformanceObligation(BaseModel):
    """Pillar 3: ASC 606 Step 2 - Distinct good or service identified in the contract."""
    id: str = Field(..., description="e.g. 'PPOB-1', 'PPOB-2'")
    name: str = Field(..., description="e.g. 'SaaS Subscription License', 'Implementation Services'")
    distinct_in_context: bool = Field(True, description="Whether separately identifiable and capable of being distinct")
    standalone_selling_price: float = Field(..., description="Estimated Standalone Selling Price (SSP)")
    allocated_transaction_price: float = Field(..., description="Allocated contract price based on relative SSP")
    timing_of_satisfaction: str = Field("OVER_TIME", description="'OVER_TIME' or 'POINT_IN_TIME'")
    recognition_period: Optional[str] = Field(None, description="e.g. 'Ratable monthly over 12 months'")
    contract_citation: Optional[str] = None
    page: Optional[int] = None


class ASC606Analysis(BaseModel):
    """Pillar 3: Full 5-Step Revenue Recognition Evaluation Model."""
    # Step 1: Identify the Contract
    step1_has_commercial_substance: bool = True
    step1_parties_committed: bool = True
    step1_collectibility_probable: bool = True
    step1_assessment: str = Field(..., description="Detailed Step 1 evaluation against ASC 606-10-25-1 criteria")

    # Step 2: Identify Performance Obligations
    step2_performance_obligations: List[PerformanceObligation] = Field(default_factory=list)
    step2_assessment: str = Field(..., description="Assessment of distinct goods/services vs bundled solutions")

    # Step 3: Determine Transaction Price
    step3_fixed_consideration: float = 0.0
    step3_variable_consideration: float = 0.0
    step3_financing_component: bool = False
    step3_total_transaction_price: float = 0.0
    step3_assessment: str = Field(..., description="Evaluation of total transaction price, refunds, discounts, penalties")

    # Step 4: Allocate Transaction Price
    step4_allocation_methodology: str = Field("Relative Standalone Selling Price (SSP)", description="Allocation approach")
    step4_assessment: str = Field(..., description="Mathematical allocation breakdown across performance obligations")

    # Step 5: Recognize Revenue
    step5_recognition_summary: str = Field(..., description="Revenue timing: Point in time delivery vs over-time ratable recognition")


class JournalEntryLine(BaseModel):
    """Single debit or credit entry in accounting schedule."""
    account_number: Optional[str] = None
    account_name: str = Field(..., description="e.g. 'Accounts Receivable', 'Deferred Revenue', 'Subscription Revenue'")
    debit: Optional[float] = None
    credit: Optional[float] = None
    description: Optional[str] = None


class JournalEntrySchedule(BaseModel):
    """Balanced accounting journal entry block."""
    schedule_id: str
    event_name: str = Field(..., description="e.g. 'Initial Invoicing on Effective Date', 'Monthly Ratable Amortization'")
    period: str = Field(..., description="e.g. '2026-10-15', 'Month 1 - Month 12'")
    lines: List[JournalEntryLine] = Field(default_factory=list)
    total_debit: float = 0.0
    total_credit: float = 0.0
    is_balanced: bool = True


class TechnicalAccountingMemo(BaseModel):
    """Pillar 3: Comprehensive Technical Accounting Memorandum & Review Package."""
    memo_id: str
    contract_title: str
    parties: List[str]
    effective_date: str
    contract_value: float
    currency: str = "USD"
    accounting_standard: AccountingStandard = AccountingStandard.ASC_606
    
    executive_summary: str
    asc606_analysis: ASC606Analysis
    suggested_journal_entries: List[JournalEntrySchedule]
    conclusion_and_disclosures: str
    
    status: str = Field("DRAFT", description="'DRAFT', 'IN_REVIEW', 'APPROVED'")
    prepared_by: str = "DCA Technical Accounting AI Engine"
    reviewed_by: Optional[str] = None
    confidence_score: float = Field(0.95, ge=0.0, le=1.0)

