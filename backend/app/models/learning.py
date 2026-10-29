
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from backend.app.models.code import CodeAnalysisResponse


class ExerciseGenerationRequest(BaseModel):
    language: str
    code: str
    analysis: CodeAnalysisResponse
    count: int = Field(default=3, ge=1, le=5)
    session_id: str | None = None

    @field_validator("language", "code")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class PracticeExercise(BaseModel):
    title: str
    concept: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    instructions: str
    starter_code: str
    expected_skills: list[str]

    @field_validator("title", "concept", "instructions")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value

    @field_validator("expected_skills")
    @classmethod
    def reject_blank_skills(cls, value: list[str]) -> list[str]:
        if not value or any(not skill.strip() for skill in value):
            raise ValueError("Expected skills must not be empty.")
        return value


class ExerciseGenerationResponse(BaseModel):
    exercises: list[PracticeExercise]
    session_id: str | None = None

    @field_validator("exercises")
    @classmethod
    def require_exercises(
        cls,
        value: list[PracticeExercise],
    ) -> list[PracticeExercise]:
        if not value:
            raise ValueError("At least one exercise must be generated.")
        return value


class ExerciseSubmissionRequest(BaseModel):
    exercise: PracticeExercise
    language: str
    answer: str
    session_id: str | None = None

    @field_validator("language", "answer")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class ExerciseEvaluationResponse(BaseModel):
    is_correct: bool
    score: int = Field(ge=0, le=100)
    feedback: str
    explanation: str
    hint: str
    strengths: list[str]
    improvements: list[str]

    @field_validator("feedback", "explanation", "hint")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class LearningSessionCreateResponse(BaseModel):
    session_id: str
    message: str


class LearningSessionReportResponse(BaseModel):
    session_id: str
    started_at: datetime
    completed_at: datetime
    total_analyses: int = Field(ge=0)
    total_exercises_generated: int = Field(ge=0)
    total_exercises_attempted: int = Field(ge=0)
    average_score: float = Field(ge=0, le=100)
    correct_answers: int = Field(ge=0)
    concepts_to_practice: list[str]
    recommendations: list[str]
    summary: str
