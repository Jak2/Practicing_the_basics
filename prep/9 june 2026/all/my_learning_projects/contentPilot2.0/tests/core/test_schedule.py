from core.models import ScheduleConfig
from core.schedule import load_schedule, save_schedule


def test_load_schedule_returns_defaults_when_file_missing(tmp_path):
    path = str(tmp_path / "schedule.json")
    cfg = load_schedule(path)
    assert cfg == ScheduleConfig()


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "schedule.json")
    original = ScheduleConfig(enabled=True, interval_hours=12, topics=2, categories=["genz"])
    save_schedule(original, path)

    loaded = load_schedule(path)
    assert loaded == original


def test_save_schedule_creates_lock_file_during_write(tmp_path, mocker):
    path = str(tmp_path / "schedule.json")
    spy = mocker.patch("core.schedule.FileLock", wraps=__import__("filelock").FileLock)
    save_schedule(ScheduleConfig(), path)
    spy.assert_called_once_with(path + ".lock")
