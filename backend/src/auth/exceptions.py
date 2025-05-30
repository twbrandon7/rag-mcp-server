
from fastapi import HTTPException, status

from src.auth.constants import ErrorCode


class AuthException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: ErrorCode,
        headers: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            error_code=ErrorCode.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            error_code=ErrorCode.INVALID_TOKEN,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code=ErrorCode.USER_NOT_FOUND,
            headers=None,
        )


class EmailExistsException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
            error_code=ErrorCode.EMAIL_EXISTS,
            headers=None,
        )
