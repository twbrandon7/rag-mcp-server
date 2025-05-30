import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlmodel import Field, Relationship, SQLModel
from pgvector.sqlalchemy import Vector


# User related models
class UserBase(SQLModel):
    email: str = Field(max_length=255, unique=True, nullable=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(SQLModel):
    email: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


# Database model for users table
class User(UserBase, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: Optional[str] = Field(default=None, max_length=255)
    google_id: Optional[str] = Field(default=None, max_length=255, unique=True)
    microsoft_id: Optional[str] = Field(default=None, max_length=255, unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"})


# Project related models
class ProjectBase(SQLModel):
    project_name: str = Field(max_length=255, nullable=False)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    project_name: Optional[str] = Field(default=None, max_length=255)


# Database model for projects table
class Project(ProjectBase, table=True):
    project_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    user: User = Relationship(back_populates="projects")
    urls: List["URL"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete"})
    shared_projects: List["SharedProject"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete"})
    
    __table_args__ = (
        UniqueConstraint("user_id", "project_name", name="uq_projects_user_id_project_name"),
    )


# Shared Project related models
class SharedProjectBase(SQLModel):
    share_token: Optional[str] = Field(default=None, max_length=255, unique=True)


class SharedProjectCreate(SharedProjectBase):
    project_id: uuid.UUID
    shared_with_user_id: Optional[uuid.UUID] = None


class SharedProjectUpdate(SQLModel):
    share_token: Optional[str] = Field(default=None, max_length=255)


# Database model for shared_projects table
class SharedProject(SharedProjectBase, table=True):
    shared_project_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.project_id", nullable=False)
    shared_with_user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.user_id")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    project: Project = Relationship(back_populates="shared_projects")


# URL related models
class URLBase(SQLModel):
    original_url: str = Field(nullable=False)
    status: str = Field(max_length=50, nullable=False, default="pending")
    failure_reason: Optional[str] = None


class URLCreate(URLBase):
    project_id: uuid.UUID


class URLUpdate(SQLModel):
    status: Optional[str] = Field(default=None, max_length=50)
    failure_reason: Optional[str] = None


# Database model for urls table
class URL(URLBase, table=True):
    url_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.project_id", nullable=False)
    submitted_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    project: Project = Relationship(back_populates="urls")
    chunks: List["Chunk"] = Relationship(back_populates="url", sa_relationship_kwargs={"cascade": "all, delete"})
    
    __table_args__ = (
        UniqueConstraint("project_id", "original_url", name="uq_urls_project_id_original_url"),
    )


# Chunk related models
class ChunkBase(SQLModel):
    content: str = Field(nullable=False)
    chunk_index: int = Field(nullable=False)


class ChunkCreate(ChunkBase):
    url_id: uuid.UUID
    project_id: uuid.UUID
    embedding: Optional[list[float]] = None


class ChunkUpdate(SQLModel):
    content: Optional[str] = None
    embedding: Optional[list[float]] = None
    chunk_index: Optional[int] = None


# Database model for chunks table
class Chunk(ChunkBase, table=True):
    chunk_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url_id: uuid.UUID = Field(foreign_key="url.url_id", nullable=False)
    project_id: uuid.UUID = Field(foreign_key="project.project_id", nullable=False)
    embedding: Optional[list[float]] = Field(
        sa_column=Column(Vector(384), nullable=False),
        default=None
    )
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    url: URL = Relationship(back_populates="chunks")


# Response models for API
class UserResponse(SQLModel):
    user_id: uuid.UUID
    email: str
    created_at: datetime


class ProjectResponse(SQLModel):
    project_id: uuid.UUID
    user_id: uuid.UUID
    project_name: str
    created_at: datetime


class SharedProjectResponse(SQLModel):
    shared_project_id: uuid.UUID
    project_id: uuid.UUID
    shared_with_user_id: Optional[uuid.UUID]
    share_token: Optional[str]
    created_at: datetime


class URLResponse(SQLModel):
    url_id: uuid.UUID
    project_id: uuid.UUID
    original_url: str
    status: str
    failure_reason: Optional[str]
    submitted_at: datetime
    last_updated_at: datetime


class ChunkResponse(SQLModel):
    chunk_id: uuid.UUID
    url_id: uuid.UUID
    project_id: uuid.UUID
    content: str
    chunk_index: int
    created_at: datetime


# Generic message and token models
class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
