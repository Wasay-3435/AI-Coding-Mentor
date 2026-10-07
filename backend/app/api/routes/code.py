from fastapi import APIRouter
from backend.app.models.code import CodeRequest
from backend.app.services.code_service import analyze_code

router = APIRouter()


@router.post("/analyze-code")
def analyze_code_route(request: CodeRequest):
    return analyze_code(request)