# -*- coding: utf-8 -*-
"""
p19_resiliencia.py -- resiliencia de la politica economica como moderador.

Hipotesis del profesor guia (predefensa, 2026-10-09): la deuda/PIB, el balance fiscal/PIB y las
reservas/PIB definen la resiliencia de la politica economica (la capacidad del gobierno y del banco
central de rescatar). Mientras mas resiliente el pais, menor deberia ser el efecto de la fragilidad
bancaria y del riesgo de cola sobre el spread; y en una crisis que afecta a todos ese resguardo
podria no bastar.

Indice R = promedio de los z-scores de (-deuda/PIB, balance fiscal/PIB, reservas/PIB): mayor R, mas
resiliencia. Sobre la especificacion PRINCIPAL (log-log rezagada, EF pais + tiempo; JLOSS_FORMA=nivlag
la repite en niveles):

    ln EMBI = a_i + d_t + b1 J + b2 D + b3 JxD + r R + g1 J*R + g2 D*R (+ g3 JxD*R) + e

  1. Moderacion: g1 y g2 (negativos si la resiliencia atenua), con DK, cluster pais y wild bootstrap.
  2. Por terciles de resiliencia: b1 y b2 en paises-trimestre de resiliencia baja / media / alta.
  3. Crisis vs. no crisis: g1 y g2 fuera de crisis y su cambio dentro de las crisis (GFC + COVID).
  4. Robustez: R medido cuatro trimestres antes (fuera del alcance de la retroalimentacion).

Salida: bbg/paper_resiliencia_numeros.csv (o _nivlag). Reutiliza p13 (datos, CRISIS_BAT) y p14
(base, wild_boot, DK).
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

COMP = [("debt_gdp", -1.0), ("fisc_bal", 1.0), ("res_gdp", 1.0)]   # signo: mayor = mas resiliente
NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = {}
CLU = dict(cov_type="clustered", cluster_entity=True)


def num(k, v):
    NUM[k] = float(v)
    return v


def preparar(d, sufijo=""):
    """centra J y D, construye el indice de resiliencia y sus interacciones."""
    cols = [c + sufijo for c, _ in COMP]
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + cols).copy()
    z = [s * (dd[c + sufijo] - dd[c + sufijo].mean()) / dd[c + sufijo].std() for c, s in COMP]
    dd["R"] = sum(z) / len(z)
    dd["R"] = (dd["R"] - dd["R"].mean()) / dd["R"].std()      # una d.e. de resiliencia = 1
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    dd["JxR"] = dd["J_c"] * dd["R"]; dd["TxR"] = dd["T_c"] * dd["R"]; dd["JxTxR"] = dd["JxT"] * dd["R"]
    cr = dd["quarter"].isin(p13.CRISIS_BAT).astype(float)
    dd["C"] = cr
    for c in ("J_c", "T_c", "R", "JxR", "TxR"):
        dd[c + "_C"] = dd[c] * cr
    return dd


def fit(dd, rhs, kw=p14.DK):
    return PanelOLS.from_formula("ln_EMBI ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects",
                                 dd.set_index(["country", "t"])).fit(**kw)


def moderacion(dd, pref, triple=False):
    rhs = ["J_c", "T_c", "JxT", "R", "JxR", "TxR"] + (["JxTxR"] if triple else [])
    m = fit(dd, rhs); mc = fit(dd, rhs, CLU)
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", dd["country"].nunique())
    for n, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3"), ("R", "r"), ("JxR", "g1"), ("TxR", "g2")) + \
            ((("JxTxR", "g3"),) if triple else ()):
        num(f"{pref}_{lab}", m.params[n]); num(f"{pref}_{lab}_p_dk", m.pvalues[n])
        num(f"{pref}_{lab}_p_pais", mc.pvalues[n])
    if not triple:
        for n, lab in (("JxR", "g1"), ("TxR", "g2")):
            p, _ = p14.wild_boot(dd, "ln_EMBI", rhs, n, weights="webb")
            num(f"{pref}_{lab}_p_wild", p)
    return m


def terciles(dd):
    dd = dd.copy()
    dd["ter"] = pd.qcut(dd["R"], 3, labels=["baja", "media", "alta"])
    for t in ("baja", "media", "alta"):
        s = dd[dd["ter"] == t]
        m, _ = p13.fit(s)
        num(f"ter_{t}_N", m.nobs)
        for n, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"ter_{t}_{lab}", m.params[n]); num(f"ter_{t}_{lab}_p_dk", m.pvalues[n])


def crisis(dd):
    rhs = ["J_c", "T_c", "JxT", "R", "JxR", "TxR", "J_c_C", "T_c_C", "R_C", "JxR_C", "TxR_C"]
    m = fit(dd, rhs)
    num("cr_N", m.nobs); num("cr_N_crisis", dd["C"].sum())
    for n, lab in (("JxR", "g1_fuera"), ("TxR", "g2_fuera"), ("JxR_C", "g1_cambio"), ("TxR_C", "g2_cambio"),
                   ("R", "r_fuera"), ("R_C", "r_cambio")):
        num(f"cr_{lab}", m.params[n]); num(f"cr_{lab}_p_dk", m.pvalues[n])
    for a, b, lab in (("JxR", "JxR_C", "g1_crisis"), ("TxR", "TxR_C", "g2_crisis"), ("R", "R_C", "r_crisis")):
        w = pd.Series(0.0, index=m.params.index); w[[a, b]] = 1.0
        est = float(w @ m.params); se = float((w @ m.cov @ w) ** 0.5)
        from scipy import stats
        num(f"cr_{lab}", est); num(f"cr_{lab}_p_dk", 2 * stats.norm.sf(abs(est / se)))


def main():
    print("p19: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, _ = p14.base()                       # trae los controles en t y en t-4 (sufijo _l4)
    dd = preparar(d)
    num("corr_R_J", dd[["R", "J_c"]].corr().iloc[0, 1]); num("corr_R_T", dd[["R", "T_c"]].corr().iloc[0, 1])
    m0, _ = p13.fit(dd)                      # principal sobre la muestra con los tres componentes
    num("base_N", m0.nobs)
    for n, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"base_{lab}", m0.params[n]); num(f"base_{lab}_p_dk", m0.pvalues[n])
    moderacion(dd, "mod")
    moderacion(dd, "mod3", triple=True)
    terciles(dd)
    crisis(dd)
    moderacion(preparar(d, "_l4"), "modl4")
    out = os.path.join(HERE, f"paper_resiliencia_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
