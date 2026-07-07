import json
from core.models import TopicResult
from agents.orchestrator import Orchestrator

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_topic(n: int = 0) -> TopicResult:
    return TopicResult(
        title=f"Topic {n}", summary="summary", source="tavily",
        category="generative-ai", url="https://example.com",
    )


def _patch_agent_inits(mocker):
    """Patch all agent constructors to avoid real API/SDK initialization."""
    mocker.patch("agents.orchestrator.TrendDiscovery.__init__", return_value=None)
    mocker.patch("agents.orchestrator.ContentGenerator.__init__", return_value=None)
    mocker.patch("agents.orchestrator.ImageGenerator.__init__", return_value=None)
    mocker.patch("agents.orchestrator.GitPublisher.__init__", return_value=None)


def test_run_generates_correct_file_count(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    _patch_agent_inits(mocker)
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [make_topic(0), make_topic(1)],
        {"tavily": {"count": 0, "error": None, "skipped": True},
         "reddit": {"count": 0, "error": None, "skipped": True},
         "hackernews": {"count": 2, "error": None, "skipped": False}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("test-slug", "---\ntitle: t\n---\ncontent"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/test-slug.png")
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="abc1234")
    mocker.patch("agents.orchestrator.GitPublisher.push", return_value="pushed")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path, run_log_path=str(tmp_path / "run_log.json"))
    orch.run(n_topics=2, n_prompts=1, n_workflows=1, categories=["generative-ai"])

    with open(manifest_path) as f:
        data = json.load(f)

    assert len(data["posts"]) == 4  # 2 topics × (1 prompt + 1 workflow)


def test_run_marks_posts_as_pushed(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    _patch_agent_inits(mocker)
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [make_topic(0)],
        {"tavily": {"count": 0, "error": None, "skipped": True},
         "reddit": {"count": 0, "error": None, "skipped": True},
         "hackernews": {"count": 2, "error": None, "skipped": False}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("slug-x", "---\ntitle: x\n---\nok"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/slug-x.png")
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="def5678")
    mocker.patch("agents.orchestrator.GitPublisher.push", return_value="pushed")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path, run_log_path=str(tmp_path / "run_log.json"))
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"])

    with open(manifest_path) as f:
        data = json.load(f)

    assert data["posts"][0]["status"] == "published"
    assert data["posts"][0]["git_commit"] == "def5678"


def test_ollama_provider_does_not_init_image_generator(mocker, tmp_path):
    """With provider=ollama, Orchestrator must not initialise ImageGenerator."""
    manifest_path = str(tmp_path / "manifest.json")

    mocker.patch("agents.orchestrator.TrendDiscovery.__init__", return_value=None)
    mocker.patch("agents.orchestrator.ContentGenerator.__init__", return_value=None)
    mocker.patch("agents.orchestrator.GitPublisher.__init__", return_value=None)
    mock_image_init = mocker.patch("agents.orchestrator.ImageGenerator.__init__", return_value=None)

    orch = Orchestrator(config_path="tests/fixtures/config_ollama.yaml", manifest_path=manifest_path, run_log_path=str(tmp_path / "run_log.json"))

    mock_image_init.assert_not_called()
    assert orch.image is None


def test_orchestrator_draft_mode_skips_push_and_sets_status_draft(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    _patch_agent_inits(mocker)
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [make_topic(0)],
        {"tavily": {"count": 0, "error": None, "skipped": True},
         "reddit": {"count": 0, "error": None, "skipped": True},
         "hackernews": {"count": 1, "error": None, "skipped": False}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("my-slug", "content"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/my-slug.png")
    mock_publish = mocker.patch("agents.orchestrator.GitPublisher.publish", return_value=None)
    mock_push = mocker.patch("agents.orchestrator.GitPublisher.push", return_value="pushed")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path, run_log_path=str(tmp_path / "run_log.json"))
    orch.git.drafts_dir = tmp_path / "drafts"
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"], draft=True)

    mock_publish.assert_called_once()
    assert mock_publish.call_args.kwargs.get("draft") is True
    mock_push.assert_not_called()

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["posts"][0]["status"] == "draft"
    assert data["posts"][0]["push_status"] is None


def test_orchestrator_live_mode_pushes_per_post_and_records_push_status(mocker, tmp_path):
    manifest_path = str(tmp_path / "manifest.json")

    _patch_agent_inits(mocker)
    mocker.patch("agents.orchestrator.TrendDiscovery.run", return_value=(
        [make_topic(0)],
        {"tavily": {"count": 0, "error": None, "skipped": True},
         "reddit": {"count": 0, "error": None, "skipped": True},
         "hackernews": {"count": 1, "error": None, "skipped": False}},
    ))
    mocker.patch("agents.orchestrator.ContentGenerator.run", return_value=("my-slug", "content"))
    mocker.patch("agents.orchestrator.ImageGenerator.run", return_value="public/images/my-slug.png")
    mocker.patch("agents.orchestrator.GitPublisher.publish", return_value="def5678")
    mocker.patch("agents.orchestrator.GitPublisher.push", return_value="pushed")

    orch = Orchestrator(config_path=FIXTURE, manifest_path=manifest_path, run_log_path=str(tmp_path / "run_log.json"))
    orch.run(n_topics=1, n_prompts=1, n_workflows=0, categories=["generative-ai"], draft=False)

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["posts"][0]["status"] == "published"
    assert data["posts"][0]["push_status"] == "pushed"
    assert data["posts"][0]["git_commit"] == "def5678"
