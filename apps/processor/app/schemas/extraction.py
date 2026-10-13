from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from app.schemas.document import BoundingBox


class ExtractedField(BaseModel):
    """Normalized field model for storage, validation, and HITL review."""
    key: str
    label: str
    value: Optional[Any] = None
    data_type: str = "string"  # "string", "date", "currency", "number", "boolean", "list"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_page: Optional[int] = None
    source_quote: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    category: str = "general"  # "parties", "dates", "financial", "legal", "risk"
    validation_status: str = "VALID"  # "VALID", "WARNING", "INVALID", "NEEDS_VERIFICATION"
    validation_notes: Optional[str] = None


class ExtractionResult(BaseModel):
    """Aggregate result from the parsing and AI extraction pipeline."""
    document_id: Optional[str] = None
    document_type: str = "contract"
    fields: List[ExtractedField] = Field(default_factory=list)
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    flags: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    processing_time_ms: int = 0
    raw_ai_response: Optional[Dict[str, Any]] = None

