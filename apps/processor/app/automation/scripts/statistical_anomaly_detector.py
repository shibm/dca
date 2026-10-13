"""Specialized Python Script: High-Volume Statistical & Benford Anomaly Detector."""

from __future__ import annotations
import math
from collections import Counter
from typing import Any, Dict, List, Tuple
from app.schemas.automation import AutomationScriptMetadata, BusinessInsight, DataAnomaly
from app.automation.rule_engine import BusinessRuleEngine


SCRIPT_METADATA = AutomationScriptMetadata(
    script_id="statistical_anomaly_detector",
    name="Statistical & Benford Forensic Anomaly Detector",
    category="ANOMALY_RISK",
    description="Employs Z-score outlier detection, Benford's Law distribution testing, and round-number bias profiling to detect audit risks.",
    version="2.0.0",
    tags=["statistics", "benford-law", "forensics", "z-score", "fraud-risk"],
    required_fields=["amount"],
    optional_fields=["invoice_id", "vendor_name", "date"],
)

# Theoretical Benford's Law first-digit probabilities: log10(1 + 1/d)
BENFORD_DISTRIBUTION = {
    1: 0.301,
    2: 0.176,
    3: 0.125,
    4: 0.097,
    5: 0.079,
    6: 0.067,
    7: 0.058,
    8: 0.051,
    9: 0.046,
}


def run(
    records: List[Dict[str, Any]], parameters: Dict[str, Any]
) -> Tuple[List[DataAnomaly], List[BusinessInsight], Dict[str, Any]]:
    """
    Execute statistical and forensic anomaly detection.
    Returns: (anomalies, insights, metrics)
    """
    anomalies: List[DataAnomaly] = []
    insights: List[BusinessInsight] = []

    engine = BusinessRuleEngine()
    z_anomalies, stats = engine.detect_statistical_anomalies(records, field="amount", z_threshold=2.8)
    anomalies.extend(z_anomalies)

    # 1. Round-Number Bias Analysis (Invoices rounded to nearest $1,000 or $5,000)
    round_number_count = 0
    first_digits: List[int] = []

    for idx, rec in enumerate(records):
        amt = rec.get("amount")
        if isinstance(amt, (int, float)) and amt > 0:
            # Round number check (e.g. $5,000.00, $25,000.00)
            if amt >= 1000 and amt % 1000 == 0:
                round_number_count += 1
                if amt >= 10000:
                    rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
                    anomalies.append(
                        DataAnomaly(
                            anomaly_id=f"ANOM-ROUND-NUM-{idx}",
                            record_index=idx,
                            record_id=rec_id,
                            field_name="amount",
                            anomaly_type="SUSPICIOUS_PATTERN",
                            severity="WARNING",
                            description=f"Artificial round-number transaction: ${amt:,.2f} precisely matches a round multiplier.",
                            original_value=amt,
                            suggested_value="Review underlying itemized invoice breakdown",
                            confidence_score=0.88,
                        )
                    )

            # First non-zero digit extraction for Benford analysis
            s_amt = str(amt).replace(".", "").lstrip("0")
            if s_amt:
                first_digits.append(int(s_amt[0]))

    total_valid = len(first_digits)
    benford_divergence_score = 0.0

    if total_valid >= 20:
        counts = Counter(first_digits)
        # Calculate Chi-Square like absolute divergence
        for d in range(1, 10):
            observed_freq = counts[d] / total_valid
            expected_freq = BENFORD_DISTRIBUTION[d]
            benford_divergence_score += abs(observed_freq - expected_freq)

        benford_divergence_score = round(benford_divergence_score, 3)

        insights.append(
            BusinessInsight(
                insight_id="INSIGHT-BENFORD-ANALYSIS",
                title="Benford's Law First-Digit Conformity",
                category="Forensic Risk",
                metric_type="SCORE",
                metric_value=benford_divergence_score,
                formatted_value=f"{benford_divergence_score:.3f} dev",
                narrative=(
                    f"First-digit distribution across {total_valid} amounts shows total divergence of {benford_divergence_score:.3f}. "
                    + ("Elevated anomaly probability indicative of manual estimates or threshold structuring." if benford_divergence_score > 0.35 else "Distribution closely aligns with natural logarithmic transaction patterns.")
                ),
                recommendation="Target high-deviation vendor categories for random sample audit." if benford_divergence_score > 0.35 else "Maintain routine monitoring.",
                trend="RISK" if benford_divergence_score > 0.35 else "NEUTRAL",
            )
        )

    # Statistical outlier insight
    insights.append(
        BusinessInsight(
            insight_id="INSIGHT-STAT-OUTLIERS",
            title="Statistical Outlier Count (|Z| > 2.8)",
            category="Distribution Profile",
            metric_type="COUNT",
            metric_value=float(len(z_anomalies)),
            formatted_value=f"{len(z_anomalies)} records",
            narrative=(
                f"Dataset contains {len(z_anomalies)} statistical amount outliers relative to median "
                f"${stats.get('median', 0.0):,.2f} and standard deviation ${stats.get('stdev', 0.0):,.2f}."
            ),
            recommendation="Segregate statistical outliers for expedited secondary controller sign-off.",
            trend="RISK" if len(z_anomalies) > 3 else "NEUTRAL",
        )
    )

    metrics = {
        **stats,
        "round_number_count": round_number_count,
        "round_number_ratio_pct": round(round_number_count / total_valid * 100.0, 1) if total_valid > 0 else 0.0,
        "benford_divergence": benford_divergence_score,
        "z_score_outliers_count": len(z_anomalies),
    }

    return anomalies, insights, metrics

