"""
Markdown report generation for the Daily AI Review project.
"""

from datetime import datetime
from pathlib import Path
import subprocess

from .config import MODEL as FALLBACK_MODEL
from .report import ReviewStatistics

REPORTS_DIR = Path("reports")
GENERATED_BY = "Daily AI Review"


def _gemini_model() -> str:
    """
    Return the Gemini model configured for review generation.
    """

    try:
        from .gemini_client import MODEL

        return MODEL

    except Exception:
        return FALLBACK_MODEL


def _format_file_list(files: list[str]) -> list[str]:
    """
    Format a file list for Markdown output.
    """

    if not files:
        return ["- None"]

    return [f"- {file}" for file in files]


def _format_failed_files(failed_files: dict[str, str]) -> list[str]:
    """
    Format failed files with their error messages for Markdown output.
    """

    if not failed_files:
        return ["- None"]

    return [
        f"- {file}: {error}"
        for file, error in failed_files.items()
    ]


def _success_rate(stats: ReviewStatistics) -> float:
    """
    Calculate the percentage of reviewed files without failures.
    """

    if stats.files_reviewed == 0:
        return 100.0

    successful = stats.files_reviewed - stats.files_failed

    return max(successful, 0) / stats.files_reviewed * 100


def _run_git_command(command: list[str]) -> str | None:
    """
    Run a Git command and return its output when available.
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


def _fallback_recommendations(stats: ReviewStatistics) -> list[str]:
    """
    Build simple next-step recommendations when Gemini is unavailable.
    """

    recommendations = [
        "- Improve documentation for frequently changed areas.",
        "- Add type hints or stronger validation where appropriate.",
        "- Remove duplicated code discovered during future reviews.",
        "- Increase automated test coverage for reviewed files.",
    ]

    if stats.files_failed > 0:
        recommendations.append(
            "- Investigate failed reviews and address the reported errors."
        )

    return recommendations[:5]


def _recommendation_prompt(
    stats: ReviewStatistics,
    modified_files: list[str],
    skipped_files: list[str],
    failed_files: dict[str, str],
) -> str:
    """
    Build the prompt used to request repository-specific recommendations.
    """

    failed_summary = "\n".join(
        f"- {file}: {error}"
        for file, error in failed_files.items()
    ) or "None"

    return f"""
Generate 3 to 5 concise repository-specific recommendations for an AI code review report.

Use these review details:

Review mode: {stats.review_mode}
Files discovered: {stats.files_discovered}
Files reviewed: {stats.files_reviewed}
Files changed: {stats.files_changed}
Files skipped: {stats.files_skipped}
Files failed: {stats.files_failed}
Success rate: {_success_rate(stats):.2f}%
Modified files: {', '.join(modified_files) or 'None'}
Skipped files: {', '.join(skipped_files) or 'None'}
Failed files:
{failed_summary}

Return only a Markdown bullet list.
Do not include headings or explanations.
""".strip()


def _parse_recommendations(text: str) -> list[str]:
    """
    Normalize Gemini recommendation text into 3-5 Markdown bullets.
    """

    recommendations = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(("- ", "* ")):
            recommendations.append("- " + line[2:].strip())
        elif line[0].isdigit() and "." in line[:4]:
            recommendations.append(
                "- " + line.split(
                    ".",
                    1,
                )[1].strip()
            )

    return recommendations[:5]


def _next_recommendations(
    stats: ReviewStatistics,
    modified_files: list[str],
    skipped_files: list[str],
    failed_files: dict[str, str],
) -> list[str]:
    """
    Generate repository-specific recommendations with a safe fallback.
    """

    try:
        from .gemini_client import GeminiClient

        client = GeminiClient()
        response = client._generate(
            _recommendation_prompt(
                stats=stats,
                modified_files=modified_files,
                skipped_files=skipped_files,
                failed_files=failed_files,
            )
        )

        text = getattr(response, "text", None)

        if text:
            recommendations = _parse_recommendations(text)

            if len(recommendations) >= 3:
                return recommendations

    except Exception:
        # Reports must still be generated when Gemini is unavailable.
        pass

    return _fallback_recommendations(stats)


def generate_review_report(
    stats: ReviewStatistics,
    modified_files: list[str],
    skipped_files: list[str],
    failed_files: dict[str, str],
    commit_title: str = "Not generated",
    commit_body: str = "No AI commit was generated.",
    changelog_files: list[str] | None = None,
) -> Path:
    """
    Generate and save a Markdown AI review report.

    The report directory is created automatically and the report filename uses
    the current date and time so each review run has a unique report artifact.
    """

    changelog_files = changelog_files or []

    now = datetime.now()
    report_path = REPORTS_DIR / now.strftime(
        "%Y-%m-%d_%H-%M-%S_review.md"
    )
    success_rate = _success_rate(stats)

    # Ensure report generation works on the first run.
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# AI Review Report",
        "",
        "## Report Metadata",
        "",
        f"- Repository name: {_repository_name()}",
        f"- Current branch: {_current_branch()}",
        f"- Generated by: {GENERATED_BY}",
        f"- Gemini model: {_gemini_model()}",
        "",
        "## Review Information",
        "",
        f"- Date: {now.strftime('%Y-%m-%d')}",
        f"- Time: {now.strftime('%H:%M:%S')}",
        f"- Review Mode: {stats.review_mode}",
        f"- Execution Time: {stats.execution_time:.2f} seconds",
        "",
        "## Repository Summary",
        "",
        f"- Files discovered: {stats.files_discovered}",
        f"- Files reviewed: {stats.files_reviewed}",
        f"- Files changed: {stats.files_changed}",
        f"- Files skipped: {stats.files_skipped}",
        f"- Files failed: {stats.files_failed}",
        f"- Success rate: {success_rate:.2f}%",
        "",
        "## Repository Health",
        "",
        "Overall Score : Pending",
        "",
        "Documentation : Pending",
        "Code Quality : Pending",
        "Maintainability : Pending",
        "Architecture : Pending",
        "Naming : Pending",
        "",
        "## Modified Files",
        "",
        *_format_file_list(modified_files),
        "",
        "## Skipped Files",
        "",
        *_format_file_list(skipped_files),
        "",
        "## Failed Files",
        "",
        *_format_failed_files(failed_files),
        "",
        "## AI Commit",
        "",
        f"- Commit title: {commit_title}",
        "- Commit body:",
        "",
        "```",
        commit_body,
        "```",
        "",
        "## Changelog",
        "",
        "Files added to AI_CHANGELOG.md:",
        "",
        *_format_file_list(changelog_files),
        "",
        "## Next Recommendations",
        "",
        *_next_recommendations(
            stats=stats,
            modified_files=modified_files,
            skipped_files=skipped_files,
            failed_files=failed_files,
        ),
        "",
        "## Review Totals",
        "",
        f"Files Reviewed: {stats.files_reviewed}",
        f"Files Modified: {stats.files_changed}",
        f"Files Skipped: {stats.files_skipped}",
        f"Files Failed: {stats.files_failed}",
        f"Success Rate: {success_rate:.2f}%",
        f"Execution Time: {stats.execution_time:.2f} seconds",
        "",
    ]

    report_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return report_path
