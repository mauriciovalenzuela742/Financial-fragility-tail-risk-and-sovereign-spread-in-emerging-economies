# Prototipo Original JLoss — Diciembre 2025

## ¿Qué es esta carpeta?

Esta carpeta contiene el **prototipo original e histórico** del proyecto de tesis sobre fragilidad bancaria sistémica, Growth-at-Risk (GaR), spread soberano (EMBI) y organización industrial bancaria. Fue desarrollado en diciembre 2025 como punto de partida conceptual y ya **no es vigente para cómputo**.

El motor vigente actual reside en:
- **Motor reconstruido:** `1_Codigo/JLoss_reconstruction/jloss_engine.py`
- **Notebook vigente:** `1_Codigo/JLoss_reconstruction_v8.ipynb`

Esta carpeta se conserva como **legado histórico documentado** y **nunca se borra**. No se utiliza como fuente de números para la tesis final. Para información sobre versiones vigentes y obsoletas, ver `4_Redaccion/CONTROL_DE_VERSIONES.md`.

---

## Inventario de archivos

### Raíz (v0/)

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Script minimal con punto de entrada del proyecto original. |
| `JLoss.ipynb` | Notebook principal que integra datos de JLoss, GaR (del CEMLA) y spreads EMBI. Limpia, transforma y unifica las tres métricas de riesgo. |
| `Jloss.dta` | Dataset en formato Stata de la métrica JLoss original (estimaciones de pérdida esperada). |
| `GaRxpaisxtime.png` | Gráfico de Growth-at-Risk por país y tiempo. |
| `Jlossxpaisxtime.png` | Gráfico de JLoss por país y tiempo. |
| `spreadxpaisxtime.png` | Gráfico de spread soberano (EMBI) por país y tiempo. |
| `pyproject.toml` | Configuración del proyecto Python (versión 0.1.0, sin dependencias listadas). |
| `README.md` | Este archivo. |

### Subdirectorio: simulation_outputs/

Contiene **la simulación del modelo teórico de organización industrial (OI) bancaria**, punto de partida conceptual del capítulo teórico final de la tesis.

| Archivo | Descripción |
|---------|-------------|
| `simulacion_modelo_oi.ipynb` | **Notebook precursor del modelo de competencia bancaria.** Simula un modelo de Cournot de competencia simétrica entre n bancos con externalidad sistémica. Compara el equilibrio privado (a_priv) con el óptimo social (a_soc), calcula pérdidas agregadas L, spreads S = λ·η(g)·L, e impuesto Pigouviano t* que alinea incentivos. Los parámetros (α, κ, ψ, δ, β, γ, λ) son ajustables según calibración. Este notebook **es el PRECURSOR CONCEPTUAL DIRECTO del working paper teórico de organización industrial que hoy reside en `4_Redaccion/modelo OI/working_paper.tex`.** |
| `simulation_model_io_full.csv` | Dataset completo de la simulación: grid de severidad macro g (0 a 2), variables de equilibrio privado y social, spreads, pérdidas y t*. |
| `summary_points.csv` | Resumen tabular de puntos representativos (g = 0, 0.5, 1.0, 1.5, 2.0) con coeficientes clave. |
| `a_priv_vs_a_soc.png` | Gráfico que muestra el nivel de riesgo privado (a_priv) vs óptimo social (a_soc) en función de severidad macro. |
| `spread_priv_vs_soc.png` | Gráfico que compara spreads privados vs spreads en el óptimo social. |
| `spread_gap.png` | Gráfico de la brecha S_priv - S_soc, visualizando el exceso de spreads debido a externalidades. |
| `t_star.png` | Gráfico del impuesto Pigouviano óptimo t* necesario para alinear el equilibrio privado con el óptimo social. |

---

## Conexión con el modelo teórico final

**`simulacion_modelo_oi.ipynb` es el precursor conceptual directo del capítulo teórico final.**

El notebook especifica un modelo simplificado de competencia bancaria que:
1. Plantea el trade-off entre beneficio privado (α·a) y costo de riesgo (κ·a²/2).
2. Introduce una externalidad sistémica: contribución de riesgo agregado a pérdidas (β·A + γ·A²).
3. Muestra que el equilibrio privado genera demasiado riesgo vs el óptimo social.
4. Propone un impuesto Pigouviano t* como mecanismo correctivo.
5. Vincula severidad macro (g) a sensibilidad fiscal (η(g)), produciendo spreads más altos en contextos frágiles.

Este modelo teórico fue elaborado posteriormente en una secuencia de documentos de fase:
- `4_Redaccion/modelo OI/Plan_Arista_OI_Competencia_Fragilidad.md` — plan estratégico.
- `4_Redaccion/modelo OI/Fase_II_Modelo_Cournot.md` — formalización del modelo.
- `4_Redaccion/modelo OI/Fase_III_Proposiciones_y_Calibracion.md` — proposiciones teóricas.
- `4_Redaccion/modelo OI/Fase_IV_Cierre_Macro_Soberano.md` — cierre macroeconómico y spillovers.

**El documento de salida es `4_Redaccion/modelo OI/working_paper.tex`**, que contiene la formalización completa del modelo, proposiciones, calibración empírica y resultados de robustez. Incluye apéndice matemático (`apendice_matematico.tex`) y figuras generadas en las fases de estimación y Monte Carlo.

---

## Control de versiones

Para información exhaustiva sobre qué archivo es vigente en cada línea de investigación del proyecto completo, consulte:

**`4_Redaccion/CONTROL_DE_VERSIONES.md`** — único documento maestro de verdad sobre vigencia de especificaciones, datos base, N de observaciones y lineaje de contenido.

Este documento es especialmente importante para:
- Distinguir entre prototipos históricos (como esta carpeta) y código vigente.
- Verificar qué base de datos (e.g., `Panel_final_all17.csv`) es canónica (N = 253).
- Confirmar de dónde provienen números citados en la tesis (con archivo fuente, especificación y N).

---

## Notas históricas

- **Fecha de creación:** Diciembre 2025.
- **Estado:** Obsoleto para computación, vigente como documentación conceptual histórica.
- **No se elimina:** Esta carpeta se preserva indefinidamente como registro del desarrollo inicial del proyecto.
- **No se reutiliza:** Los números de esta carpeta no se usan para la tesis final; se utilizan solo para referencia histórica sobre la evolución del pensamiento teórico.
