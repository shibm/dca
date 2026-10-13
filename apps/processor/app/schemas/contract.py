from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class Party(BaseModel):
    name: str = Field(..., description="Full legal name of the entity or individual")
    role: str = Field(..., description="Role in agreement, e.g. 'Disclosing Party', 'Client', 'Vendor'")
    entity_type: Optional[str] = Field(None, description="Corporation, LLC, Individual, etc.")
    jurisdiction: Optional[str] = Field(None, description="State or Country of incorporation")
    quote: Optional[str] = Field(None, description="Exact verbatim text mentioning this party")
    page: Optional[int] = Field(None, description="Page number where party is identified")


class FinancialTerms(BaseModel):
    total_value: Optional[float] = Field(None, description="Numerical contract or agreement value")
    currency: Optional[str] = Field("USD", description="3-letter currency code, e.g. USD, EUR")
    payment_terms: Optional[str] = Field(None, description="e.g. 'Net 30 days upon invoice'")
    quote: Optional[str] = Field(None, description="Exact verbatim text mentioning financial terms")
    page: Optional[int] = Field(None, description="Page number where financial terms appear")


class ContractDates(BaseModel):
    effective_date: Optional[str] = Field(None, description="YYYY-MM-DD or text representation")
    expiration_date: Optional[str] = Field(None, description="YYYY-MM-DD or text representation")
    term_length: Optional[str] = Field(None, description="Duration, e.g. '12 months', '3 years'")
    auto_renewal: Optional[bool] = Field(False, description="Whether contract auto-renews")
    renewal_notice_days: Optional[int] = Field(None, description="Days notice required prior to renewal")
    quote: Optional[str] = Field(None, description="Exact verbatim text defining dates")
    page: Optional[int] = Field(None, description="Page number where dates appear")


class SLATerms(BaseModel):
    """Pillar 1: Service Level Agreement terms, metrics, and penalty formulas."""
    uptime_guarantee: Optional[str] = Field(None, description="Uptime commitment, e.g. '99.9%' or '99.95%'")
    response_time_hours: Optional[float] = Field(None, description="Maximum support response time in hours")
    service_credit_penalty: Optional[str] = Field(None, description="Penalty formula / service credits for breach")
    penalty_cap: Optional[str] = Field(None, description="Maximum cap on SLA penalties or service credits")
    quote: Optional[str] = Field(None, description="Verbatim text defining SLA or penalty commitment")
    page: Optional[int] = Field(None, description="Page number where SLA terms appear")


class ChangeOfControlClause(BaseModel):
    """Pillar 1 (M&A Critical): Change of control triggers and acquisition rights."""
    has_change_of_control: bool = Field(False, description="Whether contract has a change of control clause")
    requires_vendor_consent: bool = Field(False, description="Does an acquisition require prior vendor consent?")
    allows_termination_on_acquisition: bool = Field(False, description="Can vendor terminate upon company acquisition?")
    quote: Optional[str] = Field(None, description="Verbatim text defining change of control provisions")
    page: Optional[int] = Field(None, description="Page number where clause appears")


class TerminationAndPenalties(BaseModel):
    """Pillar 1: Termination rights, convenience notice, and early termination fees."""
    termination_for_convenience: Optional[bool] = Field(None, description="Can either party terminate without cause?")
    convenience_notice_days: Optional[int] = Field(None, description="Notice period in days for convenience termination")
    early_termination_fee: Optional[float] = Field(None, description="Financial penalty or early termination fee")
    penalty_description: Optional[str] = Field(None, description="Description of liquidated damages or termination penalties")
    quote: Optional[str] = Field(None, description="Verbatim text defining termination terms")
    page: Optional[int] = Field(None, description="Page number where clause appears")


class RenewalConditions(BaseModel):
    """Pillar 1: Auto-renewal conditions and price escalation clauses."""
    auto_renewal: bool = Field(False, description="Whether contract renews automatically")
    renewal_term: Optional[str] = Field(None, description="Length of renewal term, e.g. '1 year'")
    notice_deadline_days: Optional[int] = Field(None, description="Notice window deadline before renewal lock-in")
    price_escalation_cap: Optional[str] = Field(None, description="Cap on price increases upon renewal, e.g. '5% annual'")
    quote: Optional[str] = Field(None, description="Verbatim text defining renewal terms")
    page: Optional[int] = Field(None, description="Page number where clause appears")


class LegalClauses(BaseModel):
    governing_law: Optional[str] = Field(None, description="State/Country governing the agreement")
    jurisdiction_venue: Optional[str] = Field(None, description="Court or arbitration venue")
    indemnification_cap: Optional[str] = Field(None, description="Indemnification liability limit/cap")
    limitation_of_liability: Optional[str] = Field(None, description="Overall liability limitation summary")
    confidentiality_period: Optional[str] = Field(None, description="Duration of confidentiality obligations")
    quotes: Dict[str, str] = Field(default_factory=dict, description="Verbatim quotes per clause")
    pages: Dict[str, int] = Field(default_factory=dict, description="Page numbers per clause")


class ContractRisk(BaseModel):
    risk_title: str = Field(..., description="Short title of the identified risk or unusual clause")
    severity: str = Field(..., description="'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'")
    description: str = Field(..., description="Explanation of why this poses a commercial or legal risk")
    clause_reference: Optional[str] = Field(None, description="Associated section or clause number")
    page: Optional[int] = Field(None, description="Page number where the risk was identified")


class StructuredContractOutput(BaseModel):
    """Pydantic model enforced on AI completion for Pillar 1 M&A and Vendor SLA contracts."""
    title: str = Field(..., description="Formal title of the document or agreement")
    document_type: str = Field(..., description="contract, nda, msa, sla, lease, invoice, or other")
    summary: str = Field(..., description="Concise 2-3 sentence executive summary of the agreement")
    parties: List[Party] = Field(default_factory=list)
    dates: ContractDates = Field(default_factory=ContractDates)
    financials: FinancialTerms = Field(default_factory=FinancialTerms)
    sla: SLATerms = Field(default_factory=SLATerms)
    change_of_control: ChangeOfControlClause = Field(default_factory=ChangeOfControlClause)
    termination: TerminationAndPenalties = Field(default_factory=TerminationAndPenalties)
    renewal: RenewalConditions = Field(default_factory=RenewalConditions)
    legal: LegalClauses = Field(default_factory=LegalClauses)
    risks: List[ContractRisk] = Field(default_factory=list)
    confidence_self_assessment: float = Field(0.9, ge=0.0, le=1.0, description="Model self-assessed confidence")
