import os
import sys
import argparse
import tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.pipeline import ExtractionPipeline
from app.schemas.extraction import ExtractionResult

app = FastAPI(
    title="DCA Document Extraction Service",
    description="Heavy PDF parsing and AI-powered contract analysis engine",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = ExtractionPipeline()


from app.services.batch_processor import BatchProcessor, MADiligenceRollupReport

batch_processor = BatchProcessor(max_workers=4)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "dca-processor",
        "ai_provider": settings.AI_PROVIDER,
        "env": settings.ENV
    }


@app.post("/extract", response_model=ExtractionResult)
async def extract_pdf(file: UploadFile = File(...)):
    """Extract structured data from an uploaded PDF file."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        _, result = pipeline.process(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/extract-batch", response_model=MADiligenceRollupReport)
async def extract_batch_endpoint(directory: str):
    """Run bulk contract diligence across a directory of PDFs for Pillar 1."""
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail=f"Directory not found: {directory}")

    try:
        report = batch_processor.process_directory(directory)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


def run_cli():
    """Command-line interface to test extraction on local files or batches."""
    parser = argparse.ArgumentParser(description="DCA PDF Extraction CLI")
    parser.add_argument("--file", "-f", help="Path to single PDF file")
    parser.add_argument("--batch", "-b", help="Path to directory containing batch of PDF contracts")
    parser.add_argument("--provider", "-p", default="mock", help="AI provider (mock, gemini, openai)")
    args = parser.parse_args()

    if args.batch:
        if not os.path.isdir(args.batch):
            print(f"Error: Directory not found at {args.batch}")
            sys.exit(1)

        print(f"\n=======================================================")
        print(f"🏛️  M&A VENDOR SLA & DILIGENCE ROLLUP: {args.batch}")
        print(f"=======================================================\n")
        report = batch_processor.process_directory(args.batch)

        print(f"Total Contracts Analyzed:         {report.total_contracts}")
        print(f"Total Financial Exposure:         ${report.total_financial_exposure:,.2f}")
        print(f"Change of Control Risks:          {report.change_of_control_risk_count} contract(s)")
        print(f"Acquisition Termination Rights:   {report.acquisition_termination_rights_count} contract(s)")
        print(f"Upcoming Renewals (< 90 days):    {report.upcoming_renewals_count} contract(s)")
        print(f"Average Portfolio Risk Score:     {report.average_risk_score}/100")
        print(f"High/Critical Risk Contracts:     {report.high_risk_contracts_count}\n")

        print(f"{'CONTRACT': <35} {'TYPE': <8} {'VALUE': <14} {'SLA': <10} {'COC RISK': <12} {'RISK SCORE'}")
        print("-" * 92)
        for c in report.contracts:
            val_str = f"${c.total_value:,.0f}" if c.total_value else "N/A"
            coc_str = "YES" if (c.requires_consent_on_acquisition or c.vendor_termination_on_acquisition) else "No"
            print(f"{c.file_name[:34]: <35} {c.document_type: <8} {val_str: <14} {str(c.uptime_sla or 'N/A'): <10} {coc_str: <12} {c.diligence_risk_score}/100")

        return

    if not args.file:
        print("Error: Specify either --file <pdf_path> or --batch <directory>")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}")
        sys.exit(1)

    print(f"=== Extracting Document: {args.file} ===")
    pipe = ExtractionPipeline()
    parsed_doc, result = pipe.process(args.file)

    print(f"\nDocument Title: {result.fields[0].value if result.fields else 'N/A'}")
    print(f"Document Type:  {result.document_type}")
    print(f"Overall Conf:   {result.overall_confidence:.1%}")
    print(f"Review Needed:  {result.requires_human_review}")
    print(f"Processing:     {result.processing_time_ms} ms\n")

    print("--- Extracted Fields ---")
    for f in result.fields:
        status_symbol = "✓" if f.validation_status == "VALID" else "⚠"
        print(f"[{status_symbol}] {f.label: <32}: {str(f.value): <30} (Conf: {f.confidence:.0%})")
        if f.source_quote:
            print(f"    Source (P.{f.source_page}): \"{f.source_quote[:70]}...\"")

    if result.flags:
        print("\n--- Review Flags ---")
        for flag in result.flags:
            print(f"  • {flag}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and any(arg in sys.argv for arg in ["--file", "-f", "--batch", "-b"]):
        run_cli()
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PROCESSOR_PORT, reload=True)

