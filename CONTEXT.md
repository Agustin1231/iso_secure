# ISO_SECURE — Contexto de Continuación

**Proyecto:** SGSI KPI Dashboard · ISO/IEC 27001:2022
**Autor:** Agustín Peralta — Universidad de San Buenaventura
**Stack:** FastAPI + SQLAlchemy + Supabase Auth · React 19 + Vite · PostgreSQL
**Repo:** https://github.com/Agustin1231/iso_secure

---

## Estado actual (última sesión)

### Fases completadas

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Renombrar `partial→en_proceso`, modelo Empresa, Auth Supabase JWT, roles (admin/auditor/supervisor/analista), auto-migración Docker | ✅ Pusheado |
| 2 | Módulos Capacitaciones, Implementación ISO y Auditoría (backend + frontend) | ✅ Pusheado |
| 3 | UI roles: dashboard role-aware, tarjetas de acceso rápido por rol, badge de rol en header, componente `AccessDenied` | ✅ Pusheado |
| 4 | Sidebar fijo en desktop + scroll mobile, filtrado de datos por empresa, videos reales en capacitaciones, controles ISO auto-asignados por empresa | ✅ Pusheado |
| 5 | Documentación `docs.html` actualizada a v2.0 | ✅ Pusheado |

### Último commit pusheado
```
e62fd13 fix: cerrar div models-grid para restaurar layout desde seccion 06
```

---

## Arquitectura actual

### Backend (`/app`)
```
routers/    auth_router.py, controls.py, dashboard.py, empresa.py,
            incidents.py, risk.py, snapshots.py,
            capacitaciones.py, implementacion.py, auditoria.py   ← Fase 2
models/     incident, control, risk, snapshot, empresa, user_profile,
            curso, curso_progreso, auditoria_item                 ← Fase 2
schemas/    control, empresa, snapshot, curso, auditoria          ← Fase 2
services/   control_service, empresa_service,
            capacitacion_service, auditoria_service               ← Fase 2
utils/      enums.py, actividad_controles.py                      ← Fase 2
```

### Enums relevantes
- `ControlStatusEnum`: compliant / en_proceso / non_compliant
- `UserRoleEnum`: admin / auditor / supervisor / analista
- `NivelCursoEnum`: basico / intermedio / avanzado
- `ProgresoEnum`: pendiente / en_proceso / completado
- `AuditoriaStatusEnum`: pendiente / en_proceso / completado

### Auth
- JWT validado vía Supabase REST (`/auth/v1/user`)
- `get_supabase_user` → solo valida JWT (para register-profile)
- `get_current_user` → JWT + perfil en DB (para endpoints normales)
- `require_role(["admin"])` → factory de dependency con RBAC

### Frontend (`/frontend/src`)
- `App.jsx` — componente único (~2100 líneas). Vistas: dashboard, incidents, controls, risk, history, empresas, usuarios, capacitaciones, implementacion, auditoria
- `api.js` — axios con interceptor de token. Exports: dashboardApi, incidentApi, riskApi, controlApi, snapshotApi, empresaApi, authApi, capacitacionApi, implementacionApi, auditoriaApi
- `ALL_NAV_ITEMS` — array con roles requeridos por ítem de sidebar
- `VIEW_ROLES` — mapa de vista → roles permitidos (guard AccessDenied)
- `ROLE_META` — por rol: label, color, descripción, módulos de acceso rápido en dashboard

### Roles y vistas autorizadas
| Vista | admin | auditor | supervisor | analista |
|-------|:-----:|:-------:|:----------:|:--------:|
| dashboard | ✅ | ✅ | ✅ | ✅ |
| incidents | ✅ | ✅ | — | ✅ |
| controls | ✅ | ✅ | — | ✅ |
| risk | ✅ | ✅ | — | — |
| history | ✅ | — | ✅ | — |
| empresas | ✅ | ✅ | — | — |
| usuarios | ✅ | — | — | — |
| capacitaciones | ✅ | ✅ | ✅ | ✅ |
| implementacion | ✅ | ✅ | — | — |
| auditoria | ✅ | ✅ | — | — |

### migrate.py — tablas creadas al iniciar contenedor
1. Rename enum `partial→en_proceso`
2. Rename columna `controls_partial→controls_en_proceso`
3. Crear tipo `userroleenum`
4. Crear tabla `empresas`
5. Crear tabla `user_profiles`
6. Crear tipos `nivelcursoenum`, `progresoenum`, `auditoriastatusenum`
7. Crear tabla `cursos`
8. Crear tabla `curso_progreso` (unique curso_id + user_id)
9. Crear tabla `auditoria_items`
10. Seed: 4 cursos iniciales con URLs reales de YouTube embed
11. `ALTER TABLE incidents ADD COLUMN IF NOT EXISTS empresa_id UUID FK`
12. `ALTER TABLE controls ADD COLUMN IF NOT EXISTS empresa_id UUID FK`
13. `ALTER TABLE risk_levels ADD COLUMN IF NOT EXISTS empresa_id UUID FK`
14. Seed de controles ISO automático para empresas existentes sin controles (según sector)

---

## Variables de entorno requeridas
```
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://rhvzjqvyimaavkdjxcvj.supabase.co
SUPABASE_ANON_KEY=eyJ...
API_PREFIX=/api/v1
```

Frontend: `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` en `/frontend/.env` (o usar fallback hardcodeado en App.jsx).

---

## Posibles próximas fases

### Fase 4 — Reportes y exportación
- Conectar el botón "Exportar Reporte" al webhook n8n real y devolver PDF
- Reporte por empresa: estado de auditoría, controles, nivel de riesgo
- Exportar checklist de auditoría a PDF/Excel por empresa

### Fase 5 — Notificaciones y alertas
- Email automático cuando un control pasa a `non_compliant`
- Alerta cuando una auditoría lleva X días sin actualizar
- Integración con Supabase Edge Functions o n8n para triggers

### Fase 6 — Métricas avanzadas y gráficos reales
- Reemplazar `dummyChartData` con datos reales de snapshots históricos
- Gráfico de evolución de compliance por empresa
- Heatmap de dominios ISO por nivel de riesgo

### Fase 7 — Multi-tenant completo ✅ Completado en sesión 2
- Filtrado de datos por `empresa_id` implementado en incidents, controls, risk, dashboard
- Supervisores/analistas ven solo datos de su empresa; admin/auditor ven todo
- Helper `_empresa_filter(user)` en cada router

### Deuda técnica conocida
- `dummyChartData` en dashboard → reemplazar con datos reales de `/snapshots`
- `frontend/src/App.jsx` es un monolito (~2100 líneas) → dividir en componentes si crece más
- Los `alert()` en catch blocks → reemplazar con toasts/snackbars
- No hay paginación en Capacitaciones (actualmente muestra todas las tarjetas)

---

## Cambios de la última sesión (sesión 2)

### 1. Sidebar CSS fix
- `position: fixed` + `overflow-y: auto` en base `.sidebar` (permite scroll mobile)
- Desktop `(min-width: 769px)`: `overflow: hidden !important` para evitar scroll
- `.main-content { grid-column: 2 }` en desktop — crítico porque `fixed` saca el sidebar del flujo del grid

### 2. Filtrado de datos por empresa (multi-tenant)
- `empresa_id` FK añadido a modelos: `Incident`, `Control`, `RiskLevel`
- Servicios actualizados: `incident_service`, `control_service`, `risk_service`, `dashboard_service` aceptan `empresa_id` opcional
- Routers `incidents.py`, `controls.py`, `risk.py`, `dashboard.py` inyectan `get_current_user` y aplican filtro según rol

### 3. Videos reales en capacitaciones
- `migrate.py` actualiza `video_url` de los 4 cursos con URLs reales de YouTube embed

### 4. Controles ISO auto-asignados por empresa
- `app/utils/actividad_controles.py` reescrito con:
  - `CONTROL_CATALOG`: 93 controles del Anexo A ISO 27001:2022 (dominios A.5–A.8)
  - `SECTOR_CONTROLES`: 7 sectores con controles específicos (finanzas, salud, tecnología, educación, manufactura, retail, gobierno)
  - `_detect_sector()`: detección por palabras clave desde texto libre de `actividad_economica`
  - `get_controls_for_empresa()`: devuelve controles base + sectoriales
- `EmpresaService._assign_controls()`: elimina controles viejos y reasigna al crear/actualizar empresa
- `POST /empresas/{id}/generar-controles`: endpoint para regenerar manualmente
- `migrate.py` paso 14: seed automático de controles para empresas existentes sin controles

### 5. Documentación `frontend/public/docs.html` → v2.0
- Todos los caracteres garbled corregidos con HTML entities (`&rarr;`, `&larr;`, `&mdash;`, `&ntilde;`, `&uacute;`)
- Versión actualizada a v2.0.0
- Métricas: 39 endpoints, 9 dominios API, 9 tablas PostgreSQL
- Arquitectura: 9 routers + 9 tablas en diagrama
- 5 nuevos grupos de endpoints: `/empresas`, `/auth`, `/capacitaciones`, `/implementacion`, `/auditoria`
- `empresa_id` destacado en tarjetas de modelos `incidents`, `controls`, `risk_levels`
- 4 nuevas tarjetas de tablas: `empresas`, `user_profiles`, `cursos`, `auditoria_items`
