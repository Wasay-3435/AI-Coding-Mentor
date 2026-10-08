from dataclasses import dataclass


@dataclass
class CodeAnalysisCase:
    name: str
    language: str
    code: str
    expected_issue_type: str
    expected_keywords: list[str]


EVALUATION_CASES = [
    CodeAnalysisCase(
        name="Undefined variable",
        language="python",
        code="print(x)",
        expected_issue_type="Runtime Error",
        expected_keywords=["x", "NameError", "defined"],
    ),

    CodeAnalysisCase(
        name="List index out of range",
        language="python",
        code="numbers = [1, 2, 3]\nprint(numbers[5])",
        expected_issue_type="Runtime Error",
        expected_keywords=["IndexError", "index", "list"],
    ),

    CodeAnalysisCase(
        name="Division by zero",
        language="python",
        code="result = 10 / 0",
        expected_issue_type="Runtime Error",
        expected_keywords=["ZeroDivisionError", "zero"],
    ),

    CodeAnalysisCase(
        name="Syntax error",
        language="python",
        code="if x > 5\n    print(x)",
        expected_issue_type="Syntax Error",
        expected_keywords=["syntax", "colon", ":"],
    ),

    CodeAnalysisCase(
        name="Potential logical error",
        language="python",
        code="def add(a, b):\n    return a - b",
        expected_issue_type="Logical Error",
        expected_keywords=["subtract", "minus", "add", "addition"],
    ),
]