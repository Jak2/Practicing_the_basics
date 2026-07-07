import yaml
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ContentPathsConfig(BaseModel):
    prompts: str
    workflows: str
    images: str


class LLMConfig(BaseModel):
    provider: str = "google"
    model: str = "gemini-2.0-flash"
    image_model: str = "imagen-3.0-generate-001"


class RedditConfig(BaseModel):
    enabled: bool = True
    subreddits: list[str] = []


class HackerNewsConfig(BaseModel):
    enabled: bool = True


class SourcesConfig(BaseModel):
    tavily: bool = True
    reddit: RedditConfig = RedditConfig()
    hackernews: HackerNewsConfig = HackerNewsConfig()


class DashboardConfig(BaseModel):
    port: int = 8000


class Config(BaseModel):
    target_repo: str
    content_paths: ContentPathsConfig
    llm: LLMConfig = LLMConfig()
    sources: SourcesConfig = SourcesConfig()
    dashboard: DashboardConfig = DashboardConfig()


def get_config(path: str = "config.yaml") -> Config:
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    return Config(**data)
