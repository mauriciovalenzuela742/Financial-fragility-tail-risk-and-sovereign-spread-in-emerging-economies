# Fragilidad Bancaria y Riesgos del Crecimiento a la Baja — repositorio de replicación

Repositorio de replicación del working paper *"Fragilidad Bancaria y Riesgos del Crecimiento a la
Baja: Cómo la Interacción entre JLoss y GaR Determina el Spread Soberano en Economías en Desarrollo"*.
Todo el aparato empírico es reproducible de principio a fin.

## Estructura

```
paper/
  paper.tex            # fuente LaTeX del artículo (estándar JFE)
  refs.bib             # bibliografía
  paper.pdf            # PDF compilado
jloss/
  JLoss_reconstruction_v8.ipynb   # motor JLoss (Merton + factor único + punto de silla EL+UL)
data/
  Panel_JLoss_v8.csv              # panel JLoss reconstruido (459 obs, 18 países)
  JLoss_by_country_v8.png         # serie por país
extractors/
  jloss_common.py      # esquema común, fetch de market cap, reporte de cobertura, parser numérico
  jloss_common.py      # esquema v8, bonos-vs-resto, transform long-format generico, market cap, cobertura
  book_pd.py           # PD contable (z-score) + calibracion a escala de mercado
  # --- 18 extractores por pais (mismo esquema v8, criterio bonos-vs-resto) ---
  extract_chile.py        # CMF Bancos API
  extract_brazil.py       # BCB Olinda IFData (OData)
  extract_colombia.py     # datos.gov.co (Socrata)
  extract_peru.py         # boletines SBS (descarga)
  extract_mexico.py       # CNBV Portafolio (descarga/exportacion)
  extract_turkey.py       # TBB (descarga/consulta)
  extract_southafrica.py  # SARB BA900 (descarga; ruta de vencimiento residual)
  extract_argentina.py    # BCRA datos abiertos (.7z)
  extract_poland.py extract_indonesia.py extract_malaysia.py extract_philippines.py
  extract_pakistan.py extract_bulgaria.py            # Hito 4 (long-format)
  extract_china.py extract_egypt.py extract_russia.py extract_venezuela.py  # Hito 5
docs/
  RUNBOOK.md           # paso a paso para producir los resultados actualizados
  JLoss_update_plan.md # mapa de fuentes públicas por país + diseño de la métrica mejorada
```

## Componentes verificados

- **Motor JLoss** (`jloss/`). Implementa la PD estructural de Merton (calibración KMV en variables
  normalizadas, distancia a default lineal), el modelo de factor único condicional y la aproximación
  de punto de silla de la distribución de pérdidas, con agregación EL+UL. **Validado contra los
  resultados oficiales de referencia a tolerancia < 1e-6** cuando el conjunto de instituciones por
  trimestre coincide (celda de validación incluida).
- **Extractores** (`extractors/`). Producen un esquema común de balance y capitalización de mercado
  por país desde fuentes públicas; la lógica de transformación está cubierta por pruebas unitarias.
  Brasil y Colombia son extracción directa por API; Perú y México requieren un paso de descarga previo.
- **PD contable** (`book_pd.py`). z-score de Roy/Laeven-Levine para instituciones no cotizadas,
  calibrado a la escala de la PD de mercado usando los bancos cotizados como puente, con cota de
  Cantelli de respaldo.

## Reproducción

1. Entorno: `pip install pandas numpy scipy matplotlib seaborn requests openpyxl "xlrd>=2.0.1" yfinance`.
2. Reconstrucción base: ejecutar `jloss/JLoss_reconstruction_v8.ipynb` → `Panel_JLoss_v8.csv`.
3. Actualización con datos públicos: seguir `docs/RUNBOOK.md` (extracción por país → PD de mercado +
   PD contable calibrada → motor JLoss con ρ doble → panel actualizado).
4. Compilar el paper: `cd paper && pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`.

## Decisiones de modelado documentadas

- Punto de default `DP = ST + 0.5·LT`; correspondencia entre cuentas contables del supervisor y los
  conceptos de deuda de corto/largo plazo (pendiente de afinar con criterio de madurez por país).
- Correlación de activos: serie con ρ=0.4 (comparable con la referencia) y serie con ρ estimado.
- PD de no cotizados: contable (z-score) calibrada a escala de mercado; fuente registrada por
  observación (`pd_source`) y sometida a robustez.
