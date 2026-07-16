# Resume Projects — Complete Concept & Technique Cheatsheet

> Every skill, library, technique, pattern, and function you used to build each project on your resume.
> **How to use:** read a project's rows; if you can't explain a term in one sentence, that's a study gap.
> Order: Work Experience first, then Key Projects. ★ = strongest interview talking point.

---

## MASTER SKILL INDEX (the union — what all your projects prove)

**Languages:** Python · JavaScript/JSX · TypeScript · SQL · Bash
**Backend/API:** FastAPI · gRPC · Pydantic v2 · SQLAlchemy 2.0 async · Celery · Typer · Rich · Streamlit · Node.js · XML-RPC · REST
**AI/LLM:** RAG · LangChain (RetrievalQA) · embeddings · vector search · prompt engineering · grounding · LLM-as-judge · hallucination detection (NLI) · faithfulness · agentic loops · tool calling · MCP · multi-provider routing · structured JSON + repair · guardrails · local inference (Ollama)
**Data/DB:** PostgreSQL · MongoDB/GridFS · Redis · SQLite · FAISS · Qdrant · Alembic · localStorage · polyglot persistence
**Concurrency:** asyncio · asyncio.Semaphore · Celery workers · multiprocessing.Pool · threading (daemon) · GIL awareness
**Stats/ML:** ANOVA · Cohen's d · cosine/Jaccard similarity · VADER · DistilBERT · sentence-transformers · TF-IDF
**Frontend:** React 18 · Vite · Tailwind · Astro SSG · WASM (Tesseract.js) · pdf.js/canvas · IntersectionObserver · Recharts/Plotly
**Infra/CI:** Docker · Docker Compose · GitHub Actions · Vercel · nginx · CDN · Slack webhooks
**Testing:** pytest · MagicMock · httpx async client · 3-tier testing · golden suites · flakiness detection
**Telecom domain:** 5G Core (AMF/AUSF/gNB/UPF/SMF) · NAS/NGAP/RRC · Diameter · SIP/IMS · pcap/Pyshark · 3GPP SBI · Robot Framework · Nokia NCD/TAF

---

# WORK EXPERIENCE

## ★ Brane Enterprises — AI Agent Runtime (agentic AI, most senior work)

- **Languages:** Python · SQL (PostgreSQL DDL/DML)
- **Frameworks/libraries:** FastAPI · Pydantic · SQLAlchemy · gRPC (grpcio, grpcio-tools, protobuf) · jsonschema (tool param validation) · MCP / FastMCP-style server
- **AI/LLM techniques:** agent loop (assemble → invoke → parse → verify → loop) · retry-with-feedback correction loop · **verifier lane** (deterministic → AI → human, short-circuit) · tool/function calling (pre-registered NFs, grant-checked) · prompt assembly (system + grounded input injection + tool-registry context) · response parser hardening (malformed LLM JSON) · **MCP server + verb-based agent routing** · multi-provider routing (instruct/thinking/vision) · conversational feedback loop
- **Data/DB:** PostgreSQL schema design — agent identity, LO↔agent junction, sibling execution tables (`lo_input_execution_agent`), attribute-permission rows · partial unique index (one primary agent per LO) · additive nullable columns (`permitted_sources`) · JSONB columns · three memory layers (scratch / episodic / distilled-RAG)
- **System-design patterns:** ★probabilistic-core / deterministic-gate · attribute-level RBAC (+ per-instance cache) · sibling-table strategy (additive, reversible) · facade / single delegation point · registry (tool registry) · in-place attempt_seq audit · mirror-to-canonical · saga/outbox (named as the cross-store consistency fix)
- **Concurrency:** gRPC model gateway (stateless, horizontal scale) · thread-pool offload for sync work
- **gRPC gateway:** one gateway fronts all providers · HTTP/2 binary · routes by model_class · port 50051 · observability metrics (`ai_agent_run_total`, `ai_gateway_latency_ms`)
- **MCP routing:** verbs (generate_image/extract/classify/…) → agent · most-specific match (exact→tenant→global→default) · context predicates (region) · exposed as MCP server (`resolve_agent`)
- **Key config/funcs:** `AgentLoopController.execute()` · `AttributeRBAC.can_read()` (cached) · `ToolExecutor.execute()` · `VerifierService.verify()` · iteration_max (default 5) · fallback on cap exhaustion
- **Design decisions:** verifier separate from generator (can't self-certify) · in-place attempts not versioned LOs · attribute RBAC over object-level · sibling tables never alter canonical · verb routing over pinning models · pre-registered tool whitelist
- **★ For Mphasis JD:** agentic + multi-agent, MCP/FastMCP, prompt engineering, guardrails, RBAC/secure REST, gRPC, microservices, Postgres.

## ★ 5G Failure-Detection & Remediation Pipeline (RAG + telecom)

- **Languages:** Python
- **Frameworks/libraries:** Pyshark (FileCapture) · Qdrant (qdrant-client) · LangChain (RetrievalQA, PromptTemplate, QdrantVectorStore) · langchain-anthropic (ChatAnthropic) · langchain-openai (OpenAIEmbeddings) · sentence-transformers · FastAPI (UploadFile) · Streamlit
- **AI/LLM techniques:** ★RAG · embeddings (ada-002, 1536-dim) · ★metadata pre-filtering (vendor/layer before similarity) · grounding · confidence-based model routing (Haiku vs Sonnet, 3-boolean heuristic) · score-threshold hallucination guard (0.65) · temperature=0.1 determinism · `return_source_documents=True` for trust · self-improving KB (unknown-errors collection)
- **Data/DB:** Qdrant (HNSW index, cosine distance, PointStruct/upsert, Filter/FieldCondition/MatchValue) · Docker-hosted (localhost:6333) · metadata payload (vendor/layer/severity/error_code/fix)
- **System-design patterns:** filtered semantic retrieval · model cost-routing · feedback loop · FastAPI file-upload wrapper (tempfile + cleanup)
- **Telecom:** pcap parsing · protocol-layer detection via `hasattr` (NAS/NGAP/RRC/Diameter/SIP/GTP) · NAS 5GMM/5GSM cause codes · Diameter result codes · SIP status codes · vendor signatures (Nokia/Ericsson/Huawei) · timers (T3560/T3502) · 5G-AKA
- **Key config/funcs:** `extract_errors_from_pcap()` (display_filter, keep_packets=False) · `search_similar_errors()` (query_filter, score_threshold) · `build_qa_chain(vendor, layer)` · `should_use_fast_model()` (score>0.92, gap>0.15, non-critical) · `POST /analyze`, `/index`, `/health`
- **Design decisions:** Qdrant over FAISS (DB-level filtering) · LangChain over manual (source docs + swappability) · cosine over euclidean · temp 0.1 for consistency
- **Gaps:** confidence parsed by string-match (not JSON mode) · scaling (Celery/sharding) hypothetical · no PII handling for IMSI · metrics (70%/55%) lack stated baseline
- **★ For Mphasis JD:** RAG, grounding, prompt engineering, information retrieval, FastAPI, document-centric.

## NFTRACE — Distributed test-trace platform (microservices + telecom)

- **Languages:** Python · SQL (SQLite) · Bash/subprocess
- **Frameworks/libraries:** FastAPI · Pydantic · redis-py · sqlite3 (stdlib) · xmlrpc.client (stdlib) · multiprocessing.Pool · Pyshark · requests (SDK) · Robot Framework (BuiltIn, keyword lib) · contextlib.contextmanager · uuid · subprocess
- **AI/LLM techniques:** none (no LLM — contrast with RF-gen)
- **Data/DB:** Redis `setex` 1h TTL (`session:{id}`, JSON blobs) · SQLite 3-table schema (sessions/nodes/validation_results) with FK · `INSERT OR REPLACE` · `sqlite3.Row` · two-tier hot(Redis)/cold(SQLite) · pcap on filesystem (path in DB, not BLOB)
- **System-design patterns:** ★session isolation (UUID per worker) · facade (REST shields legacy XML-RPC) · hot/cold storage split · client SDK pattern (NFTraceClient) · graceful degradation (per-node try/except) · context-manager convenience (`run_full_trace` yield/finally) · CI/CD lifecycle hooks (pre/post_test) · tag-based node resolution
- **Concurrency:** `multiprocessing.Pool(processes=len(nodes))` · `pool.starmap` parallel fan-out · explicit asyncio rejection (sync XML-RPC) · ceiling 5–10 nodes
- **Telecom/protocols:** XML-RPC (`ServerProxy`, `proxy.trace.start/stop/collect`) · `mergecap` via subprocess · SIP validation (REGISTER→200 OK, rule SIP_001) · Diameter (cmd_code 318 AIR, DIA_001, 2s AIR/AIA timing) · 5G NFs (gNB/AMF/UPF/SMF/AUSF) · scenario `UE_Registration_5G_AKA`
- **Testing/CI:** 3-tier (unit: test-Redis/SQLite/mock-XML-RPC/synthetic pcap · integration: httpx vs FastAPI test mode · e2e: weekly real testbed in NCD) · Nokia NCD hooks · TAF (Robot Framework execution) · test tagging
- **Key config/funcs:** `POST /sessions/start|stop|merge|validate` · `NodeManager` methods · `ProtocolValidator._validate_sip/_validate_diameter` · session states STARTING→ACTIVE→…→VALIDATED · TTL 3600s · pass_rate = passed/total×100
- **Design decisions:** FastAPI over Flask/Django (Pydantic + OpenAPI + ASGI) · Redis hot vs SQLite cold (access pattern) · XML-RPC isolated behind NodeManager (external constraint) · multiprocessing over asyncio (small testbed) · SQLite over Postgres (single-server) · pcap on FS not BLOB (50–200MB)
- **Gaps:** no async node ops (>10 ceiling) · validation post-processing not real-time · no web dashboard · single-server SQLite

## RF Keyword Generator — NL→test-code (hybrid LLM + telecom)

- **Languages:** Python
- **Frameworks/libraries:** Streamlit · FastAPI · Pydantic (response_model) · Anthropic SDK (`client.messages.create`) · `robot.api.get_model` (RF parser as library) · requests · `re` · tempfile · json · httpx · pytest
- **AI/LLM techniques:** ★structured JSON extraction with per-procedure schemas · explicit output-format rules (return-only-JSON, null-for-missing, don't-invent) · ★model right-sizing (Haiku over Sonnet, 3-5× cheaper, ~500ms) · ★hybrid regex+LLM (regex baseline, LLM upgrade, regex fallback on `JSONDecodeError`) · `apply_defaults()` backfill · (proposed) Redis cache keyed (description, procedure)
- **Data/DB:** none persistent · FastAPI request logs as ad-hoc analytics · proposed Redis memoization cache
- **System-design patterns:** frontend/backend split (Streamlit/FastAPI) for testability/scaling · 4-stage pipeline (detect → extract → fill → validate) · templates-as-data (new procedure = dict entry, no code) · regex fallback (graceful degradation) · ★validation via target runtime's own parser (RF parser, not hand-rolled)
- **Concurrency:** fully synchronous now · async + worker-pool proposed (not built)
- **Telecom:** RF `.robot` syntax (`*** Settings/Test Cases/Keywords ***`, `[Arguments]`, `${var}`, `...` continuation, case-sensitive RETURN) · Nokia libs (5GCoreLibrary/AMFLibrary/AUSFLibrary) · 3GPP SBI endpoints (`/namf-comm/v1/ue-contexts`, `/nausf-auth/v1/ue-authentications`) · procedures (UE Registration, 5G-AKA/EAP-AKA, Handover, PDU Session, Deregistration) · IMSI 15-digit regex · interfaces (N1-N9/S1-U/X2/Xn) · DNN/APN · PDU types
- **Testing/CI:** 3-tier (unit per stage · integration httpx vs FastAPI · informal 5×20 user testing) · RF parser as in-request syntax gate
- **Key config/funcs:** `POST /generate` (robot_content, params_extracted, procedure_detected) · `detect_procedure()` · `extract_params_regex/_with_llm()` · `fill_template()` (`str.format`, `{{`/`}}` escaping) · `validate_robot_syntax()` (tempfile + get_model + finally cleanup) · `claude-haiku-4-5`, max_tokens=300 · HTTP 400/422/500 · timeout=15
- **Design decisions:** templates over full-LLM-gen (deterministic correctness + cost) · RF parser reused as validator · Haiku right-sized · "why not Copilot" (domain libs + non-coder UX) · regex fallback = honest 100% uptime
- **Gaps:** no caching · synchronous (bottleneck ~500 users) · only 5 of ~15-20 procedures · placeholder defaults (no subscriber DB) · no VCS auto-commit

---

# KEY PROJECTS

## ★ LLM Evaluation Framework (JD: "evaluations and safety guardrails")

- **Languages:** Python
- **Frameworks/libraries:** FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · asyncpg · Alembic · Celery · Redis · httpx async · Streamlit · Plotly · transformers · torch · sentence-transformers
- **AI/LLM techniques:** ★LLM-as-judge (5-dim rubric: accuracy/relevance/completeness/clarity/safety, 1-5 → 0-1 normalization) · ★claim-level NLI hallucination detection (SUPPORTED/UNSUPPORTED/CONTRADICTED) · RAG faithfulness (grounded vs context-leaked) · multi-run consistency · structured JSON enforcement · PASS/REVIEW/FAIL verdicts
- **Data/DB:** PostgreSQL 16 · JSON column (`eval_scores`, schema-less extensibility) · Redis (broker + result backend)
- **System-design patterns:** ★registry/factory (evaluators + LLM clients) · ABC interfaces (`BaseEvaluator.evaluate()`, `BaseLLMClient.complete_json()`) · ★broker/worker (FastAPI→Redis→Celery) · independent evaluators + AND-logic composite (no weighted avg) · lazy model loading
- **Concurrency:** async FastAPI + async SQLAlchemy + asyncpg · async DB session DI · Celery concurrency=4 · retries (3×, 30s) · pool sizing (10 + 5 overflow)
- **Stats/ML:** cosine + Jaccard fallback · `all-MiniLM-L6-v2` (80MB) · `cross-encoder/nli-deberta-v3-base` (400MB) · mean pairwise sim + std-dev
- **Testing/CI:** golden-suite regression gating · curl/pytest CI pattern
- **Infra:** Docker Compose (5 services, health-check ordering) · Slack webhook alerts · `X-API-Key` auth
- **Key config/funcs:** `POST /api/test-cases`, `GET /api/results`, `/api/dashboard`, `/health` · thresholds (judge 0.60, hallucination 0.75, faithfulness 0.80, consistency 0.85) · CONSISTENCY_RUNS=5 · JUDGE_MODEL=claude-haiku · norm formula `(x−1)/4`
- **Design decisions:** async-first (5-30s evals can't block) · Celery over BackgroundTasks (durability/retry) · registry as sole extensibility · local-model fallback for cost · AND-logic so no failure masked
- **★ For Mphasis JD:** evaluations, guardrails, async/event-driven-adjacent, FastAPI, Docker, microservices, MongoDB-adjacent (JSON).

## ★ Prompt Regression Suite (JD: CI/CD + evaluations)

- **Languages:** Python 3.11
- **Frameworks/libraries:** FastAPI · Pydantic v2 (`model_validator`) · SQLAlchemy 2.0 async · Typer · Rich · Streamlit · Plotly · sentence-transformers · Anthropic SDK · OpenAI SDK · Ollama (httpx) · GitHub Actions
- **AI/LLM techniques:** ★tiered assertion pipeline (rule → semantic → LLM-judge, fail-fast) · LLM-as-judge (4-dim weighted: instruction 0.40/accuracy 0.30/format 0.20/tone 0.10) · forced JSON ("begin with {") · ★client-side score recomputation (distrust judge math) · ★anti-self-bias routing (judge ≠ model-under-test provider) · critical_failure flag (<0.40) · graceful degradation on parse fail · multi-run averaging · flakiness (std-dev >0.05)
- **Data/DB:** SQLite (dev) / PostgreSQL (prod, one env var) · SQLAlchemy async · 4 tables · JSON assertion configs
- **System-design patterns:** six-layer architecture · ★forward + reverse index (selective CI) · factory (LLM routing by name prefix) · fail-fast ordering · ★three-rule baseline governance · delta-based (relative) regression · stable ID derivation
- **Concurrency:** `asyncio.Semaphore` (default 10) · async Runner · lazy singleton via `lru_cache`
- **Stats/ML:** cosine · 384-dim · Flesch-Kincaid readability · weighted mean · std-dev
- **Testing/CI:** ★GitHub Actions (`pr-regression.yml`, `weekly-drift.yml`) · `git diff --name-only` selective · PR comment bot · exit-code merge gate · `prs validate` zero-cost check
- **Key config/funcs:** `Registry.affected_by()`, `.should_run_full_suite()` (>30%) · `BaselineManager.force_reset()` (ValueError on empty reason) · delta_threshold 0.05 · run_count 3 · 12 rule types (contains_keyword, max_words, valid_json, regex_match, reading_level, …) · CLI (`prs run --affected/--tag/--update-baselines`) · judge temp=0.0
- **Design decisions:** cheapest-first (~50% cost cut) · delta not absolute thresholds · PR runs never write baseline (main does) · anti-self-bias enforced in `Runner.__init__` · weekly full-suite catches provider drift
- **★ For Mphasis JD:** CI/CD (GitHub Actions), evaluations, Pytest discipline, tiered cost control.

## Bias & Fairness Auditor (JD: guardrails + banking/lending fairness)

- **Languages:** Python
- **Frameworks/libraries:** FastAPI · Pydantic Settings · SQLAlchemy async · Streamlit · Plotly · Anthropic SDK · OpenAI SDK · httpx · SciPy · fpdf2 · Docker Compose · VADER · sentence-transformers · transformers (DistilBERT)
- **AI/LLM techniques:** ★counterfactual fairness testing (placeholder substitution, Cartesian demographic matrix) · ★blind LLM-judge (labels stripped) · multi-run sampling · severity→score mapping · prompt-rewrite remediation · EU AI Act Article 13 doc generation
- **Data/DB:** SQLAlchemy async · SQLite/PostgreSQL · JSON matrices · `BiasReport` Pydantic model as universal cross-layer contract
- **System-design patterns:** six-layer (variant → execute → 4 parallel analyses → composite → orchestrate → enrich) · stateless independent pipelines · single Pydantic contract (CLI/API/dashboard/PDF, zero translation) · two-layer fallback (VADER→DistilBERT; embeddings→TF-IDF)
- **Concurrency:** `asyncio.gather` · `asyncio.Semaphore` (default 10)
- **Stats/ML:** ★ANOVA (p<0.05) · ★Cohen's d effect size · VADER · DistilBERT (sst-2) · MiniLM 384-dim · TF-IDF char-bigram cosine · within vs between-group similarity gap · structural heuristics · weighted composite (semantic 35/sentiment 30/structural 10/judge 10/length 15-reserved)
- **Infra:** Docker Compose (3 services) · fpdf2 `_safe()` Latin-1 encoder · CLI + REST (`/audits`, `/matrices`, `/reports`)
- **Key config/funcs:** bands (0-20 Pass/21-40 Review/41-60 Concern/61-100 Fail) · vader_neutral 0.2 · max_pairs 6 · sentiment/semantic/structural bias formulas · built-in matrices (gender_names_india/global, age_groups, religion_india, intersectional_hiring)
- **Design decisions:** BiasReport single contract · VADER-first/DistilBERT-fallback (cost) · blind judge (prevent judge's own bias) · fpdf2 (no OS binary deps) · length weight reserved but excluded (known config/impl mismatch)
- **Gaps:** no CI mentioned · length-weight bug (sums 0.85) · only 2D intersectionality · thresholds are standard defaults
- **★ For Mphasis JD:** guardrails, ML/NLP, statistics, regulated/banking-lending domain fit.

## EMS 2.0 (JD: MongoDB + RAG + document-centric)

- **Languages:** Python (backend) · JavaScript/JSX (frontend)
- **Frameworks/libraries:** FastAPI · React · Vite · SQLAlchemy · Pydantic v2 · pdfplumber · pytesseract · FAISS · sentence-transformers
- **AI/LLM techniques:** ★RAG (chunk 500/100 → embed → top-5 FAISS → grounded) · ★multi-strategy JSON parse/repair (direct → regex extract → cleanup → key-value) · intent classification (keyword-first → LLM) · session memory + pronoun resolution · 5 anti-hallucination guards · multi-query decomposition · deterministic inference (temp=0, seed=42)
- **Data/DB:** ★polyglot persistence — PostgreSQL (structured, SQLite fallback) + MongoDB GridFS (files) + FAISS (vectors) · flat-file job status (JSON, not DB polling)
- **System-design patterns:** polyglot persistence · 7-layer validation pipeline · all-responses-through-LLM · privacy-by-design (local Ollama) · job-status files over DB polling · zero-padded sequential IDs
- **Concurrency:** `threading.Thread(daemon=True)` (chosen over BackgroundTasks — blocking subprocess/HTTP) · frontend async polling (`GET /api/job/{id}`)
- **Frontend:** polling UI · chat state (`App.jsx`) · multipart file upload
- **Testing/CI:** not mentioned (gap)
- **Infra:** Ollama (`localhost:11434/api/generate` + CLI subprocess fallback) · GPU tuning (RTX 3060 6GB: qwen2.5:14b too big → 7b-instruct)
- **Key config/funcs:** `OllamaAdapter` · temp=0, num_predict=2048, num_ctx=4096, seed=42 · `qwen2.5:7b-instruct` · `all-MiniLM-L6-v2` · `process_cv()` · resume scoring (headers 35/keywords 25/contact 25/dates 15, threshold ≥40) · pdfplumber + pytesseract OCR · `re.search` vs `re.match` (anchored-regex bug fix) · `setattr` update CRUD
- **Design decisions:** local LLM (privacy/cost, 5-30s latency) · all interactions through LLM (natural responses) · daemon threads over BackgroundTasks · flat JSON job status · lenient OCR threshold (15%)
- **Gaps:** duplicate detection disabled · no auth/JWT · no rate limiting · in-memory session (lost on restart) · single-node FAISS · no streaming · no Postgres-FAISS transactional consistency · ~10-20% JSON parse fail · 4400-line chat handler
- **★ For Mphasis JD:** MongoDB, RAG, document processing, concurrency, (study Mongo aggregation to deepen).

## Financial Statement Parser (JD: document-centric + banking)

- **Languages:** JavaScript (React) · Docker/shell
- **Frameworks/libraries:** React 18.2 · Vite 5 · Tailwind 3.4 · Tesseract.js 5 · pdf.js (pdfjs-dist) · Recharts · SheetJS (xlsx) · jsPDF + autotable · html2canvas · file-saver · Lucide React
- **AI/LLM techniques:** Google Gemini 2.5 Flash · structured extraction (14 categories + fixed/variable) · `responseMimeType:'application/json'` forced JSON · temp 0.1 · ★three-method JSON salvage (fence strip → bracket boundary → truncation repair) · token cap (8000 chars) · BYOK · live key validation
- **Data/DB:** none server-side · localStorage (key, base64+reverse obfuscation — NOT encryption) · in-memory JS transaction object as single contract
- **System-design patterns:** ★privacy-by-design / client-side-only (file never leaves browser) · stateless/serverless (BYOK) · single shared data contract · ★processing state machine (idle→reading→ocr→extracting→complete/error) · closure-staleness fix (snapshot state to local var)
- **Concurrency:** async OCR progress normalization (PDF 0-30%, OCR 30-100%) · async multi-page loop · async fetch + HTTP-status→message mapping (400/429)
- **Frontend:** `useState` state machine · ★WASM (Tesseract.js in Web Worker) · canvas (`toDataURL`) PDF→image · drag-drop · inline-editable sortable table · html2canvas 2× density chart capture · CDN-loaded pdf.js worker
- **Testing/CI:** not mentioned (gap)
- **Infra:** static build → Vercel · Docker multi-stage (node:18-alpine → nginx:alpine)
- **Key config/funcs:** `Tesseract.recognize()` · `pdfToImages()` · Gemini `gemini-2.5-flash:generateContent` · maxOutputTokens 16384 · `calculateStats()` (burn rate, Pareto category totals, fixed/variable) · `processFileInternal(file, updateStatus=true)`
- **Design decisions:** OCR-then-text-only (privacy > simplicity vs multimodal upload) · BYOK (no hosting cost/liability) · 3-method salvage (partial > fail) · updateStatus flag (silent sub-process, "Add More" bug fix) · html2canvas (jsPDF can't render React/SVG)
- **Gaps:** key obfuscation ≠ encryption · no backend/rate-limit · large statements truncate · no tests · English-only OCR
- **★ For Mphasis JD:** document/OCR (Document AI parallel), extraction, React consumer.

## Blog — Astro Documentation Engine (frontend/build pipeline)

- **Languages:** JavaScript (ES2020) · TypeScript (env.d.ts) · CSS
- **Frameworks/libraries:** Astro 3.5+ · @astrojs/tailwind · Tailwind 3.3+ · @tailwindcss/typography · PostCSS + Autoprefixer · vanilla JS (no client framework)
- **AI/LLM techniques:** none
- **Data/DB:** none · localStorage (dark-mode pref) · build-time embedded JSON search index (`<script type="application/json">`)
- **System-design patterns:** ★zero-runtime-server / SSG · ★build-time vs runtime separation (`import.meta.glob()`) · filesystem-as-navigation (folder = URL = sidebar) · catch-all dynamic routing (`getStaticPaths()`) · Astro named slots · DOM-cloning for mobile nav
- **Concurrency:** none (synchronous build + independent client scripts)
- **Frontend:** ★`import.meta.glob()` (eager, build-time discovery) · IntersectionObserver scroll-spy (`rootMargin -80px 0 -80% 0`) · debounced search (150ms) · ★weighted client-side search (title +10/heading +5/excerpt +2) + regex highlight + `escapeHtml()` XSS guard · native `<details>/<summary>` · CSS `scroll-padding-top` · pre-paint dark-mode sync (no FOUC) · `buildTree()` flat→nested · frontmatter metadata
- **Testing/CI:** not mentioned; GitHub Actions planned
- **Infra:** static `dist/` → any CDN (Cloudflare/GitHub Pages/Netlify/Vercel)
- **Key config/funcs:** `Sidebar.astro` (`fileToRoute()`, `buildTree()`, `isActive()`) · `[...slug].astro` `getStaticPaths()` · `TableOfContents.astro` IntersectionObserver · `--navbar-height: 4rem`
- **Design decisions:** per-page embedded index (no request, always synced) vs fetched · no search library (~80 lines vanilla) · native `<details>` over JS accordion · DOM clone over shared state
- **Gaps:** shallow search (200-char excerpts) · no auth · sidebar 2 levels · index grows linearly · no image optimization · no tests/CI
- **For Mphasis JD:** frontend/React-adjacent, build pipelines (least relevant — mention if asked).

---

*Built by reading all project deep-dive reports in full. Every term is something an interviewer could ask you to explain — if you can't, study it. Lead with the ★ projects (Brane, 5G, LLM Eval, Prompt Regression) for the Mphasis Python-GenAI-FastAPI role; they carry the agentic-AI, RAG, evaluations, MCP, FastAPI, and CI/CD evidence the JD wants.*
