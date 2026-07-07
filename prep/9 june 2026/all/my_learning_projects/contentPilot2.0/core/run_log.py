from __future__ import annotations
from datetime import datetime, UTC
from typing import Literal, Optional
from pathlib import Path
from filelock import FileLock
from pydantic import BaseModel
import uuid

DEFAULT_PATH = "run_log.json"


class StepLog(BaseModel):
    name: str
    label: str
    module: str = ""
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Literal["running", "success", "failed", "skipped"] = "running"
    detail: Optional[str] = None
    error: Optional[str] = None
    children: list["StepLog"] = []


class RunLog(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Literal["running", "success", "partial", "failed"] = "running"
    steps: list[StepLog] = []


class RunLogState(BaseModel):
    runs: list[RunLog] = []


def _now() -> datetime:
    return datetime.now(UTC)


def new_step(name: str, label: str, module: str = "") -> StepLog:
    return StepLog(name=name, label=label, module=module, started_at=_now())


def finish_step(step: StepLog, status: str, detail: str | None = None, error: str | None = None) -> StepLog:
    step.finished_at = _now()
    step.duration_ms = int((step.finished_at - step.started_at).total_seconds() * 1000)
    step.status = status
    if detail:
        step.detail = detail
    if error:
        step.error = str(error)[:400]
    return step


def new_run() -> RunLog:
    return RunLog(run_id=str(uuid.uuid4())[:8], started_at=_now())


def finish_run(run: RunLog, status: str) -> None:
    run.finished_at = _now()
    run.duration_ms = int((run.finished_at - run.started_at).total_seconds() * 1000)
    run.status = status


def load_run_log(path: str = DEFAULT_PATH) -> RunLogState:
    p = Path(path)
    if not p.exists():
        return RunLogState()
    return RunLogState.model_validate_json(p.read_text())


def append_run(run: RunLog, path: str = DEFAULT_PATH) -> None:
    with FileLock(path + ".lock"):
        state = load_run_log(path)
        state.runs = ([run] + state.runs)[:20]
        Path(path).write_text(state.model_dump_json(indent=2))
