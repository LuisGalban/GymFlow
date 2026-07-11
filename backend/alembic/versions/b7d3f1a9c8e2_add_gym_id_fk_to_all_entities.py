"""add_gym_id_fk_to_all_entities

Revision ID: b7d3f1a9c8e2
Revises: 3a1b3e4c25be
Create Date: 2026-07-10 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d3f1a9c8e2'
down_revision: Union[str, Sequence[str], None] = '3a1b3e4c25be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add gym_id FK (NOT NULL) to usuarios, miembros, planes, pagos, asistencias."""

    # 1. Add gym_id as nullable first to allow data seeding
    for table in ['usuarios', 'miembros', 'planes', 'pagos', 'asistencias']:
        op.add_column(table, sa.Column('gym_id', sa.Integer(), nullable=True))

    # 2. Seed default gym if not exists
    op.execute(
        "INSERT INTO gyms (nombre, direccion, dias_gracia_default, moneda_base, fecha_alta, estado_suscripcion, estado_logico) "
        "VALUES ('GymFlow Sede Central', 'Sede Principal', 5, 'USD', now(), 'activo', true) "
        "ON CONFLICT (nombre) DO NOTHING"
    )

    # 3. Update all existing rows with gym_id=1
    for table in ['usuarios', 'miembros', 'planes', 'pagos', 'asistencias']:
        op.execute(f"UPDATE {table} SET gym_id = 1 WHERE gym_id IS NULL")

    # 4. Add FK constraints and alter columns to NOT NULL
    op.alter_column('usuarios', 'gym_id', nullable=False)
    op.create_foreign_key('fk_usuarios_gym_id', 'usuarios', 'gyms', ['gym_id'], ['id'], ondelete='RESTRICT')

    op.alter_column('miembros', 'gym_id', nullable=False)
    op.create_foreign_key('fk_miembros_gym_id', 'miembros', 'gyms', ['gym_id'], ['id'], ondelete='RESTRICT')

    op.alter_column('planes', 'gym_id', nullable=False)
    op.create_foreign_key('fk_planes_gym_id', 'planes', 'gyms', ['gym_id'], ['id'], ondelete='RESTRICT')

    op.alter_column('pagos', 'gym_id', nullable=False)
    op.create_foreign_key('fk_pagos_gym_id', 'pagos', 'gyms', ['gym_id'], ['id'], ondelete='RESTRICT')

    op.alter_column('asistencias', 'gym_id', nullable=False)
    op.create_foreign_key('fk_asistencias_gym_id', 'asistencias', 'gyms', ['gym_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    """Remove gym_id FK from all entities."""
    op.drop_constraint('fk_usuarios_gym_id', 'usuarios', type_='foreignkey')
    op.drop_column('usuarios', 'gym_id')

    op.drop_constraint('fk_miembros_gym_id', 'miembros', type_='foreignkey')
    op.drop_column('miembros', 'gym_id')

    op.drop_constraint('fk_planes_gym_id', 'planes', type_='foreignkey')
    op.drop_column('planes', 'gym_id')

    op.drop_constraint('fk_pagos_gym_id', 'pagos', type_='foreignkey')
    op.drop_column('pagos', 'gym_id')

    op.drop_constraint('fk_asistencias_gym_id', 'asistencias', type_='foreignkey')
    op.drop_column('asistencias', 'gym_id')
