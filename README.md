# AI Coding Chatbot

## GitHub Actions

[![ai-chatbot-release](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/ai-chatbot-release.yml/badge.svg?branch=AI-Chatbot)](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/ai-chatbot-release.yml)
[![ai-review](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/ai-review.yml/badge.svg?branch=AI-Chatbot)](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/ai-review.yml)
[![codeql](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/codeql.yml/badge.svg?branch=AI-Chatbot)](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/codeql.yml)
[![readme-generator](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/readme-generator.yml/badge.svg?branch=AI-Chatbot)](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/readme-generator.yml)

## Features

- Generate and explain code
- Debug programming errors
- Refactor and optimize code
- Review code and suggest improvements
- Convert code between programming languages
- Answer general programming questions
- Work with Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP, Ruby, Kotlin, Swift, Dart, SQL, HTML, CSS, Bash, PowerShell, and other common languages
- Switch Gemini models while the chatbot is running
- Configurable output-token limit to reduce unnecessary API usage
- No automatic retry after a Gemini quota or rate-limit error
- Persistent conversation sessions during the run
- View conversation history and clear conversation state
- Save conversations to local JSON files
- Load saved conversations and restore their Gemini chat context
- List saved conversations with `/saves`
- Saved conversation data is excluded from Git
- Responsive Flask web interface with chat bubbles, syntax-highlighted code, and confirmed new-chat/load controls (v2.1)

## Current Default Model

The default model is:

`gemini-3.5-flash-lite`

The model can be changed with the `GEMINI_MODEL` environment variable or interactively with `/model`.

## Requirements

- Python 3.10 or newer
- A Gemini API key
- Internet access
- The dependencies listed in `requirements.txt`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Error-cracker-1/My-First-Project.git
cd My-First-Project
git checkout AI-Chatbot
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder value:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional settings:

```text
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_MAX_OUTPUT_TOKENS=2048
```

**Never commit your real `.env` file or API key to GitHub.** The repository's `.gitignore` excludes `.env`.

## Run the Chatbot

Command-line interface:

```bash
python app.py
```

Web interface:

```bash
python web_app.py
```

You will see a prompt similar to:

```text
You:
```

Enter a programming question or task and press Enter.

## Commands

| Command | Purpose |
|---|---|
| `/model` | Open the interactive model selector |
| `/models` | Open the interactive model selector |
| `/history` | View the conversation history |
| `/clear` | Clear conversation history and start a new conversation |
| `/save NAME` | Save the current conversation as NAME |
| `/load NAME` | Load a saved conversation and restore its model/context |
| `/saves` | List saved conversations |
| `/exit` | Exit the chatbot |

## Save and Load Conversations

Conversations are stored locally as JSON under `.chatbot_data/conversations/` by default. Set `CHATBOT_STORAGE_DIR` to choose another local directory. The storage directory is ignored by Git.

Each saved conversation includes its model ID, ordered user/assistant message pairs, a UTC timestamp, and a format version. Loading restores the saved Gemini chat context directly, rather than replaying old messages as new API requests.

Missing, corrupted, unsupported, or invalid saves are handled without terminating the chatbot.

Run `python -m unittest -v test_conversation_store.py` to test persistence behavior.

## Quota and Rate-Limit Handling

The chatbot does not automatically retry requests when Gemini reports a quota or rate-limit error. This prevents an error from immediately causing additional API requests.

If you repeatedly receive `429`, `RESOURCE_EXHAUSTED`, or quota-related errors, check the Gemini API project quota and usage in Google AI Studio. Limits can vary by model and usage tier.

Reducing `GEMINI_MAX_OUTPUT_TOKENS` can limit the maximum amount of generated output per request, although it does not remove request-rate or daily-request limits.

## Project Files

| File | Description |
|---|---|
| `app.py` | Main command-line chatbot |
| `web_app.py` | Flask web interface |
| `config.py` | Configuration management and environment validation |
| `conversation_store.py` | Conversation persistence layer |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment-variable template |
| `.gitignore` | Prevents local environment files and Python cache files from being committed |
| `scripts/html_dashboard.py` | Static HTML dashboard generation script for the Daily AI Review project |
| `test_conversation_store.py` | Tests for the conversation persistence layer |

## Security

- Keep API keys in `.env`.
- Do not paste API keys into source code.
- Do not commit `.env`.
- If an API key is accidentally exposed, revoke or rotate it promptly.

## Development Workflow

This project is developed on the `AI-Chatbot` branch.

Changes are intended to follow this workflow:

1. Make a focused change.
2. Test the change.
3. Commit the change.
4. Push the branch.
5. Continue with the next improvement.

Version tags are used for tagged releases on the `AI-Chatbot` branch.

## License

No license has been specified for this project yet.

## Web Interface (v2.1)

v2.0 introduced a local browser interface while v2.1 improves the responsive layout, chat bubbles, code-block readability and copy controls, suggested prompts, and confirmation for new-chat/loading saved conversations. The existing command-line chatbot remains available.

### Start the web interface

Install the dependencies, configure `GEMINI_API_KEY`, then run:

```bash
python web_app.py
```

Open **http://127.0.0.1:5000** in your browser.

The Gemini API key remains server-side in the environment; it is not sent to the browser.

### Web features

- Send coding and general programming questions from the browser.
- Switch between the configured Gemini models.
- Keep browser conversation history during the session.
- Start a new conversation with **New chat**.
- Save and load conversations using the existing local JSON storage.
- Responsive layout for desktop and mobile browsers.
- Distinct user and assistant chat bubbles.
- Syntax highlighting for fenced code blocks and copy-code buttons.
- Suggested starter prompts when a conversation is empty.
- Confirmation before clearing the current chat or replacing it with a saved conversation.
- Client and server validation for empty/oversized messages.
- Loading and error status messages.
- The existing `python app.py` terminal interface remains available.

### Web API

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Web application |
| `/api/status` | GET | Current model and session status |
| `/api/models` | GET | Available Gemini models |
| `/api/chat` | POST | Send a message |
| `/api/model` | POST | Switch model |
| `/api/history` | GET | Read current history |
| `/api/clear` | POST | Start a new chat |
| `/api/saves` | GET | List saved conversations |
| `/api/save` | POST | Save the current conversation |
| `/api/load` | POST | Load a saved conversation |

Run the web-interface checks with:

```bash
python -m unittest -v test_web_app.py
```
