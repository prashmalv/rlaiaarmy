from anthropic import Anthropic
from config.settings import settings
from data.rlai_brand import BRAND_CONTEXT
from datetime import datetime
import json

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

class BaseMarketingAgent:
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = settings.MODEL_NAME

    def _system_prompt(self) -> str:
        return f"""You are {self.name}, {self.role} at RightLeftAI.

GOAL: {self.goal}

BACKGROUND: {self.backstory}

BRAND KNOWLEDGE:
{BRAND_CONTEXT}

TODAY: {datetime.utcnow().strftime('%Y-%m-%d')}

Always produce content that:
- Positions RightLeftAI as the go-to AI expert in India
- Is specific, data-driven, and outcome-focused
- Matches the target audience's language and pain points
- Drives brand recall and authority — not just vanity metrics

When producing JSON, return ONLY valid JSON with no markdown."""

    def _call_llm(self, user_message: str, max_tokens: int = 4096) -> str:
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self._system_prompt(),
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

    def _parse_json(self, text: str) -> dict | list:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
