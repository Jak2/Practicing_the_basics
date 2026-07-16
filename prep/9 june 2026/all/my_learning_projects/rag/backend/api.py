"""FastAPI app: serves the chat UI and exposes the RAG engine + history over HTTP."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend import history
from backend.config import get_config
from backend.engine import ask
from backend.indexing import index_folder

CFG = get_config()
history.init_db(CFG["history_db"])
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Folder-RAG")


class ChatIn(BaseModel):
    question: str


class RenameIn(BaseModel):
    title: str


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/status")
def status():
    return {"llm": CFG["llm"], "embed": CFG["embed"], "store": CFG["store"],
            "retrieval": CFG["retrieval"], "corpus_dir": CFG["corpus_dir"]}


@app.post("/api/index")
def do_index():
    return index_folder(CFG["corpus_dir"], CFG)


@app.get("/api/conversations")
def conversations():
    return history.list_conversations(CFG["history_db"])


@app.post("/api/conversations")
def new_conversation():
    cid = history.create_conversation(CFG["history_db"])
    return {"id": cid, "title": "New chat"}


@app.delete("/api/conversations/{cid}")
def remove_conversation(cid: int):
    history.delete_conversation(CFG["history_db"], cid)
    return {"ok": True}


@app.get("/api/conversations/{cid}/messages")
def messages(cid: int):
    return history.get_messages(CFG["history_db"], cid)


@app.post("/api/conversations/{cid}/chat")
def chat(cid: int, body: ChatIn):
    q = body.question.strip()
    if not q:
        raise HTTPException(400, "Empty question")
    # First user message names the conversation.
    existing = history.get_messages(CFG["history_db"], cid)
    if not existing:
        history.rename_conversation(CFG["history_db"], cid, q[:60])
    history.add_message(CFG["history_db"], cid, "user", q)
    try:
        result = ask(q, CFG)
    except Exception as e:  # surface engine/LLM errors to the UI instead of a 500 blob
        raise HTTPException(500, f"{type(e).__name__}: {e}")
    history.add_message(CFG["history_db"], cid, "assistant", result["answer"], result["sources"])
    return result
