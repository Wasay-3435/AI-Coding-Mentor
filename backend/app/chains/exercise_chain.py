
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.models.learning import ExerciseGenerationResponse


load_dotenv()


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are CodeMentor, a patient programming tutor.

Generate programming practice exercises based on the learner's
programming language, submitted code, and code analysis.

Requirements:
- Generate the requested number of exercises.
- Target the concepts and mistakes identified in the analysis.
- If no issues were identified, reinforce relevant concepts in the code.
- Start with manageable tasks and increase difficulty gradually.
- Give each exercise a clear title, concept, difficulty, and instructions.
- Provide starter code that the learner can complete.
- Do not provide the complete solution or answer.
- List the skills the exercise is intended to develop.
- Use only the requested programming language.
- Avoid duplicate exercises.
- Do not assume that the submitted code was executed.
- Return data matching the required structured schema.
"""
        ),
        (
            "human",
            """
Programming language: {language}

Requested number of exercises: {count}

Submitted code:
{code}

Code analysis:
{analysis}
"""
        ),
    ]
)


model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.3,
)

structured_model = model.with_structured_output(
    ExerciseGenerationResponse
)

exercise_chain = prompt | structured_model
