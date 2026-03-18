# ISO_SECURE — SGSI KPI Dashboard

API REST y Dashboard para indicadores y métricas de seguridad del SGSI conforme a ISO/IEC 27001:2022.

## Estructura del Proyecto

```
├── app/                    # Backend FastAPI
│   ├── models/            # Modelos SQLAlchemy
│   ├── routers/           # Endpoints API
│   ├── schemas/           # Schemas Pydantic
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades
├── frontend/              # Frontend React + Vite
│   └── src/               # Código fuente React
├── alembic/               # Migraciones de base de datos
├── main.py                # Punto de entrada FastAPI
├── Dockerfile             # Docker para backend
├── docker-compose.yml     # Orquestación de servicios
└── requirements.txt       # Dependencias Python
```

## Requisitos

- Python 3.13+
- Node.js 20+
- PostgreSQL (Supabase)

## Configuración

1. Clonar el repositorio
2. Copiar `.env.example` a `.env` y configurar las variables:

```bash
cp .env.example .env
```

3. Configurar las credenciales de Supabase en `.env`

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

## Deployment en Coolify

1. Conectar el repositorio de GitHub
2. Configurar las variables de entorno en Coolify
3. Seleccionar Docker Compose como método de deployment
4. Deploy

## API Endpoints

- `GET /` - Health check
- `GET /health` - Estado del servicio
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

### Recursos API (prefijo `/api/v1`)

- `/incidents` - Gestión de incidentes
- `/controls` - Controles de seguridad
- `/risk` - Evaluación de riesgos
- `/dashboard` - Métricas del dashboard
- `/snapshots` - Snapshots históricos

## Licencia

Privado - Antigravity
