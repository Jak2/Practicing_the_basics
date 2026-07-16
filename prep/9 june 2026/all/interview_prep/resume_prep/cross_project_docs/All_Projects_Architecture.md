# Architecture Diagrams — Work Experience + Key Projects

All diagrams reconstructed from each project's deep-dive/report — no invented components. Source file linked under each heading.

**Jump to:** [Core flow (simplest form)](#core-flow--simplest-form) · [Full diagrams](#work-experience) · [Common patterns](#common-architectural-patterns-across-all-projects) · [Plain-English version](#plain-english-architecture---one-paragraph-per-project) · [Known gaps](#known-gaps--claims-to-reconcile-before-quoting-stack-items-verbatim)

---

## CORE FLOW — simplest form

Stripped to the minimum boxes. This is "what's the flow, at its core" — no tech names, no config detail. If you can draw this on a whiteboard from memory, you know the project.

**Brane**
```
AI generates → Checker verifies (not the same AI call) → pass: commit
                                                          fail: retry with reason
```

**5G Failure Pipeline**
```
Error found → Search known errors (same vendor only) → AI writes fix from match
                                                          no match: refuse, don't guess
```

**RF Keyword Generator**
```
Plain English → AI extracts test details → Fill template → Validate → Test file
                  (fails: fall back to regex, never fully down)
```

**NFTRACE**
```
Start capture (all machines) → Stop (all machines) → Merge into one file → Validate
```

**Bias & Fairness Auditor**
```
Same prompt, only demographic changed → Run many times → Compare outputs statistically → Verdict
```

**EMS 2.0**
```
Resume PDF → Local AI reads it → Validate fields → Store in database → Chat can query it
```

**Prompt Regression Suite**
```
Prompt changes → Run test cases → Compare score to baseline → Score dropped: block the merge
```

**LLM Evaluation Framework**
```
AI response → Graded on 4 axes independently → ALL must pass (not average) → pass/fail
```

**Financial Statement Parser**
```
Bank statement → Read in browser (OCR) → AI identifies transactions → Spreadsheet out
```

**Blog/Docs Site Generator**
```
Markdown files in a folder → Site builds its own structure from them → Static site out
```

---

## PLAIN-ENGLISH ARCHITECTURE — one paragraph per project

Use this to *say out loud* in an interview before the diagram-level detail. Each one answers "what does it actually do" in a sentence or two, no jargon front-loaded.

**Brane — AI Agent Runtime.** A no-code platform let humans and deterministic automation run workflows, and I helped add a third option: a step where an AI does the work. The trick is the AI's answer is never trusted immediately — it goes through a separate checking step (rules, then maybe another AI, then maybe a human) before it's allowed to count. If it fails the check, it tries again with the reason why, up to a limit.

**5G Failure Pipeline.** Engineers used to open a network capture file and manually hunt for the error, then remember or guess the fix. My pipeline reads the file automatically, finds the error, searches a database of known errors *for that specific vendor* (so a Nokia fix never gets suggested for an Ericsson problem), and asks an AI to write a fix based on what's actually known — refusing to guess if nothing similar is found.

**RF Keyword Generator.** A tester types what they want to test in plain English ("check subscriber authentication"). An AI turns that into the technical test steps a testing tool understands. If the AI is unavailable, a simpler backup method still produces something rather than nothing — so the tool never goes fully down.

**NFTRACE.** Testing 5G equipment involves multiple machines capturing network traffic at once. This system tells all of them to start recording together, stop together, merges everyone's files into one, and checks the result against expected signaling rules — replacing what used to be manual coordination across machines.

**Bias & Fairness Auditor.** Feeds the same question to an AI many times, changing only a name or demographic detail each time, and checks statistically whether the AI treats people differently based on things that shouldn't matter — tone, amount of detail, an AI judge that can't see who it's grading. Produces a report a regulator would accept as evidence of testing.

**EMS 2.0 (AI Resume/Employee System).** Upload a resume PDF, and instead of someone typing 20 fields by hand, an AI reads it and fills the record automatically. Runs on a local AI model, so no resume data ever gets sent to an outside company. Also lets you ask questions about employees in plain English instead of writing a database query.

**Prompt Regression Suite.** "Unit tests," but for AI prompts instead of code — because a prompt can be edited, look fine, and quietly make the AI's answers worse in a way normal tests don't catch. Checks are ordered cheapest-first (free rule checks before a paid AI judge) and a change that makes quality drop blocks the pull request automatically.

**LLM Evaluation Framework.** Every AI response gets graded on four separate things — is it hallucinating, is it grounded in its source material, is it consistent, does a judge rate it well — and it only passes if it's good on *all four*, not just on average. One bad answer can't hide behind three good ones.

**Financial Statement Parser.** Upload a bank statement PDF or photo, and it turns into a clean spreadsheet automatically — reads the image in the browser, sends only the extracted text (not the file) to an AI to identify transactions, and exports to Excel/CSV/PDF. No account, no server, no database.

**Blog/Docs Site Generator.** Drop markdown files in a folder, and a website with navigation, search, and a sidebar builds itself — no one has to maintain a list of pages, because the site figures out its own structure from what files exist.

---

## WORK EXPERIENCE

### 1. Brane Enterprises — AI Agent Runtime (AI_AGENT LO type on a no-code platform)
Source: [BRANE/Brane_AI_Agent_Runtime_Deep_Dive.md](BRANE/Brane_AI_Agent_Runtime_Deep_Dive.md)

```
LO triggered (agent_type = AI_AGENT)
        │
        ▼
LO-level RBAC check (existing, unchanged)
        │
        ▼
Design-time grounding NFs run (fetch, calc, ai_with_rag)
        │
        ▼
Attribute-level RBAC filter (agent sees only granted attrs)
        │
        ▼   ┌─────────── correction loop (attempt_seq 1..max) ───────────┐
        │   │                                                            │
┌───────▼────────────┐  assemble: system + user + grounded inputs        │
│ AgentLoopController │  + tool registry + prior failure reports         │
└───────┬─────────────┘                                                  │
        ▼                                                                │
┌────────────────────┐  model may emit tool calls → NF invocation        │
│ gRPC Model Gateway  │◄────────────────┐  → existing NF handler runs it │
│ (instruct/thinking/ │  tool result    │                                │
│  vision routing,    │─────────────────┘                                │
│  stateless, scales  │                                                  │
│  by replica)         │                                                 │
└───────┬─────────────┘                                                  │
        ▼                                                                │
  ResponseParser (schema-validate + repair malformed output)             │
        ▼                                                                │
  Persist attempt → lo_input_execution_agent (sibling table)             │
  Mirror latest → lo_input_execution (canonical, unchanged)              │
        ▼                                                                │
┌──────────────────────────────┐                                        │
│ Verifier stack (SEPARATE lane)│                                        │
│ 1. deterministic (biz rules)  │ short-circuit on first fail            │
│ 2. AI verifier (diff model)   │                                        │
│ 3. human verifier (HUMAN task)│                                        │
└─────────────┬─────────────────┘                                       │
      pass │  fail → failure_report fed back into next prompt ──────────┘
            ▼
  Primary function fires; LO completes         cap exhausted → fallback state
            ▼
  Episode written → agent_episodes (memory layer 2)
```

**Tech stack:** PostgreSQL (sibling-table schema: `agents`, `lo_agents` junction, `lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`) · gRPC model gateway · MCP-backed verb router (`resolve_agent`) · Python.

---

### 2. Infinite Computer Solutions (Nokia-Ext) — 5G Failure Detection & Remediation Pipeline
Source: [5G_Failure_Detection_Pipeline_Deep_Dive.md](5G_Failure_Detection_Pipeline_Deep_Dive.md)

```
pcap file (input)
        ↓
┌────────────────────────────────┐
│ Stage 1: Pyshark Extraction     │  display filter (tshark, C-side)
│ error_text, vendor, layer,      │  → NAS/NGAP/Diameter/SIP cause codes
│ severity, timestamp             │
└───────────────┬──────────────────┘
                ↓
┌────────────────────────────────┐
│ Stage 2: Qdrant Retrieval       │  embed error_text (OpenAI ada-002, 1536d)
│ Filtered similarity search      │  MUST filter: vendor + layer (DB-level,
│ (vendor + layer + semantic)     │  before ranking) → cosine similarity
│ Return top-5, threshold 0.65    │
└───────────────┬──────────────────┘
                ↓
┌────────────────────────────────┐
│ Stage 3: LangChain RetrievalQA  │  stuff chain, chain_type_kwargs=prompt
│ Assemble context → Claude       │  return_source_documents=True
│ Model routing: Haiku (confident)│
│ / Sonnet (ambiguous/critical)   │
└───────────────┬──────────────────┘
                ↓
Output: fix_suggestion · matched_patterns · confidence · error_metadata
                ↓
      FastAPI (/analyze, /index, /health)  ·  Streamlit UI
```

**Tech stack:** Pyshark · Qdrant (Docker, HNSW/cosine) · LangChain RetrievalQA · Claude Sonnet + Haiku · FastAPI · Streamlit · (Redis claimed on resume — unverified against this deep-dive).

---

### 3. Nokia Networks — RF Keyword Generator
Source: [RF_Keyword_Generator_Deep_Dive.md](RF_Keyword_Generator_Deep_Dive.md)

```
Tester types natural-language test description
        ↓
Streamlit UI ──HTTP POST──▶ FastAPI backend
        ↓
Stage 1: Procedure detection (keyword matching)
        ↓
Stage 2: Entity extraction
   ├─ Claude Haiku (LLM path)
   └─ Regex fallback (on LLM exception → 100% uptime, NOT equivalent output)
        ↓
Stage 3: Deterministic template fill
        ↓
Stage 4: RF parser validation (syntax check only — no semantic check)
        ↓
.robot file → Streamlit → tester downloads
```

**Tech stack:** Streamlit · FastAPI · Claude Haiku (LLM extraction) · regex fallback · Robot Framework parser · pytest/httpx.

---

### 4. Nokia Networks — NFTRACE (distributed 5G trace platform)
Source: [NFTRACE_Deep_Dive.md](NFTRACE_Deep_Dive.md)

```
Test Worker(s)
   │ POST /sessions/start,stop,merge,validate
   ▼
FastAPI REST API
   │                    │
   ▼                    ▼
Redis (session cache)  SQLite (node/history — written only at merge)
   │
   ▼
XML-RPC Node Manager
   ├──▶ gNB Node
   ├──▶ AMF Node
   └──▶ UPF Node

Lifecycle:
start  → Redis: {worker_id, nodes, state:ACTIVE} → XML-RPC connects nodes,
         capture starts on all nodes
stop   → capture stops on all nodes
merge  → trace files merged into one pcap → SQLite persists history
validate → protocol dissection + SIP/Diameter rule validation → report
```

**Tech stack:** FastAPI · Redis (session cache, TTL-evicted) · SQLite (post-merge persistence) · XML-RPC (node control) · pcap merge · SIP/Diameter validators · integrates into Nokia CI/CD (NCD).

---

## KEY PROJECTS

### 5. LLM Bias & Fairness Auditor
Source: [Bias_Fairness_Auditor_Report_PROJECT_REPORT.md](Bias_Fairness_Auditor_Report_PROJECT_REPORT.md)

```
Prompt template {{placeholder}} + demographic matrix
        ↓
variant_generator.py → Cartesian product → [VariantPrompt × N]
        ↓
llm_executor.py → async, Semaphore-capped → [LLMResponse × N × runs]
        ↓
┌─────────────────── 4 independent analysis lenses ───────────────────┐
│ Sentiment (VADER → DistilBERT fallback)      weight 30%             │
│ Semantic similarity (all-MiniLM-L6-v2)       weight 35%             │
│ Structural quality (heuristics, no ML)       weight 10%             │
│ LLM Judge (blinded pairs, Claude)            weight 10%             │
└──────────────────────────┬─────────────────────────────────────────┘
                            ↓
bias_scorer.py → weighted composite → band: Pass/Review/Concern/Fail
                            ↓
enrichment.py → executive summary + remediation + EU AI Act Art.13 docs
                            ↓
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  reporting/ → PDF    api/ → JSON/HTTP    dashboard/ → Streamlit 5 tabs
```

**Tech stack:** FastAPI · Pydantic Settings/`BiasReport` contract · asyncio+Semaphore · VADER + sentence-transformers · SciPy (ANOVA, Cohen's d) · SQLAlchemy async (SQLite/Postgres) · Streamlit+Plotly · fpdf2 · Docker Compose · Claude/OpenAI/Ollama (3-provider support).

---

### 6. AI Employee Management System (EMS 2.0)
Source: [EMS_2.0_PROJECT_REPORT.md](EMS_2.0_PROJECT_REPORT.md)

```
FRONTEND (React/Vite) ──fetch()──▶ BACKEND (FastAPI)
                                       │
        ┌──────────────┬──────────────┼──────────────┐
        ▼              ▼              ▼              ▼
  /api/upload-cv  /api/job/{id}  /api/chat      /api/employees
        │                            │
        ▼                            ▼
  MongoDB GridFS              PostgreSQL + Ollama (qwen2.5:7b)
  (raw PDF) + Thread                 │
        │                            ▼
        ▼                        FAISS (vector store)
  CV pipeline (background thread):
  PDF → pdfplumber extract (pytesseract OCR fallback)
      → resume validator (score ≥ 40, pre-LLM gate)
      → Ollama LLM → JSON extraction
      → Pydantic validation
      → duplicate check
      → PostgreSQL store + FAISS index
      → job status "done"
```

**Tech stack:** React+Vite · FastAPI · Ollama (qwen2.5:7b, local — no data leaves device) · PostgreSQL (SQLite fallback) · MongoDB GridFS · FAISS · sentence-transformers (all-MiniLM-L6-v2) · pdfplumber + pytesseract · Pydantic v2 · SQLAlchemy.

---

### 7. Prompt Regression Suite
Source: [Prompt_Regression_Suite_Report_FULL_PROJECT_REPORT.md](Prompt_Regression_Suite_Report_FULL_PROJECT_REPORT.md)

```
.prompt-test.yaml files
        ↓
Registry (glob discovery, Pydantic parse, forward+reverse index)
        ↓
Change detector (CI): git diff → affected tests via reverse index
        ↓
Runner: asyncio.Semaphore dispatch, run_count× per test (default 3)
        ↓
LLM factory: claude-* / gpt-*,o1,o3,o4 / else → Ollama → LLMResponse
        ↓
┌─────────── AssertionEngine — 3 tiers, cheapest-first, FAIL-FAST ────────┐
│ Tier 0: rule-based (12 types, free) — any fail → stop, skip 1&2         │
│ Tier 1: semantic similarity (all-MiniLM-L6-v2, local, ~5ms)             │
│ Tier 2: LLM-as-judge (paid, only if 0+1 pass; temp=0.0; 4-dim rubric;   │
│         client-side score recompute; critical_failure if any dim<0.40) │
└───────────────────────────┬──────────────────────────────────────────┘
                             ↓
Multi-run average + flakiness flag (std_dev > 0.05)
                             ↓
BaselineManager: delta = mean − baseline; regression if delta < -0.05
                             ↓
SuiteRun aggregate → SQLAlchemy async ORM → SQLite/PostgreSQL
                             ↓
        ┌────────────┬───────────────┬───────────────────┐
        ▼            ▼               ▼                    ▼
  Typer CLI     FastAPI (/runs,   Streamlit dashboard  GitHub Actions
                /baselines,       (5 views, direct     pr-regression.yml
                /test-cases)      DB reads)             (merge gate) +
                                                          weekly-drift.yml
                                                          (Slack alert)
```

**Tech stack:** Python 3.11 · FastAPI · Typer+Rich · Pydantic v2 · SQLAlchemy 2.0 async · SQLite/PostgreSQL · all-MiniLM-L6-v2 · Streamlit+Plotly · GitHub Actions · Anthropic/OpenAI/Ollama.

---

### 8. LLM Evaluation Framework
Source: [LLM_EVAL_FRAMEWORK_REPORT.md](LLM_EVAL_FRAMEWORK_REPORT.md)

```
Client (curl/CI/browser)
   │ POST /api/test-cases (X-API-Key)
   ▼
FastAPI :8000 → Pydantic validate → TestCase(pending) → PostgreSQL
             → enqueue run_evaluation(id) → Redis broker
   │ HTTP 201 returned immediately (async job pattern)
   ▼
Redis :6379 → Celery Worker (concurrency=4)
   1. Fetch TestCase from PostgreSQL
   2. Call target LLM (Anthropic/OpenAI) — response, latency, tokens
   3. Run evaluators sequentially:
      ├─ LLM Judge         (threshold 0.60)
      ├─ Hallucination     (threshold 0.75, claim-level NLI)
      ├─ Faithfulness      (threshold 0.80)
      └─ Consistency       (threshold 0.85)
      → overall_passed = AND across all four (no averaging)
   4. Write EvalResult → PostgreSQL
   5. overall_passed=False → Slack webhook alert
   ▼
PostgreSQL :5432 ◄──polls 30s── Streamlit :8501 (4 tabs, Plotly)
```

**Tech stack:** FastAPI + Pydantic v2 · PostgreSQL 16 · SQLAlchemy 2.0 async + asyncpg + Alembic · Celery + Redis 7 · httpx async · Streamlit + Plotly · Docker Compose · Anthropic/OpenAI (Claude Haiku default judge).

---

### 9. Financial Statement Parser (Expense Tracker)
Source: [expense_tracker_PROJECT_REPORT.md](expense_tracker_PROJECT_REPORT.md)

```
File upload (bank statement PDF/image)
        ↓
FileUpload.jsx
   ├─ PDF → pdf.js (canvas render → image)
   └─ image → direct
        ↓
Tesseract.js OCR (WASM, in-browser)
        ↓
Extracted text, capped at 8,000 characters
        ↓
gemini.js → HTTPS POST → Gemini 2.5 Flash API   ⚠️ text LEAVES the browser
        ↓
JSON response (3-method parse/salvage incl. truncation repair)
        ↓
TransactionTable.jsx (editable)
        ↓
   ┌────────────┬─────────────────┐
   ▼            ▼                 ▼
analytics.js  export.js/         localStorage
(stats)       pdfExport.js       (obfuscated Gemini
              (CSV/Excel/PDF)     API key, BYOK)
```

**Tech stack:** React 18.2+Vite · Tailwind · Tesseract.js (OCR/WASM) · pdf.js · Google Gemini 2.5 Flash · Recharts · SheetJS · jsPDF. **No backend, no database — but NOT "100% private": OCR text is sent to Google's API.**

---

### 10. Blog / Docs Site Generator
Source: [BLOG_PROJECT_REPORT.md](BLOG_PROJECT_REPORT.md)

```
Build time:
Markdown files → import.meta.glob() discovers .md
        ↓
Sidebar tree built + search index built
        ↓
getStaticPaths() DERIVES routes (not configured — computed from the glob)
        ↓
Pages rendered to static HTML → dist/ → deploy to CDN

Request time:
URL → [...slug].astro → matched pre-generated route
    → glob finds .md file → extract frontmatter/TOC/prev-next
    → BaseLayout (Navbar|Sidebar|Content|TOC) → static HTML
    → client JS hydrates (dark mode, search, scroll spy)
```

**Tech stack:** Astro 3.5+ · Tailwind + typography plugin · PostCSS · vanilla JS (ES2020) · IntersectionObserver · localStorage · Vite `import.meta.glob()`. No backend, no database, no CMS.

---

## COMMON ARCHITECTURAL PATTERNS ACROSS ALL PROJECTS

This is the section worth memorizing — it's the answer to *"what's your engineering philosophy?"* and it's true across all ten, not asserted for effect.

### 1. Generation and verification are always separate
No project lets the thing that produces an output also certify it.
- **Brane:** verifier is a *separate execution lane* — deterministic rules → AI verifier (different model class) → human. "The generator never certifies itself."
- **5G pipeline:** the LLM adapts a *known, human-written fix* rather than inventing one; a 0.65 similarity gate sits in front of generation.
- **Bias Auditor:** the LLM judge reads *blinded* pairs — it cannot see which group it's grading.
- **Prompt Regression Suite:** the judge's own reported score is *discarded* and recomputed client-side from its stated dimension scores — "LLM arithmetic is unreliable."
- **LLM Eval Framework:** hallucination/faithfulness/consistency are evaluated by a *separate* process from the model that generated the response, with `overall_passed` using AND logic — one bad axis fails the whole thing, nothing averages it away.
- **RF Keyword Generator:** the RF parser *validates* LLM output syntactically before it's trusted, separate from the extraction step.

### 2. Every probabilistic component has a deterministic fallback or gate
- **RF Generator:** regex fallback on LLM failure (100% uptime — though not equivalent output).
- **5G pipeline:** below the 0.65 threshold, returns *nothing* rather than a guess.
- **Prompt Regression Suite:** Tier 0 rule-based checks run before any paid/probabilistic tier, and fail-fast skips the rest.
- **EMS 2.0:** a deterministic resume-quality gate (score ≥ 40) runs *before* the LLM is ever called.
- **Bias Auditor:** ANOVA/Cohen's d (deterministic statistics) sit alongside the LLM judge, not in place of it.

### 3. Additive, non-destructive change to existing systems
- **Brane:** new state lives entirely in **sibling tables** (`_agent` suffix); canonical tables get only nullable additive columns. Feature is fully reversible.
- **NFTRACE / RF Generator:** integrate into Nokia's existing CI/CD (NCD) and RF ecosystem without replacing them.
- **Prompt Regression Suite:** baseline governance (3-rule policy) never silently overwrites — PR runs are comparison-only, resets require a documented reason.

### 4. Async + concurrency cap is the default execution shape
Every project that fans out API calls uses the same pattern: **`asyncio` + a semaphore**, never unbounded concurrency.
- Brane (gRPC gateway, stateless horizontal scaling), Bias Auditor (`llm_executor.py`), Prompt Regression Suite (`Runner`), LLM Eval Framework (Celery concurrency=4 + Redis broker) all cap in-flight calls rather than firing everything at once — explicitly to avoid rate-limit failures *and*, in the Bias Auditor's case, to avoid silently unbalancing a statistical sample.

### 5. One typed data contract per system, not per-layer translation
- **Brane:** every layer reads/writes the same PostgreSQL sibling-table shapes.
- **5G pipeline:** `ExtractedError` / `RemediationResult` dataclasses cross every stage boundary.
- **Bias Auditor:** the single `BiasReport` Pydantic model is consumed unmodified by the CLI, API, dashboard, and PDF generator.
- **Prompt Regression Suite:** `TestCase → AssertionResult → TestResult → SuiteRun`, fully typed Pydantic, no raw dicts crossing a layer boundary.
- **LLM Eval Framework:** the same `TestCase`/`EvalResult` Pydantic models are shared by the API, the Celery worker, and the dashboard.

### 6. Multiple interfaces over one core engine
Nearly every project exposes the same logic through 2–4 surfaces rather than duplicating it: **CLI + REST API + Streamlit dashboard** (Bias Auditor, Prompt Regression Suite, LLM Eval Framework), or **API + UI** (5G pipeline: FastAPI + Streamlit; RF Generator: FastAPI + Streamlit; EMS 2.0: FastAPI + React). The dashboard, where present, reads the database directly rather than going through the API — an explicit decoupling so the analytics view works even if the API process is down (Prompt Regression Suite, LLM Eval Framework).

### 7. RAG over fine-tuning, whenever domain knowledge changes faster than a training cycle
- **5G pipeline:** Qdrant + LangChain RetrievalQA — the knowledge base grows from every resolved unknown error.
- **EMS 2.0:** FAISS vector store over parsed resumes.
- **Bias Auditor / Prompt Regression Suite:** local `sentence-transformers` embeddings (`all-MiniLM-L6-v2` in both) for zero-cost, zero-network semantic comparison — the same model, chosen independently in two different projects for the same reason (cheap, fast, no external dependency on the hot path).

### 8. Local-first / privacy-aware where the data is sensitive
- **EMS 2.0:** Ollama runs locally — resume data never leaves the machine, a deliberate choice over OpenAI/Anthropic.
- **Expense Tracker:** file itself never leaves the browser (though the *extracted text* does — see the flagged claim gap below).
- **Bias Auditor:** supports Ollama as a third provider specifically so an audit can run with no data leaving the org.

### 9. Structured output is coerced and validated, never trusted raw
- **Brane:** `ResponseParser` schema-validates and repairs malformed LLM JSON; a parse failure becomes a *failed attempt* that re-enters the correction loop, not a crash.
- **Prompt Regression Suite:** the judge prompt forces the response to *begin* with `{` specifically to make malformed output detectable; parser handles markdown code-fencing gracefully.
- **RF Generator:** LLM-extracted entities flow through a deterministic template and a syntax-validating parser before being trusted.
- **EMS 2.0:** LLM JSON output is Pydantic-validated before it's allowed into PostgreSQL.

### 10. Cost-aware model routing (cheap model / free tier first, expensive model only when needed)
- **5G pipeline:** Haiku on confident matches, Sonnet on ambiguous or critical ones.
- **Prompt Regression Suite:** Tier 0 (free) → Tier 1 (free, local) → Tier 2 (paid judge) fail-fast ordering.
- **RF Generator:** deterministic template fill before any LLM involvement in later stages.

---

## The one thing every project's architecture is actually arguing

Say this if asked "what's the throughline across your projects":

> "None of these treat an LLM's output as trustworthy the moment it's produced. Every one of them puts a deterministic or independent check between generation and anything that acts on the result — a threshold, a parser, a separate verifier, a blinded judge, a human gate. The interesting engineering was never making the model right. It was designing for what happens when it's wrong."

---

## Known gaps / claims to reconcile before quoting stack items verbatim

- **5G pipeline:** resume says "Redis caches frequent error lookups" — not present in this deep-dive.
- **Expense Tracker:** resume says "100% private... no data leaves your device" — the deep-dive confirms extracted transaction *text* is POSTed to Google's Gemini API. The *file* stays local; the *contents* do not.
- **Prompt Regression Suite:** "~50% cost reduction" is stated as an *estimate* in the source, not a measured figure, and only holds when tests fail (fail-fast saves nothing on an all-passing suite).
- **NFTRACE:** "50% reduction in pipeline validation time" is asserted with no stated methodology in the source.

(Full detail on each in the respective `*_Interview_QA.md` files in this folder.)
