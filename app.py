import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=api_key)

def ask_ai(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=message,
    )
    return response.text

def main() -> None:
    print("================================")
    print("        AI Chatbot v1.0")
    print("================================")
    print("Powered by Gemini")
    print("Type 'exit' to quit.\n")

    while True:
        user_message = input("You: ").strip()
        if user_message.lower() == "exit":
            print("Bot: Goodbye!")
            break
        if not user_message:
            continue
        try:
            print(f"Bot: {ask_ai(user_message)}\n")
        except Exception as error:
            print(f"Bot: Sorry, something went wrong: {error}\n")

if __name__ == "__main__":
    main()
