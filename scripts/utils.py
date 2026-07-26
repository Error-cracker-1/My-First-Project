"""
Utility functions for the Daily AI Review project.
"""

from datetime import datetime
from pathlib import Path
import shutil

from .config import BACKUP_EXTENSION


def file_changed(
    original: str,
    updated: str,
) -> bool:
    """
    Return True if the file content changed.
    """

    return original.strip() != updated.strip()


def backup_file(path: Path) -> Path:
    """
    Create a backup of a file.

    Returns the backup path.
    """

    backup = path.with_suffix(
        path.suffix + BACKUP_EXTENSION
    )

    shutil.copy2(path, backup)

    return backup


def restore_backup(path: Path) -> None:
    """
    Restore a file from its backup.
    """

    backup = path.with_suffix(
        path.suffix + BACKUP_EXTENSION
    )

    if backup.exists():
        shutil.move(backup, path)


def delete_backup(path: Path) -> None:
    """
    Delete a backup file.
    """

    backup = path.with_suffix(
        path.suffix + BACKUP_EXTENSION
    )

    if backup.exists():
        backup.unlink()


def save_file(
    path: Path,
    content: str,
) -> None:
    """
    Save UTF-8 text to a file.
    """

    path.write_text(
        content,
        encoding="utf-8",
    )


def update_changelog(
    changed_files: list[str],
    title: str,
) -> None:
    """
    Append an entry to AI_CHANGELOG.md.
    """

    changelog = Path("AI_CHANGELOG.md")

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    lines = [
        "",
        "## " + timestamp,
        "",
        f"### {title}",
        "",
        "Modified files:",
        "",
    ]

    for file in changed_files:
        lines.append(f"- {file}")

    lines.append("")

    with changelog.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))