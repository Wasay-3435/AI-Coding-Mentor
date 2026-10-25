
from fastapi import APIRouter

from backend.app.models.learning import (
    ExerciseGenerationRequest,
    ExerciseGenerationResponse,
)
from backend.app.services.learning_service import generate_exercises


router = APIRouter()


@router.post(
    "/generate-exercises",
    response_model=ExerciseGenerationResponse,
)
def generate_exercises_route(request: ExerciseGenerationRequest):
    return generate_exercises(request)
