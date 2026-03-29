"""
Script de migración automática — se ejecuta al iniciar el contenedor.
Idempotente: puede correr múltiples veces sin romper la DB.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")


async def run_migrations():
    try:
        import asyncpg
    except ImportError:
        print("[migrate] asyncpg no disponible, saltando migración.")
        return

    # Convertir URL de SQLAlchemy a asyncpg (quitar el '+asyncpg' del scheme)
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    if not url:
        print("[migrate] DATABASE_URL no configurada, saltando migración.")
        return

    print("[migrate] Conectando a la base de datos...")
    try:
        conn = await asyncpg.connect(url, timeout=15)
    except Exception as e:
        print(f"[migrate] No se pudo conectar: {e}")
        print("[migrate] Continuando sin migración (la base de datos puede no estar disponible).")
        return

    print("[migrate] Conexión exitosa. Aplicando migraciones...")

    migrations = [

        # ── 1. controlstatusenum: partial → en_proceso ──────────────────────
        (
            "Renombrar enum 'partial' → 'en_proceso'",
            """
            DO $$ BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON e.enumtypid = t.oid
                    WHERE t.typname = 'controlstatusenum'
                    AND e.enumlabel = 'partial'
                ) THEN
                    ALTER TABLE controls ALTER COLUMN status TYPE text;
                    DROP TYPE IF EXISTS controlstatusenum;
                    CREATE TYPE controlstatusenum AS ENUM ('compliant', 'en_proceso', 'non_compliant');
                    UPDATE controls SET status = 'en_proceso' WHERE status = 'partial';
                    ALTER TABLE controls
                        ALTER COLUMN status TYPE controlstatusenum
                        USING status::controlstatusenum;
                    RAISE NOTICE 'Enum controlstatusenum actualizado.';
                ELSE
                    RAISE NOTICE 'Enum ya actualizado, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 2. kpi_snapshots: controls_partial → controls_en_proceso ────────
        (
            "Renombrar columna controls_partial → controls_en_proceso",
            """
            DO $$ BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'kpi_snapshots'
                    AND column_name = 'controls_partial'
                ) THEN
                    ALTER TABLE kpi_snapshots
                        RENAME COLUMN controls_partial TO controls_en_proceso;
                    RAISE NOTICE 'Columna renombrada.';
                ELSE
                    RAISE NOTICE 'Columna ya renombrada, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 3. Tipo userroleenum ─────────────────────────────────────────────
        (
            "Crear tipo userroleenum",
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'userroleenum'
                ) THEN
                    CREATE TYPE userroleenum AS ENUM ('admin', 'auditor', 'supervisor', 'analista');
                    RAISE NOTICE 'Tipo userroleenum creado.';
                ELSE
                    RAISE NOTICE 'Tipo userroleenum ya existe, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 4. Tabla empresas ────────────────────────────────────────────────
        (
            "Crear tabla empresas",
            """
            CREATE TABLE IF NOT EXISTS empresas (
                id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                nombre           VARCHAR(200) NOT NULL,
                tipo_empresa     VARCHAR(100) NOT NULL,
                actividad_economica VARCHAR(200) NOT NULL,
                representante_legal VARCHAR(150) NOT NULL,
                email            VARCHAR(150),
                telefono         VARCHAR(50),
                nit              VARCHAR(50),
                direccion        VARCHAR(300),
                created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ),

        # ── 5. Tabla user_profiles ───────────────────────────────────────────
        (
            "Crear tabla user_profiles",
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id     UUID NOT NULL UNIQUE,
                email       VARCHAR(200),
                role        userroleenum NOT NULL DEFAULT 'analista',
                empresa_id  UUID REFERENCES empresas(id) ON DELETE SET NULL,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ),
    ]

    all_ok = True
    for name, sql in migrations:
        try:
            await conn.execute(sql)
            print(f"[migrate] ✓ {name}")
        except Exception as e:
            print(f"[migrate] ✗ {name}: {e}")
            all_ok = False

    await conn.close()

    if all_ok:
        print("[migrate] Todas las migraciones aplicadas correctamente.")
    else:
        print("[migrate] Algunas migraciones fallaron. Revisa los logs.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_migrations())
