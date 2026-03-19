# PROJECT REPORT 01
# AI Workflow Orchestration Engine — "The Brain"
### LangGraph · CrewAI · n8n · Ollama

---

**Document Version:** 1.0.0
**Classification:** Technical Design & Implementation Report
**Prepared By:** Senior Systems Architect
**Date:** 2026-03-20
**Status:** Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Requirements](#system-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Component Deep Dive](#component-deep-dive)
5. [Environment Setup & Configuration](#environment-setup--configuration)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Testing & Validation](#testing--validation)
8. [Monitoring & Observability](#monitoring--observability)
9. [Security Considerations](#security-considerations)
10. [Scalability Roadmap](#scalability-roadmap)

---

## 1. Executive Summary

This report defines the complete architecture, setup, and implementation plan for an **AI Workflow Orchestration Engine** — the central decision-making "brain" of a fully automated AI influencer pipeline. The system is built on a graph-based, stateful, multi-agent execution model using **LangGraph** as the primary orchestration layer, **CrewAI** for role-based agent delegation, and **n8n** as the visual workflow automation backbone for scheduling and integrations.

The engine is responsible for:
- Fetching and ranking trending topics from external data sources
- Delegating content tasks to specialized AI agents (Researcher, Writer, Reviewer)
- Executing self-critique loops to enforce persona consistency
- Emitting structured output payloads to downstream pipeline stages (Image, Video, Publish)

---

## 2. System Requirements

### 2.1 Hardware Requirements

| Component | Minimum | Recommended (Production) |
|-----------|---------|--------------------------|
| CPU | 8-core x86_64 | 16-core AMD EPYC / Intel Xeon |
| RAM | 16 GB | 64 GB ECC |
| Storage | 50 GB SSD | 500 GB NVMe SSD |
| GPU | Not required for orchestration | Optional: NVIDIA RTX 3090 (for local LLM) |
| Network | 100 Mbps | 1 Gbps dedicated |

### 2.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Ubuntu Server | 22.04 LTS | Host OS |
| Python | 3.11.x | Runtime |
| Docker | 26.x | Containerization |
| Docker Compose | 2.x | Multi-container orchestration |
| Node.js | 20.x LTS | n8n runtime |
| PostgreSQL | 15.x | n8n state & workflow persistence |
| Redis | 7.x | Queue management & caching |
| Ollama | Latest | Local LLM inference server |

### 2.3 Python Package Dependencies

```
langgraph>=0.2.0
langchain>=0.2.0
langchain-community>=0.2.0
langchain-ollama>=0.1.0
crewai>=0.55.0
crewai-tools>=0.8.0
fastapi>=0.111.0
uvicorn>=0.30.0
pydantic>=2.7.0
redis>=5.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
structlog>=24.2.0
prometheus-client>=0.20.0
```

### 2.4 External API Dependencies

| Service | Purpose | Tier |
|---------|---------|------|
| Google Trends API (via `pytrends`) | Trend data | Free |
| NewsAPI.org | Trending news | Free (100 req/day) |
| Reddit API | Trending topics by subreddit | Free |
| Groq API | Fast cloud LLM fallback | Free tier available |

---

## 3. Architecture Overview

### 3.1 High-Level System Diagram

```
+------------------------------------------------------------------+
|                      ORCHESTRATION ENGINE                        |
|                                                                  |
|  +------------+    +------------------------------------------+ |
|  |  Scheduler |    |           LangGraph State Machine         | |
|  |  (n8n/cron)|    |                                          | |
|  +------------+    |  +----------+      +------------------+  | |
|        |           |  |  Fetch   |----->| Topic Ranker &   |  | |
|        v           |  |  Trends  |      | Selector Node    |  | |
|  +------------+    |  +----------+      +--------+---------+  | |
|  |  External  |--->|                             |            | |
|  |  Data APIs |    |  +--------------------------v----------+ | |
|  +------------+    |  |      CrewAI Multi-Agent Layer       | | |
|                    |  |  [Researcher]->[Writer]->[Editor]   | | |
|                    |  +---------------------------+---------+ | |
|                    |                              |           | |
|                    |  +--------------------------v----------+ | |
|                    |  |     Self-Critique Review Loop       | | |
|                    |  |  (Persona Check -> Revise -> OK)    | | |
|                    |  +---------------------------+---------+ | |
|                    +------------------------------------------+ |
+------------------------------------------------------------------+
                                      |
               +-----------------------+------------------------+
               |                                               |
     +---------v----------+                       +-----------v-------+
     |   Image Pipeline   |                       |  Video Pipeline   |
     |    (Report 02)     |                       |   (Report 03)     |
     +--------------------+                       +-------------------+
```

### 3.2 LangGraph State Machine Flow

```
START
  |
  v
[fetch_trends_node]
  |  Pulls top 10 trending topics from Google Trends + NewsAPI
  |
  v
[rank_and_select_node]
  |  Scores topics by: virality, niche relevance, past performance
  |
  v
[research_node]  <- CrewAI Researcher Agent
  |  Gathers facts, statistics, and angle for topic
  |
  v
[script_write_node]  <- CrewAI Writer Agent
  |  Produces a 30-60 second short-form video script
  |
  v
[persona_review_node]  <- CrewAI Editor/Critic Agent
  |  Checks: tone, persona match, brand voice, CTA presence
  |
  v
[conditional_edge]
  |  -- PASS --> [finalize_node]
  |  -- FAIL --> [revise_node] --> [persona_review_node]  (max 3 retries)
  |
  v
[finalize_node]
  |  Packages output: script + image_prompt + hashtags + metadata
  |
  v
END -> emits payload to downstream services
```

---

## 4. Component Deep Dive

### 4.1 LangGraph — Stateful Graph Engine

LangGraph extends LangChain with persistent state across nodes. Each node in the graph is a Python function that receives the current `AgentState` (a TypedDict) and returns a delta to be merged into the state.

**Key Concepts:**
- **State:** Shared dictionary passed between all nodes. Only nodes can mutate it.
- **Nodes:** Pure functions or Runnable objects that transform state.
- **Edges:** Conditional routing logic (e.g., pass/fail review).
- **Checkpointing:** State snapshots persisted to PostgreSQL via `AsyncPostgresSaver`.

### 4.2 CrewAI — Multi-Agent Role Framework

CrewAI defines agents as role-playing entities with a `role`, `goal`, `backstory`, and assigned `tools`. A `Crew` coordinates agents through `Tasks` in sequential or hierarchical process.

| Agent Role | Goal | Tools |
|------------|------|-------|
| Senior Researcher | Find authoritative facts for the topic | SerperDevTool, WebScraperTool |
| Script Writer | Convert research into an engaging short-form script | None (pure LLM) |
| Brand Editor | Enforce persona tone, remove off-brand language | None (pure LLM) |

### 4.3 n8n — Scheduling & Integration Bus

n8n acts as the scheduler and inter-service message bus. It triggers the LangGraph workflow on a CRON schedule and receives output webhooks from each pipeline stage.

**Workflow nodes used:**
- `Schedule Trigger` — fires workflow every day at 8:00 AM
- `HTTP Request` — calls FastAPI `/orchestrate` endpoint
- `Webhook` — receives final payload
- `Switch` — routes payload to Image or Video pipeline

### 4.4 Ollama — Local LLM Server

Ollama serves open-weight LLMs over a local REST API, eliminating cloud API costs.

| Task | Model | VRAM Required |
|------|-------|---------------|
| Script Writing | `llama3:8b-instruct` | 6 GB |
| Persona Review | `mistral:7b-instruct` | 5 GB |
| Research Summarization | `gemma2:9b` | 7 GB |

---

## 5. Environment Setup & Configuration

### 5.1 Project Directory Structure

```
orchestration-engine/
├── docker-compose.yml
├── .env
├── requirements.txt
├── src/
│   ├── main.py
│   ├── graph/
│   │   ├── state.py             # AgentState TypedDict
│   │   ├── nodes.py             # All LangGraph node functions
│   │   ├── edges.py             # Conditional routing logic
│   │   └── graph_builder.py     # Compile the StateGraph
│   ├── agents/
│   │   ├── crew_config.py       # CrewAI agents & tasks
│   │   └── tools.py
│   ├── services/
│   │   ├── trends.py            # Google Trends + NewsAPI fetcher
│   │   └── topic_ranker.py
│   └── config/
│       └── settings.py
├── tests/
│   ├── test_nodes.py
│   └── test_crew.py
└── n8n-workflows/
    └── daily-content-trigger.json
```

### 5.2 Docker Compose Configuration

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: orchestration_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  orchestration-api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - ./src:/app/src

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=orchestration_db
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
  ollama_models:
```

### 5.3 Environment Variables

```env
# .env
POSTGRES_USER=orchestration
POSTGRES_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>
N8N_USER=admin
N8N_PASSWORD=<strong-random-password>

# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434
PRIMARY_MODEL=llama3:8b-instruct
REVIEWER_MODEL=mistral:7b-instruct

# Fallback Cloud LLM (Groq)
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama3-70b-8192

# External Data APIs
NEWS_API_KEY=<your-newsapi-key>
SERPER_API_KEY=<your-serper-api-key>

# Application
LOG_LEVEL=INFO
MAX_REVIEW_RETRIES=3
CONTENT_NICHE=technology,AI,productivity
```

---

## 6. Step-by-Step Implementation

### Step 1 — Define the Agent State

```python
# src/graph/state.py
from typing import TypedDict, List

class AgentState(TypedDict):
    niche: str
    trending_topics: List[dict]
    selected_topic: dict
    research_notes: str
    raw_script: str
    image_prompt: str
    hashtags: List[str]
    review_passed: bool
    review_feedback: str
    retry_count: int
    final_payload: dict
```

### Step 2 — Implement Node Functions

```python
# src/graph/nodes.py
import structlog
from langchain_ollama import ChatOllama
from src.services.trends import TrendFetcher
from src.services.topic_ranker import TopicRanker
from src.agents.crew_config import build_content_crew
from src.graph.state import AgentState
from src.config.settings import settings

log = structlog.get_logger()
llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.PRIMARY_MODEL)


async def fetch_trends_node(state: AgentState) -> dict:
    log.info("fetch_trends_node.start", niche=state["niche"])
    fetcher = TrendFetcher(niche=state["niche"])
    topics = await fetcher.fetch_all()
    return {"trending_topics": topics}


async def rank_and_select_node(state: AgentState) -> dict:
    ranker = TopicRanker()
    selected = ranker.select_top(state["trending_topics"])
    log.info("rank_and_select_node.selected", topic=selected["title"])
    return {"selected_topic": selected}


async def run_crew_node(state: AgentState) -> dict:
    crew = build_content_crew(topic=state["selected_topic"], niche=state["niche"])
    result = crew.kickoff()
    return {
        "research_notes": result.tasks_output[0].raw,
        "raw_script": result.tasks_output[1].raw,
        "image_prompt": result.tasks_output[2].raw,
    }


async def persona_review_node(state: AgentState) -> dict:
    persona_prompt = f"""
    You are a brand consistency reviewer for an AI influencer.
    Persona: Confident, witty, educational, Gen-Z friendly, never corporate.

    Review this script:
    ---
    {state['raw_script']}
    ---

    Respond with:
    VERDICT: PASS or FAIL
    FEEDBACK: <specific issues if FAIL, or "None" if PASS>
    """
    response = await llm.ainvoke(persona_prompt)
    content = response.content
    passed = "VERDICT: PASS" in content
    feedback = content.split("FEEDBACK:")[-1].strip()
    return {
        "review_passed": passed,
        "review_feedback": feedback,
        "retry_count": state.get("retry_count", 0)
    }


async def revise_node(state: AgentState) -> dict:
    revision_prompt = f"""
    Rewrite this script to address the following feedback:
    FEEDBACK: {state['review_feedback']}

    ORIGINAL SCRIPT:
    {state['raw_script']}

    Return only the revised script, no commentary.
    """
    response = await llm.ainvoke(revision_prompt)
    return {
        "raw_script": response.content,
        "retry_count": state["retry_count"] + 1
    }


async def finalize_node(state: AgentState) -> dict:
    hashtag_prompt = f"Generate 15 relevant hashtags for: {state['selected_topic']['title']}. Return as comma-separated list."
    hashtag_response = await llm.ainvoke(hashtag_prompt)
    hashtags = [h.strip() for h in hashtag_response.content.split(",")]

    payload = {
        "topic": state["selected_topic"]["title"],
        "script": state["raw_script"],
        "image_prompt": state["image_prompt"],
        "hashtags": hashtags,
        "metadata": {
            "niche": state["niche"],
            "generated_at": __import__("datetime").datetime.utcnow().isoformat()
        }
    }
    return {"final_payload": payload}
```

### Step 3 — Define Conditional Routing Edges

```python
# src/graph/edges.py
from src.graph.state import AgentState
from src.config.settings import settings

def review_router(state: AgentState) -> str:
    if state["review_passed"]:
        return "finalize"
    if state["retry_count"] >= settings.MAX_REVIEW_RETRIES:
        return "finalize"  # Force finalize after max retries
    return "revise"
```

### Step 4 — Build and Compile the Graph

```python
# src/graph/graph_builder.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.graph.state import AgentState
from src.graph.nodes import (
    fetch_trends_node, rank_and_select_node, run_crew_node,
    persona_review_node, revise_node, finalize_node
)
from src.graph.edges import review_router


def build_graph(checkpointer):
    graph = StateGraph(AgentState)

    graph.add_node("fetch_trends", fetch_trends_node)
    graph.add_node("rank_select", rank_and_select_node)
    graph.add_node("run_crew", run_crew_node)
    graph.add_node("persona_review", persona_review_node)
    graph.add_node("revise", revise_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "fetch_trends")
    graph.add_edge("fetch_trends", "rank_select")
    graph.add_edge("rank_select", "run_crew")
    graph.add_edge("run_crew", "persona_review")
    graph.add_conditional_edges(
        "persona_review",
        review_router,
        {"finalize": "finalize", "revise": "revise"}
    )
    graph.add_edge("revise", "persona_review")
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=checkpointer)
```

### Step 5 — Configure CrewAI Agents & Tasks

```python
# src/agents/crew_config.py
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_ollama import ChatOllama
from src.config.settings import settings

def build_content_crew(topic: dict, niche: str) -> Crew:
    llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.PRIMARY_MODEL)
    search_tool = SerperDevTool()

    researcher = Agent(
        role="Senior Content Researcher",
        goal=f"Find 5 surprising, shareable facts about: {topic['title']}",
        backstory="A veteran tech journalist with 15 years finding viral stories.",
        tools=[search_tool],
        llm=llm,
        max_iter=3
    )

    writer = Agent(
        role="Short-Form Video Script Writer",
        goal="Write a compelling 30-45 second video script from the research",
        backstory="An ex-Netflix scriptwriter specializing in viral short-form content.",
        llm=llm
    )

    image_director = Agent(
        role="AI Image Art Director",
        goal="Write a precise Stable Diffusion prompt matching the script's visual mood",
        backstory="A digital artist with deep expertise in Stable Diffusion prompting.",
        llm=llm
    )

    research_task = Task(
        description=f"Research '{topic['title']}' in the context of {niche}. Find 5 key facts.",
        expected_output="A bullet-point research brief with 5 key facts and sources.",
        agent=researcher
    )

    script_task = Task(
        description="Using the research brief, write a 30-45 second video script. Start with a hook. End with a CTA.",
        expected_output="A complete video script with [HOOK], [BODY], and [CTA] sections.",
        agent=writer,
        context=[research_task]
    )

    image_task = Task(
        description="Write a Stable Diffusion XL image prompt for the influencer that matches the script's mood.",
        expected_output="A single detailed image generation prompt, max 200 words.",
        agent=image_director,
        context=[script_task]
    )

    return Crew(
        agents=[researcher, writer, image_director],
        tasks=[research_task, script_task, image_task],
        process=Process.sequential,
        verbose=True
    )
```

### Step 6 — Expose via FastAPI

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncpg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.graph.graph_builder import build_graph
from src.config.settings import settings
import structlog

log = structlog.get_logger()
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    conn = await asyncpg.connect(settings.DATABASE_URL)
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()
    graph = build_graph(checkpointer)
    log.info("app.startup.complete")
    yield
    await conn.close()

app = FastAPI(title="Orchestration Engine API", lifespan=lifespan)

class OrchestrateRequest(BaseModel):
    niche: str = "AI technology"
    thread_id: str = "default"

@app.post("/orchestrate")
async def orchestrate(request: OrchestrateRequest, background_tasks: BackgroundTasks):
    config = {"configurable": {"thread_id": request.thread_id}}
    initial_state = {"niche": request.niche, "retry_count": 0}

    async def run_graph():
        async for event in graph.astream(initial_state, config=config):
            log.info("graph.event", node=list(event.keys()))

    background_tasks.add_task(run_graph)
    return {"status": "accepted", "thread_id": request.thread_id}

@app.get("/status/{thread_id}")
async def get_status(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"state": state.values}
```

### Step 7 — Pull Ollama Models

```bash
docker exec orchestration-engine-ollama-1 ollama pull llama3:8b-instruct
docker exec orchestration-engine-ollama-1 ollama pull mistral:7b-instruct
```

### Step 8 — Import n8n Workflow

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows > Import from File**
3. Import `n8n-workflows/daily-content-trigger.json`
4. Configure HTTP Request node to point to `http://orchestration-api:8000/orchestrate`
5. Activate the workflow

---

## 7. Testing & Validation

### Unit Tests

```bash
pytest tests/test_nodes.py -v
pytest tests/test_crew.py -v --timeout=120
```

### Integration Test — Full Graph Run

```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"niche": "AI technology", "thread_id": "test-001"}'

curl http://localhost:8000/status/test-001
```

### Expected Output

```json
{
  "state": {
    "final_payload": {
      "topic": "OpenAI releases GPT-5",
      "script": "[HOOK] What if I told you AI just got 10x smarter...",
      "image_prompt": "photorealistic young woman, neon-lit tech environment...",
      "hashtags": ["#AI", "#GPT5", "#Tech"],
      "metadata": {
        "niche": "AI technology",
        "generated_at": "2026-03-20T08:00:00Z"
      }
    }
  }
}
```

---

## 8. Monitoring & Observability

- **Structured Logging:** All nodes log with `structlog` in JSON format
- **Metrics:** Prometheus metrics at `/metrics` — track node latency, retry rates, failures
- **Graph Traces:** LangSmith integration (optional) for visual graph execution traces
- **n8n Dashboard:** Built-in workflow execution history and error logs

---

## 9. Security Considerations

| Risk | Mitigation |
|------|-----------|
| Prompt injection via trend data | Sanitize all external text before LLM input |
| API key exposure | Use Docker secrets / environment injection, never hardcode |
| n8n unauthenticated access | Basic auth + reverse proxy with TLS (nginx + Let's Encrypt) |
| LLM jailbreak via topic | System prompt pinning + output validation regex |
| Redis without auth | Always set `requirepass` in Redis config |

---

## 10. Scalability Roadmap

| Phase | Change | Impact |
|-------|--------|--------|
| Phase 1 (Now) | Single-container, local Ollama | 1 content piece/day |
| Phase 2 | Celery task queue + multiple graph workers | 5-10 pieces/day |
| Phase 3 | Kubernetes deployment + Groq API fallback | 50+ pieces/day |
| Phase 4 | Fine-tuned persona LoRA adapter on LLM | Higher persona fidelity |

---

*End of Report 01 — AI Workflow Orchestration Engine*
