import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import ChatbotConfig


load_dotenv()

# Current stable Gemini models suitable for coding assistance.
# The default is the cost-efficient 3.5 Flash-Lite model.
MODELS = {
    "1": ("Gemini 3.5 Flash-Lite", "gemini-3.5-flash-lite"),
    "2": ("Gemini 3.5 Flash", "gemini-3.5-flash"),
    "3": ("Gemini 3.6 Flash", "gemini-3.6-flash"),
    "4": ("Gemini 3.1 Flash-Lite", "gemini-3.1-flash-lite"),
    "5": ("Gemini 2.5 Flash-Lite", "gemini-2.5-flash-lite"),
    "6": ("Gemini 2.5 Flash", "gemini-2.5-flash"),
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
    """Create a Gemini chat and let callers handle API failures gracefully."""
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
        or "model" in lower_text and "not found" in lower_text
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


def choose_model(current_model: str) -> str:
    print("\nAvailable Gemini models:")
    for key, (name, model_id) in MODELS.items():
        marker = " (current)" if model_id == current_model else ""
        print(f"{key}. {name} [{model_id}]{marker}")

    choice = input("Select model (1-6), or press Enter to keep current: ").strip()
    if not choice:
        return current_model

    if choice not in MODELS:
        print("Invalid model selection. Keeping the current model.")
        return current_model

    selected_name, selected_model = MODELS[choice]
    print(f"Switched to {selected_name}.")
    return selected_model


def print_history(history) -> None:
    if not history:
        print("Bot: No conversation history yet.\n")
        return

    print("\n========== Conversation History ==========")
    for index, (user_message, bot_message) in enumerate(history, start=1):
        print(f"\n[{index}] You: {user_message}")
        print(f"    Bot: {bot_message}")
    print("\n===========================================\n")


def main() -> None:
    current_model = config.model
    chat = safe_create_chat(current_model)

    if chat is None:
        print("Bot: Chat startup failed. Check your configuration and try again.")
        return

    history = []

    print("================================")
    print("        AI Coding Chatbot v1.6")
    print("================================")
    print("Powered by Gemini")
    print(f"Model: {current_model}")
    print(f"Max output tokens: {MAX_OUTPUT_TOKENS}")
    print("Configuration loaded from environment variables.")
    print("Improved error handling is enabled.")
    print("Commands: /model, /models, /history, /clear, /exit")
    print("Conversation context is preserved during this session.")
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
            if selected_model != current_model:
                new_chat = safe_create_chat(selected_model)
                if new_chat is None:
                    print("Bot: Model switch failed. Keeping the current model.\n")
                    continue

                current_model = selected_model
                chat = new_chat
                history.clear()
                print("Bot: Started a new conversation with the selected model.\n")
            continue

        if command == "/history":
            print_history(history)
            continue

        if command == "/clear":
            new_chat = safe_create_chat(current_model)
            if new_chat is None:
                print("Bot: Could not clear the conversation because a new chat could not be created.\n")
                continue

            chat = new_chat
            history.clear()
            print("Bot: Conversation history cleared. Started a new conversation.\n")
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
