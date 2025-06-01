from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ShareTokenCreate(BaseModel):
    """Schema for creating a public share token"""
    pass


class ShareWithUserCreate(BaseModel):
    """Schema for sharing with a specific user"""
    shared_with_user_id: UUID


class ShareUpdate(BaseModel):
    """Schema for updating share settings"""
    shared_with_user_id: Optional[UUID] = None


class ShareResponse(BaseModel):
    """Response schema for share operations"""
    share_id: UUID
    project_id: UUID
    shared_with_user_id: Optional[UUID]
    share_token: Optional[str]
    created_at: str


class PublicShareResponse(BaseModel):
    """Response schema for public share token creation"""
    share_id: UUID
    project_id: UUID
    share_token: str
    created_at: str


class SharedProjectInfo(BaseModel):
    """Schema for shared project information"""
    project_id: UUID
    project_name: str
    owner_email: str
    shared_at: str
