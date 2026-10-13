from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    ANALYZING = "ANALYZING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    FAILED = "FAILED"


class DocumentType(str, Enum):
    CONTRACT = "contract"
    NDA = "nda"
    MSA = "msa"
    SLA = "sla"
    LEASE = "lease"
    INVOICE = "invoice"
    OTHER = "other"


class BoundingBox(BaseModel):
    """Normalized coordinates [0.0 - 1.0] or pt coordinates on PDF page."""
    x0: float
    y0: float
    x1: float
    y1: float
    page: int


class TextBlock(BaseModel):
    """Text block extracted from PDF with spatial coordinates."""
    text: str
    page: int
    bbox: Optional[BoundingBox] = None


class PageContent(BaseModel):
    """Page extracted content."""
    page_number: int
    raw_text: str
    blocks: List[TextBlock] = Field(default_factory=list)
    tables: List[List[List[Optional[str]]]] = Field(default_factory=list)


class ParsedDocument(BaseModel):
    """Document layout and text content after parsing."""
    file_name: str
    file_hash: str
    page_count: int
    full_text: str
    pages: List[PageContent]
    metadata: Dict[str, Any] = Field(default_factory=dict)

