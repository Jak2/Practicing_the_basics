from pathlib import Path
from filelock import FileLock
from core.models import ScheduleConfig

DEFAULT_PATH = "schedule.json"


def _lock_path(path: str) -> str:
    return path + ".lock"


def load_schedule(path: str = DEFAULT_PATH) -> ScheduleConfig:
    p = Path(path)
    if not p.exists():
        return ScheduleConfig()
    return ScheduleConfig.model_validate_json(p.read_text())


def save_schedule(config: ScheduleConfig, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        Path(path).write_text(config.model_dump_json(indent=2))
