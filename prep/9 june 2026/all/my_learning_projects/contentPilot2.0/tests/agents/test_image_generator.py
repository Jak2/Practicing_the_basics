from unittest.mock import MagicMock
from core.config import get_config
from agents.image_generator import ImageGenerator

FIXTURE = "tests/fixtures/config_valid.yaml"


def _make_mock_client(fake_image_bytes: bytes, mocker) -> MagicMock:
    mock_image = MagicMock()
    mock_image.image.image_bytes = fake_image_bytes

    mock_response = MagicMock()
    mock_response.generated_images = [mock_image]

    mock_client = MagicMock()
    mock_client.models.generate_images.return_value = mock_response

    mocker.patch("agents.image_generator.genai.Client", return_value=mock_client)
    return mock_client


def test_run_saves_image_and_returns_path(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    _make_mock_client(fake_bytes, mocker)

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    rel_path = agent.run("AI workflow agents", "ai-workflow-agents", str(tmp_path))

    assert rel_path == "public/images/ai-workflow-agents.png"
    assert (tmp_path / "public" / "images" / "ai-workflow-agents.png").exists()


def test_run_creates_image_dir_if_missing(mocker, tmp_path):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    _make_mock_client(fake_bytes, mocker)

    cfg = get_config(FIXTURE)
    agent = ImageGenerator(cfg)
    agent.run("test", "test-slug", str(tmp_path))

    assert (tmp_path / "public" / "images").is_dir()
