# -*- coding: utf-8 -*-
"""
x0_comun.py -- utilidades de los EXPERIMENTOS (carpeta bbg/experimentos).

Nada de esta carpeta está integrado a la tesis, al paper ni a las láminas: son pruebas exploratorias
(2026-10-13) que se reportan en REPORTE_experimentos.md para decidir después si se incorporan.

Contiene: carga del panel de la especificación principal (p13.datos), transformación within de dos
vías para el panel desbalanceado, MCO, covarianza agrupada por país y el wild cluster bootstrap
restringido (pesos de Webb) para una prueba de Wald conjunta de q restricciones de exclusión.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
BBG = os.path.dirname(HERE)
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(BBG, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, BBG)
sys.path.insert(0, os.path.dirname(BBG))

import numpy as np
import pandas as pd

import p13_figuras_paper as p13

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
PISO = 2.16 * 1.02        # JLoss "en el piso" (techo de la malla de pérdidas, tolerancia de 2 %)


def datos():
    """panel de estimación de la principal, con J_c y T_c centrados y su producto."""
    d = p13.datos()
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).sort_values(["country", "quarter"]).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    return dd.reset_index(drop=True)


def dummies_ef(dd, pais=True, tiempo=True):
    cols = [np.ones((len(dd), 1))]
    if pais:
        cols.append(pd.get_dummies(dd["country"], drop_first=True).to_numpy(float))
    if tiempo:
        cols.append(pd.get_dummies(dd["quarter"], drop_first=True).to_numpy(float))
    return np.hstack(cols)


def within(dd, cols, pais=True, tiempo=True, extra=None):
    """residuos de cada columna respecto de los efectos fijos (y de `extra`, matriz opcional)."""
    Z = dummies_ef(dd, pais, tiempo)
    if extra is not None:
        Z = np.hstack([Z, extra])
    A = dd[cols].to_numpy(float) if not isinstance(cols, np.ndarray) else cols
    return A - Z @ np.linalg.lstsq(Z, A, rcond=None)[0], Z.shape[1]


def ols(y, X):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b, y - X @ b


def cov_cluster(X, u, g):
    """sándwich agrupado (CR1) para X ya transformada; g = códigos de cluster."""
    XtXi = np.linalg.pinv(X.T @ X)
    S = np.zeros((X.shape[1], X.shape[1]))
    for c in np.unique(g):
        s = X[g == c].T @ u[g == c]
        S += np.outer(s, s)
    G = len(np.unique(g))
    return XtXi @ S @ XtXi * G / (G - 1)


def wald(b, V, idx):
    bi = b[idx]
    return float(bi @ np.linalg.pinv(V[np.ix_(idx, idx)]) @ bi)


def wild_wald(y, X, idx, g, B=999, seed=7):
    """prueba conjunta de que los coeficientes `idx` son cero, con wild cluster bootstrap restringido.
    y, X ya vienen sin efectos fijos. Devuelve (W observado, p bootstrap)."""
    idx = np.atleast_1d(idx)
    b, u = ols(y, X)
    W = wald(b, cov_cluster(X, u, g), idx)
    resto = [k for k in range(X.shape[1]) if k not in set(idx)]
    if resto:
        br, ur = ols(y, X[:, resto]); fit = X[:, resto] @ br
    else:
        ur = y.copy(); fit = np.zeros_like(y)
    rng = np.random.default_rng(seed)
    cl = np.unique(g); pos = np.searchsorted(cl, g)
    Ws = np.empty(B)
    for r in range(B):
        w = rng.choice(WEBB, size=len(cl))[pos]
        ys = fit + w * ur
        bs, us = ols(ys, X)
        Ws[r] = wald(bs, cov_cluster(X, us, g), idx)
    return W, float((1 + (Ws >= W).sum()) / (B + 1))


def t_cluster(y, X, k, g):
    b, u = ols(y, X)
    V = cov_cluster(X, u, g)
    return b[k], np.sqrt(V[k, k])


def guardar(num, nombre):
    out = os.path.join(HERE, f"{nombre}{SFX}.csv")
    pd.Series(num, name="valor").rename_axis("clave").to_csv(out)
    print("->", out)
