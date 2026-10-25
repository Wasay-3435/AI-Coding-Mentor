
from pydantic import BaseModel, field_validator


class CodeRequest(BaseModel):
    language: str
    code: str
    session_id: str | None = None

    @field_validator("language", "code")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class CodeIssue(BaseModel):
    type: str
    severity: str
    explanation: str

    @field_validator("type", "severity", "explanation")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class CodeAnalysisResponse(BaseModel):
    summary: str
    issues: list[CodeIssue]
    suggestions: list[str]

    @field_validator("summary")
    @classmethod
    def reject_blank_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Summary must not be empty.")
        return value

    @field_validator("suggestions")
    @classmethod
    def reject_blank_suggestions(cls, value: list[str]) -> list[str]:
        if any(not suggestion.strip() for suggestion in value):
            raise ValueError("Suggestions must not contain empty strings.")
        return value
