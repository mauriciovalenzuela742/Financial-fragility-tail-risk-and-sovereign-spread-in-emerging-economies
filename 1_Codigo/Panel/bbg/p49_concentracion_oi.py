# -*- coding: utf-8 -*-
"""
p49_concentracion_oi.py -- mu4 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f): la
predicción distintiva del modelo de competencia bancaria à la Cournot que tuvo la tesis (4_Redaccion/modelo OI/):
la fragilidad pesa más en el spread donde el sistema es más concentrado.

  mu4-H1: principal + HHI_{t-4} (pasivos de los mismos bancos que JLoss, bbg/concentracion_trimestral_bbg.csv,
          estandarizado) + ln JLoss_{t-1} x HHI_{t-4}; coeficiente > 0.
  Secundaria: la triple interacción ln JLoss x D x HHI.
Inferencia como en p42 (wild por país, p unilateral, sin cada país). Salida: bbg/paper_p49_numeros.csv.
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

NUM = p32.NUM


def main():
    d, raw = p14.base(); p14.check_principal(d)
    h = pd.read_csv(os.path.join(HERE, "concentracion_trimestral_bbg.csv"))
    q = pd.PeriodIndex(h["quarter"], freq="Q"); h["_qn"] = q.year * 4 + q.quarter
    d = d.merge(p14.shift(h, "HHI_q", 4, "HHI_l4"), on=["country", "_qn"], how="left")
    p1 = p42.moderacion(d, "HHI_l4", "J_c", "mu4h1", +1)
    # secundaria: triple interacción
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", "HHI_l4"]))
    x["H"] = (x["HHI_l4"] - x["HHI_l4"].mean()) / x["HHI_l4"].std()
    x["JxH"] = x["J_c"] * x["H"]; x["TxH"] = x["T_c"] * x["H"]; x["JxTxH"] = x["JxT"] * x["H"]
    rhs = ["J_c", "T_c", "JxT", "H", "JxH", "TxH", "JxTxH"]
    m = p42.fit(x, "ln_EMBI", rhs)
    NUM["sec_triple_b"] = float(m.params["JxTxH"]); NUM["sec_triple_p_dk"] = float(m.pvalues["JxTxH"])
    NUM["sec_triple_p_wild"] = p32.wild(x, "ln_EMBI", rhs, "JxTxH")
    NUM["hhi_medio"] = float(d["HHI_l4"].mean()); NUM["hhi_within_frac"] = float(
        (d["HHI_l4"] - d.groupby("country")["HHI_l4"].transform("mean")).var() / d["HHI_l4"].var())
    out = os.path.join(HERE, "paper_p49_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:24s} {v: .4f}")
    print(f"  mu4-H1 uni {p1:.3f}\n->", out)


if __name__ == "__main__":
    main()
