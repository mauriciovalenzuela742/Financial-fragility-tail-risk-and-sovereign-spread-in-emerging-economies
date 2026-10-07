# -*- coding: utf-8 -*-
"""
p16_heterogeneidad.py -- heterogeneidad por tipo de economia sobre la especificacion PRINCIPAL
(log-log rezagada, panel Panel_bloomberg_embiext.csv, 13 paises; JLOSS_FORMA=nivlag la repite en
niveles). Re-estima en la especificacion vigente la prueba de p5_robustez_arbitro.py (seccion 2b),
que solo existia sobre el panel anterior en niveles contemporaneos:

  nucleo  = 11 emergentes de financiamiento externo (alta participacion extranjera en la deuda)
  contraste = Polonia e India (mercados de deuda local profundos)

    ln EMBI_t = a_i + d_t + b1 J + b2 D + b3 JxD + g1 J*conv + g2 D*conv + g3 JxD*conv + e

b3 es la interaccion en el nucleo y b3+g3 en Polonia+India. Ademas, M4 re-estimado solo sobre el
nucleo, con Driscoll-Kraay y wild cluster bootstrap (pesos de Webb, G=11). Muestras: completa y
sin crisis (excluye GFC y COVID, como el Panel B de la Tabla 1).

Salida: bbg/paper_heterogeneidad_numeros.csv (o _nivlag). Reutiliza p13.datos/p13.fit y
p14.wild_boot; no modifica ningun archivo canonico.
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

CONV = ["poland", "india"]
NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def interaccion_grupo(d, k):
    """M4 con todas las pendientes interactuadas con el grupo de contraste (EF pais+tiempo)."""
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    dd["conv"] = dd["country"].isin(CONV).astype(float)
    for c in ("J_c", "T_c", "JxT"):
        dd[c + "_conv"] = dd[c] * dd["conv"]
    rhs = "J_c + T_c + JxT + J_c_conv + T_c_conv + JxT_conv"
    idx = dd.set_index(["country", "t"])
    for cov, kw in (("dk", p14.DK), ("pais", dict(cov_type="clustered", cluster_entity=True))):
        m = PanelOLS.from_formula(f"ln_EMBI ~ {rhs} + EntityEffects + TimeEffects", idx).fit(**kw)
        num(f"het_{k}_N", m.nobs)
        for n, lab in (("J_c", "b1_nucleo"), ("T_c", "b2_nucleo"), ("JxT", "b3_nucleo"),
                       ("J_c_conv", "dif_b1"), ("JxT_conv", "dif_b3")):
            num(f"het_{k}_{lab}", m.params[n])
            num(f"het_{k}_{lab}_p_{cov}", m.pvalues[n])
        # interaccion neta en Polonia+India y su p (combinacion lineal b3 + g3)
        w = pd.Series(0.0, index=m.params.index); w[["JxT", "JxT_conv"]] = 1.0
        b = float(w @ m.params); se = float((w @ m.cov @ w) ** 0.5)
        from scipy import stats
        num(f"het_{k}_b3_contraste", b)
        num(f"het_{k}_b3_contraste_p_{cov}", 2 * stats.norm.sf(abs(b / se)))
    return dd


def solo_nucleo(d, k):
    core = d[~d["country"].isin(CONV)]
    m, dd = p13.fit(core)
    num(f"nuc_{k}_N", m.nobs); num(f"nuc_{k}_G", dd["country"].nunique())
    for n, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"nuc_{k}_{lab}", m.params[n]); num(f"nuc_{k}_{lab}_p_dk", m.pvalues[n])
        p, _ = p14.wild_boot(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], n, weights="webb")
        num(f"nuc_{k}_{lab}_p_wild", p)
    # con los seis controles domesticos
    mc, ddc = p13.fit(core, ctr=p14.CTRLS)
    num(f"nuc_{k}_ctr_N", mc.nobs)
    num(f"nuc_{k}_ctr_b3", mc.params["JxT"]); num(f"nuc_{k}_ctr_b3_p_dk", mc.pvalues["JxT"])
    p, _ = p14.wild_boot(ddc, "ln_EMBI", ["J_c", "T_c", "JxT"] + list(p14.CTRLS), "JxT", weights="webb")
    num(f"nuc_{k}_ctr_b3_p_wild", p)
    # leave-one-country-out dentro del nucleo
    b3s, ps = [], []
    for c in sorted(core["country"].unique()):
        ml, _ = p13.fit(core[core["country"] != c])
        b3s.append(ml.params["JxT"]); ps.append(ml.pvalues["JxT"])
    num(f"nuc_{k}_loo_b3_min", min(b3s)); num(f"nuc_{k}_loo_b3_max", max(b3s))
    num(f"nuc_{k}_loo_p_max", max(ps))


def main():
    print("p16: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d = p13.datos()
    m0, _ = p13.fit(d)                      # control: debe ser la regresion principal
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4, (m0.nobs, m0.params["JxT"])
    num("principal_b3", m0.params["JxT"]); num("principal_N", m0.nobs)
    sin = d[~d["quarter"].isin(p13.CRISIS_BAT)]
    for k, dk in (("completa", d), ("sincrisis", sin)):
        interaccion_grupo(dk, k)
        solo_nucleo(dk, k)
    out = os.path.join(HERE, f"paper_heterogeneidad_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:40s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
