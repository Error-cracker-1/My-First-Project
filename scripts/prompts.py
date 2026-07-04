"""
Prompt loader for the Daily AI Review project.
"""

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """
    Load a prompt file from the prompts directory.

    The prompt is cached after the first read to
    avoid unnecessary disk access.
    """

    path = PROMPTS_DIR / name

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8"
    )


def review_prompt(
    filename: str,
    content: str,
) -> str:
    """
    Build the review prompt.
    """

    prompt = load_prompt(
        "review_prompt.txt"
    )

    return prompt.format(
        filename=filename,
        content=content,
    )


def commit_prompt(
    changed_files: list[str],
) -> str:
    """
    Build the commit message prompt.
    """

    prompt = load_prompt(
        "commit_prompt.txt"
    )

    return prompt.format(
        changed_files="\n".join(changed_files),
    )