# Section 3 — Project Explanations for the Interviewer

*Format per project: first, **the explanation** — what the project is and does, said plainly for the interviewer's ears (no story, no drama, just what it is). Then **the terms** — every technical point I'll naturally say during that explanation, each with a 2-line definition, because the moment I say "attribute-level RBAC" or "junction table" the interviewer will stop me and ask "what's that." I want an answer ready for every phrase that leaves my mouth.*

**Projects:** 3.1 Brane AI Agent Runtime · 3.2 5G Failure Detection Pipeline · 3.3 LLM Evaluation Framework · 3.4 Prompt Regression Suite · 3.5 Bias & Fairness Auditor · 3.6 NFTRACE · 3.7 RF Keyword Generator · 3.8 EMS 2.0 · 3.9 Financial Statement Parser · 3.10 Blog

---

## 3.1 Brane AI Agent Runtime

### The explanation

At Brane I contributed to the production AI-agent runtime that powers a no-code platform — users build AI agents on the platform, and the runtime is what actually executes those agents. I worked across four areas: the PostgreSQL schema for the agent system, the LLM inference layer through a gRPC model gateway, the agent loop itself (prompt assembly and the correction loop), and performance hardening. On the database side I built the agent identity, permission, and execution-tracking tables. On the inference side I integrated a gRPC gateway that routes to different model types with stateless horizontal scaling. On the loop, I engineered how the prompt is assembled each turn and a retry-with-feedback mechanism so the agent self-corrects. And I hardened it for production — caching permission checks, cutting tool overhead, and making the response parser survive malformed LLM output. It was a single-agent runtime, not multi-agent orchestration.

### The terms

- **Agent identity tables** — PostgreSQL tables that store each agent's definition and identity (who the agent is, its configuration). They're the canonical record the runtime looks up to instantiate and run a given agent.
- **Multi-agent LO junction tables** — A junction (bridge) table modeling the many-to-many relationship between agents and "LOs" (logical objects they operate on). Each row links one agent to one logical object, so an agent can act on many objects and an object can be shared by many agents.
- **Attribute-level RBAC permission rows** — Role-Based Access Control defined down to individual attributes, not just broad roles. Each row grants or denies access to a specific attribute, so an agent/user can be allowed some fields of an object but not others.
- **Agent execution sibling tables** — A set of related tables that track a run: `lo_input_execution_agent` (which agent/input drove an execution), `agent_run_scratch` (the run's working state), and `agent_episodes` (its step history). Together they persist a run so it survives restarts and can be replayed for debugging.
- **gRPC model gateway** — An internal service the agent loop calls to run model inference, using gRPC (binary protobuf over HTTP/2). It sits between the agent and the LLM providers so the agent doesn't talk to any provider directly.
- **Multi-provider model routing (instruct / thinking / vision)** — The gateway routes each request to the right model variant — instruction-following, deep-reasoning, or image-capable — and to the right provider. The agent just asks for a capability; the gateway picks the model.
- **Stateless horizontal scaling** — The gateway holds no per-request state, so any instance can handle any request and you scale by adding more instances behind a load balancer. State lives in the DB/cache, not in the gateway process.
- **Prompt assembly (agent loop)** — Building the prompt fresh each turn from parts: the system prompt, the current grounded input, the available-tools context, and any correction feedback. It's the step that turns the agent's current situation into text the model can act on.
- **Grounded input injection** — Inserting real, retrieved data into the prompt so the agent reasons from actual context instead of making things up. It's the anti-hallucination anchor for the agent's decisions.
- **Tool registry context** — The catalog of tools the agent can call — each tool's name, purpose, and input schema — injected into the prompt so the model knows its options and how to call them. Decoupled from the loop, so adding a tool is data plus a function, not a rewrite.
- **Retry-with-feedback / verifier correction loop** — After the agent produces output, a verifier validates it; on failure it feeds the specific failure back into the prompt and re-prompts, so the agent fixes its own mistake. It's bounded by a retry cap so it can't loop forever.
- **Attribute-RBAC caching** — Caching the fine-grained permission checks so they don't hit the database on every tool call or attribute access. Needed because attribute-level checks are frequent and would otherwise hammer the DB on the hot path.
- **Tool invocation overhead** — The per-call cost of the agent invoking a tool (setup, dispatch, result handling). I reduced it so each tool call in the loop was cheaper.
- **Response parser hardening (malformed LLM output)** — Making the code that parses the model's output tolerate almost-JSON — trailing commas, stray markdown fences, wrong types — instead of crashing. Necessary because LLMs return malformed structured output a meaningful fraction of the time.
- **Single-agent vs multi-agent** — This was one agent running in a loop with tools, not several specialised agents coordinating under a supervisor. I built the primitives multi-agent systems use, but not the orchestration itself.

---

## 3.2 5G Failure Detection & Remediation Pipeline

### The explanation

This is a RAG pipeline that automates 5G failure diagnosis. When a 5G failure happens, the evidence lives in pcap files — raw packet captures with tens of thousands of messages. Previously an engineer read these by hand in Wireshark, which took hours and depended on individual expertise. My pipeline extracts the error packets automatically with Pyshark, does a filtered semantic search against a knowledge base of known error patterns stored in a Qdrant vector database, and uses LangChain to feed the matched patterns to Claude, which writes a specific, contextual fix. It returns the source patterns alongside the fix so the engineer can see why. Results were 70% auto-resolution of routine errors, 55% MTTR reduction, and analysis time from hours to seconds.

### The terms

- **pcap file** — A packet capture: a binary file recording every network message exchanged, used to diagnose what actually happened on the wire. In 5G it's the raw evidence of a failure.
- **Pyshark** — A Python wrapper around the Wireshark/tshark packet dissector. I use it to open a pcap, filter to error packets, and pull out fields like the error text, vendor, and layer.
- **Signaling errors** — Protocol-level failures in the 5G control plane — authentication timeouts, handover disruptions, congestion. They're the events the pipeline detects and remediates.
- **Display filter** — A Wireshark-style filter applied at capture time so Pyshark only touches the error-relevant packets, not the tens of thousands of irrelevant ones. It massively cuts the work before Python processing.
- **NAS / NGAP / Diameter / SIP (layers)** — The different 5G protocol layers an error can occur in — e.g. NAS for registration signaling, Diameter for authentication, SIP for IMS/voice. I detect which layer an error belongs to because the fix is layer-specific.
- **Vendor / layer metadata** — Structured tags (which vendor's equipment, which protocol layer) stored alongside each error pattern. They're the filter fields that keep, say, Nokia errors matching only Nokia patterns.
- **Embeddings** — Numeric vector representations of text, so that semantically similar errors have similar vectors. I embed the error text to search by meaning rather than keywords.
- **Vector database (Qdrant)** — A database purpose-built to store embeddings and find nearest neighbours fast. I chose Qdrant because it filters by metadata (vendor/layer) at the database level *before* ranking, which FAISS can't do.
- **Cosine similarity** — A similarity measure comparing the angle between two vectors, ignoring magnitude. Correct for text because the same meaning in different lengths still points the same direction.
- **Metadata filtering** — Constraining the vector search to only vectors matching given tags (vendor, layer) before similarity ranking. It's what stops a Nokia error from ever matching an Ericsson fix.
- **LangChain RetrievalQA** — A LangChain component that ties retrieval and generation together: it retrieves the top matching documents and feeds them to the LLM with a prompt, returning the answer plus the source documents.
- **Similarity threshold (0.65)** — A cutoff below which a match is treated as "no good match," so the pipeline returns "unknown — manual review" instead of generating a fix from a weak match. It prevents confident hallucinated advice.
- **Model routing (Haiku vs Sonnet)** — A rule that sends easy, high-confidence errors to the cheaper Claude Haiku and hard/ambiguous/critical ones to the stronger Claude Sonnet. Cut API cost ~60% with no accuracy loss on hard cases.
- **return_source_documents** — A LangChain setting that returns the actual matched patterns alongside the generated fix. Gives the engineer trust (why this fix) and gives me a way to tell whether a bad answer was a retrieval or a generation problem.
- **Temperature (0.1)** — The randomness knob on the LLM; low means near-deterministic. Set low so the same pcap always yields the same fix — consistency matters for operational advice.
- **Redis caching** — Caching frequent error lookups so repeated routine errors serve from memory instead of re-running the full retrieval+LLM path. Contributes to the hours-to-seconds result.
- **MTTR** — Mean Time To Repair: the average time to resolve a failure. Reducing it 55% is the core business metric for the pipeline.

---

## 3.3 LLM Evaluation Framework

### The explanation

This is an automated quality-testing platform for LLM output. The problem it solves is silent degradation — a prompt that works today quietly gets worse after a provider updates the model, and you find out from user complaints days later. You send it a prompt and response via an API; it runs four independent quality checks in the background, stores the scores in PostgreSQL, shows them on a Streamlit dashboard, and fires a Slack alert if any score drops below threshold. In a test, it flagged a 14-point faithfulness drop in under four minutes versus an estimated 2–3 days by hand. It's built async with a Celery worker so evaluations run durably in the background, and it deploys as a single docker-compose command.

### The terms

- **LLM-as-Judge** — Using a strong LLM to score another model's output against a rubric (accuracy, relevance, completeness, clarity, safety), returning structured JSON. It replaces brittle hand-written heuristics that break on novel prompts.
- **Hallucination detector** — Breaks the response into individual factual claims and classifies each against a reference as supported, unsupported, or contradicted; the score is the fraction supported. It catches fabricated claims.
- **Faithfulness scorer** — Measures whether the answer stayed inside the retrieved context, independent of whether it's factually true. Distinguishes a retrieval problem (bad docs) from a model problem (ignoring the docs) in a RAG system.
- **Consistency checker** — Runs the same prompt several times at temperature 0.7 and measures how similar the responses are. Catches prompts that are right once but unreliable on average.
- **Celery worker** — A background task processor that pulls jobs from a queue and runs them independently of the API. Used so an evaluation can't be lost if the API restarts mid-run — durability matters for a CI gate.
- **Task queue (Redis broker)** — Redis holds the queue of pending evaluation tasks that Celery workers pull from. It decouples the API's response time from the 5–30 second evaluation runtime.
- **FastAPI / async** — The web layer; async so the API stays responsive while evaluations run in the background. It accepts the test case, stores it, enqueues the task, and returns immediately.
- **overall_passed (AND logic)** — A test passes only if *every* evaluator passes its own threshold — no averaging. So a well-written answer with one hallucinated fact still fails, because a weighted average would let it slide.
- **Threshold** — Each evaluator has a configured pass/fail cutoff (e.g. faithfulness 0.80). A score below it means fail and, combined with AND logic, fails the whole case.
- **Registry pattern** — Evaluators and LLM clients are registered by name in a factory, so adding a new evaluator is writing a class plus one registry line — no changes to the worker or API. It's the extensibility mechanism.
- **Anti-self-bias routing** — The judge model is always a different provider than the model being tested, so a model doesn't grade its own generation style. Enforced in code, not just documented.
- **SQLAlchemy async / asyncpg** — The async ORM and the fastest async PostgreSQL driver, so database calls don't block the event loop. Keeps the whole stack non-blocking end to end.
- **Streamlit dashboard** — A Python-built web dashboard showing score trends and pass/fail counts, polling every 30 seconds. Gives the team visibility without querying the database directly.
- **Slack webhook** — An incoming webhook URL that the framework posts to when a test fails, summarizing which checks failed. The proactive alert that closes the "it broke vs we noticed" gap.

---

## 3.4 Prompt Regression Suite

### The explanation

This is "pytest for prompts" — a testing framework that treats prompts as code with a test suite. It solves the problem that a prompt change can pass every normal test and still quietly break user-facing behavior, because unit tests check logic, not meaning. Each prompt gets a YAML file describing how it should behave; every pull request that touches a prompt runs those behavioral tests and blocks the merge if quality drops below a stored baseline. The core is a tiered assertion engine that runs cheap deterministic checks first and only pays for an LLM judge when needed, cutting cost ~50%. It integrates with GitHub Actions as a PR merge-gate, plus a weekly run that catches silent model drift.

### The terms

- **Tiered assertion engine** — Evaluates a response through escalating cost tiers: deterministic rules first, local semantic similarity next, paid LLM judge last. Orders checks cheapest-first so most failures cost nothing.
- **Tier 0 (rule-based)** — Deterministic, zero-cost checks — keyword presence, word-count limits, valid JSON, regex match. They catch obvious failures instantly with no API call.
- **Tier 1 (semantic similarity)** — A local sentence-transformer computes cosine similarity between the response and a reference answer (~5ms, no API cost). Catches "means the same thing but worded differently."
- **Tier 2 (LLM-as-judge)** — A paid LLM call scoring the response on a rubric, run only if the cheaper tiers pass. The expensive, last-resort check.
- **Fail-fast** — If a cheap Tier 0 check fails, the engine stops immediately — no semantic check, no judge call. A test failing a keyword check costs zero API budget.
- **Baseline / delta-based regression** — Regression fires when the score drops more than a delta (0.05) below the stored baseline, not against a fixed threshold. Lets baselines rise as prompts improve while still catching drops.
- **Three-rule baseline policy** — Baselines update automatically on merge to main (improvements recognized), never on PR runs (regressions not forgotten), and forced resets require a documented reason (audit trail). The governance that keeps it trustworthy.
- **Selective CI execution / reverse index** — A reverse index maps each prompt file to the test cases using it, so a PR runs only the affected tests — 3 changed prompts of 80 run ~12 tests, not 80. Keeps CI fast at scale.
- **Weekly drift monitor** — A scheduled full-suite run against the live model, independent of code changes. Catches silent provider model updates that shift behavior without any commit.
- **Client-side score recomputation** — The judge's self-reported "overall" is discarded and recomputed from its dimension scores in code. Because LLMs are unreliable at their own arithmetic and I'm gating a PR on that number.
- **Anti-self-bias routing** — The judge is always a different provider than the model under test, enforced at construction. Stops a model favoring output that matches its own style.
- **Multi-run averaging / flakiness** — Each test runs several times and scores are averaged; if the spread (std dev) exceeds 0.05 the case is flagged flaky rather than trusted. Separates a real regression from LLM noise.
- **GitHub Actions (PR merge-gate)** — The CI workflow that runs affected tests on a PR, posts a comment with current-vs-baseline scores, and exits non-zero to block the merge if quality regressed.
- **YAML test config / Pydantic** — Each prompt's behavioral test is a version-controlled YAML file, parsed and validated by Pydantic at load time. Invalid files are logged and skipped, not crash the whole run.
- **sentence-transformers (all-MiniLM-L6-v2)** — A small local embedding model (80MB, ~5ms/pair, zero API cost) used for the Tier-1 semantic similarity. Accurate enough for regression detection without a network call.

---

## 3.5 LLM Bias & Fairness Auditor

### The explanation

This is a tool that tests whether an LLM treats different demographic groups equally on the same task. It uses counterfactual testing — take a prompt with a placeholder like candidate name, swap in every name in a demographic matrix, run each variant many times, and measure whether the outputs differ in tone, content, structure, or quality. It runs statistical tests to separate real bias from random variation, produces a 0–100 bias score with a four-band verdict, and generates a PDF audit report structured for EU AI Act Article 13 compliance. It supports Claude, OpenAI, and local Ollama models and runs via dashboard, CLI, or API.

### The terms

- **Counterfactual fairness testing** — Changing only the demographic signal in an otherwise-identical prompt and comparing outputs, so any difference can only be attributed to that signal. A/B testing for fairness.
- **Demographic matrix / variant generation** — A defined set of demographic values (names, ages, nationalities) substituted into the prompt's placeholders to produce all the test variants. It's the Cartesian product of the demographic dimension and the template.
- **One-way ANOVA** — A statistical test for whether the mean outcome differs significantly across the demographic groups (p < 0.05). Confirms a difference is real, not chance.
- **Cohen's d** — A measure of effect size — how large the difference is in standard-deviation terms, not just whether it's statistically detectable. Needed because with enough runs even a trivial difference becomes "significant."
- **VADER** — A rule-based sentiment scorer, fast and requiring no model download, used as the first-pass tone measure. A DistilBERT transformer is the fallback for ambiguous cases.
- **DistilBERT** — A small transformer sentiment model used when VADER's scores cluster ambiguously neutral. The more accurate but heavier second layer of sentiment analysis.
- **Semantic similarity (sentence-transformers)** — Embedding responses and comparing them to detect whether the *content* differs across groups, not just the tone. Catches substantively different answers.
- **Structural quality** — Heuristics measuring whether responses are longer, more specific, or more complete for some groups — word count, concrete numbers, completeness. Catches "writes more detail for one group."
- **Blind LLM judge** — A second LLM that rates response pairs with all demographic labels stripped, so it can't import its own biases. The qualitative lens that catches implicit assumptions the heuristics miss.
- **Composite score / four-band verdict** — The four lens scores combined into a weighted 0–100 score, mapped to Pass / Review / Concern / Fail. The bands translate a number into an action for a compliance audience.
- **EU AI Act Article 13** — The EU regulation requiring operators of high-risk AI (hiring, lending) to document and explain the system's behavior to regulators. The report is structured to satisfy it as a by-product of the audit.
- **asyncio.Semaphore** — A concurrency cap so the many model calls (e.g. 500 for a 100-variant × 5-run audit) run concurrently but bounded, preventing rate-limit errors. The one control between "fast" and "instantly rate-limited."
- **BiasReport (Pydantic contract)** — A single Pydantic model consumed identically by the CLI, API, dashboard, and PDF generator. Add a field once and it propagates everywhere; any type mismatch is caught at validation.
- **fpdf2** — A pure-Python PDF library (no OS-level binary dependencies) used to generate the audit report. Chosen so the Docker image needs no system packages.

---

## 3.6 NFTRACE

### The explanation

NFTRACE is a distributed REST-based platform for tracing 5G network functions during test automation. The problem: validating network behavior in CI/CD required an engineer to manually start a trace capture on each network node, wait, stop them, collect and merge the files, and validate the protocol by hand — hours per test. NFTRACE turns that into four REST calls: start, stop, merge, validate. It uses Redis for live session state, SQLite for history, and XML-RPC to talk to the nodes. It validates SIP and Diameter protocol behavior, and it's integrated into Nokia's CI pipeline so every tagged test automatically captures and validates traces. It cut pipeline validation time 50%.

### The terms

- **REST-based lifecycle (start/stop/merge/validate)** — The four API operations that manage a trace end to end: begin capturing, stop, merge the per-node files, and validate the protocol. A test worker drives the whole trace through these calls.
- **FastAPI** — The web framework for the REST API, chosen for built-in Pydantic validation, auto OpenAPI docs, and async concurrency — important because multiple test workers hit it simultaneously.
- **Redis session caching** — Stores each active trace session's state in memory with a TTL. Fast, concurrent-safe, and auto-expires orphaned sessions from crashed workers.
- **Parallel execution isolation** — Each session is stored under a unique key so concurrent test workers never collide — one worker's stop can't affect another's trace. The mechanism that makes parallel testing safe.
- **SQLite persistence** — On-disk storage for completed session history and node state, which needs to survive restarts and is queried infrequently. The cold-storage complement to Redis's hot state.
- **XML-RPC** — A legacy remote-procedure-call protocol the telecom nodes expose; not my choice, an industry standard. NFTRACE speaks it to the nodes internally while exposing clean REST to test workers.
- **multiprocessing.Pool** — Starts and stops traces on all nodes truly in parallel, because they must fire simultaneously or you miss the opening messages on later nodes. Used because the XML-RPC client is synchronous.
- **SIP / Diameter protocol validation** — Checking that the correct signaling messages appeared in the right order with the right parameters — SIP for IMS/voice, Diameter for authentication. Catches network-behavior bugs even when the app-level test passes.
- **Nokia Continuous Delivery (NCD) / TAF** — Nokia's internal CI/CD pipeline (NCD) and test-automation framework (TAF). I integrated NFTRACE into them so trace capture happens automatically during test runs.
- **pre_test / post_test hooks** — Functions the CI pipeline calls before and after each test: pre_test starts a trace for tagged tests, post_test stops, merges, validates, and reports back. The integration that made tracing automatic.
- **Session isolation (UUID / TTL)** — Each session gets a UUID and every operation requires it, so a worker only affects its own session; the TTL auto-cleans sessions from crashed workers. Concurrency safety plus self-cleanup.

---

## 3.7 RF Keyword Generator

### The explanation

This is an internal tool that generates Robot Framework test keywords for 5G procedures from plain-English descriptions. Testers were writing this boilerplate by hand; now they type a description, pick a procedure from a dropdown, and get a ready-to-use, syntactically-valid `.robot` file in about two seconds. The key design is hybrid: an LLM (Claude Haiku) does only the natural-language understanding — extracting parameters from the description — while deterministic templates produce the actual Robot Framework structure, and Robot Framework's own parser validates the output before it's returned. A regex fallback handles LLM failures, so the tool has 100% uptime. It hit 50+ generations a week.

### The terms

- **Robot Framework keywords** — Reusable test building blocks in the Robot Framework automation tool, written in `.robot` files with a specific syntax. Testers assemble them into 5G test cases.
- **Streamlit + FastAPI** — Streamlit is the browser UI (dropdown, text box, download); FastAPI is the backend that runs the generation logic. Split so the logic is testable and reusable, not locked in the UI.
- **Claude Haiku (entity extraction)** — The small, cheap, fast Claude model used to pull structured parameters (like an IMSI) out of the free-text description. Chosen because extraction needs no reasoning, so a bigger model would be waste.
- **Deterministic procedure templates** — Pre-built Robot Framework keyword templates for each 5G procedure, into which the extracted parameters are slotted. Correct by construction, unlike LLM-generated syntax.
- **RF parser validation** — Running Robot Framework's own parser (`robot.api.get_model()`) on the generated file to guarantee it's syntactically valid before returning it. The same parser RF uses to run tests, so passing means it will run.
- **Regex fallback** — If the LLM returns unparseable output or fails, a regex extractor handles the common structured inputs so the tool still returns a result. Why it can claim 100% uptime — the LLM is an enhancement, not a dependency.
- **Procedure detection** — Determining which 5G procedure (registration, authentication, handover) the request is for, from the dropdown plus keyword matching on the description. Selects which template to fill.
- **Hybrid LLM-deterministic pipeline** — The core pattern: LLM for the unpredictable natural-language part, deterministic code for the structured part. It's what makes the output reliable and cheap versus asking the LLM to generate everything.
- **IMSI / 5G procedures** — IMSI is the 15-digit subscriber identity; the 5G procedures are the standard operations (UE registration, authentication, handover, PDU session). The domain entities the tool extracts and generates tests for.

---

## 3.8 AI Employee Management System (EMS 2.0)

### The explanation

EMS 2.0 is a chatbot-driven HR system built as a learning project. Instead of forms, you talk to it — upload a resume (PDF or image) and it auto-extracts 22+ structured fields; then all interaction is natural language ("show me who knows Python," "update John's email," "delete employee 000003"). It's privacy-first: the LLM runs locally via Ollama, so resume data never leaves the machine. It uses three databases — PostgreSQL for structured records, MongoDB GridFS for raw files, FAISS for semantic search — and layers of validation and anti-hallucination guards before any database write. It covered a cluster of concepts I wanted to learn: local LLMs, RAG, multi-database architecture, and defensive AI pipelines.

### The terms

- **Ollama (qwen2.5:7b-instruct)** — A tool for running open LLMs locally; qwen2.5:7b-instruct is the quantized model I run. Local means data privacy, no API cost, and direct control of inference parameters.
- **FastAPI / React + Vite** — FastAPI is the Python backend (API, background processing); React + Vite is the frontend (chat UI, file upload, polling). I build and consume both sides of the API.
- **PostgreSQL / MongoDB GridFS / FAISS** — Three stores, each for what it's best at: PostgreSQL for structured employee records, MongoDB GridFS for raw PDF/image files, FAISS for vector search over employee text.
- **sentence-transformers embeddings** — The local embedding model (all-MiniLM-L6-v2) that turns employee text into vectors for FAISS. Enables semantic search with no API call.
- **pdfplumber / pytesseract (OCR)** — pdfplumber extracts text from PDF resumes; pytesseract (Tesseract OCR) is the fallback for image resumes. Together they handle both real-text and scanned documents.
- **Pydantic validation** — Enforces the 22-field employee schema on the LLM's extracted JSON before writing to the database, with a retry if a critical field like name is missing. Turns unreliable model output into a guaranteed shape.
- **RAG / semantic search** — Chunk and embed resume text, then retrieve the top-relevant employees for a query even without exact keyword matches. Powers questions like "experienced DevOps engineer" with no named person.
- **Anti-hallucination guards** — Five checks that stop the LLM fabricating data — ambiguous query, non-existent employee, leading questions, etc. — each routed through the LLM so it declines naturally instead of inventing.
- **Intent classification** — Detecting what the user wants (create/read/update/delete, search, greeting) by keyword matching first, then an LLM call for the response. Routes the message to the right handler.
- **Session memory / pronoun resolution** — Keeping the last several message pairs so follow-ups work — "what are *his* skills?" resolves "his" to the last-discussed employee. Makes it feel like a real conversation.
- **Background thread processing / polling** — CV processing runs in a background thread so the API returns immediately with a job id, and the frontend polls for status. Keeps the UI responsive during 5–30s inference.
- **Multi-strategy JSON parsing** — A parse chain (direct JSON → regex extraction → key-value fallback) for the LLM's output, since raw JSON fails 10–20% of the time. Recovers most malformed-but-salvageable responses before Pydantic validation.

---

## 3.9 Financial Statement Parser

### The explanation

This is a privacy-first, browser-based tool that turns bank-statement PDFs and images into structured, exportable data (CSV, multi-sheet Excel, or PDF report) with categorized transactions. The defining feature: the original file never leaves the browser. OCR runs locally in the browser via Tesseract.js, and only the extracted text — not the file — is sent to Google Gemini to identify and categorize transactions. It's a bring-your-own-key model with no backend and no database, so there's zero hosting cost and zero data liability. It targets anyone who's spent an afternoon re-typing transactions from a scanned statement.

### The terms

- **Browser-based / privacy-first / BYOK** — The whole app runs client-side with no backend; the user brings their own Gemini API key (BYOK). Financial documents never touch a server, which is the core selling point.
- **Tesseract.js (WASM OCR)** — The Tesseract OCR engine compiled to WebAssembly so it runs inside the browser tab at near-native speed. Enables in-browser text extraction with no server-side OCR.
- **pdf.js** — Mozilla's browser PDF renderer; converts each PDF page to a canvas image that Tesseract.js then OCRs. Handles the PDF-to-image step entirely client-side.
- **Google Gemini (gemini-2.5-flash)** — The LLM that reads the OCR'd text and returns structured transactions with categories. Called with low temperature and JSON output mode for deterministic parsing.
- **Three-method JSON salvage** — Recovers a usable result when Gemini's response is truncated: strip code fences, find the outermost braces by index, then find the last complete transaction and close the JSON. Partial results beat a hard failure.
- **React + Vite + Tailwind** — The frontend stack — React/Vite for the app, Tailwind for styling. Fast dev loop, small production bundle.
- **Recharts / html2canvas / jsPDF / SheetJS** — The export stack: Recharts for the dashboard charts, html2canvas to capture those charts as images, jsPDF for the PDF report, SheetJS for the multi-sheet Excel. All client-side.
- **Analytics engine** — A pure-function stats module computing totals, net flow, daily burn rate, category breakdown, and fixed-vs-variable split from the transactions. Powers the dashboard and reports.
- **localStorage (key obfuscation)** — The Gemini API key is stored in the browser's localStorage, lightly obfuscated (reversed + base64). Explicitly not encryption — enough to deter casual inspection, honest about that limit.
- **State machine (idle→reading→ocr→extracting→complete)** — The UI is driven by an explicit status value moving through named states, with an error branch reachable from any stage. Sections render based on the current state.
- **"Add More" updateStatus flag** — A fix for a bug where processing a second file reset the global status and wiped the displayed results. Passing `updateStatus=false` lets a second file process silently without unmounting the results.

---

## 3.10 Blog (Markdown Documentation Engine)

### The explanation

This is a static documentation-site generator — my one non-AI project. Drop Markdown files in a folder and it produces a full docs website with auto-generated sidebar navigation, client-side search, a table of contents, and dark mode — with no backend and no database. It's built on Astro, which compiles everything to static HTML at build time, so the output deploys to any CDN and all interactivity runs as small vanilla-JS scripts in the browser. The point was to explore build-time-versus-runtime thinking: anything you can do at build time, you should, because it costs nothing at runtime.

### The terms

- **Astro (static site generator)** — A framework that compiles a site to static HTML at build time, with minimal client-side JavaScript. Produces fast, dependency-free pages that host anywhere.
- **import.meta.glob()** — A Vite build-time feature that imports many files at once — I use it to discover all Markdown files and build both the sidebar tree and the search index. Reads the filesystem, not an API.
- **getStaticPaths()** — An Astro function that declares, at build time, every valid path for a dynamic route so each becomes a pre-rendered HTML page. Required for static generation of dynamic routes.
- **Catch-all route ([...slug])** — A dynamic route that captures any path under `/docs/*` and maps it to the matching Markdown file. Paired with getStaticPaths to pre-generate every doc page.
- **Build-time vs runtime** — The core mental model: file discovery, routing, and search-index building happen at build; only tiny interactivity scripts run in the browser. Work moved to build time is free at runtime.
- **Tailwind CSS / dark mode (class strategy)** — Utility-first styling; dark mode toggled by adding a `dark` class to the root element, with the choice saved in localStorage. Lets user preference override system preference.
- **IntersectionObserver (scroll spy)** — A browser API that fires when an element enters the viewport; I use it to highlight the current heading in the table of contents as you scroll. More efficient than scroll-event listeners.
- **Client-side search (weighted scoring)** — A from-scratch search over a build-time-embedded index: title matches score highest, then headings, then content. Runs entirely in the browser with no backend or external library.
- **Named slots** — Astro's mechanism for a layout to define multiple insertion points (e.g. a main slot and a TOC slot), so a page injects components into the right places. Composable layouts without the layout knowing the implementation.
- **Filesystem-based routing** — The folder structure of Markdown files directly becomes the URL structure and the sidebar navigation, with no config files. Drop a file in a folder and it appears in the nav automatically.

---

*End of Section 3. Each project: a plain "what it is" for the interviewer, then a 2-line definition for every technical term I'll say — so when they stop me on any phrase, I have the crisp answer ready. Pair with [SECTION_1_QA.md](SECTION_1_QA.md) (matched-skill Q&A) and [MASTER_STUDY_NOTES.md](MASTER_STUDY_NOTES.md) (Section 2 gaps).*
