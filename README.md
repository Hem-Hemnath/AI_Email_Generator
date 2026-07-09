# ✉️ AI Email Writer

> Generate professional, polished emails in seconds using AI — built with Python, Flask, and Vanilla JavaScript.

![AI Email Writer Preview](https://img.shields.io/badge/Status-Production%20Ready-22c55e?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## 📖 Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Project Architecture](#project-architecture)  
4. [Folder Structure](#folder-structure)  
5. [Installation](#installation)  
6. [Configuration](#configuration)  
7. [Running the App](#running-the-app)  
8. [API Documentation](#api-documentation)  
9. [Switching AI Providers](#switching-ai-providers)  
10. [Deployment Guide](#deployment-guide)  

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Multi-Provider AI** | Switch between OpenAI, Gemini, Ollama, and Hugging Face |
| 📧 **16 Email Types** | Professional, Job Application, Marketing, and more |
| 🎨 **9 Tone Options** | From Formal to Enthusiastic |
| 🌍 **13 Languages** | English, Spanish, French, Japanese, and more |
| 📋 **Copy to Clipboard** | One-click copy of the full email |
| 💾 **Download as TXT** | Save email as a plain-text file |
| 🌙 **Dark / Light Mode** | Persisted across sessions |
| 📱 **Fully Responsive** | Works on mobile, tablet, and desktop |
| ✅ **Input Validation** | Client-side and server-side validation |
| ⚡ **Loading Animations** | Real-time feedback during generation |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| Backend | Python 3.10+, Flask 3.0 |
| AI Layer | OpenAI / Gemini / Ollama / Hugging Face |
| Styling | Custom CSS with glassmorphism + CSS variables |

---

## 🏗 Project Architecture

```
User Browser
     │
     ▼  HTTP / JSON
Flask Backend (app.py)
     │
     ├── validator.py      ◄─ Validate all inputs
     ├── prompt_builder.py ◄─ Construct the AI prompt
     ├── ai.py             ◄─ Send prompt to AI provider
     └── email_generator.py◄─ Orchestrate pipeline
          │
          ▼
   AI Provider (OpenAI / Gemini / Ollama / HF)
          │
          ▼
   Structured JSON email → Frontend
```

---

## 📁 Folder Structure

```
AI-Email-Writer/
│
├── app.py                 # Flask app — routes & error handlers
├── config.py              # All configuration (AI provider, keys, etc.)
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── backend/
│   ├── __init__.py        # Makes backend a Python package
│   ├── ai.py              # AI provider abstraction layer
│   ├── prompt_builder.py  # Prompt construction
│   ├── email_generator.py # Generation pipeline orchestrator
│   └── validator.py       # Input validation logic
│
├── templates/
│   └── index.html         # Single-page application HTML
│
├── static/
│   ├── css/
│   │   └── style.css      # All styles (dark mode, glassmorphism)
│   └── js/
│       └── app.js         # Frontend logic (state, API calls, UI)
│
└── outputs/               # Auto-created — saved email TXT files
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- An API key for your chosen AI provider

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/your-username/ai-email-writer.git
cd ai-email-writer
```

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Open `config.py` and edit the following:

```python
# Choose your AI provider
AI_PROVIDER = "gemini"   # Options: "openai" | "gemini" | "ollama" | "huggingface"

# Set your API key for the chosen provider
GEMINI_API_KEY = "your-api-key-here"
```

> **Tip:** Use environment variables instead of hardcoding keys:
> ```bash
> set GEMINI_API_KEY=your_key_here       # Windows CMD
> $env:GEMINI_API_KEY="your_key_here"   # Windows PowerShell
> export GEMINI_API_KEY=your_key_here   # macOS/Linux
> ```

---

## ▶️ Running the App

```bash
python app.py
```

Open your browser and go to **http://localhost:5000**

---

## 📡 API Documentation

### `GET /health`

Returns application health and active AI provider.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-01T12:00:00Z",
  "ai_provider": "gemini",
  "version": "1.0.0"
}
```

---

### `POST /generate-email`

Generates a complete email from user inputs.

**Request body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `subject` | string | ✅ | Email subject line |
| `purpose` | string | ✅ | What the email should accomplish |
| `recipient_name` | string | ✅ | Name of the email recipient |
| `sender_name` | string | ✅ | Your name |
| `email_type` | string | ✅ | One of the 16 email types |
| `tone` | string | ✅ | One of the 9 tone options |
| `language` | string | ✅ | Language for the email |
| `additional_instructions` | string | ❌ | Extra guidance for the AI |

**Response (success):**
```json
{
  "success": true,
  "email": {
    "subject": "...",
    "greeting": "...",
    "body": "...",
    "closing": "...",
    "signature": "..."
  }
}
```

**Response (error):**
```json
{
  "success": false,
  "error": "Field 'subject' is required and cannot be empty."
}
```

---

### `POST /clear`

Acknowledges a clear event (stateless — actual clearing is client-side).

---

### `POST /save-email`

Saves the generated email as a `.txt` file in the `outputs/` directory.

**Request body:**
```json
{ "filename": "my_email", "content": "Subject: ...\n\nDear ..." }
```

---

## 🔄 Switching AI Providers

Edit `config.py`:

| Provider | `AI_PROVIDER` value | Key Setting |
|---|---|---|
| Google Gemini | `"gemini"` | `GEMINI_API_KEY` |
| OpenAI | `"openai"` | `OPENAI_API_KEY` |
| Ollama (local) | `"ollama"` | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |
| Hugging Face | `"huggingface"` | `HF_API_KEY`, `HF_MODEL` |

**No other file needs to change.** All provider logic is encapsulated in `backend/ai.py`.

---

## 🌐 Deployment Guide

### Option 1: Waitress (Windows — production)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Option 2: Gunicorn (Linux/macOS — production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Render / Railway / Fly.io

1. Push your project to GitHub
2. Create a new Web Service on your chosen platform
3. Set the start command: `gunicorn app:app`
4. Add environment variables for your API keys
5. Deploy!

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

Built as a portfolio project demonstrating:
- AI API integration and prompt engineering
- RESTful API design with Flask
- Modern frontend development with Vanilla JS
- Clean, modular Python architecture
