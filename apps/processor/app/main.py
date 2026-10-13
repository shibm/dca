import os
import sys
import argparse
import tempfile
import uvicorn
from typing import List, Dict, Any, Optional
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


from app.ai.accounting_engine import TechnicalAccountingEngine
from app.schemas.accounting import TechnicalAccountingMemo

accounting_engine = TechnicalAccountingEngine()


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


@app.post("/accounting/generate-memo", response_model=TechnicalAccountingMemo)
async def generate_accounting_memo_endpoint(file: UploadFile = File(...)):
    """Pillar 3: Generate ASC 606 technical accounting memo and journal entries from contract PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parsed = pipeline.parser.parse(tmp_path)
        memo = accounting_engine.analyze_contract(parsed)
        return memo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accounting memo generation failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Pillar 4: Batch Data Automation & Python Script Execution Framework
# ---------------------------------------------------------------------------
from app.automation.engine import AutomationEngine, generate_benchmark_multi_department_dataset
from app.automation.script_registry import REGISTRY
from app.schemas.automation import AutomationJobRequest, AutomationJobResult, AutomationScriptMetadata

automation_engine = AutomationEngine()


@app.get("/automation/scripts", response_model=List[AutomationScriptMetadata])
async def list_automation_scripts_endpoint():
    """Pillar 4: List registered specialized Python automation scripts."""
    return REGISTRY.list_scripts()


@app.post("/automation/run", response_model=AutomationJobResult)
async def run_automation_endpoint(request: AutomationJobRequest):
    """Pillar 4: Run batch data normalization, business rules, and specialized Python scripts."""
    try:
        return automation_engine.run_job(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation job failed: {str(e)}")


@app.get("/automation/benchmark-dataset")
async def get_benchmark_dataset_endpoint():
    """Pillar 4: Retrieve multi-department benchmark raw dataset."""
    return {"records": generate_benchmark_multi_department_dataset()}


# ---------------------------------------------------------------------------
# Pillar 5: Intelligent Workspace & Organizational Knowledge Brain (RAG)
# ---------------------------------------------------------------------------
from app.rag.rag_engine import RAG_ENGINE
from app.schemas.workspace import Workspace, RAGQueryRequest, RAGQueryResponse, ConversationThread


@app.get("/workspaces", response_model=List[Workspace])
async def list_workspaces_endpoint():
    """Pillar 5: List all active organizational workspaces."""
    return RAG_ENGINE.list_workspaces()


@app.get("/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace_endpoint(workspace_id: str):
    """Pillar 5: Get workspace details by ID."""
    ws = RAG_ENGINE.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@app.post("/workspaces/{workspace_id}/chat", response_model=RAGQueryResponse)
async def chat_workspace_endpoint(workspace_id: str, request: RAGQueryRequest):
    """Pillar 5: Query knowledge brain with semantic search and page citations."""
    try:
        req = request.model_copy(update={"workspace_id": workspace_id})
        return RAG_ENGINE.query_workspace(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@app.get("/workspaces/{workspace_id}/conversations", response_model=List[ConversationThread])
async def list_conversations_endpoint(workspace_id: str):
    """Pillar 5: List conversation history for a workspace."""
    return RAG_ENGINE.list_workspace_conversations(workspace_id)




def run_cli():
    """Command-line interface to test contract diligence, financial normalization, or technical accounting memos."""
    parser = argparse.ArgumentParser(description="DCA Document Analysis CLI")
    parser.add_argument("--file", "-f", help="Path to single contract PDF file")
    parser.add_argument("--batch", "-b", help="Path to directory containing batch of PDF contracts (Pillar 1)")
    parser.add_argument("--financials", help="Path to single financial statement PDF (Pillar 2)")
    parser.add_argument("--compare-portfolio", help="Path to directory of portfolio company financial statements (Pillar 2)")
    parser.add_argument("--accounting-memo", help="Path to contract PDF for Pillar 3 Technical Accounting Memo generation")
    parser.add_argument("--automation-benchmark", action="store_true", help="Run batch data automation & script engine on benchmark dataset (Pillar 4)")
    parser.add_argument("--run-automation", help="Path to JSON file containing raw records to run automation framework on (Pillar 4)")
    parser.add_argument("--rag-query", help="Query the organizational knowledge brain using RAG (Pillar 5)")
    parser.add_argument("--workspace", default="ws-project-apollo", help="Target workspace ID for RAG query (Pillar 5)")
    parser.add_argument("--list-workspaces", action="store_true", help="List all active organizational workspaces (Pillar 5)")
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

    # Pillar 3: Technical Accounting Memo & Journal Entry Generation
    if args.accounting_memo:
        if not os.path.exists(args.accounting_memo):
            print(f"Error: File not found at {args.accounting_memo}")
            sys.exit(1)

        parsed = pipeline.parser.parse(args.accounting_memo)
        memo = accounting_engine.analyze_contract(parsed)

        print(f"\n==========================================================================")
        print(f"📜 PILLAR 3: TECHNICAL ACCOUNTING MEMO (ASC 606)")
        print(f"==========================================================================")
        print(f"Memo Reference:    {memo.memo_id}")
        print(f"Contract Title:    {memo.contract_title}")
        print(f"Parties:           {' vs '.join(memo.parties)}")
        print(f"Contract Value:    ${memo.contract_value:,.2f} {memo.currency}")
        print(f"Effective Date:    {memo.effective_date}")
        print(f"Accounting Model:  {memo.accounting_standard.value}")
        print(f"Status:            {memo.status}\n")

        print("--- Executive Summary ---")
        print(memo.executive_summary)

        print("\n--- ASC 606 5-Step Evaluation ---")
        eval606 = memo.asc606_analysis
        print(f"[Step 1: Contract Identification]\n  {eval606.step1_assessment}\n")
        print(f"[Step 2: Performance Obligations ({len(eval606.step2_performance_obligations)})]")
        for p in eval606.step2_performance_obligations:
            print(f"  • {p.id}: {p.name} | Allocated: ${p.allocated_transaction_price:,.2f} | Timing: {p.timing_of_satisfaction} ({p.recognition_period})")
        print(f"\n[Step 3: Transaction Price]\n  Total: ${eval606.step3_total_transaction_price:,.2f} USD\n")
        print(f"[Step 4: Price Allocation]\n  {eval606.step4_assessment}\n")
        print(f"[Step 5: Revenue Timing & Recognition]\n  {eval606.step5_recognition_summary}\n")

        print("--- Suggested Balanced Journal Entries (Debit / Credit) ---")
        for je in memo.suggested_journal_entries:
            balanced_symbol = "✓ BALANCED" if je.is_balanced else "⚠ UNBALANCED"
            print(f"\n[{je.schedule_id}] {je.event_name} ({je.period}) - {balanced_symbol}")
            print(f"{'ACCOUNT': <40} {'DEBIT ($)': <14} {'CREDIT ($)': <14}")
            print("-" * 68)
            for line in je.lines:
                deb_str = f"${line.debit:,.2f}" if line.debit else ""
                cred_str = f"${line.credit:,.2f}" if line.credit else ""
                print(f"{line.account_name[:39]: <40} {deb_str: <14} {cred_str: <14}")
            print("-" * 68)
            print(f"{'TOTAL': <40} ${je.total_debit:,.2f}{'': <6} ${je.total_credit:,.2f}")

        print("\n--- Audit Notes & Financial Disclosures ---")
        print(memo.conclusion_and_disclosures)
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

    # Pillar 4: Batch Data Automation & Python Script Execution Framework
    if args.automation_benchmark or args.run_automation:
        import json
        if args.run_automation:
            if not os.path.exists(args.run_automation):
                print(f"Error: Automation data file not found at {args.run_automation}")
                sys.exit(1)
            with open(args.run_automation, "r", encoding="utf-8") as f:
                raw_records = json.load(f)
                if isinstance(raw_records, dict) and "records" in raw_records:
                    raw_records = raw_records["records"]
        else:
            raw_records = generate_benchmark_multi_department_dataset()

        print(f"\n==========================================================================")
        print(f"⚙️  PILLAR 4: BATCH DATA AUTOMATION & PYTHON SCRIPT EXECUTION ENGINE")
        print(f"==========================================================================\n")
        req = AutomationJobRequest(
            job_id="cli-batch-run",
            script_ids=[s.script_id for s in REGISTRY.list_scripts()],
            raw_records=raw_records,
        )
        res = automation_engine.run_job(req)

        print(f"Job ID:                     {res.job_id}")
        print(f"Status:                     {res.status}")
        print(f"Execution Duration:         {res.execution_time_ms:.1f} ms")
        print(f"Total Records Ingested:     {res.total_records_ingested}")
        print(f"Cleaned Records Count:      {res.cleaned_records_count}")
        print(f"Duplicates Detected:        {res.duplicates_detected}")
        print(f"Total Anomalies Flagged:    {res.anomalies_count} (Critical: {res.critical_anomalies_count})\n")

        print("--- Specialized Python Scripts Executed ---")
        for s_log in res.script_logs:
            print(f"  • [{s_log.status}] {s_log.script_name: <45} ({s_log.execution_time_ms:.1f}ms) | Anomalies: {s_log.anomalies_flagged} | Insights: {s_log.insights_generated}")

        print("\n--- Key Business Insights & Strategic Recommendations ---")
        for ins in res.insights:
            print(f"  [{ins.trend}] {ins.title}: {ins.formatted_value}")
            print(f"      Summary:        {ins.narrative}")
            print(f"      Recommendation: {ins.recommendation}\n")

        print("--- Top Detected Anomalies & Risk Breaches ---")
        for anom in res.anomalies[:8]:
            print(f"  [{anom.severity: <8}] {anom.anomaly_type: <28} (Rec #{anom.record_index}): {anom.description}")

        return

    # Pillar 5: Intelligent Workspace & Organizational Knowledge Brain (RAG)
    if args.list_workspaces:
        print(f"\n==========================================================================")
        print(f"🧠 PILLAR 5: ORGANIZATIONAL WORKSPACES & KNOWLEDGE BASES")
        print(f"==========================================================================\n")
        workspaces = RAG_ENGINE.list_workspaces()
        print(f"{'WORKSPACE ID': <25} {'CLIENT / ORG': <30} {'DOCS': <6} {'NAME'}")
        print("-" * 90)
        for ws in workspaces:
            print(f"{ws.workspace_id: <25} {ws.client_name[:29]: <30} {ws.document_count: <6} {ws.name}")
        return

    if args.rag_query:
        print(f"\n==========================================================================")
        print(f"🧠 PILLAR 5: KNOWLEDGE BRAIN CONTEXTUAL RAG QUERY")
        print(f"==========================================================================\n")
        ws = RAG_ENGINE.get_workspace(args.workspace)
        if not ws:
            print(f"Error: Workspace '{args.workspace}' not found.")
            sys.exit(1)

        print(f"Target Workspace: {ws.name} ({ws.client_name})")
        print(f"Query:            \"{args.rag_query}\"\n")

        rag_req = RAGQueryRequest(workspace_id=args.workspace, query=args.rag_query, top_k=4)
        rag_res = RAG_ENGINE.query_workspace(rag_req)

        print(f"Retrieved Passages: {rag_res.retrieved_chunks_count} | Query Latency: {rag_res.execution_time_ms:.1f}ms\n")
        print("--- Synthesized Grounded Response ---")
        print(rag_res.answer)

        print("\n--- Verifiable Document Citations ---")
        for idx, cite in enumerate(rag_res.citations, 1):
            clause_str = f" | {cite.clause_reference}" if cite.clause_reference else ""
            print(f"  [{idx}] {cite.document_name} (Page {cite.page_number}{clause_str})")
            print(f"      Quote: \"{cite.verbatim_quote}\"")

        return

    if not args.file:
        print("Error: Specify either --file, --batch, --financials, --compare-portfolio, --accounting-memo, --automation-benchmark, or --rag-query")
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

