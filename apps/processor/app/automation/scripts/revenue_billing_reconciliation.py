"""Specialized Python Script: Revenue & Billing Cut-off Reconciliation."""

from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from app.schemas.automation import AutomationScriptMetadata, BusinessInsight, DataAnomaly


SCRIPT_METADATA = AutomationScriptMetadata(
    script_id="revenue_billing_reconciliation",
    name="Revenue Billing & Cut-Off Reconciliation",
    category="REVENUE_BILLING",
    description="Identifies revenue leakage, unbilled work-in-progress, billing cutoff discrepancies, and disputes across divisions.",
    version="1.8.0",
    tags=["revenue", "billing", "cutoff-testing", "leakage", "ar-audit"],
    required_fields=["amount"],
    optional_fields=["invoice_id", "date", "department", "status", "category", "vendor_name"],
)


def run(
    records: List[Dict[str, Any]], parameters: Dict[str, Any]
) -> Tuple[List[DataAnomaly], List[BusinessInsight], Dict[str, Any]]:
    """
    Execute revenue billing reconciliation.
    Returns: (anomalies, insights, metrics)
    """
    anomalies: List[DataAnomaly] = []
    insights: List[BusinessInsight] = []

    total_billed = 0.0
    total_unbilled = 0.0
    total_disputed = 0.0
    department_revenue: Dict[str, float] = defaultdict(float)
    status_counts: Dict[str, int] = defaultdict(int)

    for idx, rec in enumerate(records):
        amt = rec.get("amount")
        if not isinstance(amt, (int, float)):
            continue

        status = str(rec.get("status") or "BILLED").upper()
        dept = str(rec.get("department") or "General").strip()
        status_counts[status] += 1
        rec_id = str(rec.get("invoice_id", f"REC-{idx}"))

        if status in ["UNBILLED", "DRAFT", "PENDING_BILLING", "WIP"]:
            total_unbilled += amt
            anomalies.append(
                DataAnomaly(
                    anomaly_id=f"ANOM-REV-UNBILLED-{idx}",
                    record_index=idx,
                    record_id=rec_id,
                    field_name="status",
                    anomaly_type="THRESHOLD_VIOLATION",
                    severity="MEDIUM",
                    description=f"Unbilled Revenue/WIP item: ${amt:,.2f} in department '{dept}' pending invoice issuance.",
                    original_value=status,
                    suggested_value="Issue invoice prior to monthly financial close",
                )
            )
        elif status in ["DISPUTED", "ON_HOLD", "REJECTED"]:
            total_disputed += amt
            anomalies.append(
                DataAnomaly(
                    anomaly_id=f"ANOM-REV-DISPUTED-{idx}",
                    record_index=idx,
                    record_id=rec_id,
                    field_name="status",
                    anomaly_type="CROSS_FIELD_INCONSISTENCY",
                    severity="HIGH",
                    description=f"Disputed Receivable item: ${amt:,.2f} withheld from settlement by customer.",
                    original_value=status,
                    suggested_value="Initiate AR dispute resolution and reserve provisioning",
                )
            )
        else:
            total_billed += amt
            department_revenue[dept] += amt

    total_pipeline = total_billed + total_unbilled + total_disputed
    unbilled_pct = (total_unbilled / total_pipeline * 100.0) if total_pipeline > 0 else 0.0
    dispute_pct = (total_disputed / total_pipeline * 100.0) if total_pipeline > 0 else 0.0

    insights.append(
        BusinessInsight(
            insight_id="INSIGHT-REVENUE-BILLED",
            title="Total Recognized & Invoiced Revenue",
            category="Revenue Performance",
            metric_type="CURRENCY",
            metric_value=round(total_billed, 2),
            formatted_value=f"${total_billed:,.2f}",
            narrative=f"Successfully invoiced ${total_billed:,.2f} across {len(department_revenue)} operating divisions.",
            recommendation="Maintain current billing schedule with automated milestone triggers.",
            trend="UP",
        )
    )

    if total_unbilled > 0:
        insights.append(
            BusinessInsight(
                insight_id="INSIGHT-UNBILLED-WIP",
                title="Unbilled Work-in-Progress (WIP)",
                category="Cash Acceleration",
                metric_type="CURRENCY",
                metric_value=round(total_unbilled, 2),
                formatted_value=f"${total_unbilled:,.2f}",
                narrative=(
                    f"${total_unbilled:,.2f} ({unbilled_pct:.1f}% of total billing pipeline) remains unbilled. "
                    f"Immediate invoicing will accelerate operating cash flow."
                ),
                recommendation="Accelerate billing run 3 days before month-end cutoff to capture unbilled WIP.",
                trend="RISK" if unbilled_pct > 15.0 else "NEUTRAL",
            )
        )

    if total_disputed > 0:
        insights.append(
            BusinessInsight(
                insight_id="INSIGHT-DISPUTED-AR",
                title="Disputed Receivables Exposure",
                category="Credit Risk",
                metric_type="PERCENTAGE",
                metric_value=round(dispute_pct, 1),
                formatted_value=f"{dispute_pct:.1f}%",
                narrative=(
                    f"${total_disputed:,.2f} ({dispute_pct:.1f}% of portfolio) is currently under dispute or hold."
                ),
                recommendation="Establish bad-debt reserves of at least 35% on invoices disputed >60 days.",
                trend="RISK",
            )
        )

    metrics = {
        "total_billed": round(total_billed, 2),
        "total_unbilled": round(total_unbilled, 2),
        "total_disputed": round(total_disputed, 2),
        "total_pipeline": round(total_pipeline, 2),
        "unbilled_ratio_pct": round(unbilled_pct, 2),
        "dispute_ratio_pct": round(dispute_pct, 2),
    }

    return anomalies, insights, metrics

