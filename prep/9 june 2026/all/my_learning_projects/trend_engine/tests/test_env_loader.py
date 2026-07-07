import os
from trend_engine.env_loader import load_env


def test_load_env_sets_unset_vars(tmp_path, monkeypatch):
    monkeypatch.delenv("SOME_TEST_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text('SOME_TEST_KEY=abc123\n# a comment\n\nQUOTED_KEY="hello world"\n')
    load_env(env_file)
    try:
        assert os.environ["SOME_TEST_KEY"] == "abc123"
        assert os.environ["QUOTED_KEY"] == "hello world"
    finally:
        os.environ.pop("SOME_TEST_KEY", None)
        os.environ.pop("QUOTED_KEY", None)


def test_load_env_does_not_override_existing_shell_var(tmp_path, monkeypatch):
    monkeypatch.setenv("SOME_TEST_KEY", "from-shell")
    env_file = tmp_path / ".env"
    env_file.write_text("SOME_TEST_KEY=from-dotenv\n")
    load_env(env_file)
    assert os.environ["SOME_TEST_KEY"] == "from-shell"


def test_load_env_missing_file_is_a_noop(tmp_path):
    load_env(tmp_path / "does_not_exist.env")  # must not raise
