"""Unit tests for the v2.4 code-analysis input contract."""
import unittest

from code_analysis import (
    CodeAnalysisInputError,
    build_analysis_prompt,
    detect_analysis_language,
)


class CodeAnalysisTests(unittest.TestCase):
    def test_detects_language_from_extension(self):
        self.assertEqual(detect_analysis_language("sample.py"), "Python")
        self.assertEqual(detect_analysis_language("app.ts"), "TypeScript")

    def test_accepts_explicit_supported_language(self):
        self.assertEqual(
            detect_analysis_language("snippet.src", "Python"),
            "Python",
        )

    def test_rejects_unsupported_extension(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("print('hi')", "sample.exe")

    def test_rejects_unsupported_explicit_language(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("some code", "snippet.src", "made-up-language")

    def test_rejects_non_text_language(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("some code", "snippet.src", ["Python"])

    def test_rejects_empty_source(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("  ")

    def test_rejects_non_text_source(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt(None)  # type: ignore[arg-type]

    def test_rejects_oversized_source(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("x" * 120_001)

    def test_prompt_preserves_source_and_traceability(self):
        source = "def add(a, b):\n    return a + b"
        prompt = build_analysis_prompt(source, "math.py")
        self.assertIn(source, prompt)
        self.assertIn("line number", prompt.lower())
        self.assertIn("confidence", prompt.lower())
        self.assertIn("Language: Python", prompt)

    def test_requires_filename(self):
        with self.assertRaises(CodeAnalysisInputError):
            build_analysis_prompt("some code", "  ")


if __name__ == "__main__":
    unittest.main()
