"""
Utility functions for Daily AI Review.
"""

from datetime import datetime
from pathlib import Path


def file_changed(original: str, updated: str) -> bool:
    """
    Return True if the AI changed the file.
    """
    return original.strip() != updated.strip()


def save_file(path: Path, content: str) -> None:
    """
    Save UTF-8 text.
    """
    path.write_text(content, encoding="utf-8")


def backup_file(path: Path) -> None:
    """
    Create a .bak backup before editing.
    """
    backup = path.with_suffix(path.suffix + ".bak")

    backup.write_text(
        path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def restore_backup(path: Path) -> None:
    """
    Restore the backup if needed.
    """
    backup = path.with_suffix(path.suffix + ".bak")

    if backup.exists():
        path.write_text(
            backup.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        backup.unlink()


def update_changelog(changed_files: list[str], commit_title: str) -> None:
    """
    Append a summary of the AI review to AI_CHANGELOG.md.
    """

    if not changed_files:
        return

    changelog = Path("AI_CHANGELOG.md")

    with changelog.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Commit: {commit_title}\n")
        f.write(f"Files Changed: {len(changed_files)}\n\n")

        for file in changed_files:
            f.write(f"- {file}\n")

        f.write("\n")