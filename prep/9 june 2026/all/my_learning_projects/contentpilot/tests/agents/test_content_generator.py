import pytest
from unittest.mock import MagicMock
from core.config import get_config
from core.models import TopicResult
from agents.content_generator import ContentGenerator

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_topic():
    return TopicResult(
        title="AI agents are taking over workflows",
        summary="AI agents are replacing repetitive business tasks",
        source="tavily",
        category="generative-ai",
        url="https://example.com",
    )


def test_run_prompt_returns_slug_and_markdown(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\n"
        'title: "AI Workflow Agent"\n'
        'description: "Automate your business workflows with AI"\n'
        'image: ""\n'
        'tags: ["AI", "Automation"]\n'
        'created_at: "2026-06-25"\n'
        "---\n\n"
        "You are an expert AI workflow consultant...\n"
    )
    mocker.patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=mock_llm)

    agent = ContentGenerator(get_config(FIXTURE))
    slug, md = agent.run(make_topic(), "prompt")

    assert slug
    assert "-" in slug or slug.replace("-", "").isalnum()
    assert "---" in md
    assert "title:" in md


def test_run_workflow_contains_steps(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\n"
        'title: "AI Workflow Pipeline"\n'
        'description: "Build an AI workflow in 3 steps"\n'
        'tags: ["AI", "Workflow"]\n'
        'created_at: "2026-06-25"\n'
        "---\n\n"
        "## Step 1: Research\nResearch your topic\n\n"
        "## Step 2: Draft\nWrite a draft\n\n"
        "## Step 3: Publish\nPublish the content\n"
    )
    mocker.patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=mock_llm)

    agent = ContentGenerator(get_config(FIXTURE))
    slug, md = agent.run(make_topic(), "workflow")

    assert "## Step" in md


def test_slug_is_kebab_case(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "fake"})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "---\ntitle: \"My Test Post\"\ndescription: \"desc\"\n"
        "tags: []\ncreated_at: \"2026-06-25\"\n---\n\nContent\n"
    )
    mocker.patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=mock_llm)
    agent = ContentGenerator(get_config(FIXTURE))
    slug, _ = agent.run(make_topic(), "prompt")
    assert " " not in slug
    assert slug == slug.lower()
