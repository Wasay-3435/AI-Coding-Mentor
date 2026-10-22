
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests.evaluation import run_evaluation
from tests.evaluation.code_analysis_cases import EVALUATION_CASES


class TestEvaluator(unittest.TestCase):
    """Unit tests for the AI code-analysis evaluator."""

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

    def test_syntax_error_accepts_missing_colon_without_runtime_claim(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Syntax error"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "Syntax error: the if condition is missing a colon.",
        )

        self.assertTrue(result["passed"])
        self.assertTrue(result["checks"]["identifies_missing_colon"])
        self.assertTrue(
            result["checks"]["does_not_claim_undefined_x_runtime_error"]
        )

    def test_syntax_error_rejects_unsupported_undefined_variable_claim(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Syntax error"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The if condition is missing a colon. "
                "The syntax error prevents execution. "
                "The program also raises a NameError because x is undefined."
            ),
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["checks"]["identifies_missing_colon"])
        self.assertFalse(
            result["checks"]["does_not_claim_undefined_x_runtime_error"]
        )

    def test_list_index_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "List index out of range"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "Index 5 is outside the valid range for this list, "
                "causing IndexError."
            ),
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
            (
                "The list access causes an IndexError because "
                "the index is invalid."
            ),
        )

        self.assertFalse(result["passed"])

    def test_type_mismatch_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Type mismatch"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "TypeError: cannot add a string and an integer.",
        )

        self.assertTrue(result["passed"])

    def test_missing_function_argument_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Missing function argument"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "TypeError: the required name argument is missing.",
        )

        self.assertTrue(result["passed"])

    def test_empty_list_access_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Empty list access"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "The list is empty, so index 0 raises IndexError.",
        )

        self.assertTrue(result["passed"])

    def test_missing_return_statement_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Missing return statement"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The function has no return statement and therefore "
                "returns None."
            ),
        )

        self.assertTrue(result["passed"])

    def test_invalid_integer_conversion_diagnostic(self):
        case = next(
            item
            for item in EVALUATION_CASES
            if item.name == "Invalid integer conversion"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                'ValueError: "hello" is not a valid integer '
                "for int() conversion."
            ),
        )

        self.assertTrue(result["passed"])


    def test_off_by_one_loop_diagnostic(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Off-by-one loop"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "range(1, 10) excludes 10. "
                "Use range(1, 11) to include 10."
            ),
        )

        self.assertTrue(result["passed"])

    def test_off_by_one_loop_rejects_missing_correction(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Off-by-one loop"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "range excludes 10 from the output.",
        )

        self.assertFalse(result["passed"])

    def test_incorrect_comparison_diagnostic(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Incorrect comparison"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The comparison age > 18 excludes people aged exactly 18. "
                "Use age >= 18 to include them."
            ),
        )

        self.assertTrue(result["passed"])

    def test_incorrect_comparison_rejects_missing_correction(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Incorrect comparison"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "The comparison age > 18 excludes people aged exactly 18.",
        )

        self.assertFalse(result["passed"])

    def test_mutable_default_argument_diagnostic(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Mutable default argument"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The mutable default argument uses the same list across "
                "calls. Use None as the default and create a new list "
                "inside the function."
            ),
        )

        self.assertTrue(result["passed"])

    def test_mutable_default_argument_rejects_missing_fix(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Mutable default argument"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The mutable default argument shares the same list "
                "across calls."
            ),
        )

        self.assertFalse(result["passed"])

    def test_unreachable_code_diagnostic(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Unreachable code"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            (
                "The print statement is unreachable because the return "
                "statement executes before it."
            ),
        )

        self.assertTrue(result["passed"])

    def test_unreachable_code_rejects_missing_return_connection(self):
        case = next(
            item for item in EVALUATION_CASES
            if item.name == "Unreachable code"
        )

        result = run_evaluation.diagnostic_content_check(
            case,
            "The print statement is unreachable.",
        )

        self.assertFalse(result["passed"])

if __name__ == "__main__":
    unittest.main()
