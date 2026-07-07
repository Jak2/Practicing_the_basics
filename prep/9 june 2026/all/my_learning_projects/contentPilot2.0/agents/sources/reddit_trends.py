import os
from datetime import datetime, UTC
import praw
from core.trend_models import TrendItem, trend_id

TEXT_SUBS = ["ChatGPTPromptGenius", "PromptEngineering"]
IMAGE_SUBS = ["StableDiffusion", "midjourney"]
_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


class RedditTrendsSource:
    """Viral prompts from Reddit's weekly top posts.

    Text subs: the post body (selftext) is the prompt. Image subs: the title
    usually carries the prompt; the post URL is the generated image.
    """

    def fetch(self, limit: int = 20) -> list[TrendItem]:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "contentpilot2"),
        )
        per_sub = max(limit // (len(TEXT_SUBS) + len(IMAGE_SUBS)), 2)
        items: list[TrendItem] = []

        for name in TEXT_SUBS:
            for post in reddit.subreddit(name).top(time_filter="week", limit=per_sub):
                prompt = (post.selftext or post.title).strip()
                if not prompt:
                    continue
                items.append(TrendItem(
                    id=trend_id("reddit", prompt),
                    prompt=prompt,
                    source="reddit",
                    kind="text",
                    source_url=f"https://reddit.com{post.permalink}",
                    engagement=post.score,
                    fetched_at=datetime.now(UTC),
                ))

        for name in IMAGE_SUBS:
            for post in reddit.subreddit(name).top(time_filter="week", limit=per_sub):
                url = post.url or ""
                image_url = url if url.lower().endswith(_IMAGE_EXTENSIONS) else None
                items.append(TrendItem(
                    id=trend_id("reddit", post.title),
                    prompt=post.title.strip(),
                    source="reddit",
                    kind="image",
                    image_url=image_url,
                    source_url=f"https://reddit.com{post.permalink}",
                    engagement=post.score,
                    fetched_at=datetime.now(UTC),
                ))

        return items[:limit]
