# -*- coding: utf-8 -*-
"""
p35_cuantilica_spread.py -- ¿aparece la amplificación en la cola alta del spread? (mejora B8 de
4_Redaccion/evaluacion_experta.md). Se corren exactamente estas variantes y se reportan todas:

La teoría (Farhi-Tirole) predice la amplificación en los estados adversos, y la regresión principal
mide la media condicional. Aquí se estima la interacción ln JLoss_{t-1} x D_{t-1} a lo largo de la
distribución condicional del ln EMBI, tau = 0,10; 0,25; 0,50; 0,75; 0,90:

  1. MMQR (Machado y Santos Silva, 2019): regresión cuantílica por momentos con efectos fijos.
     Localización: la regresión principal (EF de país y de tiempo). Escala: |residuo| sobre los mismos
     regresores y EF. b(tau) = b_loc + b_esc * q_tau, con q_tau el cuantil del residuo estandarizado.
  2. Regresión cuantílica con variables indicadoras de país y de tiempo (Koenker, 2004, sin
     penalización), como contraste que no impone la estructura de localización y escala.
  3. Lo mismo con la distancia al incumplimiento de Merton (-DD_w, de p34) en lugar de ln JLoss.

Inferencia: bootstrap por bloques de país (se remuestrean economías completas con reemplazo, 499
réplicas; 199 en la regresión con indicadoras, por su costo), percentil del IC 95 % y p bilateral por la fracción de réplicas del lado opuesto de cero.
Con 13 economías el bootstrap de pares por país es conservador; se declara.

Salida: bbg/paper_p35_numeros.csv (o _nivlag) y figura fig_cuantilica_lnlag. Reutiliza p13, p14, p34.
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
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p34_fragilidad_alternativa as p34
from causal_core import demean2

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
TAUS = (0.10, 0.25, 0.50, 0.75, 0.90)
B = 499
REGS = ["J_c", "T_c", "JxT"]
NUM = {}


def num(k, v):
    NUM[k] = float(v)


def preparar(d, col=None, neg=False):
    x = d.copy()
    if col is not None:
        x = x.dropna(subset=[col])
        x["ln_JLoss_l1"] = -x[col] if neg else x[col]
    x = x.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    x["J_c"] = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean()
    x["T_c"] = x["D_l1"] - x["D_l1"].mean()
    x["JxT"] = x["J_c"] * x["T_c"]
    return x.reset_index(drop=True)


def mmqr(x):
    """b(tau) para cada tau. Localización y escala con EF de país y de tiempo (transformación within)."""
    y = demean2(x, ["ln_EMBI"], iters=40)["ln_EMBI"].values
    X = demean2(x, REGS, iters=40).values
    b_loc = np.linalg.lstsq(X, y, rcond=None)[0]
    # residuo con los efectos fijos: y_original - fitted (incluye alfa_i + delta_t)
    r = y - X @ b_loc                                   # residuo within = residuo de la regresión con EF
    a = np.abs(r)
    aw = demean2(x.assign(_a=a), ["_a"], iters=40)["_a"].values
    b_esc = np.linalg.lstsq(X, aw, rcond=None)[0]
    esc = a - aw + X @ b_esc                            # escala ajustada: EF de |r| + X b_esc
    esc = np.where(esc > 1e-8, esc, np.nan)
    u = r / esc
    q = np.nanquantile(u, TAUS)
    return {t: b_loc + b_esc * qt for t, qt in zip(TAUS, q)}, b_loc, b_esc


def qr_dummies(x):
    D = pd.get_dummies(x[["country", "quarter"]], drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([x[REGS], D], axis=1))
    out = {}
    for t in TAUS:
        res = sm.QuantReg(x["ln_EMBI"].values, X.values).fit(q=t, max_iter=5000)
        out[t] = np.asarray(res.params[1:4])
    return out


def boot(x, fun, seed=3, nrep=B):
    rng = np.random.default_rng(seed)
    paises = x["country"].unique()
    reps = {t: [] for t in TAUS}
    for _ in range(nrep):
        pick = rng.choice(paises, size=len(paises), replace=True)
        parts = []
        for k, c in enumerate(pick):
            g = x[x["country"] == c].copy(); g["country"] = f"{c}_{k}"; parts.append(g)
        xb = pd.concat(parts, ignore_index=True)
        try:
            rb = fun(xb)
            rb = rb[0] if isinstance(rb, tuple) else rb
        except Exception:
            continue
        for t in TAUS:
            reps[t].append(rb[t])
    return {t: np.array(v) for t, v in reps.items()}


def reportar(pref, est, reps):
    for t in TAUS:
        tt = int(round(t * 100))
        for j, lab in enumerate(("b1", "b2", "b3")):
            v = reps[t][:, j]
            num(f"{pref}_q{tt}_{lab}", est[t][j])
            num(f"{pref}_q{tt}_{lab}_lo", np.quantile(v, 0.025)); num(f"{pref}_q{tt}_{lab}_hi", np.quantile(v, 0.975))
            p = 2 * min((v <= 0).mean(), (v >= 0).mean())
            num(f"{pref}_q{tt}_{lab}_p", min(1.0, p))
        num(f"{pref}_q{tt}_nboot", len(reps[t]))


def figura(est, reps, nombre):
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.2))
    for j, tit in enumerate(("Fragilidad", "Riesgo de cola", "Interacción")):
        m = [est[t][j] for t in TAUS]
        lo = [np.quantile(reps[t][:, j], 0.025) for t in TAUS]
        hi = [np.quantile(reps[t][:, j], 0.975) for t in TAUS]
        ax[j].fill_between(TAUS, lo, hi, color="#9ecae1", alpha=0.6)
        ax[j].plot(TAUS, m, "o-", color="#08519c")
        ax[j].axhline(0, color="k", lw=0.7)
        ax[j].set_title(tit); ax[j].set_xlabel(r"cuantil $\tau$ del spread")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(p13.FIG, f"{nombre}.{ext}"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    print("p35: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    p14.check_principal(d)
    s = p34.series()
    d = p34.rezagar(d, s, ["PD_w", "DD_w"])
    x = preparar(d)
    num("N", len(x))
    est, b_loc, b_esc = mmqr(x)
    for j, lab in enumerate(("b1", "b2", "b3")):
        num(f"mmqr_loc_{lab}", b_loc[j]); num(f"mmqr_esc_{lab}", b_esc[j])
    reps = boot(x, mmqr); reportar("mmqr", est, reps)
    figura(est, reps, "fig_cuantilica" + ("_nivlag" if NIV else "_lnlag"))
    print("  MMQR listo", flush=True)
    e2 = qr_dummies(x); r2 = boot(x, qr_dummies, seed=4, nrep=199) if os.environ.get("P35_BOOT_QR", "1") == "1" else None
    if r2 is not None:
        reportar("qr", e2, r2)
    print("  QR con dummies listo", flush=True)
    xd = preparar(d, "DD_w_l1", neg=True)
    e3, _, _ = mmqr(xd); r3 = boot(xd, mmqr, seed=5); reportar("mmqr_dd", e3, r3)
    out = os.path.join(HERE, f"paper_p35_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if "_b3" in k or k.startswith("mmqr_loc") or k.startswith("mmqr_esc"):
            print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
