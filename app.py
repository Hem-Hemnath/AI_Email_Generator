"""
app.py
======
Main entry point for the AI Email Writer Flask application.
Registers all REST API routes and serves the single-page frontend.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

import config
from backend.email_generator import generate_email
from backend.validator import validate_email_request

# ─────────────────────────────────────────────
# Logging configuration
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Flask app init
# ─────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = config.SECRET_KEY
CORS(app)  # Allow cross-origin requests (useful during development)

# Ensure output directory exists
Path(config.OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main single-page application."""
    return render_template("index.html")


# ── GET /health ───────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    Returns application status and current AI provider configuration.
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ai_provider": config.AI_PROVIDER,
        "version": "1.0.0",
    }), 200


# ── POST /generate-email ──────────────────────
@app.route("/generate-email", methods=["POST"])
def generate_email_route():
    """
    Generate an AI-written email from the provided form data.

    Expected JSON body:
        {
            "subject":                  "string (required)",
            "purpose":                  "string (required)",
            "recipient_name":           "string (required)",
            "sender_name":              "string (required)",
            "email_type":               "string (required)",
            "tone":                     "string (required)",
            "language":                 "string (required)",
            "additional_instructions":  "string (optional)"
        }

    Returns:
        200 { success: true, email: { subject, greeting, body, closing, signature } }
        400 { success: false, error: "validation message" }
        500 { success: false, error: "server/AI error message" }
    """
    # Parse request body
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON."}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or empty JSON body."}), 400

    # Validate inputs
    is_valid, error_msg = validate_email_request(data)
    if not is_valid:
        logger.warning("Validation failed: %s", error_msg)
        return jsonify({"success": False, "error": error_msg}), 400

    # Generate email
    try:
        email_data = generate_email(data)
        return jsonify({"success": True, "email": email_data}), 200

    except ValueError as exc:
        logger.error("Value error during generation: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 422

    except (ConnectionError, TimeoutError) as exc:
        logger.error("Connection/timeout error: %s", exc)
        return jsonify({
            "success": False,
            "error": "Could not reach the AI provider. Please check your network or provider settings.",
        }), 503

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error during email generation")
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred: {str(exc)}",
        }), 500


# ── POST /clear ───────────────────────────────
@app.route("/clear", methods=["POST"])
def clear():
    """
    Endpoint to acknowledge a form-clear event from the frontend.
    Stateless — the actual clearing is done client-side.
    """
    return jsonify({"success": True, "message": "Session cleared."}), 200


# ── POST /save-email ──────────────────────────
@app.route("/save-email", methods=["POST"])
def save_email():
    """
    Save a generated email as a plain-text file in the outputs/ directory.

    Expected JSON body:
        { "filename": "my_email.txt", "content": "<full email text>" }

    Returns:
        200 { success: true, filename: "...", path: "..." }
        400 { success: false, error: "..." }
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON."}), 400

    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "").strip()
    content  = data.get("content", "").strip()

    if not filename or not content:
        return jsonify({"success": False, "error": "filename and content are required."}), 400

    # Sanitise filename — allow only safe characters
    safe_name = "".join(c for c in filename if c.isalnum() or c in ("_", "-", "."))
    if not safe_name.endswith(".txt"):
        safe_name += ".txt"

    file_path = Path(config.OUTPUT_FOLDER) / safe_name
    try:
        file_path.write_text(content, encoding="utf-8")
        logger.info("Email saved to: %s", file_path)
        return jsonify({
            "success": True,
            "filename": safe_name,
            "path": str(file_path),
        }), 200
    except OSError as exc:
        logger.error("Failed to save email: %s", exc)
        return jsonify({"success": False, "error": "Failed to write file."}), 500


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed."}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "error": "Internal server error."}), 500


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting AI Email Writer — provider: %s", config.AI_PROVIDER)
    logger.info("Open http://localhost:%d in your browser", config.PORT)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
