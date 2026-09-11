# -*- coding: utf-8 -*-
"""
p9_crisis_interaccion.py -- la complementariedad JLoss x D dentro y fuera de crisis,
SIN botar trimestres (indicacion del profesor coguia).

En vez de la submuestra "sin crisis" (p8, Panel B), se mantiene toda la muestra y se
interactua la complementariedad con un vector de crisis:

  Spread_it = a_i + g_t
            + b1*JLoss_it + b2*D_it
            + b3*(JLoss x D)_it
            + b4*(JLoss x D x Crisis)_it
            + b5*(JLoss x Crisis)_it + b6*(D x Crisis)_it
            + [w'X_it] + e_it            (Crisis solo -> absorbido por g_t)

  b3        = complementariedad fuera de crisis
  b3 + b4   = complementariedad en crisis
  Prediccion del coguia: b4 ~ -b3  =>  b3 + b4 ~ 0  (los respaldos oficiales
  desacoplan el canal domestico en crisis).

Convencion: D = -GaR (pp). b3 = coef(JLoss_c x D_c) = -theta.

Vector de crisis: GFC (2008Q4-2009Q4) + COVID (2020Q1-2021Q4) + estres EM (2015Q3-2016Q1).
Companion: descomposicion en Backstop (GFC+COVID, con respaldos) vs EMstress (2015-16,
sin respaldos) -- test de falsacion del mecanismo.

Salida -> bbg/crisis_interaccion_bbg.csv
"""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

from p2_regresiones import prep, CTRLS, GLOB  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

GFC = ["2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4"]
COVID = ["2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"]
EM1516 = ["2015Q3", "2015Q4", "2016Q1"]            # estres EM 2015-16 (ajustable)
CRISIS_Q = GFC + COVID + EM1516
BACKSTOP_Q = GFC + COVID                            # crisis con respaldo oficial masivo


def _fit(dd, dummies, extra_rhs, fe, cov="dk"):
    """
    dd: panel ya con D_pp. dummies: dict nombre->lista de quarters (cada uno genera
    su bloque X_c*dummy, (D_c)*dummy, (JLoss_c x D_c)*dummy).
    Devuelve el modelo + el DataFrame usado.
    """
    dd = dd.dropna(subset=["_DV", "JLoss", "D_pp"] + extra_rhs).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    rhs = ["JLoss_c", "D_c", "JxD"]
    for nm, qs in dummies.items():
        cr = dd["quarter"].isin(qs).astype(float)
        dd[f"JxD_{nm}"] = dd["JxD"] * cr
        dd[f"JLoss_{nm}"] = dd["JLoss_c"] * cr
        dd[f"D_{nm}"] = dd["D_c"] * cr
        rhs += [f"JxD_{nm}", f"JLoss_{nm}", f"D_{nm}"]
    rhs += extra_rhs
    eff = {"T": "TimeEffects", "P": "EntityEffects",
           "PT": "EntityEffects + TimeEffects"}[fe]
    f = f"_DV ~ {' + '.join(rhs)} + {eff}"
    md = dd.set_index(["country", "t"])
    kw = (dict(cov_type="kernel", kernel="bartlett") if cov == "dk"
          else dict(cov_type="clustered", cluster_entity=True))
    m = PanelOLS.from_formula(f, md).fit(**kw)
    return m, dd


def _lincom(m, names):
    """coef y se de la suma de varios parametros (delta method)."""
    b = float(sum(m.params[n] for n in names))
    V = m.cov
    var = 0.0
    for i in names:
        for j in names:
            var += float(V.loc[i, j])
    se = np.sqrt(var)
    t = b / se
    p = 2 * (1 - stats.norm.cdf(abs(t)))
    return b, se, t, p


def _get(m, n):
    return (dict(b=float(m.params[n]), se=float(m.std_errors[n]),
                 t=float(m.tstats[n]), p=float(m.pvalues[n]))
            if n in m.params.index else dict(b=np.nan, se=np.nan, t=np.nan, p=np.nan))


def run():
    d = prep()
    d["D_pp"] = -d["GaR_pp"]
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]

    n_cr = d["quarter"].isin(CRISIS_Q).sum()
    print(f"Panel: {len(d)} obs, {d['country'].nunique()} paises, "
          f"{d['quarter'].min()}..{d['quarter'].max()}")
    print(f"Crisis=1 en {n_cr} obs ({100*n_cr/len(d):.0f}%): "
          f"GFC {d['quarter'].isin(GFC).sum()}, COVID {d['quarter'].isin(COVID).sum()}, "
          f"EM15-16 {d['quarter'].isin(EM1516).sum()}\n")

    rows = []
    grids = [
        ("vector unico", {"cr": CRISIS_Q}),
        ("Backstop vs EMstress", {"bk": BACKSTOP_Q, "em": EM1516}),
    ]
    for gname, dummies in grids:
        for ctrl_lbl, ex in (("sin controles", []), ("+6 controles", ctr)):
            for fe in ("T", "P", "PT"):
                m, dd = _fit(d, dummies, ex, fe)
                b3 = _get(m, "JxD")
                rec = dict(grid=gname, controles=ctrl_lbl, fe=fe,
                           N=int(m.nobs), paises=int(m.entity_info.total),
                           R2w=round(float(m.rsquared_within), 3),
                           b3=b3["b"], b3_se=b3["se"], b3_t=b3["t"], b3_p=b3["p"])
                for nm in dummies:
                    b4 = _get(m, f"JxD_{nm}")
                    s_b, s_se, s_t, s_p = _lincom(m, ["JxD", f"JxD_{nm}"])
                    rec[f"b4_{nm}"] = b4["b"]; rec[f"b4_{nm}_se"] = b4["se"]
                    rec[f"b4_{nm}_t"] = b4["t"]; rec[f"b4_{nm}_p"] = b4["p"]
                    rec[f"b3_plus_b4_{nm}"] = s_b
                    rec[f"b3_plus_b4_{nm}_se"] = s_se
                    rec[f"b3_plus_b4_{nm}_p"] = s_p           # Wald H0: b3+b4 = 0
                    rec[f"JLoss_{nm}"] = _get(m, f"JLoss_{nm}")["b"]
                    rec[f"D_{nm}"] = _get(m, f"D_{nm}")["b"]
                rows.append(rec)
                # consola
                head = f"[{gname:22s} | {ctrl_lbl:13s} | FE {fe:2s}] N={rec['N']}"
                print(head)
                print(f"    b3 (fuera de crisis)      = {b3['b']:+.3f}  "
                      f"(t={b3['t']:+.2f}, p={b3['p']:.3f})")
                for nm in dummies:
                    lbl = {"cr": "Crisis", "bk": "Backstop", "em": "EMstress"}[nm]
                    print(f"    b4 x {lbl:9s}            = {rec['b4_'+nm]:+.3f}  "
                          f"(t={rec['b4_'+nm+'_t']:+.2f}, p={rec['b4_'+nm+'_p']:.3f})")
                    print(f"    b3 + b4 ({lbl})           = {rec['b3_plus_b4_'+nm]:+.3f}  "
                          f"(Wald p [H0: =0] = {rec['b3_plus_b4_'+nm+'_p']:.3f})")
                print()

    df = pd.DataFrame(rows)
    out = os.path.join(HERE, "crisis_interaccion_bbg.csv")
    df.to_csv(out, index=False)
    print(f"Guardado: {out}")
    return df


if __name__ == "__main__":
    run()
