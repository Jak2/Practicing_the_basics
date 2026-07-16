"""Entrypoint: start the web GUI. `python run.py` then open the printed URL."""
import uvicorn

from backend.config import get_config

if __name__ == "__main__":
    cfg = get_config()
    print(f"Folder-RAG → http://{cfg['host']}:{cfg['port']}  (corpus: {cfg['corpus_dir']})")
    uvicorn.run("backend.api:app", host=cfg["host"], port=cfg["port"])
