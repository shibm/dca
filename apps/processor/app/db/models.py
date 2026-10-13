import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    BigInteger,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="reviewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(Text, nullable=False)
    file_hash = Column(String(64), nullable=False)
    mime_type = Column(String(100), default="application/pdf")
    page_count = Column(Integer, default=0)
    document_type = Column(String(100), default="contract")
    status = Column(String(50), default="UPLOADED")  # UPLOADED, PARSING, ANALYZING, NEEDS_REVIEW, APPROVED, FAILED
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    layout_data = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    document = relationship("Document", back_populates="pages")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_key = Column(String(100), nullable=False)
    field_label = Column(String(150), nullable=False)
    field_value = Column(Text, nullable=True)
    field_category = Column(String(100), default="general")
    data_type = Column(String(50), default="string")
    confidence_score = Column(Numeric(5, 4), default=1.0)
    source_page = Column(Integer, nullable=True)
    source_quote = Column(Text, nullable=True)
    source_bounding_box = Column(JSONB, nullable=True)
    is_corrected = Column(Boolean, default=False)
    validation_status = Column(String(50), default="VALID")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    document = relationship("Document", back_populates="extractions")
    audit_logs = relationship("ExtractionAuditLog", back_populates="extraction", cascade="all, delete-orphan")


class ExtractionAuditLog(Base):
    __tablename__ = "extraction_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("document_extractions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    corrected_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    extraction = relationship("DocumentExtraction", back_populates="audit_logs")

