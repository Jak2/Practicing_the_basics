"""Local web dashboard for the Trend Engine — stdlib only, no new dependencies.

Serves ui/index.html and a small JSON API:
  GET  /api/status  -> environment checks, latest run info, run history
  GET  /api/log      -> tail of the currently-running (or last) run's output
  POST /api/launch    -> spawns `python3 run_daily.py` as a background subprocess

Usage: python3 ui/server.py  (then open http://localhost:8765)
"""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from trend_engine import config  # noqa: E402

PORT = 8765
RUN_LOG_PATH = REPO_ROOT / "output" / "run_log.md"
LIVE_LOG_PATH = REPO_ROOT / "output" / "ui_run.log"

_state_lock = threading.Lock()
_state = {"running": False, "started_at": None, "finished_at": None,
          "exit_code": None, "proc": None}


def _read_run_log_rows(limit=10):
    if not RUN_LOG_PATH.exists():
        return []
    lines = RUN_LOG_PATH.read_text().splitlines()
    data_lines = [ln for ln in lines if ln.startswith("|") and "date" not in ln and "---" not in ln]
    rows = []
    for ln in data_lines[-limit:]:
        parts = [p.strip() for p in ln.strip("|").split("|")]
        if len(parts) == 5:
            rows.append({"date": parts[0], "items": parts[1], "topics": parts[2],
                         "enriched": parts[3], "duration_s": parts[4]})
    return list(reversed(rows))


def _latest_output_dir():
    out_dir = REPO_ROOT / "output"
    if not out_dir.exists():
        return None
    day_dirs = sorted((d for d in out_dir.iterdir() if d.is_dir()), reverse=True)
    return day_dirs[0].name if day_dirs else None


def _run_pipeline():
    with _state_lock:
        _state["running"] = True
        _state["started_at"] = time.time()
        _state["finished_at"] = None
        _state["exit_code"] = None

    LIVE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LIVE_LOG_PATH, "w") as log_f:
        proc = subprocess.Popen(
            [sys.executable, "run_daily.py"],
            cwd=str(REPO_ROOT), stdout=log_f, stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        with _state_lock:
            _state["proc"] = proc
        exit_code = proc.wait()

    with _state_lock:
        _state["running"] = False
        _state["finished_at"] = time.time()
        _state["exit_code"] = exit_code
        _state["proc"] = None


def _status_payload():
    with _state_lock:
        running = _state["running"]
        started_at = _state["started_at"]
        finished_at = _state["finished_at"]
        exit_code = _state["exit_code"]

    return {
        "running": running,
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": exit_code,
        "env": {
            "youtube_api_key_set": bool(os.environ.get("YOUTUBE_API_KEY")),
            "anthropic_api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        },
        "sources_enabled": config.SOURCE_ENABLED,
        "run_history": _read_run_log_rows(),
        "latest_output_dir": _latest_output_dir(),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep terminal quiet; UI shows what matters

    def _send_json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/status":
            self._send_json(_status_payload())
        elif self.path == "/api/log":
            text = LIVE_LOG_PATH.read_text()[-8000:] if LIVE_LOG_PATH.exists() else ""
            self._send_json({"log": text})
        elif self.path in ("/", "/index.html"):
            self._serve_file(Path(__file__).parent / "index.html", "text/html")
        else:
            # serve today's report + briefs so the dashboard can link straight to them
            requested = (REPO_ROOT / self.path.lstrip("/")).resolve()
            if REPO_ROOT in requested.parents and requested.exists() and requested.is_file():
                ctype = "text/html" if requested.suffix == ".html" else "application/json"
                self._serve_file(requested, ctype)
            else:
                self._send_json({"error": "not found"}, code=404)

    def _serve_file(self, path, ctype):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/launch":
            with _state_lock:
                already_running = _state["running"]
            if already_running:
                self._send_json({"error": "already running"}, code=409)
                return
            threading.Thread(target=_run_pipeline, daemon=True).start()
            self._send_json({"started": True})
        else:
            self._send_json({"error": "not found"}, code=404)


def main():
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"Trend Engine dashboard: http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
