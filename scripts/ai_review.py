from google import genai
import os

print("=" * 50)
print("Daily AI Review Started")
print("=" * 50)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Reply with exactly: API connection successful."
)

print(response.text)