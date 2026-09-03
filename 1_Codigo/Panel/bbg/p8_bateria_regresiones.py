# -*- coding: utf-8 -*-
"""
p8_bateria_regresiones.py -- bateria "estilo Chari et al." sobre el panel unico
Bloomberg. Es el ESQUELETO de la evidencia empirica del Capitulo 2.

Grilla:  4 modelos  x  3 estructuras de efectos fijos  x  2 muestras  = 24 regresiones.

  Modelos (variable dependiente: EMBI_bps)
    M1  EMBI ~ JLoss
    M2  EMBI ~ GaR
    M3  EMBI ~ JLoss + GaR
    M4  EMBI ~ JLoss + GaR + JLoss x GaR      (interaccion, ambos centrados)

  Efectos fijos
    T   solo tiempo (trimestre)
    P   solo pais
    PT  pais + tiempo (bidireccionales, spec de referencia de la tesis)

  Muestras
    completa
    sin crisis   -- excluye GFC (2008Q4-2009Q4) y COVID (2020Q1-2021Q4)

Errores estandar de Driscoll-Kraay (kernel Bartlett) en todas.
Sin controles domesticos: la tabla mide el mecanismo desnudo; el efecto de anadir
el vector de 6 controles esta en p2_regresiones.py (deja la interaccion intacta).

Salida -> bbg/bateria_bbg.csv   (una fila por regresion, formato largo)
       -> consola: la tabla en formato ancho (rows = coef, cols = spec)
"""
import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")

CRISIS_Q = (
    [f"2008Q{k}" for k in (4,)] + [f"2009Q{k}" for k in (1, 2, 3, 4)]
    + [f"2020Q{k}" for k in (1, 2, 3, 4)] + [f"2021Q{k}" for k in (1, 2, 3, 4)]
)


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def prep():
    d = pd.read_csv(PANEL_CSV)
    d = d.dropna(subset=["EMBI_bps", "JLoss", "GaR"]).copy()
    d["GaR_pp"] = d["GaR"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").astype("int64")
    return d


def fit_one(d, model, fe):
    """Devuelve dict con coeficientes de interes."""
    dd = d.copy()
    jc, gc = dd["JLoss"].mean(), dd["GaR_pp"].mean()
    dd["JLoss_c"] = dd["JLoss"] - jc
    dd["GaR_c"] = dd["GaR_pp"] - gc
    dd["Int"] = dd["JLoss_c"] * dd["GaR_c"]

    rhs = {"M1": ["JLoss_c"],
           "M2": ["GaR_c"],
           "M3": ["JLoss_c", "GaR_c"],
           "M4": ["JLoss_c", "GaR_c", "Int"]}[model]
    eff = {"T": "TimeEffects", "P": "EntityEffects", "PT": "EntityEffects + TimeEffects"}[fe]
    f = f"EMBI_bps ~ {' + '.join(rhs)} + {eff}"
    md = dd.set_index(["country", "t"])
    m = PanelOLS.from_formula(f, md).fit(cov_type="kernel", kernel="bartlett")

    def g(name):
        if name in m.params.index:
            return dict(b=float(m.params[name]), se=float(m.std_errors[name]),
                        t=float(m.tstats[name]), p=float(m.pvalues[name]))
        return dict(b=np.nan, se=np.nan, t=np.nan, p=np.nan)

    return dict(model=model, fe=fe,
                JLoss=g("JLoss_c"), GaR=g("GaR_c"), Int=g("Int"),
                N=int(m.nobs), paises=int(md.reset_index()["country"].nunique()),
                r2=float(m.rsquared), r2w=float(m.rsquared_within))


def run():
    d = prep()
    samples = {"completa": d,
               "sin crisis": d[~d["quarter"].isin(CRISIS_Q)].copy()}
    rows = []
    for sname, ds in samples.items():
        for model in ("M1", "M2", "M3", "M4"):
            for fe in ("T", "P", "PT"):
                r = fit_one(ds, model, fe)
                r["muestra"] = sname
                rows.append(r)

    # ---- CSV largo ----
    flat = []
    for r in rows:
        base = dict(muestra=r["muestra"], modelo=r["model"], efectos_fijos=r["fe"],
                    N=r["N"], paises=r["paises"], R2=round(r["r2"], 3), R2_within=round(r["r2w"], 3))
        for k in ("JLoss", "GaR", "Int"):
            base[f"{k}_b"] = r[k]["b"]
            base[f"{k}_se"] = r[k]["se"]
            base[f"{k}_t"] = r[k]["t"]
            base[f"{k}_p"] = r[k]["p"]
        flat.append(base)
    df = pd.DataFrame(flat)
    df.to_csv(os.path.join(HERE, "bateria_bbg.csv"), index=False)

    # ---- consola: tabla ancha estilo Chari ----
    fe_lbl = {"T": "tiempo", "P": "pais", "PT": "pais+tiempo"}
    for sname, ds in samples.items():
        print("\n" + "=" * 118)
        print(f"MUESTRA: {sname}")
        print("=" * 118)
        hdr = f"{'':16s}"
        for model in ("M1", "M2", "M3", "M4"):
            for fe in ("T", "P", "PT"):
                hdr += f"{model}/{fe:>2s}".rjust(11)
        print(hdr)
        sel = [r for r in rows if r["muestra"] == sname]
        by = {(r["model"], r["fe"]): r for r in sel}
        for coef in ("JLoss", "GaR", "Int"):
            line = f"{coef:16s}"
            for model in ("M1", "M2", "M3", "M4"):
                for fe in ("T", "P", "PT"):
                    r = by[(model, fe)]
                    v = r[coef]["b"]
                    if np.isnan(v):
                        line += "".rjust(11)
                    else:
                        line += f"{v:+.2f}{stars(r[coef]['p'])}".rjust(11)
            print(line)
            line = f"{'  (t)':16s}"
            for model in ("M1", "M2", "M3", "M4"):
                for fe in ("T", "P", "PT"):
                    r = by[(model, fe)]
                    tv = r[coef]["t"]
                    line += ("" if np.isnan(tv) else f"({tv:+.1f})").rjust(11)
            print(line)
        for lab, key in (("N", "N"), ("paises", "paises")):
            line = f"{lab:16s}"
            for model in ("M1", "M2", "M3", "M4"):
                for fe in ("T", "P", "PT"):
                    line += f"{by[(model, fe)][key]}".rjust(11)
            print(line)
        line = f"{'R2 within':16s}"
        for model in ("M1", "M2", "M3", "M4"):
            for fe in ("T", "P", "PT"):
                line += f"{by[(model, fe)]['r2w']:.2f}".rjust(11)
        print(line)

    print("\nGuardado: bateria_bbg.csv")
    return df


if __name__ == "__main__":
    run()
