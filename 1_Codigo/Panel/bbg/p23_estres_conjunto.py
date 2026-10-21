# -*- coding: utf-8 -*-
"""
p23_estres_conjunto.py -- contraste directo de la "coincidencia".

Objeción de árbitro: la hipótesis habla de la COINCIDENCIA de alta fragilidad y cola adversa, pero se
contrasta solo con un producto continuo. Contraste directo: indicadores de que cada riesgo está en
su tercil alto y su conjunción.

    ln EMBI = a_i + d_t + a1 AltaJ + a2 AltaD + a3 (AltaJ x AltaD) + e

a3 es lo que la coincidencia agrega por sobre la suma de los dos indicadores (a3 > 0: amplificación;
a3 = 0: efectos aditivos). Terciles definidos dentro de cada país (coherente con los EF de país) y,
como alternativa, sobre el panel completo. También con cuartiles y fuera de crisis.

Salida: bbg/paper_estres_conjunto_numeros.csv (o _nivlag). Reutiliza p13 y p14.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import pandas as pd
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def contraste(d, pref, q=2 / 3, por_pais=True):
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    for col, nom in (("ln_JLoss_l1", "AJ"), ("D_l1", "AD")):
        umbral = dd.groupby("country")[col].transform(lambda x: x.quantile(q)) if por_pais else dd[col].quantile(q)
        dd[nom] = (dd[col] > umbral).astype(float)
    dd["AJD"] = dd["AJ"] * dd["AD"]
    idx = dd.set_index(["country", "t"])
    m = PanelOLS.from_formula("ln_EMBI ~ AJ + AD + AJD + EntityEffects + TimeEffects", idx).fit(**p14.DK)
    mc = PanelOLS.from_formula("ln_EMBI ~ AJ + AD + AJD + EntityEffects + TimeEffects", idx).fit(
        cov_type="clustered", cluster_entity=True)
    num(f"{pref}_N", m.nobs); num(f"{pref}_n_conjunto", dd["AJD"].sum())
    num(f"{pref}_n_esperado_indep", dd["AJ"].mean() * dd["AD"].mean() * len(dd))
    for n_, lab in (("AJ", "a1"), ("AD", "a2"), ("AJD", "a3")):
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_p_dk", m.pvalues[n_]); num(f"{pref}_{lab}_p_pais", mc.pvalues[n_])
    p, _ = p14.wild_boot(dd, "ln_EMBI", ["AJ", "AD", "AJD"], "AJD", weights="webb")
    num(f"{pref}_a3_p_wild", p)


def main():
    print("p23: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d = p13.datos()
    m0, _ = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4
    sin = d[~d["quarter"].isin(p13.CRISIS_BAT)]
    contraste(d, "ter_pais")
    contraste(d, "ter_panel", por_pais=False)
    contraste(d, "cua_pais", q=0.75)
    contraste(sin, "ter_pais_sincrisis")
    out = os.path.join(HERE, f"paper_estres_conjunto_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:34s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
