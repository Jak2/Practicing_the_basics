# ContentPilot 2.0 — Viral Prompt Trend Engine

Everything ContentPilot 1.0 does (autonomous content pipeline: discover → generate → draft →
approve → git publish, with dashboard + scheduler), **plus a trend-intelligence layer**: it
pulls viral AI prompts from live sources, ranks them with an explainable virality score, uses
an LLM to extract *why each prompt works* (pattern tags + analysis), and turns any trend into
a publishable post — all controlled from one dashboard.

## 2-Minute Demo Script (for interviews)

```bash
cd contentPilot2.0 && source .venv/bin/activate

# 1. One command: fetch viral prompts, score them, LLM-analyze them   (~60s)
PYTHONPATH=. python main.py trends --sources promptschat,civitai --top 15

# 2. Dashboard
PYTHONPATH=. python -m uvicorn dashboard.server:app --port 8000
```

Then in the browser, walk through:

1. **http://localhost:8000/trends** — ranked viral prompts. Each card: source badge,
   engagement + virality score (log-normalized per source — explain in one sentence),
   LLM-extracted pattern tags ("role assignment", "negative prompt", …) and a two-sentence
   "why this works" analysis. Image prompts show the actual generated image.
2. Click **Draft post** on a trend — Gemini writes a full article about that prompt pattern,
   lands in the drafts queue. Nothing goes live without approval.
3. **http://localhost:8000/drafts** — approve (git commit + push to the target site repo)
   or reject. Show the commit with `git log` in the target repo.
4. **http://localhost:8000/schedule** — the whole loop runs itself on an interval;
   **http://localhost:8000/pipeline** — full execution trace of the last run (every step,
   timing, errors).

**Talking points:** per-source failure isolation (one API down ≠ run dead), explainable
scoring over black-box, human-approval gate in front of LLM output, provider-swap via config
(Gemini ↔ Ollama), pathspec-scoped git commits (never sweeps unrelated staged work),
39→99 tests grown with TDD.

### Data sources & keys

| Source | What | Needs |
|---|---|---|
| prompts.chat (HuggingFace) | Curated text prompts, CC0 | nothing — works out of the box |
| Civitai | Weekly most-reacted image prompts + images | free API token: civitai.com → Settings → API Keys → put `CIVITAI_API_TOKEN=...` in `.env` |
| Reddit | Top weekly posts from prompt/SD subreddits | free app creds: reddit.com/prefs/apps → fill `REDDIT_CLIENT_ID/SECRET` in `.env` |

Without the optional keys the engine still runs — sources degrade gracefully (logged in
`/pipeline`, run continues).

---

Built for [Outflo](../outflo) — an AI prompt & workflow platform on Next.js + Markdown + Vercel — but works with any git-backed static site.

> **Why build this instead of just asking an AI directly?**
> You could ask an AI to update an image or rewrite a post — and for a one-off task, that works fine.
> ContentPilot exists for the cases where you don't want to be in the loop at all: it runs on a schedule,
> checks for trending content, generates posts, and pushes them live — without you doing anything.
> It's automation, not assistance. Beyond that, this was a deliberate learning project: building an
> agent pipeline, chaining LLM calls with real actions, and wiring it into a live deployment system.

**GitHub:** https://github.com/Jak2/contentpilot.git

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Before You Start](#before-you-start)
3. [First-Time Setup](#first-time-setup)
4. [Choose Your LLM Mode](#choose-your-llm-mode)
5. [Running the Agent](#running-the-agent)
6. [Running the Dashboard](#running-the-dashboard)
7. [Everyday Commands](#everyday-commands)
8. [Switching LLM Mode](#switching-llm-mode)
9. [Modifying the Project](#modifying-the-project)
10. [Running Tests](#running-tests)
11. [Troubleshooting](#troubleshooting)
12. [Uninstalling](#uninstalling)
13. [Project Structure](#project-structure)
14. [Tech Stack](#tech-stack)
15. [Future Scope](#future-scope)
16. [Known Issues](#known-issues)
17. [Documentation](#documentation)

---

## How It Works

```
python main.py

→ How many trending topics today? 2
→ Prompts per topic (with image): 1
→ Workflows per topic: 1
→ Categories (generative-ai, genz, photography, or all): all

[Step 1] Fetches trending topics from HackerNews / Reddit / Tavily
[Step 2] Generates markdown posts via LLM (Gemini or local phi3:mini)
[Step 3] Generates images via Gemini Imagen (if using cloud mode)
[Step 4] Commits files + pushes to target repo → Vercel auto-deploys
```

After the run, open the dashboard at `http://localhost:8000` to see what was generated and inspect the full pipeline execution trace.

---

## Before You Start

Make sure you have these installed on your machine before doing anything else:

```bash
python3 --version       # need 3.11 or higher
git --version           # need any recent version
```

You also need a local clone of a git-backed static site for ContentPilot to publish into.
For this project that's Outflo, which should already be at `../outflo`.

---

## First-Time Setup

Do these steps once. After that, skip to [Everyday Commands](#everyday-commands).

### Step 1 — Go to the project folder

```bash
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot
```

### Step 2 — Create the Python virtual environment

```bash
python3 -m venv --prompt venv .venv
```

This creates a `.venv` folder containing an isolated Python installation.
The `--prompt venv` makes your terminal show `(venv)` when it's active.

### Step 3 — Activate the virtual environment

```bash
# fish shell (what you're using):
source .venv/bin/activate.fish

# bash/zsh (if you ever switch):
source .venv/bin/activate
```

You'll see `(venv)` appear at the start of your terminal prompt.
**Always activate the venv before running any project commands.**

### Step 4 — Install Python dependencies

```bash
# Note: use python3 -m pip, not just "pip", because the pip script
# loses execute permissions on Windows-formatted drives (NTFS)
.venv/bin/python3 -m pip install -r requirements.txt
```

This installs everything listed in `requirements.txt` into the venv.
Takes 1–3 minutes the first time.

### Step 5 — Create your config file

```bash
cp config.yaml.example config.yaml
```

Open `config.yaml` and set the `target_repo` path to your local Outflo clone:

```yaml
target_repo: /media/asterisk/windows_drive/project/learn/my_learning_projects/outflo
```

Leave everything else as-is for now. You can change it later.

### Step 6 — Create your secrets file

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
GEMINI_API_KEY=your-key-here        # required for cloud mode
TAVILY_API_KEY=your-key-here        # optional — only if tavily: true in config.yaml
REDDIT_CLIENT_ID=your-id-here       # optional — only if reddit.enabled: true
REDDIT_CLIENT_SECRET=your-secret    # optional — same as above
REDDIT_USER_AGENT=contentpilot/1.0  # leave this as-is
```

> **You only need `GEMINI_API_KEY` to get started.** The other keys are for extra trend sources.
> If you don't have them yet, leave them as dummy values and keep `tavily: false` and
> `reddit.enabled: false` in `config.yaml`.

### Step 7 — Set up your LLM mode

Go to [Choose Your LLM Mode](#choose-your-llm-mode) now and follow one of the two paths.

---

## Choose Your LLM Mode

ContentPilot can use either a cloud LLM (Gemini via Google's API) or a local LLM
(phi3:mini running on your machine via Ollama). Pick one.

---

### Option A — Cloud Mode (Gemini)

**Use this when:** You have a Gemini API key and haven't hit the daily free-tier quota limit.

**Pros:** Faster (3–8s per post), better quality output, generates images.
**Cons:** Needs internet, hits daily free-tier limits (~50 requests/day).

**Setup:**

In `config.yaml`, set:

```yaml
llm:
  provider: google
  model: gemini-2.0-flash
  image_model: imagen-3.0-generate-001
```

In `.env`, make sure `GEMINI_API_KEY` is filled in.

That's it — no extra installation needed.

---

### Option B — Local Mode (Ollama + phi3:mini)

**Use this when:** You've hit the Gemini quota, want to work offline, or want no API costs.

**Pros:** No API key, no quota, no internet needed after setup, runs forever.
**Cons:** Slower (30–60s per post), no image generation, model can drift from exact format.

**Hardware on this machine:**
- GPU: NVIDIA GTX 1650 Mobile — 4GB VRAM
- phi3:mini uses ~2.2GB VRAM — fits comfortably

#### Step B1 — Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ollama installs as a background service and starts automatically on boot.

#### Step B2 — Download the model

```bash
ollama pull phi3:mini
```

Downloads ~2.2GB. Only needed once — cached on disk after that.

#### Step B3 — Verify Ollama is working

```bash
ollama list
# Should show:  phi3:mini

ollama run phi3:mini "Say hello in one sentence"
# Should print a sentence. Press Ctrl+D to exit.
```

#### Step B4 — Install the LangChain Ollama connector

```bash
.venv/bin/python3 -m pip install langchain-ollama
```

#### Step B5 — Switch config to local mode

In `config.yaml`, change:

```yaml
llm:
  provider: ollama
  model: phi3:mini
  image_model: imagen-3.0-generate-001   # ignored in ollama mode
```

**What doesn't work in local mode:**
Image generation still calls the Gemini Imagen API. If you don't have a valid Gemini key,
set prompts per topic to `0` when running and only generate workflows — workflows don't use images.

---

## Running the Agent

Every time you want to generate content:

```bash
# 1. Go to the project folder
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot

# 2. Activate the venv
source .venv/bin/activate.fish

# 3. Run
PYTHONPATH=. python3 main.py
```

> **Why `PYTHONPATH=.`?** This tells Python to look for modules (`core/`, `agents/`) starting
> from the current folder. Without it, you'll get `ModuleNotFoundError`.

The CLI asks 4 questions:

| Question | What to enter | Notes |
|---|---|---|
| How many trending topics? | `1` to `5` | Start with `2` |
| Prompts per topic (with image)? | `0` to `3` | Use `0` in local mode to skip images |
| Workflows per topic? | `0` to `3` | Works in both modes |
| Categories? | `all` or `generative-ai`, `genz`, `photography` | `all` means any category |

After answering, it runs automatically. You'll see log output for each step.
When done it prints where the content went (drafts by default — see below).

### Non-Interactive / Scheduled Mode

For cron, systemd timers, or any headless invocation, pass flags instead of answering prompts:

```bash
PYTHONPATH=. python3 main.py --topics 3 --prompts 1 --workflows 1 --categories all
```

By default this saves generated posts as **drafts** — nothing is committed or pushed to your
target repo until you approve them at http://localhost:8000/drafts. Add `--publish` to publish
immediately instead (the original Phase 1 behavior).

Example crontab entry (runs daily at 6 AM):

```
0 6 * * * cd /path/to/contentpilot && PYTHONPATH=. .venv/bin/python main.py --topics 3 --prompts 1 --workflows 1 >> cron.log 2>&1
```

Alternatively, enable the dashboard's built-in scheduler at http://localhost:8000/schedule —
no cron entry needed, as long as the dashboard process stays running. The dashboard is the
central control point: schedule recurring runs, trigger one-off runs, and approve/reject
drafts, all from one place.

---

## Running the Dashboard

The dashboard is a local web app that shows everything ContentPilot generated and how it ran.
Run it in a **separate terminal window** — keep it running while you use the agent.

```bash
# In a new terminal window:
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot
source .venv/bin/activate.fish
PYTHONPATH=. python3 dashboard/server.py
```

Then open **http://localhost:8000** in your browser.

> **Port already in use?** Run on a different port:
> ```bash
> PYTHONPATH=. python3 dashboard/server.py --port 8001
> ```
> Then open http://localhost:8001

**Pages:**

| Page | URL | What it shows |
|---|---|---|
| All Posts | `http://localhost:8000/` | Pipeline stage overview + all generated posts grouped by topic |
| Pipeline | `http://localhost:8000/pipeline` | Full function call tree for the last run — every function, duration, result, errors |
| Post detail | `http://localhost:8000/post/{slug}` | Full post content, image, source URL, git commit |

The **Pipeline page** shows exactly what happened step by step, including which functions failed and why:

```
Orchestrator.run()  48s
├── TrendDiscovery.run()  2s  → 2 topics fetched
│   ├── 🟠 _fetch_hackernews()  ✅  → 2 topics returned
│   ├── 🔴 _fetch_reddit()      ⏭  skipped (disabled in config.yaml)
│   └── 🔵 _fetch_tavily()      ⏭  skipped (disabled in config.yaml)
├── 📝 _generate_and_publish("AI topic", prompt)  22s  ✅
│   ├── ✍️ ContentGenerator.run()   6s   → slug: ai-topic-prompt
│   ├── 🖼️ ImageGenerator.run()    14s   → public/images/ai-topic-prompt.png
│   └── 🚀 GitPublisher.publish()  0.3s  → commit: a1b2c3d4
└── 🚀 GitPublisher.push()  2s  → commits pushed to remote
```

---

## Everyday Commands

Once everything is set up, these are the only commands you need day-to-day:

```bash
# Go to the project
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot

# Activate the venv (do this every time you open a new terminal)
source .venv/bin/activate.fish

# Generate content
PYTHONPATH=. python3 main.py

# Start the dashboard (separate terminal)
PYTHONPATH=. python3 dashboard/server.py

# Run tests
PYTHONPATH=. .venv/bin/python3 -m pytest -v

# Check Ollama status (local mode only)
ollama ps                    # shows what model is loaded
ollama list                  # shows downloaded models

# Deactivate the venv when done
deactivate
```

---

## Switching LLM Mode

You only need to edit one section in `config.yaml`. No code changes required.

### Switch to local (Ollama):

```yaml
llm:
  provider: ollama
  model: phi3:mini
```

### Switch back to cloud (Gemini):

```yaml
llm:
  provider: google
  model: gemini-2.0-flash
  image_model: imagen-3.0-generate-001
```

Save the file and run `python3 main.py` — the change takes effect immediately.

**Try a different local model:**

```bash
ollama pull llama3.2:3b        # Meta's model, good general writing
ollama pull gemma2:2b          # Google's small model, very fast
```

Then update `config.yaml`:

```yaml
llm:
  model: llama3.2:3b           # or gemma2:2b
```

---

## Modifying the Project

### Add a new trend source

Edit `agents/trend_discovery.py` — add a new `_fetch_<source>()` method following the same pattern as `_fetch_hackernews()`. Then call it in `run()` and track it in `self.source_results`.

### Change what a post looks like

Edit the prompt templates at the top of `agents/content_generator.py`:
- `PROMPT_TEMPLATE` — controls the structure of AI prompt posts
- `WORKFLOW_TEMPLATE` — controls the structure of workflow posts

### Change the dashboard layout

Edit files in `dashboard/templates/`:
- `base.html` — nav, global CSS styles
- `index.html` — the main posts page
- `pipeline.html` — the function call tree page
- `post.html` — individual post detail

### Change which sources are enabled

In `config.yaml`:

```yaml
sources:
  tavily: false        # set true if you have a Tavily API key
  reddit:
    enabled: false     # set true if you have Reddit credentials
  hackernews:
    enabled: true      # free, no key needed
```

### Add a new Python dependency

```bash
.venv/bin/python3 -m pip install <package-name>

# Then add it to requirements.txt so others can install it too:
echo "<package-name>>=<version>" >> requirements.txt
```

---

## Running Tests

```bash
# Run all 38 tests
PYTHONPATH=. .venv/bin/python3 -m pytest -v

# Run tests for a specific module
PYTHONPATH=. .venv/bin/python3 -m pytest tests/agents/test_trend_discovery.py -v
PYTHONPATH=. .venv/bin/python3 -m pytest tests/core/test_manifest.py -v
PYTHONPATH=. .venv/bin/python3 -m pytest tests/dashboard/test_server.py -v

# Run a single test by name
PYTHONPATH=. .venv/bin/python3 -m pytest -v -k "test_append_post"
```

No API keys needed — all external calls are mocked in tests.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'core'`

You forgot `PYTHONPATH=.`:

```bash
PYTHONPATH=. python3 main.py          # correct
python3 main.py                       # wrong — will fail
```

### `429 RESOURCE_EXHAUSTED` from Gemini

You hit the free daily quota. Options:
- Wait until tomorrow (resets at midnight Pacific time)
- Switch to local mode — see [Option B](#option-b--local-mode-ollama--phi3mini)

### `Permission denied` when running pip

The venv is on an NTFS drive — the pip script loses its execute bit. Always use:

```bash
.venv/bin/python3 -m pip install <package>    # correct
pip install <package>                          # wrong on this machine
```

### Dashboard shows "No posts yet" after running main.py

The run may have failed silently. Check the Pipeline page at `http://localhost:8000/pipeline`
to see which step failed and what the error was.

Also check that all sources aren't disabled — if `tavily`, `reddit`, and `hackernews` are all
`false` in `config.yaml`, no topics are fetched and nothing generates.

### Port 8000 already in use

```bash
# Find what's using it:
lsof -i :8000

# Kill it (replace 12345 with the PID shown):
kill 12345

# Or just use a different port:
PYTHONPATH=. python3 dashboard/server.py --port 8001
```

### Ollama not responding / "Connection refused"

```bash
# Check if Ollama is running:
systemctl status ollama

# Start it manually if stopped:
ollama serve

# Verify the model is loaded:
ollama ps
```

### Ollama is slow (not using GPU)

```bash
# Check if GPU is being used:
ollama ps
# Should show "GPU" next to the model name

# Check GPU driver:
nvidia-smi
```

If GPU is not showing, something else may be occupying VRAM (check `nvidia-smi` output).

---

## Uninstalling

### Remove the virtual environment

```bash
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot
rm -rf .venv
```

This removes all installed Python packages. The project code stays intact.
To reinstall, run [First-Time Setup](#first-time-setup) again from Step 2.

### Remove Ollama and its models

```bash
# Remove all downloaded models first:
ollama rm phi3:mini
ollama rm llama3.2:3b    # if you pulled this

# Uninstall Ollama:
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
sudo rm /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
```

### Remove generated files (keep code, delete data)

```bash
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/contentpilot
rm -f manifest.json run_log.json manifest.json.lock run_log.json.lock
```

This clears the post history and run logs. The code and config stay.


### Testing manually against a throwaway repo

ContentPilot commits and pushes to whatever `target_repo` points at in `config.yaml`. Never point it at your real outflo repo (or any repo with a live deploy) until you've reviewed output quality — especially with a small local model like `phi3:mini`, which can hallucinate facts. Test against a disposable repo first:

```bash
# 1. Create a throwaway git repo with the folder structure ContentPilot expects
mkdir -p /tmp/outflo-test/content/prompts /tmp/outflo-test/content/workflows /tmp/outflo-test/public/images
cd /tmp/outflo-test && git init && git commit --allow-empty -m init
# no `git remote add origin ...` — this keeps push() a harmless no-op (it fails
# with "No item found with id origin" and logs a warning, nothing more)

# 2. Point config.yaml at it
#    target_repo: /tmp/outflo-test

# 3. Run a small batch
cd my_learning_projects/contentpilot
source .venv/bin/activate      # or use .venv/bin/python directly
python main.py                 # e.g. answer 1 topic, 1 prompt, 0 workflows, all

# 4. Inspect what actually happened — don't trust the "Done!" message alone
cd /tmp/outflo-test
git log --oneline -5           # commits are local-only, confirms nothing was pushed
cat content/prompts/*.md       # read generated content for hallucinations/quality

# 5. Check the dashboard
cd my_learning_projects/contentpilot
python -m uvicorn dashboard.server:app --port 8000
# open http://localhost:8000 — cross-check the dashboard's post list and
# /pipeline trace against the git log above, don't just trust the UI

# 6. Restore config.yaml to the real outflo path only once you're satisfied
```

**Why a repo with no remote is the safe default:** `GitPublisher.publish()` commits locally (writes the file, `git add`, `git commit`) — that part always succeeds. `push()` is a separate step that tries to push to `origin`; with no remote configured it fails safely and just prints a warning, so you get real commits to inspect without any risk of touching GitHub or a live deploy.

**Known gotcha:** `git_publisher.py`'s commit step stages and commits the *entire* index, not just the new file. If your target repo has other uncommitted/staged changes, running ContentPilot will sweep them into the content commit. Run `git status` on the target repo before testing and commit or stash anything unrelated first.

#### Using the scratchpad directory for throwaway testing

Claude Code (this assistant) has a session-scoped **scratchpad directory** for exactly this kind of test — a real filesystem location outside the project where it can create disposable repos, run the actual project code against them, and inspect results, without ever risking the real project files. The pattern used to validate ContentPilot end-to-end was:

1. Create a throwaway git repo inside the scratchpad path (same steps as above — `mkdir`, `git init`, `git commit --allow-empty`, no remote).
2. Temporarily edit `config.yaml`'s `target_repo` to point at that scratchpad path.
3. Run `python main.py` normally — the *actual* ContentPilot code runs unmodified, it just writes its output into the scratchpad repo instead of outflo.
4. Inspect the results (`git log`, generated markdown, dashboard) in the scratchpad path.
5. Restore `config.yaml` back to the real `target_repo` afterward.

The scratchpad path is session-specific and gets cleaned up automatically — nothing there is meant to persist. If you want to do this yourself outside of a Claude Code session, just substitute any `/tmp/...` path (as in the steps above) for the same effect: same code, disposable output location, zero risk to the real repo.

---

## Project Structure

```
contentpilot/
├── main.py                   CLI entry point — asks 4 questions, then runs
├── config.yaml               your settings (copied from config.yaml.example)
├── config.yaml.example       template — never edit this directly
├── .env                      your secret API keys (copied from .env.example)
├── .env.example              template — never edit this directly
├── requirements.txt          all Python dependencies
├── manifest.json             auto-created — tracks every post ever published
├── run_log.json              auto-created — stores execution trace of each run
├── schedule.json             auto-created — recurring-run config (edit via /schedule page)
├── drafts/                   auto-created — staged posts awaiting approval (git-ignored)
│
├── agents/                   the AI workers — each does one specific job
│   ├── orchestrator.py       coordinator — calls all agents in order, logs each step
│   ├── trend_discovery.py    fetches trending topics from Tavily / Reddit / HackerNews
│   ├── content_generator.py  generates markdown posts via LangChain (Gemini or Ollama)
│   ├── image_generator.py    generates images via Gemini Imagen, saves as PNG
│   └── git_publisher.py      writes files to target repo and commits via GitPython
│
├── core/                     shared utilities — used by all agents
│   ├── config.py             loads and validates config.yaml
│   ├── manifest.py           reads/writes manifest.json (thread-safe)
│   ├── models.py             data models: TopicResult, PostEntry, ManifestState
│   └── run_log.py            records function-level execution into run_log.json
│
├── dashboard/
│   ├── server.py             FastAPI web app — serves the dashboard on localhost:8000
│   └── templates/
│       ├── base.html         shared layout, nav, all CSS
│       ├── index.html        home page: pipeline overview + content cards by topic
│       ├── post.html         post detail: content, image, git info, actions
│       └── pipeline.html     function call tree for the latest run
│
├── tests/                    38 tests, all passing, no API keys needed
│
└── docs/
    ├── LOCAL_LLM_SETUP.md    full guide for running with Ollama instead of Gemini
    ├── CONTENTPILOT_FULL_REPORT.md  deep architecture and module breakdown
    └── superpowers/          design spec and implementation plan (history)
```

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| LLM orchestration | LangChain | Abstracts the LLM — swap Gemini for Ollama in one config line |
| Text generation (cloud) | Gemini 2.0 Flash | Fast, high quality, has daily free-tier quota |
| Text generation (local) | phi3:mini via Ollama | Runs on GPU, no quota, slower |
| Image generation | Gemini Imagen 3 | Cloud only — no local equivalent set up yet |
| Trend discovery | Tavily + Reddit (praw) + HackerNews | HackerNews is free, others need API keys |
| Git operations | GitPython | Writes files, commits, pushes to any git repo |
| CLI | Typer + Rich | Styled terminal prompts |
| Dashboard | FastAPI + Jinja2 | Lightweight local web server, no JS framework |
| Config validation | Pydantic v2 + PyYAML | Type-checked config loading |
| Tests | pytest + pytest-mock + pytest-asyncio | All external APIs mocked |

---

## Design Standards for New Features

Ground rules established while designing Phase 4 (non-interactive CLI, scheduler, draft/approve
workflow — see PROGRESS_TRACKER.md). Apply these when extending ContentPilot further.

**Stay on Pydantic v2 for all structured data.** The codebase already uses Pydantic
(`TopicResult`, `PostEntry`, `ManifestState` in `core/models.py`) with `Literal` types for
enum-like fields, and `core/manifest.py` loads/saves via `model_validate_json()` /
`model_dump_json()`. Any new persisted structure — e.g. a future `schedule.json` — should
follow the exact same shape: a `BaseModel` in `core/models.py`, loaded/saved the same way
`manifest.json` is. Introducing a second data-modeling library (dataclasses, attrs,
marshmallow) for new features would fragment the codebase for no real gain; Pydantic already
covers validation, serialization, and type safety here.

**In-process scheduling, not a separate service.** For a single-user local tool, an in-process
scheduler (e.g. APScheduler's `AsyncIOScheduler`, integrated into the FastAPI dashboard's event
loop) is the right level of complexity — no need for Celery, a cron daemon, or a second
long-running process. Cron/systemd-timer remains documented as a lightweight, code-free
alternative for headless machines that don't run the dashboard at all.

**Reuse the `FileLock` pattern for any new JSON file.** `manifest.json` is protected from
concurrent writes via `filelock` (see `core/manifest.py`). Any new JSON-backed state (e.g.
schedule config) that can be written from more than one place — a background scheduler thread
and the dashboard UI, for instance — must use the same lock pattern to avoid races.

**Long-running work must not block the FastAPI event loop.** The Orchestrator's pipeline
(GitPython, HTTP calls to Tavily/Reddit/HackerNews/Gemini) is synchronous. If it's triggered
from inside the dashboard process (a "Run Now" button, or a scheduled job), it must run in a
thread pool executor, never awaited directly on the event loop — otherwise the entire dashboard
freezes for the duration of a run.

**Status values describe state, not actions.** `PostEntry.status` was renamed from
`"pushed"` to `"published"` (2026-07-02) so the full set — `draft`, `published`, `deleted`,
`failed` — reads consistently as a lifecycle rather than mixing verbs and states.

---

## Future Scope

### Phase 4 — Non-Interactive Mode, Scheduling & Draft/Approve Workflow
- Design in progress — see `docs/superpowers/specs/2026-07-02-contentpilot-scheduling-drafts-design.md`
- CLI flags for headless/cron invocation, a `draft` status with dashboard approve/reject,
  and an in-process scheduler (APScheduler) so the dashboard becomes the single control point
- Pending implementation checklist: `NEXT_STEPS.md`
- Motivating scenarios: `STORIES.md`

### Phase 2 — Hermes Integration
- Wrap `main.py` as a Hermes skill for conversational invocation
- **Blocker:** Hermes not yet configured on this machine

### Phase 3 — Workflow Pipeline Generator
- Sub-agent that turns a business goal into a structured multi-step AI workflow post
- Needs its own design session

### Phase 3 — Multi-Site Adapter
- Currently writes files in Outflo's folder structure only
- Future: support Hugo, Gatsby, Astro, Jekyll via a config flag

### Dashboard Improvements
- Image thumbnails on the post grid
- Bulk delete
- Category filter
- Run agent from UI (no terminal needed)
- Basic login (currently open — local use only)

### Local Image Generation
- Stable Diffusion via ComfyUI would enable offline image generation
- Needs separate setup — see `docs/LOCAL_LLM_SETUP.md` for details

---

## Known Issues

| Issue | Where | Impact | Fix |
|---|---|---|---|
| `google.generativeai` SDK is deprecated | `agents/image_generator.py:6` | Startup warning (suppressed). SDK will eventually stop working. | Migrate to `google.genai` + rewrite test mocks |
| `httpx` listed twice | `requirements.txt` | Harmless | Remove the duplicate line |
| Image gen compatibility shim | `agents/image_generator.py` | Extra code complexity | Rewrite tests to mock `google.genai.Client`, delete the shim |
| No tests for `run_log.py` | `core/run_log.py` | Silent breakage if log format changes | Add `tests/core/test_run_log.py` |
| No test for `/pipeline` route | `dashboard/server.py` | Same | Add test in `tests/dashboard/test_server.py` |

---

## Documentation

| Doc | Path | What it covers |
|---|---|---|
| **This file** | `README.md` | Full setup, usage, and command reference |
| **Progress Tracker** | `PROGRESS_TRACKER.md` | What's built, what's broken, what's next |
| **Decisions & Issues** | `decisions_and_issues.md` | Bug log, dead code, code smells, open design decisions |
| **Stories** | `STORIES.md` | Narrative scenarios (real and realistic) motivating each Phase 4 feature |
| **Next Steps** | `NEXT_STEPS.md` | Pending implementation checklist for the current phase in progress |
| **Local LLM Setup** | `docs/LOCAL_LLM_SETUP.md` | Full Ollama setup guide, model options, troubleshooting |
| **Full Report** | `docs/CONTENTPILOT_FULL_REPORT.md` | Architecture deep-dive, module breakdown, data models |
| Design Spec — Phase 1 | `docs/superpowers/specs/2026-06-25-contentpilot-design.md` | Original architecture decisions |
| Implementation Plan — Phase 1 | `docs/superpowers/plans/2026-06-25-contentpilot-implementation.md` | The 11-task TDD plan used to build Phase 1 |
| Design Spec — Phase 4 | `docs/superpowers/specs/2026-07-02-contentpilot-scheduling-drafts-design.md` | Non-interactive CLI, scheduler, draft/approve workflow (in progress) |
