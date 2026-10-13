"""Unit and integration tests for Pillar 5: Intelligent Workspace & Knowledge Brain (RAG)."""

from __future__ import annotations
import pytest
from app.rag.chunker import DocumentChunker
from app.rag.vector_store import WorkspaceVectorStore
from app.rag.rag_engine import RAGEngine
from app.schemas.workspace import RAGQueryRequest


def test_document_chunker_with_clause_detection():
    """Verify chunker detects section clauses and preserves page boundaries."""
    chunker = DocumentChunker(chunk_size=300, chunk_overlap=30)
    pages = [
        "MASTER SERVICES AGREEMENT\n\nSection 1.1: Scope of Work. Vendor will provide cloud hosting services.",
        "Section 4.2: Service Level Commitments. Vendor commits to 99.9% uptime. Failure results in a 10% penalty credit.",
    ]

    chunks = chunker.chunk_document(
        workspace_id="test-ws-1",
        document_name="Test_Contract.pdf",
        pages_text=pages,
        document_id="doc-001",
    )

    assert len(chunks) >= 2
    # Verify page numbers
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2
    # Verify clause detection
    assert chunks[1].clause_reference is not None
    assert "Section 4.2" in chunks[1].clause_reference
    assert "Service Level Commitments" in chunks[1].clause_reference


def test_vector_store_indexing_and_hybrid_search():
    """Verify hybrid search ranks semantically and lexically relevant chunks."""
    store = WorkspaceVectorStore()
    chunker = DocumentChunker()

    doc_a = [
        "Section 8.1: Indemnification and Unlimited Liability. Vendor accepts unlimited liability for data breaches.",
        "Section 12.0: Governing Law. This contract is governed by the laws of Delaware.",
    ]
    chunks = chunker.chunk_document("ws-alpha", "Vendor_Agreement.pdf", doc_a)
    store.add_chunks("ws-alpha", chunks)

    results = store.search("ws-alpha", "unlimited liability data breach", top_k=2)

    assert len(results) > 0
    top = results[0]
    assert "unlimited liability" in top.text_content.lower()
    assert top.score is not None
    assert top.score > 0.3


def test_workspace_isolation():
    """Verify strict tenant isolation: Workspace A chunks never appear in Workspace B."""
    store = WorkspaceVectorStore()
    chunker = DocumentChunker()

    # Workspace A: Healthcare records
    ws_a_pages = ["Confidential clinical trial protocol for Cancer Drug CT-990."]
    store.add_chunks("ws-healthcare", chunker.chunk_document("ws-healthcare", "Trial.pdf", ws_a_pages))

    # Workspace B: Financial records
    ws_b_pages = ["Q4 Consolidated balance sheet and cash flow report."]
    store.add_chunks("ws-finance", chunker.chunk_document("ws-finance", "BalanceSheet.pdf", ws_b_pages))

    # Search in ws-finance for clinical trial
    results_in_b = store.search("ws-finance", "Cancer Drug CT-990", top_k=5)
    assert len(results_in_b) == 0 or all("CT-990" not in r.text_content for r in results_in_b)

    # Search in ws-healthcare for balance sheet
    results_in_a = store.search("ws-healthcare", "Consolidated balance sheet", top_k=5)
    assert len(results_in_a) == 0 or all("balance sheet" not in r.text_content.lower() for r in results_in_a)


def test_rag_engine_grounded_answer_and_citations():
    """Verify RAG engine answers questions with verifiable document and page citations."""
    engine = RAGEngine()

    req = RAGQueryRequest(
        workspace_id="ws-project-apollo",
        query="What are the SLA uptime commitments and penalty terms?",
        top_k=3,
    )

    res = engine.query_workspace(req)

    assert res.workspace_id == "ws-project-apollo"
    assert len(res.answer) > 20
    assert res.retrieved_chunks_count > 0
    assert len(res.citations) > 0

    # Every citation must include document_name, page_number >= 1, and verbatim_quote
    for cite in res.citations:
        assert cite.document_name != ""
        assert cite.page_number >= 1
        assert len(cite.verbatim_quote) > 5


def test_conversation_thread_persistence():
    """Verify multi-turn conversations persist messages and conversation thread."""
    engine = RAGEngine()

    # Turn 1
    req1 = RAGQueryRequest(
        workspace_id="ws-project-apollo",
        query="Are there any change of control risks?",
    )
    res1 = engine.query_workspace(req1)
    conv_id = res1.conversation_id

    # Turn 2 in the same thread
    req2 = RAGQueryRequest(
        workspace_id="ws-project-apollo",
        query="Which vendors require consent prior to acquisition?",
        conversation_id=conv_id,
    )
    res2 = engine.query_workspace(req2)

    assert res2.conversation_id == conv_id

    thread = engine.get_conversation(conv_id)
    assert thread is not None
    # 2 user messages + 2 assistant responses = 4 messages
    assert len(thread.messages) == 4
    assert thread.messages[0].role == "user"
    assert thread.messages[1].role == "assistant"
    assert thread.messages[2].role == "user"
    assert thread.messages[3].role == "assistant"

