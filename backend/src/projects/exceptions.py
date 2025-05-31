from fastapi import HTTPException, status

from src.projects.constants import ErrorCode


class ProjectNotFoundException(HTTPException):
    """Exception raised when a project is not found."""
    
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
            headers={"X-Error-Code": ErrorCode.PROJECT_NOT_FOUND}
        )


class DuplicateProjectNameException(HTTPException):
    """Exception raised when a user tries to create a project with a name that already exists."""
    
    def __init__(self, project_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_name}' already exists for this user",
            headers={"X-Error-Code": ErrorCode.DUPLICATE_PROJECT_NAME}
        )


class UnauthorizedProjectAccessException(HTTPException):
    """Exception raised when a user tries to access a project they don't own."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project",
            headers={"X-Error-Code": ErrorCode.UNAUTHORIZED_ACCESS}
        )
