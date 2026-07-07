# ContentPilot — Design Spec

> **Date:** 2026-06-25
> **Status:** Approved — ready for implementation planning
> **Scope:** Phase 1 (standalone local tool + dashboard). Phase 2 (Hermes integration) and Phase 3 (workflow pipeline generator + multi-site) are noted but out of scope for this spec.

---

## 1. Problem Statement

Outflo (and similar content-driven static sites) require regular, high-quality posts to stay relevant and drive traffic. Manually researching trends, writing prompts, generating images, and pushing content is slow. ContentPilot automates this end-to-end: discover trending topics → generate content → push to git → site updates automatically via Vercel CI/CD.

---

## 2. Goals

- Let a user specify how many trending topics and posts per topic they want in one short CLI session
- Generate prompt posts (markdown + image) and workflow posts (multi-step markdown) per topic
- Push generated content directly into the target site's git repo
- Provide a local web dashboard to view, delete, and re-push posts
- Be model-agnostic — swap LLM providers via config, not code
- Be site-agnostic — point at any static site repo via `config.yaml`

### Out of Scope (Phase 1)

- Workflow pipeline generator (Phase 3)
- Hermes skill integration (Phase 2)
- Multi-site SaaS / hosted version (Phase 3)
- User authentication on dashboard
- Scheduled / cron-based runs

---

## 3. Architecture

### Pattern: Orchestrator + Pluggable Sub-Agents

A central `Orchestrator` coordinates four independent modules. Each module has a standard interface (`run(**kwargs) -> result`). Swapping providers or sources means replacing a module class, nothing else.

```
User
  └── CLI (typer + rich)
        └── Orchestrator
              ├── TrendDiscovery   → Tavily API + Reddit API + HackerNews API
              ├── ContentGenerator → LangChain + Gemini (text)
              ├── ImageGenerator   → Gemini Imagen API
              └── GitPublisher     → GitPython → target repo → git push

manifest.json  ← written by Orchestrator after each run (tracks all posts)

Dashboard (separate process)
  └── FastAPI + Jinja2 → localhost:8000
        ├── reads manifest.json
        └── calls GitPublisher for delete / re-push actions
```

### Key Principle

Server Components (Orchestrator, Dashboard) never know which LLM or which site they're talking to — that's fully determined by `config.yaml` and the module implementations.

---

## 4. Module Breakdown

### 4.1 TrendDiscovery

**Job:** Return a ranked list of trending topic objects for a given category.

**Sources:**
- **Tavily API** — broad web search for trending content in AI/GenZ/photography/etc.
- **Reddit API** — top posts from configurable subreddits (e.g. r/MachineLearning, r/ChatGPT, r/GenZ, r/photography)
- **HackerNews API** — top/new stories filtered by keyword relevance

**Output per topic:**
```python
{
  "title": str,
  "summary": str,
  "source": str,       # "tavily" | "reddit" | "hackernews"
  "category": str,     # "generative-ai" | "genz" | "photography" | etc.
  "url": str
}
```

**Dependencies:** `tavily-python`, `httpx`, `praw` (Reddit)

---

### 4.2 ContentGenerator

**Job:** Given a topic object, generate either a prompt post or a workflow post as a markdown string with YAML frontmatter.

**Prompt post output (markdown):**
```markdown
---
title: "..."
description: "..."
image: "/images/slug.png"
tags: ["...", "..."]
created_at: "YYYY-MM-DD"
---

[Prompt body]
```

**Workflow post output (markdown):**
```markdown
---
title: "..."
description: "..."
tags: ["...", "..."]
created_at: "YYYY-MM-DD"
---

## Step 1: ...
[content]

## Step 2: ...
[content]
```

Uses `##` H2 headings as step delimiters (matches Outflo's existing workflow parser).

**Dependencies:** `langchain`, `langchain-google-genai`, `langchain-core`

---

### 4.3 ImageGenerator

**Job:** Given a topic title and prompt slug, generate an image via Gemini Imagen and save it to the target repo's image directory.

**Output:** Relative image path (e.g. `public/images/email-marketing-copy.png`) written into the prompt post's frontmatter.

**Dependencies:** `google-generativeai`

---

### 4.4 GitPublisher

**Job:** Write markdown files to the correct paths in the target repo, stage, commit, and push.

**Operations:**
- `publish(post)` — write file, stage, commit, push
- `delete(slug, post_type)` — remove file, commit, push
- `repush(slug)` — re-write file from manifest, commit, push

Reads `target_repo`, `content_paths` from config. Uses `gitpython`.

**Dependencies:** `gitpython`

---

### 4.5 Orchestrator

**Job:** Entry point. Reads config, runs CLI session, coordinates modules in sequence per topic, writes `manifest.json`.

**CLI flow:**
```
$ python main.py

> How many trending topics would you like today? 3
> Posts per topic:
    Prompts (with image): 2
    Workflows: 1
> Categories to search [generative-ai, genz, photography, all]: all

[Fetching trends...]
[Generating content for "Topic 1"...]
  ✓ Prompt: email-marketing-copy.md
  ✓ Prompt: seo-content-strategy.md
  ✓ Workflow: content-creation-pipeline.md
[Pushing to git...]
  ✓ Committed and pushed (3 files)

[2/3 topics complete...]
```

**Dependencies:** `typer`, `rich`

---

### 4.6 Core Utilities (`core/`)

**Job:** Shared infrastructure used by all agents and the dashboard.

- `config.py` — loads and validates `config.yaml` using Pydantic; exposes a single `get_config()` singleton
- `manifest.py` — read/write `manifest.json`; thread-safe append, update, delete operations
- `models.py` — shared Pydantic models (`TopicResult`, `PostEntry`, `ManifestState`) used across all modules

No business logic lives here — only data shapes and I/O.

---

### 4.7 Dashboard

**Job:** Local web UI to view, delete, and re-push generated posts.

**Routes:**

| Route | Method | Description |
|---|---|---|
| `/` | GET | Grid of all posts — title, type, category, status, thumbnail |
| `/post/{slug}` | GET | Full post preview |
| `/api/delete/{slug}` | DELETE | Remove file from repo, commit, push, update manifest |
| `/api/repush/{slug}` | POST | Re-push a specific post via GitPublisher |

**Tech:** FastAPI + Jinja2 templates (no JS framework). Reads `manifest.json` for state.

**Dependencies:** `fastapi`, `uvicorn`, `jinja2`, `python-multipart`

---

## 5. Data Flow

```
1. User runs `python main.py`
2. CLI collects: N topics, M prompts per topic, K workflows per topic, categories
3. TrendDiscovery fetches top N topics from Tavily + Reddit + HN
4. For each topic:
   a. ContentGenerator generates M prompt markdowns
   b. ImageGenerator generates M images (one per prompt)
   c. ContentGenerator generates K workflow markdowns
   d. GitPublisher writes all files to target repo paths
   e. GitPublisher commits + pushes
   f. Orchestrator appends entries to manifest.json
5. Vercel detects push → rebuilds → site live with new content

Dashboard (separate terminal):
  python dashboard/server.py → localhost:8000
  Reads manifest.json → shows all posts
  Delete → GitPublisher.delete() → commit + push → manifest updated
  Re-push → GitPublisher.repush() → commit + push
```

---

## 6. Config System

**File:** `config.yaml` at project root

```yaml
target_repo: /path/to/outflo          # absolute path to any local git repo
content_paths:
  prompts: content/prompts             # relative to target_repo
  workflows: content/workflows
  images: public/images

llm:
  provider: google                     # google | openai | anthropic
  model: gemini-2.0-flash
  image_model: imagen-3.0-generate-001

sources:
  tavily: true
  reddit:
    enabled: true
    subreddits:
      - MachineLearning
      - artificial
      - ChatGPT
      - GenZ
      - photography
  hackernews:
    enabled: true

dashboard:
  port: 8000
```

API keys live in `.env` (gitignored):

```env
GEMINI_API_KEY=...
TAVILY_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=contentpilot/1.0
```

---

## 7. Folder Structure

```
my_learning_projects/contentpilot/
│
├── main.py                        ← CLI entry point
├── config.yaml                    ← site + model config (user edits this)
├── manifest.json                  ← auto-generated post tracking state
├── requirements.txt
├── .env                           ← API keys (gitignored)
├── .gitignore
├── README.md
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py            ← coordinates all modules
│   ├── trend_discovery.py         ← Tavily + Reddit + HN
│   ├── content_generator.py       ← LangChain + Gemini text
│   ├── image_generator.py         ← Gemini Imagen
│   └── git_publisher.py           ← GitPython operations
│
├── dashboard/
│   ├── __init__.py
│   ├── server.py                  ← FastAPI app
│   └── templates/
│       ├── base.html
│       ├── index.html             ← post grid
│       └── post.html              ← single post view
│
├── core/
│   ├── __init__.py
│   ├── config.py                  ← loads + validates config.yaml
│   ├── manifest.py                ← read/write manifest.json
│   └── models.py                  ← shared Pydantic data models
│
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-06-25-contentpilot-design.md
```

---

## 8. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| CLI | `typer` + `rich` | User interaction, progress display |
| LLM orchestration | `langchain` + `langchain-google-genai` | Model-agnostic text generation |
| Image generation | `google-generativeai` | Gemini Imagen API |
| Trend discovery | `tavily-python` + `httpx` + `praw` | Web + community trends |
| Git operations | `gitpython` | Commit + push to target repo |
| Dashboard backend | `fastapi` + `uvicorn` | Local web API |
| Dashboard frontend | `jinja2` templates | Simple HTML, no JS framework |
| Config | `pyyaml` + `pydantic` | Config loading + validation |
| Env vars | `python-dotenv` | API key management |

---

## 9. Manifest Schema

`manifest.json` tracks every generated post:

```json
{
  "posts": [
    {
      "slug": "email-marketing-copy",
      "title": "Email Marketing Copywriter",
      "type": "prompt",
      "category": "generative-ai",
      "topic": "AI email automation trends 2026",
      "status": "pushed",
      "created_at": "2026-06-25T14:32:00Z",
      "file_path": "content/prompts/email-marketing-copy.md",
      "image_path": "public/images/email-marketing-copy.png",
      "source_url": "https://reddit.com/r/MachineLearning/...",
      "git_commit": "a3f9d12"
    }
  ]
}
```

**Status values:** `pending` | `pushed` | `deleted` | `failed`

---

## 10. Future Phases (Out of Scope Now)

### Phase 2 — Hermes Integration
Wrap `main.py` as a Hermes skill. The Hermes TUI can invoke ContentPilot runs conversationally. Requires Hermes to be fully configured (API keys + setup wizard complete).

### Phase 3 — Workflow Pipeline Generator
A dedicated sub-agent that generates structured multi-step AI workflow chains based on a business goal (e.g. "build a lead generation workflow for SaaS"). Discussed separately.

### Phase 3 — Multi-Site Adapter
Abstract the `GitPublisher` and `config.yaml` further so ContentPilot can target any static site (Gatsby, Hugo, Astro, etc.) with different content path conventions. Plugin-style adapters per site type.

---

## 11. Running the Tool

```bash
# Install
cd my_learning_projects/contentpilot
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml    # edit target_repo path
cp .env.example .env                  # add API keys

# Run agent
python main.py

# Run dashboard (separate terminal)
python dashboard/server.py
# → open http://localhost:8000
```
