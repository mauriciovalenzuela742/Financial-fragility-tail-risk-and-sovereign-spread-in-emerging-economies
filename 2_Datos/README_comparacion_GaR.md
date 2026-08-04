# Comparación del GaR vs métricas de riesgo públicas

Paquete auto-contenido para contrastar la serie **GaR** (métrica oficial, 17 economías,
hasta 2026Q1) contra métricas de predicción de riesgo **públicas e independientes**, en
nivel y en variación. Todo lo necesario está en esta carpeta.

## Qué compara

| Métrica | Tipo | Fuente | Signo esperado vs GaR |
|---|---|---|---|
| `VIX` | global | `VIX_History.csv` (local) | negativo |
| `US_HY_spread` | global | `global_controls_quarterly.csv` (local) | negativo |
| `SRISK_world` | global | `vlab-srisk-all-20260728.csv` (NYU V-Lab) | negativo |
| `OFR_FSI`, `OFR_FSI_EM` | global | OFR (descarga con `--download`) | negativo |
| `EM_OAS` | global | FRED `BAMLEMCBPIOAS` (`--download`) | negativo |

El GaR es el percentil 5% del crecimiento (mayor = piso más alto = MENOS riesgo), por eso
una métrica de estrés que sube con el riesgo debe correlacionar **negativo** con el GaR.

## Cómo correr (VS Code)

1. Abrir esta carpeta en VS Code (`File → Open Folder → Redaccion`).
2. Abrir la terminal integrada (`Ctrl + ñ` o `Terminal → New Terminal`).
3. Instalar dependencias (una sola vez):

   ```
   pip install -r requirements.txt
   ```

4. Correr la comparación con lo que ya está en la carpeta (VIX, US_HY, SRISK de V-Lab):

   ```
   python comparar_gar_publicas.py --panel . --vlab vlab-srisk-all-20260728.csv --out .
   ```

5. (Opcional) Añadir las métricas que se bajan de internet (OFR FSI total + Emerging
   Markets, y el EM Corporate OAS de FRED):

   ```
   python comparar_gar_publicas.py --panel . --vlab vlab-srisk-all-20260728.csv --download --out .
   ```

## Salidas (se generan en esta carpeta)

- `comparacion_gar_publicas.csv` — correlaciones de nivel y de cambio por país y pooled
  (within), con el signo esperado y una bandera `ok / REVISAR`.
- `fig_gar_vs_publicas_overlay.png` — GaR vs la métrica mejor cubierta (estandarizadas),
  por país; se ve el co-movimiento inverso (p. ej. el desplome del GaR en 2020Q2).
- `fig_gar_vs_publicas_corr.png` — correlación de nivel del GaR con cada métrica, por país.

## Resultado con los datos actuales

- **VIX**: correlación negativa en las 17 economías (pooled within ≈ −0.50).
- **SRISK mundial (V-Lab)**: negativa en las 17 (pooled within ≈ −0.47). Benchmark
  sistémico **externo** (no entra en la construcción del GaR).
- **US_HY_spread**: serie local truncada (~11 trimestres) → ruidosa; usar la historia
  completa vía FRED (`--download`).

## Notas

- El `--vlab` detecta automáticamente si el CSV de V-Lab es **global** (una sola serie, como
  el archivo actual "World Financials - Total SRISK") o **por país** (columna `country` o
  una columna por economía).
- El archivo actual de V-Lab es el agregado mundial. Si más adelante bajas SRISK **por país**
  desde las páginas de país de V-Lab, el mismo comando lo cruza economía por economía.
- Fuentes: OFR FSI (financialresearch.gov), FRED (fred.stlouisfed.org), NYU Stern V-Lab
  (vlab.stern.nyu.edu/srisk).
