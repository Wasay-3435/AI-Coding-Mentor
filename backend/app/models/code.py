from pydantic import BaseModel


class CodeRequest(BaseModel):
    language: str
    code: str


class CodeIssue(BaseModel):
    type: str
    severity: str
    explanation: str


class CodeAnalysisResponse(BaseModel):
    summary: str
    issues: list[CodeIssue]
    suggestions: list[str]