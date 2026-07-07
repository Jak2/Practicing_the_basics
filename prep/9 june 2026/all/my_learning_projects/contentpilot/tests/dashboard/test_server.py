import pytest
import json
from datetime import datetime
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from core.models import ManifestState, PostEntry, ScheduleConfig


def make_manifest_with_post(tmp_path) -> tuple[str, PostEntry]:
    post = PostEntry(
        slug="test-post", title="Test Post", type="prompt",
        category="generative-ai", topic="AI trends", status="published",
        created_at=datetime.utcnow(), file_path="content/prompts/test-post.md",
        source_url="https://example.com", git_commit="abc1234",
    )
    state = ManifestState(posts=[post])
    path = str(tmp_path / "manifest.json")
    Path(path).write_text(state.model_dump_json(indent=2))
    return path, post


@pytest.fixture
def test_app(tmp_path, mocker):
    manifest_path, post = make_manifest_with_post(tmp_path)
    mocker.patch("dashboard.server.MANIFEST_PATH", manifest_path)
    mock_cfg = MagicMock()
    mocker.patch("dashboard.server.get_config", return_value=mock_cfg)
    mocker.patch("dashboard.server._config", mock_cfg)
    from dashboard.server import app
    return app


@pytest.mark.asyncio
async def test_index_returns_200(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "Test Post" in response.text


@pytest.mark.asyncio
async def test_post_detail_returns_200(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/post/test-post")
    assert response.status_code == 200
    assert "test-post" in response.text


@pytest.mark.asyncio
async def test_delete_returns_success(test_app, mocker):
    mocker.patch("dashboard.server.GitPublisher")
    mocker.patch("dashboard.server.delete_post")
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.delete("/api/delete/test-post")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_post_not_found_returns_404(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/post/nonexistent-slug")
    assert response.status_code == 404


def make_manifest_with_draft(tmp_path) -> tuple[str, PostEntry]:
    post = PostEntry(
        slug="draft-1", title="Draft One", type="prompt",
        category="generative-ai", topic="AI trends", status="draft",
        created_at=datetime.utcnow(), file_path="content/prompts/draft-1.md",
        source_url="https://example.com",
    )
    state = ManifestState(posts=[post])
    path = str(tmp_path / "manifest.json")
    Path(path).write_text(state.model_dump_json(indent=2))
    return path, post


@pytest.fixture
def draft_app(tmp_path, mocker):
    manifest_path, post = make_manifest_with_draft(tmp_path)
    mocker.patch("dashboard.server.MANIFEST_PATH", manifest_path)
    mock_cfg = MagicMock()
    mocker.patch("dashboard.server.get_config", return_value=mock_cfg)
    mocker.patch("dashboard.server._config", mock_cfg)
    from dashboard.server import app
    return app


@pytest.mark.asyncio
async def test_drafts_page_returns_200(draft_app, mocker):
    mocker.patch("dashboard.server._read_draft_file", return_value="---\ntitle: x\n---\nbody")
    async with AsyncClient(transport=ASGITransport(app=draft_app), base_url="http://test") as client:
        response = await client.get("/drafts")
    assert response.status_code == 200
    assert "Draft One" in response.text


@pytest.mark.asyncio
async def test_approve_draft_calls_publish_draft_and_updates_status(draft_app, mocker):
    mocker.patch("dashboard.server.GitPublisher.__init__", return_value=None)
    mock_publish_draft = mocker.patch(
        "dashboard.server.GitPublisher.publish_draft", return_value=("abc1234", "pushed")
    )
    mock_update = mocker.patch("dashboard.server.update_post_status")

    async with AsyncClient(transport=ASGITransport(app=draft_app), base_url="http://test") as client:
        response = await client.post("/api/drafts/draft-1/approve")

    assert response.status_code == 200
    mock_publish_draft.assert_called_once_with("draft-1", "prompt", None)
    assert mock_update.call_args.kwargs["status"] == "published"
    assert mock_update.call_args.kwargs["push_status"] == "pushed"
    assert mock_update.call_args.kwargs["git_commit"] == "abc1234"


@pytest.mark.asyncio
async def test_reject_draft_discards_and_deletes_manifest_entry(draft_app, mocker):
    mocker.patch("dashboard.server.GitPublisher.__init__", return_value=None)
    mock_discard = mocker.patch("dashboard.server.GitPublisher.discard_draft")
    mock_delete = mocker.patch("dashboard.server.delete_post")

    async with AsyncClient(transport=ASGITransport(app=draft_app), base_url="http://test") as client:
        response = await client.post("/api/drafts/draft-1/reject")

    assert response.status_code == 200
    mock_discard.assert_called_once_with("draft-1", "prompt")
    mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_approve_unknown_draft_returns_404(draft_app):
    async with AsyncClient(transport=ASGITransport(app=draft_app), base_url="http://test") as client:
        response = await client.post("/api/drafts/nope/approve")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_run_now_starts_orchestrator_and_returns_immediately(test_app, mocker):
    mocker.patch("dashboard.server.Orchestrator")
    mock_loop = MagicMock()
    mocker.patch("dashboard.server.asyncio.get_event_loop", return_value=mock_loop)

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/api/run-now", json={
            "topics": 2, "prompts": 1, "workflows": 1, "categories": ["all"], "publish": False,
        })

    assert response.status_code == 200
    assert response.json()["status"] == "started"
    mock_loop.run_in_executor.assert_called_once()


@pytest.mark.asyncio
async def test_run_now_rejects_negative_topics(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/api/run-now", json={
            "topics": -1, "prompts": 1, "workflows": 1, "categories": ["all"], "publish": False,
        })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_schedule_page_returns_200(test_app, mocker):
    mocker.patch("dashboard.server.load_schedule", return_value=ScheduleConfig())
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/schedule")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_schedule_saves_config_and_reschedules(test_app, mocker):
    mock_save = mocker.patch("dashboard.server.save_schedule")
    mock_reschedule = mocker.patch("dashboard.server._reschedule")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/api/schedule", json={
            "enabled": True, "interval_hours": 12, "topics": 2, "prompts": 1,
            "workflows": 1, "categories": ["all"], "publish": False,
        })

    assert response.status_code == 200
    mock_save.assert_called_once()
    mock_reschedule.assert_called_once()


def test_scheduled_run_skips_when_disabled(mocker):
    from dashboard.server import _scheduled_run
    mocker.patch("dashboard.server.load_schedule", return_value=ScheduleConfig(enabled=False))
    mock_orch_class = mocker.patch("dashboard.server.Orchestrator")

    _scheduled_run()

    mock_orch_class.assert_not_called()


def test_scheduled_run_invokes_orchestrator_when_enabled(mocker):
    from dashboard.server import _scheduled_run
    cfg = ScheduleConfig(enabled=True, interval_hours=6, topics=1, prompts=1, workflows=0, categories=["all"], publish=False)
    mocker.patch("dashboard.server.load_schedule", return_value=cfg)
    mock_orch = mocker.patch("dashboard.server.Orchestrator").return_value

    _scheduled_run()

    mock_orch.run.assert_called_once_with(
        n_topics=1, n_prompts=1, n_workflows=0, categories=["all"], draft=True,
    )
