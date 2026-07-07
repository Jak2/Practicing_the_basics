# Interview Master Cheatsheet — All Projects

> One-page reference. Scan this before walking into the room.

---

## Quick Project Map

| Project | Stack | Impact | Key Insight |
|---|---|---|---|
| **5G Failure Detection Pipeline** | Pyshark · Qdrant · LangChain · Claude | 70% auto-resolution, 55% MTTR reduction | Metadata filtering before semantic ranking — vendor-specific retrieval |
| **Bias & Fairness Auditor** | FastAPI · Claude · VADER · SciPy · Streamlit | EU AI Act Article 13 compliance | 4-pipeline blind audit — VADER→DistilBERT two-layer scoring |
| **Financial Statement Parser** | React · Tesseract.js · Gemini · SheetJS | Zero server-side data — privacy-first | Send OCR text to AI, not the raw file |
| **LLM Eval Framework** | FastAPI · Celery · Redis · PostgreSQL · Streamlit | 14-pt faithfulness drop caught in 4 min | AND logic for pass — no composite averaging masks failures |
| **NFTRACE** | FastAPI · Redis · SQLite · XML-RPC · Pyshark | 50% pipeline validation time reduction | Redis for hot state, SQLite for cold history — right tool per access pattern |
| **RF Keyword Generator** | Streamlit · FastAPI · Claude Haiku · RF Parser | 50+ weekly generations | LLM for understanding, templates for structure — hybrid pattern |

---

## The Story Arc (tell this if asked "what have you been building?")

> "My recent work sits at the intersection of AI engineering and telecom automation.
> On the telecom side I built NFTRACE — a distributed tracing platform that automated 5G network validation inside Nokia's CI/CD pipeline, and a Robot Framework keyword generator that cut test creation from hours to minutes.
> On the AI side I built three tools that address real production gaps: a failure detection pipeline that uses RAG with vendor-specific retrieval to auto-resolve 70% of 5G incidents, an LLM evaluation framework that catches model regressions before they hit users, and a bias auditor that generates EU AI Act–compliant documentation automatically.
> The common thread is production reliability — every system has a fallback, a quality gate, or an audit trail."

---

## Technology Themes (what you genuinely know deeply)

**Vector search & RAG**
- Qdrant with pre-filter metadata (not post-filter) — why this matters for multi-tenant retrieval
- LangChain RetrievalQA, `return_source_documents=True` for engineer trust
- Embedding model choice: `all-MiniLM-L6-v2` for semantic similarity

**LLM integration patterns**
- Model routing: Haiku for high-confidence/cheap, Sonnet for ambiguous/critical
- Temperature 0.1 for deterministic operational outputs
- LLM-as-judge with blind demographic stripping to prevent bias import
- Fallback chains: LLM → regex → defaults (never crash, always return something)

**Async Python production patterns**
- FastAPI + asyncio + Semaphore for rate-limiting concurrent LLM calls
- Celery + Redis for durable background tasks (tasks survive server restart)
- AND logic for quality gates — no composite averaging hides failures

**Privacy-first architecture**
- Client-side OCR (Tesseract.js WASM) — file never leaves browser
- BYOK model — zero hosting cost, zero data liability

---

## Numbers to Remember

- **70%** auto-resolution of 5G errors (Failure Detection Pipeline)
- **55%** MTTR reduction (Failure Detection Pipeline)
- **50%** pipeline validation time reduction (NFTRACE)
- **50+** weekly keyword generations (RF Generator)
- **4 minutes** to detect a 14-point faithfulness drop (LLM Eval Framework)
- **3** internal audits cited the Failure Detection Pipeline
- **200** initial error patterns in the Qdrant knowledge base
- **60%** API cost reduction from Haiku/Sonnet routing

---

## The One Design Decision Per Project (what separates you from a tutorial builder)

| Project | The Non-Obvious Decision |
|---|---|
| 5G Pipeline | Qdrant `must` filter runs at DB level — Ericsson patterns never enter the similarity computation for Nokia errors |
| Bias Auditor | Blind LLM judge — demographics stripped before the judge sees responses, preventing bias import |
| Financial Parser | OCR text sent to AI, not raw file — privacy over simplicity |
| LLM Eval | AND logic not weighted average — a 95% faithful but hallucinating response must fail |
| NFTRACE | Two-layer persistence: Redis (active, hot, TTL-managed) + SQLite (completed, cold, persistent) |
| RF Generator | LLM for entity extraction only, templates for structure — reliability + cost |
