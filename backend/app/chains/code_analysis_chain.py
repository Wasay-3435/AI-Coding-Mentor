from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.models.code import CodeAnalysisResponse


load_dotenv()


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert programming mentor.

        Analyze the user's code carefully.
        Identify bugs, programming issues, and potential improvements.

        Your analysis should be:
        - Accurate
        - Clear
        - Educational
        - Appropriate for a student learning programming

        Do not rewrite the entire program unless necessary.
        Focus on helping the student understand the problem.
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