from backend.app.models.code import CodeRequest


def analyze_code(request: CodeRequest):
    return {
        "language": request.language,
        "code": request.code,
        "message": "Code received successfully!"
    }