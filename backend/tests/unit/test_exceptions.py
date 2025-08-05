"""
Unit tests for custom exceptions
"""

import pytest
from circularity_nexus.core.exceptions import (
    CircularityNexusException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    AIProcessingError,
    BlockchainError,
    ExternalServiceError,
    RateLimitError
)


class TestCircularityNexusException:
    """Test cases for base CircularityNexusException"""
    
    def test_base_exception_creation(self):
        """Test base exception creation with default values"""
        exc = CircularityNexusException("Test error")
        
        assert str(exc) == "Test error"
        assert exc.detail == "Test error"
        assert exc.status_code == 500
        assert exc.error_code == "CircularityNexusException"
    
    def test_base_exception_with_custom_values(self):
        """Test base exception with custom status code and error code"""
        exc = CircularityNexusException(
            detail="Custom error",
            status_code=422,
            error_code="CUSTOM_ERROR"
        )
        
        assert exc.detail == "Custom error"
        assert exc.status_code == 422
        assert exc.error_code == "CUSTOM_ERROR"


class TestValidationError:
    """Test cases for ValidationError"""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        exc = ValidationError("Invalid input data")
        
        assert exc.detail == "Invalid input data"
        assert exc.status_code == 400
        assert exc.error_code == "VALIDATION_ERROR"
    
    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from base exception"""
        exc = ValidationError("Test validation error")
        
        assert isinstance(exc, CircularityNexusException)
        assert isinstance(exc, Exception)


class TestAuthenticationError:
    """Test cases for AuthenticationError"""
    
    def test_authentication_error_default(self):
        """Test AuthenticationError with default message"""
        exc = AuthenticationError()
        
        assert exc.detail == "Authentication failed"
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message"""
        exc = AuthenticationError("Invalid credentials")
        
        assert exc.detail == "Invalid credentials"
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_ERROR"


class TestAuthorizationError:
    """Test cases for AuthorizationError"""
    
    def test_authorization_error_default(self):
        """Test AuthorizationError with default message"""
        exc = AuthorizationError()
        
        assert exc.detail == "Access denied"
        assert exc.status_code == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"
    
    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message"""
        exc = AuthorizationError("Insufficient permissions")
        
        assert exc.detail == "Insufficient permissions"
        assert exc.status_code == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"


class TestNotFoundError:
    """Test cases for NotFoundError"""
    
    def test_not_found_error_default(self):
        """Test NotFoundError with default message"""
        exc = NotFoundError()
        
        assert exc.detail == "Resource not found"
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND_ERROR"
    
    def test_not_found_error_custom_message(self):
        """Test NotFoundError with custom message"""
        exc = NotFoundError("User not found")
        
        assert exc.detail == "User not found"
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND_ERROR"


class TestConflictError:
    """Test cases for ConflictError"""
    
    def test_conflict_error_default(self):
        """Test ConflictError with default message"""
        exc = ConflictError()
        
        assert exc.detail == "Resource conflict"
        assert exc.status_code == 409
        assert exc.error_code == "CONFLICT_ERROR"
    
    def test_conflict_error_custom_message(self):
        """Test ConflictError with custom message"""
        exc = ConflictError("Email already exists")
        
        assert exc.detail == "Email already exists"
        assert exc.status_code == 409
        assert exc.error_code == "CONFLICT_ERROR"


class TestAIProcessingError:
    """Test cases for AIProcessingError"""
    
    def test_ai_processing_error_default(self):
        """Test AIProcessingError with default message"""
        exc = AIProcessingError()
        
        assert exc.detail == "AI processing failed"
        assert exc.status_code == 422
        assert exc.error_code == "AI_PROCESSING_ERROR"
    
    def test_ai_processing_error_custom_message(self):
        """Test AIProcessingError with custom message"""
        exc = AIProcessingError("Groq API unavailable")
        
        assert exc.detail == "Groq API unavailable"
        assert exc.status_code == 422
        assert exc.error_code == "AI_PROCESSING_ERROR"


class TestBlockchainError:
    """Test cases for BlockchainError"""
    
    def test_blockchain_error_default(self):
        """Test BlockchainError with default message"""
        exc = BlockchainError()
        
        assert exc.detail == "Blockchain operation failed"
        assert exc.status_code == 502
        assert exc.error_code == "BLOCKCHAIN_ERROR"
    
    def test_blockchain_error_custom_message(self):
        """Test BlockchainError with custom message"""
        exc = BlockchainError("Hedera network unavailable")
        
        assert exc.detail == "Hedera network unavailable"
        assert exc.status_code == 502
        assert exc.error_code == "BLOCKCHAIN_ERROR"


class TestExternalServiceError:
    """Test cases for ExternalServiceError"""
    
    def test_external_service_error_default(self):
        """Test ExternalServiceError with default message"""
        exc = ExternalServiceError()
        
        assert exc.detail == "External service unavailable"
        assert exc.status_code == 503
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
    
    def test_external_service_error_custom_message(self):
        """Test ExternalServiceError with custom message"""
        exc = ExternalServiceError("Oracle service timeout")
        
        assert exc.detail == "Oracle service timeout"
        assert exc.status_code == 503
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"


class TestRateLimitError:
    """Test cases for RateLimitError"""
    
    def test_rate_limit_error_default(self):
        """Test RateLimitError with default message"""
        exc = RateLimitError()
        
        assert exc.detail == "Rate limit exceeded"
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_ERROR"
    
    def test_rate_limit_error_custom_message(self):
        """Test RateLimitError with custom message"""
        exc = RateLimitError("Too many requests per minute")
        
        assert exc.detail == "Too many requests per minute"
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_ERROR"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy"""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from CircularityNexusException"""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            ConflictError("test"),
            AIProcessingError("test"),
            BlockchainError("test"),
            ExternalServiceError("test"),
            RateLimitError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, CircularityNexusException)
            assert isinstance(exc, Exception)
    
    def test_exception_error_codes_are_unique(self):
        """Test all exceptions have unique error codes"""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            ConflictError("test"),
            AIProcessingError("test"),
            BlockchainError("test"),
            ExternalServiceError("test"),
            RateLimitError("test")
        ]
        
        error_codes = [exc.error_code for exc in exceptions]
        assert len(error_codes) == len(set(error_codes))  # All unique
    
    def test_exception_status_codes_are_valid_http(self):
        """Test all exceptions have valid HTTP status codes"""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            ConflictError("test"),
            AIProcessingError("test"),
            BlockchainError("test"),
            ExternalServiceError("test"),
            RateLimitError("test")
        ]
        
        for exc in exceptions:
            assert 400 <= exc.status_code < 600  # Valid HTTP error range
