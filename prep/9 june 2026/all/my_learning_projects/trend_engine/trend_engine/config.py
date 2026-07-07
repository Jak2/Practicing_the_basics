from pathlib import Path

from .env_loader import load_env

load_env()  # populates os.environ from .env at repo root, if present

DB_PATH = Path(__file__).resolve().parent.parent / "trends.db"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

SUBREDDITS = ["artificial", "OpenAI", "LocalLLaMA", "technology", "singularity", "india", "developersIndia"]

# SUBREDDITS = ["CryptoCurrency", "wallstreetbets", "finance", "india", "IndianStockMarket"]
# NICHE_AI_KEYWORDS = []  # or repurpose this list name for finance terms
# NICHE_FINANCE_KEYWORDS = ["crypto", "bitcoin", "stock", "nifty", "sensex", "ipo"]


YOUTUBE_REGIONS = ["US", "IN"]

# YouTube category IDs to keep (official IDs: 28=Science&Tech, 24=Entertainment,
# 10=Music, 17=Sports, 20=Gaming). Empty list = no filter, keep every category.
YOUTUBE_CATEGORY_IDS = ["28", "24"]

NICHE_AI_KEYWORDS = ["ai", "gpt", "llm", "openai", "anthropic", "claude", "gemini", "model", "agent", "robot", "neural", "chatbot", "deepmind", "nvidia"]
NICHE_INDIA_KEYWORDS = ["india", "indian", "delhi", "mumbai", "bengaluru", "bollywood", "rupee", "modi", "ipl", "desi"]

# Topics matching any of these (word-boundary match, case-insensitive) are dropped
# entirely before scoring — use this to hard-exclude noise (sports, celebrity gossip,
# obituaries) that the niche weights only de-prioritize but don't remove.
EXCLUDE_KEYWORDS = ["died", "obituary", "cricket", "football", "nba", "celebrity"]

# Turn individual collectors on/off without touching code. Keys match module names
# in trend_engine/collectors/ (hackernews, reddit, youtube, wikipedia).
SOURCE_ENABLED = {
    "hackernews": True,
    "reddit": True,
    "youtube": True,
    "wikipedia": True,
}

ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
