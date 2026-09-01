# -*- coding: utf-8 -*-
"""
p6_concentracion_trimestral.py -- concentracion bancaria TRIMESTRAL a partir de los
mismos balances Bloomberg que alimentan JLoss (mismo principio de homogeneidad de
fuente). Sustituye/complementa el HHI anual casi invariante de World Bank GFDD.

Para cada pais y trimestre, sobre los bancos cotizados con tot_asset > 0:
  CR3_q = suma de activos de los 3 mayores / suma de activos de todos los cotizados
  HHI_q = suma((activos_i / activos_totales)^2) * 10000   (base 0-10000, convencion HHI)

Limitacion declarada: es la concentracion del SEGMENTO COTIZADO (los bancos que
alimentan JLoss), no del sistema completo -- igual que JLoss, no observa bancos no
listados. Se valida contra el HHI anual de GFDD (nivel de sistema) por pais.

Entrada: 1_Codigo/Bloomberg_extraction/output/<pais>/balance_<pais>.csv
Salida : concentracion_trimestral_bbg.csv  (country, quarter, CR3_q, HHI_q, n_bancos)
"""
import os, glob
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BBG_OUT = os.path.join(HERE, "..", "..", "Bloomberg_extraction", "output")
MIN_BANCOS = 3  # misma convencion que jloss_engine.MIN_BANKS


def quarterly_concentration(balance_csv):
    b = pd.read_csv(balance_csv)
    b["date"] = pd.to_datetime(b["date"])
    b["quarter"] = b["date"].dt.to_period("Q").astype(str)
    b = b[b["tot_asset"] > 0].copy()
    # ultimo valor de cada banco por trimestre (evita doble conteo intra-trimestre)
    b = (b.sort_values("date")
          .groupby(["countryname", "bankname", "quarter"], as_index=False)
          .last())
    rows = []
    for (country, q), g in b.groupby(["countryname", "quarter"]):
        a = g["tot_asset"].sort_values(ascending=False).values
        n = len(a)
        total = a.sum()
        if total <= 0 or n < 1:
            continue
        share = a / total
        top3 = share[:3].sum()
        hhi = float((share ** 2).sum() * 10000)
        rows.append(dict(country=country, quarter=q, CR3_q=top3, HHI_q=hhi, n_bancos=n))
    return pd.DataFrame(rows)


def main():
    dirs = sorted(glob.glob(os.path.join(BBG_OUT, "*")))
    out = []
    for d in dirs:
        c = os.path.basename(d)
        f = os.path.join(d, f"balance_{c}.csv")
        if not os.path.exists(f):
            continue
        r = quarterly_concentration(f)
        if len(r):
            out.append(r)
            below = (r["n_bancos"] < MIN_BANCOS).mean()
            print(f"  {c:14s} {len(r):3d} trimestres  CR3_q med={r['CR3_q'].median():.2f}  "
                  f"HHI_q med={r['HHI_q'].median():6.0f}  n_bancos med={r['n_bancos'].median():.0f}  "
                  f"%<{MIN_BANCOS}bancos={below:.0%}")
    panel = pd.concat(out, ignore_index=True)
    # bajo el minimo de bancos, la concentracion es un artefacto de cobertura, no una
    # medida creible (misma logica que below_min_banks en jloss_engine) -> NaN
    below = panel["n_bancos"] < MIN_BANCOS
    panel.loc[below, ["CR3_q", "HHI_q"]] = np.nan
    print(f"\n{below.sum()} / {len(panel)} trimestres-pais bajo el minimo de "
          f"{MIN_BANCOS} bancos -> CR3_q/HHI_q puestos a NaN (no se interpolan)")
    panel.to_csv(os.path.join(HERE, "concentracion_trimestral_bbg.csv"), index=False)

    # validacion contra GFDD anual (si esta disponible en controls_all_bbg.csv o Panel_bloomberg.csv)
    try:
        pb = pd.read_csv(os.path.join(HERE, "Panel_bloomberg.csv"))
        gfdd = pb.groupby("country")["HHI_struct"].median().dropna()
        mine = panel.groupby("country")["HHI_q"].mean().dropna()
        common = gfdd.index.intersection(mine.index)
        if len(common) > 3:
            rho = np.corrcoef(gfdd.loc[common], mine.loc[common])[0, 1]
            print(f"\nValidacion: corr(HHI_q medio por pais, HHI GFDD anual) = {rho:.3f}  (n={len(common)})")
    except Exception as e:
        print("validacion omitida:", e)

    print(f"\nGuardado: concentracion_trimestral_bbg.csv ({len(panel)} filas, "
          f"{panel['country'].nunique()} paises)")


if __name__ == "__main__":
    main()
