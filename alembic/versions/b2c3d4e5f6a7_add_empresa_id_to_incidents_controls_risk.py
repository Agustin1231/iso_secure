"""Add empresa_id to incidents, controls and risk_levels

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS empresa_id UUID
        REFERENCES empresas(id) ON DELETE SET NULL
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_incidents_empresa_id ON incidents(empresa_id)")

    op.execute("""
        ALTER TABLE controls
        ADD COLUMN IF NOT EXISTS empresa_id UUID
        REFERENCES empresas(id) ON DELETE SET NULL
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_controls_empresa_id ON controls(empresa_id)")

    op.execute("""
        ALTER TABLE risk_levels
        ADD COLUMN IF NOT EXISTS empresa_id UUID
        REFERENCES empresas(id) ON DELETE SET NULL
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_risk_levels_empresa_id ON risk_levels(empresa_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_incidents_empresa_id")
    op.execute("ALTER TABLE incidents DROP COLUMN IF EXISTS empresa_id")

    op.execute("DROP INDEX IF EXISTS ix_controls_empresa_id")
    op.execute("ALTER TABLE controls DROP COLUMN IF EXISTS empresa_id")

    op.execute("DROP INDEX IF EXISTS ix_risk_levels_empresa_id")
    op.execute("ALTER TABLE risk_levels DROP COLUMN IF EXISTS empresa_id")
