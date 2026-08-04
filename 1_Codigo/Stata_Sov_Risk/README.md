# Stata_Sov_Risk — Análisis predecesor (no vigente)

## ¿Qué es esta carpeta?

Contiene el **análisis Stata anterior y ya superado** del proyecto de tesis sobre fragilidad bancaria, crecimiento bajo riesgo (Growth-at-Risk, GaR) y riesgo soberano (EMBI). Es un **artefacto de legado histórico**, conservado por referencia y trazabilidad.

**Estado: No vigente.** El análisis actualmente vigente se ejecuta en:
- **Python** (motor JLoss/GaR): `1_Codigo/JLoss_reconstruction/` y `1_Codigo/GaR/`
- **R** (regresiones de panel): `1_Codigo/Panel/Regresiones_panel_final_v3.Rmd` y `Regresiones_panel_extended_v3.Rmd`

Todos los archivos en esta carpeta fueron copiados/restaurados de golpe el **2026-06-18** (timestamp exacto: 00:15), indicando que provienen de un proyecto anterior o snapshot archivado, no de desarrollos posteriores del proyecto actual.

---

## Inventario de archivos

### Scripts de Stata (`.do`)

Los siguientes archivos contienen scripts de Stata, pero están **no legibles** (contienen solo bytes nulos, posiblemente por corrupción o restauración incompleta):

- **`Codigo.do`** (1.7 KB)
  - Archivo principal. Función original desconocida por corrupción de contenido.

- **`reg_base.do`** (201 bytes)
  - Script de base pequeño. Función original desconocida.

- **`Test_Raiz.do`** (966 bytes)
  - Posiblemente contiene una prueba de raíz unitaria (test de stationarity), basándose en el nombre. Función original desconocida.

- **`DO/Tablas extra para el paper.do`** (14 KB)
  - Script de generación de tablas complementarias para alguna versión anterior del paper. Archivo más grande del grupo .do. Función original desconocida.

### Bases de datos Stata (`.dta`)

Archivos de datos binarios, ordenados por tamaño:

**En la raíz de la carpeta:**

- **`base_jloss.dta`** (1.1 MB)
  - Base de datos principal de JLoss. Estructura y períodos desconocidos sin poder leer metadatos.

- **`Base_regresiones_f.dta`** (974 KB)
  - Base preparada para regresiones (versión F). Sufijo "f" sugiere iteración o variant final.

- **`Base_regresiones_f2.dta`** (974 KB)
  - Variante o iteración 2 de la base de regresiones (versión f2).

- **`country_id.dta`** (11 KB)
  - Tabla de referencia de códigos/IDs de países. Base muy pequeña, probablemente diccionario o lookup table.

**Subcarpeta `DTA/`:**

- **`regressdbnoiseykyieldcorreccionf.dta`** (565 KB)
  - Base específica para regresiones de riesgo soberano. El nombre sugiere: "regress_db" (base de regresión), "noisy" (con ruido), "yield" (rendimiento de bonos), "correccion" (ajuste/corrección), "f" (versión final). Usada posiblemente para análisis de spread soberano.

---

## Nota de vigencia

**Esta carpeta NO es fuente de números para la tesis final.** Véase la sección 3.15 del documento maestro `4_Redaccion/CONTROL_DE_VERSIONES.md`:

> "Análisis Stata predecesor no vigente del análisis actual en Python/R."

Los coeficientes, pruebas estadísticas, o tablas que puedan haber sido generadas por estos scripts no deben citarse en la redacción. El análisis actual, vigente y citado en la tesis, se realiza mediante:

1. **`1_Codigo/Panel/EDA_Panel_Final_17.ipynb`** (Sección 14: regresiones M1–M5 con `linearmodels`).
2. **`1_Codigo/Panel/Regresiones_panel_final_v3.Rmd`** (reporte de referencia, base principal, N=253).
3. **`1_Codigo/Panel/Regresiones_panel_extended_v3.Rmd`** (robustez, N=374).

---

## Política de conservación

Por decisión de control de versiones registrada en `4_Redaccion/CONTROL_DE_VERSIONES.md` (sección 4):

- **Se conserva** como legado e histórico.
- **No se borra** sin confirmación explícita del usuario.
- **No se modifica** ni se renombra.

El precedente documentado es la restauración de archivos Panel CSV borrados por error en julio 2026.

---

## Referencias

- **Documento maestro de vigencia**: `4_Redaccion/CONTROL_DE_VERSIONES.md`
- **Análisis Python vigente**: `1_Codigo/JLoss_reconstruction/`, `1_Codigo/GaR/`
- **Análisis R vigente**: `1_Codigo/Panel/Regresiones_panel_final_v3.Rmd`, `Regresiones_panel_extended_v3.Rmd`
