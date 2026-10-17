
from dataclasses import dataclass


@dataclass
class CodeAnalysisCase:
    name: str
    language: str
    code: str
    expected_issue_type: str
    expected_keywords: list[str]
    expected_behavior: str


EVALUATION_CASES = [
    CodeAnalysisCase(
        name="Undefined variable",
        language="python",
        code="print(x)",
        expected_issue_type="Runtime Error",
        expected_keywords=["NameError", "x"],
        expected_behavior=(
            "Identify that x is referenced before it has been defined "
            "in the current scope."
        ),
    ),
    CodeAnalysisCase(
        name="List index out of range",
        language="python",
        code="numbers = [1, 2, 3]\nprint(numbers[5])",
        expected_issue_type="Runtime Error",
        expected_keywords=["IndexError", "index"],
        expected_behavior=(
            "Explain that valid indices are 0, 1, and 2, so index 5 "
            "is outside the list."
        ),
    ),
    CodeAnalysisCase(
        name="Division by zero",
        language="python",
        code="result = 10 / 0",
        expected_issue_type="Runtime Error",
        expected_keywords=["ZeroDivisionError", "zero"],
        expected_behavior=(
            "Identify division by zero as the cause of the runtime error."
        ),
    ),
    CodeAnalysisCase(
        name="Syntax error",
        language="python",
        code="if x > 5\n    print(x)",
        expected_issue_type="Syntax Error",
        expected_keywords=["syntax", "colon"],
        expected_behavior=(
            "Identify the missing colon after the if condition. "
            "The syntax error prevents execution before runtime behavior "
            "such as an undefined x can be evaluated."
        ),
    ),
    CodeAnalysisCase(
        name="Potential logical error",
        language="python",
        code="def add(a, b):\n    return a - b",
        expected_issue_type="Logical Error",
        expected_keywords=["subtract", "add"],
        expected_behavior=(
            "Explain that the function subtracts rather than adds. "
            "Treat this as a likely mismatch with the function name, "
            "not definitive proof of programmer intent."
        ),
    ),
]
