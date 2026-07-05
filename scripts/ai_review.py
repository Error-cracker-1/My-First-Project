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

from .cache import ReviewCache
from .config import REVIEW_DELAY
from .dashboard import generate_dashboard
from .html_dashboard import generate_html_dashboard
from .function_review import (
    compare_functions,
    merge_updated_functions,
    read_head_version,
)
from .repository import (
    get_git_tracked_files,
    read_file,
)
from .utils import (
    backup_file,
    delete_backup,
    file_changed,
    restore_backup,
    save_file,
    update_changelog,
)
from .report import (
    ReviewStatistics,
    print_report,
)
from .review_report import generate_review_report
from .gemini_client import GeminiClient
from .git_commit import GitCommitManager


def line():
    """Print a separator line."""
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
        print("Repository  : Full Repository Review")
    else:
        print("Repository  : Modified Files Review")

    line()

    client = GeminiClient()
    git = GitCommitManager()
    cache = ReviewCache()

    reviewed = 0
    changed = 0
    skipped = 0
    failed = 0

    changed_files = []
    skipped_files = []
    failed_files = {}
    commit_title = "Not generated"
    commit_body = "No AI commit was generated."
    changelog_files = []

    files = get_git_tracked_files(review_mode)

    if not files:

        line()

        if review_mode == "all":
            print("No supported files were found.")
        else:
            print("No modified supported files found.")
            print("Repository is already up to date.")

        elapsed = time.time() - start_time

        stats = ReviewStatistics(
            review_mode=review_mode,
            files_discovered=0,
            files_reviewed=reviewed,
            files_changed=changed,
            files_skipped=skipped,
            files_failed=failed,
            execution_time=elapsed,
        )

        report_path = generate_review_report(
            stats=stats,
            modified_files=changed_files,
            skipped_files=skipped_files,
            failed_files=failed_files,
            commit_title=commit_title,
            commit_body=commit_body,
            changelog_files=changelog_files,
        )

        print(f"AI review report saved to: {report_path}")

        dashboard_path = generate_dashboard(
            stats=stats,
            review_mode=review_mode,
            modified_files=changed_files,
            report_path=report_path,
        )

        print(f"AI repository dashboard saved to: {dashboard_path}")

        html_dashboard_path = generate_html_dashboard(
            commit_title=commit_title,
            commit_body=commit_body,
        )

        print(f"HTML dashboard saved to: {html_dashboard_path}")

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
            skipped_files.append(str(file))
            continue

        reviewed += 1

        # Skip unchanged files during full repository review.
        if (
            review_mode == "all"
            and not cache.needs_review(
                str(file),
                original,
            )
        ):
            skipped += 1

            skipped_files.append(str(file))

            print("✓ Unchanged (cached)")

            continue

        try:

            changed_functions = None

            if Path(file).suffix.lower() == ".py":
                base_content = read_head_version(Path(file))

                if base_content is not None:
                    try:
                        changed_functions = compare_functions(
                            base_content,
                            original,
                        )

                    except SyntaxError:
                        print(
                            "Python AST parse failed; falling back "
                            "to whole-file review."
                        )

                    if changed_functions == []:
                        skipped += 1
                        skipped_files.append(str(file))
                        cache.update(
                            str(file),
                            original,
                        )

                        print(
                            "✓ No changed Python functions; "
                            "Gemini review skipped"
                        )

                        continue

            backup_file(Path(file))

            if changed_functions:
                updated_functions = {}

                for function in changed_functions:
                    updated_functions[function.qualname] = client.review_file(
                        filename=f"{file}::{function.qualname}",
                        content=function.source,
                    )

                updated = merge_updated_functions(
                    original,
                    changed_functions,
                    updated_functions,
                )

            else:
                updated = client.review_file(
                    filename=str(file),
                    content=original,
                )

            if not updated:

                print("No response from Gemini.")

                restore_backup(Path(file))

                failed += 1
                failed_files[str(file)] = "No response from Gemini."

                continue

            if file_changed(original, updated):

                save_file(
                    Path(file),
                    updated,
                )

                delete_backup(Path(file))

                cache.update(
                    str(file),
                    updated,
                )

                changed += 1

                changed_files.append(str(file))

                print("✓ File updated")

            else:

                delete_backup(Path(file))

                cache.update(
                    str(file),
                    updated,
                )

                skipped += 1
                skipped_files.append(str(file))

                print("✓ No changes needed")

            # Reduce Gemini free-tier rate limits.
            time.sleep(REVIEW_DELAY)

        except Exception as e:

            print(f"✗ Error reviewing {file}")
            print(e)

            try:
                restore_backup(Path(file))
            except Exception:
                pass

            failed += 1
            failed_files[str(file)] = str(e)

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

        commit_title = title
        commit_body = body

        print("Updating AI_CHANGELOG.md...")

        update_changelog(
            changed_files,
            title,
        )
        changelog_files = changed_files.copy()

        print("Creating Git commit...")

        committed = git.commit()

        if committed:

            print("Pushing to GitHub...")

            pushed = git.push()

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

    # Save the review cache for future runs.
    cache.save()

    elapsed = time.time() - start_time

    stats = ReviewStatistics(
        review_mode=review_mode,
        files_discovered=len(files),
        files_reviewed=reviewed,
        files_changed=changed,
        files_skipped=skipped,
        files_failed=failed,
        execution_time=elapsed,
    )

    print()

    print_report(stats)

    report_path = generate_review_report(
        stats=stats,
        modified_files=changed_files,
        skipped_files=skipped_files,
        failed_files=failed_files,
        commit_title=commit_title,
        commit_body=commit_body,
        changelog_files=changelog_files,
    )

    print(f"AI review report saved to: {report_path}")

    dashboard_path = generate_dashboard(
        stats=stats,
        review_mode=review_mode,
        modified_files=changed_files,
        report_path=report_path,
    )

    print(f"AI repository dashboard saved to: {dashboard_path}")

    html_dashboard_path = generate_html_dashboard(
        commit_title=commit_title,
        commit_body=commit_body,
    )

    print(f"HTML dashboard saved to: {html_dashboard_path}")

    line()
    print("Daily AI Review Finished")
    line()


if __name__ == "__main__":
    main()