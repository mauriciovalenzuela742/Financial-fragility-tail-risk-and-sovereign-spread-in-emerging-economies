# 4_Redaccion — Carpeta de escritura de la tesis

## 1. Qué es esta carpeta

Esta carpeta es el destino final de la **redacción** de la tesis de Magíster en Economía
Aplicada (Universidad de Chile). Aquí conviven dos papers que se ensamblarán como capítulos
de una misma tesis, usando la plantilla oficial `umemoria`:

- **Paper empírico** — JLoss × GaR × EMBI: efecto de la interacción JLoss×GaR sobre riesgo
  soberano (EMBI), con estimación en panel de países LatAm.
- **Paper teórico de Organización Industrial (OI)** — modelo de competencia Cournot y
  fragilidad financiera, con su apéndice matemático.

Los datos, código y notebooks que producen las cifras y figuras de ambos papers **no viven
aquí**: viven en `1_Codigo/` (y en menor medida `2_Datos/`), fuera de esta carpeta. Esta
carpeta contiene solo prosa, LaTeX y la plantilla de ensamblaje.

## 2. Mapa de la carpeta

| Ruta | Rol |
|---|---|
| `CONTROL_DE_VERSIONES.md` | **Documento maestro de vigencia de todo el proyecto** (no solo de esta carpeta). Ver sección 3. |
| `Boceto_1_actualizado.tex` | Texto vigente del paper empírico, pero con **números desactualizados**. Es insumo para una reescritura posterior, no fuente de cifras mientras esa reescritura no ocurra. |
| `archive/` | Borradores obsoletos del paper empírico, archivados con prefijo de fecha (`Boceto 1`, `Boceto_1_v2`, `Resultados_y_Discusion`, `Avance 1 Tesis`). Conservados por trazabilidad, no se usan. |
| `modelo OI/` | Fuente LaTeX completa del paper teórico de OI: `working_paper.tex` (vigente) y `apendice_matematico.tex` (vigente, demostraciones), compilan por separado. Incluye también los documentos de planificación `Plan_Arista_OI_Competencia_Fragilidad.md` y `Fase_II` a `Fase_VI` — **no son obsoletos**, son la bitácora de desarrollo del modelo y se conservan in situ. Y los scripts `fase3_calibracion.py`, `fase5_estimacion.py`, `mc_gar.py`, que usan un panel **simulado/de juguete** (`panel_template.csv`) para ilustración Monte Carlo del modelo teórico — no confundir con `1_Codigo/Panel/fase5_estimacion_real.py`, que usa datos reales y es el que cierra el modelo contra evidencia empírica. |
| `plantilla/` | Plantilla oficial de tesis U. de Chile: `umemoria.cls` + `main.tex` (recién renombrados desde `umemoria (2).cls` / `main (2).tex` para que `\documentclass{umemoria}` resuelva). `main.tex` es un ejemplo de otra tesis que hace `\input` de capítulos que todavía no existen (`intro.tex`, `contexto.tex`, etc.); sirve como plantilla de referencia para la fase de ensamblaje final. |

## 3. Estado actual del proyecto

- Los dos papers están **en reescritura**: el empírico porque sus cifras están desactualizadas
  (ver `CONTROL_DE_VERSIONES.md`, sección 0, sobre el conflicto de valores de θ aún sin
  resolver), el teórico porque su integración a la tesis todavía no se ha hecho.
- La **tesis ensamblada con la plantilla `umemoria` todavía no existe como tal**. `plantilla/`
  contiene solo el esqueleto de referencia; no hay capítulos propios (`intro.tex`,
  `contexto.tex`, etc.) escritos aún. El ensamblaje es una fase posterior del proyecto.

## 4. Fuente de verdad

**`CONTROL_DE_VERSIONES.md` es la única fuente de verdad sobre qué archivo es vigente**, en
esta carpeta y en el resto del proyecto (incluido `1_Codigo/`). Ante cualquier duda sobre
vigencia de un archivo, una cifra o una figura, consúltese ese documento directamente en vez
de asumir a partir de nombres o fechas de archivo — la convención de versionado del proyecto
usa el linaje de contenido, no el nombre ni el `mtime`. Este README no repite ese contenido;
solo lo resume y remite.
