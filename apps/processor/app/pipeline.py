import time
import logging
from typing import Tuple, Optional

from app.config import settings
from app.schemas.document import ParsedDocument
from app.schemas.extraction import ExtractionResult
from app.parsers.pdf_parser import PDFParser
from app.ai.llm_client import get_llm_client, BaseLLMClient
from app.ai.guardrails import ExtractionGuardrails

logger = logging.getLogger(__name__)


class ExtractionPipeline:
    """Orchestrates PDF layout parsing, LLM structured extraction, and guardrail validation."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.parser = PDFParser(extract_tables=True, normalize_coords=True)
        self.llm_client = llm_client or get_llm_client(
            provider=settings.AI_PROVIDER,
            gemini_key=settings.GEMINI_API_KEY,
            openai_key=settings.OPENAI_API_KEY,
            model_name=settings.AI_MODEL_NAME
        )
        self.guardrails = ExtractionGuardrails(confidence_threshold=settings.CONFIDENCE_THRESHOLD)

    def process(self, file_path: str, document_id: Optional[str] = None) -> Tuple[ParsedDocument, ExtractionResult]:
        """Execute end-to-end extraction on a PDF document."""
        start_time = time.time()
        logger.info(f"Starting extraction pipeline for file: {file_path}")

        # Step 1: Layout-aware PDF text and coordinate parsing
        parsed_doc = self.parser.parse(file_path)
        logger.info(f"Parsed {parsed_doc.page_count} pages, {len(parsed_doc.full_text)} chars.")

        # Step 2: AI-Powered Entity & Clause Extraction
        raw_structured_output = self.llm_client.extract(parsed_doc)

        # Step 3: Guardrails, Grounding Verification & Confidence Scoring
        extraction_result = self.guardrails.process_and_validate(raw_structured_output, parsed_doc)
        extraction_result.document_id = document_id
        extraction_result.processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Extraction completed in {extraction_result.processing_time_ms}ms with "
            f"confidence {extraction_result.overall_confidence:.1%}. "
            f"Requires review: {extraction_result.requires_human_review}"
        )

        return parsed_doc, extraction_result

