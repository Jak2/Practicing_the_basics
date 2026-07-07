# ContentPilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local CLI agent that discovers trending topics, generates AI prompt + workflow markdown posts via Gemini, and pushes them to any static site's git repo — with a FastAPI dashboard to manage published posts.

**Architecture:** Orchestrator + pluggable sub-agents pattern. A central `Orchestrator` coordinates four independent modules (`TrendDiscovery`, `ContentGenerator`, `ImageGenerator`, `GitPublisher`) each with a standard `run()` interface. Config and manifest are shared via a `core/` utilities layer. Dashboard is a separate FastAPI process reading `manifest.json`.

**Tech Stack:** Python 3.11+, LangChain + `langchain-google-genai`, `google-generativeai` (Imagen), `tavily-python`, `praw`, `gitpython`, `typer`, `rich`, `fastapi`, `uvicorn`, `jinja2`, `pydantic`, `pyyaml`, `python-dotenv`, `pytest`

## Global Constraints

- Python 3.11+ required (uses `str | None` union syntax)
- All imports are absolute from project root (`from core.config import ...`, `from agents.trend_discovery import ...`)
- Run all commands from `my_learning_projects/contentpilot/` (project root)
- All agent classes accept `config: Config` as their only constructor argument
- All agent `run()` methods have explicit typed signatures — no `**kwargs`
- API keys only from `.env` via `python-dotenv` — never hardcoded
- `manifest.json` and `config.yaml` are gitignored — never committed
- Pydantic v2 syntax throughout (`model_validate`, `model_dump_json`, not v1 `.dict()`)
- Tests use `pytest` with `pytest-mock` for patching external APIs

---

## File Map

| File | Responsibility |
|---|---|
| `core/models.py` | Shared Pydantic data models (`TopicResult`, `PostEntry`, `ManifestState`) |
| `core/config.py` | Loads + validates `config.yaml`; exposes `get_config()` |
| `core/manifest.py` | Read/write `manifest.json`; append, update, delete operations |
| `agents/trend_discovery.py` | Fetches trending topics from Tavily + Reddit + HackerNews |
| `agents/content_generator.py` | Generates prompt/workflow markdown via LangChain + Gemini |
| `agents/image_generator.py` | Generates images via Gemini Imagen, saves to target repo |
| `agents/git_publisher.py` | Writes files, commits, pushes to target repo via GitPython |
| `agents/orchestrator.py` | Coordinates all agents per topic, writes to manifest |
| `main.py` | CLI entry point (typer + rich interactive prompts) |
| `dashboard/server.py` | FastAPI app — serves post grid, handles delete/repush |
| `dashboard/templates/base.html` | Base HTML layout with nav |
| `dashboard/templates/index.html` | Post grid view |
| `dashboard/templates/post.html` | Single post detail + delete/repush buttons |
| `tests/core/test_models.py` | Unit tests for Pydantic models |
| `tests/core/test_config.py` | Unit tests for config loader |
| `tests/core/test_manifest.py` | Unit tests for manifest operations |
| `tests/agents/test_trend_discovery.py` | Unit tests with mocked Tavily/Reddit/HN |
| `tests/agents/test_content_generator.py` | Unit tests with mocked LangChain |
| `tests/agents/test_image_generator.py` | Unit tests with mocked Gemini |
| `tests/agents/test_git_publisher.py` | Unit tests with a real temp git repo |
| `tests/agents/test_orchestrator.py` | Integration test with all agents mocked |
| `tests/dashboard/test_server.py` | FastAPI test client tests |

---

## Task 1: Project Bootstrap

**Files:**
- Create: `tests/__init__.py`, `tests/core/__init__.py`, `tests/agents/__init__.py`, `tests/dashboard/__init__.py`
- Create: `pytest.ini`
- Modify: `requirements.txt` (add test deps)

**Interfaces:**
- Produces: working `pytest` setup, virtualenv with all deps installed

- [ ] **Step 1: Create and activate virtual environment**

```bash
cd my_learning_projects/contentpilot
python3 -m venv .venv
source .venv/bin/activate
```

- [ ] **Step 2: Add test dependencies to requirements.txt**

Append to `requirements.txt`:
```
# Testing
pytest>=8.0
pytest-mock>=3.14
pytest-asyncio>=0.24
httpx>=0.27       # already listed above — needed for async FastAPI test client
```

- [ ] **Step 3: Install all dependencies**

```bash
pip install -r requirements.txt
```

Expected: no errors, all packages installed.

- [ ] **Step 4: Create pytest.ini**

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

- [ ] **Step 5: Create test package structure**

```bash
mkdir -p tests/core tests/agents tests/dashboard
touch tests/__init__.py tests/core/__init__.py tests/agents/__init__.py tests/dashboard/__init__.py
```

- [ ] **Step 6: Create .env from example**

```bash
cp .env.example .env
```

Leave values blank for now — tests will mock all external calls.

- [ ] **Step 7: Verify pytest discovers tests (empty suite)**

```bash
pytest --collect-only
```

Expected output: `no tests ran` (no errors).

- [ ] **Step 8: Commit**

```bash
git add requirements.txt pytest.ini tests/
git commit -m "chore: project bootstrap — venv, pytest, test structure"
```

---

## Task 2: Core Data Models

**Files:**
- Modify: `core/models.py`
- Create: `tests/core/test_models.py`

**Interfaces:**
- Produces:
  - `TopicResult(title, summary, source, category, url)` — Pydantic model
  - `PostEntry(slug, title, type, category, topic, status, created_at, file_path, image_path, source_url, git_commit)` — Pydantic model
  - `ManifestState(posts: list[PostEntry])` — Pydantic model

- [ ] **Step 1: Write failing tests**

`tests/core/test_models.py`:
```python
import pytest
from datetime import datetime
from core.models import TopicResult, PostEntry, ManifestState


def test_topic_result_valid():
    t = TopicResult(
        title="GPT-5 release",
        summary="OpenAI releases GPT-5",
        source="tavily",
        category="generative-ai",
        url="https://example.com",
    )
    assert t.title == "GPT-5 release"
    assert t.source == "tavily"


def test_topic_result_invalid_source():
    with pytest.raises(Exception):
        TopicResult(
            title="x", summary="x", source="invalid", category="x", url="x"
        )


def test_post_entry_defaults():
    p = PostEntry(
        slug="email-copy",
        title="Email Copy",
        type="prompt",
        category="generative-ai",
        topic="AI email trends",
        status="pending",
        created_at=datetime.utcnow(),
        file_path="content/prompts/email-copy.md",
        source_url="https://reddit.com/r/ai",
    )
    assert p.image_path is None
    assert p.git_commit is None
    assert p.status == "pending"


def test_post_entry_invalid_type():
    with pytest.raises(Exception):
        PostEntry(
            slug="x", title="x", type="invalid", category="x",
            topic="x", status="pending", created_at=datetime.utcnow(),
            file_path="x", source_url="x",
        )


def test_manifest_state_empty():
    m = ManifestState()
    assert m.posts == []


def test_manifest_state_with_posts():
    p = PostEntry(
        slug="s", title="t", type="workflow", category="c",
        topic="tp", status="pushed", created_at=datetime.utcnow(),
        file_path="f", source_url="u",
    )
    m = ManifestState(posts=[p])
    assert len(m.posts) == 1
    assert m.posts[0].slug == "s"
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/core/test_models.py -v
```

Expected: `ImportError: No module named 'core.models'`

- [ ] **Step 3: Implement `core/models.py`**

```python
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class TopicResult(BaseModel):
    title: str
    summary: str
    source: Literal["tavily", "reddit", "hackernews"]
    category: str
    url: str


class PostEntry(BaseModel):
    slug: str
    title: str
    type: Literal["prompt", "workflow"]
    category: str
    topic: str
    status: Literal["pending", "pushed", "deleted", "failed"]
    created_at: datetime
    file_path: str
    image_path: Optional[str] = None
    source_url: str
    git_commit: Optional[str] = None


class ManifestState(BaseModel):
    posts: list[PostEntry] = []
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/core/test_models.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add core/models.py tests/core/test_models.py
git commit -m "feat: core data models (TopicResult, PostEntry, ManifestState)"
```

---

## Task 3: Config Loader

**Files:**
- Modify: `core/config.py`
- Create: `tests/core/test_config.py`
- Create: `tests/fixtures/config_valid.yaml`

**Interfaces:**
- Consumes: `config.yaml` on disk
- Produces: `get_config(path: str) -> Config` — returns validated `Config` Pydantic model with nested sub-models

- [ ] **Step 1: Create test fixture config**

```bash
mkdir -p tests/fixtures
```

`tests/fixtures/config_valid.yaml`:
```yaml
target_repo: /tmp/fake-repo
content_paths:
  prompts: content/prompts
  workflows: content/workflows
  images: public/images
llm:
  provider: google
  model: gemini-2.0-flash
  image_model: imagen-3.0-generate-001
sources:
  tavily: true
  reddit:
    enabled: true
    subreddits:
      - MachineLearning
      - ChatGPT
  hackernews:
    enabled: true
dashboard:
  port: 8000
```

- [ ] **Step 2: Write failing tests**

`tests/core/test_config.py`:
```python
import pytest
from core.config import get_config


FIXTURE = "tests/fixtures/config_valid.yaml"


def test_get_config_loads_target_repo():
    cfg = get_config(FIXTURE)
    assert cfg.target_repo == "/tmp/fake-repo"


def test_get_config_content_paths():
    cfg = get_config(FIXTURE)
    assert cfg.content_paths.prompts == "content/prompts"
    assert cfg.content_paths.workflows == "content/workflows"
    assert cfg.content_paths.images == "public/images"


def test_get_config_llm():
    cfg = get_config(FIXTURE)
    assert cfg.llm.provider == "google"
    assert cfg.llm.model == "gemini-2.0-flash"


def test_get_config_sources_reddit():
    cfg = get_config(FIXTURE)
    assert cfg.sources.reddit.enabled is True
    assert "MachineLearning" in cfg.sources.reddit.subreddits


def test_get_config_dashboard_port():
    cfg = get_config(FIXTURE)
    assert cfg.dashboard.port == 8000


def test_get_config_missing_file():
    with pytest.raises(FileNotFoundError):
        get_config("nonexistent.yaml")
```

- [ ] **Step 3: Run tests — expect failure**

```bash
pytest tests/core/test_config.py -v
```

Expected: `ImportError: cannot import name 'get_config'`

- [ ] **Step 4: Implement `core/config.py`**

```python
import yaml
from pydantic import BaseModel


class ContentPathsConfig(BaseModel):
    prompts: str
    workflows: str
    images: str


class LLMConfig(BaseModel):
    provider: str = "google"
    model: str = "gemini-2.0-flash"
    image_model: str = "imagen-3.0-generate-001"


class RedditConfig(BaseModel):
    enabled: bool = True
    subreddits: list[str] = []


class SourcesConfig(BaseModel):
    tavily: bool = True
    reddit: RedditConfig = RedditConfig()
    hackernews: bool = True


class DashboardConfig(BaseModel):
    port: int = 8000


class Config(BaseModel):
    target_repo: str
    content_paths: ContentPathsConfig
    llm: LLMConfig = LLMConfig()
    sources: SourcesConfig = SourcesConfig()
    dashboard: DashboardConfig = DashboardConfig()


def get_config(path: str = "config.yaml") -> Config:
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    return Config(**data)
```

- [ ] **Step 5: Run tests — expect pass**

```bash
pytest tests/core/test_config.py -v
```

Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add core/config.py tests/core/test_config.py tests/fixtures/config_valid.yaml
git commit -m "feat: config loader with Pydantic validation"
```

---

## Task 4: Manifest Manager

**Files:**
- Modify: `core/manifest.py`
- Create: `tests/core/test_manifest.py`

**Interfaces:**
- Consumes: `core/models.py` — `ManifestState`, `PostEntry`
- Produces:
  - `load_manifest(path: str) -> ManifestState`
  - `save_manifest(state: ManifestState, path: str) -> None`
  - `append_post(post: PostEntry, path: str) -> None`
  - `update_post(slug: str, status: str, git_commit: str | None, path: str) -> None`
  - `delete_post(slug: str, path: str) -> None`

All functions accept an optional `path` argument (default `"manifest.json"`) so tests can use temp files.

- [ ] **Step 1: Write failing tests**

`tests/core/test_manifest.py`:
```python
import json
import pytest
from datetime import datetime
from pathlib import Path
from core.manifest import load_manifest, save_manifest, append_post, update_post, delete_post
from core.models import ManifestState, PostEntry


def make_post(slug: str = "test-slug", post_type: str = "prompt") -> PostEntry:
    return PostEntry(
        slug=slug,
        title="Test Post",
        type=post_type,
        category="generative-ai",
        topic="AI trends",
        status="pending",
        created_at=datetime.utcnow(),
        file_path=f"content/prompts/{slug}.md",
        source_url="https://example.com",
    )


def test_load_manifest_missing_file(tmp_path):
    state = load_manifest(str(tmp_path / "missing.json"))
    assert state.posts == []


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "manifest.json")
    post = make_post()
    state = ManifestState(posts=[post])
    save_manifest(state, path)
    loaded = load_manifest(path)
    assert len(loaded.posts) == 1
    assert loaded.posts[0].slug == "test-slug"


def test_append_post(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("post-1"), path)
    append_post(make_post("post-2"), path)
    state = load_manifest(path)
    assert len(state.posts) == 2
    assert state.posts[1].slug == "post-2"


def test_update_post_status(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("my-post"), path)
    update_post("my-post", "pushed", "abc123", path)
    state = load_manifest(path)
    assert state.posts[0].status == "pushed"
    assert state.posts[0].git_commit == "abc123"


def test_delete_post(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("keep-me"), path)
    append_post(make_post("delete-me"), path)
    delete_post("delete-me", path)
    state = load_manifest(path)
    assert len(state.posts) == 1
    assert state.posts[0].slug == "keep-me"


def test_update_nonexistent_post_is_noop(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("real"), path)
    update_post("ghost", "pushed", None, path)
    state = load_manifest(path)
    assert state.posts[0].status == "pending"
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/core/test_manifest.py -v
```

Expected: `ImportError: cannot import name 'load_manifest'`

- [ ] **Step 3: Implement `core/manifest.py`**

```python
import json
from pathlib import Path
from core.models import ManifestState, PostEntry

DEFAULT_PATH = "manifest.json"


def load_manifest(path: str = DEFAULT_PATH) -> ManifestState:
    p = Path(path)
    if not p.exists():
        return ManifestState()
    return ManifestState.model_validate_json(p.read_text())


def save_manifest(state: ManifestState, path: str = DEFAULT_PATH) -> None:
    Path(path).write_text(state.model_dump_json(indent=2))


def append_post(post: PostEntry, path: str = DEFAULT_PATH) -> None:
    state = load_manifest(path)
    state.posts.append(post)
    save_manifest(state, path)


def update_post(slug: str, status: str, git_commit: str | None = None, path: str = DEFAULT_PATH) -> None:
    state = load_manifest(path)
    for post in state.posts:
        if post.slug == slug:
            post.status = status
            if git_commit:
                post.git_commit = git_commit
    save_manifest(state, path)


def delete_post(slug: str, path: str = DEFAULT_PATH) -> None:
    state = load_manifest(path)
    state.posts = [p for p in state.posts if p.slug != slug]
    save_manifest(state, path)
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/core/test_manifest.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add core/manifest.py tests/core/test_manifest.py
git commit -m "feat: manifest manager (load, save, append, update, delete)"
```

---

## Task 5: TrendDiscovery Agent

**Files:**
- Modify: `agents/trend_discovery.py`
- Create: `tests/agents/test_trend_discovery.py`

**Interfaces:**
- Consumes: `core/config.py` → `Config`; `core/models.py` → `TopicResult`
- Produces: `TrendDiscovery(config: Config).run(categories: list[str], n_topics: int) -> list[TopicResult]`

- [ ] **Step 1: Write failing tests**

`tests/agents/test_trend_discovery.py`:
```python
import pytest
from unittest.mock import MagicMock, patch
from core.config import get_config
from agents.trend_discovery import TrendDiscovery
from core.models import TopicResult

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_config():
    return get_config(FIXTURE)


def test_run_returns_topic_results(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    mocker.patch("agents.trend_discovery.TavilyClient.search", return_value={
        "results": [
            {"title": "Gemini 2.0 is here", "content": "Google releases Gemini 2.0",
             "url": "https://example.com/gemini"}
        ]
    })
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results = agent.run(["generative-ai"], n_topics=1)

    assert len(results) == 1
    assert isinstance(results[0], TopicResult)
    assert results[0].source == "tavily"
    assert results[0].category == "generative-ai"


def test_run_deduplicates_by_title(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    duplicate = TopicResult(title="Same topic", summary="desc", source="reddit",
                             category="generative-ai", url="https://a.com")
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results = agent.run(["generative-ai"], n_topics=5)

    titles = [r.title for r in results]
    assert titles.count("Same topic") == 1


def test_run_respects_n_topics_limit(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    many = [TopicResult(title=f"Topic {i}", summary="s", source="tavily",
                         category="generative-ai", url="https://x.com") for i in range(10)]
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=many)
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results = agent.run(["generative-ai"], n_topics=3)
    assert len(results) == 3
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/agents/test_trend_discovery.py -v
```

Expected: `ImportError: cannot import name 'TrendDiscovery'`

- [ ] **Step 3: Implement `agents/trend_discovery.py`**

```python
import os
import httpx
from tavily import TavilyClient
from core.config import Config
from core.models import TopicResult


class TrendDiscovery:
    def __init__(self, config: Config):
        self.config = config
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))

    def run(self, categories: list[str], n_topics: int) -> list[TopicResult]:
        results: list[TopicResult] = []
        if self.config.sources.tavily:
            results.extend(self._fetch_tavily(categories, n_topics))
        if self.config.sources.reddit.enabled:
            results.extend(self._fetch_reddit(n_topics))
        if self.config.sources.hackernews:
            results.extend(self._fetch_hackernews(n_topics))

        seen: set[str] = set()
        unique: list[TopicResult] = []
        for r in results:
            if r.title not in seen:
                seen.add(r.title)
                unique.append(r)
        return unique[:n_topics]

    def _fetch_tavily(self, categories: list[str], n: int) -> list[TopicResult]:
        query = f"trending topics 2026 {' OR '.join(categories)}"
        response = self.tavily.search(query=query, max_results=n, search_depth="advanced")
        results = []
        for item in response.get("results", []):
            cat = categories[0] if categories and categories[0] != "all" else "general"
            results.append(TopicResult(
                title=item["title"],
                summary=item.get("content", "")[:300],
                source="tavily",
                category=cat,
                url=item["url"],
            ))
        return results

    def _fetch_reddit(self, n: int) -> list[TopicResult]:
        import praw
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "contentpilot/1.0"),
        )
        results = []
        for sub_name in self.config.sources.reddit.subreddits[:3]:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=n):
                    results.append(TopicResult(
                        title=post.title,
                        summary=post.selftext[:300] if post.selftext else post.title,
                        source="reddit",
                        category=sub_name.lower(),
                        url=f"https://reddit.com{post.permalink}",
                    ))
            except Exception:
                continue
        return results

    def _fetch_hackernews(self, n: int) -> list[TopicResult]:
        try:
            resp = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5)
            ids = resp.json()[:n]
            results = []
            for story_id in ids:
                item_resp = httpx.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5
                )
                item = item_resp.json()
                if item and item.get("type") == "story":
                    results.append(TopicResult(
                        title=item.get("title", ""),
                        summary=item.get("title", ""),
                        source="hackernews",
                        category="tech",
                        url=item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    ))
            return results
        except Exception:
            return []
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/agents/test_trend_discovery.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/trend_discovery.py tests/agents/test_trend_discovery.py
git commit -m "feat: TrendDiscovery agent (Tavily + Reddit + HackerNews)"
```

---

## Task 6: ContentGenerator Agent

**Files:**
- Modify: `agents/content_generator.py`
- Create: `tests/agents/test_content_generator.py`

**Interfaces:**
- Consumes: `core/config.py` → `Config`; `core/models.py` → `TopicResult`
- Produces: `ContentGenerator(config: Config).run(topic: TopicResult, post_type: Literal["prompt", "workflow"]) -> tuple[str, str]`
  - Returns `(slug, markdown_content)` where slug is a kebab-case filename-safe string

- [ ] **Step 1: Write failing tests**

`tests/agents/test_content_generator.py`:
```python
import pytest
from unittest.mock import MagicMock
from core.config import get_config
from core.models import TopicResult
from agents.content_generator import ContentGenerator

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_topic():
    return TopicResult(
        title="AI agents are taking over workflows",
        summary="AI agents are replacing repetitive business tasks",
        source="tavily",
        category="generative-ai",
        url="https://example.com",
    )


def test_run_prompt_returns_slug_and_markdown(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\n"
        'title: "AI Workflow Agent"\n'
        'description: "Automate your business workflows with AI"\n'
        'image: ""\n'
        'tags: ["AI", "Automation"]\n'
        'created_at: "2026-06-25"\n'
        "---\n\n"
        "You are an expert AI workflow consultant...\n"
    )
    mocker.patch("agents.content_generator.ChatGoogleGenerativeAI", return_value=mock_llm)

    agent = ContentGenerator(get_config(FIXTURE))
    slug, md = agent.run(make_topic(), "prompt")

    assert slug
    assert "-" in slug or slug.replace("-", "").isalnum()
    assert "---" in md
    assert "title:" in md


def test_run_workflow_contains_steps(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\n"
        'title: "AI Workflow Pipeline"\n'
        'description: "Build an AI workflow in 3 steps"\n'
        'tags: ["AI", "Workflow"]\n'
        'created_at: "2026-06-25"\n'
        "---\n\n"
        "## Step 1: Research\nResearch your topic\n\n"
        "## Step 2: Draft\nWrite a draft\n\n"
        "## Step 3: Publish\nPublish the content\n"
    )
    mocker.patch("agents.content_generator.ChatGoogleGenerativeAI", return_value=mock_llm)

    agent = ContentGenerator(get_config(FIXTURE))
    slug, md = agent.run(make_topic(), "workflow")

    assert "## Step" in md


def test_slug_is_kebab_case(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\ntitle: \"My Test Post\"\ndescription: \"desc\"\n"
        "tags: []\ncreated_at: \"2026-06-25\"\n---\n\nContent\n"
    )
    mocker.patch("agents.content_generator.ChatGoogleGenerativeAI", return_value=mock_llm)
    agent = ContentGenerator(get_config(FIXTURE))
    slug, _ = agent.run(make_topic(), "prompt")
    assert " " not in slug
    assert slug == slug.lower()
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/agents/test_content_generator.py -v
```

Expected: `ImportError: cannot import name 'ContentGenerator'`

- [ ] **Step 3: Implement `agents/content_generator.py`**

```python
import os
import re
from typing import Literal
from datetime import date
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from core.config import Config
from core.models import TopicResult


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


PROMPT_TEMPLATE = """You are a creative AI content strategist.

Topic: {title}
Context: {summary}
Today: {date}

Generate a markdown file for an AI prompt post. Use this EXACT format:

---
title: "a concise, compelling title"
description: "one-sentence description"
image: ""
tags: ["tag1", "tag2", "tag3"]
created_at: "{date}"
---

Write an expert AI prompt here (150-300 words). The prompt should be directly usable in ChatGPT, Claude, or Gemini. Make it outcome-driven and specific to the topic.

Return ONLY the markdown — no commentary before or after."""


WORKFLOW_TEMPLATE = """You are a creative AI content strategist.

Topic: {title}
Context: {summary}
Today: {date}

Generate a markdown file for a multi-step AI workflow post. Use this EXACT format:

---
title: "a concise workflow title"
description: "one-sentence description"
tags: ["tag1", "tag2", "tag3"]
created_at: "{date}"
---

## Step 1: [Step Name]
[Detailed AI prompt for this step, 50-100 words]

## Step 2: [Step Name]
[Detailed AI prompt for this step]

## Step 3: [Step Name]
[Detailed AI prompt for this step]

## Step 4: [Step Name]
[Detailed AI prompt for this step]

Return ONLY the markdown — no commentary before or after. Use exactly ## for step headings."""


class ContentGenerator:
    def __init__(self, config: Config):
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm.model,
            google_api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    def run(self, topic: TopicResult, post_type: Literal["prompt", "workflow"]) -> tuple[str, str]:
        today = date.today().isoformat()
        if post_type == "prompt":
            prompt = PROMPT_TEMPLATE.format(title=topic.title, summary=topic.summary, date=today)
        else:
            prompt = WORKFLOW_TEMPLATE.format(title=topic.title, summary=topic.summary, date=today)

        response = self.llm.invoke([HumanMessage(content=prompt)])
        markdown = response.content.strip()

        title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', markdown)
        if title_match:
            slug = _slugify(title_match.group(1))
        else:
            slug = _slugify(topic.title)

        return slug, markdown
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/agents/test_content_generator.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/content_generator.py tests/agents/test_content_generator.py
git commit -m "feat: ContentGenerator agent (LangChain + Gemini prompt/workflow)"
```

---

## Task 7: ImageGenerator Agent

**Files:**
- Modify: `agents/image_generator.py`
- Create: `tests/agents/test_image_generator.py`

**Interfaces:**
- Consumes: `core/config.py` → `Config`
- Produces: `ImageGenerator(config: Config).run(topic_title: str, slug: str, target_repo: str) -> str`
  - Returns relative image path (e.g. `public/images/my-slug.png`) after saving file to disk

- [ ] **Step 1: Write failing tests**

`tests/agents/test_image_generator.py`:
```python
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from core.config import get_config
from agents.image_generator import ImageGenerator

FIXTURE = "tests/fixtures/config_valid.yaml"


def test_run_saves_image_and_returns_path(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    mock_response = MagicMock()
    mock_response.images = [MagicMock(image_bytes=fake_image_bytes)]
    mocker.patch("agents.image_generator.genai.ImageGenerationModel.from_pretrained",
                 return_value=MagicMock(generate_images=MagicMock(return_value=mock_response)))

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    rel_path = agent.run("AI workflow agents", "ai-workflow-agents", str(tmp_path))

    assert rel_path == "public/images/ai-workflow-agents.png"
    assert (tmp_path / "public" / "images" / "ai-workflow-agents.png").exists()


def test_run_creates_image_dir_if_missing(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50

    mock_response = MagicMock()
    mock_response.images = [MagicMock(image_bytes=fake_bytes)]
    mocker.patch("agents.image_generator.genai.ImageGenerationModel.from_pretrained",
                 return_value=MagicMock(generate_images=MagicMock(return_value=mock_response)))

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    agent.run("test", "test-slug", str(tmp_path))

    assert (tmp_path / "public" / "images").is_dir()
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/agents/test_image_generator.py -v
```

Expected: `ImportError: cannot import name 'ImageGenerator'`

- [ ] **Step 3: Implement `agents/image_generator.py`**

```python
import os
from pathlib import Path
import google.generativeai as genai
from core.config import Config


class ImageGenerator:
    def __init__(self, config: Config):
        self.config = config
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        self.model = genai.ImageGenerationModel.from_pretrained(config.llm.image_model)

    def run(self, topic_title: str, slug: str, target_repo: str) -> str:
        prompt = (
            f"High-quality digital illustration representing: {topic_title}. "
            "Modern, minimal, professional style. No text overlays."
        )
        response = self.model.generate_images(prompt=prompt, number_of_images=1)
        image_bytes = response.images[0].image_bytes

        rel_path = self.config.content_paths.images
        abs_dir = Path(target_repo) / rel_path
        abs_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{slug}.png"
        (abs_dir / filename).write_bytes(image_bytes)

        return f"{rel_path}/{filename}"
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/agents/test_image_generator.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/image_generator.py tests/agents/test_image_generator.py
git commit -m "feat: ImageGenerator agent (Gemini Imagen)"
```

---

## Task 8: GitPublisher Agent

**Files:**
- Modify: `agents/git_publisher.py`
- Create: `tests/agents/test_git_publisher.py`

**Interfaces:**
- Consumes: `core/config.py` → `Config`
- Produces:
  - `GitPublisher(config: Config).publish(slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str` → commit sha
  - `GitPublisher(config: Config).delete(slug: str, post_type: Literal["prompt", "workflow"]) -> str` → commit sha
  - `GitPublisher(config: Config).repush(slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str` → commit sha

- [ ] **Step 1: Write failing tests**

`tests/agents/test_git_publisher.py`:
```python
import pytest
import git
from pathlib import Path
from core.config import get_config, Config
from agents.git_publisher import GitPublisher

FIXTURE = "tests/fixtures/config_valid.yaml"


@pytest.fixture
def git_repo(tmp_path):
    repo = git.Repo.init(tmp_path)
    repo.config_writer().set_value("user", "name", "Test").release()
    repo.config_writer().set_value("user", "email", "test@test.com").release()
    (tmp_path / "content" / "prompts").mkdir(parents=True)
    (tmp_path / "content" / "workflows").mkdir(parents=True)
    (tmp_path / "public" / "images").mkdir(parents=True)
    readme = tmp_path / "README.md"
    readme.write_text("# Test repo")
    repo.index.add(["README.md"])
    repo.index.commit("init")
    return tmp_path, repo


def make_config_for_repo(repo_path: str) -> Config:
    cfg = get_config(FIXTURE)
    cfg.target_repo = repo_path
    return cfg


def test_publish_prompt_creates_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    sha = publisher.publish("my-prompt", "---\ntitle: test\n---\nContent", "prompt")

    assert (repo_path / "content" / "prompts" / "my-prompt.md").exists()
    assert sha
    assert len(sha) >= 7


def test_publish_workflow_creates_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    sha = publisher.publish("my-workflow", "---\ntitle: wf\n---\n## Step 1\ncontent", "workflow")

    assert (repo_path / "content" / "workflows" / "my-workflow.md").exists()


def test_delete_removes_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    publisher.publish("del-me", "---\ntitle: del\n---\ncontent", "prompt")
    assert (repo_path / "content" / "prompts" / "del-me.md").exists()

    publisher.delete("del-me", "prompt")
    assert not (repo_path / "content" / "prompts" / "del-me.md").exists()


def test_repush_overwrites_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    publisher.publish("repush-me", "---\ntitle: old\n---\nOld content", "prompt")
    publisher.repush("repush-me", "---\ntitle: new\n---\nNew content", "prompt")

    content = (repo_path / "content" / "prompts" / "repush-me.md").read_text()
    assert "New content" in content
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/agents/test_git_publisher.py -v
```

Expected: `ImportError: cannot import name 'GitPublisher'`

- [ ] **Step 3: Implement `agents/git_publisher.py`**

```python
from typing import Literal
from pathlib import Path
import git
from core.config import Config


class GitPublisher:
    def __init__(self, config: Config):
        self.config = config
        self.repo = git.Repo(config.target_repo)

    def _path_for(self, slug: str, post_type: Literal["prompt", "workflow"]) -> Path:
        base = Path(self.config.target_repo)
        if post_type == "prompt":
            return base / self.config.content_paths.prompts / f"{slug}.md"
        return base / self.config.content_paths.workflows / f"{slug}.md"

    def publish(self, slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str:
        path = self._path_for(slug, post_type)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.repo.index.add([str(path.relative_to(self.config.target_repo))])
        commit = self.repo.index.commit(f"content: add {post_type} '{slug}'")
        return commit.hexsha[:7]

    def delete(self, slug: str, post_type: Literal["prompt", "workflow"]) -> str:
        path = self._path_for(slug, post_type)
        rel = str(path.relative_to(self.config.target_repo))
        self.repo.index.remove([rel], working_tree=True)
        commit = self.repo.index.commit(f"content: remove {post_type} '{slug}'")
        return commit.hexsha[:7]

    def repush(self, slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str:
        return self.publish(slug, content, post_type)

    def push(self) -> None:
        origin = self.repo.remotes.origin
        origin.push()
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/agents/test_git_publisher.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/git_publisher.py tests/agents/test_git_publisher.py
git commit -m "feat: GitPublisher agent (write, commit, push via GitPython)"
```

---

## Task 9: Orchestrator

**Files:**
- Modify: `agents/orchestrator.py`
- Create: `tests/agents/test_orchestrator.py`

**Interfaces:**
- Consumes: all four agents + `core/manifest.py` + `core/config.py`
- Produces: `Orchestrator(config_path: str).run(n_topics: int, n_prompts: int, n_workflows: int, categories: list[str]) -> None`

- [ ] **Step 1: Write failing tests**

`tests/agents/test_orchestrator.py`:
```python
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from core.models import TopicResult
from agents.orchestrator import Orchestrator

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_topic(n: int = 0) -> TopicResult:
    return TopicResult(
        title=f"Topic {n}", summary="summary", source="tavily",
        category="generative-ai", url="https://example.com",
    )


def test_run_generates_correct_file_count(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=[make_topic(0), make_topic(1)])
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("test-slug", "---\ntitle: t\n---\ncontent"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/test-slug.png")
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="abc1234")
    mocker.patch("agents.orchestrator.GitPublisher.push")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path)
    orch.run(n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"])

    with open(manifest_path) as f:
        data = json.load(f)

    assert len(data["posts"]) == 4  # 2 topics × (1 prompt + 1 workflow)


def test_run_marks_posts_as_pushed(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=[make_topic(0)])
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("slug-x", "---\ntitle: x\n---\nok"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/slug-x.png")
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="def5678")
    mocker.patch("agents.orchestrator.GitPublisher.push")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path)
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"])

    with open(manifest_path) as f:
        data = json.load(f)

    assert data["posts"][0]["status"] == "pushed"
    assert data["posts"][0]["git_commit"] == "def5678"
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/agents/test_orchestrator.py -v
```

Expected: `ImportError: cannot import name 'Orchestrator'`

- [ ] **Step 3: Implement `agents/orchestrator.py`**

```python
from datetime import datetime
from core.config import get_config
from core.manifest import append_post, update_post
from core.models import PostEntry
from agents.trend_discovery import TrendDiscovery
from agents.content_generator import ContentGenerator
from agents.image_generator import ImageGenerator
from agents.git_publisher import GitPublisher

DEFAULT_MANIFEST = "manifest.json"


class Orchestrator:
    def __init__(self, config_path: str = "config.yaml", manifest_path: str = DEFAULT_MANIFEST):
        self.config = get_config(config_path)
        self.manifest_path = manifest_path
        self.trend = TrendDiscovery(self.config)
        self.content = ContentGenerator(self.config)
        self.image = ImageGenerator(self.config)
        self.git = GitPublisher(self.config)

    def run(self, n_topics: int, n_prompts: int, n_workflows: int, categories: list[str]) -> None:
        topics = self.trend.run(categories, n_topics)

        for topic in topics:
            for _ in range(n_prompts):
                self._generate_and_publish(topic, "prompt")
            for _ in range(n_workflows):
                self._generate_and_publish(topic, "workflow")

        self.git.push()

    def _generate_and_publish(self, topic, post_type: str) -> None:
        slug, content = self.content.run(topic, post_type)

        image_path = None
        if post_type == "prompt":
            image_path = self.image.run(topic.title, slug, self.config.target_repo)
            if image_path:
                content = content.replace('image: ""', f'image: "/{image_path}"', 1)

        commit_sha = self.git.publish(slug, content, post_type)

        post = PostEntry(
            slug=slug,
            title=topic.title,
            type=post_type,
            category=topic.category,
            topic=topic.title,
            status="pushed",
            created_at=datetime.utcnow(),
            file_path=f"content/{post_type}s/{slug}.md",
            image_path=image_path,
            source_url=topic.url,
            git_commit=commit_sha,
        )
        append_post(post, self.manifest_path)
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/agents/test_orchestrator.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/orchestrator.py tests/agents/test_orchestrator.py
git commit -m "feat: Orchestrator — coordinates all agents and writes manifest"
```

---

## Task 10: CLI Entry Point

**Files:**
- Modify: `main.py`
- Create: `tests/test_main.py`

**Interfaces:**
- Consumes: `agents/orchestrator.py` → `Orchestrator`
- Produces: `python main.py` — interactive CLI session

- [ ] **Step 1: Write failing tests**

`tests/test_main.py`:
```python
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from main import app

runner = CliRunner()


def test_cli_invokes_orchestrator(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, input="2\n1\n1\ngenerative-ai\n")

    assert result.exit_code == 0
    mock_orch.run.assert_called_once_with(
        n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"]
    )


def test_cli_handles_all_categories(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, input="1\n2\n0\nall\n")

    assert result.exit_code == 0
    _, kwargs = mock_orch.run.call_args
    assert kwargs["categories"] == ["all"]
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/test_main.py -v
```

Expected: `ImportError: cannot import name 'app' from 'main'`

- [ ] **Step 3: Implement `main.py`**

```python
import typer
from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel
from agents.orchestrator import Orchestrator

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main():
    console.print(Panel.fit("[bold yellow]ContentPilot[/bold yellow] — AI Content Agent", border_style="yellow"))

    n_topics = IntPrompt.ask("\nHow many trending topics today")
    n_prompts = IntPrompt.ask("Prompts per topic [bold](with image)[/bold]")
    n_workflows = IntPrompt.ask("Workflows per topic")
    categories_raw = Prompt.ask(
        "Categories [dim](generative-ai, genz, photography, or all)[/dim]",
        default="all",
    )
    categories = [c.strip() for c in categories_raw.split(",")]

    console.print(f"\n[green]Fetching {n_topics} trending topics...[/green]")

    orch = Orchestrator()
    orch.run(n_topics=n_topics, n_prompts=n_prompts, n_workflows=n_workflows, categories=categories)

    console.print(f"\n[bold green]✓ Done![/bold green] Check your dashboard: [link]http://localhost:8000[/link]")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/test_main.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: CLI entry point (typer + rich interactive prompts)"
```

---

## Task 11: Dashboard

**Files:**
- Modify: `dashboard/server.py`
- Modify: `dashboard/templates/base.html`
- Modify: `dashboard/templates/index.html`
- Modify: `dashboard/templates/post.html`
- Create: `tests/dashboard/test_server.py`

**Interfaces:**
- Consumes: `core/manifest.py` → `load_manifest`, `delete_post`; `core/config.py` → `get_config`; `agents/git_publisher.py` → `GitPublisher`
- Produces: FastAPI app at `localhost:8000` with routes `GET /`, `GET /post/{slug}`, `DELETE /api/delete/{slug}`, `POST /api/repush/{slug}`

- [ ] **Step 1: Write failing tests**

`tests/dashboard/test_server.py`:
```python
import pytest
import json
from datetime import datetime
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from core.models import ManifestState, PostEntry


def make_manifest_with_post(tmp_path) -> tuple[str, PostEntry]:
    post = PostEntry(
        slug="test-post", title="Test Post", type="prompt",
        category="generative-ai", topic="AI trends", status="pushed",
        created_at=datetime.utcnow(), file_path="content/prompts/test-post.md",
        source_url="https://example.com", git_commit="abc1234",
    )
    state = ManifestState(posts=[post])
    path = str(tmp_path / "manifest.json")
    Path(path).write_text(state.model_dump_json(indent=2))
    return path, post


@pytest.fixture
def test_app(tmp_path, mocker):
    manifest_path, post = make_manifest_with_post(tmp_path)
    mocker.patch("dashboard.server.MANIFEST_PATH", manifest_path)
    mocker.patch("dashboard.server.get_config")
    from dashboard.server import app
    return app


@pytest.mark.asyncio
async def test_index_returns_200(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "Test Post" in response.text


@pytest.mark.asyncio
async def test_post_detail_returns_200(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/post/test-post")
    assert response.status_code == 200
    assert "test-post" in response.text


@pytest.mark.asyncio
async def test_delete_returns_success(test_app, mocker):
    mocker.patch("dashboard.server.GitPublisher")
    mocker.patch("dashboard.server.delete_post")
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.delete("/api/delete/test-post")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_post_not_found_returns_404(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/post/nonexistent-slug")
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests — expect failure**

```bash
pytest tests/dashboard/test_server.py -v
```

Expected: `ImportError` or `404` from missing routes.

- [ ] **Step 3: Implement `dashboard/server.py`**

```python
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from core.config import get_config
from core.manifest import load_manifest, delete_post
from agents.git_publisher import GitPublisher

MANIFEST_PATH = "manifest.json"
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

app = FastAPI(title="ContentPilot Dashboard")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
async def index(request: Request):
    state = load_manifest(MANIFEST_PATH)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": [p for p in state.posts if p.status != "deleted"],
    })


@app.get("/post/{slug}")
async def post_detail(request: Request, slug: str):
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})


@app.delete("/api/delete/{slug}")
async def delete(slug: str):
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    cfg = get_config()
    publisher = GitPublisher(cfg)
    publisher.delete(slug, post.type)
    publisher.push()
    delete_post(slug, MANIFEST_PATH)
    return JSONResponse({"status": "deleted", "slug": slug})


@app.post("/api/repush/{slug}")
async def repush(slug: str):
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    file_path = post.file_path
    try:
        with open(f"{get_config().target_repo}/{file_path}") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    cfg = get_config()
    publisher = GitPublisher(cfg)
    sha = publisher.repush(post.slug, content, post.type)
    publisher.push()
    return JSONResponse({"status": "repushed", "slug": slug, "commit": sha})


if __name__ == "__main__":
    cfg = get_config()
    uvicorn.run(app, host="0.0.0.0", port=cfg.dashboard.port, reload=True)
```

- [ ] **Step 4: Implement `dashboard/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ContentPilot Dashboard</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #0f0f0f; color: #e5e5e5; min-height: 100vh; }
    nav { background: #1a1a1a; border-bottom: 1px solid #333; padding: 1rem 2rem; display: flex; align-items: center; gap: 2rem; }
    nav a { color: #e5e5e5; text-decoration: none; font-weight: 500; }
    nav .brand { font-size: 1.2rem; font-weight: 700; color: #facc15; }
    nav a:hover { color: #facc15; }
    main { padding: 2rem; max-width: 1200px; margin: 0 auto; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-prompt { background: #1d4ed8; color: #fff; }
    .badge-workflow { background: #6d28d9; color: #fff; }
    .badge-pushed { background: #15803d; color: #fff; }
    .badge-failed { background: #b91c1c; color: #fff; }
    .btn { padding: 0.4rem 1rem; border-radius: 6px; border: none; cursor: pointer; font-size: 0.85rem; font-weight: 600; }
    .btn-danger { background: #b91c1c; color: #fff; }
    .btn-primary { background: #1d4ed8; color: #fff; }
    .btn:hover { opacity: 0.85; }
  </style>
</head>
<body>
  <nav>
    <span class="brand">ContentPilot</span>
    <a href="/">All Posts</a>
  </nav>
  <main>{% block content %}{% endblock %}</main>
</body>
</html>
```

- [ ] **Step 5: Implement `dashboard/templates/index.html`**

```html
{% extends "base.html" %}
{% block content %}
<h1 style="margin-bottom:1.5rem;font-size:1.5rem;">Published Posts</h1>
{% if not posts %}
  <p style="color:#888;">No posts yet. Run <code>python main.py</code> to generate content.</p>
{% else %}
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem;">
  {% for post in posts %}
  <a href="/post/{{ post.slug }}" style="text-decoration:none;color:inherit;">
    <div style="background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:1.2rem;transition:border-color .2s;" onmouseover="this.style.borderColor='#facc15'" onmouseout="this.style.borderColor='#333'">
      {% if post.image_path %}
        <img src="/{{ post.image_path }}" alt="{{ post.title }}" style="width:100%;height:150px;object-fit:cover;border-radius:4px;margin-bottom:.8rem;" />
      {% endif %}
      <div style="display:flex;gap:.5rem;margin-bottom:.6rem;">
        <span class="badge badge-{{ post.type }}">{{ post.type }}</span>
        <span class="badge badge-{{ post.status }}">{{ post.status }}</span>
      </div>
      <h2 style="font-size:1rem;margin-bottom:.4rem;">{{ post.title }}</h2>
      <p style="color:#888;font-size:.8rem;">{{ post.category }} · {{ post.created_at.strftime('%Y-%m-%d') }}</p>
    </div>
  </a>
  {% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Implement `dashboard/templates/post.html`**

```html
{% extends "base.html" %}
{% block content %}
<div style="max-width:700px;">
  <a href="/" style="color:#facc15;text-decoration:none;font-size:.9rem;">← All Posts</a>
  <div style="margin-top:1.5rem;">
    <div style="display:flex;gap:.5rem;margin-bottom:.8rem;">
      <span class="badge badge-{{ post.type }}">{{ post.type }}</span>
      <span class="badge badge-{{ post.status }}">{{ post.status }}</span>
    </div>
    <h1 style="font-size:1.6rem;margin-bottom:.5rem;">{{ post.title }}</h1>
    <p style="color:#888;font-size:.85rem;margin-bottom:1.5rem;">
      {{ post.category }} · {{ post.created_at.strftime('%Y-%m-%d %H:%M') }} · commit {{ post.git_commit or '—' }}
    </p>
    {% if post.image_path %}
      <img src="/{{ post.image_path }}" alt="{{ post.title }}" style="width:100%;border-radius:8px;margin-bottom:1.5rem;" />
    {% endif %}
    <p style="color:#aaa;font-size:.85rem;margin-bottom:.4rem;">File: <code>{{ post.file_path }}</code></p>
    <p style="color:#aaa;font-size:.85rem;margin-bottom:1.5rem;">Source: <a href="{{ post.source_url }}" target="_blank" style="color:#facc15;">{{ post.source_url[:60] }}...</a></p>
    <div style="display:flex;gap:1rem;">
      <button class="btn btn-primary" onclick="repush('{{ post.slug }}')">Re-push</button>
      <button class="btn btn-danger" onclick="confirmDelete('{{ post.slug }}')">Delete</button>
    </div>
  </div>
</div>
<script>
async function confirmDelete(slug) {
  if (!confirm('Delete this post and remove it from git?')) return;
  const res = await fetch(`/api/delete/${slug}`, { method: 'DELETE' });
  if (res.ok) window.location.href = '/';
  else alert('Delete failed');
}
async function repush(slug) {
  const res = await fetch(`/api/repush/${slug}`, { method: 'POST' });
  if (res.ok) alert('Re-pushed successfully');
  else alert('Re-push failed');
}
</script>
{% endblock %}
```

- [ ] **Step 7: Run all dashboard tests**

```bash
pytest tests/dashboard/test_server.py -v
```

Expected: 4 passed.

- [ ] **Step 8: Run full test suite**

```bash
pytest -v
```

Expected: all tests pass with no errors.

- [ ] **Step 9: Commit**

```bash
git add dashboard/ tests/dashboard/
git commit -m "feat: FastAPI dashboard with post grid, detail view, delete, re-push"
```

---

## Final Verification

- [ ] **Copy and configure**

```bash
cp config.yaml.example config.yaml   # edit target_repo to point at outflo
cp .env.example .env                  # add GEMINI_API_KEY, TAVILY_API_KEY, REDDIT_* keys
```

- [ ] **Run the agent**

```bash
python main.py
```

Expected: interactive prompts appear, content is generated and pushed.

- [ ] **Run the dashboard**

```bash
python dashboard/server.py
```

Expected: `http://localhost:8000` shows the post grid.

- [ ] **Final commit**

```bash
git add config.yaml.example .env.example README.md
git commit -m "chore: finalize setup files and README"
```
