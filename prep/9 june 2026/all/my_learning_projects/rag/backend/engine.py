"""Retrieval seam + ask(): fetch top-k chunks, answer with citations.

Embedder / store / LLM are cached process-wide so the server doesn't reload the
embedding model on every question.
"""
import os

from backend.backends import get_embedder, get_llm
from backend.store import get_store

_emb = _store = _llm = None


def _embedder(cfg):
    global _emb
    if _emb is None:
        _emb = get_embedder(cfg)
    return _emb


def _vector_store(cfg):
    global _store
    if _store is None:
        _store = get_store(cfg, _embedder(cfg).name)
    return _store


def _model(cfg):
    global _llm
    if _llm is None:
        _llm = get_llm(cfg)
    return _llm


def retrieve(question, cfg):
    if cfg["retrieval"] != "plain":
        raise ValueError(f"unknown retrieval: {cfg['retrieval']}")  # ponytail: agentic wrapper goes here
    qvec = _embedder(cfg).embed([question])[0]
    return _vector_store(cfg).query(qvec, cfg["top_k"])


def build_context(chunks):
    parts = []
    for h in chunks:
        name = os.path.basename(h["source"]) if h.get("source") else "?"
        parts.append(f"[source: {name}]\n{h['text']}")
    return "\n\n---\n\n".join(parts)


def ask(question, cfg):
    hits = retrieve(question, cfg)
    context = build_context(hits)
    answer = _model(cfg).answer(question, context)
    sources = sorted({os.path.basename(h["source"]) for h in hits if h.get("source")})
    return {"answer": answer, "sources": sources}
