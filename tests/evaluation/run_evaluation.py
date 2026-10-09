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

    # 1. Check whether the model returned at least one issue.
    issues_found = len(result.issues) > 0

    # 2. Check whether the expected issue category was returned.
    issue_types = [
        issue.type.strip().lower()
        for issue in result.issues
    ]

    expected_type = case.expected_issue_type.strip().lower()

    type_found = any(
        expected_type == issue_type
        for issue_type in issue_types
    )

    # 3. Collect diagnostic explanations and suggestions.
    diagnostic_text = " ".join(
        [issue.explanation for issue in result.issues]
        + result.suggestions
    ).lower()

    # Require at least two expected keywords, or all keywords
    # if fewer than two were supplied.
    matched_keywords = [
        keyword
        for keyword in case.expected_keywords
        if keyword.lower() in diagnostic_text
    ]

    required_keyword_count = min(2, len(case.expected_keywords))

    keyword_found = (
        len(matched_keywords) >= required_keyword_count
    )

    # 4. Verify that at least one issue has a non-empty explanation.
    explanation_found = any(
        issue.explanation.strip()
        for issue in result.issues
    )

    # 5. Verify that at least one non-empty suggestion exists.
    suggestions_found = any(
        suggestion.strip()
        for suggestion in result.suggestions
    )

    # 6. All required checks must pass.
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


def run_evaluation(limit=None):
    """Evaluate all cases or a limited number of cases."""

    cases = (
        EVALUATION_CASES[:limit]
        if limit is not None
        else EVALUATION_CASES
    )

    results = []
    skipped = 0
    errors = 0

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
            if is_infrastructure_error(exc):
                skipped += 1
                print(
                    "SKIPPED — Provider unavailable or quota exceeded: "
                    f"{type(exc).__name__}"
                )
            else:
                errors += 1
                print(
                    f"ERROR — Unexpected failure: "
                    f"{type(exc).__name__}: {exc}"
                )

    passed = sum(result["passed"] for result in results)
    failed = sum(not result["passed"] for result in results)
    completed = len(results)
    total = len(cases)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Unexpected errors: {errors}")
    print(f"Completed evaluations: {completed}/{total}")

    if completed:
        print(f"Pass rate: {passed / completed:.1%}")
    else:
        print("Pass rate: N/A — no evaluations completed")

    print("========================================")


if __name__ == "__main__":
    run_evaluation(limit=1)
