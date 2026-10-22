# -*- coding: utf-8 -*-
"""
p45_macro_preregistrada.py -- pruebas macro preregistradas (4_Redaccion/preregistro_macro.md, commit
f820594, anterior a este script y a los datos).

  Familia primaria (p unilateral del wild bootstrap, Holm sobre tres; "firme" = Holm < 0,05 y mismo signo
  con p unilateral < 0,10 sin cada país):
    R2-H1 doom loop:        ln JLoss_{t-1} x DEBT_{t-4}  > 0
    R2-H2 pecado original:  D_{t-1} x FXDEBT_{t-4}       > 0
    R2-H3 mediano plazo:    beta2 de D4_{t-1} (GaR del crecimiento promedio de t+1..t+4) > 0
  Secundarias: FXDEBT y LCDEBT a la vez; D8; R-H3 con D4; cambios a cuatro trimestres con D4;
  componente idiosincrásico del spread (M5); régimen cambiario flexible (M8); y, como referencia, la
  principal con el GaR dentro de la muestra a un trimestre.

Reutiliza p42 (preparar, centrar, fit, moderacion, unilateral). Salida: bbg/paper_p45_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from scipy import stats

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42

NUM = p32.NUM
GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
MACRO = os.path.join(HERE, "macro_trimestral_bbg.csv")


def num(k, v):
    NUM[k] = float(v)


def gar_alt(f):
    g = pd.read_csv(os.path.join(GARNC, f)); g["country"] = g["country"].str.lower()
    g["_qn"] = pd.PeriodIndex(g["quarter"], freq="Q").year * 4 + pd.PeriodIndex(g["quarter"], freq="Q").quarter
    g["Dalt"] = -g["GaR"] * 100.0
    return g


def con_D(d, f, nombre):
    g = gar_alt(f)
    for k, sfx in ((1, "_l1"), (5, "_l5")):
        d = d.merge(p14.shift(g, "Dalt", k, nombre + sfx), on=["country", "_qn"], how="left")
    return d


def efecto_D(d, col, pref, loo=True):
    x = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", col]).copy()
    x["D_l1"] = x[col]
    x = p42.centrar(x)
    rhs = ["J_c", "T_c", "JxT"]
    m = p42.fit(x, "ln_EMBI", rhs); mc = p42.fit(x, "ln_EMBI", rhs, "pais")
    b = float(m.params["T_c"]); pw = p32.wild(x, "ln_EMBI", rhs, "T_c")
    num(f"{pref}_N", m.nobs); num(f"{pref}_b2", b); num(f"{pref}_b2_p_dk", m.pvalues["T_c"])
    num(f"{pref}_b2_p_pais", mc.pvalues["T_c"]); num(f"{pref}_b2_p_uni", p42.unilateral(pw, b, +1))
    num(f"{pref}_b1", m.params["J_c"]); num(f"{pref}_b3", m.params["JxT"]); num(f"{pref}_b3_p_wild", p32.wild(x, "ln_EMBI", rhs, "JxT"))
    sw = float((x["T_c"] - x.groupby("country")["T_c"].transform("mean")).std()); num(f"{pref}_sd_within", sw)
    if loo:
        ok = 0; bs = []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]
            mcc = p42.fit(xc, "ln_EMBI", rhs); bc = float(mcc.params["T_c"])
            pc = p42.unilateral(p32.wild(xc, "ln_EMBI", rhs, "T_c"), bc, +1)
            ok += int(bc > 0 and pc < 0.10); bs.append(bc)
        num(f"{pref}_loo_ok", ok); num(f"{pref}_loo_n", len(bs)); num(f"{pref}_loo_min", min(bs)); num(f"{pref}_loo_max", max(bs))
    return p42.unilateral(pw, b, +1)


def main():
    d, raw = p42.preparar()
    m = pd.read_csv(MACRO)
    q = pd.PeriodIndex(m["quarter"], freq="Q"); m["_qn"] = q.year * 4 + q.quarter
    for col in ("fxdebt", "lcdebt"):
        d = d.merge(p14.shift(m, col, 4, col.upper() + "_l4"), on=["country", "_qn"], how="left")
    d = d.merge(p14.shift(m, "flexible", 0, "FLEX"), on=["country", "_qn"], how="left")
    d = con_D(d, "gar_insample_h4.csv", "D4")
    d = con_D(d, "gar_insample_h8.csv", "D8")
    d = con_D(d, "gar_insample_base.csv", "D1is")
    out = os.path.join(HERE, "paper_p45_numeros.csv")
    guardar = lambda: pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    # ---------------- familia primaria
    p1 = p42.moderacion(d, "DEBT_l4", "J_c", "r2h1", +1)
    p2 = p42.moderacion(d, "FXDEBT_l4", "T_c", "r2h2", +1)
    p3 = efecto_D(d, "D4_l1", "r2h3")
    ps = sorted([("r2h1", p1), ("r2h2", p2), ("r2h3", p3)], key=lambda z: z[1])
    acum = 0.0
    for r, (k, p) in enumerate(ps):
        acum = max(acum, min(1.0, (3 - r) * p)); num(f"{k}_p_holm", acum)
    for k in ("r2h1", "r2h2", "r2h3"):
        n_loo = NUM.get(f"{k}_loo_n", NUM.get(f"{k}_paises", 13))
        num(f"{k}_firme", float(NUM[f"{k}_p_holm"] < 0.05 and NUM[f"{k}_loo_ok"] == n_loo))
    guardar()
    print(f"  R2-H1 {NUM['r2h1_b']:.4f} (uni {p1:.3f}, Holm {NUM['r2h1_p_holm']:.3f}); R2-H2 {NUM['r2h2_b']:.4f} "
          f"(uni {p2:.3f}, Holm {NUM['r2h2_p_holm']:.3f}); R2-H3 {NUM['r2h3_b2']:.4f} (uni {p3:.3f}, Holm {NUM['r2h3_p_holm']:.3f})", flush=True)
    # ---------------- secundarias
    efecto_D(d, "D1is_l1", "ref_h1is", loo=False)
    efecto_D(d, "D8_l1", "sec_h8", loo=False)
    dd = d.copy(); dd["D_l1"] = dd["D4_l1"]
    p42.moderacion(dd.dropna(subset=["D4_l1"]), "DEBT_l4", "T_c", "sec_rh3_D4", +1, loo=False)
    # FX y LC a la vez
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", "FXDEBT_l4", "LCDEBT_l4"]))
    for c in ("FXDEBT_l4", "LCDEBT_l4"):
        x[c + "_s"] = (x[c] - x[c].mean()) / x[c].std(); x["TxS_" + c] = x["T_c"] * x[c + "_s"]
    rhs = ["J_c", "T_c", "JxT", "FXDEBT_l4_s", "LCDEBT_l4_s", "TxS_FXDEBT_l4", "TxS_LCDEBT_l4"]
    mm = p42.fit(x, "ln_EMBI", rhs)
    a = np.zeros(len(rhs)); a[rhs.index("TxS_FXDEBT_l4")] = 1; a[rhs.index("TxS_LCDEBT_l4")] = -1
    V = mm.cov.loc[rhs, rhs].values; dif = float(a @ mm.params[rhs].values); se = float(np.sqrt(a @ V @ a))
    num("sec_fxlc_N", mm.nobs); num("sec_fxlc_fx", mm.params["TxS_FXDEBT_l4"]); num("sec_fxlc_lc", mm.params["TxS_LCDEBT_l4"])
    num("sec_fxlc_dif", dif); num("sec_fxlc_dif_p_dk", 2 * stats.norm.sf(abs(dif / se)))
    num("sec_fxlc_fx_p_wild", p32.wild(x, "ln_EMBI", rhs, "TxS_FXDEBT_l4"))
    # cambios a cuatro trimestres con D4
    for col, k in (("y4", None),):
        pass
    z = d.copy()
    z = z.merge(p14.shift(raw, "ln_EMBI", 4, "y_l4b"), on=["country", "_qn"], how="left")
    z = z.merge(p14.shift(raw, "ln_JLoss", 5, "J_l5b"), on=["country", "_qn"], how="left")
    z["dy4"] = z["ln_EMBI"] - z["y_l4b"]; z["dJ4"] = z["ln_JLoss_l1"] - z["J_l5b"]; z["dD44"] = z["D4_l1"] - z["D4_l5"]
    z["dD14"] = z["D1is_l1"] - z["D1is_l5"]
    for dcol, lab in (("dD44", "D4"), ("dD14", "D1is")):
        w = z.dropna(subset=["dy4", "dJ4", dcol]).copy()
        mw = p32.pfit(w, "dy4", ["dJ4", dcol], bw=8)
        num(f"sec_cambios_{lab}_b", mw.params[dcol]); num(f"sec_cambios_{lab}_p_dk", mw.pvalues[dcol])
        num(f"sec_cambios_{lab}_p_wild", p32.wild(w, "dy4", ["dJ4", dcol], dcol)); num(f"sec_cambios_{lab}_N", mw.nobs)
    # M5: componente idiosincrásico del spread
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]))
    x["m_y"] = x.groupby("quarter")["ln_EMBI"].transform("mean")
    x["y_idio"] = np.nan
    for c, g in x.groupby("country"):
        X = np.column_stack([np.ones(len(g)), g["m_y"]]); b = np.linalg.lstsq(X, g["ln_EMBI"].values, rcond=None)[0]
        x.loc[g.index, "y_idio"] = g["ln_EMBI"].values - X @ b
        num(f"m5_carga_{c}", b[1])
    from linearmodels.panel import PanelOLS
    mi = PanelOLS.from_formula("y_idio ~ J_c + T_c + JxT + EntityEffects", x.set_index(["country", "t"])).fit(**p14.DK)
    for v in ("J_c", "T_c", "JxT"):
        num(f"m5_{v}", mi.params[v]); num(f"m5_{v}_p_dk", mi.pvalues[v])
        P = p32.wb_prep(x.assign(quarter="0"), "y_idio", ["J_c", "T_c", "JxT"]); num(f"m5_{v}_p_wild", p32.wb_run(P, [v])[0])
    num("m5_share_var_global", 1 - x["y_idio"].var() / x["ln_EMBI"].var())
    # M8: régimen cambiario flexible
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", "FLEX"]))
    x["JxF"] = x["J_c"] * x["FLEX"]; x["TxF"] = x["T_c"] * x["FLEX"]
    rhs = ["J_c", "T_c", "JxT", "FLEX", "JxF", "TxF"]
    mf = p42.fit(x, "ln_EMBI", rhs)
    for v in ("JxF", "TxF", "FLEX"):
        num(f"m8_{v}", mf.params[v]); num(f"m8_{v}_p_dk", mf.pvalues[v]); num(f"m8_{v}_p_wild", p32.wild(x, "ln_EMBI", rhs, v))
    num("m8_N", mf.nobs); num("m8_frac_flexible", x["FLEX"].mean())
    guardar()
    for k, v in NUM.items():
        if "_sin_" not in k and "m5_carga" not in k:
            print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
