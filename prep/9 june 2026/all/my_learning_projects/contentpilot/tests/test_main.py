import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from main import app

runner = CliRunner()


def test_cli_invokes_orchestrator(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, input="2\n1\n1\ngenerative-ai\n")

    assert result.exit_code == 0
    mock_orch.run.assert_called_once_with(
        n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"], draft=True,
    )


def test_cli_handles_all_categories(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, input="1\n2\n0\nall\n")

    assert result.exit_code == 0
    _, kwargs = mock_orch.run.call_args
    assert kwargs["categories"] == ["all"]


def test_cli_flags_bypass_interactive_prompts(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, [
        "--topics", "2", "--prompts", "1", "--workflows", "1", "--categories", "generative-ai",
    ])

    assert result.exit_code == 0
    mock_orch.run.assert_called_once_with(
        n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"], draft=True,
    )


def test_cli_publish_flag_sets_draft_false(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, [
        "--topics", "1", "--prompts", "1", "--workflows", "0", "--categories", "all", "--publish",
    ])

    assert result.exit_code == 0
    _, kwargs = mock_orch.run.call_args
    assert kwargs["draft"] is False


def test_cli_negative_topics_fails_fast(mocker):
    mock_orch = MagicMock()
    mocker.patch("main.Orchestrator", return_value=mock_orch)

    result = runner.invoke(app, ["--topics", "-1", "--prompts", "1", "--workflows", "0"])

    assert result.exit_code != 0
    mock_orch.run.assert_not_called()
