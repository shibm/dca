import uuid
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentPage, DocumentExtraction, ExtractionAuditLog
from app.schemas.document import ParsedDocument
from app.schemas.extraction import ExtractionResult

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Handles database persistence for documents, pages, and AI extractions."""

    def __init__(self, db: Session):
        self.db = db

    def update_document_status(self, document_id: str, status: str, error_message: Optional[str] = None):
        """Update processing status of a document."""
        doc = self.db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
        if doc:
            doc.status = status
            if error_message:
                doc.error_message = error_message
            self.db.commit()

    def save_parsed_pages(self, document_id: str, parsed_doc: ParsedDocument):
        """Persist extracted text and layout coordinates per page."""
        doc_uuid = uuid.UUID(document_id)
        doc = self.db.query(Document).filter(Document.id == doc_uuid).first()
        if doc:
            doc.page_count = parsed_doc.page_count
            doc.file_hash = parsed_doc.file_hash

        # Remove existing pages if reprocessing
        self.db.query(DocumentPage).filter(DocumentPage.document_id == doc_uuid).delete()

        for page in parsed_doc.pages:
            db_page = DocumentPage(
                document_id=doc_uuid,
                page_number=page.page_number,
                raw_text=page.raw_text,
                layout_data={
                    "blocks_count": len(page.blocks),
                    "has_tables": len(page.tables) > 0,
                    "tables": page.tables
                }
            )
            self.db.add(db_page)
        self.db.commit()

    def save_extractions(self, document_id: str, result: ExtractionResult):
        """Persist extracted fields, confidence scores, and bounding boxes."""
        doc_uuid = uuid.UUID(document_id)
        doc = self.db.query(Document).filter(Document.id == doc_uuid).first()

        # Update document classification and status
        if doc:
            doc.document_type = result.document_type
            doc.status = "NEEDS_REVIEW" if result.requires_human_review else "READY"
            doc.metadata_ = {
                "overall_confidence": result.overall_confidence,
                "processing_time_ms": result.processing_time_ms,
                "flags": result.flags
            }

        # Clear old extractions if reprocessing
        self.db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc_uuid).delete()

        for field in result.fields:
            bbox_dict = field.bounding_box.model_dump() if field.bounding_box else None
            db_ext = DocumentExtraction(
                document_id=doc_uuid,
                field_key=field.key,
                field_label=field.label,
                field_value=str(field.value) if field.value is not None else None,
                field_category=field.category,
                data_type=field.data_type,
                confidence_score=field.confidence,
                source_page=field.source_page,
                source_quote=field.source_quote,
                source_bounding_box=bbox_dict,
                validation_status=field.validation_status
            )
            self.db.add(db_ext)

        self.db.commit()
        logger.info(f"Persisted {len(result.fields)} extractions for document {document_id}")

