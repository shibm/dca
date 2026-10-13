import os
import hashlib
from typing import List, Optional
import pdfplumber
from pypdf import PdfReader

from app.schemas.document import ParsedDocument, PageContent, TextBlock, BoundingBox


class PDFParser:
    """Extracts text, layout coordinates, and metadata from PDF files."""

    def __init__(self, extract_tables: bool = True, normalize_coords: bool = True):
        self.extract_tables = extract_tables
        self.normalize_coords = normalize_coords

    def compute_sha256(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of document."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def parse(self, file_path: str) -> ParsedDocument:
        """Parse PDF document and return layout-aware content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        file_name = os.path.basename(file_path)
        file_hash = self.compute_sha256(file_path)
        pages_content: List[PageContent] = []
        all_text_chunks: List[str] = []

        try:
            # Use pdfplumber for layout, text coordinates, and tables
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages, start=1):
                    raw_text = page.extract_text() or ""
                    page_width = float(page.width)
                    page_height = float(page.height)
                    
                    blocks: List[TextBlock] = []
                    # Extract words with layout bounding boxes
                    words = page.extract_words(keep_blank_chars=False)
                    for word in words:
                        x0 = float(word.get("x0", 0))
                        top = float(word.get("top", 0))
                        x1 = float(word.get("x1", 0))
                        bottom = float(word.get("bottom", 0))

                        # Normalize coordinates between 0.0 and 1.0 if requested
                        if self.normalize_coords and page_width > 0 and page_height > 0:
                            bbox = BoundingBox(
                                x0=round(x0 / page_width, 4),
                                y0=round(top / page_height, 4),
                                x1=round(x1 / page_width, 4),
                                y1=round(bottom / page_height, 4),
                                page=idx
                            )
                        else:
                            bbox = BoundingBox(
                                x0=round(x0, 2),
                                y0=round(top, 2),
                                x1=round(x1, 2),
                                y1=round(bottom, 2),
                                page=idx
                            )

                        blocks.append(TextBlock(
                            text=word.get("text", ""),
                            page=idx,
                            bbox=bbox
                        ))

                    tables = []
                    if self.extract_tables:
                        try:
                            tables = page.extract_tables() or []
                        except Exception:
                            tables = []

                    pages_content.append(PageContent(
                        page_number=idx,
                        raw_text=raw_text.strip(),
                        blocks=blocks,
                        tables=tables
                    ))
                    all_text_chunks.append(f"--- PAGE {idx} ---\n" + raw_text.strip())

        except Exception as e:
            # Fallback to pure pypdf if pdfplumber fails on non-standard PDF formats
            pages_content = self._fallback_pypdf(file_path)
            all_text_chunks = [f"--- PAGE {p.page_number} ---\n{p.raw_text}" for p in pages_content]

        full_text = "\n\n".join(all_text_chunks)
        page_count = len(pages_content)

        return ParsedDocument(
            file_name=file_name,
            file_hash=file_hash,
            page_count=page_count,
            full_text=full_text,
            pages=pages_content,
            metadata={
                "file_size_bytes": os.path.getsize(file_path),
                "is_empty": len(full_text.strip()) == 0
            }
        )

    def _fallback_pypdf(self, file_path: str) -> List[PageContent]:
        """Fallback lightweight text extractor."""
        reader = PdfReader(file_path)
        pages: List[PageContent] = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(PageContent(
                page_number=idx,
                raw_text=text.strip(),
                blocks=[],
                tables=[]
            ))
        return pages

