# DCA - Document & Contract Analysis

DCA is an intelligent document and contract processing platform designed to ingest, validate, parse, extract, review, and report on complex commercial contracts, NDAs, and agreements.

---

## 🏛️ System Architecture

- **Client Tier (`apps/web`):** React SPA (Vite + Tailwind CSS) providing side-by-side contract review, grounding citation inspection, and stakeholder analytics dashboards.
- **BFF Gateway (`apps/bff`):** Node.js (Express + TypeScript) handling JWT authentication, role-based access control, file upload validation (magic bytes & SHA-256), and audit logging.
- **Heavy Processing Tier (`apps/processor`):** Python (FastAPI + Pydantic v2 + PyMuPDF / pdfplumber) layout extraction, hallucination guardrails, grounding verification, and multi-provider AI extraction (Gemini, OpenAI, Mock).
- **Data & Storage:** PostgreSQL 16 (relational extractions & audit trails) + Redis 7 (task queue) + MinIO / S3 (encrypted object storage).

---

## 🚀 Quick Start

### 1. Prerequisites & Environment Setup

Copy the example environment configuration:
```bash
cp .env.example .env
```

Start PostgreSQL, Redis, and MinIO storage:
```bash
docker compose up -d
```
*(The `db/init.sql` schema and MinIO bucket will be provisioned automatically).*

---

### 2. Python Extraction Engine (`apps/processor`)

Activate the virtual environment and run the test suite:
```bash
cd apps/processor
source .venv/bin/activate
pip install -r requirements.txt

# Run unit tests
PYTHONPATH=. pytest tests/test_extraction.py -v
```

#### Pillar 1: M&A Vendor SLA & Contract Risk Auditor
```bash
python -m app.main --batch tests/contracts_batch
```
Analyzes 2,000+ contracts, computes total financial exposure, flags Change of Control consent triggers, and calculates uptime SLA breach penalty exposure.

#### Pillar 2: Multi-Entity Financial Statement Normalizer & 30-Company Comparator
```bash
python -m app.main --compare-portfolio tests/portfolio_financials
```
Normalizes multi-nomenclature Income Statements, Balance Sheets, and Cash Flows. Benchmarks 30+ portfolio companies across gross margins, EBITDA, YoY revenue growth, and assigns financial health scores (`EXCELLENT`, `SOLID`, `WATCHLIST`, `DISTRESSED`).

#### Pillar 3: Technical Accounting Memo & Balanced Journal Entry Studio
```bash
python -m app.main --accounting-memo tests/contracts_batch/01_CloudCore_Vendor_SLA.pdf
```
Applies the ASC 606 5-step revenue recognition framework to commercial contracts. Automatically generates balanced debit/credit journal entries for Initial Invoicing, Ratable Amortization, and Milestone Recognition.

#### Pillar 4: Batch Data Automation & Python Script Execution Framework
```bash
python -m app.main --automation-benchmark
```
Ingests disparate multi-department records (Procurement, Billing, Logistics, HR), cleans header aliases, normalizes currencies/dates, performs exact and fuzzy deduplication, evaluates enterprise business rules, runs pluggable Python scripts (Spend Audit, Revenue Reconciliation, SLA Penalties, Forensic Benford/Z-Score Outliers), and surfaces strategic insights.

#### Pillar 5: Intelligent Workspace & Organizational Knowledge Brain (RAG)
```bash
python -m app.main --list-workspaces
python -m app.main --rag-query "What are the termination rights and uptime SLA penalties for DataStream?"
```
Workspace-isolated pgvector semantic RAG engine. Indexes document chunks while preserving page boundaries and clause sections (`Section 4.1`, `Section 11`). Generates contextual AI responses grounded with verifiable verbatim page and clause citations.

---

### 🧪 Run Full Test Suite across All 5 Pillars

```bash
cd apps/processor
PYTHONPATH=. pytest -v
```
*(Runs all 21 unit & integration tests across layout parsing, M&A diligence rollups, financial normalization, ASC 606 balancing logic, batch automation scripts, and RAG hybrid vector retrieval).*

---

### 🌐 Running the Full Stack Application

1. **Start DB & Storage:**
   ```bash
   docker compose up -d
   ```
2. **Start Python Processor:**
   ```bash
   cd apps/processor
   source .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Start Node.js BFF:**
   ```bash
   cd apps/bff
   npm run dev
   ```
4. **Start React UI:**
   ```bash
   cd apps/web
   npm run dev
   ```
Visit `http://localhost:3000` to interact with all 5 pillars in the web dashboard!