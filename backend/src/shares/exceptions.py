from src.shares.constants import ErrorCode


class ShareNotFoundException(Exception):
    def __init__(self, message: str = "Share not found"):
        self.message = message
        self.error_code = ErrorCode.SHARE_NOT_FOUND
        super().__init__(self.message)


class ShareTokenNotFoundException(Exception):
    def __init__(self, message: str = "Share token not found"):
        self.message = message
        self.error_code = ErrorCode.SHARE_TOKEN_NOT_FOUND
        super().__init__(self.message)


class ProjectAlreadySharedException(Exception):
    def __init__(self, message: str = "Project already shared"):
        self.message = message
        self.error_code = ErrorCode.PROJECT_ALREADY_SHARED
        super().__init__(self.message)


class CannotShareWithSelfException(Exception):
    def __init__(self, message: str = "Cannot share project with yourself"):
        self.message = message
        self.error_code = ErrorCode.CANNOT_SHARE_WITH_SELF
        super().__init__(self.message)


class InvalidShareTokenException(Exception):
    def __init__(self, message: str = "Invalid share token"):
        self.message = message
        self.error_code = ErrorCode.INVALID_SHARE_TOKEN
        super().__init__(self.message)


class AccessDeniedException(Exception):
    def __init__(self, message: str = "Access denied"):
        self.message = message
        self.error_code = ErrorCode.ACCESS_DENIED
        super().__init__(self.message)
