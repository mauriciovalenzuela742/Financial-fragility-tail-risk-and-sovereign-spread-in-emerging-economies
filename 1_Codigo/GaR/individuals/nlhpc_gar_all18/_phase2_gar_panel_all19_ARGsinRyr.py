# -*- coding: utf-8 -*-
"""
_phase2_gar_panel_all19_ARGsinRyr.py -- EXPLORATORIO, no vigente.

Identico a phase2_gar_panel_all18.py (mismo estimador, mismos hiperparametros:
N_TAU=39, H=1, MIN_TRAIN_OBS=40, METHOD='both'), corriendo sobre
GaR_panel_all19_ARGsinRyr.xlsx (los 18 paises del pool + ARGENTINA, cuyo FCI
se construyo sin el bloque tasa/Ryr y con la ventana VSTX acortada -- ver
_build_panel_argentina_sinRyr.py y _fci_sin_ryr.py).

No toca phase2_gar_panel_all18.py, GaR_panel_all18.xlsx, ni gar_panel_all18.csv.
Salida propia: gar_panel_all19_ARGsinRyr.csv / _ckpt_all19_ARGsinRyr.csv.
"""
import os
import sys
import time
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
GAR_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GAR_ROOT)
import gar_engine as ge  # noqa: E402

SOURCE_FILE = os.path.join(HERE, "GaR_panel_all19_ARGsinRyr.xlsx")
SHEET = "Panel"
DEPENDENT = "g_GDP"
INDEPENDENT = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1
N_TAU = 39
PROBABILITY = 0.05
MIN_TRAIN_OBS = 40
METHOD = "both"
OUT_TAG = "all19_ARGsinRyr"
OUT_CSV = os.path.join(HERE, f"gar_panel_{OUT_TAG}.csv")
CKPT_CSV = os.path.join(HERE, f"_ckpt_{OUT_TAG}.csv")
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
            print(f"Tiempo agotado ({processed_this_run} fechas nuevas).")
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

    remaining_dates = [d for d in date_strs if d not in done]
    print(f"\nEsta corrida: {processed_this_run} fechas nuevas, {skipped_n} omitidas. "
          f"Pendientes: {len(remaining_dates)}")

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
