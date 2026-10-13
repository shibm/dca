import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional
import httpx

from app.schemas.document import ParsedDocument
from app.schemas.contract import (
    StructuredContractOutput,
    Party,
    ContractDates,
    FinancialTerms,
    SLATerms,
    ChangeOfControlClause,
    TerminationAndPenalties,
    RenewalConditions,
    LegalClauses,
    ContractRisk
)
from app.ai.prompts import CONTRACT_EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract interface for LLM extraction providers."""

    @abstractmethod
    def extract(self, document: ParsedDocument) -> StructuredContractOutput:
        """Process parsed document text and return structured contract output."""
        pass


class MockLLMClient(BaseLLMClient):
    """Deterministic local AI client using regex/heuristics for offline development & tests."""

    def extract(self, document: ParsedDocument) -> StructuredContractOutput:
        text = document.full_text

        # Heuristic title & type
        doc_type = "contract"
        title = "Commercial Agreement"
        if re.search(r"master service[s]? agreement", text, re.IGNORECASE):
            doc_type = "msa"
            title = "Master Services Agreement"
        elif re.search(r"statement of work|sow", text, re.IGNORECASE):
            doc_type = "sow"
            title = "Statement of Work"
        elif re.search(r"non-disclosure agreement|mutual nda", text, re.IGNORECASE):
            doc_type = "nda"
            title = "Non-Disclosure Agreement"

        # Heuristic Parties
        parties = []
        party_matches = re.findall(r'(?:by and between|between)\s+([A-Z][A-Za-z0-9\s,\.]+(?:Inc\.|LLC|Corp\.|Ltd\.|Corporation)?)\s+(?:\(?(?:\"|\')?([A-Za-z\s]+)(?:\"|\')?\)?|\band\b)', text)
        if party_matches:
            for match in party_matches[:2]:
                p_name = match[0].strip(" ,.")
                p_role = match[1].strip() if match[1] else "Party"
                parties.append(Party(
                    name=p_name,
                    role=p_role if p_role else "Contracting Party",
                    quote=p_name,
                    page=1
                ))
        
        if not parties:
            # Fallback party discovery
            between_match = re.search(r'between\s+([A-Z][\w\s\.,]+?)\s+and\s+([A-Z][\w\s\.,]+?)(?:\.|\n|,)', text)
            if between_match:
                p1 = between_match.group(1).strip()
                p2 = between_match.group(2).strip()
                parties.append(Party(name=p1, role="Disclosing Party / Client", quote=between_match.group(0), page=1))
                parties.append(Party(name=p2, role="Receiving Party / Vendor", quote=between_match.group(0), page=1))
            else:
                parties.append(Party(name="Acme Corporation", role="Customer", quote=None, page=1))
                parties.append(Party(name="Global Tech Solutions LLC", role="Service Provider", quote=None, page=1))

        # Heuristic Dates
        effective_date = None
        date_quote = None
        eff_match = re.search(r'effective\s+(?:as of|date:?)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
        if eff_match:
            effective_date = eff_match.group(1)
            date_quote = eff_match.group(0)
        else:
            effective_date = "2026-01-01"

        exp_match = re.search(r'(?:terminat\w+|expir\w+|end)\s+(?:on|date:?)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
        expiration_date = exp_match.group(1) if exp_match else None

        # Heuristic Financials
        total_value = None
        val_quote = None
        fin_match = re.search(r'\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)', text)
        if fin_match:
            val_str = fin_match.group(1).replace(",", "")
            total_value = float(val_str)
            val_quote = fin_match.group(0)

        # Heuristic Governing Law
        gov_match = re.search(r'governed by\s+(?:the laws of\s+)?(?:the\s+)?(?:State of\s+)?([A-Za-z\s]+?)(?:\.|,|\sand)', text, re.IGNORECASE)
        governing_law = gov_match.group(1).strip() if gov_match else "State of Delaware"
        gov_quote = gov_match.group(0) if gov_match else None

        # Risks
        risks = []
        if re.search(r'unlimited liability', text, re.IGNORECASE):
            risks.append(ContractRisk(
                risk_title="Unlimited Liability Clause",
                severity="HIGH",
                description="Contract explicitly mentions unlimited liability without standard financial caps.",
                page=1
            ))
        if re.search(r'automatic(?:ally)? renew', text, re.IGNORECASE):
            risks.append(ContractRisk(
                risk_title="Automatic Renewal",
                severity="MEDIUM",
                description="Contract automatically renews unless written notice is provided.",
                page=1
            ))

        # Pillar 1: Heuristic SLA Extraction
        sla_match = re.search(r'(\d{2}(?:\.\d{1,3})?%)\s*(?:uptime|availability)', text, re.IGNORECASE)
        uptime = sla_match.group(1) if sla_match else ("99.9%" if re.search(r'sla|service level', text, re.IGNORECASE) else None)
        sla_quote = sla_match.group(0) if sla_match else None
        credit_match = re.search(r'(\d+%\s*(?:service\s+credit|fee\s+reduction))', text, re.IGNORECASE)
        service_credit = credit_match.group(1) if credit_match else "10% service credit for downtime exceeding 1 hour"

        # Pillar 1 (M&A): Heuristic Change of Control Extraction
        has_coc = bool(re.search(r'change of control|acquisition|merger|consolidation', text, re.IGNORECASE))
        requires_consent = bool(
            re.search(r'(?:change of control|merger|acquisition).{1,80}?(?:require[s]?\s+(?:prior\s+)?(?:written\s+)?consent)', text, re.IGNORECASE) or
            re.search(r'(?:require[s]?\s+(?:prior\s+)?(?:written\s+)?consent).{1,80}?(?:change of control|acquisition)', text, re.IGNORECASE)
        )
        allows_term_acq = bool(
            re.search(r'(?:change of control|merger|acquisition).{1,120}?(?:right\s+to\s+terminate|immediate\s+termination)', text, re.IGNORECASE) or
            re.search(r'(?:right\s+to\s+terminate|immediate\s+termination).{1,120}?(?:change of control|acquisition)', text, re.IGNORECASE)
        )
        coc_quote_match = re.search(r'([^.\n]*?(?:change of control|merger|acquisition)[^.\n]*\.)', text, re.IGNORECASE)
        coc_quote = coc_quote_match.group(1).strip() if coc_quote_match else None

        # Pillar 1: Termination & Penalties
        term_fee_match = re.search(r'(?:early\s+termination\s+(?:fee|penalty)|liquidated\s+damages)\s*(?:of)?\s*\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)', text, re.IGNORECASE)
        early_term_fee = float(term_fee_match.group(1).replace(",", "")) if term_fee_match else None
        notice_match = re.search(r'(\d{2,3})\s*days?\s*(?:prior\s+)?written\s+notice', text, re.IGNORECASE)
        notice_days = int(notice_match.group(1)) if notice_match else 30

        # Pillar 1: Renewal terms
        renewal_notice_match = re.search(r'at\s+least\s+(\d{2,3})\s*days?\s*prior\s+to\s*(?:the\s+)?(?:expiration|renewal)', text, re.IGNORECASE)
        renewal_deadline = int(renewal_notice_match.group(1)) if renewal_notice_match else (60 if re.search(r'auto\w*\s+renew', text, re.IGNORECASE) else None)

        return StructuredContractOutput(
            title=title,
            document_type=doc_type,
            summary=f"{title} between " + " and ".join(p.name for p in parties) + ".",
            parties=parties,
            dates=ContractDates(
                effective_date=effective_date,
                expiration_date=expiration_date,
                term_length="12 months",
                auto_renewal=bool(re.search(r'auto\w*\s+renew', text, re.IGNORECASE)),
                quote=date_quote,
                page=1
            ),
            financials=FinancialTerms(
                total_value=total_value or 50000.0,
                currency="USD",
                payment_terms="Net 30 days upon invoice receipt",
                quote=val_quote,
                page=1
            ),
            sla=SLATerms(
                uptime_guarantee=uptime,
                response_time_hours=2.0 if uptime else None,
                service_credit_penalty=service_credit if uptime else None,
                penalty_cap="15% of monthly fees",
                quote=sla_quote,
                page=1
            ),
            change_of_control=ChangeOfControlClause(
                has_change_of_control=has_coc,
                requires_vendor_consent=requires_consent,
                allows_termination_on_acquisition=allows_term_acq,
                quote=coc_quote,
                page=1
            ),
            termination=TerminationAndPenalties(
                termination_for_convenience=bool(re.search(r'terminate\s+for\s+convenience', text, re.IGNORECASE)),
                convenience_notice_days=notice_days,
                early_termination_fee=early_term_fee,
                penalty_description="Standard liquidated damages" if early_term_fee else None,
                quote=None,
                page=1
            ),
            renewal=RenewalConditions(
                auto_renewal=bool(re.search(r'auto\w*\s+renew', text, re.IGNORECASE)),
                renewal_term="1 year",
                notice_deadline_days=renewal_deadline,
                price_escalation_cap="Max 5% annual escalation",
                quote=None,
                page=1
            ),
            legal=LegalClauses(
                governing_law=governing_law,
                jurisdiction_venue=f"{governing_law} Courts",
                limitation_of_liability="Capped at total fees paid in preceding 12 months",
                indemnification_cap="Mutual standard indemnification",
                quotes={"governing_law": gov_quote} if gov_quote else {},
                pages={"governing_law": 1} if gov_quote else {}
            ),
            risks=risks,
            confidence_self_assessment=0.92
        )


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini API client using structured JSON generation."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    def extract(self, document: ParsedDocument) -> StructuredContractOutput:
        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            file_name=document.file_name,
            page_count=document.page_count,
            document_content=document.full_text[:120000]  # Safe token budget
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{CONTRACT_EXTRACTION_SYSTEM_PROMPT}\n\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        with httpx.Client(timeout=90.0) as client:
            resp = client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(raw_text)
            return StructuredContractOutput.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise


class OpenAILLMClient(BaseLLMClient):
    """OpenAI API client using JSON mode / structured outputs."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def extract(self, document: ParsedDocument) -> StructuredContractOutput:
        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            file_name=document.file_name,
            page_count=document.page_count,
            document_content=document.full_text[:120000]
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": CONTRACT_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=90.0) as client:
            resp = client.post(self.endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        parsed_json = json.loads(content)
        return StructuredContractOutput.model_validate(parsed_json)


def get_llm_client(
    provider: str = "mock",
    gemini_key: Optional[str] = None,
    openai_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseLLMClient:
    """Factory to retrieve configured LLM client."""
    provider_lower = provider.lower()

    if provider_lower == "gemini" and gemini_key:
        return GeminiLLMClient(api_key=gemini_key, model_name=model_name or "gemini-1.5-pro")
    elif provider_lower == "openai" and openai_key:
        return OpenAILLMClient(api_key=openai_key, model_name=model_name or "gpt-4o")
    else:
        logger.info("Using MockLLMClient (offline / deterministic mode).")
        return MockLLMClient()
