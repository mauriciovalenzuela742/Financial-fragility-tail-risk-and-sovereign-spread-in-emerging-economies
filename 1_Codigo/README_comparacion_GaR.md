# Comparación del GaR vs métricas de riesgo públicas

Contrasta la serie **GaR** (métrica oficial, 17 economías, hasta 2026Q1) contra métricas de
predicción de riesgo **públicas e independientes**, en nivel y en variación. Se coloca en
`1_Codigo/` y lee los datos directamente de la subcarpeta `./Panel`.

## Qué compara

| Métrica | Tipo | Fuente | Signo esperado vs GaR |
|---|---|---|---|
| `VIX` | global | `Panel/VIX_History.csv` | negativo |
| `US_HY_spread` | global | `Panel/global_controls_quarterly.csv` | negativo |
| `SRISK_world` | global | `vlab-srisk-all-20260728.csv` (NYU V-Lab) | negativo |
| `OFR_FSI`, `OFR_FSI_EM` | global | OFR (`--download`) | negativo |
| `EM_OAS` | global | FRED `BAMLEMCBPIOAS` (`--download`) | negativo |

GaR = percentil 5% del crecimiento (mayor = piso más alto = MENOS riesgo); una métrica de
estrés que sube con el riesgo debe correlacionar **negativo** con el GaR.

## Cómo correr (VS Code)

1. Abrir `1_Codigo` en VS Code y abrir la terminal integrada (`Ctrl + ñ`).
2. Instalar dependencias (una vez):

   ```
   pip install -r requirements_comparacion.txt
   ```

3. Correr con lo que ya está en la carpeta (lee los datos de `./Panel`):

   ```
   python comparar_gar_publicas.py --panel Panel --vlab vlab-srisk-all-20260728.csv --out .
   ```

4. (Opcional) Añadir las métricas que se bajan de internet (OFR FSI total + Emerging Markets
   y el EM Corporate OAS de FRED):

   ```
   python comparar_gar_publicas.py --panel Panel --vlab vlab-srisk-all-20260728.csv --download --out .
   ```

## Salidas (en esta carpeta)

- `comparacion_gar_publicas.csv` — correlaciones de nivel y cambio, por país y pooled (within),
  con signo esperado y bandera `ok / REVISAR`.
- `fig_gar_vs_publicas_overlay.png` — GaR vs la métrica mejor cubierta (estandarizadas), por país.
- `fig_gar_vs_publicas_corr.png` — correlación de nivel del GaR con cada métrica, por país.

## Resultado con los datos actuales

- **VIX**: negativa en las 17 economías (pooled within ≈ −0.50).
- **SRISK mundial (V-Lab)**: negativa en las 17 (pooled within ≈ −0.47). Benchmark sistémico
  **externo** al GaR.
- **US_HY_spread**: serie local truncada (~11 trimestres) → ruidosa; usar la completa vía FRED (`--download`).

## Notas

- `--vlab` detecta si el CSV de V-Lab es **global** (una serie, como el archivo actual
  "World Financials - Total SRISK") o **por país** (columna `country` / una columna por economía).
- Fuentes: OFR FSI (financialresearch.gov), FRED (fred.stlouisfed.org), NYU Stern V-Lab
  (vlab.stern.nyu.edu/srisk).
