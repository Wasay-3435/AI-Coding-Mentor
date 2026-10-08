class AIServiceError(Exception):
    """Raised when the AI provider cannot process a request."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)