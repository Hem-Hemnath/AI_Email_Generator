"""
config.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# AI Provider
# ----------------------------

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# ----------------------------
# OpenAI
# ----------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# ----------------------------
# Gemini
# ----------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ----------------------------
# Ollama
# ----------------------------

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ----------------------------
# HuggingFace
# ----------------------------

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv(
    "HF_MODEL",
    "mistralai/Mistral-7B-Instruct-v0.3",
)
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# ----------------------------
# Flask
# ----------------------------

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "secret")

MAX_INSTRUCTIONS_LENGTH = 500
OUTPUT_FOLDER = "outputs"
if AI_PROVIDER == "gemini" and not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing.\n"
        "Create a .env file and add it."
    )