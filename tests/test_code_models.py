
import unittest

from pydantic import ValidationError

from backend.app.models.code import (
    CodeRequest,
    CodeIssue,
    CodeAnalysisResponse,
)


class TestCodeRequest(unittest.TestCase):
    def test_rejects_blank_language(self):
        with self.assertRaises(ValidationError):
            CodeRequest(language="   ", code="print(1)")

    def test_rejects_blank_code(self):
        with self.assertRaises(ValidationError):
            CodeRequest(language="python", code="  ")


class TestCodeIssue(unittest.TestCase):
    def test_rejects_blank_explanation(self):
        with self.assertRaises(ValidationError):
            CodeIssue(
                type="Runtime Error",
                severity="High",
                explanation="   ",
            )


class TestCodeAnalysisResponse(unittest.TestCase):
    def test_rejects_blank_summary(self):
        with self.assertRaises(ValidationError):
            CodeAnalysisResponse(
                summary=" ",
                issues=[],
                suggestions=[],
            )

    def test_rejects_blank_suggestion(self):
        with self.assertRaises(ValidationError):
            CodeAnalysisResponse(
                summary="The code is correct.",
                issues=[],
                suggestions=["  "],
            )

    def test_accepts_valid_response(self):
        response = CodeAnalysisResponse(
            summary="The code prints 2.",
            issues=[],
            suggestions=["Consider adding a test."],
        )

        self.assertEqual(response.summary, "The code prints 2.")
        self.assertEqual(len(response.suggestions), 1)


if __name__ == "__main__":
    unittest.main()
