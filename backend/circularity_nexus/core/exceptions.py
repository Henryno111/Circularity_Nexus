"""
Custom exceptions for Circularity Nexus
"""

from typing import Optional


class CircularityNexusException(Exception):
    """Base exception for Circularity Nexus"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(detail)


class ValidationError(CircularityNexusException):
    """Validation error"""
    
    def __init__(self, detail: str):
        super().__init__(detail, status_code=400, error_code="VALIDATION_ERROR")


class AuthenticationError(CircularityNexusException):
    """Authentication error"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(CircularityNexusException):
    """Authorization error"""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail, status_code=403, error_code="AUTHORIZATION_ERROR")


class NotFoundError(CircularityNexusException):
    """Resource not found error"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status_code=404, error_code="NOT_FOUND_ERROR")


class ConflictError(CircularityNexusException):
    """Resource conflict error"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail, status_code=409, error_code="CONFLICT_ERROR")


class AIProcessingError(CircularityNexusException):
    """AI processing error"""
    
    def __init__(self, detail: str = "AI processing failed"):
        super().__init__(detail, status_code=422, error_code="AI_PROCESSING_ERROR")


class BlockchainError(CircularityNexusException):
    """Blockchain operation error"""
    
    def __init__(self, detail: str = "Blockchain operation failed"):
        super().__init__(detail, status_code=502, error_code="BLOCKCHAIN_ERROR")


class ExternalServiceError(CircularityNexusException):
    """External service error"""
    
    def __init__(self, detail: str = "External service unavailable"):
        super().__init__(detail, status_code=503, error_code="EXTERNAL_SERVICE_ERROR")


class RateLimitError(CircularityNexusException):
    """Rate limit exceeded error"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail, status_code=429, error_code="RATE_LIMIT_ERROR")
