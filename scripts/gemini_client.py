"""
Gemini client for the Daily AI Review project.
"""

import os
import time

from google import genai

from .prompts import (
    PromptManager,
    commit_prompt,
)

MODEL = "gemini-2.5-flash"

MAX_RETRIES = 5
INITIAL_DELAY = 25


class GeminiClient:
    """
    Wrapper around the Gemini API.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY environment variable is missing."
            )

        self.client = genai.Client(api_key=api_key)
        self.prompt_manager = PromptManager()

    def _generate(self, prompt: str):
        """
        Generate content with automatic retry if the
        Gemini free-tier rate limit is exceeded.
        """

        delay = INITIAL_DELAY

        for attempt in range(MAX_RETRIES):
            try:
                return self.client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                )

            except Exception as e:
                error = str(e)

                if (
                    "429" in error
                    or "RESOURCE_EXHAUSTED" in error
                ):
                    print()
                    print("=" * 60)
                    print("Gemini rate limit reached.")
                    print(f"Retry {attempt + 1}/{MAX_RETRIES}")
                    print(f"Waiting {delay} seconds...")
                    print("=" * 60)
                    print()

                    time.sleep(delay)

                    delay *= 2
                    continue

                raise

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