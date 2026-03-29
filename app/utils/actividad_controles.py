"""
Mapeo de actividad económica → dominios ISO/IEC 27001:2022 recomendados.
Cada entrada incluye la justificación de por qué aplica a ese sector.
"""

RECOMENDACIONES: dict[str, list[dict]] = {
    "financiero": [
        {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
         "justificacion": "El sector financiero maneja datos sensibles de clientes y transacciones; requiere políticas robustas de seguridad de la información."},
        {"dominio": "A.6", "ref": "6.1 – 6.8", "nombre": "Controles de personas",
         "justificacion": "Los empleados con acceso a sistemas financieros deben ser investigados y entrenados en seguridad."},
        {"dominio": "A.8", "ref": "8.1 – 8.34", "nombre": "Controles tecnológicos",
         "justificacion": "Los sistemas bancarios y de pagos requieren controles técnicos estrictos contra accesos no autorizados y fraude."},
        {"dominio": "A.5.14", "ref": "5.14", "nombre": "Transferencia de información",
         "justificacion": "Las transferencias financieras deben estar cifradas y auditadas end-to-end."},
        {"dominio": "A.8.16", "ref": "8.16", "nombre": "Monitoreo de actividades",
         "justificacion": "Detección de transacciones fraudulentas y accesos anómalos en tiempo real."},
    ],
    "salud": [
        {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
         "justificacion": "Los datos de salud de pacientes son datos sensibles protegidos por ley; se requieren políticas estrictas."},
        {"dominio": "A.8.2", "ref": "8.2", "nombre": "Derechos de acceso privilegiado",
         "justificacion": "El acceso a historiales clínicos debe estar restringido a personal autorizado con mínimos privilegios."},
        {"dominio": "A.8.11", "ref": "8.11", "nombre": "Enmascaramiento de datos",
         "justificacion": "Los datos de pacientes deben anonimizarse cuando se usen para análisis o investigación."},
        {"dominio": "A.8.24", "ref": "8.24", "nombre": "Uso de criptografía",
         "justificacion": "Los registros médicos electrónicos deben estar cifrados en tránsito y en reposo."},
        {"dominio": "A.5.34", "ref": "5.34", "nombre": "Privacidad y protección de datos personales",
         "justificacion": "Cumplimiento con normativas de protección de datos personales de salud (e.g., Ley 1581 Colombia)."},
    ],
    "tecnologia": [
        {"dominio": "A.8", "ref": "8.1 – 8.34", "nombre": "Controles tecnológicos",
         "justificacion": "Las empresas de tecnología deben proteger su código fuente, infraestructura y datos de clientes."},
        {"dominio": "A.8.8", "ref": "8.8", "nombre": "Gestión de vulnerabilidades técnicas",
         "justificacion": "Las empresas tech son objetivo frecuente de ataques; el parcheo oportuno es crítico."},
        {"dominio": "A.8.25", "ref": "8.25", "nombre": "Ciclo de vida de desarrollo seguro",
         "justificacion": "La seguridad debe integrarse en el SDLC desde el diseño (Security by Design)."},
        {"dominio": "A.8.29", "ref": "8.29", "nombre": "Pruebas de seguridad en desarrollo",
         "justificacion": "Las aplicaciones deben pasar pruebas de seguridad (SAST/DAST) antes de salir a producción."},
        {"dominio": "A.5.23", "ref": "5.23", "nombre": "Seguridad en servicios en la nube",
         "justificacion": "Las empresas tecnológicas suelen operar en nube; deben gestionar la seguridad del proveedor cloud."},
    ],
    "educacion": [
        {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
         "justificacion": "Las instituciones educativas manejan datos de menores de edad y expedientes académicos sensibles."},
        {"dominio": "A.6.3", "ref": "6.3", "nombre": "Concienciación, educación y capacitación en SI",
         "justificacion": "Estudiantes y docentes deben ser entrenados en prácticas seguras de uso de TI."},
        {"dominio": "A.8.3", "ref": "8.3", "nombre": "Restricción de acceso a la información",
         "justificacion": "Los sistemas LMS y bases de datos académicas deben limitar acceso según roles."},
        {"dominio": "A.5.34", "ref": "5.34", "nombre": "Privacidad y protección de datos personales",
         "justificacion": "Cumplimiento con normativas de privacidad para datos de estudiantes menores de edad."},
    ],
    "comercio": [
        {"dominio": "A.8.24", "ref": "8.24", "nombre": "Uso de criptografía",
         "justificacion": "Las transacciones de e-commerce y POS deben estar cifradas (TLS, PCI-DSS)."},
        {"dominio": "A.8.16", "ref": "8.16", "nombre": "Monitoreo de actividades",
         "justificacion": "Los sistemas de punto de venta requieren monitoreo contra fraude y manipulación."},
        {"dominio": "A.5.14", "ref": "5.14", "nombre": "Transferencia de información",
         "justificacion": "Los datos de tarjetas de crédito y pedidos deben transferirse de forma segura."},
        {"dominio": "A.8.12", "ref": "8.12", "nombre": "Prevención de fuga de datos",
         "justificacion": "La información de inventario, clientes y precios es activo crítico del negocio."},
    ],
    "gobierno": [
        {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
         "justificacion": "Las entidades gubernamentales manejan información clasificada y datos ciudadanos."},
        {"dominio": "A.5.7", "ref": "5.7", "nombre": "Inteligencia sobre amenazas",
         "justificacion": "Los gobiernos son objetivo de ataques APT; la inteligencia de amenazas es esencial."},
        {"dominio": "A.5.30", "ref": "5.30", "nombre": "Preparación TIC para continuidad del negocio",
         "justificacion": "Los servicios públicos digitales no pueden interrumpirse; se requiere continuidad garantizada."},
        {"dominio": "A.7", "ref": "7.1 – 7.14", "nombre": "Controles físicos",
         "justificacion": "Los centros de datos gubernamentales requieren controles físicos estrictos de acceso."},
        {"dominio": "A.5.34", "ref": "5.34", "nombre": "Privacidad y protección de datos personales",
         "justificacion": "Los gobiernos custodian datos de todos los ciudadanos; el cumplimiento legal es obligatorio."},
    ],
    "manufactura": [
        {"dominio": "A.7", "ref": "7.1 – 7.14", "nombre": "Controles físicos",
         "justificacion": "Las plantas industriales tienen equipos físicos (OT/ICS) que deben protegerse físicamente."},
        {"dominio": "A.8.20", "ref": "8.20", "nombre": "Seguridad en redes",
         "justificacion": "La convergencia IT/OT en manufactura crea vectores de ataque críticos (ransomware industrial)."},
        {"dominio": "A.5.30", "ref": "5.30", "nombre": "Preparación TIC para continuidad del negocio",
         "justificacion": "La interrupción de líneas de producción tiene impacto económico directo; se requiere BCP sólido."},
        {"dominio": "A.8.7", "ref": "8.7", "nombre": "Protección contra malware",
         "justificacion": "Los sistemas SCADA/PLC son vulnerables a malware específico como Stuxnet y similares."},
    ],
}

# Alias y variaciones comunes
_ALIASES: dict[str, str] = {
    "banca": "financiero",
    "banco": "financiero",
    "seguros": "financiero",
    "fintech": "financiero",
    "clinica": "salud",
    "hospital": "salud",
    "farmaceutico": "salud",
    "farmacia": "salud",
    "software": "tecnologia",
    "it": "tecnologia",
    "ti": "tecnologia",
    "sistemas": "tecnologia",
    "universidad": "educacion",
    "colegio": "educacion",
    "escuela": "educacion",
    "retail": "comercio",
    "supermercado": "comercio",
    "ecommerce": "comercio",
    "e-commerce": "comercio",
    "publico": "gobierno",
    "estatal": "gobierno",
    "municipal": "gobierno",
    "industria": "manufactura",
    "industrial": "manufactura",
    "produccion": "manufactura",
}

DEFAULT_RECOMENDACIONES = [
    {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
     "justificacion": "Los controles organizacionales son la base de cualquier SGSI independiente del sector."},
    {"dominio": "A.6", "ref": "6.1 – 6.8", "nombre": "Controles de personas",
     "justificacion": "El factor humano es el vector de ataque más común; la capacitación es esencial."},
    {"dominio": "A.8.24", "ref": "8.24", "nombre": "Uso de criptografía",
     "justificacion": "La protección de datos en tránsito y en reposo es un control fundamental universal."},
]


def get_recomendaciones(actividad_economica: str) -> tuple[list[dict], str]:
    """
    Retorna (lista_recomendaciones, sector_detectado).
    Hace matching parcial (lowercase) contra claves y aliases.
    """
    actividad_lower = actividad_economica.lower()

    # Búsqueda directa
    for key in RECOMENDACIONES:
        if key in actividad_lower:
            return RECOMENDACIONES[key], key

    # Búsqueda por alias
    for alias, sector in _ALIASES.items():
        if alias in actividad_lower:
            return RECOMENDACIONES[sector], sector

    # Fallback: recomendaciones genéricas
    return DEFAULT_RECOMENDACIONES, "general"
