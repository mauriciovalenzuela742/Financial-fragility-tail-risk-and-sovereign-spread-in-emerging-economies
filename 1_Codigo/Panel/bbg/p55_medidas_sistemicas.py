# -*- coding: utf-8 -*-
"""
p55_medidas_sistemicas.py -- U6 del preregistro 4 (4_Redaccion/preregistro_umbrales.md, commit 7ad3810):
medidas de riesgo sistémico de mercado con los mismos bancos de JLoss.

  Retorno del sistema bancario: retorno logarítmico diario ponderado por la capitalización del día
  anterior de los bancos de JLoss (mktcap_<país>.csv). Mercado: índice accionario del país (STX_<PAÍS>.csv,
  el mismo del FCI).
  MES (Acharya et al., 2017): retorno medio del sistema bancario en el 5 % de los peores días del mercado,
       en la ventana de cuatro trimestres que cierra en q; se usa -MES (mayor = más riesgo).
  DeltaCoVaR (Adrian y Brunnermeier, 2016): regresión cuantílica (5 %) del retorno de mercado sobre el del
       sistema bancario en la ventana de ocho trimestres que cierra en q; DeltaCoVaR = b_05 x (VaR_05 del
       sistema - mediana del sistema); se usa -DeltaCoVaR.
  Se reportan la correlación de rangos con JLoss (total y dentro del país), la regresión principal con cada
  medida en lugar de ln JLoss (en t-1, estandarizada) y el umbral U1 reestimado con cada una (p52).
Salida: bbg/medidas_sistemicas_bbg.csv y bbg/paper_p55_numeros.csv.
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
import statsmodels.api as sm
from scipy.stats import spearmanr

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p52_umbrales as p52

NUM = p32.NUM
BBG = os.path.abspath(os.path.join(HERE, "..", "..", "Bloomberg_extraction", "output"))
STX = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals"))
SERIE = os.path.join(HERE, "medidas_sistemicas_bbg.csv")
PAISES = ["brazil", "chile", "china", "colombia", "india", "indonesia", "malaysia", "mexico", "peru",
          "philippines", "poland", "southafrica", "turkey"]


def num(k, v):
    NUM[k] = float(v)


def medidas_pais(c):
    mk = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"))
    mk["date"] = pd.to_datetime(mk["date"])
    w = mk[mk["mktcap"] > 0].pivot_table(index="date", columns="bankname", values="mktcap").sort_index()
    r = np.log(w).diff(); wl = w.shift(1)
    rb = (r * wl).sum(axis=1, min_count=1) / wl.where(r.notna()).sum(axis=1, min_count=1)
    s = pd.read_csv(os.path.join(STX, c.upper(), f"STX_{c.upper()}.csv"))
    s["date"] = pd.to_datetime(s["DATES"], format="%d/%m/%Y")
    s = s.dropna(subset=["date", "STX"]).drop_duplicates("date", keep="last")
    rm = np.log(s.set_index("date")["STX"].sort_index().where(lambda v: v > 0)).diff()
    rb = rb[~rb.index.duplicated(keep="last")]
    z = pd.concat([rb.rename("rb"), rm.rename("rm")], axis=1).dropna()
    z = z[(z.abs() < 0.5).all(axis=1)]
    q = z.index.to_period("Q")
    filas = []
    for qq in sorted(set(q)):
        fin = z.index[q == qq].max()
        v4 = z[(z.index > (qq - 4).end_time) & (z.index <= fin)]
        v8 = z[(z.index > (qq - 8).end_time) & (z.index <= fin)]
        f = {"country": c, "quarter": str(qq)}
        if len(v4) >= 150:
            cut = v4["rm"].quantile(0.05)
            f["MES"] = -float(v4.loc[v4["rm"] <= cut, "rb"].mean())
        if len(v8) >= 300:
            try:
                m = sm.QuantReg(v8["rm"].values, sm.add_constant(v8["rb"].values)).fit(q=0.05)
                f["DCoVaR"] = -float(m.params[1] * (v8["rb"].quantile(0.05) - v8["rb"].median()))
            except Exception:
                pass
        filas.append(f)
    return pd.DataFrame(filas)


def main():
    if os.path.exists(SERIE):
        ms = pd.read_csv(SERIE)
    else:
        ms = pd.concat([medidas_pais(c) for c in PAISES], ignore_index=True)
        ms.to_csv(SERIE, index=False)
    q = pd.PeriodIndex(ms["quarter"], freq="Q"); ms["_qn"] = q.year * 4 + q.quarter
    d, raw = p52.preparar()
    for v in ("MES", "DCoVaR"):
        d = d.merge(p14.shift(ms, v, 1, v + "_l1"), on=["country", "_qn"], how="left")
        x = d.dropna(subset=[v + "_l1", "ln_JLoss_l1"])
        num(f"{v}_N", len(x)); num(f"{v}_paises", x["country"].nunique())
        num(f"{v}_spearman", spearmanr(x[v + "_l1"], x["ln_JLoss_l1"]).correlation)
        a = x[v + "_l1"] - x.groupby("country")[v + "_l1"].transform("mean")
        b = x["ln_JLoss_l1"] - x.groupby("country")["ln_JLoss_l1"].transform("mean")
        num(f"{v}_spearman_within", spearmanr(a, b).correlation)
        # regresión principal con la medida (estandarizada) en lugar de ln JLoss
        dv = d.dropna(subset=[v + "_l1"]).copy()
        dv["ln_JLoss_l1"] = (dv[v + "_l1"] - dv[v + "_l1"].mean()) / dv[v + "_l1"].std()
        xx = p42.centrar(dv.dropna(subset=["ln_EMBI", "D_l1"]))
        rhs = ["J_c", "T_c", "JxT"]; m = p42.fit(xx, "ln_EMBI", rhs)
        num(f"{v}_b1", m.params["J_c"]); num(f"{v}_b1_p_dk", m.pvalues["J_c"])
        num(f"{v}_b1_p_wild", p32.wild(xx, "ln_EMBI", rhs, "J_c"))
        num(f"{v}_b2", m.params["T_c"]); num(f"{v}_b3", m.params["JxT"])
        # umbral U1 con la medida
        p52.bloque_agrupado(dv, f"U1{v}", "FCI_l1", ["J_c", "T_c"], ["JxT"])
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p55_numeros.csv"))
    for k, val in NUM.items():
        if "_alto_" not in k:
            print(f"  {k:30s} {val: .4f}")


if __name__ == "__main__":
    main()
