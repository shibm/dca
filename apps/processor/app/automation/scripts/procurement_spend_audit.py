"""Specialized Python Script: Procurement & Spend Analytics Audit."""

from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from app.schemas.automation import AutomationScriptMetadata, BusinessInsight, DataAnomaly


SCRIPT_METADATA = AutomationScriptMetadata(
    script_id="procurement_spend_audit",
    name="Procurement Spend & Maverick Buying Auditor",
    category="PROCUREMENT",
    description="Analyzes spend concentration, detects unapproved maverick spend lacking POs, and flags duplicate payment exposures.",
    version="2.1.0",
    tags=["procurement", "spend-audit", "maverick-spend", "duplicate-payments"],
    required_fields=["vendor_name", "amount"],
    optional_fields=["po_number", "date", "department", "category", "invoice_id"],
)


def run(
    records: List[Dict[str, Any]], parameters: Dict[str, Any]
) -> Tuple[List[DataAnomaly], List[BusinessInsight], Dict[str, Any]]:
    """
    Execute procurement spend audit.
    Returns: (anomalies, insights, metrics)
    """
    anomalies: List[DataAnomaly] = []
    insights: List[BusinessInsight] = []

    po_threshold = float(parameters.get("po_threshold", 5000.0))
    vendor_spend: Dict[str, float] = defaultdict(float)
    vendor_counts: Dict[str, int] = defaultdict(int)
    maverick_records: List[Dict[str, Any]] = []
    total_spend = 0.0

    # Group payments for duplicate detection: (vendor_name, amount) -> list of records
    vendor_amount_buckets: Dict[Tuple[str, float], List[Tuple[int, Dict[str, Any]]]] = defaultdict(list)

    for idx, rec in enumerate(records):
        amt = rec.get("amount")
        if not isinstance(amt, (int, float)) or amt <= 0:
            continue

        v_name = str(rec.get("vendor_name") or "UNKNOWN_VENDOR").strip()
        vendor_spend[v_name] += amt
        vendor_counts[v_name] += 1
        total_spend += amt

        # Check for Maverick buying (spend >= threshold lacking PO)
        po = str(rec.get("po_number") or "").strip()
        if amt >= po_threshold and (not po or po.lower() in ["none", "n/a", "pending", ""]):
            maverick_records.append(rec)
            rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
            anomalies.append(
                DataAnomaly(
                    anomaly_id=f"ANOM-MAVERICK-{idx}",
                    record_index=idx,
                    record_id=rec_id,
                    field_name="po_number",
                    anomaly_type="MISSING_MANDATORY_FIELD",
                    severity="HIGH",
                    description=f"Maverick Spend: ${amt:,.2f} disbursed to '{v_name}' without approved PO (Policy threshold: ${po_threshold:,.2f}).",
                    original_value=None,
                    suggested_value="Enforce retroactive PO or manager signoff",
                )
            )

        # Check for suspected duplicate payments (same vendor, same amount)
        norm_v = v_name.lower()
        vendor_amount_buckets[(norm_v, round(amt, 2))].append((idx, rec))

    # Detect duplicate payment clusters
    suspected_duplicate_amount = 0.0
    for (norm_v, rounded_amt), occurrences in vendor_amount_buckets.items():
        if len(occurrences) > 1:
            for idx, rec in occurrences[1:]:
                rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
                suspected_duplicate_amount += rounded_amt
                anomalies.append(
                    DataAnomaly(
                        anomaly_id=f"ANOM-SUSPECT-DUP-{idx}",
                        record_index=idx,
                        record_id=rec_id,
                        field_name="amount",
                        anomaly_type="SUSPICIOUS_PATTERN",
                        severity="CRITICAL",
                        description=(
                            f"Suspected duplicate payment: {len(occurrences)} identical disbursements of "
                            f"${rounded_amt:,.2f} issued to '{norm_v.title()}'."
                        ),
                        original_value=rounded_amt,
                        suggested_value="Hold payment pending duplicate invoice review",
                        confidence_score=0.96,
                    )
                )

    # Calculate Spend Concentration
    sorted_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_vendors[:5]
    top_5_spend = sum(spend for _, spend in top_5)
    concentration_pct = (top_5_spend / total_spend * 100.0) if total_spend > 0 else 0.0

    maverick_spend_total = sum(float(r.get("amount") or 0) for r in maverick_records)
    maverick_pct = (maverick_spend_total / total_spend * 100.0) if total_spend > 0 else 0.0

    # Generate Strategic Business Insights
    insights.append(
        BusinessInsight(
            insight_id="INSIGHT-SPEND-CONCENTRATION",
            title="Top 5 Vendor Spend Concentration",
            category="Procurement Risk",
            metric_type="PERCENTAGE",
            metric_value=round(concentration_pct, 1),
            formatted_value=f"{concentration_pct:.1f}%",
            narrative=(
                f"Top 5 suppliers represent ${top_5_spend:,.2f} ({concentration_pct:.1f}%) of ${total_spend:,.2f} total spend. "
                f"Primary vendor: '{top_5[0][0]}' (${top_5[0][1]:,.2f})."
                if top_5 else "No vendor spend data available."
            ),
            recommendation="Consolidate volume with top vendors to negotiate tier-3 tier discounts of 8-12%.",
            trend="RISK" if concentration_pct > 60.0 else "NEUTRAL",
        )
    )

    insights.append(
        BusinessInsight(
            insight_id="INSIGHT-MAVERICK-BUYING",
            title="Unapproved Maverick Spend Exposure",
            category="Compliance",
            metric_type="CURRENCY",
            metric_value=round(maverick_spend_total, 2),
            formatted_value=f"${maverick_spend_total:,.2f}",
            narrative=(
                f"{len(maverick_records)} transactions totaling ${maverick_spend_total:,.2f} ({maverick_pct:.1f}% of total) "
                f"bypassed formal PO generation."
            ),
            recommendation="Institute automated ERP approval gates blocking invoice release without linked PO.",
            trend="RISK" if maverick_pct > 10.0 else "NEUTRAL",
        )
    )

    if suspected_duplicate_amount > 0:
        insights.append(
            BusinessInsight(
                insight_id="INSIGHT-DUPLICATE-RECOVERY",
                title="Potential Duplicate Payment Recovery",
                category="Cash Leakage",
                metric_type="CURRENCY",
                metric_value=round(suspected_duplicate_amount, 2),
                formatted_value=f"${suspected_duplicate_amount:,.2f}",
                narrative=(
                    f"Identified multiple identical disbursements to identical payees. "
                    f"Estimated recovery opportunity: ${suspected_duplicate_amount:,.2f}."
                ),
                recommendation="Dispatch claw-back statements to vendors or initiate vendor credit offsets.",
                trend="RISK",
            )
        )

    metrics = {
        "total_spend": round(total_spend, 2),
        "total_vendors": len(vendor_spend),
        "top_5_vendor_concentration_pct": round(concentration_pct, 2),
        "maverick_spend_total": round(maverick_spend_total, 2),
        "maverick_spend_pct": round(maverick_pct, 2),
        "suspected_duplicate_amount": round(suspected_duplicate_amount, 2),
    }

    return anomalies, insights, metrics

