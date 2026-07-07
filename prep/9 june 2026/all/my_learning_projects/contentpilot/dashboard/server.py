import asyncio
import os
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from core.config import get_config
from core.manifest import load_manifest, delete_post, update_post_status
from core.run_log import load_run_log
from agents.git_publisher import GitPublisher
from agents.orchestrator import Orchestrator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.schedule import load_schedule, save_schedule
from core.models import ScheduleConfig

MANIFEST_PATH = "manifest.json"
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

app = FastAPI(title="ContentPilot Dashboard")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

scheduler = AsyncIOScheduler()


def _scheduled_run() -> None:
    cfg = load_schedule()
    if not cfg.enabled:
        return
    try:
        orch = Orchestrator()
        orch.run(
            n_topics=cfg.topics,
            n_prompts=cfg.prompts,
            n_workflows=cfg.workflows,
            categories=cfg.categories,
            draft=not cfg.publish,
        )
    except Exception as e:
        # A scheduled run must never take the schedule down with it — log and
        # let the next interval fire normally. Orchestrator.run() already
        # catches and logs per-step failures into run_log.json; this is the
        # outer guard for anything that escapes that (e.g. a bad config).
        import sys
        print(f"[ContentPilot] Scheduled run failed: {e}", file=sys.stderr)


def _reschedule() -> None:
    scheduler.remove_all_jobs()
    cfg = load_schedule()
    if cfg.enabled:
        scheduler.add_job(_scheduled_run, "interval", hours=cfg.interval_hours, id="contentpilot_schedule")


@app.on_event("startup")
async def _on_startup() -> None:
    scheduler.start()
    _reschedule()

try:
    _config = get_config()
except FileNotFoundError:
    _config = None

if _config:
    public_dir = Path(_config.target_repo) / "public"
    if public_dir.exists():
        app.mount("/public", StaticFiles(directory=str(public_dir)), name="repo-public")

# Serve draft images (drafts.html references /drafts/<image_path>)
_drafts_dir = Path("drafts")
_drafts_dir.mkdir(exist_ok=True)
app.mount("/drafts-files", StaticFiles(directory=str(_drafts_dir)), name="drafts-files")


def _read_file(file_path: str) -> str:
    if not _config:
        return ""
    p = Path(_config.target_repo) / file_path
    return p.read_text() if p.exists() else ""


def _read_draft_file(file_path: str) -> str:
    p = Path("drafts") / file_path
    return p.read_text() if p.exists() else ""


def _strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].strip()
    return content.strip()


def _preview(content: str, n: int = 280) -> str:
    body = _strip_frontmatter(content)
    return body[:n] + ("…" if len(body) > n else "")


def _pipeline_stats(posts):
    prompts = [p for p in posts if p.type == "prompt"]
    workflows = [p for p in posts if p.type == "workflow"]
    published = [p for p in posts if p.status == "published"]
    failed = [p for p in posts if p.status == "failed"]
    images_ok = [p for p in prompts if p.image_path]
    images_failed = [p for p in prompts if not p.image_path]

    sources = []
    if _config:
        if _config.sources.tavily:
            sources.append("Tavily")
        if _config.sources.reddit.enabled:
            sources.append("Reddit")
        if _config.sources.hackernews.enabled:
            sources.append("HackerNews")

    return {
        "topics": len({p.topic for p in posts}),
        "prompts": len(prompts),
        "workflows": len(workflows),
        "content_total": len(posts),
        "images_ok": len(images_ok),
        "images_failed": len(images_failed),
        "published": len(published),
        "failed": len(failed),
        "sources": sources,
    }


@app.get("/")
async def index(request: Request):
    state = load_manifest(MANIFEST_PATH)
    active = [p for p in state.posts if p.status != "deleted"]
    stats = _pipeline_stats(active)

    by_topic = defaultdict(list)
    for post in active:
        content = _read_file(post.file_path)
        by_topic[post.topic].append({
            "slug": post.slug,
            "title": post.title,
            "type": post.type,
            "category": post.category,
            "status": post.status,
            "image_path": post.image_path,
            "source_url": post.source_url,
            "git_commit": post.git_commit,
            "push_status": post.push_status,
            "created_at": post.created_at,
            "preview": _preview(content),
            "has_content": bool(content),
        })

    return templates.TemplateResponse(
        request,
        "index.html",
        {"stats": stats, "by_topic": dict(by_topic), "total": len(active)},
    )


@app.get("/post/{slug}")
async def post_detail(request: Request, slug: str):
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    raw = _read_file(post.file_path)
    body = _strip_frontmatter(raw)
    return templates.TemplateResponse(
        request, "post.html", {"post": post, "body": body}
    )


@app.get("/pipeline")
async def pipeline(request: Request):
    state = load_run_log("run_log.json")
    latest = state.runs[0] if state.runs else None
    history = state.runs[1:6]  # last 5 older runs for the sidebar
    return templates.TemplateResponse(
        request,
        "pipeline.html",
        {"run": latest, "history": history},
    )


@app.get("/drafts")
async def drafts_page(request: Request):
    state = load_manifest(MANIFEST_PATH)
    drafts = [p for p in state.posts if p.status == "draft"]
    items = []
    for post in drafts:
        content = _read_draft_file(post.file_path)
        items.append({
            "slug": post.slug,
            "title": post.title,
            "type": post.type,
            "category": post.category,
            "image_path": post.image_path,
            "source_url": post.source_url,
            "created_at": post.created_at,
            "preview": _preview(content),
        })
    return templates.TemplateResponse(request, "drafts.html", {"drafts": items, "total": len(items)})


@app.post("/api/drafts/{slug}/approve")
async def approve_draft(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug and p.status == "draft"), None)
    if not post:
        raise HTTPException(status_code=404, detail="Draft not found")
    publisher = GitPublisher(_config)
    commit_sha, push_status = publisher.publish_draft(slug, post.type, post.image_path)
    update_post_status(slug, status="published", push_status=push_status, git_commit=commit_sha, path=MANIFEST_PATH)
    return JSONResponse({"status": "published", "slug": slug, "commit": commit_sha, "push_status": push_status})


@app.post("/api/drafts/{slug}/reject")
async def reject_draft(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug and p.status == "draft"), None)
    if not post:
        raise HTTPException(status_code=404, detail="Draft not found")
    publisher = GitPublisher(_config)
    publisher.discard_draft(slug, post.type)
    delete_post(slug, MANIFEST_PATH)
    return JSONResponse({"status": "rejected", "slug": slug})


class RunNowRequest(BaseModel):
    topics: int = Field(ge=0)
    prompts: int = Field(ge=0)
    workflows: int = Field(ge=0)
    categories: list[str]
    publish: bool = False


@app.post("/api/run-now")
async def run_now(payload: RunNowRequest):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")

    def _execute():
        orch = Orchestrator()
        orch.run(
            n_topics=payload.topics,
            n_prompts=payload.prompts,
            n_workflows=payload.workflows,
            categories=payload.categories,
            draft=not payload.publish,
        )

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _execute)
    return JSONResponse({"status": "started"})


@app.get("/schedule")
async def schedule_page(request: Request):
    cfg = load_schedule()
    return templates.TemplateResponse(request, "schedule.html", {"cfg": cfg})


@app.post("/api/schedule")
async def update_schedule(cfg: ScheduleConfig):
    save_schedule(cfg)
    _reschedule()
    return JSONResponse({"status": "saved"})


@app.delete("/api/delete/{slug}")
async def delete(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    publisher = GitPublisher(_config)
    publisher.delete(slug, post.type)
    publisher.push()
    delete_post(slug, MANIFEST_PATH)
    return JSONResponse({"status": "deleted", "slug": slug})


@app.post("/api/repush/{slug}")
async def repush(slug: str):
    if _config is None:
        raise HTTPException(status_code=500, detail="config.yaml not found — run from project root")
    state = load_manifest(MANIFEST_PATH)
    post = next((p for p in state.posts if p.slug == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    file_path = post.file_path
    try:
        with open(f"{_config.target_repo}/{file_path}") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    publisher = GitPublisher(_config)
    sha = publisher.repush(post.slug, content, post.type)
    publisher.push()
    return JSONResponse({"status": "repushed", "slug": slug, "commit": sha})


if __name__ == "__main__":
    cfg = get_config()
    uvicorn.run("dashboard.server:app", host="0.0.0.0", port=cfg.dashboard.port, reload=True)
