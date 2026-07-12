import hashlib
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


def trend_id(source: str, prompt: str) -> str:
    return hashlib.sha1(f"{source}:{prompt}".encode()).hexdigest()[:12]


class TrendInsight(BaseModel):
    pattern_tags: list[str]
    why_viral: str
    category: str


class TrendItem(BaseModel):
    id: str
    prompt: str
    source: Literal["civitai", "promptschat"]
    kind: Literal["image", "text"]
    image_url: str | None = None
    source_url: str = ""
    engagement: int = 0
    virality_score: float = 0.0
    insight: TrendInsight | None = None
    fetched_at: datetime


class TrendState(BaseModel):
    trends: list[TrendItem] = []
    last_refreshed: datetime | None = None
