# -*- coding: utf-8 -*-
"""
p50_exposicion_soberana.py -- mu5 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f): la
exposición de los bancos domésticos a la deuda soberana como moderador (el canal de home bias de
Farhi-Tirole).

  Tenencia: participación de los bancos domésticos en la deuda total del gobierno (%), Arslanalp y Tsuda,
  hoja "Table 3.2 DomesticBank", con el mismo lector que p26.
  mu5-H1: principal + tenencia_{t-4} (estandarizada) + ln JLoss_{t-1} x tenencia_{t-4}; coeficiente > 0.
Inferencia como en p42. Salida: bbg/paper_p50_numeros.csv y bbg/tenencia_bancaria_bbg.csv.
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
import p26_participacion_extranjera as p26
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42

NUM = p32.NUM
SERIE = os.path.join(HERE, "tenencia_bancaria_bbg.csv")


def main():
    if os.path.exists(SERIE):
        t = pd.read_csv(SERIE)
    else:
        t, _ = p26._bloque("Table 3.2 DomesticBank")
        t = t.rename(columns={"v": "tenencia_bancos"}); t.to_csv(SERIE, index=False)
    d, raw = p14.base(); p14.check_principal(d)
    q = pd.PeriodIndex(t["quarter"], freq="Q"); t["_qn"] = q.year * 4 + q.quarter
    d = d.merge(p14.shift(t, "tenencia_bancos", 4, "TEN_l4"), on=["country", "_qn"], how="left")
    p1 = p42.moderacion(d, "TEN_l4", "J_c", "mu5h1", +1)
    NUM["tenencia_media"] = float(d["TEN_l4"].mean())
    NUM["tenencia_within_frac"] = float((d["TEN_l4"] - d.groupby("country")["TEN_l4"].transform("mean")).var() / d["TEN_l4"].var())
    for c, v in d.groupby("country")["TEN_l4"].mean().items():
        NUM[f"tenencia_{c}"] = float(v)
    out = os.path.join(HERE, "paper_p50_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:24s} {v: .4f}")
    print(f"  mu5-H1 uni {p1:.3f}\n->", out)


if __name__ == "__main__":
    main()
