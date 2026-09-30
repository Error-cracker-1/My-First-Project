"""
Repository report utilities for the Daily AI Review project.
"""

from dataclasses import dataclass


@dataclass
class ReviewStatistics:
    review_mode: str
    files_discovered: int
    files_reviewed: int
    files_changed: int
    files_skipped: int
    files_failed: int
    execution_time: float


def calculate_repository_health(
    changed: int,
    failed: int,
) -> int:
    """
    Calculate a simple repository health score.

    Starts at 100.

    -2 points per modified file.
    -5 points per failed file.

    Minimum score is 0.
    """

    score = 100

    score -= changed * 2
    score -= failed * 5

    return max(score, 0)


def print_report(stats: ReviewStatistics):
    """
    Print the final AI Repository Report.
    """

    health = calculate_repository_health(
        stats.files_changed,
        stats.files_failed,
    )

    print()
    print("=" * 60)
    print("🤖 AI Repository Report")
    print("=" * 60)

    print(f"Review Mode       : {stats.review_mode}")
    print(f"Files Discovered  : {stats.files_discovered}")
    print(f"Files Reviewed    : {stats.files_reviewed}")
    print(f"Files Changed     : {stats.files_changed}")
    print(f"Files Skipped     : {stats.files_skipped}")
    print(f"Files Failed      : {stats.files_failed}")
    print(f"Repository Health : {health}/100")

    print()
    print("Summary")
    print("-" * 60)

    if stats.files_failed == 0:
        print("✓ No review failures detected.")
    else:
        print(
            f"⚠ {stats.files_failed} file(s) failed during review."
        )

    if stats.files_changed == 0:
        print("✓ Repository is already optimized.")
    else:
        print(
            f"✓ AI improved {stats.files_changed} file(s)."
        )

    if health >= 95:
        print("✓ Repository is in excellent condition.")
    elif health >= 80:
        print("✓ Repository is in good condition.")
    elif health >= 60:
        print("⚠ Repository needs attention.")
    else:
        print("✗ Repository health is poor.")

    print()
    print(
        f"Execution Time    : {stats.execution_time:.2f} seconds"
    )

    print("=" * 60)