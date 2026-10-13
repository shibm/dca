# 🚀 DCA Platform: Complete Demo Guide & Solution Overview

Welcome to the **Document & Contract Analysis (DCA)** platform demonstration. This guide provides an executive overview of what the platform solves, where to begin your evaluation, and step-by-step instructions to run the demo via the **Interactive Web UI** or **Instant CLI Commands**.

---

## 🎯 What DCA Solves: The 5 Enterprise Pillars

Large enterprises and investment firms spend millions of dollars and thousands of hours manually reviewing commercial agreements, standardizing financial statements across portfolio companies, drafting complex accounting memorandums, and reconciling inconsistent multi-department data.

DCA solves this by uniting **automated document extraction**, **deterministic financial & accounting rules**, and **contextual RAG AI** into five dedicated pillars:

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DCA PLATFORM ARCHITECTURE                                   │
├─────────────────┬─────────────────┬──────────────────┬────────────────────┬───────────────────┤
│    PILLAR 1     │    PILLAR 2     │     PILLAR 3     │      PILLAR 4      │     PILLAR 5      │
│  M&A Vendor SLA │ Multi-Entity 30 │ Technical ASC606 │ Batch Data Script  │   Intelligent     │
│   Risk Auditor  │   Comparator    │ Accounting Memo  │  Execution Engine  │  Knowledge Brain  │
├─────────────────┼─────────────────┼──────────────────┼────────────────────┼───────────────────┤
│ • 2,000+ Vendor │ • P&L, BS, CF   │ • ASC 606 5-Step │ • Inconsistent CSV │ • Workspaces &    │
│   Agreements    │   Normalizer    │   Analysis       │   / JSON records   │   Engagements     │
│ • Change-of-    │ • 30 Portfolio  │ • Balanced Dr/Cr │ • Rule Engine &    │ • Semantic Vector │
│   Control Risks │   Companies     │   Journal Entries│   Z-Score Outliers │   pgvector RAG    │
│ • Uptime SLA    │ • Health Score: │ • Standalone SSP │ • 4 Pluggable      │ • Verifiable Page │
│   Penalties     │   Distressed/OK │   Allocations    │   Domain Scripts   │   Citations       │
└─────────────────┴─────────────────┴──────────────────┴────────────────────┴───────────────────┘
```

1. **Pillar 1: M&A Vendor SLA & Contract Risk Auditor**
   - *Problem:* In an acquisition, auditing 2,000+ vendor contracts for termination rights, Change of Control (CoC) consent requirements, and SLA penalty liabilities takes weeks of lawyer review.
   - *Solution:* Bulk-analyzes contract portfolios in seconds; extracts termination triggers, uptime guarantees, and penalty caps; computes an automated **M&A Diligence Risk Index (0–100)**.

2. **Pillar 2: Multi-Entity Financial Statement Normalizer & 30-Company Comparator**
   - *Problem:* An investment firm owning 30 companies receives financial statements with conflicting line-item naming, negative number conventions `($1,250,000)`, and varying accounting standards.
   - *Solution:* Ingests disparate statements; maps lines to canonical GAAP/IFRS taxonomies; computes EBITDA margins, Free Cash Flow, YoY growth %; benchmarks all 30 entities side-by-side in one dashboard; scores financial health (`EXCELLENT`, `SOLID`, `WATCHLIST`, `DISTRESSED`).

3. **Pillar 3: Technical Accounting Memo & Balanced Journal Entry Studio**
   - *Problem:* Preparing technical accounting memos under ASC 606 (Revenue from Contracts with Customers) and creating audit-ready journal entries is error-prone and time-consuming.
   - *Solution:* Extracts performance obligations and variable consideration; computes relative Standalone Selling Price (SSP) allocations; generates **mathematically balanced Debit/Credit journal entries**; provides human-in-the-loop review, editing, and audit export.

4. **Pillar 4: Batch Data Automation & Python Script Execution Framework**
   - *Problem:* Companies receive thousands of messy, duplicated records from Procurement, Billing, Logistics, and HR in disparate formats with missing purchase orders and payment anomalies.
   - *Solution:* Normalizes header aliases and currencies; detects duplicates; runs business rules (Maverick spend, executive approval thresholds); executes specialized Python plugins (Spend Audit, Revenue Reconciliation, SLA Penalties, Forensic Benford/Z-Score Outliers); generates strategic business insights.

5. **Pillar 5: Intelligent Workspace & Organizational Knowledge Brain (RAG)**
   - *Problem:* Teams work across multiple clients and engagements without centralized knowledge, leading to repetitive research and hallucinated answers.
   - *Solution:* Engagement-isolated workspaces with tenant security; clause-aware document chunking (`Section 4.1`, `Section 11`); hybrid vector semantic retrieval; conversational AI answering questions with **clickable, verifiable page and clause citations**.

---

## ⚡ Where to Begin: 2-Minute Quick Demo

If you want to immediately see all 5 pillars in action without starting full infrastructure, use the **Instant CLI Demo Mode**. It runs against pre-packaged, realistic enterprise contracts, financial statements, and multi-department records.

### Instant CLI Demo (Zero Setup)

Navigate to `apps/processor` and run:

```bash
cd /Users/hydear/Documents/dca/apps/processor
source .venv/bin/activate
```

#### 1️⃣ Demo Pillar 1: M&A Vendor SLA Diligence Rollup
```bash
python -m app.main --batch tests/contracts_batch
```
> **What you'll see:** Total portfolio financial exposure, Change of Control consent risks, acquisition termination rights, and risk score ranking across acquired vendor contracts.

#### 2️⃣ Demo Pillar 2: 30-Company Financial Benchmarking
```bash
python -m app.main --compare-portfolio tests/portfolio_financials
```
> **What you'll see:** Multi-entity comparative dashboard, total portfolio revenue, gross margins, EBITDA, YoY revenue growth, and financial health classifications (`EXCELLENT`, `DISTRESSED`).

#### 3️⃣ Demo Pillar 3: ASC 606 Accounting Memo & Balanced Journal Entries
```bash
python -m app.main --accounting-memo tests/contracts_batch/01_CloudCore_Vendor_SLA.pdf
```
> **What you'll see:** ASC 606 5-step evaluation, relative Standalone Selling Price allocations, and a **mathematically balanced Debit/Credit schedule** where Total Debits equal Total Credits.

#### 4️⃣ Demo Pillar 4: Batch Data Automation & Script Engine
```bash
python -m app.main --automation-benchmark
```
> **What you'll see:** Multi-department data normalization, duplicate detection, maverick spend identification lacking POs, statistical Z-score outliers ($1.85M transaction), Benford divergence, and strategic recommendations.

#### 5️⃣ Demo Pillar 5: Intelligent Workspace RAG Knowledge Brain
```bash
python -m app.main --rag-query "What are the termination rights and uptime SLA penalties for DataStream?"
```
> **What you'll see:** A contextual AI answer synthesized strictly from verified documents, accompanied by **exact page and clause citations** (`02_DataStream_Critical_Risk.pdf`, Page 2, Section 11).

---

---

## 🖥️ Interactive Web UI Demo: Step-by-Step

You can run the full stack **with or without Docker**:

> [!NOTE]
> **Can you run this project WITHOUT Docker? YES!**
> Docker is **purely optional** (only used for containerized PostgreSQL, Redis, and MinIO storage).
> The Python Processor, Node.js BFF, and React Web UI all have **built-in in-memory vector storage, memory caches, and demo fallbacks**.
> You can run the entire system natively on your machine without installing or launching Docker.

---

### Option A: Running Completely WITHOUT Docker (Zero-Docker Mode)

#### 1. Start Python Processor (Port 8000)
```bash
cd apps/processor
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*(Runs all 5 pillars, in-memory vector search, ASC 606 engine, and batch automation).*

#### 2. Start Node.js BFF (Port 4000)
```bash
cd apps/bff
npm install
npm run dev
```
*(Automatically activates built-in offline demo fallbacks when PostgreSQL is not running).*

#### 3. Start React Web UI (Port 3000)
```bash
cd apps/web
npm install
npm run dev
```

Open **`http://localhost:3000`** in your browser!

---

### Option B: Running WITH Docker (Optional - for persistent DB)

If you have Docker installed and want containerized PostgreSQL 16, Redis 7, and MinIO object storage:

```bash
docker compose up -d
```
*(Automatically provisions PostgreSQL schema from `db/init.sql` and initializes MinIO).*
Then start Python (`uvicorn app.main:app --reload`), BFF (`npm run dev`), and Web (`npm run dev`) as above.

### Step 3: Start Node.js BFF (Port 4000)
```bash
cd apps/bff
npm install
npm run dev
```

### Step 4: Start React Frontend (Port 3000)
```bash
cd apps/web
npm install
npm run dev
```

Open your browser to: **`http://localhost:3000`**

---

## 🧭 Interactive UI Walkthrough Guide

Use the top navigation bar to explore each pillar:

```
[ DCA ]  [ M&A / SLA (P1) ]  [ Financials (P2) ]  [ Accounting Studio (P3) ]  [ Automation (P4) ]  [ Workspace (P5) ]  [ Upload Document ]  [ HITL Review ]  [ Reports ]
```

### 1. Workspace (Pillar 5) — The Operational Hub
- Click **"Workspace (P5)"** on the top navigation.
- Notice the **Active Engagement Switcher**:
  - `Project Apollo: M&A Diligence & SLA Review` (Private Equity / M&A)
  - `Apex Holdings: 30-Company Financial Audit` (Asset Management)
- **Knowledge Base (Left Pane):** Shows indexed documents, page counts, and one-click workflow triggers.
- **Contextual AI Chat (Right Pane):**
  - Click any sample prompt pill (e.g., *"What are the change of control risks and immediate termination penalties?"*).
  - Inspect the synthesized response.
  - Notice the **Verifiable Sources & Citations** at the bottom of the message.
  - Click any citation to expand and inspect the verbatim quote grounded directly from the PDF page.

### 2. M&A / SLA Diligence (Pillar 1)
- Click **"M&A / SLA (P1)"**.
- Review the top summary cards:
  - Total Contracts Analyzed
  - Total Financial Exposure ($)
  - Change of Control Risk Count
  - Average Portfolio Diligence Risk Index
- Inspect the **Vendor SLA & Risk Register Table**:
  - Filter by risk level or search for a specific vendor.
  - Click any contract row to drill down into the side-by-side HITL review view.
  - Click **"Export Diligence CSV"** to download an audit spreadsheet.

### 3. Financials Comparator (Pillar 2)
- Click **"Financials (P2)"**.
- View multi-entity benchmarking across the portfolio:
  - Aggregate Revenue, Average Gross Margin, Average EBITDA Margin, YoY Growth.
- Use the **Search & Health Filters**:
  - Filter by `DISTRESSED` to view high-risk entities experiencing negative growth or operating losses.
  - Filter by `EXCELLENT` to see top cash-generating companies.
- Click **"Export Benchmark CSV"** for leadership reporting.

### 4. Accounting Studio (Pillar 3)
- Click **"Accounting Studio (P3)"**.
- Explore the **3 Accounting Tabs**:
  - **ASC 606 5-Step Evaluation:** Review the contract identification, distinct performance obligations, transaction price, and recognition timing.
  - **Balanced Journal Entries:** Inspect the double-entry accounting schedule (Initial Billing, Ratable SaaS Amortization, and Milestone Recognition). Notice the green `BALANCED` badges confirming Debits equal Credits.
  - **Memorandum Editor & Export:** Edit the Executive Summary and click **"Export Technical Memo"** to download an audit-ready memorandum.
  - Click **"Sign-off & Approve Memo"** to log formal CPA review.

### 5. Automation & Script Runner (Pillar 4)
- Click **"Automation (P4)"**.
- Click **"Run Batch Engine"** to ingest multi-department records.
- Explore the **4 Sub-Tabs**:
  - **Anomalies & Policy Breaches:** Review detected duplicate records, missing POs on transactions >$10k, executive board thresholds, and statistical Z-score outliers ($1.85M transaction).
  - **Strategic Business Insights:** Inspect cards highlighting spend concentration (95.6%), maverick spend ($279k), and duplicate recovery opportunities ($60.2k).
  - **Python Plugin Registry:** Toggle specialized script plugins (Spend Audit, Revenue Reconciliation, SLA Penalties, Forensic Benford/Z-Score Outliers).
  - **Normalized Dataset Preview:** View disparate multi-department columns mapped to standardized canonical schema attributes.

### 6. Human-In-The-Loop Review & Spatial PDF Mapping
- Click **"HITL Review"**.
- View the side-by-side split screen:
  - Left pane: PDF document viewer.
  - Right pane: Extracted fields with confidence scores.
  - Click any field to highlight its bounding box on the original PDF.
  - Correct any field value and enter a reason — the change is recorded with a full audit trail in `extraction_audit_logs`.
  - Click **"Approve Document"** to lock the verified extractions.

---

## 🧪 Automated Test Suite Verification

Every component is validated with a comprehensive automated test suite. Run the tests anytime:

```bash
cd apps/processor
PYTHONPATH=. ./apps/processor/.venv/bin/pytest -v
```

**Expected Result:**
```
============================== 21 passed in 1.58s ==============================
apps/processor/tests/test_extraction.py (3 tests)                      PASSED
apps/processor/tests/test_pillar1_sla_diligence.py (3 tests)          PASSED
apps/processor/tests/test_pillar2_financial_normalizer.py (3 tests)   PASSED
apps/processor/tests/test_pillar3_accounting_memo.py (2 tests)        PASSED
apps/processor/tests/test_pillar4_automation.py (5 tests)             PASSED
apps/processor/tests/test_pillar5_workspace_rag.py (5 tests)          PASSED
```

---

## 🛡️ Enterprise Security & Grounding Principles

- **Zero-Hallucination Guarantee:** RAG answers and extracted contract terms must be grounded in verbatim source quotes from the document.
- **Tenant & Workspace Isolation:** Chunks and embeddings are partitioned by `workspace_id`. Chunks from Workspace A never leak into Workspace B.
- **Auditability:** Every field edit in the HITL review interface records user ID, timestamp, prior value, new value, and justification.
- **Mathematical Integrity:** All financial ratios and ASC 606 journal entry lines are checked programmatically for balancing ($\sum \text{Debits} == \sum \text{Credits}$).

