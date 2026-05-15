# ISO_SECURE — Plataforma de Cumplimiento ISO 27001

Plataforma web completa para la gestion de seguridad de la informacion (SGSI) conforme a ISO/IEC 27001:2022. Incluye dashboard de KPIs, gestion de incidentes, controles ISO, evaluacion de riesgos, capacitaciones, auditoria interna y soporte multi-tenant.

**Universidad de San Buenaventura** — Ingenieria de Sistemas

## Arquitectura del Sistema

La documentacion visual completa de la arquitectura esta disponible en [`/frontend/public/arquitectura.html`](frontend/public/arquitectura.html).

El modelamiento de amenazas STRIDE (Microsoft Threat Modeling) esta disponible en [`/frontend/public/threat-modeling.html`](frontend/public/threat-modeling.html) — incluye DFD, 24 amenazas identificadas, arboles de amenazas, matriz de riesgo y hoja de ruta de mitigaciones.

La metodologia adoptada PASTA + STRIDE esta documentada en [`/frontend/public/metodologia-amenazas.html`](frontend/public/metodologia-amenazas.html) — incluye justificacion, comparativa de 6 metodologias, 7 etapas PASTA aplicadas, 12 vulnerabilidades con mapeo OWASP/ISO, y 15 mitigaciones priorizadas.

### Stack Tecnologico

| Capa | Tecnologia | Version |
|------|-----------|---------|
| **Frontend** | React + Vite | 19.0 / 8.0 |
| **Backend** | FastAPI + Python | 0.111+ / 3.13 |
| **ORM** | SQLAlchemy (async) | 2.0+ |
| **Base de Datos** | PostgreSQL (Supabase) | 15+ |
| **Autenticacion** | Supabase JWT + RBAC | OAuth 2.0 |
| **Validacion** | Pydantic | v2 |
| **Migraciones** | Alembic | latest |
| **Charts** | Chart.js + react-chartjs-2 | 4.5 |
| **Animaciones** | Framer Motion | 12.38 |
| **HTTP Client** | Axios (frontend) / HTTPX (backend) | 1.13 / latest |
| **Servidor** | Uvicorn (ASGI) + Nginx (static) | latest / alpine |
| **Contenedores** | Docker + Docker Compose | latest / v3.8 |

### Arquitectura Backend (Layered Architecture)

```
main.py                        Punto de entrada FastAPI + CORS + Lifespan
  |
  +-- app/auth.py              JWT Validation (Supabase) + RBAC (require_role)
  |
  +-- app/routers/             9 Routers — 39 Endpoints REST
  |     auth_router.py           /auth        (5 endpoints)
  |     incidents.py             /incidents   (5 endpoints)
  |     controls.py              /controls    (4 endpoints)
  |     risk.py                  /risk        (4 endpoints)
  |     dashboard.py             /dashboard   (3 endpoints)
  |     empresa.py               /empresas    (4 endpoints)
  |     capacitaciones.py        /capacitaciones (4 endpoints)
  |     implementacion.py        /implementacion (3 endpoints)
  |     auditoria.py             /auditoria   (4 endpoints)
  |     snapshots.py             /snapshots   (2 endpoints)
  |
  +-- app/schemas/             Pydantic v2 Request/Response validation
  +-- app/services/            9 Services — Business Logic Layer
  +-- app/models/              9 SQLAlchemy ORM Models (Mapped)
  +-- app/utils/               Enums (8) + actividad_controles.py (93 controles ISO)
  |
  +-- app/database.py          AsyncEngine + AsyncSession + Connection Pool
```

### Arquitectura Frontend

```
frontend/src/
  +-- main.jsx                 React DOM + StrictMode + BrowserRouter
  +-- App.jsx                  Componente raiz (~2100 lineas) — 11 vistas
  +-- api.js                   Axios client + Bearer token interceptor
  +-- ChatWidget.jsx           ISORA AI Assistant (SSE Streaming)
```

**11 Vistas:** Dashboard, Incidentes, Controles, Riesgos, Historial, Empresas, Usuarios, Capacitaciones, Implementacion, Auditoria, Resumen

### Base de Datos — 9 Tablas

| Tabla | Descripcion | FK |
|-------|------------|-----|
| `empresas` | Registro multi-tenant de organizaciones | — |
| `user_profiles` | Usuarios + roles (admin/auditor/supervisor/analista) | empresas |
| `incidents` | Incidentes de seguridad | empresas |
| `controls` | Controles ISO 27001 (93 por sector) | empresas |
| `risk_levels` | Evaluaciones de riesgo (P x I) | empresas |
| `auditoria_items` | Checklist de auditoria interna | empresas |
| `cursos` | Cursos de capacitacion con video | — |
| `curso_progreso` | Progreso de usuario por curso | cursos |
| `kpi_snapshots` | Snapshots historicos de metricas | — |

### Autenticacion y Roles (RBAC)

- **JWT** validado via Supabase REST (`/auth/v1/user`)
- **4 roles:** admin, auditor, supervisor, analista
- **Multi-tenant:** admin/auditor ven todo; supervisor/analista solo su empresa

| Vista | admin | auditor | supervisor | analista |
|-------|:-----:|:-------:|:----------:|:--------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Incidentes | ✅ | ✅ | — | ✅ |
| Controles | ✅ | ✅ | — | ✅ |
| Riesgos | ✅ | ✅ | — | — |
| Empresas | ✅ | ✅ | — | — |
| Usuarios | ✅ | — | — | — |
| Capacitaciones | ✅ | ✅ | ✅ | ✅ |
| Implementacion | ✅ | ✅ | — | — |
| Auditoria | ✅ | ✅ | — | — |

### Despliegue (Docker Compose)

```
docker-compose.yml
  +-- frontend (nginx:alpine)     Puerto 3000 -> 80
  |     Build: Node 20 -> npm ci -> npm run build -> dist/
  |
  +-- backend (python:3.13-slim)  Puerto 8001 -> 8000
  |     Startup: python migrate.py && uvicorn main:app
  |
  +-- app-network (bridge)        DNS interno entre servicios
```

**Servicios externos:** Supabase Cloud (PostgreSQL + Auth), ISORA AI (SSE), YouTube CDN (videos)

## Estructura del Proyecto

```
iso_secure/
├── app/
│   ├── models/              # 9 modelos SQLAlchemy (Mapped)
│   ├── routers/             # 9 routers FastAPI (39 endpoints)
│   ├── schemas/             # Schemas Pydantic v2
│   ├── services/            # 9 servicios de logica de negocio
│   └── utils/               # Enums + catalogo de controles ISO
├── frontend/
│   ├── src/                 # React 19 + Vite 8
│   └── public/              # Assets + docs.html + arquitectura.html
├── alembic/                 # Migraciones de base de datos
├── main.py                  # Punto de entrada FastAPI
├── migrate.py               # Auto-migraciones en startup Docker
├── seed.py                  # Datos de prueba con Faker
├── Dockerfile               # Backend container
├── docker-compose.yml       # Orquestacion
├── requirements.txt         # Dependencias Python
└── .env.example             # Template de variables de entorno
```

## Requisitos

- Python 3.13+
- Node.js 20+
- PostgreSQL (Supabase)

## Configuracion

1. Clonar el repositorio
2. Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Variables requeridas:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
API_PREFIX=/api/v1
DEBUG=false
```

## Desarrollo Local

### Backend

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Deployment con Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/docs

## API Endpoints (39 total)

- `GET /` — Health check
- `GET /health` — Estado del servicio
- `GET /docs` — Documentacion Swagger
- `GET /redoc` — Documentacion ReDoc

### Recursos API (prefijo `/api/v1`)

| Recurso | Endpoints | Descripcion |
|---------|-----------|-------------|
| `/auth` | 5 | Registro, perfil, usuarios, roles |
| `/incidents` | 5 | CRUD incidentes + estadisticas |
| `/controls` | 4 | Controles ISO + compliance % |
| `/risk` | 4 | Riesgos: actual, historico, por dominio |
| `/dashboard` | 3 | KPIs consolidados + semaforo + export |
| `/empresas` | 4 | Organizaciones + auto-asignar controles |
| `/capacitaciones` | 4 | Cursos + progreso de usuario |
| `/implementacion` | 3 | Tareas de implementacion ISO |
| `/auditoria` | 4 | Checklist de auditoria interna |
| `/snapshots` | 2 | Snapshots historicos de metricas |

## Autor

Agustin Peralta — Universidad de San Buenaventura

## Licencia

MIT License - Copyright (c) 2026 Agustin Peralta
