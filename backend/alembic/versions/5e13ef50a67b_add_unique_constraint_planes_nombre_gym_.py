"""add unique constraint planes nombre gym_id

Revision ID: 5e13ef50a67b
Revises: b7d3f1a9c8e2
Create Date: 2026-07-10 21:14:49.818833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e13ef50a67b'
down_revision: Union[str, Sequence[str], None] = 'b7d3f1a9c8e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on planes(nombre, gym_id)."""
    op.create_unique_constraint('uq_plan_nombre_gym', 'planes', ['nombre', 'gym_id'])


def downgrade() -> None:
    """Remove unique constraint on planes(nombre, gym_id)."""
    op.drop_constraint('uq_plan_nombre_gym', 'planes', type_='unique')
