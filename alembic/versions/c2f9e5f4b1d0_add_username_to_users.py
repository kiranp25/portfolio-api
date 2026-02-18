"""add username to users

Revision ID: c2f9e5f4b1d0
Revises: ba3178f67c22
Create Date: 2026-02-15 00:00:00.000002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2f9e5f4b1d0"
down_revision: Union[str, Sequence[str], None] = "ba3178f67c22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=80), nullable=True))

    op.execute(
        """
        UPDATE users
        SET username = (
            COALESCE(
                NULLIF(regexp_replace(lower(split_part(email_id, '@', 1)), '[^a-z0-9_]+', '', 'g'), ''),
                'user'
            ) || '_' || id::text
        )
        WHERE username IS NULL
        """
    )

    op.alter_column("users", "username", existing_type=sa.String(length=80), nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
