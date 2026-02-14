"""
Advisory Service Database Migration
Create forums tables for Farm Connect

Revision ID: advisory_001
Revises: add_accounts_owner_index
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = 'advisory_001'
down_revision = 'add_accounts_owner_index'  # Update this to your latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Create advisory service tables for forums and moderation"""
    
    # Create enum types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE thread_status AS ENUM ('open', 'resolved', 'closed', 'archived');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE thread_category AS ENUM (
                'pest_disease', 'irrigation', 'fertilization', 'soil_health',
                'weather', 'harvest_storage', 'market_prices', 'equipment',
                'organic_farming', 'livestock', 'general'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE moderation_status AS ENUM ('pending', 'approved', 'rejected', 'flagged');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create forum_threads table
    op.create_table(
        'forum_threads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(220), nullable=False, unique=True),
        sa.Column('content_body', sa.Text, nullable=False),
        sa.Column('content_format', sa.String(20), default='markdown'),
        
        # Author info
        sa.Column('author_id', sa.String(36), nullable=False, index=True),
        sa.Column('author_username', sa.String(100), nullable=False),
        sa.Column('author_reputation', sa.Integer, default=0),
        sa.Column('author_badge', sa.String(50)),
        
        # Categorization
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(50)),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), default=[]),
        
        # Context
        #sa.Column('context_field_id', sa.String(36), nullable=True),
        #sa.Column('context_crop_cycle_id', sa.String(36), nullable=True),
        sa.Column('context_field_id', postgresql.UUID()),
        sa.Column('context_crop_cycle_id', postgresql.UUID()),
        sa.Column('context_crop_type', sa.String(100)),
        sa.Column('context_growth_stage', sa.String(50)),
        
        # Status
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('moderation_status', sa.String(20), default='approved'),
        sa.Column('moderation_notes', sa.Text),
        
        # Metrics
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('upvote_count', sa.Integer, default=0),
        sa.Column('downvote_count', sa.Integer, default=0),
        sa.Column('bookmark_count', sa.Integer, default=0),
        sa.Column('share_count', sa.Integer, default=0),
        
        # Resolution
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('accepted_answer_id', sa.String(36)),
        sa.Column('helpful_count', sa.Integer, default=0),
        sa.Column('resolution_summary', sa.Text),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now()),
        sa.Column('bumped_at', sa.DateTime, default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime, default=sa.func.now()),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['context_field_id'], ['fields.id'], ondelete='set null'),
    )
    
    # Create indexes for forum_threads
    op.create_index('idx_forum_threads_slug', 'forum_threads', ['slug'], unique=True)
    op.create_index('idx_forum_threads_category', 'forum_threads', ['category'])
    op.create_index('idx_forum_threads_status', 'forum_threads', ['status'])
    op.create_index('idx_forum_threads_author', 'forum_threads', ['author_id'])
    op.create_index('idx_forum_threads_bumped', 'forum_threads', ['bumped_at'])
    op.create_index('idx_forum_threads_created', 'forum_threads', ['created_at'])
    op.create_index('idx_forum_threads_context', 'forum_threads', ['context_field_id', 'context_crop_type'])
    op.create_index('idx_forum_threads_tags', 'forum_threads', ['tags'], postgresql_using='gin')
    
    # Create forum_comments table
    op.create_table(
        'forum_comments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('thread_id', sa.String(36), nullable=False, index=True),
        sa.Column('parent_id', sa.String(36)),
        
        # Author info
        sa.Column('author_id', sa.String(36), nullable=False, index=True),
        sa.Column('author_username', sa.String(100), nullable=False),
        sa.Column('author_reputation', sa.Integer, default=0),
        sa.Column('author_badge', sa.String(50)),
        
        # Content
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('content_format', sa.String(20), default='markdown'),
        sa.Column('attachments', postgresql.JSON, default=[]),
        
        # Moderation
        sa.Column('moderation_status', sa.String(20), default='approved'),
        sa.Column('moderation_notes', sa.Text),
        
        # Engagement
        sa.Column('upvote_count', sa.Integer, default=0),
        sa.Column('downvote_count', sa.Integer, default=0),
        
        # Status
        sa.Column('is_accepted_answer', sa.Boolean, default=False),
        sa.Column('is_edited', sa.Boolean, default=False),
        sa.Column('edit_history', postgresql.JSON, default=[]),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now()),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['parent_id'], ['forum_comments.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='cascade'),
    )
    
    # Create indexes for forum_comments
    op.create_index('idx_forum_comments_thread', 'forum_comments', ['thread_id'])
    op.create_index('idx_forum_comments_parent', 'forum_comments', ['parent_id'])
    op.create_index('idx_forum_comments_author', 'forum_comments', ['author_id'])
    op.create_index('idx_forum_comments_created', 'forum_comments', ['created_at'])
    
    # Create forum_votes table
    op.create_table(
        'forum_votes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('thread_id', sa.String(36)),
        sa.Column('comment_id', sa.String(36)),
        sa.Column('voter_id', sa.String(36), nullable=False, index=True),
        sa.Column('vote_type', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        
        # Constraints
        sa.CheckConstraint('(thread_id IS NOT NULL) OR (comment_id IS NOT NULL)'),
        sa.CheckConstraint("vote_type IN ('up', 'down')"),
        sa.UniqueConstraint('thread_id', 'voter_id', name='uq_thread_vote'),
        sa.UniqueConstraint('comment_id', 'voter_id', name='uq_comment_vote'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['comment_id'], ['forum_comments.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['voter_id'], ['users.id'], ondelete='cascade'),
    )
    
    # Create forum_bookmarks table
    op.create_table(
        'forum_bookmarks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('thread_id', sa.String(36), nullable=False, index=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('folder_name', sa.String(100)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='cascade'),
        
        # Unique constraint
        sa.UniqueConstraint('thread_id', 'user_id', name='uq_bookmark'),
    )
    
    # Create forum_reports table
    op.create_table(
        'forum_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('thread_id', sa.String(36)),
        sa.Column('comment_id', sa.String(36)),
        sa.Column('reporter_id', sa.String(36), nullable=False, index=True),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('report_reason', sa.Text, nullable=False),
        sa.Column('evidence', sa.Text),
        
        # Moderation
        sa.Column('assigned_moderator_id', sa.String(36)),
        sa.Column('moderation_status', sa.String(20), default='pending'),
        sa.Column('moderation_decision', sa.String(20)),
        sa.Column('moderation_notes', sa.Text),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['comment_id'], ['forum_comments.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['assigned_moderator_id'], ['users.id'], ondelete='set null'),
    )
    
    # Create indexes for forum_reports
    op.create_index('idx_forum_reports_status', 'forum_reports', ['moderation_status'])
    op.create_index('idx_forum_reports_type', 'forum_reports', ['report_type'])
    op.create_index('idx_forum_reports_created', 'forum_reports', ['created_at'])
    
    # Create user_notifications table
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('action_url', sa.String(500)),
        
        # Context
        sa.Column('thread_id', sa.String(36)),
        sa.Column('comment_id', sa.String(36)),
        sa.Column('article_id', sa.String(36)),
        sa.Column('from_user_id', sa.String(36)),
        sa.Column('from_user_name', sa.String(100)),
        
        # Delivery
        sa.Column('channels', postgresql.ARRAY(sa.String(20)), default=['in_app']),
        sa.Column('channel_status', postgresql.JSON, default={}),
        
        # Status
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('read_at', sa.DateTime),
        sa.Column('priority', sa.String(20), default='normal'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='cascade'),
        sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ondelete='set null'),
        sa.ForeignKeyConstraint(['comment_id'], ['forum_comments.id'], ondelete='set null'),
    )
    
    # Create indexes for user_notifications
    op.create_index('idx_user_notifications_user', 'user_notifications', ['user_id', 'is_read'])
    op.create_index('idx_user_notifications_type', 'user_notifications', ['notification_type'])
    op.create_index('idx_user_notifications_created', 'user_notifications', ['created_at'])
    
    # Create user_notification_preferences table
    op.create_table(
        'user_notification_preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, unique=True),
        
        # Channel preferences
        sa.Column('email_enabled', sa.Boolean, default=True),
        sa.Column('sms_enabled', sa.Boolean, default=False),
        sa.Column('push_enabled', sa.Boolean, default=True),
        sa.Column('in_app_enabled', sa.Boolean, default=True),
        
        # Type preferences
        sa.Column('reply_notifications', sa.Boolean, default=True),
        sa.Column('upvote_notifications', sa.Boolean, default=True),
        sa.Column('mention_notifications', sa.Boolean, default=True),
        sa.Column('moderation_notifications', sa.Boolean, default=True),
        sa.Column('article_notifications', sa.Boolean, default=False),
        
        # Frequency
        sa.Column('email_digest', sa.String(20), default='immediate'),
        sa.Column('max_daily_notifications', sa.Integer, default=50),
        
        # Quiet hours
        sa.Column('quiet_hours_enabled', sa.Boolean, default=False),
        sa.Column('quiet_hours_start', sa.Integer),
        sa.Column('quiet_hours_end', sa.Integer),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now()),
        
        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='cascade'),
    )


def downgrade():
    """Drop advisory service tables"""
    
    # Drop tables in reverse order
    op.drop_table('user_notification_preferences')
    op.drop_table('user_notifications')
    op.drop_table('forum_reports')
    op.drop_table('forum_bookmarks')
    op.drop_table('forum_votes')
    op.drop_table('forum_comments')
    op.drop_table('forum_threads')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS thread_status CASCADE")
    op.execute("DROP TYPE IF EXISTS thread_category CASCADE")
    op.execute("DROP TYPE IF EXISTS moderation_status CASCADE")
