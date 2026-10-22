
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
    CodeAnalysisCase(
        name="Type mismatch",
        language="python",
        code='age = "twenty"\nprint(age + 5)',
        expected_issue_type="Runtime Error",
        expected_keywords=["TypeError", "string"],
        expected_behavior=(
            "Explain that Python cannot add a string and an integer "
            "using the plus operator in this context."
        ),
    ),
    CodeAnalysisCase(
        name="Missing function argument",
        language="python",
        code=(
            "def greet(name):\n"
            '    print(f"Hello, {name}")\n'
            "greet()"
        ),
        expected_issue_type="Runtime Error",
        expected_keywords=["TypeError", "argument"],
        expected_behavior=(
            "Identify that greet requires the name argument but is called "
            "without the required argument."
        ),
    ),
    CodeAnalysisCase(
        name="Empty list access",
        language="python",
        code="items = []\nprint(items[0])",
        expected_issue_type="Runtime Error",
        expected_keywords=["IndexError", "empty"],
        expected_behavior=(
            "Explain that the list is empty and has no valid index 0."
        ),
    ),
    CodeAnalysisCase(
        name="Missing return statement",
        language="python",
        code=(
            "def calculate_total(price, tax):\n"
            "    price + tax\n"
            "result = calculate_total(10, 2)\n"
            "print(result)"
        ),
        expected_issue_type="Logical Error",
        expected_keywords=["return", "None"],
        expected_behavior=(
            "Explain that calculate_total computes price + tax but does "
            "not return the result, so the function call evaluates to None."
        ),
    ),
    CodeAnalysisCase(
        name="Invalid integer conversion",
        language="python",
        code='number = int("hello")',
        expected_issue_type="Runtime Error",
        expected_keywords=["ValueError", "integer"],
        expected_behavior=(
            "Identify that the string hello is not a valid integer "
            "representation and int() raises ValueError."
        ),
    ),
]
