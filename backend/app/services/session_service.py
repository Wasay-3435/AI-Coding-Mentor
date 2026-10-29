
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from backend.app.models.code import CodeAnalysisResponse
from backend.app.models.learning import (
    ExerciseEvaluationResponse,
    ExerciseGenerationResponse,
    LearningSessionReportResponse,
)


_sessions: dict[str, dict] = {}
_sessions_lock = RLock()


class SessionNotFoundError(Exception):
    """Raised when a requested learning session does not exist."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_session() -> dict:
    session_id = str(uuid4())
    started_at = _now()

    with _sessions_lock:
        _sessions[session_id] = {
            "started_at": started_at,
            "analyses": [],
            "generated_exercises": [],
            "evaluations": [],
        }

    return {
        "session_id": session_id,
        "message": "Learning session created successfully.",
    }


def _get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if session is None:
        raise SessionNotFoundError(
            f"Learning session '{session_id}' was not found."
        )
    return session


def record_analysis(
    session_id: str,
    analysis: CodeAnalysisResponse,
) -> None:
    with _sessions_lock:
        session = _get_session(session_id)
        session["analyses"].append(analysis.model_dump())


def record_generated_exercises(
    session_id: str,
    result: ExerciseGenerationResponse,
) -> None:
    with _sessions_lock:
        session = _get_session(session_id)

        session["generated_exercises"].extend(
            exercise.model_dump()
            for exercise in result.exercises
        )


def record_evaluation(
    session_id: str,
    result: ExerciseEvaluationResponse,
    concept: str,
) -> None:
    with _sessions_lock:
        session = _get_session(session_id)
        session["evaluations"].append(
            {
                "concept": concept,
                **result.model_dump(),
                "recorded_at": _now().isoformat(),
            }
        )


def get_session_report(
    session_id: str,
) -> LearningSessionReportResponse:
    with _sessions_lock:
        session = _get_session(session_id)

        analyses = list(session["analyses"])
        exercises = list(session["generated_exercises"])
        evaluations = list(session["evaluations"])
        started_at = session["started_at"]

    total_attempted = len(evaluations)
    average_score = (
        sum(item["score"] for item in evaluations) / total_attempted
        if total_attempted
        else 0.0
    )

    concepts_to_practice = sorted(
        {
            item["concept"]
            for item in evaluations
            if item["score"] < 80
        }
    )

    if not evaluations:
        recommendations = [
            "Attempt a practice exercise to establish your current level."
        ]
    else:
        recommendations = []

        if concepts_to_practice:
            recommendations.append(
                "Review these concepts and retry related exercises: "
                + ", ".join(concepts_to_practice)
                + "."
            )

        if average_score >= 80:
            recommendations.append(
                "Continue with more challenging exercises to reinforce "
                "your understanding."
            )
        else:
            recommendations.append(
                "Review the feedback and hints from your attempted exercises."
            )

    if not recommendations:
        recommendations.append(
            "Continue practising and review your feedback after each exercise."
        )

    correct_answers = sum(
        1 for item in evaluations if item["is_correct"]
    )

    if not evaluations:
        summary = (
            f"You completed {len(analyses)} code analysis "
            f"and generated {len(exercises)} practice exercises, "
            "but have not submitted any exercise answers yet."
        )
    else:
        summary = (
            f"You completed {len(analyses)} code analyses and generated "
            f"{len(exercises)} exercises. You attempted {total_attempted} "
            f"exercises, with an average score of {average_score:.1f}% "
            f"and {correct_answers} correct answers."
        )

    return LearningSessionReportResponse(
        session_id=session_id,
        started_at=started_at,
        completed_at=_now(),
        total_analyses=len(analyses),
        total_exercises_generated=len(exercises),
        total_exercises_attempted=total_attempted,
        average_score=round(average_score, 2),
        correct_answers=correct_answers,
        concepts_to_practice=concepts_to_practice,
        recommendations=recommendations,
        summary=summary,
    )
