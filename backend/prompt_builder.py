"""
prompt_builder.py
=================
Constructs a structured AI prompt from the user's email request data.
The prompt instructs the AI to return a JSON object with the email parts.
"""

from typing import Optional


def build_email_prompt(
    subject: str,
    purpose: str,
    recipient_name: str,
    sender_name: str,
    email_type: str,
    tone: str,
    language: str,
    additional_instructions: Optional[str] = "",
) -> str:
    """
    Build the prompt string that will be sent to the AI model.

    Args:
        subject: Email subject/topic.
        purpose: The core purpose or description of the email.
        recipient_name: Name of the person being emailed.
        sender_name: Name of the person sending the email.
        email_type: Category of email (e.g., Professional, Job Application).
        tone: Desired tone (e.g., Formal, Friendly).
        language: Language to write the email in.
        additional_instructions: Any extra guidance from the user.

    Returns:
        A fully formatted prompt string ready to send to an LLM.
    """

    extra = (
        f"\nAdditional instructions from the user: {additional_instructions}"
        if additional_instructions
        else ""
    )

    prompt = f"""
You are an expert professional email writer. Your task is to generate a complete, 
high-quality email based on the specifications below.

=== EMAIL SPECIFICATIONS ===
Email Type          : {email_type}
Subject/Topic       : {subject}
Purpose/Description : {purpose}
Recipient Name      : {recipient_name}
Sender Name         : {sender_name}
Tone                : {tone}
Language            : {language}{extra}

=== OUTPUT FORMAT ===
Respond ONLY with a valid JSON object in exactly this structure (no additional text, markdown, or code fences):

{{
  "subject": "<the email subject line>",
  "greeting": "<the opening greeting line>",
  "body": "<the main email body paragraphs, use \\n\\n between paragraphs>",
  "closing": "<the closing phrase>",
  "signature": "<sender name and any relevant sign-off details>"
}}

=== GUIDELINES ===
- The tone must be {tone}. Adjust vocabulary and sentence structure accordingly.
- The email must be in {language}.
- Ensure the email is complete, professional, and appropriate for a {email_type} email.
- Use natural, human-sounding language — avoid robotic or template-sounding text.
- The body should be substantive (at least 2–3 meaningful paragraphs).
- Do NOT include any explanations, notes, or text outside the JSON object.
"""
    return prompt.strip()
