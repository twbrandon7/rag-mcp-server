from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    project_name: str


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    project_name: str


class ProjectResponse(BaseModel):
    """Schema for project response."""
    project_id: UUID4
    user_id: UUID4
    project_name: str
    created_at: datetime


class ProjectListResponse(BaseModel):
    """Schema for a project in list response."""
    project_id: UUID4
    created_at: datetime
