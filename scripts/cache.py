"""
Review cache for the Daily AI Review project.

Stores SHA-256 hashes of reviewed files so
unchanged files can be skipped.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CACHE_DIR = Path(".cache")
CACHE_FILE = CACHE_DIR / "review_cache.json"


class ReviewCache:
    """
    Stores hashes of reviewed files.
    """

    def __init__(self):

        CACHE_DIR.mkdir(exist_ok=True)

        if CACHE_FILE.exists():
            try:
                self.cache = json.loads(
                    CACHE_FILE.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception:
                self.cache = {}
        else:
            self.cache = {}

    def _hash(self, content: str) -> str:
        """
        Return SHA-256 hash of content.
        """

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def needs_review(
        self,
        filename: str,
        content: str,
    ) -> bool:
        """
        Return True if the file has changed.
        """

        current = self._hash(content)

        previous = self.cache.get(filename)

        return current != previous

    def update(
        self,
        filename: str,
        content: str,
    ) -> None:
        """
        Store latest hash.
        """

        self.cache[filename] = self._hash(content)

    def save(self) -> None:
        """
        Save cache to disk.
        """

        CACHE_FILE.write_text(
            json.dumps(
                self.cache,
                indent=4,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def clear(self) -> None:
        """
        Clear the cache.
        """

        self.cache.clear()

        self.save()