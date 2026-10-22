
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.chains.code_analysis_chain import code_analysis_chain
from tests.evaluation.code_analysis_cases import EVALUATION_CASES


INFRASTRUCTURE_ERROR_MARKERS = (
    "429",
    "503",
    "resource_exhausted",
    "unavailable",
    "rate limit",
    "quota",
    "timeout",
    "timed out",
    "connection error",
)


def normalize_text(value):
    """Normalize text for case-insensitive matching."""
    return " ".join(str(value).lower().split())


def diagnostic_content_check(case, diagnostic_text, summary=None):
    """Check case-specific facts in a model response."""
    text = normalize_text(diagnostic_text)
    summary_text = normalize_text(
        summary if summary is not None else diagnostic_text
    )

    if case.name == "Undefined variable":
        checks = {
            "mentions_variable_x": "x" in text,
            "identifies_undefined_variable": any(
                phrase in text
                for phrase in (
                    "not defined",
                    "undefined",
                    "has not been defined",
                    "hasn't been defined",
                    "not been declared",
                    "nameerror",
                    "before it is defined",
                    "before being defined",
                )
            ),
        }

    elif case.name == "List index out of range":
        checks = {
            "mentions_invalid_index": "5" in text or "five" in text,
            "identifies_out_of_range_access": any(
                phrase in text
                for phrase in (
                    "out of range",
                    "out of bounds",
                    "does not exist",
                    "doesn't exist",
                    "invalid index",
                    "indexerror",
                    "outside the valid range",
                    "outside the bounds",
                    "valid indices",
                )
            ),
        }

    elif case.name == "Division by zero":
        checks = {
            "identifies_division_by_zero": (
                "zero" in text
                and any(
                    phrase in text
                    for phrase in (
                        "division",
                        "divide",
                        "zerodivisionerror",
                        "dividing",
                    )
                )
            ),
        }

    elif case.name == "Syntax error":
        checks = {
            "identifies_missing_colon": (
                "colon" in text
                and any(
                    phrase in text
                    for phrase in (
                        "missing",
                        "forgot",
                        "expected",
                        "require",
                        "add a colon",
                        "needs a colon",
                        "should have a colon",
                    )
                )
            ),
            # Suggestions may discuss hypothetical issues after the
            # syntax error is fixed. Check unsupported runtime claims
            # against the summary separately.
            "does_not_claim_undefined_x_runtime_error": not any(
                phrase in summary_text
                for phrase in (
                    "nameerror",
                    "undefined variable",
                    "variable x is not defined",
                    "variable x is undefined",
                    "x is not defined",
                    "x is undefined",
                    "x has not been defined",
                )
            ),
        }

    elif case.name == "Potential logical error":
        checks = {
            "identifies_subtraction": any(
                phrase in text
                for phrase in (
                    "subtract",
                    "subtraction",
                    "minus",
                    "a - b",
                    "a-b",
                )
            ),
            "recognizes_addition_expectation": any(
                phrase in text
                for phrase in (
                    "addition",
                    "add the arguments",
                    "add the numbers",
                    "sum of",
                    "instead of adding",
                    "rather than adding",
                    "expected to add",
                    "should add",
                )
            ),
        }

    elif case.name == "Type mismatch":
        checks = {
            "identifies_type_error": (
                "typeerror" in text or "type error" in text
            ),
            "identifies_string_integer_mismatch": (
                "string" in text
                and ("integer" in text or "int" in text)
                and any(
                    phrase in text
                    for phrase in (
                        "cannot add",
                        "can't add",
                        "unsupported operand",
                        "incompatible",
                        "between",
                        "concatenate",
                    )
                )
            ),
        }

    elif case.name == "Missing function argument":
        checks = {
            "identifies_missing_argument": any(
                phrase in text
                for phrase in (
                    "missing",
                    "required argument",
                    "required positional argument",
                    "without the argument",
                    "no argument",
                    "expects an argument",
                )
            ),
            "identifies_function_call_error": (
                "typeerror" in text
                or "type error" in text
                or "argument" in text
            ),
        }

    elif case.name == "Empty list access":
        checks = {
            "identifies_empty_list": (
                "empty" in text or "no elements" in text
            ),
            "identifies_invalid_index": (
                "indexerror" in text
                or "index" in text
                or "out of range" in text
            ),
        }

    elif case.name == "Missing return statement":
        checks = {
            "identifies_missing_return": (
                "return" in text
                and any(
                    phrase in text
                    for phrase in (
                        "does not return",
                        "doesn't return",
                        "no return",
                        "without returning",
                        "missing return",
                        "not returned",
                        "implicitly returns",
                    )
                )
            ),
            "identifies_none_result": (
                "none" in text
                or "no value" in text
                or "no result" in text
            ),
        }

    elif case.name == "Invalid integer conversion":
        checks = {
            "identifies_value_error": (
                "valueerror" in text or "value error" in text
            ),
            "identifies_invalid_integer_conversion": (
                "int(" in text
                or "integer" in text
                or "convert" in text
                or "conversion" in text
                or "parse" in text
            ),
            "identifies_invalid_input": (
                "hello" in text
                or "not a valid" in text
                or "invalid literal" in text
                or "cannot convert" in text
                or "can't convert" in text
            ),
        }

    elif case.name == "Off-by-one loop":
        checks = {
            "identifies_exclusive_range_endpoint": (
                "range" in text
                and any(
                    phrase in text
                    for phrase in (
                        "excludes 10",
                        "exclude 10",
                        "does not include 10",
                        "doesn't include 10",
                        "not include 10",
                        "stops before 10",
                        "stop before 10",
                        "upper bound is exclusive",
                        "exclusive upper bound",
                    )
                )
            ),
            "suggests_correct_endpoint": (
                "range(1, 11)" in text
                or "range(1,11)" in text
                or "range(1, 10 + 1)" in text
                or "range(1,10 + 1)" in text
            ),
        }

    elif case.name == "Incorrect comparison":
        checks = {
            "identifies_boundary_condition": (
                "18" in text
                and any(
                    phrase in text
                    for phrase in (
                        "greater than",
                        "strictly greater",
                        "exactly 18",
                        "age 18",
                        "equal to 18",
                        "includes 18",
                        "exclude people aged 18",
                        "not include people aged 18",
                    )
                )
            ),
            "suggests_inclusive_comparison": (
                ">= " in text
                or ">=18" in text
                or "greater than or equal" in text
                or "greater than or equal to" in text
            ),
        }

    elif case.name == "Mutable default argument":
        checks = {
            "identifies_shared_mutable_default": (
                "mutable" in text
                and any(
                    phrase in text
                    for phrase in (
                        "default argument",
                        "default list",
                        "shared list",
                        "same list",
                        "reused across calls",
                        "reused between calls",
                        "persists between calls",
                        "created once",
                        "shared mutable",
                    )
                )
            ),
            "suggests_safe_default": (
                "none" in text
                and (
                    "default" in text
                    or "list" in text
                )
            ),
        }

    elif case.name == "Unreachable code":
        checks = {
            "identifies_unreachable_statement": any(
                phrase in text
                for phrase in (
                    "unreachable",
                    "never execute",
                    "never run",
                    "will not execute",
                    "won't execute",
                    "cannot be reached",
                    "can't be reached",
                )
            ),
            "connects_return_to_unreachable_code": (
                "return" in text
                and any(
                    phrase in text
                    for phrase in (
                        "before",
                        "after",
                        "following",
                        "subsequent",
                        "immediately",
                        "early return",
                    )
                )
            ),
        }

    else:
        return {
            "passed": False,
            "checks": {"known_test_case": False},
        }

    return {
        "passed": bool(checks) and all(checks.values()),
        "checks": checks,
    }


def evaluate_case(case):
    """Run one case and evaluate the structured AI response."""
    result = code_analysis_chain.invoke({
        "language": case.language,
        "code": case.code,
    })

    issues = result.issues
    issues_found = len(issues) > 0

    issue_types = [
        normalize_text(issue.type)
        for issue in issues
    ]
    expected_type = normalize_text(case.expected_issue_type)
    type_found = expected_type in issue_types

    diagnostic_text = " ".join(
        [result.summary]
        + [issue.explanation for issue in issues]
        + result.suggestions
    )
    normalized_text = normalize_text(diagnostic_text)

    expected_keywords = getattr(case, "expected_keywords", [])
    matched_keywords = [
        keyword
        for keyword in expected_keywords
        if normalize_text(keyword) in normalized_text
    ]

    required_keyword_count = len(expected_keywords)
    keyword_found = (
        len(matched_keywords) == required_keyword_count
    )

    diagnostic_check = diagnostic_content_check(
        case,
        diagnostic_text,
        summary=result.summary,
    )
    diagnostic_found = diagnostic_check["passed"]

    explanation_found = any(
        isinstance(issue.explanation, str)
        and issue.explanation.strip()
        for issue in issues
    )
    suggestions_found = any(
        isinstance(suggestion, str) and suggestion.strip()
        for suggestion in result.suggestions
    )

    passed = all((
        issues_found,
        type_found,
        keyword_found,
        diagnostic_found,
        explanation_found,
        suggestions_found,
    ))

    return {
        "name": case.name,
        "passed": passed,
        "issues_found": issues_found,
        "type_found": type_found,
        "expected_issue_type": case.expected_issue_type,
        "returned_issue_types": [
            issue.type for issue in issues
        ],
        "keyword_found": keyword_found,
        "matched_keywords": matched_keywords,
        "required_keyword_count": required_keyword_count,
        "diagnostic_found": diagnostic_found,
        "diagnostic_checks": diagnostic_check["checks"],
        "expected_behavior": getattr(case, "expected_behavior", ""),
        "explanation_found": explanation_found,
        "suggestions_found": suggestions_found,
        "summary": result.summary,
    }


def is_infrastructure_error(exc):
    """Identify common provider availability and quota errors."""
    message = str(exc).lower()
    return any(
        marker in message
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
            "completion_rate": (
                round(completed / total, 4)
                if total
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
    if limit is not None and limit < 0:
        raise ValueError(
            "limit must be zero or a positive integer"
        )

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
            print(
                "Diagnostic checks passed: "
                f"{result['diagnostic_found']}"
            )
            print(
                "Diagnostic check details: "
                f"{result['diagnostic_checks']}"
            )
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
                    "SKIPPED - Possible provider or network issue: "
                    f"{type(exc).__name__}"
                )
            else:
                error_details.append(error_record)
                print(
                    f"ERROR - Unexpected failure: "
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
    print(
        f"Pass rate: {passed / completed:.1%}"
        if completed
        else "Pass rate: N/A"
    )
    print(
        f"Completion rate: {completed / len(cases):.1%}"
        if cases
        else "Completion rate: N/A"
    )
    print("========================================")

    save_evaluation_report(
        results=results,
        skipped_cases=skipped_cases,
        errors=error_details,
        total=len(cases),
    )


if __name__ == "__main__":
    run_evaluation()
