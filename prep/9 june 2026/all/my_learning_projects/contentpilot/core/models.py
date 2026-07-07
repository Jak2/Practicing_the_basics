from pydantic import BaseModel, field_validator
from typing import Literal
from datetime import datetime


class TopicResult(BaseModel):
    title: str
    summary: str
    source: Literal["tavily", "reddit", "hackernews"]
    category: str
    url: str


class PostEntry(BaseModel):
    slug: str
    title: str
    type: Literal["prompt", "workflow"]
    category: str
    topic: str
    status: Literal["draft", "published", "deleted", "failed"]
    push_status: Literal["pushed", "failed", "no_remote"] | None = None

    @field_validator("status", mode="before")
    @classmethod
    def _migrate_legacy_status(cls, v):
        # manifest.json files written before 2026-07-02 used "pushed"
        return "published" if v == "pushed" else v
    created_at: datetime
    file_path: str
    image_path: str | None = None
    source_url: str
    git_commit: str | None = None


class ManifestState(BaseModel):
    posts: list[PostEntry] = []


class ScheduleConfig(BaseModel):
    enabled: bool = False
    interval_hours: int = 24
    topics: int = 3
    prompts: int = 1
    workflows: int = 1
    categories: list[str] = ["all"]
    publish: bool = False
