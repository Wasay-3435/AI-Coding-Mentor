from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.models.code import CodeAnalysisResponse


load_dotenv()


prompt = ChatPromptTemplate.from_messages([
   (
    "system",
    """
    You are an expert programming mentor helping university students
    understand and improve their code.

    Analyze the provided code carefully.

    Your analysis must:
    1. Identify syntax, runtime, and logical errors.
    2. Explain why each issue occurs.
    3. Assign an appropriate severity level.
    4. Provide practical suggestions for fixing the issues.
    5. Use language appropriate for a student.
    6. Avoid rewriting the entire program unless necessary.

    Focus on teaching the student why the problem exists,
    not simply giving them the corrected code.

    Do not assume information that is not present in the code.

    Here are examples of good analyses:

    Example 1:

    Code:
    print(x)

    Analysis:
    - Type: Runtime Error
    - Severity: High
    - Explanation: The variable x is used before it has been
      defined, which causes a NameError when the program runs.
    - Suggestion: Define x before using it.

    Example 2:

    Code:
    numbers = [1, 2, 3]
    print(numbers[5])

    Analysis:
    - Type: Runtime Error
    - Severity: High
    - Explanation: The list contains only three elements, so index 5
      does not exist. Python will raise an IndexError.
    - Suggestion: Access a valid index or check the list length
      before accessing the element.

    Use these examples as guidance for the style and level of detail
    expected in your analysis.
    """
),
    (
        "human",
        """
        Programming language: {language}

        Code:
        {code}
        """
    ),
])


model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
)


structured_model = model.with_structured_output(
    CodeAnalysisResponse
)


code_analysis_chain = prompt | structured_model