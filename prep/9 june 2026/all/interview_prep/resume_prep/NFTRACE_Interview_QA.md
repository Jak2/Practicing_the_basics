# NFTRACE — Interview Q&A
### Distributed REST-based network function tracing platform (Nokia Networks)
### 40+ questions, organised by attack surface

**Ground rule for this doc:** every fact below traces to `NFTRACE_Deep_Dive.md`. Anything the source does not contain is marked `[FILL: ...]`. Do not improvise over a `[FILL]` in the room — say "I'd have to check" instead. A wrong number is worse than a gap.

---

## READ THIS FIRST — where this project is actually attackable

The interviewer is a systems person. They will not ask you what FastAPI is. They will go straight at the seams. These are the seven questions that can genuinely hurt you, and why.

| # | The question | Why it hurts | Your one-line posture |
|---|---|---|---|
| 1 | "Two workers hit `/sessions/stop` for the same session at the same time. Walk me through it." | Every endpoint does **read Redis → mutate dict → `setex` back**. No `WATCH`/`MULTI`, no Lua, no lock. It's a textbook lost-update read-modify-write race. | Concede it. "There is no compare-and-set. It's last-write-wins. Here's the exact window and here's what I'd add." |
| 2 | "You say session isolation. What actually stops Worker 2 from stopping Worker 1's trace?" | Nothing does. `worker_id` is stored in the Redis blob at start but **never checked** in `/sessions/stop`, `/merge` or `/validate`. Isolation is by *UUID unguessability*, not by *authorization*. | "It's isolation by namespacing, not by ownership. Anyone holding the session_id can stop it. The fix is three lines and I never wrote them." |
| 3 | "SQLite + parallel workers. SQLite serializes writers. Doesn't that contradict your own design?" | The deep-dive justifies SQLite by claiming *"sequential write patterns — one session completes, then the next writes."* But `/sessions/merge` and `/validate` both write SQLite, and N workers merge concurrently. The premise is shakier than the doc admits. | "The justification I wrote is the weakest sentence in the design. Writes are sequential *per session*, not across sessions. It survived because write volume is tiny — two writes per session, not because the reasoning was right." |
| 4 | "Redis is your live state, SQLite is your history. What happens when they diverge?" | SQLite is only written at **merge** and **validate**. A session that starts and dies before merge exists **nowhere on disk**. The 3600s TTL then silently deletes it, and the traces on the nodes are never stopped. | "They can't diverge, because there's nothing to diverge *from* until merge. That's the real bug — the write to durable storage happens too late." |
| 5 | "Your TTL is 3600 seconds. What's your longest test?" | If any test (or any gap between `stop` and `merge`) exceeds one hour, Redis drops the key, `/sessions/stop` returns 404, and the capture on the physical node **runs forever**. A resource leak on shared lab hardware. | Give the number if you have it: `[FILL: longest real test scenario runtime in the NCD pipeline]`. Otherwise concede the TTL was a guess. |
| 6 | "Where's the 50% reduction number from? How did you measure it?" | **The source does not substantiate it.** It is asserted three times (lines 29, 896, 974) with zero methodology — no baseline, no sample size, no instrument. | Have a real answer ready or downgrade the claim. See Q34. This is your single largest exposure. |
| 7 | "You keep saying 'distributed.' What's distributed about it?" | One FastAPI server, one Redis, one SQLite **file**, one `/tmp` directory. The *nodes* are distributed. The *platform* is a single box. | "The workload is distributed; the control plane is a single server. Calling it a distributed system in the CAP sense would be a stretch and I'm not going to." |

**Rule:** on 1–5, concede fast and precisely. A precise concession reads as ownership. A vague defence reads as a bluff — and a systems interviewer will chase a bluff for ten minutes.

---

## SECTION 1 — FRAMING

**Q1. Give me NFTRACE in ninety seconds.**

> It's a REST platform that automates 5G trace capture inside a CI/CD pipeline. Before it, validating a network function meant a test engineer manually starting a packet capture on each node — gNB, AMF, UPF, SMF, AUSF — running the scenario, manually stopping each capture, pulling the files off each node one at a time, running dissection scripts locally, and eyeballing SIP and Diameter signalling by hand. Hours per scenario, and not repeatable.
>
> NFTRACE turns that into four HTTP calls: `POST /sessions/start`, `/sessions/stop`, `/sessions/merge`, `/sessions/validate`. FastAPI on the front, Redis holding live session state so parallel workers don't collide, SQLite for history, and XML-RPC out the back because that's the only interface the network nodes expose. It's wired into Nokia Continuous Delivery so any test tagged `trace` captures and validates automatically.

**Q2. What was actually yours?**

> `[FILL: your exact scope — did you design the whole thing or own specific layers? Which parts did you personally write vs. inherit? Be precise; "architected" in the bullet sets a high bar and they will probe it.]` The one piece the source records as unambiguously recognised work is the TAF/NCD integration — the `pre_test`/`post_test` hooks that let a test *pass its assertions but still fail trace validation*.

**Q3. Who used it, and how many of them?**

> `[FILL: number of test engineers / teams / pipelines using NFTRACE, and over what period]`

**Q4. Why does trace validation matter if the test already passed?**

> That's the point of the whole thing. A test can pass at the application level — the UE registered successfully — while the Diameter signalling underneath had a timing violation or a missing message. The assertion says PASS; the network behaviour was wrong. The NCD hook is explicit about this: if `report["failed"] > 0` and `test_status == "PASS"`, it flags a trace failure on the job. That catches a class of defect that was previously invisible, because nobody was looking at the packets.

---

## SECTION 2 — ARCHITECTURE

**Q5. Draw me the request path for a single trace.**

> Worker calls `POST /sessions/start` with `worker_id`, `nodes`, `scenario`, `mode`, optional `filter_profile`. FastAPI mints a `uuid4` session_id, writes the session blob into Redis under `session:{session_id}` with a 3600-second TTL and state `STARTING`. It constructs a `NodeManager`, which resolves each node_id to a hostname/port out of the SQLite `nodes` table, then fans out over `multiprocessing.Pool.starmap` to call `proxy.trace.start(session_id, filter_profile)` on every node at once. State flips to `ACTIVE`, Redis is rewritten. The test runs. `stop` fans out `proxy.trace.stop(session_id)`. `merge` pulls each node's pcap back over XML-RPC, writes them to `/tmp/{session_id}_{node_id}.pcap`, and shells out to `mergecap -w` to produce `/tmp/{session_id}_merged.pcap`. `validate` runs pyshark over the merged pcap with a display filter of `sip` or `diameter` and applies rule IDs. SQLite gets written at merge and again at validate.

**Q6. Why four separate endpoints instead of one `POST /trace` that does everything?**

> Because the test scenario has to run *between* start and stop, and NFTRACE isn't the thing running it — TAF/Robot Framework is. The lifecycle has to be split at exactly the point where control leaves the platform. That's also the decoupling the resume bullet refers to: the test scenario knows nothing about validation logic, and the validation rules know nothing about the scenario. They meet only through a session_id.

**Q7. Why is `merge` a separate call from `stop`? You could merge on stop.**

> `[FILL: your real reason. Honest candidate answer supported by the code: merge is expensive — it pulls 50–200MB of pcap per node over XML-RPC and shells out to mergecap — and keeping it separate lets stop return fast so the test worker can move on. But the source does not state this rationale, so don't claim it as remembered fact.]`

**Q8. What's the state machine?**

> `STARTING → ACTIVE → STOPPED → MERGED → VALIDATED`. It's enforced in two places only: `/merge` rejects anything not in `STOPPED` with a 400, and `/validate` rejects anything not in `MERGED` — except it also accepts `ACTIVE`, which is a bug I'll happily walk you through.

**Q9. That bug — go on.**

> `/sessions/validate` guards with `if session["state"] not in ("MERGED", "ACTIVE")`. Letting `ACTIVE` through means you can validate a session that was never merged, so `session.get("merged_file")` is `None`, and `ProtocolValidator` hands `None` to `pyshark.FileCapture`. It's a state-machine hole that a single test with an out-of-order call would catch. I'd tighten it to `MERGED` only.

**Q10. Where does the session state actually live — Redis or SQLite?**

> Redis is authoritative for anything live. SQLite is authoritative for anything finished. `GET /sessions/{session_id}` encodes exactly that: read Redis, and on a miss fall through to `db_client.get_session(session_id)`. The problem is the *seam*: SQLite is first written at merge. So there's a window — from start until merge — where a session exists only in a volatile store with a one-hour TTL.

---

## SECTION 3 — CONCURRENCY (the sharpest section — know it cold)

**Q11. Two workers call `/sessions/stop` on the same session_id simultaneously. What happens?**

> Both read the same JSON from Redis. Both build a `NodeManager` and both fan out `proxy.trace.stop(session_id)` to every node — so the node gets a duplicate stop, and whether that's idempotent is a property of the node firmware, not of my code `[FILL: is proxy.trace.stop idempotent on the real nodes? Confirm — this determines whether the duplicate stop is harmless or an error]`. Then both write `state=STOPPED` back with `setex`. Last write wins. In this specific case the outcome is benign because both writes are identical. It is not benign in Q12.

**Q12. Now make it not benign.**

> Interleave `stop` and `merge`. `merge` reads the session, checks `state == STOPPED`, does the collect-and-merge, then writes back a dict containing `state=MERGED` **and** `merged_file`. If a `stop` for the same session read *before* that write and lands *after* it, the `stop` writer's dict has no `merged_file` key — it overwrites the merged one and the file path is gone. The pcap still exists on disk at `/tmp/{session_id}_merged.pcap`, but the session no longer knows about it, and `/validate` will run pyshark on `None`. That's a lost update, and it's structural: every endpoint is a read-modify-write against a single Redis string with no compare-and-set.

**Q13. So there's no lock anywhere?**

> No. No Redis lock, no `WATCH`/`MULTI`, no Lua script, no `SETNX` claim, no row lock. The design leans on the assumption that one session is only ever driven by one worker — which the client SDK does enforce, because `NFTraceClient` holds a single `self.session_id` and drives it linearly. The assumption holds in practice and is nowhere enforced by the server. That's the honest answer.

**Q14. How would you fix it?**

> Cheapest correct fix: stop storing the session as one opaque JSON string. Use a Redis **hash** and mutate fields with `HSET`, so `stop` writing `state` cannot clobber `merged_file` — the two writers touch different fields. That kills the whole class of lost update in Q12 without introducing a lock.
>
> For genuine mutual exclusion on the lifecycle transitions, add a per-session lock: `SET lock:{session_id} {worker_id} NX EX 60`, held across the transition, released by a Lua compare-and-delete so you can't release someone else's lock. And gate the transition itself on an atomic CAS — a small Lua script that reads state, checks the expected value, and writes the new one in one round trip.

**Q15. You said the SDK enforces one-worker-per-session. Show me where that breaks.**

> The batch-mode example breaks it, and it's in the source. It creates N sessions in a loop, keeps the IDs in a list, then reassigns `client.session_id = session_id` on one shared client object to drive each one. That's a single client mutating a field to time-share across sessions. It's fine while it's sequential. The moment someone parallelises that loop — which is exactly what "batch mode for CI/CD overnight runs" invites — you have concurrent mutation of `client.session_id` and workers stopping each other's sessions. The protection was convention, and the convention is one `for` loop away from being violated.

**Q16. Two different workers trace the same physical node at the same time. Does that work?**

> It works only if the node itself supports multiple concurrent named captures, keyed by the session_id I pass into `proxy.trace.start(session_id, filter_profile)`. That's the load-bearing assumption of the entire isolation story: my session isolation is only real if the *node's* capture is also session-scoped. If the node's `trace.start` is a global toggle, then Worker 2's start reconfigures Worker 1's capture and Worker 2's stop kills it — and my Redis isolation buys me nothing, because the collision is downstream of Redis. `[FILL: confirm the node's XML-RPC trace interface is genuinely session-scoped — this is the single assumption the isolation claim rests on]`

**Q17. `multiprocessing.Pool(processes=len(self.nodes))` — anything wrong with that?**

> Two things. It forks a process pool on every single start and every single stop, so per-session you pay two pool spin-ups; for 5–10 nodes that's noise, and the design says so explicitly, but it's not free. And `Pool(processes=0)` raises a `ValueError` — so if `_resolve_nodes` returns an empty list, because every node_id in the request was missing from the SQLite `nodes` table, the endpoint blows up with an unhandled exception rather than a clean 400. `_resolve_nodes` silently skips rows it can't find; it should reject unknown node_ids at the boundary.

**Q18. Why multiprocessing and not asyncio?**

> The nodes speak XML-RPC and `xmlrpc.client` in the standard library is synchronous. Going async meant adding an async XML-RPC dependency. `Pool.starmap` gave true parallel fan-out with stdlib only. And the fan-out has to be genuinely simultaneous — if you start node 1, then node 2, then node 3 sequentially, you miss the opening messages on nodes 2 and 3, which are usually the interesting ones in a registration flow. For 5–10 nodes it's the right trade. At 50+ nodes I'd switch to asyncio with an async XML-RPC client — that's in my own "what I'd change" list.

**Q19. Is `merge` parallel too?**

> No — and that's an inconsistency I'd flag against my own design. `start_trace` and `stop_trace` use `Pool.starmap`; `collect_and_merge` is a plain `for` loop over the nodes, pulling each file sequentially. Since the file pull is the single most expensive step — 50–200MB per node over XML-RPC — merge is the one place parallelism would actually pay, and it's the one place I didn't use it.

---

## SECTION 4 — REDIS

**Q20. Why Redis at all? Why not a dict in the FastAPI process?**

> A dict dies with the process. If the NFTRACE server restarts mid-run, every active session vanishes and every running worker is stranded — it can't stop its trace, can't collect its files, and the captures keep running on the nodes. Redis survives the API process restarting. That's the whole argument; it's about the blast radius of a server restart, not about speed.

**Q21. Why not SQLite for session state too, then?**

> Access pattern. Session state churns — `STARTING → ACTIVE → STOPPED → MERGED → VALIDATED`, several writes per session, from many workers at once. SQLite serializes writers on a disk file. Redis is in-memory with sub-millisecond writes and no writer lock. SQLite carries the cold path: completed history, read occasionally.

**Q22. Redis evicts your key mid-run. What breaks?**

> Everything downstream, silently. `/sessions/stop` does `redis_client.get(...)` and raises a 404 — "Session not found or expired". The worker cannot stop its own trace. The physical node keeps capturing, holding the file open, filling disk on shared lab hardware, and nobody ever collects it. And because SQLite isn't written until merge, the session leaves no record at all — it's as if it never existed. It's the worst failure mode in the system: not a crash, a leak that's invisible until the node's disk fills.

**Q23. So the TTL is a bug?**

> The TTL is doing two jobs and only one of them well. It's a garbage collector for orphaned sessions — worker crashed, nobody will ever call stop — and for that it's exactly right, it's why there's no cleanup cron. But it's also, accidentally, a hard ceiling on session lifetime, and nothing in the code ties that ceiling to how long tests actually run. Every write refreshes it to 3600, so it's really "one hour of inactivity", not "one hour total" — which softens it, because start→stop→merge→validate each reset the clock. The exposed gap is the one between `start` and `stop`: that's the actual test duration, with no intermediate writes. If a scenario runs over an hour, the session evaporates underneath it. `[FILL: longest test scenario runtime — if it's well under an hour, say so, and the TTL is defensible; if not, this is a live bug]`

**Q24. Fix it.**

> Two changes. First, decouple the TTL from the test: on `start`, set the TTL from the caller's declared max duration rather than a hard-coded 3600, or have the SDK heartbeat the key while the test runs. Second, and more important — write the session row to SQLite at **start**, not at merge. Then Redis is a pure cache, SQLite is the ledger, and an evicted key is a cache miss you can recover from instead of an amnesia event. That's a genuine design error in the version I built: durable state was written too late.

**Q25. Redis and SQLite disagree. Which one is right?**

> During a run, Redis — it's the only one with the current state. After validate, they should agree, because `/validate` writes both. But the honest answer is that the code has no reconciliation path at all: `GET /sessions/{id}` reads Redis and falls back to SQLite, so if they disagree you get whichever store you happened to hit. There is no version number, no updated_at comparison, nothing to detect the divergence. In practice divergence is rare because SQLite is only written from two places and both are after Redis. In principle it's undetectable, and that's a design gap, not a feature.

**Q26. Single Redis instance?**

> Yes — `redis.Redis(host="localhost", port=6379)`. Localhost, same box as the API. No cluster, no sentinel, no replica. It's a single point of failure and it means the "distributed" platform has an entirely centralized control plane. For an internal lab tool where the failure mode is "restart Redis, re-run the pipeline", that was an acceptable trade. It would not be acceptable if this were customer-facing.

**Q27. Is Redis configured to persist?**

> `[FILL: was RDB/AOF persistence enabled on the Redis instance? The code only ever calls setex — the durability claim in the design ("Redis persists across restarts") depends entirely on the Redis config, not on anything in this codebase.]` I'd flag that the design doc asserts Redis survives restarts, and that assertion is only true if AOF or RDB was actually turned on. If it was running with default in-memory-only settings, that claim is wrong.

---

## SECTION 5 — SQLITE

**Q28. Why SQLite over Postgres?**

> Single server in the test lab, low write volume, no replication requirement, and no DBA to run a Postgres install. SQLite is a file — zero infrastructure, no connection pool, no credentials to manage. For an internal tool where the cost of an extra service is a person's afternoon every quarter, that's the right call. The migration trigger would be multi-server deployment or hundreds of concurrent writes.

**Q29. But SQLite has a single-writer lock, and you have N concurrent workers. Isn't your justification wrong?**

> Partly, yes — and this is the weakest sentence in my own design doc. I justified SQLite with "sequential write patterns: one session completes, then the next writes." That's true *within* a session and false *across* sessions: twenty workers merging at once means twenty concurrent `INSERT OR REPLACE` calls into `sessions`. What actually saves it is volume, not sequencing — it's two writes per session, each tiny, and SQLite handles a burst of small serialized writes fine. So the design works; the reasoning I wrote down for why it works was sloppy.

**Q30. Show me the SQLite failure mode.**

> `get_db()` opens `sqlite3.connect("nftrace.db")` with no `timeout` argument, so the default busy timeout is five seconds; and there's no `PRAGMA journal_mode=WAL`, so it's in rollback-journal mode, where a writer blocks readers as well as writers. Under a burst of concurrent merges, a worker can hit `database is locked` and get a 500 — *after* the pcap merge has already completed and the file is sitting on disk. The trace succeeded; the API call failed. Turning on WAL and setting an explicit busy timeout are two lines and I'd do both.

**Q31. Anything in that schema you'd change?**

> `validation_results` — the table with `result_id`, `session_id`, `protocol`, `rule_id`, `passed`, `detail` — is created by `init_db()` and, as far as the code I have shows, never written to. The validation report gets JSON-blobbed into `sessions.validation_report` instead. So the one table that would let you answer the useful question — "which rule fails most across all scenarios?" — is dead. I'd either write to it or drop it, because a table that exists and is always empty is a trap for whoever inherits this.

**Q32. Why aren't the pcap files in the database?**

> A 5-node trace capturing two minutes of 5G signalling is 50–200MB. SQLite can hold BLOBs, but that would bloat the database file and slow down every query against it. Files go on the filesystem at `/tmp/{session_id}_merged.pcap`; SQLite stores only the path. The obvious extension is to point that path at a network share or object store.

**Q33. `/tmp`. Who cleans it up?**

> Nobody, in the code I have. Every merge writes one file per node plus one merged file into `/tmp` and nothing ever deletes them. On a long-running lab server that's an unbounded disk leak, and at 50–200MB per merged trace it's not a slow one. Session IDs are UUIDs so there's no collision, but there's no reaper either. `[FILL: was there a cron job / tmpfiles.d rule cleaning /tmp on that box? If yes, say so — if not, own it.]`

---

## SECTION 6 — THE METRIC

**Q34. Fifty percent reduction in pipeline validation time. How did you measure that?**

> **This is the question to prepare hardest.** The source asserts the number three times and never defines it. Do not bluff it. Prepare exactly one of these:
>
> **(a) If you have real numbers:** `[FILL: what was the before baseline — hours per scenario, measured how? What was the after? Over how many scenarios? Wall-clock pipeline stage duration from NCD job logs, or engineer-hours?]`
>
> **(b) If you don't:** "It's the number the team reported and it's a wall-clock comparison of the validation stage, not an instrumented benchmark. What I can defend concretely is *why* it dropped: the manual path was start capture on each node by hand, wait, stop by hand, pull the files off each node one at a time, run dissection locally, and read SIP and Diameter by eye. The automated path is four HTTP calls with the node fan-out running in parallel. The saving is mostly the serial human steps disappearing, plus the parallel start/stop. If you want a defensible number, I'd want to point you at the NCD job durations before and after, and I don't have those in front of me."
>
> Answer (b) is a strong answer. Answer (b) delivered confidently beats a made-up methodology every time — and a systems interviewer *will* pull on a made-up methodology.

**Q35. Is "50% faster" even the interesting metric here?**

> Honestly, no — and I'd rather be judged on the other one. The thing NFTRACE does that nothing else did is catch a test that **passes its assertions and still has broken signalling underneath**. The NCD hook flags exactly that case: `report["failed"] > 0 and test_status == "PASS"`. Speed made the pipeline cheaper. That check made it *tell the truth*. `[FILL: how many such "passed-but-signalling-broken" defects did this actually catch? Even one concrete example is worth more than the 50% number.]`

---

## SECTION 7 — FAILURE MODES

**Q36. A node is unreachable when you start a trace.**

> Here I have to correct my own documentation. The design doc says NodeManager wraps each XML-RPC call in a try/except, starts the session with a partial node list, records which nodes failed, and puts a caveat in the validation report — "Trace for gNB-002 unavailable, results may be incomplete." The *code* I can show you does none of that: `_start_single_node` calls `proxy.trace.start(...)` bare, inside a `Pool.starmap`, with no exception handling. An unreachable node raises inside a pool worker, `starmap` re-raises it in the parent, and `/sessions/start` 500s — after Redis already holds a session in state `STARTING` and after some other nodes may already be capturing. So the failure isn't partial-degradation, it's a half-started session that's now orphaned until the TTL kills it. The documented behaviour is the behaviour I *wanted*; the shipped behaviour is fail-fast-and-leak. `[FILL: confirm which of these two is true of the real code you wrote — the deep-dive contradicts itself here and you need to know which side you're on before the interview.]`

**Q37. A node crashes mid-trace, after start, before stop.**

> `stop` fans out to every node in the session's node list, including the dead one. The XML-RPC call to it fails, and with no try/except that exception propagates — so a single dead node means `/sessions/stop` fails, and the *healthy* nodes never get their stop either, depending on where in the pool the failure lands. That's the worst shape of failure: one dead node poisons the shutdown of the good ones. The fix is per-node isolation — every node's start/stop/collect wrapped individually, failures collected into a per-node status map on the session, and the session state reflecting "STOPPED with 4 of 5 nodes; gNB-002 unreachable."

**Q38. A worker starts a session and never stops it. Leak?**

> Two leaks, at different layers. The Redis key is handled — the 3600s TTL is precisely the garbage collector for this case, which is why there's no cleanup job. But the TTL only cleans up *my* record of the session. The **capture on the physical node keeps running**, because the only thing that stops it is `proxy.trace.stop(session_id)`, and the session_id needed to make that call just expired out of Redis. So the orphan cleanup is exactly backwards: it deletes the one piece of information required to clean up the real resource. The right shape is a reaper that scans for sessions past their deadline, calls stop on their nodes, *then* deletes the key.

**Q39. Merge on a partially-failed set — three of five nodes gave you a file. What's in the merged pcap?**

> `collect_and_merge` loops the nodes, pulls each file, appends the path, and hands the whole list to `mergecap -w`. There's no check that the file list matches the node list, and no `check=True` failure unless mergecap itself errors. So you get a merged pcap that is silently *incomplete* — it looks like a valid trace, pyshark parses it happily, the SIP or Diameter validation runs over it, and the report says PASS because the messages that would have failed the rule were on the node you never collected from. **That's the scariest bug in the system**, because the output is a green check mark on a lie. Missing data reads as passing data. Any fix has to make an incomplete merge loudly fail, not quietly succeed.

**Q40. What about clock skew between nodes? You're merging pcaps from different machines.**

> `mergecap` merges packets in timestamp order, so a merged multi-node pcap is only meaningful if the nodes' clocks agree. Any time-ordering rule — and my own example Diameter rule `DIA_001` is explicitly a timing rule, "Authentication-Information-Request must get an Answer within 2 seconds" — is measuring the skew as much as the network. `[FILL: were the testbed nodes NTP-synced? If yes, say so and the concern is closed. If you never checked, say that — it's a real hole in a timing-based validation and pretending otherwise is dangerous.]`

**Q41. What's your auth story on the REST API?**

> There isn't one. No API key, no token, no `Depends()` security dependency on any endpoint. Anyone on the lab network who can reach port 8000 can start, stop, merge or validate any session — and since `worker_id` is never checked, they can drive *someone else's* session. It was an internal tool on a closed test network, which is the reason, not the excuse. The minimum I'd add before it went anywhere else is a shared token and an ownership check on `session["worker_id"]`.

---

## SECTION 8 — CLIENT SDK, VALIDATION, INTEGRATION

**Q42. Why does the client SDK exist? Workers could just call the REST API.**

> To keep the session_id out of the test author's hands. `NFTraceClient` holds `self.session_id` internally — the Robot Framework keyword author writes `Start Trace  gNB-001  AMF-01` and `Stop And Validate  Diameter  DIA_001`, and never touches a UUID. That's the decoupling the resume bullet means: the test scenario expresses *what* to trace, and the validation rules express *what's correct*, and neither knows about the other.

**Q43. There's a bug in `run_full_trace`. Find it.**

> It's a generator, not a function. The body has a bare `yield` in the middle — the point where the caller runs the test scenario — and a `return self.validate(...)` in the `finally`. In a generator, that `return` sets `StopIteration.value`; it does not hand a report back to a caller doing `report = client.run_full_trace(...)`. And it isn't decorated with `@contextlib.contextmanager`, so you can't use it in a `with` block either. As written, calling it does nothing at all until you iterate it. It wants to be `@contextmanager` and to hand the report out through the context object, or to just not exist — every real caller in the source, including the NCD hook, drives start/stop/merge/validate explicitly anyway.

**Q44. There's another one. The report shape.**

> Yes — and this one is worse because it's in the integration path. `/sessions/validate` returns `{"session_id": ..., "state": "VALIDATED", "report": {...}}`, and the `report` is the thing with `total`, `passed`, `failed`, `pass_rate`, `failures`. But both consumers — the Robot Framework keyword and the NCD `post_test` hook — do `if report["failed"] > 0`, where `report` is the *whole response*. That's a `KeyError`, not a comparison. Either the endpoint should return the summary unwrapped, or the callers should read `response["report"]["failed"]`. `[FILL: confirm whether the real integration code unwrapped this correctly — if it did, the deep-dive's snippets are simplified and this is a doc bug, not a shipped bug. Know which.]`

**Q45. Walk me through the validation rule engine.**

> `ProtocolValidator` takes the merged pcap, a protocol, and a list of rule IDs. It opens a `pyshark.FileCapture` with a display filter — `sip` or `diameter` — iterates packets, and for each packet applies every rule in the list. Results go into a list, and `_summarise` reduces them to total, passed, failed, and a pass rate.

**Q46. That pass rate. Does it mean anything?**

> No, and I'd rather say so than be caught. The loop is `for packet in cap: for rule_id in self.rules:` — so `total` is packets × rules, not the number of *checks that matter*. A trace with 10,000 packets and 3 rules reports a denominator of 30,000, almost all of which are the default `{"passed": True}` returned by rules that didn't apply to that packet. So the pass rate is dominated by non-applicable checks and is guaranteed to look great. The number is structurally meaningless as a quality signal — the only field in that report anyone should read is `failures`, which is the actual list.

**Q47. Is the rule engine itself correct?**

> `SIP_001` is not. The rule is meant to be "every REGISTER must get a 200 OK", but the implementation matches a REGISTER and immediately returns `passed: False` with a comment saying it's a flag for a second pass — a second pass that isn't in the code I have. So as written, `SIP_001` fails on **every** REGISTER, unconditionally, whether or not a 200 OK followed. It's a placeholder that reads like a rule. And correlating a request to its response is exactly the thing this design makes hard: a per-packet rule function can't see the response, because it only ever gets one packet. A correct request/response rule needs a stateful pass over the whole capture with a transaction table keyed on Call-ID — for SIP — or session-id for Diameter, and that's a different engine, not a different rule.

**Q48. `pyshark.FileCapture` — anything about that worry you?**

> It's never closed. `FileCapture` spawns a `tshark` subprocess; without a `close()` or a `with` block, you leak a process per validate call. Over a long-running server that's a process-table leak. It should be `with pyshark.FileCapture(...) as cap:`.

**Q49. Real-time mode vs batch mode — what's actually different in the code?**

> `mode` is a string on `StartRequest`, defaulting to `"realtime"`, and it's stored in the Redis blob and in the SQLite `sessions` row. In the code I can show you, **nothing branches on it** — start, stop, merge and validate behave identically either way. Batch mode is a usage pattern, not a code path: the caller loops start over several scenarios, runs them all, then loops stop/merge/validate. So `mode` is metadata for the history table, not behaviour. `[FILL: did the real system branch on mode anywhere — a scheduler, a queue? If not, be upfront that it's a label.]`

**Q50. How does NCD know which nodes to trace?**

> From the Robot Framework test tags. `pre_test` only fires if `"trace"` is in the tags at all, then `_resolve_nodes_from_tags` looks for a tag shaped `nodes:gNB-001+AMF-01`, splits on `+`, and falls back to `["gNB-001", "AMF-01"]` if none is present. Protocol selection is even blunter: `post_test` does `"Diameter" if "auth" in test_name.lower() else "SIP"`. Rule selection is a substring match of the scenario name against a dict — `UE_Registration`, `Authentication`, `Handover` — defaulting to `["DIA_001"]`. It's convention-over-configuration, and it's fragile: rename a test and its validation rules silently change. That's the kind of thing that's fine with ten tests and a liability with two hundred.

**Q51. How did you test NFTRACE itself?**

> Three layers, per the design: unit tests per component — Redis session ops against a test Redis, SQLite CRUD, `NodeManager` against mock XML-RPC servers, `ProtocolValidator` against synthetic pcap fixtures with known contents. Integration tests with `httpx` driving the full FastAPI stack: start a session, assert the Redis state, simulate a node response, stop, merge, validate, assert the SQLite history. Then end-to-end runs against real nodes in the actual testbed, weekly, through the very NCD pipeline NFTRACE was integrated into. `[FILL: coverage number, or the count of tests, if you have it]`

**Q52. Did any of those tests catch the concurrency bugs you've been describing?**

> No — and that's the whole lesson. Every one of those tests drives a single session through a linear lifecycle. The lost update in Q12 requires two sessions overlapping in a specific interleaving; a single-session test can never produce it. That's what makes this class of bug so dangerous in test infrastructure specifically: the tool that's supposed to tell you the truth about the network has a failure mode that its own test suite is structurally incapable of seeing.

---

## SECTION 9 — CLOSING

**Q53. What would you change with more time?**

> Three from the design doc, and three I'd now put ahead of them. From the doc: async node operations to replace `multiprocessing.Pool`; streaming validation so a critical protocol violation aborts the test mid-run instead of being found in post-processing; and a dashboard so QA leads can see pass rates and error trends without going through the SDK.
>
> But I'd do these first: write the session to SQLite at **start**, not at merge, so an evicted Redis key is a recoverable cache miss instead of amnesia. Move the session from a Redis string to a Redis hash so concurrent writers can't clobber each other's fields. And make an incomplete merge fail loudly, because a merged pcap that's silently missing a node produces a green validation report on a lie — which in a *trust* tool is the one thing you can never ship.

**Q54. What's the one thing you'd tell someone building this again?**

> Durable state must be written at the moment of *commitment*, not at the moment of *completion*. I wrote the session to SQLite when it merged, because that's when I "had something worth saving." But the thing worth saving was the fact that traces were now running on five physical machines and somebody has to turn them off. The moment that became true was `start`. Everything that leaked in that system leaked out of that one gap.

**Q55. Would you build it the same way today?**

> The shape, yes: a REST facade over a legacy XML-RPC estate, with the ugly protocol confined to one class, is the right architecture — when the nodes eventually move to gRPC, only `NodeManager` changes and the SDK never notices. The state layer, no. I'd collapse it. Two stores with two lifetimes and no reconciliation path bought me a performance argument I never actually needed — the session write volume was tiny — and cost me an entire class of failure that my test suite couldn't see.

---

## CHEAT CARD — trigger → exact line to say

| They say | You say |
|---|---|
| "Race condition?" | "Yes. Every endpoint is a read-modify-write on a single Redis string with no CAS. `stop` racing `merge` can clobber `merged_file`. Fix is a Redis hash so the writers touch different fields." |
| "Session isolation?" | "It's namespacing, not authorization. `worker_id` is stored at start and never checked at stop. Anyone with the UUID can stop anyone's trace." |
| "SQLite can't do concurrent writes." | "Correct, and my own justification for it was sloppy. Writes are sequential per session, not across sessions. It survives on volume — two small writes per session — not on the reasoning I wrote down." |
| "Redis evicts the key." | "Then the worker can't stop its own trace, and the capture on the physical node runs forever. The TTL deletes the one thing needed to clean up the real resource. That's backwards, and it's my bug." |
| "Two sources of truth?" | "Worse — SQLite isn't written until merge, so before that there's only one, and it's volatile. Durable state was written too late." |
| "Why XML-RPC?" | "Constraint, not choice. The gNBs and third-party telecom servers only expose XML-RPC. The design decision was confining it to `NodeManager` so the REST API and SDK never see it." |
| "How distributed is it really?" | "The workload is distributed across nodes. The control plane is one box: one FastAPI process, one localhost Redis, one SQLite file. I'm not going to call that a distributed system in the CAP sense." |
| "Where's the 50% from?" | "It's a wall-clock comparison of the validation stage, not an instrumented benchmark. What I'll defend precisely is the mechanism: serial human steps removed, node fan-out parallelised." |
| "What's the best thing in it?" | "The NCD hook that fails a job when the test passes but the signalling is wrong. Speed made the pipeline cheaper; that check made it honest." |
| "Biggest mistake?" | "Writing durable state at merge instead of at start." |
| You're cornered and don't know | "I don't know — I'd have to go and check. What I *can* tell you is..." (then pivot to a mechanism you own) |

---

## PREP PRIORITY

**Tier 1 — cannot walk in without these (do not skip one):**
- Q11, Q12, Q13, Q14 — the lost-update race. Be able to narrate the interleaving out loud, unprompted, in under 60 seconds.
- Q22, Q23, Q24 — Redis eviction and the TTL leak.
- Q29, Q30 — SQLite writer lock, and the fact that your own written justification was weak.
- Q34 — the 50% number. Pick answer (a) or (b) and rehearse it verbatim.
- Q39 — silently incomplete merge. This is your scariest bug and volunteering it makes you look senior.

**Tier 2 — likely, and cheap to prepare:**
- Q5, Q8, Q9 (state machine + the `ACTIVE` hole), Q16 (node-side session scoping), Q18 (multiprocessing vs asyncio), Q36/Q37 (node failure), Q46/Q47 (the validation rules are weaker than they look), Q53/Q54 (what you'd change).

**Tier 3 — nice to have, only if there's time:**
- Q2, Q6, Q26, Q31, Q42, Q49, Q50, Q55.

**Do not volunteer Tier 3 unprompted.** Every minute you spend on FastAPI-vs-Flask is a minute not spent proving you understand your own concurrency model.

---

## [FILL] LIST — resolve all of these before the interview

1. **Q2** — Your exact scope. Which layers did you personally design and write vs. inherit? "Architected" sets a high bar.
2. **Q3** — How many engineers / teams / pipelines used NFTRACE, over what period.
3. **Q7** — Your real reason `merge` is a separate call from `stop`.
4. **Q11** — Is `proxy.trace.stop(session_id)` idempotent on the real nodes?
5. **Q16** — **Critical.** Is the node's XML-RPC trace interface genuinely session-scoped, or is `trace.start` a global toggle? Your entire isolation claim rests on this.
6. **Q23 / Q5 (attack table)** — Longest real test scenario runtime in the NCD pipeline. If it's well under an hour, the 3600s TTL is defensible.
7. **Q27** — Was Redis AOF/RDB persistence actually enabled? The design's "Redis survives restarts" claim is false without it.
8. **Q33** — Was anything cleaning `/tmp` on that server?
9. **Q34** — **Highest priority.** The 50% figure: what was measured, how, against what baseline, over how many scenarios?
10. **Q35** — At least one concrete example of a defect NFTRACE caught that the test assertions missed. Worth more than the 50%.
11. **Q36** — **Contradiction in your own source.** The prose says node failures are caught with try/except and degrade to a partial node list; the code shows no try/except at all. Find out which is true of the code you actually wrote.
12. **Q40** — Were the testbed nodes NTP-synced? `DIA_001` is a 2-second timing rule; without clock sync it's measuring skew.
13. **Q44** — Did the real NCD hook read `response["report"]["failed"]` correctly, or is the `report["failed"]` KeyError a shipped bug?
14. **Q49** — Did anything actually branch on `mode` (realtime vs batch), or is it just a label on the history row?
15. **Q51** — Test count or coverage figure, if you have one.

**A note on 11 and 13:** these are places where your own deep-dive document contradicts itself. An interviewer who reads carefully will not find them — but *you* will trip over them if you narrate from the prose and then get asked to show the code. Resolve them.
