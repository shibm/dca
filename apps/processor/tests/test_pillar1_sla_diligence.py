import os
import pytest
from app.pipeline import ExtractionPipeline
from app.services.batch_processor import BatchProcessor

BATCH_DIR = "apps/processor/tests/contracts_batch"


def test_pillar1_sla_and_change_of_control():
    """Verify SLA uptime, service credit penalty, and Change of Control extraction."""
    pipeline = ExtractionPipeline()
    sla_pdf = os.path.join(BATCH_DIR, "01_CloudCore_Vendor_SLA.pdf")
    _, result = pipeline.process(sla_pdf)

    field_map = {f.key: f for f in result.fields}

    # Verify SLA extracted
    assert "uptime_sla" in field_map
    assert "99.95%" in str(field_map["uptime_sla"].value)

    # Verify Change of Control detected
    assert "change_of_control" in field_map
    assert "Requires Vendor Consent" in str(field_map["change_of_control"].value)


def test_pillar1_critical_acquisition_risk():
    """Verify acquisition termination right and early termination penalty extraction."""
    pipeline = ExtractionPipeline()
    risk_pdf = os.path.join(BATCH_DIR, "02_DataStream_Critical_Risk.pdf")
    _, result = pipeline.process(risk_pdf)

    field_map = {f.key: f for f in result.fields}

    assert "change_of_control" in field_map
    assert "Vendor May Terminate Upon Acquisition" in str(field_map["change_of_control"].value)

    # Early termination fee
    assert "early_termination_penalty" in field_map
    assert "50,000" in str(field_map["early_termination_penalty"].value)

    # Critical risk flags
    assert any("M&A Critical" in flag or "Financial Liability" in flag for flag in result.flags)
    assert result.requires_human_review is True


def test_pillar1_batch_diligence_rollup():
    """Verify batch rollup metrics across all vendor contracts."""
    processor = BatchProcessor(max_workers=2)
    report = processor.process_directory(BATCH_DIR)

    assert report.total_contracts == 3
    assert report.total_financial_exposure == 755000.00
    assert report.change_of_control_risk_count == 2
    assert report.acquisition_termination_rights_count == 1
    assert report.high_risk_contracts_count >= 1

    # Ensure contracts are sorted by risk score descending
    assert report.contracts[0].diligence_risk_score >= report.contracts[-1].diligence_risk_score

