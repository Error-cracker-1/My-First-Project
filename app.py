import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import ChatbotConfig


load_dotenv()

config = ChatbotConfig.from_env()
client = genai.Client(api_key=config.api_key)

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
    return client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            # This chatbot currently has no tools/functions, so automatic
            # function calling is unnecessary and can produce an SDK warning.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )


def ask_ai(message: str, chat) -> str:
    response = chat.send_message(message)
    return response.text


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

    chat = create_chat(current_model)
    history = []

    print("================================")
    print("        AI Coding Chatbot v1.5")
    print("================================")
    print("Powered by Gemini")
    print(f"Model: {current_model}")
    print(f"Max output tokens: {MAX_OUTPUT_TOKENS}")
    print("Configuration loaded from environment variables.")
    print("Commands: /model, /models, /history, /clear, /exit")
    print("Conversation context is preserved during this session.")
    print("Supports many programming languages, not just Python.\n")

    while True:
        user_message = input("You: ").strip()
        command = user_message.lower()

        if command in {"/exit", "exit"}:
            print("Bot: Goodbye!")
            break

        if command in {"/model", "/models"}:
            selected_model = choose_model(current_model)
            if selected_model != current_model:
                current_model = selected_model
                chat = create_chat(current_model)
                history.clear()
                print("Bot: Started a new conversation with the selected model.\n")
            continue

        if command == "/history":
            print_history(history)
            continue

        if command == "/clear":
            chat = create_chat(current_model)
            history.clear()
            print("Bot: Conversation history cleared. Started a new conversation.\n")
            continue

        if not user_message:
            continue

        try:
            bot_message = ask_ai(user_message, chat)
            history.append((user_message, bot_message))
            print(f"Bot: {bot_message}\n")
        except Exception as error:
            error_text = str(error)
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
                print("Bot: Gemini quota/rate limit reached. No automatic retry was made, so this message will not consume additional requests. Check your Gemini API project quota and try again later.\n")
            else:
                print(f"Bot: Sorry, something went wrong: {error}\n")


if __name__ == "__main__":
    main()
