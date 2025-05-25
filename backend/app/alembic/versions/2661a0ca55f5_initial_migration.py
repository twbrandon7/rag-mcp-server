"""initial migration

Revision ID: 2661a0ca55f5
Revises: 
Create Date: 2025-05-25 13:14:29.536769

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


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
        'user',
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
        'project',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id'),
        sa.UniqueConstraint('user_id', 'project_name', name='uq_projects_user_id_project_name')
    )
    
    # Create shared_projects table
    op.create_table(
        'sharedproject',
        sa.Column('shared_project_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('shared_with_user_id', sa.UUID(), nullable=True),
        sa.Column('share_token', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_user_id'], ['user.user_id']),
        sa.PrimaryKeyConstraint('shared_project_id'),
        sa.UniqueConstraint('share_token')
    )
    
    # Create urls table
    op.create_table(
        'url',
        sa.Column('url_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('original_url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('url_id'),
        sa.UniqueConstraint('project_id', 'original_url', name='uq_urls_project_id_original_url')
    )
    
    # Create chunks table
    op.create_table(
        'chunk',
        sa.Column('chunk_id', sa.UUID(), nullable=False),
        sa.Column('url_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.ARRAY(sa.Float), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id']),
        sa.ForeignKeyConstraint(['url_id'], ['url.url_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    
    # Create vector column using pgvector
    op.execute(
        'ALTER TABLE chunk ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector'
    )
    
    # Create HNSW index on chunks.embedding for efficient similarity search
    op.execute(
        'CREATE INDEX idx_chunks_embedding ON chunk USING hnsw (embedding vector_l2_ops)'
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('chunk')
    op.drop_table('url')
    op.drop_table('sharedproject')
    op.drop_table('project')
    op.drop_table('user')
    # No need to drop the pgvector extension as other databases might be using it
