"""refactor_knowledge_articles

Revision ID: 0143ba166256
Revises: dbaab859c21c
Create Date: 2026-02-14 14:09:58.601199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0143ba166256'
down_revision: Union[str, Sequence[str], None] = 'dbaab859c21c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old metadata column and topic enum dependency
    op.execute("ALTER TABLE knowledge_articles DROP COLUMN IF EXISTS metadata")
    op.execute("ALTER TABLE knowledge_articles DROP COLUMN IF EXISTS topic")
    
    # Add new columns to knowledge_articles
    op.add_column('knowledge_articles', sa.Column('content_format', sa.String(20), server_default='markdown'))
    op.add_column('knowledge_articles', sa.Column('article_type', sa.String(50), nullable=False, server_default='best_practice'))
    op.add_column('knowledge_articles', sa.Column('category', sa.String(50), nullable=False, server_default='general'))
    op.add_column('knowledge_articles', sa.Column('subcategory', sa.String(50), nullable=True))
    op.add_column('knowledge_articles', sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'))
    # author_id already exists from a8391ae9c1a3
    op.add_column('knowledge_articles', sa.Column('author_username', sa.String(100), nullable=False, server_default='unknown'))
    op.add_column('knowledge_articles', sa.Column('author_badge', sa.String(50), nullable=True))
    op.add_column('knowledge_articles', sa.Column('contributors', postgresql.ARRAY(sa.String()), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('reviewer_id', sa.String(), nullable=True))
    op.add_column('knowledge_articles', sa.Column('review_status', sa.String(20), server_default='pending'))
    op.add_column('knowledge_articles', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('knowledge_articles', sa.Column('version', sa.Integer(), server_default='1'))
    op.add_column('knowledge_articles', sa.Column('previous_versions', sa.Text(), nullable=True))
    op.add_column('knowledge_articles', sa.Column('change_summary', sa.Text(), nullable=True))
    op.add_column('knowledge_articles', sa.Column('related_crop_types', postgresql.ARRAY(sa.String(50)), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('related_regions', postgresql.ARRAY(sa.String(50)), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('related_articles', postgresql.ARRAY(sa.String()), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('linked_treatments', postgresql.ARRAY(sa.String()), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('keywords', postgresql.ARRAY(sa.String(50)), server_default='{}'))
    op.add_column('knowledge_articles', sa.Column('search_vector', sa.Text(), nullable=True))
    op.add_column('knowledge_articles', sa.Column('view_count', sa.Integer(), server_default='0'))
    op.add_column('knowledge_articles', sa.Column('helpful_count', sa.Integer(), server_default='0'))
    op.add_column('knowledge_articles', sa.Column('not_helpful_count', sa.Integer(), server_default='0'))
    op.add_column('knowledge_articles', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('knowledge_articles', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    
    # Create indexes
    op.create_index('idx_knowledge_articles_category_status', 'knowledge_articles', ['category', 'status'])
    op.create_index('idx_knowledge_articles_type_status', 'knowledge_articles', ['article_type', 'status'])
    op.create_index('idx_knowledge_articles_published', 'knowledge_articles', ['published_at'])
    
    # Create knowledge_article_versions table
    op.create_table(
        'knowledge_article_versions',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_id', postgresql.UUID(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_format', sa.String(20), server_default='markdown'),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('editor_id', sa.String(), nullable=False),
        sa.Column('editor_username', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['article_id'], ['knowledge_articles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_versions_article', 'knowledge_article_versions', ['article_id', 'version_number'])
    
    # Create knowledge_article_ratings table
    op.create_table(
        'knowledge_article_ratings',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('is_helpful', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['article_id'], ['knowledge_articles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_ratings_unique', 'knowledge_article_ratings', ['article_id', 'user_id'], unique=True)
    op.create_index('idx_knowledge_ratings_user', 'knowledge_article_ratings', ['user_id'])
    
    # Create knowledge_categories table
    op.create_table(
        'knowledge_categories',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('parent_id', postgresql.UUID(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('article_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['parent_id'], ['knowledge_categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_knowledge_categories_slug', 'knowledge_categories', ['slug'])
    
    # Create article_search_queries table
    op.create_table(
        'article_search_queries',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('query_text', sa.String(200), nullable=False),
        sa.Column('results_count', sa.Integer(), server_default='0'),
        sa.Column('clicked_article_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_search_queries_daily', 'article_search_queries', ['query_text', 'created_at'])
    op.create_index('idx_search_queries_text', 'article_search_queries', ['query_text'])
    op.create_index('idx_search_queries_clicked', 'article_search_queries', ['clicked_article_id'])
    op.create_index('idx_search_queries_user', 'article_search_queries', ['user_id'])
    op.create_index('idx_search_queries_created', 'article_search_queries', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new tables
    op.drop_table('article_search_queries')
    op.drop_table('knowledge_categories')
    op.drop_table('knowledge_article_ratings')
    op.drop_table('knowledge_article_versions')
    
    # Drop indexes
    op.drop_index('idx_knowledge_articles_published', 'knowledge_articles')
    op.drop_index('idx_knowledge_articles_type_status', 'knowledge_articles')
    op.drop_index('idx_knowledge_articles_category_status', 'knowledge_articles')
    
    # Drop new columns
    op.drop_column('knowledge_articles', 'updated_at')
    op.drop_column('knowledge_articles', 'expires_at')
    op.drop_column('knowledge_articles', 'not_helpful_count')
    op.drop_column('knowledge_articles', 'helpful_count')
    op.drop_column('knowledge_articles', 'view_count')
    op.drop_column('knowledge_articles', 'search_vector')
    op.drop_column('knowledge_articles', 'keywords')
    op.drop_column('knowledge_articles', 'linked_treatments')
    op.drop_column('knowledge_articles', 'related_articles')
    op.drop_column('knowledge_articles', 'related_regions')
    # author_id should not be dropped as it existed before this migration
    op.drop_column('knowledge_articles', 'related_crop_types')
    op.drop_column('knowledge_articles', 'change_summary')
    op.drop_column('knowledge_articles', 'previous_versions')
    op.drop_column('knowledge_articles', 'version')
    op.drop_column('knowledge_articles', 'approved_at')
    op.drop_column('knowledge_articles', 'review_status')
    op.drop_column('knowledge_articles', 'reviewer_id')
    op.drop_column('knowledge_articles', 'contributors')
    op.drop_column('knowledge_articles', 'author_badge')
    op.drop_column('knowledge_articles', 'author_username')
    op.drop_column('knowledge_articles', 'tags')
    op.drop_column('knowledge_articles', 'subcategory')
    op.drop_column('knowledge_articles', 'category')
    op.drop_column('knowledge_articles', 'article_type')
    op.drop_column('knowledge_articles', 'content_format')
    
    # Restore old columns
    op.add_column('knowledge_articles', sa.Column('topic', sa.Enum('CROP_SELECTION', 'PEST_MANAGEMENT', 'DISEASE_MANAGEMENT', 'SOIL_HEALTH', 'IRRIGATION', 'FERTILIZATION', 'HARVEST_TIMING', 'POST_HARVEST', 'MARKET_ADVICE', 'FINANCIAL_PLANNING', 'GENERAL', name='advisory_topic'), nullable=False))
    op.add_column('knowledge_articles', sa.Column('metadata', postgresql.JSONB(), server_default='{}'))