# -*- coding: utf-8 -*-
"""
p30_influencia_paises.py -- influencia de países individuales sobre la especificación PRINCIPAL
(log-log rezagada, panel Panel_bloomberg_embiext.csv, 13 países; JLOSS_FORMA=nivlag la repite en
niveles). Convierte en análisis la salvedad del leave-one-out (b1 depende de Turquía, b2 de Polonia):

  1. Pendientes país por país sobre variables sin la media transversal de cada trimestre, estimador
     mean-group y pruebas de homogeneidad de pendientes (Pesaran-Yamagata, Swamy clásico y Swamy/Q
     con varianzas HAC).
  2. Palanca: participación de cada país en la variación within (doble demeaning) de J, D y el
     spread, descomposición exacta (FWL) del coeficiente agrupado por país y DFBETA.
  3. Tendencias lineales por país y cargas país-específicas de factores globales (VIX, HY).
  4. Medición de JLoss frente a su piso (2,16): z-score within, percentil, dummy de piso, fuera del piso.
  5. Spreads bajos y forma funcional: excluir EMBI < 60 / < 100 pb, Box-Cox (lambda = 0,44), Polonia
     antes/después de 2019Q3.
  6. Composición: sin EMBI empalmado con FMI (GFSR), sin trimestres con pocos bancos, desde 2010,
     D interactuado con muestra de entrenamiento corta del GaR.
  7. Wild cluster bootstrap (Webb, B=999) de las filas principales de los bloques 3 a 5.

Salidas: bbg/paper_influencia_numeros.csv (o _nivlag) y fig_pendientes_pais_lnlag (vía p13.save).
Reutiliza p13 (datos, fit, save) y p14 (wild_boot, DK). No modifica ningún archivo canónico.
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
from scipy import stats

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
from causal_core import demean2

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
CORTOS = ["philippines", "indonesia", "southafrica"]
PISO = 2.16            # piso de JLoss (cota inferior de la calibración; 12 obs. quedan por debajo)
TOL = 0.02             # "en el piso": JLoss_{t-1} <= PISO * (1 + TOL)
LAMBDA = 0.44          # óptimo de la verosimilitud perfilada Box-Cox reportado en la tesis
Q_POL = "2019Q3"       # quiebre de Polonia: primer trimestre con EMBI < 40 pb (visual, no buscado)
B_WILD = 999
COEF = (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3"))
NUM = {}
WILD = []              # (prefijo, datos, y, regresores) de las filas que van al bootstrap


def num(k, v):
    NUM[k] = float(v)
    return v


def qn(s):
    q = pd.PeriodIndex(s, freq="Q")
    return np.asarray(q.year * 4 + q.quarter)


def reg(d, pref, extra=None, y=None, wild=False, verb=True):
    """especificación principal sobre `d` (con columnas extra opcionales); guarda b1-b3 y p DK."""
    d = d.copy()
    if y is not None:
        d["ln_EMBI"] = y
    m, dd = p13.fit(d, extra=extra)
    num(f"{pref}_N", m.nobs); num(f"{pref}_G", dd["country"].nunique())
    for n_, lab in COEF:
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_se", m.std_errors[n_])
        num(f"{pref}_{lab}_p", m.pvalues[n_])
    if wild:
        WILD.append((pref, dd, ["J_c", "T_c", "JxT"] + list(extra or [])))
    if verb:
        print(f"    {pref:34s} N={int(m.nobs):4d}  " + "  ".join(
            f"{lab}={m.params[n_]:+.4f} (p={m.pvalues[n_]:.3f})" for n_, lab in COEF))
    return m, dd


def con_extras(d, tend=False, vix=False, hy=False):
    """agrega tendencias lineales por país y/o cargas país-específicas de VIX y HY. Se omite un país
    de referencia en cada familia: la suma de las N columnas es colineal con los efectos de tiempo."""
    d = d.copy()
    paises = sorted(d["country"].unique())[1:]
    t = (qn(d["quarter"]) - qn(d["quarter"]).mean()) / 4.0
    fam = []
    if tend:
        fam.append(("tr", t))
    if vix:
        fam.append(("vix", d["VIX"] if NIV else np.log(d["VIX"])))
    if hy:
        fam.append(("hy", d["US_HY_spread"] if NIV else np.log(d["US_HY_spread"])))
    cols = []
    for pre, v in fam:
        v = np.asarray(v, dtype=float); v = v - v.mean()
        for c in paises:
            d[f"{pre}_{c}"] = v * (d["country"] == c).values
            cols.append(f"{pre}_{c}")
    return d, cols


# ================================================================ 1. pendientes por país
def bloque_pendientes(d, m0):
    print("  [1] pendientes país por país")
    x = d[["country", "quarter", "ln_EMBI", "ln_JLoss_l1", "D_l1"]].copy()
    x["J"] = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean()
    x["D"] = x["D_l1"] - x["D_l1"].mean()
    x["JD"] = x["J"] * x["D"]
    x["y"] = x["ln_EMBI"]
    nq = x.groupby("quarter")["y"].transform("size")
    num("pp_obs_trimestre_un_pais", (nq == 1).sum())
    x = x[nq > 1].copy()                                 # trimestres con un solo país: sin información
    for c in ("y", "J", "D", "JD"):
        x[c] = x[c] - x.groupby("quarter")[c].transform("mean")
    filas, V2, XX, Xy, yy = [], {}, {}, {}, {}
    for pais, g in x.groupby("country"):
        g = g.sort_values("quarter")
        T = len(g); L = int(np.floor(4 * (T / 100.0) ** (2.0 / 9.0)))
        X = sm.add_constant(g[["J", "D"]])
        r = sm.OLS(g["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": L})
        r0 = sm.OLS(g["y"], X).fit()
        ri = sm.OLS(g["y"], sm.add_constant(g[["J", "D", "JD"]])).fit(cov_type="HAC", cov_kwds={"maxlags": L})
        filas.append(dict(pais=pais, T=T, b1=r.params["J"], se1=r.bse["J"], b2=r.params["D"], se2=r.bse["D"],
                          b1_i=ri.params["J"], b2_i=ri.params["D"], b3_i=ri.params["JD"], se3_i=ri.bse["JD"],
                          s2=r0.scale))
        V2[pais] = r.cov_params().loc[["J", "D"], ["J", "D"]].values
        Xd = (g[["J", "D"]] - g[["J", "D"]].mean()).values; yd = (g["y"] - g["y"].mean()).values
        XX[pais], Xy[pais], yy[pais] = Xd.T @ Xd, Xd.T @ yd, (Xd, yd)
    P = pd.DataFrame(filas).set_index("pais")
    for pais, r in P.iterrows():
        num(f"pp_{pais}_T", r["T"])
        for k in ("b1", "se1", "b2", "se2", "b3_i", "se3_i"):
            num(f"pp_{pais}_{k}", r[k])
        num(f"pp_{pais}_b1_p", 2 * stats.norm.sf(abs(r["b1"] / r["se1"])))
        num(f"pp_{pais}_b2_p", 2 * stats.norm.sf(abs(r["b2"] / r["se2"])))
        print(f"    {pais:12s} T={int(r['T']):3d}  b1={r['b1']:+.4f} ({r['se1']:.4f})  b2={r['b2']:+.4f} ({r['se2']:.4f})"
              f"  | con interacción: b3={r['b3_i']:+.4f} ({r['se3_i']:.4f})")
    # mean-group (Pesaran y Smith, 1995): promedio simple, ee no paramétrico = sd / raíz(N)
    mg = {}
    for tag, sub in (("todos", P), ("T40", P[P["T"] >= 40]), ("sin_turquia", P.drop("turkey")),
                     ("sin_polonia", P.drop("poland"))):
        num(f"mg_{tag}_G", len(sub))
        for k in ("b1", "b2", "b3_i"):
            b = sub[k].mean(); se = sub[k].std(ddof=1) / np.sqrt(len(sub))
            lab = k.replace("_i", "")
            num(f"mg_{tag}_{lab}", b); num(f"mg_{tag}_{lab}_se", se)
            num(f"mg_{tag}_{lab}_p", 2 * stats.t.sf(abs(b / se), len(sub) - 1))
            mg[(tag, lab)] = (b, se)
        num(f"mg_{tag}_b1_mediana", sub["b1"].median()); num(f"mg_{tag}_b2_mediana", sub["b2"].median())
        num(f"mg_{tag}_b1_n_pos", (sub["b1"] > 0).sum()); num(f"mg_{tag}_b2_n_pos", (sub["b2"] > 0).sum())
        print(f"    MG {tag:12s} G={len(sub):2d}  b1={mg[(tag,'b1')][0]:+.4f} ({mg[(tag,'b1')][1]:.4f})"
              f"  b2={mg[(tag,'b2')][0]:+.4f} ({mg[(tag,'b2')][1]:.4f})  b3={mg[(tag,'b3')][0]:+.4f} ({mg[(tag,'b3')][1]:.4f})")
    # agrupado comparable (sin interacción) sobre los mismos datos: EF de país tras quitar la media transversal
    k = 2; N = len(P)
    bfe = np.linalg.solve(sum(XX.values()), sum(Xy.values()))
    num("pp_agrupado_sinint_b1", bfe[0]); num("pp_agrupado_sinint_b2", bfe[1])
    bi = {p_: P.loc[p_, ["b1", "b2"]].values.astype(float) for p_ in P.index}
    # Pesaran y Yamagata (2008): varianza sigma_i^2 de los residuos del EF agrupado; versión ajustada
    # con media k y varianza 2k(T_i-k-1)/(T_i+1) por país (panel desbalanceado).
    s2t = {p_: float(((yy[p_][1] - yy[p_][0] @ bfe) ** 2).sum() / (P.loc[p_, "T"] - 1)) for p_ in P.index}
    bw = np.linalg.solve(sum(XX[p_] / s2t[p_] for p_ in P.index), sum(Xy[p_] / s2t[p_] for p_ in P.index))
    dz = np.array([(bi[p_] - bw) @ (XX[p_] / s2t[p_]) @ (bi[p_] - bw) for p_ in P.index])
    delta = np.sqrt(N) * (dz.mean() - k) / np.sqrt(2 * k)
    Ti = P["T"].values.astype(float)
    dadj = ((dz - k) / np.sqrt(2 * k * (Ti - k - 1) / (Ti + 1))).sum() / np.sqrt(N)
    num("hom_PY_delta", delta); num("hom_PY_delta_p", stats.norm.sf(delta))
    num("hom_PY_delta_adj", dadj); num("hom_PY_delta_adj_p", stats.norm.sf(dadj))
    # Swamy (1970) clásico: sigma_i^2 de cada regresión individual, chi2 con k(N-1) g.l.
    Vi = {p_: np.linalg.inv(XX[p_] / P.loc[p_, "s2"]) for p_ in P.index}
    for tag, VV in (("swamy", Vi), ("swamy_hac", V2)):
        W = {p_: np.linalg.inv(VV[p_]) for p_ in P.index}
        b_ = np.linalg.solve(sum(W.values()), sum(W[p_] @ bi[p_] for p_ in P.index))
        S = sum((bi[p_] - b_) @ W[p_] @ (bi[p_] - b_) for p_ in P.index)
        num(f"hom_{tag}_chi2", S); num(f"hom_{tag}_gl", k * (N - 1)); num(f"hom_{tag}_p", stats.chi2.sf(S, k * (N - 1)))
    # Q de Cochran por coeficiente con ee HAC (qué pendiente es la heterogénea), con y sin el país influyente
    for lab, se, fuera in (("b1", "se1", "turkey"), ("b2", "se2", "poland")):
        for tag, sub in (("", P), ("_sin_influyente", P.drop(fuera))):
            w = 1 / sub[se] ** 2; bq = (w * sub[lab]).sum() / w.sum()
            Q = (w * (sub[lab] - bq) ** 2).sum()
            num(f"hom_Q_{lab}{tag}", Q); num(f"hom_Q_{lab}{tag}_p", stats.chi2.sf(Q, len(sub) - 1))
            num(f"hom_Q_{lab}{tag}_media_precision", bq); num(f"hom_Q_{lab}{tag}_media_precision_se", w.sum() ** -0.5)
    print(f"    PY delta={delta:.2f} (p={stats.norm.sf(delta):.4f})  delta_adj={dadj:.2f}  "
          f"Swamy p={NUM['hom_swamy_p']:.4f}  Swamy-HAC p={NUM['hom_swamy_hac_p']:.4f}  "
          f"Q b1 p={NUM['hom_Q_b1_p']:.4f}  Q b2 p={NUM['hom_Q_b2_p']:.4f}")
    fig_pendientes(P, m0, mg)
    return P


def fig_pendientes(P, m0, mg):
    """pendiente de cada riesgo país por país (IC 95 % HAC), con el agrupado EF y el mean-group."""
    import matplotlib.pyplot as plt
    orden = P.sort_values("T", ascending=False).index
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.4), sharey=True)
    for ax, b, se, v, tit in ((axs[0], "b1", "se1", "J_c", "Fragilidad bancaria"), (axs[1], "b2", "se2", "T_c", "Riesgo de cola")):
        ax.axvline(0, color=p13.INK2, lw=0.8)
        ax.axvline(m0.params[v], color=p13.INK, lw=1.4, label=f"EF agrupado ({m0.params[v]:.3f})")
        ax.axvline(mg[("todos", b)][0], color=p13.RED, lw=1.4, ls="--", label=f"mean-group ({mg[('todos', b)][0]:.3f})")
        for i, pais in enumerate(orden):
            bb, ss = P.loc[pais, b], P.loc[pais, se]
            ax.plot([bb - 1.96 * ss, bb + 1.96 * ss], [i, i], color=p13.BLUE, lw=1.8)
            ax.plot(bb, i, "o", color=p13.BLUE, ms=5)
        ax.set_title(tit, fontsize=10); ax.legend(fontsize=7.5, loc="lower right")
        ax.set_xlabel("pendiente del país (pb), IC 95 % HAC" if NIV else "pendiente del país, IC 95 % HAC")
    axs[0].set_yticks(range(len(orden)))
    axs[0].set_yticklabels([f"{p13.NOMBRE[c]} ({int(P.loc[c, 'T'])})" for c in orden], fontsize=8)
    axs[0].invert_yaxis()
    p13.save(fig, "fig_pendientes_pais_lnlag")


# ================================================================ 2. palanca
def bloque_palanca(d, m0, dd0, P):
    print("  [2] palanca: variación within, contribución FWL y DFBETA")
    w = demean2(dd0, ["ln_EMBI", "J_c", "T_c", "JxT"], iters=60)
    w["country"] = dd0["country"].values
    tot = {c: (w[c] ** 2).sum() for c in ("ln_EMBI", "J_c", "T_c", "JxT")}
    X = w[["J_c", "T_c", "JxT"]].values; y = w["ln_EMBI"].values
    bchk = np.linalg.lstsq(X, y, rcond=None)[0]
    assert abs(bchk[0] - m0.params["J_c"]) < 1e-4 and abs(bchk[1] - m0.params["T_c"]) < 1e-4, bchk
    # FWL: b_k = suma_i c_i con c_i = suma_t r_it y_it / suma r^2 (r = regresor k parcializado de los otros)
    for j, lab in ((0, "b1"), (1, "b2"), (2, "b3")):
        otros = [i for i in range(3) if i != j]
        r = X[:, j] - X[:, otros] @ np.linalg.lstsq(X[:, otros], X[:, j], rcond=None)[0]
        w["r_" + lab] = r; w["ry_" + lab] = r * y
    for pais, g in w.groupby("country"):
        num(f"pal_{pais}_share_J", (g["J_c"] ** 2).sum() / tot["J_c"])
        num(f"pal_{pais}_share_D", (g["T_c"] ** 2).sum() / tot["T_c"])
        num(f"pal_{pais}_share_JxD", (g["JxT"] ** 2).sum() / tot["JxT"])
        num(f"pal_{pais}_share_spread", (g["ln_EMBI"] ** 2).sum() / tot["ln_EMBI"])
        num(f"pal_{pais}_share_obs", len(g) / len(w))
        for lab in ("b1", "b2", "b3"):
            sr = (w["r_" + lab] ** 2).sum()
            num(f"pal_{pais}_peso_{lab}", (g["r_" + lab] ** 2).sum() / sr)        # peso en la variación parcializada
            num(f"pal_{pais}_contrib_{lab}", g["ry_" + lab].sum() / sr)            # aporte aditivo al coeficiente
    for lab, n_ in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        s = sum(NUM[f"pal_{p_}_contrib_{lab}"] for p_ in P.index)
        assert abs(s - m0.params[n_]) < 1e-4, (lab, s)
    for pais in P.index:
        m, _ = p13.fit(d[d["country"] != pais])
        for n_, lab in COEF:
            num(f"loo_{pais}_{lab}", m.params[n_]); num(f"loo_{pais}_{lab}_p", m.pvalues[n_])
            num(f"dfbeta_{pais}_{lab}", (m0.params[n_] - m.params[n_]) / m0.std_errors[n_])
        print(f"    {pais:12s} shareJ={NUM[f'pal_{pais}_share_J']:.3f} shareD={NUM[f'pal_{pais}_share_D']:.3f} "
              f"shareY={NUM[f'pal_{pais}_share_spread']:.3f} | contrib b1={NUM[f'pal_{pais}_contrib_b1']:+.4f} "
              f"b2={NUM[f'pal_{pais}_contrib_b2']:+.4f} | DFBETA b1={NUM[f'dfbeta_{pais}_b1']:+.2f} "
              f"b2={NUM[f'dfbeta_{pais}_b2']:+.2f} b3={NUM[f'dfbeta_{pais}_b3']:+.2f}")
    # ¿la influencia sigue a la palanca? correlación entre |DFBETA| y participación en la variación
    sj = [NUM[f"pal_{p_}_share_J"] for p_ in P.index]; sd_ = [NUM[f"pal_{p_}_share_D"] for p_ in P.index]
    num("pal_corr_absdfbeta_b1_shareJ", np.corrcoef(np.abs([NUM[f"dfbeta_{p_}_b1"] for p_ in P.index]), sj)[0, 1])
    num("pal_corr_absdfbeta_b2_shareD", np.corrcoef(np.abs([NUM[f"dfbeta_{p_}_b2"] for p_ in P.index]), sd_)[0, 1])
    # sin Turquía y sin Polonia a la vez
    reg(d[~d["country"].isin(["turkey", "poland"])], "loo_sin_turquia_polonia")


# ================================================================ 3. tendencias y factores comunes
def bloque_factores(d):
    print("  [3] tendencias por país y cargas de factores globales")
    specs = (("base", {}), ("tend", dict(tend=True)), ("vix", dict(vix=True)), ("hy", dict(hy=True)),
             ("vixhy", dict(vix=True, hy=True)), ("tend_vixhy", dict(tend=True, vix=True, hy=True)))
    for mtag, sub in (("todos", d), ("sin_turquia", d[d["country"] != "turkey"]), ("sin_polonia", d[d["country"] != "poland"])):
        for stag, kw in specs:
            x, cols = con_extras(sub, **kw)
            reg(x, f"fac_{stag}_{mtag}", extra=cols,
                wild=(stag in ("tend", "vixhy", "tend_vixhy") and mtag in ("todos", "sin_turquia")))


# ================================================================ 4. medición de JLoss y su piso
def bloque_piso(d):
    print("  [4] piso de JLoss y unidades alternativas")
    J = d["JLoss_l1"]
    num("piso_valor", PISO); num("piso_min_JLoss", J.min()); num("piso_n_bajo_piso", (J < PISO * 0.999).sum())
    num("piso_share_2pct_del_minimo", (J <= J.min() * 1.02).mean())
    for tol in (0.02, 0.05, 0.10):
        num(f"piso_share_{int(tol*100)}pct", (J <= PISO * (1 + tol)).mean())
    for q in (5, 25, 50, 75, 95):
        num(f"piso_p{q}_JLoss", np.percentile(J, q))
    for pais, g in d.groupby("country"):
        num(f"piso_{pais}_share_2pct", (g["JLoss_l1"] <= PISO * 1.02).mean())
        num(f"piso_{pais}_mediana", g["JLoss_l1"].median())
        num(f"piso_{pais}_sd_within_lnJ", g["ln_JLoss_l1"].std())
        print(f"    {pais:12s} en el piso (2 %)={NUM[f'piso_{pais}_share_2pct']:.2f}  mediana={g['JLoss_l1'].median():.2f}")
    sdw = float((d["ln_JLoss_l1"] - d.groupby("country")["ln_JLoss_l1"].transform("mean")).std())
    num("piso_sd_within_J", sdw)
    num("piso_p50_a_p75_lnJ", (np.log(np.percentile(J, 75)) - np.log(np.percentile(J, 50))) if not NIV
        else np.percentile(J, 75) - np.percentile(J, 50))
    # (a) z-score within-país: una unidad = una desviación estándar propia del país
    a = d.copy(); g = a.groupby("country")["ln_JLoss_l1"]
    a["ln_JLoss_l1"] = (a["ln_JLoss_l1"] - g.transform("mean")) / g.transform("std")
    reg(a, "med_zscore", wild=True)
    # (b) percentil en el panel: una unidad = del mínimo al máximo; 0,10 = diez puntos percentiles
    b = d.copy(); b["ln_JLoss_l1"] = b["JLoss_l1"].rank(pct=True)
    reg(b, "med_rank", wild=True)
    b2 = d.copy(); b2["ln_JLoss_l1"] = b2.groupby("country")["JLoss_l1"].rank(pct=True)
    reg(b2, "med_rank_within")
    for tol in (0.02, 0.05):
        tg = f"{int(tol*100)}pct"
        on = d["JLoss_l1"] <= PISO * (1 + tol)
        num(f"med_piso_{tg}_n_en_piso", on.sum())
        # (c1) fragilidad binaria: una unidad = estar fuera del piso
        c1 = d.copy(); c1["ln_JLoss_l1"] = (~on).astype(float)
        reg(c1, f"med_fuera_binaria_{tg}", wild=(tol == TOL))
        # (c2) dummy de piso y su interacción con D, sumadas a la especificación principal
        c2 = d.copy(); c2["piso"] = on.astype(float)
        c2["pisoxD"] = c2["piso"] * (c2["D_l1"] - c2["D_l1"].mean())
        m, _ = reg(c2, f"med_dummy_piso_{tg}", extra=["piso", "pisoxD"])
        for v in ("piso", "pisoxD"):
            num(f"med_dummy_piso_{tg}_{v}", m.params[v]); num(f"med_dummy_piso_{tg}_{v}_p", m.pvalues[v])
        # (d) solo observaciones fuera del piso
        reg(d[~on], f"med_solo_fuera_{tg}", wild=(tol == TOL))
        reg(d[on], f"med_solo_en_piso_{tg}")


# ================================================================ 5. spreads bajos y forma funcional
def bloque_spreads(d, P):
    print("  [5] spreads bajos, Box-Cox y Polonia")
    for u in (60, 100):
        bajo = d["EMBI_bps"] < u
        num(f"bajo{u}_n", bajo.sum()); num(f"bajo{u}_n_polonia", (bajo & (d["country"] == "poland")).sum())
        reg(d[~bajo], f"sp_sin_embi_{u}", wild=True)
    num("sp_polonia_embi_min", d.loc[d["country"] == "poland", "EMBI_bps"].min())
    # Box-Cox del spread con los mismos regresores; efecto reexpresado como semielasticidad en la mediana
    E = d["EMBI_bps"]
    for lam in (LAMBDA, 0.5):
        tg = "boxcox" if lam == LAMBDA else "raiz"
        m, _ = reg(d, f"sp_{tg}", y=(E ** lam - 1) / lam, wild=(lam == LAMBDA))
        for n_, lab in COEF:   # d ln EMBI = d y_bc / EMBI^lambda
            num(f"sp_{tg}_{lab}_semielast_mediana", m.params[n_] / np.median(E) ** lam)
            num(f"sp_{tg}_{lab}_t", m.tstats[n_])
    num("sp_boxcox_lambda", LAMBDA); num("sp_embi_mediana", np.median(E))
    sp = d[d["country"] != "poland"]
    reg(sp, "sp_boxcox_sin_polonia", y=(sp["EMBI_bps"] ** LAMBDA - 1) / LAMBDA)
    # Polonia antes / desde 2019Q3 (el EMBI polaco cae bajo 40 pb y toca 15 pb en 2021)
    pol = d["country"] == "poland"; post = qn(d["quarter"]) >= qn(pd.Series([Q_POL]))[0]
    num("pol_n_pre", (pol & ~post).sum()); num("pol_n_post", (pol & post).sum())
    reg(d[~(pol & post)], "sp_polonia_solo_pre")
    reg(d[~(pol & ~post)], "sp_polonia_solo_post")
    x = d[["country", "quarter", "ln_EMBI", "ln_JLoss_l1", "D_l1"]].copy()
    x = x[x.groupby("quarter")["ln_EMBI"].transform("size") > 1]
    for c in ("ln_EMBI", "ln_JLoss_l1", "D_l1"):
        x[c] = x[c] - x.groupby("quarter")[c].transform("mean")
    xp = x[x["country"] == "poland"]
    for tg, g in (("pre", xp[qn(xp["quarter"]) < qn(pd.Series([Q_POL]))[0]]), ("post", xp[qn(xp["quarter"]) >= qn(pd.Series([Q_POL]))[0]])):
        r = sm.OLS(g["ln_EMBI"], sm.add_constant(g[["ln_JLoss_l1", "D_l1"]])).fit(
            cov_type="HAC", cov_kwds={"maxlags": int(np.floor(4 * (len(g) / 100.0) ** (2.0 / 9.0)))})
        num(f"pol_{tg}_T", len(g))
        for v, lab in (("ln_JLoss_l1", "b1"), ("D_l1", "b2")):
            num(f"pol_{tg}_{lab}", r.params[v]); num(f"pol_{tg}_{lab}_se", r.bse[v])
        print(f"    Polonia {tg:4s} T={len(g):2d} b1={r.params['ln_JLoss_l1']:+.4f} ({r.bse['ln_JLoss_l1']:.4f}) "
              f"b2={r.params['D_l1']:+.4f} ({r.bse['D_l1']:.4f})")


# ================================================================ 6. composición
def bloque_composicion(d):
    print("  [6] composición de la muestra")
    num("comp_n_gfsr", (d["embi_source"] == "GFSR").sum())
    reg(d[d["embi_source"] != "GFSR"], "comp_sin_gfsr")
    reg(d[~d["country"].isin(CORTOS)], "comp_sin_cortos")
    # banderas rezagadas (JLoss y D entran en t-1): pocos bancos y tamaño de la muestra de entrenamiento
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])[["country", "quarter", "below_min_banks", "n_train", "n_banks"]]
    raw["_qn"] = qn(raw["quarter"]) + 1
    raw = raw.rename(columns={"below_min_banks": "pocos_l1", "n_train": "n_train_l1", "n_banks": "n_banks_l1"})
    x = d.copy(); x["_qn"] = qn(x["quarter"])
    x = x.merge(raw.drop(columns="quarter"), on=["country", "_qn"], how="left")
    assert len(x) == len(d) and x["n_train_l1"].notna().all() and x["pocos_l1"].notna().all()
    pocos = x["pocos_l1"].astype(bool)
    num("comp_n_pocos_bancos_l1", pocos.sum()); num("comp_n_pocos_bancos_t", d["below_min_banks"].astype(bool).sum())
    reg(x[~pocos], "comp_sin_pocos_bancos")
    reg(d[qn(d["quarter"]) >= 2010 * 4 + 1], "comp_desde_2010")
    # D interactuado con muestra de entrenamiento corta (cuartil inferior de n_train en t-1). n_train
    # solo depende del trimestre (GaR en pseudo tiempo real), así que la dummy en nivel la absorben
    # los efectos de tiempo y solo entra su interacción con D.
    u = x["n_train_l1"].quantile(0.25)
    x["ntr_bajo"] = (x["n_train_l1"] <= u).astype(float)
    x["ntr_bajoxD"] = x["ntr_bajo"] * (x["D_l1"] - x["D_l1"].mean())
    num("comp_ntrain_umbral_p25", u); num("comp_ntrain_n_bajo", x["ntr_bajo"].sum())
    num("comp_ntrain_ultimo_trimestre_bajo", x.loc[x["ntr_bajo"] == 1, "_qn"].max() / 4.0)
    m, _ = reg(x, "comp_ntrain", extra=["ntr_bajoxD"])
    num("comp_ntrain_bajoxD", m.params["ntr_bajoxD"]); num("comp_ntrain_bajoxD_p", m.pvalues["ntr_bajoxD"])
    w = pd.Series(0.0, index=m.params.index); w[["T_c", "ntr_bajoxD"]] = 1.0
    b = float(w @ m.params); se = float((w @ m.cov @ w) ** 0.5)
    num("comp_ntrain_b2_muestra_corta", b); num("comp_ntrain_b2_muestra_corta_p", 2 * stats.norm.sf(abs(b / se)))
    reg(x[x["ntr_bajo"] == 0], "comp_ntrain_solo_largo")


# ================================================================ 7. wild cluster bootstrap
def bloque_wild():
    print(f"  [7] wild cluster bootstrap (Webb, B={B_WILD})")
    for pref, dd, regs in WILD:
        ps = []
        for n_, lab in COEF:
            p, _ = p14.wild_boot(dd, "ln_EMBI", regs, n_, B=B_WILD, weights="webb")
            num(f"{pref}_{lab}_p_wild", p); ps.append(f"{lab} p_wild={p:.3f} (DK {NUM[f'{pref}_{lab}_p']:.3f})")
        print(f"    {pref:34s} " + "  ".join(ps))


def main():
    print("p30: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d = p13.datos()
    m0, dd0 = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4, (m0.nobs, m0.params["JxT"])
    m0, dd0 = reg(d, "principal", wild=True)
    P = bloque_pendientes(d, m0)
    bloque_palanca(d, m0, dd0, P)
    bloque_factores(d)
    bloque_piso(d)
    bloque_spreads(d, P)
    bloque_composicion(d)
    bloque_wild()
    out = os.path.join(HERE, f"paper_influencia_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    print("->", out, f"({len(NUM)} cifras)")


if __name__ == "__main__":
    main()
