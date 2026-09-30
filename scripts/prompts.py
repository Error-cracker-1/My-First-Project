"""
Prompt loading and selection for the Daily AI Review project.
"""

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

GENERIC_REVIEW_PROMPT = "generic_review.txt"

REVIEW_PROMPTS_BY_EXTENSION = {
    ".py": "python_review.txt",
    ".html": "html_review.txt",
    ".css": "css_review.txt",
    ".js": "javascript_review.txt",
    ".md": "markdown_review.txt",
    ".ps1": "powershell_review.txt",
    ".json": "json_review.txt",
}


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


class PromptManager:
    def __init__(
        self,
        prompts_by_extension: dict[str, str] | None = None,
        generic_prompt: str = GENERIC_REVIEW_PROMPT,
    ):
        self.prompts_by_extension = (
            prompts_by_extension or REVIEW_PROMPTS_BY_EXTENSION
        )
        self.generic_prompt = generic_prompt

    def prompt_name_for_file(self, filename: str) -> str:
        extension = Path(filename).suffix.lower()
        prompt_name = self.prompts_by_extension.get(
            extension, self.generic_prompt
        )
        prompt_path = PROMPTS_DIR / prompt_name
        if not prompt_path.exists():
            return self.generic_prompt
        return prompt_name

    def review_prompt(self, filename: str, content: str) -> str:
        prompt = load_prompt(self.prompt_name_for_file(filename))
        return prompt.format(filename=filename, content=content)


def review_prompt(filename: str, content: str) -> str:
    return PromptManager().review_prompt(filename=filename, content=content)


def commit_prompt(changed_files: list[str]) -> str:
    prompt = load_prompt("commit_prompt.txt")
    return prompt.format(changed_files="\n".join(changed_files))
