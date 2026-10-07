from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful programming mentor."
    ),
    (
        "human",
        "Explain this programming concept: {concept}"
    ),
])


model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.2,
)


chain = prompt | model


result = chain.invoke({
    "concept": "Python decorators"
})

print(result.content)