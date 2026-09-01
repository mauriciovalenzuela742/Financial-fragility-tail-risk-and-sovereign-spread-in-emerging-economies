# Control de versiones — Tesis JLoss × GaR × EMBI

*Documento maestro. Establecido el 2026-08-03. Sustituye, en materia de vigencia, a
`README_ORGANIZACION.md` (2026-07-25), que quedó desactualizado (declara vigentes
`Boceto_1_v2.tex` y `Regresiones_panel_v2`, ambos ya superados).*

Este archivo es la **única fuente de verdad** sobre qué archivo es vigente por hilo de
investigación. Ante cualquier discrepancia entre este documento y un README de subcarpeta,
manda este documento.

---

## 0. Por qué existe este documento

Se detectaron **cuatro valores distintos del mismo coeficiente θ** (interacción JLoss×GaR)
circulando en el proyecto:

| Valor | Dónde | Base / ventana | N | Estado |
|---|---|---|---|---|
| −0,352 a −0,363 | Abstract de `Boceto_1_actualizado.tex` | `Panel_final.csv`, 2010Q1–2022Q2 | 248 | **Superado** |
| −0,316 | Cuerpo de `Boceto_1_actualizado.tex`, tabla M3 | corrida `Regresiones_panel_v2` | — | **Superado** |
| −0,338 | `1_Codigo/Panel/LEEME_analisis_v3.md` (25-jul) | `Panel_final_all17.csv`, M3 | 253 | **Por confirmar** |
| −0,313 | `1_Codigo/Plan_tablas_riesgo.md` (28-jul) | `Panel_final_all17.csv`, FE país+tiempo | 253 | **Más reciente** |

La causa no fue sólo prosa desincronizada: **el panel se reconstruyó varias veces y las
especificaciones no son las mismas**. Según `Plan_tablas_riesgo.md` (28-jul, el documento más
reciente del proyecto), −0,338 corresponde a la columna **"+SRISK y SRISK×GaR"**, no a M3
pelado, que da −0,313. Esto contradice el etiquetado de `LEEME_analisis_v3.md` (25-jul).

> **PENDIENTE CRÍTICO — no resuelto en este documento.** Debe re-ejecutarse la Sección 14 de
> `EDA_Panel_Final_17.ipynb` y fijarse **un único valor oficial de θ para M3/all17**,
> registrándolo en la sección 5 de este archivo. Hasta entonces, **ningún número nuevo debe
> escribirse en la prosa de la tesis.**

### Test rápido de vigencia de cualquier resultado empírico

**Mire el N, no el nombre del archivo:**

- **N = 253** → base canónica actual `Panel_final_all17.csv` (5 países LatAm, 2007Q4–2022Q2). **Vigente.**
- **N = 374** → base de robustez `Panel_extended_15paises.csv` (11 países). **Vigente (robustez).**
- **N = 248 o N = 293** → builds superados (`Panel_final.csv` y predecesores). **Obsoleto.**

---

## 1. Convención de nombres de versión

### Regla 1 — El número ordena LINAJE DE CONTENIDO, no fecha de archivo

`_v1`, `_v2`, `_v3`… con **N mayor = más reciente**. Pero la versión la define el **linaje del
contenido** (qué base lee, qué metodología usa), no la fecha del archivo en disco. Una
re-corrida de un notebook viejo actualiza su `mtime` sin convertirlo en la versión vigente.

### Regla 2 — La firma de vigencia es (base que lee, ventana, N), no el nombre

Antes de citar un número, verifique en el archivo **qué CSV lee** y **qué N reporta**. El
nombre del archivo es una etiqueta; la base que lee es el hecho.

### Regla 3 — Un `_vN` que miente NO se re-numera: se marca OBSOLETO

**Caso testigo: `EDA_panel_2_v2.ipynb` (25-jul 17:32).** Por nombre parece "v2" y por fecha es
posterior a `EDA_Panel_Final_17.ipynb` (25-jul 22:35). Verificado: su cabecera es idéntica a
`EDA_panel_2.ipynb` (26-jun), hace `pd.read_csv('Panel_final.csv')`, cubre 5 países
2010Q1–2022Q2 y **no tiene celda de configuración `INFILE`/`OUTDIR`** — la marca distintiva
del linaje v3. Además, `LEEME_analisis_v3.md` enumera exactamente cuatro archivos v3 y éste
**no** está entre ellos.

**Conclusión: su "_v2" significa "segunda corrida del notebook viejo", no "generación 2 de la
cadena canónica". Es una rama muerta con fecha reciente.** No se renumera ni se renombra: se
declara obsoleto aquí y en el LEEME de la carpeta.

### Regla 4 — Renombrado físico sólo en `4_Redaccion/`

- **`4_Redaccion/` (prosa): SÍ se renombra y se archiva.** Riesgo bajo, verificado (no hay
  `\input`/`\include` cruzados entre los Bocetos; su único path relativo, `\graphicspath`,
  ya estaba roto antes de tocar nada).
- **`1_Codigo/` (scripts, notebooks, CSVs): NUNCA se renombra.** Ver sección 2.

### Regla 5 — Todo número en la prosa cita su fuente

Al escribir un coeficiente en la tesis, debe poder responderse: **archivo fuente + spec + N**.
Si no se puede, el número no entra.

### Formato

- Prosa: `<pieza>_v<N>.<ext>` — el N más alto es el vigente.
- Superados: se mueven a `4_Redaccion/archive/` **conservando su nombre**, con prefijo de
  fecha de su última modificación: `2026-06-26_Boceto_1.tex`.
- Código: no se renombra. La cadena vigente se declara en el `LEEME_*.md` de cada carpeta.

---

## 2. Política de renombrado en `1_Codigo/` — NO TOCAR

**Decisión: no se renombra ningún archivo de `1_Codigo/`.** Justificación concreta:

- `EDA_Panel_Final_17.ipynb` fija `INFILE = 'Panel_final_all17.csv'` en su celda de config;
  `EDA_Panel_Extended_11.ipynb` fija `INFILE = 'Panel_extended_15paises.csv'`.
- Los cuatro `.Rmd` leen nombres de CSV literales y requieren working directory en `Panel/`.
- `causal_core.py` y `sign_core.py` se importan por nombre desde sus notebooks.
- `comparar_gar_publicas.py` lee la subcarpeta `./Panel` por ruta relativa.
- `working_paper.tex` referencia 4 PNG por nombre en su propia carpeta.

El modo de falla grave no es el `FileNotFoundError` — ése se ve. Es que **un notebook siga
corriendo contra el CSV equivocado y emita números plausibles pero falsos**: precisamente el
mecanismo que originó el conflicto de θ. La cadena canónica se declara en documentación.

---

## 3. Cadena canónica por hilo de investigación

Rutas relativas desde `Jloss/`.

### 3.1 Paper teórico / Organización Industrial

| Campo | Contenido |
|---|---|
| **Vigente** | `working_paper.tex` (+ `.pdf`) |
| **Ruta** | `4_Redaccion/modelo OI/working_paper.tex` |
| **Por qué** | 2026-07-27 00:24. Documento de cierre del modelo Cournot; consolida las fases II–VI en un paper autocontenido de 10 pp. Referencia 4 figuras por nombre en su misma carpeta (`fase3_calibracion.png`, `fase4_embi.png`, `fase5_montecarlo.png`, `fase6_robustez.png`) → **la carpeta se mueve como unidad o no se mueve**. |
| **Predecesores** | `Plan_Arista_OI_Competencia_Fragilidad.md`, `Fase_II`…`Fase_VI` (22-jul): **no son obsoletos**, son la bitácora de desarrollo y la memoria del razonamiento. Se conservan in situ. `1_Codigo/v0/simulation_outputs/simulacion_modelo_oi.ipynb` (dic-2025): precursor conceptual, legado. |
| **Acción** | **No tocar.** |

### 3.2 Apéndice matemático del modelo OI

| Campo | Contenido |
|---|---|
| **Vigente** | `apendice_matematico.tex` (+ `.pdf`) |
| **Ruta** | `4_Redaccion/modelo OI/apendice_matematico.tex` |
| **Por qué** | 2026-07-26 22:39. Es `\documentclass{article}` independiente, **sin `\input` hacia/desde `working_paper.tex`**: los dos compilan por separado. |
| **Predecesores** | Ninguno. |
| **Acción** | **No tocar.** Al migrar a la plantilla U. de Chile se convierte en Anexo. |

### 3.3 Paper empírico (texto de la tesis)

| Campo | Contenido |
|---|---|
| **Vigente** | `paper2_empirico.tex`, capítulo 2 de la tesis ensamblada |
| **Ruta** | `4_Redaccion/tesis/paper2_empirico.tex` (`\input` por `4_Redaccion/tesis/main.tex`) |
| **Por qué** | Fase 4 (reescritura: dos bases, no tres; números reconciliados; sección de identificación causal) + Fase 5–6 (despiece de la tesis en capítulos con plantilla `umemoria`, `main.tex` compila a 62 páginas). Sucesor directo de `Boceto_1_actualizado.tex`: mismo contenido y números, reformateado de artículo `elsarticle` a `\chapter` de tesis. |
| **Citado** | Corregido a natbib real (`\citep`/`\citet` + `\begin{thebibliography}`), igual que `paper1_oi.tex`; antes usaba citas de texto plano "(Autor, Año)" con una lista `itemize` manual, sin verificación de LaTeX. |
| **Predecesor congelado** | `Boceto_1_actualizado.tex` (`4_Redaccion/`) — ya no se edita; superado por `paper2_empirico.tex`. Sus predecesores (`Boceto_1_v2.tex`, `Boceto 1.tex`, etc.) permanecen en `archive/`. |
| **Acción** | Editar solo `4_Redaccion/tesis/paper2_empirico.tex`. No tocar `Boceto_1_actualizado.tex`. |

### 3.4 Tesis ensamblada (plantilla oficial + capítulos)

| Campo | Contenido |
|---|---|
| **Vigente** | `4_Redaccion/tesis/` completa: `main.tex` + `umemoria.cls` + `introduccion_general.tex` + `paper2_empirico.tex` + `paper1_oi.tex` + `discusion_general.tex` + `anexoA_matematico.tex` |
| **Ruta** | `4_Redaccion/tesis/` |
| **Por qué** | Fase 5–6: ensamblaje de los dos papers como capítulos + introducción/discusión general + anexo matemático sobre la plantilla oficial U. de Chile v1.6. Compila limpio (`main.pdf`, 62 páginas). Sustituye al esqueleto vacío de `4_Redaccion/plantilla/`. |
| **Predecesor obsoleto** | `4_Redaccion/plantilla/` — esqueleto genérico de ejemplo (aún sobre un tema no relacionado a esta tesis), nunca se llenó; `4_Redaccion/tesis/` es la copia real con los capítulos ya escritos. **No confundir ambas carpetas.** |
| **Sincronía con los standalone de `modelo OI/`** | `paper1_oi.tex` y `anexoA_matematico.tex` son adaptaciones (formato de capítulo, referencias cruzadas entre capítulos) del contenido de `4_Redaccion/modelo OI/working_paper.tex` y `apendice_matematico.tex`. Cuando se corrija el contenido teórico en esos archivos standalone, debe reaplicarse la misma corrección aquí — no son copias independientes que puedan divergir en el fondo, solo en el formato. |
| **Acción** | Editar dentro de `4_Redaccion/tesis/`. No archivar `4_Redaccion/plantilla/` sin confirmación explícita (puede servir de referencia de la clase `umemoria` original). |

### 3.5 Construcción del panel base

| Campo | Contenido |
|---|---|
| **Vigente (base principal)** | `rebuild_panel_all17.py` → `Panel_final_all17.csv` |
| **Ruta** | `1_Codigo/Panel/` |
| **Por qué** | 25-jul 02:12. Base declarada principal por `LEEME_analisis_v3.md` y por `Plan_tablas_riesgo.md`: 5 países LatAm con EMBI, GaR entrenado con 17 economías, 2007Q4–2022Q2, con controles domésticos. **N = 253.** |
| **Vigente (robustez)** | `Panel_extended_15paises.csv` (25-jul 15:37) — 11 países con EMBI, sin controles domésticos, usa `VIX_cboe`. **N = 374.** |
| **Insumo GaR** | `gar_panel_all17.csv` (24-jul 19:27) — momentos completos del GaR. |
| **Cadena histórica** | `consolidate_panel.py` (16-jul), `consolidate_panel_v2.py` (16-jul), `build_panel_v2.py` (17-jul), `add_paper_controls.py`, `fetch_global_controls.py`, `rebuild_profit_margin.py`, `patch_chile_debt.py` (17-jul). Superados por `rebuild_panel_all17.py`, pero **son la única receta de varios controles**. No re-ejecutar sin revisar. |
| **Intermedios legado** | `Panel_final.csv`, `Panel_final_prebackup.csv`, `Panel_final_prebackup_all17.csv`, `Panel_partial_EMBI_GaR.csv`, `gar_panel_all15.csv`, `gar_panel_latam.csv`, `controls_panel.csv`, `profit_margin_1999_2011.csv`, `global_controls_quarterly.csv`. Los notebooks del linaje viejo los leen. **Ya fueron restaurados una vez tras borrarlos por error (ver `README_ORGANIZACION.md`, sección CORRECCIÓN). No volver a borrarlos.** |
| **Acción** | **Documentar in situ. No renombrar, no borrar.** |

### 3.6 EDA del panel

| Campo | Contenido |
|---|---|
| **Vigente** | `EDA_Panel_Final_17.ipynb` (principal) y `EDA_Panel_Extended_11.ipynb` (robustez) |
| **Ruta** | `1_Codigo/Panel/` |
| **Por qué** | 25-jul 22:35. Únicos con **celda de configuración `INFILE`/`OUTDIR_NAME`** y autodetección de columnas — la marca del linaje v3, "una base por archivo". Declarados vigentes por `LEEME_analisis_v3.md`. Generan `eda_output_final17/` y `eda_output_ext11/`. Incluyen las Secciones 13 (forma de la distribución del GaR) y 14 (figuras de resultados). |
| **Obsoletos** | `EDA_panel.ipynb` (26-jun 16:18), `EDA_panel_2.ipynb` (26-jun 12:46), **`EDA_panel_2_v2.ipynb` (25-jul 17:32 — rama muerta con fecha reciente, ver Regla 3)**, y la carpeta `eda_output/` (26-jun). |
| **Acción** | **Documentar in situ como obsoletos. No renombrar, no borrar** (los tres leen `Panel_final.csv`, que sigue en disco). |

### 3.7 Regresiones / estimación del mecanismo JLoss×GaR (M1–M5)

| Campo | Contenido |
|---|---|
| **Vigente — reproducible sin R** | **Sección 14 de `EDA_Panel_Final_17.ipynb`** |
| **Ruta** | `1_Codigo/Panel/EDA_Panel_Final_17.ipynb` |
| **Por qué** | Reajusta M1–M5 con `linearmodels` (FE + errores Driscoll–Kraay) replicando la salida de R. **No hay R instalado en el entorno**, así que ésta es la única cadena re-ejecutable. Es la ruta canónica de cómputo. |
| **Vigente — de registro** | `Regresiones_panel_final_v3.Rmd` → `.html` (25-jul 17:12/17:36); robustez: `Regresiones_panel_extended_v3.Rmd` → `.html` (17:14/17:37) |
| **Por qué** | Corrida v3, una base por archivo. Sólo legibles vía su `.html` ya generado (no se puede re-ejecutar el `.Rmd`, no hay R). |
| **Modelo de referencia** | **M3 (+controles)** en la base principal all17; **M2 (FE país+tiempo)** en la extendida (no tiene controles domésticos). |
| **Obsoletos** | `Regresiones_panel_v2.Rmd` / `.html` / `.tex` (17-jul 18:43–18:45). |
| **ADVERTENCIA** | `fig_cobertura.pdf`, `fig_efecto_marginal.pdf`, `fig_forest_theta.pdf` y `figures/` (17-jul 19:11) **son producto de la corrida v2 obsoleta** y son las que cita `Boceto_1_actualizado.tex`. **Deben regenerarse desde la Sección 14 antes de entrar a la tesis.** |
| **Acción** | **Documentar in situ. No renombrar.** Regenerar figuras en la Fase 2. |

### 3.8 Identificación causal

| Campo | Contenido |
|---|---|
| **Vigente** | `Causalidad_Final_17.ipynb`, `Causalidad_Extended_11.ipynb`, `causal_core.py` |
| **Ruta** | `1_Codigo/Panel/` |
| **Por qué** | 26-jul 14:09–14:12. Wild cluster bootstrap, proyecciones locales, IV shift-share. Sin predecesores. Salidas en `causal_output_final17/` y `causal_output_ext11/`. |
| **Síntesis** | `Interpretacion_causal_y_regulacion.md` (26-jul 14:15) — documento de cierre sobre qué se puede y qué no se puede afirmar causalmente. **Insumo directo de la sección de limitaciones de la tesis.** |
| **Salvedad de datos** | `instituciones.csv` (26-jul 14:03) está marcado como **plantilla/provisional, no oficial**. Todo resultado que dependa de él es preliminar. |
| **Predecesores** | Ninguno. |
| **Acción** | **No tocar.** |

### 3.9 Robustez del signo

| Campo | Contenido |
|---|---|
| **Vigente** | `Robustez_del_signo.ipynb`, `sign_core.py`, `sign_output/`, `Robustez_del_signo_LEEME.md` |
| **Ruta** | `1_Codigo/Panel/` |
| **Por qué** | 26-jul 14:29–14:30. Hilo único, sin predecesores. |
| **Acción** | **No tocar.** |

### 3.10 Puente OI ↔ datos reales (H4a/H4b, concentración GFDD)

| Campo | Contenido |
|---|---|
| **Vigente (estimación)** | `fase5_estimacion_real.py` → `fase5_real_resultados.csv`, `fase5_real_amplificacion.png` |
| **Ruta** | `1_Codigo/Panel/` |
| **Por qué** | 26-jul 15:58–15:59. Testea H4a/H4b con **datos reales**. Es el punto más avanzado de la investigación: cierra el modelo teórico contra evidencia. |
| **Vigente (robustez)** | `fase5_robustez_concentracion.py` → `.csv`, con `concentracion_metrics.csv` (26-jul 17:16–17:17). Cinco proxies: CR3, CR5, compuesto, Lerner, Boone. |
| **Datos reales** | `hhi_gfdd.csv`, `hhi_gfdd_raw.json`, `hhi_nivel.csv`, `hhi_anual.csv` (World Bank GFDD), `panel_real_final17.csv`, `panel_real_ext11.csv` (26-jul 15:52–15:53). |
| **Síntesis** | `OI_datos_CONSOLIDADO.md` (26-jul 17:30) — **documento de cierre integrador**: une el modelo OI con toda la evidencia empírica. Complementado por `OI_GFDD_resultados.md` (17:17). |
| **NO CONFUNDIR** | `4_Redaccion/modelo OI/fase5_estimacion.py` + `panel_template.csv` (27-jul) usan un panel **SIMULADO de juguete**. Pese a su fecha posterior, **no son evidencia empírica**: pertenecen al paper teórico como ilustración Monte Carlo. Caso de manual de la Regla 1 (fecha posterior, linaje distinto). |
| **Acción** | **No tocar.** Distinción simulado/real anotada aquí y en el LEEME de ambas carpetas. |

### 3.11 Motor JLoss (cómputo)

| Campo | Contenido |
|---|---|
| **Vigente** | `jloss_engine.py` (24-jul 15:24) + `JLoss_reconstruction_v8.ipynb` (24-jul 14:58) |
| **Ruta** | `1_Codigo/JLoss_reconstruction/` |
| **Por qué** | El "v8" del nombre coincide con el linaje de contenido (las v1–v5 ya fueron eliminadas en la limpieza del 25-jul). Salidas: `Panel_JLoss_v8.csv`, `JLoss_by_country_v8.png`. |
| **Insumo vigente** | `JLoss-pipeline/extraccion/` — extractores por país. |
| **Legado (conservar)** | `matlab/` (~825 MB, código antiguo re-tocado el 25-jul + `.mat` en su mayoría redundantes/fragmentados), `output_v0/` (may-2025), `Jloss.zip`, `Panel_regresion_v2.csv`. |
| **No versionable** | `JLoss-pipeline/venv/` (~508 MB) — ya excluido en `.gitignore`. |
| **Acción** | **Documentar como legado. NO BORRAR** (ver sección 4). |

### 3.12 Motor GaR / FCI (cómputo)

| Campo | Contenido |
|---|---|
| **Vigente** | `gar_engine.py`, `fci_engine.py`, `phase2_gar_panel.py` (22-jun) |
| **Ruta** | `1_Codigo/GaR/` |
| **Por qué** | Motor Python estable; los READMEs de la carpeta (`GaR_pipeline_README.md`, `FCI_pipeline_README.md`) lo documentan. Antigüedad = estabilidad, no obsolescencia: no ha sido superado por nada. |
| **Insumos por país** | `individuals/` (25-jul, completo), `other_countries/` (28-jul, **incompleto — trabajo en curso**). |
| **Validación interna** | `GaR_test.xlsx` (referencia CEMLA), `Auditoria_JLoss_GaR.xlsx` (9-jul). |
| **Referencia, no vigente para cómputo** | `CGARP v2.1/` — implementación R de referencia CEMLA. Sólo validación cruzada; el cómputo propio es el Python. |
| **Auxiliares** | `fetch_controls.py`, `run_reg_extended.py` (25-jun). |
| **Acción** | **No tocar.** |

### 3.13 Validación externa del GaR vs. series públicas

| Campo | Contenido |
|---|---|
| **Vigente** | `comparar_gar_publicas.py`, `comparacion_gar_publicas.csv`, `fig_gar_vs_publicas_corr.png`, `fig_gar_vs_publicas_overlay.png`, `README_comparacion_GaR.md`, `requirements_comparacion.txt`, `vlab-srisk-all-20260728.csv` |
| **Ruta** | **`1_Codigo/` (raíz)** |
| **Por qué es ésta y no la de `2_Datos/`** | Los scripts `.py` son byte-idénticos, pero la copia de `1_Codigo/` es posterior (README 17:40, salidas 18:44) y su `comparacion_gar_publicas.csv` es **más completo (4.597 B vs 2.303 B)**. La copia de `2_Datos/` (17:06–17:08) es el paquete portátil autocontenido anterior. |
| **Duplicado / predecesor congelado** | `2_Datos/README_comparacion_GaR.md`, `comparar_gar_publicas.py`, `comparacion_gar_publicas.csv`, `requirements.txt`, ambas figuras, `VIX_History.csv`, `gar_panel_all17.csv`, `global_controls_quarterly.csv`, `vlab-srisk-all-20260728.csv` (todos 28-jul 17:06–17:08). |
| **¿Está integrado?** | **Sí, y es el hilo vivo más reciente.** Alimenta `Defensa_GaR_preguntas_respuestas.md` (28-jul 19:55) y la **Tabla 2 (estilo Tabla A.3)** de `Plan_tablas_riesgo.md` (28-jul 20:14). No está huérfano: es posterior a los borradores porque los borradores son los atrasados. |
| **Dónde debe ir en la tesis** | (a) Sección/anexo "Validación externa del GaR", apoyada en `Defensa_GaR_preguntas_respuestas.md`; (b) Tabla A.3 de métricas de comparación, según `Plan_tablas_riesgo.md`. |
| **Acción** | Copia de `1_Codigo/` = canónica. La de `2_Datos/` se declara **congelada (paquete portátil)**; no se borra ni se renombra. |

### 3.14 Guion de defensa — hilo más reciente

| Campo | Contenido |
|---|---|
| **Vigente** | `4_Redaccion/Defensa_preguntas.md` (2026-09-01) — 30 preguntas de la comisión sobre toda la investigación, con guion de respuesta y cifras trazables al pipeline post-revisión de árbitro. Complemento específico de GaR: `1_Codigo/Defensa_GaR_preguntas_respuestas.md` (28-jul). |
| **Ruta** | `4_Redaccion/` y `1_Codigo/` |
| **Por qué** | **Son los dos artefactos de investigación más recientes de todo el repositorio.** `Plan_tablas_riesgo.md` contiene el conjunto de θ más granular y actual (Paneles A–C: supervivencia de θ a métricas de riesgo, especificidad del GaR, horse-race JLoss×GaR vs JLoss×VIX) y es el que reconcilia parcialmente las cifras en conflicto. `Defensa_GaR_preguntas_respuestas.md` documenta la validación del porteo R→Python (corr 0,9995 en FCI México; `max|diff| ≈ 1e-15` en preprocesamiento). |
| **Predecesores** | Ninguno. |
| **Acción** | **No tocar. Tratar como fuente prioritaria de cifras**, por encima de `LEEME_analisis_v3.md`, hasta que se resuelva el pendiente crítico de la sección 0. |
| **Pendientes que declaran** | Correr Paneles A–C en la base extendida; añadir columnas OFR FSI, EM Corporate OAS y US HY (vía `--download`); volcar las tablas a Markdown/CSV. |

### 3.15 Análisis predecesores completos (legado)

| Campo | Contenido |
|---|---|
| **`1_Codigo/Stata_Sov_Risk/`** | Todo con timestamp idéntico (18-jun 00:15) → copiado/restaurado de golpe. Análisis Stata **predecesor no vigente** del análisis actual en Python/R. Contiene `Codigo.do`, `reg_base.do`, `Test_Raiz.do`, `base_jloss.dta`, `Base_regresiones_f.dta`/`f2.dta`. |
| **`1_Codigo/v0/`** | Prototipo original (dic-2025). Incluye `JLoss.ipynb` y `simulation_outputs/simulacion_modelo_oi.ipynb`, precursor conceptual del working paper de OI. |
| **`3_Marco_teorico/`** | 14 PDFs de literatura externa. **Fuera del sistema de versionado**: son referencias fijas. |
| **Acción** | **Documentar como legado. NO BORRAR** (ver sección 4). |

---

## 4. Política para carpetas pesadas no vigentes

**Regla: DOCUMENTAR como legado / no vigente. NUNCA BORRAR sin confirmación explícita.**

| Carpeta | Tamaño | Estado |
|---|---|---|
| `1_Codigo/JLoss_reconstruction/matlab/` | ~825 MB | Legado. `.mat` y `.asv` ya excluidos por `.gitignore`. |
| `1_Codigo/JLoss_reconstruction/JLoss-pipeline/venv/` | ~508 MB | No versionable. Ya excluido por `.gitignore`. Regenerable desde `requirements`. |
| `1_Codigo/Stata_Sov_Risk/` | — | Análisis predecesor completo. |
| `1_Codigo/JLoss_reconstruction/matlab_JLOSS.zip` | ~512 MB | Comprimido redundante con `matlab/` (si aún existe). |

**El borrado de cualquiera de estas carpetas requiere confirmación explícita del usuario
humano (Mauricio). Ningún agente ni proceso automático puede darla en su nombre.** La acción
por defecto es dejarlas en disco y anotarlas como legado en el README correspondiente. Ya hay
precedente en este proyecto: en la limpieza del 25-jul se borraron 7 CSV del Panel por error
y hubo que restaurarlos.

---

## 5. Números oficiales

> **★ DV = EMBI, 13 países (2026-09-02).** La variable dependiente del capítulo empírico es
> el **EMBI Global Diversified (J.P. Morgan)**, como en Chari et al. (2024); el CDS 5A de
> Bloomberg queda como **serie de robustez**. Fuente EMBI: `2_Datos/embi.xlsx`. **Hungría sale
> del panel** por el mismo criterio de bancos mínimos que ya excluía a Bulgaria (2 bancos,
> `below_min_banks` 89/89 trimestres). Panel de estimación: **13 países, N = 721 (M1) / 614
> (M2)**. Pipeline: `bbg/p1..p7`. Fuente de verdad: `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`
> (sección superior "★ DISEÑO VIGENTE").
>
> | Parámetro | Spec | Valor (EMBI, 13 países) |
> |---|---|---|
> | θ (JLoss×GaR) | M2 (+6 controles), N=614 | **−0,16** (DK p=0,26; wild boot p=0,14) — **NO significativo** |
> | θ (JLoss×GaR) | M1 sin controles, N=721 | −0,14 (p=0,57) |
> | β₁ (nivel JLoss), β₂ (nivel GaR) | M2 | +2,8 (t=2,7) / −4,3 (t=−2,3) — **ambos significativos** |
> | θ — EMBI vs CDS, submuestra común (606 obs) | M1 | −0,66 (p=0,046) vs −0,76 (p=0,048) — **la métrica no cambia el resultado** |
> | θ — **núcleo 11 EM de financiamiento externo** | M2, N=479 | **−0,47** (t=−2,29, **p=0,023**; wild boot 0,015) |
> | θ — diferencia grupo Polonia+India | interacción de grupo | +0,36 (p=0,23) — no significativa (solo 2 países) |
> | θ — pre-2020 / término post-2020 | interacción de crisis | −1,0 (p=0,057) / +1,0 (p=0,12) |
> | θ — ventana móvil 2012–2016 | — | −0,65 (t=−2,4, p=0,018) |
> | umbral Hansen (efecto JLoss severo/benigno) | — | +5,9 / +2,0 pb, LR=27,5 |
> | β₄ (JLoss×D×HHI, **H4b**) | 3 proxies HHI | +122 / +152 / ≈0 — **NO IDENTIFICADO** (signo inestable, IC boot cruza cero) |
> | H1 causal | proyecciones locales | +4,6 pb (t=2,9) — respalda H1; IV *shift-share* F≈11, 2ª etapa n.s., Sargan rechaza |
>
> **El θ marginal negativo (−0,35, p=0,056) de la versión con CDS era específico del CDS** —
> no del mecanismo, sino de la composición de la muestra: el CDS de Bloomberg estaba truncado
> para Polonia (14 trim.) y ausente para India. La prosa de la tesis pasa a: canales de nivel
> (H1, H2) sólidos; complementariedad (H3) **condicional** — significativa en el núcleo de EM
> de financiamiento externo, no en el conjunto. Reescritos: los 5 `.tex` + `anexoB_datos.tex`
> + resumen de `main.tex`. Compila limpio (82 pp). Nuevo bloque de heterogeneidad en
> `bbg/p5_robustez_arbitro.py`.
>
> ---
>
> **Reancla en Bloomberg + panel único (2026-08-31, v3) [SUPERADO por lo anterior en la DV].** Toda la investigación empírica se
> reconstruyó sobre datos de Bloomberg (JLoss, CDS soberano 5A, factores globales; GaR mantiene
> sus insumos FCI de estadísticas nacionales) y se reestructuró como **una sola investigación
> sobre un único panel**, sin la partición "núcleo LatAm / panel ampliado". Variable
> dependiente = **CDS 5A de Bloomberg y solo eso** (celda vacía si no hay dato). Controles
> domésticos reconstruidos para todos los países. Corea del Sur y Bulgaria quedan fuera por
> JLoss no válido a nivel país (`1_Codigo/Panel/bbg/DIAGNOSTICO_COREA.md`).
> **Fuente de verdad: `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`.** Pipeline: `bbg/p0..p4`.
> Nuevo `4_Redaccion/tesis/anexoB_datos.tex` = tabla de procedencia de datos.
>
> Muestra de estimación: **838 obs, 14 países** (11 con CDS continuo + Hungría/Polonia 14 trim.
> + Pakistán 1), 2004Q1–2026Q1.
>
> | Parámetro | Spec | Valor Bloomberg (panel único) | (era, v8 regulatorio) |
> |---|---|---|---|
> | θ (JLoss×GaR) | **M2 (+6 controles), N=738** | **−0,354** (DK p=0,056; wild boot p=0,035; cluster país p=0,001) | −0,338 |
> | θ (JLoss×GaR) | M1 sin controles, N=838 | −0,543 (p=0,028) | −0,359 |
> | θ (JLoss×GaR) | pre-2020 | −0,39 (t=−1,02, **n.s.** — promedia post-2012 con 2004–2011 nulo) | — |
> | θ (JLoss×GaR) | ventanas móviles 5 años desde 2012 | −0,2 a −1,2, todas significativas | — |
> | θ (JLoss×GaR) | invariancia de cola (GaR q05 / skew-t / ES) | −0,354 / −0,354 / −0,390 | — |
> | θ (JLoss×GaR) | sin China / sin China+Turquía | −0,17 (n.s.) / −0,07 (n.s.) | — |
> | umbral Hansen (efecto JLoss severo/benigno) | — | +8,1 / +2,3 pb, LR=80 | +2,83 / −1,31 |
> | β₄ (JLoss×D×HHI, **H4b**) | HHI estructural | t agrup. −2,34 pero **IC90 boot (−627,+212) → H4b NO IDENTIFICADO** | +721 (t=2,98) |
> | IV shift-share (nivel de JLoss) | — | β=+32,6 pb, p=0,038; F 1ª etapa ≈ 9,5 | — |
>
> Cambios de fondo en la prosa: (i) la tesis es **una sola investigación / un solo panel**;
> (ii) lo respaldado es el **signo y la forma** de θ, con significancia marginal ($p\approx0{,}05$),
> **regularidad post-GFC** (no artefacto de COVID: negativa y significativa en todas las
> ventanas móviles desde 2012, nula antes) e identificación que **descansa en pocos países**
> (sin China deja de ser significativa); (iii) **H4b no identificado** (IC robusto cruza cero),
> no "rechazada / significativa en dirección contraria". Reescritos: los 5 `.tex` +
> `anexoB_datos.tex`. Nueva batería de árbitro: `bbg/p5_robustez_arbitro.py` →
> `robustez_arbitro_bbg.csv`, `diag_por_pais_bbg.csv`, `fig_ventanas_theta.pdf`. Compila
> limpio (77 pp).
>
> **Revisión de árbitro senior (2026-08-31).** Ver plan e informe en
> `~/.claude/plans/adaptive-discovering-tarjan.md`. Pendiente: bootstrap de regresor generado
> re-estimando GaR; re-corrida del motor JLoss con cotas de pérdida más anchas; serie de
> concentración trimestral; empaquetado de los dos papers para envío a revista hispana.
>
> ---
>
> **Registro histórico (v8, datos regulatorios) — 2026-08-03.** Detalle en
> **`1_Codigo/Panel/NUMEROS_CANONICOS.md`** (marcado SUPERADO).

| Parámetro | Base | Spec | N | Valor oficial | Fecha de corrida | Archivo fuente |
|---|---|---|---|---|---|---|
| θ (JLoss×GaR) | all17 | M3 (+controles) | 253 | **−0,338** (t=−2,22, p=0,028) | 2026-08-03 | Sección 14 (celda M1–M5) de `EDA_Panel_Final_17.ipynb`, re-ejecutada sobre `Panel_final_all17.csv` |
| θ (JLoss×GaR) | extendida | M2 (FE país+tiempo) | 374 | **−0,212** (t=−1,83, p=0,069) | 2026-08-03 | ídem, sobre `Panel_extended_15paises.csv` |
| β₄ (JLoss×D×HHI, H4b) | extendida (11 países) | HHI estructural | — | **+721** (t=2,98, P(β₄>0)=87%) | 2026-08-03 | `fase5_estimacion_real.py`, re-ejecutado |

El valor −0,313 reportado en `1_Codigo/Plan_tablas_riesgo.md` (28-jul) **no pudo verificarse**
de forma independiente porque el script que lo produjo no quedó guardado; se documenta la
discrepancia en detalle en `NUMEROS_CANONICOS.md` §2 en vez de descartarla en silencio.

**Ningún número entra a la prosa de la tesis sin trazarse a `NUMEROS_CANONICOS.md`.**

---

## 6. Acciones ejecutadas (registro)

### En `4_Redaccion/` — renombrado y archivo físicos

- Creada `4_Redaccion/archive/`. Movidos con nombre prefijado por fecha:
  - `Boceto 1.tex` → `archive/2026-06-26_Boceto_1.tex`
  - `Resultados_y_Discusion.md` → `archive/2026-06-26_Resultados_y_Discusion.md`
  - `Avance 1 Tesis Mauricio Valenzuela.pdf` → `archive/2026-06-26_Avance_1_Tesis.pdf`
  - `Boceto_1_v2.tex` → `archive/2026-07-17_Boceto_1_v2.tex`
  - `Boceto_1_v2.pdf` → `archive/2026-07-17_Boceto_1_v2.pdf`
- Permanecen activos en `4_Redaccion/`: `Boceto_1_actualizado.tex` (insumo de reescritura,
  Fase 4), `modelo OI/` (completa, como unidad), `plantilla/`, este documento.
- En `plantilla/`: `umemoria (2).cls` → `umemoria.cls`, `main (2).tex` → `main.tex`.

### En `1_Codigo/` — solo documentación (pendiente, Fase 1.4)

- Actualizar `1_Codigo/Panel/LEEME_analisis_v3.md`: marcar explícitamente
  `EDA_panel_2_v2.ipynb`, `EDA_panel_2.ipynb`, `EDA_panel.ipynb`, `eda_output/` y
  `Regresiones_panel_v2.*` como linaje obsoleto.
- Anotar en `1_Codigo/Panel/` que `fig_*.pdf` y `figures/` son de la corrida v2 y deben
  regenerarse (Fase 2).
- Anotar en `4_Redaccion/modelo OI/` que `fase5_estimacion.py` + `panel_template.csv` son
  simulados, y que la versión real es `1_Codigo/Panel/fase5_estimacion_real.py`.
- Anotar en `2_Datos/README_comparacion_GaR.md` que esa copia está congelada y la canónica
  vive en `1_Codigo/`.

### En la raíz (pendiente)

- Actualizar `README_ORGANIZACION.md`: hoy declara vigentes `Boceto_1_v2.tex` y
  `Regresiones_panel_v2`, ambos superados. Debe reducirse a describir la estructura de
  carpetas y remitir a este documento para toda cuestión de vigencia.

### Correcciones técnicas pendientes

1. Fijar el θ oficial (sección 5) — **bloqueante para escribir la prosa final** (Fase 2).
2. Corregir `\graphicspath` al reescribir el paper empírico (Fase 4).
3. Regenerar las 3 figuras desde la Sección 14 de `EDA_Panel_Final_17.ipynb` (Fase 2).
4. ~~Renombrar la plantilla U. de Chile para que `\documentclass{umemoria}` resuelva~~ — hecho.
