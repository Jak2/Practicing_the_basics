# Folder-RAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Point the tool at a folder, ask questions in natural language, get answers grounded in those documents with citations — from a CLI **and** a ChatGPT-style web GUI with persistent history.

**Architecture:** Load files → chunk → embed once into a persistent vector DB → on a question, retrieve top-k chunks → feed them + the question to an LLM → return answer with citations. Four swap points behind config: LLM backend, embedding backend, vector store, retrieval strategy. A FastAPI layer exposes the engine over HTTP and serves a single-file web UI; chat history persists in SQLite. Start simple; upgrade paths (Qdrant, cloud embeddings, agentic retrieval) are seams, not day-one code.

**Tech Stack:** Python 3.12, `chromadb` (persistent, on-disk), `sentence-transformers` (local embeddings), `anthropic` SDK (Claude), `ollama` (optional local LLM), `pymupdf` (PDF → text), `pyyaml`, `python-dotenv`, `fastapi` + `uvicorn`, `sqlite3` (stdlib) for history, vanilla HTML/CSS/JS frontend (no build step).

## Status

- **Phase 1 (CLI engine)** — DONE. 6 engine tests pass.
- **Phase 2 (web GUI + restructure)** — DONE. 7 tests pass (engine + history); server endpoints and frontend smoke-tested.
- **Phase 3 (local-first + one-command setup)** — DONE. Default LLM is now Ollama + `qwen2.5:1.5b` (no API key); overridable via `.env` (`RAG_LLM`, `RAG_OLLAMA_MODEL`). Cross-platform `install.{sh,ps1}` (deps + Ollama + model + `.env`) and `run.{sh,ps1}` (ensure Ollama up → index on first run → serve).

## Project structure (after Phase 2 restructure)

```
rag/
├── backend/            # server-side Python package
│   ├── config.py       # central config: .env overrides config.yaml
│   ├── backends.py     # LLM + embedder factories (swap points)
│   ├── store.py        # vector store wrapper (Chroma)
│   ├── indexing.py     # load / chunk / hash / index a folder   (was index.py)
│   ├── engine.py       # retrieval seam + ask() w/ citations     (was ask.py; now cached)
│   ├── history.py      # persistent chat history (SQLite)
│   ├── api.py          # FastAPI app: HTTP endpoints + serves UI
│   └── cli.py          # command-line index / ask
├── frontend/index.html # entire chat UI, one self-contained file
├── tests/test_rag.py
├── config.yaml         # engine defaults (four switches + tuning)
├── .env.example        # central control switch
├── requirements.txt
└── run.py              # start the web GUI
```

> **Restructure note:** Phase-1 modules moved into the `backend/` package —
> `index.py → indexing.py`, `ask.py → engine.py`, `load_config` extracted into
> `config.py`. The Phase-1 task specs below are kept as historical record; file
> paths there predate the `backend/` move.

## Global Constraints

- Model when `llm: claude`: **`claude-opus-4-8`** (exact string). Adaptive thinking (`thinking={"type":"adaptive"}`), stream the answer, read final via `.get_final_message()`.
- Never truncate documents silently.
- **Embedder identity is stamped into the DB.** On query, if the config embedder ≠ the one that built the index, hard-error.
- Incremental indexing: track file content hashes; only (re)embed new/changed files. Skip dotfiles/dot-dirs (`.git`, `.venv`).
- Answers always carry citations (source file).
- Four config switches ship with defaults: `embed: local`, `llm: claude`, `store: chroma`, `retrieval: plain`. **`.env` is the central override** (overrides `config.yaml`).
- No LangChain / LangGraph. Raw SDKs. Frontend has no build toolchain — one HTML file.

---

### Task 1: Config + backend factories

**Files:**
- Create: `my_learning_projects/rag/config.yaml`
- Create: `my_learning_projects/rag/backends.py`
- Test: `my_learning_projects/rag/test_rag.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `load_config(path="config.yaml") -> dict` — returns dict with keys `llm`, `embed`, `store`, `retrieval`, `db_dir`, `chunk_tokens`, `chunk_overlap`, `top_k`.
  - `get_embedder(cfg) -> Embedder` where `Embedder` has `.name: str` and `.embed(texts: list[str]) -> list[list[float]]`.
  - `get_llm(cfg) -> LLM` where `LLM` has `.answer(question: str, context: str) -> str`.

- [ ] **Step 1: Write `config.yaml`**

```yaml
llm: claude          # claude | ollama
embed: local         # local | (future: openai, voyage)
store: chroma        # chroma | (future: qdrant)
retrieval: plain     # plain | (future: agentic)
db_dir: .rag_db
chunk_tokens: 800
chunk_overlap: 100
top_k: 6
ollama_model: llama3.1
```

- [ ] **Step 2: Write the failing test for the embedder factory**

```python
# test_rag.py
from backends import load_config, get_embedder

def test_local_embedder_has_name_and_embeds():
    cfg = load_config()
    emb = get_embedder({**cfg, "embed": "local"})
    assert emb.name  # non-empty identity string
    vecs = emb.embed(["hello world", "goodbye"])
    assert len(vecs) == 2 and len(vecs[0]) > 0
```

- [ ] **Step 3: Run it, confirm it fails** — `cd my_learning_projects/rag && python -m pytest test_rag.py::test_local_embedder_has_name_and_embeds -v` → FAIL (module not found).

- [ ] **Step 4: Implement `backends.py`**

```python
import yaml

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

# ---- Embedders ----
class LocalEmbedder:
    def __init__(self, model="BAAI/bge-small-en-v1.5"):
        from sentence_transformers import SentenceTransformer
        self._m = SentenceTransformer(model)
        self.name = f"local:{model}"
    def embed(self, texts):
        return self._m.encode(texts, normalize_embeddings=True).tolist()

def get_embedder(cfg):
    kind = cfg["embed"]
    if kind == "local":
        return LocalEmbedder()
    raise ValueError(f"unknown embed backend: {kind}")  # ponytail: add openai/voyage when needed

# ---- LLMs ----
class ClaudeLLM:
    def __init__(self):
        import anthropic
        self._c = anthropic.Anthropic()
        self.name = "claude:claude-opus-4-8"
    def answer(self, question, context):
        with self._c.messages.stream(
            model="claude-opus-4-8",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=(
                "Answer the question using ONLY the provided context. "
                "Cite the source file for each claim like [source: filename]. "
                "If the context does not contain the answer, say so plainly."
            ),
            messages=[{"role": "user",
                       "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}"}],
        ) as s:
            return "".join(b.text for b in s.get_final_message().content if b.type == "text")

class OllamaLLM:
    def __init__(self, model="llama3.1"):
        import ollama
        self._ollama = ollama
        self._model = model
        self.name = f"ollama:{model}"
    def answer(self, question, context):
        r = self._ollama.chat(model=self._model, messages=[
            {"role": "system", "content": "Answer using ONLY the context. Cite source files like [source: filename]. If not answerable from context, say so."},
            {"role": "user", "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}"},
        ])
        return r["message"]["content"]

def get_llm(cfg):
    kind = cfg["llm"]
    if kind == "claude":
        return ClaudeLLM()
    if kind == "ollama":
        return OllamaLLM(cfg.get("ollama_model", "llama3.1"))
    raise ValueError(f"unknown llm backend: {kind}")  # ponytail: add openai-compatible when needed
```

- [ ] **Step 5: Run test, confirm PASS.** (Requires `pip install sentence-transformers pyyaml` first.)

- [ ] **Step 6: Commit** — `git add my_learning_projects/rag && git commit -m "feat(rag): config + embedder/llm backend factories"`

---

### Task 2: Loader + chunker (with incremental hashing)

**Files:**
- Create: `my_learning_projects/rag/index.py` (loader + chunker portion)
- Test: `my_learning_projects/rag/test_rag.py` (append)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces:
  - `load_file(path: str) -> str` — extract text; supports `.pdf` (via pymupdf), `.md`, `.txt`, `.py`, and other UTF-8 text; returns `""` for unreadable/binary.
  - `chunk_text(text: str, size_tokens=800, overlap=100) -> list[str]` — split on paragraph/heading boundaries, ~`size_tokens` each (word-count proxy: ~0.75 words/token → ~`size_tokens*0.75` words), `overlap` word carryover.
  - `file_hash(path: str) -> str` — sha256 of file bytes.

- [ ] **Step 1: Write failing tests**

```python
from index import chunk_text, file_hash

def test_chunk_splits_and_overlaps():
    text = "\n\n".join(f"Paragraph {i} " * 60 for i in range(5))
    chunks = chunk_text(text, size_tokens=100, overlap=20)
    assert len(chunks) >= 2
    assert all(c.strip() for c in chunks)

def test_file_hash_stable(tmp_path):
    p = tmp_path / "a.txt"; p.write_text("hello")
    assert file_hash(str(p)) == file_hash(str(p))
```

- [ ] **Step 2: Run, confirm FAIL.**

- [ ] **Step 3: Implement loader + chunker in `index.py`**

```python
import hashlib, os

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()

def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            import pymupdf
            doc = pymupdf.open(path)
            return "\n".join(page.get_text() for page in doc)
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""  # unreadable/binary — skip

def chunk_text(text, size_tokens=800, overlap=100):
    words_per_chunk = int(size_tokens * 0.75)
    overlap_words = int(overlap * 0.75)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], []
    count = 0
    for p in paras:
        w = p.split()
        if count + len(w) > words_per_chunk and cur:
            chunks.append(" ".join(cur))
            cur = cur[-overlap_words:] if overlap_words else []
            count = len(cur)
        cur.extend(w); count += len(w)
    if cur:
        chunks.append(" ".join(cur))
    return chunks
```

- [ ] **Step 4: Run tests, confirm PASS.**

- [ ] **Step 5: Commit** — `git commit -am "feat(rag): file loader + boundary-aware chunker + hashing"`

---

### Task 3: Vector store wrapper + `index_folder`

**Files:**
- Create: `my_learning_projects/rag/store.py`
- Modify: `my_learning_projects/rag/index.py` (add `index_folder`)
- Test: append to `test_rag.py`

**Interfaces:**
- Consumes: `get_embedder` (Task 1); `load_file`, `chunk_text`, `file_hash` (Task 2).
- Produces:
  - `get_store(cfg, embedder_name) -> Store`. `Store` methods: `.embedder_name() -> str|None` (stamped identity, None on fresh DB), `.set_embedder_name(name)`, `.upsert(ids, embeddings, docs, metadatas)`, `.query(embedding, top_k) -> list[dict]` (each `{text, source, chunk}`), `.known_hashes() -> dict[path,hash]`, `.record_hash(path, hash)`, `.delete_by_source(path)`.
  - `index_folder(folder: str, cfg: dict) -> dict` returning `{"added": n, "skipped": m, "updated": k}`.

- [ ] **Step 1: Failing end-to-end index test**

```python
from index import index_folder
from backends import load_config

def test_index_folder_embeds_new_files(tmp_path):
    (tmp_path / "doc.md").write_text("The capital of France is Paris. " * 30)
    cfg = {**load_config(), "db_dir": str(tmp_path / "db"), "embed": "local", "store": "chroma"}
    stats = index_folder(str(tmp_path), cfg)
    assert stats["added"] >= 1
    # second run skips unchanged
    stats2 = index_folder(str(tmp_path), cfg)
    assert stats2["added"] == 0 and stats2["skipped"] >= 1
```

- [ ] **Step 2: Run, confirm FAIL.**

- [ ] **Step 3: Implement `store.py`** (Chroma; embedder name stamped in a `_meta` collection)

```python
class ChromaStore:
    def __init__(self, db_dir):
        import chromadb
        self._client = chromadb.PersistentClient(path=db_dir)
        self._col = self._client.get_or_create_collection("chunks")
        self._meta = self._client.get_or_create_collection("_meta")
    def embedder_name(self):
        got = self._meta.get(ids=["embedder"])
        return got["metadatas"][0]["name"] if got["ids"] else None
    def set_embedder_name(self, name):
        self._meta.upsert(ids=["embedder"], documents=["_"], metadatas=[{"name": name}],
                          embeddings=[[0.0]])
    def known_hashes(self):
        got = self._meta.get(where={"kind": "filehash"})
        return {m["path"]: m["hash"] for m in got["metadatas"]} if got["ids"] else {}
    def record_hash(self, path, h):
        self._meta.upsert(ids=[f"hash:{path}"], documents=["_"],
                          metadatas=[{"kind": "filehash", "path": path, "hash": h}],
                          embeddings=[[0.0]])
    def delete_by_source(self, path):
        self._col.delete(where={"source": path})
    def upsert(self, ids, embeddings, docs, metadatas):
        self._col.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)
    def query(self, embedding, top_k):
        r = self._col.query(query_embeddings=[embedding], n_results=top_k)
        out = []
        for doc, meta in zip(r["documents"][0], r["metadatas"][0]):
            out.append({"text": doc, "source": meta.get("source"), "chunk": meta.get("chunk")})
        return out

def get_store(cfg, embedder_name):
    if cfg["store"] == "chroma":
        s = ChromaStore(cfg["db_dir"])
    else:
        raise ValueError(f"unknown store: {cfg['store']}")  # ponytail: add qdrant when >1M chunks
    stamped = s.embedder_name()
    if stamped is None:
        s.set_embedder_name(embedder_name)
    elif stamped != embedder_name:
        raise SystemExit(
            f"DB was built with embedder '{stamped}' but config uses '{embedder_name}'. "
            f"Re-index into a fresh db_dir, or switch the config back.")
    return s
```

- [ ] **Step 4: Implement `index_folder` in `index.py`**

```python
import os
from backends import get_embedder
from store import get_store

def index_folder(folder, cfg):
    emb = get_embedder(cfg)
    store = get_store(cfg, emb.name)
    known = store.known_hashes()
    added = skipped = updated = 0
    for root, _, files in os.walk(folder):
        for fn in files:
            path = os.path.join(root, fn)
            if path.startswith(os.path.join(folder, cfg["db_dir"])):
                continue
            h = file_hash(path)
            if known.get(path) == h:
                skipped += 1; continue
            text = load_file(path)
            if not text.strip():
                continue
            chunks = chunk_text(text, cfg["chunk_tokens"], cfg["chunk_overlap"])
            if not chunks:
                continue
            if path in known:
                store.delete_by_source(path); updated += 1
            else:
                added += 1
            vecs = emb.embed(chunks)
            ids = [f"{h}:{i}" for i in range(len(chunks))]
            metas = [{"source": path, "chunk": i} for i in range(len(chunks))]
            store.upsert(ids, vecs, chunks, metas)
            store.record_hash(path, h)
    return {"added": added, "skipped": skipped, "updated": updated}
```

- [ ] **Step 5: Run test, confirm PASS.**

- [ ] **Step 6: Commit** — `git commit -am "feat(rag): chroma store + incremental index_folder with embedder-stamp guard"`

---

### Task 4: Retriever + `ask`

**Files:**
- Create: `my_learning_projects/rag/ask.py`
- Test: append to `test_rag.py`

**Interfaces:**
- Consumes: `get_embedder`, `get_llm` (Task 1); `get_store` (Task 3).
- Produces:
  - `retrieve(question, cfg) -> list[dict]` — the seam. `plain` = embed question, `store.query` top_k. (Agentic swaps in here later, callers unchanged.)
  - `build_context(chunks) -> str` — formats chunks with `[source: ...]` tags.
  - `ask(question, cfg) -> dict` returning `{"answer": str, "sources": list[str]}`.

- [ ] **Step 1: Failing test** (stub the LLM so the test needs no API key)

```python
from ask import build_context, retrieve

def test_build_context_tags_sources():
    ctx = build_context([{"text": "Paris.", "source": "/f/doc.md", "chunk": 0}])
    assert "doc.md" in ctx and "Paris." in ctx

def test_retrieve_finds_relevant(tmp_path):
    from index import index_folder
    from backends import load_config
    (tmp_path / "doc.md").write_text("The capital of France is Paris. " * 30)
    cfg = {**load_config(), "db_dir": str(tmp_path / "db"), "embed": "local", "store": "chroma"}
    index_folder(str(tmp_path), cfg)
    hits = retrieve("What is the capital of France?", {**cfg, "retrieval": "plain"})
    assert any("Paris" in h["text"] for h in hits)
```

- [ ] **Step 2: Run, confirm FAIL.**

- [ ] **Step 3: Implement `ask.py`**

```python
import os
from backends import get_embedder, get_llm
from store import get_store

def retrieve(question, cfg):
    if cfg["retrieval"] != "plain":
        raise ValueError(f"unknown retrieval: {cfg['retrieval']}")  # ponytail: agentic wrapper goes here
    emb = get_embedder(cfg)
    store = get_store(cfg, emb.name)
    qvec = emb.embed([question])[0]
    return store.query(qvec, cfg["top_k"])

def build_context(chunks):
    parts = []
    for h in chunks:
        name = os.path.basename(h["source"]) if h.get("source") else "?"
        parts.append(f"[source: {name}]\n{h['text']}")
    return "\n\n---\n\n".join(parts)

def ask(question, cfg):
    hits = retrieve(question, cfg)
    context = build_context(hits)
    answer = get_llm(cfg).answer(question, context)
    sources = sorted({os.path.basename(h["source"]) for h in hits if h.get("source")})
    return {"answer": answer, "sources": sources}
```

- [ ] **Step 4: Run tests, confirm PASS.**

- [ ] **Step 5: Commit** — `git commit -am "feat(rag): retriever seam + ask() with citations"`

---

### Task 5: CLI

**Files:**
- Create: `my_learning_projects/rag/cli.py`
- Create: `my_learning_projects/rag/README.md`

**Interfaces:**
- Consumes: `index_folder` (Task 3), `ask` (Task 4), `load_config` (Task 1).
- Produces: `python -m cli index <folder>` and `python -m cli ask "<question>"` (run from the `rag/` dir).

- [ ] **Step 1: Implement `cli.py`**

```python
import sys
from backends import load_config
from index import index_folder
from ask import ask

def main():
    cfg = load_config()
    if len(sys.argv) < 2:
        print("usage: python -m cli [index <folder> | ask \"<question>\"]"); return
    cmd = sys.argv[1]
    if cmd == "index":
        stats = index_folder(sys.argv[2], cfg)
        print(f"indexed: +{stats['added']} new, {stats['updated']} updated, {stats['skipped']} unchanged")
    elif cmd == "ask":
        res = ask(sys.argv[2], cfg)
        print(res["answer"])
        print("\nsources:", ", ".join(res["sources"]) or "(none)")
    else:
        print(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write `README.md`** — install (`pip install anthropic chromadb sentence-transformers pymupdf pyyaml ollama`), the four switches, `export ANTHROPIC_API_KEY=...` (or `ant auth login`), the embedder-mismatch guard, and the `index <folder>` / `ask "..."` commands.

- [ ] **Step 3: Manual smoke test** — index the `rag/` folder itself and ask a question:

```bash
cd my_learning_projects/rag
python -m cli index .
python -m cli ask "What are the four config switches?"
```
Expected: an answer naming llm/embed/store/retrieval, plus a `sources:` line. Verify the answer is grounded (mentions config.yaml / README).

- [ ] **Step 4: Commit** — `git commit -am "feat(rag): cli + README"`

---

## Phase 2: Web GUI + restructure (DONE)

**Goal:** ChatGPT-style chat over the same engine, persistent history, clean
frontend/backend separation, one central `.env` switch.

### Task 6: Restructure into `backend/` package + central config
- Moved engine modules into `backend/`; renamed `index.py→indexing.py`, `ask.py→engine.py`.
- `backend/config.py`: `get_config()` loads `config.yaml`, then overlays `.env`
  (`RAG_LLM`/`RAG_EMBED`/`RAG_STORE`/`RAG_RETRIEVAL`, plus `RAG_CORPUS_DIR`,
  `RAG_HISTORY_DB`, `RAG_HOST`, `RAG_PORT`, `ANTHROPIC_API_KEY`). `.env` = central switch.
- `engine.py` caches embedder/store/LLM process-wide so the server doesn't reload the
  embedding model per question.
- Updated `cli.py` → `python -m backend.cli`. Tests → `tests/`, imports repointed.

### Task 7: Persistent history (SQLite)
- `backend/history.py`: `conversations` + `messages` tables. Functions:
  `init_db`, `create_conversation`, `list_conversations`, `rename_conversation`,
  `delete_conversation`, `add_message`, `get_messages`. Sources stored as JSON.
- Test `test_history_roundtrip` covers create → add → read → delete.

### Task 8: FastAPI layer (`backend/api.py`)
- Endpoints: `GET /` (serves UI), `GET /api/status`, `POST /api/index`,
  `GET/POST /api/conversations`, `DELETE /api/conversations/{id}`,
  `GET /api/conversations/{id}/messages`, `POST /api/conversations/{id}/chat`.
- First user message titles the conversation. Engine/LLM errors → clean `HTTPException`
  with a readable `detail` (the UI renders it as `⚠ …`, never a raw 500 blob).
- `run.py` boots uvicorn on `RAG_HOST:RAG_PORT`.

### Task 9: Frontend (`frontend/index.html`)
- Single self-contained file, no build step. Sidebar (new chat, conversation list,
  delete, backend pills, Reindex, Theme) + chat column + pinned composer.
- Design: cool-neutral palette, indigo accent (`#4f6bed` / dark `#7c8cf5`), `system-ui`
  body + `ui-monospace` for source chips; token-based light/dark, both themes designed;
  `prefers-reduced-motion` respected. Source files shown as chips under each answer.
- Vanilla `fetch` against the `/api/*` endpoints; theme persisted in `localStorage`.

**Verified:** 7/7 tests pass; live server exercised (status, frontend served,
conversation CRUD, index = 15 files, graceful chat error without API key).

---

## Upgrade paths (deliberately NOT built now)

- **Qdrant** — add a `QdrantStore` with the same `Store` interface; flip `store: qdrant`. Do it when chunk count crosses ~1M or you need heavy metadata filtering.
- **Agentic / hybrid retrieval** — implement behind the `retrieve()` seam under `retrieval: agentic`: LLM issues multiple searches / adds BM25 keyword search, loops until confident. Do it only when plain vector retrieval visibly misses on multi-hop questions.
- **Cloud embeddings** (`embed: openai|voyage`) — add a factory branch; requires re-indexing into a fresh `db_dir` (the stamp guard enforces this).
- **Reranker / query rewriting** — add only when retrieval quality measurably hurts.

## Self-review

- Spec coverage: folder Q&A (Tasks 2–5), three switches + retrieval seam (Tasks 1,3,4), persistent DB (Task 3), incremental indexing (Task 3), citations (Task 4), embedder-stamp guard (Task 3). ✅
- Type consistency: `Store`/`Embedder`/`LLM` method names match across tasks; `retrieve`/`ask`/`build_context` signatures consistent. ✅
- One runnable check per task with assertable behavior; API-key-free tests use local embedder + stubbed context. ✅
