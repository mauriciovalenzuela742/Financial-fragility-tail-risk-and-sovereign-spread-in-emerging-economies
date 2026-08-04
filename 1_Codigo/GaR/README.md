# GaR — Motor de cómputo Growth-at-Risk

**Proyecto:** *Fragilidad Bancaria y Riesgos del Crecimiento a la Baja: Cómo la Interacción entre JLoss y GaR Determina el Spread Soberano en Economías en Desarrollo.*

Esta carpeta contiene el motor propio (Python) que calcula la serie $GaR_{i,t}$ — el percentil 5% condicional del crecimiento del PIB, por país y trimestre — y su insumo principal, el Índice de Condiciones Financieras (FCI). Es un porteo del framework CEMLA C-GARP (R) a Python, validado contra la implementación de referencia.

Para el detalle metodológico completo, el instructivo de ejecución y el diccionario de columnas de la salida, ver los README específicos de cada pipeline:

- [`GaR_pipeline_README.md`](GaR_pipeline_README.md) — motor GaR, instructivo paso a paso, validación.
- [`FCI_pipeline_README.md`](FCI_pipeline_README.md) — motor FCI, formato de insumos, instructivo para agregar un país nuevo.

Este README da la vista de conjunto de la carpeta: qué archivo hace qué, qué datos están completos y cuáles no, y cómo encaja esto en el resto del proyecto.

---

## 1. Qué hace este motor

La metodología es **regresión cuantílica de panel con efectos fijos**, siguiendo Adrian, Boyarchenko & Giannone (2019, *Vulnerable Growth*) y la plataforma de código abierto CEMLA C-GARP (Ossandon Busch et al., 2022):

1. Se regresiona el crecimiento del PIB interanual (`g_GDP`), adelantado `h` trimestres, sobre `g_GDP` contemporáneo, el VIX (factor *push* global) y el FCI ortogonalizado respecto al VIX — todo por país y en cada corte temporal.
2. La regresión es **cuantílica** (no OLS): se estiman 19–39 cuantiles $\tau$ de la distribución condicional del crecimiento futuro, con **efectos fijos compartidos entre cuantiles** (estimador `pfe` de Koenker, 2004), resuelta como un único programa lineal (solver HiGHS).
3. El **GaR** es, por definición, el cuantil condicional al 5% ($\hat{Q}(0.05)$) de esa distribución estimada — la cola izquierda del crecimiento esperado. De la función cuantil completa también se derivan `prob_neg` (probabilidad de crecimiento negativo), Expected Shortfall (`ES`), media, dispersión y asimetría de la cola.
4. Como control de robustez se ajusta además una distribución **skew-t** (Azzalini–Capitanio) a los mismos cuantiles, replicando el enfoque paramétrico de Adrian-Boyarchenko-Giannone.
5. Todo esto se corre en **ventana expansiva**: en cada corte trimestral $t$ los coeficientes se re-estiman solo con datos hasta $t$ (pseudo *real-time*, sin *look-ahead*), produciendo la serie $GaR_{i,t}$ completa.

El insumo central de la regresión — el **FCI** — se calcula aparte, por país, a partir de series diarias de bolsa (STX), tasa soberana (Ryr) e IPC (CPI), más el tipo de cambio real efectivo (rEER) mensual: es una forma cuadrática que resume el estrés financiero sistémico (co-movimiento entre los sub-índices bursátil, de tasa y cambiario).

---

## 2. Mapa de archivos

| Archivo | Rol |
|---|---|
| `gar_engine.py` | **Motor GaR.** Preprocesamiento (lead, ortogonalización, z-scores), estimador de panel `pfe` vía LP (`fit_pfe`), lectura del GaR desde los cuantiles (`gar_from_quantiles`), ajuste skew-t de robustez (`gar_from_skewt`) y el snapshot completo por fecha (`estimate_at`). |
| `fci_engine.py` | **Motor FCI.** Bloque bursátil (`get_STX`), bloque de tasa (`get_Ryr_daily`), bloque cambiario (`get_rEER`), estandarización expansiva (`method_b_max`), correlaciones EWMA (`corr_EWMA`) y agregación en la forma cuadrática (`FCIS`). Orquestador por país: `compute_fci(country_dir, country, ref_dir)`. |
| `phase2_gar_panel.py` | **Driver de ventana expansiva.** Envuelve `gar_engine.estimate_at` sobre cada fecha de corte trimestral del panel `GaR_panel.xlsx` y guarda la serie en `gar_panel_latam.csv` (5 países LatAm, checkpoint reanudable `_ckpt_latam.csv`). |
| `fetch_controls.py` | Descarga controles macro domésticos (deuda/PIB, balance fiscal, reservas/PIB, cuenta corriente, inflación, REER) desde WDI/BIS para 5 países LatAm y los deja en `controls_panel.csv`, listo para merge por `(country, quarter)`. No es parte del cómputo del GaR — alimenta las regresiones extendidas. |
| `run_reg_extended.py` | Une `controls_panel.csv` al panel EMBI×JLoss×GaR y corre las especificaciones ampliadas con `linearmodels.PanelOLS` (SE Driscoll-Kraay), probando la hipótesis $\theta$ (interacción JLoss×GaR) < 0. Salida: `Panel_regresion_v3.csv`, `Tabla_resultados_extendida.csv`. |
| `GaR_pipeline_README.md` | Instructivo y reporte de validación del pipeline GaR (metodología, decisiones fijadas, diccionario de la salida). |
| `FCI_pipeline_README.md` | Instructivo y reporte de validación del pipeline FCI (formato de insumos por país, instructivo para país nuevo, actualización de ventana). |
| `GaR_test.xlsx`, `Auditoria_JLoss_GaR.xlsx` | Artefactos de **validación interna**: referencia CEMLA para verificar etapa por etapa el porteo (`GaR_test.xlsx`) y auditoría cruzada del panel final (`Auditoria_JLoss_GaR.xlsx`, 9-jul). |

Nota sobre alcance: `phase2_gar_panel.py` en la raíz de esta carpeta corre sobre `GaR_panel.xlsx` (5 países LatAm) y es el driver documentado en `GaR_pipeline_README.md`. La extensión a los 17 países del panel final (`gar_panel_all17.csv`, insumo vigente de `1_Codigo/Panel/`, ver CONTROL_DE_VERSIONES.md) se corrió con variantes de este mismo driver (`phase2_gar_panel_all17.py` y copias de `gar_engine.py`/`fci_engine.py`) que viven dentro de `individuals/`, junto con el instructivo `instructivo_backtest_GaR_local.md` que documenta esa corrida (incluye un bug de vintage de FCI y un bug de `g_GDP` para Malasia/Filipinas, ambos ya corregidos). El motor en sí (`gar_engine.py`/`fci_engine.py`) es el mismo código; lo que cambia entre variantes es el panel de entrada y la cantidad de países.

---

## 3. Estructura de datos por país

### `individuals/` — insumos completos (25-jul)

Un subdirectorio por país con las series primarias y derivadas necesarias para el panel:

```
individuals/<PAIS>/
   CPI_<PAIS>.csv     IPC (diaria)
   Ryr_<PAIS>.csv     Rendimiento soberano 10Y (diaria)
   STX_<PAIS>.csv     Índice bursátil (diaria)
   rEER_<PAIS>.csv    Tipo de cambio real efectivo (mensual)
   GDP_<PAIS>.csv     PIB real (nivel)
   gGDP_<PAIS>.csv    Crecimiento interanual del PIB (derivado de GDP)
   FCI_<PAIS>.csv     Salida de fci_engine.compute_fci para ese país
```

Contiene **21 países** (`ARGENTINA, BRAZIL, BULGARIA, CHILE, CHINA, COLOMBIA, HUNGARY, INDIA, INDONESIA, MALAYSIA, MEXICO, PAKISTAN, PERU, PHILIPPINES, POLAND, RUSSIA, SAUDIARABIA, SOUTHAFRICA, SOUTHKOREA, THAILAND, TURKEY`) más `US/` como país de referencia (tasa y CPI, requeridos por el bloque de tasa del FCI). De estos, **17 tienen FCI calculable y forman el panel vigente** (`gar_panel_all17.csv`, ver `instructivo_backtest_GaR_local.md`); **ARGENTINA y SAUDIARABIA quedan bloqueados** por no tener fuente pública de rendimiento soberano 10Y (`Ryr`), documentado en `instructivo_FCI_paises_restantes.md`. Los scripts de extracción que alimentan esta carpeta (descarga de CPI/GDP/Ryr/STX/rEER desde Investing/IFS/FRED/BIS) están en `extraction_individuals/`.

### `other_countries/` — trabajo en curso, incompleto (28-jul)

Extracción parcial para 5 países candidatos a incorporar más adelante:

```
other_countries/
   EGYPT/      Ryr, STX (parcial, MSCI en vez de índice local) — falta CPI, rEER
   PANAMA/     vacío — nada extraído aún
   UAE/        rEER, MSCI (parcial) — falta CPI, Ryr, STX propiamente dicho
   VENEZUELA/  solo CPI — falta Ryr, STX, rEER
   VIETNAM/    Ryr, índice bursátil MSCI (parcial) — falta CPI, rEER
```

Ninguno de estos países tiene el set completo de 4 insumos que exige `fci_engine.compute_fci` (ver `FCI_pipeline_README.md`, sección 3), por lo que **ninguno entra todavía al panel GaR**. Es la frontera de expansión del proyecto, no datos listos para usar.

---

## 4. `CGARP v2.1/` — referencia de validación, no motor de cómputo

`CGARP v2.1/` es la **implementación en R de CEMLA** (Ossandon Busch et al., 2022) que sirvió de base para portar `gar_engine.py` y `fci_engine.py` a Python:

```
CGARP v2.1/
   Code/      GaR_*.R, fci_*.R — código fuente R original (rqpd, wrappers, parámetros)
   Source/    (vacío)
   output/    FCI_test.xlsx, GaR_20260508_*.xlsx — corridas de referencia + PDFs de manual (FCI README.pdf, GaR README.pdf)
```

**No se usa para calcular el GaR ni el FCI de la tesis.** Su único rol es la **validación cruzada** del motor Python propio: correr la misma configuración en R y Python y comparar salidas etapa por etapa (ver la nota de validación al inicio de `gar_engine.py` y la sección 1 de `FCI_pipeline_README.md`, que reporta corr=0.9995 del FCI propio contra la referencia). El motor vigente para producir resultados de la tesis es siempre el Python de esta carpeta.

---

## 5. Relación con el resto del proyecto

El flujo de datos hacia adelante es:

```
individuals/<PAIS>/*.csv  →  fci_engine.compute_fci  →  FCI_<PAIS>.csv
                                                              │
GaR_panel*.xlsx (g_GDP, VIX, FCI por país/trimestre)  ←───────┘
        │
        ▼
phase2_gar_panel*.py (ventana expansiva, gar_engine.estimate_at)
        │
        ▼
gar_panel_<tag>.csv  (GaR, ES, prob_neg, momentos — por país y trimestre)
        │
        ▼
1_Codigo/Panel/   (merge con JLoss y EMBI por (country, quarter);
                    notebooks EDA, regresiones de mecanismo JLoss×GaR,
                    tabla de resultados de la tesis)
```

`gar_panel_all17.csv` es el insumo GaR del panel base vigente de la tesis (5 países LatAm con EMBI, GaR entrenado con 17 economías) que consumen los notebooks y regresiones en `1_Codigo/Panel/`. `fetch_controls.py` y `run_reg_extended.py`, en cambio, son un ramal aparte: agregan controles macro domésticos y corren especificaciones de robustez sobre un panel ya ensamblado (`Panel_regresion_v2.csv`), no participan en el cómputo del GaR en sí.

---

## 6. Fuente de verdad de vigencia

Este README describe la carpeta tal como está organizada, pero **la determinación de qué está vigente, qué es legado y por qué** para todo el proyecto — incluyendo esta carpeta (sección 3.12, "Motor GaR / FCI (cómputo)") — vive en:

**`4_Redaccion/CONTROL_DE_VERSIONES.md`**

Ante cualquier duda sobre qué archivo usar o si algo quedó obsoleto, esa es la referencia autoritativa, no este README.
