# -*- coding: utf-8 -*-
"""
Robustez: theta con JLoss de malla de perdidas ANCHA [0.01, 0.20].
Requiere que el motor ya haya escrito ../../JLoss_reconstruction/Panel_JLoss_wide.csv
(ver _engine_wide.py; ~40 min). Este script solo hace el splice + la regresion.
Salida -> robustez_widebounds_bbg.csv
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p2_regresiones import fit, row, CTRLS

WIDE = os.path.join(HERE, "..", "..", "JLoss_reconstruction", "Panel_JLoss_wide.csv")

w = pd.read_csv(WIDE)
w["country"] = w["countryname"].str.lower()
w = w[["country", "quarter", "JLoss"]].rename(columns={"JLoss": "JLoss_wide"}).dropna()

p = pd.read_csv(os.path.join(HERE, "Panel_bloomberg.csv"))
m = p.merge(w, on=["country", "quarter"], how="left")
est = m.dropna(subset=["EMBI_cds", "JLoss", "GaR"])
rho = est[["JLoss", "JLoss_wide"]].corr().iloc[0, 1]
ratio = (est["JLoss_wide"] / est["JLoss"]).median()
print(f"cobertura wide: {est['JLoss_wide'].notna().sum()}/{len(est)}  "
      f"corr(base,wide)={rho:.4f}  ratio mediano={ratio:.2f}")

ctr = [c for c in CTRLS if c in p.columns and p[c].notna().sum() > 50]


def prep(df):
    d = df.copy()
    d["GaR_pp"] = d["GaR"] * 100.0
    if "ES" in d:
        d["ES_pp"] = d["ES"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    return d.dropna(subset=["EMBI_cds", "JLoss", "GaR_pp"]).copy()


rows = []
for lbl, jc in [("base [0.01,0.048]", "JLoss"), ("wide [0.01,0.20]", "JLoss_wide")]:
    d = m.copy()
    d["JLoss"] = d[jc]
    d = prep(d)
    for sp, ex in [("M1", []), ("M2", ctr)]:
        mm, _ = fit(d, ex, "dk")
        rr = row(mm, f"{sp} {lbl}")
        rows.append(rr)
        print(f"  {sp} {lbl:18s}  theta={rr['theta']:+.4f}  t={rr['t']:+.2f}  "
              f"p={rr['p']:.3f}  N={rr['N']}")

pd.DataFrame(rows).to_csv(os.path.join(HERE, "robustez_widebounds_bbg.csv"), index=False)
print("\nGuardado: robustez_widebounds_bbg.csv")
