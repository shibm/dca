"""Specialized Python Script: Vendor SLA & Contractual Penalty Calculator."""

from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from app.schemas.automation import AutomationScriptMetadata, BusinessInsight, DataAnomaly


SCRIPT_METADATA = AutomationScriptMetadata(
    script_id="vendor_sla_penalty_calculator",
    name="Vendor SLA Breach & Penalty Calculator",
    category="VENDOR_SLA",
    description="Cross-references operational metrics (uptime, delivery delay, MTTR) against contractual commitments to compute clawback penalties.",
    version="1.5.0",
    tags=["vendor-sla", "penalties", "breach-detection", "clawbacks"],
    required_fields=["vendor_name"],
    optional_fields=["amount", "uptime", "sla_target", "delay_days", "status"],
)


def run(
    records: List[Dict[str, Any]], parameters: Dict[str, Any]
) -> Tuple[List[DataAnomaly], List[BusinessInsight], Dict[str, Any]]:
    """
    Execute vendor SLA penalty calculations.
    Returns: (anomalies, insights, metrics)
    """
    anomalies: List[DataAnomaly] = []
    insights: List[BusinessInsight] = []

    vendor_penalties: Dict[str, float] = defaultdict(float)
    breach_count = 0
    total_evaluated = 0

    daily_delay_fine = float(parameters.get("daily_delay_fine", 500.0))
    uptime_threshold = float(parameters.get("uptime_threshold", 99.5))

    for idx, rec in enumerate(records):
        total_evaluated += 1
        v_name = str(rec.get("vendor_name") or "UNKNOWN_VENDOR").strip()
        rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
        amt = float(rec.get("amount") or 0.0)

        # 1. Delivery / Fulfillment Delay Check
        delay_days = rec.get("delay_days")
        if delay_days is not None:
            try:
                days = float(delay_days)
                if days > 0:
                    breach_count += 1
                    penalty = days * daily_delay_fine
                    vendor_penalties[v_name] += penalty
                    anomalies.append(
                        DataAnomaly(
                            anomaly_id=f"ANOM-SLA-DELAY-{idx}",
                            record_index=idx,
                            record_id=rec_id,
                            field_name="delay_days",
                            anomaly_type="THRESHOLD_VIOLATION",
                            severity="HIGH" if days > 5 else "WARNING",
                            description=(
                                f"SLA Breach: Delivery delayed by {days:.0f} days for '{v_name}'. "
                                f"Contractual penalty calculated at ${penalty:,.2f}."
                            ),
                            original_value=days,
                            suggested_value=0,
                        )
                    )
            except (ValueError, TypeError):
                pass

        # 2. Uptime / Availability Check
        uptime = rec.get("uptime") or rec.get("uptime_percent")
        if uptime is not None:
            try:
                up_val = float(str(uptime).replace("%", ""))
                target = float(str(rec.get("sla_target") or uptime_threshold).replace("%", ""))
                if up_val < target:
                    breach_count += 1
                    # Penalty: 10% credit if under target, 25% if under target - 1.0%
                    deficit = target - up_val
                    penalty_rate = 0.25 if deficit >= 1.0 else 0.10
                    penalty = amt * penalty_rate if amt > 0 else 2500.0
                    vendor_penalties[v_name] += penalty
                    anomalies.append(
                        DataAnomaly(
                            anomaly_id=f"ANOM-SLA-UPTIME-{idx}",
                            record_index=idx,
                            record_id=rec_id,
                            field_name="uptime",
                            anomaly_type="THRESHOLD_VIOLATION",
                            severity="CRITICAL" if deficit >= 1.0 else "HIGH",
                            description=(
                                f"Availability Breach: '{v_name}' reported {up_val:.2f}% uptime vs {target:.2f}% SLA target. "
                                f"Assessed penalty credit: ${penalty:,.2f}."
                            ),
                            original_value=up_val,
                            suggested_value=target,
                        )
                    )
            except (ValueError, TypeError):
                pass

    total_clawbacks = sum(vendor_penalties.values())

    insights.append(
        BusinessInsight(
            insight_id="INSIGHT-SLA-CLAWBACKS",
            title="Total Contractual SLA Penalties Due",
            category="Vendor Operations",
            metric_type="CURRENCY",
            metric_value=round(total_clawbacks, 2),
            formatted_value=f"${total_clawbacks:,.2f}",
            narrative=(
                f"Identified {breach_count} contractual SLA breaches across {len(vendor_penalties)} vendors, "
                f"resulting in ${total_clawbacks:,.2f} in recoverable penalties/credits."
            ),
            recommendation="Deduct assessed service credits directly from pending vendor AP remittances.",
            trend="RISK" if total_clawbacks > 10000 else "NEUTRAL",
        )
    )

    if vendor_penalties:
        top_breacher = sorted(vendor_penalties.items(), key=lambda x: x[1], reverse=True)[0]
        insights.append(
            BusinessInsight(
                insight_id="INSIGHT-TOP-SLA-DEFICIT",
                title=f"Highest Deficit: {top_breacher[0]}",
                category="Vendor Risk",
                metric_type="CURRENCY",
                metric_value=round(top_breacher[1], 2),
                formatted_value=f"${top_breacher[1]:,.2f}",
                narrative=f"Vendor '{top_breacher[0]}' accumulated the highest penalty burden of ${top_breacher[1]:,.2f}.",
                recommendation="Convene mandatory Quarterly Business Review (QBR) to address recurring breach trends.",
                trend="RISK",
            )
        )

    metrics = {
        "total_clawbacks_due": round(total_clawbacks, 2),
        "total_sla_breaches": breach_count,
        "vendors_with_breaches": len(vendor_penalties),
        "total_evaluated_records": total_evaluated,
    }

    return anomalies, insights, metrics

