# -*- coding: utf-8 -*-
"""
p14_arbitro_lnlag.py -- pruebas que pediria un arbitro sobre la especificacion PRINCIPAL del
paper (log-log rezagada, panel Panel_bloomberg_embiext.csv, 13 paises):

    ln EMBI_t = a_i + d_t + b1 lnJLoss_{t-1} + b2 D_{t-1} + b3 lnJLoss_{t-1} x D_{t-1} + e

Bloques (Tier 1 del plan de arbitro):
  1. causalidad inversa y dinamica: canal inverso, placebo de adelantos, spread rezagado
  2. inferencia: wild cluster bootstrap (G=13) y sensibilidad al ancho de banda DK
  3. identificacion en logs: proyecciones locales e IV shift-share
  4. regresor generado: segunda etapa sobre las 500 replicas NLHPC del GaR
  5. EMstress: vector extendido de estres sin respaldo + test de permutacion
  6. controles: controles t-4, canales (JLoss -> fiscal / TCR), Oster, tabla estilo Chari
  7. forma funcional: prueba PE (niveles vs logs) y Box-Cox
  8. medicion de JLoss: malla ancha y transformacion por percentiles

Salidas: tablas_regresiones/tabla_arbitro_*.tex, figuras *_arb en paper_empirico/figuras/,
bbg/paper_arbitro_numeros.csv (toda cifra citada). Reutiliza p13 (datos, fit, save), p9b,
causal_core (demean2, cluster_se). No modifica ningun archivo canonico.
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
import matplotlib.pyplot as plt
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from linearmodels.iv import IV2SLS
from scipy import stats

import p13_figuras_paper as p13
import p12_tablas_latex_lnlag as p12
import p9b_bateria_crisis as p9b
from p2_regresiones import CTRLS
from causal_core import demean2, cluster_se

BLUE, ORANGE, RED, INK, INK2 = p13.BLUE, p13.ORANGE, p13.RED, p13.INK, p13.INK2
ROOT = p13.ROOT
TAB = p13.TAB
MACRO = os.path.join(ROOT, "1_Codigo", "Bloomberg_extraction", "output_macro")
WIDE = os.path.join(ROOT, "1_Codigo", "JLoss_reconstruction", "Panel_JLoss_wide.csv")
REPLICAS = os.path.join(ROOT, "1_Codigo", "GaR", "individuals", "nlhpc_gar_all18", "gar_replicas_nlhpc.csv")
CANON = os.path.join(HERE, "Panel_bloomberg.csv")          # trae USD_NEER_log y CTOT_shock
DK = dict(cov_type="kernel", kernel="bartlett")

# episodios de estres emergente SIN respaldo oficial masivo (lista fija, definida ex ante)
TAPER = ["2013Q2", "2013Q3"]          # taper tantrum (Eichengreen y Gupta, 2015)
EM1516 = p9b.EM1516                   # 2015Q3-2016Q1
EM2018 = ["2018Q2", "2018Q3"]         # venta masiva EM 2018 (Argentina, Turquia; FMI GFSR oct-2018)
EMSTRESS_EXT = TAPER + EM1516 + EM2018

NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def star(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def fb(b, p, dec=4):
    s = f"{b:.{dec}f}".replace(".", "{,}")
    return f"${s}^{{{star(p)}}}$" if star(p) else f"${s}$"


def fse(se, dec=4):
    return f"$({se:.{dec}f})$".replace(".", "{,}")


def fnum(x, dec=3):
    return f"${x:.{dec}f}$".replace(".", "{,}")


# ================================================================ datos
def raw_panel():
    r = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    q = pd.PeriodIndex(r["quarter"], freq="Q")
    r["_qn"] = q.year * 4 + q.quarter
    r["GaR_pp"] = r["GaR"] * 100
    r["D_pp"] = -r["GaR_pp"]
    r["ln_EMBI"] = np.log(r["EMBI_bps"].where(r["EMBI_bps"] > 0))
    r["ln_JLoss"] = np.log(r["JLoss"].where(r["JLoss"] > 0))
    c = pd.read_csv(CANON)[["country", "quarter", "USD_NEER_log", "CTOT_shock"]]
    return r.merge(c, on=["country", "quarter"], how="left")


def shift(raw, col, k, name):
    """valor de `col` en el trimestre q-k (k>0 rezago, k<0 adelanto), por pais, sin huecos."""
    t = raw[["country", "_qn", col]].copy()
    t["_qn"] = t["_qn"] + k
    return t.rename(columns={col: name})


def base():
    """muestra de la regresion principal (p13.datos) + rezagos/adelantos que usa p14."""
    raw = raw_panel()
    d = p13.datos()
    q = pd.PeriodIndex(d["quarter"], freq="Q")
    d["_qn"] = q.year * 4 + q.quarter
    for col, k, name in (("ln_EMBI", 1, "ln_EMBI_l1"), ("ln_JLoss", -1, "ln_JLoss_f1"),
                         ("D_pp", -1, "D_f1"), ("ln_JLoss", 0, "ln_JLoss_t"), ("D_pp", 0, "D_t")):
        d = d.merge(shift(raw, col, k, name), on=["country", "_qn"], how="left")
    for c in CTRLS:
        d = d.merge(shift(raw, c, 4, c + "_l4"), on=["country", "_qn"], how="left")
    # choques globales/comerciales rezagados un trimestre, alineados con ln JLoss_{t-1} (instrumentos)
    for col in ("OnOffRun_spread_log", "USD_NEER_log", "CTOT_shock"):
        d = d.merge(shift(raw, col, 1, col + "_l1"), on=["country", "_qn"], how="left")
    return d, raw


def check_principal(d):
    m, dd = p13.fit(d)
    assert int(m.nobs) == 765 and abs(m.params["JxT"] + 0.0112) < 5e-4, (m.nobs, m.params["JxT"])
    return m, dd


# ================================================================ 1. causalidad inversa / dinamica
def bloque_causalidad(d, m0):
    out = {}
    # (a) canal inverso: ln JLoss_t sobre ln EMBI_{t-1} y D_{t-1}
    dd = d.dropna(subset=["ln_JLoss_t", "ln_EMBI_l1", "D_l1"]).copy()
    m = PanelOLS.from_formula("ln_JLoss_t ~ ln_EMBI_l1 + D_l1 + EntityEffects + TimeEffects",
                              dd.set_index(["country", "t"])).fit(**DK)
    out["inverso"] = m
    num("arb_inverso_b", m.params["ln_EMBI_l1"]); num("arb_inverso_se", m.std_errors["ln_EMBI_l1"])
    num("arb_inverso_p", m.pvalues["ln_EMBI_l1"]); num("arb_inverso_N", m.nobs)
    # (b) placebo de adelantos: agrega ln JLoss_{t+1} y D_{t+1}
    m, _ = p13.fit(d, ctr=["ln_JLoss_f1", "D_f1"])
    out["adelantos"] = m
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT"), ("fJ", "ln_JLoss_f1"), ("fD", "D_f1")):
        num(f"arb_lead_{k}", m.params[n]); num(f"arb_lead_{k}_p", m.pvalues[n])
    num("arb_lead_N", m.nobs)
    # (c) dinamica: agrega ln EMBI_{t-1}; efecto de largo plazo b1/(1-rho) por metodo delta
    m, _ = p13.fit(d, ctr=["ln_EMBI_l1"])
    out["dinamica"] = m
    rho, b1 = m.params["ln_EMBI_l1"], m.params["J_c"]
    V = m.cov.loc[["J_c", "ln_EMBI_l1"], ["J_c", "ln_EMBI_l1"]].values
    g = np.array([1 / (1 - rho), b1 / (1 - rho) ** 2])
    lr, lr_se = b1 / (1 - rho), float(np.sqrt(g @ V @ g))
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT"), ("rho", "ln_EMBI_l1")):
        num(f"arb_din_{k}", m.params[n]); num(f"arb_din_{k}_p", m.pvalues[n])
    num("arb_din_lp", lr); num("arb_din_lp_se", lr_se)
    num("arb_din_lp_p", 2 * (1 - stats.norm.cdf(abs(lr / lr_se)))); num("arb_din_N", m.nobs)
    b2, rhoV = m.params["T_c"], m.cov.loc[["T_c", "ln_EMBI_l1"], ["T_c", "ln_EMBI_l1"]].values
    g2 = np.array([1 / (1 - rho), b2 / (1 - rho) ** 2])
    num("arb_din_lpD", b2 / (1 - rho)); num("arb_din_lpD_se", float(np.sqrt(g2 @ rhoV @ g2)))
    return out


# ================================================================ 2. inferencia
def wild_boot(dd, y, regs, key, B=1999, seed=7, weights="rademacher"):
    """wild cluster bootstrap restringido (H0: key=0), t con SE cluster por pais; misma
    implementacion que p2_regresiones.wild_boot / causal_core.wild_cluster_boot, generalizada
    a cualquier y y regresores (ya centrados) y con pesos Rademacher o Webb."""
    d = dd.dropna(subset=[y] + regs).copy()
    cl = d["country"].values
    yv = demean2(d, [y], iters=40)[y].values
    X = demean2(d, regs, iters=40).values
    ki = regs.index(key)
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ (X.T @ yv); e = yv - X @ b
    t_obs = b[ki] / np.sqrt(cluster_se(X, e, cl, XtXi)[ki, ki])
    keep = [i for i in range(len(regs)) if i != ki]
    br = np.linalg.lstsq(X[:, keep], yv, rcond=None)[0]
    fit_r = X[:, keep] @ br; res_r = yv - fit_r
    rng = np.random.default_rng(seed); uniq = np.unique(cl)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
    tb = np.empty(B)
    for i in range(B):
        w = rng.choice([-1.0, 1.0] if weights == "rademacher" else webb, size=len(uniq))
        wv = np.array([dict(zip(uniq, w))[c] for c in cl])
        ys = fit_r + wv * res_r
        bs = XtXi @ (X.T @ ys); es = ys - X @ bs
        tb[i] = bs[ki] / np.sqrt(cluster_se(X, es, cl, XtXi)[ki, ki])
    return float(np.mean(np.abs(tb) >= abs(t_obs))), float(t_obs)


def validar_wild_boot():
    """reproduce p2_regresiones.wild_boot (M2 en niveles con controles) con la misma semilla."""
    import p2_regresiones as p2
    d = p2.prep()
    ctr = [c for c in CTRLS if d[c].notna().sum() > 50]
    p_ref = p2.wild_boot(d, ctr, B=999)
    dd = d.dropna(subset=["_DV", "JLoss", "GaR_pp"] + ctr).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean(); dd["GaR_pp_c"] = dd["GaR_pp"] - dd["GaR_pp"].mean()
    dd["JxT"] = dd["JLoss_c"] * dd["GaR_pp_c"]
    p_mio, _ = wild_boot(dd, "_DV", ["JLoss_c", "GaR_pp_c", "JxT"] + ctr, "JxT", B=999, seed=7)
    num("arb_wb_validacion_p2", p_ref); num("arb_wb_validacion_p14", p_mio)
    assert abs(p_ref - p_mio) < 1e-9, (p_ref, p_mio)


def bloque_inferencia(dd):
    for key, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        for w in ("rademacher", "webb"):
            p, t = wild_boot(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], key, weights=w)
            num(f"arb_wb_{lab}_{w}", p)
        num(f"arb_wb_{lab}_tcluster", t)
    for bw in (2, 4, 8):
        m = PanelOLS.from_formula("ln_EMBI ~ J_c + T_c + JxT + EntityEffects + TimeEffects",
                                  dd.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett",
                                                                      bandwidth=bw)
        for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
            num(f"arb_bw{bw}_{k}_se", m.std_errors[n]); num(f"arb_bw{bw}_{k}_p", m.pvalues[n])


# ================================================================ 3. LP e IV en logs
def bloque_lp(d, raw, H=6):
    rows = []
    for h in range(H + 1):
        dd = d.merge(shift(raw, "ln_EMBI", -h, "y_h"), on=["country", "_qn"], how="left")
        dd = dd.dropna(subset=["y_h", "ln_JLoss_l1", "D_l1", "ln_EMBI_l1"]).copy()
        m = PanelOLS.from_formula("y_h ~ ln_JLoss_l1 + D_l1 + ln_EMBI_l1 + EntityEffects + TimeEffects",
                                  dd.set_index(["country", "t"])).fit(**DK)
        rows.append((h, m.params["ln_JLoss_l1"], m.std_errors["ln_JLoss_l1"],
                     m.params["D_l1"], m.std_errors["D_l1"], int(m.nobs)))
        num(f"arb_lp_h{h}_J", m.params["ln_JLoss_l1"]); num(f"arb_lp_h{h}_J_p", m.pvalues["ln_JLoss_l1"])
        num(f"arb_lp_h{h}_D", m.params["D_l1"]); num(f"arb_lp_h{h}_D_p", m.pvalues["D_l1"])
    t = pd.DataFrame(rows, columns=["h", "bJ", "seJ", "bD", "seD", "N"])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, b, se, lab, col in ((axes[0], "bJ", "seJ", r"ln JLoss$_{t-1}$", BLUE),
                                (axes[1], "bD", "seD", r"D$_{t-1}$", ORANGE)):
        ax.axhline(0, color=INK2, lw=0.8)
        ax.fill_between(t.h, t[b] - 1.96 * t[se], t[b] + 1.96 * t[se], color=col, alpha=0.15, lw=0)
        ax.plot(t.h, t[b], "o-", color=col, lw=1.8)
        ax.set_xlabel("horizonte h (trimestres)"); ax.set_title(f"Respuesta de ln EMBI$_{{t+h}}$ a {lab}", fontsize=9.5)
    axes[0].set_ylabel("coeficiente (IC 95 %)")
    p13.save(fig, "fig_lp_lnlag_arb")
    return t


def _Z(d, g, pre_year=2012):
    """shift-share: phi_c (sensibilidad pre-muestra de ln JLoss a g) x g, rezagado como JLoss."""
    phi = {}
    pre = d[d.t.dt.year < pre_year]
    for c, gg in pre.groupby("country"):
        gg = gg.dropna(subset=[g, "ln_JLoss_l1"])
        phi[c] = np.polyfit(gg[g], gg["ln_JLoss_l1"], 1)[0] if len(gg) > 5 and gg[g].std() > 0 else np.nan
    gm = np.nanmean(list(phi.values()))
    return d["country"].map(lambda c: phi.get(c, gm)).fillna(gm) * d[g]


def bloque_iv(d):
    dd = d.copy()
    dd["Z_onoff"] = _Z(dd, "OnOffRun_spread_log_l1")
    dd["Z_usd"] = _Z(dd, "USD_NEER_log_l1")
    dd["Z_ctot"] = dd["CTOT_shock_l1"]
    res = {}
    for lab, zs in (("onoff", ["Z_onoff"]), ("usd", ["Z_usd"]), ("ctot", ["Z_ctot"]),
                    ("todos", ["Z_onoff", "Z_usd", "Z_ctot"])):
        s = dd.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + zs).copy()
        dm = demean2(s, ["ln_EMBI", "ln_JLoss_l1", "D_l1"] + zs, iters=40)
        exog = dm[["D_l1"]]
        m = IV2SLS(dm["ln_EMBI"], exog, dm[["ln_JLoss_l1"]], dm[zs]).fit(cov_type="clustered",
                                                                          clusters=s["country"].values)
        fs = sm.OLS(dm["ln_JLoss_l1"], sm.add_constant(dm[["D_l1"] + zs], has_constant="add")).fit()
        F = fs.f_test(np.column_stack([np.zeros((len(zs), 2)), np.eye(len(zs))])).fvalue
        num(f"arb_iv_{lab}_b", m.params["ln_JLoss_l1"]); num(f"arb_iv_{lab}_se", m.std_errors["ln_JLoss_l1"])
        num(f"arb_iv_{lab}_p", m.pvalues["ln_JLoss_l1"]); num(f"arb_iv_{lab}_F", float(np.squeeze(F)))
        num(f"arb_iv_{lab}_N", len(s))
        if len(zs) > 1:
            num(f"arb_iv_{lab}_sargan_p", m.sargan.pval)
        res[lab] = m
    return res


# ================================================================ 4. regresor generado
def bloque_boot_gar(d0, m0, raw):
    rep = pd.read_csv(REPLICAS, usecols=["seed", "country", "quarter", "GaR"])
    rep["country"] = rep["country"].str.lower()
    q = pd.PeriodIndex(rep["quarter"], freq="Q"); rep["_qn"] = q.year * 4 + q.quarter + 1  # rezago t-1
    rep["D_l1_rep"] = -rep["GaR"] * 100
    base_d = d0[["country", "quarter", "t", "_qn", "ln_EMBI", "ln_JLoss_l1", "D_l1"]].copy()
    bs = []
    for s, g in rep.groupby("seed"):
        dd = base_d.merge(g[["country", "_qn", "D_l1_rep"]], on=["country", "_qn"], how="left")
        dd["D_l1"] = dd["D_l1_rep"].fillna(dd["D_l1"])    # paises/trimestres sin replica: valor oficial
        m, _ = p13.fit(dd)
        bs.append((m.params["J_c"], m.params["T_c"], m.params["JxT"]))
    bs = np.array(bs)
    num("arb_bootgar_R", len(bs))
    for i, (k, n) in enumerate((("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT"))):
        sb = bs[:, i].std(ddof=1); sdk = m0.std_errors[n]; sc = np.sqrt(sb ** 2 + sdk ** 2)
        num(f"arb_bootgar_{k}_sd", sb); num(f"arb_bootgar_{k}_se_comb", sc)
        num(f"arb_bootgar_{k}_p_comb", 2 * (1 - stats.norm.cdf(abs(m0.params[n] / sc))))
        num(f"arb_bootgar_{k}_aumento_se", sc / sdk - 1)


# ================================================================ 5. EMstress extendido y permutacion
def bloque_emstress():
    dc = p12.prep_cr()
    ctr = [c for c in CTRLS if c in dc.columns and dc[c].notna().sum() > 50]
    out = {}
    for lab, dums in (("ext", {"bk": p9b.BACKSTOP_Q, "em": EMSTRESS_EXT}),
                      ("taper", {"bk": p9b.BACKSTOP_Q, "em": TAPER}),
                      ("em1516", {"bk": p9b.BACKSTOP_Q, "em": EM1516}),
                      ("em2018", {"bk": p9b.BACKSTOP_Q, "em": EM2018})):
        for fe in ("PT", "T", "P"):
            m, dd, _ = p9b.fit_crisis_model(dc, "CM4", dums, fe, ctr)
            for nm in ("bk", "em"):
                b, se, t, p = p9b._lincom(m, ["JxD", f"JxD_{nm}"])
                num(f"arb_crisis_{lab}_{fe}_{nm}", b); num(f"arb_crisis_{lab}_{fe}_{nm}_p", p)
            num(f"arb_crisis_{lab}_{fe}_b3", m.params["JxD"]); num(f"arb_crisis_{lab}_{fe}_N", m.nobs)
    # misma CM4 (Backstop / EMstress 2015-16, FE pais+tiempo) con errores cluster por pais (G=13),
    # el estandar mas exigente que Driscoll-Kraay con pocos paises
    dums = {"bk": p9b.BACKSTOP_Q, "em": EM1516}
    m, dd, _ = p9b.fit_crisis_model(dc, "CM4", dums, "PT", ctr)
    rhs, _ = p9b._build_rhs("CM4", dums)
    mc = PanelOLS.from_formula(f"_DV ~ {' + '.join(rhs + ctr)} + EntityEffects + TimeEffects",
                               dd.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    for nm in ("bk", "em"):
        b, se, t, p = p9b._lincom(mc, ["JxD", f"JxD_{nm}"])
        num(f"arb_crisis_cluster_{nm}", b); num(f"arb_crisis_cluster_{nm}_p", p)
    # permutacion: todas las ventanas de 3 trimestres consecutivos fuera de Backstop
    qs = sorted(dc["quarter"].unique())
    qn = {q: pd.Period(q, freq="Q").year * 4 + pd.Period(q, freq="Q").quarter for q in qs}
    obs = NUM["arb_crisis_em1516_PT_em"]
    sims, omitidas = [], []
    for i in range(len(qs) - 2):
        w = qs[i:i + 3]
        if any(q in p9b.BACKSTOP_Q for q in w) or qn[w[2]] - qn[w[0]] != 2:
            continue
        # ventana con pocas economias: la interaccion queda absorbida por los EF de tiempo
        if dc.dropna(subset=ctr)[dc.dropna(subset=ctr)["quarter"].isin(w)]["country"].nunique() < 5:
            omitidas.append(w[0])
            continue
        try:
            m, dd, _ = p9b.fit_crisis_model(dc, "CM4", {"bk": p9b.BACKSTOP_Q, "em": w}, "PT", ctr)
        except Exception:
            omitidas.append(w[0])
            continue
        b = p9b._lincom(m, ["JxD", "JxD_em"])[0]
        sims.append((w[0], b))
    num("arb_perm_omitidas", len(omitidas))
    s = pd.DataFrame(sims, columns=["inicio", "suma"])
    p_perm = (s["suma"] >= obs).mean()
    num("arb_perm_n", len(s)); num("arb_perm_p", p_perm); num("arb_perm_obs", obs)
    num("arb_perm_rank", (s["suma"] > obs).sum() + 1)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.hist(s["suma"], bins=25, color=BLUE, alpha=0.75)
    ax.axvline(obs, color=RED, lw=2, label=f"EMstress 2015Q3–2016Q1 ({obs:+.3f})")
    for q0, lab in (("2013Q2", "taper"), ("2018Q2", "2018")):
        v = s.loc[s.inicio == q0, "suma"]
        if len(v):
            ax.axvline(v.iloc[0], color=ORANGE, lw=1.2, ls="--")
            ax.annotate(lab, (v.iloc[0], ax.get_ylim()[1] * 0.9), fontsize=8, color=ORANGE, ha="left")
    ax.set_xlabel(r"$\hat\beta_3+\hat\beta_4$ en una ventana de 3 trimestres (CM4, FE país + tiempo)")
    ax.set_ylabel("número de ventanas")
    ax.set_title(f"Permutación: {len(s)} ventanas fuera de Backstop; p = {p_perm:.3f}", fontsize=9.5)
    ax.legend(fontsize=8)
    p13.save(fig, "fig_permutacion_emstress_arb")


# ================================================================ 6. controles
def cargar_bbg_macro(d):
    add = []
    for c in d.country.unique():
        fx = pd.read_csv(os.path.join(MACRO, c, f"fxvol_{c}.csv"))
        pm = pd.read_csv(os.path.join(MACRO, c, f"prof_margin_{c}.csv"))[["quarter", "prof_margin_system"]]
        x = fx.merge(pm, on="quarter", how="outer"); x["country"] = c
        add.append(x)
    a = pd.concat(add)
    a["prof_margin"] = a["prof_margin_system"] * 100
    return d.merge(a[["country", "quarter", "fx_vol", "prof_margin"]], on=["country", "quarter"], how="left")


def r2_within(m, dd, y="ln_EMBI"):
    ydm = demean2(dd, [y], iters=40)[y].values
    return 1 - float((m.resids ** 2).sum()) / float((ydm ** 2).sum())


def bloque_controles(d):
    ctr = [c for c in CTRLS if d[c].notna().sum() > 50]
    l4 = [c + "_l4" for c in ctr]
    m, _ = p13.fit(d, ctr=l4)
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"arb_ctrl_l4_{k}", m.params[n]); num(f"arb_ctrl_l4_{k}_p", m.pvalues[n])
    num("arb_ctrl_l4_N", m.nobs)
    # canales: el control en t sobre ln JLoss_{t-1} y D_{t-1}
    for c in ("fisc_bal", "reer", "infl_yoy", "debt_gdp"):
        dd = d.dropna(subset=[c, "ln_JLoss_l1", "D_l1"]).copy()
        m = PanelOLS.from_formula(f"{c} ~ ln_JLoss_l1 + D_l1 + EntityEffects + TimeEffects",
                                  dd.set_index(["country", "t"])).fit(**DK)
        num(f"arb_canal_{c}_b", m.params["ln_JLoss_l1"]); num(f"arb_canal_{c}_p", m.pvalues["ln_JLoss_l1"])
        num(f"arb_canal_{c}_N", m.nobs)
    # Oster (2019): delta para b1, R_max = 1,3 R~ (misma muestra con y sin controles)
    s = d.dropna(subset=ctr).copy()
    ms, ds = p13.fit(s); ml, dl = p13.fit(s, ctr=ctr)
    b_s, r_s = ms.params["J_c"], r2_within(ms, ds)
    b_l, r_l = ml.params["J_c"], r2_within(ml, dl)
    rmax = min(1.0, 1.3 * r_l)
    delta0 = (b_l * (r_l - r_s)) / ((b_s - b_l) * (rmax - r_l)) if b_s != b_l else np.nan
    bstar = b_l - (b_s - b_l) * (rmax - r_l) / (r_l - r_s)
    num("arb_oster_b_corto", b_s); num("arb_oster_r_corto", r_s)
    num("arb_oster_b_largo", b_l); num("arb_oster_r_largo", r_l)
    num("arb_oster_rmax", rmax); num("arb_oster_delta_b0", delta0); num("arb_oster_bstar_d1", bstar)


def tabla_chari(d):
    d = cargar_bbg_macro(d)
    specs = [
        ("(1)", ["ln_JLoss_l1"], "PT"),
        ("(2)", ["ln_JLoss_l1", "fx_vol", "prof_margin"], "PT"),
        ("(3)", ["ln_JLoss_l1", "fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp"], "PT"),
        ("(4)", ["ln_JLoss_l1", "fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp",
                 "VIX", "UST10Y_log", "US_HY_spread_log", "OnOffRun_spread_log"], "P"),
        ("(5)", ["ln_JLoss_l1", "D_l1", "fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp",
                 "VIX", "UST10Y_log", "US_HY_spread_log", "OnOffRun_spread_log"], "P"),
        ("(6)", ["ln_JLoss_l1", "D_l1", "fx_vol", "prof_margin", "debt_gdp", "res_gdp", "ca_gdp"], "PT"),
    ]
    lab = {"ln_JLoss_l1": r"$\ln JLoss_{t-1}$", "D_l1": r"$D_{t-1}=-GaR_{t-1}$",
           "fx_vol": "Volatilidad cambiaria", "prof_margin": r"Margen de utilidad bancario (\%)",
           "debt_gdp": r"Deuda/PIB (\%)", "res_gdp": r"Reservas/PIB (\%)", "ca_gdp": r"Cuenta corriente/PIB (\%)",
           "VIX": "VIX", "UST10Y_log": r"$\ln$ tasa Tesoro EE.UU.\ 10 años",
           "US_HY_spread_log": r"$\ln$ spread alto rendimiento EE.UU.", "OnOffRun_spread_log": r"$\ln$ spread on/off-the-run"}
    fits = []
    for nm, x, fe in specs:
        dd = d.dropna(subset=["ln_EMBI"] + x).copy()
        eff = "EntityEffects + TimeEffects" if fe == "PT" else "EntityEffects"
        m = PanelOLS.from_formula(f"ln_EMBI ~ {' + '.join(x)} + {eff}", dd.set_index(["country", "t"])).fit(**DK)
        fits.append((nm, fe, m))
        num(f"arb_chari{nm[1]}_J", m.params["ln_JLoss_l1"]); num(f"arb_chari{nm[1]}_J_p", m.pvalues["ln_JLoss_l1"])
        num(f"arb_chari{nm[1]}_N", m.nobs)
    order = list(lab)
    L = [r"\begin{table}[htbp]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{4pt}",
         r"\caption[Batería estilo Chari et al.\ (2024)]{Spread soberano y fragilidad bancaria: batería de "
         r"controles al estilo de la Tabla 4 de \citet{Chari2024b} (variable dependiente: $\ln$ EMBI)}",
         r"\label{tab:chari-arb}", r"\begin{tabular}{l" + "c" * len(fits) + "}", r"\toprule",
         " & " + " & ".join(n for n, _, _ in fits) + r" \\", r"\midrule"]
    for v in order:
        if not any(v in m.params.index for _, _, m in fits):
            continue
        L.append(lab[v] + " & " + " & ".join(fb(m.params[v], m.pvalues[v], 3) if v in m.params.index else ""
                                              for _, _, m in fits) + r" \\")
        L.append(" & " + " & ".join(fse(m.std_errors[v], 3) if v in m.params.index else ""
                                    for _, _, m in fits) + r" \\")
    L += [r"\midrule",
          "Observaciones & " + " & ".join(str(int(m.nobs)) for _, _, m in fits) + r" \\",
          r"$R^2$ \textit{within} & " + " & ".join(fnum(m.rsquared_within) for _, _, m in fits) + r" \\",
          "EF de país & " + " & ".join("SÍ" for _ in fits) + r" \\",
          "EF de tiempo & " + " & ".join("SÍ" if fe == "PT" else "NO" for _, fe, _ in fits) + r" \\",
          r"\bottomrule", r"\end{tabular}",
          r"\par\smallskip\parbox{0.95\linewidth}{\scriptsize \textit{Nota:} Réplica de la estructura de la "
          r"Tabla 4 de \citet{Chari2024b} con los datos de este trabajo: $JLoss$ rezagado un trimestre y controles "
          r"que se incorporan progresivamente; las columnas (4) y (5) reemplazan los efectos fijos de tiempo por "
          r"factores financieros globales. Volatilidad cambiaria y margen de utilidad del sistema bancario de "
          r"Bloomberg; no se dispone de la serie histórica de la calificación soberana ni del PIB per cápita, que "
          r"\citet{Chari2024b} también incluyen. Errores de Driscoll--Kraay entre paréntesis. ***, ** y * indican "
          r"significancia al 1\%, 5\% y 10\%. Fuente: \texttt{p14\_arbitro\_lnlag.py}.}",
          r"\end{table}"]
    with open(os.path.join(TAB, "tabla_arbitro_chari.tex"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("  tabla_arbitro_chari.tex")


# ================================================================ 7. forma funcional
def _dummies_ols(y, X, d, cluster=True):
    D = pd.get_dummies(d[["country", "quarter"]].astype(str), drop_first=True, dtype=float)
    Z = sm.add_constant(pd.concat([X.reset_index(drop=True), D.reset_index(drop=True)], axis=1))
    kw = dict(cov_type="cluster", cov_kwds={"groups": d["country"].values}) if cluster else {}
    return sm.OLS(np.asarray(y), Z).fit(**kw), Z


def bloque_forma(d):
    dd = d.dropna(subset=["EMBI_bps", "ln_EMBI", "JLoss_l1", "ln_JLoss_l1", "D_l1"]).copy().reset_index(drop=True)
    Jl = dd["JLoss_l1"] - dd["JLoss_l1"].mean(); Jg = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    Dc = dd["D_l1"] - dd["D_l1"].mean()
    Xlin = pd.DataFrame({"J": Jl, "D": Dc, "JxD": Jl * Dc})
    Xlog = pd.DataFrame({"J": Jg, "D": Dc, "JxD": Jg * Dc})
    mlin, _ = _dummies_ols(dd["EMBI_bps"], Xlin, dd)
    mlog, _ = _dummies_ols(dd["ln_EMBI"], Xlog, dd)
    yl = np.clip(mlin.fittedvalues, 1.0, None); yg = mlog.fittedvalues
    # PE (MacKinnon, White y Davidson, 1983)
    m1, _ = _dummies_ols(dd["EMBI_bps"], Xlin.assign(pe=np.log(yl) - yg), dd)
    m2, _ = _dummies_ols(dd["ln_EMBI"], Xlog.assign(pe=yl - np.exp(yg)), dd)
    num("arb_pe_H0lineal_t", m1.tvalues["pe"]); num("arb_pe_H0lineal_p", m1.pvalues["pe"])
    num("arb_pe_H0log_t", m2.tvalues["pe"]); num("arb_pe_H0log_p", m2.pvalues["pe"])
    # Box-Cox sobre el spread, con los regresores de la especificacion principal
    y = dd["EMBI_bps"].values
    sly = np.log(y).sum()
    _, Z = _dummies_ols(dd["ln_EMBI"], Xlog, dd, cluster=False)
    Zv = Z.values
    lams = np.linspace(-0.8, 1.2, 101)
    ll = []
    for lam in lams:
        yt = np.log(y) if abs(lam) < 1e-9 else (y ** lam - 1) / lam
        b = np.linalg.lstsq(Zv, yt, rcond=None)[0]
        ssr = ((yt - Zv @ b) ** 2).sum()
        ll.append(-len(y) / 2 * np.log(ssr / len(y)) + (lam - 1) * sly)
    ll = np.array(ll); i = ll.argmax()
    ci = lams[ll >= ll[i] - 1.92]
    num("arb_boxcox_lambda", lams[i]); num("arb_boxcox_ci_lo", ci.min()); num("arb_boxcox_ci_hi", ci.max())
    num("arb_boxcox_LR_log", 2 * (ll[i] - ll[np.argmin(abs(lams))]))
    num("arb_boxcox_LR_lineal", 2 * (ll[i] - ll[np.argmin(abs(lams - 1))]))
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(lams, ll - ll[i], color=BLUE, lw=2)
    ax.axhline(-1.92, color=RED, ls="--", lw=1, label="IC 95 %")
    for v, lab in ((0, "log"), (1, "lineal")):
        ax.axvline(v, color=INK2, lw=0.8, ls=":"); ax.annotate(lab, (v, -1), fontsize=8, color=INK2)
    ax.set_xlabel(r"$\lambda$ (Box–Cox del spread)"); ax.set_ylabel("log-verosimilitud relativa")
    ax.set_ylim(max((ll - ll[i]).min(), -60), 2)
    ax.set_title(f"Perfil Box–Cox: $\\hat\\lambda$ = {lams[i]:.2f}", fontsize=9.5); ax.legend(fontsize=8)
    p13.save(fig, "fig_boxcox_arb")


# ================================================================ 8. medicion de JLoss
def bloque_jloss(d, raw):
    w = pd.read_csv(WIDE); w["country"] = w["countryname"].str.lower()
    q = pd.PeriodIndex(w["quarter"], freq="Q"); w["_qn"] = q.year * 4 + q.quarter + 1
    w["ln_JLoss_wide_l1"] = np.log(w["JLoss"])
    dd = d.merge(w[["country", "_qn", "ln_JLoss_wide_l1"]], on=["country", "_qn"], how="left")
    num("arb_wide_corr", dd[["ln_JLoss_l1", "ln_JLoss_wide_l1"]].corr().iloc[0, 1])
    x = dd.dropna(subset=["ln_JLoss_wide_l1"]).copy()
    x["ln_JLoss_l1"] = x["ln_JLoss_wide_l1"]
    m, _ = p13.fit(x)
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"arb_wide_{k}", m.params[n]); num(f"arb_wide_{k}_p", m.pvalues[n])
    num("arb_wide_N", m.nobs)
    r = d.copy(); r["ln_JLoss_l1"] = r["JLoss_l1"].rank(pct=True)
    m, _ = p13.fit(r)
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"arb_rank_{k}", m.params[n]); num(f"arb_rank_{k}_p", m.pvalues[n])


# ================================================================ tabla resumen
def tabla_resumen():
    g = NUM.get
    filas = [
        (r"\textit{Causalidad inversa y dinámica}", None),
        (r"Canal inverso: $\ln JLoss_t$ sobre $\ln$ EMBI$_{t-1}$", ("arb_inverso_b", "arb_inverso_p")),
        (r"Principal $+$ adelantos: $\ln JLoss_{t-1}$", ("arb_lead_b1", "arb_lead_b1_p")),
        (r"\quad adelanto $\ln JLoss_{t+1}$", ("arb_lead_fJ", "arb_lead_fJ_p")),
        (r"Dinámica ($+\ln$ EMBI$_{t-1}$): $\ln JLoss_{t-1}$ corto plazo", ("arb_din_b1", "arb_din_b1_p")),
        (r"\quad persistencia $\rho$", ("arb_din_rho", "arb_din_rho_p")),
        (r"\quad efecto de largo plazo $\beta_1/(1-\rho)$", ("arb_din_lp", "arb_din_lp_p")),
        (r"\textit{Inferencia (regresión principal)}", None),
        (r"\textit{Wild cluster bootstrap} $p$: $\beta_1$ / $\beta_2$ / $\beta_3$", "wb"),
        (r"\textit{Identificación en logs}", None),
        (r"Proyección local $h=0$: $\ln JLoss_{t-1}$", ("arb_lp_h0_J", "arb_lp_h0_J_p")),
        (r"Proyección local $h=4$: $\ln JLoss_{t-1}$", ("arb_lp_h4_J", "arb_lp_h4_J_p")),
        (r"IV on/off-the-run ($F$ primera etapa)", ("arb_iv_onoff_b", "arb_iv_onoff_p", "arb_iv_onoff_F")),
        (r"IV dólar amplio", ("arb_iv_usd_b", "arb_iv_usd_p", "arb_iv_usd_F")),
        (r"IV términos de intercambio", ("arb_iv_ctot_b", "arb_iv_ctot_p", "arb_iv_ctot_F")),
        (r"\textit{Regresor generado (500 réplicas del GaR)}", None),
        (r"$p$ combinado: $\beta_1$ / $\beta_2$ / $\beta_3$", "bg"),
        (r"\textit{Controles}", None),
        (r"Controles en $t-4$: $\ln JLoss_{t-1}$", ("arb_ctrl_l4_b1", "arb_ctrl_l4_b1_p")),
        (r"Canal: balance fiscal$_t$ sobre $\ln JLoss_{t-1}$", ("arb_canal_fisc_bal_b", "arb_canal_fisc_bal_p")),
        (r"Canal: TCR$_t$ sobre $\ln JLoss_{t-1}$", ("arb_canal_reer_b", "arb_canal_reer_p")),
        (r"Canal: inflación$_t$ sobre $\ln JLoss_{t-1}$", ("arb_canal_infl_yoy_b", "arb_canal_infl_yoy_p")),
        (r"\textit{Medición de $JLoss$}", None),
        (r"Malla ancha: $\beta_1$", ("arb_wide_b1", "arb_wide_b1_p")),
        (r"Malla ancha: $\beta_3$", ("arb_wide_b3", "arb_wide_b3_p")),
        (r"Percentil de $JLoss_{t-1}$: $\beta_1$", ("arb_rank_b1", "arb_rank_b1_p")),
        (r"Percentil de $JLoss_{t-1}$: $\beta_3$", ("arb_rank_b3", "arb_rank_b3_p")),
    ]
    L = [r"\begin{table}[htbp]", r"\centering", r"\footnotesize",
         r"\caption[Pruebas de identificación, inferencia y medición]{Pruebas de identificación, inferencia y "
         r"medición sobre la especificación principal}", r"\label{tab:arbitro}",
         r"\begin{tabular}{lcc}", r"\toprule", r"Prueba & Coeficiente & $p$ \\", r"\midrule"]
    for lab, keys in filas:
        if keys is None:
            L.append(rf"\multicolumn{{3}}{{l}}{{{lab}}} \\")
        elif keys == "wb":
            L.append(lab + " & & " + " / ".join(fnum(g(f"arb_wb_{k}_webb"), 3) for k in ("b1", "b2", "b3")) + r" \\")
        elif keys == "bg":
            L.append(lab + " & & " + " / ".join(fnum(g(f"arb_bootgar_{k}_p_comb"), 3) for k in ("b1", "b2", "b3")) + r" \\")
        else:
            extra = f" \\;[$F={g(keys[2]):.1f}$]".replace(".", "{,}") if len(keys) > 2 else ""
            L.append(f"{lab} & {fb(g(keys[0]), g(keys[1]))}{extra} & {fnum(g(keys[1]), 3)} \\\\")
    L += [r"\bottomrule", r"\end{tabular}",
          r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize \textit{Nota:} Todas las filas usan la muestra y la "
          r"especificación de la regresión principal salvo indicación (errores de Driscoll--Kraay). \textit{Wild "
          r"cluster bootstrap}: pesos de Webb, 1\,999 réplicas, 13 \textit{clusters}. Proyecciones locales: $\ln$ "
          r"EMBI$_{t+h}$ sobre $\ln JLoss_{t-1}$, $D_{t-1}$ y $\ln$ EMBI$_{t-1}$. IV: $\ln JLoss_{t-1}$ instrumentado "
          r"con un \textit{shift-share} de exposición pre-2012, errores \textit{cluster} por país. Regresor generado: "
          r"error estándar de Driscoll--Kraay combinado en cuadratura con la dispersión de 500 réplicas "
          r"\textit{bootstrap} de la primera etapa del $GaR$. Fuente: \texttt{p14\_arbitro\_lnlag.py}.}",
          r"\end{table}"]
    with open(os.path.join(TAB, "tabla_arbitro_resumen.tex"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("  tabla_arbitro_resumen.tex")


def main():
    print("p14: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]))
    validar_wild_boot()
    print("  wild bootstrap validado contra p2 (p =", NUM["arb_wb_validacion_p2"], ")")
    d, raw = base()
    m0, dd0 = check_principal(d)
    print("  principal reproducida (N=765, b3=-0,0112)")
    out = os.path.join(HERE, "paper_arbitro_numeros.csv")

    def guardar(msg):   # se guarda tras cada bloque: un fallo posterior no borra lo ya calculado
        pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
        print(f"  {msg} ({len(NUM)} cifras)", flush=True)

    bloque_causalidad(d, m0); guardar("1. causalidad/dinamica")
    bloque_inferencia(dd0); guardar("2. inferencia")
    bloque_lp(d, raw); bloque_iv(d); guardar("3. LP e IV")
    bloque_boot_gar(d, m0, raw); guardar("4. regresor generado")
    bloque_emstress(); guardar("5. EMstress")
    bloque_controles(d); tabla_chari(d); guardar("6. controles")
    bloque_forma(d); guardar("7. forma funcional")
    bloque_jloss(d, raw); guardar("8. medicion JLoss")
    tabla_resumen(); guardar("tabla resumen")


if __name__ == "__main__":
    main()
