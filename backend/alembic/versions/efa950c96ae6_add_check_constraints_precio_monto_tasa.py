"""add_check_constraints_precio_monto_tasa

Revision ID: efa950c96ae6
Revises: 942c0e770a15
Create Date: 2026-07-09 01:20:23.423982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efa950c96ae6'
down_revision: Union[str, Sequence[str], None] = '942c0e770a15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint('ck_plan_precio_usd_no_negativo', 'planes', 'precio_usd >= 0')
    op.create_check_constraint('ck_pago_monto_original_positivo', 'pagos', 'monto_original > 0')
    op.create_check_constraint('ck_pago_tasa_cambio_positivo', 'pagos', 'tasa_cambio > 0')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_plan_precio_usd_no_negativo', 'planes', type_='check')
    op.drop_constraint('ck_pago_monto_original_positivo', 'pagos', type_='check')
    op.drop_constraint('ck_pago_tasa_cambio_positivo', 'pagos', type_='check')
