
from enum import Enum, auto


class ErrorCode(str, Enum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    INACTIVE_USER = "INACTIVE_USER"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_EXISTS = "EMAIL_EXISTS"
