# 5G Failure Detection & Remediation Pipeline
## Pyshark · Qdrant · LangChain RetrievalQA · Claude API

---

## Elevator Pitch (30 seconds)

> "I built a pipeline that automatically diagnoses 5G network failures from pcap files.
> It extracts signaling errors using Pyshark, semantically matches them against a Qdrant vector database of known failure patterns — filtered by vendor and network layer so Nokia errors only match Nokia fixes — then uses Claude to synthesise a contextual remediation suggestion. It reduced Mean Time To Repair by 55% and auto-resolved 70% of routine errors without human escalation."

---

## The Problem

Engineers manually opened pcap files in Wireshark, scrolled through thousands of packets, and matched what they saw against years of experience. One incident = hours of analysis. The same error got rediscovered repeatedly with no institutional memory, and fix quality varied by individual expertise.

---

## Architecture — 4 Stages

```
pcap file
   ↓
Stage 1: Pyshark Extraction
  - display_filter applied at capture level (not Python) → only error packets
  - Extract: error_text, vendor (Nokia/Ericsson/Huawei), layer (NAS/NGAP/Diameter/SIP), severity
   ↓
Stage 2: Qdrant Vector Search
  - Embed error_text → vector[1536] via OpenAI embeddings
  - Filter: must[vendor=nokia, layer=NAS] → THEN rank by cosine similarity
  - Return top-5 patterns above score_threshold=0.65
   ↓
Stage 3: LangChain RetrievalQA
  - Assemble retrieved patterns as context
  - Build prompt: 5G expert persona + known patterns + specific error
  - Call Claude (Haiku or Sonnet based on routing)
  - Return fix_suggestion + source_documents
   ↓
Output: fix_suggestion · matched_patterns · confidence · error_metadata
```

---

## The Key Design Decisions (what interviewers love)

### 1. Why Qdrant over FAISS or ChromaDB?

**FAISS** has no metadata filtering. You search the entire corpus and filter in Python afterward — Ericsson patterns appear in the similarity ranking for Nokia errors, then get discarded. This degrades both speed and result quality.

**Qdrant's `must` filter runs at the database level** — only Nokia NAS vectors are considered for similarity computation. You never compute similarity against irrelevant patterns.

*Interview answer:* "The critical requirement was that Nokia errors must only match Nokia patterns — an Ericsson fix has different CLI syntax and would be wrong or unusable. FAISS has no native metadata filtering, so you'd search the full corpus first. Qdrant's must filter runs before semantic ranking. Faster and produces only relevant results."

### 2. Why cosine similarity (not dot product or Euclidean)?

Cosine similarity measures the angle between vectors, not magnitude. "T3560 timeout" and "NAS 5GMM authentication procedure failed due to T3560 timer expiry" point in the same direction — same concept, different verbosity. Cosine: high (correct). Euclidean: large (wrong).

### 3. Why temperature=0.1?

Fix suggestions must be deterministic — same pcap, same fix. High temperature introduces creative variation that is actively harmful for operational tooling. An engineer running the same pcap twice must get the same recommendation.

### 4. Why `return_source_documents=True`?

Trust. An ops engineer is about to restart a service or change a network config based on this suggestion. Showing "this fix is based on pattern AUTH_TIMEOUT_T3560 — matched with 0.94 similarity" gives the engineer grounds to evaluate it critically. Without source docs, it's a black box they won't trust.

### 5. Model routing — Haiku vs Sonnet

```
top_score > 0.92 AND score_gap > 0.15 AND severity != "critical"
→ True: Claude Haiku (fast, cheap, well-defined match)
→ False: Claude Sonnet (deep reasoning, ambiguous cases, critical errors)
```

Cut API costs ~60% without sacrificing accuracy on hard cases.

### 6. score_threshold=0.65

Below 0.65, patterns are too dissimilar — returning a low-confidence match produces hallucinated advice, which is worse than returning nothing. The pipeline returns "unknown — manual review required" and logs to an `unknown_errors` collection for knowledge base growth.

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Packet extraction | Pyshark (Python) | Programmatic Wireshark — display filters at capture level, not Python |
| Vector DB | Qdrant (Docker) | Native metadata filtering; persistent volume; production-grade |
| Embeddings | OpenAI `text-embedding-ada-002` | 1536-dim; compatible with Qdrant's cosine distance |
| RAG orchestration | LangChain RetrievalQA | `return_source_documents=True`; swap LLM/retriever in one line |
| LLM (primary) | `claude-sonnet-4-6` | Deep reasoning for ambiguous/critical errors |
| LLM (fast path) | `claude-haiku-4-5-20251001` | High-confidence matches; 3-5x cheaper |
| API | FastAPI | Async file upload endpoint; clean OpenAPI docs |
| UI | Streamlit | Internal ops tool; severity color coding; expandable fix suggestions |

---

## Results

- **70%** auto-resolution of routine errors without human escalation
- **55%** reduction in Mean Time To Repair (MTTR)
- Adopted by operations teams for daily use
- Cited in **3 internal audits** as a reliability improvement

---

## Anticipated Interview Questions

**Q: Walk me through this pipeline.**
> Pyshark extracts signaling errors from pcap files — filtered at the capture level so Python only processes error packets. Qdrant does a filtered semantic search, using a vendor+layer must filter before similarity ranking so Nokia errors never pull Ericsson fixes. LangChain RetrievalQA assembles the top-5 matched patterns as context, sends them with the specific error to Claude, and returns both the fix and the source documents so engineers can see why the system suggested this fix. Result: 70% auto-resolution, 55% MTTR reduction.

**Q: What happens when an error has no match?**
> Below the 0.65 score threshold, the pipeline returns a no_match result flagged "unknown pattern — manual review required." The error is logged to an `unknown_errors` Qdrant collection. Operations engineers review these periodically and add new patterns — so the system improves over time by capturing its own failure cases.

**Q: How would you scale this to 1000 pcap files per day?**
> Three changes: async FastAPI endpoints (I/O bound — Pyshark and Qdrant are both network I/O); Celery task queue (pcap analysis takes 5-30s — return job ID immediately, poll for results); Qdrant horizontal scaling with sharding (collection grows rapidly at 1000 files/day — sharding keeps search latency stable).

**Q: Why not just return the closest matched document?**
> The closest document is generic — written for the general case. Claude adds three things the document alone can't: contextualisation to the specific error instance (specific timing, retry count, node); synthesis across multiple retrieved patterns when the error partially matches more than one issue; and natural language the engineer can act on immediately. A document says "check T3560 timer." Claude says "this occurred during a traffic spike — the 1s T3560 expiry suggests poor signal, increase to 3s in AMF config and monitor."
