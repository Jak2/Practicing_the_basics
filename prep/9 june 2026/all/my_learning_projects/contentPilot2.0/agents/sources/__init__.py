from agents.sources.civitai import CivitaiSource
from agents.sources.promptschat import PromptsChatSource
from agents.sources.reddit_trends import RedditTrendsSource

SOURCES = {
    "civitai": CivitaiSource,
    "promptschat": PromptsChatSource,
    "reddit": RedditTrendsSource,
}
