#!/bin/bash
# ==============================================================================
# run_gar_all18.sbatch -- motor GaR pooled (18 paises, incluye Rusia) en NLHPC.
#
# Reanuda desde _ckpt_all18.csv (63 trimestres ya hechos, hasta 2018Q2). Al
# terminar deja gar_panel_all18.csv en este mismo directorio.
#
# EDITAR antes de enviar: la linea --account (codigo de proyecto NLHPC) y,
# si hace falta, la particion y el modulo de Python.
#
# Enviar:   sbatch run_gar_all18.sbatch
# Ver cola: squeue -u $USER
# Log:      gar_all18_<jobid>.out
# ==============================================================================
#SBATCH --job-name=gar_all18
#SBATCH --partition=general           # o 'slims' / 'largemem' segun disponibilidad
#SBATCH --account=TU_CODIGO_NLHPC     # <<< REEMPLAZAR (p.ej. nlhpcXXXX)
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G                     # el programa lineal de los trimestres recientes es lo pesado
#SBATCH --time=24:00:00               # sobra; si corta por walltime, reenviar y sigue del checkpoint
#SBATCH --output=gar_all18_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=maosvalenzuela@gmail.com

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "Nodo: $(hostname) | inicio: $(date)"
echo "Trimestres ya en checkpoint: $(( $(wc -l < _ckpt_all18.csv) - 1 )) filas"

# --- Entorno Python -----------------------------------------------------------
# Opcion A (recomendada): venv propio con pip. Solo la primera vez.
module purge 2>/dev/null || true
module load Python/3.10.8 2>/dev/null || module load Python 2>/dev/null || true

if [ ! -d venv_gar ]; then
    python3 -m venv venv_gar
    ./venv_gar/bin/pip install --quiet --upgrade pip
    ./venv_gar/bin/pip install --quiet -r requirements.txt
fi
PY=./venv_gar/bin/python

echo "Python: $($PY --version) | $($PY -c 'import scipy,numpy,pandas; print(scipy.__version__, numpy.__version__, pandas.__version__)')"

# HiGHS a veces respeta OMP_NUM_THREADS para el LP
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# --- Corrida ----------------------------------------------------------------
$PY phase2_gar_panel_all18.py

echo "fin: $(date)"
if [ -f gar_panel_all18.csv ]; then
    echo "LISTO -> gar_panel_all18.csv ($(( $(wc -l < gar_panel_all18.csv) - 1 )) filas)"
else
    echo "AUN INCOMPLETO -- reenviar este mismo script para continuar desde el checkpoint."
fi
