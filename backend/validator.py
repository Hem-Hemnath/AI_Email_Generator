"""
validator.py
============
Input validation utilities for the AI Email Writer backend.
All validation logic is centralised here to keep other modules clean.
"""

from typing import Tuple, Dict, Any

# ─────────────────────────────────────────────
# Allowed values for select fields
# ─────────────────────────────────────────────
VALID_EMAIL_TYPES = {
    "Professional", "Business", "Formal", "Informal", "Friendly",
    "Job Application", "Internship Request", "Leave Request",
    "Complaint", "Apology", "Thank You", "Meeting Request",
    "Follow-up", "Customer Support", "Sales", "Marketing",
}

VALID_TONES = {
    "Professional", "Friendly", "Formal", "Casual", "Confident",
    "Persuasive", "Polite", "Apologetic", "Enthusiastic",
}

VALID_LANGUAGES = {
    "English", "Spanish", "French", "German", "Italian",
    "Portuguese", "Dutch", "Russian", "Japanese", "Chinese",
    "Arabic", "Hindi", "Korean",
}

MAX_LEN = {
    "subject": 200,
    "purpose": 1000,
    "recipient_name": 100,
    "sender_name": 100,
    "additional_instructions": 500,
}


def validate_email_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate the incoming email generation request payload.

    Args:
        data: Dictionary parsed from the incoming JSON request.

    Returns:
        (True, "") on success, or (False, "error message") on failure.
    """

    # --- Required fields presence check ---
    required_fields = ["subject", "purpose", "recipient_name", "sender_name",
                       "email_type", "tone", "language"]

    for field in required_fields:
        value = data.get(field, "").strip()
        if not value:
            return False, f"Field '{field}' is required and cannot be empty."

    # --- Length checks ---
    for field, max_len in MAX_LEN.items():
        raw = data.get(field, "")
        if raw and len(raw) > max_len:
            return False, (
                f"Field '{field}' exceeds the maximum allowed length of {max_len} characters."
            )

    # --- Allowed-value checks ---
    email_type = data.get("email_type", "").strip()
    if email_type not in VALID_EMAIL_TYPES:
        return False, f"Invalid email_type: '{email_type}'."

    tone = data.get("tone", "").strip()
    if tone not in VALID_TONES:
        return False, f"Invalid tone: '{tone}'."

    language = data.get("language", "").strip()
    if language not in VALID_LANGUAGES:
        return False, f"Invalid language: '{language}'."

    return True, ""
