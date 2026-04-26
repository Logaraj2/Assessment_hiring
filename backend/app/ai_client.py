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
            wait_seconds = 10  # conservative default
            # Check standard headers
            retry_after = response.headers.get("retry-after", "")
            ratelimit_reset = response.headers.get("x-ratelimit-reset-requests", "") or response.headers.get("x-ratelimit-reset", "")

            if retry_after.isdigit():
                wait_seconds = int(retry_after)
            elif ratelimit_reset:
                # Could be seconds or a timestamp
                if ratelimit_reset.replace(".", "").isdigit():
                    wait_seconds = max(1, int(float(ratelimit_reset)))
            else:
                # Parse from error body
                try:
                    err_body = response.json()
                    err_msg = str(err_body.get("error", {}).get("message", ""))
                    # Match patterns like "try again in 58s", "wait 120 seconds", "10s"
                    match = re.search(r'(\d+)\s*s(?:ec(?:ond)?s?)?', err_msg, re.IGNORECASE)
                    if match:
                        wait_seconds = int(match.group(1))
                    # Match "try again in X.Xs"
                    match2 = re.search(r'(\d+\.?\d*)\s*s(?:ec)?', err_msg, re.IGNORECASE)
                    if match2:
                        wait_seconds = max(1, int(float(match2.group(1))))
                except Exception:
                    pass

            # Log headers for debugging
            print(f"[429] Rate limited. Headers: retry-after={retry_after}, "
                  f"x-ratelimit-reset-requests={response.headers.get('x-ratelimit-reset-requests', '')}, "
                  f"x-ratelimit-reset={response.headers.get('x-ratelimit-reset', '')}. "
                  f"Wait: {wait_seconds}s")
            try:
                print(f"[429] Body: {response.text[:500]}")
            except Exception:
                pass

            raise HTTPException(
                status_code=429,
                detail={
                    "message": f"Rate limit exceeded (free API tier). Please wait {wait_seconds} seconds.",
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
