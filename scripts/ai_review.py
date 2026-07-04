"""
Daily AI Review

Reviews Git-tracked files with Gemini.

Supports two review modes:

    modified -> Review only modified supported files.
    all      -> Review every supported tracked file.

After reviewing files, the script:
- Saves improvements.
- Updates AI_CHANGELOG.md.
- Creates an AI-generated commit.
- Pushes the commit to feature-1.
"""

import sys
import time
from pathlib import Path

from .repository import (
    get_git_tracked_files,
    read_file,
)
from .utils import (
    file_changed,
    save_file,
    backup_file,
    restore_backup,
    delete_backup,
    update_changelog,
)
from .gemini_client import GeminiClient
from .git_commit import GitCommitManager


def line():
    print("=" * 60)


def get_review_mode() -> str:
    """
    Determine which review mode should be used.

    Supported modes:

        modified
        all

    Default:
        modified
    """

    if len(sys.argv) <= 1:
        return "modified"

    mode = sys.argv[1].strip().lower()

    if mode in ("modified", "all"):
        return mode

    print(f"Unknown review mode: {mode}")
    print("Falling back to 'modified'.")
    print()

    return "modified"


def main():

    start_time = time.time()

    review_mode = get_review_mode()

    line()
    print("Daily AI Review Started")
    line()

    print(f"Review Mode : {review_mode}")

    if review_mode == "all":
        print("Repository   : Full Repository Review")
    else:
        print("Repository   : Modified Files Review")

    line()

    client = GeminiClient()
    git = GitCommitManager()

    reviewed = 0
    changed = 0
    skipped = 0
    failed = 0

    changed_files = []

    files = get_git_tracked_files(review_mode)

    if not files:

        line()

        if review_mode == "all":
            print("No supported files were found.")
        else:
            print("No modified supported files found.")
            print("Repository is already up to date.")

        line()
        return

    print(f"Files discovered : {len(files)}")

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

            # Reduce the chance of hitting Gemini free-tier limits.
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

    print(f"Review Mode       : {review_mode}")
    print(f"Files discovered  : {len(files)}")
    print(f"Files reviewed    : {reviewed}")
    print(f"Files changed     : {changed}")
    print(f"Files skipped     : {skipped}")
    print(f"Files failed      : {failed}")

    if changed_files:

        print()
        print("Modified files:")

        for file in changed_files:
            print(f"  ✓ {file}")

        print()
        print("Generating AI commit message...")

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

    print(f"Review mode        : {review_mode}")
    print(f"Total time         : {elapsed:.2f} seconds")

    if reviewed:
        success = ((reviewed - failed) / reviewed) * 100
        print(f"Success rate       : {success:.1f}%")

    line()
    print("Daily AI Review Finished")
    line()


if __name__ == "__main__":
    main()