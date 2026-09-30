"""
Repository dashboard generation for the Daily AI Review project.
"""

from datetime import datetime
import json
from pathlib import Path
import subprocess
from typing import Any


from .cache import CACHE_FILE
from .config import (
    BACKUP_EXTENSION,
    EXCLUDED_DIRECTORIES,
    EXCLUDED_FILES,
    MODEL as FALLBACK_MODEL,
    SUPPORTED_EXTENSIONS,
)
from .report import ReviewStatistics

DASHBOARD_PATH = Path("AI_REPORT.md")
DASHBOARD_STATE_PATH = Path(".cache") / "dashboard_stats.json"
REPORTS_DIR = Path("reports")
GENERATED_BY = "Daily AI Review"


def _run_git_command(command: list[str]) -> str | None:
    """
    Run a Git command and return stripped stdout when available.
    """

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

    except Exception:
        return None

    output = result.stdout.strip()

    return output or None


def _repository_name() -> str:
    """
    Return the repository name from Git metadata when possible.
    """

    root = _run_git_command(
        [
            "git",
            "rev-parse",
            "--show-toplevel",
        ]
    )

    if root:
        return Path(root).name

    return Path.cwd().name


def _current_branch() -> str:
    """
    Return the current Git branch name when possible.
    """

    branch = _run_git_command(
        [
            "git",
            "branch",
            "--show-current",
        ]
    )

    return branch or "Unknown"


def _gemini_model() -> str:
    """
    Return the Gemini model configured for review generation.
    """

    try:
        from .gemini_client import MODEL

        return MODEL

    except Exception:
        return FALLBACK_MODEL


def _tracked_files() -> list[Path]:
    """
    Return all files currently tracked by Git.
    """

    output = _run_git_command(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            "HEAD",
        ]
    )

    if not output:
        return []

    return [
        Path(line.strip())
        for line in output.splitlines()
        if line.strip()
    ]


def _is_supported(path: Path) -> bool:
    """
    Return True when a tracked path matches reviewable file rules.
    """

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    if path.name in EXCLUDED_FILES:
        return False

    if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
        return False

    return True


def _load_dashboard_state() -> dict[str, float | list[str]]:
    """
    Load persisted dashboard totals from disk.
    """

    if not DASHBOARD_STATE_PATH.exists():
        return {}

    try:
        return json.loads(
            DASHBOARD_STATE_PATH.read_text(
                encoding="utf-8",
            )
        )

    except Exception:
        return {}


def _save_dashboard_state(state: dict[str, float | list[str]]) -> None:
    """
    Persist dashboard totals for future review runs.
    """

    DASHBOARD_STATE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DASHBOARD_STATE_PATH.write_text(
        json.dumps(
            state,
            indent=4,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _update_dashboard_state(
    stats: ReviewStatistics,
    modified_files: list[str],
    file_change_details: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Add the current review statistics to persisted dashboard totals.
    """

    state = _load_dashboard_state()

    total_reviews = int(state.get("total_reviews_completed", 0)) + 1
    total_files_reviewed = int(state.get("total_files_reviewed", 0))
    total_files_modified = int(state.get("total_files_modified", 0))
    total_execution_time = float(state.get("total_execution_time", 0.0))
    recent_modified_files = list(
        state.get("recent_modified_files", [])
    )
    recent_file_changes = list(
        state.get("recent_file_changes", [])
    )

    total_files_reviewed += stats.files_reviewed
    total_files_modified += stats.files_changed
    total_execution_time += stats.execution_time
    recent_modified_files.extend(modified_files)

    if file_change_details:
        recent_file_changes = (recent_file_changes + file_change_details)[-10:]

    state = {
        "total_reviews_completed": total_reviews,
        "total_files_reviewed": total_files_reviewed,
        "total_files_modified": total_files_modified,
        "total_execution_time": total_execution_time,
        "average_execution_time": total_execution_time / total_reviews,
        "recent_modified_files": recent_modified_files[-10:],
        "recent_file_changes": recent_file_changes,
    }

    _save_dashboard_state(state)

    return state


def _format_detailed_changes(file_changes: list[dict[str, str]] | None) -> list[str]:
    """
    Format detailed file changes for Markdown dashboard display.
    """
    if not file_changes:
        return ["- None"]

    lines = []
    for fc in file_changes:
        f_path = fc.get("file", "Unknown file")
        f_what = fc.get("what", "Code modifications applied")
        f_why = fc.get("why", "Improve quality and maintainability")
        lines.append(f"- **`{f_path}`**")
        lines.append(f"  - **What Changed**: {f_what}")
        lines.append(f"  - **Why Changed**: {f_why}")
    return lines


def _recent_modified_files(state: dict[str, Any]) -> list[str]:
    """
    Return the persisted most recent modified files for dashboard display.
    """

    files = state.get("recent_modified_files", [])

    if not files:
        return ["- None"]

    return [f"- {file}" for file in files[-10:]]



def _display_report_path(report: Path) -> str:
    """
    Return a dashboard-friendly report path.
    """

    try:
        return report.relative_to(Path.cwd()).as_posix()

    except ValueError:
        if report.parent.name == REPORTS_DIR.name:
            return (
                Path(REPORTS_DIR.name) / report.name
            ).as_posix()

        return report.as_posix()


def _recent_reports(current_report: Path | None) -> list[str]:
    """
    Return the last 10 generated Markdown reports as Markdown links.
    """

    reports = sorted(
        REPORTS_DIR.glob("*_review.md"),
        reverse=True,
    )

    if current_report and current_report not in reports:
        reports.insert(0, current_report)

    if not reports:
        return ["- None"]

    links = []

    for report in reports[:10]:
        display_path = _display_report_path(report)
        links.append(f"- [{display_path}]({display_path})")

    return links


def generate_dashboard(
    stats: ReviewStatistics,
    review_mode: str,
    modified_files: list[str],
    report_path: Path | None = None,
    file_change_details: list[dict[str, str]] | None = None,
) -> Path:
    """
    Generate or overwrite the root AI repository dashboard.

    Dashboard totals are persisted between runs in a small JSON state file.
    """

    now = datetime.now()
    tracked_files = _tracked_files()
    supported_files = [
        path
        for path in tracked_files
        if _is_supported(path)
    ]
    state = _update_dashboard_state(
        stats=stats,
        modified_files=modified_files,
        file_change_details=file_change_details,
    )

    lines = [
        "# AI Repository Dashboard",
        "",
        "## Repository Information",
        "",
        f"- Repository name: {_repository_name()}",
        f"- Current branch: {_current_branch()}",
        f"- Last review date: {now.strftime('%Y-%m-%d')}",
        f"- Last review time: {now.strftime('%H:%M:%S')}",
        f"- Gemini model: {_gemini_model()}",
        "",
        "## Repository Statistics",
        "",
        f"- Total tracked files: {len(tracked_files)}",
        f"- Supported files: {len(supported_files)}",
        f"- Files reviewed: {stats.files_reviewed}",
        f"- Files changed: {stats.files_changed}",
        f"- Files skipped: {stats.files_skipped}",
        f"- Files failed: {stats.files_failed}",
        "",
        "## Review Statistics",
        "",
        f"- Total reviews completed: {state['total_reviews_completed']}",
        f"- Total files reviewed: {state['total_files_reviewed']}",
        f"- Total files modified: {state['total_files_modified']}",
        f"- Total execution time: {state['total_execution_time']:.2f} seconds",
        f"- Average execution time: {state['average_execution_time']:.2f} seconds",
        "",
        "## Repository Health",
        "",
        "- Overall Score: Pending",
        "- Documentation: Pending",
        "- Code Quality: Pending",
        "- Maintainability: Pending",
        "- Architecture: Pending",
        "- Naming: Pending",
        "",
        "## Recent Modified Files",
        "",
        *_recent_modified_files(state),
        "",
        "## Detailed File Changes",
        "",
        *_format_detailed_changes(state.get("recent_file_changes") or file_change_details),
        "",
        "## Recent Reports",

        "",
        *_recent_reports(report_path),
        "",
        "## Current Configuration",
        "",
        f"- Review mode: {review_mode}",
        f"- Cache enabled: {CACHE_FILE.parent.exists()}",
        "- PromptManager enabled: True",
        f"- Automatic backups enabled: {bool(BACKUP_EXTENSION)}",
        "- AI changelog enabled: True",
        "",
        "## Next Planned Features",
        "",
        "- Repository Health Score",
        "- HTML Dashboard",
        "- Web Interface",
        "- Pull Request Review",
        "- Function-level Review",
        "",
    ]

    DASHBOARD_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return DASHBOARD_PATH
