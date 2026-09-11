# -*- coding: utf-8 -*-
"""
gar_insample_robustez.py -- GaR IN-SAMPLE (no ventana expansiva) para la
robustez de endogeneidad Ryr <-> EMBI.

La serie GaR "oficial" de la tesis es pseudo-tiempo-real (se re-estima en cada
fecha de corte). Esa re-corrida completa sin CDIFF pertenece a NLHPC (~2-4 h).
Como PREVIEW / robustez: se ajusta la regresion cuantilica de panel UNA vez
sobre toda la muestra y se lee el GaR de todas las filas historicas. Se hace
lo mismo con el FCI base y con el FCI sin CDIFF -> comparacion apples-to-apples.

Uso:
  python gar_insample_robustez.py GaR_panel_all18.xlsx           base
  python gar_insample_robustez.py GaR_panel_all18_noCDIFF.xlsx   noCDIFF
Salida: gar_insample_<tag>.csv  (country, quarter, GaR, ES, prob_neg, ...)
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gar_engine as ge

DEP = "g_GDP"
INDEP = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1
N_TAU = 39
PROB = 0.05


def main(xlsx, tag):
    t0 = time.time()
    panel = pd.read_excel(xlsx, sheet_name="Panel")
    panel = panel.dropna(subset=["Country"]).copy()
    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    last = panel["_d"].max().strftime("%d/%m/%Y")

    est_all, orth_vars = ge.preprocess(panel, last, DEP, list(INDEP),
                                       list(ORTH_DEP), list(ORTH_IND), H)
    p_names = list(INDEP) + orth_vars
    est = est_all[est_all[["future_dep_var"] + p_names].notna().all(axis=1)].copy()
    print(f"[{tag}] fit_pfe sobre {len(est)} obs, {est['N_Country'].nunique()} paises, "
          f"hasta {last} ...")
    c_hat, b_hat, a_hat = ge.fit_pfe(est, p_names, N_TAU)
    taus = np.arange(1, N_TAU + 1) / (N_TAU + 1)
    print(f"[{tag}] LP resuelto en {time.time()-t0:.0f}s. b_hat medio (g_GDP, VIX, FCI_res): "
          f"{b_hat.mean(axis=0).round(4)}")

    rows = []
    for _, row in est_all.iterrows():
        c = row["N_Country"]
        xv = row[p_names].values.astype(float)
        d = {"GaR": np.nan}
        if not np.isnan(xv).any() and not (isinstance(c, float) and np.isnan(c)):
            Q = c_hat + (xv @ b_hat.T) + a_hat.get(int(c), 0.0)
            d = ge.gar_from_quantiles(Q, taus, PROB)
        q = pd.Timestamp(row["Date"] if not isinstance(row["Date"], str)
                         else pd.to_datetime(row["Date"], format="%d/%m/%Y"))
        rows.append({"country": str(row["Country"]).lower(),
                     "quarter": f"{q.year}Q{(q.month-1)//3+1}",
                     "GaR": d["GaR"], "ES": d.get("ES"), "prob_neg": d.get("prob_neg"),
                     "std": d.get("std"), "skew": d.get("skew")})
    out = pd.DataFrame(rows).dropna(subset=["GaR"])
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       f"gar_insample_{tag}.csv")
    out.to_csv(dst, index=False)
    print(f"[{tag}] escrito {dst}  ({len(out)} filas)  total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
