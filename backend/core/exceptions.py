"""Application exception hierarchy.

Raised by services and repositories; converted to HTTP responses by the
global exception handler. No FastAPI or HTTP imports here.
"""


class AppError(Exception):
    """Base class for all application errors."""

    message: str = "An unexpected error occurred."
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str | None = None) -> None:
        self.message = message if message is not None else self.__class__.message
        super().__init__(self.message)


class NotFoundError(AppError):
    message = "The requested resource was not found."
    code = "NOT_FOUND"
    status_code = 404


class PermissionDenied(AppError):
    message = "You do not have permission to perform this action."
    code = "PERMISSION_DENIED"
    status_code = 403


class ValidationError(AppError):
    message = "The provided data is invalid."
    code = "VALIDATION_ERROR"
    status_code = 422


class ConflictError(AppError):
    message = "A conflict occurred with the current state of the resource."
    code = "CONFLICT"
    status_code = 409


class InvalidStateTransition(AppError):
    message = "This state transition is not permitted."
    code = "INVALID_STATE_TRANSITION"
    status_code = 400


class InsufficientStockError(AppError):
    message = "Insufficient stock to fulfil this request."
    code = "INSUFFICIENT_STOCK"
    status_code = 409


class AccountSuspended(AppError):
    message = "This account has been suspended."
    code = "ACCOUNT_SUSPENDED"
    status_code = 403


class TokenExpired(AppError):
    message = "The token has expired."
    code = "TOKEN_EXPIRED"
    status_code = 401


class InvalidToken(AppError):
    message = "The token is invalid."
    code = "INVALID_TOKEN"
    status_code = 401
