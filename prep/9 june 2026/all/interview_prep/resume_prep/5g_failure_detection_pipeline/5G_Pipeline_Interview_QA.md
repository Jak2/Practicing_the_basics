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

---

## APPENDIX A — The four layers that contain hallucination (memorize this)

**The framing line:** *"None of the four layers is 'trust the model.'"*

**1. Grounding — adapt, don't invent.**
The retrieved pattern already carries a known, human-written fix. Claude's job is to *adapt* a vetted fix to the specific error instance, not author one from scratch. That's a far smaller, safer task than free-form fix generation — it's rewriting, not inventing.

**2. The 0.65 similarity threshold.**
No match above 0.65 → return **no fix**, flag "unknown pattern — manual review required." The system's most important capability is refusing to answer. A confident wrong fix on a live 5G core is worse than no fix.

**3. Explicit abstention in the prompt.**
The prompt tells Claude: *"if the retrieved patterns are not a good match, say so rather than guessing."* A licence to say "I don't know" instead of confabulating — a second line of defence behind the threshold.

**4. Advisory, and it shows its work.**
`return_source_documents=True` — the engineer sees which pattern the fix came from and at what similarity, then reviews and executes. **There is no path from model output to a live command.** A human is always the gate.

**Reinforcing factors (not one of the four, but say them if pressed):** the vendor+layer filter never surfaces a cross-vendor fix, and temperature 0.1 keeps output near-deterministic and consistent.

---

## APPENDIX B — "Why 0.65, why not higher?"

It's a **recall vs. precision trade-off**, tuned deliberately toward *not dropping real matches*.

**Push it higher (e.g. 0.85):**
- Only near-identical matches accepted. Precision up — fewer weak patterns reach the LLM.
- But you **reject genuine matches worded differently.** "T3560 timeout" vs "NAS authentication timeout after registration attempt" are the same failure and won't score 0.85 — so errors you *have* the pattern for get dumped into manual review.
- The auto-resolution rate collapses. The tool stops being useful — engineers are back to manual work on errors the system actually knew.

**Push it lower (e.g. 0.4):**
- Almost anything counts as a match. Claude gets fed patterns that aren't really about this error.
- It generates a confident fix from an irrelevant pattern — **the exact hallucination the threshold exists to stop.** The dangerous direction on a live network.

**0.65 is the balance:** high enough that below it the patterns genuinely aren't about the error (real "I don't know" territory), low enough that semantic rephrasing still matches.

**The asymmetry is the real justification — say this out loud:**
> "I tuned it toward safety, not symmetry. The cost of the two errors isn't equal. Over-referring to manual review just wastes a bit of an engineer's time. Under-referring hands someone a confident wrong fix for a live 5G core. When the downside is that lopsided, you bias toward caution — I'd rather send a real match to manual review occasionally than generate one bad fix."

**Honesty caveat (concede if pushed):** 0.65 was tuned by hand against the pattern set, not from a formal precision/recall sweep. The rigorous version is a labelled set of error→correct-pattern pairs, plot precision and recall across thresholds, and pick from the curve. "Empirically chosen, biased toward recall; the principled version is an ROC curve I didn't build."

---

Here is the interview preparation guide structured cleanly in Markdown format.

Based on this project, an interviewer (especially for Python, AI/ML, Telecom, or Backend roles) can ask questions ranging from high-level architecture to implementation details. Below are common and advanced questions.

## Project Architecture and Technical Interview Blueprint

### 1. Project Overview

**Explain your project in 2 minutes.**
> "It's a 5G failure detection and remediation pipeline. When a 5G failure happens, the evidence is in a pcap — a packet capture. Before this, an engineer opened it in Wireshark, scrolled thousands of packets, and matched what he saw against his own memory of known failures. Hours per incident, and dependent on who was on shift. My pipeline automates it in three stages: Pyshark extracts only the error packets and parses out the error text, vendor, layer and severity; Qdrant does a semantic search against a knowledge base of known 5G error patterns, filtered by vendor and layer so a Nokia error only matches Nokia patterns; then LangChain feeds the matches to Claude, which writes a specific fix. Output is advisory — a human still executes it. Results: 70% auto-resolution of routine errors, 55% MTTR reduction."

**What problem does this project solve?**
> "Diagnosis was slow, expertise-dependent, and had no institutional memory — the same error got rediscovered repeatedly, and a junior missed what a senior spotted instantly. The pipeline turns hours of manual pcap reading into a seconds-long automated pass, and captures the senior engineers' knowledge into a reusable knowledge base."

**Why did you choose this architecture?**
> "Three-stage because each stage is a different problem. Extraction is deterministic parsing — no AI needed, so Pyshark. Matching needs *meaning*, not keywords, and must never cross vendors — so a vector DB with metadata filtering. Fix generation needs synthesis to the specific instance — so an LLM. Each tool is doing the one thing it's best at, and they're decoupled so I could swap any stage."

**What was your role in the project?**
> "I built the pipeline end to end — the Pyshark extraction, the Qdrant knowledge base and filtered retrieval, the LangChain chain, the model routing, and the FastAPI/Streamlit surfaces. `[FILL: confirm team size — were you solo on this, or did you own these slices of a larger effort? Be precise.]`"

**What are the inputs and outputs of the system?**
> "Input: a `.pcap`/`.pcapng` file. Output per error found: a structured result — fix suggestion, confidence level (high/medium/low), the matched known patterns with their similarity scores, and the error metadata (vendor, layer, severity). The similarity scores matter — they let the engineer see *why* a fix was suggested instead of trusting a black box."

**What technologies did you use and why?**
> "Pyshark for extraction (Python wrapper over tshark's mature dissectors). Qdrant for retrieval (native metadata filtering at the DB level). OpenAI embeddings for the vectors. LangChain RetrievalQA to wire retrieval to the LLM and get source documents back. Claude Sonnet and Haiku for fix generation with cost-based routing. FastAPI to expose it as an API, Streamlit for the UI. `[FILL: Redis is on the resume for caching — confirm it's real and what it cached; the deep-dive doesn't cover it. See Section 8.]`"

---

### 2. Pyshark & Packet Capture

**What is Pyshark?**
> "A Python wrapper around tshark — Wireshark's command-line engine. It gives you Wireshark's entire protocol-dissection library from Python, so I parse a NAS or NGAP field by name instead of decoding bytes by hand."

**How does Pyshark work internally?**
> "It shells out to tshark, which does the actual capture-file parsing and dissection in C, and streams the results back as XML (PDML) which Pyshark turns into Python packet objects. So the heavy parsing is native tshark; Pyshark is the Python layer on top."

**Why did you choose Pyshark over Scapy?**
> "Scapy is brilliant for crafting and low-level manipulation, but its dissection of complex telecom stacks — 5G NAS, NGAP, Diameter — is far weaker than Wireshark's. tshark has mature, maintained dissectors for exactly those protocols. I needed to *read* signaling accurately, not craft packets, so the tool with the better dissectors won."

**What is a PCAP file?**
> "Packet CAPture — a binary file storing every packet seen on an interface, with per-packet timestamps and the full frame bytes. It's the raw record of what actually crossed the network."

**How are packets stored inside a PCAP?**
> "A global header, then a sequence of records: each is a small per-packet header (timestamp, captured length, original length) followed by the raw packet bytes. pcapng is the newer format with richer metadata blocks. tshark reads both."

**How did you filter only signaling packets?**
> "A tshark display filter applied at capture-read time, before anything reaches Python: `(nas_5gs.cause_5gmm || nas_5gs.cause_5gsm) || ngap.cause_group || diameter.result_code >= 3000 || sip.status_code >= 400`. That collapses hundreds of thousands of packets down to just the error-bearing ones in C, so Python never constructs an object for a packet I'm going to discard."

**Which protocols were you analyzing?**
> "NAS (5GMM/5GSM), NGAP, Diameter, and SIP. Those are the layers where the failures I cared about surface — registration, authentication, handover, and IMS. Note: my `detect_layer` has RRC and GTP branches too, but the display filter doesn't select them — so in practice those are dead branches, not real coverage. I'd either wire them in fully or delete them (see Q43 above)."

**How did you detect authentication timeout?**
> "It's not timer inference — it's the cause code. A NAS 5GMM cause 24 is 'Authentication failure'; the T3560 timeout surfaces as that cause in the signaling. I map the numeric cause to a human description at extraction time. So detection is deterministic: the failure is *declared* in the packet, I'm reading it, not statistically guessing it."

**How did you identify handover failures?**
> "NGAP cause group — a HandoverFailure carries `radio-network / no-radio-resources-available` or similar. I read the cause group and cause fields off the NGAP layer."

**How did you detect congestion?**
> "NAS cause 22 is 'Congestion' — the AMF rejects registration with that cause and starts the T3502 back-off. Again, read from the cause value, not inferred."

**How did you extract timestamps?**
> "`packet.sniff_time` — tshark's per-packet capture timestamp. It goes into the `ExtractedError` so the LLM can contextualise the fix (e.g. 'this occurred at 03:42 during a traffic spike')."

**How did you correlate multiple packets belonging to one UE?**
> "Honestly — I don't, and I'd say that plainly. The pipeline processes each error packet independently; there's no session/UE correlation by SUPI or by procedure. Each error is matched and remediated on its own. That's a real limitation: a failure that only makes sense across a message sequence isn't reconstructed. UE-level correlation — grouping by identifier and analysing the procedure as a unit — is the single biggest extension I'd make."

**How did you handle large PCAP files?**
> "Two things. The display filter shrinks the working set in C before Python. And `keep_packets=False` on the FileCapture, so each packet is discarded after the loop body instead of Pyshark holding them all in memory — constant memory instead of linear in file size."

**What were the limitations of Pyshark?**
> "It's slower than raw parsing because of the tshark subprocess and the XML round-trip. Error handling is coarse — a genuinely malformed packet and an absent field both surface as `AttributeError`, so my extractor wraps field access in try/except and can silently skip. And it depends on a matching tshark version being installed. For accuracy of dissection it was the right call; for raw throughput it isn't the fastest option."

---

### 3. 5G Network Concepts

**Explain the 5G registration procedure.**
> "The UE sends a Registration Request over NAS to the AMF. The AMF triggers authentication with the AUSF/UDM (5G-AKA), then security-mode setup to establish NAS ciphering and integrity. Once authenticated and secured, the AMF accepts registration and the UE can set up PDU sessions via the SMF. My pipeline catches the failures along that path — cause 24 if authentication fails, cause 22 if the AMF is congested and rejects."

**What is NAS signaling?**
> "Non-Access Stratum — the signaling directly between the UE and the core (the AMF), carrying registration, authentication, mobility and session management. It rides transparently over the radio; the base station doesn't interpret it. Cause codes like 5GMM 24 or 22 live here."

**What is RRC?**
> "Radio Resource Control — the signaling between the UE and the gNB (the base station) that manages the radio connection: connection setup, bearer configuration, handover over the air. It's the layer below NAS."

**Difference between NAS and RRC?**
> "NAS is UE-to-core (AMF) and is about registration, mobility, sessions — the gNB just relays it. RRC is UE-to-gNB and is about the radio link itself. NAS travels *inside* RRC over the air interface. My pipeline reads NAS; RRC is one of the dead branches I mentioned."

**What is NGAP?**
> "NG Application Protocol — the control-plane signaling between the gNB and the AMF over the N2 interface. Handover coordination, UE context management, and PDU session resource setup happen here. Handover failures surface as NGAP cause groups."

**What is Xn handover?**
> "A handover coordinated *directly* between two gNBs over the Xn interface, without the core mediating the decision. Faster, used when the two gNBs have an Xn link."

**What is N2 handover?**
> "A handover routed through the core over N2 (NGAP) — the source gNB talks to the AMF, which coordinates with the target. Used when there's no direct Xn, or across AMF boundaries. It's more signaling-heavy, so more places to fail — which is why NGAP cause groups matter."

**What causes authentication failure?**
> "5G-AKA mismatch — wrong or desynchronised USIM credentials, an AUSF/HSS unreachable from the AMF, or the T3560 timer expiring because the UE didn't respond in time (often poor signal). Surfaces as NAS 5GMM cause 24, or on the Diameter side as an AIR timeout / result-code failure."

**What causes handover failure?**
> "No radio resources at the target cell (target congested), a missing or broken Xn/X2 link, or overly aggressive handover thresholds (A3 offset) triggering handovers that can't complete. Surfaces as an NGAP HandoverFailure with a radio-network cause."

**What causes congestion?**
> "Too many active UE contexts against AMF capacity, or backhaul saturation. The AMF sheds load by rejecting registration with NAS cause 22 and back-off timers. My knowledge base has a Nokia/Huawei congestion pattern for exactly this."

**What is AMF?**
> "Access and Mobility Management Function — the core control-plane anchor for the UE: registration, connection, mobility, and NAS termination. Most of the NAS failures I detect are AMF-side."

**What is SMF?**
> "Session Management Function — sets up and manages PDU sessions, allocates IPs, and controls the UPF. It's the session brain."

**What is UPF?**
> "User Plane Function — the data-plane forwarder that actually carries user traffic, under SMF control. It's the packet-pushing element, not signaling — so it's outside what my pipeline reads."

**What signaling messages were parsed?**
> "The error-bearing ones: NAS Registration Reject / Authentication Reject (via 5GMM/5GSM cause), NGAP HandoverFailure (via cause group), Diameter AIA/error result-codes ≥3000, and SIP 4xx/5xx. Not full procedures — the specific messages that declare a failure."

**What KPIs were monitored?**
> "This isn't a live-KPI monitor — it's forensic on captured pcaps. The signals it works from are failure counts by cause, by vendor, by layer. The operational metric it moved was MTTR — time from incident to fix — not a real-time counter. I'd be precise about that: it's a diagnosis accelerator, not a KPI dashboard."

---

### 4. Error Detection Logic

**How exactly did your pipeline detect an authentication timeout?**
> "It reads the declared cause, it doesn't infer a timeout from timing. The failed authentication surfaces in the NAS layer as 5GMM cause 24; the display filter selects packets carrying `nas_5gs.cause_5gmm`, and the extractor maps cause 24 to 'Authentication failure'. So 'detection' here is deterministic parsing of a cause code the network already set — not a heuristic."

**Did you use rule-based detection or AI?**
> "Detection is rule-based and deterministic — display filters plus cause-code mapping. AI is only in the *remediation* half: semantic matching and fix synthesis. That split is deliberate — I don't want a probabilistic model deciding *whether* an error exists; the packet already says so. AI is reserved for the judgment task, suggesting the fix."

**How did you define timeout?**
> "I didn't define a timeout threshold myself — the network defines it via its timers (T3560 for authentication, T3502 for congestion back-off), and the expiry manifests as a cause code in the signaling. I read the consequence, not the clock. If I *were* inferring timeouts from inter-packet timing, I'd need NTP-synced captures and a defined delta — which is exactly why reading the declared cause is more robust."

**What happens if packets arrive out of order?**
> "Because detection is per-packet on a declared cause, ordering doesn't affect whether an error is *detected*. Where it would matter is correlation — reconstructing a procedure across messages — which I don't do. So out-of-order packets are a non-issue for my current per-error design, and would become a real concern only if I added UE/procedure correlation."

**How did you reduce false positives?**
> "The detection side has very few — a cause code is an explicit failure declaration, not a guess. The false-positive risk is on the *remediation* side: matching an error to the wrong known pattern. That's controlled by the 0.65 similarity threshold (below it, return no fix and flag manual review) and by the vendor+layer filter (never match across vendors)."

**How did you validate the detected failures?**
> "Detected failures are ground-truth by construction — they're cause codes the network set. Validation effort went into the *fixes*, not the detection. And honestly, that validation was human — engineers using the output and escalation rate — not an automated eval set. That's the weakest link, and it's the first thing I'd build (a labelled error→correct-fix set). `[FILL: did you ever spot-check detection output against Wireshark manually? If so, say so.]`"

**How accurate was your detection?**
> "Detection accuracy is essentially bounded by tshark's dissection correctness, which is very high — I'm reading fields Wireshark already decoded. I'd resist quoting a detection-accuracy percentage, because there's no labelled benchmark behind one; the honest statement is 'detection is deterministic parsing, so it's as accurate as the dissector.' The 70% figure is auto-*resolution* of routine errors, which is a remediation metric, not a detection one."

**How did you test edge cases?**
> "`[FILL: be honest about what testing actually existed. The deep-dive documents no automated test suite.]` The edge cases I designed for explicitly: a packet with the layer but no readable error field (returns None, skipped), an unknown vendor (falls back to `unknown` — which, as I flag in Q44, is actually a bug because it poisons the filter), and no-match errors below the 0.65 threshold (flagged for manual review rather than force-fitted)."

---

### 5. Vector Database

**Which vector database did you use?**
> "Qdrant, running as a Docker container on localhost:6333, collection `5g_error_patterns`."

**Why did you choose it?**
> "Native metadata filtering at the database level. My hard requirement was that a Nokia error never matches an Ericsson pattern — a cross-vendor fix is worse than no fix because the engineer can execute it. FAISS has no metadata filtering, so you'd search the whole corpus and filter in Python afterward, meaning Ericsson vectors are still in the ranking. Qdrant's `must` filter runs *before* similarity, so only Nokia-NAS vectors are ever considered. (Full comparison in Q9/Q10 above.)"

**How are error patterns stored?**
> "Each known pattern is one point: the vector (embedding of the pattern's text description) plus a payload. One pattern = one point, no chunking — the descriptions are a paragraph each, so there's nothing to split."

**What metadata is stored?**
> "In the payload: `text` (the embeddable description), `vendor`, `layer`, `severity` (the filter fields), `error_code` (canonical id), `fix` (the known remediation), `protocol`, and `component`. The `fix` being retrievable matters — it means Claude sees a known-good fix to adapt, rather than inventing one from scratch."

**How are embeddings generated?**
> "The pattern's `text` is sent to the embedding model, which returns a 1536-dimension vector. Patterns are batch-embedded once at index time; the incoming error is embedded per query."

**Which embedding model did you use?**
> "OpenAI `text-embedding-ada-002`, 1536 dimensions. Fair follow-up is 'why a general-purpose model on telecom jargon' — the answer (Q34 above) is that the metadata filter carries the domain precision, so the embedding only has to rank within an already-narrow single-vendor, single-layer subspace."

**How is similarity calculated?**
> "Cosine similarity, configured on the collection (`Distance.COSINE`). Qdrant uses an HNSW index for approximate nearest-neighbour so it's fast at scale."

**What is cosine similarity?**
> "The cosine of the angle between two vectors — it measures direction, not magnitude. That's the right choice here because magnitude tracks how *verbose* a description is. 'T3560 timeout' and a long paragraph describing the same failure point the same direction but have very different magnitudes; cosine calls them near-identical, Euclidean would call them far apart."

**What happens if multiple documents have similar scores?**
> "Two things. Retrieval returns the top-5, so a near-tie just means several patterns go to the LLM and it synthesises across them — which is often correct, because the error genuinely sits between two known failures. And I *use* the score gap: a high top score with a large gap to the second is a confident single match (routed to Haiku); a near-tie is ambiguous and routed to Sonnet for deeper reasoning (Q25 above)."

**How often is the vector database updated?**
> "On demand via a re-index endpoint, not on a schedule. When the ops team resolves a novel error manually, it becomes a new pattern and gets indexed. Unmatched errors are also logged to a separate `unknown_errors` collection for periodic review — so the system's own failures become its next version's coverage."

---

### 6. LangChain

**What is LangChain?**
> "A framework for composing LLM applications — it standardises retrievers, prompts, chains, and model clients behind common interfaces, so the pieces are swappable and you don't hand-wire each integration."

**Why did you use RetrievalQA?**
> "It packages the exact retrieve-then-generate pattern I needed, and gives me two things for free: `return_source_documents=True`, so I get back *which* patterns matched — the trust feature, non-negotiable for an engineer acting on a fix — and swappability, so testing FAISS before settling on Qdrant was a one-line change instead of a rewrite. The cost is that it hides the final prompt; I used `verbose=True` in development to see what Claude actually receives (Q17 above)."

**Explain RetrievalQA architecture.**
> "Query comes in. The retriever embeds it and fetches the top-k documents from the vector store (with my vendor+layer filter). The chain stuffs those documents plus the query into a prompt template and sends it to the LLM. It returns the generated answer plus the source documents. `chain_type='stuff'` because five short patterns fit in one prompt — no need for map-reduce or refine."

**What is a Retriever?**
> "The component that, given a query, returns relevant documents. Mine is `QdrantVectorStore.as_retriever()` with `k=5` and a metadata filter on vendor and layer. It abstracts 'embed the query, search Qdrant, apply the filter, return matches' behind one interface."

**What is a Chain?**
> "A composed sequence of steps — here, retrieve → assemble prompt → call LLM → return. The chain is what turns individual components into one callable pipeline."

**What is PromptTemplate?**
> "A parameterised prompt with slots. Mine injects the vendor and layer into a role instruction ('you are a 5G ops expert on {vendor} at {layer}'), then the retrieved patterns as context, then the specific error, and demands four structured sections: DIAGNOSIS, FIX, CONFIDENCE, MATCHED_PATTERN — plus an explicit instruction to say so if the patterns don't match rather than guess."

**What is memory in LangChain?**
> "Memory persists state across calls in a conversational chain — prior turns carried into the next prompt."

**Did you use Conversation Memory?**
> "No. Each error is an independent, stateless query — there's no conversation to carry. Memory would add state I don't need and a source of cross-contamination between unrelated errors. Deliberately stateless."

**What chunk size did you use?**
> "None — there's no document chunking in this project. That surprises people expecting a standard RAG doc-splitting story, but my knowledge base entries are short, self-contained error patterns. One pattern is one embedded unit. Chunking exists to fit long documents into context and preserve retrieval granularity; my documents are already a paragraph, so splitting them would only fragment a coherent pattern."

**How did you split documents?**
> "I didn't, for the reason above — each error pattern is atomic. If the knowledge base ever held long-form troubleshooting guides instead of discrete patterns, then I'd introduce a splitter (recursive character or semantic) — but for discrete patterns it would be wrong."

**How did you avoid hallucinations?**
> "Four layers, none of them 'trust the model' (full version in Q38 above). The fix is *grounded* — the retrieved pattern carries a known human-written fix, so Claude adapts rather than invents. The 0.65 threshold returns nothing on a weak match. The prompt explicitly licenses abstention. And the output is advisory and shows its source documents — a human reviews and executes; there's no path from model output to a live command. temperature=0.1 also keeps it near-deterministic."

---

### 7. LLM

**Which LLM did you use?**
> "Claude — two models with routing: `claude-sonnet-4-6` as the default deep-reasoning model, and `claude-haiku-4-5` on the fast path for high-confidence, non-critical matches."

**Why that model?**
> "Claude for strong instruction-following and structured output on a synthesis task. Two models because most errors are confident single matches that Haiku handles fine at lower cost and latency, while ambiguous or critical ones deserve Sonnet. The routing (Q24 above) cut cost roughly 60% without giving up quality on the hard cases."

**How does the LLM generate remediation suggestions?**
> "It's given the retrieved known patterns — including their known fixes — plus the specific error and its metadata, and asked to produce a fix *contextualised to this instance*: the specific timing, node, retry count. So it's not authoring from scratch; it's adapting a vetted fix. That's why the output is 'increase T3560 from 1s to 3s because this occurred during a traffic spike on poor signal,' not a generic 'check the timer.'"

**How do you prevent incorrect fixes?**
> "Grounding (adapt a known fix, don't invent), the 0.65 threshold (no confident match → no fix), the vendor+layer filter (never a cross-vendor fix), and the advisory model (a human executes). The most important capability is the system's willingness to say 'I don't know — manual review.'"

**How do you control response length?**
> "The prompt structure — four defined sections — bounds it naturally, and I could set max_tokens on the client. It's not free-form; the model fills a template."

**What prompt did you use?**
> "A role-scoped template: '5G ops expert on {vendor} at {layer}', then the retrieved patterns as context, then the new error, then a demand for DIAGNOSIS / FIX (with specific timer and parameter names) / CONFIDENCE / MATCHED_PATTERN — and the abstention instruction: if the patterns aren't a good match, say so rather than guessing."

**Did you use system prompts?**
> "The role and instructions are set as the system/instruction frame of the template — the stable part — with the retrieved context and specific error as the variable part. Keeping the instructions in the stable frame is also what makes them cacheable and consistent."

**How did you evaluate LLM responses?**
> "Honestly — there was no automated fix-quality evaluation in this project. The quality signal was human: engineers using it and the escalation rate. That's the weakest part of the system, and it's exactly the gap that pushed me to build a separate LLM Evaluation Framework and Prompt Regression Suite — golden sets and regression harnesses for LLM output. I'd wire those in here. `[FILL: any before/after or spot-check numbers you actually have.]`"

**What if no relevant document is found?**
> "If nothing comes back above 0.65, the pipeline returns no fix, flags the error 'unknown pattern — manual review required,' and logs it to a separate `unknown_errors` collection for the ops team to resolve and promote into the knowledge base. The system improves from its own misses instead of guessing."

---

### 8. Redis

> ⚠️ **RESOLVE THIS BEFORE THE INTERVIEW.** Redis is on your resume ("Redis caches frequent error lookups") but the deep-dive contains no Redis implementation. You must decide which is true and answer consistently. Two honest positions below — pick the real one. Do **not** invent a TTL and an eviction policy you never wrote; that's the fastest way to get caught, because the follow-ups are specific.

**If Redis was genuinely in the system — the defensible design:**

**Why Redis?**
> "The same error signatures recur constantly across pcaps — the same NAS cause 24, the same SIP 503. Re-embedding an identical error text and re-querying Qdrant for it every time is pure waste. Redis caches the retrieval result so a repeat error skips the embedding call and the vector search."

**What data did you cache?**
> "The retrieval result — the matched patterns — keyed by the error signature. `[FILL: did you also cache the generated fix? If so, that's the risky one — see expiration below.]`"

**What cache key did you use?**
> "`(error_text, vendor, layer)` — the signature that determines the retrieval result. `[FILL: confirm actual key.]`"

**What TTL did you configure?**
> "The thing that makes a cached entry stale is a knowledge-base update — and in this project the KB changes on-demand, only when the ops team adds a pattern for a novel error, so it's infrequent. On that basis a TTL of **1 hour** is the sensible default: short enough that a new pattern propagates within the working session, long enough to catch the constant repeat-error traffic where the same NAS cause 24 or SIP 503 recurs all day.
>
> But TTL is the *weaker* mechanism here, and I'd say so: a time-based expiry is a guess about how much staleness is acceptable. The correct invalidation signal isn't time, it's the knowledge-base version. So I'd version-key the cache — include a KB version number in the key and bump it on every re-index — and then every stale entry is orphaned *instantly* the moment the knowledge base changes, no scan, no waiting for expiry. TTL then becomes just a memory-hygiene backstop (set it long, say a day), and the version-key does the correctness work. So: 1 hour if relying on TTL alone, but really version-keyed to the KB so a re-index invalidates immediately."
>
> *`[FILL: if Redis was genuinely in the build and you set a specific TTL, state your real value instead. The above is the defensible design answer, not a claim about what you configured.]`*

**How much latency did Redis reduce?**
> "`[FILL: only quote a number you actually measured. If you didn't, say 'it removes the embedding round-trip and the vector search on repeats — but the LLM call dominates latency anyway (Q46), so the win is on cost and on repeat-error throughput, not on the tail latency of a fresh error.']`"

**What happens after cache expiration?**
> "On a miss it falls through to the normal path — embed, search, cache the fresh result. The important design point: if I cached the *fix*, expiration alone isn't enough — a cached fix outliving a knowledge-base update would serve stale remediation, so the cache key should be versioned with the knowledge base and invalidated on re-index, not just aged out."

**What cache eviction policy did you use?**
> "`[FILL: allkeys-lru is the sensible default for a cache — say that only if it's what you set. If you didn't configure one, say 'default, and I'd set allkeys-lru for a pure cache workload.']`"

**If Redis was NOT actually in this project:** take it off the resume bullet, or move it to the project where it *is* real. A listed technology you can't walk through is a landmine precisely because an interviewer probes keywords. Better to have a clean, smaller stack than one impressive-looking word you can't defend.

---

### 9. Python

**How did you structure your Python project?**
> "By stage, one module per responsibility: `extractor.py` (Pyshark → `ExtractedError`), `qdrant_setup.py` (indexing + direct search), `retrieval_chain.py` (the LangChain chain), `model_router.py` (Haiku/Sonnet decision), `pipeline.py` (the orchestrator tying them together), plus `main.py` (FastAPI) and `ui.py` (Streamlit). Each stage is independently testable and swappable."

**Which design patterns did you use?**
> "A dataclass as the data contract (`ExtractedError`, `RemediationResult`) passed between stages. A pipeline/pipe-and-filter structure — each stage takes the previous stage's output. And a routing/strategy decision for model selection. Nothing heavier — the value was in keeping stages decoupled, not in pattern ceremony."

**Did you use generators?**
> "Yes, implicitly — Pyshark's `FileCapture` is iterated packet by packet, and with `keep_packets=False` that's a streaming iteration, not a materialised list. That's what keeps memory constant on large pcaps."

**How did you handle exceptions?**
> "Field access in the extractor is wrapped in try/except on `AttributeError`, because a missing packet field raises that — and I return `None` and skip rather than crash the whole file for one bad packet. The honest weakness (Q, limitations): a bare `except AttributeError: pass` means a malformed packet and a genuinely-absent field look identical, so some skips are silent. In the API layer, provider/HTTP errors map to clean responses rather than 500s."

**How did you parse nested packet fields?**
> "Via Pyshark's attribute access — `packet.nas_5gs.cause_5gmm`, `packet.ngap.cause_group` — with `hasattr`/`getattr` guards because not every packet has every layer or field. Layer detection dispatches to the right extractor per protocol."

**How did you optimize performance?**
> "The big ones: the tshark display filter (shrink the packet set in C before Python), `keep_packets=False` (constant memory), model routing (cheap model on easy cases), and the 0.65 threshold short-circuit (no LLM call when there's no match). The LLM call dominates latency, so optimisation effort belongs in *avoiding* it, not in the retrieval path (Q46)."

**Did you use multithreading?**
> "No. As written, the pipeline is single-threaded — `process_pcap` iterates errors in a plain sequential loop, and there's no threading anywhere in the code. The natural concurrency point, if I added it, is the per-error LLM calls: those are I/O-bound (waiting on the Claude API), so `asyncio` would let many run in parallel without threads. That's the change I'd make to speed up a pcap with many errors."

**Did you use multiprocessing?**
> "No — there's no multiprocessing in the code as written. Where it would fit: Pyshark/tshark parsing is CPU-bound, so if I needed to process many pcap files at once, the right move is multiprocessing across files — one process per file — since CPU-bound work doesn't benefit from async or threads (the GIL). That's the scaling answer for the 1000-files/day question (Q40)."

**How did you manage memory?**
> "`keep_packets=False` is the key one — packets aren't retained after processing. The display filter also means far fewer packets are ever constructed. So memory stays roughly constant regardless of pcap size."

---

### 10. Database

**Why use a vector database instead of SQL?**
> "Because the query is 'find the most *semantically similar* known error,' and SQL can't do that — SQL matches exact values or patterns, not meaning. 'T3560 timeout' and 'NAS authentication timeout' share no keywords but mean the same thing; a vector DB finds that by comparing embeddings, a SQL `LIKE` can't. I still need the exact-match part — vendor and layer — and Qdrant does that too, as a metadata filter alongside the similarity search. So it's both: exact filter + semantic rank."

**What is embedding?**
> "A learned numeric vector that represents the *meaning* of a piece of text — 1536 numbers, in my case. Texts with similar meaning map to vectors that point in similar directions, which is what makes semantic search possible."

**How is semantic search different from keyword search?**
> "Keyword search matches exact words; semantic search matches meaning. 'T3560 timer expired' finds my stored 'NAS authentication timeout after registration attempt' even with zero shared words, because both embed to nearby vectors. Keyword search would return nothing. I embed the error, and Qdrant finds the nearest stored vectors by cosine similarity."

**How are embeddings stored?**
> "As the vector of each Qdrant point, indexed with HNSW for fast approximate nearest-neighbour search, with the human-readable text and metadata alongside in the point's payload. The collection is created at a fixed 1536 dimensions — which means swapping the embedding model is a re-index, not a config change (Q45)."

---

### 11. Performance

**How many PCAP files can your system process?**
> "As built, it's synchronous per file, so throughput is bounded by the per-file time. To scale to high volume (Q40) I'd add Celery for background jobs and multiprocess the tshark parsing across files. `[FILL: any real throughput number you measured — otherwise don't quote one.]`"

**What is the average processing time?**
> "`[FILL: the real per-pcap number — know this cold.]` What I can state structurally: per error, the LLM call dominates by one to two orders of magnitude — embedding is tens of milliseconds, the Qdrant search is single-digit milliseconds, and the Claude call is seconds. So processing time scales with the number of *errors* found times the LLM latency, not with pcap size."

**What is the bottleneck?**
> "The LLM call, unambiguously. Vector search was never the bottleneck. That's why the optimisations that matter are the ones that *avoid* an LLM call — Haiku routing on easy cases, the 0.65 threshold short-circuit, and caching on repeat errors — not tuning retrieval."

**How did Redis improve performance?**
> "`[FILL: only if Redis is real — see Section 8.] `If present, it removes the embedding round-trip and vector search for *repeat* error signatures — so the win is on cost and repeat-error throughput, not on the latency of a fresh error, which is dominated by the LLM. If Redis wasn't actually in the build, say so and don't claim a Redis speedup."

**What optimizations did you implement?**
> "Display filter (C-side packet reduction), `keep_packets=False` (constant memory), DB-level metadata filtering (smaller similarity search space), model routing (~60% cost cut), and the threshold short-circuit (skip the LLM entirely on no-match)."

**How scalable is the system?**
> "The retrieval and generation scale well — Qdrant shards horizontally, the LLM is a stateless external call. The scaling work is on ingestion: make the endpoints async, move pcap analysis to a Celery queue with a job-id/poll pattern (analysis takes 5–30s, too long to hold an HTTP connection), and multiprocess parsing. I'd add Celery first, because the long-request problem bites at 10 files a day, not 1000."

---

### 12. Scenario-Based Questions

**Suppose authentication timeout occurs repeatedly. What will your system do?**
> "Each occurrence is detected the same way — cause 24 — and matched to the same known pattern, so it returns the same fix (temperature 0.1 keeps it consistent). If Redis caching is in place, the repeats are served from cache without re-embedding. What the system does *not* currently do is recognise 'this is the same recurring incident' and escalate differently — it treats each as an independent error. Recurrence detection would be a good addition: a repeated identical signature is itself a signal that the suggested fix didn't stick."

**If Redis is down, how does your application behave?**
> "`[FILL: only if Redis is real.]` It should degrade gracefully — a cache being down means fall through to the normal embed-and-search path, slower but fully functional. A cache must never be a hard dependency. If Redis isn't actually in the build, answer honestly that there's no cache layer to fail."

**If the vector database is unavailable, what happens?**
> "That's a hard dependency — no Qdrant, no retrieval, no grounded fix. The correct behaviour is to fail cleanly with a clear error and *not* fall through to an ungrounded LLM call, because an LLM generating a fix with no retrieved patterns is exactly the hallucination risk the whole design avoids. Better to return 'retrieval unavailable' than a confident guess."

**How would you process live packet captures instead of PCAP files?**
> "Pyshark has a `LiveCapture` mode over an interface instead of `FileCapture` over a file — the same display filter and extraction logic apply. The real change is that it becomes a streaming pipeline: errors arrive continuously, so I'd feed them onto a queue and process asynchronously rather than batch-per-file. Detection stays identical; the orchestration becomes event-driven."

**How would you deploy this project in production?**
> "Containerised — Qdrant already runs as a Docker container, and the FastAPI app and Streamlit UI each in their own. docker-compose for the stack; Kubernetes if it needs to scale out. Secrets (API keys) via environment/secret store, never in the image. Add Celery workers for async pcap jobs."

**How would you monitor the pipeline?**
> "Metrics I'd expose: errors detected per pcap, match rate vs. no-match (below-threshold) rate, model-routing split (Haiku vs Sonnet), LLM latency and cost, and the size of the `unknown_errors` collection over time. That last one is the real health signal — a growing unknown rate means the knowledge base is falling behind the network. Plus standard request metrics and error rates on the API."

**How would you handle millions of packets per hour?**
> "The display filter already discards the vast majority in C before Python — that's the first defence, because only error packets matter. Beyond that: multiprocess the parsing (one worker per pcap/stream), queue the errors, and scale the LLM stage horizontally since it's a stateless external call. The packet volume is handled by filtering early; the real scaling constraint is the number of *errors*, because each error costs an LLM call."

---

### 13. Advanced AI Questions

**What is Retrieval-Augmented Generation (RAG)?**
> "Instead of relying on what a model learned in training, you *retrieve* relevant documents at query time and put them in the prompt, so the model generates grounded in current, specific knowledge. My pipeline is RAG: retrieve the matching error patterns from Qdrant, then have Claude generate the fix grounded in them."

**Why use RAG instead of fine-tuning an LLM?**
> "Three reasons here. The knowledge base changes constantly — every resolved novel error is a new pattern — and with RAG that's a re-index, whereas fine-tuning would be a retraining cycle for every update. RAG gives *provenance* — I can show the engineer which pattern the fix came from, which fine-tuning can't. And it's cheaper and faster to iterate. Fine-tuning changes *behaviour/style*; RAG injects *knowledge* — and my problem is a knowledge problem."

**Difference between embeddings and tokens.**
> "Tokens are the chunks of text the model reads — sub-word units. An embedding is a single vector representing the *meaning* of a piece of text (a word, a sentence, a document). Tokens are the input units; an embedding is a semantic representation you can compare with cosine similarity."

**What are embedding dimensions?**
> "The length of the embedding vector — 1536 for the model I used. Each dimension is a learned feature of meaning. More dimensions can capture finer distinctions but cost more storage and compute. The number is fixed by the model, and it's baked into the Qdrant collection — which is why swapping models means a re-index."

**What is semantic similarity?**
> "How close two pieces of text are in *meaning*, measured as the cosine similarity of their embeddings. High similarity = same meaning even with different words. It's the core operation of the retrieval stage."

**What is prompt engineering?**
> "Deliberately structuring the prompt to get reliable, correct output. In my case: scoping the model to a role (vendor+layer expert), supplying grounded context, demanding a fixed output structure, and explicitly licensing abstention ('say so if the patterns don't match'). It's the difference between a generic answer and a specific, safe one."

**What are hallucinations?**
> "When a model generates confident, fluent output that isn't grounded in fact — a plausible fix that's simply wrong. It's the central risk of putting an LLM near a live network. I contain it with grounding, the similarity threshold, abstention, and keeping the system advisory (Q38)."

**How does context improve LLM accuracy?**
> "It replaces the model's fuzzy parametric memory with specific, correct facts for *this* query. Given the actual known pattern and the actual error metadata, Claude adapts a vetted fix instead of recalling a generic one — grounded in-context knowledge beats trained-in memory for a factual, current task."

**How would you improve retrieval quality?**
> "A domain-adapted or fine-tuned embedding model — general embeddings do fine because the metadata filter carries the domain precision, but they'd struggle to separate two similar timers within one vendor and layer (T3560 vs T3510). Also: better knowledge-base curation (dedupe patterns, version fixes against network software release), and possibly hybrid search (semantic + keyword) so an exact error code is always an exact hit."

---

### 14. HR/Ownership Questions

**What was the biggest challenge?**
> "Making a probabilistic tool trustworthy enough for engineers to act on against a live network. The technical core was standard RAG; the hard part was the safety discipline — never surfacing a cross-vendor fix, refusing to answer below a confidence threshold, and keeping the tool advisory so a human always executes. In telecom, a confident wrong fix is worse than no tool at all."

**What bug took the longest to fix?**
> "The vendor black hole (Q44). Errors were coming back flagged 'no known pattern,' so I assumed knowledge-base gaps and spent `[FILL: time]` writing more patterns — and it didn't help. The real cause: vendor detection was returning `unknown`, which went straight into the Qdrant filter as `vendor = unknown`, matched zero rows, and the pipeline honestly reported 'no pattern.' A classification failure disguised as a coverage failure — the two need completely different fixes and the system reported them identically. Fix: fail loudly on unresolved vendor, and source vendor from capture metadata instead of string-matching the packet. `[FILL: confirm this actually happened to you before telling it as a war story.]`"

**If you rebuilt this project today, what would you change?**
> "Four things: structured output from the model instead of parsing confidence out of prose; an automated fix-quality eval set instead of relying on humans not complaining; vendor from capture metadata, not packet string-matching; and a domain-adapted embedding model if precision needed to climb. And I'd add UE/session correlation so multi-message failures are analysed as procedures, not isolated packets."

**What did you learn from this project?**
> "That putting an LLM into an operational environment is a *containment* problem, not a modelling problem. The interesting engineering wasn't making the model right — it was designing for what happens when it's wrong: the threshold, the filter, the abstention, the advisory boundary. And that the dangerous output was never the obviously-wrong one — it was the one that was right about the error and wrong about the network."

**How does this project relate to real telecom operations?**
> "Directly — it came out of watching operations engineers spend hours on pcap diagnosis and lose the same institutional knowledge every time a senior went on leave. It's partly a diagnostic accelerator and partly institutional-memory capture. It plugs into the real workflow: an engineer gets a vendor-specific, grounded fix suggestion with its source, reviews it, and executes — turning hours of manual analysis into a seconds-long advisory pass while keeping the human in control."

---

## Core Interview Focal Points

If this project appears on your resume, be especially prepared for these:

* **Explain the end-to-end architecture.**
* **How did you detect authentication timeouts from PCAP files?**
* **Why use Pyshark instead of Scapy?**
* **Explain the complete RAG pipeline.**
* **Why use a vector database?**
* **How does RetrievalQA work?**
* **How are embeddings generated?**
* **Why use Redis, and what exactly is cached?**
* **What happens when a new error pattern is encountered?**
* **What would you improve to make the system production-ready?**

> Being able to answer these confidently will cover the majority of technical follow-up questions for this project.