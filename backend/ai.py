"""
ai.py
=====
AI provider abstraction layer.
Supports OpenAI, Gemini, Ollama, and Hugging Face.
Switch providers via config.py — no other file needs to change.
"""

import json
import logging
from typing import Dict

import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Helper: parse JSON from model response
# ─────────────────────────────────────────────
def _parse_json_response(raw_text: str) -> Dict:
    """
    Attempt to extract and parse a JSON object from the AI's raw response.
    Handles cases where the model wraps JSON in markdown code fences.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        text = "\n".join(lines[1:-1]).strip()

    # Some models wrap with a single backtick block
    text = text.strip("`").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI JSON response: %s\nRaw text: %s", exc, raw_text)
        raise ValueError(
            "The AI returned an unexpected format. Please try again."
        ) from exc


# ─────────────────────────────────────────────
# OpenAI
# ─────────────────────────────────────────────
def _call_openai(prompt: str) -> Dict:
    """Send prompt to OpenAI and return parsed JSON email parts."""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "openai package not installed. Run: pip install openai"
        ) from exc

    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in config.py or environment variables.")

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.OPENAI_MAX_TOKENS,
        temperature=config.OPENAI_TEMPERATURE,
    )
    raw_text = response.choices[0].message.content
    return _parse_json_response(raw_text)


# ─────────────────────────────────────────────
# Google Gemini
# ─────────────────────────────────────────────
def _call_gemini(prompt: str) -> Dict:
    """
    Google Gemini using the new google-genai SDK.
    """

    try:
        from google import genai
    except ImportError:
        raise ImportError(
            "google-genai is not installed.\n"
            "Run:\n\npip install google-genai"
        )

    if not config.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found."
        )

    client = genai.Client(
        api_key=config.GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )

    raw_text = response.text

    return _parse_json_response(raw_text)


# ─────────────────────────────────────────────
# Ollama (local)
# ─────────────────────────────────────────────
def _call_ollama(prompt: str) -> Dict:
    """Send prompt to a locally running Ollama instance."""
    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "requests package not installed. Run: pip install requests"
        ) from exc

    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            f"Cannot connect to Ollama at {config.OLLAMA_BASE_URL}. "
            "Make sure Ollama is running locally."
        ) from exc

    raw_text = resp.json().get("response", "")
    return _parse_json_response(raw_text)


# ─────────────────────────────────────────────
# Hugging Face Inference API
# ─────────────────────────────────────────────
def _call_huggingface(prompt: str) -> Dict:
    """Send prompt to Hugging Face Inference API and return parsed JSON."""
    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "requests package not installed. Run: pip install requests"
        ) from exc

    if not config.HF_API_KEY:
        raise ValueError("HF_API_KEY is not set in config.py or environment variables.")

    headers = {"Authorization": f"Bearer {config.HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024, "temperature": 0.7},
    }
    resp = requests.post(config.HF_API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()

    result = resp.json()
    # HF returns a list of generated text objects
    if isinstance(result, list):
        raw_text = result[0].get("generated_text", "")
    else:
        raw_text = result.get("generated_text", "")

    # Strip echoed prompt if the model echoes the input
    if prompt in raw_text:
        raw_text = raw_text.replace(prompt, "").strip()

    return _parse_json_response(raw_text)


# ─────────────────────────────────────────────
# Public dispatch function
# ─────────────────────────────────────────────
def call_ai(prompt: str) -> Dict:
    """
    Dispatch the prompt to the currently configured AI provider.

    Args:
        prompt: The prompt string to send to the model.

    Returns:
        A dict with keys: subject, greeting, body, closing, signature.

    Raises:
        ValueError: For configuration or parse errors.
        ConnectionError: When the provider cannot be reached (Ollama).
        Exception: For any other provider-level errors.
    """
    provider = config.AI_PROVIDER.lower()
    logger.info("Calling AI provider: %s", provider)

    if provider == "openai":
        return _call_openai(prompt)
    elif provider == "gemini":
        return _call_gemini(prompt)
    elif provider == "ollama":
        return _call_ollama(prompt)
    elif provider == "huggingface":
        return _call_huggingface(prompt)
    else:
        raise ValueError(
            f"Unknown AI_PROVIDER '{provider}'. "
            "Choose from: openai, gemini, ollama, huggingface"
        )
