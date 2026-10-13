import re
import logging
from typing import Dict, List, Optional, Any, Tuple
import pdfplumber

logger = logging.getLogger(__name__)


def parse_financial_number(val_str: Optional[str]) -> Optional[float]:
    """Parse financial number strings, handling negatives in parentheses like ($1,234.50), (1,234.50), M/k multipliers."""
    if not val_str:
        return None

    cleaned = val_str.strip().replace("$", "").replace("€", "").replace("£", "").replace(",", "")
    if not cleaned or cleaned == "-" or cleaned.lower() == "n/a" or cleaned == "—":
        return 0.0

    # Negative accounting formatting: (123.45) or ($123.45) -> -123.45
    is_negative = False
    if cleaned.startswith("(") and cleaned.endswith(")"):
        is_negative = True
        cleaned = cleaned[1:-1].strip().replace("$", "").replace("€", "").replace("£", "")
    elif cleaned.startswith("-"):
        is_negative = True
        cleaned = cleaned[1:].strip().replace("$", "").replace("€", "").replace("£", "")

    # Multipliers
    multiplier = 1.0
    if cleaned.lower().endswith("m"):
        multiplier = 1_000_000.0
        cleaned = cleaned[:-1].strip()
    elif cleaned.lower().endswith("k"):
        multiplier = 1_000.0
        cleaned = cleaned[:-1].strip()
    elif cleaned.lower().endswith("b"):
        multiplier = 1_000_000_000.0
        cleaned = cleaned[:-1].strip()

    try:
        val = float(cleaned) * multiplier
        return -val if is_negative else val
    except ValueError:
        return None


class FinancialTableExtractor:
    """Extracts and normalizes financial statement line items from PDF tabular structures."""

    # Taxonomy mapping: canonical key -> regex patterns matching variations
    LINE_ITEM_TAXONOMY = {
        "revenue": [
            r"^(?:total\s+)?revenue[s]?",
            r"^(?:net\s+)?sales",
            r"^turnover",
            r"^operating\s+revenue[s]?",
            r"^total\s+billings"
        ],
        "cogs": [
            r"^cost\s+of\s+(?:goods\s+sold|sales|revenue)",
            r"^cost\s+of\s+products\s+sold",
            r"^direct\s+operating\s+costs"
        ],
        "gross_profit": [
            r"^gross\s+profit",
            r"^gross\s+margin"
        ],
        "operating_expenses": [
            r"^(?:total\s+)?operating\s+expenses",
            r"^total\s+opex",
            r"^operating\s+costs"
        ],
        "ebitda": [
            r"^ebitda",
            r"^adjusted\s+ebitda",
            r"^operating\s+profit\s+before\s+depreciation"
        ],
        "operating_income": [
            r"^operating\s+income",
            r"^operating\s+profit",
            r"^ebit\b",
            r"^operating\s+surplus"
        ],
        "net_income": [
            r"^net\s+income",
            r"^net\s+(?:profit|earnings)",
            r"^profit\s+(?:for\s+the\s+year|loss)",
            r"^net\s+loss"
        ],
        "cash_and_equivalents": [
            r"^cash\s+and\s+(?:cash\s+)?equivalents",
            r"^cash\s+at\s+bank",
            r"^liquid\s+funds"
        ],
        "total_assets": [
            r"^total\s+assets",
            r"^total\s+current\s+and\s+non-current\s+assets"
        ],
        "total_debt": [
            r"^total\s+debt",
            r"^total\s+borrowings",
            r"^(?:total\s+)?loans\s+and\s+borrowings"
        ],
        "total_liabilities": [
            r"^total\s+liabilities",
            r"^total\s+liabilities\s+and\s+equity"
        ],
        "total_shareholder_equity": [
            r"^(?:total\s+)?(?:stockholders\'?|shareholders\'?)\s+equity",
            r"^total\s+equity",
            r"^net\s+assets"
        ],
        "operating_cash_flow": [
            r"^cash\s+(?:flow\s+)?from\s+operating\s+activities",
            r"^operating\s+cash\s+flow",
            r"^net\s+cash\s+provided\s+by\s+operating"
        ],
        "capital_expenditures": [
            r"^capital\s+expenditures",
            r"^capex",
            r"^purchase\s+of\s+property,\s+plant"
        ],
        "free_cash_flow": [
            r"^free\s+cash\s+flow",
            r"^fcf\b"
        ]
    }

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, float]:
        """Extract all financial lines matching standard taxonomy."""
        extracted_data: Dict[str, float] = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # 1. Structured table extraction
                tables = page.extract_tables() or []
                for table in tables:
                    for row in table:
                        if not row or len(row) < 2:
                            continue
                        
                        label_cell = str(row[0]).strip().lower() if row[0] else ""
                        if not label_cell:
                            continue

                        for canonical_key, patterns in self.LINE_ITEM_TAXONOMY.items():
                            if canonical_key in extracted_data:
                                continue

                            for pat in patterns:
                                if re.search(pat, label_cell, re.IGNORECASE):
                                    for cell in row[1:]:
                                        num = parse_financial_number(str(cell))
                                        if num is not None:
                                            extracted_data[canonical_key] = num
                                            break
                                    break

                # 2. Text line pattern matching fallback
                page_text = page.extract_text() or ""
                for line in page_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    for canonical_key, patterns in self.LINE_ITEM_TAXONOMY.items():
                        if canonical_key in extracted_data:
                            continue

                        for pat in patterns:
                            # Look for pattern followed by a financial number, e.g. $1,200 or ($1,200) or -$1,200
                            match = re.search(pat + r'\s+[\$€£]?\s*(\(?[\$€£]?[\d,]+(?:\.\d{1,2})?\)?|\-)', line, re.IGNORECASE)
                            if match:
                                num = parse_financial_number(match.group(1))
                                if num is not None:
                                    extracted_data[canonical_key] = num
                                    break

        return extracted_data
