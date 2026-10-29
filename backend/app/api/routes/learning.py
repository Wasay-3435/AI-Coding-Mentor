
from fastapi import APIRouter, HTTPException

from backend.app.models.learning import (
    ExerciseGenerationRequest,
    ExerciseGenerationResponse,
    ExerciseSubmissionRequest,
    ExerciseEvaluationResponse,
    LearningSessionCreateResponse,
    LearningSessionReportResponse,
)
from backend.app.services.learning_service import generate_exercises
from backend.app.services.evaluation_service import evaluate_exercise
from backend.app.services.session_service import (
    SessionNotFoundError,
    create_session,
    get_session_report,
    record_generated_exercises,
    record_evaluation,
)


router = APIRouter()


@router.post(
    "/sessions",
    response_model=LearningSessionCreateResponse,
)
def create_learning_session_route():
    return create_session()


@router.get(
    "/sessions/{session_id}/report",
    response_model=LearningSessionReportResponse,
)
def get_learning_session_report_route(session_id: str):
    try:
        return get_session_report(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/generate-exercises",
    response_model=ExerciseGenerationResponse,
)
def generate_exercises_route(request: ExerciseGenerationRequest):
    result = generate_exercises(request)

    if request.session_id:
        try:
            record_generated_exercises(request.session_id, result)
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return result


@router.post(
    "/evaluate-exercise",
    response_model=ExerciseEvaluationResponse,
)
def evaluate_exercise_route(request: ExerciseSubmissionRequest):
    result = evaluate_exercise(request)

    if request.session_id:
        try:
            record_evaluation(
                request.session_id,
                result,
                request.exercise.concept,
            )
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return result
