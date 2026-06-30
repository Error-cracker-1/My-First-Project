"""
Git commit manager for the Daily AI Review project.
"""

import subprocess

from scripts.gemini_client import GeminiClient


class GitCommitManager:
    """
    Handles Git operations for the AI review workflow.
    """

    def __init__(self):
        self.client = GeminiClient()

    def _run(self, command: list[str]) -> subprocess.CompletedProcess:
        """
        Execute a Git command.
        """

        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

    def current_branch(self) -> str:
        """
        Return the current Git branch.
        """

        result = self._run(
            ["git", "branch", "--show-current"]
        )

        return result.stdout.strip()

    def has_changes(self) -> bool:
        """
        Return True if the repository contains changes.
        """

        result = self._run(
            ["git", "status", "--porcelain"]
        )

        return bool(result.stdout.strip())

    def changed_files(self) -> list[str]:
        """
        Return a list of modified files.
        """

        result = self._run(
            ["git", "diff", "--name-only"]
        )

        return [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

    def commit(self) -> bool:
        """
        Create an AI-generated Git commit.
        """

        if not self.has_changes():
            print("No repository changes detected.")
            return False

        files = self.changed_files()

        if not files:
            print("No tracked files changed.")
            return False

        print()
        print("=" * 60)
        print("Files to commit")
        print("=" * 60)

        for file in files:
            print(f"• {file}")

        print()

        title, body = self.client.generate_commit_message(files)

        try:

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
            print(f"Title : {title}")
            print()
            print(body)
            print("=" * 60)
            print()

            return True

        except subprocess.CalledProcessError as e:

            print()
            print("=" * 60)
            print("Git commit failed.")
            print("=" * 60)

            if e.stderr:
                print(e.stderr)

            print()

            return False

    def push(self, branch: str = "feature-1") -> bool:
        """
        Push commits to GitHub.
        """

        current = self.current_branch()

        if current != branch:
            print(
                f"Current branch is '{current}', expected '{branch}'."
            )
            return False

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
            print("Push completed successfully.")
            print(f"Branch : {branch}")
            print("=" * 60)
            print()

            return True

        except subprocess.CalledProcessError as e:

            print()
            print("=" * 60)
            print("Git push failed.")
            print("=" * 60)

            if e.stderr:
                print(e.stderr)

            print()

            return False