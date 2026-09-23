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
| **Sincronía con el envío standalone** | `4_Redaccion/envios/paper_empirico/main.tex` (y `paper_teorico/main.tex`) reutilizan `paper2_empirico.tex`/`paper1_oi.tex` vía `\input` — el cuerpo nunca diverge. Lo que **sí** puede divergir, porque no se actualiza solo: (a) `\begin{abstract}` y `cover_letter.md`, texto propio; (b) `envios/paper_empirico/figuras/` y `envios/paper_teorico/figuras/`, **copias propias** de los PDF de `bbg/figuras/` / `tesis/imagenes/` — un tercer punto de sincronización manual además de `tesis/imagenes/` (ver §3.5 y la nota de `p4_figuras.py` sobre `_save()`). Cualquier cambio de resultado central o de figura debe replicarse a mano en los tres. **Auditoría 2026-09-19:** las figuras de ambos `envios/` estaban desactualizadas (databan del 2026-09-01, previas a varias re-ejecuciones del pipeline) — recopiadas desde `tesis/imagenes/` y ambos `main.tex` recompilados limpios (`paper_empirico` 49 pp, `paper_teorico` 31 pp); el abstract y `cover_letter.md` de `paper_empirico` seguían vigentes (última sincronía textual 2026-09-18: interacción de crisis Backstop/EMstress y batería C1/C2/C3 como resultado vigente; antes citaban 14 países y el CDS como variable dependiente principal). Este resync de figuras es manual y no quedó automatizado — revisar de nuevo tras la próxima corrida de `p4_figuras.py`/`p5_robustez_arbitro.py` que cambie una figura vigente. |

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

> **Segunda ronda: capítulo único, batería de crisis, doble titulación, figuras nuevas
> (2026-09-23).** Tras ver el PDF de la reescritura del 2026-09-22, el autor pidió una
> segunda ronda de ajustes:
>
> - **Fusión a un solo capítulo continuo.** `introduccion_general.tex`, `paper2_empirico.tex`
>   y `discusion_general.tex` se fusionan en `4_Redaccion/tesis/investigacion.tex`
>   (`\label{chap:investigacion}`), resolviendo la redundancia entre la discusión general y la
>   discusión del capítulo que ya había señalado el árbitro. Los tres archivos originales se
>   archivan en `4_Redaccion/archive/` con prefijo `2026-09-23_` (no se borran). `main.tex`
>   ahora hace un solo `\input{investigacion}` antes del apéndice. Se actualizó
>   `4_Redaccion/envios/paper_empirico/main.tex` (`\input` + su mecanismo `\definelabel`, que
>   además tenía un defecto silencioso arrastrado de la ronda anterior: seguía neutralizando
>   `chap:anexoB`, un label ya renombrado a `chap:anexoA` desde el 2026-09-22 — corregido) y se
>   copiaron las figuras nuevas a `envios/paper_empirico/figuras/`.
> - **Doble titulación y comisión.** `main.tex` ahora declara `\memoria{Ingeniero Civil
>   Industrial}` junto a `\tesis{Magíster en Economía Aplicada}` (la clase `umemoria.cls` ya
>   soportaba ambas simultáneas, sin hack) y `\comision{Patricio Valenzuela, Alejandro
>   Corvalán}` (con coma — el TODO comentado original usaba `\\`, que `pgffor` no separa como
>   lista; corregido de paso).
> - **Batería de interacción de crisis (24 especificaciones nuevas).** Extiende la
>   especificación de crisis (antes una sola fila fija) a cuatro modelos anidados CM1–CM4 ×
>   tres estructuras de efectos fijos, en dos paneles (vector único; Backstop/EMstress) — script
>   nuevo `1_Codigo/Panel/bbg/p9b_bateria_crisis.py` → `bateria_crisis_bbg.csv`, que **verifica
>   su propia replicación** contra `p9_crisis_interaccion.py` al ejecutarse (`SystemExit` si no
>   coincide a 5e-4) y coincidió exacto. Presentada como Tablas 1.6–1.7 con metadata de
>   `PanelOLS Estimation Summary` (entidades, R² *within/overall*, F-statistic en caption) —
>   estilo pedido por el autor, con el acabado tipográfico de la batería principal en vez del
>   *screenshot* de consola del `Informe_Taller_Tesis_I.pdf`. Canonicalizado en
>   `NUMEROS_CANONICOS_BBG.md`, sección "★ Batería de interacción de crisis".
> - **Dos figuras nuevas** en `p4_figuras.py`: `fig_gar_paises()` (evolución de `D=-GaR` por
>   país, mismo patrón que `fig_jloss_paises()`) y `fig_comovimiento()` (co-movimiento agregado
>   del panel: `D=-GaR`, `JLoss` y `EMBI` estandarizados —z-score—, mediana transversal por
>   trimestre), en la línea de las Figuras 2–4 del `Informe_Taller_Tesis_I.pdf` original.
> - **Diagrama conceptual recuperado.** La Figura 1 del informe original (estructura de
>   mercado → conducta bancaria → externalidades → `JLoss` → spread, con retroalimentación) se
>   recreó como diagrama TikZ (`\usepackage{tikz}` reintroducido en `main.tex`, solo para esta
>   figura) en la nueva Sección 1.1.3 ("El mecanismo conceptual"), con encuadre honesto: se
>   presenta como mapa intuitivo que motiva la investigación, no como una predicción derivada
>   de un modelo formal (el capítulo teórico que lo derivaba ya no está en el documento).
> - **Fix de la Figura 1.10 (antes 2.7), el *forest plot* de robustez de θ/β₃.** Caption y
>   prosa reescritos para que sea imposible leer el cruce por cero de los intervalos de
>   confianza como "el signo no es robusto": el punto estimado tiene el signo predicho en
>   **24 de 25 filas (96%)**; la única excepción (M3, FE país + factores globales) tiene un
>   coeficiente de apenas +0,01, estadísticamente indistinguible de cero, no una reversión de
>   signo — diagnóstico verificado directamente sobre `tabla_theta_bbg.csv`/`robustez_bbg.csv`.
> - Verificado: `latexmk -pdf main.tex` compila limpio, **67 páginas** (antes 67 — el volumen
>   de contenido nuevo compensa la fusión de portadas/preámbulos redundantes de los tres
>   capítulos separados); `envios/paper_empirico/main.tex` compila limpio, 60 páginas.
>
> ---
>
> **Reescritura estructural: se saca la arista teórica del documento ensamblado (2026-09-22).**
> Por decisión del autor, la tesis queda **solo con la arista empírica**. Cambios:
>
> - **`paper1_oi.tex` y `anexoA_matematico.tex` (Cap. 3 "Organización industrial bancaria" y
>   Anexo A matemático), y la carpeta `4_Redaccion/modelo OI/`: se CONSERVAN íntegros en
>   disco** (no se editan, no se borran) — quedan como **legado/pausado**, fuera del
>   ensamblado. Se sacan únicamente del `\input` de `main.tex` (antes: introducción →
>   paper2\_empirico → paper1\_oi → discusión → anexoA\_matematico → anexoB\_datos; ahora:
>   introducción → paper2\_empirico → discusión → anexoB\_datos). Si en el futuro se retoma la
>   arista teórica, basta reinsertar esos dos `\input` y los `\newtheorem`/`\restateprop` del
>   preámbulo (removidos de `main.tex` porque solo esos dos archivos los usaban — verificado
>   por grep sobre los cuatro archivos que sí siguen en el `\input`).
> - **Título** de `main.tex`: pierde "y Organización Industrial Bancaria". Nuevo: *"Fragilidad
>   Bancaria Sistémica y Riesgo de Cola del Crecimiento: Determinantes del Spread Soberano en
>   Economías Emergentes"*, convergiendo con el título ya aprobado por el comité en
>   `Informe_Taller_Tesis_I.pdf` ("Fragilidad financiera, riesgo de cola y spread soberano en
>   economías emergentes"), manteniendo "bancaria sistémica" por precisión.
> - **`\guia{Juan Francisco Martínez Sepúlveda}` y `\coguia{Ronald Fischer}`** completados
>   (antes comentados con TODO "no se puede inventar" — ya confirmados por el usuario).
> - **`H4a/H4b`** (amplificación de la complementariedad por concentración bancaria, HHI; los
>   tres proxies no identificados — `NUMEROS_CANONICOS_BBG.md` §6/"H4a y H4b") **se reintegran
>   a `paper2_empirico.tex`**, pero solo en una nueva subsección dentro de "Agenda futura"
>   (§7.4), motivada desde la literatura de competencia-fragilidad bancaria
>   (Martínez-Miera & Repullo 2010; Boyd & De Nicolò 2005 — cita nueva, agregada a la
>   bibliografía del capítulo) y sin mencionar el modelo de Cournot ni "el Capítulo 3". Se
>   explicita que es agenda futura, no hallazgo principal.
> - **`paper2_empirico.tex`**: reescritura de prosa (no solo recorte) para dar arco narrativo
>   al capítulo — abre re-anclando en el objetivo general, la hipótesis central y los
>   resultados de la muestra piloto de `Informe_Taller_Tesis_I.pdf` (dic-2025, no citado antes
>   en ningún lado de la tesis), narra la traducción de convención de signo (β₃<0 bajo `GaR`
>   original ⇔ θ=−β₃, es decir β₃>0 bajo `D≡−GaR`), y narra el hallazgo condicional (H3) como
>   una versión más precisa —no una retractación— del hallazgo preliminar del informe. Se
>   eliminan las 8 referencias cruzadas al Capítulo 3 (resumen, introducción ×2, estado del
>   arte ×2, descriptivos, limitaciones, conclusión). Se integra la figura nueva
>   `fig_crisis_regimen.pdf` (generada por `p4_figuras.py`, función `fig_crisis_regimen()`) en
>   `sec:crisis-interaccion`, antes sin figura. Ningún número económico ni tabla existente se
>   modificó.
> - **`main.tex`**: resumen reescrito a una sola arista (párrafo 2 sobre el modelo de Cournot
>   eliminado; párrafo 3 pierde el punto (iv) sobre el microfundamento estructural, aportes
>   renumerados de 5 a 4); preámbulo pierde `tikz`/`tikzlibrary`, `{../modelo OI/}` del
>   `\graphicspath`, y los `\newtheorem`/`\restateprop` exclusivos del Cap. 3/Anexo A.
> - **`introduccion_general.tex`**: reescritura completa. "Dos aristas de una misma
>   investigación" pasa a "El objetivo de esta investigación", anclado explícitamente en
>   `Informe_Taller_Tesis_I.pdf`. El aporte "cuarto, un microfundamento estructural" se
>   elimina; queda en 4 aportes (antes 5).
> - **`discusion_general.tex`**: reescritura completa y considerablemente más corta —la
>   síntesis de "dos aristas" se reemplaza por una síntesis breve que cierra el círculo con el
>   informe de Taller de Tesis I sin repetir en detalle la batería de 24 regresiones (que ya
>   vive en el Cap. 2); implicancias de política pierden la dimensión de organización
>   industrial/Cournot; limitaciones y agenda futura pierden los ítems 100% teóricos (extensión
>   de dos períodos del bloque soberano, microfundamento de ρ(n)) y quedan como síntesis de
>   alto nivel para no duplicar la lista de 8 ítems ya en `paper2_empirico.tex` §7.3.
> - **`anexoB_datos.tex`**: cambio mínimo en el párrafo de apertura (ya no remite al
>   Capítulo~1/`sec:datos_reales`); la sección "Concentración bancaria e instituciones" (HHI,
>   `HHI_q`, rating S&P, WGI) se conserva íntegra porque H4a/H4b sigue vigente, solo reubicado.
> - **Hallazgo colateral, corregido en el mismo commit:** `introduccion_general.tex` y
>   `anexoB_datos.tex` citaban con `\citep`/`\citet`/`\citealp` las claves sin sufijo
>   (`Chari2024`, `ABG2019`, `FarhiTirole2018`, `AcharyaDrechslerSchnabl2014`), que **nunca
>   estuvieron definidas** (no hay `\bibliography` global; cada capítulo trae su propio
>   `thebibliography` con claves sufijadas `...b`) — el PDF las renderizaba como signos de
>   interrogación literales ("?", "??") desde antes de esta sesión. Corregidas a las claves
>   sufijadas (`Chari2024b`, `ABG2019b`, etc., ya definidas en la bibliografía de
>   `paper2_empirico.tex`, capítulo que se `\input`ea antes en el documento). `MMR2010`
>   (sin sufijo) dejó de usarse al eliminar los párrafos sobre el modelo de Cournot.
> - **Compilación**: `latexmk -pdf main.tex` limpia — **0 errores** (`grep -c "^! " main.log`
>   = 0), **0 citas/referencias indefinidas**. Página: **94 → 67** páginas (la reducción es
>   sobre todo la salida del Cap. 3 teórico y el Anexo A matemático, ambos con muchas
>   proposiciones/demostraciones/figuras).
>
> Prosa: los 5 archivos de `4_Redaccion/tesis/` listados arriba. Números citados en las partes
> nuevas: sección H4a/H4b nueva (`NUMEROS_CANONICOS_BBG.md` §6, filas de los tres proxies de
> HHI); hipótesis y resultados de la muestra piloto (`Informe_Taller_Tesis_I.pdf`, páginas
> 2 y 10-12); resto, cifras ya vigentes en el capítulo, sin cambios.
>
> **Adenda — revisión menor del árbitro senior, 8 puntos corregidos (2026-09-22, mismo día).**
> 1. `umemoria.cls` líneas 261-263: bug de plantilla, imprimía "PROFESORA GUÍA" hardcodeado sin
>    importar el nombre del profesor. Corregido a "PROFESOR GUÍA" (cambio directo de string; la
>    clase no tenía mecanismo de género).
> 2. `paper2_empirico.tex`, resumen del capítulo: "un panel quince veces mayor" que la muestra
>    piloto era aritméticamente incorrecto (13/4≈3,25×; 721/234≈3,1×) e inconsistente con "más
>    del triple" diez líneas después. Unificado a "más del triple".
> 3. Robustez "sin deuda/PIB": estaba transcrita como β₃=+0,16 (t=0,96); el valor correcto de
>    `1_Codigo/Panel/bbg/robustez_bbg.csv` (fila `sin deuda/PIB`) es θ=−0,1833 ⇒ β₃=+0,18,
>    t=+0,99. Corregido en la prosa y **canonicalizada por primera vez** en
>    `NUMEROS_CANONICOS_BBG.md` (sección superior vigente, nueva subsección "Otras pruebas de
>    robustez (M2, 13 países, panel EMBI vigente)").
> 4. La cita de detalle de H4a/H4b (IC90 *bootstrap* y P(β₄>0) por proxy) apuntaba a la
>    "Sección 6" del canónico, que es parte **legada** del panel CDS de 14 países (el propio
>    archivo indica no citarla en prosa). Verificado contra `fase5_bbg.csv` directamente
>    (columnas `N,paises`: 721/721/706, 13 países, DV `EMBI_bps` en
>    `p3_causal_fase5.py::load_for_causal`) que ese detalle **sí es vigente** para el panel EMBI
>    actual, no un residuo CDS. Se replicó la tabla completa (con columna `N` añadida) en el
>    bloque vigente "H4a / H4b ... no identificados" de la sección superior, y se actualizó la
>    cita en `paper2_empirico.tex` §7.4 para apuntar ahí en vez de a la Sección 6 legada.
> 5. El t de proyecciones locales (canónico +2,85) aparecía redondeado de forma inconsistente:
>    2,9 en el resumen del capítulo, 2,8 en el cuerpo (§6.8) y en Limitaciones (§7.3, ítem 8).
>    Unificado a 2,9 en las tres apariciones.
> 6. La prueba de Pesaran (CD=−1,07, p=0,28, `diagnosticos_bbg.csv`) no estaba canonicalizada.
>    Agregada como nueva subsección "Diagnósticos del panel (M2, 13 países, panel EMBI
>    vigente)" en `NUMEROS_CANONICOS_BBG.md`, junto a "Coeficientes de control en M2".
> 7. "...como se muestra en la Sección 6..." (referencia a EMBI vs. CDS) era texto plano en vez
>    de `\ref{}`. Se agregó `\label{sec:embi-cds}` a la subsección "El spread: EMBI o CDS, la
>    métrica no cambia el resultado" y se reemplazó por `\ref{sec:embi-cds}`.
> 8. El único apéndice usaba `\label{chap:anexoB}` pero se despliega como "Anexo A" (residuo del
>    Anexo A del capítulo teórico eliminado). Todas las referencias vivían en los 5 archivos de
>    mi scope (`anexoB_datos.tex`, `main.tex`, `introduccion_general.tex`,
>    `paper2_empirico.tex` ×6) — ninguna en `paper1_oi.tex`/`anexoA_matematico.tex` — así que se
>    renombró a `\label{chap:anexoA}` en las 9 ocurrencias.
>
> Recompilado: `latexmk -pdf main.tex` — 0 errores, 0 citas/referencias indefinidas, **67
> páginas** (sin cambio respecto de la versión anterior).

> **C1 — bootstrap de regresor generado: EJECUTADO en NLHPC, resultado final (2026-09-17).**
> Job `13095760` (`gar_boot`), `~/nlhpc_gar_all18/`: **B=500 réplicas, fidelidad completa
> (n_tau=39), 500/500 sin errores, 171,9 min**. Segunda etapa corrida local sobre
> `gar_replicas_nlhpc.csv` (700.000 filas). Resultado: el SE combinado (segunda etapa DK/Wald
> + primera etapa *bootstrap*, en cuadratura) crece apenas 2–15\,% según la fila, y **ningún
> `p`-valor cambia de categoría** — β₃ muestra completa sigue no significativo (p: 0,239→0,248);
> β₃ fuera de crisis sigue en el margen del 5\,% (0,043→0,048); *Backstop* sigue sin rechazar
> cero (0,270→0,284); *EMstress* sigue significativo (0,0002→0,0012). La inferencia
> Driscoll–Kraay/Wald ya reportada en la tesis no subestimaba de forma material la
> incertidumbre de tratar al `GaR` como dato. Detalle completo (tabla, metodología de
> combinación, y el hallazgo de *vintage* de abajo):
> `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`, sección "Bootstrap de regresor generado (C1)".
> Prosa: párrafo "Regresores generados" en `paper2_empirico.tex` §6.8 (nueva
> `\label{sec:ident-causal}`), y §7.4 Agenda futura reescrita (el punto (v) —el propio
> *bootstrap*— pasa de pendiente a hecho; el punto (iii) corregido: Rusia ya tiene `GaR`, solo
> le falta EMBI). Cita nueva: Pagan (1984). Compila limpio (94 pp, 0 refs indefinidas).
>
> **Hallazgo colateral — el `GaR` vigente de `Panel_bloomberg.csv` YA es la versión con Rusia
> (18 países)**, confirmado de forma directa (no solo por la nota de la re-ejecución
> 2026-09-06): `git log` → commit `d4fcdef` (anterior a esta sesión) reconstruyó
> `Panel_bloomberg.csv` con `gar_panel_all18.csv`, y son byte-idénticos donde coinciden. Esto
> explica por qué β₃ (M2, muestra completa) re-ejecutado en vivo da **+0,188** en vez de los
> +0,160 que cita la tabla "★ Resultado central — H3" (todavía sin actualizar, deriva de
> exactamente la magnitud que esa nota anticipaba, |Δ|≈0,03) — y confirma que el trabajo de
> esta sesión sobre interacción de crisis, endogeneidad `Ryr`, C1 y C2 es internamente
> consistente entre sí (todos usan el `GaR` vigente con Rusia vía `gar_panel_all18.csv`), solo
> la tabla superior y la prosa de la tesis siguen ancladas al estado pre-2026-09-06. No cambia
> la decisión de la Parte D de abajo (diferir la propagación completa hasta tener Argentina).
>
> ---
>
> **Parte D — limpieza de consistencia (2026-09-16).** Los cuatro puntos del plan de árbitro:
>
> 1. **Deriva de descriptivos de `JLoss` (sd 4,0 vs 4,6 vs 4,8)** — **ya reconciliada** en una
>    revisión previa a esta sesión: las tres menciones vigentes (`paper2_empirico.tex` §2.4.1
>    y §7.3, `paper1_oi.tex` §5.5) dicen consistentemente **media 4,8 / sd 4,6**, y coincide
>    exacto con `Panel_bloomberg.csv` recalculado en vivo (`JLoss.describe()`: media 4,786,
>    sd 4,592, N=721, 13 países). Sin cambios.
> 2. **Cohorte de β₄ (+122/+152 vs +139/+171)** — reconciliada: +122/+152 era una fila de
>    registro fechada 2026-09-02, **superada** desde entonces por `p3_causal_fase5.py` →
>    `fase5_bbg.csv` (tras excluir Hungría y otras correcciones de *pipeline*); +139/+171/≈0
>    es lo canónico (`NUMEROS_CANONICOS_BBG.md` "H4a/H4b") y lo que cita `paper1_oi.tex` —
>    verificado re-ejecutando el script, reproduce exacto. Anotada la fila vieja como
>    superada; ninguna conclusión cambia bajo ninguna de las dos cohortes.
> 3. **Re-ejecución 2026-09-06 con Rusia (18 países en el pool de GaR)** — decisión
>    reafirmada: **sigue sin propagarse** a la prosa ni al panel de estimación EMBI. El efecto
>    es cuantitativamente inmaterial (|Δθ| ≤ 0,03, ninguna conclusión cambia) y Argentina
>    sigue pendiente de Bloomberg — el plan siempre fue batchear ambas actualizaciones en una
>    sola pasada. Todo el trabajo de esta sesión (crisis, `Ryr`, C1, C2) se construyó también
>    sobre la base **all17** vigente, así que no hay mezcla de *vintages* dentro de la tesis.
>    Detalle: `NUMEROS_CANONICOS_BBG.md`, sección "RE-EJECUCIÓN 2026-09-06".
> 4. **`\graphicspath` y 3 figuras pendientes** — **obsoleto**: esos ítems (§6 de este
>    documento, "Correcciones técnicas pendientes" 1-3) databan de la fase pre-Bloomberg
>    (`EDA_Panel_Final_17.ipynb`, `Boceto_1_actualizado.tex`); el paper empírico fue reescrito
>    muchas veces desde entonces sobre la base Bloomberg y `latexmk -pdf` compila sin ninguna
>    advertencia de figura faltante. Marcados como hechos/superados en §6.
>
> Con esto se cierran los cuatro puntos de la Parte D del plan de árbitro. Compila limpio
> (93 pp, 0 refs indefinidas) — sin cambios de prosa en esta entrada más allá de las
> anotaciones de este documento.
>
> ---
>
> **C3 — posicionamiento vs. Chari et al. (2024) (2026-09-16): verificado, ya estaba afilado;
> se agregó la referencia cruzada al Canal~I.** Punto C3 del plan de árbitro: agudizar en la
> introducción y en "Brecha en la literatura" (§3.6) la distinción cola doméstica endógena del
> crecimiento ≠ ciclo financiero global exógeno. Al revisar `paper2_empirico.tex` se encontró
> que esta distinción **ya estaba articulada con precisión** en tres lugares (Introducción
> §1, Hipótesis §2.4, Brecha en la literatura §3.6) — trabajo de una revisión previa de
> árbitro, no de esta sesión — nombrando explícitamente que Chari et al. (2024) interactúan
> `JLoss` con factores financieros **globales** (VIX, tasa del Tesoro, *spreads* de alto
> rendimiento) mientras este capítulo lo hace con una vulnerabilidad **doméstica y endógena**
> (`GaR`) que la propia fragilidad bancaria contribuye a generar, con la distinción de
> política ya explicitada ("la primera interacción indica cuándo un sistema bancario frágil
> expone al soberano al ciclo financiero global; la segunda, cuándo lo expone a su propio
> ciclo doméstico"). Único cambio hecho: la frase "canal de *credit crunch*" en §3.6 ahora
> referencia explícitamente el **Canal I** del modelo estructural del Capítulo 1
> (`paper1_oi.tex`, nueva etiqueta `\label{sec:canal1}` en la subsección homónima — cambio
> puramente mecánico/aditivo, no avanza contenido de la línea teórica, que sigue pausada),
> cerrando el vínculo teoría↔evidencia que pedía el plan. Compila limpio (93 pp).
>
> ---
>
> **C2 — IV reforzado con commodity ToT shift-share (2026-09-16): intentado, primera etapa
> nula, no cierra la identificación.** Punto C2 del plan de árbitro: reforzar la IV de C2 con
> un instrumento más exógeno que los dos existentes (`OnOffRun`, USD BIS — cuya "participación"
> se estima regresando `JLoss` contra el choque). Nuevo instrumento: choque de términos de
> intercambio por exposición sectorial a *commodities*, con participaciones de exportación
> **pre-muestra** (Banco Mundial WDI, 1998–2003, antes de 2004Q1) ponderando el índice de
> precio mundial de cada categoría (World Bank Pink Sheet) — la "participación" viene de datos
> comerciales externos, exógena por construcción, no de una regresión contra `JLoss`. Nuevos:
> `1_Codigo/Panel/bbg/p7b_iv_commodity_tot.py` (construcción) + `p7c_iv_reforzado.py`
> (estimación) + `causal_core.iv_commodity_tot`/`iv_commodity_tot_plus_existentes`. Resultado:
> primera etapa **prácticamente nula para `JLoss`** (`F≈0,03`) aunque el instrumento sí
> co-mueve con el EMBI directamente (corr. *within* ≈ −0,16) — el ciclo de *commodities* es
> relevante para el riesgo soberano agregado, no para la fragilidad *bancaria* específica.
> Añadido a los 2 instrumentos existentes, el Sargan sobre-identificado sigue rechazando
> (`p=0,0014`, vs. `p=0,0003` con 2). Conclusión (punto (b) del plan): **no forzar** — se
> documenta el intento y se re-etiqueta la IV como evidencia que no cierra la identificación
> bajo ninguno de los tres instrumentos probados; el peso de H1 sigue en OLS+EF y proyecciones
> locales. Detalle: `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` sección "IV reforzado —
> commodity ToT shift-share (C2)". Prosa actualizada en `paper2_empirico.tex` §6.8
> (Identificación causal), §7.3 (Limitaciones, punto octavo) y §7.4 (Agenda futura, punto vi).
> Compila limpio.
>
> ---
>
> **C1 — bootstrap de regresor generado del GaR (2026-09-15): diseñado y validado,
> ejecución movida a NLHPC.** Punto C1 del plan de árbitro: SE de `β₃` que propague el
> error de primera etapa del `GaR` (block bootstrap por país, re-estimando la regresión
> cuantílica de panel en cada réplica — detalle completo en
> `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`, sección "Bootstrap de regresor generado
> (C1)"). Tres intentos de correrlo LOCAL (4 *workers*, 2 *workers*, 1 proceso en serie)
> murieron por falta de memoria del sistema (máquina de 8GB, ~600MB libres de base) — no es
> un defecto del script: la metodología fue validada (ajuste único a fidelidad reducida
> reproduce de cerca los números oficiales) y la lógica de remuestreo fue verificada
> end-to-end con un *dry run* barato. Decisión del usuario: mover la ejecución a NLHPC con
> fidelidad completa. Nuevos: `1_Codigo/GaR/individuals/nlhpc_gar_all18/p10_boot_gar_nlhpc.py`
> + `run_boot_gar_nlhpc.sbatch` (primera etapa, cluster) y
> `1_Codigo/Panel/bbg/p10_boot_gar.py segunda_etapa` (segunda etapa, local, trivial en
> tiempo/memoria). **Pendiente:** el usuario corre el sbatch en NLHPC; al volver el resultado,
> se completa el SE bootstrap y se actualiza esta sección + `paper2_empirico.tex` §6.8/§7.4.
>
> ---
>
> **Interacción de crisis + endogeneidad `Ryr` (2026-09-10/11, indicaciones del coguía) —
> línea teórica PAUSADA, foco 100% en Cap. 2.** Reunión con el profesor coguía: se acuerda no
> avanzar en la teoría y cerrar el paper empírico. Dos indicaciones concretas + pendientes de
> árbitro (bootstrap GaR, IV, Chari) quedan como alcance. Plan:
> `~/.claude/plans/arma-el-dag-de-moonlit-moonbeam.md`.
>
> **(1) Vector de crisis en vez de botar trimestres.** Nueva especificación con toda la
> muestra: `β₃` = complementariedad fuera de crisis, `β₄` = término triple con el vector de
> crisis (GFC 2008Q4–2009Q4 + COVID 2020Q1–2021Q4 + estrés EM 2015Q3–2016Q1). Descompuesta en
> *Backstop* (GFC+COVID, con respaldo oficial masivo) vs *EMstress* (2015–16, sin respaldo):
> **β₃ ≈ +0,81 fuera de crisis (p=0,051); se anula bajo Backstop (β₃+β₄ ≈ 0, Wald p=0,77,
> NO rechaza) y sobrevive bajo EMstress (β₃+β₄ ≈ +1,05, Wald p<0,001)** — test de falsación
> directo del mecanismo (el canal se apaga sólo donde hay respaldo oficial). Corrido y
> verificado idéntico en Python (`p9_crisis_interaccion.py`, `linearmodels`/DK) y R
> (`crisis_interaccion.R`, `plm`+`vcovSCC`+`car::linearHypothesis`), y replicado en
> `EDA_Panel_Final_bbg.ipynb` (§8) y `analisis_bloomberg.Rmd`. Reemplaza al corte por
> submuestra (batería Panel B, "excluir trimestres de crisis") como resultado principal de la
> dimensión temporal; el Panel B queda como robustez secundaria.
>
> **(2) Endogeneidad `Ryr` ↔ EMBI.** El `Ryr` (rendimiento soberano 10Y local) alimenta el FCI
> vía `iRyr = (VRyr+CDIFF)/2`; `CDIFF` es el único término tipo-spread del FCI y se solapa
> conceptualmente con el EMBI (DV). Diagnóstico por etapas (`p9_diag_ryr.py`): la correlación
> con el EMBI se **atenúa de 0,68 (spread crudo) a 0,07 (contribución de CDIFF a iRyr)** por la
> propia transformación (diferenciación + piso móvil + estandarización expansiva). Verificado
> además por **reconstrucción real del GaR sin CDIFF** (`fci_engine.compute_fci(drop_cdiff=True)`,
> `build_fci_no_cdiff.py`, `gar_insample_robustez.py`, `p9_robustez_gar_nocdiff.py`;
> `corr(GaR_sin_CDIFF, GaR_con_CDIFF)=0,985`): **β₃ no se mueve de forma material** (+0,19→+0,23
> muestra completa; +0,84→+0,86 fuera de crisis; cancelación Backstop y supervivencia EMstress
> intactas). El EMBI/CDS nunca entran al FCI ni al GaR. Conclusión: preocupación conceptualmente
> válida, cuantitativamente inmaterial.
>
> Fuente de verdad de ambos resultados: `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`
> (secciones "Interacción de crisis — SIN botar trimestres" y "Endogeneidad `Ryr` ↔ EMBI").
> Prosa: nuevas subsecciones `sec:crisis-interaccion` (§6.6.1) y `sec:ryr-endogeneidad` (§6.4.2)
> en `paper2_empirico.tex`, más actualización del resumen del capítulo, síntesis, limitaciones
> y del resumen de tesis en `main.tex`. Compila limpio (92 pp, 0 refs/citas indefinidas).
> **Pendiente:** C1 (bootstrap de regresor generado re-estimando GaR por réplica), C2 (IV
> reforzado), C3 (afinar posicionamiento vs. Chari et al. 2024), Parte D (limpieza de
> consistencia: deriva de descriptivos, cohorte de β₄, figuras pendientes).
>
> ---
>
> **Revisión de la línea teórica — Cap. 3 (2026-09-09).** Preparación de la reunión con el
> profesor sobre el capítulo teórico. Plan e informe:
> `4_Redaccion/modelo OI/Plan_Revision_Linea_Teorica_2026-09.md`
> (copia de trabajo en `~/.claude/plans/`).
> Sin cambios de números; ediciones de estructura y encuadre en `4_Redaccion/tesis/paper1_oi.tex`:
> (i) box "Convención de signos" ($D\equiv-\GaR$) al inicio del capítulo;
> (ii) nueva figura TikZ `fig:dag` (Fig. 3.3) + subsección "El DAG del mecanismo" (§3.5.4) —
> requiere `\usepackage{tikz}` en `main.tex` y `envios/paper_teorico/main.tex`;
> (iii) Cuadro `tab:estimandos` (Tabla 3.1) "Qué estima cada coeficiente" (§3.5.3);
> (iv) subsección "$n$ como instrumento de política" (§2.6, `sec:npolitica`);
> (v) Observación `rem:decouple` (Obs. 3.3): la derivada cruzada de la Prop. 5 no depende del Canal I;
> (vi) párrafo de MDE en §5.4 — H4b como "predicción registrada del modelo".
> Compila limpio: tesis 89 pp, `paper_teorico` standalone 31 pp.
>
> **Sincronización de los standalone de `modelo OI/` (2026-09-09).** `working_paper.tex` y
> `apendice_matematico.tex` pasados de convención $\GaR$-primitiva a **$D\equiv-\GaR$**
> ($\beta_1,\beta_2^{D},\beta_3,\beta_4>0$): box "Convención de signos", Prop. de la derivada
> cruzada y de la amplificación enunciadas con el `iff` en $D$, `eq:emp` en $D$, captions de
> figuras, validación Monte Carlo ($\beta_3=+0{,}80$, $\beta_4=+3{,}0$), y **§5.4 de
> `working_paper.tex` reescrita a los resultados Bloomberg**: H4a condicional
> ($\hat\theta=-0{,}16$ muestra completa; $\hat\beta_3=+0{,}47$, $p=0{,}023$ en el núcleo de
> 11 EM) y **H4b NO identificado** (ya no reporta "$\hat\beta_4=+721$ confirma"). `apendice_matematico.tex`
> añade la tabla $D/\GaR$ y una nota de numeración (Prop. 1–5 aquí $=$ Prop. 2–6 en la tesis;
> la tesis antepone existencia y unicidad como Prop. 1). Requirió `\usepackage{mdframed}` en
> `working_paper.tex`. Compilan limpio: `working_paper` 15 pp, `apendice_matematico` 7 pp,
> `envios/paper_empirico` 44 pp. **Pendiente:** portar a `working_paper.tex` la figura DAG,
> el cuadro de estimandos y la subsección "$n$ como instrumento de política".
>
> ---
>
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
> | β₄ (JLoss×D×HHI, **H4b**) | 3 proxies HHI | +122 / +152 / ≈0 — **NO IDENTIFICADO** (signo inestable, IC boot cruza cero) — **superado, ver nota** |
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
> **Nota (Parte D, 2026-09-16) — cohorte de β₄ reconciliada.** La fila de β₄ de arriba
> (+122/+152/≈0, fechada 2026-09-02) queda **superada** por `p3_causal_fase5.py` →
> `fase5_bbg.csv`, la corrida vigente desde entonces (tras la exclusión de Hungría y otras
> correcciones del *pipeline*): **β₄ = +139 (estructural, t=+0,39) / +171 (anual, t=+0,81) /
> ≈0 (trimestral, t=−0,54)**, documentado como canónico en la sección "H4a / H4b" de
> `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` y citado en `paper1_oi.tex`. Verificado
> re-ejecutando `p3_causal_fase5.py` el 2026-09-16: reproduce +139/+171 exacto. La conclusión
> cualitativa (H4b no identificado, IC de *bootstrap* cruza cero en los tres proxies) es la
> misma bajo ambas cohortes de números — no cambia ninguna lectura de la tesis.
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

1. ~~Fijar el θ oficial (sección 5) — bloqueante para escribir la prosa final (Fase 2)~~ —
   **hecho** (verificado 2026-09-16, Parte D): la Sección 5 tiene un θ/β₃ oficial trazable
   desde hace varias reescrituras del paper; toda la prosa vigente cita filas de
   `NUMEROS_CANONICOS_BBG.md`.
2. ~~Corregir `\graphicspath` al reescribir el paper empírico (Fase 4)~~ — **hecho**: el
   paper empírico fue reescrito varias veces sobre la base Bloomberg; `latexmk -pdf` compila
   sin ninguna advertencia de figura faltante (verificado 2026-09-16).
3. ~~Regenerar las 3 figuras desde la Sección 14 de `EDA_Panel_Final_17.ipynb` (Fase 2)~~ —
   **superado**: ese notebook (base `all17`, CDS) fue reemplazado por
   `1_Codigo/Panel/bbg/EDA_Panel_Final_bbg.ipynb` (base Bloomberg, EMBI), cuya Sección 14 (y
   la nueva Sección 8, interacción de crisis) generan todas las figuras vigentes en
   `bbg/figuras/`, ya citadas sin error en la tesis.
4. ~~Renombrar la plantilla U. de Chile para que `\documentclass{umemoria}` resuelva~~ — hecho.
5. ~~Auditoría de rigor del paper empírico para el envío standalone (2026-09-18)~~ — **hecho**:
   revisión línea por línea de `paper2_empirico.tex` contra adjetivos no sustentados,
   consistencia de notación y trazabilidad de cifras a `NUMEROS_CANONICOS_BBG.md`. Un
   hallazgo real: en la sección "Identificación causal" (párrafo de *wild cluster bootstrap*),
   el $p$-valor de $\beta_3$ en el panel completo estaba transcrito como $0{,}67$; el valor
   canónico (`NUMEROS_CANONICOS_BBG.md`, línea ~263: `p_wildboot = 0,138`) y el propio
   "Resumen del capítulo" del mismo archivo (línea 7) dan $p=0{,}14$ — corregido. El resto del
   cuerpo (Introducción, Marco teórico, Estado del arte, Metodología, Datos, Resultados,
   Discusión) pasó la auditoría sin hallazgos adicionales.
