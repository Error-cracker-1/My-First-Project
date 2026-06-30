"""
Utility functions for the Daily AI Review project.
"""

from datetime import datetime
from pathlib import Path
import shutil


def file_changed(original: str, updated: str) -> bool:
    """
    Return True if the AI changed the file.
    """
    return original.strip() != updated.strip()


def save_file(path: Path, content: str) -> None:
    """
    Save UTF-8 text.
    """
    path.write_text(
        content,
        encoding="utf-8",
    )


def backup_file(path: Path) -> Path:
    """
    Create a backup before editing.
    """

    backup = path.with_suffix(
        path.suffix + ".bak"
    )

    shutil.copy2(path, backup)

    return backup


def restore_backup(path: Path) -> bool:
    """
    Restore the backup if it exists.
    """

    backup = path.with_suffix(
        path.suffix + ".bak"
    )

    if not backup.exists():
        return False

    shutil.copy2(backup, path)

    backup.unlink()

    return True


def delete_backup(path: Path) -> None:
    """
    Delete the backup after a successful review.
    """

    backup = path.with_suffix(
        path.suffix + ".bak"
    )

    if backup.exists():
        backup.unlink()


def update_changelog(
    changed_files: list[str],
    commit_title: str,
) -> None:
    """
    Update AI_CHANGELOG.md.
    """

    if not changed_files:
        return

    changelog = Path(
        "AI_CHANGELOG.md"
    )

    with changelog.open(
        "a",
        encoding="utf-8",
    ) as f:

        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write(
            f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        )
        f.write(
            f"Commit: {commit_title}\n"
        )
        f.write(
            f"Files Changed: {len(changed_files)}\n"
        )
        f.write("\n")

        for file in changed_files:
            f.write(f"- {file}\n")

        f.write("\n")


def print_header(title: str) -> None:
    """
    Print a formatted header.
    """

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_success(message: str) -> None:
    """
    Print a success message.
    """

    print(f"✓ {message}")


def print_error(message: str) -> None:
    """
    Print an error message.
    """

    print(f"✗ {message}")