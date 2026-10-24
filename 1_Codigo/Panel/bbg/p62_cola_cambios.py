# -*- coding: utf-8 -*-
"""
p62_cola_cambios.py -- Q3 del preregistro 7 (4_Redaccion/preregistro_quant.md, commit d968986): ¿la
coincidencia de los dos riesgos ensancha la cola de los cambios del spread, aunque no suba su nivel?

Indicadores sin anticipación (ventana expansiva por país):
  AltaJ_{m-1} = 1 si -DD_lag_{m-1} supera el percentil 2/3 de su país hasta m-1 (>= 36 meses);
  AltaD_m     = 1 si D_{q-2} supera el percentil 2/3 de su país hasta q-2 (>= 12 trimestres);
  Conj        = AltaJ x AltaD.

Q3-H1: MMQR (Machado y Santos Silva, 2019) de d ln s_m, con EF de país y de mes en la localización y EF de
       país en la escala; c3 (escala de Conj) > 0; bootstrap por bloques de país (999).
Q3-H2: VaR al 95% fuera de la muestra (desde 2015-01, reestimado cada mes): regresión cuantílica de r sobre
       los indicadores con indicadoras de país, frente a un VaR normal EWMA (lambda 0,97); Diebold-Mariano
       unilateral sobre la pérdida cuantílica media por mes (Newey-West, 6). Condición: Christoffersen
       (cobertura condicional) con p > 0,05.

Holm sobre Q1-H1 (paper_p60_numeros.csv), Q3-H1 y Q3-H2. Salida: bbg/paper_p62_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, chi2

import p60_senal_dd as p60
from causal_core import demean2

TAUS = (0.05, 0.50, 0.95)
NREP = 999
NUM = {}
REGS = ["AltaJ", "AltaD", "Conj"]


def num(k, v):
    NUM[k] = float(v)
    return v


# ================================================================ indicadores
def alto_expansivo(v, minobs):
    out, hist = [], []
    for a in v:
        if np.isnan(a):
            out.append(np.nan); continue
        hist.append(a)
        out.append(float(a > np.quantile(hist, 2 / 3)) if len(hist) >= minobs else np.nan)
    return np.array(out)


def alto_completo(v):
    q = np.nanquantile(v, 2 / 3)
    return np.where(np.isnan(v), np.nan, (v > q).astype(float))


def datos(expansivo=True):
    x = p60.panel_mensual().sort_values(["country", "month"])
    # AltaJ en m-1
    f = alto_expansivo if expansivo else (lambda v, k: alto_completo(v))
    x["_aj"] = x.groupby("country")["DD_lag"].transform(lambda s: pd.Series(f(-s.values, 36), index=s.index))
    prev_m = x.groupby("country")["month"].shift(1)
    cont = (x["month"] - prev_m).apply(lambda d: getattr(d, "n", np.nan)) == 1
    x["AltaJ"] = np.where(cont, x.groupby("country")["_aj"].shift(1), np.nan)
    # AltaD con el trimestre q-2
    g = pd.read_csv(p60.PANEL, usecols=["country", "quarter", "GaR_pp"]).dropna()
    g["q2"] = pd.PeriodIndex(g["quarter"], freq="Q"); g["D"] = -g["GaR_pp"]
    g = g.sort_values(["country", "q2"])
    g["AltaD"] = g.groupby("country")["D"].transform(lambda s: pd.Series(f(s.values, 12), index=s.index))
    x = x.merge(g[["country", "q2", "AltaD"]], on=["country", "q2"], how="left")
    x["Conj"] = x["AltaJ"] * x["AltaD"]
    # cambios del spread a uno y tres meses
    x["dy"] = np.log(x["s"]) - np.log(x["s_l1"])
    g3 = x.groupby("country")
    s2, m2 = g3["s"].shift(-2), g3["month"].shift(-2)
    ok3 = ((m2 - x["month"]).apply(lambda d: getattr(d, "n", np.nan)) == 2) & x["s_l1"].notna()
    x["dy3"] = np.where(ok3, np.log(s2) - np.log(x["s_l1"]), np.nan)
    return x.reset_index(drop=True)


# ================================================================ MMQR
def mmqr(d, y, fe_tiempo=True):
    d = d.copy(); d["_t"] = d["month"].astype(str)
    if fe_tiempo:
        Y = demean2(d, [y], "country", "_t", 40)[y].values
        X = demean2(d, REGS, "country", "_t", 40).values
    else:
        Y = (d[y] - d.groupby("country")[y].transform("mean")).values
        X = (d[REGS] - d.groupby("country")[REGS].transform("mean")).values
    b_loc = np.linalg.lstsq(X, Y, rcond=None)[0]
    r = Y - X @ b_loc
    a = np.abs(r)
    ac = a - pd.Series(a).groupby(d["country"].values).transform("mean").values
    Xc = (d[REGS] - d.groupby("country")[REGS].transform("mean")).values
    b_esc = np.linalg.lstsq(Xc, ac, rcond=None)[0]
    esc = (a - ac) + Xc @ b_esc
    u = np.where(esc > 1e-8, r / np.where(esc > 1e-8, esc, 1), np.nan)
    q = np.nanquantile(u, TAUS)
    return b_loc, b_esc, {t: b_loc + b_esc * qt for t, qt in zip(TAUS, q)}


def boot_c3(d, y, fe_tiempo=True, nrep=NREP, seed=p60.SEMILLA):
    rng = np.random.default_rng(seed); paises = d["country"].unique(); out = []
    por = {c: d[d["country"] == c] for c in paises}
    for _ in range(nrep):
        pick = rng.choice(paises, len(paises), replace=True)
        xb = pd.concat([por[c].assign(country=f"{c}_{k}") for k, c in enumerate(pick)], ignore_index=True)
        if xb["Conj"].sum() == 0:
            continue
        try:
            out.append(mmqr(xb, y, fe_tiempo)[1])
        except Exception:
            continue
    return np.array(out)


def q3h1(d, pref, y="dy", fe_tiempo=True):
    s = d.dropna(subset=[y] + REGS)
    s = s[s["month"] >= p60.INICIO]
    b_loc, b_esc, bq = mmqr(s, y, fe_tiempo)
    reps = boot_c3(s, y, fe_tiempo)
    p = float((reps[:, 2] <= 0).mean())
    num(f"{pref}_N", len(s)); num(f"{pref}_n_conj", s["Conj"].sum())
    for j, lab in enumerate(REGS):
        num(f"{pref}_loc_{lab}", b_loc[j]); num(f"{pref}_esc_{lab}", b_esc[j])
        num(f"{pref}_esc_{lab}_p_uni", float((reps[:, j] <= 0).mean()))
    for t in TAUS:
        num(f"{pref}_q{int(t*100)}_Conj", bq[t][2])
    num(f"{pref}_c3_p", p); num(f"{pref}_nboot", len(reps))
    print(f"  {pref:<18} N={len(s)} conj={int(s['Conj'].sum())}  escala: J {b_esc[0]:+.4f} D {b_esc[1]:+.4f} "
          f"Conj {b_esc[2]:+.4f} (p uni {p:.3f})  loc Conj {b_loc[2]:+.4f}")
    return p


# ================================================================ VaR fuera de la muestra
def var_pronosticos(d, tau=0.05, hasta_excluir=None):
    d = d.dropna(subset=["r"]).sort_values(["country", "month"]).copy()
    meses = sorted(m for m in d["month"].unique() if m >= p60.INICIO)
    z = norm.ppf(tau); lam = 0.97
    # EWMA por país (recursivo, solo con el pasado)
    d["v_ewma"] = np.nan
    for c, g in d.groupby("country"):
        r = g["r"].values
        if len(r) <= 12:
            continue
        v = np.var(r[:12]); vals = [np.nan] * 12
        for k in range(12, len(r)):
            vals.append(v)                           # pronóstico para k con la información hasta k-1
            v = lam * v + (1 - lam) * r[k] ** 2
        d.loc[g.index, "v_ewma"] = vals
    d["q_ewma"] = z * np.sqrt(d["v_ewma"])
    d["q_hist"] = d.groupby("country")["r"].transform(
        lambda s: s.shift(1).rolling(60, min_periods=24).quantile(tau))
    d["q_cond"] = np.nan
    base = d.dropna(subset=REGS)
    for m in meses:
        tr = base[base["month"] < m]
        te = base[base["month"] == m]
        if len(te) == 0 or len(tr) < 100:
            continue
        paises = sorted(tr["country"].unique())
        def dis(f):
            D = pd.get_dummies(pd.Categorical(f["country"], categories=paises), drop_first=True, dtype=float)
            D.index = f.index
            return sm.add_constant(pd.concat([f[REGS], D], axis=1), has_constant="add")
        te = te[te["country"].isin(paises)]
        if len(te) == 0:
            continue
        res = sm.QuantReg(tr["r"].values, dis(tr).values).fit(q=tau, max_iter=5000)
        d.loc[te.index, "q_cond"] = dis(te).values @ res.params
    ev = d[(d["month"] >= p60.INICIO)].dropna(subset=["q_cond", "q_ewma", "q_hist"])
    if hasta_excluir is not None:
        ev = ev[~ev["month"].between(*hasta_excluir)]
    return ev


def tick(r, q, tau):
    return (tau - (r < q).astype(float)) * (r - q)


def christoffersen(ev, col, tau):
    hit = (ev["r"] < ev[col]).astype(int)
    n1 = hit.sum(); n = len(hit); pi = n1 / n
    lr_uc = -2 * (n1 * np.log(tau) + (n - n1) * np.log(1 - tau)
                  - (n1 * np.log(max(pi, 1e-12)) + (n - n1) * np.log(max(1 - pi, 1e-12))))
    n00 = n01 = n10 = n11 = 0
    for c, g in ev.assign(h=hit.values).groupby("country"):
        h = g.sort_values("month")["h"].values; mm = g.sort_values("month")["month"].values
        for a in range(1, len(h)):
            if (mm[a] - mm[a - 1]).n != 1:
                continue
            n00 += (h[a - 1] == 0) & (h[a] == 0); n01 += (h[a - 1] == 0) & (h[a] == 1)
            n10 += (h[a - 1] == 1) & (h[a] == 0); n11 += (h[a - 1] == 1) & (h[a] == 1)
    p01 = n01 / max(n00 + n01, 1); p11 = n11 / max(n10 + n11, 1); p_ = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    ll = lambda p, a, b: a * np.log(max(1 - p, 1e-12)) + b * np.log(max(p, 1e-12))
    lr_ind = -2 * (ll(p_, n00 + n10, n01 + n11) - ll(p01, n00, n01) - ll(p11, n10, n11))
    return dict(tasa=pi, p_uc=float(chi2.sf(lr_uc, 1)), p_cc=float(chi2.sf(lr_uc + lr_ind, 2)))


def diebold_mariano(ev, base, tau):
    l_c = tick(ev["r"], ev["q_cond"], tau); l_b = tick(ev["r"], ev[base], tau)
    dm = (l_b - l_c).groupby(ev["month"].values).mean()
    b, t = p60.nw_media(dm.values)
    return float(b[0]), float(t[0]), float(norm.sf(t[0])), len(dm)


def q3h2(d, pref, tau=0.05, base="q_ewma", excl=None):
    ev = var_pronosticos(d, tau, excl)
    dif, t, p, T = diebold_mariano(ev, base, tau)
    num(f"{pref}_N", len(ev)); num(f"{pref}_meses", T)
    num(f"{pref}_dm_dif", dif); num(f"{pref}_dm_t", t); num(f"{pref}_dm_p", p)
    for col in ("q_cond", "q_ewma", "q_hist"):
        c = christoffersen(ev, col, tau)
        for k, v in c.items():
            num(f"{pref}_{col}_{k}", v)
        num(f"{pref}_{col}_tick", tick(ev["r"], ev[col], tau).mean())
    cc = NUM[f"{pref}_q_cond_p_cc"]
    print(f"  {pref:<18} N={len(ev)} meses={T}  DM vs {base}: t={t:.2f} p={p:.3f}  "
          f"tasa cond {NUM[f'{pref}_q_cond_tasa']:.3f} (CC p {cc:.3f}); ewma {NUM[f'{pref}_q_ewma_tasa']:.3f}; "
          f"hist {NUM[f'{pref}_q_hist_tasa']:.3f}")
    return p, cc


def holm(ps):
    orden = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(orden):
        run = max(run, (m - k) * ps[i]); adj[i] = min(1.0, run)
    return adj


def main():
    print("p62: Q3, la cola de los cambios del spread bajo simultaneidad")
    d = datos()
    p_h1 = q3h1(d, "q3h1")
    p_h2, cc = q3h2(d, "q3h2")
    # secundarias
    q3h1(d, "s_h3", y="dy3")
    q3h1(d[~d["month"].between(pd.Period("2020-01", freq="M"), pd.Period("2021-12", freq="M"))], "s_sin2020")
    q3h2(d, "s_var_sin2020", excl=(pd.Period("2020-01", freq="M"), pd.Period("2021-12", freq="M")))
    q3h1(datos(expansivo=False), "s_terciles_completos")
    q3h2(d, "s_var99", tau=0.01)
    q3h2(d, "s_var_vs_hist", base="q_hist")
    q3h1(d, "s_sin_ef_mes", fe_tiempo=False)
    # Holm sobre la familia primaria
    p1 = pd.read_csv(os.path.join(HERE, "paper_p60_numeros.csv"), index_col=0)["valor"]
    ps = np.array([p1["q1h1_p"], p_h1, p_h2])
    adj = holm(ps)
    for k, v in zip(("q1h1", "q3h1", "q3h2"), adj):
        num(f"holm_{k}", v)
    num("q1h1_pasa", float(adj[0] < 0.05 and p1["sin_turquia_sr"] > 0))
    num("q3h1_pasa", float(adj[1] < 0.05))
    num("q3h2_pasa", float(adj[2] < 0.05 and cc > 0.05))
    print(f"  Holm: Q1-H1 {adj[0]:.3f}  Q3-H1 {adj[1]:.3f}  Q3-H2 {adj[2]:.3f}  "
          f"(pasan: {int(NUM['q1h1_pasa'])}, {int(NUM['q3h1_pasa'])}, {int(NUM['q3h2_pasa'])})")
    out = os.path.join(HERE, "paper_p62_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
