# Pipeline Growth-at-Risk (GaR) — Reporte e Instructivo

**Proyecto:** *Fragilidad Bancaria y Riesgos del Crecimiento a la Baja: Cómo la Interacción entre JLoss y GaR Determina el Spread Soberano en Economías en Desarrollo.*

**Componente:** Construcción de la métrica $GaR_{i,t}$ (porteo del framework CEMLA C-GARP de R a Python).

---

## 1. Resumen ejecutivo

Se portó la cadena Growth-at-Risk de CEMLA (originalmente en R, dependiente de `rqpd`) a Python, y se extendió de una estimación de *snapshot* único a una **serie temporal $GaR_{i,t}$ en ventana expansiva** (pseudo *real-time*, sin *look-ahead*). El motor estima, para cada trimestre y país, la distribución condicional del crecimiento del PIB un trimestre adelante mediante regresión cuantílica de panel con efectos fijos compartidos, y extrae el percentil 5% (GaR) junto con medidas de dispersión y asimetría de la cola.

Salida actual: `gar_panel_latam.csv` — 5 países LatAm (Brasil, Chile, Colombia, México, Perú), 56 trimestres (2010Q1–2023Q4).

---

## 2. Archivos del pipeline

| Archivo | Rol |
|---|---|
| `gar_engine.py` | Motor: preprocesamiento, estimador `pfe` (LP), lectura del GaR y ajuste skew-t. |
| `phase2_gar_panel.py` | Driver: bucle de ventana expansiva que produce la serie y la guarda en CSV. |
| `GaR_panel.xlsx` | **Insumo único** del motor (panel con `Date, Country, N_Country, g_GDP, VIX, FCI`). |
| `gar_panel_latam.csv` | **Salida**: serie $GaR_{i,t}$ + diagnósticos, formato largo. |
| `_ckpt_latam.csv` | Checkpoint reanudable (se regenera; puede borrarse). |

---

## 3. Metodología

### 3.1 Estimador de panel (`pfe`)
Regresión cuantílica de panel con **efectos fijos compartidos entre cuantiles** (Koenker, 2004), lo que `rqpd` denomina `method="pfe"`. Se resuelve como **un único programa lineal** con el solver HiGHS (vía `scipy.optimize.linprog`), eliminando la dependencia de R/`rqpd`. La normalización fija el efecto fijo del último país a cero (categoría base) más un intercepto por cuantil.

> El LP de HiGHS alcanza el **óptimo global exacto** del estimador. En la validación, su valor objetivo es estrictamente menor que el de `rqpd` (2.40614 vs 2.40654): el solver de punto interior de `rqpd` se detiene antes por tolerancia. Las diferencias de coeficientes son O(1e-3) y provienen de la implementación de referencia, no del porteo.

### 3.2 Lectura del GaR (método principal)
El GaR al 5% **es, por definición, el cuantil condicional 0.05**, que el estimador entrega directamente. No se usa KDE ni ancho de banda. Se aplica *rearrangement* (Chernozhukov, Fernández-Val & Galichon, 2010) para garantizar monotonicidad de la función cuantil. De ahí se derivan:
- $GaR_{i,t} = \hat{Q}_{i,t}(0.05)$
- `prob_neg` $= \hat{Q}^{-1}(0)$ (probabilidad de crecimiento negativo)
- `ES` (Expected Shortfall) $= \tfrac{1}{0.05}\int_0^{0.05}\hat{Q}(\tau)\,d\tau$
- `mean`, dispersión robusta (`std` vía IQR, `iqr_05_95`), asimetría (Bowley) y curtosis (Moors).

### 3.3 Control de robustez (skew-t de Adrian)
Como control metodológico se ajusta una **skew-t de Azzalini–Capitanio** a los cuantiles estimados (Adrian, Boyarchenko & Giannone, 2019, *Vulnerable Growth*), minimizando la distancia cuadrática en los cuantiles ancla {0.05, 0.25, 0.75, 0.95}. Entrega `GaR_st`, media, escala (ω = anchura de cola), `nu` (fatness) y asimetría.

### 3.4 Ventana expansiva
En cada corte $t$ los coeficientes cuantílicos se **re-estiman solo con datos hasta $t$**. Las observaciones dentro del horizonte $h$ del borde quedan con `future_dep_var` faltante y salen de la estimación: no hay *look-ahead*.

---

## 4. Decisiones fijadas

| Parámetro | Valor | Razón |
|---|---|---|
| Horizonte `h` | **1 trimestre** | Alinea el GaR con la frecuencia trimestral del panel JLoss y el *merge* por `(country, quarter)`; riesgo de cola contemporáneo con $JLoss_{i,t}$. |
| `n_tau` | **39** | Rejilla τ = {0.025, 0.05, …, 0.975}; el 0.05 cae exacto (GaR sin interpolar) y la cola por debajo del 5% queda muestreada (ES más fino). |
| Método GaR | **Cuantil directo** | Sin ancho de banda arbitrario; es la lectura del estimador de Koenker en su propio nivel. |
| Robustez | **skew-t (ABG)** | Confirma que el GaR no depende del suavizado. |
| Estimación | **Ventana expansiva** | Pseudo *real-time*, sin *look-ahead*. |

---

## 5. Definiciones y unidades

| Variable | Definición | Unidad |
|---|---|---|
| `g_GDP` | Crecimiento **interanual** del PIB real (q vs q−4) | decimal (0.045 = 4.5%) |
| `future_dep_var` | `g_GDP` adelantado `h=1` (variable a predecir) | decimal |
| **`GaR`** | Percentil 5% condicional de `future_dep_var` | decimal interanual |
| `VIX` | Volatilidad implícita S&P500 (factor *push* global) | puntos índice (% anualizado) |
| `FCI` | Índice de condiciones financieras CEMLA (mayor = más estrés) | índice adimensional |
| `Ryr` | Rendimiento soberano 10Y (insumo FCI) | % anual |
| `CPI` / `STX` / `rEER` | Insumos FCI: IPC, índice bursátil, TCR efectivo | índices base ~100 |

> `g_GDP` es **interanual**, no trimestral anualizado. Con `h=1`, el GaR mide el riesgo de cola del crecimiento interanual del próximo trimestre (trimestres consecutivos solapan 3 meses, propiedad estándar del GaR sobre crecimiento YoY, como en ABG). Todas las columnas en unidades de crecimiento (`GaR`, `ES`, `mean`, `std`, `iqr_05_95`) comparten las unidades de `g_GDP`.

---

## 6. Validación realizada

**Etapas internas vs. `GaR_test.xlsx` (referencia CEMLA):**
- Preprocesamiento (lead, ortogonalización, z-scores): exacto, max|diff| ~1e-15.
- Estimador `pfe`: óptimo global exacto; coeficientes dentro de ~1e-3 de la referencia (que es subóptima por tolerancia de `rqpd`).

**Validación de la serie (bloque A):**
- **Robustez de método:** $\text{corr}(GaR_{\text{directo}}, GaR_{\text{skew-t}}) = 0.9996$, RMSE $=0.0011$. El percentil 5% no es artefacto del suavizado.
- **Volatilidad del GaR** (σ de la serie por país): ~3.4–4.4 pp.
- **Dispersión / anchura de cola:** `iqr_05_95` ~0.057–0.059; escala skew-t ~0.013–0.014.
- **Timing de crisis:** COVID-2020Q2 → GaR ≈ −18%, dispersión 0.077, `prob_neg`=1.0; *tightening* 2022Q3 → dispersión 0.100.
- **Mecanismo ABG:** $\text{corr}(GaR, \text{dispersión}) = -0.235$: peor cola coincide con colas más anchas (*vulnerable growth*).

---

## 7. INSTRUCTIVO PASO A PASO (Windows)

### Paso 0 — Requisitos
- Python 3.10+ (probado en 3.12). Verificar en *PowerShell* o *CMD*:
  ```
  python --version
  ```
- Si no está instalado, descargar de python.org y marcar **"Add Python to PATH"** en el instalador.

### Paso 1 — Instalar dependencias
En PowerShell:
```
pip install numpy pandas scipy openpyxl
```
(Versiones probadas: numpy 2.4, scipy 1.17, pandas 3.0, openpyxl 3.1. No requiere R ni `highspy`: el solver HiGHS viene dentro de `scipy`.)

### Paso 2 — Carpeta de trabajo
Colocar en una misma carpeta:
```
C:\GaR\
   ├── gar_engine.py
   ├── phase2_gar_panel.py
   └── GaR_panel.xlsx
```

### Paso 3 — Revisar el insumo `GaR_panel.xlsx`
Debe tener una hoja **`Panel`** con las columnas, **sin nada fuera de la tabla**:
`Date` (DD/MM/YYYY), `Country`, `N_Country` (entero 1..K), `g_GDP`, `VIX`, `FCI`.

### Paso 4 — Configurar parámetros (opcional)
Abrir `phase2_gar_panel.py` y ajustar el bloque de configuración si hace falta:
```python
SOURCE_FILE   = 'GaR_panel.xlsx'   # nombre del insumo
DEPENDENT     = 'g_GDP'
INDEPENDENT   = ('g_GDP', 'VIX')   # FCI entra ortogonalizado
H             = 1                   # horizonte (trimestres)
N_TAU         = 39                  # rejilla de cuantiles
PROBABILITY   = 0.05               # nivel del GaR / ES
MIN_TRAIN_OBS = 40                  # muestra mínima por corte
OUT_TAG       = 'latam'             # sufijo del archivo de salida
```

### Paso 5 — Ejecutar
Desde la carpeta `C:\GaR\` en PowerShell:
```
cd C:\GaR
python phase2_gar_panel.py
```
La consola imprime el avance por trimestre. Tarda ~4–5 min para 5 países (escala con el nº de países y de trimestres). Si se interrumpe, **al volver a ejecutar retoma desde el checkpoint** `_ckpt_<tag>.csv`.

### Paso 6 — Resultado
Se genera `gar_panel_latam.csv` (formato largo). Para forzar un recálculo limpio, borrar primero `_ckpt_latam.csv`.

### (Alternativa) Una sola fecha
Para estimar un único corte sin el bucle completo, en un script o consola Python:
```python
import pandas as pd
from gar_engine import estimate_at
panel = pd.read_excel('GaR_panel.xlsx', sheet_name='Panel')
print(estimate_at(panel, '01/12/2023', method='both'))
```

---

## 8. Diccionario de la salida (`gar_panel_*.csv`)

| Columna | Significado |
|---|---|
| `country`, `quarter`, `date` | Identificadores (`quarter` en formato `YYYYQq`). |
| `GaR` | **Percentil 5% condicional** (método principal). |
| `GaR_st` | GaR del ajuste skew-t (robustez ABG). |
| `prob_neg` | Probabilidad de crecimiento negativo el próximo trimestre. |
| `ES` | Expected Shortfall al 5% (media de la cola). |
| `mean` | Media de la distribución condicional. |
| `std`, `iqr_05_95` | Dispersión (escala robusta; anchura de cola 5–95). |
| `scale_st` | Escala ω del skew-t (anchura estructural de cola). |
| `skew`, `skew_st` | Asimetría (Bowley; parámetro del skew-t). |
| `nu_st` | Grados de libertad del skew-t (fatness; usar con cautela). |
| `n_train` | Tamaño de la muestra de estimación en ese corte. |

---

## 9. Pendiente para escalar a los 18 países (bloque B)

El motor consume un **único insumo** (`GaR_panel.xlsx`). Para los 13 países fuera de LatAm hay que construir, por país y a frecuencia trimestral:
1. `g_GDP` — crecimiento interanual del PIB real.
2. Los **4 insumos del FCI** (cadena `fci_*.R`, aún por portar): `CPI`, `Ryr` (soberano 10Y), `STX` (bursátil) diarias; `rEER` (TCR) mensual. Más el país de referencia (`US`) para el rendimiento real.
3. `VIX` es **compartido** (ya disponible).

Luego: ampliar `GaR_panel.xlsx` a 18 países y re-correr `phase2_gar_panel.py`. Finalmente, *merge* de `gar_panel.csv` con `Panel_JLoss_v7.csv` por `(country, quarter)`.

---

## Referencias
- Adrian, T., Boyarchenko, N. & Giannone, D. (2019). *Vulnerable Growth*. American Economic Review.
- Chernozhukov, V., Fernández-Val, I. & Galichon, A. (2010). *Quantile and Probability Curves Without Crossing*. Econometrica.
- Koenker, R. (2004). *Quantile Regression for Longitudinal Data*. Journal of Multivariate Analysis.
- Ossandon Busch et al. (2022). *Growth at Risk: methodology and applications in an open-source platform* (CEMLA C-GARP). Latin American Journal of Central Banking.
