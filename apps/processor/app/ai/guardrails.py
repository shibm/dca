import re
from datetime import datetime
from typing import List, Optional, Tuple
from app.schemas.document import ParsedDocument, BoundingBox
from app.schemas.contract import StructuredContractOutput
from app.schemas.extraction import ExtractedField, ExtractionResult


class ExtractionGuardrails:
    """Validates AI extracted results, checks grounding, and computes risk scores."""

    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold

    def verify_grounding(self, quote: Optional[str], page_number: Optional[int], document: ParsedDocument) -> Tuple[bool, Optional[BoundingBox]]:
        """Verify if the quote exists in the source text and locate its bounding box."""
        if not quote or not quote.strip():
            return False, None

        cleaned_quote = re.sub(r'\s+', ' ', quote.strip()).lower()

        # Check in the designated page first
        target_pages = []
        if page_number and 1 <= page_number <= len(document.pages):
            target_pages = [document.pages[page_number - 1]]
        else:
            target_pages = document.pages

        for page in target_pages:
            cleaned_page_text = re.sub(r'\s+', ' ', page.raw_text).lower()
            if cleaned_quote in cleaned_page_text:
                matching_bbox = self._find_quote_bbox(quote, page)
                return True, matching_bbox

        cleaned_full_text = re.sub(r'\s+', ' ', document.full_text).lower()
        if cleaned_quote in cleaned_full_text:
            return True, None

        return False, None

    def _find_quote_bbox(self, quote: str, page) -> Optional[BoundingBox]:
        """Aggregate bounding boxes of words forming the quote."""
        if not page.blocks:
            return None

        first_word = quote.strip().split()[0].lower()
        for block in page.blocks:
            if block.bbox and block.text.lower().startswith(first_word):
                return block.bbox
        return None

    def validate_dates(self, effective_date: Optional[str], expiration_date: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Check logical consistency of dates."""
        if not effective_date or not expiration_date:
            return True, None

        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%d-%b-%Y"]
        eff_dt, exp_dt = None, None

        for fmt in date_formats:
            try:
                eff_dt = datetime.strptime(effective_date.strip(), fmt)
                break
            except ValueError:
                continue

        for fmt in date_formats:
            try:
                exp_dt = datetime.strptime(expiration_date.strip(), fmt)
                break
            except ValueError:
                continue

        if eff_dt and exp_dt and eff_dt > exp_dt:
            return False, f"Effective date ({effective_date}) cannot be after expiration date ({expiration_date})"

        return True, None

    def process_and_validate(self, raw_output: StructuredContractOutput, document: ParsedDocument) -> ExtractionResult:
        """Transform AI output into normalized, grounded ExtractedFields with Pillar 1 M&A/SLA flags."""
        fields: List[ExtractedField] = []
        flags: List[str] = []
        requires_review = False
        risk_points = 0

        # 1. Document Title & Summary
        fields.append(ExtractedField(
            key="title",
            label="Document Title",
            value=raw_output.title,
            data_type="string",
            confidence=0.95,
            category="general"
        ))

        fields.append(ExtractedField(
            key="document_type",
            label="Document Classification",
            value=raw_output.document_type,
            data_type="string",
            confidence=0.90,
            category="general"
        ))

        fields.append(ExtractedField(
            key="summary",
            label="Executive Summary",
            value=raw_output.summary,
            data_type="string",
            confidence=0.95,
            category="general"
        ))

        # 2. Parties
        if not raw_output.parties:
            flags.append("No contracting parties detected")
            requires_review = True
            risk_points += 15
        else:
            for idx, party in enumerate(raw_output.parties, start=1):
                is_grounded, bbox = self.verify_grounding(party.quote, party.page, document)
                conf = 0.95 if is_grounded else 0.65
                status = "VALID" if is_grounded else "NEEDS_VERIFICATION"

                fields.append(ExtractedField(
                    key=f"party_{idx}",
                    label=f"Party #{idx} ({party.role})",
                    value=party.name,
                    data_type="string",
                    confidence=conf,
                    source_page=party.page,
                    source_quote=party.quote,
                    bounding_box=bbox,
                    category="parties",
                    validation_status=status
                ))

        # 3. Dates & Deadlines
        dates = raw_output.dates
        dates_valid, date_err = self.validate_dates(dates.effective_date, dates.expiration_date)
        if not dates_valid and date_err:
            flags.append(date_err)
            requires_review = True
            risk_points += 20

        if dates.effective_date:
            is_grounded, bbox = self.verify_grounding(dates.quote, dates.page, document)
            fields.append(ExtractedField(
                key="effective_date",
                label="Effective Date",
                value=dates.effective_date,
                data_type="date",
                confidence=0.95 if is_grounded else 0.70,
                source_page=dates.page,
                source_quote=dates.quote,
                bounding_box=bbox,
                category="dates",
                validation_status="VALID" if dates_valid else "INVALID",
                validation_notes=date_err
            ))

        if dates.expiration_date:
            fields.append(ExtractedField(
                key="expiration_date",
                label="Expiration Date",
                value=dates.expiration_date,
                data_type="date",
                confidence=0.90,
                source_page=dates.page,
                category="dates",
                validation_status="VALID" if dates_valid else "INVALID"
            ))

        # 4. Financial Terms
        fin = raw_output.financials
        if fin.total_value is not None:
            is_grounded, bbox = self.verify_grounding(fin.quote, fin.page, document)
            fields.append(ExtractedField(
                key="total_contract_value",
                label="Total Contract Value",
                value=f"{fin.currency} {fin.total_value:,.2f}" if fin.currency else str(fin.total_value),
                data_type="currency",
                confidence=0.95 if is_grounded else 0.70,
                source_page=fin.page,
                source_quote=fin.quote,
                bounding_box=bbox,
                category="financial",
                validation_status="VALID" if is_grounded else "NEEDS_VERIFICATION"
            ))

        if fin.payment_terms:
            fields.append(ExtractedField(
                key="payment_terms",
                label="Payment Terms",
                value=fin.payment_terms,
                data_type="string",
                confidence=0.90,
                category="financial"
            ))

        # 5. Pillar 1: Service Level Agreement (SLA) & Penalty Metrics
        sla = raw_output.sla
        if sla.uptime_guarantee:
            is_grounded, bbox = self.verify_grounding(sla.quote, sla.page, document)
            fields.append(ExtractedField(
                key="uptime_sla",
                label="Uptime SLA Guarantee",
                value=sla.uptime_guarantee,
                data_type="string",
                confidence=0.95 if is_grounded else 0.75,
                source_page=sla.page,
                source_quote=sla.quote,
                bounding_box=bbox,
                category="sla",
                validation_status="VALID"
            ))

        if sla.service_credit_penalty:
            fields.append(ExtractedField(
                key="sla_penalty_formula",
                label="SLA Penalty / Service Credits",
                value=sla.service_credit_penalty,
                data_type="string",
                confidence=0.90,
                source_page=sla.page,
                category="sla",
                validation_status="VALID"
            ))

        # 6. Pillar 1 (M&A Diligence): Change of Control Triggers
        coc = raw_output.change_of_control
        if coc.has_change_of_control:
            is_grounded, bbox = self.verify_grounding(coc.quote, coc.page, document)
            status_desc = "Present"
            if coc.requires_vendor_consent:
                status_desc = "M&A Trigger: Requires Vendor Consent"
                flags.append("M&A Risk: Contract requires vendor consent upon acquisition")
                requires_review = True
                risk_points += 30
            elif coc.allows_termination_on_acquisition:
                status_desc = "M&A Risk: Vendor May Terminate Upon Acquisition"
                flags.append("M&A Critical: Vendor has right to terminate upon company acquisition")
                requires_review = True
                risk_points += 40

            fields.append(ExtractedField(
                key="change_of_control",
                label="Change of Control Provision",
                value=status_desc,
                data_type="string",
                confidence=0.92 if is_grounded else 0.70,
                source_page=coc.page,
                source_quote=coc.quote,
                bounding_box=bbox,
                category="legal",
                validation_status="WARNING" if (coc.requires_vendor_consent or coc.allows_termination_on_acquisition) else "VALID"
            ))

        # 7. Pillar 1: Termination & Penalties
        term = raw_output.termination
        if term.early_termination_fee is not None:
            fields.append(ExtractedField(
                key="early_termination_penalty",
                label="Early Termination Penalty",
                value=f"${term.early_termination_fee:,.2f}",
                data_type="currency",
                confidence=0.90,
                source_page=term.page,
                category="financial",
                validation_status="WARNING" if term.early_termination_fee > 0 else "VALID"
            ))
            if term.early_termination_fee > 0:
                flags.append(f"Financial Liability: Early termination fee of ${term.early_termination_fee:,.2f}")
                risk_points += 25

        if term.convenience_notice_days is not None:
            fields.append(ExtractedField(
                key="termination_notice_days",
                label="Termination Notice Window",
                value=f"{term.convenience_notice_days} days",
                data_type="number",
                confidence=0.90,
                category="dates"
            ))

        # 8. Pillar 1: Renewal Conditions & Deadlines
        ren = raw_output.renewal
        if ren.auto_renewal:
            deadline_str = f"Deadline: {ren.notice_deadline_days} days prior" if ren.notice_deadline_days else "Auto-renews"
            fields.append(ExtractedField(
                key="auto_renewal_clause",
                label="Auto-Renewal Lock-In",
                value=deadline_str,
                data_type="string",
                confidence=0.92,
                source_page=ren.page,
                category="dates",
                validation_status="WARNING" if (ren.notice_deadline_days and ren.notice_deadline_days >= 60) else "VALID"
            ))
            if ren.notice_deadline_days and ren.notice_deadline_days >= 60:
                flags.append(f"Operational Risk: Auto-renews unless notice given {ren.notice_deadline_days} days prior")
                risk_points += 15

        # 9. Governing Law & Liability Caps
        legal = raw_output.legal
        if legal.governing_law:
            quote = legal.quotes.get("governing_law")
            page = legal.pages.get("governing_law")
            is_grounded, bbox = self.verify_grounding(quote, page, document)
            fields.append(ExtractedField(
                key="governing_law",
                label="Governing Law",
                value=legal.governing_law,
                data_type="string",
                confidence=0.95 if is_grounded else 0.75,
                source_page=page,
                source_quote=quote,
                bounding_box=bbox,
                category="legal"
            ))

        if legal.limitation_of_liability:
            fields.append(ExtractedField(
                key="limitation_of_liability",
                label="Limitation of Liability",
                value=legal.limitation_of_liability,
                data_type="string",
                confidence=0.85,
                category="legal"
            ))

        # 10. Commercial & Legal Risks
        for idx, risk in enumerate(raw_output.risks, start=1):
            if risk.severity in ["HIGH", "CRITICAL"]:
                flags.append(f"Risk [{risk.severity}]: {risk.risk_title}")
                requires_review = True
                risk_points += (30 if risk.severity == "CRITICAL" else 20)

            fields.append(ExtractedField(
                key=f"risk_{idx}",
                label=f"Risk: {risk.risk_title} ({risk.severity})",
                value=risk.description,
                data_type="string",
                confidence=0.88,
                source_page=risk.page,
                category="risk",
                validation_status="WARNING" if risk.severity in ["HIGH", "CRITICAL"] else "VALID"
            ))

        # Overall Confidence and M&A Diligence Risk Index
        avg_confidence = sum(f.confidence for f in fields) / len(fields) if fields else 0.0
        if avg_confidence < self.confidence_threshold:
            requires_review = True
            flags.append(f"Overall confidence ({avg_confidence:.0%}) below review threshold ({self.confidence_threshold:.0%})")

        diligence_risk_score = min(risk_points, 100)

        raw_dict = raw_output.model_dump()
        raw_dict["diligence_risk_score"] = diligence_risk_score

        return ExtractionResult(
            document_type=raw_output.document_type,
            fields=fields,
            overall_confidence=round(avg_confidence, 4),
            flags=flags,
            requires_human_review=requires_review,
            raw_ai_response=raw_dict
        )
