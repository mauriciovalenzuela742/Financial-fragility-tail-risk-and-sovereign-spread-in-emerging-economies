# Instructivo: correr el backtest GaR (panel de 17 países) en tu máquina local

## Actualización — panel de 17 países + fix de vintage FCI (última)

**Qué se hizo:**

1. **Bug de vintage en FCI, corregido.** `GaR_panel_all.xlsx` traía el FCI
   "horneado" del momento en que se construyó ese archivo. Los CSV
   `individuals/<PAIS>/FCI_<PAIS>.csv` se siguieron recalculando después con
   más historia (`method_b_max` es una estandarización expansiva: cada
   recálculo con más meses cambia los z-scores de TODA la serie, no solo el
   tramo nuevo). Resultado: el FCI del panel y el FCI de los CSV habían
   divergido — verificado con BRASIL 2010Q1: panel = 0.2586, CSV recalculado =
   0.3084. Se recalculó `compute_fci()` para los 17 países **en una sola
   corrida** (mismo `initial=1990-01-01`, `final=2026-05-31`), se
   sobrescribieron los 17 `FCI_<PAIS>.csv` y se reconstruyó el panel con ese
   FCI fresco. 1158 de 1987 filas cambiaron de valor; cobertura idéntica (sin
   huecos nuevos). Este fix aplica a los 15 países ya existentes, no solo a
   los 2 nuevos — es necesario porque el estimador `pfe` comparte
   coeficientes (`b_hat`/`c_hat`) entre todos los países del pool en cada
   corte de fecha.
2. **MALAYSIA y PHILIPPINES agregados** (`N_Country` 16 y 17). Tenían FCI ya
   calculable (`STX`/`Ryr`/`rEER` completos) pero no estaban en
   `GaR_panel_all.xlsx` porque en su momento no había `g_GDP` verificable. Eso
   ya se resolvió (`GDP_MALAYSIA.csv`/`GDP_PHILIPPINES.csv`, fuente IMF IFS,
   mismo pipeline que el resto — ver `extraction_individuals/download_CPI_GDP.py`).
   MALAYSIA solo tiene historia de PIB desde 2015 (44 trimestres); PHILIPPINES
   desde 1981 (180 trimestres, FCI válido desde ~2000).
3. **Resultado:** `GaR_panel_all17.xlsx` (nuevo archivo, no reemplaza
   `GaR_panel_all.xlsx`) y `phase2_gar_panel_all17.py` (`OUT_TAG="all17"`,
   checkpoint propio `_ckpt_all17.csv`, no toca `_ckpt_all15.csv`).
4. **Verificación ya hecha** (antes de pasarte esto): `preprocess()` corre sin
   error en las 261 fechas del panel; una corrida completa de `estimate_at()`
   en una fecha temprana (01/12/2002, muestra chica) resuelve el LP en 0.3s y
   da GaR razonable para PHILIPPINES. La corrida completa (`estimate_at` con
   muestra grande, ej. 2020+) no se pudo probar en este entorno porque un solo
   corte ya supera el límite de ~45s del sandbox remoto — exactamente la razón
   por la que este backtest se corre local (ver sección "Por qué correrlo
   local" abajo). No hay motivo para esperar que falle: es el mismo código
   `gar_engine.py`, sin cambios, solo con más filas en el panel de entrada.

## Actualización — bug real encontrado en `g_GDP` de MALAYSIA/PHILIPPINES (corregido)

La primera corrida de `phase2_gar_panel_all17.py` (ya hecha una vez, resultado
descartado — ver `gar_panel_all17_BUGGY_gGDP_backup.csv`) movió el GaR de los
15 países originales de forma sistemática y grande (mediana -0.045, con
cruces de signo, ej. INDIA 2007Q4 pasó de +0.107 a -0.108). Descompuse la
causa con `estimate_at()` en varias fechas puntuales (barato, sin correr el
backtest completo):

- Efecto del fix de FCI solo (mismos 15 países, FCI viejo vs. fresco): chico,
  |diff| < 0.01 en todos los casos probados.
- Efecto de agregar MALAYSIA/PHILIPPINES al pool: grande, sistemáticamente
  negativo, -0.02 a -0.16.

Eso apuntó a MALAYSIA/PHILIPPINES como la causa. Revisando `gGDP_MALAYSIA.csv`
y `gGDP_PHILIPPINES.csv`: **estaban mal calculados** — no eran la variación
interanual (YoY, `GDP_t/GDP_{t-4} - 1`) que usa el resto del panel, sino algo
mal escalado (Philippines oscilaba entre -12% y +16% cada trimestre alternado,
un patrón estacional típico de dato trimestral SIN ajuste interanual;
Malaysia llegaba a mostrar "187%" de crecimiento en un trimestre). Verificado
a mano contra el nivel de PIB: el YoY correcto de Philippines en 2025 ronda
+3% a +5%, no los -12%/+16% que traía el archivo.

**Corregido:** recalculé `gGDP_<PAIS>.csv` para ambos países como
`GDP_t/GDP_{t-4} - 1` (misma fórmula que `download_CPI_GDP.py` usa para el
resto del panel). Resultado: std de MALAYSIA pasó de 3.83 a 0.049, PHILIPPINES
de 0.100 a 0.041 — ahora en línea con el resto del panel (que va de 0.018 a
0.074). Reconstruí `GaR_panel_all17.xlsx` con este `g_GDP` corregido (FCI
fresco sin cambios). Repetí la descomposición puntual: con el fix, agregar
MALAYSIA/PHILIPPINES ahora mueve el GaR de los países existentes en |diff| <
0.004 — el corrimiento grande desapareció.

**Los archivos `_BUGGY_gGDP_backup` quedan solo como respaldo/evidencia — no
los uses.** Borré el checkpoint viejo (`_ckpt_all17.csv`) para forzar una
corrida limpia.

## Actualización — METHOD="both" (agrega columnas skew-t para la sección 13.3)

`gar_panel_all15.csv` solo tiene las columnas del método `quantile` directo
(`GaR`, `prob_neg`, `ES`, `ER`, `mean`, `std`, `iqr_05_95`, `skew`, `kurt`).
La sección 13.3 del paper (densidad condicional skew-t para Chile, trimestre
de estrés vs. benigno) necesita además `GaR_st`, `scale_st` ($\omega$),
`alpha_st` ($\alpha$), `nu_st` ($\nu$), `skew_st`, `mean_st`, `std_st`,
`sse_st` — que solo se calculan con `method="both"` (ajusta también la
skew-t de Azzalini vía `gar_from_skewt`). Cambié `METHOD = "both"` en
`phase2_gar_panel_all17.py`. Probado en una fecha chica (01/12/2002): corre
sin error, columnas confirmadas, **pero tarda ~11s por fecha** (vs. ~0.2-0.3s
con `method="quantile"` solo) porque agrega una optimización Nelder-Mead por
país en cada corte — el ajuste skew-t no tiene forma cerrada. Con 17 países y
~260 fechas, esto puede llevar bastante más que los 20-50 min originales;
contá con que la corrida completa tome más tiempo esta vez.

Nota: en fechas muy tempranas (muestra chica, ej. 2002) el fit skew-t puede
devolver `nu_st` con valores extremos (ej. 10^5-10^13) para algún país — es un
óptimo degenerado del Nelder-Mead cuando hay poca información para pinchar la
forma de la cola, no un bug de esta corrida. Debería estabilizarse en
trimestres con más historia (que es lo que usa la sección 13.3 para Chile).
Si ves algo raro ahí, avisame.

## Qué falta (para vos, local)

Correr `phase2_gar_panel_all17.py` de nuevo (el checkpoint viejo ya no existe,
así que arranca de cero). Al terminar, comparar `gar_panel_all17.csv` contra
`gar_panel_all15.csv` para los 15 países originales — con el fix de `g_GDP` ya
deberían moverse poco (< 0.01 típico, ver la descomposición arriba). Si aun
así ves un salto grande en algún país/trimestre puntual, avisame antes de
usarlo en el paper.

## Actualización anterior (12 → 15 países)

El panel creció de 12 a **15 países** (se sumaron CHINA, PAKISTAN, SOUTHAFRICA) y se
corrigió un bug real: BULGARIA, INDONESIA, POLAND, SOUTHKOREA, PAKISTAN y SOUTHAFRICA
tenían `g_GDP` trimestral **QoQ mal etiquetado como interanual** (mismo problema que ya
se había detectado antes en otros 7 países). Todos reconstruidos vía
`pct_change(4)` sobre el nivel de PIB. HUNGARY se extendió hasta 2026Q1 con la fuente
oficial (KSH/stadat), reemplazando la serie FRED que llegaba solo hasta 2023Q3.

Por este cambio de datos, **borré el checkpoint anterior** (`_ckpt_all12.csv`, que
había avanzado hasta 2014Q4) porque quedó inconsistente con el panel corregido. El
nuevo driver (`phase2_gar_panel_all.py`, `OUT_TAG = "all15"`) arranca de cero con
`_ckpt_all15.csv`.

## Por qué correrlo local

El backtest reestima el modelo en cada trimestre (100+ cortes) y el LP crece con el
tamaño de muestra acumulada. En el sandbox remoto cada llamada tiene un límite de ~45s,
así que el progreso queda fragmentado en decenas de llamadas. En tu máquina no hay ese
límite: corre de corrido, probablemente 20-50 minutos totales (depende de tu CPU y de
que ahora son 15 países en vez de 12).

## 1. Requisitos

```bash
pip install pandas numpy scipy openpyxl
```

## 2. Archivos en tu carpeta `individuals/`

- `GaR_panel_all17.xlsx` — panel de 17 países (los 15 de antes + MALAYSIA y
  PHILIPPINES), hoja `Panel`, con FCI recalculado en vintage único (ver
  arriba). `GaR_panel_all.xlsx` (15 países, FCI viejo) se deja intacto por si
  necesitás comparar.
- `gar_engine.py` — motor GaR (sin cambios).
- `phase2_gar_panel_all17.py` — driver de ventana expansiva, sin límite de
  tiempo artificial, `OUT_TAG = "all17"`.

## 3. Cómo correr

```bash
cd C:\Users\HOME\Documents\Jloss\GaR\individuals
python phase2_gar_panel_all17.py
```

Progreso por consola, por ejemplo:

```
[95/264] 01/03/2015  n_train=428  paises=13  OK  (41.2s)
```

## 4. Si se corta a la mitad

Reanuda solo: guarda checkpoint (`_ckpt_all17.csv`) después de cada trimestre. Si se
corta, corré el mismo comando de nuevo.

## 5. Cuándo termina

```
COMPLETO: gar_panel_all17.csv (N filas).
```

## 6. Qué NO está incluido (documentado, no es un bug)

- **RUSSIA, THAILAND**: sin serie OECD/IMF trimestral de `g_GDP` interanual
  verificable (MALAYSIA y PHILIPPINES ya se resolvieron, ver arriba).
- **ARGENTINA, SAUDIARABIA**: sin `Ryr` (bono soberano 10Y), bloqueando el FCI.

## 7. Aproximaciones metodológicas a tener presentes (para la sección de datos del paper)

- **PAKISTAN**: el FCI requiere ~120 meses de historia para el burn-in de
  estandarización. `CPI_PAKISTAN.csv` solo tenía datos mensuales desde 2017. Se
  extendió 2007-2017 con el índice **anual** del World Bank (FRED `DDOE01PKA086NWDB`),
  interpolado a mensual y reescalado por empalme al nivel de la serie existente.
  Aproximación razonable para el burn-in, pero de menor resolución (anual interpolada)
  que el resto de la serie (mensual real).
- **SOUTHAFRICA**: mismo problema pero en `STX` (bursátil). Se extendió 1997-2017 con
  el índice de precios de acciones **mensual** de OECD (FRED `SPASTT01ZAM661N`),
  reescalado por empalme al nivel de la serie diaria existente. Aquí la resolución sí
  es mensual (mejor que Pakistan), pero sigue siendo menor que la serie diaria post-2017.
- **CHINA**: `g_GDP` 1993Q1-2024Q1 viene de OECD (dataflow
  `DF_QNA_EXPENDITURE_GROWTH_OECD`, transformación GY = interanual). Los últimos 8
  trimestres (2024Q2-2026Q1) no estaban disponibles todavía en esa tabla OECD (rezago
  de reporte del desglose por gasto) y se completaron con las cifras oficiales de NBS
  reportadas en prensa — mismo indicador (PIB real interanual), pero fuente secundaria
  para ese tramo final.

Todo esto queda como nota al pie en el propio `GaR_panel_all.xlsx`.

## 8. Siguiente paso

Con `gar_panel_all17.csv`, el paso final del pipeline es el *merge* con `Jloss.dta`
(JLoss ya está completo para MALAYSIA y PHILIPPINES, claves `malasia`/`filipinas`) y
con el EMBI de Bloomberg (`Panel_extended_15paises.csv` ya corrió ese reemplazo) por
`(country, quarter)`, siguiendo el mismo join que hace `build_panel_v2.py`. Avisame
cuando tengas `gar_panel_all17.csv` y hago ese merge final para dejar el panel con
17 países.
