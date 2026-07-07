"""LLM enricher: clusters same-story topics and annotates them with analyst metadata.

Consumes ranked topic dicts from score.rank_topics and produces annotated,
deduplicated topics via a Claude call. Falls back to a degraded (math-only)
mode if the LLM call fails after one retry.
"""
import json
import logging

from trend_engine import config

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"AI", "tech", "India", "meme", "other"}
VALID_PLATFORM_FIT = {"short-video", "thread", "long-form"}
VALID_STAGES = {"early-signal", "rising", "peaking"}

PROMPT_TEMPLATE = """You are a sharp trend analyst. Given a list of trending topic candidates, \
cluster topics that refer to the same underlying story/event, and annotate each resulting cluster.

For each cluster, output:
- canonical_key: the topic_key of the best/highest-signal representative in the cluster. \
This MUST be exactly one of the input topic_keys.
- merged_keys: list of the OTHER topic_keys (if any) merged into this cluster (excludes canonical_key itself).
- explanation: one sharp, analyst-voice sentence on why this is going viral.
- category: one of "AI", "tech", "India", "meme", "other".
- platform_fit: one of "short-video", "thread", "long-form" — the best format for this story.
- stage: one of "early-signal", "rising", "peaking".

Return ONLY JSON, no prose, no markdown fences, matching this schema exactly:
{{"topics": [{{"canonical_key": "...", "merged_keys": ["..."], "explanation": "...", \
"category": "...", "platform_fit": "...", "stage": "..."}}]}}

Candidates:
{candidates}
"""

MAX_TOPICS = 100
REQUIRED_KEYS = {"canonical_key", "merged_keys", "explanation", "category", "platform_fit", "stage"}


def _call_llm(payload: str) -> str:
    """Call the Anthropic API. Isolated as a module-level function for mocking.

    Instantiates the client lazily so importing this module never requires
    ANTHROPIC_API_KEY to be set.
    """
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": payload}],
    )
    return next((b.text for b in response.content if b.type == "text"), "")


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def _parse(response_text: str, candidates: list[dict]) -> list[dict]:
    """Validate JSON, merge clusters onto candidates, pass through unmentioned ones."""
    text = _strip_fences(response_text)
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"LLM response is not valid JSON: {e}") from e

    if not isinstance(data, dict) or "topics" not in data:
        raise ValueError("LLM response missing top-level 'topics' key")

    topics = data["topics"]
    if not isinstance(topics, list):
        raise ValueError("'topics' must be a list")

    by_key = {c["topic_key"]: c for c in candidates}
    valid_keys = set(by_key.keys())

    consumed_keys: set[str] = set()
    result: list[dict] = []

    for cluster in topics:
        if not isinstance(cluster, dict):
            raise ValueError("each cluster must be an object")
        missing = REQUIRED_KEYS - set(cluster.keys())
        if missing:
            raise ValueError(f"cluster missing required keys: {missing}")

        canonical_key = cluster["canonical_key"]
        if canonical_key not in valid_keys:
            raise ValueError(f"unknown canonical_key: {canonical_key!r}")

        merged_keys = cluster["merged_keys"]
        if not isinstance(merged_keys, list):
            raise ValueError("merged_keys must be a list")

        # Dedupe merged_keys (preserve first occurrence), drop non-strings and self-references.
        seen: set[str] = set()
        deduped_merged_keys: list[str] = []
        for mk in merged_keys:
            if not isinstance(mk, str):
                continue
            if mk == canonical_key:
                continue
            if mk in seen:
                continue
            seen.add(mk)
            deduped_merged_keys.append(mk)

        # Cross-cluster key reuse guard: skip this cluster entirely if any of its
        # keys were already consumed by an earlier cluster in this parse.
        cluster_keys = [canonical_key] + deduped_merged_keys
        already_consumed = [k for k in cluster_keys if k in consumed_keys]
        if already_consumed:
            logger.warning(
                "skipping cluster with canonical_key=%r: keys already consumed by an earlier cluster: %s",
                canonical_key, already_consumed,
            )
            continue

        base = dict(by_key[canonical_key])
        total_score = base.get("score", 0)
        for mk in deduped_merged_keys:
            if mk in valid_keys:
                total_score += by_key[mk].get("score", 0)
                consumed_keys.add(mk)

        base["score"] = total_score
        base["explanation"] = str(cluster["explanation"])[:300]

        category = cluster["category"]
        base["category"] = category if category in VALID_CATEGORIES else "other"

        platform_fit = cluster["platform_fit"]
        base["platform_fit"] = platform_fit if platform_fit in VALID_PLATFORM_FIT else "short-video"

        stage = cluster["stage"]
        base["stage"] = stage if stage in VALID_STAGES else "rising"

        consumed_keys.add(canonical_key)
        result.append(base)

    # Pass through candidates the LLM didn't mention, with degraded-default annotations.
    for c in candidates:
        if c["topic_key"] not in consumed_keys:
            passthrough = dict(c)
            passthrough["explanation"] = ""
            passthrough["category"] = "unclassified"
            passthrough["platform_fit"] = ""
            passthrough["stage"] = ""
            result.append(passthrough)

    result.sort(key=lambda t: t.get("score", 0), reverse=True)
    return result[:MAX_TOPICS]


def _degrade(candidates: list[dict]) -> list[dict]:
    out = []
    for c in candidates[:MAX_TOPICS]:
        item = dict(c)
        item["explanation"] = ""
        item["category"] = "unclassified"
        item["platform_fit"] = ""
        item["stage"] = ""
        out.append(item)
    return out


def enrich(candidates: list[dict]) -> tuple[list[dict], bool]:
    """Enrich ranked topics via LLM clustering/annotation.

    Returns (topics, enriched_flag). On LLM failure after one retry, returns
    degraded (math-only) output with enriched_flag=False.
    """
    slim_candidates = [
        {
            "topic_key": c["topic_key"],
            "title": c.get("title"),
            "score": round(c.get("score", 0), 2),
            "sources": c.get("sources"),
        }
        for c in candidates
    ]
    payload = PROMPT_TEMPLATE.format(candidates=json.dumps(slim_candidates))

    for attempt in range(2):
        try:
            response_text = _call_llm(payload)
            parsed = _parse(response_text, candidates)
            return parsed, True
        except Exception as e:
            logger.warning("enrich attempt %d failed: %s", attempt + 1, e)

    return _degrade(candidates), False
