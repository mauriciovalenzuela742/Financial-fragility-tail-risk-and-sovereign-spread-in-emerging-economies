# -*- coding: utf-8 -*-
"""
p21_estacionariedad.py -- ¿es espuria la regresión en niveles?

Objeción de árbitro: el spread es muy persistente (rho = 0,94) y JLoss y el riesgo de cola también;
una regresión en niveles entre series casi integradas puede ser espuria. Tres respuestas sobre la
especificación PRINCIPAL (log-log rezagada, panel embiext; JLOSS_FORMA=nivlag la repite en niveles):

  1. Raíz unitaria de panel: prueba de Fisher (Maddala-Wu) sobre ADF por país, con la serie original y
     con la serie menos su media transversal de cada trimestre (quita la dependencia común).
  2. Dependencia transversal: estadístico CD de Pesaran sobre los residuos de la principal, con y sin
     efectos fijos de tiempo.
  3. Primeras diferencias: D.ln EMBI_t sobre D.ln JLoss_{t-1}, D.D_{t-1} y D.(JxD)_{t-1}.

Salida: bbg/paper_estacionariedad_numeros.csv (o _nivlag). Reutiliza p13 (datos, fit) y p14.
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
from linearmodels.panel import PanelOLS
from scipy import stats
from statsmodels.tsa.stattools import adfuller

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def fisher_adf(d, col, minT=20):
    """Maddala-Wu: -2 * suma ln(p_i) ~ chi2(2N) bajo H0 de raíz unitaria en todos los países."""
    ps = []
    for _, g in d.sort_values("_qn").groupby("country"):
        x = g[col].dropna().to_numpy()
        if len(x) >= minT and np.std(x) > 0:
            ps.append(max(adfuller(x, maxlag=4, autolag="AIC", regression="c")[1], 1e-12))
    st = -2.0 * np.sum(np.log(ps))
    return float(stats.chi2.sf(st, 2 * len(ps))), len(ps)


def pesaran_cd(res):
    """CD de Pesaran para panel no balanceado; res: Serie con índice (country, t)."""
    w = res.unstack(0)
    cols = list(w.columns); tot = 0.0; n = 0
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a = w[[cols[i], cols[j]]].dropna()
            if len(a) >= 8:
                tot += np.sqrt(len(a)) * a.corr().iloc[0, 1]; n += 1
    cd = np.sqrt(1.0 / n) * tot
    return float(cd), float(2 * stats.norm.sf(abs(cd)))


def main():
    print("p21: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, dd = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4

    # 1. raíz unitaria de panel, sobre todas las observaciones disponibles de cada serie
    r = raw[raw["country"].isin(d["country"].unique())].copy()
    for col, lab in (("ln_EMBI", "spread"), ("ln_JLoss", "jloss"), ("D_pp", "cola")):
        p, n = fisher_adf(r, col)
        num(f"ur_{lab}_p", p); num(f"ur_{lab}_paises", n)
        r[col + "_cs"] = r[col] - r.groupby("_qn")[col].transform("mean")
        p2, _ = fisher_adf(r, col + "_cs")
        num(f"ur_{lab}_p_sin_comun", p2)

    # 2. dependencia transversal de los residuos
    cd, p = pesaran_cd(m0.resids); num("cd_PT", cd); num("cd_PT_p", p)
    mp, _ = p13.fit(d, fe="P")
    cd, p = pesaran_cd(mp.resids); num("cd_P", cd); num("cd_P_p", p)

    # 3. primeras diferencias (trimestres consecutivos dentro de cada país)
    dd = dd.sort_values(["country", "_qn"]).copy()
    g = dd.groupby("country")
    consec = (dd["_qn"] - g["_qn"].shift(1)) == 1
    for c in ("ln_EMBI", "J_c", "T_c", "JxT"):
        dd["d_" + c] = (dd[c] - g[c].shift(1)).where(consec)
    fd = dd.dropna(subset=["d_ln_EMBI", "d_J_c", "d_T_c", "d_JxT"]).copy()
    num("fd_N", len(fd))
    for fe, eff in (("T", "TimeEffects"), ("PT", "EntityEffects + TimeEffects"), ("sinEF", "1")):
        m = PanelOLS.from_formula(f"d_ln_EMBI ~ d_J_c + d_T_c + d_JxT + {eff}",
                                  fd.set_index(["country", "t"])).fit(**p14.DK)
        for n_, lab in (("d_J_c", "b1"), ("d_T_c", "b2"), ("d_JxT", "b3")):
            num(f"fd_{fe}_{lab}", m.params[n_]); num(f"fd_{fe}_{lab}_p", m.pvalues[n_])
    for n_, lab in (("d_J_c", "b1"), ("d_T_c", "b2"), ("d_JxT", "b3")):
        p, _ = p14.wild_boot(fd, "d_ln_EMBI", ["d_J_c", "d_T_c", "d_JxT"], n_, weights="webb")
        num(f"fd_PT_{lab}_p_wild", p)
    # sin la interacción: efectos de nivel en diferencias
    m = PanelOLS.from_formula("d_ln_EMBI ~ d_J_c + d_T_c + EntityEffects + TimeEffects",
                              fd.set_index(["country", "t"])).fit(**p14.DK)
    num("fd_M3_b1", m.params["d_J_c"]); num("fd_M3_b1_p", m.pvalues["d_J_c"])
    num("fd_M3_b2", m.params["d_T_c"]); num("fd_M3_b2_p", m.pvalues["d_T_c"])

    # 4. coherencia con la especificación dinámica: rezago del spread + dos rezagos de cada riesgo.
    #    Si el spread responde al CAMBIO de la fragilidad, J_{t-1} y J_{t-2} entran con signos opuestos
    #    y la especificación con un solo rezago (p14) lo esconde.
    for c in ("J_c", "T_c"):
        dd[c + "_l"] = g[c].shift(1).where(consec)
    ad = dd.dropna(subset=["ln_EMBI", "ln_EMBI_l1", "J_c", "T_c", "J_c_l", "T_c_l"]).copy()
    m = PanelOLS.from_formula("ln_EMBI ~ ln_EMBI_l1 + J_c + J_c_l + T_c + T_c_l + EntityEffects + TimeEffects",
                              ad.set_index(["country", "t"])).fit(**p14.DK)
    num("adl_N", m.nobs); num("adl_rho", m.params["ln_EMBI_l1"])
    for n_, lab in (("J_c", "J_l1"), ("J_c_l", "J_l2"), ("T_c", "D_l1"), ("T_c_l", "D_l2")):
        num(f"adl_{lab}", m.params[n_]); num(f"adl_{lab}_p", m.pvalues[n_])
    for a, b, lab in (("J_c", "J_c_l", "J_suma"), ("T_c", "T_c_l", "D_suma")):
        w = pd.Series(0.0, index=m.params.index); w[[a, b]] = 1.0
        est = float(w @ m.params); se = float((w @ m.cov @ w) ** 0.5)
        num(f"adl_{lab}", est); num(f"adl_{lab}_p", 2 * stats.norm.sf(abs(est / se)))

    out = os.path.join(HERE, f"paper_estacionariedad_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
