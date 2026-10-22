# -*- coding: utf-8 -*-
"""
p48_garantias.py -- mu3 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f): garantías
implícitas y propiedad.

  mu3-H1: regresión principal con F_nacional (estatales y privados nacionales) y F_extranjero (filiales),
          -DD ponderado por pasivos, rezagados; economías-trimestre con ambos grupos;
          b_nacional - b_extranjero > 0.
  mu3-H2: principal + participación estatal en los pasivos de los bancos cotizados (t-4, estandarizada) y
          su producto con ln JLoss_{t-1}; coeficiente > 0.
Inferencia como en p46 (wild por país, p unilateral, sin cada país). Salida: bbg/paper_p48_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import pandas as pd

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p46_panel_bancos as p46

NUM = p32.NUM


def main():
    b = p46.panel()
    d, raw = p14.base(); p14.check_principal(d)
    out = os.path.join(HERE, "paper_p48_numeros.csv")
    g = p46.fragilidad_grupos(b, "propiedad")
    NUM["mu3h1_trimestres_con_ambos"] = float(len(g))
    p1 = p46.dos_grupos(d, g, "mu3h1")
    # participación estatal
    st = b.assign(est=(b["propiedad"] == "estatal") * b["total_liab"]).groupby(["country", "quarter"]).agg(
        est=("est", "sum"), tot=("total_liab", "sum")).reset_index()
    st["ESTATAL"] = st["est"] / st["tot"] * 100
    q = pd.PeriodIndex(st["quarter"], freq="Q"); st["_qn"] = q.year * 4 + q.quarter
    d = d.merge(p14.shift(st, "ESTATAL", 4, "ESTATAL_l4"), on=["country", "_qn"], how="left")
    p2 = p42.moderacion(d, "ESTATAL_l4", "J_c", "mu3h2", +1)
    NUM["mu3h2_estatal_media"] = float(d["ESTATAL_l4"].mean())
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:26s} {v: .4f}")
    print(f"  mu3-H1 uni {p1:.3f}; mu3-H2 uni {p2:.3f}\n->", out)


if __name__ == "__main__":
    main()
