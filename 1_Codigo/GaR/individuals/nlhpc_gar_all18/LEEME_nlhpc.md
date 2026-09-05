# Correr el motor GaR (18 países, con Rusia) en NLHPC

La máquina local se queda sin RAM en los trimestres recientes (el programa lineal
de la regresión cuantílica pooled crece con la ventana expansiva). Esta carpeta
tiene todo lo necesario para terminarlo en el cluster.

## Qué hace

`phase2_gar_panel_all18.py` reestima la regresión cuantílica de panel con efectos
fijos compartidos (Koenker 2004, port del pipeline CEMLA) sobre **18 países** —
los 17 de siempre **+ Rusia** (51 trimestres, 2013Q2–2025Q4). Es idéntico al
`phase2_gar_panel_all17.py` salvo la fuente de datos.

Reanuda desde `_ckpt_all18.csv`: **63 trimestres ya están hechos** (hasta 2018Q2),
faltan ~27 (2018Q3–2025Q3), que son los más pesados. Al terminar deja
`gar_panel_all18.csv`.

## Archivos

| archivo | qué es |
|---|---|
| `phase2_gar_panel_all18.py` | driver (ventana expansiva, checkpoint por trimestre) |
| `gar_engine.py` | motor: preprocesamiento, LP del estimador pfe, KDE→GaR, ajuste skew-t |
| `GaR_panel_all18.xlsx` | panel de entrada (Date, Country, N_Country, g_GDP, VIX, FCI) |
| `_ckpt_all18.csv` | progreso parcial de la corrida local (63 trimestres) |
| `requirements.txt` | numpy, scipy, pandas, openpyxl |
| `run_gar_all18.sbatch` | script SLURM |

## Pasos

### 1. Subir la carpeta

```bash
# desde tu máquina, en 1_Codigo/GaR/individuals/
scp -r nlhpc_gar_all18 TU_USUARIO@leftraru.nlhpc.cl:~/
```

### 2. Editar el sbatch

En `run_gar_all18.sbatch`, reemplazar:
- `--account=TU_CODIGO_NLHPC` → tu código de proyecto (lo ves con `sacctmgr show assoc user=$USER format=account`)
- si `general` está saturada o el módulo `Python/3.10.8` no existe, ajustar
  `--partition` y la línea `module load` (ver `ml avail Python`)

### 3. Enviar

```bash
cd ~/nlhpc_gar_all18
sbatch run_gar_all18.sbatch
squeue -u $USER            # ver estado
tail -f gar_all18_*.out    # ver progreso: una línea "[i/N] dd/mm/aaaa ... OK" por trimestre
```

La primera vez arma un venv con pip (1–2 min). Después corre el motor. Estimado:
**2–6 h** según nodo. Si corta por walltime, `sbatch` de nuevo el mismo script y
sigue desde donde quedó.

### 4. Traer el resultado

```bash
# desde tu máquina
scp TU_USUARIO@leftraru.nlhpc.cl:~/nlhpc_gar_all18/gar_panel_all18.csv \
    1_Codigo/Panel/gar_panel_all18.csv
```

Avisame cuando lo tengas y sigo con: re-cablear `p1_build_panels.py`, re-correr
`p0`–`p8`, y actualizar la batería / tesis / artifact con los números nuevos.

## Nota sobre la cobertura de Rusia

Rusia tendrá GaR ~2013Q3–2025Q3. Pero su CDS en el panel actual solo llega hasta
**2015Q4** (14 trimestres), y no tiene EMBI Global Diversified. La intersección
efectiva CDS+JLoss+GaR para Rusia serán ~10–13 trimestres — entra a la muestra de
robustez (DV = CDS), no a la principal (DV = EMBI). Si conseguís CDS de Rusia más
reciente de Bloomberg, se amplía.

## Opcional: terminar en minutos con un array job

Los trimestres son independientes entre sí (cada uno usa solo datos ≤ su fecha).
Si querés paralelizar en vez de esperar la corrida secuencial, avisame y te armo
la variante `--array` (un trimestre por tarea + merge).
