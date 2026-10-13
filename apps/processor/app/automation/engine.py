"""End-to-end batch automation orchestrator for multi-department datasets."""

from __future__ import annotations
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.schemas.automation import (
    AutomationJobRequest,
    AutomationJobResult,
    BusinessInsight,
    DataAnomaly,
    ScriptExecutionLog,
)
from app.automation.normalizer import DataNormalizer
from app.automation.rule_engine import BusinessRuleEngine
from app.automation.script_registry import REGISTRY


class AutomationEngine:
    """Orchestrates ingestion, normalization, rule validation, and script execution."""

    def __init__(self):
        self.normalizer = DataNormalizer()
        self.registry = REGISTRY

    def run_job(self, request: AutomationJobRequest) -> AutomationJobResult:
        """Execute a full automation batch workflow."""
        job_id = request.job_id or f"job-{uuid.uuid4().hex[:8]}"
        started_at = datetime.utcnow().isoformat() + "Z"
        start_time = time.perf_counter()

        all_anomalies: List[DataAnomaly] = []
        all_insights: List[BusinessInsight] = []
        script_logs: List[ScriptExecutionLog] = []
        combined_metrics: Dict[str, Any] = {}

        # 1. Normalization & Deduplication
        cleaned_records, norm_anomalies, dup_count = self.normalizer.process_dataset(request.raw_records)
        all_anomalies.extend(norm_anomalies)

        # 2. Business Rule Validation
        rule_engine = BusinessRuleEngine(request.custom_rules)
        rule_anomalies = rule_engine.evaluate_rules(cleaned_records)
        all_anomalies.extend(rule_anomalies)

        # 3. Specialized Python Script Execution
        for script_id in request.script_ids:
            s_anomalies, s_insights, s_metrics, s_log = self.registry.execute_script(
                script_id, cleaned_records, request.parameters
            )
            all_anomalies.extend(s_anomalies)
            all_insights.extend(s_insights)
            script_logs.append(s_log)
            combined_metrics[script_id] = s_metrics

        # Sort anomalies by severity: CRITICAL -> HIGH -> WARNING -> INFO
        severity_order = {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "MEDIUM": 2, "INFO": 3}
        all_anomalies.sort(key=lambda a: severity_order.get(a.severity, 4))

        critical_count = sum(1 for a in all_anomalies if a.severity == "CRITICAL")
        execution_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        completed_at = datetime.utcnow().isoformat() + "Z"

        summary_metrics = {
            "total_records_ingested": len(request.raw_records),
            "cleaned_records_count": len(cleaned_records),
            "duplicates_detected": dup_count,
            "total_anomalies_flagged": len(all_anomalies),
            "critical_anomalies_count": critical_count,
            "high_risk_anomalies_count": sum(1 for a in all_anomalies if a.severity == "HIGH"),
            "scripts_executed_count": len(request.script_ids),
            "execution_time_ms": execution_ms,
            "subsystem_metrics": combined_metrics,
        }

        return AutomationJobResult(
            job_id=job_id,
            status="COMPLETED",
            started_at=started_at,
            completed_at=completed_at,
            execution_time_ms=execution_ms,
            total_records_ingested=len(request.raw_records),
            cleaned_records_count=len(cleaned_records),
            duplicates_detected=dup_count,
            anomalies_count=len(all_anomalies),
            critical_anomalies_count=critical_count,
            anomalies=all_anomalies,
            insights=all_insights,
            script_logs=script_logs,
            summary_metrics=summary_metrics,
            sample_cleaned_records=cleaned_records[:20],  # Return preview of first 20 records
        )


def generate_benchmark_multi_department_dataset() -> List[Dict[str, Any]]:
    """
    Generate realistic benchmark records from 4 disparate business units:
    - Procurement (messy supplier headers, missing POs, negative credits)
    - Finance & Billing (delayed billing, unbilled WIP, disputed receivables)
    - Logistics (delivery delays, fulfillment SLA metrics)
    - IT & Infrastructure (uptime percentages, SLA breaches, large contracts)
    """
    return [
        # --- Procurement Records (Varied Headers, Currency Strings, Missing POs) ---
        {
            "Supplier Name": "AWS Cloud Services LLC",
            "invoice_no": "INV-2026-9011",
            "invoice_amount": "$45,200.00",
            "date": "2026-02-14",
            "PO#": "PO-99120",
            "cost_center": "IT Infrastructure",
            "spend_category": "Cloud Hosting",
            "status": "APPROVED",
        },
        {
            "vendor": "AWS Cloud Services LLC",
            "inv_num": "INV-2026-9011",  # EXACT DUPLICATE
            "amt": "$45,200.00",
            "txn_date": "2026-02-14",
            "po": "PO-99120",
            "dept": "IT Infrastructure",
            "category": "Cloud Hosting",
            "status": "APPROVED",
        },
        {
            "merchant": "Apex Hardware Direct",
            "bill_id": "INV-8820",
            "Total Price": "$12,450.00",
            "Billing Date": "2026-02-15",
            "PO#": "",  # MISSING PO -> MAVERICK SPEND (> $10k)
            "department": "Engineering Hardware",
            "spend_category": "Lab Equipment",
            "status": "PAID",
        },
        {
            "supplier": "Global Courier Express",
            "doc_id": "GCX-10492",
            "line_total": "$1,450.00",
            "created_date": "2026-02-16",
            "po_no": "PO-88122",
            "division": "Logistics",
            "category": "Freight & Shipping",
            "delay_days": 6,  # SLA DELAY > 5 DAYS
            "status": "DELIVERED",
        },
        {
            "supplier_name": "MegaCorp Industrial Supply",
            "invoice_id": "MC-5091",
            "amount": "$285,000.00",  # EXECUTIVE THRESHOLD AUDIT (> $250k)
            "date": "2026-02-18",
            "po_number": "PO-77001",
            "department": "Manufacturing Operations",
            "category": "Raw Materials",
            "status": "PENDING_APPROVAL",
        },
        {
            "vendor_name": "Nexus Software Corp",
            "invoice_id": "NEX-4401",
            "amount": "($3,200.00)",  # NEGATIVE AMOUNT (Accounting parenthesis)
            "date": "2026-02-19",
            "po_number": "PO-55120",
            "department": "Marketing",
            "category": "Software Subscriptions",
            "description": "Quarterly Rebate Credit",  # Recognized Credit Memo
            "status": "CREDIT_MEMO",
        },
        {
            "vendor_name": "Apex Cloud Systems",
            "invoice_id": "ACS-8812",
            "amount": "$15,000.00",  # ARTIFICIAL ROUND NUMBER
            "date": "2026-02-20",
            "po_number": "PO-33019",
            "department": "IT Operations",
            "uptime": "98.80%",  # SLA BREACH (< 99.5%)
            "sla_target": "99.90%",
            "status": "DISPUTED",
        },
        {
            "vendor_name": "Apex Cloud Systems",
            "invoice_id": "ACS-8819",
            "amount": "$15,000.00",  # SUSPECTED DUPLICATE DISBURSEMENT ($15k to same vendor)
            "date": "2026-02-22",
            "po_number": "PO-33019",
            "department": "IT Operations",
            "uptime": "99.95%",
            "status": "PAID",
        },
        # --- Finance & Billing / Revenue Records ---
        {
            "client_name": "Enterprise Holdings Ltd",
            "invoice_id": "BILL-7701",
            "amount": "$84,000.00",
            "date": "2026-02-21",
            "department": "Enterprise Consulting",
            "category": "Professional Services",
            "status": "UNBILLED",  # UNBILLED WIP
        },
        {
            "client_name": "Fintech Global Inc",
            "invoice_id": "BILL-7702",
            "amount": "$120,500.00",
            "date": "2026-02-22",
            "department": "Enterprise Consulting",
            "category": "SaaS Platform",
            "status": "BILLED",
        },
        {
            "client_name": "Summit Health Systems",
            "invoice_id": "BILL-7703",
            "amount": "$62,300.00",
            "date": "2026-02-23",
            "department": "Healthcare Solutions",
            "category": "SaaS Platform",
            "status": "DISPUTED",  # DISPUTED RECEIVABLE
        },
        # --- Extreme Statistical Outlier ($1,850,000 transaction) ---
        {
            "vendor_name": "Titan Heavy Machinery AG",
            "invoice_id": "TITAN-900",
            "amount": "$1,850,000.00",  # STATISTICAL Z-SCORE OUTLIER
            "date": "2026-02-24",
            "po_number": "PO-10099",
            "department": "Capital Expenditures",
            "category": "Heavy Machinery",
            "status": "APPROVED",
        },
        # --- Standard Routine Transactions ---
        {
            "vendor_name": "Staples Office Supplies",
            "invoice_id": "STP-101",
            "amount": "$450.25",
            "date": "2026-02-24",
            "po_number": "PO-40011",
            "department": "General Administration",
            "category": "Office Supplies",
            "status": "PAID",
        },
        {
            "vendor_name": "Slack Technologies",
            "invoice_id": "SLK-992",
            "amount": "$2,400.00",
            "date": "2026-02-25",
            "po_number": "PO-40012",
            "department": "IT Operations",
            "category": "Collaboration Tools",
            "status": "PAID",
        },
        {
            "vendor_name": "Zoom Video Communications",
            "invoice_id": "ZM-881",
            "amount": "$1,800.00",
            "date": "2026-02-25",
            "po_number": "PO-40013",
            "department": "IT Operations",
            "category": "Video Conferencing",
            "status": "PAID",
        },
    ]

