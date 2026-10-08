from backend.app.models.code import CodeRequest
from backend.app.chains.code_analysis_chain import code_analysis_chain


def analyze_code(request: CodeRequest):
    result = code_analysis_chain.invoke({
        "language": request.language,
        "code": request.code,
    })

    return result