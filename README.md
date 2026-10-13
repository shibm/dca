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

#### Run Pillar 1 Batch Diligence across a folder of vendor contracts:
```bash
python -m app.main --batch tests/contracts_batch
```
Generates the M&A diligence portfolio rollup: total financial exposure, change-of-control consent requirements, and SLA penalty matrix.

#### Run Pillar 2 Multi-Entity Financial Benchmarking across 30+ portfolio companies:
```bash
python -m app.main --compare-portfolio tests/portfolio_financials
```
Normalizes Income Statements, Balance Sheets, and Cash Flows across portfolio companies. Computes EBITDA margins, Free Cash Flow, YoY growth %, and assesses financial health status (`EXCELLENT`, `SOLID`, `WATCHLIST`, `DISTRESSED`).

#### Run Pillar 2 Single Financial Statement Normalizer:
```bash
python -m app.main --financials tests/portfolio_financials/01_CloudVanguard_SaaS_FY2025.pdf
```

#### Run Single Contract Extraction:
```bash
python -m app.main --file tests/sample_contract.pdf
```

#### Start FastAPI Extraction Server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 3. Node.js BFF Service (`apps/bff`)

```bash
cd apps/bff
npm install
npm run dev
```
Runs on `http://localhost:4000`.

---

### 4. React Frontend (`apps/web`)

```bash
cd apps/web
npm install
npm run dev
```
Runs on `http://localhost:3000` with proxy routing to the BFF at `/api`.

---

## 🔍 The 10-Step Extraction & Verification Pipeline

1. **Authentication:** JWT tokens & RBAC roles (`admin`, `reviewer`, `stakeholder`).
2. **PDF Validation:** MIME inspection and `%PDF` magic byte header verification.
3. **Secure Storage:** SHA-256 deduplication and AES-256 encrypted object storage.
4. **Layout Extraction:** Text blocks, spatial bounding boxes `[x0, y0, x1, y1]`, and tables via `pdfplumber`.
5. **AI Extraction:** Pydantic structured output models (`parties`, `financials`, `dates`, `legal_clauses`, `risks`).
6. **Guardrails & Grounding:** Verifies citations against verbatim document text and validates chronological date consistency.
7. **Database Storage:** Relational persistence into PostgreSQL with confidence scoring.
8. **Dashboard Display:** Side-by-side review screen mapping citations to PDF coordinates.
9. **HITL Review:** Field corrections recorded in `extraction_audit_logs` before final approval.
10. **Stakeholder Reporting:** Aggregated metrics and one-click CSV/PDF export.


how to run - 

Start DB & Storage: docker compose up -d
Start Python Processor: cd apps/processor && source .venv/bin/activate && uvicorn app.main:app --reload
Start Node.js BFF: cd apps/bff && npm run dev
Start React UI: cd apps/web && npm run dev