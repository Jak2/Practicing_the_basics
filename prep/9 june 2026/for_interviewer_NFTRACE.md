# NFTRACE — Distributed Network Function Tracing Platform
## FastAPI · Redis · SQLite · XML-RPC · Pyshark · multiprocessing · Robot Framework

---

## Elevator Pitch (30 seconds)

> "I architected NFTRACE, a distributed REST-based tracing platform for 5G telecom test automation. Before it existed, validating network function behavior required engineers to manually start traces on distributed nodes, wait for test scenarios, collect and merge trace files, and run protocol validation — hours per test scenario. NFTRACE automated the entire lifecycle through a REST API: start/stop/merge/validate via four calls. I then single-handedly integrated it into Nokia's Continuous Delivery CI/CD pipeline, enabling automatic trace capture and protocol validation for every tagged test case. Result: 50% reduction in pipeline validation time."

---

## The Problem

In 5G test automation, validating behavior requires tracing messages between distributed nodes — gNBs, AMFs, UPFs, SMFs, AUSFs — across a CI/CD pipeline. The manual process:

1. Engineer manually starts trace capture on each network node
2. Waits for test scenario to complete
3. Manually stops capture
4. Collects trace files from each node individually
5. Runs post-processing filters and dissection scripts locally
6. Validates SIP/Diameter signaling behavior by hand

Hours per test scenario. Error-prone. Non-repeatable. Blocked CI/CD pipelines from running automated validations at scale.

---

## Architecture — Three Layers

```
Test Workers (N concurrent)
  Worker 1 (Session A)  |  Worker 2 (Session B)  |  Worker N (Session N)
         |                       |                         |
         └───────────────────────┴─────────────────────────┘
                                 ↓
                    FastAPI REST API :8000
                 /sessions/start  stop  merge  validate
                    /nodes   /health
                         ↓              ↓
                      Redis           SQLite
                  (active sessions)  (completed history,
                   TTL=1hr, sub-ms)   node registry)
                         ↓
                  XML-RPC Node Manager
                  (multiprocessing.Pool for parallel ops)
                         ↓
          gNB-001    AMF-01    UPF-01    SMF-01
          (network nodes — each exposes XML-RPC interface)
```

---

## Session Lifecycle

```
POST /sessions/start
  → Redis: store session_id → {worker_id, nodes, state: STARTING}
  → XML-RPC NodeManager: start_trace() in parallel on all nodes (multiprocessing.Pool)
  → Redis: state → ACTIVE

[Test scenario runs against live network]

POST /sessions/stop
  → XML-RPC: stop_trace() in parallel on all nodes
  → Redis: state → STOPPED

POST /sessions/merge
  → XML-RPC: collect trace files from each node
  → mergecap (Wireshark tool): merge into single pcap at /tmp/{session_id}_merged.pcap
  → Redis: state → MERGED | SQLite: persist session record

POST /sessions/validate
  → Pyshark: open merged pcap with display_filter="sip" or "diameter"
  → ProtocolValidator: apply validation rules (SIP_001, DIA_001, etc.)
  → Return: {total, passed, failed, pass_rate, failures[]}
```

---

## The Key Design Decisions

### 1. Two-layer persistence: Redis (hot) + SQLite (cold)

**Redis** — in-memory, sub-millisecond read/write, TTL-managed:
- Active session state that changes rapidly (STARTING→ACTIVE→STOPPING→STOPPED)
- Concurrent-safe: multiple workers reading/writing their own sessions never collide
- `setex(f"session:{session_id}", 3600, json.dumps(data))` — orphaned sessions (worker crashed) auto-expire
- Process-restart safe: Redis persists, in-memory dict doesn't

**SQLite** — on-disk, persistent, queried infrequently:
- Completed session history that must survive server restarts
- Node registry (hostname, type, port, state)
- Validation result audit trail

*Why not only Redis?* Session history disappears on Redis restart or eviction. *Why not only SQLite?* Under 20 concurrent workers, SQLite's write serialisation would bottleneck rapid state transitions during active traces.

### 2. Session isolation via UUID-keyed session IDs

Multiple workers run simultaneously on the same pool of network nodes. Without isolation, Worker 2's stop command could accidentally stop Worker 1's trace — corrupting ongoing test data. Each session is stored under `session:{uuid4()}`. Every operation requires the session ID. A worker can only affect its own session.

### 3. XML-RPC for node communication — and why it's an abstraction win

XML-RPC is a telecom industry standard — Nokia gNBs, Ericsson test servers, and third-party equipment expose it. Not a design choice; a constraint. The architectural win: NFTRACE's REST API completely shields test workers from XML-RPC. Workers call clean REST. NFTRACE translates internally. When the industry moves to gRPC or REST for node interfaces (happening slowly), only the NodeManager layer changes — the REST API and SDK remain unchanged.

### 4. multiprocessing.Pool for parallel node operations

Starting and stopping traces on N nodes must happen simultaneously — if you start sequentially, you miss the initial messages on nodes 2 and 3. `multiprocessing.Pool.starmap` gives true parallel execution across CPU cores. The alternative was asyncio, but `xmlrpc.client` is synchronous. Multiprocessing avoided adding an async XML-RPC dependency. For 5-10 nodes (typical testbed), overhead is negligible.

### 5. Why SQLite over PostgreSQL?

NFTRACE is deployed on a single server in the test lab with sequential write patterns (one session completes before the next writes) and low concurrent read access (engineers look at historical results one at a time). SQLite is zero-infrastructure — no server, no connection pooling, no credentials, no DBA. Adding PostgreSQL would be complexity with no benefit for this deployment profile. The decision documents exactly when to migrate: multi-server deployment, failover, or 100s of concurrent writes.

### 6. mergecap for trace merging (not custom code)

Merging pcap files from multiple nodes with correct timestamp ordering is non-trivial. `mergecap` (part of the Wireshark toolkit) does this correctly and is battle-tested in telecom environments. A `subprocess.run(["mergecap", "-w", output] + files)` is more reliable than a custom binary merge implementation.

---

## NCD CI/CD Integration — Why It Earned Recognition

Nokia Continuous Delivery (NCD) is Nokia's internal CI/CD platform. TAF (Test Automation Framework) runs Robot Framework test suites at scale.

**The integration problem:** TAF and NCD had no mechanism to trigger trace collection during test execution. Tests ran but there was no automatic way to start NFTRACE, collect traces, and feed validation results back into the pipeline report.

**What was built:** `pre_test()` and `post_test()` hooks in the NCD pipeline executor.

```python
def pre_test(self, test_name, test_tags):
    if "trace" not in test_tags: return
    nodes = self._resolve_nodes_from_tags(test_tags)
    session_id = self.client.start(nodes=nodes, scenario=test_name)
    self.active_sessions[test_name] = session_id

def post_test(self, test_name, test_status):
    self.client.stop() → merge() → validate()
    if report["failed"] > 0 and test_status == "PASS":
        ncd_reporter.flag_trace_failure(test_name, ...)  # test passed but network behavior was wrong
```

**Why this was recognized:** A test could pass execution (assertions pass) but fail trace validation — the network behavior was wrong even though the test passed. This caught a class of bugs previously invisible: latent protocol errors that would cause failures under load or in edge cases. No manual intervention needed — every tagged test automatically captures traces, validates protocol behavior, and reports back to the pipeline.

---

## Protocol Validation — SIP and Diameter

**SIP (Session Initiation Protocol):** Used in 5G IMS for voice/video/messaging setup.

**Diameter:** Authentication and authorization protocol. Carries Authentication-Information-Request/Answer between UE, gNB, AMF, and AUSF during 5G-AKA registration.

Validating these means checking: correct messages appear, in the correct order, with correct parameters. A test can pass at the application level (UE successfully registered) while Diameter signaling underneath had timing violations or missing messages — indicating a latent defect invisible without trace validation.

---

## Results

- **50%** reduction in pipeline validation time across CI/CD workflows
- Hundreds of engineering hours saved annually
- Integrated into Nokia Continuous Delivery (NCD) pipeline — recognized by onsite team
- Caught a class of bugs previously invisible: tests passing while network behavior was wrong

---

## Anticipated Interview Questions

**Q: Why did you use Redis when you already had SQLite?**
> They serve different access patterns. Redis is in-memory and sub-millisecond — right for active session state that transitions 4-5 times during a trace and needs to be read under concurrent access from N workers. SQLite is persistent on disk — right for completed session history that needs to survive server restarts but is read infrequently. Using SQLite for active state under 20 concurrent workers would create write serialisation bottlenecks. Using only Redis means history disappears on eviction or restart. Two-layer persistence gives the right tool for each pattern.

**Q: How does session isolation work with multiple concurrent workers?**
> Each session gets a UUID at creation, stored as the Redis key `session:{uuid4()}`. Every subsequent operation — stop, merge, validate — must include this session ID. Workers can only affect their own sessions because they only know their own session ID. The UUID space makes collisions practically impossible. TTL on the Redis key means a worker that crashes doesn't leave orphaned sessions that block node resources indefinitely.

**Q: What are SIP and Diameter? Why validate them in a test pipeline?**
> SIP is used in 5G IMS for multimedia session setup — voice calls, video, messaging. Diameter is the authentication protocol that carries the credentials exchange between the UE, the AMF, and the authentication server during registration. Validating them means checking that the correct protocol messages appeared in the right order with correct parameters. A test can pass (UE registered successfully) while the underlying Diameter exchange had timing violations or missing messages — latent defects that cause failures under load but are invisible without trace-level validation.

**Q: Why multiprocessing over asyncio for node operations?**
> Starting traces on N nodes must happen simultaneously — sequential start means you miss the initial messages on nodes 2 and 3. `asyncio` would require an async-compatible XML-RPC library, which adds a dependency. `multiprocessing.Pool.starmap` gives true parallel execution using the standard `xmlrpc.client` library. For 5-10 nodes in a typical testbed, multiprocessing overhead is negligible. At 50+ nodes, switching to asyncio + async XML-RPC would be the right migration.

**Q: What would you change with more time?**
> Three things. First, async node operations — replace multiprocessing with asyncio + async XML-RPC to reduce resource overhead and improve scalability past 10 concurrent sessions. Second, streaming trace validation — currently validation runs post-session. Real-time streaming could abort the test immediately on a critical protocol violation. Third, a web dashboard showing session history, pass/fail rates per scenario, and protocol error trends — useful for QA leads and managers, not just test engineers.
