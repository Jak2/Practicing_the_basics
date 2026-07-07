import os
import re
from typing import Literal
from datetime import date
from langchain_core.messages import HumanMessage
from core.config import Config
from core.models import TopicResult


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


PROMPT_TEMPLATE = """You are a creative AI content strategist.

Topic: {title}
Context: {summary}
Today: {date}

Generate a markdown file for an AI prompt post. Use this EXACT format:

---
title: "a concise, compelling title"
description: "one-sentence description"
image: ""
tags: ["tag1", "tag2", "tag3"]
created_at: "{date}"
---

Write an expert AI prompt here (150-300 words). The prompt should be directly usable in ChatGPT, Claude, or Gemini. Make it outcome-driven and specific to the topic.

Return ONLY the markdown — no commentary before or after."""


WORKFLOW_TEMPLATE = """You are a creative AI content strategist.

Topic: {title}
Context: {summary}
Today: {date}

Generate a markdown file for a multi-step AI workflow post. Use this EXACT format:

---
title: "a concise workflow title"
description: "one-sentence description"
tags: ["tag1", "tag2", "tag3"]
created_at: "{date}"
---

## Step 1: [Step Name]
[Detailed AI prompt for this step, 50-100 words]

## Step 2: [Step Name]
[Detailed AI prompt for this step]

## Step 3: [Step Name]
[Detailed AI prompt for this step]

## Step 4: [Step Name]
[Detailed AI prompt for this step]

Return ONLY the markdown — no commentary before or after. Use exactly ## for step headings."""


class ContentGenerator:
    def __init__(self, config: Config):
        if config.llm.provider == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=config.llm.model, temperature=0.7)
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=config.llm.model,
                google_api_key=os.getenv("GEMINI_API_KEY", ""),
            )

    def run(self, topic: TopicResult, post_type: Literal["prompt", "workflow"]) -> tuple[str, str]:
        today = date.today().isoformat()
        if post_type == "prompt":
            prompt = PROMPT_TEMPLATE.format(title=topic.title, summary=topic.summary, date=today)
        else:
            prompt = WORKFLOW_TEMPLATE.format(title=topic.title, summary=topic.summary, date=today)

        response = self.llm.invoke([HumanMessage(content=prompt)])
        markdown = response.content.strip()

        title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', markdown)
        if title_match:
            slug = _slugify(title_match.group(1))
        else:
            slug = _slugify(topic.title)

        return slug, markdown
