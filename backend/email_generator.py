"""
email_generator.py
==================
Orchestrates prompt construction → AI call → result validation.
Returns a clean, structured email dictionary to the Flask route.
"""

import logging
from typing import Dict

from backend.prompt_builder import build_email_prompt
from backend.ai import call_ai

logger = logging.getLogger(__name__)

# Keys that must be present in the AI response
REQUIRED_EMAIL_KEYS = {"subject", "greeting", "body", "closing", "signature"}


def generate_email(form_data: Dict) -> Dict:
    """
    Generate a complete email from user-supplied form data.

    Steps:
        1.  Extract and sanitise form fields.
        2.  Build the AI prompt via prompt_builder.
        3.  Send the prompt to the configured AI provider.
        4.  Validate and return the structured response.

    Args:
        form_data: Validated request payload dict.

    Returns:
        Dict with keys: subject, greeting, body, closing, signature.

    Raises:
        ValueError: If the AI response is missing required fields.
        Exception: For AI provider or network errors (propagated as-is).
    """

    # 1. Extract fields
    subject               = form_data.get("subject", "").strip()
    purpose               = form_data.get("purpose", "").strip()
    recipient_name        = form_data.get("recipient_name", "").strip()
    sender_name           = form_data.get("sender_name", "").strip()
    email_type            = form_data.get("email_type", "Professional").strip()
    tone                  = form_data.get("tone", "Professional").strip()
    language              = form_data.get("language", "English").strip()
    additional_instructions = form_data.get("additional_instructions", "").strip()

    # 2. Build prompt
    prompt = build_email_prompt(
        subject=subject,
        purpose=purpose,
        recipient_name=recipient_name,
        sender_name=sender_name,
        email_type=email_type,
        tone=tone,
        language=language,
        additional_instructions=additional_instructions,
    )
    logger.debug("Prompt built (%d chars)", len(prompt))

    # 3. Call AI
    email_data = call_ai(prompt)

    # 4. Validate AI response structure
    missing = REQUIRED_EMAIL_KEYS - set(email_data.keys())
    if missing:
        raise ValueError(
            f"AI response is missing expected fields: {', '.join(sorted(missing))}"
        )

    logger.info("Email generated successfully for subject: '%s'", subject)
    return email_data
