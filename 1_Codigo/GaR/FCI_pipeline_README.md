# Pipeline Índice de Condiciones Financieras (FCI) — Reporte e Instructivo

**Proyecto:** *Fragilidad Bancaria y Riesgos del Crecimiento a la Baja: Cómo la Interacción entre JLoss y GaR Determina el Spread Soberano en Economías en Desarrollo.*

**Componente:** Cálculo del FCI por país (porteo de la cadena CEMLA `fci_*.R` a Python), insumo del pipeline GaR.

---

## 1. Estado y validación

Se portó la cadena FCI de CEMLA (R → Python) en `fci_engine.py`. Es un porteo fiel: con las series reales de referencia de EE.UU., el FCI calculado reproduce la referencia oficial `FCI_MEXICO.csv` con:

- **corr = 0.9995**, **RMSE = 0.016**, medias 0.437 (propio) vs 0.439 (referencia), solapamiento completo (212/212 meses).

El residuo es numérico (interpolación de huecos, redondeo de bordes) y no metodológico. El motor es genérico: `compute_fci(carpeta_pais, "PAÍS", carpeta_US)` sirve para cualquier país con las cuatro series CEMLA.

> **Detalle de integración:** el motor emite fechas de **fin de mes hábil** (p. ej. `2024-03-29`); la referencia usa **fin de mes calendario** (`2024-03-31`). El *merge* del FCI hacia el panel debe hacerse por **año-mes** (o trimestre), nunca por fecha exacta.

---

## 2. Metodología (resumen)

Por país, a partir de series diarias (STX, Ryr, CPI domésticas) y de referencia (Ryr, CPI de EE.UU.), más rEER mensual:

1. **Bloque bursátil** (`get_STX`): índice real `rSTX = STX/CPI`; retorno diario `lnSTX`; estandarización por sd rolling de ~10 años (`tilde`); `VSTX` = media móvil de |retorno estandarizado| (~1 mes); `CMAX` = caída desde el máximo móvil (~2 años).
2. **Bloque tasa** (`get_Ryr_daily`): rendimiento real `rRyr = Ryr − inflación interanual`; `VRyr` análogo a `VSTX`; spread real vs EE.UU. `chSpread = rRyr − rRbs`; `CDIFF` = desviación sobre el mínimo móvil.
3. **Colapso a fin de mes** de `VSTX, CMAX, VRyr, CDIFF`.
4. **Bloque rEER** (mensual, `get_rEER`): `VEER` (cambio mensual estandarizado) y `CUMUL` (movimiento acumulado semestral).
5. **Estandarización expansiva** `method_b_max` (escala por máximo móvil, `timeFrame=120`) de las seis columnas.
6. **Subíndices**: $i_{STX}=(VSTX+CMAX)/2$, $i_{Ryr}=(VRyr+CDIFF)/2$, $i_{EER}=(VEER+CUMUL)/2$.
7. **Correlaciones EWMA** ($\lambda=0.85$) entre subíndices.
8. **FCI = forma cuadrática** $FCI_t = I_t' \, C_t \, I_t$, con $I=(i_{STX},i_{Ryr},i_{EER})$ y $C$ la matriz de correlaciones EWMA. Captura el **estrés financiero sistémico**, ponderando la co-movilidad de los mercados. Mayor FCI = condiciones más estresadas.

Parámetros (defaults CEMLA, en `fci_engine.py`): `LAG_TILDE=2599`, `LAG_PERIOD=20`, `LAG_WINDOW=520`, `LAG_YEAR=261`, `LAG_TILDE_M=119`, `LAG_WINDOW_M=6`, `TIME_FRAME=120`, `LAMBDA=0.85`, `method_b_max`.

---

## 3. Datos requeridos (por país + referencia EE.UU.)

| Archivo | Contenido | Formato fecha | Frecuencia |
|---|---|---|---|
| `CPI_<PAÍS>.csv` | Índice de precios al consumidor | `DD/MM/YYYY` | diaria/mensual |
| `Ryr_<PAÍS>.csv` | Rendimiento soberano 10Y | `DD/MM/YYYY` | diaria |
| `STX_<PAÍS>.csv` | Índice bursátil | `DD/MM/YYYY` | diaria |
| `rEER_<PAÍS>.csv` | Tipo de cambio real efectivo | `YYYYMM` | mensual |
| `CPI_US.csv`, `Ryr_US.csv` | IPC y 10Y de EE.UU. (referencia) | `DD/MM/YYYY` | diaria |

Reglas: dos columnas (`DATES` + columna homónima al prefijo), valor numérico puro, **un solo archivo por prefijo y carpeta**.

---

## 4. INSTRUCTIVO — FCI de un país nuevo (ej. Panamá)

### Paso 1 — Reunir las series
Descargar las cuatro series de Panamá y las dos de EE.UU. en el formato de la Sección 3.

Fuentes típicas: `CPI` → INEC Panamá / IFS; `Ryr` → bonos globales PAN (Investing/Bloomberg); `STX` → BVPSI (Bolsa de Valores de Panamá); `rEER` → BIS / IFS; `CPI_US`/`Ryr_US` → FRED (`CPIAUCSL`, `DGS10`).

### Paso 2 — Organizar carpetas
```
C:\GaR\individuals\PANAMA\  → CPI_PANAMA.csv, Ryr_PANAMA.csv, STX_PANAMA.csv, rEER_PANAMA.csv
C:\GaR\individuals\US\      → CPI_US.csv, Ryr_US.csv
```

### Paso 3 — Dependencias
```
pip install numpy pandas
```

### Paso 4 — Ejecutar
```python
from fci_engine import compute_fci
fci = compute_fci(r'C:\GaR\individuals\PANAMA', 'PANAMA',
                  r'C:\GaR\individuals\US',
                  initial='1990-01-01', final='2026-03-31')
fci.to_csv('FCI_PANAMA.csv', index=False)   # columnas: DATES, country, iSTX, iRyr, iEER, FCI
```

### Paso 5 — Integrar al panel GaR
Agregar la columna `FCI` al `GaR_panel.xlsx` (junto con `g_GDP` y `VIX` de Panamá), haciendo el *merge* **por año-mes → trimestre**. Luego correr `phase2_gar_panel.py`.

**Caveats Panamá:** economía **dolarizada** (el rendimiento real y el spread vs EE.UU. son directamente interpretables) y mercado bursátil delgado (BVP), que puede inducir ruido en el bloque `STX`. Documentar como limitación de datos.

---

## 5. INSTRUCTIVO — Actualizar los 5 países a inicios de 2026

Sin cambios de metodología; solo refrescar insumos y extender la ventana:

1. **Re-descargar** las cuatro series CEMLA de Brasil, Chile, Colombia, México y Perú **hasta el último dato de 2026** (idealmente 2026Q1), más `CPI_US`/`Ryr_US` actualizados. Mantener formato/encabezados.
2. **Sobrescribir** los CSV en cada `individuals/<PAÍS>/` (un archivo por prefijo).
3. **Re-calcular** el FCI con `final='2026-03-31'`:
   ```python
   from fci_engine import compute_fci
   for c in ['BRAZIL','CHILE','COLOMBIA','MEXICO','PERU']:
       compute_fci(fr'C:\GaR\individuals\{c}', c, r'C:\GaR\individuals\US',
                   final='2026-03-31').to_csv(f'FCI_{c}.csv', index=False)
   ```
   > La estandarización `method_b_max` y la correlación EWMA son **expansivas**: extender la muestra no altera el pasado salvo por el reescalado natural del máximo móvil. Si el máximo histórico se actualiza con un dato nuevo extremo, documentarlo.
4. **Reconstruir** `GaR_panel.xlsx` con los FCI extendidos + `g_GDP` y `VIX` hasta 2026Q1.
5. **Re-ejecutar** `phase2_gar_panel.py`. El GaR en ventana expansiva incorpora los nuevos trimestres sin tocar los previos.

---

## 6. Salida del motor (`FCI_<PAÍS>.csv`)

| Columna | Significado |
|---|---|
| `DATES` | Fin de mes hábil. |
| `country` | País. |
| `iSTX`, `iRyr`, `iEER` | Subíndices de estrés (bursátil, tasa, cambiario), en [0,1]. |
| `FCI` | Índice de condiciones financieras (forma cuadrática; mayor = más estrés). |

---

## 7. Referencias
- Ossandon Busch et al. (2022). *Growth at Risk: methodology and applications in an open-source platform* (CEMLA C-GARP). Latin American Journal of Central Banking.
- Duprey, T. (2019). *Cross-country comparison of financial stress*. (base de `method_a_cdf`).
