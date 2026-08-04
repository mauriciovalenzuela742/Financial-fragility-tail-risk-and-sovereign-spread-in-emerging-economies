# Análisis v3 — una base por archivo, sin intervenciones intermedias

Cuatro archivos nuevos, cada uno lee **una sola** base. Correr desde esta carpeta (`Panel/`).

## Base principal — all17 (5 países LatAm con EMBI, GaR entrenado con 17 economías)

| Archivo | Herramienta | Lee | Genera |
|---|---|---|---|
| `EDA_Panel_Final_17.ipynb` | Python / VSCode (*Run All*) | `Panel_final_all17.csv` | `eda_output_final17/` (7 tablas + 10 figuras) |
| `Regresiones_panel_final_v3.Rmd` | R / RStudio (*Knit*) | `Panel_final_all17.csv` | HTML con tablas y figuras |

## Robustez — extendida (11 países con EMBI, sin controles domésticos)

| Archivo | Herramienta | Lee | Genera |
|---|---|---|---|
| `EDA_Panel_Extended_11.ipynb` | Python / VSCode | `Panel_extended_15paises.csv` | `eda_output_ext11/` |
| `Regresiones_panel_extended_v3.Rmd` | R / RStudio | `Panel_extended_15paises.csv` | HTML |

## Cómo correr

**Python (EDA):** abrir el `.ipynb` en VSCode y *Run All*.
Requiere: `pip install pandas numpy matplotlib seaborn scipy statsmodels linearmodels`.
Ya vienen ejecutados una vez (las carpetas `eda_output_*` existen); se regeneran al correr.

### Secciones 13 y 14 (las más importantes) — añadidas

Ambos EDA ahora incluyen, además del exploratorio (1–12):

- **Sección 13 — forma de la distribución del GaR.** Lee `gar_panel_all17.csv` (momentos
  completos) filtrado a los países de la base: volatilidad del GaR, anchura de colas 5–95%
  y ES, y la densidad condicional **skew-t** en un trimestre benigno vs. de estrés. En la
  base final all17 el GaR coincide exacto con el panel; en la extendida los momentos vienen
  de la corrida de 17 economías (nota incluida en el notebook).
- **Sección 14 — figuras de resultados basadas en las regresiones.** Reajusta los modelos
  con `linearmodels` (FE + SE **Driscoll–Kraay**), reproduciendo tu salida de R: efecto
  marginal, superficie de complementariedad, binscatter por régimen, *forest* de θ, umbral
  de Hansen, series por país, contabilidad del spread (COVID), contrafactual sin doom-loop
  y *leave-one-country-out*. El modelo de referencia es **M3 (+controles)** en la base final
  y **M2 (FE país+tiempo)** en la extendida (no tiene controles domésticos).
  θ reproducido: **−0.338** (final all17, M3) y **−0.212** (extendida, M2).

**R (regresiones):** abrir el `.Rmd` en RStudio, fijar el working directory a esta carpeta
(`Session → Set Working Directory → To Source File Location`) y *Knit*.
Requiere: `install.packages(c("plm","lmtest","sandwich","modelsummary","ggplot2","dplyr","tidyr","car","kableExtra"))`.

## Diferencias clave respecto a la versión anterior (v2)

- v2 cargaba y comparaba **tres bases** en un mismo documento (corta/larga/extendida) con
  parámetros intermedios hardcodeados. **v3 analiza cada base por separado**, sin ese cruce.
- Las grillas de gráficos por país se **generalizaron** (5 u 11 países automáticamente).
- El EDA **auto-detecta** las columnas presentes (controles domésticos, VIX vs VIX_cboe),
  por eso el mismo código sirve para las dos bases.
- Export LaTeX sin depender de `jinja2` (portable en cualquier versión de pandas).

## Especificaciones replicadas en los `.Rmd`

Núcleo M1–M5 (FE país+tiempo, +controles, log, +VIX), efecto marginal de JLoss según GaR,
diagnósticos (Pesaran CD, Wooldridge, Hausman), VIF, variantes de error estándar
(Driscoll-Kraay / cluster país / cluster tiempo / Arellano), sin-COVID, dinámico (EMBI
rezagado), interacción con ES, batería agrupado→FE, índices agregados (X_dom, X_global) y
síntesis (triangulación de θ). El extendido omite los controles domésticos (no existen en
esa base) y usa VIX_cboe.
