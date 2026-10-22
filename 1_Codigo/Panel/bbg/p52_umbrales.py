# -*- coding: utf-8 -*-
"""
p52_umbrales.py -- U1-U3 del preregistro 4 (4_Redaccion/preregistro_umbrales.md, commit 7ad3810):
umbrales de vigilancia agrupados y por país, comparación entre ambos (C1-C5) y simulación de potencia.

  Modelo agrupado: ln EMBI = sum_x (b_x x + d_x x*H) + L + delta*H + phi*q_s + EF país + EF tiempo,
  H = 1[q > gamma]. d_x es la diferencia de pendientes alto - bajo. gamma por MCO concentrados tras la
  transformación within bidireccional (proyección exacta sobre las indicadoras de país y de tiempo), malla
  de hasta 200 valores entre los percentiles 15 y 85 de q, con >= 15 % de las observaciones y >= 3 países
  en cada régimen.
    U1: q = FCI_{t-1}, S = {J, T}, L = {JxT}.     U2: q = deuda_{t-4} (debt_q), S = {T}, L = {J, JxT}.
    U3: q = D_{t-1}, S = {J}, L = {T}.
  Linealidad: sup-LR = n (SSR_lin - SSR(gamma))/SSR(gamma); p del bootstrap por bloques de país (999):
  cada país conserva sus regresores y recibe un bloque circular de residuos del modelo lineal de un país
  sorteado (adaptación de Hansen 1999 a un panel no balanceado, declarada); variante wild por país
  (Rademacher). IC de gamma por inversión del LR (7,35 al 95 %; 5,94 al 90 %). Diferencias con DK y wild
  por país (p32.wild, Webb, 999), p unilateral en la dirección predicha (> 0). Sin cada país: gamma y
  diferencias.
  Por país (>= 50 trimestres con q): y = ln EMBI - lambda_t (efectos de tiempo de la principal lineal),
  constante, q, H, S, S*H y L; variante con controles globales en t-1 (ln VIX, ln UST10Y, ln US HY).
  IC de gamma por inversión del LR escalado por eta^2 (Hansen 2000, núcleo de Epanechnikov en gamma) y
  percentil de bootstrap por bloques móviles (4 trimestres, 999); linealidad con el bootstrap de
  regresores fijos (Hansen 1996, 999); Holm sobre los países.
  C1-C5 y potencia como en el preregistro (secciones 3 y 5).
Salida: bbg/paper_p52_numeros.csv, bbg/umbrales_pais_bbg.csv y la figura fig_umbrales_pais.
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
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p45_macro_preregistrada as p45

NUM = p32.NUM
B = int(os.environ.get("P52_B", 999))
GAR = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
MIN_T = 50
GLOB = ["lnVIX_l1", "UST10Y_log_l1", "US_HY_spread_log_l1"]
ES = {"brazil": "Brasil", "chile": "Chile", "china": "China", "colombia": "Colombia", "india": "India",
      "indonesia": "Indonesia", "malaysia": "Malasia", "mexico": "México", "peru": "Perú", "philippines": "Filipinas",
      "poland": "Polonia", "southafrica": "Sudáfrica", "turkey": "Turquía"}


def num(k, v):
    NUM[k] = float(v)


def qlin(qcol):
    """q entra en forma lineal salvo que ya sea un regresor (U3: q = D_{t-1}, que es T)."""
    return [] if qcol == "D_l1" else ["q_s"]


# ================================================================ datos
def fci(f, nombre):
    x = pd.read_excel(os.path.join(GAR, f))
    x["country"] = x["Country"].str.lower()
    q = pd.PeriodIndex(pd.to_datetime(x["Date"], format="%d/%m/%Y"), freq="Q")
    x["_qn"] = q.year * 4 + q.quarter
    return x[["country", "_qn", "FCI", "VIX"]].rename(columns={"FCI": nombre, "VIX": nombre + "_vix"})


def preparar():
    d, raw = p42.preparar()                       # base + DEBT (con relleno anual) en t-4; verifica la principal
    r = pd.read_csv(p42.RES)
    q = pd.PeriodIndex(r["quarter"], freq="Q"); r["_qn"] = q.year * 4 + q.quarter
    d = d.merge(p14.shift(r, "debt_q", 4, "debtq_l4"), on=["country", "_qn"], how="left")
    for f, nom in (("GaR_panel_all18.xlsx", "FCI"), ("GaR_panel_all19_noRyr.xlsx", "FCInr")):
        x = fci(f, nom)
        # FCI ortogonal al VIX: residuo de una regresión por país en toda su historia
        if nom == "FCI":
            x["FCIov"] = np.nan
            for c, g in x.dropna(subset=["FCI", "FCI_vix"]).groupby("country"):
                b = np.polyfit(g["FCI_vix"], g["FCI"], 1)
                x.loc[g.index, "FCIov"] = g["FCI"] - np.polyval(b, g["FCI_vix"])
            d = d.merge(p14.shift(x, "FCIov", 1, "FCIov_l1"), on=["country", "_qn"], how="left")
        d = d.merge(p14.shift(x, nom, 1, nom + "_l1"), on=["country", "_qn"], how="left")
    raw = raw.copy(); raw["lnVIX"] = np.log(raw["VIX"])
    for c in ("lnVIX", "UST10Y_log", "US_HY_spread_log"):
        d = d.merge(p14.shift(raw, c, 1, c + "_l1"), on=["country", "_qn"], how="left")
    dd = pd.read_csv(os.path.join(HERE, "fragilidad_alternativa_bbg.csv"))
    q = pd.PeriodIndex(dd["quarter"], freq="Q"); dd["_qn"] = q.year * 4 + q.quarter
    dd["F_DD"] = -dd["DD_w"]
    d = d.merge(p14.shift(dd, "F_DD", 1, "FDD_l1"), on=["country", "_qn"], how="left")
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    # percentil propio del FCI: toda la muestra del país y expansivo (mínimo 12 trimestres)
    d = d.sort_values(["country", "_qn"])
    d["FCIpct_l1"] = d.groupby("country")["FCI_l1"].rank(pct=True) * 100
    def expans(s):
        v = s.values; out = np.full(len(v), np.nan)
        for i in range(len(v)):
            h = v[:i + 1]; h = h[~np.isnan(h)]
            if len(h) >= 12 and not np.isnan(v[i]):
                out[i] = (h <= v[i]).mean() * 100
        return pd.Series(out, index=s.index)
    d["FCIexp_l1"] = d.groupby("country")["FCI_l1"].transform(expans)
    return d, raw


def lambdas(d):
    """efectos de tiempo de la regresión principal lineal (para los modelos por país), media cero."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"])).reset_index(drop=True)
    C = pd.get_dummies(x["country"]).values.astype(float)
    Tq = pd.get_dummies(x["quarter"])
    X = np.column_stack([x[["J_c", "T_c", "JxT"]].values, C, Tq.values[:, 1:].astype(float)])
    b = np.linalg.lstsq(X, x["ln_EMBI"].values, rcond=None)[0]
    lam = np.concatenate([[0.0], b[3 + C.shape[1]:]])
    return pd.Series(lam - lam.mean(), index=Tq.columns)


# ================================================================ núcleo agrupado
def aniquilador(x):
    D = np.column_stack([pd.get_dummies(x["country"]).values, pd.get_dummies(x["quarter"]).values]).astype(float)
    return np.eye(len(x)) - D @ np.linalg.pinv(D)


def malla(q, paises, minfrac=0.15, minpais=3, n=200):
    g = np.unique(np.quantile(q, np.linspace(.15, .85, n)))
    ok = []
    for v in g:
        H = q > v
        if min(H.mean(), 1 - H.mean()) >= minfrac and len(set(paises[H])) >= minpais and len(set(paises[~H])) >= minpais:
            ok.append(v)
    return np.array(ok)


def ssr_mat(Q, Y):
    return (Y * Y).sum(0) - ((Q.T @ Y) ** 2).sum(0)


def umbral_agrupado(x, qcol, S, L, boot=True, seed=11):
    """x centrado (J_c, T_c, JxT), sin faltantes. Devuelve dict con gamma, LR, p y la malla."""
    x = x.reset_index(drop=True)
    M = aniquilador(x)
    q = x[qcol].values.astype(float)
    x = x.assign(q_s=(q - q.mean()) / q.std())
    y = M @ x["ln_EMBI"].values
    X0 = M @ x[S + L + qlin(qcol)].values.astype(float)
    Q0, _ = np.linalg.qr(X0)
    grid = malla(q, x["country"].values)
    Qs = []
    for g in grid:
        H = (q > g).astype(float)
        Z = M @ np.column_stack([x[S].values * H[:, None], H])
        Qs.append(np.linalg.qr(np.column_stack([X0, Z]))[0])
    n = len(y)
    s0 = float(ssr_mat(Q0, y[:, None])[0])
    s = np.array([float(ssr_mat(Qg, y[:, None])[0]) for Qg in Qs])
    i = int(s.argmin()); g_hat = grid[i]
    LRg = n * (s - s[i]) / s[i]
    LR = n * (s0 - s[i]) / s[i]
    out = dict(gamma=g_hat, LR=LR, grid=grid, LRg=LRg, n=n,
               ci95=(grid[LRg <= 7.35].min(), grid[LRg <= 7.35].max()),
               ci90=(grid[LRg <= 5.94].min(), grid[LRg <= 5.94].max()))
    if boot:
        b0 = np.linalg.lstsq(X0, y, rcond=None)[0]
        fit0 = X0 @ b0; e0 = y - fit0
        rng = np.random.default_rng(seed)
        paises = x["country"].values; uniq = list(dict.fromkeys(paises))
        idx = {c: np.where(paises == c)[0] for c in uniq}           # filas ordenadas por tiempo
        def sup(Y):
            S0 = ssr_mat(Q0, Y); S1 = np.min(np.vstack([ssr_mat(Qg, Y) for Qg in Qs]), axis=0)
            return n * (S0 - S1) / S1
        # (a) bloques de país
        E = np.zeros((n, B))
        for b in range(B):
            for c in uniq:
                k = uniq[rng.integers(len(uniq))]; ek = e0[idx[k]]; Tj = len(idx[c])
                st = rng.integers(len(ek))
                E[idx[c], b] = ek[(st + np.arange(Tj)) % len(ek)]
        Y = M @ (fit0[:, None] + E)
        out["p_bloques"] = float(np.mean(sup(Y) >= LR))
        # (b) wild por país (Rademacher)
        W = rng.choice([-1.0, 1.0], size=(len(uniq), B))
        wi = np.array([uniq.index(c) for c in paises])
        Y = M @ (fit0[:, None] + e0[:, None] * W[wi, :])
        out["p_wild"] = float(np.mean(sup(Y) >= LR))
    return out


def diferencias(x, qcol, S, L, g):
    """pendientes por régimen en gamma: diferencia (coef. de x*H) con DK y wild por país."""
    x = x.copy(); q = x[qcol].values
    x["q_s"] = (q - q.mean()) / q.std(); x["H"] = (q > g).astype(float)
    hs = []
    for s in S:
        x[s + "_H"] = x[s] * x["H"]; hs.append(s + "_H")
    rhs = S + hs + L + ["H"] + qlin(qcol)
    m = p42.fit(x, "ln_EMBI", rhs)
    res = {}
    for s in S:
        d = float(m.params[s + "_H"]); pw = p32.wild(x, "ln_EMBI", rhs, s + "_H")
        res[s] = dict(bajo=float(m.params[s]), alto=float(m.params[s]) + d, dif=d,
                      p_dk=float(m.pvalues[s + "_H"]), p_uni=p42.unilateral(pw, d, +1))
    res["frac_alto"] = float(x["H"].mean())
    res["frac_alto_pais"] = x.groupby("country")["H"].mean().to_dict()
    return res


def bloque_agrupado(d, pref, qcol, S, L, loo=False, boot=True):
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", qcol] + [c for c in S + L if c not in ("J_c", "T_c", "JxT")]))
    u = umbral_agrupado(x, qcol, S, L, boot=boot)
    num(f"{pref}_N", u["n"]); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_gamma", u["gamma"]); num(f"{pref}_gamma_pct", (x[qcol] <= u["gamma"]).mean() * 100)
    num(f"{pref}_LR", u["LR"]); num(f"{pref}_ci95_lo", u["ci95"][0]); num(f"{pref}_ci95_hi", u["ci95"][1])
    num(f"{pref}_ci90_lo", u["ci90"][0]); num(f"{pref}_ci90_hi", u["ci90"][1])
    num(f"{pref}_malla_lo", u["grid"].min()); num(f"{pref}_malla_hi", u["grid"].max())
    if boot:
        num(f"{pref}_p_bloques", u["p_bloques"]); num(f"{pref}_p_wild", u["p_wild"])
    r = diferencias(x, qcol, S, L, u["gamma"])
    for s in S:
        for k, v in r[s].items():
            num(f"{pref}_{s}_{k}", v)
    num(f"{pref}_frac_alto", r["frac_alto"])
    for c, v in r["frac_alto_pais"].items():
        num(f"{pref}_alto_{c}", v)
    if loo:
        signos = {s: 0 for s in S}; gs = []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]
            uc = umbral_agrupado(xc, qcol, S, L, boot=False); gs.append(uc["gamma"])
            rc = diferencias(xc, qcol, S, L, uc["gamma"])
            for s in S:
                signos[s] += int(rc[s]["dif"] > 0)
                num(f"{pref}_sin_{c}_{s}_dif", rc[s]["dif"]); num(f"{pref}_sin_{c}_{s}_p_uni", rc[s]["p_uni"])
            num(f"{pref}_sin_{c}_gamma", uc["gamma"])
        for s in S:
            num(f"{pref}_{s}_loo_pos", signos[s])
        num(f"{pref}_loo_gamma_min", min(gs)); num(f"{pref}_loo_gamma_max", max(gs))
        num(f"{pref}_loo_n", x["country"].nunique())
    return x, u, r


# ================================================================ por país
def malla_pais(q, n=60, minobs=10):
    g = np.unique(np.quantile(q, np.linspace(.15, .85, n)))
    return np.array([v for v in g if min((q > v).sum(), (q <= v).sum()) >= minobs])


def disenio(xc, qcol, S, L, extra):
    q = xc[qcol].values.astype(float)
    cols = [np.ones(len(xc))] + ([q] if qlin(qcol) else [])
    X0 = np.column_stack(cols + [xc[S + L + extra].values.astype(float)])
    return q, X0


def alt(X0, Sx, q, g):
    H = (q > g).astype(float)
    return np.column_stack([X0, Sx * H[:, None], H]), H


def umbral_pais(xc, qcol, S, L, extra, seed=5, boot=True):
    xc = xc.sort_values("_qn").reset_index(drop=True)
    y = xc["y_net"].values
    q, X0 = disenio(xc, qcol, S, L, extra)
    Sx = xc[S].values.astype(float)
    grid = malla_pais(q)
    if len(grid) == 0:
        return None
    Qs, Xs = [], []
    for g in grid:
        X, _ = alt(X0, Sx, q, g); Xs.append(X); Qs.append(np.linalg.qr(X)[0])
    Q0 = np.linalg.qr(X0)[0]; n = len(y)
    s0 = float(ssr_mat(Q0, y[:, None])[0])
    s = np.array([float(ssr_mat(Qg, y[:, None])[0]) for Qg in Qs])
    i = int(s.argmin()); g_hat = grid[i]
    LRg = n * (s - s[i]) / s[i]; LR = n * (s0 - s[i]) / s[i]
    # eta^2 (Hansen 2000): delta = parámetros del régimen alto, núcleo de Epanechnikov en gamma
    X, H = alt(X0, Sx, q, g_hat)
    b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    k0 = X0.shape[1]; delta = b[k0:]
    dx = np.column_stack([Sx, np.ones(n)]) @ delta
    h = 1.06 * q.std() * n ** (-0.2)
    u = (q - g_hat) / h; w = np.where(np.abs(u) < 1, 0.75 * (1 - u ** 2), 0.0)
    sig2 = s[i] / n
    eta2 = float((w * dx ** 2 * e ** 2).sum() / (sig2 * (w * dx ** 2).sum())) if (w * dx ** 2).sum() > 0 else 1.0
    eta2 = max(eta2, 1e-6)
    ci = {lev: (grid[LRg / eta2 <= c].min(), grid[LRg / eta2 <= c].max()) for lev, c in (("90", 5.94), ("95", 7.35))}
    ci_set90 = grid[LRg / eta2 <= 5.94]
    res = dict(gamma=g_hat, LR=LR, eta2=eta2, ci90=ci["90"], ci95=ci["95"], ci_set90=ci_set90, n=n, grid=grid,
               q=q, ssr=s, ssr0=s0)
    # pendientes por régimen con HAC
    names = ["c", "q"] + S + L + extra + [z + "_H" for z in S] + ["H"]
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    for j, z in enumerate(S):
        jb, jh = 1 + len(qlin(qcol)) + j, k0 + j
        res[z] = dict(bajo=float(m.params[jb]), alto=float(m.params[jb] + m.params[jh]),
                      dif=float(m.params[jh]), p_dif=float(m.pvalues[jh]))
    res["frac_alto"] = float(H.mean())
    if boot:
        rng = np.random.default_rng(seed)
        b0 = np.linalg.lstsq(X0, y, rcond=None)[0]; e0 = y - X0 @ b0
        Y = e0[:, None] * rng.standard_normal((n, B))           # regresores fijos (Hansen 1996)
        S0 = ssr_mat(Q0, Y); S1 = np.min(np.vstack([ssr_mat(Qg, Y) for Qg in Qs]), axis=0)
        res["p_lin"] = float(np.mean(n * (S0 - S1) / S1 >= LR))
        # bloques móviles (pares), 4 trimestres
        gb = []
        nb = int(np.ceil(n / 4))
        for _ in range(B):
            st = rng.integers(0, n - 3, size=nb)
            ii = (st[:, None] + np.arange(4)).ravel()[:n]
            yb, qb, X0b, Sxb = y[ii], q[ii], X0[ii], Sx[ii]
            gridb = [g for g in grid if min((qb > g).sum(), (qb <= g).sum()) >= 10]
            if not gridb:
                continue
            sb = [np.sum((yb - alt(X0b, Sxb, qb, g)[0] @ np.linalg.lstsq(alt(X0b, Sxb, qb, g)[0], yb, rcond=None)[0]) ** 2)
                  for g in gridb]
            gb.append(gridb[int(np.argmin(sb))])
        res["ci90_bb"] = (float(np.quantile(gb, .05)), float(np.quantile(gb, .95)))
    return res


def holm(ps):
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden); acum = 0.0; out = {}
    for r, (k, p) in enumerate(orden):
        acum = max(acum, min(1.0, (m - r) * p)); out[k] = acum
    return out


def bloque_pais(d, lam, pref, qcol, S, L, g_pool, g_pool_pct=None, extra=(), boot=True, c5=False):
    """umbrales por país; C1, C3, C4 y (opcional) C5. Devuelve las filas y las piezas de C2."""
    extra = list(extra)
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", qcol] + extra +
                              [c for c in S + L if c not in ("J_c", "T_c", "JxT")]))
    x = x.assign(y_net=x["ln_EMBI"] - x["quarter"].map(lam))
    filas, piezas = [], {}
    paises = [c for c, g in x.groupby("country") if len(g) >= MIN_T]
    num(f"{pref}_n_paises", len(paises))
    for c in paises:
        xc = x[x["country"] == c]
        r = umbral_pais(xc, qcol, S, L, extra, boot=boot)
        if r is None:
            continue
        pct = lambda v: float((r["q"] <= v).mean() * 100)
        f = dict(variable=pref, pais=c, T=r["n"], gamma=r["gamma"], gamma_pct=pct(r["gamma"]),
                 ci90_lo=r["ci90"][0], ci90_hi=r["ci90"][1], ci95_lo=r["ci95"][0], ci95_hi=r["ci95"][1],
                 ci90_lo_pct=pct(r["ci90"][0]), ci90_hi_pct=pct(r["ci90"][1]), LR=r["LR"], eta2=r["eta2"],
                 frac_alto=r["frac_alto"],
                 contiene_pool=float(r["ci90"][0] <= g_pool <= r["ci90"][1]))
        if g_pool_pct is not None:
            f["contiene_pool_pct"] = float(pct(r["ci90"][0]) <= g_pool_pct <= pct(r["ci90"][1]))
        if boot:
            f["p_lin"] = r["p_lin"]; f["ci90_bb_lo"], f["ci90_bb_hi"] = r["ci90_bb"]
        for z in S:
            for k, v in r[z].items():
                f[f"{z}_{k}"] = v
        if c5:   # quiebre en una fecha con la misma malla relativa
            xs = xc.sort_values("_qn").reset_index(drop=True)
            y = xs["y_net"].values; n = len(y)
            _, X0 = disenio(xs, qcol, S, L, extra); Sx = xs[S].values.astype(float)
            tt = np.arange(n)
            sb = []
            for k in range(int(.15 * n), int(.85 * n) + 1):
                X, _ = alt(X0, Sx, tt, k - 0.5)
                sb.append(np.sum((y - X @ np.linalg.lstsq(X, y, rcond=None)[0]) ** 2))
            f["ssr_umbral"] = float(r["ssr"].min()); f["ssr_quiebre"] = float(min(sb))
            f["quiebre_mejor"] = float(min(sb) <= r["ssr"].min())
        filas.append(f); piezas[c] = xc
    if boot and filas:
        hp = holm({f["pais"]: f["p_lin"] for f in filas})
        for f in filas:
            f["p_lin_holm"] = hp[f["pais"]]
        num(f"{pref}_paises_lin_holm05", sum(f["p_lin_holm"] < 0.05 for f in filas))
        num(f"{pref}_paises_lin_p05", sum(f["p_lin"] < 0.05 for f in filas))
    if filas:
        F = pd.DataFrame(filas)
        num(f"{pref}_C1_contienen", F["contiene_pool"].sum()); num(f"{pref}_C1_de", len(F))
        if "contiene_pool_pct" in F:
            num(f"{pref}_C1pct_contienen", F["contiene_pool_pct"].sum())
        num(f"{pref}_C3_pct_min", F["gamma_pct"].min()); num(f"{pref}_C3_pct_max", F["gamma_pct"].max())
        num(f"{pref}_C3_pct_med", F["gamma_pct"].median()); num(f"{pref}_C3_pct_sd", F["gamma_pct"].std())
        for z in S:
            v = F[f"{z}_dif"]
            num(f"{pref}_C4_{z}_mg", v.mean()); num(f"{pref}_C4_{z}_mg_se", v.std() / np.sqrt(len(v)))
            num(f"{pref}_C4_{z}_pos", (v > 0).sum())
        if c5:
            num(f"{pref}_C5_quiebre_mejor", F["quiebre_mejor"].sum())
    return filas, piezas


def c2_comun(piezas, qcol, S, L, extra, pool_grid, pref, seed=3, nb=499):
    """F_H: umbral común (pendientes propias) frente a umbrales por país, con wild bajo el común."""
    extra = list(extra)
    datos = {}
    for c, xc in piezas.items():
        xs = xc.sort_values("_qn").reset_index(drop=True)
        q, X0 = disenio(xs, qcol, S, L, extra); Sx = xs[S].values.astype(float)
        y = xs["y_net"].values
        Q0 = np.linalg.qr(X0)[0]
        own = [np.linalg.qr(alt(X0, Sx, q, g)[0])[0] for g in malla_pais(q)]
        com = []
        for g in pool_grid:
            if min((q > g).sum(), (q <= g).sum()) >= 10:
                com.append(np.linalg.qr(alt(X0, Sx, q, g)[0])[0])
            else:
                com.append(Q0)                                  # régimen inviable en el país: lineal
        datos[c] = (y, own, com, X0, Sx, q)

    def stats(Ys):
        so = 0.0; sc = np.zeros((len(pool_grid),) + Ys[next(iter(Ys))].shape[1:])
        for c, (y, own, com, *_r) in datos.items():
            Y = Ys[c]
            so = so + np.min(np.vstack([ssr_mat(Qg, Y) for Qg in own]), axis=0)
            sc = sc + np.vstack([ssr_mat(Qg, Y) for Qg in com])
        jc = np.argmin(sc, axis=0); smin = sc.min(axis=0)
        N = sum(len(v[0]) for v in datos.values())
        return (smin - so) / (so / N), jc
    F, jc = stats({c: v[0][:, None] for c, v in datos.items()})
    F = float(F[0]); g_til = pool_grid[int(jc[0])]
    rng = np.random.default_rng(seed); Ys = {}
    for c, (y, own, com, X0, Sx, q) in datos.items():
        if min((q > g_til).sum(), (q <= g_til).sum()) >= 10:
            X = alt(X0, Sx, q, g_til)[0]
        else:
            X = X0
        b = np.linalg.lstsq(X, y, rcond=None)[0]; fit = X @ b; e = y - fit
        Ys[c] = fit[:, None] + e[:, None] * rng.choice([-1.0, 1.0], size=(len(y), nb))
    Fb, _ = stats(Ys)
    num(f"{pref}_C2_F", F); num(f"{pref}_C2_p", float(np.mean(Fb >= F))); num(f"{pref}_C2_gamma_comun", g_til)


# ================================================================ potencia
def potencia(x, qcol, S, L, pref, reps=200, nb=199, seed=17):
    x = x.reset_index(drop=True)
    M = aniquilador(x); q = x[qcol].values.astype(float)
    x = x.assign(q_s=(q - q.mean()) / q.std())
    X0 = M @ x[S + L + qlin(qcol)].values.astype(float); Q0 = np.linalg.qr(X0)[0]
    y = M @ x["ln_EMBI"].values
    b0 = np.linalg.lstsq(X0, y, rcond=None)[0]; e0 = y - X0 @ b0
    grid = malla(q, x["country"].values)
    Qs = [np.linalg.qr(np.column_stack([X0, M @ np.column_stack([x[S].values * (q > g)[:, None], (q > g)])]))[0]
          for g in grid]
    n = len(y); g0 = np.median(q); H0 = (q > g0).astype(float)
    efecto = M @ (x[S].values * H0[:, None] @ b0[:len(S)])        # régimen alto: pendiente doble
    paises = x["country"].values; uniq = list(dict.fromkeys(paises)); wi = np.array([uniq.index(c) for c in paises])
    rng = np.random.default_rng(seed)
    def sup(Y):
        S0 = ssr_mat(Q0, Y); S1 = np.min(np.vstack([ssr_mat(Qg, Y) for Qg in Qs]), axis=0)
        return n * (S0 - S1) / S1
    rech = 0
    for _ in range(reps):
        ys = X0 @ b0 + efecto + M @ (e0 * rng.choice([-1.0, 1.0], size=len(uniq))[wi])
        LR = sup(ys[:, None])[0]
        bs = np.linalg.lstsq(X0, ys, rcond=None)[0]; f0 = X0 @ bs; es = ys - f0
        Yb = M @ (f0[:, None] + es[:, None] * rng.choice([-1.0, 1.0], size=(len(uniq), nb))[wi, :])
        rech += int(np.mean(sup(Yb) >= LR) < 0.05)
    num(f"{pref}_potencia", rech / reps)


def potencia_pais(piezas, qcol, S, L, extra, pref, reps=200, nb=199, seed=19):
    rng = np.random.default_rng(seed); tasas = []
    for c, xc in piezas.items():
        xs = xc.sort_values("_qn").reset_index(drop=True)
        q, X0 = disenio(xs, qcol, S, L, list(extra)); Sx = xs[S].values.astype(float); y = xs["y_net"].values
        grid = malla_pais(q)
        Q0 = np.linalg.qr(X0)[0]; Qs = [np.linalg.qr(alt(X0, Sx, q, g)[0])[0] for g in grid]
        b0 = np.linalg.lstsq(X0, y, rcond=None)[0]; e0 = y - X0 @ b0; n = len(y)
        H = (q > np.median(q)).astype(float); ef = (Sx * H[:, None]) @ b0[1 + len(qlin(qcol)):1 + len(qlin(qcol)) + len(S)]
        def sup(Y):
            S0 = ssr_mat(Q0, Y); S1 = np.min(np.vstack([ssr_mat(Qg, Y) for Qg in Qs]), axis=0)
            return n * (S0 - S1) / S1
        r = 0
        for _ in range(reps):
            ys = X0 @ b0 + ef + e0[rng.integers(0, n, n)]
            LR = sup(ys[:, None])[0]
            es = ys - X0 @ np.linalg.lstsq(X0, ys, rcond=None)[0]
            r += int(np.mean(sup(es[:, None] * rng.standard_normal((n, nb))) >= LR) < 0.05)
        tasas.append(r / reps); num(f"{pref}_potencia_{c}", r / reps)
    num(f"{pref}_potencia_pais_media", np.mean(tasas))


# ================================================================ figura
def figura(F):
    import matplotlib.pyplot as plt
    vs = [("U1", "Tensión financiera (FCI, percentil propio)"), ("U2", "Deuda/PIB (percentil propio)"),
          ("U3", "Riesgo de cola D (percentil propio)")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=False)
    for ax, (v, tit) in zip(axes, vs):
        G = F[F["variable"] == v].sort_values("pais")
        if G.empty:
            ax.set_visible(False); continue
        yy = np.arange(len(G))
        ax.hlines(yy, G["ci90_lo_pct"], G["ci90_hi_pct"], color=p13.BLUE, lw=3, alpha=.6)
        ax.plot(G["gamma_pct"], yy, "o", color=p13.BLUE)
        gp = NUM.get(f"{v}_pctvar_gamma")
        if gp is not None:
            ax.axvline(gp, color=p13.RED, ls="--", lw=1.5, label="agrupado")
        ax.set_yticks(yy); ax.set_yticklabels(G["pais"].map(ES))
        ax.set_xlim(0, 100); ax.set_xlabel("umbral, percentil propio del país"); ax.set_title(tit, fontsize=10)
        ax.grid(axis="x", color=p13.GRID)
    axes[0].legend(loc="lower right", fontsize=8)
    p13.save(fig, "fig_umbrales_pais")


# ================================================================ main
def main():
    d, raw = preparar()
    lam = lambdas(d)
    filas = []
    specs = [  # pref, q, S, L, primaria
        ("U1", "FCI_l1", ["J_c", "T_c"], ["JxT"]),
        ("U2", "debtq_l4", ["T_c"], ["J_c", "JxT"]),
        ("U3", "D_l1", ["J_c"], ["T_c"]),
    ]
    piezas_all = {}
    for pref, qcol, S, L in specs:
        print(f"== {pref} agrupado ({qcol})")
        x, u, r = bloque_agrupado(d, pref, qcol, S, L, loo=True)
        # variante en percentil propio, para C1 en percentiles
        xp = x.copy(); xp["qpct"] = xp.groupby("country")[qcol].rank(pct=True) * 100
        up = umbral_agrupado(xp, "qpct", S, L, boot=False)
        num(f"{pref}_pctvar_gamma", up["gamma"])
        print(f"== {pref} por país")
        fp, piezas = bloque_pais(d, lam, pref, qcol, S, L, u["gamma"], up["gamma"], c5=(pref == "U2"))
        filas += fp; piezas_all[pref] = piezas
        c2_comun(piezas, qcol, S, L, [], u["grid"], pref)
        fg, _ = bloque_pais(d, lam, pref + "glob", qcol, S, L, u["gamma"], up["gamma"], extra=GLOB, boot=False)
        filas += fg
        potencia(x, qcol, S, L, pref)
        potencia_pais(piezas, qcol, S, L, [], pref)
        pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p52_numeros.csv"))
    # secundarias agrupadas
    print("== secundarias")
    for pref, qcol, S, L in (("U1nr", "FCInr_l1", ["J_c", "T_c"], ["JxT"]),
                             ("U1pct", "FCIpct_l1", ["J_c", "T_c"], ["JxT"]),
                             ("U1exp", "FCIexp_l1", ["J_c", "T_c"], ["JxT"]),
                             ("U1ov", "FCIov_l1", ["J_c", "T_c"], ["JxT"]),
                             ("U2debt", "DEBT_l4", ["T_c"], ["J_c", "JxT"])):
        bloque_agrupado(d, pref, qcol, S, L)
    # U1 con la DD de Merton en lugar de JLoss y U2 con D4
    dd = d.dropna(subset=["FDD_l1"]).copy(); dd["ln_JLoss_l1"] = dd["FDD_l1"]
    bloque_agrupado(dd, "U1dd", "FCI_l1", ["J_c", "T_c"], ["JxT"])
    d4 = d.dropna(subset=["D4_l1"]).copy(); d4["D_l1"] = d4["D4_l1"]
    bloque_agrupado(d4, "U2d4", "debtq_l4", ["T_c"], ["J_c", "JxT"])
    F = pd.DataFrame(filas)
    F.to_csv(os.path.join(HERE, "umbrales_pais_bbg.csv"), index=False)
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p52_numeros.csv"))
    figura(F)
    for k, v in NUM.items():
        if "_sin_" not in k and "_alto_" not in k:
            print(f"  {k:34s} {v: .4f}")


if __name__ == "__main__":
    main()
