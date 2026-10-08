from fastapi import FastAPI

from backend.app.api.routes.code import router as code_router
from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.utils.exceptions import AIServiceError

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
