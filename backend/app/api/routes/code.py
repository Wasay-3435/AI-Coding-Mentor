
from fastapi import APIRouter, HTTPException

from backend.app.models.code import CodeRequest, CodeAnalysisResponse
from backend.app.services.code_service import analyze_code
from backend.app.services.session_service import (
    SessionNotFoundError,
    record_analysis,
)


router = APIRouter()


@router.post(
    "/analyze-code",
    response_model=CodeAnalysisResponse,
)
def analyze_code_route(request: CodeRequest):
    result = analyze_code(request)

    if request.session_id:
        try:
            record_analysis(request.session_id, result)
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return result
