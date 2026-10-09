
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.chains.code_analysis_chain import code_analysis_chain
from tests.evaluation.code_analysis_cases import EVALUATION_CASES


INFRASTRUCTURE_ERROR_MARKERS = (
    "503",
    "UNAVAILABLE",
    "429",
    "RESOURCE_EXHAUSTED",
    "timeout",
    "timed out",
)


def evaluate_case(case):
    """Run one case and evaluate the structured AI response."""

    result = code_analysis_chain.invoke({
        "language": case.language,
        "code": case.code,
    })

    # Check whether the model returned any issues.
    issues_found = len(result.issues) > 0

    # Check whether the expected issue category was returned.
    issue_types = [
        issue.type.strip().lower()
        for issue in result.issues
    ]

    expected_type = case.expected_issue_type.strip().lower()

    type_found = any(
        expected_type == issue_type
        for issue_type in issue_types
    )

    # Collect explanations and suggestions for keyword matching.
    diagnostic_text = " ".join(
        [issue.explanation for issue in result.issues]
        + result.suggestions
    ).lower()

    matched_keywords = [
        keyword
        for keyword in case.expected_keywords
        if keyword.lower() in diagnostic_text
    ]

    required_keyword_count = min(
        2,
        len(case.expected_keywords),
    )

    keyword_found = (
        len(matched_keywords) >= required_keyword_count
    )

    # Check that at least one issue has a non-empty explanation.
    explanation_found = any(
        issue.explanation.strip()
        for issue in result.issues
    )

    # Check that at least one non-empty suggestion exists.
    suggestions_found = any(
        suggestion.strip()
        for suggestion in result.suggestions
    )

    # All required checks must pass.
    passed = (
        issues_found
        and type_found
        and keyword_found
        and explanation_found
        and suggestions_found
    )

    return {
        "name": case.name,
        "passed": passed,
        "issues_found": issues_found,
        "type_found": type_found,
        "keyword_found": keyword_found,
        "matched_keywords": matched_keywords,
        "explanation_found": explanation_found,
        "suggestions_found": suggestions_found,
        "summary": result.summary,
    }


def is_infrastructure_error(exc):
    """Identify common provider availability and quota errors."""

    message = str(exc).lower()

    return any(
        marker.lower() in message
        for marker in INFRASTRUCTURE_ERROR_MARKERS
    )


def save_evaluation_report(
    results,
    skipped_cases,
    errors,
    total,
    output_path=None,
):
    """Save evaluation results and summary statistics to JSON."""

    passed = sum(result["passed"] for result in results)
    failed = sum(not result["passed"] for result in results)
    completed = len(results)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_cases": total,
            "completed": completed,
            "passed": passed,
            "failed": failed,
            "skipped": len(skipped_cases),
            "unexpected_errors": len(errors),
            "pass_rate": (
                round(passed / completed, 4)
                if completed
                else None
            ),
        },
        "results": results,
        "skipped_cases": skipped_cases,
        "errors": errors,
    }

    if output_path is None:
        report_dir = Path(__file__).parent / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "latest_report.json"
    else:
        report_path = Path(output_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"\nJSON report saved to: {report_path}")

    return report


def run_evaluation(limit=None):
    """Evaluate all cases or a limited number of cases."""

    cases = (
        EVALUATION_CASES[:limit]
        if limit is not None
        else EVALUATION_CASES
    )

    results = []
    skipped_cases = []
    error_details = []

    for case in cases:
        print(f"\nEvaluating: {case.name}")

        try:
            result = evaluate_case(case)
            results.append(result)

            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
            print(f"Summary: {result['summary']}")
            print(f"Issues present: {result['issues_found']}")
            print(f"Correct issue type: {result['type_found']}")
            print(f"Expected keywords found: {result['keyword_found']}")
            print(f"Matched keywords: {result['matched_keywords']}")
            print(f"Explanation present: {result['explanation_found']}")
            print(f"Suggestions present: {result['suggestions_found']}")

        except Exception as exc:
            error_record = {
                "name": case.name,
                "error_type": type(exc).__name__,
                "message": str(exc),
            }

            if is_infrastructure_error(exc):
                skipped_cases.append(error_record)

                print(
                    "SKIPPED — Provider unavailable or quota exceeded: "
                    f"{type(exc).__name__}"
                )
            else:
                error_details.append(error_record)

                print(
                    f"ERROR — Unexpected failure: "
                    f"{type(exc).__name__}: {exc}"
                )

    passed = sum(result["passed"] for result in results)
    failed = sum(not result["passed"] for result in results)
    completed = len(results)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total cases: {len(cases)}")
    print(f"Completed evaluations: {completed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {len(skipped_cases)}")
    print(f"Unexpected errors: {len(error_details)}")

    if completed:
        print(f"Pass rate: {passed / completed:.1%}")
    else:
        print("Pass rate: N/A — no cases completed")

    print("========================================")

    # Save the report even if the provider quota is exhausted.
    save_evaluation_report(
        results=results,
        skipped_cases=skipped_cases,
        errors=error_details,
        total=len(cases),
    )


if __name__ == "__main__":
    run_evaluation()
