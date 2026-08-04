# JLoss Reconstruction

Motor de cómputo de **JLoss** (*Joint Losses*), el indicador de fragilidad bancaria sistémica
$JLoss_{i,t}$ usado en la tesis "Fragilidad Bancaria y Riesgos del Crecimiento a la Baja". Esta
carpeta contiene el motor vigente, el pipeline de extracción de datos por país, y el código MATLAB
legado del que el motor Python fue portado y contra el que fue validado.

## 1. Qué mide JLoss y cómo se calcula

JLoss combina **pérdida esperada (EL)** y **pérdida no esperada (UL)** del sistema bancario de un
país en un trimestre dado, expresada como porcentaje del pasivo total del sistema:

$$JLoss_t = \frac{EL_t + UL_t}{\sum_i EAD_{i,t}} \times 100$$

El cómputo tiene tres etapas:

1. **PD individual — modelo estructural de Merton/KMV.** Para cada banco-trimestre se estima la
   probabilidad de default (EDF) resolviendo el sistema de KMV en variables normalizadas
   ($x = [V_A/E,\ \sigma_A]$) a partir de la capitalización bursátil, su volatilidad realizada
   trimestral (anualizada por $\sqrt{4}$) y el punto de default $D^* = ST + 0{,}5 \times LT$
   (deuda de corto plazo + la mitad de la de largo plazo). La distancia a default (DD) es lineal
   (no el $d_2$ de Black-Scholes), replicando `indivpds.m`.
2. **Condicionalización a un factor sistémico — Vasicek (modelo de un factor).** Cada PD
   individual se condiciona a la realización del factor común $V$ vía
   `cond_pd(pd, rho, V) = Φ((Φ⁻¹(pd) − ρV) / √(1−ρ²))`, integrando por cuadratura de
   Gauss-Hermite (orden 7) sobre el factor. En la corrida oficial $\rho = 0{,}4$ es plano para
   todos los bancos (valor constante verificado en `jloss.mat`).
3. **Agregación de la distribución de pérdidas por aproximación de punto de silla (saddle-point)**
   y **contribución marginal.** La distribución de pérdidas agregadas del sistema se aproxima con
   el método de punto de silla (`K0`/`K1`/`K2`, cumulantes; `find_saddle` resuelve la ecuación de
   punto de silla con `brentq`) sobre una malla de pérdida $[0{,}01,\ 0{,}048]$ en 500 pasos. Se
   obtiene el $VaR_{99}$ de la distribución agregada (`find_var99`) y luego la **contribución
   marginal de cada banco** a ese $VaR_{99}$ (`loss_contrib_py`), cuya suma es $UL$. $EL$ es
   simplemente $\sum_i EAD_i \times PD_i$, con $EAD_i = LGD \times$ pasivos del banco ($LGD=0{,}45$
   fijo).

Parámetros del modelo (idénticos a la corrida oficial de MATLAB): `LGD=0.45`, malla de pérdida
`[0.01, 0.048]` con `NUM_STEPS=500`, cuadratura Gauss-Hermite de orden `NUM_ORDER=7`,
`PERCENTILE=0.99`, `R_FREE=0.04`, horizonte `MERTON_T=1.0`, `RHO_FLAT=0.4`.

## 2. Motor y notebook vigentes

- **`jloss_engine.py`** (24-jul) es el motor vigente, reutilizable como librería o CLI
  (`python jloss_engine.py --countries chile brazil peru mexico --indir . --out Panel_JLoss_v9.csv`).
  El bloque saddle-point (`cond_pd`, `K0`, `K1`, `K2`, `find_saddle`, `get_prob_cdf`,
  `loss_distrib_py`, `find_var99`, `loss_contrib_py`, `compute_jloss`) está copiado **verbatim**
  del notebook certificado v8 y no debe modificarse sin re-validar contra `pd_indiv.mat` del
  legado MATLAB. El solver Merton/KMV (`merton_pd`) sí fue **corregido respecto al notebook**:
  agrega multi-arranque (parte de una inicialización KMV ingenua $V_A \approx E + D$ antes de
  probar el $x_0=[1,1]$ histórico de `KMVOptsearch.m`), lo que sube la tasa de convergencia de
  ~43% a ~83% sin alterar los valores donde el método original ya convergía (diferencia máxima
  1,3e-9) — el problema que corrige es un sesgo de selección que descartaba justo a los bancos más
  apalancados (los que más contribuyen al riesgo sistémico).
- **`JLoss_reconstruction_v8.ipynb`** (24-jul) es el notebook de reconstrucción certificado: para
  14 países toma directamente el `CR` oficial de `matlab/jloss.mat` (resultados MATLAB), y para 4
  países ausentes de ese archivo (Rusia, Sudáfrica, Turquía, Venezuela) calcula JLoss desde cero
  con el mismo motor Merton/KMV + punto de silla. Documenta la certificación: reproduce `CR` de
  MATLAB a tolerancia $<10^{-6}$ cuando el conjunto de bancos por trimestre coincide.
- **Salidas vigentes:** `Panel_JLoss_v8.csv` (panel país-trimestre, 459 obs., 18 países) y
  `JLoss_by_country_v8.png` (serie por país), ambos en la raíz de esta carpeta.
- `Panel_regresion_v2.csv` y `Jloss.zip` en la raíz son artefactos anteriores — ver
  `CONTROL_DE_VERSIONES.md` para su estatus exacto.

## 3. `JLoss-pipeline/` — pipeline de extracción por país

Repositorio de replicación más amplio, con su propio `README.md` y `RUNBOOK.md` (léanse ahí los
detalles completos; resumen aquí):

- **`extraccion/`** contiene un subdirectorio por país (28 en total) con el extractor que produce
  el esquema común `balance_<pais>.csv` / `mktcap_<pais>.csv` / `coverage_<pais>.csv` que consume
  `jloss_engine.py`. Los extractores **vigentes y resueltos** (fuente pública confirmada, según el
  análisis de vigencia del proyecto) son:
  - Chile — API CMF Bancos (`extract_chile.py`)
  - Brasil — BCB Olinda IFData / OData (`extract_brazil.py`)
  - Colombia — datos.gov.co / Socrata (`extract_colombia.py`, más scripts auxiliares de descarga
    XBRL de la SFC)
  - Perú — boletines SBS, requiere descarga previa (`download_sbs.py` + `extract_peru.py`)
  - México — CNBV Portafolio, requiere descarga/exportación previa (`download_cnbv.py` +
    `extract_mexico.py`)
  - Sudáfrica — SARB BA900 (`download_ba900.py`, `ba900_parse.py`, `extract_southafrica.py`)
  - Argentina — BCRA datos abiertos, `.7z` (`extract_argentina.py`)
  - Además: Bulgaria, China, Egipto, Hungría, India, Indonesia, Malasia, Pakistán, Panamá,
    Filipinas, Polonia, Rusia, Arabia Saudita, Corea del Sur, Tailandia, Turquía, Venezuela,
    Vietnam — cada uno en su propia carpeta bajo `extraccion/`.
  - `jloss_common.py` (bajo `extraccion/argentina/`) trae el esquema común, el fetch de market
    cap y el reporte de cobertura reutilizados por los extractores.
- **`resultados/`** contiene una copia del notebook v8, los `balance_*.csv`/`mktcap_*.csv`/
  `coverage_*.csv` consolidados para Brasil/Chile/Colombia/México/Perú, y scripts de
  consolidación/comprobación (`build_panel.py`, `consolidation.py`, `comprobation_<pais>.py`,
  `book_pd.py` — PD contable tipo z-score de Roy/Laeven-Levine para bancos no cotizados, calibrada
  a la escala de la PD de mercado).
- **`RUNBOOK.md`** describe el flujo completo para producir una versión actualizada del panel
  (PD de mercado + PD contable calibrada + motor JLoss con $\rho$ doble: plano 0,4 vs. estimado
  por factor común) — no es necesario ejecutarlo para reproducir `Panel_JLoss_v8.csv`, que ya está
  generado.

## 4. Legado: `matlab/` y `output_v0/`

- **`matlab/`** (~825 MB) es el código **original en MATLAB** (`countrypd.m`, `loss_distrib.m`,
  `loss_contrib.m`, `get_prob.m`, `LinealXY2.m`, `find_saddlev1.m`, `get_K1st/2nd/3rd.m`,
  `KMVfun.m`, `KMVOptsearch.m`, `indivpds.m`, entre otros) del que el motor Python (`jloss_engine.py`
  / notebook v8) fue portado. Es **histórico, ya no es la fuente de cómputo vigente**: el motor
  Python fue validado contra él y lo reproduce a tolerancia $<10^{-6}$. Contiene además una gran
  cantidad de `.mat` de datos intermedios, en su mayoría redundantes o fragmentados (múltiples
  `data_mktcap_processed_*.mat` y `data_price_processed_*.mat` particionados por rango de
  columnas). **Se conserva como legado — no borrar sin autorización explícita del usuario.**
- **`output_v0/`** es un output antiguo (mayo-2025), predecesor de las salidas actuales
  (`countryPDS.m`, `jloss_filled.mat`, `prelim_results.xlsx`, `visualizaciones_v0.ipynb`).
  Igualmente histórico y no vigente. **No borrar.**

## 5. Hallazgo de higiene: entorno virtual committeado

`JLoss-pipeline/venv/` (~508 MB) es un entorno virtual de Python que quedó **committeado** en el
repositorio — no debería versionarse nunca (es binario, regenerable, y specific de la máquina que
lo creó). Ya está excluido en el `.gitignore` de la raíz del proyecto, por lo que Git no lo va a
volver a trackear a futuro, pero el histórico ya lo tiene. Se documenta aquí como hallazgo de
higiene; **no se ha borrado ni se sugiere borrarlo** sin confirmación explícita del usuario (podría
requerir limpiar el historial de Git, no solo el working tree).

## 6. Relación con el resto del proyecto

`Panel_JLoss_v8.csv` es el insumo de JLoss para la construcción del panel de la tesis en
`1_Codigo/Panel/` (los scripts `consolidate_panel.py` / `build_panel_v2.py` incorporan la serie
JLoss al panel EMBI × GaR × JLoss, típicamente a través de su conversión a `Jloss.dta`). De ahí en
adelante, la serie JLoss alimenta la estimación del mecanismo $JLoss \times GaR$ documentado en
`4_Redaccion/`.

## 7. Fuente de verdad

El estatus de vigencia de **todo** el proyecto (qué está vigente, qué es legado, qué no debe
versionarse) se mantiene en `4_Redaccion/CONTROL_DE_VERSIONES.md` — sección 3.11 ("Motor JLoss
(cómputo)") documenta específicamente esta carpeta. Ante cualquier duda o discrepancia con lo
descrito aquí, ese archivo es la referencia autoritativa.
