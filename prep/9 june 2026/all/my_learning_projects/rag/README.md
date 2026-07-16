# Folder-RAG

Point it at a folder, then **chat with your documents** in a minimalist web UI —
ChatGPT-style, with persistent history. Every answer is grounded only in the
indexed files and cites the source documents. Also usable from the command line.

Like handing Claude a folder path, but private, local, and reusable.

By default it runs **fully local** — Ollama with `qwen2.5:1.5b`, no API key, nothing
leaves your machine.

---

## Quick start (zero-fuss)

Clone the repo, then run one script — it installs Python deps, installs Ollama, pulls
the default model, and writes your `.env`:

**Linux / macOS**
```bash
cd my_learning_projects/rag
./install.sh        # deps + Ollama + qwen2.5:1.5b
# edit .env → set RAG_CORPUS_DIR to the folder you want to query
./run.sh            # starts Ollama if needed, indexes on first run, opens the GUI
```

**Windows (PowerShell)**
```powershell
cd my_learning_projects\rag
.\install.ps1
# edit .env → set RAG_CORPUS_DIR
.\run.ps1
```

Then open <http://127.0.0.1:8000> and ask. That's it — no cloud account required.

> Want Claude instead of local? Set `RAG_LLM=claude` and `ANTHROPIC_API_KEY=...` in
> `.env`. Everything else is unchanged.

---

## What it is

```
 your folder ──▶ [ index ] ──▶ vector DB ──▶ [ retrieve top-k ] ──▶ [ LLM ] ──▶ cited answer
                  chunk+embed     (Chroma)      by similarity        Claude/Ollama
```

- **Index** walks a folder, extracts text (PDF via PyMuPDF, plus Markdown / text /
  code), chunks it, embeds each chunk, and stores vectors on disk. Re-indexing is
  incremental — only new or changed files are re-embedded (tracked by file hash).
- **Ask** embeds your question, fetches the nearest chunks, and hands them to an LLM
  that answers using *only* that context and cites the source files.
- **Chat GUI** — a clean web interface with a conversation sidebar and persistent
  history (SQLite). Ask from the browser; history survives restarts.

Everything is swappable behind config: the **LLM**, the **embedder**, the **vector
store**, and the **retrieval strategy**. Start simple; upgrade paths (Qdrant, cloud
embeddings, agentic/hybrid retrieval) are documented seams, not day-one code.

---

## Project layout — frontend and backend cleanly separated

```
rag/
├── backend/            ← all server-side logic (Python package)
│   ├── config.py       ← central config: .env overrides config.yaml
│   ├── backends.py     ← LLM + embedder factories (the swap points)
│   ├── store.py        ← vector store wrapper (Chroma)
│   ├── indexing.py     ← load / chunk / hash / index a folder
│   ├── engine.py       ← retrieval seam + ask() with citations
│   ├── history.py      ← persistent chat history (SQLite)
│   ├── api.py          ← FastAPI app (HTTP endpoints + serves the UI)
│   └── cli.py          ← command-line index / ask
├── frontend/
│   └── index.html      ← the entire chat UI (one self-contained file, no build step)
├── tests/
│   └── test_rag.py     ← engine + history tests (no API key needed)
├── config.yaml         ← engine defaults (the four switches)
├── .env.example        ← central control switch — copy to .env
├── requirements.txt
└── run.py              ← start the web GUI
```

---

## Setup

```bash
# 1. Create a venv on a native (non-Windows-mounted) filesystem, then install:
python3 -m venv ~/.venvs/rag
~/.venvs/rag/bin/pip install -r requirements.txt

# 2. Configure — copy the template and edit:
cp .env.example .env
#   set ANTHROPIC_API_KEY=...          (needed when RAG_LLM=claude)
#   set RAG_CORPUS_DIR=/path/to/docs   (the folder to answer questions from)
```

> **Windows-drive note:** if the project lives on a `/media/.../windows_drive` mount,
> executables there won't run — keep the venv on the native filesystem
> (e.g. `~/.venvs/rag`) as above.

---

## Run the GUI

```bash
~/.venvs/rag/bin/python run.py
# → Folder-RAG → http://127.0.0.1:8000
```

Open the URL. First time: click **Reindex folder** in the sidebar to build the index,
then start a new chat and ask away. Sources appear as chips under each answer;
conversations persist in the sidebar.

## Run from the command line

```bash
cd rag
~/.venvs/rag/bin/python -m backend.cli index            # index RAG_CORPUS_DIR
~/.venvs/rag/bin/python -m backend.cli index /some/dir  # or an explicit folder
~/.venvs/rag/bin/python -m backend.cli ask "your question"
```

---

## The central switch — `.env`

`.env` is the one place to control the app; anything set there overrides `config.yaml`.

| Variable | Purpose |
|----------|---------|
| `RAG_CORPUS_DIR` | folder to answer questions from |
| `RAG_LLM` | `ollama` (default) \| `claude` |
| `RAG_OLLAMA_MODEL` | local model, default `qwen2.5:1.5b` |
| `ANTHROPIC_API_KEY` | Claude auth (only when `RAG_LLM=claude`) |
| `RAG_EMBED` | `local` |
| `RAG_STORE` | `chroma` |
| `RAG_RETRIEVAL` | `plain` |
| `RAG_HOST` / `RAG_PORT` | web server bind |
| `RAG_HISTORY_DB` | chat-history SQLite path |

`config.yaml` holds the engine defaults and tuning knobs (`chunk_tokens`,
`chunk_overlap`, `top_k`, `ollama_model`). Set an engine switch in `.env` only when
you want to override the YAML default.

### Local (default) vs Claude

- **Local (default):** Ollama + `qwen2.5:1.5b`, embeddings already local — nothing
  leaves your machine, no API key. Swap the model with `RAG_OLLAMA_MODEL` (any tag
  you've `ollama pull`ed).
- **Claude:** set `RAG_LLM=claude` and `ANTHROPIC_API_KEY` in `.env`.

---

## Gotchas

- **Embedder is stamped into the DB.** Switching `embed` after building an index
  hard-errors — the old vectors are incompatible. Re-index into a fresh `db_dir`.
- Dotfiles and dot-directories (`.git`, `.venv`, …) are skipped during indexing.
- Start with the defaults. Qdrant, cloud embeddings, and agentic/hybrid retrieval are
  documented upgrade seams in `IMPLEMENTATION_PLAN.md` — add them only when plain
  vector RAG measurably falls short.

## Test

```bash
~/.venvs/rag/bin/python -m pytest tests/ -q
```
