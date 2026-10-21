# -*- coding: utf-8 -*-
"""
p22_inferencia_potencia.py -- ¿qué vara de inferencia corresponde con 13 países y 88 trimestres?

Objeción de árbitro: la tesis usa el wild cluster bootstrap como veredicto ("robusto solo si
resiste"), pero Driscoll-Kraay es asintótico en T (aquí T ~ 88) y el bootstrap por país puede tener
poca potencia con 13 clusters. Sobre la especificación PRINCIPAL (log-log rezagada):

  1. Errores alternativos: cluster por país, por trimestre y doble cluster (país y trimestre).
  2. Simulación de tamaño y potencia: se generan muestras con y* = ajuste + w_c * residuo (w_c =
     Rademacher por país, que conserva la autocorrelación dentro de cada país), bajo H1 (efecto =
     el estimado) y bajo H0 (efecto = 0), y se mide cuán seguido rechaza al 5 % cada método.
  3. Comparaciones múltiples: p-valores de Holm para la familia de contrastes de la interacción.

Salida: bbg/paper_inferencia_numeros.csv. Reutiliza p13, p14 y los CSV de p16.
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

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14

S = int(os.environ.get("JLOSS_SIM", 150))      # simulaciones
B = int(os.environ.get("JLOSS_SIM_B", 199))    # réplicas del wild bootstrap dentro de cada una
REGS = ["J_c", "T_c", "JxT"]
F = "ln_EMBI ~ J_c + T_c + JxT + EntityEffects + TimeEffects"
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def errores(dd):
    idx = dd.set_index(["country", "t"])
    for lab, kw in (("dk", p14.DK), ("pais", dict(cov_type="clustered", cluster_entity=True)),
                    ("tiempo", dict(cov_type="clustered", cluster_time=True)),
                    ("doble", dict(cov_type="clustered", cluster_entity=True, cluster_time=True))):
        m = PanelOLS.from_formula(F, idx).fit(**kw)
        for n_, c in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"p_{lab}_{c}", m.pvalues[n_])


def simular(dd, m0):
    rng = np.random.default_rng(11)
    paises = dd["country"].unique()
    e = m0.resids.reindex(dd.set_index(["country", "t"]).index).to_numpy()
    y = dd["ln_EMBI"].to_numpy()
    rech = {}
    casos = [("H1", "J_c", 0.0), ("H1", "T_c", 0.0), ("H0", "J_c", m0.params["J_c"]), ("H0", "T_c", m0.params["T_c"])]
    for s in range(S):
        w = dict(zip(paises, rng.choice([-1.0, 1.0], size=len(paises))))
        wv = dd["country"].map(w).to_numpy()
        for hip, coef, quita in casos:
            ds = dd.copy()
            ds["ln_EMBI"] = y - e + wv * e - quita * dd[coef].to_numpy()
            idx = ds.set_index(["country", "t"])
            p_dk = PanelOLS.from_formula(F, idx).fit(**p14.DK).pvalues[coef]
            p_cl = PanelOLS.from_formula(F, idx).fit(cov_type="clustered", cluster_entity=True).pvalues[coef]
            p_w, _ = p14.wild_boot(ds, "ln_EMBI", REGS, coef, B=B, seed=1000 + s, weights="webb")
            for met, p in (("dk", p_dk), ("pais", p_cl), ("wild", p_w)):
                rech.setdefault((hip, coef, met), []).append(p < 0.05)
        if (s + 1) % 25 == 0:
            print(f"   simulación {s + 1}/{S}", flush=True)
    for (hip, coef, met), v in rech.items():
        lab = {"J_c": "b1", "T_c": "b2"}[coef]
        num(f"sim_{'potencia' if hip == 'H1' else 'tamano'}_{met}_{lab}", np.mean(v))
    num("sim_S", S); num("sim_B", B)


def holm():
    """familia de contrastes de la interacción (p de Driscoll-Kraay), con corrección de Holm."""
    h = pd.read_csv(os.path.join(HERE, "paper_heterogeneidad_numeros.csv"), index_col=0)["valor"]
    a = pd.read_csv(os.path.join(HERE, "paper_arbitro_numeros.csv"), index_col=0).iloc[:, 0]
    fam = {"b3_principal": NUM["p_dk_b3"], "b3_nucleo_completa": h["nuc_completa_b3_p_dk"],
           "b3_nucleo_sincrisis": h["nuc_sincrisis_b3_p_dk"], "b3_contraste_sincrisis": h["het_sincrisis_b3_contraste_p_dk"]}
    # sumas por régimen de crisis (CM4, EF país + tiempo; Tabla de crisis del texto, NUMEROS_CANONICOS §10)
    fam["b3_b4_backstop"] = 0.030
    fam["b3_b4_emstress"] = 0.080
    del a
    ps = pd.Series(fam).sort_values()
    m = len(ps); adj = []; prev = 0.0
    for i, p in enumerate(ps):
        prev = max(prev, min(1.0, (m - i) * p)); adj.append(prev)
    for (k, p), q in zip(ps.items(), adj):
        num(f"holm_{k}_p", p); num(f"holm_{k}_p_holm", q)
    num("holm_familia", m)


def main():
    print("p22: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), f"| S={S}, B={B}")
    d = p13.datos()
    m0, dd = p13.fit(d)
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] + 0.0112) < 5e-4
    errores(dd)
    holm()
    simular(dd, m0)
    out = os.path.join(HERE, "paper_inferencia_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:44s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
