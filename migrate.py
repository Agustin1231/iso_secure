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

        # ── 6. Tipos para capacitaciones ────────────────────────────────────
        (
            "Crear tipo nivelcursoenum",
            """
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nivelcursoenum') THEN
                    CREATE TYPE nivelcursoenum AS ENUM ('basico', 'intermedio', 'avanzado');
                    RAISE NOTICE 'Tipo nivelcursoenum creado.';
                ELSE
                    RAISE NOTICE 'Tipo nivelcursoenum ya existe, omitiendo.';
                END IF;
            END $$;
            """
        ),
        (
            "Crear tipo progresoenum",
            """
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'progresoenum') THEN
                    CREATE TYPE progresoenum AS ENUM ('pendiente', 'en_proceso', 'completado');
                    RAISE NOTICE 'Tipo progresoenum creado.';
                ELSE
                    RAISE NOTICE 'Tipo progresoenum ya existe, omitiendo.';
                END IF;
            END $$;
            """
        ),
        (
            "Crear tipo auditoriastatusenum",
            """
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'auditoriastatusenum') THEN
                    CREATE TYPE auditoriastatusenum AS ENUM ('pendiente', 'en_proceso', 'completado');
                    RAISE NOTICE 'Tipo auditoriastatusenum creado.';
                ELSE
                    RAISE NOTICE 'Tipo auditoriastatusenum ya existe, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 7. Tabla cursos ──────────────────────────────────────────────────
        (
            "Crear tabla cursos",
            """
            CREATE TABLE IF NOT EXISTS cursos (
                id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                titulo           VARCHAR(200) NOT NULL,
                descripcion      TEXT,
                video_url        VARCHAR(500),
                material_texto   TEXT,
                categoria        VARCHAR(100),
                nivel            nivelcursoenum NOT NULL DEFAULT 'basico',
                created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ),

        # ── 8. Tabla curso_progreso ──────────────────────────────────────────
        (
            "Crear tabla curso_progreso",
            """
            CREATE TABLE IF NOT EXISTS curso_progreso (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                curso_id    UUID NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
                user_id     UUID NOT NULL,
                status      progresoenum NOT NULL DEFAULT 'pendiente',
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (curso_id, user_id)
            );
            """
        ),

        # ── 9. Tabla auditoria_items ─────────────────────────────────────────
        (
            "Crear tabla auditoria_items",
            """
            CREATE TABLE IF NOT EXISTS auditoria_items (
                id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                empresa_id        UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
                iso_control_ref   VARCHAR(20),
                control_name      VARCHAR(200) NOT NULL,
                activity_desc     TEXT,
                status            auditoriastatusenum NOT NULL DEFAULT 'pendiente',
                notas             TEXT,
                auditor_id        UUID,
                fecha_evaluacion  DATE,
                created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ),

        # ── 10. Seed: incidentes activos iniciales ───────────────────────────
        (
            "Seed incidentes activos iniciales",
            """
            INSERT INTO incidents (id, title, description, severity, status, category, reported_by, reported_at)
            SELECT * FROM (VALUES
                (
                    gen_random_uuid(),
                    'Acceso no autorizado a servidor de archivos',
                    'Se detectó un intento de acceso desde una IP externa no registrada al servidor de archivos corporativo. El sistema bloqueó el acceso pero el evento quedó sin análisis forense.',
                    'high'::severityenum,
                    'open'::incidentstatusenum,
                    'Control de Acceso',
                    'Sistema de Monitoreo',
                    NOW() - INTERVAL '2 days'
                ),
                (
                    gen_random_uuid(),
                    'Credenciales de usuario comprometidas',
                    'Un usuario reportó que sus credenciales de correo fueron utilizadas desde una ubicación geográfica desconocida. Se sospecha phishing. El usuario fue bloqueado preventivamente.',
                    'critical'::severityenum,
                    'in_progress'::incidentstatusenum,
                    'Gestión de Identidades',
                    'Help Desk',
                    NOW() - INTERVAL '5 days'
                ),
                (
                    gen_random_uuid(),
                    'Política de contraseñas no aplicada en sistemas legacy',
                    'Auditoría interna detectó que 3 sistemas legacy no aplican la política de rotación de contraseñas cada 90 días definida en el Anexo A.5.17.',
                    'medium'::severityenum,
                    'open'::incidentstatusenum,
                    'Cumplimiento',
                    'Auditoría Interna',
                    NOW() - INTERVAL '7 days'
                ),
                (
                    gen_random_uuid(),
                    'Backup sin cifrar en almacenamiento en nube',
                    'Se identificó que los backups automáticos diarios se están almacenando en S3 sin cifrado en reposo, incumpliendo el control A.8.24 de ISO 27001:2022.',
                    'high'::severityenum,
                    'in_progress'::incidentstatusenum,
                    'Protección de Datos',
                    'Equipo de Infraestructura',
                    NOW() - INTERVAL '10 days'
                ),
                (
                    gen_random_uuid(),
                    'Falta de registro de actividad en base de datos de producción',
                    'Los logs de auditoría de la base de datos de producción estaban desactivados durante 48 horas por mantenimiento no comunicado, generando un gap en la trazabilidad.',
                    'medium'::severityenum,
                    'open'::incidentstatusenum,
                    'Auditoría y Trazabilidad',
                    'DBA',
                    NOW() - INTERVAL '1 day'
                )
            ) AS v(id, title, description, severity, status, category, reported_by, reported_at)
            WHERE NOT EXISTS (SELECT 1 FROM incidents LIMIT 1);
            """
        ),

        # ── 11. empresa_id en incidents ─────────────────────────────────────
        (
            "Agregar empresa_id a tabla incidents",
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'incidents' AND column_name = 'empresa_id'
                ) THEN
                    ALTER TABLE incidents
                        ADD COLUMN empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL;
                    CREATE INDEX IF NOT EXISTS ix_incidents_empresa_id ON incidents(empresa_id);
                    RAISE NOTICE 'Columna empresa_id agregada a incidents.';
                ELSE
                    RAISE NOTICE 'empresa_id ya existe en incidents, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 12. empresa_id en controls ───────────────────────────────────────
        (
            "Agregar empresa_id a tabla controls",
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'controls' AND column_name = 'empresa_id'
                ) THEN
                    ALTER TABLE controls
                        ADD COLUMN empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL;
                    CREATE INDEX IF NOT EXISTS ix_controls_empresa_id ON controls(empresa_id);
                    RAISE NOTICE 'Columna empresa_id agregada a controls.';
                ELSE
                    RAISE NOTICE 'empresa_id ya existe en controls, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 13. empresa_id en risk_levels ────────────────────────────────────
        (
            "Agregar empresa_id a tabla risk_levels",
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'risk_levels' AND column_name = 'empresa_id'
                ) THEN
                    ALTER TABLE risk_levels
                        ADD COLUMN empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL;
                    CREATE INDEX IF NOT EXISTS ix_risk_levels_empresa_id ON risk_levels(empresa_id);
                    RAISE NOTICE 'Columna empresa_id agregada a risk_levels.';
                ELSE
                    RAISE NOTICE 'empresa_id ya existe en risk_levels, omitiendo.';
                END IF;
            END $$;
            """
        ),

        # ── 14. Seed: cursos iniciales ──────────────────────────────────────
        (
            "Seed cursos iniciales",
            """
            INSERT INTO cursos (id, titulo, descripcion, video_url, material_texto, categoria, nivel)
            SELECT * FROM (VALUES
                (
                    gen_random_uuid(),
                    'Fundamentos de ISO/IEC 27001:2022',
                    'Introducción a la norma ISO 27001, su estructura y los requisitos clave del SGSI.',
                    'https://www.youtube.com/embed/iZNUDnf7QgQ',
                    'La norma ISO/IEC 27001:2022 establece los requisitos para implementar, mantener y mejorar un Sistema de Gestión de Seguridad de la Información (SGSI). Este curso cubre la estructura de alto nivel (HLS), los 93 controles del Anexo A y el proceso de certificación.',
                    'Fundamentos',
                    'basico'::nivelcursoenum
                ),
                (
                    gen_random_uuid(),
                    'Gestión de Riesgos en Seguridad de la Información',
                    'Metodología para identificar, analizar y tratar riesgos de seguridad conforme a ISO 27001.',
                    'https://www.youtube.com/embed/EOJO6rF776w',
                    'El proceso de gestión de riesgos es el corazón del SGSI. Aprenderás a construir el contexto organizacional, identificar activos de información, amenazas, vulnerabilidades y calcular el nivel de riesgo usando matrices de probabilidad × impacto.',
                    'Gestión de Riesgos',
                    'intermedio'::nivelcursoenum
                ),
                (
                    gen_random_uuid(),
                    'Controles de Seguridad — Anexo A (2022)',
                    'Revisión detallada de los 93 controles agrupados en 4 dominios del Anexo A actualizado.',
                    'https://www.youtube.com/embed/W5jdv-VnVfM',
                    'ISO 27001:2022 reorganizó los controles en 4 categorías: Organizacionales (37), Personas (8), Físicos (14) y Tecnológicos (34). Estudiaremos cada uno con ejemplos prácticos de implementación y evidencias requeridas para auditoría.',
                    'Controles',
                    'intermedio'::nivelcursoenum
                ),
                (
                    gen_random_uuid(),
                    'Auditoría Interna del SGSI',
                    'Cómo planificar y ejecutar auditorías internas conforme al requisito 9.2 de ISO 27001.',
                    'https://www.youtube.com/embed/SATi2IrDPXw',
                    'Las auditorías internas verifican la conformidad y eficacia del SGSI. Este módulo avanzado cubre la planificación del programa de auditoría, técnicas de recopilación de evidencia, redacción de hallazgos y seguimiento de no conformidades.',
                    'Auditoría',
                    'avanzado'::nivelcursoenum
                )
            ) AS v(id, titulo, descripcion, video_url, material_texto, categoria, nivel)
            WHERE NOT EXISTS (SELECT 1 FROM cursos LIMIT 1);
            """
        ),

        # ── 15. Generar controles ISO para empresas existentes sin controles ──
        (
            "Generar controles ISO para empresas existentes",
            """
            DO $$
            DECLARE
                emp RECORD;
                sector TEXT;
            BEGIN
                FOR emp IN SELECT id, actividad_economica FROM empresas LOOP
                    IF NOT EXISTS (SELECT 1 FROM controls WHERE empresa_id = emp.id LIMIT 1) THEN
                        -- Detectar sector
                        sector := 'general';
                        IF emp.actividad_economica ILIKE '%financiero%' OR emp.actividad_economica ILIKE '%banca%' OR emp.actividad_economica ILIKE '%banco%' OR emp.actividad_economica ILIKE '%seguros%' OR emp.actividad_economica ILIKE '%fintech%' THEN
                            sector := 'financiero';
                        ELSIF emp.actividad_economica ILIKE '%salud%' OR emp.actividad_economica ILIKE '%clinica%' OR emp.actividad_economica ILIKE '%hospital%' OR emp.actividad_economica ILIKE '%farmac%' THEN
                            sector := 'salud';
                        ELSIF emp.actividad_economica ILIKE '%tecnolog%' OR emp.actividad_economica ILIKE '%software%' OR emp.actividad_economica ILIKE '% it %' OR emp.actividad_economica ILIKE '%sistemas%' THEN
                            sector := 'tecnologia';
                        ELSIF emp.actividad_economica ILIKE '%educac%' OR emp.actividad_economica ILIKE '%universid%' OR emp.actividad_economica ILIKE '%colegio%' OR emp.actividad_economica ILIKE '%escuela%' THEN
                            sector := 'educacion';
                        ELSIF emp.actividad_economica ILIKE '%comercio%' OR emp.actividad_economica ILIKE '%retail%' OR emp.actividad_economica ILIKE '%ecommerce%' OR emp.actividad_economica ILIKE '%supermercado%' THEN
                            sector := 'comercio';
                        ELSIF emp.actividad_economica ILIKE '%gobierno%' OR emp.actividad_economica ILIKE '%estatal%' OR emp.actividad_economica ILIKE '%municipal%' OR emp.actividad_economica ILIKE '%publico%' THEN
                            sector := 'gobierno';
                        ELSIF emp.actividad_economica ILIKE '%manufactur%' OR emp.actividad_economica ILIKE '%industri%' OR emp.actividad_economica ILIKE '%produccion%' THEN
                            sector := 'manufactura';
                        END IF;

                        -- Controles base para todos los sectores
                        INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct)
                        VALUES
                            (gen_random_uuid(), emp.id, 'A.5', '5.1',  'Políticas de seguridad de la información', 'Se deben definir, aprobar y comunicar políticas de seguridad de la información alineadas con los requisitos del negocio.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.5', '5.2',  'Roles y responsabilidades de seguridad', 'Los roles y responsabilidades de seguridad deben estar definidos y asignados conforme a las políticas establecidas.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.6', '6.3',  'Concienciación, educación y capacitación en seguridad', 'El personal debe recibir formación y actualizaciones periódicas sobre políticas y procedimientos de seguridad.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.8', '8.5',  'Autenticación segura', 'Las tecnologías y procedimientos de autenticación segura deben implementarse basándose en restricciones de acceso a la información.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.8', '8.7',  'Protección contra malware', 'La protección contra malware debe implementarse y apoyarse con una concienciación adecuada del usuario.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.8', '8.20', 'Seguridad en redes', 'Las redes y dispositivos de red deben asegurarse, gestionarse y controlarse para proteger la información.', 'non_compliant'::controlstatusenum, 0),
                            (gen_random_uuid(), emp.id, 'A.8', '8.24', 'Uso de criptografía', 'Se deben definir e implementar reglas sobre el uso de criptografía, incluida la gestión de claves criptográficas.', 'non_compliant'::controlstatusenum, 0);

                        -- Controles adicionales por sector
                        IF sector = 'financiero' THEN
                            INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct) VALUES
                                (gen_random_uuid(), emp.id, 'A.5', '5.14', 'Transferencia de información', 'Se deben establecer reglas y controles para proteger la información durante su transferencia.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.2',  'Derechos de acceso privilegiado', 'La asignación y uso de derechos de acceso privilegiado debe restringirse y controlarse.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.16', 'Monitoreo de actividades', 'Las redes y sistemas deben monitorearse para detectar comportamientos anómalos.', 'non_compliant'::controlstatusenum, 0);
                        ELSIF sector = 'salud' THEN
                            INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct) VALUES
                                (gen_random_uuid(), emp.id, 'A.5', '5.34', 'Privacidad y protección de datos personales', 'Los requisitos de privacidad y protección de datos personales deben identificarse y cumplirse.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.11', 'Enmascaramiento de datos', 'El enmascaramiento de datos debe utilizarse conforme a la política de control de acceso.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.2',  'Derechos de acceso privilegiado', 'El acceso a historiales clínicos debe estar restringido a personal autorizado.', 'non_compliant'::controlstatusenum, 0);
                        ELSIF sector = 'tecnologia' THEN
                            INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct) VALUES
                                (gen_random_uuid(), emp.id, 'A.8', '8.8',  'Gestión de vulnerabilidades técnicas', 'La información sobre vulnerabilidades técnicas debe obtenerse oportunamente y gestionarse.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.25', 'Ciclo de vida de desarrollo seguro', 'Se deben establecer y aplicar reglas para el desarrollo seguro de software y sistemas.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.8', '8.29', 'Pruebas de seguridad en desarrollo', 'Los procesos de pruebas de seguridad deben definirse e implementarse en el SDLC.', 'non_compliant'::controlstatusenum, 0);
                        ELSIF sector = 'gobierno' THEN
                            INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct) VALUES
                                (gen_random_uuid(), emp.id, 'A.5', '5.7',  'Inteligencia sobre amenazas', 'Se debe recopilar y analizar información sobre amenazas relevantes.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.5', '5.30', 'Preparación TIC para continuidad del negocio', 'La preparación de las TIC debe planificarse para garantizar disponibilidad.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.7', '7.1',  'Perímetros de seguridad física', 'Se deben definir y usar perímetros de seguridad para proteger áreas con información sensible.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.5', '5.34', 'Privacidad y protección de datos personales', 'Los requisitos de privacidad y protección de datos ciudadanos deben cumplirse.', 'non_compliant'::controlstatusenum, 0);
                        ELSIF sector = 'manufactura' THEN
                            INSERT INTO controls (id, empresa_id, iso_domain, iso_control_ref, name, description, status, compliance_pct) VALUES
                                (gen_random_uuid(), emp.id, 'A.7', '7.1',  'Perímetros de seguridad física', 'Se deben definir perímetros de seguridad para proteger plantas y equipos industriales.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.7', '7.4',  'Monitoreo de seguridad física', 'Las instalaciones industriales deben monitorearse para detectar accesos no autorizados.', 'non_compliant'::controlstatusenum, 0),
                                (gen_random_uuid(), emp.id, 'A.5', '5.30', 'Preparación TIC para continuidad del negocio', 'La continuidad de líneas de producción debe garantizarse con planes TIC robustos.', 'non_compliant'::controlstatusenum, 0);
                        END IF;

                        RAISE NOTICE 'Controles generados para empresa % (sector: %)', emp.id, sector;
                    ELSE
                        RAISE NOTICE 'Empresa % ya tiene controles, omitiendo.', emp.id;
                    END IF;
                END LOOP;
            END $$;
            """
        ),

        # ── 16. Actualizar video_url de cursos existentes ────────────────────
        (
            "Actualizar video_url de cursos con URLs correctas",
            """
            UPDATE cursos SET video_url = 'https://www.youtube.com/embed/iZNUDnf7QgQ'
            WHERE titulo = 'Fundamentos de ISO/IEC 27001:2022';

            UPDATE cursos SET video_url = 'https://www.youtube.com/embed/EOJO6rF776w'
            WHERE titulo = 'Gestión de Riesgos en Seguridad de la Información';

            UPDATE cursos SET video_url = 'https://www.youtube.com/embed/W5jdv-VnVfM'
            WHERE titulo = 'Controles de Seguridad — Anexo A (2022)';

            UPDATE cursos SET video_url = 'https://www.youtube.com/embed/SATi2IrDPXw'
            WHERE titulo = 'Auditoría Interna del SGSI';
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
