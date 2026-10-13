"""Business rule execution and statistical anomaly detection engine."""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.automation import BusinessRule, DataAnomaly


DEFAULT_ENTERPRISE_RULES: List[BusinessRule] = [
    BusinessRule(
        rule_id="RULE-MANDATORY-PO-HIGH-VALUE",
        rule_name="Mandatory PO for High-Value Transactions",
        rule_type="CONDITIONAL",
        target_field="po_number",
        severity="HIGH",
        threshold_value=10000.0,
        description="Transactions over $10,000 must have a valid Purchase Order (PO) to prevent maverick spend.",
        mandatory=True,
    ),
    BusinessRule(
        rule_id="RULE-MAX-THRESHOLD-AUDIT",
        rule_name="Executive Authorization Threshold",
        rule_type="THRESHOLD",
        target_field="amount",
        severity="CRITICAL",
        threshold_value=250000.0,
        operator="gt",
        description="Single transaction exceeds $250,000 threshold requiring CFO / Board review.",
    ),
    BusinessRule(
        rule_id="RULE-NEGATIVE-AMOUNT-AUDIT",
        rule_name="Unclassified Negative Amount",
        rule_type="CONDITIONAL",
        target_field="amount",
        severity="WARNING",
        threshold_value=0.0,
        operator="lt",
        description="Negative transaction amount detected without explicit Credit Memo / Refund classification.",
    ),
    BusinessRule(
        rule_id="RULE-FUTURE-DATE",
        rule_name="Future-Dated Invoice Anomaly",
        rule_type="PATTERN_MATCH",
        target_field="date",
        severity="HIGH",
        description="Invoice date is set in the future relative to transaction processing time.",
    ),
]


class BusinessRuleEngine:
    """Evaluates declarative business rules and statistical outlier models over datasets."""

    def __init__(self, custom_rules: Optional[List[BusinessRule]] = None):
        self.rules: List[BusinessRule] = list(DEFAULT_ENTERPRISE_RULES)
        if custom_rules:
            self.rules.extend(custom_rules)

    def evaluate_rules(self, records: List[Dict[str, Any]]) -> List[DataAnomaly]:
        """Execute all active business rules across the records."""
        anomalies: List[DataAnomaly] = []
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        for idx, rec in enumerate(records):
            rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
            amount = rec.get("amount")

            for rule in self.rules:
                # 1. Mandatory PO on high-value spend
                if rule.rule_id == "RULE-MANDATORY-PO-HIGH-VALUE":
                    if isinstance(amount, (int, float)) and amount >= (rule.threshold_value or 10000.0):
                        po = str(rec.get("po_number") or "").strip()
                        if not po or po.lower() in ["none", "n/a", "null", "pending", ""]:
                            anomalies.append(
                                DataAnomaly(
                                    anomaly_id=f"ANOM-RULE-{rule.rule_id}-{idx}",
                                    record_index=idx,
                                    record_id=rec_id,
                                    field_name="po_number",
                                    anomaly_type="MISSING_MANDATORY_FIELD",
                                    severity=rule.severity,
                                    description=f"{rule.description} (Transaction amount: ${amount:,.2f})",
                                    original_value=po or "EMPTY",
                                    suggested_value="Assign approved PO before disbursement",
                                    confidence_score=0.98,
                                )
                            )

                # 2. Executive Threshold Audit
                elif rule.rule_id == "RULE-MAX-THRESHOLD-AUDIT":
                    if isinstance(amount, (int, float)) and amount > (rule.threshold_value or 250000.0):
                        anomalies.append(
                            DataAnomaly(
                                anomaly_id=f"ANOM-RULE-{rule.rule_id}-{idx}",
                                record_index=idx,
                                record_id=rec_id,
                                field_name="amount",
                                anomaly_type="THRESHOLD_VIOLATION",
                                severity=rule.severity,
                                description=f"{rule.description} (Amount: ${amount:,.2f} > ${rule.threshold_value:,.2f})",
                                original_value=amount,
                                suggested_value=None,
                                confidence_score=0.99,
                            )
                        )

                # 3. Negative Amount
                elif rule.rule_id == "RULE-NEGATIVE-AMOUNT-AUDIT":
                    if isinstance(amount, (int, float)) and amount < 0:
                        status = str(rec.get("status") or "").lower()
                        category = str(rec.get("category") or "").lower()
                        desc = str(rec.get("description") or "").lower()
                        is_credit = any(
                            kw in status or kw in category or kw in desc
                            for kw in ["credit", "refund", "reversal", "memo", "discount"]
                        )
                        if not is_credit:
                            anomalies.append(
                                DataAnomaly(
                                    anomaly_id=f"ANOM-RULE-{rule.rule_id}-{idx}",
                                    record_index=idx,
                                    record_id=rec_id,
                                    field_name="amount",
                                    anomaly_type="CROSS_FIELD_INCONSISTENCY",
                                    severity=rule.severity,
                                    description=rule.description,
                                    original_value=amount,
                                    suggested_value="Verify whether line item is an unrecorded credit memo",
                                    confidence_score=0.92,
                                )
                            )

                # 4. Future-dated transactions
                elif rule.rule_id == "RULE-FUTURE-DATE":
                    rec_date = str(rec.get("date") or "").strip()
                    if rec_date and rec_date > today_str:
                        anomalies.append(
                            DataAnomaly(
                                anomaly_id=f"ANOM-RULE-{rule.rule_id}-{idx}",
                                record_index=idx,
                                record_id=rec_id,
                                field_name="date",
                                anomaly_type="SUSPICIOUS_PATTERN",
                                severity=rule.severity,
                                description=f"Invoice date '{rec_date}' is in the future (current system date: {today_str})",
                                original_value=rec_date,
                                suggested_value=today_str,
                                confidence_score=0.95,
                            )
                        )

        return anomalies

    def detect_statistical_anomalies(
        self, records: List[Dict[str, Any]], field: str = "amount", z_threshold: float = 2.8
    ) -> Tuple[List[DataAnomaly], Dict[str, float]]:
        """
        Compute population statistics (mean, stdev, min, max, median) and flag Z-score outliers.
        """
        anomalies: List[DataAnomaly] = []
        valid_vals: List[float] = []

        for rec in records:
            val = rec.get(field)
            if isinstance(val, (int, float)) and not math.isnan(val):
                valid_vals.append(float(val))

        if len(valid_vals) < 4:
            return anomalies, {}

        # Calculate mean and standard deviation
        n = len(valid_vals)
        mean = sum(valid_vals) / n
        variance = sum((x - mean) ** 2 for x in valid_vals) / (n - 1) if n > 1 else 0.0
        stdev = math.sqrt(variance) if variance > 0 else 0.0

        sorted_vals = sorted(valid_vals)
        median = sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        stats = {
            "count": float(n),
            "mean": round(mean, 2),
            "stdev": round(stdev, 2),
            "median": round(median, 2),
            "min": round(sorted_vals[0], 2),
            "max": round(sorted_vals[-1], 2),
        }

        if stdev == 0:
            return anomalies, stats

        # Detect outliers exceeding Z-score threshold
        for idx, rec in enumerate(records):
            val = rec.get(field)
            if isinstance(val, (int, float)) and not math.isnan(val):
                z_score = (float(val) - mean) / stdev
                if abs(z_score) >= z_threshold:
                    severity = "CRITICAL" if abs(z_score) >= 4.0 else "HIGH"
                    rec_id = str(rec.get("invoice_id", f"REC-{idx}"))
                    anomalies.append(
                        DataAnomaly(
                            anomaly_id=f"ANOM-ZSCORE-{field.upper()}-{idx}",
                            record_index=idx,
                            record_id=rec_id,
                            field_name=field,
                            anomaly_type="Z_SCORE_OUTLIER",
                            severity=severity,
                            description=(
                                f"Statistical outlier on '{field}': value ${float(val):,.2f} is "
                                f"{abs(z_score):.2f} standard deviations from the dataset mean (${mean:,.2f})."
                            ),
                            original_value=round(float(val), 2),
                            suggested_value=round(mean, 2),
                            z_score=round(z_score, 2),
                            confidence_score=min(0.99, 0.85 + (abs(z_score) / 20.0)),
                        )
                    )

        return anomalies, stats

