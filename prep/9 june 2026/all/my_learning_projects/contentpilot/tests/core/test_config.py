import pytest
from core.config import get_config


FIXTURE = "tests/fixtures/config_valid.yaml"


def test_get_config_loads_target_repo():
    cfg = get_config(FIXTURE)
    assert cfg.target_repo == "/tmp/fake-repo"


def test_get_config_content_paths():
    cfg = get_config(FIXTURE)
    assert cfg.content_paths.prompts == "content/prompts"
    assert cfg.content_paths.workflows == "content/workflows"
    assert cfg.content_paths.images == "public/images"


def test_get_config_llm():
    cfg = get_config(FIXTURE)
    assert cfg.llm.provider == "google"
    assert cfg.llm.model == "gemini-2.0-flash"


def test_get_config_sources_reddit():
    cfg = get_config(FIXTURE)
    assert cfg.sources.reddit.enabled is True
    assert "MachineLearning" in cfg.sources.reddit.subreddits


def test_get_config_dashboard_port():
    cfg = get_config(FIXTURE)
    assert cfg.dashboard.port == 8000


def test_get_config_missing_file():
    with pytest.raises(FileNotFoundError):
        get_config("nonexistent.yaml")
