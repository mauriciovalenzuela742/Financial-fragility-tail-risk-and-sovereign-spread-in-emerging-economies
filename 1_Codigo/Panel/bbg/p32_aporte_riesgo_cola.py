# -*- coding: utf-8 -*-
"""
p32_aporte_riesgo_cola.py -- ¿qué AGREGA el riesgo de cola del crecimiento al modelo de Chari et al.?

Que la fragilidad bancaria (JLoss) importa para el spread soberano ya lo establecen Chari et al.
(2024). La pregunta propia de la tesis es qué agrega el riesgo de cola doméstico (D = -GaR) a ese
modelo y qué ocurre cuando ambos riesgos coinciden. Familia de contrastes DECLARADA EX ANTE (se
corren exactamente estos y se reportan todos, sea cual sea el resultado):

  1. Información incremental sobre el modelo de Chari: se parte de la especificación estilo Chari
     de p14.tabla_chari (columna 3: fragilidad rezagada + sus controles, EF de país y tiempo), se
     agrega D_{t-1} y luego D y la interacción. Coeficientes con p DK, cluster por país y wild
     bootstrap; Wald conjunto (b2=b3=0); R2 parcial; lo mismo sin controles. Fuera de muestra:
     pronósticos a un trimestre con ventana expansiva y contraste de Clark-West.
  2. El riesgo de cola con una oportunidad justa (el GaR se mueve lento): (a) cambios a cuatro
     trimestres; (b) proyecciones locales h=0..8; (c) medidas alternativas de cola presentes en el
     panel (ES, prob. de crecimiento negativo, GaR t-sesgada); (d) between vs. within; (e) todo
     lo anterior y la principal sin Polonia y sin cada uno de los demás países.
  3. La simultaneidad como hecho: frecuencia del estrés conjunto (terciles altos dentro de país,
     como p23) por país y por año, esperado bajo independencia, permutación por bloques,
     persistencia, regresiones cruzadas (qué riesgo antecede) y poder predictivo del indicador
     conjunto sobre el spread en t+1..t+4.
  4. Aditividad con bandas: IC 95 % de b3 (DK, cluster y wild bootstrap invertido) traducido a la
     mayor amplificación que los datos permiten descartar cuando AMBOS riesgos están una desviación
     estándar within-país sobre su media; también con Box-Cox (lambda = 0,44) del spread.

Simplificaciones (declaradas):
  - Fuera de muestra: pendiente común con EF de país (LSDV), SIN efectos de tiempo (no son
    pronosticables); se pronostica un país en tau solo si tiene >= 8 observaciones previas; la
    interacción entra sin centrar (mismo espacio generado que la centrada). El GaR del panel se
    usa tal cual (n_train crece en el tiempo, lo que sugiere estimación recursiva, pero aquí no se
    reestima). Clark-West: el MSPE ajustado se suma por trimestre y se contrasta la media de esa
    serie con error estándar HAC de Newey-West (4 rezagos), que es el análogo Driscoll-Kraay de
    una regresión sobre la constante; valor p unilateral.
  - Wild bootstrap: restringido, pesos de Webb, B = 999 (no 1 999) por la cantidad de contrastes;
    implementación vectorizada que se valida contra p14.wild_boot con la misma semilla.
  - Proyecciones locales: ancho de banda DK = max(4, h+1) por el solapamiento del horizonte.
  - Cambios a cuatro trimestres: DK con ancho de banda 8 (principal) y 5 (mínimo exigido).
  - Permutación: desplazamiento circular de la serie del indicador de D dentro de cada país
    (conserva la dependencia serial de cada serie, rompe la alineación); los huecos de la muestra
    se ignoran al desplazar.
  - Medidas alternativas: el panel no trae otro cuantil (p. ej. 10 %); se usan ES, prob_neg y
    GaR_st. iqr_05_95 es dispersión y no cola, por lo que no se incluye.

Salida: bbg/paper_aporte_numeros.csv (o _nivlag) y figura fig_aporte_cola_lnlag. Reutiliza p13 y p14.
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
from scipy import stats
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
from causal_core import demean2, cluster_se

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
B_WILD = 999
LAMBDA_BC = 0.44
CTR_CHARI = ["fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp"]     # columna (3) de p14.tabla_chari
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def pfit(dd, y, rhs, cov="dk", bw=None):
    """PanelOLS con EF de país y de tiempo; cov = 'dk' (Bartlett) o 'pais' (cluster por país)."""
    kw = dict(cov_type="clustered", cluster_entity=True) if cov == "pais" else dict(p14.DK)
    if cov == "dk" and bw is not None:
        kw["bandwidth"] = bw
    return PanelOLS.from_formula(f"{y} ~ {' + '.join(rhs)} + EntityEffects + TimeEffects",
                                 dd.set_index(["country", "t"])).fit(**kw)


# ================================================================ wild bootstrap vectorizado
def wb_prep(dd, y, regs):
    d = dd.dropna(subset=[y] + regs)
    cl = d["country"].values
    uniq, idx = np.unique(cl, return_inverse=True)
    yv = demean2(d, [y], iters=40)[y].values
    X = demean2(d, regs, iters=40).values
    return dict(y=yv, X=X, cl=cl, uniq=uniq, idx=idx, regs=list(regs))


def wb_run(P, keys, null=None, B=B_WILD, seed=7):
    """Wild cluster bootstrap restringido (H0: coeficientes de `keys` = null), pesos de Webb.
    Con una clave equivale a p14.wild_boot (t cluster); con varias usa el Wald cluster conjunto."""
    X, cl, idx = P["X"], P["cl"], P["idx"]
    ki = [P["regs"].index(k) for k in keys]
    null = np.zeros(len(ki)) if null is None else np.atleast_1d(np.asarray(null, float))
    yv = P["y"] - X[:, ki] @ null
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ (X.T @ yv); e = yv - X @ b
    V = cluster_se(X, e, cl, XtXi)[np.ix_(ki, ki)]
    w_obs = float(b[ki] @ np.linalg.solve(V, b[ki]))
    keep = [i for i in range(X.shape[1]) if i not in ki]
    if keep:
        fit_r = X[:, keep] @ np.linalg.lstsq(X[:, keep], yv, rcond=None)[0]
    else:
        fit_r = np.zeros_like(yv)
    res_r = yv - fit_r
    rng = np.random.default_rng(seed)
    G = len(P["uniq"])
    W = np.array([rng.choice(WEBB, size=G) for _ in range(B)])          # mismos sorteos que p14
    Ys = fit_r[:, None] + res_r[:, None] * W.T[idx, :]
    Bs = XtXi @ (X.T @ Ys); E = Ys - X @ Bs
    A = XtXi[ki, :]
    meat = np.zeros((len(ki), len(ki), B))
    for g in range(G):
        mk = idx == g
        Ag = A @ (X[mk].T @ E[mk])
        meat += np.einsum("ib,jb->ijb", Ag, Ag)
    n, k = X.shape
    Vb = meat * (G / (G - 1)) * ((n - 1) / (n - k))
    bK = Bs[ki, :]
    sol = np.linalg.solve(Vb.transpose(2, 0, 1), bK.T[:, :, None])[:, :, 0]
    wb = np.einsum("bi,ib->b", sol, bK)
    return float(np.mean(wb >= w_obs)), w_obs


def wild(dd, y, regs, keys, **kw):
    return wb_run(wb_prep(dd, y, regs), keys if isinstance(keys, list) else [keys], **kw)[0]


def wild_ci(dd, y, regs, key, b, se, npts=81, ancho=6.0):
    """IC 95 % por inversión del contraste wild: valores c tales que H0: b = c no se rechaza al 5 %."""
    P = wb_prep(dd, y, regs)
    grid = b + se * np.linspace(-ancho, ancho, npts)
    ps = np.array([wb_run(P, [key], null=[c])[0] for c in grid])
    ok = np.where(ps >= 0.05)[0]
    lo_i, hi_i = ok.min(), ok.max()

    def cruce(i_in, i_out):       # interpolación lineal del punto donde p cruza 0,05
        if i_out < 0 or i_out >= npts:
            return grid[i_in]
        return grid[i_in] + (grid[i_out] - grid[i_in]) * (ps[i_in] - 0.05) / (ps[i_in] - ps[i_out])
    return float(cruce(lo_i, lo_i - 1)), float(cruce(hi_i, hi_i + 1))


def ssr_within(dd, y, regs):
    yv = demean2(dd, [y], iters=40)[y].values
    if not regs:
        return float(yv @ yv)
    X = demean2(dd, regs, iters=40).values
    e = yv - X @ np.linalg.lstsq(X, yv, rcond=None)[0]
    return float(e @ e)


def centrar(dd, tail="D_l1"):
    dd = dd.copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd[tail] - dd[tail].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    return dd


# ================================================================ 1. información incremental
def incremental(d, ctr, pref):
    dd = centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + ctr))
    num(f"{pref}_N", len(dd)); num(f"{pref}_paises", dd["country"].nunique())
    m0 = pfit(dd, "ln_EMBI", ["J_c"] + ctr)
    num(f"{pref}_m0_b1", m0.params["J_c"]); num(f"{pref}_m0_b1_p_dk", m0.pvalues["J_c"])
    for nom, rhs, claves in (("m1", ["J_c", "T_c"], (("T_c", "b2"),)),
                             ("m2", ["J_c", "T_c", "JxT"], (("T_c", "b2"), ("JxT", "b3")))):
        m = pfit(dd, "ln_EMBI", rhs + ctr); mc = pfit(dd, "ln_EMBI", rhs + ctr, cov="pais")
        num(f"{pref}_{nom}_b1", m.params["J_c"]); num(f"{pref}_{nom}_b1_p_dk", m.pvalues["J_c"])
        for v, lab in claves:
            num(f"{pref}_{nom}_{lab}", m.params[v]); num(f"{pref}_{nom}_{lab}_se_dk", m.std_errors[v])
            num(f"{pref}_{nom}_{lab}_p_dk", m.pvalues[v]); num(f"{pref}_{nom}_{lab}_p_pais", mc.pvalues[v])
            num(f"{pref}_{nom}_{lab}_p_wild", wild(dd, "ln_EMBI", rhs + ctr, v))
    # Wald conjunto b2 = b3 = 0
    w = m.wald_test(formula="T_c = JxT = 0"); wc = mc.wald_test(formula="T_c = JxT = 0")
    G = dd["country"].nunique()
    num(f"{pref}_wald_dk", w.stat); num(f"{pref}_wald_dk_p", w.pval)
    num(f"{pref}_wald_pais", wc.stat); num(f"{pref}_wald_pais_p_chi2", wc.pval)
    num(f"{pref}_wald_pais_p_F", 1 - stats.f.cdf(wc.stat / 2, 2, G - 1))      # F(2, G-1): pocos clusters
    num(f"{pref}_wald_p_wild", wild(dd, "ln_EMBI", ["J_c", "T_c", "JxT"] + ctr, ["T_c", "JxT"]))
    # R2 within y R2 parciales (sobre datos sin EF de país ni tiempo)
    s_fe = ssr_within(dd, "ln_EMBI", [])
    s0 = ssr_within(dd, "ln_EMBI", ["J_c"] + ctr)
    s1 = ssr_within(dd, "ln_EMBI", ["J_c", "T_c"] + ctr)
    s2 = ssr_within(dd, "ln_EMBI", ["J_c", "T_c", "JxT"] + ctr)
    sD = ssr_within(dd, "ln_EMBI", ["T_c"] + ctr)
    num(f"{pref}_r2w_m0", 1 - s0 / s_fe); num(f"{pref}_r2w_m1", 1 - s1 / s_fe); num(f"{pref}_r2w_m2", 1 - s2 / s_fe)
    num(f"{pref}_r2parcial_D", 1 - s1 / s0)                 # D dado J (+ controles)
    num(f"{pref}_r2parcial_D_y_inter", 1 - s2 / s0)         # D e interacción dado J
    num(f"{pref}_r2parcial_inter", 1 - s2 / s1)
    num(f"{pref}_r2parcial_J_dado_D", 1 - s1 / sD)          # referencia: J dado D


def nw_t(x, L=4):
    """media de x y su estadístico t con varianza de largo plazo de Newey-West (Bartlett, L rezagos)."""
    x = np.asarray(x, float); T = len(x); u = x - x.mean()
    lrv = u @ u / T
    for j in range(1, L + 1):
        lrv += 2 * (1 - j / (L + 1)) * (u[j:] @ u[:-j]) / T
    return x.mean(), x.mean() / np.sqrt(lrv / T)


def fuera_de_muestra(d):
    dd = d.dropna(subset=["ln_EMBI", "ln_EMBI_l1", "ln_JLoss_l1", "D_l1"]).copy()
    dd["JD"] = dd["ln_JLoss_l1"] * dd["D_l1"]
    modelos = {"ar": ["ln_EMBI_l1"], "J": ["ln_EMBI_l1", "ln_JLoss_l1"],
               "JD": ["ln_EMBI_l1", "ln_JLoss_l1", "D_l1"], "JDx": ["ln_EMBI_l1", "ln_JLoss_l1", "D_l1", "JD"],
               "D": ["ln_EMBI_l1", "D_l1"]}
    q0, q1 = dd["_qn"].min(), dd["_qn"].max()
    inicio = q0 + int(np.ceil(0.4 * (q1 - q0 + 1)))
    filas = []
    for tau in sorted(q for q in dd["_qn"].unique() if q >= inicio):
        tr = dd[dd["_qn"] < tau]
        ok = tr.groupby("country").size()
        te = dd[(dd["_qn"] == tau) & dd["country"].isin(ok[ok >= 8].index)]
        if te.empty:
            continue
        paises = sorted(tr["country"].unique())
        Dtr = (tr["country"].values[:, None] == np.array(paises)[None, :]).astype(float)
        Dte = (te["country"].values[:, None] == np.array(paises)[None, :]).astype(float)
        fila = {"country": te["country"].values, "_qn": tau, "y": te["ln_EMBI"].values,
                "f_rw": te["ln_EMBI_l1"].values}
        for nom, x in modelos.items():
            beta = np.linalg.lstsq(np.column_stack([Dtr, tr[x].values]), tr["ln_EMBI"].values, rcond=None)[0]
            fila["f_" + nom] = np.column_stack([Dte, te[x].values]) @ beta
        filas.append(pd.DataFrame(fila))
    f = pd.concat(filas, ignore_index=True)
    num("oos_N", len(f)); num("oos_trimestres", f["_qn"].nunique())
    num("oos_inicio_anio", (inicio - 1) // 4); num("oos_inicio_trim", (inicio - 1) % 4 + 1)
    for nom in ["rw"] + list(modelos):
        f["e_" + nom] = f["y"] - f["f_" + nom]
        num(f"oos_rmse_{nom}", np.sqrt((f["e_" + nom] ** 2).mean()))
    for nom in ("J", "JD", "JDx", "D"):
        num(f"oos_ratio_{nom}_vs_ar", NUM[f"oos_rmse_{nom}"] / NUM["oos_rmse_ar"])
    num("oos_ratio_JD_vs_J", NUM["oos_rmse_JD"] / NUM["oos_rmse_J"])
    num("oos_ratio_JDx_vs_J", NUM["oos_rmse_JDx"] / NUM["oos_rmse_J"])
    num("oos_ratio_JDx_vs_JD", NUM["oos_rmse_JDx"] / NUM["oos_rmse_JD"])
    # Clark-West (anidado: chico vs grande) y Diebold-Mariano sin ajuste
    for chico, grande in (("ar", "J"), ("ar", "D"), ("J", "JD"), ("JD", "JDx"), ("J", "JDx")):
        cw = f["e_" + chico] ** 2 - (f["e_" + grande] ** 2 - (f["f_" + chico] - f["f_" + grande]) ** 2)
        dm = f["e_" + chico] ** 2 - f["e_" + grande] ** 2
        _, t_cw = nw_t(cw.groupby(f["_qn"]).sum().values)
        _, t_dm = nw_t(dm.groupby(f["_qn"]).sum().values)
        k = f"oos_{grande}_vs_{chico}"
        num(k + "_cw_t", t_cw); num(k + "_cw_p_unilateral", 1 - stats.norm.cdf(t_cw))
        num(k + "_dm_t", t_dm); num(k + "_dm_p_bilateral", 2 * (1 - stats.norm.cdf(abs(t_dm))))


# ================================================================ 2. cola con una oportunidad justa
def agregar_rezagos(d, raw):
    r = raw.copy()
    r["D_st"] = -r["GaR_st"] * 100.0
    d = d.copy()
    for col, k, name in (("ln_EMBI", 2, "y_l2"), ("ln_EMBI", 3, "y_l3"), ("ln_EMBI", 4, "y_l4"),
                         ("ln_JLoss", 2, "J_l2"), ("ln_JLoss", 5, "J_l5"), ("D_pp", 2, "D_l2"),
                         ("D_pp", 5, "D_l5"), ("D_st", 1, "DST_l1")) + tuple(
                             ("ln_EMBI", -h, f"y_f{h}") for h in range(1, 9)):
        d = d.merge(p14.shift(r, col, k, name), on=["country", "_qn"], how="left")
    d["y_f0"] = d["ln_EMBI"]
    d["dy1"] = d["ln_EMBI_l1"] - d["y_l2"]; d["dy2"] = d["y_l2"] - d["y_l3"]
    d["dJ1"] = d["ln_JLoss_l1"] - d["J_l2"]; d["dD1"] = d["D_l1"] - d["D_l2"]
    return d


def est_principal(d):
    m, _ = p13.fit(d)
    return {k: (m.params[v], m.pvalues[v]) for k, v in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT"))}


def est_cuatro(d, bw=8):
    """(a) cambios a cuatro trimestres; el producto se centra con las medias de la muestra usada."""
    dd = d.dropna(subset=["ln_EMBI", "y_l4", "ln_JLoss_l1", "J_l5", "D_l1", "D_l5"]).copy()
    mJ, mD = dd["ln_JLoss_l1"].mean(), dd["D_l1"].mean()
    dd["d4y"] = dd["ln_EMBI"] - dd["y_l4"]
    dd["d4J"] = dd["ln_JLoss_l1"] - dd["J_l5"]; dd["d4D"] = dd["D_l1"] - dd["D_l5"]
    dd["d4JD"] = (dd["ln_JLoss_l1"] - mJ) * (dd["D_l1"] - mD) - (dd["J_l5"] - mJ) * (dd["D_l5"] - mD)
    m = pfit(dd, "d4y", ["d4J", "d4D", "d4JD"], bw=bw)
    return {k: (m.params[k], m.pvalues[k]) for k in ("d4J", "d4D", "d4JD")}, m, dd


def est_lp(d, H=8):
    """(b) proyecciones locales en diferencias; DK con ancho de banda max(4, h+1)."""
    out = {}
    for h in range(H + 1):
        dd = d.dropna(subset=[f"y_f{h}", "ln_EMBI_l1", "dD1", "dJ1", "dy1", "dy2"]).copy()
        dd["yh"] = dd[f"y_f{h}"] - dd["ln_EMBI_l1"]
        m = pfit(dd, "yh", ["dD1", "dJ1", "dy1", "dy2"], bw=max(4, h + 1))
        out[h] = dict(bD=m.params["dD1"], pD=m.pvalues["dD1"], seD=m.std_errors["dD1"],
                      bJ=m.params["dJ1"], pJ=m.pvalues["dJ1"], seJ=m.std_errors["dJ1"], N=m.nobs)
    return out


ALT = (("es", "DES_l1"), ("probneg", "prob_neg_l1"), ("garst", "DST_l1"))


def est_alt(d):
    out = {}
    for lab, col in ALT:
        m, dd = p13.fit(d, tail=col)
        sdw = float((dd[col] - dd.groupby("country")[col].transform("mean")).std())
        out[lab] = dict(b1=m.params["J_c"], p1=m.pvalues["J_c"], b2=m.params["T_c"], p2=m.pvalues["T_c"],
                        b3=m.params["JxT"], p3=m.pvalues["JxT"], N=m.nobs, sdw=sdw, dd=dd)
    return out


def bloque_cola(d):
    # (a)
    for bw in (8, 5):
        r, m, dd4 = est_cuatro(d, bw=bw)
        for k in ("d4J", "d4D", "d4JD"):
            num(f"cuatro_bw{bw}_{k}", r[k][0]); num(f"cuatro_bw{bw}_{k}_p_dk", r[k][1])
    num("cuatro_N", m.nobs)
    mc = pfit(dd4, "d4y", ["d4J", "d4D", "d4JD"], cov="pais")
    for k in ("d4J", "d4D", "d4JD"):
        num(f"cuatro_{k}_p_pais", mc.pvalues[k])
        num(f"cuatro_{k}_p_wild", wild(dd4, "d4y", ["d4J", "d4D", "d4JD"], k))
    # (b)
    lp = est_lp(d)
    for h, r in lp.items():
        num(f"lp_h{h}_D", r["bD"]); num(f"lp_h{h}_D_p_dk", r["pD"])
        num(f"lp_h{h}_J", r["bJ"]); num(f"lp_h{h}_J_p_dk", r["pJ"]); num(f"lp_h{h}_N", r["N"])
    num("lp_D_n_sig5", sum(r["pD"] < 0.05 for r in lp.values()))
    num("lp_J_n_sig5", sum(r["pJ"] < 0.05 for r in lp.values()))
    # (c)
    alt = est_alt(d)
    for lab, r in alt.items():
        for k in ("b1", "p1", "b2", "p2", "b3", "p3", "N"):
            num(f"alt_{lab}_{k if k[0] != 'p' else k[1:].join(['b', '_p_dk'])}", r[k])
        num(f"alt_{lab}_efecto_1sd", r["b2"] * r["sdw"])
        num(f"alt_{lab}_b2_p_wild", wild(r["dd"], "ln_EMBI", ["J_c", "T_c", "JxT"], "T_c"))
        num(f"alt_{lab}_corr_con_D", r["dd"][["T_c"]].corrwith(r["dd"]["D_l1"]).iloc[0])
    # (d) between vs within
    m0, dd = p13.fit(d)
    cm = dd.groupby("country")[["ln_EMBI", "ln_JLoss_l1", "D_l1"]].mean()
    r1 = stats.linregress(cm["D_l1"], cm["ln_EMBI"])
    num("between_b_D", r1.slope); num("between_b_D_p", r1.pvalue); num("between_r2_D", r1.rvalue ** 2)
    sp = stats.spearmanr(cm["D_l1"], cm["ln_EMBI"])
    num("between_spearman_D", sp[0]); num("between_spearman_D_p", sp[1])
    import statsmodels.api as sm
    r2 = sm.OLS(cm["ln_EMBI"], sm.add_constant(cm[["ln_JLoss_l1", "D_l1"]])).fit()
    num("between_b_D_con_J", r2.params["D_l1"]); num("between_b_D_con_J_p", r2.pvalues["D_l1"])
    num("between_b_J_con_D", r2.params["ln_JLoss_l1"]); num("between_b_J_con_D_p", r2.pvalues["ln_JLoss_l1"])
    num("between_n", len(cm))
    num("between_sd_D", cm["D_l1"].std())
    num("within_sd_D", (dd["D_l1"] - dd.groupby("country")["D_l1"].transform("mean")).std())
    num("within_b_D", m0.params["T_c"]); num("within_b_D_p_dk", m0.pvalues["T_c"])
    mp, _ = p13.fit(d, fe="P")
    num("within_soloEFpais_b_D", mp.params["T_c"]); num("within_soloEFpais_b_D_p_dk", mp.pvalues["T_c"])
    # (e) sin Polonia y sin cada país
    reg = {}
    for pais in sorted(d["country"].unique()):
        s = d[d["country"] != pais]
        fila = {}
        for k, (b, p) in est_principal(s).items():
            fila[f"principal_{k}"] = (b, p)
        for k, (b, p) in est_cuatro(s)[0].items():
            fila[f"cuatro_{k}"] = (b, p)
        for h, r in est_lp(s).items():
            fila[f"lp_h{h}_D"] = (r["bD"], r["pD"]); fila[f"lp_h{h}_J"] = (r["bJ"], r["pJ"])
        for lab, r in est_alt(s).items():
            fila[f"alt_{lab}_b2"] = (r["b2"], r["p2"])
        reg[pais] = fila
        print(f"    sin {pais:12s} b2={fila['principal_b2'][0]:+.4f} (p={fila['principal_b2'][1]:.3f})"
              f"  d4D={fila['cuatro_d4D'][0]:+.4f} (p={fila['cuatro_d4D'][1]:.3f})", flush=True)
    for k in reg["poland"]:
        bs = np.array([reg[c][k][0] for c in reg]); ps = np.array([reg[c][k][1] for c in reg])
        num(f"sinpolonia_{k}", reg["poland"][k][0]); num(f"sinpolonia_{k}_p_dk", reg["poland"][k][1])
        num(f"loo_{k}_min", bs.min()); num(f"loo_{k}_max", bs.max()); num(f"loo_{k}_n_sig5", (ps < 0.05).sum())
    for c in reg:                                         # detalle por país del efecto de nivel de D
        num(f"loo_pais_{c}_principal_b2", reg[c]["principal_b2"][0])
        num(f"loo_pais_{c}_principal_b2_p_dk", reg[c]["principal_b2"][1])
    return lp


def fig_lp(lp):
    import matplotlib.pyplot as plt
    hs = sorted(lp)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, b, se, lab, col in ((axes[0], "bD", "seD", r"$\Delta D_{t-1}$ (riesgo de cola)", p13.ORANGE),
                                (axes[1], "bJ", "seJ", (r"$\Delta JLoss_{t-1}$" if NIV else r"$\Delta\ln JLoss_{t-1}$")
                                 + " (fragilidad bancaria)", p13.BLUE)):
        bb = np.array([lp[h][b] for h in hs]); ss = np.array([lp[h][se] for h in hs])
        ax.axhline(0, color=p13.INK2, lw=0.8)
        ax.fill_between(hs, bb - 1.96 * ss, bb + 1.96 * ss, color=col, alpha=0.15, lw=0)
        ax.plot(hs, bb, "o-", color=col, lw=1.8)
        ax.set_xlabel("horizonte h (trimestres)"); ax.set_title(f"Respuesta acumulada del spread a {lab}", fontsize=9.5)
    axes[0].set_ylabel("coeficiente (IC 95 %, Driscoll–Kraay)")
    p13.save(fig, "fig_aporte_cola_lnlag")


# ================================================================ 3. simultaneidad como hecho
def rachas(dd):
    """largo de cada episodio de estrés conjunto (trimestres consecutivos dentro de país)."""
    out = []
    for _, g in dd.sort_values("_qn").groupby("country"):
        n = 0; prev = None
        for q, a in zip(g["_qn"].values, g["AJD"].values):
            if a == 1 and (n == 0 or q - prev == 1):
                n += 1
            else:
                if n:
                    out.append(n)
                n = 1 if a == 1 else 0
            prev = q
        if n:
            out.append(n)
    return out


def rachas_vec(a):
    a = np.concatenate([[0], a, [0]]); c = np.diff(a)
    return list(np.where(c == -1)[0] - np.where(c == 1)[0])


def bloque_simultaneidad(d, R=999, seed=11):
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).sort_values(["country", "_qn"]).copy()
    for col, nom in (("ln_JLoss_l1", "AJ"), ("D_l1", "AD")):
        dd[nom] = (dd[col] > dd.groupby("country")[col].transform(lambda x: x.quantile(2 / 3))).astype(float)
    dd["AJD"] = dd["AJ"] * dd["AD"]
    dd["anio"] = dd["t"].dt.year
    dd["crisis"] = dd["quarter"].isin(p13.CRISIS_BAT)
    obs = dd["AJD"].sum()
    g = dd.groupby("country")
    esp_pais = g.apply(lambda x: len(x) * x["AJ"].mean() * x["AD"].mean())
    num("conj_N", len(dd)); num("conj_obs", obs); num("conj_frac", obs / len(dd))
    num("conj_esp_indep", esp_pais.sum()); num("conj_razon_obs_esp", obs / esp_pais.sum())
    for c, x in g:
        num(f"conj_pais_{c}", x["AJD"].sum()); num(f"conj_pais_{c}_n", len(x)); num(f"conj_pais_{c}_esp", esp_pais[c])
    num("conj_paises_obs_mayor_esp", sum(g["AJD"].sum() > esp_pais))
    for a, x in dd.groupby("anio"):
        num(f"conj_anio_{a}", x["AJD"].sum()); num(f"conj_anio_{a}_n", len(x))
        num(f"conj_anio_{a}_esp", len(x) * x["AJ"].mean() * x["AD"].mean())
    num("conj_frac_en_crisis", dd.loc[dd["crisis"], "AJD"].sum() / obs)
    num("conj_frac_muestra_en_crisis", dd["crisis"].mean())
    obs_sc = dd.loc[~dd["crisis"], "AJD"].sum(); num("conj_obs_sincrisis", obs_sc)
    # chi-cuadrado ingenuo (ignora dependencia serial y entre países)
    tab = pd.crosstab(dd["AJ"], dd["AD"])
    chi = stats.chi2_contingency(tab, correction=False)
    num("conj_chi2", chi[0]); num("conj_chi2_p", chi[1])
    num("conj_phi", np.corrcoef(dd["AJ"], dd["AD"])[0, 1])
    # permutación por bloques: desplazamiento circular del indicador de D dentro de cada país
    rng = np.random.default_rng(seed)
    series = [(x["AJ"].values, x["AD"].values, (~x["crisis"]).values.astype(float), x["_qn"].values) for _, x in g]
    sim = np.empty(R); sim_sc = np.empty(R); sim_len = np.empty(R)
    for r in range(R):
        tot = tot_sc = 0.0; ls = []
        for aj, ad, nc, qn in series:
            j = np.roll(ad, rng.integers(1, len(ad))) * aj
            tot += j.sum(); tot_sc += (j * nc).sum(); ls += rachas_vec(j)
        sim[r] = tot; sim_sc[r] = tot_sc; sim_len[r] = np.mean(ls) if ls else 0.0
    num("conj_perm_R", R); num("conj_perm_media", sim.mean())
    num("conj_perm_p_unilateral", (1 + (sim >= obs).sum()) / (R + 1))
    num("conj_perm_q95", np.quantile(sim, 0.95))
    num("conj_perm_sincrisis_media", sim_sc.mean())
    num("conj_perm_sincrisis_p_unilateral", (1 + (sim_sc >= obs_sc).sum()) / (R + 1))
    # persistencia (la versión con huecos corta el episodio; la permutación los ignora, se compara igual a igual)
    ls = rachas(dd)
    ls_sinhuecos = [l for _, x in g for l in rachas_vec(x["AJD"].values)]
    num("conj_episodios", len(ls)); num("conj_racha_media", np.mean(ls)); num("conj_racha_max", np.max(ls))
    num("conj_racha_media_sinhuecos", np.mean(ls_sinhuecos)); num("conj_perm_racha_media", sim_len.mean())
    num("conj_perm_racha_p_unilateral", (1 + (sim_len >= np.mean(ls_sinhuecos)).sum()) / (R + 1))
    for nom in ("AJ", "AD"):
        num(f"conj_racha_media_{nom}", np.mean([l for _, x in g for l in rachas_vec(x[nom].values)]))
    # regresiones cruzadas: qué riesgo antecede al otro
    x = dd.dropna(subset=["ln_JLoss_t", "D_t"]).copy()
    sw = {c: float(demean2(x, [c], iters=40)[c].std()) for c in ("ln_JLoss_t", "D_t", "ln_JLoss_l1", "D_l1")}
    for y, propio, cruz, lab in (("ln_JLoss_t", "ln_JLoss_l1", "D_l1", "D_a_J"), ("D_t", "D_l1", "ln_JLoss_l1", "J_a_D")):
        m = pfit(x, y, [propio, cruz]); mc = pfit(x, y, [propio, cruz], cov="pais")
        num(f"cruz_{lab}_b", m.params[cruz]); num(f"cruz_{lab}_p_dk", m.pvalues[cruz]); num(f"cruz_{lab}_p_pais", mc.pvalues[cruz])
        num(f"cruz_{lab}_p_wild", wild(x, y, [propio, cruz], cruz))
        num(f"cruz_{lab}_b_estandarizado", m.params[cruz] * sw[cruz] / sw[y])
        num(f"cruz_{lab}_rho_propio", m.params[propio]); num(f"cruz_{lab}_N", m.nobs)
    num("cruz_corr_within_J_D", np.corrcoef(demean2(dd, ["ln_JLoss_l1"], iters=40)["ln_JLoss_l1"],
                                           demean2(dd, ["D_l1"], iters=40)["D_l1"])[0, 1])
    # ¿predice el indicador conjunto en t-1 el spread en t+h más allá de los dos indicadores?
    for h in range(0, 5):
        s = dd.dropna(subset=[f"y_f{h}"])
        m = pfit(s, f"y_f{h}", ["AJ", "AD", "AJD"], bw=max(4, h + 1)); mc = pfit(s, f"y_f{h}", ["AJ", "AD", "AJD"], cov="pais")
        for v, lab in (("AJ", "a1"), ("AD", "a2"), ("AJD", "a3")):
            num(f"pred_h{h}_{lab}", m.params[v]); num(f"pred_h{h}_{lab}_p_dk", m.pvalues[v]); num(f"pred_h{h}_{lab}_p_pais", mc.pvalues[v])
        num(f"pred_h{h}_a3_p_wild", wild(s, f"y_f{h}", ["AJ", "AD", "AJD"], "AJD"))
        num(f"pred_h{h}_N", m.nobs)


# ================================================================ 4. aditividad con bandas
def bandas(d, pref, escala=None):
    """IC 95 % de b3 y su traducción: efecto extra cuando ambos riesgos están 1 de within-país sobre su
    media, frente a la suma de los dos efectos por separado. `escala` convierte unidades de la variable
    dependiente a (pb, %) cuando no es ni log ni pb (Box-Cox)."""
    m, dd = p13.fit(d); mc, _ = p13.fit(d, cov="pais")
    b1, b2, b3 = m.params["J_c"], m.params["T_c"], m.params["JxT"]
    sJ = float((dd["J_c"] - dd.groupby("country")["J_c"].transform("mean")).std())
    sD = float((dd["T_c"] - dd.groupby("country")["T_c"].transform("mean")).std())
    G = dd["country"].nunique(); tc = stats.t.ppf(0.975, G - 1)
    ics = {"dk": (b3 - 1.96 * m.std_errors["JxT"], b3 + 1.96 * m.std_errors["JxT"]),
           "pais": (b3 - tc * mc.std_errors["JxT"], b3 + tc * mc.std_errors["JxT"]),
           "wild": wild_ci(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], "JxT", b3, mc.std_errors["JxT"])}
    num(f"{pref}_b1", b1); num(f"{pref}_b2", b2); num(f"{pref}_b3", b3)
    num(f"{pref}_b3_p_dk", m.pvalues["JxT"]); num(f"{pref}_b3_p_pais", mc.pvalues["JxT"])
    num(f"{pref}_sd_within_J", sJ); num(f"{pref}_sd_within_D", sD)
    sep = b1 * sJ + b2 * sD
    num(f"{pref}_suma_separados", sep); num(f"{pref}_extra_punto", b3 * sJ * sD)
    num(f"{pref}_extra_punto_sobre_suma", b3 * sJ * sD / sep)
    for k, (lo, hi) in ics.items():
        num(f"{pref}_b3_ic_{k}_lo", lo); num(f"{pref}_b3_ic_{k}_hi", hi)
        num(f"{pref}_extra_{k}_lo", lo * sJ * sD); num(f"{pref}_extra_{k}_hi", hi * sJ * sD)
        num(f"{pref}_extra_{k}_hi_sobre_suma", hi * sJ * sD / sep)
        num(f"{pref}_extra_{k}_lo_sobre_suma", lo * sJ * sD / sep)
    # traducción a porcentaje del spread (y a pb)
    emb = float(dd["EMBI_bps"].mean()); num(f"{pref}_embi_medio_pb", emb)
    if escala is None and not NIV:           # logs: efecto exacto exp(.)-1
        f = lambda x: 100 * (np.exp(sep + x) - np.exp(sep))
        num(f"{pref}_suma_separados_pct", 100 * (np.exp(sep) - 1))
    else:                                    # pb (niveles) o Box-Cox linealizado en el spread medio
        e_pb = 1.0 if escala is None else escala(emb)
        f = lambda x: 100 * x * e_pb / emb
        num(f"{pref}_suma_separados_pct", 100 * sep * e_pb / emb); num(f"{pref}_suma_separados_pb", sep * e_pb)
        for k, (lo, hi) in ics.items():
            num(f"{pref}_extra_{k}_lo_pb", lo * sJ * sD * e_pb); num(f"{pref}_extra_{k}_hi_pb", hi * sJ * sD * e_pb)
        num(f"{pref}_extra_punto_pb", b3 * sJ * sD * e_pb)
    num(f"{pref}_extra_punto_pct", f(b3 * sJ * sD))
    for k, (lo, hi) in ics.items():
        num(f"{pref}_extra_{k}_lo_pct", f(lo * sJ * sD)); num(f"{pref}_extra_{k}_hi_pct", f(hi * sJ * sD))


def bloque_aditividad(d):
    bandas(d, "adit")
    # Box-Cox (lambda = 0,44) del spread, regresores como en la forma logarítmica (igual en ambas formas)
    x = d.copy()
    x["ln_EMBI"] = (x["EMBI_bps"] ** LAMBDA_BC - 1) / LAMBDA_BC
    x["ln_JLoss_l1"] = np.log(x["JLoss_l1"])
    bandas(x, "adit_bc", escala=lambda s: s ** (1 - LAMBDA_BC))      # d(spread) = d(y) * spread^(1-lambda)


def main():
    print("p32: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, dd0 = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4, (m0.nobs, m0.params["JxT"])
    for n_, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"principal_{lab}", m0.params[n_]); num(f"principal_{lab}_p_dk", m0.pvalues[n_])
    num("principal_N", m0.nobs)
    # validación del wild bootstrap vectorizado contra p14.wild_boot (misma semilla y pesos)
    p_ref, _ = p14.wild_boot(dd0, "ln_EMBI", ["J_c", "T_c", "JxT"], "JxT", B=B_WILD, weights="webb")
    p_mio = wild(dd0, "ln_EMBI", ["J_c", "T_c", "JxT"], "JxT")
    num("wild_validacion_p14", p_ref); num("wild_validacion_p32", p_mio)
    assert abs(p_ref - p_mio) < 0.005, (p_ref, p_mio)
    out = os.path.join(HERE, f"paper_aporte_numeros{SFX}.csv")

    def guardar(msg):
        pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
        print(f"  {msg} ({len(NUM)} cifras)", flush=True)

    d = agregar_rezagos(p14.cargar_bbg_macro(d), raw)
    incremental(d, CTR_CHARI, "inc_chari"); incremental(d, [], "inc_sinctrl")
    fuera_de_muestra(d); guardar("1. informacion incremental")
    lp = bloque_cola(d); fig_lp(lp); guardar("2. cola con oportunidad justa")
    bloque_simultaneidad(d); guardar("3. simultaneidad")
    bloque_aditividad(d); guardar("4. aditividad con bandas")
    for k, v in NUM.items():
        print(f"  {k:44s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
