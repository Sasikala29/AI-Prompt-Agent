class AppError(Exception):
    """Base application error."""
    
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class ProviderUnavailableError(AppError):
    def __init__(self, message: str = "LLM provider is currently unavailable."):
        super().__init__(message, "provider_unavailable")


class ModelNotFoundError(AppError):
    def __init__(self, message: str = "Requested model was not found."):
        super().__init__(message, "model_not_found")


class LLMTimeoutError(AppError):
    def __init__(self, message: str = "LLM request timed out."):
        super().__init__(message, "llm_timeout")


class LLMResponseError(AppError):
    def __init__(self, message: str = "Invalid response received from LLM."):
        super().__init__(message, "llm_response_error")
