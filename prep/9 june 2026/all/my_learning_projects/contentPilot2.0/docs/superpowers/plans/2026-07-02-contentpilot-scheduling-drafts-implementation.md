# ContentPilot Phase 4 — Non-Interactive CLI, Scheduler & Draft/Approve Workflow — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ContentPilot runnable non-interactively (cron/scheduler-friendly), add a `draft` post state so automated runs stage content for human approval instead of publishing immediately, and give the FastAPI dashboard an in-process scheduler so it's the single control point for scheduling, running, and approving content.

**Architecture:** Layer three additions onto the existing Phase 1 Orchestrator/Agent pipeline without rewriting it: (1) `GitPublisher` learns to write to a local `drafts/` staging area and to promote an approved draft into the target repo via a pathspec-scoped commit + push; (2) `Orchestrator.run()` gains a `draft: bool` parameter threaded through from three equivalent triggers — CLI flags, a dashboard "Run Now" button, and an APScheduler job — so all three execute the identical code path; (3) the dashboard gains `/drafts` (approve/reject), `/run-now`, and `/schedule` routes plus an `AsyncIOScheduler` instance started at app startup.

**Tech Stack:** Python 3.12, Typer + Rich (CLI), FastAPI + Jinja2 (dashboard), APScheduler (new dependency — `AsyncIOScheduler`), Pydantic v2 (all structured data, no other modeling library), `filelock` (concurrency-safe JSON files), GitPython, pytest + pytest-mock (all tests, no live API/network calls).

## Global Constraints

- All new persisted structures (`ScheduleConfig`) are Pydantic v2 `BaseModel` subclasses in `core/models.py`, loaded/saved with `model_validate_json()` / `model_dump_json()` — the same pattern `PostEntry`/`ManifestState` already use. Do not introduce dataclasses, attrs, or `pydantic-settings`.
- Any new JSON file that can be written from more than one place (dashboard UI + scheduler thread) must use the `filelock.FileLock` pattern from `core/manifest.py` — see `README.md`, "Design Standards for New Features."
- `GitPublisher.publish()` / `delete()` must remain pathspec-scoped commits (`repo.git.commit("-m", msg, "--", path)`), never `repo.index.commit()` — this is BUG-3's fix (`decisions_and_issues.md`); do not regress it.
- `PostEntry.status` stays `Literal["draft", "published", "deleted", "failed"]` — do not reintroduce `"pushed"` or `"pending"`.
- Long-running/synchronous work (`Orchestrator.run()`) triggered from inside the FastAPI dashboard process must never block the event loop — use `loop.run_in_executor()` for the `/run-now` route; APScheduler jobs registered as plain (non-async) functions are automatically dispatched to APScheduler's own thread pool executor, so no extra wrapping is needed there.
- No inline editing of draft content in the dashboard — approve or reject only (spec, Section 2, Out of Scope).
- Every new/modified function keeps the existing project's plain, low-ceremony style (see `core/manifest.py`, `agents/git_publisher.py`) — no added abstractions beyond what's specified below.

---

## File Structure

```
core/models.py            MODIFY  — add ScheduleConfig, add PostEntry.push_status
core/schedule.py          CREATE  — load_schedule()/save_schedule(), FileLock-protected
core/manifest.py          MODIFY  — add update_post_status()
agents/git_publisher.py   MODIFY  — draft-aware publish(), publish_draft(), discard_draft(), push() returns status
agents/orchestrator.py    MODIFY  — run(..., draft: bool) threaded through; per-post push replaces batch push
main.py                   MODIFY  — Typer options for non-interactive mode
dashboard/server.py       MODIFY  — /drafts, /run-now, /schedule routes; AsyncIOScheduler startup
dashboard/templates/base.html    MODIFY — nav links for Drafts / Schedule
dashboard/templates/drafts.html  CREATE — pending drafts queue, approve/reject
dashboard/templates/schedule.html CREATE — schedule config form
dashboard/templates/index.html   MODIFY — push_status badge
dashboard/templates/post.html    MODIFY — push_status badge
requirements.txt          MODIFY  — add apscheduler

tests/core/test_models.py         MODIFY — ScheduleConfig, push_status
tests/core/test_manifest.py       MODIFY — update_post_status
tests/core/test_schedule.py       CREATE — load/save round-trip
tests/agents/test_git_publisher.py MODIFY — draft publish, publish_draft, discard_draft
tests/agents/test_orchestrator.py  MODIFY — draft flag behavior
tests/test_main.py                MODIFY — flag-mode CLI
tests/dashboard/test_server.py    MODIFY — /drafts, /run-now, /schedule routes
```

---

## Task 1: `ScheduleConfig` model and `PostEntry.push_status`

**Files:**
- Modify: `core/models.py`
- Test: `tests/core/test_models.py`

**Interfaces:**
- Produces: `ScheduleConfig(BaseModel)` with fields `enabled: bool`, `interval_hours: int`, `topics: int`, `prompts: int`, `workflows: int`, `categories: list[str]`, `publish: bool` — all with defaults so `ScheduleConfig()` is valid.
- Produces: `PostEntry.push_status: Literal["pushed", "failed", "no_remote"] | None = None`

- [ ] **Step 1: Write the failing tests**

Append to `tests/core/test_models.py`:

```python
from core.models import ScheduleConfig


def test_schedule_config_defaults():
    cfg = ScheduleConfig()
    assert cfg.enabled is False
    assert cfg.interval_hours == 24
    assert cfg.topics == 3
    assert cfg.prompts == 1
    assert cfg.workflows == 1
    assert cfg.categories == ["all"]
    assert cfg.publish is False


def test_schedule_config_custom_values():
    cfg = ScheduleConfig(enabled=True, interval_hours=6, topics=5, categories=["generative-ai"])
    assert cfg.enabled is True
    assert cfg.interval_hours == 6
    assert cfg.categories == ["generative-ai"]


def test_post_entry_push_status_defaults_to_none():
    p = PostEntry(
        slug="s", title="t", type="prompt", category="c", topic="tp",
        status="draft", created_at=datetime.utcnow(), file_path="x.md",
        source_url="http://x",
    )
    assert p.push_status is None


def test_post_entry_push_status_accepts_literal_values():
    p = PostEntry(
        slug="s", title="t", type="prompt", category="c", topic="tp",
        status="published", created_at=datetime.utcnow(), file_path="x.md",
        source_url="http://x", push_status="pushed",
    )
    assert p.push_status == "pushed"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_models.py -v`
Expected: FAIL — `ImportError: cannot import name 'ScheduleConfig'` and/or `TypeError: unexpected keyword argument 'push_status'`

- [ ] **Step 3: Implement**

In `core/models.py`, modify `PostEntry` and add `ScheduleConfig`:

```python
class PostEntry(BaseModel):
    slug: str
    title: str
    type: Literal["prompt", "workflow"]
    category: str
    topic: str
    status: Literal["draft", "published", "deleted", "failed"]
    push_status: Literal["pushed", "failed", "no_remote"] | None = None
    created_at: datetime
    file_path: str
    image_path: str | None = None
    source_url: str
    git_commit: str | None = None


class ManifestState(BaseModel):
    posts: list[PostEntry] = []


class ScheduleConfig(BaseModel):
    enabled: bool = False
    interval_hours: int = 24
    topics: int = 3
    prompts: int = 1
    workflows: int = 1
    categories: list[str] = ["all"]
    publish: bool = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_models.py -v`
Expected: PASS (all tests including pre-existing ones)

- [ ] **Step 5: Commit**

```bash
git add core/models.py tests/core/test_models.py
git commit -m "feat: add ScheduleConfig and PostEntry.push_status"
```

---

## Task 2: `core/schedule.py` — load/save schedule config

**Files:**
- Create: `core/schedule.py`
- Test: `tests/core/test_schedule.py`

**Interfaces:**
- Consumes: `ScheduleConfig` from `core/models.py` (Task 1)
- Produces: `load_schedule(path: str = "schedule.json") -> ScheduleConfig`, `save_schedule(config: ScheduleConfig, path: str = "schedule.json") -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/core/test_schedule.py`:

```python
from core.models import ScheduleConfig
from core.schedule import load_schedule, save_schedule


def test_load_schedule_returns_defaults_when_file_missing(tmp_path):
    path = str(tmp_path / "schedule.json")
    cfg = load_schedule(path)
    assert cfg == ScheduleConfig()


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "schedule.json")
    original = ScheduleConfig(enabled=True, interval_hours=12, topics=2, categories=["genz"])
    save_schedule(original, path)

    loaded = load_schedule(path)
    assert loaded == original


def test_save_schedule_creates_lock_file_during_write(tmp_path, mocker):
    path = str(tmp_path / "schedule.json")
    spy = mocker.patch("core.schedule.FileLock", wraps=__import__("filelock").FileLock)
    save_schedule(ScheduleConfig(), path)
    spy.assert_called_once_with(path + ".lock")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_schedule.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.schedule'`

- [ ] **Step 3: Implement**

Create `core/schedule.py`, mirroring `core/manifest.py`'s pattern exactly:

```python
from pathlib import Path
from filelock import FileLock
from core.models import ScheduleConfig

DEFAULT_PATH = "schedule.json"


def _lock_path(path: str) -> str:
    return path + ".lock"


def load_schedule(path: str = DEFAULT_PATH) -> ScheduleConfig:
    p = Path(path)
    if not p.exists():
        return ScheduleConfig()
    return ScheduleConfig.model_validate_json(p.read_text())


def save_schedule(config: ScheduleConfig, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        Path(path).write_text(config.model_dump_json(indent=2))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_schedule.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/schedule.py tests/core/test_schedule.py
git commit -m "feat: add core/schedule.py for schedule.json load/save"
```

---

## Task 3: `core/manifest.py` — `update_post_status()`

**Files:**
- Modify: `core/manifest.py`
- Test: `tests/core/test_manifest.py`

**Interfaces:**
- Consumes: `PostEntry`, `ManifestState` from `core/models.py`
- Produces: `update_post_status(slug: str, status: str, push_status: str | None = None, git_commit: str | None = None, path: str = DEFAULT_PATH) -> None` — updates an existing `PostEntry` in place; raises `ValueError` if slug not found.

- [ ] **Step 1: Write the failing test**

Append to `tests/core/test_manifest.py` (follow the existing fixture style already in that file — a `PostEntry` with `status="draft"` appended first):

```python
import pytest
from core.manifest import update_post_status


def test_update_post_status_changes_status_and_push_status(tmp_path):
    path = str(tmp_path / "manifest.json")
    post = PostEntry(
        slug="my-draft", title="t", type="prompt", category="c", topic="tp",
        status="draft", created_at=datetime.utcnow(), file_path="drafts/my-draft.md",
        source_url="http://x",
    )
    append_post(post, path)

    update_post_status("my-draft", status="published", push_status="pushed", git_commit="abc1234", path=path)

    state = load_manifest(path)
    updated = next(p for p in state.posts if p.slug == "my-draft")
    assert updated.status == "published"
    assert updated.push_status == "pushed"
    assert updated.git_commit == "abc1234"


def test_update_post_status_raises_for_unknown_slug(tmp_path):
    path = str(tmp_path / "manifest.json")
    with pytest.raises(ValueError):
        update_post_status("does-not-exist", status="published", path=path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_manifest.py -v`
Expected: FAIL — `ImportError: cannot import name 'update_post_status'`

- [ ] **Step 3: Implement**

In `core/manifest.py`, add:

```python
def update_post_status(
    slug: str,
    status: str,
    push_status: str | None = None,
    git_commit: str | None = None,
    path: str = DEFAULT_PATH,
) -> None:
    with FileLock(_lock_path(path)):
        state = load_manifest(path)
        for post in state.posts:
            if post.slug == slug:
                post.status = status
                if push_status is not None:
                    post.push_status = push_status
                if git_commit is not None:
                    post.git_commit = git_commit
                save_manifest(state, path)
                return
        raise ValueError(f"No post found with slug '{slug}'")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_manifest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/manifest.py tests/core/test_manifest.py
git commit -m "feat: add update_post_status() to core/manifest.py"
```

---

## Task 4: `GitPublisher` — draft-aware publish, `publish_draft()`, `discard_draft()`, status-returning `push()`

**Files:**
- Modify: `agents/git_publisher.py`
- Test: `tests/agents/test_git_publisher.py`

**Interfaces:**
- Consumes: `Config` from `core/config.py` (unchanged)
- Produces:
  - `GitPublisher(config, drafts_dir: str = "drafts")` — new optional constructor param
  - `publish(slug, content, post_type, draft: bool = False) -> str | None` — returns `None` when `draft=True` (no commit made); returns 7-char commit SHA otherwise (unchanged behavior when `draft=False`)
  - `publish_draft(slug, post_type, image_rel_path: str | None = None) -> tuple[str, str]` — returns `(commit_sha, push_status)`
  - `discard_draft(slug, post_type) -> None`
  - `push() -> str` — now **returns** `"pushed" | "failed" | "no_remote"` instead of only printing a warning (existing callers that ignore the return value are unaffected)

- [ ] **Step 1: Write the failing tests**

Append to `tests/agents/test_git_publisher.py` (the `git_repo` fixture already exists in this file — reuse it):

```python
def test_publish_draft_true_writes_to_drafts_dir_not_target_repo(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))

    commit_sha = publisher.publish("draft-post", "---\ntitle: d\n---\ncontent", "prompt", draft=True)

    assert commit_sha is None
    assert (drafts_dir / "content" / "prompts" / "draft-post.md").exists()
    assert not (repo_path / "content" / "prompts" / "draft-post.md").exists()
    assert repo.head.commit.message == "init\n"  # no new commit made


def test_publish_draft_promotes_file_commits_and_pushes(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))
    publisher.publish("promote-me", "---\ntitle: p\n---\ncontent", "prompt", draft=True)

    commit_sha, push_status = publisher.publish_draft("promote-me", "prompt")

    assert (repo_path / "content" / "prompts" / "promote-me.md").exists()
    assert not (drafts_dir / "content" / "prompts" / "promote-me.md").exists()
    assert commit_sha
    assert push_status == "no_remote"  # git_repo fixture has no origin remote


def test_publish_draft_raises_if_no_draft_exists(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg, drafts_dir=str(tmp_path / "drafts"))

    with pytest.raises(FileNotFoundError):
        publisher.publish_draft("never-existed", "prompt")


def test_discard_draft_deletes_file_without_git_operation(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))
    publisher.publish("reject-me", "---\ntitle: r\n---\ncontent", "prompt", draft=True)

    publisher.discard_draft("reject-me", "prompt")

    assert not (drafts_dir / "content" / "prompts" / "reject-me.md").exists()
    assert repo.head.commit.message == "init\n"


def test_push_returns_no_remote_when_origin_missing(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    assert publisher.push() == "no_remote"
```

Note: `import pytest` must already be at the top of this file — if not, add it.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/agents/test_git_publisher.py -v`
Expected: FAIL — `TypeError: publish() got an unexpected keyword argument 'draft'` and `AttributeError: 'GitPublisher' object has no attribute 'publish_draft'`

- [ ] **Step 3: Implement**

Replace `agents/git_publisher.py` in full:

```python
import shutil
from typing import Literal
from pathlib import Path
import git
from core.config import Config

DEFAULT_DRAFTS_DIR = "drafts"


class GitPublisher:
    def __init__(self, config: Config, drafts_dir: str = DEFAULT_DRAFTS_DIR):
        self.config = config
        self.repo = git.Repo(config.target_repo)
        self.drafts_dir = Path(drafts_dir)

    def _path_for(self, slug: str, post_type: Literal["prompt", "workflow"], base: Path) -> Path:
        if post_type == "prompt":
            return base / self.config.content_paths.prompts / f"{slug}.md"
        return base / self.config.content_paths.workflows / f"{slug}.md"

    def publish(
        self,
        slug: str,
        content: str,
        post_type: Literal["prompt", "workflow"],
        draft: bool = False,
    ) -> str | None:
        if draft:
            path = self._path_for(slug, post_type, self.drafts_dir)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return None

        base = Path(self.config.target_repo)
        path = self._path_for(slug, post_type, base)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        rel = str(path.relative_to(base))
        self.repo.git.add(rel)
        # Pathspec-scoped commit: only commits changes to `rel`, leaving any
        # other staged changes in the repo untouched (index.commit() would
        # have committed the whole index, sweeping in unrelated staged work).
        self.repo.git.commit("-m", f"content: add {post_type} '{slug}'", "--", rel)
        return self.repo.head.commit.hexsha[:7]

    def publish_draft(
        self,
        slug: str,
        post_type: Literal["prompt", "workflow"],
        image_rel_path: str | None = None,
    ) -> tuple[str, str]:
        draft_path = self._path_for(slug, post_type, self.drafts_dir)
        if not draft_path.exists():
            raise FileNotFoundError(f"No draft found for slug '{slug}'")

        content = draft_path.read_text(encoding="utf-8")
        commit_sha = self.publish(slug, content, post_type, draft=False)
        draft_path.unlink()

        if image_rel_path:
            draft_image = self.drafts_dir / image_rel_path
            if draft_image.exists():
                target_image = Path(self.config.target_repo) / image_rel_path
                target_image.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(draft_image), str(target_image))

        push_status = self.push()
        return commit_sha, push_status

    def discard_draft(self, slug: str, post_type: Literal["prompt", "workflow"]) -> None:
        path = self._path_for(slug, post_type, self.drafts_dir)
        if path.exists():
            path.unlink()

    def delete(self, slug: str, post_type: Literal["prompt", "workflow"]) -> str:
        path = self._path_for(slug, post_type, Path(self.config.target_repo))
        rel = str(path.relative_to(self.config.target_repo))
        self.repo.git.rm(rel)
        self.repo.git.commit("-m", f"content: remove {post_type} '{slug}'", "--", rel)
        return self.repo.head.commit.hexsha[:7]

    def repush(self, slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str:
        return self.publish(slug, content, post_type)

    def push(self) -> str:
        try:
            origin = self.repo.remotes["origin"]
        except IndexError:
            return "no_remote"
        try:
            origin.push()
            return "pushed"
        except git.exc.GitCommandError as e:
            import sys
            print(f"[ContentPilot] Warning: could not push to remote — {e}", file=sys.stderr)
            return "failed"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/agents/test_git_publisher.py -v`
Expected: PASS (all tests, including the pre-existing `test_publish_does_not_commit_unrelated_staged_changes`)

- [ ] **Step 5: Commit**

```bash
git add agents/git_publisher.py tests/agents/test_git_publisher.py
git commit -m "feat: add draft-aware publish, publish_draft, discard_draft to GitPublisher"
```

---

## Task 5: `Orchestrator.run()` — thread `draft` flag through, per-post push replaces batch push

**Files:**
- Modify: `agents/orchestrator.py`
- Test: `tests/agents/test_orchestrator.py`

**Interfaces:**
- Consumes: `GitPublisher.publish(..., draft=...)` (Task 4), `PostEntry.push_status` (Task 1)
- Produces: `Orchestrator.run(self, n_topics: int, n_prompts: int, n_workflows: int, categories: list[str], draft: bool = False) -> None`

**Design change from Phase 1:** the old code called `self.git.push()` once, after all posts were generated, as a single batch push. This meant every `PostEntry` in a run shared one undifferentiated push outcome, and a failure only printed a stderr warning (Story 4 in `STORIES.md`). This task moves the push to happen once per post, immediately after that post's commit, and records the real outcome on that post's `push_status`. Draft posts skip the push step entirely (nothing was committed to `target_repo`).

- [ ] **Step 1: Write the failing tests**

Look at the existing `tests/agents/test_orchestrator.py` fixture setup first — it already mocks `GitPublisher.publish` and `GitPublisher.push`; reuse the same `FIXTURE`/`manifest_path`/mocking pattern. Append:

```python
def test_orchestrator_draft_mode_skips_push_and_sets_status_draft(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [TopicResult(title="t", summary="s", source="hackernews", category="generative-ai", url="http://x")],
        {"hackernews": {"skipped": False, "error": None, "count": 1}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("my-slug", "content"))
    mock_publish = mocker.patch("agents.orchestrator.GitPublisher.publish", return_value=None)
    mock_push = mocker.patch("agents.orchestrator.GitPublisher.push")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path)
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"], draft=True)

    mock_publish.assert_called_once_with("my-slug", "content", "prompt", draft=True)
    mock_push.assert_not_called()

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["posts"][0]["status"] == "draft"
    assert data["posts"][0]["push_status"] is None


def test_orchestrator_live_mode_pushes_per_post_and_records_push_status(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [TopicResult(title="t", summary="s", source="hackernews", category="generative-ai", url="http://x")],
        {"hackernews": {"skipped": False, "error": None, "count": 1}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("my-slug", "content"))
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="def5678")
    mocker.patch("agents.orchestrator.GitPublisher.push", return_value="pushed")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path)
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"], draft=False)

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["posts"][0]["status"] == "published"
    assert data["posts"][0]["push_status"] == "pushed"
    assert data["posts"][0]["git_commit"] == "def5678"
```

Check the top of `tests/agents/test_orchestrator.py` for the existing `TopicResult` import — add it if not already imported (`from core.models import TopicResult`).

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/agents/test_orchestrator.py -v`
Expected: FAIL — `TypeError: run() got an unexpected keyword argument 'draft'`

- [ ] **Step 3: Implement**

In `agents/orchestrator.py`, replace `run()` and `_logged_generate()`:

```python
    def run(self, n_topics: int, n_prompts: int, n_workflows: int, categories: list[str], draft: bool = False) -> None:
        run = new_run()
        overall_status = "success"

        # ── Step 1: Trend Discovery ──────────────────────────────────────
        td_step = new_step("trend_discovery", "TrendDiscovery.run()", "agents/trend_discovery.py")
        try:
            topics, source_results = self.trend.run(categories, n_topics)
            for src, data in source_results.items():
                child = new_step(f"fetch_{src}", f"_fetch_{src}()", "agents/trend_discovery.py")
                if data["skipped"]:
                    finish_step(child, "skipped", detail="disabled in config.yaml")
                elif data["error"]:
                    finish_step(child, "failed", error=data["error"])
                    overall_status = "partial"
                else:
                    finish_step(child, "success", detail=f"{data['count']} topic(s) returned")
                td_step.children.append(child)
            finish_step(td_step, "success", detail=f"{len(topics)} topic(s) fetched")
        except Exception as e:
            topics = []
            finish_step(td_step, "failed", error=str(e))
            overall_status = "partial"
        run.steps.append(td_step)

        # ── Steps 2-4: Generate + publish per topic ──────────────────────
        for topic in topics:
            for _ in range(n_prompts):
                step = self._logged_generate(topic, "prompt", draft)
                if step.status == "failed":
                    overall_status = "partial"
                run.steps.append(step)
            for _ in range(n_workflows):
                step = self._logged_generate(topic, "workflow", draft)
                if step.status == "failed":
                    overall_status = "partial"
                run.steps.append(step)

        finish_run(run, overall_status)
        append_run(run, self.run_log_path)

    def _logged_generate(self, topic, post_type: str, draft: bool = False) -> StepLog:
        short_title = topic.title[:40] + ("…" if len(topic.title) > 40 else "")
        parent = new_step(
            f"gen_{post_type}",
            f'_generate_and_publish("{short_title}", {post_type})',
            "agents/orchestrator.py",
        )

        # ── Content generation ───────────────────────────────────────────
        cg = new_step("content_gen", "ContentGenerator.run()", "agents/content_generator.py")
        try:
            slug, content = self.content.run(topic, post_type)
            finish_step(cg, "success", detail=f"slug: {slug}")
        except Exception as e:
            finish_step(cg, "failed", error=str(e))
            parent.children.append(cg)
            print(f"[ContentPilot] content gen failed for '{topic.title}': {e}", file=sys.stderr)
            return finish_step(parent, "failed", error="content generation failed")
        parent.children.append(cg)

        # ── Image generation (prompts only) ──────────────────────────────
        image_path = None
        if post_type == "prompt" and self.image is not None:
            image_target = str(self.git.drafts_dir) if draft else self.config.target_repo
            ig = new_step("image_gen", "ImageGenerator.run()", "agents/image_generator.py")
            try:
                image_path = self.image.run(topic.title, slug, image_target)
                if image_path:
                    content = content.replace('image: ""', f'image: "/{image_path}"', 1)
                    finish_step(ig, "success", detail=image_path)
                else:
                    finish_step(ig, "failed", error="no image bytes returned by API")
            except Exception as img_err:
                finish_step(ig, "failed", error=str(img_err))
                print(f"[ContentPilot] image gen failed for '{slug}': {img_err}", file=sys.stderr)
            parent.children.append(ig)

        # ── Git publish ──────────────────────────────────────────────────
        gp = new_step("git_publish", "GitPublisher.publish()", "agents/git_publisher.py")
        try:
            commit_sha = self.git.publish(slug, content, post_type, draft=draft)
            finish_step(gp, "success", detail=f"commit: {commit_sha[:8]}" if commit_sha else "draft saved")
        except Exception as e:
            finish_step(gp, "failed", error=str(e))
            parent.children.append(gp)
            return finish_step(parent, "failed", error="git publish failed")
        parent.children.append(gp)

        # ── Git push (live posts only — drafts are never pushed) ─────────
        push_status = None
        if not draft:
            push_step = new_step("git_push", "GitPublisher.push()", "agents/git_publisher.py")
            push_status = self.git.push()
            if push_status == "pushed":
                finish_step(push_step, "success", detail="pushed to remote")
            elif push_status == "no_remote":
                finish_step(push_step, "skipped", detail="no remote configured")
            else:
                finish_step(push_step, "failed", error="push failed — see stderr")
            parent.children.append(push_step)

        # ── Manifest ─────────────────────────────────────────────────────
        content_dir = self.config.content_paths.prompts if post_type == "prompt" else self.config.content_paths.workflows
        post = PostEntry(
            slug=slug,
            title=topic.title,
            type=post_type,
            category=topic.category,
            topic=topic.title,
            status="draft" if draft else "published",
            push_status=push_status,
            created_at=datetime.now(UTC),
            file_path=f"{content_dir}/{slug}.md",
            image_path=image_path,
            source_url=topic.url,
            git_commit=commit_sha,
        )
        append_post(post, self.manifest_path)
        return finish_step(parent, "success", detail=f"{'draft saved' if draft else 'published'}: {slug}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/agents/test_orchestrator.py -v`
Expected: PASS (all tests, including pre-existing ones — the old "Step: Git push" batch-push test, if present, must be updated or removed since that code path no longer exists; check for and update any test asserting a single end-of-run `GitPublisher.push` call)

- [ ] **Step 5: Commit**

```bash
git add agents/orchestrator.py tests/agents/test_orchestrator.py
git commit -m "feat: thread draft flag through Orchestrator.run(), push per-post with tracked status"
```

---

## Task 6: `main.py` — non-interactive CLI flags

**Files:**
- Modify: `main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `Orchestrator.run(n_topics, n_prompts, n_workflows, categories, draft)` (Task 5)
- Produces: `main.py`'s Typer command accepts `--topics`, `--prompts`, `--workflows`, `--categories`, `--publish` as optional flags; interactive mode remains the default when no flags are given.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_main.py`:

```python
def test_cli_flags_bypass_interactive_prompts(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, [
        "--topics", "2", "--prompts", "1", "--workflows", "1", "--categories", "generative-ai",
    ])

    assert result.exit_code == 0
    mock_orch.run.assert_called_once_with(
        n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"], draft=True,
    )


def test_cli_publish_flag_sets_draft_false(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, [
        "--topics", "1", "--prompts", "1", "--workflows", "0", "--categories", "all", "--publish",
    ])

    assert result.exit_code == 0
    _, kwargs = mock_orch.run.call_args
    assert kwargs["draft"] is False


def test_cli_negative_topics_fails_fast(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, ["--topics", "-1", "--prompts", "1", "--workflows", "0"])

    assert result.exit_code != 0
    mock_orch.run.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/test_main.py -v`
Expected: FAIL — `Error: No such option: --topics` (Typer rejects the unknown flags)

- [ ] **Step 3: Implement**

Replace `main.py` in full:

```python
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel
from agents.orchestrator import Orchestrator

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    topics: Optional[int] = typer.Option(None, "--topics", min=0, help="Number of trending topics"),
    prompts: Optional[int] = typer.Option(None, "--prompts", min=0, help="Prompt posts per topic"),
    workflows: Optional[int] = typer.Option(None, "--workflows", min=0, help="Workflow posts per topic"),
    categories: Optional[str] = typer.Option(None, "--categories", help="Comma-separated categories, or 'all'"),
    publish: bool = typer.Option(False, "--publish", help="Publish immediately instead of saving as drafts"),
):
    non_interactive = topics is not None or prompts is not None or workflows is not None or categories is not None

    if non_interactive:
        if topics is None or prompts is None or workflows is None:
            console.print("[bold red]Error:[/bold red] --topics, --prompts, and --workflows are all required together in non-interactive mode.")
            raise typer.Exit(code=1)
        n_topics, n_prompts, n_workflows = topics, prompts, workflows
        categories_list = [c.strip() for c in (categories or "all").split(",")]
    else:
        console.print(Panel.fit("[bold yellow]ContentPilot[/bold yellow] — AI Content Agent", border_style="yellow"))
        n_topics = IntPrompt.ask("\nHow many trending topics today")
        n_prompts = IntPrompt.ask("Prompts per topic [bold](with image)[/bold]")
        n_workflows = IntPrompt.ask("Workflows per topic")
        categories_raw = Prompt.ask(
            "Categories [dim](generative-ai, genz, photography, or all)[/dim]",
            default="all",
        )
        categories_list = [c.strip() for c in categories_raw.split(",")]

    console.print(f"\n[green]Fetching {n_topics} trending topics...[/green]")

    orch = Orchestrator()
    orch.run(
        n_topics=n_topics,
        n_prompts=n_prompts,
        n_workflows=n_workflows,
        categories=categories_list,
        draft=not publish,
    )

    mode = "published" if publish else "saved as drafts — review at http://localhost:8000/drafts"
    console.print(f"\n[bold green]Done![/bold green] Content {mode}.")


if __name__ == "__main__":
    app()
```

Note: `typer.Option(..., min=0)` makes Typer reject negative integers with a non-zero exit before `Orchestrator` is even constructed, satisfying `test_cli_negative_topics_fails_fast`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/test_main.py -v`
Expected: PASS (all tests, including the pre-existing interactive-mode tests — verify `test_cli_invokes_orchestrator` and `test_cli_handles_all_categories` still pass; they call `Orchestrator.run` without `draft=`, so update those two pre-existing assertions to include `draft=True` since interactive mode now always saves drafts by default)

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add non-interactive CLI flags to main.py"
```

---

## Task 7: `requirements.txt` — add APScheduler

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add the dependency**

In `requirements.txt`, under the `# Dashboard` section, add:

```
apscheduler>=3.10
```

- [ ] **Step 2: Install and verify**

Run: `.venv/bin/pip install apscheduler>=3.10`
Expected: Successful install, no conflicts with existing pinned versions

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add apscheduler dependency"
```

---

## Task 8: Dashboard — `/drafts` routes (list, approve, reject)

**Files:**
- Modify: `dashboard/server.py`
- Create: `dashboard/templates/drafts.html`
- Test: `tests/dashboard/test_server.py`

**Interfaces:**
- Consumes: `GitPublisher.publish_draft()`, `.discard_draft()` (Task 4); `update_post_status()`, `delete_post()` (Task 3, existing)
- Produces: `GET /drafts`, `POST /api/drafts/{slug}/approve`, `POST /api/drafts/{slug}/reject`

- [ ] **Step 1: Write the failing tests**

Check `tests/dashboard/test_server.py`'s existing top-of-file fixtures (`client`, manifest patching pattern used by `test_index_returns_200` etc.) and follow the same style. Append:

```python
def test_drafts_page_returns_200(client, mocker):
    mocker.patch("dashboard.server.load_manifest", return_value=ManifestState(posts=[
        PostEntry(
            slug="draft-1", title="Draft One", type="prompt", category="generative-ai",
            topic="AI trends", status="draft", created_at=datetime.utcnow(),
            file_path="content/prompts/draft-1.md", source_url="http://x",
        ),
    ]))
    mocker.patch("dashboard.server._read_file", return_value="---\ntitle: x\n---\nbody")

    response = client.get("/drafts")
    assert response.status_code == 200


def test_approve_draft_calls_publish_draft_and_updates_status(client, mocker):
    mocker.patch("dashboard.server.load_manifest", return_value=ManifestState(posts=[
        PostEntry(
            slug="draft-1", title="Draft One", type="prompt", category="generative-ai",
            topic="AI trends", status="draft", created_at=datetime.utcnow(),
            file_path="content/prompts/draft-1.md", source_url="http://x",
        ),
    ]))
    mock_publish_draft = mocker.patch(
        "dashboard.server.GitPublisher.publish_draft", return_value=("abc1234", "pushed")
    )
    mock_update = mocker.patch("dashboard.server.update_post_status")

    response = client.post("/api/drafts/draft-1/approve")

    assert response.status_code == 200
    mock_publish_draft.assert_called_once()
    mock_update.assert_called_once_with(
        "draft-1", status="published", push_status="pushed", git_commit="abc1234", path="manifest.json"
    )


def test_reject_draft_discards_and_deletes_manifest_entry(client, mocker):
    mocker.patch("dashboard.server.load_manifest", return_value=ManifestState(posts=[
        PostEntry(
            slug="draft-1", title="Draft One", type="prompt", category="generative-ai",
            topic="AI trends", status="draft", created_at=datetime.utcnow(),
            file_path="content/prompts/draft-1.md", source_url="http://x",
        ),
    ]))
    mock_discard = mocker.patch("dashboard.server.GitPublisher.discard_draft")
    mock_delete = mocker.patch("dashboard.server.delete_post")

    response = client.post("/api/drafts/draft-1/reject")

    assert response.status_code == 200
    mock_discard.assert_called_once_with("draft-1", "prompt")
    mock_delete.assert_called_once()


def test_approve_unknown_draft_returns_404(client, mocker):
    mocker.patch("dashboard.server.load_manifest", return_value=ManifestState(posts=[]))
    response = client.post("/api/drafts/nope/approve")
    assert response.status_code == 404
```

Check the top of the test file for existing imports (`ManifestState`, `PostEntry`, `datetime`) — add any missing ones matching the existing style.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v -k draft`
Expected: FAIL — `404 Not Found` on `/drafts` (route doesn't exist yet)

- [ ] **Step 3: Implement**

In `dashboard/server.py`, add the import and three routes. First, update imports:

```python
from core.manifest import load_manifest, delete_post, update_post_status
```

Then add routes after the existing `/pipeline` route and before `/api/delete/{slug}`:

```python
@app.get("/drafts")
async def drafts_page(request: Request):
    state = load_manifest(MANIFEST_PATH)
    drafts = [p for p in state.posts if p.status == "draft"]
    items = []
    for post in drafts:
        content = _read_draft_file(post.file_path)
        items.append({
            "slug": post.slug,
            "title": post.title,
            "type": post.type,
            "category": post.category,
            "image_path": post.image_path,
            "source_url": post.source_url,
            "created_at": post.created_at,
            "preview": _preview(content),
        })
    return templates.TemplateResponse(request, "drafts.html", {"drafts": items, "total": len(items)})


@app.post("/api/drafts/{slug}/approve")
async def approve_draft(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug and p.status == "draft"), None)
    if not post:
        raise HTTPException(status_code=404, detail="Draft not found")
    publisher = GitPublisher(_config)
    commit_sha, push_status = publisher.publish_draft(slug, post.type, post.image_path)
    update_post_status(slug, status="published", push_status=push_status, git_commit=commit_sha, path=MANIFEST_PATH)
    return JSONResponse({"status": "published", "slug": slug, "commit": commit_sha, "push_status": push_status})


@app.post("/api/drafts/{slug}/reject")
async def reject_draft(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug and p.status == "draft"), None)
    if not post:
        raise HTTPException(status_code=404, detail="Draft not found")
    publisher = GitPublisher(_config)
    publisher.discard_draft(slug, post.type)
    delete_post(slug, MANIFEST_PATH)
    return JSONResponse({"status": "rejected", "slug": slug})
```

Add the helper `_read_draft_file`, right after the existing `_read_file`:

```python
def _read_draft_file(file_path: str) -> str:
    p = Path("drafts") / file_path
    return p.read_text() if p.exists() else ""
```

Create `dashboard/templates/drafts.html`:

```html
{% extends "base.html" %}
{% block content %}
<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:1.2rem;">
  <h2 style="font-size:1rem;color:#888;text-transform:uppercase;letter-spacing:.05em;">Pending Drafts</h2>
  <span style="font-size:.8rem;color:#555;">{{ total }} awaiting review</span>
</div>

{% if not drafts %}
  <p class="empty-state">No drafts waiting. Run a non-interactive pipeline or a scheduled job to generate some.</p>
{% else %}
  <div class="cards-row">
    {% for post in drafts %}
    <div class="content-card type-{{ post.type }}">
      <div class="card-badges">
        <span class="badge badge-{{ post.type }}">{{ post.type }}</span>
        <span class="badge badge-draft">draft</span>
      </div>
      <div class="card-title">{{ post.title }}</div>
      {% if post.type == "prompt" and post.image_path %}
        <img src="/drafts/{{ post.image_path }}" alt="{{ post.title }}" class="card-image" />
      {% endif %}
      {% if post.preview %}
        <div class="card-preview">{{ post.preview }}</div>
      {% endif %}
      <div class="card-footer" style="gap:.6rem;">
        <button onclick="approveDraft('{{ post.slug }}')" style="background:#15803d;color:#fff;border:none;padding:.4rem .8rem;border-radius:4px;cursor:pointer;">Approve</button>
        <button onclick="rejectDraft('{{ post.slug }}')" style="background:#b91c1c;color:#fff;border:none;padding:.4rem .8rem;border-radius:4px;cursor:pointer;">Reject</button>
        <span class="card-date">{{ post.created_at.strftime('%b %d, %H:%M') }}</span>
      </div>
    </div>
    {% endfor %}
  </div>
{% endif %}

<script>
async function approveDraft(slug) {
  const res = await fetch(`/api/drafts/${slug}/approve`, { method: "POST" });
  if (res.ok) location.reload();
  else alert("Approve failed — check server logs.");
}
async function rejectDraft(slug) {
  const res = await fetch(`/api/drafts/${slug}/reject`, { method: "POST" });
  if (res.ok) location.reload();
  else alert("Reject failed — check server logs.");
}
</script>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.py dashboard/templates/drafts.html tests/dashboard/test_server.py
git commit -m "feat: add /drafts dashboard page with approve/reject actions"
```

---

## Task 9: Dashboard — `/run-now` route

**Files:**
- Modify: `dashboard/server.py`
- Test: `tests/dashboard/test_server.py`

**Interfaces:**
- Consumes: `Orchestrator.run(n_topics, n_prompts, n_workflows, categories, draft)` (Task 5)
- Produces: `POST /api/run-now`, request body `{topics, prompts, workflows, categories, publish}`, returns immediately without waiting for the run to finish

- [ ] **Step 1: Write the failing test**

Append to `tests/dashboard/test_server.py`:

```python
def test_run_now_starts_orchestrator_and_returns_immediately(client, mocker):
    mock_orch_class = mocker.patch("dashboard.server.Orchestrator")
    mock_executor = mocker.patch("dashboard.server.asyncio.get_event_loop")

    response = client.post("/api/run-now", json={
        "topics": 2, "prompts": 1, "workflows": 1, "categories": ["all"], "publish": False,
    })

    assert response.status_code == 200
    assert response.json()["status"] == "started"
    mock_executor.return_value.run_in_executor.assert_called_once()


def test_run_now_rejects_negative_topics(client):
    response = client.post("/api/run-now", json={
        "topics": -1, "prompts": 1, "workflows": 1, "categories": ["all"], "publish": False,
    })
    assert response.status_code == 422
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v -k run_now`
Expected: FAIL — `404 Not Found`

- [ ] **Step 3: Implement**

In `dashboard/server.py`, add imports:

```python
import asyncio
from pydantic import BaseModel, Field
from agents.orchestrator import Orchestrator
```

Add a request model and route, after the `/drafts` routes:

```python
class RunNowRequest(BaseModel):
    topics: int = Field(ge=0)
    prompts: int = Field(ge=0)
    workflows: int = Field(ge=0)
    categories: list[str]
    publish: bool = False


@app.post("/api/run-now")
async def run_now(payload: RunNowRequest):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")

    def _execute():
        orch = Orchestrator()
        orch.run(
            n_topics=payload.topics,
            n_prompts=payload.prompts,
            n_workflows=payload.workflows,
            categories=payload.categories,
            draft=not payload.publish,
        )

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _execute)
    return JSONResponse({"status": "started"})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.py tests/dashboard/test_server.py
git commit -m "feat: add /api/run-now route, executes pipeline off the event loop"
```

---

## Task 10: Dashboard — `AsyncIOScheduler` + `/schedule` routes

**Files:**
- Modify: `dashboard/server.py`
- Create: `dashboard/templates/schedule.html`
- Test: `tests/dashboard/test_server.py`

**Interfaces:**
- Consumes: `load_schedule()`, `save_schedule()` (Task 2), `ScheduleConfig` (Task 1), `Orchestrator.run()` (Task 5)
- Produces: `GET /schedule`, `POST /api/schedule`; an `AsyncIOScheduler` instance (module-level `scheduler`) started on FastAPI startup

- [ ] **Step 1: Write the failing tests**

Append to `tests/dashboard/test_server.py`:

```python
def test_schedule_page_returns_200(client, mocker):
    mocker.patch("dashboard.server.load_schedule", return_value=ScheduleConfig())
    response = client.get("/schedule")
    assert response.status_code == 200


def test_update_schedule_saves_config_and_reschedules(client, mocker):
    mock_save = mocker.patch("dashboard.server.save_schedule")
    mock_reschedule = mocker.patch("dashboard.server._reschedule")

    response = client.post("/api/schedule", json={
        "enabled": True, "interval_hours": 12, "topics": 2, "prompts": 1,
        "workflows": 1, "categories": ["all"], "publish": False,
    })

    assert response.status_code == 200
    mock_save.assert_called_once()
    mock_reschedule.assert_called_once()


def test_scheduled_run_skips_when_disabled(mocker):
    from dashboard.server import _scheduled_run
    mocker.patch("dashboard.server.load_schedule", return_value=ScheduleConfig(enabled=False))
    mock_orch_class = mocker.patch("dashboard.server.Orchestrator")

    _scheduled_run()

    mock_orch_class.assert_not_called()


def test_scheduled_run_invokes_orchestrator_when_enabled(mocker):
    from dashboard.server import _scheduled_run
    cfg = ScheduleConfig(enabled=True, interval_hours=6, topics=1, prompts=1, workflows=0, categories=["all"], publish=False)
    mocker.patch("dashboard.server.load_schedule", return_value=cfg)
    mock_orch = mocker.patch("dashboard.server.Orchestrator").return_value

    _scheduled_run()

    mock_orch.run.assert_called_once_with(
        n_topics=1, n_prompts=1, n_workflows=0, categories=["all"], draft=True,
    )
```

Add `from core.models import ScheduleConfig` to the test file's imports if not already present.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v -k schedule`
Expected: FAIL — `404 Not Found` on `/schedule`, `ImportError` for `_scheduled_run`

- [ ] **Step 3: Implement**

In `dashboard/server.py`, add imports:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.schedule import load_schedule, save_schedule
from core.models import ScheduleConfig
```

Add the scheduler instance and helpers, near the top-level `app = FastAPI(...)` line:

```python
scheduler = AsyncIOScheduler()


def _scheduled_run() -> None:
    cfg = load_schedule()
    if not cfg.enabled:
        return
    try:
        orch = Orchestrator()
        orch.run(
            n_topics=cfg.topics,
            n_prompts=cfg.prompts,
            n_workflows=cfg.workflows,
            categories=cfg.categories,
            draft=not cfg.publish,
        )
    except Exception as e:
        # A scheduled run must never take the schedule down with it — log and
        # let the next interval fire normally. Orchestrator.run() already
        # catches and logs per-step failures into run_log.json; this is the
        # outer guard for anything that escapes that (e.g. a bad config).
        import sys
        print(f"[ContentPilot] Scheduled run failed: {e}", file=sys.stderr)


def _reschedule() -> None:
    scheduler.remove_all_jobs()
    cfg = load_schedule()
    if cfg.enabled:
        scheduler.add_job(_scheduled_run, "interval", hours=cfg.interval_hours, id="contentpilot_schedule")


@app.on_event("startup")
async def _on_startup() -> None:
    scheduler.start()
    _reschedule()
```

Add the routes, after the `/api/run-now` route:

```python
@app.get("/schedule")
async def schedule_page(request: Request):
    cfg = load_schedule()
    return templates.TemplateResponse(request, "schedule.html", {"cfg": cfg})


@app.post("/api/schedule")
async def update_schedule(cfg: ScheduleConfig):
    save_schedule(cfg)
    _reschedule()
    return JSONResponse({"status": "saved"})
```

Create `dashboard/templates/schedule.html`:

```html
{% extends "base.html" %}
{% block content %}
<div style="max-width:480px;">
  <h2 style="font-size:1rem;color:#888;text-transform:uppercase;letter-spacing:.05em;margin-bottom:1.2rem;">Scheduled Runs</h2>

  <form id="schedule-form" style="display:flex;flex-direction:column;gap:.8rem;">
    <label style="display:flex;align-items:center;gap:.5rem;">
      <input type="checkbox" id="enabled" {% if cfg.enabled %}checked{% endif %} /> Enabled
    </label>
    <label>Interval (hours)
      <input type="number" id="interval_hours" value="{{ cfg.interval_hours }}" min="1" style="width:100%;padding:.4rem;background:#1a1a1a;color:#e5e5e5;border:1px solid #333;border-radius:4px;" />
    </label>
    <label>Topics per run
      <input type="number" id="topics" value="{{ cfg.topics }}" min="0" style="width:100%;padding:.4rem;background:#1a1a1a;color:#e5e5e5;border:1px solid #333;border-radius:4px;" />
    </label>
    <label>Prompts per topic
      <input type="number" id="prompts" value="{{ cfg.prompts }}" min="0" style="width:100%;padding:.4rem;background:#1a1a1a;color:#e5e5e5;border:1px solid #333;border-radius:4px;" />
    </label>
    <label>Workflows per topic
      <input type="number" id="workflows" value="{{ cfg.workflows }}" min="0" style="width:100%;padding:.4rem;background:#1a1a1a;color:#e5e5e5;border:1px solid #333;border-radius:4px;" />
    </label>
    <label>Categories (comma-separated, or "all")
      <input type="text" id="categories" value="{{ cfg.categories | join(', ') }}" style="width:100%;padding:.4rem;background:#1a1a1a;color:#e5e5e5;border:1px solid #333;border-radius:4px;" />
    </label>
    <label style="display:flex;align-items:center;gap:.5rem;">
      <input type="checkbox" id="publish" {% if cfg.publish %}checked{% endif %} /> Publish immediately (skip drafts queue)
    </label>
    <button type="submit" style="background:#facc15;color:#1a1a1a;border:none;padding:.6rem;border-radius:4px;font-weight:600;cursor:pointer;">Save</button>
  </form>
  <p id="save-status" style="margin-top:.6rem;color:#15803d;"></p>
</div>

<script>
document.getElementById("schedule-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    enabled: document.getElementById("enabled").checked,
    interval_hours: parseInt(document.getElementById("interval_hours").value, 10),
    topics: parseInt(document.getElementById("topics").value, 10),
    prompts: parseInt(document.getElementById("prompts").value, 10),
    workflows: parseInt(document.getElementById("workflows").value, 10),
    categories: document.getElementById("categories").value.split(",").map(s => s.trim()),
    publish: document.getElementById("publish").checked,
  };
  const res = await fetch("/api/schedule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  document.getElementById("save-status").textContent = res.ok ? "Saved." : "Save failed.";
});
</script>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.py dashboard/templates/schedule.html tests/dashboard/test_server.py
git commit -m "feat: add AsyncIOScheduler and /schedule dashboard page"
```

---

## Task 11: Dashboard nav + push_status badges on existing pages

**Files:**
- Modify: `dashboard/templates/base.html`
- Modify: `dashboard/templates/index.html`
- Modify: `dashboard/templates/post.html`

**Interfaces:**
- Consumes: `PostEntry.push_status` (Task 1)

- [ ] **Step 1: Add nav links**

In `dashboard/templates/base.html`, update the `<nav>` block:

```html
  <nav>
    <span class="brand">ContentPilot</span>
    <a href="/">All Posts</a>
    <a href="/drafts">📝 Drafts</a>
    <a href="/schedule">⏰ Schedule</a>
    <a href="/pipeline" class="nav-pipeline">⚙ Pipeline</a>
  </nav>
```

- [ ] **Step 2: Show push_status on the post card footer**

In `dashboard/templates/index.html`, inside the `card-footer` div (after the existing `card-date` span), add:

```html
        <div class="card-footer">
          <a href="/post/{{ post.slug }}" class="card-link">View full →</a>
          <span class="card-date">{{ post.created_at.strftime('%b %d, %H:%M') }}</span>
        </div>
```

becomes:

```html
        <div class="card-footer">
          <a href="/post/{{ post.slug }}" class="card-link">View full →</a>
          <span class="card-date">{{ post.created_at.strftime('%b %d, %H:%M') }}</span>
        </div>
        {% if post.push_status %}
        <div style="font-size:.72rem;margin-top:.3rem;color:{% if post.push_status == 'pushed' %}#4ade80{% elif post.push_status == 'no_remote' %}#facc15{% else %}#f87171{% endif %};">
          push: {{ post.push_status }}
        </div>
        {% endif %}
```

(You must locate the exact existing block by searching for `card-footer` in `dashboard/templates/index.html` — it currently spans two lines with `<a href="/post/...">` and `<span class="card-date">`; also add `"push_status": post.push_status,` to the dict built in `dashboard/server.py`'s `index()` route, next to the existing `"git_commit": post.git_commit,` line.)

- [ ] **Step 3: Show push_status on the post detail page**

In `dashboard/templates/post.html`, in the metadata `<p>` block that already shows the commit SHA (the line with `{% if post.git_commit %}`), append right after that conditional:

```html
    <p style="color:#555;font-size:.82rem;margin-bottom:1.2rem;">
      {{ post.created_at.strftime('%Y-%m-%d %H:%M UTC') }}
      {% if post.git_commit %} · commit <code style="background:#1a1a1a;padding:1px 5px;border-radius:3px;font-size:.8rem;">{{ post.git_commit[:8] }}</code>{% endif %}
      {% if post.push_status %} · push: <span style="color:{% if post.push_status == 'pushed' %}#4ade80{% elif post.push_status == 'no_remote' %}#facc15{% else %}#f87171{% endif %};">{{ post.push_status }}</span>{% endif %}
    </p>
```

- [ ] **Step 4: Run the full test suite to check for template regressions**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest -q`
Expected: PASS (39+ tests — templates aren't unit tested directly, but `test_index_returns_200` and `test_post_detail_returns_200` will fail loudly on a Jinja2 syntax error)

- [ ] **Step 5: Commit**

```bash
git add dashboard/templates/base.html dashboard/templates/index.html dashboard/templates/post.html dashboard/server.py
git commit -m "feat: add Drafts/Schedule nav links and push_status display"
```

---

## Task 12: Full suite check, README, and NEXT_STEPS.md cleanup

**Files:**
- Modify: `README.md`
- Modify: `NEXT_STEPS.md`
- Modify: `PROGRESS_TRACKER.md`

- [ ] **Step 1: Run the entire test suite one final time**

Run: `PYTHONPATH=. .venv/bin/python3 -m pytest -v`
Expected: PASS — every test across `tests/core/`, `tests/agents/`, `tests/dashboard/`, `tests/test_main.py`

- [ ] **Step 2: Update `README.md`'s "Running the Agent" section**

Add a subsection documenting flag-mode usage and a cron example:

```markdown
### Non-Interactive / Scheduled Mode

For cron, systemd timers, or any headless invocation, pass flags instead of answering prompts:

\`\`\`bash
python main.py --topics 3 --prompts 1 --workflows 1 --categories all
\`\`\`

By default this saves generated posts as **drafts** — nothing is pushed to your target repo
until you approve them at http://localhost:8000/drafts. Add `--publish` to publish immediately
instead, matching Phase 1's original behavior.

Example crontab entry (runs daily at 6 AM):

\`\`\`
0 6 * * * cd /path/to/contentpilot && .venv/bin/python main.py --topics 3 --prompts 1 --workflows 1 >> cron.log 2>&1
\`\`\`

Alternatively, enable the dashboard's built-in scheduler at http://localhost:8000/schedule —
no cron entry needed, as long as the dashboard process (`python -m uvicorn dashboard.server:app`)
stays running.
```

Update the Project Structure tree to add `drafts/` (auto-created, git-ignored) and `schedule.json` (auto-created) alongside the existing `manifest.json`/`run_log.json` entries in the "Files That Are Auto-Created at Runtime" table.

- [ ] **Step 3: Update `PROGRESS_TRACKER.md`**

Change the Phase 4 row from "🚧 In design" to "✅ Complete", and add one line noting the design change from the spec (per-post push instead of batch push) if it wasn't already anticipated in the spec text.

- [ ] **Step 4: Update `NEXT_STEPS.md`**

Check off every item in the "Pending — not yet implemented" section that this plan completed. Move the "Manual verification" checklist items to the top as the only remaining unchecked work, since those are inherently manual (cannot be completed by an automated task).

- [ ] **Step 5: Commit**

```bash
git add README.md PROGRESS_TRACKER.md NEXT_STEPS.md
git commit -m "docs: document Phase 4 non-interactive/scheduling/draft workflow"
```

---

## Manual Verification (do after Task 12, not automated)

These come directly from `NEXT_STEPS.md` and the spec's Section 6 — run them against a disposable target repo (see `README.md`'s "Testing manually against a throwaway repo" section), never against a live site, until you've confirmed the flow end-to-end:

1. Cron-style run: `python main.py --topics 1 --prompts 1 --workflows 0 --categories all` with zero keyboard input — confirm it produces a `draft` entry, no commit in the target repo.
2. Dashboard-triggered run: POST to `/api/run-now`, then approve the resulting draft at `/drafts` — confirm the commit lands in the disposable target repo and, if a remote exists, actually pushes.
3. Reject a draft — confirm the target repo is completely untouched (no commit, no file).
4. Enable the schedule at `/schedule` with a short `interval_hours` for testing, confirm `_scheduled_run` fires without manual intervention (check `run_log.json` for the new run entry).
