"""fix_apply_unique_constraint_planes

Revision ID: a229e190aabc
Revises: f4a05b01c123
Create Date: 2026-07-11 13:24:30.889546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a229e190aabc'
down_revision: Union[str, Sequence[str], None] = 'f4a05b01c123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply the unique constraint on planes(nombre, gym_id) that was missed in 5e13ef50a67b."""
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_plan_nombre_gym'
            ) THEN
                ALTER TABLE planes ADD CONSTRAINT uq_plan_nombre_gym UNIQUE (nombre, gym_id);
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    """Remove the unique constraint on planes(nombre, gym_id)."""
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_plan_nombre_gym'
            ) THEN
                ALTER TABLE planes DROP CONSTRAINT uq_plan_nombre_gym;
            END IF;
        END
        $$;
    """)
