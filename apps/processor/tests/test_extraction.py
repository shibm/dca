import os
import pytest
from app.parsers.pdf_parser import PDFParser
from app.ai.guardrails import ExtractionGuardrails
from app.pipeline import ExtractionPipeline
from app.schemas.contract import (
    StructuredContractOutput,
    Party,
    ContractDates,
    FinancialTerms,
    LegalClauses,
    ContractRisk
)

SAMPLE_PDF_PATH = "apps/processor/tests/sample_contract.pdf"


def test_pdf_parser():
    """Verify layout and text extraction from sample contract."""
    parser = PDFParser(extract_tables=True, normalize_coords=True)
    doc = parser.parse(SAMPLE_PDF_PATH)

    assert doc.page_count == 2
    assert len(doc.file_hash) == 64
    assert "MASTER SERVICES AGREEMENT" in doc.full_text
    assert "Acme Global Technologies Inc." in doc.full_text
    assert "Apex Cloud Solutions LLC" in doc.full_text

    # Verify bounding boxes exist for extracted words
    page_1 = doc.pages[0]
    assert len(page_1.blocks) > 0
    assert page_1.blocks[0].bbox is not None
    assert 0.0 <= page_1.blocks[0].bbox.x0 <= 1.0


def test_guardrails_grounding_and_validation():
    """Verify that quotes are verified against source text and dates validated."""
    parser = PDFParser()
    doc = parser.parse(SAMPLE_PDF_PATH)
    guardrails = ExtractionGuardrails(confidence_threshold=0.75)

    # Grounded quote
    is_grounded, bbox = guardrails.verify_grounding("Delaware", 2, doc)
    assert is_grounded is True

    # Hallucinated quote
    is_hallucinated, _ = guardrails.verify_grounding("Fictional Non-existent Clause 999", 1, doc)
    assert is_hallucinated is False

    # Date validation
    valid, _ = guardrails.validate_dates("2026-10-15", "2027-10-14")
    assert valid is True

    invalid, err = guardrails.validate_dates("2027-10-15", "2026-10-14")
    assert invalid is False
    assert "cannot be after" in err


def test_extraction_pipeline_end_to_end():
    """Verify complete extraction pipeline with mock AI provider."""
    pipeline = ExtractionPipeline()
    parsed_doc, result = pipeline.process(SAMPLE_PDF_PATH)

    assert result.document_type in ["contract", "msa"]
    assert result.overall_confidence > 0.70
    assert len(result.fields) > 5

    field_map = {f.key: f for f in result.fields}
    assert "title" in field_map
    assert "effective_date" in field_map
    assert "total_contract_value" in field_map
    assert "governing_law" in field_map

    # Ensure parties were extracted
    assert any("party" in k for k in field_map.keys())

    # Check high-risk detection (unlimited liability in sample)
    assert any("Unlimited Liability" in flag or "Risk" in flag for flag in result.flags)

