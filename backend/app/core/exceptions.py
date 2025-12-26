from typing import Any, Optional


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(AppException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message, code="AUTHORIZATION_ERROR", details=details)


class ValidationError(AppException):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(AppException):
    """Raised when resource is not found."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class DatabaseError(AppException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database operation failed", details: Optional[Any] = None):
        super().__init__(message, code="DATABASE_ERROR", details=details)


class FileProcessingError(AppException):
    """Raised when file processing fails."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="FILE_PROCESSING_ERROR", details=details)
