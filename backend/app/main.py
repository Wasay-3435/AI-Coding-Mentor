
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.routes.code import router as code_router
from backend.app.api.routes.learning import router as learning_router
from backend.app.utils.exceptions import AIServiceError, AIResponseError


app = FastAPI(
    title="AI Coding Mentor",
    description="AI-powered coding mentorship platform",
    version="0.1.0",
)


@app.exception_handler(AIServiceError)
async def ai_service_error_handler(
    request: Request,
    exc: AIServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "error": "AI service unavailable",
            "message": exc.message,
        },
    )


@app.exception_handler(AIResponseError)
async def ai_response_error_handler(
    request: Request,
    exc: AIResponseError,
):
    return JSONResponse(
        status_code=502,
        content={
            "error": "Invalid AI response",
            "message": exc.message,
        },
    )


@app.get("/")
def root():
    return {"message": "AI Coding Mentor API is running!"}


app.include_router(
    code_router,
    prefix="/api/v1",
    tags=["Code"],
)

app.include_router(
    learning_router,
    prefix="/api/v1",
    tags=["Learning"],
)
