"""add_new_roles_to_user_role_enum

Revision ID: dbaab859c21c
Revises: a8391ae9c1a3
Create Date: 2026-02-14 11:27:44.928892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbaab859c21c'
down_revision: Union[str, Sequence[str], None] = 'a8391ae9c1a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum ADD VALUE 'MODERATOR'; EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum ADD VALUE 'AGRONOMIST'; EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum ADD VALUE 'FIELD_ANALYST'; EXCEPTION WHEN duplicate_object THEN null; END $$;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum DROP VALUE 'MODERATOR'; EXCEPTION WHEN undefined_object THEN null; END $$;")
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum DROP VALUE 'AGRONOMIST'; EXCEPTION WHEN undefined_object THEN null; END $$;")
    op.execute("DO $$ BEGIN ALTER TYPE user_role_enum DROP VALUE 'FIELD_ANALYST'; EXCEPTION WHEN undefined_object THEN null; END $$;")
