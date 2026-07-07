# ContentPilot — Full Project Report

> **Date:** 2026-06-25
> **Status:** Phase 1 MVP — Complete, tested, ready to configure
> **Stack:** Python 3.11 · LangChain · Gemini API · Tavily · Reddit · HackerNews · FastAPI · GitPython

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [Problem It Solves](#2-problem-it-solves)
3. [How It Works — End to End](#3-how-it-works--end-to-end)
4. [Tech Stack & Rationale](#4-tech-stack--rationale)
5. [Architecture](#5-architecture)
6. [Module Breakdown](#6-module-breakdown)
7. [Data Model](#7-data-model)
8. [Config System](#8-config-system)
9. [Dashboard](#9-dashboard)
10. [Test Suite](#10-test-suite)
11. [Folder Structure](#11-folder-structure)
12. [Setup & Running](#12-setup--running)
13. [What's Pending](#13-whats-pending)
14. [Known Issues & Technical Debt](#14-known-issues--technical-debt)
15. [Key Design Decisions](#15-key-design-decisions)

---

## 1. Project Vision

ContentPilot is a local AI agent that automates the full pipeline of content creation for any static site — from trend discovery to published post. It was purpose-built for **Outflo** (an AI prompt & workflow platform on Next.js + Markdown + Vercel) but is site-agnostic by design.

The agent:
- Discovers what's trending in AI, GenZ, photography, or any topic
- Generates AI prompt posts and workflow posts as markdown files
- Creates matching images via Gemini Imagen
- Commits and pushes the content to the site's git repo
- Vercel (or any CI/CD) picks up the push and deploys automatically

The builder interacts with a short CLI session; the rest is automatic.

---

## 2. Problem It Solves

Outflo (and any content-driven static site) needs regular, high-quality posts to stay relevant and drive SEO traffic. The manual workflow — research trends, write prompts, generate images, format markdown, push to git — is slow and repetitive.

ContentPilot collapses this into a single command:

```
python main.py
→ How many topics today? 3
→ Prompts per topic: 2
→ Workflows per topic: 1
→ Categories: generative-ai, photography
[generates 9 posts, commits, pushes — site live in ~60 seconds]
```

---

## 3. How It Works — End to End

```
User runs: python main.py

CLI asks:
  → N trending topics
  → M prompts per topic (each gets an image)
  → K workflows per topic
  → Categories to search (generative-ai / genz / photography / all)

For each topic:
  1. TrendDiscovery  → fetches topics from Tavily + Reddit + HackerNews
  2. ContentGenerator → generates M prompt markdowns via Gemini (LangChain)
  3. ImageGenerator   → generates M images via Gemini Imagen, saves to repo
  4. ContentGenerator → generates K workflow markdowns via Gemini
  5. GitPublisher     → writes all files to target repo, git commit
  6. Manifest         → records each post with status="pushed"

After all topics:
  GitPublisher.push() → pushes to remote (git origin)

Vercel detects push → rebuilds → site live with new content

Dashboard (separate terminal):
  python dashboard/server.py → http://localhost:8000
  View all posts, delete, re-push
```

---

## 4. Tech Stack & Rationale

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Best ecosystem for AI/ML tooling |
| LLM orchestration | LangChain + `langchain-google-genai` | Model-agnostic abstraction — swap Gemini for Claude/GPT in one config line |
| Text generation | Gemini 2.0 Flash | Fast, cost-effective, good instruction following |
| Image generation | Gemini Imagen 3 | Same API key as text — no separate account needed |
| Trend discovery | Tavily API | Purpose-built for AI agent web search; structured JSON results |
| Community pulse | Reddit API (praw) + HackerNews API | Real-time signal from AI/GenZ communities |
| Git operations | GitPython | Programmatic commit/push without subprocess shell calls |
| CLI | Typer + Rich | Clean interactive prompts with colored output |
| Dashboard | FastAPI + Jinja2 | Lightweight local web UI, no JS framework overhead |
| Config | Pydantic v2 + PyYAML | Type-validated config with clear error messages |
| Env vars | python-dotenv | Standard `.env` pattern, never hardcoded keys |
| Tests | pytest + pytest-mock + pytest-asyncio | Full TDD, async dashboard tests, mock external APIs |
| Concurrency safety | filelock | Prevents manifest corruption from concurrent dashboard requests |

### Why Not Inside Outflo?

ContentPilot is a **separate repo** pointing at Outflo via `config.yaml`. This means:
- It works with any static site (Gatsby, Hugo, Astro) by changing one config line
- The agent doesn't pollute the Outflo codebase
- It can be used independently of Outflo's frontend development

---

## 5. Architecture

### Pattern: Orchestrator + Pluggable Sub-Agents

```
User
  └── CLI (typer + rich)
        └── Orchestrator
              ├── TrendDiscovery   → Tavily + Reddit + HackerNews
              ├── ContentGenerator → LangChain + Gemini (text)
              ├── ImageGenerator   → Gemini Imagen
              └── GitPublisher     → GitPython → target repo → git push

manifest.json  ← written by Orchestrator (tracks all posts)

Dashboard (separate process)
  └── FastAPI + Jinja2 → localhost:8000
        ├── reads manifest.json
        └── calls GitPublisher for delete/re-push
```

### Key Principle

Every agent has a standard `run()` interface with explicit typed parameters. The Orchestrator calls them in sequence per topic. Swapping providers means replacing one class — nothing else changes.

### Error Handling Strategy

- **Per-post failures** (API timeout, rate limit, generation error): the post is skipped, logged to stderr, and the batch continues. The manifest records `status="failed"` for that post.
- **Image failures** within a prompt post: the post is still published without an image. The image field remains empty in the frontmatter.
- **Git push failures** (no remote, network error): the commits are local, the error is logged to stderr, and the run completes. Content is not lost.

---

## 6. Module Breakdown

### `core/models.py` — Shared Data Models

```python
TopicResult(title, summary, source, category, url)
# source: Literal["tavily", "reddit", "hackernews"]

PostEntry(slug, title, type, category, topic, status,
          created_at, file_path, image_path, source_url, git_commit)
# type: Literal["prompt", "workflow"]
# status: Literal["pending", "pushed", "deleted", "failed"]

ManifestState(posts: list[PostEntry])
```

### `core/config.py` — Config Loader

Loads `config.yaml` using Pydantic. Exposes `get_config(path="config.yaml") -> Config`. Raises `FileNotFoundError` for missing file. Nested models: `ContentPathsConfig`, `LLMConfig`, `RedditConfig`, `SourcesConfig`, `DashboardConfig`.

### `core/manifest.py` — Manifest Manager

Read/write `manifest.json`. Thread-safe via `filelock`. All functions accept an optional `path` argument (defaults to `"manifest.json"`) for test isolation.

Functions: `load_manifest`, `save_manifest`, `append_post`, `update_post`, `delete_post`.

### `agents/trend_discovery.py` — TrendDiscovery

```python
TrendDiscovery(config).run(categories: list[str], n_topics: int) -> list[TopicResult]
```

- Queries Tavily with a structured search query per category
- Fetches hot posts from each configured subreddit via Reddit API
- Fetches top HackerNews stories via public Firebase API
- Deduplicates by title, returns `n_topics` results
- Failures per-source logged to stderr, don't kill the batch

### `agents/content_generator.py` — ContentGenerator

```python
ContentGenerator(config).run(topic: TopicResult, post_type: Literal["prompt", "workflow"]) -> tuple[str, str]
# Returns (slug, markdown_content)
```

Uses LangChain `ChatGoogleGenerativeAI` with carefully crafted prompt templates. Prompt posts include YAML frontmatter. Workflow posts use `##` H2 headings as step delimiters (matches Outflo's parser). Slugs are kebab-case, max 60 chars.

### `agents/image_generator.py` — ImageGenerator

```python
ImageGenerator(config).run(topic_title: str, slug: str, target_repo: str) -> str
# Returns relative image path e.g. "public/images/my-slug.png"
```

Calls Gemini Imagen API, saves PNG bytes to `target_repo/content_paths.images/slug.png`. Creates parent directories if missing.

### `agents/git_publisher.py` — GitPublisher

```python
GitPublisher(config).publish(slug, content, post_type) -> str  # commit sha
GitPublisher(config).delete(slug, post_type) -> str
GitPublisher(config).repush(slug, content, post_type) -> str
GitPublisher(config).push() -> None  # safe — logs warning if no remote
```

Uses `git.Repo(target_repo)` from GitPython. `push()` handles missing remote gracefully.

### `agents/orchestrator.py` — Orchestrator

```python
Orchestrator(config_path="config.yaml", manifest_path="manifest.json").run(
    n_topics, n_prompts, n_workflows, categories
) -> None
```

Coordinates all four agents. Per-post try/except: failures are logged and marked in manifest, the batch continues.

### `main.py` — CLI Entry Point

Interactive typer + rich CLI. Asks 4 questions, instantiates `Orchestrator`, calls `run()`.

### `dashboard/server.py` — Dashboard

FastAPI app. Config loaded once at module startup. Routes:

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Post grid — all non-deleted posts |
| `/post/{slug}` | GET | Post detail — 404 if missing |
| `/api/delete/{slug}` | DELETE | Remove file from repo, commit, push, delete from manifest |
| `/api/repush/{slug}` | POST | Re-write file, commit, push |

---

## 7. Data Model

### `manifest.json` — Post Tracking

```json
{
  "posts": [
    {
      "slug": "email-marketing-copywriter",
      "title": "Email Marketing Copywriter",
      "type": "prompt",
      "category": "generative-ai",
      "topic": "AI email automation trends 2026",
      "status": "pushed",
      "created_at": "2026-06-25T14:32:00Z",
      "file_path": "content/prompts/email-marketing-copywriter.md",
      "image_path": "public/images/email-marketing-copywriter.png",
      "source_url": "https://reddit.com/r/MachineLearning/...",
      "git_commit": "a3f9d12"
    }
  ]
}
```

### Prompt Markdown Format

```markdown
---
title: "Email Marketing Copywriter"
description: "Generate high-converting email campaigns using AI"
image: "/public/images/email-marketing-copywriter.png"
tags: ["Marketing", "Email", "AI"]
created_at: "2026-06-25"
---

[AI prompt body — 150-300 words, directly usable in ChatGPT/Claude/Gemini]
```

### Workflow Markdown Format

```markdown
---
title: "Content Creation Pipeline"
description: "5-step AI workflow from idea to published post"
tags: ["Content", "Workflow", "AI"]
created_at: "2026-06-25"
---

## Step 1: Research & Ideation
[AI prompt for this step]

## Step 2: Outline
[AI prompt]

## Step 3: First Draft
[AI prompt]
```

---

## 8. Config System

`config.yaml` (copy from `config.yaml.example`):

```yaml
target_repo: /path/to/outflo        # any local git repo

content_paths:
  prompts: content/prompts           # relative to target_repo
  workflows: content/workflows
  images: public/images

llm:
  provider: google                   # google | openai | anthropic
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

`.env` (copy from `.env.example`):

```env
GEMINI_API_KEY=
TAVILY_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=contentpilot/1.0
```

---

## 9. Dashboard

FastAPI + Jinja2 local web app at `http://localhost:8000`.

**Views:**
- **`/`** — Dark-themed post grid. Each card shows title, type badge (prompt/workflow), status badge (pushed/failed/deleted), category, date, and thumbnail if available.
- **`/post/{slug}`** — Full post detail. Shows all metadata, image preview, source URL, commit sha. Delete and Re-push buttons with JS confirmation.

**API:**
- `DELETE /api/delete/{slug}` — removes file from repo, commits, pushes, removes from manifest
- `POST /api/repush/{slug}` — re-reads file from disk, commits, pushes

**Design:** dark background (`#0f0f0f`), yellow accent (`#facc15`), minimal — no JS framework.

---

## 10. Test Suite

```
38 tests — 0 failing
```

| File | Tests | What's tested |
|---|---|---|
| `tests/core/test_models.py` | 6 | Pydantic validation, Literal enforcement, optional fields |
| `tests/core/test_config.py` | 6 | YAML loading, nested models, FileNotFoundError on missing file |
| `tests/core/test_manifest.py` | 6 | Append, roundtrip, update status + commit, delete, no-op on missing slug |
| `tests/agents/test_trend_discovery.py` | 3 | TopicResult shape, deduplication, n_topics limit |
| `tests/agents/test_content_generator.py` | 3 | Prompt frontmatter, workflow ## steps, kebab slug generation |
| `tests/agents/test_image_generator.py` | 2 | PNG saved to correct path, image directory auto-created |
| `tests/agents/test_git_publisher.py` | 4 | Real temp git repo — publish, delete, repush verified by file existence |
| `tests/agents/test_orchestrator.py` | 2 | Correct post count, status="pushed" with git_commit in manifest |
| `tests/test_main.py` | 2 | CLI args correctly passed to Orchestrator.run() |
| `tests/dashboard/test_server.py` | 4 | GET 200 with content, detail 200, 404 on missing, delete JSON response |

**Testing approach:** All external APIs (Gemini, Tavily, Reddit, HackerNews) are mocked at the module level using `pytest-mock`. GitPublisher tests use a real `git.Repo.init(tmp_path)` — actual file writes and commits. Dashboard tests use `httpx.AsyncClient` with `ASGITransport`.

---

## 11. Folder Structure

```
contentpilot/
├── main.py                        ← CLI entry point
├── config.yaml.example            ← copy to config.yaml
├── manifest.json                  ← auto-generated (gitignored)
├── requirements.txt
├── .env.example                   ← copy to .env
├── .gitignore
├── pytest.ini
├── README.md
├── PROGRESS_TRACKER.md            ← this project's status
│
├── agents/
│   ├── orchestrator.py            ← coordinates all modules
│   ├── trend_discovery.py         ← Tavily + Reddit + HN
│   ├── content_generator.py       ← LangChain + Gemini text
│   ├── image_generator.py         ← Gemini Imagen
│   └── git_publisher.py           ← GitPython operations
│
├── core/
│   ├── config.py                  ← loads + validates config.yaml
│   ├── manifest.py                ← read/write manifest.json
│   └── models.py                  ← shared Pydantic data models
│
├── dashboard/
│   ├── server.py                  ← FastAPI app
│   └── templates/
│       ├── base.html
│       ├── index.html             ← post grid
│       └── post.html              ← single post detail
│
├── tests/
│   ├── core/
│   │   ├── test_models.py
│   │   ├── test_config.py
│   │   └── test_manifest.py
│   ├── agents/
│   │   ├── test_trend_discovery.py
│   │   ├── test_content_generator.py
│   │   ├── test_image_generator.py
│   │   ├── test_git_publisher.py
│   │   └── test_orchestrator.py
│   ├── dashboard/
│   │   └── test_server.py
│   ├── fixtures/
│   │   └── config_valid.yaml
│   └── test_main.py
│
└── docs/
    ├── CONTENTPILOT_FULL_REPORT.md       ← this file
    └── superpowers/
        ├── specs/
        │   └── 2026-06-25-contentpilot-design.md
        └── plans/
            └── 2026-06-25-contentpilot-implementation.md
```

---

## 12. Setup & Running

### Prerequisites

- Python 3.11+
- A local clone of Outflo (or any Markdown-based static site with a git remote)
- API keys: Gemini, Tavily, Reddit app credentials

### Install

```bash
cd my_learning_projects/contentpilot
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```bash
cp config.yaml.example config.yaml
# Edit config.yaml: set target_repo to your Outflo local path

cp .env.example .env
# Edit .env: add GEMINI_API_KEY, TAVILY_API_KEY, REDDIT_* credentials
```

### Run the Agent

```bash
python main.py
```

Output:
```
╭─────────────────────────────────────╮
│  ContentPilot — AI Content Agent    │
╰─────────────────────────────────────╯

How many trending topics today? 3
Prompts per topic (with image): 2
Workflows per topic: 1
Categories (generative-ai, genz, photography, or all): all

Fetching 3 trending topics...
[generates 9 posts, commits, pushes]
✓ Done! Check your dashboard: http://localhost:8000
```

### Run the Dashboard

```bash
# In a separate terminal
python dashboard/server.py
```

Open `http://localhost:8000` in your browser.

### Run Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

---

## 13. What's Pending

### Immediate (Phase 2)

**Hermes Integration**
- Wrap `main.py` as a Hermes skill so ContentPilot can be invoked conversationally from the Hermes TUI
- **Blocker:** Hermes setup not complete — needs API keys + `docker compose run --rm hermes setup` (see `personal_os/STATUS_TRACKER.md`)

**Outflo Frontend**
- Outflo's frontend was built before ContentPilot — UI not yet adapted to leverage agent-generated content patterns
- Dashboard design improvements (bulk delete, category filter, re-run agent from UI)

### Phase 3

**Workflow Pipeline Generator**
- A dedicated sub-agent that generates multi-step AI workflow chains from a business goal input
- E.g. "Build a lead generation workflow for SaaS" → structured 6-step workflow
- Needs its own brainstorming + spec session

**Multi-Site Adapter**
- Abstract `GitPublisher` content paths to support Gatsby, Hugo, Astro, Jekyll conventions
- Plugin-style adapters: `outflo`, `hugo`, `gatsby`, `custom`
- Config flag: `site_type: outflo`

**Dashboard Auth**
- Currently open with no authentication — local use only
- Add simple token or basic auth before any non-local deployment

---

## 14. Known Issues & Technical Debt

| Priority | Issue | Location | Fix |
|---|---|---|---|
| Medium | `google.generativeai` SDK deprecated, emits FutureWarning | `agents/image_generator.py` | Migrate to `google.genai` natively; update test patch target |
| Low | Test files use `datetime.utcnow()` (deprecated) | `tests/core/test_models.py`, `tests/core/test_manifest.py`, `tests/dashboard/test_server.py` | Replace with `datetime.now(UTC)` |
| Low | `post.html` truncates URLs to 60 chars and adds `"..."` unconditionally | `dashboard/templates/post.html` | Only truncate if `len(url) > 60` |
| Low | `requirements.txt` lists `httpx` twice | `requirements.txt` | Deduplicate |
| Low | `push()` not asserted in orchestrator test | `tests/agents/test_orchestrator.py` | Add `GitPublisher.push.assert_called_once()` |

---

## 15. Key Design Decisions

| Decision | Why |
|---|---|
| Separate repo (not inside Outflo) | Site-agnostic from day 1. Points at any git repo via config. |
| Orchestrator + pluggable agents | Standard `run()` interface per agent. Swap providers by swapping the class. |
| LangChain abstraction | Change from Gemini to Claude/GPT = one line in `config.yaml`. |
| Markdown output | Matches Outflo's existing format exactly. No frontend changes needed. |
| Git commit (not API/webhook) | Vercel deploys automatically on push. Zero extra infrastructure. |
| manifest.json for tracking | Decoupled from the target site. Dashboard reads it independently. |
| filelock on manifest | Prevents corruption from concurrent FastAPI delete/repush requests. |
| Per-post error handling | A failed image generation doesn't kill 9 other posts. |
| Real git repo in tests | GitPublisher tests catch real integration bugs that mocks would miss. |

---

*Report generated: 2026-06-25*
