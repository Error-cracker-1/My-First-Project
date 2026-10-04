import os\nfrom pathlib import Path\nfrom dotenv import load_dotenv
from google import genai
from google.genai import types

from config import ChatbotConfig


load_dotenv()

# Models supported by the configuration system.
MODELS = {
    "1": ("Gemini 3.8 Flash", "gemini-3.8-flash"),
    "2": ("Gemini 3.7 Flash", "gemini-3.7-flash"),
    "3": ("Gemini 3.6 Flash", "gemini-3.6-flash"),
    "4": ("Gemini 3.5 Flash", "gemini-3.5-flash"),
    "5": ("Gemini 3.5 Flash-Lite", "gemini-3.5-flash-lite"),
    "6": ("Gemini 3.1 Flash-Lite", "gemini-3.1-flash-lite"),
    "7": ("Gemini 3.1 Pro Preview", "gemini-3.1-pro-preview"),
    "8": ("Gemini 3 Flash Preview", "gemini-3-flash-preview"),
    "9": ("Gemini 2.5 Pro", "gemini-2.5-pro"),
    "10": ("Gemini 2.5 Flash", "gemini-2.5-flash"),
    "11": ("Gemini 2.5 Flash-Lite", "gemini-2.5-flash-lite"),
}

MODEL_ALIASES = {
    "3.8": "gemini-3.8-flash",
    "3.7": "gemini-3.7-flash",
    "3.6": "gemini-3.6-flash",
    "flash": "gemini-3.5-flash",
    "flash-lite": "gemini-3.5-flash-lite",
    "3.1-lite": "gemini-3.1-flash-lite",
    "3.1-pro": "gemini-3.1-pro-preview",
    "3-flash": "gemini-3-flash-preview",
    "2.5-pro": "gemini-2.5-pro",
    "2.5-flash": "gemini-2.5-flash",
    "2.5-lite": "gemini-2.5-flash-lite",
}

config = ChatbotConfig.from_env()
client = genai.Client(api_key=config.api_key)

DEFAULT_MODEL = config.model
MAX_OUTPUT_TOKENS = config.max_output_tokens

SYSTEM_INSTRUCTION = """You are a general-purpose programming and software-development assistant.
You can work with Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP,
Ruby, Kotlin, Swift, Dart, SQL, HTML, CSS, Bash, PowerShell, and other common
programming languages.

Help users write, explain, debug, refactor, optimize, test, and translate code.
Preserve the programming language requested by the user. When providing code,
use fenced code blocks with the correct language identifier. Do not claim to
have executed code unless it was actually executed. Ask for missing context
when necessary. Keep answers concise unless the user asks for more detail.
"""


def create_chat(model: str):
    """Create a Gemini chat using the current configuration."""
    return client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )


def classify_error(error: Exception) -> str:
    """Return a user-friendly category for common Gemini/API failures."""
    error_text = str(error).strip()
    lower_text = error_text.lower()

    if (
        "429" in error_text
        or "resource_exhausted" in lower_text
        or "quota" in lower_text
        or "rate limit" in lower_text
    ):
        return (
            "Gemini quota or rate limit reached. "
            "The request was not automatically retried."
        )

    if (
        "401" in error_text
        or "403" in error_text
        or "unauthenticated" in lower_text
        or "permission denied" in lower_text
        or "api key" in lower_text
        or "invalid api key" in lower_text
    ):
        return (
            "Gemini authentication or permission error. "
            "Check GEMINI_API_KEY and the API project's access."
        )

    if (
        "404" in error_text
        or "not found" in lower_text
        or ("model" in lower_text and "not found" in lower_text)
    ):
        return (
            "The selected Gemini model is unavailable. "
            "Use /model to select another configured model."
        )

    if (
        "timeout" in lower_text
        or "timed out" in lower_text
        or "connection" in lower_text
        or "network" in lower_text
        or "503" in error_text
        or "502" in error_text
        or "500" in error_text
    ):
        return (
            "Gemini service or network error. "
            "Check your connection and try the message again."
        )

    return "Unexpected Gemini error. The conversation is still available."


def safe_create_chat(model: str):
    """Create a chat without allowing an API failure to terminate the program."""
    try:
        return create_chat(model)
    except Exception as error:
        print(f"Bot: Unable to start the Gemini chat. {classify_error(error)}")
        return None


def ask_ai(message: str, chat):
    """Send a message and return either the response or a safe error message."""
    try:
        response = chat.send_message(message)
        if not response or not getattr(response, "text", None):
            return None, "Gemini returned an empty response. Please try again."
        return response.text, None
    except Exception as error:
        return None, classify_error(error)


def model_display_name(model_id: str) -> str:
    """Return the friendly name for a model ID."""
    for name, configured_id in MODELS.values():
        if configured_id == model_id:
            return name
    return model_id


def choose_model(current_model: str) -> str:
    print("\n========== Model Manager ==========")
    print(f"Current model: {model_display_name(current_model)}")
    print(f"Model ID:      {current_model}\n")

    for key, (name, model_id) in MODELS.items():
        marker = " [CURRENT]" if model_id == current_model else ""
        print(f"{key}. {name}{marker}")
        print(f"   ID: {model_id}")

    print("\nAliases:")
    print("  flash-lite  -> Gemini 3.5 Flash-Lite")
    print("  flash       -> Gemini 3.5 Flash")
    print("  flash-3.6   -> Gemini 3.6 Flash")

    choice = input("\nSelect 1-6, enter an alias, or press Enter to keep current: ").strip().lower()
    if not choice:
        return current_model

    if choice in MODELS:
        return MODELS[choice][1]

    if choice in MODEL_ALIASES:
        return MODEL_ALIASES[choice]

    print("Invalid model selection. Keeping the current model.")
    return current_model


MAX_FILE_SIZE = 512 * 1024
SUPPORTED_FILE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".h", ".cpp", ".cc",
    ".cxx", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".kt", ".kts", ".swift",
    ".dart", ".sql", ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".txt", ".md",
    ".ps1", ".psm1", ".bat", ".cmd", ".sh", ".bash", ".zsh", ".fish",
    ".vue", ".svelte", ".astro",
}


def detect_language(path: Path) -> str:
    if path.name.lower() == "dockerfile":
        return "dockerfile"
    labels = {
        ".py": "python", ".js": "javascript", ".jsx": "jsx", ".ts": "typescript",
        ".tsx": "tsx", ".java": "java", ".c": "c", ".h": "c", ".cpp": "cpp",
        ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".cs": "csharp",
        ".go": "go", ".rs": "rust", ".php": "php", ".rb": "ruby",
        ".kt": "kotlin", ".kts": "kotlin", ".swift": "swift", ".dart": "dart",
        ".sql": "sql", ".html": "html", ".htm": "html", ".css": "css",
        ".scss": "scss", ".sass": "sass", ".less": "less", ".json": "json",
        ".xml": "xml", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
        ".md": "markdown", ".ps1": "powershell", ".sh": "bash", ".bash": "bash",
        ".zsh": "zsh", ".fish": "fish", ".bat": "batch", ".cmd": "batch",
        ".vue": "vue", ".svelte": "svelte", ".astro": "astro", ".txt": "text",
    }
    return labels.get(path.suffix.lower(), "text")


def read_code_file(file_path: str):
    path = Path(file_path.strip().strip('"')).expanduser()
    if not path.exists():
        return None, "File not found."
    if not path.is_file():
        return None, "The supplied path is not a file."
    if path.stat().st_size > MAX_FILE_SIZE:
        return None, "File is larger than the 512 KB v1.8 input limit."
    if path.suffix.lower() not in SUPPORTED_FILE_EXTENSIONS and path.name.lower() != "dockerfile":
        return None, "Unsupported file type. Use a text or source-code file."
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "The file is not valid UTF-8 text."
    except OSError as error:
        return None, f"Could not read the file: {error}"
    language = detect_language(path)
    return (
        f"File: {path.name}\nPath: {path}\nLanguage: {language}\n\n"
        f"~~~{language}\n{content}\n~~~",
        None,
    )


def send_file_to_ai(file_path: str, chat):
    file_context, error = read_code_file(file_path)
    if error:
        return None, error
    prompt = (
        "A local source/text file has been provided for analysis. "
        "Do not execute it. Use it as context for the user's request.\n\n"
        + file_context
    )
    return ask_ai(prompt, chat)

def print_history(history, model: str) -> None:
    if not history:
        print(f"Bot: No conversation history for {model_display_name(model)} yet.\n")
        return

    print(f"\n========== History: {model_display_name(model)} ==========")
    for index, (user_message, bot_message) in enumerate(history, start=1):
        print(f"\n[{index}] You: {user_message}")
        print(f"    Bot: {bot_message}")
    print("\n===========================================\n")


def print_model_status(current_model: str, sessions) -> None:
    print("\n========== Model Status ==========")
    print(f"Active: {model_display_name(current_model)}")
    print(f"ID:     {current_model}")
    print(f"Stored model sessions: {len(sessions)}")
    for model_id, (_, history) in sessions.items():
        print(f"  - {model_display_name(model_id)}: {len(history)} messages")
    print("==================================\n")


def main() -> None:
    current_model = config.model
    initial_chat = safe_create_chat(current_model)

    if initial_chat is None:
        print("Bot: Chat startup failed. Check your configuration and try again.")
        return

    # Keep a separate chat and local history for each selected model.
    # Switching models no longer destroys the previous model's session.
    sessions = {
        current_model: (initial_chat, []),
    }

    print("================================")
    print("        AI Coding Chatbot v1.8")
    print("================================")
    print("Powered by Gemini")
    print(f"Model: {model_display_name(current_model)}")
    print(f"Model ID: {current_model}")
    print(f"Max output tokens: {MAX_OUTPUT_TOKENS}")
    print("Configuration loaded from environment variables.")
    print("Improved error handling is enabled.")
    print("Enhanced model switching is enabled.")\n    print("File/code input is enabled (512 KB UTF-8 text/source limit).")
    print("Commands: /model, /models, /file, /current, /history, /clear, /exit")
    print("Conversation sessions are preserved separately for each model.")
    print("Supports many programming languages, not just Python.\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break

        command = user_message.lower()

        if command in {"/exit", "exit"}:
            print("Bot: Goodbye!")
            break

        if command in {"/model", "/models"}:
            selected_model = choose_model(current_model)
            if selected_model == current_model:
                continue

            if selected_model in sessions:
                chat, _ = sessions[selected_model]
                current_model = selected_model
                print(
                    f"Bot: Switched to {model_display_name(current_model)}. "
                    "Previous session restored.\n"
                )
                continue

            new_chat = safe_create_chat(selected_model)
            if new_chat is None:
                print("Bot: Model switch failed. Keeping the current model.\n")
                continue

            sessions[selected_model] = (new_chat, [])
            current_model = selected_model
            print(
                f"Bot: Switched to {model_display_name(current_model)}. "
                "A new session was created for this model.\n"
            )
            continue

        if command == "/current":
            print_model_status(current_model, sessions)
            continue

        chat, history = sessions[current_model]

        if command == "/history":
            print_history(history, current_model)
            continue

        if command == "/clear":
            new_chat = safe_create_chat(current_model)
            if new_chat is None:
                print(
                    "Bot: Could not clear the conversation because a new "
                    "chat could not be created.\n"
                )
                continue

            sessions[current_model] = (new_chat, [])
            print(
                f"Bot: {model_display_name(current_model)} conversation "
                "history cleared.\n"
            )
            continue

        if command == "/file":
            file_path = input("File path: ").strip()
            bot_message, error_message = send_file_to_ai(file_path, chat)
            if error_message:
                print(f"Bot: {error_message}\n")
                continue
            history.append((f"[File input] {file_path}", bot_message))
            print(f"Bot: {bot_message}\n")
            continue

        if command.startswith("/file "):
            file_path = user_message[6:].strip()
            bot_message, error_message = send_file_to_ai(file_path, chat)
            if error_message:
                print(f"Bot: {error_message}\n")
                continue
            history.append((f"[File input] {file_path}", bot_message))
            print(f"Bot: {bot_message}\n")
            continue

        if not user_message:
            continue

        bot_message, error_message = ask_ai(user_message, chat)

        if error_message:
            print(f"Bot: {error_message}\n")
            continue

        history.append((user_message, bot_message))
        print(f"Bot: {bot_message}\n")


if __name__ == "__main__":
    main()
