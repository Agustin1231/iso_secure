"""Phase 1: rename partial->en_proceso, add empresas and user_profiles

Revision ID: a1b2c3d4e5f6
Revises: f08358e89b83
Create Date: 2026-03-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f08358e89b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. Rename enum value: partial -> en_proceso in controlstatusenum    #
    # ------------------------------------------------------------------ #
    # Convert column to text to allow type drop/recreate
    op.execute("ALTER TABLE controls ALTER COLUMN status TYPE text")
    op.execute("DROP TYPE IF EXISTS controlstatusenum")
    op.execute("CREATE TYPE controlstatusenum AS ENUM ('compliant', 'en_proceso', 'non_compliant')")
    op.execute("UPDATE controls SET status = 'en_proceso' WHERE status = 'partial'")
    op.execute(
        "ALTER TABLE controls ALTER COLUMN status "
        "TYPE controlstatusenum USING status::controlstatusenum"
    )

    # ------------------------------------------------------------------ #
    # 2. Rename column controls_partial -> controls_en_proceso            #
    # ------------------------------------------------------------------ #
    op.alter_column('kpi_snapshots', 'controls_partial', new_column_name='controls_en_proceso')

    # ------------------------------------------------------------------ #
    # 3. Create userroleenum type                                         #
    # ------------------------------------------------------------------ #
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userroleenum') THEN
                CREATE TYPE userroleenum AS ENUM ('admin', 'auditor', 'supervisor', 'analista');
            END IF;
        END $$;
    """)

    # ------------------------------------------------------------------ #
    # 4. Create empresas table                                            #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre VARCHAR(200) NOT NULL,
            tipo_empresa VARCHAR(100) NOT NULL,
            actividad_economica VARCHAR(200) NOT NULL,
            representante_legal VARCHAR(150) NOT NULL,
            email VARCHAR(150),
            telefono VARCHAR(50),
            nit VARCHAR(50),
            direccion VARCHAR(300),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    # ------------------------------------------------------------------ #
    # 5. Create user_profiles table                                       #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE,
            email VARCHAR(200),
            role userroleenum NOT NULL DEFAULT 'analista',
            empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    # ------------------------------------------------------------------ #
    # Reverse order                                                       #
    # ------------------------------------------------------------------ #
    op.execute("DROP TABLE IF EXISTS user_profiles")
    op.execute("DROP TABLE IF EXISTS empresas")
    op.execute("DROP TYPE IF EXISTS userroleenum")

    # Rename controls_en_proceso back to controls_partial
    op.alter_column('kpi_snapshots', 'controls_en_proceso', new_column_name='controls_partial')

    # Restore controlstatusenum with partial
    op.execute("ALTER TABLE controls ALTER COLUMN status TYPE text")
    op.execute("DROP TYPE IF EXISTS controlstatusenum")
    op.execute("CREATE TYPE controlstatusenum AS ENUM ('compliant', 'partial', 'non_compliant')")
    op.execute("UPDATE controls SET status = 'partial' WHERE status = 'en_proceso'")
    op.execute(
        "ALTER TABLE controls ALTER COLUMN status "
        "TYPE controlstatusenum USING status::controlstatusenum"
    )
