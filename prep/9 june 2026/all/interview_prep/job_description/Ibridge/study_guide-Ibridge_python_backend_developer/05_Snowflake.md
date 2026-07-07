# 05 — Snowflake (Working Knowledge ONLY)

JD says **"basic understanding"** and "working knowledge only" — read queries, support backend integrations. Goal: **sound informed, not expert.** ~2 hours total. Don't over-invest.

---

## jak_ai_job_coach — Before You Start

**Interviewer perspective:** For a "basic understanding" JD requirement, they are not looking for a Snowflake DBA. They are testing that you are *not blank* — that you can have an intelligent conversation, won't be blocked on day one, and can ramp quickly. The candidate who bombs this question says "I've never used it." The candidate who passes says "I haven't run production Snowflake workloads, but I understand the architecture and the integration pattern is straightforward from a FastAPI backend."

**Senior signal vs junior signal:**
- Junior: "I know it's a cloud database." Full stop.
- Senior: Explains *why* it exists (OLAP vs OLTP), *how* it would connect to a backend system they own, *what* they'd cache vs query live, and *where* it fits relative to PostgreSQL in the data stack.

**Common weak answer to avoid:** Pretending you've used it when you haven't. Interviewers who know Snowflake will immediately ask a follow-up ("what warehouse size did you use?", "how did you handle the credit cost?") and the bluff collapses. Honest framing + architectural understanding is stronger than a bluff.

---

## 1. What Snowflake is (the elevator pitch)
- A **cloud-native data warehouse** (SaaS — Software as a Service / "Data Cloud") for **analytics (OLAP — Online Analytical Processing)**, not transactional app workloads (OLTP — Online Transaction Processing, like PostgreSQL).
- Runs on AWS/Azure/GCP. You don't manage servers — fully managed, scales on demand.
- You query it with **standard SQL** — so your SQL knowledge transfers directly.

---

## 2. The one thing that makes it special: separation of storage & compute
- **Storage layer**: data stored compressed in columnar format in cloud object storage (S3 etc.).
- **Compute layer = "Virtual Warehouses"**: independent compute clusters (T-shirt sizes XS→4XL). You can spin up/down, resize, and run many warehouses on the **same data** without contention.
- **Cloud services layer**: brains — query optimization, metadata, security, transactions.
- **Why it matters**: scale compute up for a heavy query, scale to zero when idle (pay per use); analytics teams don't block each other.

---

## 3. Key concepts to name-drop
- **Virtual Warehouse**: compute cluster; auto-suspend/auto-resume to save cost.
- **Database → Schema → Table** hierarchy (same as you know).
- **Micro-partitions**: data auto-split into ~16MB compressed columnar chunks with metadata → enables **pruning** (skip partitions that can't match a filter) instead of manual indexing.
- **Clustering key**: optional, for very large tables to keep related data co-located.
- **Time Travel**: query/restore data as it was up to N days ago (`AT`/`BEFORE`) — undo accidental deletes.
- **Zero-copy cloning**: instant clone of a table/db without duplicating storage (metadata pointers) — great for test environments.
- **Stages**: locations to load/unload data (internal or external S3); `COPY INTO` for bulk load.
- **Streams & Tasks**: change-data-capture (streams) + scheduled SQL (tasks) for pipelines.
- **Warehouses vs databases**: warehouse = compute; database = storage. They scale independently — the key mental model.
- **Snowpark**: run Python/Java/Scala against Snowflake (you could mention as the Python tie-in).

---

## 4. Columnar / OLAP vs row / OLTP (likely the only deep question)
| | OLTP (PostgreSQL) | OLAP (Snowflake) |
|---|---|---|
| Workload | Many small reads/writes (app) | Big aggregations/scans (analytics) |
| Storage | Row-based | Columnar |
| Indexes | B-tree indexes | Micro-partition pruning (no manual indexes) |
| Scale | Vertical mostly | Elastic compute, separate from storage |

---

## 5. How backend integrates with Snowflake (your actual job angle)

**Veteran layer — the backend integration framing:**
> "From a FastAPI backend perspective, Snowflake is just another SQL data source behind a repository layer. The integration pattern: connection via `snowflake-connector-python`, queries via standard SQL, results mapped to Pydantic models, hot aggregates cached in Redis. The difference from PostgreSQL is that you'd use Snowflake for analytical queries — aggregations across millions of rows for dashboards or reports — not for transactional app reads. In practice, I'd have the FastAPI service query Snowflake for pre-aggregated analytical results (e.g., ad performance stats), cache them with a short TTL in Redis so I'm not hitting the warehouse on every API call, and keep PostgreSQL for the operational data (users, campaigns, real-time writes)."

- Python connector: **`snowflake-connector-python`** or **SQLAlchemy dialect** / Snowpark.
- Auth via key-pair / OAuth / user-password; use a connection pool; warehouse auto-suspend to control cost.
- Pattern: backend reads analytical results from Snowflake (e.g. ad performance aggregates) to serve via FastAPI, OR writes/loads events into Snowflake for analytics.

---

## 6. Honest framing — the exact script when pushed deeper

**The baseline answer (use this when asked about Snowflake experience):**
> "My production warehouse work is PostgreSQL — that's where I'm deep. I understand Snowflake's architecture: separated storage and compute, virtual warehouses, micro-partition pruning instead of manual indexes, Time Travel for recovery. Since it's standard SQL with a Python connector, integrating it from a FastAPI backend follows the same repository pattern I'd use for any SQL source. The JD scope is working-knowledge support, and I'm confident I can ramp on the operational specifics quickly."

**If they push harder ("have you actually written Snowflake queries?"):**
> "I haven't run production Snowflake workloads directly — I want to be straight with you on that. What I have is strong SQL fundamentals from PostgreSQL, a solid grasp of the architectural differences, and I've worked through the integration patterns. If there's a specific scenario you want to walk through, I'm happy to reason through it — I'd rather show you how I think than claim experience I don't have."

**Why this works:** It's specific enough to show preparation, honest enough to build trust, and ends on a forward offer ("reason through it") rather than a dead stop. Interviewers respect candidates who know their knowledge boundary.

---

## 7. Follow-up: "How would you optimize a slow Snowflake query?"

*You don't need hands-on experience to answer this — these concepts transfer directly from PostgreSQL knowledge.*

**Model answer:**
> "I'd work the same way I would for a slow PostgreSQL query — start with understanding what the query is actually doing. In Snowflake specifically:
> - **Pruning / clustering keys**: if the query is scanning a massive table on a low-cardinality filter column, adding a clustering key keeps related micro-partitions together so Snowflake can prune more aggressively — analogous to a partial index in PostgreSQL.
> - **Warehouse size**: if pruning is fine but execution is slow, bump the warehouse size. Snowflake scales compute horizontally, so an XS→M jump cuts execution time roughly by 4x on a scan-heavy query.
> - **Query profile**: Snowflake has a visual query profile in the UI that shows which step is the bottleneck (join, sort, scan) — I'd go there first before guessing.
> - **Materialized views**: for expensive aggregations that are read frequently (dashboards), pre-compute and cache the result as a materialized view.
> - **Result caching**: Snowflake caches query results for 24 hours — if the same query runs repeatedly on unchanged data, it returns instantly. Make sure you're not inadvertently busting the cache.
> The underlying principle is the same as PostgreSQL: identify where the cost is, then reduce the scan or the compute, not both at once."

**Senior signal:** Mentions the query profile / explain plan first rather than jumping to "add an index." Shows cost-awareness (warehouse size = credits = money).

**Follow-up to the follow-up they might ask:** "What's a clustering key vs an index?" — Answer: Snowflake has no traditional B-tree indexes. Instead, micro-partitions store min/max metadata. A clustering key tells Snowflake how to organize data into micro-partitions so the min/max metadata is tight and pruning skips more partitions. Conceptually similar to a partial sort index, but at the storage organization level.

---

## 8. Follow-up: "What's Snowflake's Time Travel and when would you use it from a backend?"

**Model answer:**
> "Time Travel lets you query or restore data as it was at any point within a retention window — up to 90 days on enterprise tier. The SQL is `SELECT * FROM my_table AT (timestamp => '2026-06-01 12:00:00')` or `BEFORE (statement => '<query_id>')`.
>
> From a backend perspective I'd use it in three scenarios:
> 1. **Data recovery** — a bad migration or a bug wrote incorrect data. Instead of trying to reconstruct from logs, I can query the table as it was before the bad write and use that to issue corrective updates.
> 2. **Audit trails** — a customer disputes what their data showed at a specific point in time. I can reproduce it exactly rather than relying on application-level audit logs.
> 3. **Debugging data issues** — something looks wrong in the analytics today; I can diff the current state against yesterday's snapshot directly in SQL to find when the anomaly appeared.
>
> It's essentially a built-in point-in-time recovery at the SQL layer — you don't need a separate backup/restore process for these cases."

**Interviewer perspective:** This is a bonus question. If you know it, you score extra. If you don't, say "I know the concept — it's point-in-time query/restore within a retention window, useful for recovery and auditing — but I haven't used the exact syntax in production."

---

## 9. Likely questions (full list)
1. What is Snowflake / how does it differ from PostgreSQL? (§1, §4)
2. What's separation of storage and compute? (§2)
3. What's a virtual warehouse? (compute cluster, auto-suspend)
4. OLTP vs OLAP?
5. How would a Python backend connect to Snowflake? (§5)
6. What is Time Travel / zero-copy cloning? (§8 + name-drop)
7. How would you optimize a slow Snowflake query? (§7)
8. Have you used Snowflake directly? (§6 — the honest framing)
