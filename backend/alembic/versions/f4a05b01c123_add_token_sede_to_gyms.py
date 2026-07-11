"""add token_sede to gyms and update subscription status values

Revision ID: f4a05b01c123
Revises: 5e13ef50a67b
Create Date: 2026-07-10 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4a05b01c123'
down_revision: Union[str, Sequence[str], None] = '5e13ef50a67b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add token_sede UUID column to gyms table for onboarding flow."""
    op.add_column('gyms', sa.Column('token_sede', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint('uq_gyms_token_sede', 'gyms', ['token_sede'])
    op.create_index('ix_gyms_token_sede', 'gyms', ['token_sede'])


def downgrade() -> None:
    """Remove token_sede column."""
    op.drop_index('ix_gyms_token_sede', 'gyms')
    op.drop_constraint('uq_gyms_token_sede', 'gyms', type_='unique')
    op.drop_column('gyms', 'token_sede')
