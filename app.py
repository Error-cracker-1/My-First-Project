import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=api_key)

MODELS = {
    "1": ("Gemini 3.8 Flash", "gemini-3.8-flash"),
    "2": ("Gemini 3.7 Flash", "gemini-3.7-flash"),
    "3": ("Gemini 3.6 Flash", "gemini-3.6-flash"),
    "4": ("Gemini 3.5 Flash-Lite", "gemini-3.5-flash-lite"),
    "5": ("Gemini 2.5 Pro", "gemini-2.5-pro"),
    "6": ("Gemini 2.5 Flash", "gemini-2.5-flash"),
}

SYSTEM_INSTRUCTION = """You are a general-purpose programming and software-development assistant.
You can work with Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP,
Ruby, Kotlin, Swift, Dart, SQL, HTML, CSS, Bash, PowerShell, and other common
programming languages.

Help users write, explain, debug, refactor, optimize, test, and translate code.
Preserve the programming language requested by the user. When providing code,
use fenced code blocks with the correct language identifier. Do not claim to
have executed code unless it was actually executed. Ask for missing context
when necessary.
"""


def ask_ai(message: str, model: str) -> str:
    response = client.models.generate_content(
        model=model,
        contents=message,
        config={"system_instruction": SYSTEM_INSTRUCTION},
    )
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


def main() -> None:
    current_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    print("================================")
    print("        AI Coding Chatbot v1.1")
    print("================================")
    print("Powered by Gemini")
    print(f"Model: {current_model}")
    print("Commands: /model, /models, /exit")
    print("Supports many programming languages, not just Python.\n")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in {"/exit", "exit"}:
            print("Bot: Goodbye!")
            break

        if user_message.lower() in {"/model", "/models"}:
            current_model = choose_model(current_model)
            continue

        if not user_message:
            continue

        try:
            print(f"Bot: {ask_ai(user_message, current_model)}\n")
        except Exception as error:
            print(f"Bot: Sorry, something went wrong: {error}\n")


if __name__ == "__main__":
    main()
