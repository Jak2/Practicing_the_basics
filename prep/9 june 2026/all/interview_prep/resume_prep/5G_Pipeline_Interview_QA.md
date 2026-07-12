# 5G Failure Detection & Remediation Pipeline — 47 Interview Questions & Answers

**Role:** Python Developer · Automation Engineer — Infinite Computer Solutions (Nokia-Ext), Jun 2025 – Apr 2026
**Stack:** Pyshark · Qdrant · LangChain RetrievalQA · Claude (Sonnet + Haiku) · Redis · FastAPI · Streamlit
**Companion doc:** [5G_Failure_Detection_Pipeline_Deep_Dive.md](5G_Failure_Detection_Pipeline_Deep_Dive.md) — architecture + full code

---

## READ THIS FIRST — the questions that can actually hurt you

The deep-dive answers the *architecture* questions well. It does **not** answer these. A good interviewer gets to them by minute ten — and the Section I ones are found by anyone who actually reads your code.

| # | The question | Why it's dangerous |
|---|---|---|
| Q31 | "How do you know it's 70%? How did you measure that?" | The headline number on your resume. If you can't defend the measurement, the number becomes a liability instead of an asset. |
| Q32 | "Your resume says Redis caches frequent error lookups. Where is Redis in this design?" | **Your resume claims Redis. The deep-dive never mentions it.** An interviewer with both in front of him will notice. |
| Q34 | "You used OpenAI's general-purpose embeddings on 5G telecom jargon. Why would that work?" | The sharpest *design* hole. There's a good answer — but only if you've thought about it. |
| Q36 | "200 patterns. Why do you need a vector database for 200 rows?" | The "did you over-engineer this" question. Architects love asking it. |
| Q38 | "The LLM writes fixes engineers run against a live network. What stops it hallucinating a destructive command?" | The safety question. On telecom infrastructure, this is the one that decides whether they trust you. |
| **Q43** | **"Your layer detector handles RRC and GTP. Your display filter doesn't. Which is it?"** | **A real bug in the code. Dead branches. Found in 30 seconds by anyone reading both functions.** |
| **Q44** | **"What happens when `detect_vendor` returns `unknown`?"** | **A silent black hole — a classification bug that masquerades as a coverage gap. Also your best bug story.** |
| **Q45** | **"You hardcoded 1536 dimensions. What happens when you swap the embedding model?"** | **Tests whether you know a model swap means a full re-index, not a config change.** |

**The one-liner to open with:**
> "The insight that makes this more than a tutorial RAG project is that in a multi-vendor network, *semantic similarity is not enough* — an Ericsson fix for a Nokia error is worse than no fix, because the engineer can execute it. So retrieval is filtered by vendor and layer at the database level, before ranking ever happens."

---

## SECTION A — Framing (he opens here)

### Q1. "Walk me through the pipeline."
> "Before this, diagnosing a 5G failure meant an engineer opening a pcap in Wireshark and scrolling through thousands of packets, matching what they saw against their own memory of known failure patterns. Hours per incident, and completely dependent on who was on shift — a junior misses an authentication timeout a senior spots instantly.
>
> The pipeline is three stages. **Pyshark** applies a display filter to the pcap and extracts only the error packets, parsing out the error text, the vendor, the protocol layer and a severity. **Qdrant** does a semantic search against a curated knowledge base of known 5G error patterns — but *filtered* by vendor and layer, so a Nokia NAS error only ever matches Nokia NAS patterns. Then **LangChain RetrievalQA** feeds the matched patterns plus the specific error into **Claude**, which synthesises a contextual fix.
>
> Result: 70% auto-resolution of routine errors, 55% MTTR reduction, hours to seconds."

---

### Q2. "What made this hard? It sounds like a standard RAG pipeline."
**The question behind the question: did you understand your domain, or did you follow a tutorial?**
> "Three things break the standard pipeline in 5G.
>
> **One — semantic variation.** 'T3560 timer expired' and 'NAS authentication timeout after registration attempt' are the same failure in different words. Keyword search misses that entirely. That's the part vector search solves, and it's the easy part.
>
> **Two — vendor context, and this is the one that matters.** Nokia's `maxUEsServed` and Ericsson's `maxNoOfUEs` are the same parameter. But the *fixes* aren't transferable at all — Nokia AMF config is done through NetAct CLI, Ericsson through OSS CLI. Different commands, different parameter names, different restart procedures. So a semantically perfect Ericsson match for a Nokia error is **actively dangerous** — the engineer either can't run it, or runs the wrong command on a live network. Pure semantic search will happily hand you that.
>
> **Three — retrieval isn't the answer.** The closest known document is written for the general case. The engineer has a *specific* instance — this timing, this node, this retry count. That's what the LLM is for: not retrieval, synthesis."

---

### Q3. "What was the actual output an engineer saw?"
> "A structured result per error: the fix suggestion, a confidence level (high/medium/low), the matched patterns *with their similarity scores*, and the error metadata. That second-to-last item matters — `return_source_documents=True` in the chain. The engineer sees 'this fix is based on pattern AUTH_TIMEOUT_T3560, which matched at 0.94 similarity.' Without it the system is a black box telling an engineer to restart a network component. With it, it's a transparent advisory tool he can evaluate."

---

## SECTION B — Stage 1: Pyshark extraction

### Q4. "Why a display filter instead of just iterating packets in Python?"
> "The filter runs inside tshark, in C, before anything reaches Python. A pcap can hold hundreds of thousands of packets and maybe a few dozen are errors. Filtering in Python means constructing a Python object for every single packet just to throw it away — that's the whole cost. The display filter — `nas_5gs.cause_5gmm || ngap.cause_group || diameter.result_code >= 3000 || sip.status_code >= 400` — collapses the packet set to just error-bearing packets before Python sees a single one."

---

### Q5. "What is `keep_packets=False` doing and why?"
> "By default Pyshark holds every parsed packet in memory for the lifetime of the capture object. On a large pcap that's an OOM waiting to happen. `keep_packets=False` means each packet is discarded after the loop body processes it — constant memory instead of linear in file size."

---

### Q6. "Walk me through what you extract per layer."
> "Each protocol carries its error in a different field, so extraction is layer-dispatched.
> - **NAS** — the 5GMM/5GSM cause value. Cause 24 is authentication failure, 22 is congestion, 11 is PLMN not allowed. I map the numeric cause to a human description.
> - **NGAP** — the cause group and cause, e.g. `radio-network / no-radio-resources-available` on a handover failure.
> - **Diameter** — the Result-Code, where anything ≥3000 is a protocol error. 3002 is Unable-to-Deliver, 5012 Unable-to-Comply.
> - **SIP** — the status code, 4xx/5xx.
>
> All of it normalizes into one `ExtractedError` dataclass: error_text, vendor, layer, severity, timestamp, packet number."

---

### Q7. "Vendor detection is substring-matching the whole packet as a string. Isn't that fragile?"
**He is right. Concede it and show you know the better answer.**
> "Yes — that's the weakest component in the pipeline, and I'd call it out before you do. `str(packet).lower()` and looking for `nokia`, `nsn`, `netact`… it works because in this deployment the vendor signature is reliably present in the capture, and it falls back to `unknown` rather than guessing wrong. But it's a heuristic, it's O(packet size) per packet, and a coincidental substring in a payload could misclassify.
>
> The correct fix is that vendor is a property of the *capture*, not the packet — you know which node you captured from. So vendor should come from the capture metadata or be passed in with the upload, not sniffed. If it were misclassifying in production, that's the change I'd make."

---

### Q8. "Severity is keyword-matching the error text. Same objection?"
> "Same class of heuristic, but lower stakes — severity only feeds the model-routing decision, so a misclassification costs you a slightly more expensive model call, not a wrong fix. If 'critical' matched wrongly you route to Sonnet unnecessarily. The failure mode is *cost*, not *correctness*. That's why I was comfortable with a keyword list there and not comfortable with it for vendor."

**This answer is worth more than either individual one — it shows you graded your own shortcuts by blast radius.**

---

## SECTION C — Stage 2: Qdrant and retrieval (the core of the interview)

### Q9. "Why Qdrant? Why not FAISS?"
**The most likely deep question in the whole interview.**
> "The requirement was vendor- and layer-specific retrieval. **FAISS has no native metadata filtering** — it's a similarity index, not a database. So with FAISS you search the entire corpus, get back the top-k by pure semantic similarity, and then filter to Nokia in Python. Two problems: you've spent compute ranking Ericsson vectors you were always going to discard, and worse — if the top 5 are all Ericsson, you filter them out and you're left with nothing, or you have to over-fetch and hope.
>
> Qdrant runs the `must` filter **at the database level, before semantic ranking**. Only Nokia NAS vectors ever enter the similarity computation. The top-5 is the top-5 *of the relevant subspace*. Faster and structurally incapable of surfacing a cross-vendor fix."

---

### Q10. "And ChromaDB? pgvector?"
> "Chroma supports filtering but does it post-retrieval in Python — same structural problem as FAISS, just wrapped nicer. pgvector would be the right call if we were already on Postgres, but we weren't, and standing up Postgres purely to get vector search is infrastructure you have to justify. Qdrant is a Docker container and a persistent volume."

---

### Q11. "Why cosine similarity and not Euclidean or dot product?"
> "Cosine measures the angle between vectors, not their magnitude — and magnitude here is basically a proxy for *how verbose the description is*. 'T3560 timeout' and 'NAS 5GMM authentication procedure failed due to T3560 timer expiry after the UE did not respond to the Authentication Request' mean the same thing. They point in the same direction; they have very different magnitudes. Cosine says they're near-identical. Euclidean says they're far apart. For matching error descriptions of wildly varying verbosity, cosine is the only correct choice."

---

### Q12. "What's in the payload, and why store the fix there?"
> "The `text` field is what gets embedded — the error description. Everything else is payload: vendor, layer, severity (the filter fields), error_code (a canonical id), the known `fix`, protocol, component.
>
> The `fix` being retrievable is deliberate. It means Claude sees the *known remediation* alongside the error description — it isn't inventing a fix from scratch, it's **adapting a known-good fix** to a specific instance. That's a much smaller, safer generation task than free-form fix authoring, and it's a big part of why hallucination is contained."

---

### Q13. "What does `score_threshold=0.65` protect you from?"
> "Hallucinated advice. Below 0.65, the retrieved patterns aren't actually about this error — they're just the nearest things in an empty neighborhood. If you hand Claude five irrelevant patterns and ask for a fix, it will produce one, and it will sound confident. So below the threshold the pipeline returns **no result** and flags it 'unknown — manual review required.'
>
> Saying 'I don't know' is a feature. A confident wrong fix executed against a live 5G core is worse than no fix at all."

---

### Q14. "You use 0.65 in the pipeline and 0.7 as a default in the search function. Which is it?"
**A detail-check. He's testing whether you actually wrote this or copied it.**
> "0.65 is what the pipeline passes explicitly — the function default of 0.7 is overridden at the call site. If they'd drifted apart in production that's a config smell; both should come from one place. Fair catch."

Never bluff a discrepancy. Owning it costs nothing and buys credibility.

---

### Q15. "How did you pick 0.65?"
> "Empirically, against the knowledge base. Too high and genuinely-matching errors get dropped into manual review, which erodes the auto-resolution rate. Too low and you start generating fixes from unrelated patterns, which is the dangerous direction. I tuned it toward *safety* — I'd rather over-refer to manual review than under-refer, because the cost of the two errors is not symmetric."

**If you didn't tune it methodically, say so:** "It was tuned by hand against the pattern set rather than by a formal sweep — a proper precision/recall curve over a labeled set would be the rigorous version."

---

### Q16. "Why top_k=5 and not 1 or 20?"
> "One is brittle — if the top match is subtly wrong you have no cross-check, and you lose the case where an error partially matches two patterns and the real answer is the combination. Twenty floods the prompt with weak matches, which dilutes the signal and costs tokens. Five is enough for Claude to synthesize across genuinely-related patterns without drowning in noise."

---

## SECTION D — Stage 3: LangChain and Claude

### Q17. "Why LangChain? You could call Qdrant and Claude directly in about 50 lines."
**Honest answer beats a defensive one — and this deep-dive already has the honest answer.**
> "I could, and for a fixed pipeline the manual version isn't much worse. What LangChain bought me: `return_source_documents=True` for free, which is the trust feature and non-negotiable; swappability — I actually tested FAISS before settling on Qdrant, and with LangChain that was a one-line change instead of a rewrite; and clean prompt-template separation.
>
> **The cost, and it's real:** LangChain hides the final prompt that goes to the model. When fix quality was poor, I couldn't immediately see what Claude was actually receiving. `verbose=True` in development, off in production. If I were building it again today I'd weigh that abstraction cost more heavily — the debugging tax is not trivial."

---

### Q18. "Why is the chain rebuilt per query? That looks wasteful."
**Sharp question. There's a real reason and a real cost.**
> "Because the retriever's filter — vendor and layer — changes for every error, and LangChain doesn't cleanly support injecting a dynamic filter into an already-constructed retriever. So the chain gets built per error with that error's filter baked in.
>
> It is wasteful: `from_existing_collection` re-establishes the vectorstore handle each time. At the volume we ran, it was noise against a multi-second LLM call. If it mattered I'd cache chains keyed by `(vendor, layer)` — there are only a dozen or so combinations, so the cache is tiny and hits almost every time."

**Volunteering the fix for a cost you accepted = senior. Pretending there's no cost = junior.**

---

### Q19. "Why `chain_type='stuff'`?"
> "Five short error patterns fit comfortably in the context window — there's nothing to map-reduce or refine over. `stuff` puts them all in one prompt in one call. Map-reduce would mean N calls and N× the latency and cost for zero benefit at this document count. You'd reach for refine or map-reduce if the retrieved documents were long or numerous; these are a paragraph each."

---

### Q20. "Why temperature 0.1 and not 0?"
> "Consistency is the requirement — the same pcap should yield the same fix, or engineers stop trusting it. 0.0 is fully deterministic; 0.1 allows minor phrasing variation while keeping the substance stable. Honestly, 0.0 would also have been defensible here and arguably more correct for an operational tool. 0.1 was the more conservative choice against degenerate/repetitive output, but I wouldn't fight for it — the important thing is that it's *near-zero*, because creative variation in a network remediation instruction is a defect, not a feature."

---

### Q21. "Walk me through the prompt."
> "It assigns a role — a 5G ops expert on *this specific vendor and layer*, injected into the template. Then the retrieved patterns as context. Then the new error. Then it demands four structured sections: DIAGNOSIS, FIX (explicitly: specific timer names, parameter names, command examples), CONFIDENCE, and MATCHED_PATTERN.
>
> And the line I care most about: **'If the retrieved patterns are not a good match for the error, say so explicitly rather than guessing.'** That's a second line of defense behind the 0.65 threshold — a licence to abstain."

---

### Q22. "The confidence field is parsed by substring-matching the model's output text. That's brittle."
**It is. Don't defend it.**
> "It is. `'confidence: high' in text.lower()`, defaulting to medium on a parse miss. It works because the prompt dictates the format, but it's exactly the kind of thing that breaks silently when a model version changes its formatting. The right answer is structured output — a tool/function-call schema, so confidence comes back as a typed field instead of being scraped out of prose. That's the first thing I'd change."

---

### Q23. "Isn't the model's self-reported confidence meaningless anyway?"
**This is a trap, and the answer is: partly yes, and that's why it isn't the only signal.**
> "On its own, largely — a model's self-assessed confidence is not calibrated, and it'll tell you 'high' with the same certainty whether it's right or wrong. Which is why the confidence an engineer actually sees is backed by something objective: **the retrieval similarity score.** The 0.65 threshold and the top-match score are real, measurable, and independent of the model's opinion of itself. The model's confidence field is a secondary signal, and the similarity score is the primary one. If I had to drop one, I'd drop the model's."

---

## SECTION E — Model routing (the cost story)

### Q24. "Explain the Haiku/Sonnet routing."
> "Three boolean conditions, no ML. Route to **Haiku** — fast and cheap — only when all three hold: top similarity above 0.92 (a confident match), a gap of more than 0.15 to the second match (a *clear* winner, not a tie), and severity is not critical. Anything else goes to **Sonnet**: ambiguous multi-pattern matches, low top score meaning a novel error, or anything critical.
>
> Roughly 60% API cost reduction, with the hard cases still getting the strong model."

---

### Q25. "Why does the score *gap* matter? Isn't a high top score enough?"
**The best question in this section, and the answer shows real thought.**
> "No, and this is the interesting bit. A top score of 0.95 with a second at 0.94 is *not* a confident match — it's a near-tie between two patterns, which means the error sits between two known failure modes. That's precisely the case where you want synthesis across patterns, which is Sonnet's job. High-score-plus-large-gap means 'this is unambiguously that known error' — a lookup, basically, and Haiku handles it fine.
>
> Absolute score tells you *is there a match*. The gap tells you *is it the only match*. You need both."

---

### Q26. "Why force critical severity to Sonnet even on a confident match?"
> "Asymmetric cost. On a critical error the downside of a subtly-wrong fix is an outage or a bad change on a live core; the downside of using Sonnet is a few cents and a couple of seconds. When the costs are that lopsided you don't optimize the cheap side. Cost routing is fine on warnings. It is not fine on criticals."

---

### Q27. "60% cost cut — how do you know?"
**Be careful. Don't overclaim.**
> "It's the proportion of errors that satisfied the fast-path conditions multiplied by the price delta between the two models — the routing decision is logged per error, so the split is countable. It's an estimate from that split, not a controlled billing experiment."

---

## SECTION F — Knowledge base

### Q28. "Where did the 200 patterns come from?"
> "Two sources. Nokia and Ericsson internal documentation — troubleshooting guides, error code references, post-incident reports. And the operations team's institutional knowledge: senior engineers with 10+ years of mental models for common failures. I interviewed them and converted that into structured patterns — description, vendor, layer, severity, error code, step-by-step fix.
>
> That second source is really the point of the project. **The knowledge was in people's heads and it walked out of the door when they went on leave.** The pipeline is partly a RAG system and partly an institutional-memory capture exercise."

**That last line plays extremely well with a manager. It reframes the project from 'a tool' to 'a risk mitigation'.**

---

### Q29. "What happens on an error with no match?"
> "Returns no fix, flags it 'unknown pattern — manual review required', and logs it to a separate `unknown_errors` collection — not for retrieval, for *analysis*. The ops team periodically reviews that collection, resolves the errors manually, and promotes them into the knowledge base. The system's failures become its next version's coverage."

---

### Q30. "So the knowledge base grows. Doesn't that eventually degrade retrieval?"
> "It can, and there are two failure modes to watch. **Duplicate patterns** — two near-identical descriptions of one failure fragment the similarity mass and can both land in the top-5, wasting slots. And **stale fixes** — a fix that was right on one software release and is wrong on the next, which is the more dangerous one, because a stale fix retrieves with high confidence.
>
> Mitigation is curation, not automation: dedupe on promotion, and version the patterns against the network software release they apply to. At 200 patterns this wasn't yet biting. At 2,000 it would."

---

## SECTION G — The measurement and safety questions (PREPARE THESE HARDEST)

### Q31. "70% auto-resolution and 55% MTTR reduction. How were those measured?"
**Your headline numbers. If you fumble this, they become a liability.**

The honest structure of the answer:
> "**70% auto-resolution** = the proportion of errors where the pipeline produced a fix that the engineer applied without escalating to a senior — measured over `[FILL: the period and the sample — e.g. 'the first N weeks of ops-team use, across N incidents']`. The denominator is routine errors, not all errors; novel failures were always going to escalate and the system flags them itself.
>
> **55% MTTR reduction** = median time from incident raised to incident resolved, compared against the baseline from `[FILL: where the before-number came from — ticketing system? the ops team's own records?]` for the same class of incidents."

**`[FILL]` these two before the interview.** If you genuinely don't have a rigorous measurement, the correct move is:

> "Those are the numbers the operations team reported from their own tracking, not a controlled study I ran — I'd want to be precise about that. What I can speak to directly is the mechanism: the analysis step went from an engineer manually scanning a pcap to a seconds-long automated pass, and the escalation rate for routine errors dropped sharply."

**A candidate who says "here's exactly how solid that number is" is trusted more than one who recites it confidently and folds under one follow-up.** Do not fold. Pre-empt.

---

### Q32. "Your resume says Redis caches frequent error lookups. I don't see Redis anywhere in the architecture."
**⚠️ THIS IS A REAL GAP BETWEEN YOUR RESUME AND YOUR DEEP-DIVE. Resolve it before you walk in.**

Your resume bullet: *"Redis caches frequent error lookups"*. The deep-dive has no Redis.

Two legitimate positions — pick the one that is **true**:

**If Redis was really there:**
> "Redis caches the embedding-and-retrieval step. The same error signatures recur constantly across pcaps — the same NAS cause 24, the same SIP 503. Re-embedding an identical error text and re-querying Qdrant for it is pure waste. So the cache is keyed on `(error_text, vendor, layer)` and holds the retrieval result. On a repeat error it skips the embedding call and the vector search entirely. `[FILL: whether you also cached the Claude response — and if so, the TTL, because a cached fix outliving a knowledge-base update is a correctness bug]`"

**If Redis is not actually in this system:** take it off the resume bullet, or move it to the project where it *is* true. A stack item you can't walk through is a landmine — the interviewer will ask about it precisely *because* it's a keyword.

Either way: **decide this before the interview, not during it.**

---

### Q33. "What's the cache invalidation story?" (only arises if Q32 = yes)
> "The key risk is a cached fix surviving a knowledge-base update — you'd serve a stale remediation with full confidence. So the cache has to be invalidated on re-index. The clean way is to version the cache key with the knowledge-base version: bump the version on `/index`, and every old entry is orphaned instantly without a scan. A TTL alone isn't enough — it just bounds how long you're wrong."

---

### Q34. "You embedded 5G telecom jargon with OpenAI's general-purpose model. Why would that work?"
**The sharpest technical hole in the design. There IS a good answer.**
> "Fair challenge — `text-embedding-ada-002` never saw a 3GPP spec in the way a domain model would. Two reasons it holds up here.
>
> First, **the pattern texts aren't raw jargon — they're written as natural-language descriptions.** 'NAS authentication timeout — UE failed to respond to Authentication Request within T3560' is mostly ordinary English with a few identifiers in it. The semantic weight is carried by words like *timeout, authentication, failed to respond*, which a general model represents perfectly well.
>
> Second, and more importantly: **the filter carries the domain precision, not the embedding.** I'm never asking the embedding to distinguish Nokia from Ericsson, or NAS from NGAP — that's metadata, and it's exact. The embedding only has to rank within an already-narrow, single-vendor, single-layer subspace. That's a much easier job than doing domain discrimination from scratch.
>
> Where it *would* break: if two distinct failure modes in the same vendor and layer differed only by an identifier — T3560 versus T3510 — a general embedding may not separate them cleanly. That's the case for a fine-tuned or domain-adapted embedding model, and it's the first upgrade I'd make if precision needed to go up."

**That third paragraph — naming the exact condition under which your own design fails — is the strongest thing you can do in a technical interview.**

---

### Q35. "You have OpenAI embeddings and Anthropic generation. Why two providers?"
> "It's a seam, not a principle — embeddings and generation are separable concerns and I picked each independently. But it's fair to flag: two vendors means two API keys, two failure domains, two bills. `sentence-transformers` is already an installed dependency, and moving to a local HuggingFace embedding model removes the OpenAI dependency entirely and costs nothing per query. For a system running at volume that's the right move.
>
> **What it is *not* is a one-line change** — and I'd say that before you ask. See Q45: the collection is created with a fixed vector dimension. Swapping the embedding model means a new dimension, which means a new collection and a full re-index. It's a migration, not a config flip."

---

### Q36. "200 patterns. Why do you need a vector database for 200 rows?"
**The over-engineering challenge. Do not get defensive — meet it head-on.**
> "At 200 rows, you're right that you could brute-force it — 200 cosine comparisons is microseconds, and you could hold it in a list. The vector DB isn't earning its keep on *scale* at that size.
>
> What it earns its keep on is **the filter semantics and the growth path**. Vendor+layer filtering before ranking is the load-bearing feature, and I get it declaratively instead of hand-rolling it. And the knowledge base is designed to grow — every unresolved error is a candidate pattern, so the ops team is continuously adding to it. Building the brute-force version means rewriting it the moment that becomes real.
>
> But I'll grant the honest version: **at 200 patterns Qdrant is the right shape, not yet a necessary one.** If someone had pushed back on that during design, my counter would have been the operational cost — it's one Docker container — not a performance argument I couldn't defend."

**Conceding the premise and then re-winning on a different axis is far more convincing than pretending 200 rows need HNSW.**

---

### Q37. "How do you evaluate whether the fixes are actually *good*?"
> "That's the weakest part of the system, and I'd say so plainly. There was no automated fix-quality evaluation — no golden set of error-to-correct-fix pairs scored automatically on every change. The quality signal was human: engineers using it, and the escalation rate.
>
> If I were extending it, that's the first thing I'd build — a labeled evaluation set from resolved incidents, and a regression harness that scores every prompt or model change against it. `[FILL: mention that you have built exactly this elsewhere — your LLM Evaluation Framework and Prompt Regression Suite are literally that tool. Bridge to them.]`"

**This is a gift: it lets you pivot straight into your LLM Eval Framework and Prompt Regression Suite projects. Set that bridge up deliberately.**

---

### Q38. "An LLM is writing fixes an engineer will run against a live 5G core. What stops it hallucinating something destructive?"
**The safety question. On telecom infra, this is the one that decides whether they trust you.**
> "Four layers, and none of them is 'trust the model.'
>
> **1. It's grounded, not generative-from-scratch.** The retrieved pattern includes a *known, human-written fix*. Claude's job is to adapt a vetted remediation to a specific instance — a much narrower task than authoring one. It's rewriting, not inventing.
>
> **2. The 0.65 threshold.** No good match, no fix at all — the error is flagged for manual review. The system's most important capability is refusing to answer.
>
> **3. The prompt explicitly licenses abstention** — 'if the retrieved patterns are not a good match, say so rather than guessing.'
>
> **4. And the real one: it's advisory, and it shows its work.** `return_source_documents=True` means the engineer sees which pattern the fix came from and at what similarity. A human reviews and executes. The system never touches the network. **There is no path from model output to a live command.**
>
> That last point is the design decision I'd defend hardest. The moment you let an LLM's output execute directly against a production 5G core, none of the other three layers save you."

---

### Q39. "What if the pcap contains subscriber data? Privacy?"
> "Good question, and the honest answer is that the boundary matters: the extracted error text is what leaves the building — it goes to the embedding API and to Claude. That text is protocol-level diagnostics — cause codes, timer names, status codes — not payload. But IMSIs and identifiers *can* appear in signaling. `[FILL: what the actual data-handling policy was — was the extraction scrubbing identifiers? was it an internal/approved model endpoint?]` If it wasn't addressed, the right answer is: that's a real gap, and the fix is scrubbing subscriber identifiers at the extraction boundary, before anything crosses an API line."

**Do not bluff a compliance answer. "That's a gap and here's the fix" is a safe answer. An invented policy is not.**

---

## SECTION H — Scale, ops, and the closing questions

### Q40. "1000 pcap files a day. What changes?"
> "Three things. **Async FastAPI** — extraction and retrieval are I/O-bound, so async endpoints let a single worker hold many in-flight requests. **Celery**, because analysis takes 5–30 seconds depending on file size and you cannot hold an HTTP connection open for that — the POST enqueues a job, returns a job id, the client polls. And **Qdrant sharding** if the collection grows enough for search latency to move, though at these pattern counts the LLM call dominates the latency budget, not the vector search.
>
> The honest ordering: I'd do Celery first, because the long-running-request problem bites you at 10 files a day, not 1000."

---

### Q41. "What was the hardest bug?"
`[FILL: this needs a real answer from you. Strong candidates, based on the design:]`
- *A vendor misdetection sending Nokia errors into an Ericsson-filtered search, returning zero results and silently dropping the error into "no match"* — a failure that looks like "no known pattern" but is actually a classification bug. Nasty because it fails quietly.
- *Pyshark's `AttributeError` behavior* — the extractor is wrapped in a bare `try/except AttributeError: pass`, which means a genuinely malformed packet and an absent field look identical. Silent skips.

Whichever you pick, structure it: **symptom → what I assumed → what it actually was → the fix → what I changed to prevent the class.**

---

### Q42. "What would you do differently?"
**Have these ready. A candidate with no critique of their own system hasn't understood it.**
> "Four, in order.
>
> 1. **Structured output instead of substring-parsing the confidence field.** It's the most obvious latent bug — it breaks silently on a model formatting change.
> 2. **An automated fix-quality evaluation set.** Right now quality is measured by humans not complaining. That doesn't scale and it doesn't catch regressions.
> 3. **Vendor from capture metadata, not from string-matching the packet.** It's a heuristic sitting underneath a safety-critical filter — that's the wrong place for a heuristic.
> 4. **A domain-adapted embedding model,** if precision needed to improve — general embeddings do fine because the metadata filter does the hard discrimination, but they'd struggle to separate two similar timers within a single vendor and layer."

---

## SECTION I — Code-level defects (an interviewer who reads your code finds these)

These are **real defects in the code as written in the deep-dive**, not hypotheticals. Each one is findable in under a minute by someone reading the source. Getting caught by one is bad. Raising it yourself is excellent — nothing signals engineering maturity faster than being the harshest reviewer of your own code.

---

### Q43. "Your `detect_layer` handles RRC and GTP. Your display filter doesn't select them. Which is it?"
**A real bug. Two functions that disagree.**

The display filter selects only:
```
nas_5gs.cause_5gmm || nas_5gs.cause_5gsm || ngap.cause_group
|| diameter.result_code >= 3000 || sip.status_code >= 400
```
But `detect_layer()` has branches for `rrc` and `gtp`. **Those branches are unreachable** — an RRC or GTP packet never survives the display filter, so Python never sees one. And `extract_error_text()` has no RRC or GTP handler anyway, so even if one arrived it would return `None` and be skipped.

> "That's a genuine inconsistency, and it's the right thing to catch. The filter is the source of truth — RRC and GTP are *not* covered by the pipeline. Those branches in `detect_layer` are aspirational: they were scaffolding for the layers I intended to add and never did. Dead code that implies coverage the system doesn't have, which is worse than no code at all, because it misleads the next reader into thinking RRC errors are handled.
>
> The fix is one of two things and you have to pick: either delete the branches, or add RRC and GTP to the display filter *and* write their `extract_error_text` handlers. Half-covering a protocol layer is the worst of both."

**The deeper point to make — it earns you the room:**
> "And the general lesson: the display filter is a **whitelist**, which means anything not on it is invisible. That's the right default for performance, but it means my coverage is exactly as good as that filter string — and there's nothing in the system that tells me when a real error class is being silently excluded. The pipeline can't report on failures it can't see. If I were hardening it, I'd add a count of *total* packets versus *filtered* packets, so a pcap full of errors the filter doesn't recognize doesn't quietly come back as 'no errors found.'"

---

### Q44. "What happens when `detect_vendor` can't identify the vendor?"
**Your best bug story. This is a silent black hole.**

`detect_vendor()` returns `"unknown"` on no match. That string then goes straight into the Qdrant query as a hard `must` filter:
```python
FieldCondition(key="vendor", match=MatchValue(value="unknown"))
```
**No pattern in the knowledge base is stored with `vendor: "unknown"`.** So the filter matches zero rows. Zero results. The pipeline returns `None` and the error is logged as *"no similar patterns found — manual review required."*

> "Which is the trap: **a classification failure that presents as a coverage failure.** The system says 'I don't have a pattern for this error.' What actually happened is 'I couldn't tell which vendor this was, so I searched an empty subspace.' Those are completely different problems and they demand completely different fixes — one means write more patterns, the other means fix the detector — and the system reports them identically.
>
> You'd spend a week adding patterns for an error class that was already covered."

**The fix, and there are three defensible tiers:**
1. **Fail loudly.** If vendor is `unknown`, don't query — return a distinct `vendor_unresolved` status. Never silently search a subspace you know is empty.
2. **Degrade deliberately.** Drop the vendor filter and search on layer only, but mark the result low-confidence and tell the engineer the vendor was unresolved so he applies the fix with his eyes open.
3. **Fix the root cause** — vendor is a property of the *capture*, not the packet. Take it from the upload metadata instead of sniffing packet strings. (See Q7.)

> "I'd do 1 and 3. Never 2 alone — silently widening a safety filter is how a Nokia engineer ends up looking at an Ericsson fix, which is the exact failure the whole design exists to prevent."

**If asked "what was your hardest bug?" (Q41) — this is the answer.** Symptom: errors mysteriously reported as unknown. Assumption: knowledge base gaps. Actual cause: vendor detection failing, poisoning the filter. Fix: fail loudly + source vendor from capture metadata. Class prevented: never let an unresolved classification silently become a query constraint.

---

### Q45. "You hardcode `size=1536` on the collection. What happens when you change the embedding model?"
**Tests whether you understand that a vector DB has a schema.**

> "The collection is created with a fixed vector dimension — 1536, matching `text-embedding-ada-002`. That dimension is part of the collection's schema, not a runtime parameter. So switching to a `sentence-transformers` model that emits 384-dim vectors doesn't just change a config line — **Qdrant will reject the writes**, because the vectors don't match the collection's declared shape.
>
> A model swap is therefore a **migration**: create a new collection at the new dimension, re-embed every pattern in the knowledge base, upsert into the new collection, cut the reads over, drop the old one. At 200 patterns that's minutes and it's cheap. At 20,000 it's a planned job with a dual-read window.
>
> And the subtle part people miss: **you cannot mix.** Every vector in a collection must come from the same embedding model. If you re-index half the patterns with a new model, similarity scores across the two halves are meaningless — you're comparing vectors from two different spaces. It's all-or-nothing, which is why it's a migration and not an upgrade."

**Why this answer lands:** most candidates treat the embedding model as a swappable component because a framework makes it *look* swappable. Knowing that the vector store's schema pins you to it is a real, earned piece of knowledge.

---

### Q46. "What's the end-to-end latency, and what dominates?"
**Basic, and I should have asked it sooner — it's the budget that justifies several other design choices.**

> "Per error, the pipeline is: embed the query (one API call, tens of milliseconds), Qdrant filtered search (single-digit milliseconds at this collection size — it's not the bottleneck and it never was), then the Claude call, which is **seconds**. The LLM dominates by one to two orders of magnitude.
>
> Everything else is noise against it. `[FILL: the real end-to-end number for a typical pcap — worth knowing]`"

**This is the number that retroactively justifies two earlier answers, so connect them explicitly:**
- **Q18** — rebuilding the LangChain chain per query is wasteful, but it's milliseconds against a multi-second LLM call. *That's why it was acceptable.*
- **Q36** — Qdrant isn't earning its keep on speed at 200 patterns, because vector search was never the bottleneck. *That's why the honest defense is filter semantics, not performance.*

> "Which also tells you where optimization effort belongs: not in the retrieval path. It belongs in **not making the LLM call at all** — which is exactly what the Haiku routing does on confident matches, and what a cache on repeat error signatures does. Both attack the only cost that matters."

**This is the strongest structural answer in the doc.** It shows you know where your time actually goes, which is the thing that separates engineers who profile from engineers who guess.

---

### Q47. "Your deep-dive says 'cited in 3 internal audits.' Your resume doesn't. Where does that number come from?"
**⚠️ SECOND RESUME/DOC MISMATCH — the opposite direction from Redis.**

The deep-dive claims *"Cited in 3 internal audits as a reliability improvement"* and its "optimal bullet" folds that into the resume. **Your actual resume bullet does not contain it.**

**Before the interview, resolve it the same way as Redis:**
- **If it's true and you can name the audits** — it's a strong claim, put it back on the resume.
- **If you can't source it** — strip it out of the deep-dive so it never comes out of your mouth in a room.

> **The rule for both this and Redis: never carry a claim in your prep material that isn't on your resume, and never carry a claim on your resume you can't walk through.** Prep docs leak into interviews — you rehearse a line often enough and it comes out under pressure. An unsourceable number is the one mistake that reframes everything else you said as suspect.

---

## Cheat card — the lines to say exactly

| Trigger | Line |
|---|---|
| Opening | "Semantic similarity isn't enough — an Ericsson fix for a Nokia error is *worse* than no fix, because the engineer can actually execute it." |
| Qdrant vs FAISS | "FAISS filters after ranking. Qdrant filters before. One of those can never surface a cross-vendor fix." |
| The threshold | "Saying 'I don't know' is a feature. A confident wrong fix on a live 5G core is worse than no fix." |
| Grounding | "Claude isn't authoring a fix, it's adapting a known-good one. That's a much smaller, safer generation task." |
| Model routing | "Absolute score tells you *is there a match*. The gap tells you *is it the only match*. You need both." |
| Critical → Sonnet | "When the costs are that lopsided, you don't optimize the cheap side." |
| Safety (the big one) | "It's advisory and it shows its work. There is no path from model output to a live command." |
| Embeddings | "The filter carries the domain precision, not the embedding." |
| Knowledge base | "The knowledge was in senior engineers' heads and it walked out of the door with them. This is partly a RAG system and partly institutional-memory capture." |
| Over-engineering charge | "At 200 patterns Qdrant is the right *shape*, not yet a *necessary* one." |
| The vendor black hole (Q44) | "A classification failure that presents as a coverage failure. The system says 'no pattern for this.' What happened is 'I searched an empty subspace.'" |
| The display filter (Q43) | "The filter is a whitelist. My coverage is exactly as good as that filter string — and nothing tells me when a real error class is being silently excluded." |
| Embedding dimension (Q45) | "You can't mix. Every vector in a collection comes from one model, or the scores are meaningless. It's a migration, not an upgrade." |
| Latency (Q46) | "The LLM dominates by two orders of magnitude. So optimization doesn't belong in the retrieval path — it belongs in *not making the call at all*." |

---

## Prep priority

**Tier 1 — can make you look dishonest, not merely unprepared. Fix before anything else.**
1. **Q32 — the Redis discrepancy.** Your resume claims it; the deep-dive has no trace of it.
2. **Q47 — the "3 internal audits" claim.** The deep-dive asserts it; your resume doesn't. Opposite direction, same hazard.
3. **Q31 — how 70% and 55% were measured.** Headline numbers with no methodology are a liability. Pre-empt; never recite and fold.

**Tier 2 — the questions a strong interviewer reaches by minute ten.**
4. **Q38 — safety / hallucination on a live network.** The trust question in telecom.
5. **Q44 — the `unknown` vendor black hole.** Also your answer to "hardest bug" (Q41). Rehearse it as a story.
6. **Q34 — general embeddings on telecom jargon.** The answer that names its own failure condition is the strongest thing in this doc.

**Tier 3 — raise these yourself before he finds them.**
7. **Q43 — RRC/GTP dead branches.** Real bug. Volunteering it costs nothing and buys enormous credibility.
8. **Q36 — "why a vector DB for 200 rows."** Concede the premise, re-win on a different axis.
9. **Q45 / Q46 — embedding dimension, and where the latency actually goes.**

## The `[FILL]` list — do not walk in with these blank

- **Q31** — how 70% and 55% were actually measured (period, sample, baseline source).
- **Q32** — is Redis real in this project? If yes, what does it cache. If no, fix the resume.
- **Q37** — bridge to your LLM Eval Framework / Prompt Regression Suite.
- **Q39** — the actual data-handling / subscriber-identifier policy, if there was one.
- **Q41** — the hardest bug. **Q44 is your answer** — but confirm it actually happened before telling it as a war story.
- **Q46** — real end-to-end latency for a typical pcap.
- **Q47** — can you source "3 internal audits"? If not, strike it from the deep-dive.

---

## One rule that governs this whole document

**Never carry a claim in prep material that isn't on your resume. Never carry a claim on your resume you can't walk through.**

Prep docs leak. Rehearse a line enough times and it comes out under pressure. An unsourceable number is the single mistake that reframes everything else you said as suspect — and you don't get to argue your way back from it.
