# -*- coding: utf-8 -*-
"""
_explora_logs_bateria.py -- EXPLORATORIO, no vigente. Replica EXACTA de
p8_bateria_regresiones.py (24 regresiones: 4 modelos anidados x 3 efectos fijos x 2 muestras)
pero con la transformacion log-log de la Ecuacion 18 del Informe de Taller de Tesis I:

    ln(Spread) ~ ln(JLoss) + GaR + ln(JLoss) x GaR + FE

en vez de la especificacion en niveles que usa la tesis vigente (Chari et al. 2024):

    Spread ~ JLoss + D + JLoss x D + FE

Diferencias respecto de p8_bateria_regresiones.py (todo lo demas es identico: mismo panel,
mismos paises, mismas 3 estructuras de FE, mismas 2 muestras, mismos errores DK):
  - DV: ln(EMBI_bps) en vez de EMBI_bps directo. EMBI_bps > 0 siempre en la muestra
    de estimacion, asi que el log esta bien definido.
  - JLoss: ln(JLoss) centrado en vez de JLoss centrado. JLoss > 0 siempre.
  - GaR: se deja en NIVELES (no en logs) -- GaR puede ser negativo (percentil 5% del
    crecimiento), por lo que ln(GaR) no esta definido para gran parte de la muestra. El
    propio Eq. 18 del informe original tampoco logaritma GaR, solo Spread y JLoss.

No se toca p8_bateria_regresiones.py ni bateria_bbg.csv (los canonicos). Salida a
bateria_logs_EXPLORATORIO.csv (no referenciada en la tesis).
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
    assert (d["EMBI_bps"] > 0).all(), "EMBI_bps <= 0 en alguna fila: ln() no definido"
    assert (d["JLoss"] > 0).all(), "JLoss <= 0 en alguna fila: ln() no definido"
    d["ln_EMBI"] = np.log(d["EMBI_bps"])
    d["ln_JLoss"] = np.log(d["JLoss"])
    return d


def fit_one(d, model, fe):
    dd = d.copy()
    jc, gc = dd["ln_JLoss"].mean(), dd["GaR_pp"].mean()
    dd["JLoss_c"] = dd["ln_JLoss"] - jc
    dd["GaR_c"] = dd["GaR_pp"] - gc
    dd["Int"] = dd["JLoss_c"] * dd["GaR_c"]

    rhs = {"M1": ["JLoss_c"],
           "M2": ["GaR_c"],
           "M3": ["JLoss_c", "GaR_c"],
           "M4": ["JLoss_c", "GaR_c", "Int"]}[model]
    eff = {"T": "TimeEffects", "P": "EntityEffects", "PT": "EntityEffects + TimeEffects"}[fe]
    f = f"ln_EMBI ~ {' + '.join(rhs)} + {eff}"
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
    out = os.path.join(HERE, "bateria_logs_EXPLORATORIO.csv")
    df.to_csv(out, index=False)

    fe_lbl = {"T": "tiempo", "P": "pais", "PT": "pais+tiempo"}
    for sname, ds in samples.items():
        print("\n" + "=" * 118)
        print(f"MUESTRA: {sname}   [ln(EMBI) ~ ln(JLoss) + GaR + ln(JLoss) x GaR]")
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
                    line += ("".rjust(11) if np.isnan(v)
                             else f"{v:+.4f}{stars(r[coef]['p'])}".rjust(11))
            print(line)
            line = f"{'  (t)':16s}"
            for model in ("M1", "M2", "M3", "M4"):
                for fe in ("T", "P", "PT"):
                    tv = by[(model, fe)][coef]["t"]
                    line += ("" if np.isnan(tv) else f"({tv:+.1f})").rjust(11)
            print(line)
        line = f"{'R2 within':16s}"
        for model in ("M1", "M2", "M3", "M4"):
            for fe in ("T", "P", "PT"):
                line += f"{by[(model, fe)]['r2w']:.2f}".rjust(11)
        print(line)

    print(f"\nGuardado (exploratorio, no canonico): {out}")
    return df


if __name__ == "__main__":
    run()
