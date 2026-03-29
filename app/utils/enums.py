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
    en_proceso = "en_proceso"
    non_compliant = "non_compliant"

class RiskLevelEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    auditor = "auditor"
    supervisor = "supervisor"
    analista = "analista"

class NivelCursoEnum(str, enum.Enum):
    basico = "basico"
    intermedio = "intermedio"
    avanzado = "avanzado"

class ProgresoEnum(str, enum.Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    completado = "completado"

class AuditoriaStatusEnum(str, enum.Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    completado = "completado"
