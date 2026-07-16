from backend.config import get_config
from backend.backends import get_embedder
from backend.indexing import chunk_text, file_hash, index_folder
from backend.engine import build_context, retrieve
from backend import history


def _cfg(tmp_path, **over):
    base = get_config()
    base.update({"db_dir": str(tmp_path / "db"), "embed": "local", "store": "chroma",
                 "retrieval": "plain"})
    base.update(over)
    return base


def test_local_embedder_has_name_and_embeds():
    emb = get_embedder({"embed": "local"})
    assert emb.name
    vecs = emb.embed(["hello world", "goodbye"])
    assert len(vecs) == 2 and len(vecs[0]) > 0


def test_chunk_splits_and_overlaps():
    text = "\n\n".join(f"Paragraph {i} " * 60 for i in range(5))
    chunks = chunk_text(text, size_tokens=100, overlap=20)
    assert len(chunks) >= 2 and all(c.strip() for c in chunks)


def test_file_hash_stable(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello")
    assert file_hash(str(p)) == file_hash(str(p))


def test_index_folder_incremental(tmp_path):
    (tmp_path / "doc.md").write_text("The capital of France is Paris. " * 30)
    cfg = _cfg(tmp_path)
    stats = index_folder(str(tmp_path), cfg)
    assert stats["added"] >= 1
    stats2 = index_folder(str(tmp_path), cfg)
    assert stats2["added"] == 0 and stats2["skipped"] >= 1


def test_build_context_tags_sources():
    ctx = build_context([{"text": "Paris.", "source": "/f/doc.md", "chunk": 0}])
    assert "doc.md" in ctx and "Paris." in ctx


def test_retrieve_finds_relevant(tmp_path):
    (tmp_path / "doc.md").write_text("The capital of France is Paris. " * 30)
    cfg = _cfg(tmp_path)
    index_folder(str(tmp_path), cfg)
    # engine caches globals; reset so the tmp store is used
    import backend.engine as eng
    eng._emb = eng._store = None
    hits = retrieve("What is the capital of France?", cfg)
    assert any("Paris" in h["text"] for h in hits)


def test_history_roundtrip(tmp_path):
    db = str(tmp_path / "h.sqlite")
    history.init_db(db)
    cid = history.create_conversation(db, "First")
    history.add_message(db, cid, "user", "hi")
    history.add_message(db, cid, "assistant", "hello", ["a.md"])
    msgs = history.get_messages(db, cid)
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[1]["sources"] == ["a.md"]
    assert any(c["id"] == cid for c in history.list_conversations(db))
    history.delete_conversation(db, cid)
    assert history.get_messages(db, cid) == []
