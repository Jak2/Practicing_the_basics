# Section 2 — Gap Analysis: Explanation + Term Definitions

*Same format. For each gap (a requirement in the JDs I can't yet back with hands-on evidence): **the explanation** — what it is, my honest bridge from what I* have *done, and where it doesn't apply — stated plainly for the interviewer. Then **the terms** — every concept in that area with a 2-line definition, because these are the topics interviewers probe hardest to catch a bluff, so I over-prepare the vocabulary.*

**Topics:** 2.1 LangGraph · 2.2 Multi-agent orchestration · 2.3 Advanced retrieval · 2.4 Vector DB breadth · 2.5 MCP · 2.6 ML/DL fundamentals · 2.7 Snowflake/Databricks · 2.8 Cloud breadth · 2.9 Streaming · 2.10 Django · 2.11 MLOps/LLMOps · 2.12 Knowledge graphs · 2.13 OAuth2/OIDC/SSO · 2.14 Golang/R/HF · 2.15 Domain compliance · 2.16 Fine-tuning

*Honesty rule: I state what I've built (the primitives), name the framework I haven't used, and show the bridge is short. Never claim a project I didn't do.*

---

## 2.1 LangGraph

### The explanation

LangGraph is a framework for building agents as stateful graphs with cycles — nodes are functions (an LLM call, a tool call, a router), edges are transitions, and a shared state object flows through. I've shipped LangChain RetrievalQA, not LangGraph, but I built the same execution model by hand at Brane — an agent loop with a tool registry, a verifier correction loop (which is a conditional edge back to the generation node), and state persisted in Postgres (a hand-rolled checkpointer). So I understand the model deeply; LangGraph just formalizes what I implemented manually. It doesn't apply to simple linear chains — for a plain retrieve-then-generate, LangChain is enough.

### The terms

- **State graph** — Modeling an agent as a graph where nodes are functions and a typed state object flows through, accumulating changes. Built for agents that loop, unlike linear chains.
- **State object** — A typed dict each node reads and updates, carrying the agent's working context through the graph. My Brane `agent_run_scratch` is the same idea.
- **Node** — A function in the graph — an LLM call, a tool call, or a router. Reads and updates the state.
- **Conditional edge** — A transition that routes based on state — "if the model asked for a tool, go to the tool node; else finish." How LangGraph expresses branching and loops.
- **Cycle** — A loop in the graph, back to an earlier node, until a stop condition. My verifier retry is a cycle back to the generation node.
- **Checkpointer** — Persists graph state between steps so agents are durable and resumable, and can pause for human-in-the-loop. My Postgres execution tables are a hand-rolled version.
- **Human-in-the-loop (HITL)** — Checkpointing and pausing at a node for human approval before continuing. LangGraph supports it natively via the checkpointer.
- **LangChain vs LangGraph** — LangChain is composable chains/components, largely linear; LangGraph is stateful graphs with cycles and conditional routing, for looping agents. Different tools for different shapes.
- **Recursion limit** — A cap on graph steps so an agent that keeps deciding to call a tool can't loop forever. The stop-condition safety I built as a retry cap at Brane.

---

## 2.2 Multi-agent orchestration (CrewAI, AutoGen, Swarm, A2A)

### The explanation

Multi-agent means splitting a complex task across specialized agents (a planner, a researcher, a critic) with a supervisor routing work and aggregating results. Brane was a single-agent loop, so I haven't built multi-agent systems or used CrewAI/AutoGen/Swarm — but I own every primitive they compose (tool-calling, a verifier/critic loop, state persistence, per-role prompt assembly), and my evaluation background applies directly since judging multi-agent output is itself an eval problem. Where it doesn't apply: most tasks — a single well-prompted agent with good tools usually suffices, and multi-agent multiplies cost, latency, and failure surface.

### The terms

- **Multi-agent orchestration** — Coordinating several specialized agents on one task, betting that specialization plus review beats one giant prompt. Justified only for genuinely decomposable tasks.
- **Supervisor / hierarchical** — One orchestrator agent delegates subtasks to worker agents and aggregates their results. The most common coordination pattern.
- **Peer / round-robin** — Agents converse turn-by-turn until a termination condition (AutoGen group chat). Good for code-gen-and-execute loops.
- **A2A (agent-to-agent)** — Structured message-passing protocols between autonomous agents. How agents coordinate directly rather than through a central controller.
- **CrewAI** — A framework for a role-based "crew" — agents with defined roles, goals, tools, and tasks. Good for structured pipelines.
- **AutoGen** — Microsoft's conversational multi-agent framework where agents (including a human proxy) exchange messages until termination. Strong for code generation + execution.
- **OpenAI Swarm / Agents SDK** — Lightweight handoffs between agents with shared context. A minimal multi-agent approach.
- **Termination condition** — The rule that stops the agents (task done, max turns), needed because agents can loop between each other. The multi-agent version of a step cap.
- **When not to use multi-agent** — When a single agent with good tools suffices; multi-agent multiplies token cost, latency, and failure modes. Reach for it only on genuinely decomposable, independently-verifiable subtasks.

---

## 2.3 Advanced retrieval (reranking, hybrid, query rewriting, HNSW tuning, Graph-RAG)

### The explanation

My 5G RAG used filtered dense semantic search — solid, but not the advanced retrieval stack some JDs list. I understand each piece and where it fits in the pipeline I already own end to end, and adding a reranker or hybrid fusion is a bounded upgrade, not a rewrite. My faithfulness-vs-hallucination eval is exactly what tells me whether retrieval is the failure point that needs these upgrades. It doesn't apply when a simple dense search already meets quality — you add complexity only when retrieval is measurably the bottleneck.

### The terms

- **Hybrid retrieval (BM25 + dense)** — Combining keyword search (BM25, great for exact identifiers) with dense embeddings (semantics), fusing scores. Pure dense misses exact codes; pure keyword misses paraphrases.
- **BM25** — A sparse keyword-ranking algorithm scoring on term frequency. Strong for exact terms, IDs, rare tokens that embeddings blur.
- **Reciprocal Rank Fusion** — A method to combine rankings from BM25 and dense search into one list. How hybrid retrieval merges the two signals.
- **Reranking** — A cross-encoder re-scores the top-50 first-stage results down to a precise top-5. The highest-ROI RAG precision upgrade.
- **Cross-encoder vs bi-encoder** — A bi-encoder embeds query and doc separately (fast, coarse); a cross-encoder reads them together (slow, accurate). Bi-encoder for first-stage, cross-encoder to rerank the shortlist.
- **Query rewriting** — Rewriting a vague or conversational query into a retrieval-optimized one before searching. Improves recall on messy user input.
- **Multi-hop retrieval** — Decomposing a question that needs multiple facts into sub-queries, retrieving each, then synthesizing. I did compound-query decomposition in EMS — the same idea.
- **Structure-aware chunking** — Splitting documents on headings/sections so each chunk is a coherent unit, versus blind fixed-size. Better retrieval than the 500-char chunks I used.
- **HNSW tuning** — Adjusting the index params: `M` (edges per node, recall vs memory), `ef_construction` (build quality), `ef_search` (query recall vs latency). The lever when recall/latency misses target.
- **Graph-RAG** — Retrieving by traversing a knowledge graph of entities/relations, alone or with vectors, for multi-hop reasoning across documents. Ties to knowledge graphs (see 2.12).

---

## 2.4 Vector DB breadth (Weaviate, Pinecone, Milvus, OpenSearch, pgvector)

### The explanation

I've shipped Qdrant and FAISS; the rest I understand conceptually. Because I chose Qdrant specifically for metadata filtering over the alternatives, I can place any of these on the axes that matter — managed vs self-hosted, native hybrid support, filtering quality, scale ceiling, and whether vectors sit beside your relational/keyword data. They all do ANN over HNSW-ish indexes; the differentiators are operational. It doesn't matter which you pick until those axes actually constrain you.

### The terms

- **Pinecone** — Fully-managed, serverless vector DB — zero ops, you pay and it scales. Pick when you want managed and don't want to run infra.
- **Weaviate** — Open-source with native hybrid search and built-in vectorization modules. Strong for hybrid + structured queries.
- **Milvus** — Open-source, built for massive scale (billions of vectors) with GPU indexing. Pick at very large scale.
- **OpenSearch / Elasticsearch** — One engine giving both BM25 keyword search and vector kNN. The natural home for hybrid retrieval if you're already on Elastic.
- **pgvector** — A Postgres extension putting vectors next to relational data — one DB, transactional. Pick when already on Postgres at moderate scale.
- **Managed vs self-hosted** — Pinecone is managed; Weaviate/Milvus/Qdrant self-hostable. The first axis to reason about — ops burden vs control.
- **Native hybrid support** — Whether the DB does BM25 + dense in one engine (Weaviate, OpenSearch) or only dense. Matters if you need exact-match plus semantic.
- **Scale ceiling** — How many vectors it handles well — Milvus targets billions, others less. Reason about it when your corpus is huge.
- **Co-location** — Whether vectors sit beside your relational data (pgvector) or keyword index (OpenSearch), avoiding a separate service. A real simplicity win when it fits.

---

## 2.5 MCP (Model Context Protocol)

### The explanation

MCP is an open protocol (from Anthropic) that standardizes how an LLM app connects to external tools, data, and context — "USB-C for LLM tools." A model host speaks MCP to any MCP server, which exposes tools (callable functions), resources (readable data), and prompts (templates). It's in my resume as a familiarity; I haven't published an MCP server, but my Brane tool-registry context is an in-house version of what MCP standardizes, so building one is wrapping my existing tool functions behind the MCP interface. It doesn't apply where a single hard-wired integration is simpler than the protocol overhead.

### The terms

- **MCP (Model Context Protocol)** — An open standard for connecting an LLM app to external tools/data, so a tool built once works with any MCP-speaking client. Decouples the model host from the tools.
- **MCP server** — A process that exposes tools, resources, and prompts over MCP; the model host connects to it and can invoke what it advertises. Where you wrap your tool functions.
- **Host / client / server** — The LLM app (host) connects via a client to one or more servers; JSON-RPC message passing. The three-part architecture.
- **Tools (MCP)** — Callable functions a server advertises with a schema, which the host's model can invoke. My Brane tool registry is the in-house equivalent.
- **Resources (MCP)** — Readable data/context a server exposes to the model (files, records). The "give the model context" half of the protocol.
- **JSON-RPC** — The remote-procedure-call format MCP uses for host-server messages. How the host discovers and invokes a server's capabilities.
- **Why MCP exists** — Before it, every agent hard-wired its own tool integrations; MCP standardizes the interface so tools are reusable across clients. Decoupling, like an API contract for tools.

---

## 2.6 ML/DL fundamentals (transformers, fine-tuning, NLP, CV, time-series)

### The explanation

This is my biggest honest gap: I use LLMs as APIs, not as models I train — I haven't trained a neural net, fine-tuned an LLM, or done classical ML/CV/time-series. But I understand transformer internals, the fine-tuning spectrum, and — importantly — I've done real statistical evaluation in my bias auditor (ANOVA, Cohen's d, embeddings, a DistilBERT model as a component). So for a role that's mostly building LLM applications with light ML, I'm strong; for core model training or CV/time-series research, I'm honest that's a growth area. I never bluff a training project I didn't do.

### The terms

- **Self-attention** — The transformer core: every token attends to every other, weighting relevance (Q·K softmax → weighted sum of V). Captures relationships across the whole sequence.
- **Multi-head attention** — Running attention several times in parallel to capture different relation types. Stacked with feed-forward layers to form the transformer.
- **Tokenization** — Splitting text into subword tokens (BPE/WordPiece) the model processes. Why it matters for token economics and context limits.
- **BERT vs GPT** — BERT is an encoder (bidirectional, good for classification/NER/embeddings); GPT is a decoder (autoregressive, good for generation). Different architectures for different tasks.
- **Fine-tuning spectrum** — Full fine-tuning (all weights, expensive) → LoRA/PEFT (train small adapters, cheap) → instruction tuning/RLHF (align behavior). vs prompting/RAG (no weight update).
- **LoRA / PEFT** — Parameter-Efficient Fine-Tuning: freeze the base model, train small low-rank adapter matrices. The cheap, standard way to fine-tune now.
- **Zero/few-shot vs fine-tuning** — Prompting with no/few examples (no training) vs updating weights. The senior rule: prefer prompting + RAG; fine-tune only for a stubborn behavior/format with good labeled data.
- **Supervised vs unsupervised** — Learning from labeled data (classify/regress) vs finding structure in unlabeled data (cluster/reduce dimensions). Classical ML basics.
- **Model evaluation metrics** — Precision/recall/F1, ROC-AUC, confusion matrix for classification. How you measure a trained model — my bias auditor uses genuine statistics (ANOVA, Cohen's d).
- **RLHF** — Reinforcement Learning from Human Feedback, aligning a model's behavior to human preferences. Part of the instruction-tuning end of the spectrum.

---

## 2.7 Snowflake / Databricks

### The explanation

My warehouse work is PostgreSQL; I've no hands-on Snowflake or Databricks. But I understand Snowflake's model — a cloud data warehouse for analytics (OLAP) with storage separated from compute, virtual warehouses you size and auto-suspend, columnar storage, and standard SQL — and since it's standard SQL with a Python connector, my SQL and integration skills transfer directly. Calibrated to Ibridge's "working knowledge only": I can support integrations and read queries day one and ramp fast; I won't bluff deep Snowflake tuning.

### The terms

- **OLAP vs OLTP** — OLAP is analytics over large data (Snowflake); OLTP is an app's transactional reads/writes (Postgres). Snowflake is built for the former, Postgres the latter.
- **Storage-compute separation** — Snowflake stores data in one layer and runs compute in independent clusters, so you scale each separately. Spin compute up for a heavy job, down when idle.
- **Virtual warehouse** — A Snowflake compute cluster that runs queries, sized up/down, auto-suspending when idle and auto-resuming on a query. You pay for compute only when used.
- **Columnar storage** — Storing data by column rather than row, efficient for analytical aggregations over few columns of many rows. Standard for warehouses.
- **snowflake-connector-python** — The official Python connector (plus a SQLAlchemy dialect) to query Snowflake from a backend. Makes it a standard SQL data source behind a data-access layer.
- **Databricks** — A Spark-based lakehouse (data lake + warehouse) with notebooks and MLflow, for large-scale data/ML pipelines. The other enterprise data platform named in JDs.
- **Lakehouse** — An architecture combining a data lake's cheap raw storage with a warehouse's structured querying. Databricks' model.

---

## 2.8 Cloud breadth (AWS ECS/Lambda/Step Functions/Kinesis, Azure OpenAI, GCP)

### The explanation

My hands-on AWS is AppSync, AppFlow, and IAM from Abjayon — not ECS/Lambda/Step Functions/Kinesis, and not Azure OpenAI. But I understand those as managed versions of patterns I've already built: containers (→ ECS/EKS), state machines (→ Step Functions), object storage + metadata (→ S3 + RDS), gateways (→ API Gateway), monitoring (→ CloudWatch). Azure OpenAI is the same OpenAI models behind a different endpoint, so my integration experience transfers directly. I ramp fast and I'm straight about what I've run versus understand.

### The terms

- **EC2** — AWS virtual machines you manage. The most basic compute; I map container/K8s knowledge onto the managed compute services instead.
- **Lambda** — Serverless event-driven functions, auto-scaling, pay-per-invocation, with cold starts and time/memory limits. For glue and event handlers.
- **ECS / Fargate / EKS** — Managed container running (ECS/Fargate) and managed Kubernetes (EKS). Since I containerize with Docker, this is running what I already build, managed.
- **Step Functions** — Orchestrates a workflow as a state machine of Lambdas/services with retries. Maps to my agent loop and NFTRACE lifecycle state machines.
- **S3** — Durable, cheap object storage for files/media/backups. The "asset in S3, metadata in Postgres" pattern.
- **RDS** — Managed relational database (including Postgres). I know Postgres; RDS is the managed version.
- **API Gateway** — Managed edge entry point — auth, rate limiting, routing, SSL. The managed version of my FastAPI-middleware gateway.
- **CloudWatch** — AWS logs, metrics, and alarms. The managed version of my structured-logging + RED-metrics + alerting.
- **Kinesis** — Managed high-throughput event streaming — producers, partitions, consumer groups. A genuine gap; I know the concepts but haven't run streaming.
- **Azure OpenAI** — The same OpenAI models behind Azure's endpoint, keys, and deployment-name convention plus enterprise compliance. My OpenAI/Anthropic integration transfers — different endpoint, same call pattern.

---

## 2.9 Streaming (LLM token streaming + data streaming)

### The explanation

Two kinds. LLM token streaming — yielding tokens as generated so the user sees output immediately — I haven't shipped (EMS buffers responses), but it's a bounded upgrade to my async FastAPI endpoints: swap the buffered call for a streamed generator via StreamingResponse. Data streaming (Kafka/Kinesis) for high-throughput event pipelines is a genuine gap — my experience is batch and request-response. So token streaming is a small step I can articulate precisely; large-scale data streaming I understand conceptually but haven't run.

### The terms

- **LLM token streaming** — Streaming tokens as the model generates them (SSE / provider `stream=True`) instead of waiting for the full completion. Improves perceived latency.
- **SSE (Server-Sent Events)** — A one-way server-to-client streaming protocol over HTTP, used to push tokens to the browser. Served via FastAPI StreamingResponse.
- **StreamingResponse** — The FastAPI response type that streams chunks from an async generator. The bounded change to add token streaming to my existing async endpoints.
- **Data streaming (Kafka/Kinesis)** — High-throughput event pipelines: producers write to a topic/stream, consumers process it. Versus my batch/request-response experience.
- **Partitions** — Splitting a stream so consumers can process in parallel and ordering is maintained within a partition. A core streaming concept.
- **Consumer groups** — Multiple consumers sharing the work of a stream, each reading a subset of partitions. How you scale stream processing.
- **Backpressure (streaming)** — Slowing producers when consumers can't keep up, via bounded buffers. Prevents overwhelming the pipeline.
- **At-least-once delivery** — A guarantee that each message is processed at least once (possibly duplicated), requiring idempotent consumers. The common streaming delivery semantic.

---

## 2.10 Django

### The explanation

I'm FastAPI/Flask-adjacent, not Django, but I don't pretend otherwise — I map it. Django is batteries-included (ORM, admin, auth, migrations, templates) and synchronous-first; FastAPI is async-native, lighter, API-focused. Every Django concept has a direct analogue in my stack: its ORM ≈ SQLAlchemy, migrations ≈ Alembic, DRF serializers ≈ Pydantic, test framework ≈ pytest + TestClient. So the transfer is syntax and conventions, not concepts — I'd be productive in days. It doesn't fit where you want a pure async API service with no admin/template weight — that's where I'd pick FastAPI.

### The terms

- **Batteries-included** — Django ships an ORM, admin panel, auth, migrations, and template engine out of the box. Great for CRUD-with-admin; heavier than a pure API needs.
- **Django ORM** — Django's object-relational mapper, analogous to SQLAlchemy which I know well. Same concept — models mapped to tables.
- **Django migrations** — Django's schema-migration system, analogous to Alembic which I use. Versioned, reviewable schema changes.
- **Django REST Framework (DRF)** — The library for building REST APIs in Django; its serializers are analogous to Pydantic models which I know deeply. Validation and serialization.
- **Django test framework** — Django's testing tools, analogous to pytest + TestClient which I use. Same testing concepts.
- **WSGI (Django)** — Django is synchronous-first on WSGI, with async support bolted on later. FastAPI is async-native on ASGI — the key architectural difference.
- **When to pick Django** — A CRUD-heavy app that benefits from the admin panel, built-in auth, and ORM. I'd pick it there; FastAPI for async API services.

---

## 2.11 MLOps / LLMOps

### The explanation

This is a gap that mostly isn't one — I have the discipline, not the named tooling. I've built LLMOps from first principles: my Prompt Regression Suite is a CI quality gate with baseline governance, drift monitoring, and audit trails; my LLM Eval Framework does continuous evaluation with threshold alerts; my Bias Auditor produces regulatory documentation and guardrail recommendations. That's evaluation, monitoring, drift detection, governance, and Responsible AI — the substance. What I lack is MLflow specifically and commercial monitoring platforms (LangSmith, Arize), which I'd pick up fast because I built the harder custom equivalents.

### The terms

- **LLMOps** — Operating LLMs in production: versioning prompts/models, evaluation, monitoring quality/cost/latency, drift detection, guardrails, governance. I built the substance custom.
- **MLOps** — The ML equivalent — training pipelines, model registry, experiment tracking, deployment, monitoring. My gap is more the training-side tooling (see 2.6).
- **MLflow** — A platform for experiment tracking and model registry. The named tool I haven't used; conceptually simple given I built custom eval/regression systems.
- **Drift monitoring** — Detecting when a model's behavior shifts in production (e.g. a provider update). My prompt-regression weekly full-suite run does exactly this.
- **Model registry** — A versioned store of models with stage/metadata, so you track and promote versions. What MLflow provides; I built the prompt-baseline equivalent.
- **Guardrails** — Runtime checks constraining model behavior (block unsafe output, enforce format). My bias auditor generates guardrail recommendations; agent output gets validated.
- **Responsible AI** — Bias testing, transparency, and governance for AI systems. My bias auditor's EU AI Act reporting is concrete Responsible AI work.
- **Experiment tracking** — Logging model runs, params, and metrics to compare them. MLflow's core; I did the equivalent comparing models in my eval framework.
- **LangSmith / Arize** — Commercial LLM observability/monitoring platforms. Tools I'd adopt as a shortcut, having built the harder custom versions.

---

## 2.12 Knowledge graphs, ontology, Graph databases

### The explanation

Genuine tooling gap — no graph DB or ontology work. But I understand the why: graph databases (Neo4j) store data as nodes and relationships for relationship-heavy, multi-hop queries that are painful in SQL, and an ontology is the formal schema of entity types and allowed relations. My relational schema design with junction tables is essentially hand-drawn graph edges, so the data-modeling foundation transfers; the tooling (Cypher, Neo4j) is new. It doesn't apply where your queries are straightforward relational lookups — a graph DB earns its place on relationship traversal.

### The terms

- **Graph database (Neo4j)** — Stores data as nodes, relationships, and properties, queried by traversal. Strong for relationship-heavy queries ("all X connected to Y within 3 hops") that are painful in SQL.
- **Cypher** — Neo4j's query language for expressing graph traversals. The new tooling I'd learn; the concepts transfer from my relational modeling.
- **Ontology** — A formal schema of entity types and the relations allowed between them — a domain model. Drives structured, consistent knowledge layers.
- **Graph-RAG** — Retrieving by traversing a knowledge graph (or graph + vectors) for multi-hop reasoning across documents. Ties to advanced retrieval (2.3).
- **Nodes and edges** — The graph primitives — entities (nodes) and relationships (edges) with properties. A junction table is a materialized edge, which is my bridge to the concept.
- **Multi-hop traversal** — Following relationships across several steps to answer a question connecting distant facts. What graph DBs do that multi-join SQL does painfully.

---

## 2.13 OAuth2 / OIDC / SSO depth

### The explanation

Partial gap — I've built JWT plus attribute-level RBAC (strong), and I can explain OAuth2/OIDC/SSO thoroughly, but I've implemented the full OAuth dance less than I've read it. My token-verification and authorization experience covers half of it solidly; the redirect-consent-code-exchange flow I've read more than built. So I'm honest: JWT and RBAC are hands-on, OAuth2/OIDC I understand well and would implement confidently.

### The terms

- **OAuth2** — Delegated authorization — an app acts on a user's behalf without their password. Roles: resource owner, client, authorization server, resource server.
- **Authorization-code flow** — The web flow: redirect to the auth server, user consents, get a code, exchange it server-side for an access token (+ refresh). The standard OAuth2 flow.
- **OIDC (OpenID Connect)** — An identity layer on OAuth2 adding an ID token (a JWT with identity claims) so you know who the user is, not just what they can access. Authentication on top of authorization.
- **ID token** — The JWT OIDC issues with identity claims (`sub`, email). Distinguishes OIDC (identity) from raw OAuth2 (access).
- **SSO (Single Sign-On)** — One identity provider authenticating a user across many apps, built on OIDC. Log in once, access everything.
- **Resource owner / client / authorization server / resource server** — The four OAuth2 roles: the user, the app, the identity provider (Google), and the API holding the data. The players in the flow.
- **Consent** — The user approving the app's requested access at the authorization server before a code is issued. The user-control step in the flow.

---

## 2.14 Golang, R / R Shiny, Hugging Face training

### The explanation

These are explicitly optional in the JDs ("a plus", "bonus"), so I don't over-invest, but I stay honest. Golang — I don't write it; I understand it's for high-performance concurrent services (goroutines/channels), and I'm willing to learn (one JD literally says "or willingness to learn"). R/R Shiny — a statistical language + its dashboard framework; I do the equivalent in Python/Streamlit, a direct conceptual analogue. Hugging Face — I use sentence-transformers and a DistilBERT model (I consume HF models), but I haven't used HF for training/fine-tuning, so partial.

### The terms

- **Goroutines / channels** — Go's lightweight concurrency primitives — cheap concurrent functions and typed pipes between them. Go's model for high-performance concurrent services.
- **R / R Shiny** — A statistical language (R) and its interactive dashboard framework (Shiny). I do the equivalent analytics in Python + Streamlit — same concept, different syntax.
- **Hugging Face Transformers** — A library/hub of pretrained transformer models and training tooling. I consume its models (sentence-transformers, DistilBERT) but haven't trained/fine-tuned with it.
- **sentence-transformers** — A Hugging Face-ecosystem library for embedding models (all-MiniLM-L6-v2). I use it for embeddings and semantic similarity — real, but consuming not training.
- **Consuming vs training HF models** — Using a pretrained model for inference/embeddings (what I do) vs fine-tuning/training one (what I haven't). The honest boundary.

---

## 2.15 Domain compliance (HIPAA, healthcare, fintech)

### The explanation

I haven't worked in HIPAA/healthcare or fintech, but I have real regulated-compliance experience that transfers: my Bias & Fairness Auditor is built around the EU AI Act (Articles 9 and 13), EEOC, and RBI AI-governance guidelines — bias testing, audit documentation, guardrails, PII-awareness (the blind judge strips demographic labels). Plus carrier-grade delivery discipline at Nokia. So I understand "build to a regulatory standard, produce audit evidence, handle sensitive data carefully," and I'd map that to HIPAA fast. Notably, Gainwell's role excludes PHI access — application development only — which fits me well.

### The terms

- **HIPAA** — US healthcare privacy regulation governing Protected Health Information (PHI). Requires minimum-necessary access, audit trails, and safeguards — concepts my EU-AI-Act work maps to.
- **PHI / PII** — Protected Health Information / Personally Identifiable Information — sensitive data requiring careful handling. My bias auditor strips demographic labels; I don't send/log sensitive data.
- **EU AI Act (Article 9 / 13)** — EU regulation on high-risk AI: Article 9 requires documented bias testing before deployment, Article 13 requires explainability to regulators. My bias auditor builds to it.
- **EEOC** — US Equal Employment Opportunity Commission guidelines on hiring fairness. One of the regulatory frameworks my bias auditor targets.
- **Audit trail** — A recorded, reviewable history of what a system did and why (my prompt-regression baseline resets, the bias audit report). Core to any compliance regime.
- **Least-necessary access** — Granting access only to the data strictly required — HIPAA's minimum-necessary, the same principle as least-privilege IAM I've done. Transfers directly.

---

## 2.16 Fine-tuning (retrievers, small LLMs)

### The explanation

Covered in depth in 2.6 — I haven't fine-tuned. The short version for the JDs that call it out: I know the spectrum (full → LoRA/PEFT → instruction tuning) and, critically, when not to — prefer prompting + RAG first, fine-tune only for a stubborn behavior/format/domain with good labeled data. My default is to reach for RAG (which I've shipped) before fine-tuning (which I haven't), which is usually the correct engineering call anyway. It doesn't apply where prompting or RAG already meets the need.

### The terms

- **Full fine-tuning** — Updating all of a model's weights on your data. Most expensive and the least-used option now.
- **LoRA / PEFT** — Parameter-Efficient Fine-Tuning — freeze the base, train small low-rank adapters. The cheap, standard fine-tuning approach.
- **Instruction tuning** — Fine-tuning a model to follow instructions in a particular style/format. The behavior-alignment end of the spectrum.
- **Fine-tuning vs RAG** — Fine-tuning bakes knowledge/behavior into weights (expensive, stale on change); RAG injects knowledge at inference (cheap to update, transparent). Fine-tune for behavior, RAG for knowledge.
- **When to fine-tune** — Only for a stubborn behavior, format, or domain the base model won't do reliably, with good labeled data. Otherwise prompting + RAG — my shipped default.
- **Fine-tuning a retriever** — Training the embedding/retrieval model on domain data to improve retrieval relevance. The Codvo "fine-tune retrievers" ask — a retrieval-quality lever I understand but haven't done.

---

*End of Section 2 terms. Each gap: an honest statement of what it is, my bridge from what I've built, and where it doesn't apply — then a 2-line definition for every term, so I can hold the conversation on ground I haven't shipped without bluffing. Pair with [SECTION_1_TERMS.md](SECTION_1_TERMS.md) (matched skills) and [SECTION_3_DEEP.md](SECTION_3_DEEP.md) (projects).*

