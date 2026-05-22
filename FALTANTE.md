# FALTANTE.md — Estado de entregables

> Actualizado: **22 de mayo de 2026** — Rocky para Agustín.

## ✅ Brief completo (recibido del usuario)

| Etapa | Actividad | Fecha | % | Estado |
|-------|-----------|-------|---|--------|
| 1 | AF-1 — Análisis e Ingeniería de Requerimientos | 27 Abr 2026 | 5% | ✅ Entregado |
| 2 | AF-2 — Arquitectura y Diseño | 04 May 2026 | 5% | ✅ Entregado |
| 3 | AF-3 — Codificación e Integración (Rev código + SAST) | 11 May 2026 | 5% | ✅ Entregado |
| 4 | AF-4 — Pruebas y Despliegue (DAST + Config Segura) | 18 May 2026 | 5% | ✅ Entregado |
| 5 | **AS-1 SUMATIVA — Entrega Final** | 25 May 2026 | **20%** | ✅ Documento listo |

## 📦 Entregables generados

```
entregas/
├── etapa-1-requerimientos/etapa-1.pdf            ✅
├── etapa-2-arquitectura/etapa-2.pdf              ✅
├── etapa-3-codificacion/etapa-3.pdf              ✅
├── etapa-4-pruebas-despliegue/etapa-4.pdf        ✅
└── etapa-5-entrega-final/
    ├── etapa-5-entrega-final.pdf                 ✅
    └── soportes-iso-secure.zip                   ✅
```

## 🎯 Pendiente (Agustín)

1. **Sustentación grabada** — video del estudiante explicando el proyecto.
2. **Subir al Aula Virtual** antes de las **23:55 del lunes 25 de mayo 2026**.
3. **URL de despliegue Coolify** se completa cuando el push a `main` dispare el deploy.

## 🔗 URLs

- **Repo:** https://github.com/Agustin1231/iso_secure
- **Branch entrega:** `entrega-final` (mergeada a `main` para deploy automático)
- **Despliegue:** auto vía Coolify al push a `main` (URL se notifica por Telegram)

## 🎬 Guion sugerido para la sustentación (5-10 min)

1. **(1 min) Contexto del problema** — por qué un SGSI ISO 27001 y por qué multi-tenant.
2. **(1 min) Demo del producto** — login, dashboard, control de incidentes, riesgo, capacitaciones.
3. **(2 min) Arquitectura** — capas, stack, decisiones clave (ADR-01..04).
4. **(2 min) Seguridad de origen** — modelo de amenazas STRIDE+PASTA, riesgos P×I.
5. **(2 min) SDLC seguro** — SAST + DAST + hardening + IR.
6. **(1 min) Cierre** — cumplimiento ISO 27001:2022 (≈30 controles del Anexo A) y próximos pasos.
