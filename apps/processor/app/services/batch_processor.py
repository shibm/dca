import os
import glob
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.pipeline import ExtractionPipeline
from app.schemas.extraction import ExtractionResult
from app.schemas.document import ParsedDocument

logger = logging.getLogger(__name__)


class ContractDiligenceItem(BaseModel):
    file_name: str
    document_type: str
    parties: List[str]
    total_value: Optional[float] = None
    currency: Optional[str] = "USD"
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    uptime_sla: Optional[str] = None
    has_change_of_control: bool = False
    requires_consent_on_acquisition: bool = False
    vendor_termination_on_acquisition: bool = False
    auto_renewal: bool = False
    renewal_notice_deadline_days: Optional[int] = None
    early_termination_penalty: Optional[float] = None
    diligence_risk_score: int = 0
    confidence_score: float = 0.0
    flags: List[str] = Field(default_factory=list)


class MADiligenceRollupReport(BaseModel):
    """Portfolio-wide M&A Diligence Rollup for analyzing thousands of vendor contracts."""
    total_contracts: int = 0
    total_financial_exposure: float = 0.0
    change_of_control_risk_count: int = 0
    acquisition_termination_rights_count: int = 0
    upcoming_renewals_count: int = 0
    average_risk_score: float = 0.0
    high_risk_contracts_count: int = 0
    contracts: List[ContractDiligenceItem] = Field(default_factory=list)


class BatchProcessor:
    """Processes large batches of vendor contracts concurrently and compiles M&A diligence rollups."""

    def __init__(self, max_workers: int = 4):
        self.pipeline = ExtractionPipeline()
        self.max_workers = max_workers

    def process_file(self, file_path: str) -> ContractDiligenceItem:
        """Process a single contract and map to M&A diligence item."""
        parsed_doc, result = self.pipeline.process(file_path)
        raw_ai = result.raw_ai_response or {}

        field_map = {f.key: f for f in result.fields}

        # Extract parties
        parties = [f.value for k, f in field_map.items() if k.startswith("party_") and f.value]

        # Extract financials
        val_str = field_map.get("total_contract_value")
        total_val = None
        if val_str and val_str.value:
            # Parse number
            clean_num = ''.join(c for c in str(val_str.value) if c.isdigit() or c == '.')
            try:
                total_val = float(clean_num) if clean_num else None
            except ValueError:
                total_val = None

        # Change of control
        coc_clause = raw_ai.get("change_of_control", {})
        has_coc = coc_clause.get("has_change_of_control", False)
        req_consent = coc_clause.get("requires_vendor_consent", False)
        term_on_acq = coc_clause.get("allows_termination_on_acquisition", False)

        # SLA
        sla_terms = raw_ai.get("sla", {})
        uptime = sla_terms.get("uptime_guarantee")

        # Dates & Renewal
        dates = raw_ai.get("dates", {})
        renewal = raw_ai.get("renewal", {})
        term = raw_ai.get("termination", {})

        return ContractDiligenceItem(
            file_name=os.path.basename(file_path),
            document_type=result.document_type,
            parties=parties,
            total_value=total_val,
            currency="USD",
            effective_date=dates.get("effective_date"),
            expiration_date=dates.get("expiration_date"),
            uptime_sla=uptime,
            has_change_of_control=has_coc,
            requires_consent_on_acquisition=req_consent,
            vendor_termination_on_acquisition=term_on_acq,
            auto_renewal=renewal.get("auto_renewal", False),
            renewal_notice_deadline_days=renewal.get("notice_deadline_days"),
            early_termination_penalty=term.get("early_termination_fee"),
            diligence_risk_score=raw_ai.get("diligence_risk_score", 0),
            confidence_score=result.overall_confidence,
            flags=result.flags
        )

    def process_directory(self, directory_path: str) -> MADiligenceRollupReport:
        """Scan directory for PDF contracts, process in parallel, and generate diligence report."""
        pdf_paths = glob.glob(os.path.join(directory_path, "*.pdf"))
        if not pdf_paths:
            return MADiligenceRollupReport()

        items: List[ContractDiligenceItem] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.process_file, p): p for p in pdf_paths}
            for future in as_completed(future_to_file):
                try:
                    item = future.result()
                    items.append(item)
                except Exception as e:
                    logger.error(f"Failed processing {future_to_file[future]}: {e}")

        # Compile Portfolio Diligence Rollup
        total_val = sum(i.total_value or 0.0 for i in items)
        coc_count = sum(1 for i in items if i.has_change_of_control and (i.requires_consent_on_acquisition or i.vendor_termination_on_acquisition))
        acq_term_count = sum(1 for i in items if i.vendor_termination_on_acquisition)
        high_risk = sum(1 for i in items if i.diligence_risk_score >= 50)
        renewals = sum(1 for i in items if i.auto_renewal and (i.renewal_notice_deadline_days or 0) >= 30)
        avg_score = (sum(i.diligence_risk_score for i in items) / len(items)) if items else 0.0

        return MADiligenceRollupReport(
            total_contracts=len(items),
            total_financial_exposure=round(total_val, 2),
            change_of_control_risk_count=coc_count,
            acquisition_termination_rights_count=acq_term_count,
            upcoming_renewals_count=renewals,
            average_risk_score=round(avg_score, 1),
            high_risk_contracts_count=high_risk,
            contracts=sorted(items, key=lambda x: x.diligence_risk_score, reverse=True)
        )

