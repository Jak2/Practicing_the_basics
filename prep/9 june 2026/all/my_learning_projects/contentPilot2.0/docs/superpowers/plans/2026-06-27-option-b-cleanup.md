# ContentPilot Option B Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dead code, fix two runtime bugs, and eliminate three code smells so the codebase is clean and correct before Phase 2 work begins.

**Architecture:** Five targeted tasks executed in dependency order. Tasks 1–2 are isolated. Task 3 changes TrendDiscovery's return type, which Task 3 also updates in the orchestrator. Task 4 guards ImageGenerator init. Task 5 rewrites the image generator shim. Each task leaves the test suite fully passing before the next begins.

**Tech Stack:** Python 3.12, Pydantic v2, pytest + pytest-mock, google-genai SDK, FastAPI.

## Global Constraints

- All commands run from `my_learning_projects/contentpilot/` with venv active: `source .venv/bin/activate.fish`
- Run tests with: `PYTHONPATH=. .venv/bin/python -m pytest -v` — must stay green after every task
- Do NOT push to git (user constraint)
- Do NOT modify any files outside `my_learning_projects/contentpilot/`
- Do NOT add new features — this is a cleanup-only plan (YAGNI)
- Preserve all existing test behaviour unless a test is directly for dead code being removed

---

## File Map

| File | What changes |
|---|---|
| `requirements.txt` | Remove `pydantic-settings` line and duplicate `httpx` line |
| `core/models.py` | Remove `"pending"` from `PostEntry.status` Literal |
| `core/manifest.py` | Remove `update_post()` function |
| `tests/core/test_manifest.py` | Remove `update_post` import + 2 tests that use it; fix `make_post()` to use `status="pushed"` |
| `agents/trend_discovery.py` | Remove inner try/except from `_fetch_hackernews()`; change `run()` return type to tuple; remove `self.source_results` side-effect |
| `agents/orchestrator.py` | Unpack tuple from `trend.run()`; guard `ImageGenerator` init behind `provider == "google"` |
| `tests/agents/test_trend_discovery.py` | Unpack tuple in all 3 existing tests; add 1 new test for HackerNews error propagation |
| `tests/fixtures/config_ollama.yaml` | New fixture: same as `config_valid.yaml` but `provider: ollama` |
| `tests/agents/test_orchestrator.py` | Add 1 new test: Ollama provider does not initialise ImageGenerator |
| `agents/image_generator.py` | Delete shim class + monkey-patch; rewrite `ImageGenerator` to use `google.genai.Client` directly |
| `tests/agents/test_image_generator.py` | Rewrite both tests to mock `google.genai.Client` instead of `genai.ImageGenerationModel` |

---

### Task 1: Remove dead code

**Files:**
- Modify: `requirements.txt`
- Modify: `core/models.py`
- Modify: `core/manifest.py`
- Modify: `tests/core/test_manifest.py`

**Interfaces:**
- Consumes: nothing from prior tasks
- Produces: `PostEntry.status` is now `Literal["pushed", "deleted", "failed"]` — Tasks 3–5 must not use `"pending"` when creating PostEntry

- [ ] **Step 1: Remove dead lines from requirements.txt**

Open `requirements.txt`. Delete the line `pydantic-settings>=2.0`. Delete the second `httpx>=0.27` line (the one at the bottom with the comment "already listed above"). The first `httpx>=0.27` (line 9, under "Trend discovery") stays.

Result — `requirements.txt` should contain exactly one `httpx` entry and no `pydantic-settings` entry.

- [ ] **Step 2: Remove `"pending"` from PostEntry.status**

In `core/models.py`, change line 20:
```python
# Before
status: Literal["pending", "pushed", "deleted", "failed"]

# After
status: Literal["pushed", "deleted", "failed"]
```

- [ ] **Step 3: Remove `update_post()` from manifest.py**

In `core/manifest.py`, delete the entire `update_post` function (lines 30–38):
```python
# Delete this entire function:
def update_post(slug: str, status: str, git_commit: str | None = None, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        state = load_manifest(path)
        for post in state.posts:
            if post.slug == slug:
                post.status = status
                if git_commit:
                    post.git_commit = git_commit
        save_manifest(state, path)
```

- [ ] **Step 4: Update test_manifest.py**

In `tests/core/test_manifest.py`, make these three changes:

**4a.** Change the import on line 5 — remove `update_post`:
```python
# Before
from core.manifest import load_manifest, save_manifest, append_post, update_post, delete_post

# After
from core.manifest import load_manifest, save_manifest, append_post, delete_post
```

**4b.** In `make_post()`, change `status="pending"` to `status="pushed"`:
```python
def make_post(slug: str = "test-slug", post_type: str = "prompt") -> PostEntry:
    return PostEntry(
        slug=slug,
        title="Test Post",
        type=post_type,
        category="generative-ai",
        topic="AI trends",
        status="pushed",          # was "pending"
        created_at=datetime.utcnow(),
        file_path=f"content/prompts/{slug}.md",
        source_url="https://example.com",
    )
```

**4c.** Delete the two `update_post` tests entirely:
```python
# Delete test_update_post_status (lines 47–53)
# Delete test_update_nonexistent_post_is_noop (lines 66–71)
```

After deletions, `test_manifest.py` should have exactly 4 tests: `test_load_manifest_missing_file`, `test_save_and_load_roundtrip`, `test_append_post`, `test_delete_post`.

- [ ] **Step 5: Run tests — expect 4 manifest tests passing, 36 total**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/core/test_manifest.py -v
```

Expected output:
```
PASSED tests/core/test_manifest.py::test_load_manifest_missing_file
PASSED tests/core/test_manifest.py::test_save_and_load_roundtrip
PASSED tests/core/test_manifest.py::test_append_post
PASSED tests/core/test_manifest.py::test_delete_post
4 passed
```

Then run the full suite to confirm nothing else broke:
```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

Expected: 36 passed (was 38 — the 2 deleted update_post tests are gone).

- [ ] **Step 6: Commit**

```bash
git add requirements.txt core/models.py core/manifest.py tests/core/test_manifest.py
git commit -m "chore: remove dead code — update_post, pending status, pydantic-settings, httpx duplicate"
```

---

### Task 2: Fix HackerNews silent failure (BUG-1)

**Files:**
- Modify: `agents/trend_discovery.py`
- Modify: `tests/agents/test_trend_discovery.py`

**Interfaces:**
- Consumes: `TrendDiscovery.run()` still returns `list[TopicResult]` (Task 3 changes this — do Task 2 first)
- Produces: `_fetch_hackernews()` now raises instead of returning `[]` on error

**Context:** `_fetch_hackernews()` has an inner `try/except Exception: return []` that swallows all errors before they reach the outer handler in `run()`. Result: `source_results["hackernews"]` always shows success even when HackerNews is unreachable. Fix: remove the inner try/except.

- [ ] **Step 1: Write the failing test**

Add this test at the bottom of `tests/agents/test_trend_discovery.py`:

```python
def test_hackernews_error_surfaces_in_source_results(mocker):
    """_fetch_hackernews errors must propagate so run() records them as failed, not success."""
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.httpx.get", side_effect=Exception("connection refused"))

    agent = TrendDiscovery(make_config())
    results = agent.run(["generative-ai"], n_topics=3)

    assert results == []
    assert agent.source_results["hackernews"]["error"] is not None
    assert agent.source_results["hackernews"]["error"] == "connection refused"
```

- [ ] **Step 2: Run the test — expect FAIL**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_trend_discovery.py::test_hackernews_error_surfaces_in_source_results -v
```

Expected: FAIL — the test asserts `error is not None` but currently `_fetch_hackernews` swallows the exception and returns `[]`, so `source_results["hackernews"]` gets `{"count": 0, "error": None, "skipped": False}` (the success path).

- [ ] **Step 3: Remove the inner try/except from `_fetch_hackernews()`**

In `agents/trend_discovery.py`, replace the entire `_fetch_hackernews` method:

```python
def _fetch_hackernews(self, n: int) -> list[TopicResult]:
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
```

The only change is the removal of `try:` / `except Exception: return []`. The body is identical.

- [ ] **Step 4: Run tests — expect all passing**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_trend_discovery.py -v
```

Expected: 4 passed (3 original + 1 new).

Run the full suite:
```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

Expected: 37 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/trend_discovery.py tests/agents/test_trend_discovery.py
git commit -m "fix: HackerNews exceptions now propagate to run() error handler instead of being swallowed"
```

---

### Task 3: Return source_results from run() instead of side-effect (SMELL-2)

**Files:**
- Modify: `agents/trend_discovery.py`
- Modify: `agents/orchestrator.py`
- Modify: `tests/agents/test_trend_discovery.py`

**Interfaces:**
- Consumes: `_fetch_hackernews()` raises on error (from Task 2)
- Produces: `TrendDiscovery.run()` now returns `tuple[list[TopicResult], dict[str, dict]]`
  - First element: deduplicated topics list (same as before)
  - Second element: source_results dict — same shape as before: `{"hackernews": {"count": int, "error": str|None, "skipped": bool}, ...}`

**Context:** `TrendDiscovery.run()` currently populates `self.source_results` as a mutable side effect. The orchestrator then reads `self.trend.source_results` after calling `run()`. This is fragile — calling `run()` twice clobbers the first results. Fix: return `source_results` as the second element of the return value.

- [ ] **Step 1: Update existing trend_discovery tests to unpack the tuple**

In `tests/agents/test_trend_discovery.py`, update all three original tests.

Change `test_run_returns_topic_results`:
```python
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
    results, source_results = agent.run(["generative-ai"], n_topics=1)

    assert len(results) == 1
    assert isinstance(results[0], TopicResult)
    assert results[0].source == "tavily"
    assert results[0].category == "generative-ai"
```

Change `test_run_deduplicates_by_title`:
```python
def test_run_deduplicates_by_title(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    duplicate = TopicResult(title="Same topic", summary="desc", source="reddit",
                             category="generative-ai", url="https://a.com")
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results, _ = agent.run(["generative-ai"], n_topics=5)

    titles = [r.title for r in results]
    assert titles.count("Same topic") == 1
```

Change `test_run_respects_n_topics_limit`:
```python
def test_run_respects_n_topics_limit(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    many = [TopicResult(title=f"Topic {i}", summary="s", source="tavily",
                         category="generative-ai", url="https://x.com") for i in range(10)]
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=many)
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results, _ = agent.run(["generative-ai"], n_topics=3)
    assert len(results) == 3
```

Update `test_hackernews_error_surfaces_in_source_results` (added in Task 2):
```python
def test_hackernews_error_surfaces_in_source_results(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.httpx.get", side_effect=Exception("connection refused"))

    agent = TrendDiscovery(make_config())
    results, source_results = agent.run(["generative-ai"], n_topics=3)

    assert results == []
    assert source_results["hackernews"]["error"] is not None
    assert source_results["hackernews"]["error"] == "connection refused"
```

- [ ] **Step 2: Run tests — expect FAIL (source_results not returned yet)**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_trend_discovery.py -v
```

Expected: multiple FAILs — `cannot unpack non-sequence list`.

- [ ] **Step 3: Rewrite `TrendDiscovery.run()` to return the tuple**

In `agents/trend_discovery.py`, replace the entire `run()` method and `__init__`:

```python
class TrendDiscovery:
    def __init__(self, config: Config):
        self.config = config
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", "")) if config.sources.tavily else None

    def run(self, categories: list[str], n_topics: int) -> tuple[list[TopicResult], dict[str, dict]]:
        source_results: dict[str, dict] = {}
        results: list[TopicResult] = []

        if self.config.sources.tavily:
            try:
                fetched = self._fetch_tavily(categories, n_topics)
                results.extend(fetched)
                source_results["tavily"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["tavily"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["tavily"] = {"count": 0, "error": None, "skipped": True}

        if self.config.sources.reddit.enabled:
            try:
                fetched = self._fetch_reddit(n_topics)
                results.extend(fetched)
                source_results["reddit"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["reddit"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["reddit"] = {"count": 0, "error": None, "skipped": True}

        if self.config.sources.hackernews.enabled:
            try:
                fetched = self._fetch_hackernews(n_topics)
                results.extend(fetched)
                source_results["hackernews"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["hackernews"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["hackernews"] = {"count": 0, "error": None, "skipped": True}

        seen: set[str] = set()
        unique: list[TopicResult] = []
        for r in results:
            if r.title not in seen:
                seen.add(r.title)
                unique.append(r)
        return unique[:n_topics], source_results
```

Changes from the original:
- Removed `self.source_results = {}` from `__init__`
- Removed `self.source_results` from `__init__` attribute (the comment too)
- `run()` uses a local `source_results` dict instead of `self.source_results`
- `run()` returns `(unique[:n_topics], source_results)` instead of just `unique[:n_topics]`

- [ ] **Step 4: Update orchestrator.py to unpack the tuple**

In `agents/orchestrator.py`, in the `run()` method, change the TrendDiscovery call block:

```python
# Before (lines 40–58):
td_step = new_step("trend_discovery", "TrendDiscovery.run()", "agents/trend_discovery.py")
try:
    topics = self.trend.run(categories, n_topics)
    # build per-source child steps from source_results populated by TrendDiscovery
    for src, data in self.trend.source_results.items():

# After:
td_step = new_step("trend_discovery", "TrendDiscovery.run()", "agents/trend_discovery.py")
try:
    topics, source_results = self.trend.run(categories, n_topics)
    for src, data in source_results.items():
```

Only two lines change: `topics = self.trend.run(...)` becomes `topics, source_results = self.trend.run(...)`, and `self.trend.source_results.items()` becomes `source_results.items()`.

- [ ] **Step 5: Run tests — expect all passing**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_trend_discovery.py tests/agents/test_orchestrator.py -v
```

Expected: 4 + 2 = 6 passed.

Full suite:
```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

Expected: 37 passed.

- [ ] **Step 6: Commit**

```bash
git add agents/trend_discovery.py agents/orchestrator.py tests/agents/test_trend_discovery.py
git commit -m "refactor: TrendDiscovery.run() returns source_results as tuple instead of mutating self"
```

---

### Task 4: Lazy ImageGenerator initialization (BUG-2)

**Files:**
- Create: `tests/fixtures/config_ollama.yaml`
- Modify: `agents/orchestrator.py`
- Modify: `tests/agents/test_orchestrator.py`

**Interfaces:**
- Consumes: nothing from prior tasks (independent)
- Produces: `Orchestrator.__init__()` sets `self.image = None` when `provider == "ollama"`; `_logged_generate()` guards image gen on `self.image is not None`

**Context:** `Orchestrator.__init__()` unconditionally creates `ImageGenerator(self.config)`, which calls `genai.configure()` and loads the Imagen model even when `provider: ollama`. With no Gemini key this can crash at startup. Fix: only initialize when using the Google provider.

- [ ] **Step 1: Create the Ollama config fixture**

Create `tests/fixtures/config_ollama.yaml`:

```yaml
target_repo: /tmp/fake-repo
content_paths:
  prompts: content/prompts
  workflows: content/workflows
  images: public/images
llm:
  provider: ollama
  model: phi3:mini
  image_model: imagen-3.0-generate-001
sources:
  tavily: true
  reddit:
    enabled: true
    subreddits:
      - MachineLearning
  hackernews:
    enabled: true
dashboard:
  port: 8000
```

- [ ] **Step 2: Write the failing test**

Add to `tests/agents/test_orchestrator.py`:

```python
def test_ollama_provider_does_not_init_image_generator(mocker, tmp_path):
    """With provider=ollama, Orchestrator must not initialise ImageGenerator."""
    manifest_path = str(tmp_path / "manifest.json")

    mocker.patch("agents.orchestrator.TrendDiscovery.__init__", return_value=None)
    mocker.patch("agents.orchestrator.ContentGenerator.__init__", return_value=None)
    mocker.patch("agents.orchestrator.GitPublisher.__init__", return_value=None)
    mock_image_init = mocker.patch("agents.orchestrator.ImageGenerator.__init__", return_value=None)

    orch = Orchestrator(config_path="tests/fixtures/config_ollama.yaml", manifest_path=manifest_path)

    mock_image_init.assert_not_called()
    assert orch.image is None
```

- [ ] **Step 3: Run test — expect FAIL**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_orchestrator.py::test_ollama_provider_does_not_init_image_generator -v
```

Expected: FAIL — `ImageGenerator.__init__` is currently called unconditionally.

- [ ] **Step 4: Update `Orchestrator.__init__()` to guard ImageGenerator**

In `agents/orchestrator.py`, change the `__init__` method:

```python
def __init__(
    self,
    config_path: str = "config.yaml",
    manifest_path: str = DEFAULT_MANIFEST,
    run_log_path: str = DEFAULT_RUN_LOG,
):
    self.config = get_config(config_path)
    self.manifest_path = manifest_path
    self.run_log_path = run_log_path
    self.trend = TrendDiscovery(self.config)
    self.content = ContentGenerator(self.config)
    self.image = ImageGenerator(self.config) if self.config.llm.provider == "google" else None
    self.git = GitPublisher(self.config)
```

Only one line changes: `self.image = ImageGenerator(self.config)` becomes the conditional.

- [ ] **Step 5: Guard image generation in `_logged_generate()` against `self.image is None`**

In `agents/orchestrator.py`, find the image generation block inside `_logged_generate()` and add the `self.image is not None` guard:

```python
# Before:
if post_type == "prompt":
    ig = new_step("image_gen", "ImageGenerator.run()", "agents/image_generator.py")

# After:
if post_type == "prompt" and self.image is not None:
    ig = new_step("image_gen", "ImageGenerator.run()", "agents/image_generator.py")
```

- [ ] **Step 6: Run tests — expect all passing**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_orchestrator.py -v
```

Expected: 3 passed (2 original + 1 new).

Full suite:
```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

Expected: 38 passed.

- [ ] **Step 7: Commit**

```bash
git add tests/fixtures/config_ollama.yaml agents/orchestrator.py tests/agents/test_orchestrator.py
git commit -m "fix: ImageGenerator only initialises when provider is google, not for ollama"
```

---

### Task 5: Remove `_ImageGenerationModel` shim (SMELL-1)

**Files:**
- Modify: `agents/image_generator.py`
- Modify: `tests/agents/test_image_generator.py`

**Interfaces:**
- Consumes: `Orchestrator.image` is `None` when provider is ollama (Task 4) — so `ImageGenerator` is only ever constructed when a real Gemini key is expected
- Produces: `ImageGenerator` uses `google.genai.Client` directly, no shim, no monkey-patch

**Context:** `agents/image_generator.py` contains a 30-line `_ImageGenerationModel` wrapper class and a module-level monkey-patch (`genai.ImageGenerationModel = _ImageGenerationModel`) that exists solely so test mocks targeting `genai.ImageGenerationModel.from_pretrained` keep working. The real implementation already uses `google.genai.Client` internally (inside the shim). Fix: delete the shim, use `google.genai.Client` directly, update the 2 tests to mock the client.

- [ ] **Step 1: Rewrite `agents/image_generator.py`**

Replace the entire file with:

```python
import os
from pathlib import Path
import google.genai as genai
from google.genai import types as genai_types
from core.config import Config


class ImageGenerator:
    def __init__(self, config: Config):
        self.config = config
        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

    def run(self, topic_title: str, slug: str, target_repo: str) -> str:
        prompt = (
            f"High-quality digital illustration representing: {topic_title}. "
            "Modern, minimal, professional style. No text overlays."
        )
        response = self._client.models.generate_images(
            model=self.config.llm.image_model,
            prompt=prompt,
            config=genai_types.GenerateImagesConfig(number_of_images=1),
        )
        image_bytes = response.generated_images[0].image.image_bytes

        rel_path = self.config.content_paths.images
        abs_dir = Path(target_repo) / rel_path
        abs_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{slug}.png"
        (abs_dir / filename).write_bytes(image_bytes)

        return f"{rel_path}/{filename}"
```

What changed vs. the original:
- Removed `import warnings` and `warnings.filterwarnings(...)` (no longer needed)
- Removed `import google.generativeai as genai` (old SDK, replaced)
- Removed `_ImageGenerationModel` class entirely (50+ lines)
- Removed `genai.ImageGenerationModel = _ImageGenerationModel` monkey-patch
- `__init__` now creates `self._client = genai.Client(...)` directly
- `run()` calls `self._client.models.generate_images(...)` directly
- Response access changes from `response.images[0].image_bytes` to `response.generated_images[0].image.image_bytes` (new SDK attribute path)

- [ ] **Step 2: Rewrite `tests/agents/test_image_generator.py`**

Replace the entire file with:

```python
from unittest.mock import MagicMock
from core.config import get_config
from agents.image_generator import ImageGenerator

FIXTURE = "tests/fixtures/config_valid.yaml"


def _make_mock_client(fake_image_bytes: bytes, mocker) -> MagicMock:
    mock_image = MagicMock()
    mock_image.image.image_bytes = fake_image_bytes

    mock_response = MagicMock()
    mock_response.generated_images = [mock_image]

    mock_client = MagicMock()
    mock_client.models.generate_images.return_value = mock_response

    mocker.patch("agents.image_generator.genai.Client", return_value=mock_client)
    return mock_client


def test_run_saves_image_and_returns_path(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    _make_mock_client(fake_bytes, mocker)

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    rel_path = agent.run("AI workflow agents", "ai-workflow-agents", str(tmp_path))

    assert rel_path == "public/images/ai-workflow-agents.png"
    assert (tmp_path / "public" / "images" / "ai-workflow-agents.png").exists()


def test_run_creates_image_dir_if_missing(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    _make_mock_client(fake_bytes, mocker)

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    agent.run("test", "test-slug", str(tmp_path))

    assert (tmp_path / "public" / "images").is_dir()
```

What changed:
- Removed old mock target `agents.image_generator.genai.ImageGenerationModel.from_pretrained`
- New mock target: `agents.image_generator.genai.Client` (patches the constructor)
- Mock response now uses `.generated_images[0].image.image_bytes` (new SDK shape)
- Added `_make_mock_client()` helper to avoid repeating the 8-line mock setup in both tests

- [ ] **Step 3: Run the image generator tests — expect passing**

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/agents/test_image_generator.py -v
```

Expected:
```
PASSED tests/agents/test_image_generator.py::test_run_saves_image_and_returns_path
PASSED tests/agents/test_image_generator.py::test_run_creates_image_dir_if_missing
2 passed
```

- [ ] **Step 4: Run full suite**

```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

Expected: 38 passed, 0 failed.

- [ ] **Step 5: Commit**

```bash
git add agents/image_generator.py tests/agents/test_image_generator.py
git commit -m "refactor: remove _ImageGenerationModel shim, use google.genai.Client directly"
```

---

## Notes on SMELL-3 (categories)

The `categories` parameter only applies to Tavily — Reddit and HackerNews already do not accept it in their `_fetch_*` signatures. The code is already correct; the misleading part is the CLI prompt in `main.py` which implies categories filter all sources. No code change is required. This is documented in `decisions_and_issues.md` under DECISION-2 as accepted behaviour.

---

## Self-Review

**Spec coverage check:**
- BUG-1 (HackerNews silent failure) → Task 2 ✅
- BUG-2 (ImageGenerator unconditional init) → Task 4 ✅
- DEAD-1 (update_post) → Task 1 ✅
- DEAD-2 (pending status) → Task 1 ✅
- DEAD-3 (pydantic-settings) → Task 1 ✅
- DEAD-4 (httpx duplicate) → Task 1 ✅
- SMELL-1 (ImageGenerator shim) → Task 5 ✅
- SMELL-2 (source_results side-effect) → Task 3 ✅
- SMELL-3 (categories) → Noted, no code change needed ✅

**Placeholder scan:** No TBDs, no "implement later", all steps contain complete code.

**Type consistency:**
- Task 3 changes `run()` return type to `tuple[list[TopicResult], dict[str, dict]]`
- Task 3 updates orchestrator to unpack: `topics, source_results = self.trend.run(...)` ✅
- Task 3 updates all 4 trend_discovery tests to unpack ✅
- Task 4 sets `self.image = None` for ollama; Task 4 also guards `_logged_generate()` with `self.image is not None` ✅
