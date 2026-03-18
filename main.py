from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import incidents, controls, risk, dashboard, snapshots
import os
from dotenv import load_dotenv

load_dotenv()

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
app.include_router(snapshots.router, prefix=f"{API_PREFIX}/snapshots", tags=["Snapshots"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "ISO_SECURE", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
