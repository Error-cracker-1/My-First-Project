"""
Daily AI Review

Reviews modified Git-tracked files with Gemini,
saves improvements, updates the changelog,
creates an AI-generated commit,
and pushes them to feature-1.
"""

import time
from pathlib import Path

from scripts.repository import (
    get_git_tracked_files,
    read_file,
)
from scripts.utils import (
    file_changed,
    save_file,
    backup_file,
    restore_backup,
    delete_backup,
    update_changelog,
)
from scripts.gemini_client import GeminiClient
from scripts.git_commit import GitCommitManager


def line():
    print("=" * 60)


def main():
    start_time = time.time()

    line()
    print("Daily AI Review Started")
    line()

    client = GeminiClient()
    git = GitCommitManager()

    reviewed = 0
    changed = 0
    skipped = 0
    failed = 0

    changed_files = []

    files = get_git_tracked_files()

    if not files:
        line()
        print("No modified supported files found.")
        print("Repository is already up to date.")
        line()
        return

    print(f"Files to review: {len(files)}")

    for file in files:

        print()
        print("-" * 60)
        print(f"Reviewing: {file}")
        print("-" * 60)

        original = read_file(file)

        if original is None:
            skipped += 1
            continue

        reviewed += 1

        try:

            backup_file(Path(file))

            updated = client.review_file(
                filename=str(file),
                content=original,
            )

            if not updated:

                print("No response from Gemini.")

                restore_backup(Path(file))

                failed += 1

                continue

            if file_changed(original, updated):

                save_file(
                    Path(file),
                    updated,
                )

                delete_backup(Path(file))

                changed += 1

                changed_files.append(str(file))

                print("✓ File updated")

            else:

                delete_backup(Path(file))

                skipped += 1

                print("✓ No changes needed")

            # Reduce chance of hitting Gemini limits.
            time.sleep(2)

        except Exception as e:

            print(f"✗ Error reviewing {file}")
            print(e)

            try:
                restore_backup(Path(file))
            except Exception:
                pass

            failed += 1
        line()
    print("Review Summary")
    line()

    print(f"Files discovered : {len(files)}")
    print(f"Files reviewed   : {reviewed}")
    print(f"Files changed    : {changed}")
    print(f"Files skipped    : {skipped}")
    print(f"Files failed     : {failed}")

    if changed_files:

        print()
        print("Modified files:")

        for file in changed_files:
            print(f"  ✓ {file}")

        print()
        print("Generating commit message...")

        title, body = client.generate_commit_message(
            changed_files
        )

        print("Updating AI_CHANGELOG.md...")

        update_changelog(
            changed_files,
            title,
        )

        print("Creating Git commit...")

        committed = git.commit()

        if committed:

            print("Pushing to feature-1...")

            pushed = git.push("feature-1")

            if pushed:
                print("✓ Push completed successfully.")
            else:
                print("✗ Push failed.")

        else:

            print("Commit was not created.")

    else:

        print()
        print("No files were modified.")
        print("Nothing to commit.")

    elapsed = time.time() - start_time

    line()
    print("Execution Summary")
    line()

    print(f"Total execution time : {elapsed:.2f} seconds")

    if reviewed:
        print(
            f"Success rate         : "
            f"{((reviewed - failed) / reviewed) * 100:.1f}%"
        )

    line()
    print("Daily AI Review Finished")
    line()


if __name__ == "__main__":
    main()