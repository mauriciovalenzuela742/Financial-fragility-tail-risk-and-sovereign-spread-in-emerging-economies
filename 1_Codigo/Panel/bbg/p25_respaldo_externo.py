# -*- coding: utf-8 -*-
"""
p25_respaldo_externo.py -- respaldo externo medido por país y fecha.

Objeción de árbitro: en la tesis el "respaldo externo" es una variable de tiempo (Backstop = crisis
global y pandemia para todos los países). El contraste creíble usa variación entre países: quién
tenía, en cada trimestre, acceso a una línea swap de la Reserva Federal o a la Línea de Crédito
Flexible (FCL) del FMI. Ventanas en respaldo_externo.csv, con la fuente de cada una.

    ln EMBI = a_i + d_t + b1 J + b2 D + b3 JxD + a Acc + c1 J*Acc + c2 D*Acc + c3 JxD*Acc + e

Si el respaldo desacopla la transmisión: c1, c2 < 0 (cada riesgo pesa menos con acceso) y c3 < 0.
Se estima sobre la muestra completa, solo con la FCL, solo con el swap, y dentro de las crisis
globales (GFC y pandemia), donde la comparación es entre países con y sin acceso en el mismo
trimestre.

Salida: bbg/paper_respaldo_numeros.csv (o _nivlag). Reutiliza p13 (datos, CRISIS_BAT) y p14.
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
CLU = dict(cov_type="clustered", cluster_entity=True)


def num(k, v):
    NUM[k] = float(v)
    return v


def acceso(d):
    """agrega swap_fed, fcl_fmi y acc (cualquiera) según las ventanas de respaldo_externo.csv."""
    v = pd.read_csv(os.path.join(HERE, "respaldo_externo.csv"))
    d = d.copy(); d["swap_fed"] = 0.0; d["fcl_fmi"] = 0.0
    for _, r in v.iterrows():
        m = (d["country"] == r["country"]) & (d["quarter"] >= r["desde"]) & (d["quarter"] <= r["hasta"])
        d.loc[m, r["instrumento"]] = 1.0
    d["acc"] = ((d["swap_fed"] + d["fcl_fmi"]) > 0).astype(float)
    return d


def estimar(d, col, pref, wild=True):
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    dd["A"] = dd[col]
    dd["JxA"] = dd["J_c"] * dd["A"]; dd["TxA"] = dd["T_c"] * dd["A"]; dd["JxTxA"] = dd["JxT"] * dd["A"]
    rhs = ["J_c", "T_c", "JxT", "A", "JxA", "TxA", "JxTxA"]
    idx = dd.set_index(["country", "t"])
    f = "ln_EMBI ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, idx).fit(**p14.DK); mc = PanelOLS.from_formula(f, idx).fit(**CLU)
    num(f"{pref}_N", m.nobs); num(f"{pref}_n_acceso", dd["A"].sum()); num(f"{pref}_paises_acceso", dd.loc[dd["A"] > 0, "country"].nunique())
    for n_, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3"), ("A", "a"), ("JxA", "c1"), ("TxA", "c2"), ("JxTxA", "c3")):
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_p_dk", m.pvalues[n_]); num(f"{pref}_{lab}_p_pais", mc.pvalues[n_])
    if wild:
        for n_, lab in (("JxA", "c1"), ("TxA", "c2"), ("JxTxA", "c3")):
            p, _ = p14.wild_boot(dd, "ln_EMBI", rhs, n_, weights="webb")
            num(f"{pref}_{lab}_p_wild", p)


def main():
    print("p25: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d = p13.datos()
    m0, _ = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4
    d = acceso(d)
    print("   trimestres con acceso por país:", d[d["acc"] > 0].groupby("country").size().to_dict())
    estimar(d, "acc", "acc")
    estimar(d, "fcl_fmi", "fcl", wild=False)
    estimar(d, "swap_fed", "swap", wild=False)
    cr = d[d["quarter"].isin(p13.CRISIS_BAT)]
    estimar(cr, "acc", "crisis_acc")
    out = os.path.join(HERE, f"paper_respaldo_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
