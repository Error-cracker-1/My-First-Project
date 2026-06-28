"""
Gemini client for the Daily AI Review project.
"""

import os
from google import genai

MODEL = "gemini-2.5-flash"


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY environment variable is missing."
            )

        self.client = genai.Client(api_key=api_key)

    def review_file(self, filename: str, content: str) -> str:
        """
        Send a single file to Gemini for review and return the updated file.
        """

        prompt = f"""
You are an expert software engineer reviewing a Git repository.

Review ONLY this file.

Filename:
{filename}

Rules:
- Preserve functionality.
- Do not invent new features.
- Fix bugs if they exist.
- Improve readability.
- Improve formatting.
- Improve comments where useful.
- Keep the same programming language.
- Return ONLY the complete updated file.
- Do NOT explain your changes.
- Do NOT use markdown.
- Do NOT wrap the answer in ```.

File:

{content}
"""

        response = self.client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            return content

        text = text.strip()

        # Remove accidental markdown code fences
        if text.startswith("```"):
            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        # Remove accidental language tag
        if text.lower().startswith("python\n"):
            text = text[7:]

        return text if text else content

    def generate_commit_message(self, changed_files: list[str]) -> tuple[str, str]:
        """
        Generate a Git commit title and body.
        """

        prompt = f"""
Generate a professional Git commit message.

Changed files:

{chr(10).join(changed_files)}

Return exactly in this format:

TITLE:
<one line>

BODY:
<multiple lines>

Do not use markdown.
"""

        response = self.client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            return (
                "AI repository review",
                "Automated repository review completed."
            )

        text = text.strip()

        title = "AI repository review"
        body = "Automated repository review completed."

        if "TITLE:" in text and "BODY:" in text:
            try:
                title_part, body_part = text.split("BODY:", 1)
                title = title_part.replace("TITLE:", "").strip()
                body = body_part.strip()
            except Exception:
                pass

        return title, body