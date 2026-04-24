from anthropic import Anthropic
from config.settings import settings
from typing import Optional
import json

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _parse_json_robust(text: str):
    """Strip markdown fences, try multiple extraction strategies."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for start_ch, end_ch in [('{', '}'), ('[', ']')]:
        s = text.find(start_ch)
        e = text.rfind(end_ch)
        if s != -1 and e > s:
            try:
                return json.loads(text[s:e + 1])
            except json.JSONDecodeError:
                pass
    raise json.JSONDecodeError("Cannot parse JSON", text, 0)


class BaseAgent:
    """Base class for all AI Dev Team agents."""

    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = settings.MODEL_NAME

    def _call_llm(self, system_prompt: str, user_message: str, max_tokens: int = 8096) -> str:
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

    def _system_prompt(self) -> str:
        return f"""You are {self.name}, a {self.role} in an AI-powered software development team.

Goal: {self.goal}

Background: {self.backstory}

Always respond with structured, actionable output. When asked for JSON, return valid JSON only.
Be concise, precise, and professional."""

    def log_action(self, action: str, input_data: str, output_data: str) -> dict:
        return {
            "agent": self.name,
            "role": self.role,
            "action": action,
            "input": input_data[:500] if len(input_data) > 500 else input_data,
            "output_summary": output_data[:1000] if len(output_data) > 1000 else output_data,
        }
