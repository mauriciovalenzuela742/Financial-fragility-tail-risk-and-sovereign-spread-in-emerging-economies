#!/bin/bash
# ==============================================================================
# run_boot_gar_nlhpc.sbatch -- bootstrap de regresor generado del GaR (punto C1
# del plan de arbitro), fidelidad completa (n_tau=39, B=500).
#
# SOLO la primera etapa (remuestreo + regresion cuantilica de panel) corre
# aqui -- no requiere linearmodels, solo numpy/scipy/pandas/openpyxl, que ya
# estan en venv_gar/. La segunda etapa (beta3/beta4 por replica) es trivial en
# tiempo/memoria y se corre LOCAL sobre el resultado:
#     python 1_Codigo/Panel/bbg/p10_boot_gar.py segunda_etapa gar_replicas_nlhpc.csv
#
# Reanuda desde gar_replicas_nlhpc.csv (una replica se considera terminada si
# su `seed` ya aparece en el archivo). El venv (venv_gar/) ya esta creado con:
# numpy scipy pandas openpyxl.
#
# Enviar:   cd ~/nlhpc_gar_all18nc && sbatch run_boot_gar_nlhpc.sbatch
# Cola:     squeue -u $USER
# Log:      gar_boot_<jobid>.out
# Si corta por walltime: reenviar el mismo script, sigue del checkpoint.
# ==============================================================================
#SBATCH --job-name=gar_boot
#SBATCH --partition=main
#SBATCH --account=users
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=gar_boot_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=maosvalenzuela@gmail.com

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "Nodo: $(hostname) | inicio: $(date)"
[ -f gar_replicas_nlhpc.csv ] && echo "Checkpoint: $(( $(wc -l < gar_replicas_nlhpc.csv) - 1 )) filas (pais-trimestre-replica)" || echo "Sin checkpoint (primera corrida)"

module load python/3.12.3-legacy-skylake     # provee libiomp5 que necesita el interprete del venv
PY=./venv_gar/bin/python
$PY --version
$PY -c 'import scipy,numpy,pandas; print("scipy",scipy.__version__,"numpy",numpy.__version__,"pandas",pandas.__version__)'

export OMP_NUM_THREADS=1   # el paralelismo es a nivel de replica (8 workers), no dentro de HiGHS

# B=500 workers=8 (matching --cpus-per-task). Editar aqui si se quiere mas/menos.
$PY p10_boot_gar_nlhpc.py boot 500 8

echo "fin: $(date)"
if [ -f gar_replicas_nlhpc.csv ]; then
    n=$(( $(wc -l < gar_replicas_nlhpc.csv) - 1 ))
    echo "gar_replicas_nlhpc.csv: $n filas"
else
    echo "AUN INCOMPLETO -- reenviar este script para continuar desde el checkpoint."
fi
