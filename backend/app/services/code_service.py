from backend.app.models.code import CodeRequest
from backend.app.chains.code_analysis_chain import code_analysis_chain
from backend.app.utils.exceptions import AIServiceError


def analyze_code(request: CodeRequest):
    try:
        result = code_analysis_chain.invoke({
            "language": request.language,
            "code": request.code,
        })

        return result

    except Exception as exc:
        print(f"AI service error: {exc}")

        raise AIServiceError(
            "The AI service is temporarily unavailable. Please try again later."
        )