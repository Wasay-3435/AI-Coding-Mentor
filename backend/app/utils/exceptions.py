
class AIServiceError(Exception):
    """Raised when the AI provider is unavailable or cannot process a request."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AIResponseError(Exception):
    """Raised when the AI response cannot be validated or parsed."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
