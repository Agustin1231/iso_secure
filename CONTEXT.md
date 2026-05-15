# ISO_SECURE — Contexto de Continuación

**Proyecto:** SGSI KPI Dashboard · ISO/IEC 27001:2022
**Autor:** Agustín Peralta — Universidad de San Buenaventura
**Stack:** FastAPI + SQLAlchemy + Supabase Auth · React 19 + Vite · PostgreSQL
**Repo:** https://github.com/Agustin1231/iso_secure

---

## Estado actual (ultima sesion)

### Fases completadas

| Fase | Descripcion | Estado |
|------|-------------|--------|
| 1 | Renombrar `partial→en_proceso`, modelo Empresa, Auth Supabase JWT, roles (admin/auditor/supervisor/analista), auto-migracion Docker | ✅ Pusheado |
| 2 | Modulos Capacitaciones, Implementacion ISO y Auditoria (backend + frontend) | ✅ Pusheado |
| 3 | UI roles: dashboard role-aware, tarjetas de acceso rapido por rol, badge de rol en header, componente `AccessDenied` | ✅ Pusheado |
| 4 | Sidebar fijo en desktop + scroll mobile, filtrado de datos por empresa, videos reales en capacitaciones, controles ISO auto-asignados por empresa | ✅ Pusheado |
| 5 | Documentacion `docs.html` actualizada a v2.0 | ✅ Pusheado |
| 6 | Manual de usuario con videos por modulo + anexos XLSX | ✅ Pusheado |
| 7 | **Documentacion de arquitectura completa** — HTML interactivo con 7 secciones: arquitectura general, backend, frontend, stack tecnologico, despliegue, autenticacion/RBAC, modelo de datos ER | ✅ Pusheado |

### Ultimo commit pusheado
```
451509a fix(manual): poster en t=2s para saltar frame inicial negro
```

---

## Arquitectura actual

> Documentacion visual completa: [`frontend/public/arquitectura.html`](frontend/public/arquitectura.html)

### Stack Tecnologico

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Frontend | React + Vite | 19.0 / 8.0 |
| Backend | FastAPI + Python | 0.111+ / 3.13 |
| ORM | SQLAlchemy (async) | 2.0+ |
| Base de Datos | PostgreSQL (Supabase) | 15+ |
| Auth | Supabase JWT + RBAC | OAuth 2.0 |
| Validacion | Pydantic v2 | latest |
| Migraciones | Alembic | latest |
| Charts | Chart.js + react-chartjs-2 | 4.5 |
| Animaciones | Framer Motion | 12.38 |
| HTTP | Axios (FE) / HTTPX (BE) | 1.13 / latest |
| Server | Uvicorn + Nginx | latest / alpine |
| Deploy | Docker + Docker Compose | latest / v3.8 |

### Backend (`/app`) — Layered Architecture

```
main.py            FastAPI app + CORS + Lifespan + 9 Router includes

routers/ (39 endpoints)
  auth_router.py     /auth            5 endpoints (register, me, users, role)
  incidents.py       /incidents       5 endpoints (CRUD + stats)
  controls.py        /controls        4 endpoints (CRUD + compliance)
  risk.py            /risk            4 endpoints (current, create, history, by-domain)
  dashboard.py       /dashboard       3 endpoints (summary, kpis, export)
  empresa.py         /empresas        4 endpoints (CRUD + generar-controles)
  capacitaciones.py  /capacitaciones  4 endpoints (cursos + progreso)
  implementacion.py  /implementacion  3 endpoints (tareas ISO)
  auditoria.py       /auditoria       4 endpoints (checklist)
  snapshots.py       /snapshots       2 endpoints (historicos)

models/ (9 tablas)
  empresa, user_profile, incident, control, risk,
  snapshot, curso, curso_progreso, auditoria_item

schemas/    Pydantic v2 request/response (9 modulos)
services/   Business logic layer (9 servicios)
utils/      enums.py (8 enums) + actividad_controles.py (93 controles, 7 sectores)
auth.py     get_supabase_user + get_current_user + require_role()
database.py AsyncEngine + AsyncSession + Connection Pool
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

### Documentacion de arquitectura (Fase 7)
- Archivo: `frontend/public/arquitectura.html` — HTML interactivo con navegacion fija
- 7 secciones: Arquitectura General, Backend, Frontend, Stack Tecnologico, Despliegue, Autenticacion/RBAC, Modelo de Datos ER
- Incluye: diagramas de capas, flujos de auth (login + request protegido), matriz RBAC completa, relaciones entre entidades, 8 enums, pipeline de deploy

### Deuda tecnica conocida
- `dummyChartData` en dashboard → reemplazar con datos reales de `/snapshots`
- `frontend/src/App.jsx` es un monolito (~2100 lineas) → dividir en componentes si crece mas
- Los `alert()` en catch blocks → reemplazar con toasts/snackbars
- No hay paginacion en Capacitaciones (actualmente muestra todas las tarjetas)
- URLs de video en cursos no se validan para integridad

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
