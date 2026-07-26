"""
Repository utilities for the Daily AI Review project.
"""

from pathlib import Path
import subprocess

from .config import (
    EXCLUDED_DIRECTORIES,
    EXCLUDED_FILES,
    SKIP_SELF_REVIEW,
    SELF_REVIEW_PATHS,
    SUPPORTED_EXTENSIONS,
)


def _is_supported(path: Path) -> bool:
    """
    Return True if the file should be reviewed.
    """

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    if path.name in EXCLUDED_FILES:
        return False

    if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
        return False

    if SKIP_SELF_REVIEW:
        if any(part in SELF_REVIEW_PATHS for part in path.parts):
            return False

    return True


GIT_FAILED = False


def _git_files(command: list[str]) -> list[Path]:
    """
    Return Git files matching the given command.
    """
    global GIT_FAILED

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        files = []

        for line in result.stdout.splitlines():
            line = line.strip()

            if not line:
                continue

            path = Path(line)

            if _is_supported(path):
                files.append(path)

        return sorted(files)
    except Exception as e:
        GIT_FAILED = True
        print(f"Warning: Git command {command} failed ({e}). Falling back to file system scan.")
        files = []
        for p in Path.cwd().rglob("*"):
            if p.is_file():
                try:
                    rel_path = p.relative_to(Path.cwd())
                    if _is_supported(rel_path):
                        files.append(rel_path)
                except Exception:
                    pass
        return sorted(files)


def get_git_tracked_files(
    mode: str = "modified",
) -> list[Path]:
    """
    Return repository files.

    modified -> only modified tracked files

    all -> every tracked supported file
    """

    if mode == "all":
        return _git_files(
            [
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                "HEAD",
            ]
        )

    return _git_files(
        [
            "git",
            "diff",
            "--name-only",
        ]
    )


def read_file(path: Path) -> str | None:
    """
    Read a UTF-8 text file.
    """

    try:
        return path.read_text(
            encoding="utf-8",
        )

    except Exception as e:
        print(f"Unable to read {path}")
        print(e)
        return None