"""
phase2_gar_panel_all15_fciFix.py — Driver de descomposicion: mismos 15 paises
de "all15" (sin MALAYSIA/PHILIPPINES), pero con el FCI recalculado en vintage
unico (el mismo fix que se aplico en GaR_panel_all17.xlsx).

Objetivo: aislar cuanto del corrimiento observado en gar_panel_all17.csv (vs.
gar_panel_all15.csv) se debe al fix de vintage del FCI, y cuanto se debe a
agregar MALAYSIA/PHILIPPINES al pool. Con las tres series (all15 viejo,
all15_fciFix, all17) se puede hacer:

  diff_por_fix_FCI      = all15_fciFix - all15        (mismos 15 paises)
  diff_por_paises_nuevos = all17 - all15_fciFix         (mismos 15 paises,
                                                          FCI ya fijo en ambos)

Identico en todo lo demas (parametros del modelo, checkpointing) a
phase2_gar_panel_all17.py / phase2_gar_panel_all.py.
"""
import os
import sys
import time
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gar_engine as ge

SOURCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GaR_panel_all15_fciFix.xlsx")
SHEET = "Panel"
DEPENDENT = "g_GDP"
INDEPENDENT = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1
N_TAU = 39
PROBABILITY = 0.05
MIN_TRAIN_OBS = 40
METHOD = "quantile"
OUT_TAG = "all15_fciFix"
OUT_CSV = f"gar_panel_{OUT_TAG}.csv"
CKPT_CSV = f"_ckpt_{OUT_TAG}.csv"
TIME_BUDGET_SEC = 10**9


def min_train_size(panel, selected_date):
    est_all, orth_vars = ge.preprocess(panel, selected_date, DEPENDENT,
                                       list(INDEPENDENT), list(ORTH_DEP),
                                       list(ORTH_IND), H)
    p_names = list(INDEPENDENT) + orth_vars
    est = est_all[est_all[["future_dep_var"] + p_names].notna().all(axis=1)]
    return len(est), est["N_Country"].nunique()


def main():
    t0 = time.time()
    panel = pd.read_excel(SOURCE_FILE, sheet_name=SHEET)
    panel = panel.dropna(subset=["Country"]).copy()

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
    processed_this_run = 0

    for i, d in enumerate(date_strs, 1):
        if d in done:
            continue
        if time.time() - t0 > TIME_BUDGET_SEC:
            print(f"Tiempo agotado en esta corrida ({processed_this_run} fechas nuevas). "
                  f"Volver a ejecutar para continuar.")
            break
        n_train, n_countries = min_train_size(panel, d)
        if n_train < MIN_TRAIN_OBS:
            skipped_n += 1
            done.add(d)
            continue
        try:
            out = ge.estimate_at(panel, d, dependent=DEPENDENT,
                                  independent=INDEPENDENT, orth_dep=ORTH_DEP,
                                  orth_ind=ORTH_IND, h=H, n_tau=N_TAU,
                                  probability=PROBABILITY, method=METHOD)
        except Exception as e:
            print(f"  [{d}] ERROR: {e}")
            done.add(d)
            continue
        out["n_train"] = n_train
        results.append(out)
        pd.concat(results, ignore_index=True).to_csv(CKPT_CSV, index=False)
        done.add(d)
        processed_this_run += 1
        print(f"[{i}/{len(date_strs)}] {d}  n_train={n_train}  paises={n_countries}  OK  "
              f"({time.time()-t0:.1f}s)")

    print(f"\nEsta corrida: {processed_this_run} fechas nuevas procesadas, {skipped_n} omitidas "
          f"por muestra insuficiente. Fechas pendientes: {len([d for d in date_strs if d not in done])}")

    remaining_dates = [d for d in date_strs if d not in done]
    if not remaining_dates:
        final = pd.concat(results, ignore_index=True) if results else prev
        final["_d"] = pd.to_datetime(final["date"], format="%d/%m/%Y")
        final["quarter"] = final["_d"].dt.year.astype(str) + "Q" + final["_d"].dt.quarter.astype(str)
        final = final.drop(columns="_d").sort_values(["country", "date"])
        final.to_csv(OUT_CSV, index=False)
        print(f"\nCOMPLETO: {OUT_CSV} ({len(final)} filas).")
    else:
        print("Quedan fechas pendientes. Ejecutar de nuevo para continuar.")


if __name__ == "__main__":
    main()
