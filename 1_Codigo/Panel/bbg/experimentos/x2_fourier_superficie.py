# -*- coding: utf-8 -*-
"""
x2_fourier_superficie.py -- EXPERIMENTO B1: forma flexible de Fourier para la superficie del spread.

Pregunta: ¿hay amplificación con una forma no lineal que el producto J x D no ve?

=========================== DECLARADO ANTES DE ESTIMAR (2026-10-13) ===========================
 - J = ln JLoss(t-1) y D = riesgo de cola(t-1) se reescalan a [0, 2*pi] entre sus percentiles 1 y 99
   (recortando fuera de ese rango): uJ, uD.
 - Modelo: efectos fijos de país y tiempo + J + D (lineales, centrados)
     + parte ADITIVA no lineal: sen(k uJ), cos(k uJ), sen(k uD), cos(k uD), k = 1..K
     + parte CRUZADA: J*D y sen/cos de k(uJ + uD) y de k(uJ - uD), k = 1..K.
 - K = 1 es la especificación primaria (5 términos cruzados); K = 2 se reporta como secundaria.
 - Contraste único que da el veredicto: separabilidad aditiva, es decir, todos los términos
   cruzados iguales a cero; prueba de Wald con covarianza agrupada por país y p del wild cluster
   bootstrap restringido (Webb, B = 999).
 - Se reporta además: (i) la no linealidad de la parte aditiva (sus términos = 0); (ii) el "extra"
   de la superficie cuando ambos riesgos están una d.e. dentro del país sobre su media, frente a la
   suma de mover cada uno por separado; (iii) una prueba de cordura con datos simulados (tamaño sin
   interacción y potencia con una interacción sembrada de +0,034, la del "grupo de once economías").
=================================================================================================
Salida: experimentos/x2_fourier.csv (y _nivlag). No se integra a ningún documento.
"""
import numpy as np
import pandas as pd

import x0_comun as x0

NUM = {}
B = 999


def num(k, v):
    NUM[k] = float(v)
    return v


def escala(x):
    lo, hi = np.quantile(x, [0.01, 0.99])
    return 2 * np.pi * (np.clip(x, lo, hi) - lo) / (hi - lo)


def base(J, D, K):
    """devuelve (X, nombres, idx_aditivos, idx_cruzados); J y D centrados."""
    uJ, uD = escala(J), escala(D)
    cols, nom = [J, D], ["J", "D"]
    for k in range(1, K + 1):
        for lab, u in (("J", uJ), ("D", uD)):
            cols += [np.sin(k * u), np.cos(k * u)]; nom += [f"sen{k}{lab}", f"cos{k}{lab}"]
    n_ad = len(cols)
    cols.append(J * D); nom.append("JxD")
    for k in range(1, K + 1):
        for lab, u in (("mas", uJ + uD), ("menos", uJ - uD)):
            cols += [np.sin(k * u), np.cos(k * u)]; nom += [f"sen{k}{lab}", f"cos{k}{lab}"]
    X = np.column_stack(cols)
    return X, nom, list(range(2, n_ad)), list(range(n_ad, X.shape[1]))


def extra_punto(J, D, K, dd):
    """contraste f(J1,D1) - f(J1,D0) - f(J0,D1) + f(J0,D0): vector de pesos sobre los coeficientes,
    con J0, D0 = medias y J1, D1 = media + una d.e. dentro del país."""
    sdJ = (dd["J_c"] - dd.groupby("country")["J_c"].transform("mean")).std()
    sdD = (dd["T_c"] - dd.groupby("country")["T_c"].transform("mean")).std()
    pts = [(sdJ, sdD, 1), (sdJ, 0.0, -1), (0.0, sdD, -1), (0.0, 0.0, 1)]
    # la base usa la escala de la muestra: se evalúa agregando los puntos a los vectores originales
    Jx = np.concatenate([J, [p[0] for p in pts]]); Dx = np.concatenate([D, [p[1] for p in pts]])
    lo, hi = np.quantile(J, [0.01, 0.99]); lo2, hi2 = np.quantile(D, [0.01, 0.99])
    uJ = 2 * np.pi * (np.clip(Jx, lo, hi) - lo) / (hi - lo); uD = 2 * np.pi * (np.clip(Dx, lo2, hi2) - lo2) / (hi2 - lo2)
    cols = [Jx, Dx]
    for k in range(1, K + 1):
        for u in (uJ, uD):
            cols += [np.sin(k * u), np.cos(k * u)]
    cols.append(Jx * Dx)
    for k in range(1, K + 1):
        for u in (uJ + uD, uJ - uD):
            cols += [np.sin(k * u), np.cos(k * u)]
    F = np.column_stack(cols)[-4:]
    return np.array([p[2] for p in pts]) @ F, sdJ, sdD


def estimar(dd, K, pref, seed=7):
    J, D = dd["J_c"].to_numpy(), dd["T_c"].to_numpy()
    X, nom, ia, ic = base(J, D, K)
    A, _ = x0.within(dd, np.column_stack([dd["ln_EMBI"].to_numpy(), X]))
    y, Xw = A[:, 0], A[:, 1:]
    g = pd.factorize(dd["country"])[0]
    b, u = x0.ols(y, Xw)
    V = x0.cov_cluster(Xw, u, g)
    num(f"{pref}_N", len(y)); num(f"{pref}_k", Xw.shape[1]); num(f"{pref}_q_cruzados", len(ic))
    W, p = x0.wild_wald(y, Xw, ic, g, B=B, seed=seed)
    num(f"{pref}_cruzados_W", W); num(f"{pref}_cruzados_p_wild", p)
    Wa, pa = x0.wild_wald(y, Xw, ia, g, B=B, seed=seed + 1)
    num(f"{pref}_aditivos_nolineales_W", Wa); num(f"{pref}_aditivos_nolineales_p_wild", pa)
    # R2 within: lineal aditivo, lineal con producto, Fourier aditivo, Fourier completo
    sst = (y ** 2).sum()
    for lab, idx in (("lineal", [0, 1]), ("lineal_JxD", [0, 1, ic[0]]), ("fourier_aditivo", [0, 1] + ia),
                     ("fourier_completo", list(range(Xw.shape[1])))):
        _, uu = x0.ols(y, Xw[:, idx]); num(f"{pref}_r2_{lab}", 1 - (uu ** 2).sum() / sst)
    w, sdJ, sdD = extra_punto(J, D, K, dd)
    wc = np.zeros(len(b)); wc[ic] = w[ic]              # solo los términos cruzados aportan al contraste
    ex = float(wc @ b); se = float(np.sqrt(wc @ V @ wc))
    lin = float(b[0] * sdJ + b[1] * sdD)
    num(f"{pref}_extra_1sd", ex); num(f"{pref}_extra_1sd_ee", se); num(f"{pref}_extra_1sd_t", ex / se)
    num(f"{pref}_suma_lineal_1sd", lin)
    return y, Xw, ic, g, b


def cordura(dd, K, S=200, Bs=199):
    """tamaño y potencia de la prueba de términos cruzados con datos simulados."""
    J, D = dd["J_c"].to_numpy(), dd["T_c"].to_numpy()
    X, nom, ia, ic = base(J, D, K)
    A, _ = x0.within(dd, np.column_stack([dd["ln_EMBI"].to_numpy(), X]))
    y, Xw = A[:, 0], A[:, 1:]
    g = pd.factorize(dd["country"])[0]
    resto = [k for k in range(Xw.shape[1]) if k not in ic]
    br, ur = x0.ols(y, Xw[:, resto]); fit = Xw[:, resto] @ br
    cl = np.unique(g); pos = np.searchsorted(cl, g)
    rng = np.random.default_rng(3)
    beta = 0.034 if not x0.NIV else 1.8
    rech = {"tamano": 0, "potencia": 0}
    for s in range(S):
        w = rng.choice([-1.0, 1.0], size=len(cl))[pos]
        y0 = fit + w * ur
        for lab, yy in (("tamano", y0), ("potencia", y0 + beta * Xw[:, ic[0]])):
            _, p = x0.wild_wald(yy, Xw, ic, g, B=Bs, seed=100 + s)
            rech[lab] += p < 0.05
    num(f"cordura_K{K}_tamano", rech["tamano"] / S); num(f"cordura_K{K}_potencia", rech["potencia"] / S)
    num(f"cordura_K{K}_S", S); num(f"cordura_K{K}_beta_sembrada", beta)


def main():
    print("x2: forma", "niveles" if x0.NIV else "logs")
    dd = x0.datos()
    assert len(dd) == 765
    # comprobación: con solo J, D y JxD se recupera la principal
    A, _ = x0.within(dd, ["ln_EMBI", "J_c", "T_c", "JxT"])
    b, _ = x0.ols(A[:, 0], A[:, 1:])
    ref = 0.2464 if x0.NIV else -0.0112
    assert abs(b[2] - ref) < 5e-4, b
    num("principal_b1", b[0]); num("principal_b2", b[1]); num("principal_b3", b[2])
    for K in (1, 2):
        estimar(dd, K, f"K{K}")
    for lab, s in (("sinpolonia", dd[dd["country"] != "poland"]), ("sincrisis", dd[~dd["quarter"].isin(x0.p13.CRISIS_BAT)]),
                   ("fuerapiso", dd[dd["JLoss_l1"] > x0.PISO])):
        s = s.copy()
        s["J_c"] = s["ln_JLoss_l1"] - s["ln_JLoss_l1"].mean(); s["T_c"] = s["D_l1"] - s["D_l1"].mean()
        estimar(s, 1, f"K1_{lab}")
    cordura(dd, 1)
    for k, v in NUM.items():
        print(f"  {k:42s} {v: .4f}")
    x0.guardar(NUM, "x2_fourier")


if __name__ == "__main__":
    main()
