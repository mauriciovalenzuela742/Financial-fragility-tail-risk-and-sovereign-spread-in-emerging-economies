"""
phase2_gar_panel.py — Driver de ventana expansiva para gar_engine.py.

Recorre cada fecha (trimestre) del panel en orden ascendente y, en cada corte,
re-estima el modelo de regresion cuantilica de panel SOLO con datos <= esa
fecha (sin look-ahead), extrayendo el GaR condicional (h trimestres adelante)
para cada pais. Guarda un checkpoint incremental para poder reanudar si se
interrumpe.

Uso:
    python phase2_gar_panel.py
"""
import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gar_engine as ge

# ----------------------------- Configuracion ---------------------------------
# Ruta relativa: correr este script desde la misma carpeta que GaR_panel.xlsx
SOURCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GaR_panel.xlsx")
SHEET = "Panel"
DEPENDENT = "g_GDP"
INDEPENDENT = ("g_GDP", "VIX")   # FCI entra ortogonalizado (ver ORTH_DEP/IND)
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1                             # horizonte (trimestres)
N_TAU = 39                        # grid tau = {0.025,0.05,...,0.975} -> 0.05 exacto
PROBABILITY = 0.05
MIN_TRAIN_OBS = 40                # minimo de observaciones (pais-trimestre) para estimar
METHOD = "quantile"                   # 'quantile' (directo) + skew-t de robustez
OUT_TAG = "latam"
OUT_CSV = f"gar_panel_{OUT_TAG}.csv"
CKPT_CSV = f"_ckpt_{OUT_TAG}.csv"


def min_train_size(panel, selected_date):
    """Cuenta cuantas filas (pais-trimestre) quedarian en el set de entrenamiento
    (future_dep_var + covariables no-NA) para esa fecha de corte, sin correr el LP."""
    est_all, orth_vars = ge.preprocess(panel, selected_date, DEPENDENT,
                                       list(INDEPENDENT), list(ORTH_DEP),
                                       list(ORTH_IND), H)
    p_names = list(INDEPENDENT) + orth_vars
    est = est_all[est_all[["future_dep_var"] + p_names].notna().all(axis=1)]
    return len(est), est["N_Country"].nunique()


def main():
    panel = pd.read_excel(SOURCE_FILE, sheet_name=SHEET)
    panel = panel.dropna(subset=["Country"]).copy()  # descarta filas de nota al pie

    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    all_dates = sorted(panel["_d"].unique())
    date_strs = [d.strftime("%d/%m/%Y") for d in all_dates]

    done = set()
    if os.path.exists(CKPT_CSV):
        prev = pd.read_csv(CKPT_CSV)
        done = set(prev["date"].unique())
        print(f"Checkpoint encontrado: {len(done)} fechas ya procesadas.")
    else:
        prev = pd.DataFrame()

    results = [prev] if len(prev) else []
    skipped_n = 0

    for i, d in enumerate(date_strs, 1):
        if d in done:
            continue
        n_train, n_countries = min_train_size(panel, d)
        if n_train < MIN_TRAIN_OBS:
            skipped_n += 1
            continue
        try:
            out = ge.estimate_at(panel, d, dependent=DEPENDENT,
                                  independent=INDEPENDENT, orth_dep=ORTH_DEP,
                                  orth_ind=ORTH_IND, h=H, n_tau=N_TAU,
                                  probability=PROBABILITY, method=METHOD)
        except Exception as e:
            print(f"  [{d}] ERROR: {e}")
            continue
        out["n_train"] = n_train
        results.append(out)
        # checkpoint incremental
        pd.concat(results, ignore_index=True).to_csv(CKPT_CSV, index=False)
        print(f"[{i}/{len(date_strs)}] {d}  n_train={n_train}  paises={n_countries}  OK")

    if not results:
        print("Sin fechas nuevas para procesar (todo ya esta en el checkpoint).")
        final = prev
    else:
        final = pd.concat(results, ignore_index=True)

    final["_d"] = pd.to_datetime(final["date"], format="%d/%m/%Y")
    final["quarter"] = final["_d"].dt.year.astype(str) + "Q" + \
        final["_d"].dt.quarter.astype(str)
    final = final.drop(columns="_d").sort_values(["country", "date"])
    final.to_csv(OUT_CSV, index=False)
    print(f"\nListo: {OUT_CSV}  ({len(final)} filas, {skipped_n} fechas omitidas por "
          f"muestra insuficiente < {MIN_TRAIN_OBS}).")


if __name__ == "__main__":
    main()
