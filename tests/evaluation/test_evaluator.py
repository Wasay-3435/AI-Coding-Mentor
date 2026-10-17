
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests.evaluation import run_evaluation
from tests.evaluation.code_analysis_cases import EVALUATION_CASES


class TestEvaluator(unittest.TestCase):

    def setUp(self):
        self.case = SimpleNamespace(
            name="Undefined variable",
            language="python",
            code="print(x)",
            expected_issue_type="Runtime Error",
            expected_keywords=["x", "NameError"],
            expected_behavior=(
                "Identify that x is referenced before it has been defined."
            ),
        )

        self.good_response = SimpleNamespace(
            summary="Variable x is not defined, causing a NameError.",
            issues=[
                SimpleNamespace(
                    type="Runtime Error",
                    severity="High",
                    explanation=(
                        "The variable x is used before it has been defined."
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
        self.assertTrue(result["issues_found"])
        self.assertTrue(result["type_found"])
        self.assertTrue(result["keyword_found"])
        self.assertTrue(result["diagnostic_found"])
        self.assertTrue(result["explanation_found"])
        self.assertTrue(result["suggestions_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_wrong_issue_type_fails(self, mock_chain):
        response = SimpleNamespace(
            summary=self.good_response.summary,
            issues=[
                SimpleNamespace(
                    type="Syntax Error",
                    severity="High",
                    explanation=(
                        "Variable x is undefined, causing a NameError."
                    ),
                )
            ],
            suggestions=["Define x first."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["type_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_missing_suggestions_fails(self, mock_chain):
        response = SimpleNamespace(
            summary=self.good_response.summary,
            issues=self.good_response.issues,
            suggestions=[],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["suggestions_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_missing_issues_fails(self, mock_chain):
        response = SimpleNamespace(
            summary=self.good_response.summary,
            issues=[],
            suggestions=["Define x first."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["issues_found"])
        self.assertFalse(result["type_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_insufficient_keywords_fails(self, mock_chain):
        response = SimpleNamespace(
            summary="A variable is used.",
            issues=[
                SimpleNamespace(
                    type="Runtime Error",
                    severity="High",
                    explanation="The variable is used before definition.",
                )
            ],
            suggestions=["Define the variable first."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["keyword_found"])

    @patch("tests.evaluation.run_evaluation.code_analysis_chain")
    def test_empty_explanation_fails(self, mock_chain):
        response = SimpleNamespace(
            summary=self.good_response.summary,
            issues=[
                SimpleNamespace(
                    type="Runtime Error",
                    severity="High",
                    explanation="   ",
                )
            ],
            suggestions=["Define x first."],
        )
        mock_chain.invoke.return_value = response

        result = run_evaluation.evaluate_case(self.case)

        self.assertFalse(result["passed"])
        self.assertFalse(result["explanation_found"])

    def test_undefined_variable_diagnostic(self):
        result = run_evaluation.diagnostic_content_check(
            self.case,
            "Variable x is not defined, causing a NameError.",
        )

        self.assertTrue(result["passed"])

    def test_list_index_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "List index out of range"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "Index 5 is outside the valid range for this list, "
            "causing IndexError.",
        )

        self.assertTrue(result["passed"])

    def test_list_index_diagnostic_rejects_missing_index(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "List index out of range"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "The list access causes an IndexError because "
            "the index is invalid.",
        )

        self.assertFalse(result["passed"])
