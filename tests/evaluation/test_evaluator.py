
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from tests.evaluation import run_evaluation
from backend.app.models.code import (
    CodeAnalysisResponse,
    CodeIssue,
)


class TestEvaluator(unittest.TestCase):

    def setUp(self):
        self.case = SimpleNamespace(
            name="Undefined variable",
            language="python",
            code="print(x)",
            expected_issue_type="Runtime Error",
            expected_keywords=["NameError", "x", "defined"],
        )

        self.good_response = CodeAnalysisResponse(
            summary="The code references an undefined variable.",
            issues=[
                CodeIssue(
                    type="Runtime Error",
                    severity="High",
                    explanation=(
                        "Variable x is not defined, "
                        "which causes a NameError."
                    ),
                )
            ],
            suggestions=["Define x before using it."],
        )

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_correct_analysis_passes(self, mock_chain):
        mock_chain.invoke.return_value = self.good_response

        result = run_evaluation.evaluate_case(self.case)

        self.assertTrue(result["passed"])
        self.assertTrue(result["type_found"])
        self.assertTrue(result["keyword_found"])
        self.assertTrue(result["explanation_found"])
        self.assertTrue(result["suggestions_found"])
        mock_chain.invoke.assert_called_once()

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_wrong_issue_type_fails(self, mock_chain):
        wrong_response = CodeAnalysisResponse(
            summary="The code has a syntax problem.",
            issues=[
                CodeIssue(
                    type="Syntax Error",
                    severity="High",
                    explanation="The code cannot be parsed.",
                )
            ],
            suggestions=["Check the syntax."],
        )

        mock_chain.invoke.return_value = wrong_response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["type_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_missing_suggestions_fails(self, mock_chain):
        response_without_suggestions = CodeAnalysisResponse(
            summary="An undefined variable is referenced.",
            issues=[
                CodeIssue(
                    type="Runtime Error",
                    severity="High",
                    explanation="Variable x is undefined.",
                )
            ],
            suggestions=[],
        )

        mock_chain.invoke.return_value = response_without_suggestions

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["suggestions_found"])
        
        
    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_missing_issues_fails(self, mock_chain):
        response = CodeAnalysisResponse(
            summary="No issues were identified.",
            issues=[],
            suggestions=["Review the code manually."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["issues_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_insufficient_keywords_fails(self, mock_chain):
        response = CodeAnalysisResponse(
            summary="There may be a problem.",
            issues=[
                CodeIssue(
                    type="Runtime Error",
                    severity="High",
                    explanation="Variable x has a problem.",
                )
            ],
            suggestions=["Check the variable."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["keyword_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_empty_explanation_fails(self, mock_chain):
        response = CodeAnalysisResponse(
            summary="An undefined variable was detected.",
            issues=[
                CodeIssue(
                    type="Runtime Error",
                    severity="High",
                    explanation="   ",
                )
            ],
            suggestions=["Define x before using it."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["explanation_found"])


if __name__ == "__main__":
    unittest.main()
