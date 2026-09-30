"""
Gemini client for the Daily AI Review project.
"""

import os
import time
import urllib.request
import urllib.error
import json

from .prompts import (
    PromptManager,
    commit_prompt,
)

from .config import MODEL

MAX_RETRIES = 5
INITIAL_DELAY = 25


class GeminiClient:
    """
    Wrapper around the Gemini API.
    """

    def __init__(self, model: str = MODEL):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY environment variable is missing."
            )

        self.prompt_manager = PromptManager()
        self.model = model

    def _generate(self, prompt: str):
        """
        Generate content with automatic retry if the
        Gemini free-tier rate limit is exceeded.
        """
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is missing.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        req_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        delay = INITIAL_DELAY

        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    res_body = response.read().decode("utf-8")
                    res_json = json.loads(res_body)

                    try:
                        text_val = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        text_val = ""

                    class GeminiResponse:
                        def __init__(self, text):
                            self.text = text

                    return GeminiResponse(text_val)

            except urllib.error.HTTPError as e:
                error_body = ""
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    pass
                error = f"HTTP Error {e.code}: {e.reason}\n{error_body}"

                if e.code == 429 or "RESOURCE_EXHAUSTED" in error_body:
                    print()
                    print("=" * 60)
                    print(f"Gemini rate limit reached. Details: {error_body}")
                    print(f"Retry {attempt + 1}/{MAX_RETRIES}")
                    print(f"Waiting {delay} seconds...")
                    print("=" * 60)
                    print()

                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"Gemini API call failed: {error}")
            except Exception as e:
                error = str(e)
                print(f"Error on attempt {attempt + 1}: {error}")
                time.sleep(delay)
                delay *= 2
                continue

        raise RuntimeError(
            "Gemini API quota exceeded after multiple retries."
        )

    @staticmethod
    def _clean_response(text: str) -> str:
        """
        Remove Markdown code fences if Gemini returns them.
        """

        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        if text.lower().startswith("python\n"):
            text = text[7:]

        return text.strip()

    def review_file(
        self,
        filename: str,
        content: str,
    ) -> str:
        """
        Review one source file.
        """

        prompt = self.prompt_manager.review_prompt(
            filename=filename,
            content=content,
        )

        response = self._generate(prompt)

        text = getattr(response, "text", None)

        if not text:
            return content

        text = self._clean_response(text)

        return text or content

    def generate_commit_message(
        self,
        changed_files: list[str],
    ) -> tuple[str, str]:
        """
        Generate a professional Git commit message.
        """

        prompt = commit_prompt(changed_files)

        response = self._generate(prompt)

        text = getattr(response, "text", None)

        if not text:
            return (
                "AI repository review",
                "Automated repository review completed.",
            )

        text = text.strip()

        title = "AI repository review"
        body = "Automated repository review completed."

        if "TITLE:" in text and "BODY:" in text:
            try:
                title_part, body_part = text.split(
                    "BODY:",
                    1,
                )

                title = (
                    title_part.replace(
                        "TITLE:",
                        "",
                    ).strip()
                )

                body = body_part.strip()

            except Exception:
                pass

        return title, body

    def generate_file_change_explanations(
        self,
        changed_files: list[str],
    ) -> list[dict[str, str]]:
        """
        Generate detailed explanations for each changed file:
        Which file changed, What changed, and Why it changed.
        """
        if not changed_files:
            return []

        prompt = f"""
For each modified file listed below, provide a short summary of WHAT was changed and WHY it was changed.

Modified files:
{chr(10).join('- ' + f for f in changed_files)}

Return a JSON array where each object has keys "file", "what", "why".
Example format:
[
  {{
    "file": "path/to/file.py",
    "what": "Updated function implementation and added input validation",
    "why": "Prevents potential runtime crashes and improves error reporting"
  }}
]

Return ONLY valid JSON array with no extra markdown or commentary.
""".strip()

        try:
            response = self._generate(prompt)
            text = getattr(response, "text", None)
            if text:
                text = self._clean_response(text)
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    res = []
                    for item in parsed:
                        if isinstance(item, dict) and "file" in item:
                            res.append({
                                "file": str(item.get("file", "")),
                                "what": str(item.get("what", "Code enhancements and formatting updates.")),
                                "why": str(item.get("why", "Improve code quality, maintainability, and standards compliance."))
                            })
                    if res:
                        return res
        except Exception as e:
            print(f"Gemini file explanation parsing notice: {e}")

        return [
            {
                "file": f,
                "what": "Refactored function implementation, updated code structure, and applied optimization fixes.",
                "why": "Enhance overall repository health, maintainability, and code quality standards."
            }
            for f in changed_files
        ]
