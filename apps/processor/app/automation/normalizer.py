"""Data validation and normalization pipeline for multi-department disparate datasets."""

from __future__ import annotations
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from app.schemas.automation import DataAnomaly


# Canonical field mapping dictionary: canonical_key -> list of common column alias variations
FIELD_ALIASES: Dict[str, List[str]] = {
    "vendor_name": [
        "vendor", "vendor_name", "supplier", "supplier_name", "merchant", 
        "payee", "contractor", "party", "company_name", "client_name", "customer", "customer_name"
    ],
    "vendor_id": [
        "vendor_id", "vendor_code", "supplier_id", "supplier_num", "payee_id"
    ],
    "invoice_id": [
        "invoice_id", "invoice_no", "invoice_number", "inv_id", "inv_num", 
        "inv_no", "bill_id", "bill_num", "transaction_id", "txn_id", "doc_id", "reference"
    ],
    "amount": [
        "amount", "amt", "invoice_amount", "total", "total_amount", "total_price", "price",
        "spend", "cost", "net_amount", "line_total", "billed_amount", "charge", "unit_price"
    ],
    "date": [
        "date", "invoice_date", "inv_date", "txn_date", "transaction_date", 
        "billing_date", "bill_date", "payment_date", "timestamp", "created_date"
    ],
    "po_number": [
        "po", "po_number", "po_no", "po_num", "purchase_order", "po_ref", "order_number"
    ],
    "department": [
        "department", "dept", "cost_center", "business_unit", "bu", "org_unit", "division"
    ],
    "category": [
        "category", "spend_category", "expense_type", "gl_account", "gl_code", 
        "account_code", "service_type", "item_category"
    ],
    "status": [
        "status", "payment_status", "approval_status", "state", "invoice_status"
    ],
    "description": [
        "description", "desc", "memo", "notes", "line_description", "item_name", "details"
    ]
}


def sanitize_column_name(col: str) -> str:
    """Normalize raw column headers to lowercase snake_case for fuzzy matching."""
    cleaned = re.sub(r"[^\w\s]", "", str(col).strip().lower())
    return re.sub(r"\s+", "_", cleaned)


def map_columns_to_canonical(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map raw inconsistent dictionary keys into DCA standard canonical attributes.
    Preserves original attributes under their standard or original names.
    """
    canonical_record: Dict[str, Any] = {}
    matched_raw_keys: Set[str] = set()

    # Pre-clean raw keys for matching
    cleaned_to_raw = {sanitize_column_name(k): k for k in raw_record.keys()}

    for canonical_name, aliases in FIELD_ALIASES.items():
        found_key: Optional[str] = None
        for alias in aliases:
            cleaned_alias = sanitize_column_name(alias)
            if cleaned_alias in cleaned_to_raw:
                found_key = cleaned_to_raw[cleaned_alias]
                break

        if found_key is not None:
            canonical_record[canonical_name] = raw_record[found_key]
            matched_raw_keys.add(found_key)

    # Retain unmapped custom columns as-is
    for k, v in raw_record.items():
        if k not in matched_raw_keys and sanitize_column_name(k) not in canonical_record:
            canonical_record[k] = v

    return canonical_record


def parse_clean_amount(val: Any) -> Optional[float]:
    """Parse dirty currency strings ($1,250.50, (300.00), -45.00, etc.) to float."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    is_negative = False

    # Check for accounting parentheses e.g. ($1,250.00) or (450)
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()
    elif s.startswith("-"):
        is_negative = True
        s = s[1:].strip()

    # Strip currency symbols, commas, spaces, USD/EUR
    s = re.sub(r"[^\d.]", "", s)
    if not s:
        return None

    try:
        num = float(s)
        return -num if is_negative else num
    except ValueError:
        return None


def parse_clean_date(val: Any) -> Optional[str]:
    """Parse dates from multiple department formats into standard ISO YYYY-MM-DD."""
    if val is None or val == "":
        return None
    s = str(val).strip()

    # If already YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s

    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%b %d, %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return s  # Return original string if format is unparseable


class DataNormalizer:
    """End-to-end normalization and deduplication processor for raw records."""

    def __init__(self, deduplicate_keys: Optional[List[str]] = None):
        self.deduplicate_keys = deduplicate_keys or ["vendor_name", "invoice_id"]

    def normalize_record(self, raw_record: Dict[str, Any], record_idx: int) -> Tuple[Dict[str, Any], List[DataAnomaly]]:
        """Normalize a single raw record and report any format/type anomalies."""
        anomalies: List[DataAnomaly] = []
        canonical = map_columns_to_canonical(raw_record)

        # 1. Clean Amount
        if "amount" in canonical:
            original_amt = canonical["amount"]
            cleaned_amt = parse_clean_amount(original_amt)
            if cleaned_amt is None and original_amt is not None:
                anomalies.append(
                    DataAnomaly(
                        anomaly_id=f"ANOM-FMT-AMT-{record_idx}",
                        record_index=record_idx,
                        record_id=str(canonical.get("invoice_id", f"REC-{record_idx}")),
                        field_name="amount",
                        anomaly_type="INVALID_FORMAT",
                        severity="HIGH",
                        description=f"Unable to parse numeric amount from '{original_amt}'",
                        original_value=str(original_amt),
                        suggested_value=None,
                    )
                )
            else:
                canonical["amount"] = cleaned_amt

        # 2. Clean Date
        if "date" in canonical:
            original_date = canonical["date"]
            cleaned_date = parse_clean_date(original_date)
            canonical["date"] = cleaned_date

        # 3. Clean String fields (vendor_name, po_number, department)
        for str_field in ["vendor_name", "po_number", "department", "category", "invoice_id"]:
            if str_field in canonical and canonical[str_field] is not None:
                cleaned_str = str(canonical[str_field]).strip()
                # Remove repeated whitespace
                canonical[str_field] = re.sub(r"\s+", " ", cleaned_str)

        return canonical, anomalies

    def process_dataset(
        self, raw_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[DataAnomaly], int]:
        """
        Normalize all records and perform deduplication.
        Returns:
            (cleaned_records, anomalies_list, duplicate_count)
        """
        cleaned_records: List[Dict[str, Any]] = []
        all_anomalies: List[DataAnomaly] = []
        seen_keys: Dict[str, int] = {}
        duplicates_count = 0

        for idx, raw in enumerate(raw_records):
            norm_record, record_anomalies = self.normalize_record(raw, idx)
            all_anomalies.extend(record_anomalies)

            # Deduplication key generation
            v_name = str(norm_record.get("vendor_name", "")).strip().lower()
            inv_id = str(norm_record.get("invoice_id", "")).strip().lower()
            amt = str(norm_record.get("amount", "")).strip()
            date = str(norm_record.get("date", "")).strip()

            # Primary deduplication key: vendor + invoice_id if available; else vendor + amount + date
            if inv_id and v_name:
                dedup_key = f"{v_name}::{inv_id}"
            elif v_name and amt and date:
                dedup_key = f"{v_name}::{amt}::{date}"
            else:
                dedup_key = f"REC::{idx}"

            if dedup_key in seen_keys:
                duplicates_count += 1
                first_idx = seen_keys[dedup_key]
                all_anomalies.append(
                    DataAnomaly(
                        anomaly_id=f"ANOM-DEDUP-{idx}",
                        record_index=idx,
                        record_id=str(norm_record.get("invoice_id", f"REC-{idx}")),
                        field_name="invoice_id",
                        anomaly_type="DUPLICATE_RECORD",
                        severity="CRITICAL",
                        description=f"Duplicate record detected. Exact match with record index #{first_idx} for key '{dedup_key}'.",
                        original_value=dedup_key,
                        suggested_value="Flag for de-duplication or audit review",
                        confidence_score=0.99,
                    )
                )
                norm_record["_is_duplicate"] = True
                norm_record["_duplicate_of_index"] = first_idx
            else:
                seen_keys[dedup_key] = idx
                norm_record["_is_duplicate"] = False

            cleaned_records.append(norm_record)

        return cleaned_records, all_anomalies, duplicates_count
