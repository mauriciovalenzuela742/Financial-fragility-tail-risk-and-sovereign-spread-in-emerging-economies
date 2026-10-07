# -*- coding: utf-8 -*-
"""
_explora_logs_crisis.py -- EXPLORATORIO, no vigente. Replica EXACTA de
p9b_bateria_crisis.py (24 regresiones: 4 modelos anidados CM1-CM4 x 3 efectos fijos x 2
paneles de crisis) pero con ln(EMBI) y ln(JLoss) en vez de niveles, igual criterio que
_explora_logs_bateria.py. D = -GaR se deja en niveles (no logaritmado: puede ser negativo).

No se toca p9_crisis_interaccion.py ni p9b_bateria_crisis.py ni sus CSV canonicos.
Salida a bateria_crisis_logs_EXPLORATORIO.csv (no referenciada en la tesis).
"""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")
CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]

GFC = ["2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4"]
COVID = ["2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"]
EM1516 = ["2015Q3", "2015Q4", "2016Q1"]
CRISIS_Q = GFC + COVID + EM1516
BACKSTOP_Q = GFC + COVID

PANELS = [
    ("A_vector_unico", {"cr": CRISIS_Q}),
    ("B_backstop_emstress", {"bk": BACKSTOP_Q, "em": EM1516}),
]
FE_MAP = {"T": "TimeEffects", "P": "EntityEffects", "PT": "EntityEffects + TimeEffects"}
MODEL_BASE = {
    "CM1": {"JLoss": "JLoss_c"},
    "CM2": {"D": "D_c"},
    "CM3": {"JLoss": "JLoss_c", "D": "D_c"},
    "CM4": {"JxD": "JxD"},
}


def prep():
    d = pd.read_csv(PANEL_CSV)
    d = d.dropna(subset=["EMBI_bps", "JLoss", "GaR"]).copy()
    d["GaR_pp"] = d["GaR"] * 100.0
    d["D_pp"] = -d["GaR_pp"]
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").astype("int64")
    assert (d["EMBI_bps"] > 0).all() and (d["JLoss"] > 0).all()
    d["_DV"] = np.log(d["EMBI_bps"])
    d["ln_JLoss"] = np.log(d["JLoss"])
    return d


def _lincom(m, names):
    b = float(sum(m.params[n] for n in names))
    V = m.cov
    se = float(np.sqrt(sum(float(V.loc[i, j]) for i in names for j in names)))
    t = b / se
    p = 2 * (1 - stats.norm.cdf(abs(t)))
    return b, se, t, p


def _get(m, n):
    if n in m.params.index:
        return dict(b=float(m.params[n]), se=float(m.std_errors[n]),
                    t=float(m.tstats[n]), p=float(m.pvalues[n]))
    return dict(b=np.nan, se=np.nan, t=np.nan, p=np.nan)


def _build_rhs(model, dummies):
    base = MODEL_BASE[model]
    rhs = {"CM1": ["JLoss_c"], "CM2": ["D_c"], "CM3": ["JLoss_c", "D_c"],
           "CM4": ["JLoss_c", "D_c", "JxD"]}[model]
    for nm in dummies:
        if model == "CM1":
            rhs.append(f"JLoss_{nm}")
        elif model == "CM2":
            rhs.append(f"D_{nm}")
        elif model == "CM3":
            rhs += [f"JLoss_{nm}", f"D_{nm}"]
        elif model == "CM4":
            rhs += [f"JxD_{nm}", f"JLoss_{nm}", f"D_{nm}"]
    return rhs, base


def fit_crisis_model(d, model, dummies, fe, ctr):
    dd = d.dropna(subset=["_DV", "ln_JLoss", "D_pp"] + ctr).copy()
    dd["JLoss_c"] = dd["ln_JLoss"] - dd["ln_JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    for nm, qs in dummies.items():
        cr = dd["quarter"].isin(qs).astype(float)
        dd[f"JxD_{nm}"] = dd["JxD"] * cr
        dd[f"JLoss_{nm}"] = dd["JLoss_c"] * cr
        dd[f"D_{nm}"] = dd["D_c"] * cr

    rhs, base = _build_rhs(model, dummies)
    all_rhs = rhs + ctr
    f = f"_DV ~ {' + '.join(all_rhs)} + {FE_MAP[fe]}"
    md = dd.set_index(["country", "t"])
    m = PanelOLS.from_formula(f, md).fit(cov_type="kernel", kernel="bartlett")
    return m, dd, base


def run():
    d = prep()
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    print(f"Panel: {len(d)} obs, {d['country'].nunique()} paises, controles: {ctr}")
    print("Especificacion: ln(EMBI) ~ ln(JLoss) + D + ln(JLoss) x D + (.) x vector-crisis\n")

    rows = []
    for panel_name, dummies in PANELS:
        for model in ("CM1", "CM2", "CM3", "CM4"):
            for fe in ("T", "P", "PT"):
                m, dd, base = fit_crisis_model(d, model, dummies, fe, ctr)
                rec = dict(panel=panel_name, modelo=model, fe=fe, N=int(m.nobs))
                for coef_name in ("JLoss_c", "D_c", "JxD"):
                    if coef_name in m.params.index:
                        g = _get(m, coef_name)
                        rec[f"{coef_name}_b"] = g["b"]; rec[f"{coef_name}_t"] = g["t"]
                        rec[f"{coef_name}_p"] = g["p"]
                for nm, lbl in (("cr", "Crisis"), ("bk", "Backstop"), ("em", "EMstress")):
                    if nm not in dummies:
                        continue
                    for prefix, base_col in base.items():
                        crisis_col = f"{prefix}_{nm}"
                        if crisis_col in m.params.index:
                            g = _get(m, crisis_col)
                            rec[f"{crisis_col}_b"] = g["b"]; rec[f"{crisis_col}_t"] = g["t"]
                            rec[f"{crisis_col}_p"] = g["p"]
                            sb, sse, st, sp = _lincom(m, [base_col, crisis_col])
                            rec[f"{prefix}_sum_{nm}_b"] = sb
                            rec[f"{prefix}_sum_{nm}_t"] = st
                            rec[f"{prefix}_sum_{nm}_p"] = sp
                rows.append(rec)

                if model == "CM4" and fe == "PT":
                    print(f"[{panel_name:22s} | {model} | FE {fe:2s}] N={rec['N']}")
                    print(f"    JxD (fuera de crisis) = {rec.get('JxD_b', float('nan')):+.4f} "
                          f"(t={rec.get('JxD_t', float('nan')):+.2f}, p={rec.get('JxD_p', float('nan')):.3f})")
                    for nm, lbl in (("cr", "Crisis"), ("bk", "Backstop"), ("em", "EMstress")):
                        if f"JxD_sum_{nm}_b" in rec:
                            print(f"    JxD + JxD_{nm} ({lbl:9s}) = {rec[f'JxD_sum_{nm}_b']:+.4f} "
                                  f"(Wald t={rec[f'JxD_sum_{nm}_t']:+.2f}, p={rec[f'JxD_sum_{nm}_p']:.3f})")
                    print()

    df = pd.DataFrame(rows)
    out = os.path.join(HERE, "bateria_crisis_logs_EXPLORATORIO.csv")
    df.to_csv(out, index=False)
    print(f"Guardado (exploratorio, no canonico): {out}  ({len(df)} filas)")
    return df


if __name__ == "__main__":
    run()
