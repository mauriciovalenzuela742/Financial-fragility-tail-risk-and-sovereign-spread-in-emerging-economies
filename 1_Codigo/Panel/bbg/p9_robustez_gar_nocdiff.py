# -*- coding: utf-8 -*-
"""
p9_robustez_gar_nocdiff.py -- robustez de endogeneidad Ryr <-> EMBI.

Re-estima θ / β₃ (muestra completa + interacción de crisis Backstop/EMstress)
sobre 3 versiones del GaR:
  (a) oficial        -- gar_panel_all18.csv (ventana expansiva, con CDIFF)
  (b) in-sample base -- gar_insample_base.csv (un ajuste, con CDIFF)
  (c) in-sample noCDIFF -- gar_insample_noCDIFF.csv (un ajuste, SIN CDIFF)

(b) vs (c) es la comparación apples-to-apples que aísla el efecto de CDIFF;
(a) vs (b) mide el efecto de ir a in-sample.

Salida -> bbg/robustez_gar_nocdiff.csv
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")

CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]
GFC = ["2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4"]
COVID = ["2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"]
EM1516 = ["2015Q3", "2015Q4", "2016Q1"]
BACKSTOP = GFC + COVID


def base_panel():
    d = pd.read_csv(PANEL_CSV)
    d = d.dropna(subset=["EMBI_bps", "JLoss"]).copy()
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


def with_gar(d, gar_series):
    """gar_series: DataFrame country,quarter,GaR (fracción)."""
    g = gar_series.rename(columns={"GaR": "GaR_alt"})[["country", "quarter", "GaR_alt"]]
    m = d.drop(columns=[c for c in ("GaR",) if c in d]).merge(g, on=["country", "quarter"], how="inner")
    m = m.dropna(subset=["GaR_alt"]).copy()
    m["GaR_pp"] = m["GaR_alt"] * 100
    m["D_pp"] = -m["GaR_pp"]
    return m


def fit_m2(d):
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"] + ctr).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    f = ("EMBI_bps ~ JLoss_c + D_c + JxD + " + " + ".join(ctr)
         + " + EntityEffects + TimeEffects")
    m = PanelOLS.from_formula(f, dd.set_index(["country", "t"])).fit(
        cov_type="kernel", kernel="bartlett")
    return dict(N=int(m.nobs), b3=m.params["JxD"], t3=m.tstats["JxD"], p3=m.pvalues["JxD"],
                b1=m.params["JLoss_c"], bD=m.params["D_c"])


def fit_crisis(d):
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"] + ctr).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    for nm, qs in (("bk", BACKSTOP), ("em", EM1516)):
        cr = dd["quarter"].isin(qs).astype(float)
        dd[f"JxD_{nm}"], dd[f"JLoss_{nm}"], dd[f"D_{nm}"] = dd["JxD"] * cr, dd["JLoss_c"] * cr, dd["D_c"] * cr
    rhs = ["JLoss_c", "D_c", "JxD", "JxD_bk", "JLoss_bk", "D_bk", "JxD_em", "JLoss_em", "D_em"] + ctr
    f = "EMBI_bps ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, dd.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
    V = m.cov
    out = dict(N=int(m.nobs), b3=m.params["JxD"], t3=m.tstats["JxD"], p3=m.pvalues["JxD"])
    for nm in ("bk", "em"):
        b = float(m.params["JxD"] + m.params[f"JxD_{nm}"])
        se = float(np.sqrt(V.loc["JxD", "JxD"] + V.loc[f"JxD_{nm}", f"JxD_{nm}"] + 2 * V.loc["JxD", f"JxD_{nm}"]))
        out[f"b4_{nm}"] = m.params[f"JxD_{nm}"]
        out[f"sum_{nm}"] = b
        out[f"sum_{nm}_p"] = 2 * (1 - stats.norm.cdf(abs(b / se)))
    return out


def main():
    d = base_panel()
    gars = {
        "GaR oficial (expansiva, con CDIFF)":
            pd.read_csv(os.path.join(os.path.dirname(HERE), "gar_panel_all18.csv")),
        "GaR in-sample base (con CDIFF)":
            pd.read_csv(os.path.join(GARNC, "gar_insample_base.csv")),
        "GaR in-sample SIN CDIFF":
            pd.read_csv(os.path.join(GARNC, "gar_insample_noCDIFF.csv")),
    }
    rows = []
    for lbl, g in gars.items():
        g["country"] = g["country"].str.lower()
        dm = with_gar(d, g)
        m2 = fit_m2(dm)
        cr = fit_crisis(dm)
        print(f"\n=== {lbl} ===  (N muestra completa = {m2['N']})")
        print(f"  M2 muestra completa: β₃ = {m2['b3']:+.3f}  (t={m2['t3']:+.2f}, p={m2['p3']:.3f})   "
              f"β₁={m2['b1']:+.2f}  coef(D)={m2['bD']:+.2f}")
        print(f"  Crisis (N={cr['N']}): β₃ fuera = {cr['b3']:+.3f} (t={cr['t3']:+.2f})  |  "
              f"Backstop β₄={cr['b4_bk']:+.3f}, β₃+β₄={cr['sum_bk']:+.3f} (Wald p={cr['sum_bk_p']:.3f})  |  "
              f"EMstress β₄={cr['b4_em']:+.3f}, β₃+β₄={cr['sum_em']:+.3f} (Wald p={cr['sum_em_p']:.3f})")
        rows.append(dict(gar=lbl, **{f"m2_{k}": v for k, v in m2.items()},
                         **{f"cr_{k}": v for k, v in cr.items()}))
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "robustez_gar_nocdiff.csv"), index=False)
    print("\nGuardado: bbg/robustez_gar_nocdiff.csv")


if __name__ == "__main__":
    main()
