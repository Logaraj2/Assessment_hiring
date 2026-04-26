import httpx
import json
import re

from fastapi import HTTPException
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
    for msg in messages:
        formatted_messages.append(dict(msg))

    # Prepend system prompt to the first user message since some models
    # (e.g. Gemma) don't support the system role
    if system and formatted_messages:
        for msg in formatted_messages:
            if msg["role"] == "user":
                msg["content"] = f"[Instructions: {system}]\n\n{msg['content']}"
                break

    payload = {
        "model": settings.ai_model,
        "max_tokens": max_tokens,
        "messages": formatted_messages
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(settings.openrouter_base_url, headers=headers, json=payload)

        if response.status_code == 429:
            # Parse retry-after from header or response body
            retry_after = response.headers.get("retry-after", "")
            wait_seconds = 60  # default
            if retry_after.isdigit():
                wait_seconds = int(retry_after)
            else:
                # Try to parse from response body
                try:
                    err_body = response.json()
                    err_msg = err_body.get("error", {}).get("message", "")
                    # Look for patterns like "try again in 58s" or "60 seconds"
                    match = re.search(r'(\d+)\s*s(?:ec|econds?)?', err_msg, re.IGNORECASE)
                    if match:
                        wait_seconds = int(match.group(1))
                except Exception:
                    pass

            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded. Free API tier has request limits.",
                    "retry_after_seconds": wait_seconds
                }
            )

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
