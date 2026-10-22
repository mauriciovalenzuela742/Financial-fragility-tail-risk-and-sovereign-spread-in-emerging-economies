# -*- coding: utf-8 -*-
"""
p45b_rezago_gar.py -- robustez del fechado del riesgo de cola: el GaR de t-1 es el pronóstico, hecho con
la información de t-1, del crecimiento de t. ¿Cambia algo si se usa el de t-2 (pronóstico hecho en t-2 del
crecimiento de t-1)? Se corre exactamente esto y se reporta:

  1. La regresión principal con D_{t-2} en lugar de D_{t-1} (ln JLoss_{t-1} sin cambios), en logaritmos y
     en niveles (pb).
  2. Con D_{t-1} y D_{t-2} a la vez (y la interacción con D_{t-1}), para ver cuál de los dos rezagos lleva la
     asociación.
  3. La correlación entre D_{t-1} y D_{t-2} dentro del país.

Mismo panel, EF de país y de tiempo, Driscoll-Kraay y wild cluster bootstrap por país.
Salida: bbg/paper_p45b_numeros.csv. Reutiliza p14, p32, p42.
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

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42

NUM = p32.NUM


def num(k, v):
    NUM[k] = float(v)


def main():
    d, raw = p14.base()
    p14.check_principal(d)
    d = d.merge(p14.shift(raw, "D_pp", 2, "D_l2"), on=["country", "_qn"], how="left")
    for forma in ("log", "niv"):
        x = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", "D_l2"]).copy()
        if forma == "niv":
            x["ln_EMBI"] = x["EMBI_bps"]; x["ln_JLoss_l1"] = x["JLoss_l1"]
        # (1) D_{t-2} en lugar de D_{t-1}
        y = x.copy(); y["D_l1"] = y["D_l2"]; y = p42.centrar(y)
        rhs = ["J_c", "T_c", "JxT"]
        m = p42.fit(y, "ln_EMBI", rhs)
        for v, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"{forma}_l2_{lab}", m.params[v]); num(f"{forma}_l2_{lab}_p_dk", m.pvalues[v])
            num(f"{forma}_l2_{lab}_p_wild", p32.wild(y, "ln_EMBI", rhs, v))
        num(f"{forma}_l2_N", m.nobs)
        # referencia: D_{t-1} sobre la misma muestra
        z = p42.centrar(x.copy())
        mz = p42.fit(z, "ln_EMBI", rhs)
        for v, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"{forma}_l1_{lab}", mz.params[v]); num(f"{forma}_l1_{lab}_p_dk", mz.pvalues[v])
        # (2) ambos rezagos
        z["T2_c"] = z["D_l2"] - z["D_l2"].mean()
        rhs2 = ["J_c", "T_c", "T2_c", "JxT"]
        m2 = p42.fit(z, "ln_EMBI", rhs2)
        for v, lab in (("T_c", "ambos_D1"), ("T2_c", "ambos_D2")):
            num(f"{forma}_{lab}", m2.params[v]); num(f"{forma}_{lab}_p_dk", m2.pvalues[v])
            num(f"{forma}_{lab}_p_wild", p32.wild(z, "ln_EMBI", rhs2, v))
    w = d.dropna(subset=["D_l1", "D_l2"])
    a = w["D_l1"] - w.groupby("country")["D_l1"].transform("mean")
    b = w["D_l2"] - w.groupby("country")["D_l2"].transform("mean")
    num("corr_within_D1_D2", np.corrcoef(a, b)[0, 1])
    out = os.path.join(HERE, "paper_p45b_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:24s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
