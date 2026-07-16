"""File loading, chunking, hashing, and incremental folder indexing."""
import hashlib
import os

from backend.backends import get_embedder
from backend.store import get_store


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
        cur.extend(w)
        count += len(w)
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def index_folder(folder, cfg):
    emb = get_embedder(cfg)
    store = get_store(cfg, emb.name)
    known = store.known_hashes()
    added = skipped = updated = 0
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip .git, .venv, .pytest_cache, ...
        for fn in files:
            if fn.startswith("."):
                continue
            path = os.path.join(root, fn)
            if os.path.abspath(path).startswith(os.path.abspath(cfg["db_dir"])):
                continue
            h = file_hash(path)
            if known.get(path) == h:
                skipped += 1
                continue
            text = load_file(path)
            if not text.strip():
                continue
            chunks = chunk_text(text, cfg["chunk_tokens"], cfg["chunk_overlap"])
            if not chunks:
                continue
            if path in known:
                store.delete_by_source(path)
                updated += 1
            else:
                added += 1
            vecs = emb.embed(chunks)
            ids = [f"{h}:{i}" for i in range(len(chunks))]
            metas = [{"source": path, "chunk": i} for i in range(len(chunks))]
            store.upsert(ids, vecs, chunks, metas)
            store.record_hash(path, h)
    return {"added": added, "skipped": skipped, "updated": updated}
