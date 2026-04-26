import httpx
import json
import re

from app.config import settings


def call_ai(messages: list, system: str = None, max_tokens: int = 2000) -> str:
    """Call OpenRouter API and return the response text."""
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://skill-assessment-agent.app",
        "X-Title": "Skill Assessment Agent"
    }

    formatted_messages = []
    if system:
        formatted_messages.append({"role": "system", "content": system})
    formatted_messages.extend(messages)

    payload = {
        "model": settings.ai_model,
        "max_tokens": max_tokens,
        "messages": formatted_messages
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(settings.openrouter_base_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def extract_json_object(text: str) -> dict | None:
    """Extract first JSON object from AI response text."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def extract_json_array(text: str) -> list | None:
    """Extract first JSON array from AI response text."""
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None
