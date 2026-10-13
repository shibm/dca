"""Semantic text chunker with page boundary and legal clause preservation."""

from __future__ import annotations
import re
from typing import List, Optional
from app.schemas.workspace import DocumentChunk


SECTION_CLAUSE_REGEX = re.compile(
    r"(?:Section|Article|Clause|\bPart)\s+([0-9A-Za-z\.\-_]+)(?::|\s+[-–—]\s+|\s+)([^\n\.\,]+)",
    re.IGNORECASE,
)


class DocumentChunker:
    """Splits document pages into context-rich semantic chunks with citation metadata."""

    def __init__(self, chunk_size: int = 450, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        workspace_id: str,
        document_name: str,
        pages_text: List[str],
        document_id: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """
        Chunk pages of text into DocumentChunk objects.
        pages_text is a 0-indexed list where index 0 is page 1.
        """
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for page_num_0, text in enumerate(pages_text):
            page_number = page_num_0 + 1
            if not text or not text.strip():
                continue

            # Detect dominant section/clause on this page
            page_clause: Optional[str] = None
            clause_match = SECTION_CLAUSE_REGEX.search(text)
            if clause_match:
                page_clause = f"Section {clause_match.group(1)}: {clause_match.group(2).strip()}"

            # Split page text into paragraphs or sentences
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [text.strip()]

            current_chunk_text = ""
            current_clause = page_clause

            for para in paragraphs:
                # Check for inline clause header
                p_match = SECTION_CLAUSE_REGEX.search(para)
                if p_match:
                    current_clause = f"Section {p_match.group(1)}: {p_match.group(2).strip()}"

                if len(current_chunk_text) + len(para) <= self.chunk_size:
                    current_chunk_text = f"{current_chunk_text}\n\n{para}".strip()
                else:
                    if current_chunk_text:
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"chunk-{document_id or 'doc'}-p{page_number}-{chunk_idx}",
                                workspace_id=workspace_id,
                                document_id=document_id,
                                document_name=document_name,
                                chunk_index=chunk_idx,
                                page_number=page_number,
                                clause_reference=current_clause,
                                text_content=current_chunk_text,
                                token_count=len(current_chunk_text.split()),
                            )
                        )
                        chunk_idx += 1

                    # Start next chunk with overlap or fresh paragraph
                    current_chunk_text = para

            if current_chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chunk-{document_id or 'doc'}-p{page_number}-{chunk_idx}",
                        workspace_id=workspace_id,
                        document_id=document_id,
                        document_name=document_name,
                        chunk_index=chunk_idx,
                        page_number=page_number,
                        clause_reference=current_clause,
                        text_content=current_chunk_text,
                        token_count=len(current_chunk_text.split()),
                    )
                )
                chunk_idx += 1

        return chunks

