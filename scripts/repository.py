from pathlib import Path
import subprocess

SUPPORTED_EXTENSIONS = {
    ".py",
    ".html",
    ".css",
    ".js",
    ".md",
    ".txt",
    ".xml",
    ".ps1",
}

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".github",
    "__pycache__",
    "docs",
    "scripts",
    "prompts",
}

EXCLUDED_FILES = {
    "AI_CHANGELOG.md",
    "requirements.txt",
    "Requirements.txt",
}

MAX_FILE_SIZE = 100_000  # characters


def get_git_tracked_files():
    """Return Git-tracked files that the AI should review."""

    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )

    files = []

    for line in result.stdout.splitlines():
        path = Path(line)

        # Skip excluded directories
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        # Skip excluded files
        if path.name in EXCLUDED_FILES:
            continue

        # Skip unsupported extensions
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Skip minified files
        if path.name.endswith(".min.js") or path.name.endswith(".min.css"):
            continue

        files.append(path)

    return files


def read_file(path: Path):
    """Read a UTF-8 text file safely."""

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