"""Pydantic schemas for Pillar 5: Intelligent Workspace & Organizational Knowledge Brain (RAG)."""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class WorkspaceMember(BaseModel):
    user_id: str
    name: str
    email: str
    role: Literal["OWNER", "PARTNER", "SENIOR_ANALYST", "EDITOR", "VIEWER"] = "EDITOR"


class Workspace(BaseModel):
    workspace_id: str
    name: str
    client_name: str
    description: str
    industry: str = "General Corporate"
    status: Literal["ACTIVE", "ARCHIVED"] = "ACTIVE"
    document_count: int = 0
    members: List[WorkspaceMember] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: str


class DocumentChunk(BaseModel):
    chunk_id: str
    workspace_id: str
    document_id: Optional[str] = None
    document_name: str
    chunk_index: int
    page_number: int
    clause_reference: Optional[str] = None
    text_content: str
    token_count: int = 0
    score: Optional[float] = None


class Citation(BaseModel):
    document_id: Optional[str] = None
    document_name: str
    page_number: int
    clause_reference: Optional[str] = None
    verbatim_quote: str
    relevance_score: float = 0.95


class ChatMessage(BaseModel):
    message_id: str
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    citations: List[Citation] = Field(default_factory=list)
    created_at: str


class ConversationThread(BaseModel):
    conversation_id: str
    workspace_id: str
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: str


class RAGQueryRequest(BaseModel):
    workspace_id: str
    query: str
    conversation_id: Optional[str] = None
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class RAGQueryResponse(BaseModel):
    workspace_id: str
    conversation_id: str
    query: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    retrieved_chunks_count: int
    execution_time_ms: float

