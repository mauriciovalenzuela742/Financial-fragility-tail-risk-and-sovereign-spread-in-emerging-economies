#!/bin/bash
# ==============================================================================
# run_gar_all18.sbatch -- motor GaR pooled (18 paises, incluye Rusia) en NLHPC.
#
# Reanuda desde _ckpt_all18.csv. Al terminar deja gar_panel_all18.csv aca mismo.
# El venv (venv_gar/) ya esta creado con: numpy scipy pandas openpyxl.
#
# Enviar:   cd ~/nlhpc_gar_all18 && sbatch run_gar_all18.sbatch
# Cola:     squeue -u $USER
# Log:      gar_all18_<jobid>.out
# Si corta por walltime: reenviar el mismo script, sigue del checkpoint.
# ==============================================================================
#SBATCH --job-name=gar_all18
#SBATCH --partition=main
#SBATCH --account=users
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=gar_all18_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=maosvalenzuela@gmail.com

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "Nodo: $(hostname) | inicio: $(date)"
echo "Trimestres en checkpoint al arrancar: $(( $(wc -l < _ckpt_all18.csv) - 1 )) filas"

module load python/3.12.3-legacy-skylake     # provee libiomp5 que necesita el interprete del venv
PY=./venv_gar/bin/python
$PY --version
$PY -c 'import scipy,numpy,pandas; print("scipy",scipy.__version__,"numpy",numpy.__version__,"pandas",pandas.__version__)'

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

$PY phase2_gar_panel_all18.py

echo "fin: $(date)"
if [ -f gar_panel_all18.csv ]; then
    echo "LISTO -> gar_panel_all18.csv ($(( $(wc -l < gar_panel_all18.csv) - 1 )) filas)"
else
    echo "AUN INCOMPLETO -- reenviar este script para continuar desde el checkpoint."
fi
