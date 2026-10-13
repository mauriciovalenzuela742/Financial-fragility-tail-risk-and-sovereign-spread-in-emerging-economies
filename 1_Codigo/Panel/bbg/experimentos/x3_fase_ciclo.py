# -*- coding: utf-8 -*-
"""
x3_fase_ciclo.py -- EXPERIMENTO B2: ¿cambia la transmisión con la fase del ciclo financiero global?

Reemplaza las ventanas de crisis elegidas a mano (Backstop / EMstress) por una variable continua.

=========================== DECLARADO ANTES DE ESTIMAR (2026-10-13) ===========================
 - Ciclo financiero global: promedio de los componentes de ciclo (pasa-banda de Christiano-
   Fitzgerald, 6 a 32 trimestres) del log del VIX y del log del spread de alto rendimiento de EE.UU.,
   cada uno estandarizado. Fase phi_t = ángulo de la señal analítica (transformada de Hilbert).
   phi = 0 es el máximo de estrés; phi = +-pi, el mínimo.
 - Modelo: principal + cada regresor (J, D, JxD) multiplicado por sen(phi_t) y por cos(phi_t):
       beta(phi) = b0 + bs*sen(phi) + bc*cos(phi).
   Los términos sen(phi_t) y cos(phi_t) solos quedan absorbidos por los efectos fijos de tiempo.
 - Contraste que da el veredicto, uno por coeficiente: bs = bc = 0 (Wald agrupado por país, p del
   wild cluster bootstrap, Webb, B = 999). Se reporta también la prueba conjunta de los seis.
 - Variantes declaradas: ciclo solo con el VIX; ciclo solo con el spread de alto rendimiento;
   bandas de 6 a 40 trimestres.
 - Límite conocido: el filtro es de dos lados (usa datos futuros), de modo que la fase no es
   conocible en tiempo real; es una descripción, no una regla.
=================================================================================================
Salida: experimentos/x3_fase_ciclo.csv (y _nivlag). No se integra a ningún documento.
"""
import os

import numpy as np
import pandas as pd
from scipy.signal import hilbert
from statsmodels.tsa.filters.cf_filter import cffilter

import x0_comun as x0

NUM = {}
B = 999


def num(k, v):
    NUM[k] = float(v)
    return v


def fase_global(series=("VIX", "US_HY_spread"), low=6, high=32):
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    g = raw.groupby("quarter")[list(series)].first().dropna().sort_index()
    comp = []
    for s in series:
        c, _ = cffilter(np.log(g[s].to_numpy()), low=low, high=high, drift=True)
        comp.append((c - c.mean()) / c.std())
    ciclo = np.mean(comp, axis=0)
    phi = np.angle(hilbert(ciclo))
    return pd.DataFrame({"quarter": g.index, "ciclo": ciclo, "phi": phi})


def estimar(dd, f, pref):
    s = dd.merge(f, on="quarter", how="inner").copy()
    sn, cs = np.sin(s["phi"].to_numpy()), np.cos(s["phi"].to_numpy())
    cols = [s["J_c"], s["T_c"], s["JxT"]]
    nom = ["J", "D", "JxD"]
    for lab, v in (("J", s["J_c"]), ("D", s["T_c"]), ("JxD", s["JxT"])):
        cols += [v * sn, v * cs]; nom += [f"{lab}_sen", f"{lab}_cos"]
    A, _ = x0.within(s, np.column_stack([s["ln_EMBI"].to_numpy()] + [np.asarray(c) for c in cols]))
    y, X = A[:, 0], A[:, 1:]
    g = pd.factorize(s["country"])[0]
    b, u = x0.ols(y, X)
    V = x0.cov_cluster(X, u, g)
    num(f"{pref}_N", len(y))
    for k, n_ in enumerate(nom):
        num(f"{pref}_{n_}", b[k]); num(f"{pref}_{n_}_t", b[k] / np.sqrt(V[k, k]))
    for j, lab in enumerate(("J", "D", "JxD")):
        idx = [3 + 2 * j, 4 + 2 * j]
        W, p = x0.wild_wald(y, X, idx, g, B=B, seed=20 + j)
        num(f"{pref}_{lab}_fase_W", W); num(f"{pref}_{lab}_fase_p_wild", p)
        amp = np.hypot(b[idx[0]], b[idx[1]])
        num(f"{pref}_{lab}_amplitud", amp)
        num(f"{pref}_{lab}_fase_del_maximo", np.arctan2(b[idx[0]], b[idx[1]]))   # phi donde beta(phi) es máximo
        num(f"{pref}_{lab}_beta_en_max_estres", b[j] + b[idx[1]])                 # phi = 0
        num(f"{pref}_{lab}_beta_en_min_estres", b[j] - b[idx[1]])                 # phi = pi
    W, p = x0.wild_wald(y, X, list(range(3, 9)), g, B=B, seed=30)
    num(f"{pref}_conjunta6_W", W); num(f"{pref}_conjunta6_p_wild", p)


def main():
    print("x3: forma", "niveles" if x0.NIV else "logs")
    dd = x0.datos()
    assert len(dd) == 765
    f = fase_global()
    num("ciclo_T", len(f))
    # descripción: qué fase tienen los trimestres de crisis
    cr = f[f["quarter"].isin(x0.p13.CRISIS_BAT)]
    num("ciclo_cos_fase_media_en_crisis", np.cos(cr["phi"]).mean()); num("ciclo_cos_fase_media_fuera", np.cos(f[~f["quarter"].isin(x0.p13.CRISIS_BAT)]["phi"]).mean())
    num("ciclo_valor_medio_en_crisis", cr["ciclo"].mean())
    f.to_csv(os.path.join(x0.HERE, "x3_fase_global.csv"), index=False)
    estimar(dd, f, "global")
    estimar(dd, fase_global(("VIX",)), "vix")
    estimar(dd, fase_global(("US_HY_spread",)), "hy")
    estimar(dd, fase_global(high=40), "global_6_40")
    sp = dd[dd["country"] != "poland"].copy()
    sp["J_c"] = sp["ln_JLoss_l1"] - sp["ln_JLoss_l1"].mean(); sp["T_c"] = sp["D_l1"] - sp["D_l1"].mean(); sp["JxT"] = sp["J_c"] * sp["T_c"]
    estimar(sp, f, "global_sinpolonia")
    for k, v in NUM.items():
        print(f"  {k:42s} {v: .4f}")
    x0.guardar(NUM, "x3_fase_ciclo")


if __name__ == "__main__":
    main()
