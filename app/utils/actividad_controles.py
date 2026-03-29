"""
Mapeo de actividad económica → dominios ISO/IEC 27001:2022 recomendados.
Catálogo de controles reales del Anexo A para auto-asignación por empresa.
"""

# ── Catálogo completo de controles por dominio ──────────────────────────────
# Cada control tiene: iso_domain, iso_control_ref, name, description
CONTROL_CATALOG: dict[str, list[dict]] = {
    "A.5": [
        {"ref": "5.1",  "name": "Políticas de seguridad de la información",
         "desc": "Se deben definir, aprobar y comunicar políticas de seguridad de la información alineadas con los requisitos del negocio."},
        {"ref": "5.2",  "name": "Roles y responsabilidades de seguridad de la información",
         "desc": "Los roles y responsabilidades de seguridad deben estar definidos y asignados conforme a las políticas establecidas."},
        {"ref": "5.3",  "name": "Segregación de funciones",
         "desc": "Las funciones conflictivas deben estar segregadas para reducir el riesgo de acceso no autorizado o modificación de activos."},
        {"ref": "5.9",  "name": "Inventario de información y otros activos",
         "desc": "Se debe mantener un inventario actualizado de activos de información y otros activos relacionados con la seguridad."},
        {"ref": "5.14", "name": "Transferencia de información",
         "desc": "Se deben establecer reglas, procedimientos y controles para proteger la información durante su transferencia."},
        {"ref": "5.23", "name": "Seguridad de la información para el uso de servicios en la nube",
         "desc": "Los procesos de adquisición, uso, gestión y salida de servicios en la nube deben estar definidos según los requisitos de seguridad."},
        {"ref": "5.30", "name": "Preparación de las TIC para la continuidad del negocio",
         "desc": "La preparación de las TIC debe planificarse, implementarse, mantenerse y probarse para garantizar la disponibilidad de la información."},
        {"ref": "5.34", "name": "Privacidad y protección de datos personales",
         "desc": "Los requisitos de privacidad y protección de datos personales deben identificarse y cumplirse conforme a la legislación vigente."},
        {"ref": "5.7",  "name": "Inteligencia sobre amenazas",
         "desc": "Se debe recopilar y analizar información sobre amenazas relevantes para generar inteligencia de seguridad accionable."},
        {"ref": "5.37", "name": "Procedimientos operativos documentados",
         "desc": "Los procedimientos de operación para las instalaciones de procesamiento de información deben documentarse y estar disponibles."},
    ],
    "A.6": [
        {"ref": "6.1", "name": "Investigación de antecedentes",
         "desc": "Las verificaciones de antecedentes de candidatos a empleo deben realizarse antes de la contratación, conforme a leyes y ética."},
        {"ref": "6.2", "name": "Términos y condiciones del empleo",
         "desc": "Los acuerdos contractuales deben establecer las responsabilidades del empleado y de la organización en materia de seguridad."},
        {"ref": "6.3", "name": "Concienciación, educación y capacitación en seguridad",
         "desc": "El personal debe recibir formación y actualizaciones periódicas sobre políticas y procedimientos de seguridad de la información."},
        {"ref": "6.5", "name": "Responsabilidades tras la finalización o cambio de empleo",
         "desc": "Las responsabilidades y obligaciones de seguridad vigentes tras la terminación o cambio de empleo deben comunicarse y cumplirse."},
        {"ref": "6.8", "name": "Notificación de eventos de seguridad de la información",
         "desc": "El personal debe notificar los eventos de seguridad observados a través de los canales de reporte establecidos."},
    ],
    "A.7": [
        {"ref": "7.1",  "name": "Perímetros de seguridad física",
         "desc": "Se deben definir y usar perímetros de seguridad para proteger las áreas que contienen información y activos de procesamiento."},
        {"ref": "7.2",  "name": "Controles de entrada física",
         "desc": "Las áreas seguras deben estar protegidas con controles de entrada apropiados para garantizar el acceso solo a personal autorizado."},
        {"ref": "7.4",  "name": "Monitoreo de seguridad física",
         "desc": "Las instalaciones deben monitorearse continuamente para detectar y prevenir el acceso físico no autorizado."},
        {"ref": "7.8",  "name": "Ubicación y protección de equipos",
         "desc": "Los equipos deben ubicarse y protegerse para reducir los riesgos de amenazas físicas y ambientales."},
        {"ref": "7.10", "name": "Medios de almacenamiento",
         "desc": "Los medios de almacenamiento deben gestionarse a lo largo de su ciclo de vida: adquisición, uso, transporte y eliminación segura."},
        {"ref": "7.12", "name": "Seguridad del cableado",
         "desc": "Los cables de energía y telecomunicaciones que transportan datos deben protegerse contra intercepciones, interferencias o daños."},
    ],
    "A.8": [
        {"ref": "8.2",  "name": "Derechos de acceso privilegiado",
         "desc": "La asignación y uso de derechos de acceso privilegiado debe restringirse, controlarse y revisarse periódicamente."},
        {"ref": "8.3",  "name": "Restricción de acceso a la información",
         "desc": "El acceso a información y funciones de sistemas de aplicación debe restringirse conforme a la política de control de acceso."},
        {"ref": "8.5",  "name": "Autenticación segura",
         "desc": "Las tecnologías y procedimientos de autenticación segura deben implementarse basándose en restricciones de acceso a la información."},
        {"ref": "8.7",  "name": "Protección contra malware",
         "desc": "La protección contra malware debe implementarse y apoyarse con una concienciación adecuada del usuario."},
        {"ref": "8.8",  "name": "Gestión de vulnerabilidades técnicas",
         "desc": "La información sobre vulnerabilidades técnicas debe obtenerse oportunamente, evaluarse y tomarse las medidas apropiadas."},
        {"ref": "8.11", "name": "Enmascaramiento de datos",
         "desc": "El enmascaramiento de datos debe utilizarse conforme a la política de control de acceso y otros requisitos de negocio."},
        {"ref": "8.12", "name": "Prevención de fuga de datos",
         "desc": "Se deben aplicar medidas de prevención de fuga de datos a sistemas, redes y dispositivos que procesan información sensible."},
        {"ref": "8.16", "name": "Monitoreo de actividades",
         "desc": "Las redes, sistemas y aplicaciones deben monitorearse para detectar comportamientos anómalos y tomar acciones correctivas."},
        {"ref": "8.20", "name": "Seguridad en redes",
         "desc": "Las redes y dispositivos de red deben asegurarse, gestionarse y controlarse para proteger la información en sistemas y aplicaciones."},
        {"ref": "8.24", "name": "Uso de criptografía",
         "desc": "Se deben definir e implementar reglas sobre el uso de criptografía, incluida la gestión de claves criptográficas."},
        {"ref": "8.25", "name": "Ciclo de vida de desarrollo seguro",
         "desc": "Se deben establecer y aplicar reglas para el desarrollo seguro de software y sistemas."},
        {"ref": "8.29", "name": "Pruebas de seguridad en desarrollo y aceptación",
         "desc": "Los procesos de pruebas de seguridad deben definirse e implementarse en el ciclo de vida de desarrollo."},
        {"ref": "8.32", "name": "Gestión de cambios",
         "desc": "Los cambios en las instalaciones de procesamiento de información y sistemas deben estar sujetos a procedimientos de gestión de cambios."},
        {"ref": "8.34", "name": "Protección de los sistemas de información durante las pruebas de auditoría",
         "desc": "Las pruebas de auditoría y otras actividades de aseguramiento deben planificarse y acordarse para minimizar interrupciones."},
    ],
}

# ── Dominios recomendados por sector ────────────────────────────────────────
# Cada sector indica qué refs de control debe incluir (del catálogo CONTROL_CATALOG)
SECTOR_CONTROLES: dict[str, list[tuple[str, list[str]]]] = {
    "financiero": [
        ("A.5", ["5.1", "5.2", "5.3", "5.9", "5.14", "5.30", "5.34", "5.37"]),
        ("A.6", ["6.1", "6.2", "6.3", "6.5", "6.8"]),
        ("A.8", ["8.2", "8.3", "8.5", "8.7", "8.8", "8.16", "8.20", "8.24", "8.32"]),
    ],
    "salud": [
        ("A.5", ["5.1", "5.2", "5.9", "5.34", "5.37"]),
        ("A.6", ["6.1", "6.3", "6.5", "6.8"]),
        ("A.8", ["8.2", "8.3", "8.5", "8.7", "8.11", "8.20", "8.24", "8.32"]),
    ],
    "tecnologia": [
        ("A.5", ["5.1", "5.2", "5.9", "5.23", "5.37"]),
        ("A.6", ["6.3", "6.8"]),
        ("A.8", ["8.2", "8.3", "8.5", "8.7", "8.8", "8.20", "8.24", "8.25", "8.29", "8.32", "8.34"]),
    ],
    "educacion": [
        ("A.5", ["5.1", "5.2", "5.9", "5.34", "5.37"]),
        ("A.6", ["6.3", "6.5", "6.8"]),
        ("A.8", ["8.3", "8.5", "8.7", "8.20", "8.24"]),
    ],
    "comercio": [
        ("A.5", ["5.1", "5.9", "5.14", "5.37"]),
        ("A.6", ["6.3", "6.8"]),
        ("A.8", ["8.5", "8.7", "8.12", "8.16", "8.20", "8.24"]),
    ],
    "gobierno": [
        ("A.5", ["5.1", "5.2", "5.3", "5.7", "5.9", "5.30", "5.34", "5.37"]),
        ("A.6", ["6.1", "6.2", "6.3", "6.5", "6.8"]),
        ("A.7", ["7.1", "7.2", "7.4", "7.8", "7.10", "7.12"]),
        ("A.8", ["8.2", "8.3", "8.5", "8.7", "8.16", "8.20", "8.24", "8.32"]),
    ],
    "manufactura": [
        ("A.5", ["5.1", "5.9", "5.30", "5.37"]),
        ("A.6", ["6.3", "6.8"]),
        ("A.7", ["7.1", "7.2", "7.4", "7.8", "7.12"]),
        ("A.8", ["8.7", "8.8", "8.16", "8.20", "8.24", "8.32"]),
    ],
    "general": [
        ("A.5", ["5.1", "5.2", "5.9", "5.37"]),
        ("A.6", ["6.3", "6.8"]),
        ("A.8", ["8.5", "8.7", "8.20", "8.24"]),
    ],
}

# ── Alias y variaciones comunes ──────────────────────────────────────────────
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

# ── Recomendaciones de dominio (usadas en ImplementacionView) ────────────────
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

DEFAULT_RECOMENDACIONES = [
    {"dominio": "A.5", "ref": "5.1 – 5.37", "nombre": "Controles organizacionales",
     "justificacion": "Los controles organizacionales son la base de cualquier SGSI independiente del sector."},
    {"dominio": "A.6", "ref": "6.1 – 6.8", "nombre": "Controles de personas",
     "justificacion": "El factor humano es el vector de ataque más común; la capacitación es esencial."},
    {"dominio": "A.8.24", "ref": "8.24", "nombre": "Uso de criptografía",
     "justificacion": "La protección de datos en tránsito y en reposo es un control fundamental universal."},
]


def _detect_sector(actividad_economica: str) -> str:
    """Detecta el sector a partir de la actividad económica."""
    actividad_lower = actividad_economica.lower()
    for key in RECOMENDACIONES:
        if key in actividad_lower:
            return key
    for alias, sector in _ALIASES.items():
        if alias in actividad_lower:
            return sector
    return "general"


def get_recomendaciones(actividad_economica: str) -> tuple[list[dict], str]:
    """
    Retorna (lista_recomendaciones, sector_detectado).
    Hace matching parcial (lowercase) contra claves y aliases.
    """
    sector = _detect_sector(actividad_economica)
    return RECOMENDACIONES.get(sector, DEFAULT_RECOMENDACIONES), sector


def get_controls_for_empresa(actividad_economica: str) -> list[dict]:
    """
    Retorna la lista de controles ISO 27001:2022 a asignar a una empresa
    según su actividad económica. Cada control incluye: iso_domain,
    iso_control_ref, name, description.
    """
    sector = _detect_sector(actividad_economica)
    sector_plan = SECTOR_CONTROLES.get(sector, SECTOR_CONTROLES["general"])

    # Construir lookup rápido por dominio+ref
    catalog_lookup: dict[tuple[str, str], dict] = {}
    for domain, controls in CONTROL_CATALOG.items():
        for c in controls:
            catalog_lookup[(domain, c["ref"])] = c

    result = []
    for domain, refs in sector_plan:
        for ref in refs:
            ctrl = catalog_lookup.get((domain, ref))
            if ctrl:
                result.append({
                    "iso_domain": domain,
                    "iso_control_ref": ref,
                    "name": ctrl["name"],
                    "description": ctrl["desc"],
                })
    return result
