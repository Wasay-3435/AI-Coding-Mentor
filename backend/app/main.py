from fastapi import FastAPI

from backend.app.api.routes.code import router as code_router


app = FastAPI(
    title="AI Coding Mentor",
    description="AI-powered coding mentorship platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Coding Mentor API is running!"
    }


app.include_router(
    code_router,
    prefix="/api/v1",
    tags=["Code"],
)
