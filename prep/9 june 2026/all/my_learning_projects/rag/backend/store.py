"""Vector store wrapper (Chroma) with embedder-identity + file-hash tracking."""


class ChromaStore:
    def __init__(self, db_dir):
        import chromadb
        self._client = chromadb.PersistentClient(path=db_dir)
        self._col = self._client.get_or_create_collection("chunks")
        self._meta = self._client.get_or_create_collection("meta")

    def embedder_name(self):
        got = self._meta.get(ids=["embedder"])
        return got["metadatas"][0]["name"] if got["ids"] else None

    def set_embedder_name(self, name):
        self._meta.upsert(ids=["embedder"], documents=["_"],
                          metadatas=[{"name": name}], embeddings=[[0.0]])

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
