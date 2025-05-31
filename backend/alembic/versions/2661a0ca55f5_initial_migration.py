"""initial migration

Revision ID: 2661a0ca55f5
Revises: 
Create Date: 2025-05-25 13:14:29.536769

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '2661a0ca55f5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create pgvector extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('microsoft_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('microsoft_id')
    )
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id'),
        sa.UniqueConstraint('user_id', 'project_name', name='uq_projects_user_id_project_name')
    )
    
    # Create shared_projects table
    op.create_table(
        'shared_projects',
        sa.Column('shared_project_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('shared_with_user_id', sa.UUID(), nullable=True),
        sa.Column('share_token', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('shared_project_id'),
        sa.UniqueConstraint('share_token')
    )
    
    # Create urls table
    op.create_table(
        'urls',
        sa.Column('url_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('original_url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('url_id'),
        sa.UniqueConstraint('project_id', 'original_url', name='uq_urls_project_id_original_url')
    )
    
    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('chunk_id', sa.UUID(), nullable=False),
        sa.Column('url_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id']),
        sa.ForeignKeyConstraint(['url_id'], ['urls.url_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    
    # Create HNSW index on chunks.embedding for efficient similarity search
    op.execute(
        'CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_l2_ops)'
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('chunks')
    op.drop_table('urls')
    op.drop_table('shared_projects')
    op.drop_table('projects')
    op.drop_table('users')
    # No need to drop the pgvector extension as other databases might be using it
