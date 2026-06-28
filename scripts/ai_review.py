"""
Daily AI Review

Reads Git-tracked files, reviews them with Gemini,
saves improvements, commits the changes,
and pushes them to feature-1.
"""

from pathlib import Path

from scripts.repository import get_git_tracked_files, read_file
from scripts.utils import (
    file_changed,
    save_file,
    update_changelog,
)
from scripts.gemini_client import GeminiClient
from scripts.git_commit import GitCommitManager


def main():
    print("=" * 60)
    print("Daily AI Review Started")
    print("=" * 60)

    client = GeminiClient()
    git = GitCommitManager()

    changed_files = []

    files = get_git_tracked_files()

    if not files:
        print("No supported files found.")
        return

    for file in files:
        original = read_file(file)

        if original is None:
            continue

        print(f"\nReviewing {file}")

        try:
            updated = client.review_file(
                filename=str(file),
                content=original,
            )

            if not updated:
                print("No response from Gemini.")
                continue

            if file_changed(original, updated):
                save_file(Path(file), updated)
                changed_files.append(str(file))
                print("✓ Updated")
            else:
                print("✓ No changes")

        except Exception as e:
            print(f"✗ Error reviewing {file}")
            print(e)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print(f"Files changed: {len(changed_files)}")

    for file in changed_files:
        print(f" - {file}")

    if changed_files:
        print("\nGenerating commit message...")

        title, body = client.generate_commit_message(changed_files)

        print("Updating AI_CHANGELOG.md...")
        update_changelog(changed_files, title)

        print("Creating Git commit...")
        committed = git.commit()

        if committed:
            print("Pushing to feature-1...")
            git.push("feature-1")
        else:
            print("Commit was not created.")
    else:
        print("\nNothing to commit.")


if __name__ == "__main__":
    main()