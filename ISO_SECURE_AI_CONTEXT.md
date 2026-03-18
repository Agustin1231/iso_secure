# ISO_SECURE — Contexto Completo para Agente IA

> Este documento es el contexto de referencia para construir la API REST de indicadores y métricas de seguridad del SGSI (Sistema de Gestión de Seguridad de la Información) alineado con ISO/IEC 27001:2022. Contiene toda la información necesaria para generar el código, las tablas, los endpoints y la lógica de negocio. El agente debe seguir este documento como fuente única de verdad.

---

## 1. DESCRIPCIÓN GENERAL DEL PROYECTO

**Nombre:** ISO_SECURE  
**Versión:** 1.0.0 (PoC)  
**Tipo:** API REST  
**Propósito:** Exponer endpoints para registrar, consultar y analizar los KPIs (Key Performance Indicators) y KRIs (Key Risk Indicators) del SGSI de una organización, conforme a ISO/IEC 27001:2022 y el marco de medición ISO/IEC 27004.

### ¿Qué hace esta API?

- Permite **reportar incidentes de seguridad** y consultar estadísticas sobre ellos (MTTR, tasa de resolución, cantidad por severidad).
- Permite **registrar y consultar controles ISO 27001** del Anexo A y calcular el porcentaje global de cumplimiento.
- Permite **registrar evaluaciones de riesgo** por dominio ISO y consultar el nivel de riesgo actual e histórico.
- Expone un **dashboard ejecutivo** que consolida todos los KPIs en un solo endpoint para reportes a la alta dirección.

### Contexto académico

- **Proyecto:** ISO_SECURE 27001
- **Asignatura:** Seguridad Informática
- **Universidad:** Universidad de San Buenaventura
- **Programa:** Ingeniería de Sistemas
- **Fecha de exposición:** 18 de marzo de 2026
- **Duración de la exposición:** 10 minutos

---

## 2. STACK TECNOLÓGICO

| Capa | Tecnología | Versión recomendada | Notas |
|---|---|---|---|
| Framework principal | FastAPI | 0.111+ | Async, OpenAPI auto-generado |
| Validación de datos | Pydantic | v2 (pydantic>=2.0) | Schemas de request y response |
| ORM | SQLAlchemy | 2.0+ async | Modo async con asyncpg |
| Base de datos | PostgreSQL | 15+ | Hosted en Supabase |
| Driver async | asyncpg | latest | Driver nativo async para PostgreSQL |
| Migraciones | Alembic | latest | Control de versiones del schema |
| Servidor ASGI | Uvicorn | latest | Con workers para producción |
| Variables de entorno | python-dotenv | latest | Carga de .env |
| Generación de UUIDs | uuid (stdlib) | — | uuid4 para todos los IDs |
| Fechas | datetime (stdlib) | — | Siempre en UTC |
| Seeding de datos | Faker | latest | Para poblar datos de prueba |

### Dependencias (requirements.txt)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
python-dotenv>=1.0.0
faker>=24.0.0
httpx>=0.27.0
```

---

## 3. ESTRUCTURA DE CARPETAS

```
iso_secure/
├── main.py                    # Entrada de la app FastAPI
├── requirements.txt
├── .env                       # Variables de entorno (NO subir a git)
├── .env.example               # Plantilla de variables de entorno
├── alembic.ini                # Config de Alembic
├── alembic/
│   └── versions/              # Archivos de migración
├── app/
│   ├── __init__.py
│   ├── database.py            # Conexión a PostgreSQL / Supabase
│   ├── models/
│   │   ├── __init__.py
│   │   ├── incident.py        # Modelo SQLAlchemy: Incident
│   │   ├── control.py         # Modelo SQLAlchemy: Control
│   │   ├── risk.py            # Modelo SQLAlchemy: RiskLevel
│   │   └── snapshot.py        # Modelo SQLAlchemy: KpiSnapshot
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── incident.py        # Pydantic schemas: Incident
│   │   ├── control.py         # Pydantic schemas: Control
│   │   ├── risk.py            # Pydantic schemas: RiskLevel
│   │   ├── snapshot.py        # Pydantic schemas: KpiSnapshot
│   │   └── dashboard.py       # Pydantic schemas: Dashboard/resumen
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── incidents.py       # Router con todos los endpoints de /incidents
│   │   ├── controls.py        # Router con todos los endpoints de /controls
│   │   ├── risk.py            # Router con todos los endpoints de /risk
│   │   └── dashboard.py       # Router con todos los endpoints de /dashboard
│   ├── services/
│   │   ├── __init__.py
│   │   ├── incident_service.py  # Lógica de negocio para incidentes
│   │   ├── control_service.py   # Lógica de negocio para controles
│   │   ├── risk_service.py      # Lógica de negocio para riesgos
│   │   └── dashboard_service.py # Lógica de negocio para dashboard
│   └── utils/
│       ├── __init__.py
│       └── enums.py           # Todos los Enum del proyecto
└── seed.py                    # Script para insertar datos falsos con Faker
```

---

## 4. VARIABLES DE ENTORNO (.env)

```env
# Supabase / PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# App config
APP_NAME=ISO_SECURE
APP_VERSION=1.0.0
DEBUG=true

# API
API_PREFIX=/api/v1
```

El agente debe usar `DATABASE_URL` como única variable de conexión. No hardcodear credenciales.

---

## 5. BASE DE DATOS — SUPABASE / POSTGRESQL

### 5.1 Conexión (app/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### 5.2 Tablas y Modelos SQLAlchemy

---

#### TABLA: `incidents`

**Propósito:** Registrar todos los incidentes de seguridad reportados en el SGSI.

```python
# app/models/incident.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import SeverityEnum, IncidentStatusEnum

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[SeverityEnum] = mapped_column(SAEnum(SeverityEnum), nullable=False)
    status: Mapped[IncidentStatusEnum] = mapped_column(SAEnum(IncidentStatusEnum), nullable=False, default=IncidentStatusEnum.open)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
```

**Campos explicados:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id` | UUID | Auto | PK generado automáticamente con uuid4 |
| `title` | VARCHAR(200) | Sí | Título descriptivo del incidente |
| `description` | TEXT | No | Descripción detallada del incidente |
| `severity` | ENUM | Sí | Nivel de gravedad: `low`, `medium`, `high`, `critical` |
| `status` | ENUM | Auto | Estado actual: `open`, `in_progress`, `closed`. Default: `open` |
| `category` | VARCHAR(100) | No | Categoría: `phishing`, `malware`, `acceso_no_autorizado`, `fuga_de_datos`, `otro` |
| `reported_by` | VARCHAR(100) | No | Nombre o email de quien reporta |
| `reported_at` | TIMESTAMP TZ | Auto | Fecha/hora de reporte. Default: NOW() UTC |
| `resolved_at` | TIMESTAMP TZ | No | Fecha/hora de resolución. NULL si no está cerrado |

---

#### TABLA: `controls`

**Propósito:** Registrar los controles del Anexo A de ISO 27001 y su estado de cumplimiento.

```python
# app/models/control.py
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Date, Numeric, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import ControlStatusEnum

class Control(Base):
    __tablename__ = "controls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iso_domain: Mapped[str] = mapped_column(String(10), nullable=False)
    iso_control_ref: Mapped[str] = mapped_column(String(20), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[ControlStatusEnum] = mapped_column(SAEnum(ControlStatusEnum), nullable=False)
    compliance_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    responsible: Mapped[str] = mapped_column(String(100), nullable=True)
    last_reviewed: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

**Campos explicados:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id` | UUID | Auto | PK |
| `iso_domain` | VARCHAR(10) | Sí | Dominio del Anexo A: `A.5`, `A.6`, `A.7`, ..., `A.18` |
| `iso_control_ref` | VARCHAR(20) | No | Referencia exacta: `A.5.1`, `A.9.4.2`, etc. |
| `name` | VARCHAR(200) | Sí | Nombre del control |
| `description` | VARCHAR(500) | No | Descripción del control |
| `status` | ENUM | Sí | `compliant`, `partial`, `non_compliant` |
| `compliance_pct` | DECIMAL(5,2) | Sí | Porcentaje de 0.00 a 100.00 |
| `responsible` | VARCHAR(100) | No | Responsable del control |
| `last_reviewed` | DATE | No | Última fecha de revisión |
| `created_at` | TIMESTAMP TZ | Auto | Fecha de creación |
| `updated_at` | TIMESTAMP TZ | Auto | Última actualización |

---

#### TABLA: `risk_levels`

**Propósito:** Registrar evaluaciones de riesgo por dominio ISO usando la matriz probabilidad × impacto.

```python
# app/models/risk.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import RiskLevelEnum

class RiskLevel(Base):
    __tablename__ = "risk_levels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[RiskLevelEnum] = mapped_column(SAEnum(RiskLevelEnum), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

**Campos explicados:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id` | UUID | Auto | PK |
| `domain` | VARCHAR(100) | Sí | Dominio evaluado: `Seguridad de Activos`, `Control de Acceso`, `Criptografía`, etc. |
| `level` | ENUM | Sí | Nivel calculado: `low`, `medium`, `high`, `critical` |
| `score` | INTEGER | Sí | score = probability × impact. Rango: 1–25 |
| `probability` | INTEGER | Sí | Probabilidad de ocurrencia: 1 (muy baja) a 5 (muy alta) |
| `impact` | INTEGER | Sí | Impacto en la organización: 1 (muy bajo) a 5 (muy alto) |
| `notes` | VARCHAR(500) | No | Observaciones sobre la evaluación |
| `recorded_at` | TIMESTAMP TZ | Auto | Fecha/hora del registro |

**Lógica de cálculo del nivel de riesgo:**

```python
# Esta lógica va en risk_service.py
def calculate_risk_level(probability: int, impact: int) -> tuple[int, str]:
    score = probability * impact
    if score <= 4:
        level = "low"
    elif score <= 9:
        level = "medium"
    elif score <= 16:
        level = "high"
    else:
        level = "critical"
    return score, level
```

---

#### TABLA: `kpi_snapshots`

**Propósito:** Guardar snapshots periódicos de todos los KPIs para análisis de tendencias y reportes históricos.

```python
# app/models/snapshot.py
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Integer, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    total_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    resolved_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_resolution_hrs: Mapped[float] = mapped_column(Numeric(8, 2), nullable=True)
    total_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_compliant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_partial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_non_compliant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    global_compliance_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    global_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

**Campos explicados:**

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | PK |
| `snapshot_date` | DATE | Fecha del snapshot (única por día) |
| `total_incidents` | INTEGER | Total de incidentes registrados a esa fecha |
| `open_incidents` | INTEGER | Incidentes con status = open |
| `resolved_incidents` | INTEGER | Incidentes con status = closed |
| `critical_incidents` | INTEGER | Incidentes con severity = critical |
| `avg_resolution_hrs` | DECIMAL | Promedio de horas para cerrar un incidente |
| `total_controls` | INTEGER | Total de controles registrados |
| `controls_compliant` | INTEGER | Controles en status = compliant |
| `controls_partial` | INTEGER | Controles en status = partial |
| `controls_non_compliant` | INTEGER | Controles en status = non_compliant |
| `global_compliance_pct` | DECIMAL | (compliant / total) × 100 |
| `global_risk_score` | DECIMAL | Promedio del score de todos los risk_levels activos |
| `created_at` | TIMESTAMP TZ | Cuándo se generó el snapshot |

---

### 5.3 Enums (app/utils/enums.py)

```python
import enum

class SeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class IncidentStatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class ControlStatusEnum(str, enum.Enum):
    compliant = "compliant"
    partial = "partial"
    non_compliant = "non_compliant"

class RiskLevelEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
```

---

## 6. SCHEMAS PYDANTIC (v2)

### 6.1 Incidents (app/schemas/incident.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.utils.enums import SeverityEnum, IncidentStatusEnum

class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=200, description="Título del incidente")
    description: Optional[str] = Field(None, description="Descripción detallada")
    severity: SeverityEnum
    category: Optional[str] = Field(None, max_length=100)
    reported_by: Optional[str] = Field(None, max_length=100)

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatusEnum
    resolved_at: Optional[datetime] = None  # Requerido si status=closed

class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: SeverityEnum
    status: IncidentStatusEnum
    category: Optional[str]
    reported_by: Optional[str]
    reported_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}

class IncidentStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    closed: int
    by_severity: dict  # {"low": int, "medium": int, "high": int, "critical": int}
    avg_resolution_hrs: Optional[float]
    resolution_rate_pct: float  # (closed / total) * 100
```

### 6.2 Controls (app/schemas/control.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.utils.enums import ControlStatusEnum

class ControlCreate(BaseModel):
    iso_domain: str = Field(..., max_length=10, description="Ej: A.5, A.9")
    iso_control_ref: Optional[str] = Field(None, max_length=20)
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: ControlStatusEnum
    compliance_pct: float = Field(..., ge=0.0, le=100.0)
    responsible: Optional[str] = Field(None, max_length=100)
    last_reviewed: Optional[date] = None

class ControlUpdate(BaseModel):
    status: Optional[ControlStatusEnum] = None
    compliance_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    responsible: Optional[str] = None
    last_reviewed: Optional[date] = None
    description: Optional[str] = None

class ControlResponse(BaseModel):
    id: UUID
    iso_domain: str
    iso_control_ref: Optional[str]
    name: str
    description: Optional[str]
    status: ControlStatusEnum
    compliance_pct: float
    responsible: Optional[str]
    last_reviewed: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ComplianceResponse(BaseModel):
    total_controls: int
    compliant: int
    partial: int
    non_compliant: int
    global_compliance_pct: float
    by_domain: dict  # {"A.5": {"compliant": 3, "total": 4, "pct": 75.0}, ...}
```

### 6.3 Risk (app/schemas/risk.py)

```python
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.utils.enums import RiskLevelEnum

class RiskCreate(BaseModel):
    domain: str = Field(..., max_length=100)
    probability: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)
    # score y level se calculan automáticamente en el servicio

class RiskResponse(BaseModel):
    id: UUID
    domain: str
    level: RiskLevelEnum
    score: int
    probability: int
    impact: int
    notes: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}

class RiskCurrentResponse(BaseModel):
    global_score: float
    global_level: RiskLevelEnum
    total_domains: int
    by_level: dict  # {"low": 2, "medium": 3, "high": 1, "critical": 0}
    highest_risk_domain: Optional[str]
    recorded_at: datetime

class RiskByDomainItem(BaseModel):
    domain: str
    level: RiskLevelEnum
    score: int
    probability: int
    impact: int
    recorded_at: datetime

class RiskByDomainResponse(BaseModel):
    domains: list[RiskByDomainItem]
    total: int
```

### 6.4 Dashboard (app/schemas/dashboard.py)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardSummaryResponse(BaseModel):
    generated_at: datetime
    # Bloque incidentes
    incidents_total: int
    incidents_open: int
    incidents_in_progress: int
    incidents_closed: int
    incidents_critical_active: int
    incidents_avg_resolution_hrs: Optional[float]
    incidents_resolution_rate_pct: float
    # Bloque controles
    controls_total: int
    controls_compliant: int
    controls_non_compliant: int
    controls_global_compliance_pct: float
    # Bloque riesgo
    risk_global_score: Optional[float]
    risk_global_level: Optional[str]
    risk_highest_domain: Optional[str]

class KpiItem(BaseModel):
    name: str
    value: float
    unit: str
    status: str   # "green" | "amber" | "red"
    threshold_green: float
    threshold_amber: float
    description: str

class DashboardKpisResponse(BaseModel):
    generated_at: datetime
    kpis: list[KpiItem]

class DashboardExportResponse(BaseModel):
    format: str
    generated_at: datetime
    data: dict
```

---

## 7. ENDPOINTS — ESPECIFICACIÓN COMPLETA

> **Base URL:** `http://localhost:8000/api/v1`  
> Todos los endpoints devuelven JSON. Los errores siguen el formato `{"detail": "mensaje de error"}`.

---

### 7.1 MÓDULO: `/incidents`

---

#### `GET /api/v1/incidents`

**Descripción:** Devuelve la lista paginada de todos los incidentes registrados, con soporte para filtros opcionales.

**Query parameters:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `skip` | int | No | 0 | Offset de paginación |
| `limit` | int | No | 20 | Máximo de resultados (max: 100) |
| `status` | string | No | — | Filtrar por: `open`, `in_progress`, `closed` |
| `severity` | string | No | — | Filtrar por: `low`, `medium`, `high`, `critical` |
| `category` | string | No | — | Filtrar por categoría exacta |

**Response 200:**

```json
{
  "total": 42,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "title": "Acceso no autorizado al servidor de archivos",
      "description": "...",
      "severity": "high",
      "status": "open",
      "category": "acceso_no_autorizado",
      "reported_by": "admin@empresa.com",
      "reported_at": "2026-03-10T14:30:00Z",
      "resolved_at": null
    }
  ]
}
```

**Lógica:**
1. Construir query SELECT sobre `incidents`.
2. Aplicar filtros si vienen en query params (WHERE severity = X, etc.).
3. Aplicar ORDER BY reported_at DESC.
4. Aplicar LIMIT y OFFSET.
5. Hacer COUNT(*) con los mismos filtros para el campo `total`.

---

#### `POST /api/v1/incidents`

**Descripción:** Registra un nuevo incidente de seguridad en el sistema.

**Request body:** `IncidentCreate`

```json
{
  "title": "Phishing detectado en correo corporativo",
  "description": "Usuario recibió email sospechoso con enlace malicioso",
  "severity": "medium",
  "category": "phishing",
  "reported_by": "soporte@empresa.com"
}
```

**Response 201:** `IncidentResponse` (el incidente creado completo)

**Lógica:**
1. Validar body con Pydantic (`IncidentCreate`).
2. Crear instancia del modelo `Incident`.
3. Asignar `id` = uuid4, `status` = `open`, `reported_at` = datetime.now(UTC).
4. `resolved_at` = None.
5. Guardar en base de datos.
6. Retornar el incidente creado con status HTTP 201.

---

#### `GET /api/v1/incidents/{incident_id}`

**Descripción:** Devuelve el detalle completo de un incidente específico por su UUID.

**Path parameter:** `incident_id` (UUID)

**Response 200:** `IncidentResponse`

**Response 404:**
```json
{"detail": "Incidente no encontrado"}
```

**Lógica:**
1. Buscar en `incidents` WHERE id = incident_id.
2. Si no existe → raise HTTPException(404).
3. Si existe → retornar como `IncidentResponse`.

---

#### `PUT /api/v1/incidents/{incident_id}/status`

**Descripción:** Actualiza el estado de un incidente. Si el nuevo estado es `closed`, registra automáticamente la fecha de resolución.

**Path parameter:** `incident_id` (UUID)

**Request body:** `IncidentStatusUpdate`

```json
{
  "status": "closed",
  "resolved_at": "2026-03-15T09:00:00Z"
}
```

**Response 200:** `IncidentResponse` (incidente actualizado)

**Response 404:** Si el incidente no existe.

**Response 422:** Si status = `closed` pero `resolved_at` es null (validar en el servicio).

**Lógica:**
1. Buscar el incidente por ID → 404 si no existe.
2. Si `status` = `closed` y `resolved_at` es None → asignar `resolved_at` = datetime.now(UTC).
3. Si `status` != `closed` → limpiar `resolved_at` a None.
4. Actualizar el registro.
5. Retornar el incidente actualizado.

---

#### `GET /api/v1/incidents/stats`

**Descripción:** Devuelve los KPIs calculados sobre todos los incidentes. Este es el endpoint principal de métricas de incidentes.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `days` | int | 30 | Últimos N días a considerar para el cálculo |

**Response 200:** `IncidentStatsResponse`

```json
{
  "total": 42,
  "open": 15,
  "in_progress": 8,
  "closed": 19,
  "by_severity": {
    "low": 10,
    "medium": 18,
    "high": 10,
    "critical": 4
  },
  "avg_resolution_hrs": 28.5,
  "resolution_rate_pct": 45.24
}
```

**Lógica:**
1. Filtrar incidentes de los últimos `days` días (WHERE reported_at >= NOW() - INTERVAL 'X days').
2. Calcular `total` = COUNT(*).
3. Calcular `open`, `in_progress`, `closed` = COUNT(*) WHERE status = X.
4. Calcular `by_severity` = COUNT(*) GROUP BY severity.
5. Calcular `avg_resolution_hrs`: para incidentes cerrados, promedio de (resolved_at - reported_at) en horas.
6. Calcular `resolution_rate_pct` = (closed / total) * 100. Si total = 0 → retornar 0.0.

> **IMPORTANTE:** Este endpoint es el KPI principal de incidentes. No es un endpoint CRUD, es analítico.

---

### 7.2 MÓDULO: `/controls`

---

#### `GET /api/v1/controls`

**Descripción:** Devuelve todos los controles ISO 27001 registrados, con filtros opcionales.

**Query parameters:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `skip` | int | No | 0 | Offset |
| `limit` | int | No | 50 | Máximo resultados |
| `status` | string | No | — | `compliant`, `partial`, `non_compliant` |
| `iso_domain` | string | No | — | Filtrar por dominio: `A.5`, `A.9`, etc. |

**Response 200:**

```json
{
  "total": 35,
  "items": [
    {
      "id": "uuid",
      "iso_domain": "A.9",
      "iso_control_ref": "A.9.1.1",
      "name": "Política de control de acceso",
      "description": "...",
      "status": "compliant",
      "compliance_pct": 95.0,
      "responsible": "CISO",
      "last_reviewed": "2026-02-01",
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-02-01T08:00:00Z"
    }
  ]
}
```

**Lógica:** SELECT con filtros opcionales, ORDER BY iso_domain ASC, iso_control_ref ASC.

---

#### `POST /api/v1/controls`

**Descripción:** Registra un nuevo control ISO 27001 en el sistema.

**Request body:** `ControlCreate`

```json
{
  "iso_domain": "A.9",
  "iso_control_ref": "A.9.1.1",
  "name": "Política de control de acceso",
  "description": "Establecer, documentar y revisar la política de control de acceso.",
  "status": "partial",
  "compliance_pct": 60.0,
  "responsible": "Área de TI",
  "last_reviewed": "2026-01-20"
}
```

**Response 201:** `ControlResponse`

**Lógica:**
1. Validar body.
2. Crear `Control` con uuid4, timestamps automáticos.
3. Guardar y retornar con 201.

---

#### `PUT /api/v1/controls/{control_id}`

**Descripción:** Actualiza parcialmente un control (PATCH semántico con PUT). Permite actualizar status, porcentaje, responsable o fecha de revisión.

**Path parameter:** `control_id` (UUID)

**Request body:** `ControlUpdate` (todos los campos opcionales)

```json
{
  "status": "compliant",
  "compliance_pct": 100.0,
  "last_reviewed": "2026-03-15"
}
```

**Response 200:** `ControlResponse` (control actualizado)

**Response 404:** Si el control no existe.

**Lógica:**
1. Buscar control por ID → 404 si no existe.
2. Solo actualizar los campos que vengan en el body (no None).
3. Actualizar `updated_at` = datetime.now(UTC).
4. Guardar y retornar.

---

#### `GET /api/v1/controls/compliance`

**Descripción:** Devuelve el KPI de cumplimiento global de controles ISO 27001. Es el endpoint analítico más importante del módulo.

**Response 200:** `ComplianceResponse`

```json
{
  "total_controls": 35,
  "compliant": 22,
  "partial": 8,
  "non_compliant": 5,
  "global_compliance_pct": 62.86,
  "by_domain": {
    "A.5": {
      "total": 4,
      "compliant": 3,
      "partial": 1,
      "non_compliant": 0,
      "compliance_pct": 75.0
    },
    "A.9": {
      "total": 6,
      "compliant": 4,
      "partial": 1,
      "non_compliant": 1,
      "compliance_pct": 66.67
    }
  }
}
```

**Lógica:**
1. SELECT COUNT(*) total, COUNT WHERE status='compliant', COUNT WHERE status='partial', COUNT WHERE status='non_compliant'.
2. global_compliance_pct = (compliant / total) * 100.
3. GROUP BY iso_domain para construir `by_domain`.
4. Para cada dominio: calcular compliance_pct = (compliant_en_dominio / total_en_dominio) * 100.

---

### 7.3 MÓDULO: `/risk`

---

#### `GET /api/v1/risk/current`

**Descripción:** Devuelve el estado de riesgo actual del SGSI, calculado sobre el último registro de cada dominio.

**Response 200:** `RiskCurrentResponse`

```json
{
  "global_score": 11.3,
  "global_level": "high",
  "total_domains": 8,
  "by_level": {
    "low": 2,
    "medium": 3,
    "high": 2,
    "critical": 1
  },
  "highest_risk_domain": "Control de Acceso",
  "recorded_at": "2026-03-15T14:00:00Z"
}
```

**Lógica:**
1. Para cada `domain` único, tomar el registro más reciente (MAX recorded_at).
2. Calcular `global_score` = promedio de los scores de esos registros.
3. Calcular `global_level` a partir del `global_score` usando la misma función de cálculo.
4. Contar cuántos dominios tienen cada nivel → `by_level`.
5. `highest_risk_domain` = dominio con el score más alto.
6. `recorded_at` = MAX(recorded_at) de todos los registros considerados.

---

#### `POST /api/v1/risk`

**Descripción:** Registra una nueva evaluación de riesgo para un dominio. El score y el nivel se calculan automáticamente.

**Request body:** `RiskCreate`

```json
{
  "domain": "Control de Acceso",
  "probability": 4,
  "impact": 5,
  "notes": "Múltiples cuentas sin MFA habilitado"
}
```

**Response 201:** `RiskResponse`

```json
{
  "id": "uuid",
  "domain": "Control de Acceso",
  "level": "critical",
  "score": 20,
  "probability": 4,
  "impact": 5,
  "notes": "Múltiples cuentas sin MFA habilitado",
  "recorded_at": "2026-03-15T14:00:00Z"
}
```

**Lógica:**
1. Validar body (probability y impact entre 1–5).
2. Calcular `score` = probability × impact.
3. Calcular `level` usando la función `calculate_risk_level`.
4. Crear el registro con uuid4 y recorded_at = NOW(UTC).
5. Guardar y retornar con 201.

---

#### `GET /api/v1/risk/history`

**Descripción:** Devuelve el historial de evaluaciones de riesgo, útil para ver la evolución del riesgo en el tiempo.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `days` | int | 90 | Últimos N días |
| `domain` | string | — | Filtrar por dominio específico |
| `skip` | int | 0 | Offset |
| `limit` | int | 50 | Límite |

**Response 200:**

```json
{
  "total": 24,
  "items": [
    {
      "id": "uuid",
      "domain": "Control de Acceso",
      "level": "high",
      "score": 16,
      "probability": 4,
      "impact": 4,
      "notes": "...",
      "recorded_at": "2026-03-01T10:00:00Z"
    }
  ]
}
```

**Lógica:** SELECT WHERE recorded_at >= NOW() - INTERVAL 'X days', con filtro opcional de domain. ORDER BY recorded_at DESC.

---

#### `GET /api/v1/risk/by-domain`

**Descripción:** Devuelve el riesgo actual de cada dominio (último registro por dominio), ordenado de mayor a menor score.

**Response 200:** `RiskByDomainResponse`

```json
{
  "domains": [
    {
      "domain": "Control de Acceso",
      "level": "critical",
      "score": 20,
      "probability": 4,
      "impact": 5,
      "recorded_at": "2026-03-15T14:00:00Z"
    },
    {
      "domain": "Seguridad Física",
      "level": "medium",
      "score": 9,
      "probability": 3,
      "impact": 3,
      "recorded_at": "2026-03-10T09:00:00Z"
    }
  ],
  "total": 8
}
```

**Lógica:**
1. Hacer subquery para obtener el MAX(recorded_at) por cada dominio.
2. JOIN con `risk_levels` para obtener el registro completo más reciente de cada dominio.
3. ORDER BY score DESC.

---

### 7.4 MÓDULO: `/dashboard`

---

#### `GET /api/v1/dashboard/summary`

**Descripción:** Endpoint principal para la alta dirección. Consolida todos los KPIs del SGSI en un solo response. Este es el endpoint más importante de la API.

**Response 200:** `DashboardSummaryResponse`

```json
{
  "generated_at": "2026-03-17T10:00:00Z",
  "incidents_total": 42,
  "incidents_open": 15,
  "incidents_in_progress": 8,
  "incidents_closed": 19,
  "incidents_critical_active": 3,
  "incidents_avg_resolution_hrs": 28.5,
  "incidents_resolution_rate_pct": 45.24,
  "controls_total": 35,
  "controls_compliant": 22,
  "controls_non_compliant": 5,
  "controls_global_compliance_pct": 62.86,
  "risk_global_score": 11.3,
  "risk_global_level": "high",
  "risk_highest_domain": "Control de Acceso"
}
```

**Lógica:**
1. Ejecutar las mismas queries que hacen `/incidents/stats`, `/controls/compliance` y `/risk/current`.
2. Se puede hacer en paralelo con `asyncio.gather()` para optimizar.
3. Consolidar todos los resultados en un solo objeto `DashboardSummaryResponse`.
4. `generated_at` = datetime.now(UTC).

---

#### `GET /api/v1/dashboard/kpis`

**Descripción:** Devuelve todos los KPIs con sus valores actuales, umbrales de alerta semáforo (verde/ámbar/rojo) y descripciones.

**Response 200:** `DashboardKpisResponse`

```json
{
  "generated_at": "2026-03-17T10:00:00Z",
  "kpis": [
    {
      "name": "Tasa de Resolución de Incidentes",
      "value": 45.24,
      "unit": "%",
      "status": "red",
      "threshold_green": 80.0,
      "threshold_amber": 60.0,
      "description": "Porcentaje de incidentes cerrados sobre el total"
    },
    {
      "name": "Cumplimiento de Controles ISO",
      "value": 62.86,
      "unit": "%",
      "status": "amber",
      "threshold_green": 85.0,
      "threshold_amber": 70.0,
      "description": "Porcentaje de controles en estado compliant"
    },
    {
      "name": "Score de Riesgo Global",
      "value": 11.3,
      "unit": "score",
      "status": "red",
      "threshold_green": 6.0,
      "threshold_amber": 10.0,
      "description": "Promedio del score de riesgo (probabilidad x impacto) por dominio"
    },
    {
      "name": "MTTR (Tiempo Medio de Resolución)",
      "value": 28.5,
      "unit": "horas",
      "status": "amber",
      "threshold_green": 24.0,
      "threshold_amber": 48.0,
      "description": "Promedio de horas para resolver un incidente"
    }
  ]
}
```

**Lógica del semáforo:**

```python
def get_kpi_status(value: float, threshold_green: float, threshold_amber: float, higher_is_better: bool = True) -> str:
    if higher_is_better:
        if value >= threshold_green:
            return "green"
        elif value >= threshold_amber:
            return "amber"
        else:
            return "red"
    else:
        # Para KPIs donde menor es mejor (ej: score de riesgo, MTTR)
        if value <= threshold_green:
            return "green"
        elif value <= threshold_amber:
            return "amber"
        else:
            return "red"
```

**KPIs y sus umbrales (hardcodeados en el servicio):**

| KPI | Verde | Ámbar | Rojo | Dirección |
|---|---|---|---|---|
| Tasa de resolución de incidentes | >= 80% | >= 60% | < 60% | Mayor es mejor |
| Cumplimiento de controles ISO | >= 85% | >= 70% | < 70% | Mayor es mejor |
| Score de riesgo global | <= 6 | <= 10 | > 10 | Menor es mejor |
| MTTR (horas) | <= 24h | <= 48h | > 48h | Menor es mejor |

---

#### `GET /api/v1/dashboard/export`

**Descripción:** Exporta todos los datos del SGSI en un JSON estructurado listo para descargar, guardar o enviar a un sistema externo.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `format` | string | `json` | Solo `json` en el PoC |

**Response 200:** `DashboardExportResponse`

```json
{
  "format": "json",
  "generated_at": "2026-03-17T10:00:00Z",
  "data": {
    "summary": { /* mismo objeto que /dashboard/summary */ },
    "kpis": [ /* mismo array que /dashboard/kpis */ ],
    "incidents": {
      "stats": { /* mismo objeto que /incidents/stats */ },
      "recent": [ /* últimos 10 incidentes */ ]
    },
    "controls": {
      "compliance": { /* mismo objeto que /controls/compliance */ }
    },
    "risk": {
      "current": { /* mismo objeto que /risk/current */ },
      "by_domain": { /* mismo objeto que /risk/by-domain */ }
    }
  }
}
```

**Lógica:** Ejecutar todos los endpoints analíticos en paralelo y consolidar.

---

## 8. ARCHIVO main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import incidents, controls, risk, dashboard
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al iniciar (en producción usar Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="ISO_SECURE — SGSI KPI API",
    description="API REST para indicadores y métricas de seguridad del SGSI conforme a ISO/IEC 27001:2022",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

app.include_router(incidents.router, prefix=f"{API_PREFIX}/incidents", tags=["Incidents"])
app.include_router(controls.router, prefix=f"{API_PREFIX}/controls", tags=["Controls"])
app.include_router(risk.router, prefix=f"{API_PREFIX}/risk", tags=["Risk"])
app.include_router(dashboard.router, prefix=f"{API_PREFIX}/dashboard", tags=["Dashboard"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "ISO_SECURE", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
```

---

## 9. SCRIPT DE SEED (seed.py)

El script debe insertar datos realistas en las 4 tablas. Usar la librería `Faker` con locale `es_ES`.

```python
# seed.py
import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone, date
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base
from app.models.incident import Incident
from app.models.control import Control
from app.models.risk import RiskLevel
from app.models.snapshot import KpiSnapshot
from app.utils.enums import SeverityEnum, IncidentStatusEnum, ControlStatusEnum, RiskLevelEnum
from dotenv import load_dotenv
import os

load_dotenv()
fake = Faker('es_ES')

# --- Datos de referencia ---

INCIDENT_CATEGORIES = ["phishing", "malware", "acceso_no_autorizado", "fuga_de_datos", "denegacion_servicio", "otro"]

INCIDENT_TITLES = [
    "Phishing detectado en correo corporativo",
    "Intento de acceso no autorizado al servidor",
    "Infección por ransomware en estación de trabajo",
    "Fuga de datos de clientes en base de datos",
    "Credenciales comprometidas detectadas",
    "Denegación de servicio en portal web",
    "Malware en dispositivo de usuario",
    "Acceso fuera de horario a sistemas críticos",
    "Exfiltración de datos sospechosa por VPN",
    "Vulnerabilidad crítica sin parche en servidor",
]

ISO_CONTROLS = [
    ("A.5",  "A.5.1",  "Políticas de seguridad de la información"),
    ("A.5",  "A.5.2",  "Revisión de las políticas de seguridad"),
    ("A.6",  "A.6.1",  "Roles y responsabilidades de seguridad"),
    ("A.6",  "A.6.2",  "Segregación de funciones"),
    ("A.7",  "A.7.1",  "Seguridad en la contratación"),
    ("A.7",  "A.7.2",  "Concienciación y formación en seguridad"),
    ("A.8",  "A.8.1",  "Inventario de activos de información"),
    ("A.8",  "A.8.2",  "Clasificación de la información"),
    ("A.9",  "A.9.1",  "Política de control de acceso"),
    ("A.9",  "A.9.2",  "Gestión de acceso de usuarios"),
    ("A.9",  "A.9.3",  "Responsabilidades del usuario"),
    ("A.9",  "A.9.4",  "Control de acceso a sistemas y aplicaciones"),
    ("A.10", "A.10.1", "Controles criptográficos"),
    ("A.11", "A.11.1", "Seguridad de las áreas seguras"),
    ("A.11", "A.11.2", "Seguridad de los equipos"),
    ("A.12", "A.12.1", "Procedimientos operacionales y responsabilidades"),
    ("A.12", "A.12.2", "Protección contra malware"),
    ("A.12", "A.12.3", "Copias de seguridad"),
    ("A.12", "A.12.4", "Registro y supervisión"),
    ("A.13", "A.13.1", "Gestión de seguridad en redes"),
    ("A.14", "A.14.1", "Requisitos de seguridad en sistemas de información"),
    ("A.15", "A.15.1", "Seguridad en las relaciones con proveedores"),
    ("A.16", "A.16.1", "Gestión de incidentes de seguridad"),
    ("A.17", "A.17.1", "Continuidad de la seguridad de la información"),
    ("A.18", "A.18.1", "Cumplimiento con requisitos legales y contractuales"),
]

RISK_DOMAINS = [
    "Seguridad de Activos",
    "Control de Acceso",
    "Criptografía",
    "Seguridad Física y del Entorno",
    "Seguridad en Operaciones",
    "Seguridad en Comunicaciones",
    "Gestión de Incidentes",
    "Continuidad del Negocio",
]
```

**Datos de incidentes a insertar:** 30 incidentes con fechas aleatorias en los últimos 90 días. Distribución sugerida: 40% closed, 30% in_progress, 30% open. Severidades: 25% critical, 35% high, 25% medium, 15% low.

**Datos de controles a insertar:** Los 25 controles listados en `ISO_CONTROLS`. Distribución sugerida: 50% compliant (compliance_pct entre 85–100), 30% partial (40–84), 20% non_compliant (0–39).

**Datos de risk_levels a insertar:** Para cada uno de los 8 dominios, insertar 3 registros históricos (hace 60 días, hace 30 días, hoy) para poder ver evolución.

**Datos de kpi_snapshots a insertar:** 30 snapshots, uno por día durante el último mes, con datos calculados coherentes con los incidentes y controles.

---

## 10. TABLA RESUMEN DE ENDPOINTS

| Método | Endpoint | Tipo | Descripción |
|---|---|---|---|
| GET | `/api/v1/incidents` | CRUD | Listar incidentes con filtros y paginación |
| POST | `/api/v1/incidents` | CRUD | Reportar nuevo incidente |
| GET | `/api/v1/incidents/{id}` | CRUD | Detalle de un incidente |
| PUT | `/api/v1/incidents/{id}/status` | CRUD | Cambiar estado del incidente |
| GET | `/api/v1/incidents/stats` | **KPI** | Estadísticas: total, tasa resolución, MTTR, por severidad |
| GET | `/api/v1/controls` | CRUD | Listar controles con filtros |
| POST | `/api/v1/controls` | CRUD | Registrar control ISO 27001 |
| PUT | `/api/v1/controls/{id}` | CRUD | Actualizar control |
| GET | `/api/v1/controls/compliance` | **KPI** | % cumplimiento global y por dominio |
| GET | `/api/v1/risk/current` | **KPI** | Nivel de riesgo actual del SGSI |
| POST | `/api/v1/risk` | CRUD | Registrar evaluación de riesgo |
| GET | `/api/v1/risk/history` | CRUD | Historial de riesgos por período |
| GET | `/api/v1/risk/by-domain` | **KPI** | Riesgo actual desglosado por dominio |
| GET | `/api/v1/dashboard/summary` | **KPI** | Resumen ejecutivo consolidado |
| GET | `/api/v1/dashboard/kpis` | **KPI** | KPIs con semáforo verde/ámbar/rojo |
| GET | `/api/v1/dashboard/export` | Export | Exportar todos los datos en JSON |

---

## 11. INSTRUCCIONES PARA EL AGENTE IA

Cuando generes el código de este proyecto, sigue estas reglas estrictamente:

1. **Genera el proyecto completo**, no fragmentos. Todos los archivos listados en la estructura de carpetas deben existir.

2. **Usa SQLAlchemy 2.0 async** con `Mapped` y `mapped_column`. No uses el estilo declarativo antiguo.

3. **Todos los IDs son UUID4**. Nunca uses enteros autoincrement como PK.

4. **Todas las fechas van en UTC** usando `datetime.now(timezone.utc)`.

5. **Los endpoints analíticos** (`/stats`, `/compliance`, `/current`, `/by-domain`, `/summary`, `/kpis`) no son CRUD. Hacen queries agregadas. No retornan listas simples.

6. **El router de `/incidents/stats`** debe declararse ANTES de `/{incident_id}` para que FastAPI no lo confunda con un path parameter.

7. **Los servicios** contienen toda la lógica de negocio. Los routers solo validan y llaman al servicio correspondiente.

8. **El script `seed.py`** debe ser ejecutable directamente con `python seed.py` y debe limpiar las tablas antes de insertar.

9. **La función `calculate_risk_level`** en `risk_service.py` es la única fuente de verdad para el cálculo de score y nivel. No duplicarla.

10. **En `dashboard_service.py`**, usar `asyncio.gather()` para ejecutar las queries en paralelo.

11. **Genera los comments en español** en el código, ya que es un proyecto universitario en español.

12. **No implementes autenticación** en el PoC. El CORS está abierto para pruebas locales.

13. **El `.env.example`** debe tener todas las variables con valores de ejemplo pero sin credenciales reales.

14. **Supabase:** La conexión es a través de la connection string de PostgreSQL directa (no usar el SDK de Supabase). El `DATABASE_URL` usa el formato `postgresql+asyncpg://...`.

---

## 12. CÓMO EJECUTAR EL PROYECTO

```bash
# 1. Clonar / crear el proyecto
cd iso_secure

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con la DATABASE_URL de Supabase

# 5. Crear tablas (o usar Alembic para migraciones)
python -c "import asyncio; from app.database import engine, Base; asyncio.run(engine.begin().__aenter__().run_sync(Base.metadata.create_all))"

# 6. Poblar con datos de prueba
python seed.py

# 7. Ejecutar el servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 8. Verificar
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
# API: http://localhost:8000/api/v1/dashboard/summary
```

---

*Documento generado como contexto para agente IA — Proyecto ISO_SECURE 27001 — Universidad de San Buenaventura — Exposición: 18 de marzo de 2026*
