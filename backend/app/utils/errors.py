"""Custom exception classes for the application."""


class AppError(Exception):
    """Base application error."""
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)


class LLMError(AppError):
    def __init__(self, message: str):
        super().__init__("LLMError", message)


class MarketAPIError(AppError):
    def __init__(self, message: str):
        super().__init__("MarketAPIError", message)


class TavilyError(AppError):
    def __init__(self, message: str):
        super().__init__("TavilyError", message)


class RetrievalError(AppError):
    def __init__(self, message: str):
        super().__init__("RetrievalError", message)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__("ValidationError", message)


class InternalError(AppError):
    def __init__(self, message: str):
        super().__init__("InternalError", message)
