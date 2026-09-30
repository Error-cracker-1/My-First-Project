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
import json
from pathlib import Path

# Add local lib folder to sys.path to ensure dependencies are found
LIB_DIR = Path(__file__).parent.parent / "lib"
if LIB_DIR.exists():
    sys.path.insert(0, str(LIB_DIR))

from .cache import ReviewCache
from .config import REVIEW_DELAY, STATE_FILE_PATH
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
    GIT_FAILED,
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


def update_state_progress(completed_files: int, total_files: int) -> None:
    """Updates the state file with the current progress of the review."""
    try:
        from .config import STATE_FILE_PATH
        path = Path(STATE_FILE_PATH)
        state = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                pass
        
        percentage = int((completed_files / total_files) * 100) if total_files > 0 else 100
        state["progress"] = {
            "completed": completed_files,
            "total": total_files,
            "percentage": percentage
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, default=str)
    except Exception:
        pass


def get_model_from_state() -> str | None:
    """Reads the current model from the state file."""
    try:
        if Path(STATE_FILE_PATH).exists():
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("model")
    except Exception:
        pass
    return None


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

    model = get_model_from_state()
    if model:
        print(f"Using model: {model}")
        client = GeminiClient(model=model)
    else:
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
    file_change_details = []

    files = get_git_tracked_files(review_mode)


    if not files:
        update_state_progress(0, 0)

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
            file_change_details=file_change_details,
        )

        print(f"AI review report saved to: {report_path}")

        dashboard_path = generate_dashboard(
            stats=stats,
            review_mode=review_mode,
            modified_files=changed_files,
            report_path=report_path,
            file_change_details=file_change_details,
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
    total_files = len(files)
    update_state_progress(0, total_files)

    for idx, file in enumerate(files):

        print()
        print("-" * 60)
        print(f"Reviewing: {file}")
        print("-" * 60)

        original = read_file(file)

        if original is None:
            skipped += 1
            skipped_files.append(str(file))
            update_state_progress(idx + 1, total_files)
            continue

        reviewed += 1

        # Skip unchanged files during full repository review, or when git fails.
        if (
            (review_mode == "all" or GIT_FAILED)
            and not cache.needs_review(
                str(file),
                original,
            )
        ):
            skipped += 1

            skipped_files.append(str(file))

            print("✓ Unchanged (cached)")

            update_state_progress(idx + 1, total_files)
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

                        update_state_progress(idx + 1, total_files)
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

                update_state_progress(idx + 1, total_files)
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

        update_state_progress(idx + 1, total_files)
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

        print("Generating detailed file change explanations (Which, What, Why)...")
        file_change_details = client.generate_file_change_explanations(changed_files)

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
        file_change_details=file_change_details,
    )

    print(f"AI review report saved to: {report_path}")

    dashboard_path = generate_dashboard(
        stats=stats,
        review_mode=review_mode,
        modified_files=changed_files,
        report_path=report_path,
        file_change_details=file_change_details,
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