import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from core.trend_models import TrendItem, TrendInsight

_PROMPT_TEMPLATE = """You analyze viral AI prompts. Given the prompt below, return ONLY a JSON object
(no markdown, no commentary) with exactly these keys:
- "pattern_tags": 2-5 short strings naming the prompting techniques used
  (e.g. "role assignment", "negative prompt", "lens spec", "step-by-step constraint")
- "why_viral": exactly two sentences explaining why this prompt design works
- "category": one short label (e.g. "portrait", "coding-assistant", "productivity")

PROMPT TO ANALYZE:
{prompt}
"""


class InsightExtractor:
    """LLM-powered analysis of why a viral prompt works. Failure returns None —
    a trend without insight is still worth showing ("analysis pending")."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=0.2)

    def extract(self, item: TrendItem) -> TrendInsight | None:
        try:
            reply = self.llm.invoke(_PROMPT_TEMPLATE.format(prompt=item.prompt[:2000]))
            text = reply.content.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return TrendInsight.model_validate_json(text)
        except Exception as e:
            print(f"[ContentPilot2] insight failed for {item.id}: {e}", file=sys.stderr)
            return None
