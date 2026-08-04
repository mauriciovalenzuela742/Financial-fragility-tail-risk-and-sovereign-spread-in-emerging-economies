# -*- coding: utf-8 -*-
"""
run_reg_extended.py
===================
Une los controles macro (controls_panel.csv) al panel base
(Panel_regresion_v2.csv) y corre las especificaciones ampliadas.

Entradas (mismo directorio):
    Panel_regresion_v2.csv   <- panel EMBI x JLoss x GaR (ya construido)
    controls_panel.csv       <- salida de fetch_controls.py

Salidas:
    Panel_regresion_v3.csv          (panel + controles)
    Tabla_resultados_extendida.csv

Convenciones:
  - GaR y ES en puntos porcentuales (x100).
  - JLoss, GaR y la cola se centran -> terminos individuales = efecto en la media.
  - SE Driscoll-Kraay (robustos a dependencia transversal y autocorrelacion).
  - Hipotesis de complementariedad:  theta (JLoss x GaR) < 0.

REQUISITOS: pip install pandas numpy linearmodels
"""

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS

DK = dict(cov_type="kernel", kernel="bartlett")
CONTROLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]


def load():
    p = pd.read_csv("Panel_regresion_v2.csv")
    try:
        c = pd.read_csv("controls_panel.csv")
        p = p.merge(c, on=["country", "quarter"], how="left")
        print("Controles unidos:", [x for x in CONTROLS if x in p.columns])
    except FileNotFoundError:
        print("AVISO: controls_panel.csv no encontrado -> corre sin controles macro.")
    return p


def prep(p):
    p = p.copy()
    p["t"] = pd.PeriodIndex(p["quarter"], freq="Q").to_timestamp()
    p["GaR_pp"] = p["GaR"] * 100
    p["ES_pp"] = p["ES"] * 100
    for v in ["JLoss", "GaR_pp", "ES_pp"]:
        p[v + "_c"] = p[v] - p[v].mean()
    p["JxG_c"] = p["JLoss_c"] * p["GaR_pp_c"]
    p["lnEMBI"] = np.log(p["EMBI_bps"])
    return p


def available_controls(p):
    """Controles presentes y con cobertura util (>=80% no-nulos en la muestra)."""
    out = []
    for c in CONTROLS:
        if c in p.columns and p[c].notna().mean() >= 0.80:
            out.append(c)
    return out


def fit(p, formula, label):
    # filtra filas completas para los regresores usados (evita perder por NaN dispersos)
    pp = p.set_index(["country", "t"])
    r = PanelOLS.from_formula(formula, pp, drop_absorbed=True).fit(**DK)
    print(f"\n{'='*66}\n{label}\n{'='*66}")
    for v in r.params.index:
        st = "***" if r.pvalues[v] < .01 else "**" if r.pvalues[v] < .05 \
            else "*" if r.pvalues[v] < .10 else ""
        print(f"  {v:11s} b={r.params[v]:10.4f}  t={r.tstats[v]:6.2f}  "
              f"p={r.pvalues[v]:.4f} {st}")
    print(f"  N={r.nobs}  R2(overall)={r.rsquared:.3f}")
    return r


def main():
    p = prep(load())
    ctrls = available_controls(p)
    cstr = (" + " + " + ".join(ctrls)) if ctrls else ""
    print("Controles con cobertura >=80%:", ctrls if ctrls else "(ninguno)")

    rows, models = [], {}

    # referencia sin controles
    models["M0"] = fit(
        p, "EMBI_bps ~ JLoss_c + GaR_pp_c + JxG_c + EntityEffects + TimeEffects",
        "M0  FE bidireccional + interaccion (sin controles macro)")

    # ampliada FE bidireccional + controles domesticos
    models["M_FE2"] = fit(
        p, f"EMBI_bps ~ JLoss_c + GaR_pp_c + JxG_c{cstr} + EntityEffects + TimeEffects",
        "M1  FE bidireccional + interaccion + controles macro domesticos")

    # ampliada FE pais + controles + VIX (factor global explicito)
    glob = " + VIX" if "VIX" in p.columns else ""
    models["M_FEpais"] = fit(
        p, f"EMBI_bps ~ JLoss_c + GaR_pp_c + JxG_c{cstr}{glob} + EntityEffects",
        "M2  FE pais + interaccion + controles + VIX")

    # robustez log-spread
    models["M_log"] = fit(
        p, f"lnEMBI ~ JLoss_c + GaR_pp_c + JxG_c{cstr} + EntityEffects + TimeEffects",
        "M3  log-spread (robustez)")

    # exportar tabla
    for n, r in models.items():
        for v in r.params.index:
            rows.append({"modelo": n, "var": v,
                         "coef": round(r.params[v], 4),
                         "se": round(r.std_errors[v], 4),
                         "t": round(r.tstats[v], 2),
                         "p": round(r.pvalues[v], 4)})
        rows.append({"modelo": n, "var": "_N/R2", "coef": int(r.nobs),
                     "se": "", "t": round(r.rsquared, 3), "p": "R2_overall"})
    pd.DataFrame(rows).to_csv("Tabla_resultados_extendida.csv", index=False)

    # efecto marginal de JLoss segun severidad de cola (de M_FE2)
    r = models["M_FE2"]
    b, V = r.params, r.cov
    mu = p["GaR_pp"].mean()
    print("\nEfecto marginal  dEMBI/dJLoss = b_JLoss + theta*(GaR-mu):")
    for qq, lab in [(.10, "cola severa p10"), (.50, "mediana"), (.90, "benigno p90")]:
        g = p["GaR_pp"].quantile(qq)
        me = b["JLoss_c"] + b["JxG_c"] * (g - mu)
        se = np.sqrt(V.loc["JLoss_c", "JLoss_c"]
                     + (g - mu) ** 2 * V.loc["JxG_c", "JxG_c"]
                     + 2 * (g - mu) * V.loc["JLoss_c", "JxG_c"])
        print(f"  GaR={g:+6.2f}pp ({lab:15s}) -> {me:5.2f} pb  (t={me/se:4.2f})")

    # guardar panel ampliado
    keep = ["country", "quarter", "EMBI_bps", "JLoss", "GaR", "ES", "VIX"] + \
           [c for c in CONTROLS if c in p.columns]
    p[keep].to_csv("Panel_regresion_v3.csv", index=False)
    print("\nGuardado: Panel_regresion_v3.csv, Tabla_resultados_extendida.csv")


if __name__ == "__main__":
    main()