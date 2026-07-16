"""Central configuration. `.env` overrides `config.yaml` — one place to control everything."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def get_config():
    with open(ROOT / "config.yaml") as f:
        cfg = yaml.safe_load(f)

    # .env is the central switch — override engine behavior from there
    for key in ("llm", "embed", "store", "retrieval"):
        env = os.getenv(f"RAG_{key.upper()}")
        if env:
            cfg[key] = env
    if os.getenv("RAG_OLLAMA_MODEL"):
        cfg["ollama_model"] = os.getenv("RAG_OLLAMA_MODEL")

    cfg["db_dir"] = str(ROOT / cfg.get("db_dir", ".rag_db"))
    cfg["corpus_dir"] = os.getenv("RAG_CORPUS_DIR", str(ROOT))
    cfg["history_db"] = str(ROOT / os.getenv("RAG_HISTORY_DB", ".rag_history.sqlite"))
    cfg["host"] = os.getenv("RAG_HOST", "127.0.0.1")
    cfg["port"] = int(os.getenv("RAG_PORT", "8000"))
    return cfg
