# -*- coding: utf-8 -*-
"""
x6_kernels_hac.py -- EXPERIMENTO: kernel espectral cuadrático (QS) frente a Bartlett en Driscoll-Kraay.

El kernel NO cambia los coeficientes; cambia los errores estándar. La tesis usa Driscoll-Kraay con
kernel de Bartlett y ancho fijo de 3 trimestres (p14.DK). Aquí se comparan, sobre los datos reales:

  bt_3     Bartlett, ancho fijo 3 (el de la tesis)
  bt_and   Bartlett, ancho automático de Andrews (1991), AR(1) sobre la serie de momentos
  bt_nw    Bartlett, ancho automático de Newey-West (1994)
  qs_and   espectral cuadrático, ancho de Andrews (1991)
  qs_nw    espectral cuadrático, ancho de Newey-West (1994)
  pz_and   Parzen, ancho de Andrews (control)
  bt_pw    Bartlett preblanqueado con AR(1) y recoloreado (Andrews y Monahan, 1992)
  qs_pw    espectral cuadrático preblanqueado
  + valores críticos "fixed-b" (Kiefer y Vogelsang, 2005) para bt_and y qs_and

Como la inferencia es sobre un coeficiente a la vez, Driscoll-Kraay se reduce a la varianza de largo
plazo de una serie escalar: u_t = suma sobre países de (X a)_it e_it, con a la fila de (X'X)^-1.
El ancho automático se elige sobre esa serie. Convención de ancho S: Bartlett pesa (1 - j/S) para
j < S (el "3" de linearmodels es S = 4); QS y Parzen usan x = j/S.

Salidas: experimentos/x6_kernels.csv (y _nivlag) y x6_sensibilidad_ancho.png. No se integra.
"""
import os

import numpy as np
import pandas as pd
from scipy import stats

import x0_comun as x0

NUM = {}
METODOS = ("bt_3", "bt_and", "bt_nw", "qs_and", "qs_nw", "pz_and", "bt_pw", "qs_pw")


def num(k, v):
    NUM[k] = float(v)
    return v


# ---------------------------------------------------------------- kernels
def w_bartlett(j, S):
    return np.clip(1.0 - j / S, 0.0, None)


def w_parzen(j, S):
    x = j / S
    return np.where(x <= 0.5, 1 - 6 * x ** 2 + 6 * x ** 3, np.where(x <= 1.0, 2 * (1 - x) ** 3, 0.0))


def w_qs(j, S):
    z = 6.0 * np.pi * (j / S) / 5.0
    return 3.0 / z ** 2 * (np.sin(z) / z - np.cos(z))


KERN = {"bt": w_bartlett, "pz": w_parzen, "qs": w_qs}


def autocov(u):
    """sumas cruzadas u_t u_{t-j}, j = 0..T-1 (sin dividir)."""
    T = len(u)
    return np.array([u[j:] @ u[:T - j] for j in range(T)])


def lrv(g, kern, S):
    """varianza de largo plazo (sin dividir) a partir de las sumas cruzadas g."""
    j = np.arange(1, len(g))
    return g[0] + 2.0 * (KERN[kern](j, max(S, 1e-8)) * g[1:]).sum()


def rho_ar1(u):
    r = (u[1:] @ u[:-1]) / (u[:-1] @ u[:-1])
    return float(np.clip(r, -0.97, 0.97))


def ancho_andrews(u, kern):
    """ancho óptimo de Andrews (1991) con aproximación AR(1) para una serie escalar."""
    T = len(u); r = rho_ar1(u)
    a1 = 4 * r ** 2 / ((1 - r) ** 2 * (1 + r) ** 2); a2 = 4 * r ** 2 / (1 - r) ** 4
    if kern == "bt":
        return 1.1447 * (a1 * T) ** (1 / 3)
    return {"pz": 2.6614, "qs": 1.3221}[kern] * (a2 * T) ** (1 / 5)


def ancho_nw94(g, T, kern):
    """ancho automático de Newey y West (1994) para una serie escalar (g = sumas cruzadas)."""
    q, c, pot = (1, 1.1447, 2 / 9) if kern == "bt" else (2, 1.3221, 2 / 25)
    n = int(np.floor(4 * (T / 100) ** pot))
    j = np.arange(1, n + 1)
    s0 = g[0] + 2 * g[1:n + 1].sum(); sq = 2 * (j ** q * g[1:n + 1]).sum()
    if s0 <= 0:
        return float(n)
    return c * ((sq / s0) ** 2) ** (1 / (2 * q + 1)) * T ** (1 / (2 * q + 1))


def varianzas(u):
    """devuelve {método: (varianza de largo plazo sin escalar, ancho S)} para la serie de momentos u."""
    T = len(u); g = autocov(u); out = {}
    out["bt_3"] = (lrv(g, "bt", 4.0), 4.0)
    for k in ("bt", "qs", "pz"):
        S = ancho_andrews(u, k); out[f"{k}_and"] = (lrv(g, k, S), S)
    for k in ("bt", "qs"):
        S = ancho_nw94(g, T, k); out[f"{k}_nw"] = (lrv(g, k, S), S)
    r = rho_ar1(u); v = u[1:] - r * u[:-1]; gv = autocov(v)
    for k in ("bt", "qs"):
        S = ancho_andrews(v, k)
        out[f"{k}_pw"] = (max(lrv(gv, k, S), 0.0) / (1 - r) ** 2, S)
    return out


# ---------------------------------------------------------------- valores críticos fixed-b
_FB = {}


def fixedb_cv(kern, b, n=200, reps=20000, seed=5):
    """cuantil 95 % de |t| bajo la distribución límite fixed-b, por simulación; rejilla en b."""
    rej = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.75, 1.00])
    if kern not in _FB:
        rng = np.random.default_rng(seed)
        v = rng.standard_normal((reps, n)); m = v.mean(1); v -= m[:, None]
        G = np.stack([(v[:, j:] * v[:, :n - j]).sum(1) for j in range(n)], axis=1)      # reps x n
        cvs = []
        for bb in rej:
            j = np.arange(1, n)
            om = G[:, 0] + 2.0 * (G[:, 1:] * KERN[kern](j, bb * n)[None, :]).sum(1)
            t = np.abs(np.sqrt(n) * m / np.sqrt(np.clip(om, 1e-12, None) / n))
            cvs.append(np.quantile(t, 0.95))
        _FB[kern] = (rej, np.array(cvs))
    rej, cvs = _FB[kern]
    return float(np.interp(np.clip(b, rej[0], rej[-1]), rej, cvs))


# ---------------------------------------------------------------- inferencia de un coeficiente
def momentos(yw, Xw, k, ti):
    """coeficiente k y su serie de momentos por fecha (para Driscoll-Kraay escalar)."""
    XtXi = np.linalg.inv(Xw.T @ Xw)
    b = XtXi @ (Xw.T @ yw); e = yw - Xw @ b
    xe = (Xw @ XtXi[k]) * e
    return b[k], np.bincount(ti, weights=xe)


def tabla(yw, Xw, k, ti, escala, pref):
    b, u = momentos(yw, Xw, k, ti)
    T = len(u)
    num(f"{pref}_b", b); num(f"{pref}_rho_momentos", rho_ar1(u)); num(f"{pref}_T", T)
    for m, (v, S) in varianzas(u).items():
        se = np.sqrt(max(v, 0.0) * escala)
        num(f"{pref}_{m}_ee", se); num(f"{pref}_{m}_ancho", S)
        num(f"{pref}_{m}_p", 2 * stats.norm.sf(abs(b / se)) if se > 0 else np.nan)
        num(f"{pref}_{m}_positiva", float(v > 0))
        if m in ("bt_and", "qs_and"):
            cv = fixedb_cv(m[:2], S / T)
            num(f"{pref}_{m}_cv_fixedb", cv); num(f"{pref}_{m}_rechaza5_fixedb", float(abs(b / se) > cv))
    return b, u


def preparar(dd, y, regs, extra=None):
    cols = np.column_stack([dd[y].to_numpy(float)] + [dd[r].to_numpy(float) for r in regs])
    A, nfe = x0.within(dd, cols, extra=extra)
    ti = pd.factorize(dd["quarter"], sort=True)[0]
    escala = len(dd) / (len(dd) - nfe - len(regs))
    return A[:, 0], A[:, 1:], ti, escala


def validar(dd):
    """igualdad con linearmodels para los tres kernels, en la regresión principal."""
    from linearmodels.panel import PanelOLS
    yw, Xw, ti, esc = preparar(dd, "ln_EMBI", ["J_c", "T_c", "JxT"])
    idx = dd.set_index(["country", "t"])
    peor = 0.0
    for kern, nombre, bw in (("bt", "bartlett", 3), ("pz", "parzen", 5), ("qs", "qs", 5)):
        m = PanelOLS.from_formula("ln_EMBI ~ J_c + T_c + JxT + EntityEffects + TimeEffects", idx).fit(
            cov_type="kernel", kernel=nombre, bandwidth=bw)
        for k, n_ in enumerate(("J_c", "T_c", "JxT")):
            b, u = momentos(yw, Xw, k, ti)
            S = bw if kern == "qs" else bw + 1
            se = np.sqrt(lrv(autocov(u), kern, S) * esc)
            peor = max(peor, abs(se / m.std_errors[n_] - 1), abs(b / m.params[n_] - 1))
    num("validacion_peor_dif_relativa", peor)
    print(f"   validación contra linearmodels: peor diferencia relativa = {peor:.2e}")
    assert peor < 1e-6, peor


def sensibilidad(dd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    yw, Xw, ti, esc = preparar(dd, "ln_EMBI", ["J_c", "T_c", "JxT"])
    anchos = np.arange(1, 25)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, k, tit in ((axs[0], 0, "Fragilidad bancaria"), (axs[1], 1, "Riesgo de cola")):
        b, u = momentos(yw, Xw, k, ti); g = autocov(u)
        for kern, lab, col in (("bt", "Bartlett", "#1f4e79"), ("qs", "Espectral cuadrático", "#d9822b")):
            p = [2 * stats.norm.sf(abs(b) / np.sqrt(max(lrv(g, kern, S), 1e-30) * esc)) for S in anchos]
            ax.plot(anchos, p, color=col, lw=1.8, label=lab)
            for S, pp in zip(anchos, p):
                num(f"sens_{('b1', 'b2')[k]}_{kern}_S{S}_p", pp)
        ax.axhline(0.05, color="gray", lw=0.8, ls="--"); ax.axvline(4, color="gray", lw=0.8, ls=":")
        ax.set_title(tit, fontsize=10); ax.set_xlabel("ancho de banda S (trimestres)")
    axs[0].set_ylabel("p-valor (Driscoll-Kraay)"); axs[0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(x0.HERE, f"x6_sensibilidad_ancho{x0.SFX}.png"), dpi=140)
    plt.close(fig)


def main():
    print("x6: forma", "niveles" if x0.NIV else "logs")
    dd = x0.datos()
    assert len(dd) == 765
    validar(dd)
    # 1. regresión principal
    yw, Xw, ti, esc = preparar(dd, "ln_EMBI", ["J_c", "T_c", "JxT"])
    for k, lab in enumerate(("b1", "b2", "b3")):
        tabla(yw, Xw, k, ti, esc, f"principal_{lab}")
    # 2. primeras diferencias (como p21): cambio del spread sobre cambio rezagado de cada riesgo
    q = pd.PeriodIndex(dd["quarter"], freq="Q"); dd["_qn"] = q.year * 4 + q.quarter
    g = dd.groupby("country"); consec = (dd["_qn"] - g["_qn"].shift(1)) == 1
    for c in ("ln_EMBI", "J_c", "T_c", "JxT"):
        dd["d_" + c] = (dd[c] - g[c].shift(1)).where(consec)
    fd = dd.dropna(subset=["d_ln_EMBI", "d_J_c", "d_T_c", "d_JxT"])
    yw, Xw, ti, esc = preparar(fd, "d_ln_EMBI", ["d_J_c", "d_T_c", "d_JxT"])
    for k, lab in enumerate(("b1", "b2", "b3")):
        tabla(yw, Xw, k, ti, esc, f"difs_{lab}")
    # 3. mismo trimestre con spread de cierre: cierre(t-1) - cierre(t-2) sobre el cambio de J en t-1
    alt = pd.read_csv(os.path.join(x0.BBG, "embi_trimestral_alternativo.csv"))[["country", "quarter", "EMBI_eop5"]]
    alt = alt[alt["EMBI_eop5"] > 0].copy()
    alt["y_eop"] = alt["EMBI_eop5"] if x0.NIV else np.log(alt["EMBI_eop5"])
    qa = pd.PeriodIndex(alt["quarter"], freq="Q"); alt["_qn"] = qa.year * 4 + qa.quarter
    alt = alt.sort_values(["country", "_qn"]); ga = alt.groupby("country")
    ok = ((alt["_qn"] - ga["_qn"].shift(1)) == 1) & ((alt["_qn"] - ga["_qn"].shift(2)) == 2)
    alt["d_eop_l1"] = (ga["y_eop"].shift(1) - ga["y_eop"].shift(2)).where(ok)
    mt = fd.merge(alt[["country", "quarter", "d_eop_l1"]], on=["country", "quarter"], how="inner").dropna(subset=["d_eop_l1"])
    yw, Xw, ti, esc = preparar(mt, "d_eop_l1", ["d_J_c", "d_T_c"])
    tabla(yw, Xw, 0, ti, esc, "mismotrim_b1"); num("mismotrim_N", len(mt))
    # 4. riesgo de cola sobre el modelo al estilo de Chari (fragilidad + sus controles)
    import p14_arbitro_lnlag as p14
    d14, _ = p14.base()
    ctr = [c for c in ("fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp") if c in d14.columns]
    ch = d14.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + ctr).copy()
    ch["J_c"] = ch["ln_JLoss_l1"] - ch["ln_JLoss_l1"].mean(); ch["T_c"] = ch["D_l1"] - ch["D_l1"].mean()
    yw, Xw, ti, esc = preparar(ch, "ln_EMBI", ["J_c", "T_c"] + ctr)
    tabla(yw, Xw, 1, ti, esc, "chari_b2"); tabla(yw, Xw, 0, ti, esc, "chari_b1"); num("chari_N", len(ch)); num("chari_n_controles", len(ctr))
    # 5. precedencia fragilidad(t-1) -> riesgo de cola(t)
    import x1_comprobaciones as x1
    p = x1.panel_cruzado(); p = p[p["country"].isin(dd["country"].unique())].dropna(subset=["D", "J_l1", "D_l1"])
    yw, Xw, ti, esc = preparar(p, "D", ["J_l1", "D_l1"])
    tabla(yw, Xw, 0, ti, esc, "precedencia_JD"); num("precedencia_N", len(p))
    sensibilidad(x0.datos())
    for k, v in NUM.items():
        if not k.startswith("sens_"):
            print(f"  {k:44s} {v: .4f}")
    x0.guardar(NUM, "x6_kernels")


if __name__ == "__main__":
    main()
