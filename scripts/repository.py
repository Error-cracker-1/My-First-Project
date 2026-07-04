"""
Repository utilities for the Daily AI Review project.
"""

from pathlib import Path
import subprocess
from typing import Set, List, Optional


SUPPORTED_EXTENSIONS: Set[str] = {
    ".py",
    ".html",
    ".css",
    ".md",
    ".txt",
    ".ps1",
}

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".venv",
    ".github",
    "__pycache__",
    "docs",
    "prompts",
    "scripts",
}

EXCLUDED_FILES: Set[str] = {
    "AI_CHANGELOG.md",
    "requirements.txt",
    "Requirements.txt",
}

MAX_FILE_SIZE: int = 100_000  # characters


def get_git_tracked_files(review_mode: str = "modified") -> List[Path]:
    """
    Return Git-tracked files for AI review, filtered by review mode and exclusions.

    Args:
        review_mode (str): Specifies which files to retrieve.
                           "modified" -> Only modified supported files.
                           "all"      -> All supported tracked files.
                           Defaults to "modified".

    Returns:
        list[Path]: A sorted list of Path objects representing the filtered files.

    Raises:
        ValueError: If an invalid `review_mode` is provided.
        subprocess.CalledProcessError: If the underlying git command fails.
    """
    if review_mode == "modified":
        command = [
            "git",
            "diff",
            "--name-only",
            "HEAD",
        ]
    elif review_mode == "all":
        command = [
            "git",
            "ls-files",
        ]
    else:
        raise ValueError(
            f"Invalid review mode: '{review_mode}'. Expected 'modified' or 'all'."
        )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    files: List[Path] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        path = Path(line)

        # Skip files residing in excluded directories (e.g., .git/, .venv/)
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        # Skip files explicitly named in EXCLUDED_FILES
        if path.name in EXCLUDED_FILES:
            continue

        # Skip files with unsupported extensions
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files.append(path)

    return sorted(files)


def read_file(path: Path) -> Optional[str]:
    """
    Read a UTF-8 text file safely and return its content.

    Handles decoding errors, large files, and other read errors by returning None.
    Prints informative messages to stdout for skipped files or errors.

    Args:
        path (Path): The path to the file to read.

    Returns:
        Optional[str]: The content of the file as a string if successful and
                       within size limits, otherwise None.
    """
    try:
        text = path.read_text(encoding="utf-8")

        if len(text) > MAX_FILE_SIZE:
            print(f"Skipping large file: {path}")
            return None

        return text
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {path}")
        return None
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None