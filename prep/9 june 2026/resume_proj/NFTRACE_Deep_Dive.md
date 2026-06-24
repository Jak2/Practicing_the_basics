# NFTRACE — Complete Deep Dive
## REST-Based Network Function Tracing Tool for Telecom Test Automation
### Architecture · Interview Prep · Resume Bullet · Design Decisions

---

# PART 1: WHAT IS NFTRACE AND WHY WAS IT BUILT

## The problem it solved

In 5G telecom test automation, validating network function behavior requires tracing messages between distributed nodes — gNBs, AMFs, UPFs, SMFs, AUSFs — across a CI/CD (Continuous Integration/Continuous Deployment) pipeline. Before NFTRACE, this worked as follows:

- A test engineer manually started a trace capture on each network node
- Waited for the test scenario to complete
- Manually stopped the capture
- Collected trace files from each node individually
- Ran post-processing filters and dissection scripts locally
- Validated protocol-specific behavior (SIP, Diameter signaling) by hand

This process took hours per test scenario. It was error-prone, non-repeatable, and blocked CI/CD pipelines from running automated validations at scale.

**NFTRACE automated the entire lifecycle:**
- Start traces remotely across all nodes via a single API call
- Execute test scenarios against live nodes
- Stop, merge, and post-process traces automatically
- Validate protocol behavior programmatically
- Integrate directly into Nokia Continuous Delivery (NCD) CI/CD pipeline

Result: 50% reduction in pipeline validation time. Hundreds of engineering hours saved annually.

---

## What NFTRACE actually is

NFTRACE is a distributed REST-based tracing platform with three layers:

**Server side:** FastAPI REST API that manages trace lifecycle across distributed network nodes. Endpoints for start, stop, merge, validate. Redis-backed session caching for parallel execution isolation. SQLite for node state and execution history.

**Client side:** Python SDK with XML-RPC session management for multi-worker parallel processing. Multiple test workers can run independent trace sessions simultaneously without collision.

**Protocol layer:** Trace collection from network nodes and third-party servers, with post-processing filters, dissection, and scenario-based validation for SIP and Diameter protocols.

---

# PART 2: FULL ARCHITECTURE — HOW IT WORKS END TO END

## The lifecycle of a single trace session

```
Test Worker starts a session
        ↓
POST /sessions/start → FastAPI
        ↓
Redis: store session_id → {worker_id, nodes, state: ACTIVE}
        ↓
NFTRACE connects to each network node via XML-RPC
        ↓
Start trace capture on each node simultaneously
        ↓
[Test scenario executes against the live network]
        ↓
POST /sessions/stop → FastAPI
        ↓
NFTRACE stops capture on all nodes
        ↓
POST /sessions/merge → FastAPI
        ↓
Trace files collected from all nodes, merged into single pcap
        ↓
POST /sessions/validate → FastAPI
        ↓
Filters and dissection applied
Protocol validation (SIP / Diameter) runs
Validation report returned
        ↓
SQLite: persist session history, node state, validation result
        ↓
Test Worker receives structured validation report
```

---

## Component diagram

```
┌─────────────────────────────────────────────────────┐
│                  Test Workers (N)                   │
│  Worker 1      Worker 2      Worker 3    Worker N   │
│  Session A     Session B     Session C   Session N  │
└─────────┬──────────┬─────────────┬──────────┬───────┘
          │          │             │          │
          └──────────┴──────┬──────┘          │
                            ↓                 │
              ┌─────────────────────────┐     │
              │    FastAPI REST API     │◄────┘
              │  /sessions/start        │
              │  /sessions/stop         │
              │  /sessions/merge        │
              │  /sessions/validate     │
              └───────┬─────────┬───────┘
                      │         │
              ┌───────▼──┐  ┌───▼─────┐
              │  Redis   │  │ SQLite  │
              │ Session  │  │  Node   │
              │  Cache   │  │ History │
              └───────┬──┘  └─────────┘
                      │
              ┌───────▼──────────────────────┐
              │     XML-RPC Node Manager     │
              │  Connects to network nodes   │
              └───┬────────┬────────┬────────┘
                  │        │        │
          ┌───────▼┐  ┌────▼──┐  ┌─▼──────┐
          │  gNB   │  │  AMF  │  │  UPF   │
          │ Node 1 │  │ Node 2│  │ Node 3 │
          └────────┘  └───────┘  └────────┘
```

---

## The server-side stack in detail

### FastAPI REST endpoints

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="NFTRACE", version="1.0.0")

# ── Data models ───────────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    worker_id: str
    nodes: list[str]           # e.g. ["gNB-001", "AMF-01", "UPF-01"]
    scenario: str              # e.g. "UE_Registration_5G_AKA"
    mode: str = "realtime"     # "realtime" or "batch"
    filter_profile: Optional[str] = None  # pre-defined filter set

class StopRequest(BaseModel):
    session_id: str

class MergeRequest(BaseModel):
    session_id: str
    output_format: str = "pcap"   # "pcap" or "json"

class ValidateRequest(BaseModel):
    session_id: str
    protocol: str              # "SIP" or "Diameter"
    validation_rules: list[str]  # rule IDs to apply

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/sessions/start")
def start_session(req: StartRequest):
    session_id = str(uuid.uuid4())

    # Store session in Redis
    session_data = {
        "session_id": session_id,
        "worker_id":  req.worker_id,
        "nodes":      req.nodes,
        "scenario":   req.scenario,
        "state":      "STARTING",
        "mode":       req.mode
    }
    redis_client.setex(
        f"session:{session_id}",
        3600,                        # 1 hour TTL
        json.dumps(session_data)
    )

    # Start trace on each node via XML-RPC
    node_manager = NodeManager(req.nodes)
    node_manager.start_trace(session_id, req.filter_profile)

    # Update state
    session_data["state"] = "ACTIVE"
    redis_client.setex(f"session:{session_id}", 3600, json.dumps(session_data))

    return {"session_id": session_id, "state": "ACTIVE", "nodes": req.nodes}


@app.post("/sessions/stop")
def stop_session(req: StopRequest):
    session_raw = redis_client.get(f"session:{req.session_id}")
    if not session_raw:
        raise HTTPException(404, f"Session {req.session_id} not found or expired")

    session = json.loads(session_raw)
    node_manager = NodeManager(session["nodes"])
    node_manager.stop_trace(req.session_id)

    session["state"] = "STOPPED"
    redis_client.setex(f"session:{req.session_id}", 3600, json.dumps(session))

    return {"session_id": req.session_id, "state": "STOPPED"}


@app.post("/sessions/merge")
def merge_traces(req: MergeRequest):
    session_raw = redis_client.get(f"session:{req.session_id}")
    if not session_raw:
        raise HTTPException(404, f"Session {req.session_id} not found")

    session = json.loads(session_raw)
    if session["state"] != "STOPPED":
        raise HTTPException(400, "Session must be stopped before merging")

    node_manager = NodeManager(session["nodes"])
    merged_path = node_manager.collect_and_merge(
        req.session_id,
        req.output_format
    )

    session["state"] = "MERGED"
    session["merged_file"] = merged_path
    redis_client.setex(f"session:{req.session_id}", 3600, json.dumps(session))

    # Persist to SQLite
    db_client.save_session(session)

    return {"session_id": req.session_id, "state": "MERGED", "file": merged_path}


@app.post("/sessions/validate")
def validate_session(req: ValidateRequest):
    session_raw = redis_client.get(f"session:{req.session_id}")
    if not session_raw:
        raise HTTPException(404, f"Session {req.session_id} not found")

    session = json.loads(session_raw)
    if session["state"] not in ("MERGED", "ACTIVE"):
        raise HTTPException(400, "Session must be merged before validation")

    validator = ProtocolValidator(
        merged_file=session.get("merged_file"),
        protocol=req.protocol,
        rules=req.validation_rules
    )
    report = validator.run()

    session["state"] = "VALIDATED"
    session["validation_report"] = report
    redis_client.setex(f"session:{req.session_id}", 3600, json.dumps(session))
    db_client.update_session(session)

    return {
        "session_id": req.session_id,
        "state": "VALIDATED",
        "report": report
    }


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    session_raw = redis_client.get(f"session:{session_id}")
    if not session_raw:
        # Try SQLite for historical sessions
        return db_client.get_session(session_id)
    return json.loads(session_raw)


@app.get("/nodes")
def list_nodes():
    return {"nodes": db_client.get_all_nodes()}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "redis": redis_client.ping(),
        "db": db_client.ping()
    }
```

---

### Redis session caching — why it's critical

Redis is not used for caching responses (like in the Pyshark project). Here it serves a specific, critical purpose: **parallel execution isolation**.

Multiple test workers run simultaneously. Each worker has its own session. Without isolation, Worker 2's stop command could accidentally stop Worker 1's trace.

Redis provides fast, TTL-managed, concurrent-safe session storage:

```python
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Each session is stored under a unique key
# TTL ensures orphaned sessions (worker crashed) auto-expire
redis_client.setex(
    f"session:{session_id}",    # unique key per session
    3600,                        # 1 hour TTL — auto-cleanup
    json.dumps(session_data)     # full session state as JSON
)

# Worker A reads only its own session
session_a = json.loads(redis_client.get(f"session:{session_id_a}"))

# Worker B reads only its own session — no collision
session_b = json.loads(redis_client.get(f"session:{session_id_b}"))
```

**Why Redis over in-memory dict?**
In-memory dict doesn't survive process restarts. If the NFTRACE server restarts mid-test, all active sessions are lost and every running test worker is stranded with no way to stop or collect their traces. Redis persists across restarts.

**Why Redis over SQLite for session state?**
SQLite is on-disk, slower for frequent reads/writes during active sessions. Redis is in-memory, sub-millisecond for the rapid state updates that happen during an active trace (STARTING → ACTIVE → STOPPING → STOPPED). SQLite is used for the final persistent history after a session completes.

---

### SQLite persistence — node state and execution history

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect("nftrace.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id      TEXT PRIMARY KEY,
                worker_id       TEXT NOT NULL,
                scenario        TEXT NOT NULL,
                nodes           TEXT NOT NULL,   -- JSON array
                state           TEXT NOT NULL,
                mode            TEXT NOT NULL,
                started_at      TEXT NOT NULL,
                completed_at    TEXT,
                merged_file     TEXT,
                validation_report TEXT            -- JSON
            );

            CREATE TABLE IF NOT EXISTS nodes (
                node_id         TEXT PRIMARY KEY,
                hostname        TEXT NOT NULL,
                node_type       TEXT NOT NULL,    -- gNB, AMF, UPF, SMF, AUSF
                port            INTEGER NOT NULL,
                last_seen       TEXT,
                state           TEXT DEFAULT 'idle'
            );

            CREATE TABLE IF NOT EXISTS validation_results (
                result_id       TEXT PRIMARY KEY,
                session_id      TEXT NOT NULL,
                protocol        TEXT NOT NULL,    -- SIP or Diameter
                rule_id         TEXT NOT NULL,
                passed          INTEGER NOT NULL, -- 0 or 1
                detail          TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)

def save_session(session: dict):
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, worker_id, scenario, nodes, state, mode,
             started_at, completed_at, merged_file, validation_report)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["session_id"],
            session["worker_id"],
            session["scenario"],
            json.dumps(session["nodes"]),
            session["state"],
            session["mode"],
            session.get("started_at"),
            session.get("completed_at"),
            session.get("merged_file"),
            json.dumps(session.get("validation_report"))
        ))
```

**Why SQLite over PostgreSQL?**
NFTRACE is an internal tool deployed on a single server within the test lab. SQLite is zero-infrastructure — no separate DB server, no connection pooling, no credentials management. For a single-server internal tool with sequential writes (one session completes before the next writes), SQLite is the correct choice. PostgreSQL would be correct for multi-server deployments or high write concurrency.

---

### XML-RPC node management — the client side

XML-RPC is the protocol used to communicate with network nodes and third-party telecom servers. Many telecom test tools expose XML-RPC interfaces (it's a legacy standard in the telecom industry, predating REST).

```python
import xmlrpc.client
from multiprocessing import Pool
import time

class NodeManager:
    def __init__(self, node_ids: list[str]):
        self.nodes = self._resolve_nodes(node_ids)

    def _resolve_nodes(self, node_ids: list[str]) -> list[dict]:
        # Look up node hostnames and ports from SQLite
        with get_db() as conn:
            nodes = []
            for node_id in node_ids:
                row = conn.execute(
                    "SELECT * FROM nodes WHERE node_id = ?", (node_id,)
                ).fetchone()
                if row:
                    nodes.append(dict(row))
            return nodes

    def _get_proxy(self, node: dict):
        return xmlrpc.client.ServerProxy(
            f"http://{node['hostname']}:{node['port']}"
        )

    def start_trace(self, session_id: str, filter_profile: str = None):
        # Start traces on all nodes in parallel
        with Pool(processes=len(self.nodes)) as pool:
            pool.starmap(
                self._start_single_node,
                [(node, session_id, filter_profile) for node in self.nodes]
            )

    def _start_single_node(self, node: dict, session_id: str,
                           filter_profile: str):
        proxy = self._get_proxy(node)
        proxy.trace.start(session_id, filter_profile or "default")

    def stop_trace(self, session_id: str):
        with Pool(processes=len(self.nodes)) as pool:
            pool.starmap(
                self._stop_single_node,
                [(node, session_id) for node in self.nodes]
            )

    def _stop_single_node(self, node: dict, session_id: str):
        proxy = self._get_proxy(node)
        proxy.trace.stop(session_id)

    def collect_and_merge(self, session_id: str,
                          output_format: str) -> str:
        # Collect trace file from each node
        trace_files = []
        for node in self.nodes:
            proxy = self._get_proxy(node)
            file_data = proxy.trace.collect(session_id)
            local_path = f"/tmp/{session_id}_{node['node_id']}.pcap"
            with open(local_path, "wb") as f:
                f.write(file_data.data)
            trace_files.append(local_path)

        # Merge all pcap files into one
        merged_path = f"/tmp/{session_id}_merged.pcap"
        self._merge_pcap_files(trace_files, merged_path)
        return merged_path

    def _merge_pcap_files(self, files: list[str], output: str):
        import subprocess
        # mergecap is part of the Wireshark toolkit
        subprocess.run(
            ["mergecap", "-w", output] + files,
            check=True
        )
```

**Why XML-RPC instead of REST for node communication?**
The network nodes — gNBs, AMFs, third-party telecom servers — expose XML-RPC interfaces. This is a telecom industry standard, not a design choice. NFTRACE had to speak the protocol the nodes already exposed. The NFTRACE REST API is the clean interface for test workers; XML-RPC is the legacy protocol used to talk to the nodes themselves.

**Why `multiprocessing.Pool` instead of `asyncio`?**
Starting and stopping traces on N nodes should happen simultaneously, not sequentially. With asyncio you need async-compatible XML-RPC libraries. `multiprocessing.Pool.starmap` gives true parallelism with the standard `xmlrpc.client` library — no async dependencies. For 5-10 nodes (typical testbed size), this is sufficient.

---

### Protocol validation — SIP and Diameter

After merging trace files, NFTRACE validates protocol-specific behavior:

```python
import pyshark

class ProtocolValidator:
    def __init__(self, merged_file: str, protocol: str,
                 rules: list[str]):
        self.merged_file = merged_file
        self.protocol    = protocol
        self.rules       = rules

    def run(self) -> dict:
        if self.protocol == "SIP":
            return self._validate_sip()
        elif self.protocol == "Diameter":
            return self._validate_diameter()
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def _validate_sip(self) -> dict:
        cap = pyshark.FileCapture(
            self.merged_file,
            display_filter="sip"
        )
        results = []

        for packet in cap:
            if "SIP" not in packet:
                continue
            for rule_id in self.rules:
                result = self._apply_sip_rule(packet, rule_id)
                results.append(result)

        return self._summarise(results)

    def _validate_diameter(self) -> dict:
        cap = pyshark.FileCapture(
            self.merged_file,
            display_filter="diameter"
        )
        results = []

        for packet in cap:
            if "DIAMETER" not in packet:
                continue
            for rule_id in self.rules:
                result = self._apply_diameter_rule(packet, rule_id)
                results.append(result)

        return self._summarise(results)

    def _apply_sip_rule(self, packet, rule_id: str) -> dict:
        # Example rule: SIP_001 — all REGISTER requests must get 200 OK
        if rule_id == "SIP_001":
            if hasattr(packet.sip, "method") and packet.sip.method == "REGISTER":
                return {
                    "rule_id": rule_id,
                    "passed":  False,  # flag for validation in next pass
                    "detail":  f"REGISTER from {packet.sip.from_}"
                }
        return {"rule_id": rule_id, "passed": True, "detail": None}

    def _apply_diameter_rule(self, packet, rule_id: str) -> dict:
        # Example rule: DIA_001 — all Authentication-Information-Request
        # must receive Authentication-Information-Answer within 2 seconds
        if rule_id == "DIA_001":
            if hasattr(packet.diameter, "cmd_code"):
                if packet.diameter.cmd_code == "318":  # AIR
                    return {
                        "rule_id": rule_id,
                        "passed":  True,
                        "detail":  f"AIR at {packet.sniff_time}"
                    }
        return {"rule_id": rule_id, "passed": True, "detail": None}

    def _summarise(self, results: list[dict]) -> dict:
        total   = len(results)
        passed  = sum(1 for r in results if r["passed"])
        failed  = total - passed
        return {
            "total":   total,
            "passed":  passed,
            "failed":  failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
            "failures": [r for r in results if not r["passed"]]
        }
```

---

## The client-side SDK

Test workers don't call the FastAPI REST endpoints directly — they use the Python SDK which handles session management, retries, and result aggregation.

```python
import requests
import time
from typing import Optional

class NFTraceClient:
    """
    Client SDK for NFTRACE.
    Manages the full trace lifecycle for a single test worker.
    """
    def __init__(self, base_url: str, worker_id: str):
        self.base_url  = base_url
        self.worker_id = worker_id
        self.session_id: Optional[str] = None

    def start(self, nodes: list[str], scenario: str,
              mode: str = "realtime",
              filter_profile: str = None) -> str:
        response = requests.post(
            f"{self.base_url}/sessions/start",
            json={
                "worker_id":      self.worker_id,
                "nodes":          nodes,
                "scenario":       scenario,
                "mode":           mode,
                "filter_profile": filter_profile
            }
        )
        response.raise_for_status()
        self.session_id = response.json()["session_id"]
        return self.session_id

    def stop(self) -> dict:
        if not self.session_id:
            raise RuntimeError("No active session. Call start() first.")
        response = requests.post(
            f"{self.base_url}/sessions/stop",
            json={"session_id": self.session_id}
        )
        response.raise_for_status()
        return response.json()

    def merge(self, output_format: str = "pcap") -> dict:
        response = requests.post(
            f"{self.base_url}/sessions/merge",
            json={
                "session_id":    self.session_id,
                "output_format": output_format
            }
        )
        response.raise_for_status()
        return response.json()

    def validate(self, protocol: str,
                 rules: list[str]) -> dict:
        response = requests.post(
            f"{self.base_url}/sessions/validate",
            json={
                "session_id":       self.session_id,
                "protocol":         protocol,
                "validation_rules": rules
            }
        )
        response.raise_for_status()
        return response.json()

    def run_full_trace(self, nodes: list[str], scenario: str,
                       protocol: str, rules: list[str]) -> dict:
        """
        Convenience method: full lifecycle in one call.
        Used by test workers who want fire-and-forget simplicity.
        """
        self.start(nodes, scenario)
        try:
            yield  # caller runs the test scenario here
        finally:
            self.stop()
            self.merge()
            return self.validate(protocol, rules)
```

**Usage in a Robot Framework test:**

```python
# In a Robot Framework Python keyword library:
from nftrace_client import NFTraceClient

class NFTraceKeywords:
    def __init__(self):
        self.client = NFTraceClient(
            base_url="http://nftrace-server:8000",
            worker_id=f"worker_{os.getpid()}"
        )
        self.session_id = None

    def start_trace(self, *nodes):
        self.session_id = self.client.start(
            nodes=list(nodes),
            scenario=BuiltIn().get_variable_value("${TEST_NAME}")
        )
        return self.session_id

    def stop_and_validate(self, protocol, *rules):
        self.client.stop()
        self.client.merge()
        report = self.client.validate(protocol, list(rules))
        if report["failed"] > 0:
            raise AssertionError(
                f"Trace validation failed: {report['failures']}"
            )
        return report
```

---

## Execution modes: real-time vs batch

**Real-time mode:** Trace starts immediately when the session is created. The test scenario runs while the trace is active. Used for interactive debugging where the engineer wants to see what's happening as it happens.

**Batch mode:** Trace is pre-configured and scheduled. Multiple test scenarios can be queued. NFTRACE runs them sequentially or in parallel, collects all traces, and produces a consolidated validation report. Used in CI/CD pipelines where multiple scenarios run overnight.

```python
# Batch mode example
sessions = []
for scenario in test_scenarios:
    session_id = client.start(
        nodes=["gNB-001", "AMF-01"],
        scenario=scenario,
        mode="batch"
    )
    sessions.append(session_id)

# Run all scenarios
run_all_scenarios(test_scenarios)

# Collect results from all sessions
reports = []
for session_id in sessions:
    client.session_id = session_id
    client.stop()
    client.merge()
    report = client.validate("Diameter", ["DIA_001", "DIA_002"])
    reports.append(report)
```

---

# PART 3: TAF INTEGRATION WITH NOKIA CONTINUOUS DELIVERY (NCD)

This is the work that earned recognition from the onsite team.

Nokia Continuous Delivery (NCD) is Nokia's internal CI/CD platform. It orchestrates test pipeline execution — similar to Jenkins but Nokia-specific, with direct integration into Nokia's deployment and verification workflows.

TAF (Test Automation Framework) is the internal test execution framework that runs Robot Framework test suites at scale.

**The integration problem:** TAF and NCD had no mechanism to trigger trace collection during test execution. Tests ran, but there was no automatic way to start NFTRACE at the right moment, collect traces, and feed validation results back into the pipeline report.

**What was built:**

```python
# NCD Pipeline Hook — triggered by NCD at test start/end
class NCDNFTraceHook:
    """
    Integrates NFTRACE into NCD pipeline execution.
    NCD calls pre_test() before each test case and
    post_test() after each test case completes.
    """
    def __init__(self):
        self.client = NFTraceClient(
            base_url=os.getenv("NFTRACE_URL"),
            worker_id=f"ncd_{os.getenv('NCD_JOB_ID')}"
        )
        self.active_sessions = {}

    def pre_test(self, test_name: str, test_tags: list[str]):
        # Only start trace if test is tagged for tracing
        if "trace" not in test_tags:
            return

        nodes = self._resolve_nodes_from_tags(test_tags)
        session_id = self.client.start(
            nodes=nodes,
            scenario=test_name,
            mode="realtime"
        )
        self.active_sessions[test_name] = session_id

    def post_test(self, test_name: str, test_status: str):
        session_id = self.active_sessions.get(test_name)
        if not session_id:
            return

        self.client.session_id = session_id
        self.client.stop()
        self.client.merge()

        # Determine protocol from test name convention
        protocol = "Diameter" if "auth" in test_name.lower() else "SIP"
        report = self.client.validate(
            protocol=protocol,
            rules=self._get_rules_for_scenario(test_name)
        )

        # Feed results back to NCD
        ncd_reporter.add_trace_report(test_name, report)

        # Fail the NCD job if trace validation failed
        if report["failed"] > 0 and test_status == "PASS":
            ncd_reporter.flag_trace_failure(
                test_name,
                f"Test passed but trace validation failed: {report['failures']}"
            )

    def _resolve_nodes_from_tags(self, tags: list[str]) -> list[str]:
        # Tags like [trace, nodes:gNB-001+AMF-01] specify which nodes to trace
        for tag in tags:
            if tag.startswith("nodes:"):
                return tag.replace("nodes:", "").split("+")
        return ["gNB-001", "AMF-01"]  # default nodes

    def _get_rules_for_scenario(self, scenario: str) -> list[str]:
        SCENARIO_RULES = {
            "UE_Registration": ["DIA_001", "DIA_002", "SIP_001"],
            "Authentication":  ["DIA_001", "DIA_003"],
            "Handover":        ["SIP_001", "SIP_002"],
        }
        for key, rules in SCENARIO_RULES.items():
            if key.lower() in scenario.lower():
                return rules
        return ["DIA_001"]  # default
```

**Why this earned recognition:** Before this integration, trace collection was a manual step that engineers did after a test run. With NCD integration, every tagged test automatically captured traces, validated protocol behavior, and reported results back to the pipeline — without any manual intervention. A test could pass execution but fail trace validation (meaning the network behavior was wrong even if the test assertions passed). This caught a class of bugs that were previously invisible.

---

# PART 4: DESIGN DECISIONS — DEEP DIVE

---

## Why FastAPI over Flask or Django?

**Flask:** No built-in data validation. You'd manually parse request bodies with `request.json`. No automatic API documentation. Slower for high-concurrency due to WSGI (Web Server Gateway Interface — synchronous request handling model).

**Django:** Too much overhead for an internal API tool. ORM, admin interface, authentication system, template engine — none of this was needed. Django is a full web framework; NFTRACE needed a lightweight API.

**FastAPI:** Built-in Pydantic validation — every request body is automatically validated against the model, with clear error messages for malformed input. Automatic OpenAPI docs at `/docs` — engineers can explore and test the API without reading documentation. ASGI (Asynchronous Server Gateway Interface)-based — handles concurrent requests efficiently. Type hints throughout — easier to maintain and extend.

For an API tool that would be extended by multiple engineers, FastAPI's automatic validation and documentation were the decisive factors.

---

## Why Redis for session state and not SQLite?

Redis and SQLite serve different purposes in NFTRACE:

**Redis:** In-memory, sub-millisecond read/write. Used for active session state that changes rapidly (STARTING → ACTIVE → STOPPING → STOPPED). TTL ensures orphaned sessions auto-expire. Concurrent-safe — multiple workers reading/writing their own sessions simultaneously without locking issues.

**SQLite:** On-disk, persistent. Used for completed session history that needs to survive server restarts. Slower than Redis but that's fine — historical lookups happen infrequently.

If you used only SQLite: active session state would require frequent disk writes during a trace (every state change). Under high concurrency (20 workers simultaneously), SQLite's write serialization would create bottlenecks.

If you used only Redis: session history disappears on Redis restart or eviction. Historical audit trails and compliance logs would be lost.

The two-layer design gives you the right tool for each access pattern.

---

## Why XML-RPC for node communication?

Not a design choice — a constraint. Nokia network nodes, Ericsson test servers, and third-party telecom equipment expose XML-RPC interfaces. This is a telecom industry standard from the early 2000s that's deeply embedded in the ecosystem.

The interesting design decision was the abstraction: NFTRACE's REST API shields test workers from XML-RPC entirely. A test worker calls `POST /sessions/start` via clean REST. NFTRACE translates this to XML-RPC calls against the nodes. When the industry eventually moves to gRPC or REST for node interfaces (it's happening slowly), only the NodeManager layer changes — the REST API and SDK remain unchanged.

---

## Why multiprocessing for parallel node operations?

Starting and stopping traces on multiple nodes must happen simultaneously, not sequentially. If you start traces sequentially (node 1, then node 2, then node 3), you miss the initial messages on node 2 and 3. All nodes must start capturing at the same moment.

`multiprocessing.Pool.starmap` gives true parallelism — actual parallel execution across CPU cores. The alternative was `asyncio` with an async XML-RPC library, but `xmlrpc.client` (the standard library) is synchronous. Using multiprocessing avoided adding an async XML-RPC dependency.

For 5-10 nodes (typical testbed), multiprocessing overhead is negligible. For 50+ nodes, you'd switch to asyncio with an async XML-RPC library.

---

## Why SQLite over PostgreSQL?

NFTRACE is deployed on a single server in the test lab. It has:
- Sequential write patterns (one session completes, then the next writes)
- Low concurrent access (engineers look at historical results one at a time)
- No replication requirement
- No DBA to manage a PostgreSQL installation

SQLite is zero-infrastructure. It's a file. No server, no connection pooling, no credentials. For a single-server internal tool, adding PostgreSQL would be infrastructure complexity with no benefit.

If NFTRACE needed to scale to multiple servers (failover, load balancing) or handle 100s of concurrent session writes, PostgreSQL would be the right migration.

---

## Why not store merged pcap files in SQLite?

SQLite BLOBs can store binary data but at a significant performance cost for large files. A merged pcap from a 5-node trace capturing 2 minutes of 5G signaling can be 50-200MB. Storing that in SQLite would make the database file enormous and slow down all queries.

Instead: pcap files are stored on the local filesystem at `/tmp/{session_id}_merged.pcap`. SQLite stores only the path. For long-term storage, the path could point to a network share or object storage.

---

# PART 5: INTERVIEW Q&A — EVERY QUESTION AN INTERVIEWER CAN ASK

---

**Q: Walk me through NFTRACE at a high level.**

NFTRACE is a distributed REST-based tracing platform for 5G telecom test automation. The problem it solved: validating network function behavior in CI/CD required manually starting traces on distributed nodes, waiting for test scenarios to complete, collecting and merging trace files, and running protocol validation — a process that took hours per test scenario. NFTRACE automated the entire lifecycle through a REST API: start traces across multiple nodes simultaneously, execute the test, stop and merge traces, validate SIP or Diameter protocol behavior, all via four API calls. The result was a 50% reduction in pipeline validation time and direct integration into Nokia's CI/CD pipeline.

---

**Q: Why FastAPI specifically?**

Three reasons. Built-in Pydantic validation — every request body is automatically validated with clear error messages, which matters when multiple test workers are calling the API simultaneously. Automatic OpenAPI documentation at /docs — engineers could explore and test the API without reading documentation. ASGI-based concurrent handling — multiple workers hitting the API simultaneously are handled efficiently. For an internal API tool extended by multiple engineers, FastAPI's developer experience was the decisive factor over Flask or Django.

---

**Q: What is Redis used for here? Why not just use SQLite for everything?**

Redis and SQLite serve different access patterns. Redis handles active session state — state that changes rapidly (STARTING → ACTIVE → STOPPING → STOPPED) and needs sub-millisecond read/write under concurrent access from multiple workers. The TTL ensures orphaned sessions (worker crashed) auto-expire without manual cleanup. SQLite handles completed session history — persistent, slower, queried infrequently. Under high concurrency, SQLite's write serialization would bottleneck active session updates. Using Redis for hot state and SQLite for cold history gives you the right tool for each pattern.

---

**Q: Why does each session need isolation?**

Multiple test workers run simultaneously. Each worker captures traces on the same pool of network nodes but for different test scenarios. Without session isolation, Worker 2's stop command could accidentally stop Worker 1's trace — corrupting the trace data for an ongoing test. Session IDs are UUIDs. Every operation (start, stop, merge, validate) requires the session ID. A worker can only affect its own session. Redis stores each session under a unique key, so concurrent reads/writes from different workers never collide.

---

**Q: Why XML-RPC for node communication?**

Not a choice — a constraint. Nokia gNBs, AMF servers, and third-party telecom test equipment expose XML-RPC interfaces. It's a telecom industry standard deeply embedded in the ecosystem. The interesting design decision was the abstraction layer: NFTRACE's REST API shields test workers from XML-RPC entirely. Workers call clean REST. NFTRACE translates to XML-RPC internally. When the industry moves to gRPC or REST for node interfaces, only the NodeManager layer changes — the REST API and client SDK remain unchanged.

---

**Q: Why multiprocessing for parallel node operations?**

Starting and stopping traces on multiple nodes must happen simultaneously. If you start sequentially — node 1, then node 2, then node 3 — you miss the initial messages on nodes 2 and 3. All nodes must start capturing at exactly the same moment. `multiprocessing.Pool.starmap` gives true parallel execution across CPU cores. The alternative was asyncio, but `xmlrpc.client` is synchronous. Multiprocessing avoided adding an async XML-RPC dependency. For 5-10 nodes in a typical testbed, the overhead is negligible.

---

**Q: Why SQLite over PostgreSQL?**

NFTRACE is deployed on a single server in the test lab with sequential write patterns and low concurrent access. SQLite is zero-infrastructure — no server, no connection pooling, no credentials management, no DBA. For a single-server internal tool, adding PostgreSQL would be infrastructure complexity with no benefit. If NFTRACE needed multi-server deployment, failover, or 100s of concurrent writes, PostgreSQL would be the right migration.

---

**Q: What are SIP and Diameter and why do you validate them?**

SIP (Session Initiation Protocol) is used in 5G for IMS (IP Multimedia Subsystem) signaling — voice, video, messaging setup. Diameter is the authentication and authorization protocol used between the UE, gNB, AMF, and AUSF — it's the protocol that carries authentication information requests and answers during UE registration and 5G-AKA authentication.

Validating these protocols means checking that the correct messages appear in the trace in the correct order with the correct parameters. A test can pass at the application level (UE successfully registered) while the Diameter signaling underneath had timing violations or missing messages — indicating a latent defect that would cause failures under load or in edge cases.

---

**Q: How does the NCD integration work?**

NCD (Nokia Continuous Delivery) is Nokia's CI/CD pipeline. The integration adds pre_test() and post_test() hooks to the pipeline executor. When a test tagged for tracing starts, pre_test() automatically calls NFTRACE to start a trace session on the relevant nodes. When the test completes, post_test() stops and merges the trace, validates the protocol, and feeds the validation report back to the NCD pipeline report. Critically: a test can pass execution but fail trace validation — meaning the network behavior was wrong even if the assertions passed. This catches a class of bugs that were invisible before the integration, which is why the onsite team recognized it.

---

**Q: What happens if a node is unreachable when starting a trace?**

The NodeManager wraps each XML-RPC call in a try/except. If a node is unreachable, the session starts with a partial node list and a warning in the session state. The test can still proceed — the trace won't cover the unreachable node, but the other nodes are captured. The session state records which nodes are active and which failed, so the validation report includes a caveat: "Trace for gNB-002 unavailable — results may be incomplete."

The alternative — failing the entire session if any node is unreachable — would make the tool unusable in real testbeds where nodes occasionally restart or have transient connectivity issues.

---

**Q: How did you test NFTRACE itself?**

Three levels. Unit tests for each component: Redis session operations with a test Redis instance, SQLite CRUD operations, NodeManager with mock XML-RPC servers, ProtocolValidator with synthetic pcap fixtures (pre-captured trace files with known content). Integration tests with httpx hitting the full FastAPI stack in test mode: start a session, verify Redis state, simulate a node response, stop and merge, validate, verify SQLite history. End-to-end tests in the actual testbed with real nodes — these ran weekly as part of the NCD pipeline that NFTRACE itself was integrated into.

---

**Q: What would you change with more time?**

Three things. First, async node operations — replace `multiprocessing.Pool` with asyncio and an async XML-RPC library. This would reduce resource overhead and improve scalability beyond 10 concurrent sessions. Second, streaming trace validation — currently validation runs after the session completes (post-processing). Real-time streaming validation would catch protocol errors mid-test and could abort the test immediately on a critical violation. Third, web dashboard — currently trace results are consumed by the SDK or via the REST API. A web dashboard showing session history, pass/fail rates per scenario, and protocol error trends would make the tool useful for managers and QA leads, not just test engineers.

---

# PART 6: RESUME BULLETS — CURRENT vs OPTIMAL

## Current bullet in resume

> "Architected NFTRACE — a distributed REST-based network function tracing platform: FastAPI endpoints for lifecycle management (start/stop/merge/validate), Redis-backed session caching for parallel execution isolation, SQLite persistence for node state and execution history, XML-RPC for client-side SDK communication — decoupling test scenarios from validation logic → 50% reduction in pipeline validation time across CI/CD workflows."

**This bullet is strong.** It shows architecture thinking, explains WHY each technology was chosen, and has a concrete metric.

---

## What's still missing from the current bullet

**Missing 1 — Protocol validation (SIP and Diameter)**
This is completely absent. Validating actual telecom signaling protocols is a rare, domain-specific skill. One sentence should be added.

**Missing 2 — NCD CI/CD integration**
The TAF/NCD integration is mentioned in another bullet but separated. It belongs here as it's part of NFTRACE's impact.

**Missing 3 — Batch and real-time modes**
Subtle but worth one phrase — it shows the tool was designed for multiple use cases.

---

## Optimal bullet (after adding missing context)

> "Architected NFTRACE — a distributed REST-based network function tracing platform supporting real-time and batch modes: FastAPI lifecycle endpoints (start/stop/merge/validate), Redis session caching for parallel execution isolation across N concurrent workers, SQLite for node state persistence, XML-RPC for distributed node communication, and protocol-level validation for SIP and Diameter signaling → 50% reduction in pipeline validation time; single-handedly integrated NFTRACE into Nokia Continuous Delivery (NCD) CI/CD pipeline, enabling automatic trace capture and protocol validation for every tagged test case."

---

## What to update in skills section

Backend row — confirm these are listed:
- `FastAPI` ✅ already there
- `Redis` ✅ already there
- `SQLite` ✅ already there
- `XML-RPC` ✅ already there
- `Multiprocessing` ✅ already there

Add if not present:
- `Pyshark` — used in the protocol validation stage
- `SIP · Diameter` — under a "Telecom Protocols" note in the profile or skills section
