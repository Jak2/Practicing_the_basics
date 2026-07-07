from pathlib import Path
from filelock import FileLock
from core.trend_models import TrendState

DEFAULT_PATH = "trends.json"


def _lock_path(path: str) -> str:
    return path + ".lock"


def load_trends(path: str = DEFAULT_PATH) -> TrendState:
    p = Path(path)
    if not p.exists():
        return TrendState()
    return TrendState.model_validate_json(p.read_text())


def save_trends(state: TrendState, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        Path(path).write_text(state.model_dump_json(indent=2))


def delete_trend(trend_id: str, path: str = DEFAULT_PATH) -> None:
    state = load_trends(path)
    state.trends = [t for t in state.trends if t.id != trend_id]
    save_trends(state, path)
