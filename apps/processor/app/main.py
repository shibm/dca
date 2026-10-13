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


from app.services.portfolio_comparator import PortfolioComparator
from app.ai.financial_normalizer import FinancialNormalizer
from app.schemas.financials import NormalizedFinancialReport, MultiEntityComparisonReport

portfolio_comparator = PortfolioComparator(max_workers=4)
financial_normalizer = FinancialNormalizer()


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


@app.post("/extract-financials", response_model=NormalizedFinancialReport)
async def extract_financials_endpoint(file: UploadFile = File(...)):
    """Pillar 2: Extract normalized financial statements from single PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parsed = pipeline.parser.parse(tmp_path)
        report = financial_normalizer.normalize(tmp_path, parsed.full_text)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial normalization failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/compare-portfolio", response_model=MultiEntityComparisonReport)
async def compare_portfolio_endpoint(directory: str):
    """Pillar 2: Benchmark multi-entity financial performance across a portfolio folder."""
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail=f"Directory not found: {directory}")

    try:
        report = portfolio_comparator.compare_portfolio(directory)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio comparison failed: {str(e)}")


def run_cli():
    """Command-line interface to test contract diligence, financial normalization, or portfolio benchmarking."""
    parser = argparse.ArgumentParser(description="DCA Document Analysis CLI")
    parser.add_argument("--file", "-f", help="Path to single contract PDF file")
    parser.add_argument("--batch", "-b", help="Path to directory containing batch of PDF contracts (Pillar 1)")
    parser.add_argument("--financials", help="Path to single financial statement PDF (Pillar 2)")
    parser.add_argument("--compare-portfolio", help="Path to directory of portfolio company financial statements (Pillar 2)")
    parser.add_argument("--provider", "-p", default="mock", help="AI provider (mock, gemini, openai)")
    args = parser.parse_args()

    # Pillar 2: 30-Company Comparative Benchmarking
    if args.compare_portfolio:
        if not os.path.isdir(args.compare_portfolio):
            print(f"Error: Directory not found at {args.compare_portfolio}")
            sys.exit(1)

        print(f"\n==========================================================================")
        print(f"📊 PILLAR 2: MULTI-ENTITY PORTFOLIO FINANCIAL BENCHMARKING")
        print(f"==========================================================================\n")
        report = portfolio_comparator.compare_portfolio(args.compare_portfolio)

        print(f"Total Companies Benchmarked:     {report.total_entities_analyzed}")
        print(f"Reporting Period:                {report.reporting_period}")
        print(f"Total Portfolio Revenue:         ${report.total_portfolio_revenue:,.2f}")
        print(f"Average Gross Margin:            {report.average_gross_margin_pct:.1f}%")
        print(f"Average EBITDA Margin:           {report.average_ebitda_margin_pct:.1f}%")
        print(f"Median YoY Revenue Growth:       {report.median_revenue_growth_pct:.1f}%")
        print(f"Distressed Companies:            {report.distressed_entities_count}")
        print(f"Watchlist Companies:             {report.watchlist_entities_count}\n")

        print(f"{'COMPANY': <28} {'PERIOD': <8} {'REVENUE ($)': <14} {'YOY %': <8} {'GROSS %': <9} {'EBITDA ($)': <14} {'EBITDA %': <9} {'STATUS'}")
        print("-" * 105)
        for c in report.companies:
            yoy_str = f"{c.yoy_revenue_growth_pct:+.1f}%" if c.yoy_revenue_growth_pct is not None else "N/A"
            gm_str = f"{c.gross_margin_pct:.1f}%" if c.gross_margin_pct is not None else "N/A"
            em_str = f"{c.ebitda_margin_pct:.1f}%" if c.ebitda_margin_pct is not None else "N/A"
            print(f"{c.entity_name[:27]: <28} {c.fiscal_period: <8} ${c.revenue:,.0f} {yoy_str: <8} {gm_str: <9} ${c.ebitda:,.0f} {em_str: <9} {c.health_status}")

        return

    # Pillar 2: Single Financial Statement Normalization
    if args.financials:
        if not os.path.exists(args.financials):
            print(f"Error: File not found at {args.financials}")
            sys.exit(1)

        parsed = pipeline.parser.parse(args.financials)
        rep = financial_normalizer.normalize(args.financials, parsed.full_text)
        print(f"\n=======================================================")
        print(f"📊 NORMALIZED FINANCIAL REPORT: {rep.entity_name} ({rep.fiscal_period})")
        print(f"=======================================================")
        print(f"Reporting Currency:  {rep.currency}")
        print(f"Standard:            {rep.reporting_standard}")
        print(f"Health Status:       {rep.health_status}\n")

        print("--- Income Statement ---")
        inc = rep.income_statement
        print(f"  Revenue:            ${inc.revenue:,.2f}")
        print(f"  Cost of Goods Sold: ${inc.cogs:,.2f}")
        print(f"  Gross Profit:       ${inc.gross_profit:,.2f} ({inc.gross_margin_pct:.1f}%)")
        print(f"  Operating Expenses: ${inc.operating_expenses:,.2f}")
        print(f"  EBITDA:             ${inc.ebitda:,.2f} ({inc.ebitda_margin_pct:.1f}%)")
        print(f"  Net Income:         ${inc.net_income:,.2f} ({inc.net_margin_pct:.1f}%)\n")

        print("--- Balance Sheet & Cash Flow ---")
        bs = rep.balance_sheet
        cf = rep.cash_flow
        print(f"  Cash & Equivalents: ${bs.cash_and_equivalents:,.2f}")
        print(f"  Total Debt:         ${bs.total_debt:,.2f}")
        print(f"  Shareholder Equity: ${bs.total_shareholder_equity:,.2f}")
        print(f"  Operating Cash Flow:${cf.operating_cash_flow:,.2f}")
        print(f"  Free Cash Flow:     ${cf.free_cash_flow:,.2f}")

        if rep.health_notes:
            print("\n--- Health Assessment Notes ---")
            for n in rep.health_notes:
                print(f"  • {n}")
        return

    # Pillar 1: Batch M&A Diligence
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
    if len(sys.argv) > 1:
        run_cli()
    else:
        uvicorn.run("app.main:app", host=settings.PROCESSOR_HOST, port=settings.PROCESSOR_PORT, reload=True)

