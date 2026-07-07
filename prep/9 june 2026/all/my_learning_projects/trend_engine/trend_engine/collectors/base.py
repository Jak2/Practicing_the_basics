import datetime as dt
import functools
import logging
import re

logger = logging.getLogger(__name__)

USER_AGENT = "trend-engine/0.1 (learning project; contact via github)"


def normalize_key(title: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    lowered = title.lower()
    no_punct = re.sub(r"[^\w\s]", " ", lowered)
    collapsed = re.sub(r"\s+", " ", no_punct).strip()
    return collapsed


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def epoch_to_iso(epoch_seconds):
    """Convert a unix timestamp to UTC isoformat, or None if missing/invalid."""
    if epoch_seconds is None:
        return None
    try:
        return dt.datetime.fromtimestamp(float(epoch_seconds), tz=dt.timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def safe_collect(func):
    """Decorator: never let collect() raise. Log and return [] on error."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Collector %s failed", func.__module__)
            return []

    return wrapper
