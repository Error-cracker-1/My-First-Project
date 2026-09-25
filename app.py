import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

client = OpenAI(api_key=api_key)

def ask_ai(message: str) -> str:
    response = client.responses.create(
        model="gpt-5.5",
        instructions="You are a helpful and friendly AI chatbot.",
        input=message,
    )
    return response.output_text

def main() -> None:
    print("================================")
    print("        AI Chatbot v1.0")
    print("================================")
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
