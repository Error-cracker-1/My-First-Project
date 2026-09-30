"""
Git commit manager for the Daily AI Review project.
"""

import subprocess

from .config import TARGET_BRANCH
from .gemini_client import GeminiClient


class GitCommitManager:
    """
    Handles Git commit and push operations.
    """

    def __init__(self):
        self.client = GeminiClient()

    def has_changes(self) -> bool:
        """
        Return True if the repository contains changes.
        """

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )

            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Warning: Failed to check git changes ({e}). Assuming no changes.")
            return False

    def changed_files(self) -> list[str]:
        """
        Return a list of changed tracked files.
        """

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )

            return [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]
        except Exception as e:
            print(f"Warning: Failed to get git changed files ({e}). Returning empty list.")
            return []

    def commit(self) -> bool:
        """
        Create an AI-generated Git commit.
        """

        try:
            if not self.has_changes():
                print("No changes detected.")
                return False

            files = self.changed_files()

            if not files:
                print("No tracked files changed.")
                return False

            title, body = self.client.generate_commit_message(files)

            subprocess.run(
                ["git", "add", "."],
                check=True,
            )

            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    title,
                    "-m",
                    body,
                ],
                check=True,
            )

            print()
            print("=" * 60)
            print("Commit created successfully.")
            print("=" * 60)
            print()

            return True

        except Exception as e:
            print()
            print("=" * 60)
            print(f"Failed to create commit: {e}")
            print("=" * 60)
            print()

            return False

    def push(
        self,
        branch: str | None = None,
    ) -> bool:
        """
        Push commits to GitHub.
        """

        if branch is None:
            branch = TARGET_BRANCH

        try:
            subprocess.run(
                [
                    "git",
                    "push",
                    "origin",
                    branch,
                ],
                check=True,
            )

            print()
            print("=" * 60)
            print(f"Pushed successfully to {branch}.")
            print("=" * 60)
            print()

            return True

        except Exception as e:
            print()
            print("=" * 60)
            print(f"Failed to push changes: {e}")
            print("=" * 60)
            print()

            return False