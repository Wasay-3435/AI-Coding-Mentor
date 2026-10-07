from fastapi import APIRouter

from backend.app.models.code import CodeRequest

router = APIRouter()


@router.post("/analyze-code")
def analyze_code(request: CodeRequest):
    return {
        "language": request.language,
        "code": request.code,
        "message": "Code received successfully!"
    }