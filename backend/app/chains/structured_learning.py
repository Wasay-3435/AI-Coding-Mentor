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
        Analyze the provided code and identify programming issues.
        Be precise and educational.
        """
    ),
    (
        "human",
        """
        Language: {language}

        Code:
        {code}
        """
    ),
])


model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
)


structured_model = model.with_structured_output(CodeAnalysisResponse)


chain = prompt | structured_model


result = chain.invoke({
    "language": "python",
    "code": "print(x)",
})


print(result)
print(type(result))