from fastapi import APIRouter

from backend.app.models.code import CodeRequest, CodeAnalysisResponse
from backend.app.services.code_service import analyze_code


router = APIRouter()


@router.post(
    "/analyze-code",
    response_model=CodeAnalysisResponse,
)
def analyze_code_route(request: CodeRequest):
    return analyze_code(request)