import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone, date as date_type
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import delete
from app.database import Base, DATABASE_URL
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

# --- Lógica de cálculo auxiliar ---
def calculate_risk(prob, impact):
    score = prob * impact
    if score <= 4: level = RiskLevelEnum.low
    elif score <= 9: level = RiskLevelEnum.medium
    elif score <= 16: level = RiskLevelEnum.high
    else: level = RiskLevelEnum.critical
    return score, level

async def seed():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # 1. Limpiar tablas
        print("Limpiando tablas...")
        await session.execute(delete(KpiSnapshot))
        await session.execute(delete(Incident))
        await session.execute(delete(Control))
        await session.execute(delete(RiskLevel))
        await session.commit()

        # 2. Seed Incidents (30 registros)
        print("Insertando incidentes...")
        for _ in range(30):
            reported_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 90))
            status = random.choices(
                [IncidentStatusEnum.open, IncidentStatusEnum.in_progress, IncidentStatusEnum.closed],
                weights=[30, 30, 40]
            )[0]
            
            resolved_at = None
            if status == IncidentStatusEnum.closed:
                resolved_at = reported_at + timedelta(hours=random.randint(1, 72))
                # Asegurar que no sea mayor que NOW
                if resolved_at > datetime.now(timezone.utc):
                    resolved_at = datetime.now(timezone.utc)

            incident = Incident(
                id=uuid.uuid4(),
                title=random.choice(INCIDENT_TITLES),
                description=fake.sentence(),
                severity=random.choices(
                    [SeverityEnum.low, SeverityEnum.medium, SeverityEnum.high, SeverityEnum.critical],
                    weights=[15, 25, 35, 25]
                )[0],
                status=status,
                category=random.choice(INCIDENT_CATEGORIES),
                reported_by=fake.name(),
                reported_at=reported_at,
                resolved_at=resolved_at
            )
            session.add(incident)

        # 3. Seed Controls (25 registros)
        print("Insertando controles...")
        for domain, ref, name in ISO_CONTROLS:
            status = random.choices(
                [ControlStatusEnum.compliant, ControlStatusEnum.partial, ControlStatusEnum.non_compliant],
                weights=[50, 30, 20]
            )[0]
            
            compliance_pct = 0.0
            if status == ControlStatusEnum.compliant: compliance_pct = random.uniform(85, 100)
            elif status == ControlStatusEnum.partial: compliance_pct = random.uniform(40, 84)
            else: compliance_pct = random.uniform(0, 39)

            control = Control(
                id=uuid.uuid4(),
                iso_domain=domain,
                iso_control_ref=ref,
                name=name,
                description=f"Control de seguridad para {name}",
                status=status,
                compliance_pct=round(compliance_pct, 2),
                responsible=random.choice(["CISO", "Área de TI", "RH", "Legal"]),
                last_reviewed=date_type.today() - timedelta(days=random.randint(0, 60))
            )
            session.add(control)

        # 4. Seed Risk Levels (8 dominios x 3 registros)
        print("Insertando evaluaciones de riesgo...")
        for domain in RISK_DOMAINS:
            for days_ago in [60, 30, 0]:
                prob = random.randint(1, 5)
                imp = random.randint(1, 5)
                score, level = calculate_risk(prob, imp)
                
                risk = RiskLevel(
                    id=uuid.uuid4(),
                    domain=domain,
                    level=level,
                    score=score,
                    probability=prob,
                    impact=imp,
                    notes=fake.sentence(),
                    recorded_at=datetime.now(timezone.utc) - timedelta(days=days_ago)
                )
                session.add(risk)

        # 5. Seed Snapshots (30 días)
        print("Insertando snapshots históricos...")
        for i in range(30, -1, -1):
            snap_date = date_type.today() - timedelta(days=i)
            snapshot = KpiSnapshot(
                id=uuid.uuid4(),
                snapshot_date=snap_date,
                total_incidents=random.randint(10, 50),
                open_incidents=random.randint(5, 20),
                resolved_incidents=random.randint(5, 30),
                critical_incidents=random.randint(1, 5),
                avg_resolution_hrs=round(random.uniform(10, 48), 2),
                total_controls=25,
                controls_compliant=random.randint(10, 15),
                controls_partial=random.randint(5, 10),
                controls_non_compliant=random.randint(1, 5),
                global_compliance_pct=round(random.uniform(50, 90), 2),
                global_risk_score=round(random.uniform(5, 15), 2)
            )
            session.add(snapshot)

        await session.commit()
        print("Seed completado con éxito.")

if __name__ == "__main__":
    asyncio.run(seed())
