-- ============================================================
-- FASE 1 - Migración ISO_SECURE
-- Aplicar en: Supabase Dashboard → SQL Editor
-- ============================================================

-- 1. Renombrar enum value: partial → en_proceso
ALTER TABLE controls ALTER COLUMN status TYPE text;
DROP TYPE IF EXISTS controlstatusenum;
CREATE TYPE controlstatusenum AS ENUM ('compliant', 'en_proceso', 'non_compliant');
UPDATE controls SET status = 'en_proceso' WHERE status = 'partial';
ALTER TABLE controls ALTER COLUMN status TYPE controlstatusenum USING status::controlstatusenum;

-- 2. Renombrar columna controls_partial → controls_en_proceso
ALTER TABLE kpi_snapshots RENAME COLUMN controls_partial TO controls_en_proceso;

-- 3. Crear tipo de roles
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userroleenum') THEN
        CREATE TYPE userroleenum AS ENUM ('admin', 'auditor', 'supervisor', 'analista');
    END IF;
END $$;

-- 4. Crear tabla empresas
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
);

-- 5. Crear tabla user_profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    email VARCHAR(200),
    role userroleenum NOT NULL DEFAULT 'analista',
    empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Verificación final
SELECT 'Migración completada exitosamente' AS resultado;
