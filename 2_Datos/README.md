# 2_Datos — Datos sueltos del proyecto GaR y spread soberano

## Propósito

Carpeta de datos compartidos para el análisis de fragilidad bancaria, Growth-at-Risk (GaR) y spread soberano. Contiene series públicas de control global, panel oficial de GaR para 17 economías, índices de estrés sistémico (EMBI, SRISK), y un paquete portátil autocontenido del ejercicio de validación externa del GaR.

## Inventario de archivos

### Datos de control global y riesgo
- **VIX_History.csv** (430 KB) — Volatilidad implícita del S&P 500, histórico diario desde 1990. Métrica global de apetito por riesgo.
- **global_controls_quarterly.csv** (8.5 KB) — Tipos de interés de EE.UU. a 10 años, spreads HY corporativo, spreads on-off-run, datos trimestrales 2003-2026.
- **EMBI_real_8countries_2006_2014.csv** (7.8 KB) — Índice EMBI (riesgo soberano, puntos base) para 8 países emergentes, 2006-2014 anual.
- **embi.xlsx** (527 KB) — EMBI en formato Excel, probable histórico ampliado.

### GaR (Growth-at-Risk) — Panel oficial
- **gar_panel_all17.csv** (468 KB) — Panel oficial de GaR: 17 economías (Brasil, México, Chile, Colombia, Perú, Turquía, Polonia, Indonesia, Malasia, Pakistán, Filipinas, Rusia, India, China, Sudáfrica, Corea del Sur, Hungría), trimestral desde 2003Q1. Contiene percentil 5% del crecimiento y estadísticos de la distribución condicional (media, desviación, sesgo, curtosis, ajuste Student-t).
- **growth-at-risk-with-a-pr.xls** (14.4 KB) — Archivo de referencia de GaR en Excel, probable metodología o muestra vintage.

### Validación externa del GaR — Copia congelada portátil
Nota importante: **Esta carpeta contiene una COPIA CONGELADA (anterior, autocontenida) del ejercicio de validación del GaR vs. métricas públicas. La versión canónica y vigente de este análisis reside en `1_Codigo/` (directorio raíz del proyecto, archivos con el mismo nombre).** Esta copia se conserva como paquete portátil independiente, pero NO es la fuente de números.

- **comparar_gar_publicas.py** (16.6 KB) — Script Python que correlaciona el GaR con métricas públicas de predicción de riesgo (VIX, spreads corporativos HY, SRISK de V-Lab, OFR FSI, FRED EM OAS) en nivel y en variación, por país y pooled. Detecta automáticamente formatos de V-Lab (global o por país).
- **README_comparacion_GaR.md** (3.0 KB) — Documentación del ejercicio: qué se compara, cómo correr, interpretación de resultados.
- **requirements.txt** (0.02 KB) — Dependencias Python: pandas, numpy, matplotlib.
- **comparacion_gar_publicas.csv** (2.3 KB) — Resultados: correlaciones de nivel y cambio, flag de signo, por país y agregado pooled.
- **vlab-srisk-all-20260728.csv** (6.4 KB) — SRISK mundial (capital shortfall sistémico) de NYU Stern V-Lab, mensual 2000-2026, fuente de datos para la validación.
- **fig_gar_vs_publicas_overlay.png** (295 KB) — Gráfico: GaR vs métrica mejor cubierta (estandarizadas) por país, se observa el co-movimiento inverso esperado.
- **fig_gar_vs_publicas_corr.png** (68 KB) — Gráfico: correlación de nivel del GaR con cada métrica pública, por país.

## Nota sobre vigencia

La fuente de verdad única sobre el estado vigente del proyecto (qué versiones de datos son canónicas, qué análisis están activos, qué se ha descartado) es el archivo de control de versiones en la carpeta de redacción. Consulta:

**`4_Redaccion/CONTROL_DE_VERSIONES.md`**
