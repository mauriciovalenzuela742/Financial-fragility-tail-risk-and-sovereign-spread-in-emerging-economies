# -*- coding: utf-8 -*-
"""
x5_kernel_rff.py -- EXPERIMENTO B4: transformación sinusoidal aleatoria (kernel) y regresión lineal.

Pregunta: ¿un modelo no lineal general predice el spread mejor que el lineal, y necesita la
interacción entre los dos riesgos?

=========================== DECLARADO ANTES DE ESTIMAR (2026-10-13) ===========================
 - Características aleatorias de Fourier (Rahimi y Recht, 2007): z(x) = sqrt(2/m) cos(w'x + b), con
   w ~ N(0, gamma^2 I) y b ~ U(0, 2 pi); aproximan un kernel gaussiano. Sobre ellas, regresión ridge.
 - Cuatro modelos, todos sobre J = ln JLoss(t-1) y D = riesgo de cola(t-1) estandarizados:
       L   lineal aditivo (J, D)
       LI  lineal con el producto J*D
       KA  kernel ADITIVO: 50 características de J solo + 50 de D solo (no admite interacción)
       KC  kernel CONJUNTO: 100 características de (J, D) (admite cualquier interacción)
 - Efectos fijos de país y de tiempo: se quitan de la variable dependiente y de las características
   sobre la muestra completa antes de validar (simplificación declarada: filtra las medias de país
   y trimestre de los pliegues de prueba; afecta por igual a los cuatro modelos).
 - Validación cruzada: (a) cinco bloques contiguos de tiempo; (b) dejar un país fuera.
   gamma en {0,5; 1; 2} y penalización lambda en {0,1; 1; 10; 100} se eligen DENTRO de cada pliegue
   de entrenamiento (validación interna por bloques de tiempo). Promedio de cinco semillas.
 - Lectura declarada: si KC no mejora a KA, la aditividad no depende de la forma funcional; si KA
   no mejora a L, la linealidad basta. Es evidencia predictiva, sin inferencia sobre coeficientes.
 - Prueba de cordura: con una interacción sembrada de +0,034 (y de tres veces ese tamaño) se
   comprueba si KC y LI le ganan a sus versiones aditivas.
=================================================================================================
Salida: experimentos/x5_kernel.csv (y _nivlag). No se integra a ningún documento.
"""
import numpy as np
import pandas as pd

import x0_comun as x0

NUM = {}
GAMMAS = (0.5, 1.0, 2.0)
LAMBDAS = (0.1, 1.0, 10.0, 100.0)
M = 50
SEMILLAS = 5


def num(k, v):
    NUM[k] = float(v)
    return v


def rff(x, m, gamma, rng):
    x = np.atleast_2d(x.T).T
    w = rng.normal(0, gamma, size=(x.shape[1], m)); b = rng.uniform(0, 2 * np.pi, m)
    return np.sqrt(2.0 / m) * np.cos(x @ w + b)


def ridge_pred(Xtr, ytr, Xte, lam):
    k = Xtr.shape[1]
    beta = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(k), Xtr.T @ ytr)
    return Xte @ beta


def pliegues_tiempo(tcod, n=5):
    u = np.unique(tcod)
    return [np.isin(tcod, b) for b in np.array_split(u, n)]


def cv_error(feats_por_hp, y, folds, tcod):
    """feats_por_hp: dict {hp: matriz} (hp = gamma o None). Elige (hp, lambda) dentro de cada pliegue."""
    err = np.zeros(len(y))
    for te in folds:
        tr = ~te
        mejor, mejor_e = None, np.inf
        internos = pliegues_tiempo(tcod[tr], 4)
        for hp, F in feats_por_hp.items():
            lams = LAMBDAS if hp is not None else (1e-8,)
            for lam in lams:
                e = 0.0
                for v in internos:
                    pr = ridge_pred(F[tr][~v], y[tr][~v], F[tr][v], lam)
                    e += ((y[tr][v] - pr) ** 2).sum()
                if e < mejor_e:
                    mejor, mejor_e = (hp, lam), e
        hp, lam = mejor
        err[te] = y[te] - ridge_pred(feats_por_hp[hp][tr], y[tr], feats_por_hp[hp][te], lam)
    return err


def construir(dd, y, zJ, zD, seed):
    """devuelve dict modelo -> {hp: características sin efectos fijos}."""
    rng = np.random.default_rng(seed)
    W = lambda F: x0.within(dd, F)[0]
    mods = {"L": {None: W(np.column_stack([zJ, zD]))},
            "LI": {None: W(np.column_stack([zJ, zD, zJ * zD]))}, "KA": {}, "KC": {}}
    for gm in GAMMAS:
        mods["KA"][gm] = W(np.column_stack([rff(zJ, M, gm, rng), rff(zD, M, gm, rng)]))
        mods["KC"][gm] = W(rff(np.column_stack([zJ, zD]), 2 * M, gm, rng))
    return mods


def evaluar(dd, y, zJ, zD, pref):
    tcod = pd.factorize(dd["quarter"], sort=True)[0]
    pcod = pd.factorize(dd["country"])[0]
    esquemas = {"tiempo": pliegues_tiempo(tcod, 5), "pais": [pcod == c for c in np.unique(pcod)]}
    res = {(e, m): [] for e in esquemas for m in ("L", "LI", "KA", "KC")}
    for s in range(SEMILLAS):
        mods = construir(dd, y, zJ, zD, 100 + s)
        for e, folds in esquemas.items():
            for m, F in mods.items():
                res[(e, m)].append(np.sqrt((cv_error(F, y, folds, tcod) ** 2).mean()))
    base = np.sqrt((y ** 2).mean())
    for e in esquemas:
        num(f"{pref}_{e}_recm_solo_EF", base)
        for m in ("L", "LI", "KA", "KC"):
            v = np.mean(res[(e, m)])
            num(f"{pref}_{e}_recm_{m}", v); num(f"{pref}_{e}_razon_{m}_vs_L", v / np.mean(res[(e, "L")]))
        num(f"{pref}_{e}_razon_KC_vs_KA", np.mean(res[(e, "KC")]) / np.mean(res[(e, "KA")]))
        num(f"{pref}_{e}_razon_LI_vs_L", np.mean(res[(e, "LI")]) / np.mean(res[(e, "L")]))
        num(f"{pref}_{e}_dispersion_semillas_KC", np.std(res[(e, "KC")]))


def main():
    print("x5: forma", "niveles" if x0.NIV else "logs")
    dd = x0.datos()
    assert len(dd) == 765
    zJ = ((dd["J_c"] - dd["J_c"].mean()) / dd["J_c"].std()).to_numpy()
    zD = ((dd["T_c"] - dd["T_c"].mean()) / dd["T_c"].std()).to_numpy()
    y = x0.within(dd, ["ln_EMBI"])[0][:, 0]
    num("N", len(y))
    evaluar(dd, y, zJ, zD, "datos")
    # prueba de cordura: interacción sembrada sobre el ajuste aditivo + residuos con signo aleatorio por país
    Xa = x0.within(dd, np.column_stack([dd["J_c"], dd["T_c"]]))[0]
    b, u = x0.ols(y, Xa)
    jx = x0.within(dd, np.column_stack([dd["JxT"]]))[0][:, 0]
    rng = np.random.default_rng(5)
    g = pd.factorize(dd["country"])[0]
    w = rng.choice([-1.0, 1.0], size=g.max() + 1)[g]
    beta = 1.8 if x0.NIV else 0.034
    for lab, mult in (("sembrada_x0", 0.0), ("sembrada_x1", 1.0), ("sembrada_x3", 3.0)):
        ys = Xa @ b + w * u + mult * beta * jx
        evaluar(dd, ys, zJ, zD, lab)
    for k, v in NUM.items():
        print(f"  {k:42s} {v: .4f}")
    x0.guardar(NUM, "x5_kernel")


if __name__ == "__main__":
    main()
