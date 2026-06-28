"""
Git commit manager for the Daily AI Review project.
"""

import subprocess

from scripts.gemini_client import GeminiClient


class GitCommitManager:
    def __init__(self):
        self.client = GeminiClient()

    def has_changes(self) -> bool:
        """
        Return True if tracked files have changed.
        """
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )

        return bool(result.stdout.strip())

    def changed_files(self) -> list[str]:
        """
        Return a list of modified tracked files.
        """
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

    def commit(self) -> bool:
        """
        Create a commit if changes exist.
        """

        if not self.has_changes():
            print("No changes detected.")
            return False

        files = self.changed_files()

        if not files:
            print("No tracked files changed.")
            return False

        title, body = self.client.generate_commit_message(files)

        subprocess.run(
            ["git", "add", "-u"],
            check=True,
        )

        try:
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

            print("Commit created successfully.")
            return True

        except subprocess.CalledProcessError:
            print("Git could not create a commit.")
            return False

    def push(self, branch: str = "feature-1") -> bool:
        """
        Push to the specified branch.
        """

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

            print(f"Pushed to {branch}.")
            return True

        except subprocess.CalledProcessError:
            print("Failed to push changes.")
            return False