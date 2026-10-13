"""Unit and integration tests for Pillar 4: Batch Data Automation & Python Script Execution Framework."""

from __future__ import annotations
import pytest
from app.schemas.automation import AutomationJobRequest, BusinessRule
from app.automation.normalizer import DataNormalizer, parse_clean_amount, parse_clean_date
from app.automation.rule_engine import BusinessRuleEngine
from app.automation.script_registry import REGISTRY
from app.automation.engine import AutomationEngine, generate_benchmark_multi_department_dataset


def test_data_normalizer_column_mapping_and_cleaning():
    """Verify disparate column headers, currencies, dates, and deduplication."""
    raw_dataset = [
        {
            "Supplier Name": "AWS Cloud Services LLC",
            "invoice_no": "INV-2026-9011",
            "invoice_amount": "$45,200.00",
            "date": "2026-02-14",
            "PO#": "PO-99120",
        },
        {
            "vendor": "AWS Cloud Services LLC",
            "inv_num": "INV-2026-9011",  # EXACT DUPLICATE
            "amt": "$45,200.00",
            "txn_date": "2026-02-14",
            "po": "PO-99120",
        },
        {
            "company_name": "Apex Hardware Direct",
            "doc_id": "INV-8820",
            "Total Price": "($3,450.50)",  # Negative currency
            "Billing Date": "02/15/2026",
            "PO#": "PO-55100",
        },
    ]

    normalizer = DataNormalizer()
    cleaned, anomalies, dup_count = normalizer.process_dataset(raw_dataset)

    assert len(cleaned) == 3
    assert dup_count == 1
    assert cleaned[0]["vendor_name"] == "AWS Cloud Services LLC"
    assert cleaned[0]["invoice_id"] == "INV-2026-9011"
    assert cleaned[0]["amount"] == 45200.0
    assert cleaned[0]["date"] == "2026-02-14"
    assert cleaned[0]["_is_duplicate"] is False

    # Second record is duplicate
    assert cleaned[1]["_is_duplicate"] is True
    assert cleaned[1]["_duplicate_of_index"] == 0

    # Third record has negative parsed amount and converted date
    assert cleaned[2]["amount"] == -3450.50
    assert cleaned[2]["date"] == "2026-02-15"


def test_business_rule_engine():
    """Verify enterprise business rule triggers (Maverick spend, Executive threshold, unclassified credit)."""
    engine = BusinessRuleEngine()
    test_records = [
        {
            "invoice_id": "INV-1",
            "vendor_name": "Unapproved Vendor",
            "amount": 25000.0,
            "po_number": "",  # Missing PO on > $10k -> MAVERICK SPEND
        },
        {
            "invoice_id": "INV-2",
            "vendor_name": "Mega Machinery",
            "amount": 500000.0,  # > $250k -> EXECUTIVE THRESHOLD AUDIT
            "po_number": "PO-99123",
        },
        {
            "invoice_id": "INV-3",
            "vendor_name": "Widget Supplies",
            "amount": -500.0,
            "status": "PENDING",  # Negative amount without credit memo status
        },
    ]

    anomalies = engine.evaluate_rules(test_records)
    rule_types = [a.anomaly_type for a in anomalies]

    assert "MISSING_MANDATORY_FIELD" in rule_types
    assert "THRESHOLD_VIOLATION" in rule_types
    assert "CROSS_FIELD_INCONSISTENCY" in rule_types


def test_statistical_zscore_and_outlier_detection():
    """Verify Z-score outlier detection on amounts."""
    engine = BusinessRuleEngine()
    # 9 normal transactions ($1,000 to $5,000) and 1 extreme outlier ($2,000,000)
    records = [{"invoice_id": f"INV-{i}", "amount": float(1000 + i * 400)} for i in range(9)]
    records.append({"invoice_id": "INV-EXTREME", "amount": 2000000.0})

    anomalies, stats = engine.detect_statistical_anomalies(records, field="amount", z_threshold=2.5)

    assert len(anomalies) >= 1
    outlier = anomalies[0]
    assert outlier.record_id == "INV-EXTREME"
    assert outlier.anomaly_type == "Z_SCORE_OUTLIER"
    assert outlier.z_score is not None
    assert outlier.z_score > 2.5
    assert stats["max"] == 2000000.0


def test_procurement_and_sla_specialized_scripts():
    """Verify specialized domain scripts compute accurate domain metrics."""
    # 1. Procurement spend audit
    sample_records = [
        {"vendor_name": "Apex Cloud", "amount": 100000.0, "po_number": "PO-1"},
        {"vendor_name": "Apex Cloud", "amount": 25000.0, "po_number": ""},  # Maverick spend
        {"vendor_name": "Apex Cloud", "amount": 25000.0, "po_number": ""},  # Duplicate disbursement
        {"vendor_name": "Vendor B", "amount": 10000.0, "po_number": "PO-2"},
    ]
    anom, insights, metrics = REGISTRY.execute_script("procurement_spend_audit", sample_records)[:3]
    assert metrics["total_spend"] == 160000.0
    assert metrics["maverick_spend_total"] == 50000.0
    assert metrics["suspected_duplicate_amount"] == 25000.0
    assert len(insights) >= 2

    # 2. Vendor SLA penalty calculation
    sla_records = [
        {"vendor_name": "FastDelivery LLC", "amount": 5000.0, "delay_days": 4},
        {"vendor_name": "CloudPlatform", "amount": 20000.0, "uptime": "98.0%", "sla_target": "99.5%"},
    ]
    sla_anom, sla_insights, sla_metrics = REGISTRY.execute_script(
        "vendor_sla_penalty_calculator", sla_records, {"daily_delay_fine": 500.0}
    )[:3]
    assert sla_metrics["total_sla_breaches"] == 2
    assert sla_metrics["total_clawbacks_due"] > 0


def test_end_to_end_automation_job():
    """Verify end-to-end execution of AutomationEngine on multi-department benchmark data."""
    raw_data = generate_benchmark_multi_department_dataset()
    engine = AutomationEngine()

    request = AutomationJobRequest(
        job_id="test-job-001",
        script_ids=[
            "procurement_spend_audit",
            "revenue_billing_reconciliation",
            "vendor_sla_penalty_calculator",
            "statistical_anomaly_detector",
        ],
        raw_records=raw_data,
    )

    result = engine.run_job(request)

    assert result.status == "COMPLETED"
    assert result.total_records_ingested == len(raw_data)
    assert result.duplicates_detected >= 1
    assert result.anomalies_count >= 5
    assert result.critical_anomalies_count >= 1
    assert len(result.insights) >= 4
    assert len(result.script_logs) == 4
    assert all(log.status == "SUCCESS" for log in result.script_logs)
    assert result.execution_time_ms > 0
    assert len(result.sample_cleaned_records) > 0

