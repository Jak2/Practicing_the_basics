import os
import httpx
import praw
from tavily import TavilyClient
from core.config import Config
from core.models import TopicResult


class TrendDiscovery:
    def __init__(self, config: Config):
        self.config = config
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", "")) if config.sources.tavily else None

    def run(self, categories: list[str], n_topics: int) -> tuple[list[TopicResult], dict[str, dict]]:
        source_results: dict[str, dict] = {}
        results: list[TopicResult] = []

        if self.config.sources.tavily:
            try:
                fetched = self._fetch_tavily(categories, n_topics)
                results.extend(fetched)
                source_results["tavily"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["tavily"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["tavily"] = {"count": 0, "error": None, "skipped": True}

        if self.config.sources.reddit.enabled:
            try:
                fetched = self._fetch_reddit(n_topics)
                results.extend(fetched)
                source_results["reddit"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["reddit"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["reddit"] = {"count": 0, "error": None, "skipped": True}

        if self.config.sources.hackernews.enabled:
            try:
                fetched = self._fetch_hackernews(n_topics)
                results.extend(fetched)
                source_results["hackernews"] = {"count": len(fetched), "error": None, "skipped": False}
            except Exception as e:
                source_results["hackernews"] = {"count": 0, "error": str(e), "skipped": False}
        else:
            source_results["hackernews"] = {"count": 0, "error": None, "skipped": True}

        seen: set[str] = set()
        unique: list[TopicResult] = []
        for r in results:
            if r.title not in seen:
                seen.add(r.title)
                unique.append(r)
        return unique[:n_topics], source_results

    def _fetch_tavily(self, categories: list[str], n: int) -> list[TopicResult]:
        query = f"trending topics 2026 {' OR '.join(categories)}"
        response = self.tavily.search(query=query, max_results=n, search_depth="advanced")
        results = []
        for item in response.get("results", []):
            cat = categories[0] if categories and categories[0] != "all" else "general"
            results.append(TopicResult(
                title=item["title"],
                summary=item.get("content", "")[:300],
                source="tavily",
                category=cat,
                url=item["url"],
            ))
        return results

    def _fetch_reddit(self, n: int) -> list[TopicResult]:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "contentpilot/1.0"),
        )
        results = []
        for sub_name in self.config.sources.reddit.subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=n):
                    results.append(TopicResult(
                        title=post.title,
                        summary=post.selftext[:300] if post.selftext else post.title,
                        source="reddit",
                        category=sub_name.lower(),
                        url=f"https://reddit.com{post.permalink}",
                    ))
            except Exception as e:
                import sys
                print(f"[ContentPilot] Warning: Reddit fetch failed for r/{sub_name}: {e}", file=sys.stderr)
                continue
        return results

    def _fetch_hackernews(self, n: int) -> list[TopicResult]:
        resp = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5)
        ids = resp.json()[:n]
        results = []
        for story_id in ids:
            item_resp = httpx.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5
            )
            item = item_resp.json()
            if item and item.get("type") == "story":
                results.append(TopicResult(
                    title=item.get("title", ""),
                    summary=item.get("title", ""),
                    source="hackernews",
                    category="tech",
                    url=item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                ))
        return results
