
import json
import tempfile
import unittest
from pathlib import Path

from tests.evaluation.run_evaluation import save_evaluation_report


class TestEvaluationReport(unittest.TestCase):

    def test_report_saves_summary_and_results(self):
        """The report should preserve results and calculate counts."""

        results = [
            {
                "name": "Undefined variable",
                "passed": True,
                "issues_found": True,
                "type_found": True,
                "keyword_found": True,
                "matched_keywords": ["NameError", "defined"],
                "explanation_found": True,
                "suggestions_found": True,
                "summary": "An undefined variable causes a NameError.",
            },
            {
                "name": "Syntax error",
                "passed": False,
                "issues_found": True,
                "type_found": False,
                "keyword_found": True,
                "matched_keywords": ["syntax"],
                "explanation_found": True,
                "suggestions_found": True,
                "summary": "The classification was incorrect.",
            },
        ]

        skipped_cases = [
            {
                "name": "Division by zero",
                "error_type": "GoogleRateLimitError",
                "message": "Quota exceeded",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "latest_report.json"

            save_evaluation_report(
                results=results,
                skipped_cases=skipped_cases,
                errors=[],
                total=3,
                output_path=report_path,
            )

            with report_path.open(encoding="utf-8") as file:
                report = json.load(file)

        summary = report["summary"]

        self.assertEqual(summary["total_cases"], 3)
        self.assertEqual(summary["completed"], 2)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(summary["unexpected_errors"], 0)

        self.assertEqual(len(report["results"]), 2)
        self.assertEqual(len(report["skipped_cases"]), 1)
        self.assertEqual(report["errors"], [])
        self.assertIn("timestamp", report)

        # One of two completed cases passed.
        self.assertEqual(summary["pass_rate"], 0.5)

    def test_zero_completed_cases_has_no_pass_rate(self):
        """The pass rate should be None when no cases complete."""

        skipped_cases = [
            {
                "name": "Case A",
                "error_type": "GoogleRateLimitError",
                "message": "Quota exceeded",
            },
            {
                "name": "Case B",
                "error_type": "GoogleRateLimitError",
                "message": "Quota exceeded",
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "latest_report.json"

            save_evaluation_report(
                results=[],
                skipped_cases=skipped_cases,
                errors=[],
                total=2,
                output_path=report_path,
            )

            with report_path.open(encoding="utf-8") as file:
                report = json.load(file)

        summary = report["summary"]

        self.assertIsNone(summary["pass_rate"])
        self.assertEqual(summary["total_cases"], 2)
        self.assertEqual(summary["completed"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 2)


if __name__ == "__main__":
    unittest.main()