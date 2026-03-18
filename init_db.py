import asyncio
from app.database import engine, Base
from app.models.incident import Incident
from app.models.control import Control
from app.models.risk import RiskLevel
from app.models.snapshot import KpiSnapshot

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas recreadas con func.now().")

if __name__ == "__main__":
    asyncio.run(init_db())
