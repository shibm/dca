import os
import pytest
from app.parsers.pdf_parser import PDFParser
from app.ai.accounting_engine import TechnicalAccountingEngine
from app.schemas.accounting import AccountingStandard

CONTRACT_PATH = "apps/processor/tests/sample_contract.pdf"


def test_pillar3_accounting_memo_generation():
    """Verify ASC 606 5-step analysis and journal entry creation."""
    parser = PDFParser()
    parsed_doc = parser.parse(CONTRACT_PATH)

    engine = TechnicalAccountingEngine()
    memo = engine.analyze_contract(parsed_doc, standard=AccountingStandard.ASC_606)

    assert memo.contract_value == 175_000.0
    assert memo.currency == "USD"
    assert memo.accounting_standard == AccountingStandard.ASC_606
    assert "Acme Global Technologies" in memo.parties[0]
    assert memo.status == "DRAFT"

    # Step 2: Performance Obligations
    ppobs = memo.asc606_analysis.step2_performance_obligations
    assert len(ppobs) >= 1
    total_allocated = sum(p.allocated_transaction_price for p in ppobs)
    assert total_allocated == memo.contract_value

    # Verify Journal Entry Schedules are balanced
    assert len(memo.suggested_journal_entries) >= 2
    for je in memo.suggested_journal_entries:
        assert je.is_balanced is True
        assert round(je.total_debit, 2) == round(je.total_credit, 2)

    # Initial Invoicing Debit to Accounts Receivable
    je_initial = memo.suggested_journal_entries[0]
    ar_line = next(l for l in je_initial.lines if "Accounts Receivable" in l.account_name)
    assert ar_line.debit == 175_000.0


def test_pillar3_journal_entry_balancing_logic():
    """Verify that every debit line corresponds to a matching credit line in schedules."""
    parser = PDFParser()
    parsed_doc = parser.parse(CONTRACT_PATH)

    engine = TechnicalAccountingEngine()
    memo = engine.analyze_contract(parsed_doc)

    for schedule in memo.suggested_journal_entries:
        deb_sum = sum(line.debit or 0.0 for line in schedule.lines)
        cred_sum = sum(line.credit or 0.0 for line in schedule.lines)
        assert round(deb_sum, 2) == round(cred_sum, 2)

