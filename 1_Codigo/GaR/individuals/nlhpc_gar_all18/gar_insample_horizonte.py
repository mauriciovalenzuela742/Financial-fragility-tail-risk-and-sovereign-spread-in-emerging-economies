# -*- coding: utf-8 -*-
"""
gar_insample_horizonte.py -- GaR dentro de la muestra a un horizonte de k trimestres (preregistro 2,
4_Redaccion/preregistro_macro.md, commit f820594, mejora M3).

Igual que gar_insample_robustez.py (misma regresión cuantílica de panel con efectos fijos, FCI
ortogonalizado respecto del VIX, 39 cuantiles, una sola estimación con toda la muestra), pero la variable
dependiente es el crecimiento PROMEDIO de los k trimestres siguientes, (g_{t+1} + ... + g_{t+k}) / k, en
lugar del crecimiento del trimestre siguiente. GaR_k es su cuantil 5 %.

Uso:  python gar_insample_horizonte.py GaR_panel_all18.xlsx 4     -> gar_insample_h4.csv
      python gar_insample_horizonte.py GaR_panel_all18.xlsx 8     -> gar_insample_h8.csv
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gar_engine as ge

INDEP = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
N_TAU = 39
PROB = 0.05


def main(xlsx, k):
    t0 = time.time()
    panel = pd.read_excel(xlsx, sheet_name="Panel").dropna(subset=["Country"]).copy()
    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    panel = panel.sort_values(["Country", "_d"])
    g = panel.groupby("Country")["g_GDP"]
    panel["g_fwd"] = sum(g.shift(-j) for j in range(1, k + 1)) / k        # promedio de t+1..t+k
    last = panel["_d"].max().strftime("%d/%m/%Y")
    est_all, orth_vars = ge.preprocess(panel, last, "g_fwd", list(INDEP), list(ORTH_DEP), list(ORTH_IND), 0)
    p_names = list(INDEP) + orth_vars
    est = est_all[est_all[["future_dep_var"] + p_names].notna().all(axis=1)].copy()
    print(f"[h{k}] fit_pfe sobre {len(est)} obs, {est['N_Country'].nunique()} países ...", flush=True)
    c_hat, b_hat, a_hat = ge.fit_pfe(est, p_names, N_TAU)
    taus = np.arange(1, N_TAU + 1) / (N_TAU + 1)
    rows = []
    for _, row in est_all.iterrows():
        c = row["N_Country"]
        xv = row[p_names].values.astype(float)
        if np.isnan(xv).any() or (isinstance(c, float) and np.isnan(c)):
            continue
        Q = c_hat + (xv @ b_hat.T) + a_hat.get(int(c), 0.0)
        d = ge.gar_from_quantiles(Q, taus, PROB)
        q = pd.to_datetime(row["Date"], format="%d/%m/%Y") if isinstance(row["Date"], str) else pd.Timestamp(row["Date"])
        rows.append({"country": str(row["Country"]).lower(), "quarter": f"{q.year}Q{(q.month - 1) // 3 + 1}", "GaR": d["GaR"]})
    out = pd.DataFrame(rows).dropna(subset=["GaR"])
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"gar_insample_h{k}.csv")
    out.to_csv(dst, index=False)
    print(f"[h{k}] escrito {dst} ({len(out)} filas) en {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
