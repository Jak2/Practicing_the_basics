# ContentPilot — Decisions & Issues

> Last updated: 2026-07-02
> Source: Code audit (brainstorming session — cleanup goal: Option B); BUG-3 found and fixed
> during manual end-to-end testing ahead of the v1.1 (scheduling + drafts) design work.

This file tracks known bugs, dead code, code smells, and open design decisions.
It is separate from PROGRESS_TRACKER.md, which tracks features. This file tracks quality.

---

## Fixed Bugs

### BUG-3 (Fixed 2026-07-02): `publish()`/`delete()` committed the entire git index, not just the target file

**File:** `agents/git_publisher.py`
**Severity:** High — could push unrelated, unreviewed changes to a live repo.

`GitPublisher.publish()` called `self.repo.index.add([path])` followed by
`self.repo.index.commit(message)`. `index.commit()` commits **everything currently staged**,
not just the file that was just added. If the target repo had other files staged (e.g. work
in progress unrelated to ContentPilot), a routine content run would silently sweep them into
the `content: add ...` commit and push them live.

**Fix:** Switched to pathspec-scoped commits — `repo.git.add(rel)` then
`repo.git.commit("-m", msg, "--", rel)` — which only commits changes to the specified path,
regardless of what else is staged. Same pattern applied to `delete()`. Added a regression test,
`test_publish_does_not_commit_unrelated_staged_changes`, in `tests/agents/test_git_publisher.py`.

**Also fixed in the same pass:** renamed `PostEntry.status` value `"pushed"` → `"published"`
(and added `"draft"` to the `Literal`, in preparation for the drafts feature — see
PROGRESS_TRACKER.md Phase 4) for clarity: `draft → published → deleted/failed` reads as a
lifecycle, whereas `pushed` read as an action rather than a state. Updated all call sites,
dashboard templates, and tests; full suite (39 tests) passes.

---

## Current Bugs

These are broken at runtime and should be fixed first.

### BUG-1: HackerNews exceptions silently swallowed

**File:** `agents/trend_discovery.py` → `_fetch_hackernews()`
**Severity:** Medium

`_fetch_hackernews()` has its own inner `try/except` that returns `[]` on any error.
The outer `try/except` in `TrendDiscovery.run()` never fires for HackerNews failures.
Result: `source_results["hackernews"]` always shows success even when HackerNews is
completely unreachable. The dashboard Pipeline page will show a green step for a failed fetch.

**Fix:** Remove the inner `try/except` from `_fetch_hackernews()`. Let exceptions propagate
to the outer handler in `run()`, which already handles them correctly.

---

### BUG-2: ImageGenerator initializes unconditionally regardless of provider

**File:** `agents/orchestrator.py` → `__init__()`
**Severity:** Medium

`self.image = ImageGenerator(self.config)` is called in `Orchestrator.__init__()` regardless
of `config.llm.provider`. When `provider: ollama`, this still calls `genai.configure()` and
loads the Imagen model. If `GEMINI_API_KEY` is absent or empty, this can crash at startup —
before any content is even attempted.

**Fix:** Make `ImageGenerator` initialization lazy. Only instantiate it inside
`_logged_generate()` when `post_type == "prompt"` and `provider == "google"`. Or add a guard
in `Orchestrator.__init__()`: `self.image = ImageGenerator(self.config) if self.config.llm.provider == "google" else None`.

---

## Dead Code

Safe to delete. These have no callers and no path to future use.

### DEAD-1: `update_post()` in manifest.py — never called

**File:** `core/manifest.py`

`update_post()` exists to change a post's status from "pending" to "pushed", but posts are
always created with `status="pushed"` directly (in orchestrator.py). The "pending" state was
never implemented in practice.

**Fix:** Delete `update_post()` from `manifest.py` and remove "pending" from the
`status: Literal[...]` in `core/models.py` `PostEntry`.

---

### DEAD-2: `status: "pending"` on PostEntry — never used

**File:** `core/models.py` → `PostEntry`

Companion to DEAD-1. The `"pending"` literal in `PostEntry.status` has never been assigned
anywhere in the codebase.

**Fix:** Remove `"pending"` from `Literal["pending", "pushed", "deleted", "failed"]`.

---

### DEAD-3: `pydantic-settings` in requirements.txt — never imported

**File:** `requirements.txt`

`pydantic-settings>=2.0` is listed but never imported. The config system uses plain PyYAML +
Pydantic `BaseModel`, not `pydantic-settings`. Adds ~2MB to the venv for nothing.

**Fix:** Remove the line.

---

### DEAD-4: `httpx` listed twice in requirements.txt

**File:** `requirements.txt`

`httpx>=0.27` appears at line 9 (trend discovery) and again at line 37 (dashboard test
client). Harmless but confusing.

**Fix:** Remove the duplicate.

---

## Code Smells

These work, but make the code harder to understand, extend, or test correctly.

### SMELL-1: `_ImageGenerationModel` shim in image_generator.py

**File:** `agents/image_generator.py`
**Lines:** ~31–53 (the wrapper class + monkey-patch)

A 30-line wrapper class + a multi-paragraph comment block exist entirely to avoid updating
2 lines of test mock targets. The shim patches `genai.ImageGenerationModel` with a custom
class so tests can keep patching `genai.ImageGenerationModel.from_pretrained` — even though
the real code now uses `google.genai.Client`.

This is technical debt masquerading as a design pattern.

**Fix:** Delete the shim. Rewrite `ImageGenerator` to use `google.genai.Client` directly.
Update the 2 test mock targets in `tests/agents/test_image_generator.py` to patch
`google.genai.Client.models.generate_images` instead.

---

### SMELL-2: `source_results` as a mutable side-effect on TrendDiscovery

**File:** `agents/trend_discovery.py` and `agents/orchestrator.py`

`TrendDiscovery.run()` populates `self.source_results` as a side effect, then the
orchestrator reads `self.trend.source_results` after `run()` returns. This is an implicit
communication channel through shared state.

Problems:
- Calling `run()` twice in one session silently clobbers the first results
- The orchestrator has to "know" to read the attribute after calling `run()`
- Makes TrendDiscovery harder to test in isolation

**Fix:** Return source metadata from `run()` alongside the topics list. Change the return
type to a named tuple or small dataclass: `(topics: list[TopicResult], source_results: dict)`.
Orchestrator reads from the return value, not from instance state.

---

### SMELL-3: `categories` parameter is half-implemented

**Files:** `main.py`, `agents/orchestrator.py`, `agents/trend_discovery.py`

The CLI asks for categories, the orchestrator passes them to `trend.run()`, which passes them
to `_fetch_tavily()` — but `_fetch_reddit()` and `_fetch_hackernews()` ignore the parameter
entirely. HackerNews hardcodes `category="tech"`. Reddit uses the subreddit name as category.

This creates a false impression that categories filter across all sources. They only filter
Tavily. The parameter is threaded through 3 layers for partial effect.

**Fix (chosen — Option B):** Remove `categories` from the signatures of `_fetch_reddit()`
and `_fetch_hackernews()` since they can't use it. Each method sets its own hardcoded category
(`sub_name.lower()` for Reddit, `"tech"` for HackerNews). The `categories` parameter stays
on `_fetch_tavily()` and `run()` — it just stops pretending to affect the other sources.

---

## Open Design Decisions

These are questions where a decision needs to be made before implementation.

### DECISION-1: FileLock on manifest and run_log

**Files:** `core/manifest.py`, `core/run_log.py`

Both use `filelock.FileLock` to prevent concurrent writes. ContentPilot is a single-process
CLI tool — there is no concurrency. The locks add ~1 dependency for a problem that doesn't
exist yet.

**Options:**
- Keep them (harmless, and protects against a future scheduler or parallel invocation)
- Remove them (simpler, and honest about the current use case)

**Status:** Undecided. Currently leaning toward keeping — they're harmless and the intent
is clear. Revisit if a scheduler (Phase 3 future work) is added.

---

### DECISION-2: HackerNews summary is just a copy of the title

**File:** `agents/trend_discovery.py` → `_fetch_hackernews()`

```python
summary=item.get("title", ""),  # same as title — no real summary
```

HackerNews stories don't have body text in the API (they're links to external articles).
So there's genuinely nothing to use as a summary. ContentGenerator's prompt receives the
title twice — as `{title}` and as `{summary}`.

**Options:**
- Accept it — phi3:mini and Gemini both generate reasonable content from title alone
- Fetch the linked article's metadata via a HEAD request + OG tags for a real summary
- Use the HN comment thread description as a proxy

**Status:** Accepted as-is for now. Fetching article metadata would require an extra HTTP
call per story and added parsing logic. Not worth it for a local tool.

---

## Chosen Cleanup Scope: Option B

From the audit session (2026-06-27), the agreed cleanup approach is **Option B**:

- Fix BUG-1 and BUG-2
- Delete DEAD-1 through DEAD-4
- Fix SMELL-1 (remove shim, update tests)
- Fix SMELL-2 (return source_results from run() instead of side-effect)
- Fix SMELL-3 (remove categories from HN/Reddit fetch signatures)

**Not in scope for this cleanup:**
- FileLock removal (DECISION-1 — keep for now)
- HackerNews summary improvement (DECISION-2 — accepted as-is)
- run_log simplification (the Pydantic model + dashboard serves a real purpose)
