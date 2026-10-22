# -*- coding: utf-8 -*-
"""
p43_revision_econometrica.py -- revisión econométrica en busca de otros resultados (no preespecificada;
se corren exactamente estas cuatro pruebas y se reportan todas):

  E1. Factores comunes con cargas heterogéneas: CCE de Pesaran (2006). Los efectos fijos de tiempo
      suponen que un choque global mueve a todas las economías por igual; el CCE agrega los promedios
      transversales de cada trimestre (del spread y de los regresores) con una carga propia de cada
      país. CCEP: agrupado, con EF de país y los promedios interactuados con indicadoras de país
      (errores agrupados por país y wild bootstrap). CCE-MG: una regresión por país (economías con al
      menos 24 trimestres) y la media de los coeficientes, con el error estándar no paramétrico.
  E2. ¿Nivel o transitoria? ARDL(1,1,1) de grupo de medias agrupado (PMG, Pesaran, Shin y Smith, 1999):
      d ln EMBI_it = phi_i (ln EMBI_{i,t-1} - th1 ln JLoss_{i,t-1} - th2 D_{i,t-1}) + dinámica propia de
      cada país; th común (largo plazo), phi_i y la dinámica, por país. Variables sin la media
      transversal de cada trimestre (el análogo de los EF de tiempo en PSS). Estimación por máxima
      verosimilitud concentrada; errores por bootstrap de bloques de país (199). Se compara con el MG
      (th por país, promediado) y se reporta la prueba de Hausman.
  E3. Pendientes por país con agrupación parcial: modelo de efectos aleatorios en los coeficientes
      (DerSimonian-Laird) sobre las pendientes país por país de la regresión principal sin interacción
      (variables sin la media transversal de cada trimestre). Media de efectos aleatorios, tau, I2,
      pendientes encogidas (Bayes empírico) y la media sin Turquía.
  E4. VAR de panel mensual de (d(-DD_w), d ln EMBI), tres rezagos, EF de país y sin la media
      transversal de cada mes (p37). Impulso-respuesta acumulada del spread a un choque de fragilidad
      (Cholesky, fragilidad primero y, como robustez, segundo) y descomposición de la varianza del
      error de pronóstico a 12 meses; IC por bootstrap de bloques de país (199).

Salida: bbg/paper_p43_numeros.csv. Reutiliza p13, p14, p32, p37.
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
from scipy import stats, optimize
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p37_mensual_fechado as p37

NUM = p32.NUM
B = 199


def num(k, v):
    NUM[k] = float(v)


def base():
    d, raw = p14.base()
    p14.check_principal(d)
    d = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    d["J_c"] = d["ln_JLoss_l1"] - d["ln_JLoss_l1"].mean()
    d["T_c"] = d["D_l1"] - d["D_l1"].mean()
    d["JxT"] = d["J_c"] * d["T_c"]
    return d, raw


# ================================================================ E1. CCE
def e1(d):
    regs = ["J_c", "T_c", "JxT"]
    x = d.copy()
    csa = []
    for v in ["ln_EMBI"] + regs:
        x[f"m_{v}"] = x.groupby("quarter")[v].transform("mean"); csa.append(f"m_{v}")
    inter = []
    for c in sorted(x["country"].unique()):
        for v in csa:
            col = f"{v}__{c}"; x[col] = np.where(x["country"] == c, x[v], 0.0); inter.append(col)
    m = PanelOLS(x.set_index(["country", "t"])["ln_EMBI"], x.set_index(["country", "t"])[regs + inter],
                 entity_effects=True, check_rank=False).fit(cov_type="clustered", cluster_entity=True)
    for v in regs:
        num(f"e1_ccep_{v}", m.params[v]); num(f"e1_ccep_{v}_p_pais", m.pvalues[v])
    # wild: los promedios interactuados entran como regresores (EF de país por demean2 con 'quarter' constante)
    x["_const_q"] = "0"
    for v in regs:
        P = p32.wb_prep(x.assign(quarter=x["_const_q"]), "ln_EMBI", regs + inter)
        num(f"e1_ccep_{v}_p_wild", p32.wb_run(P, [v])[0])
    num("e1_ccep_N", m.nobs)
    # sin cada país: coeficiente del riesgo de cola y p agrupado por país (CCEP)
    bs, ps = [], []
    for c in sorted(x["country"].unique()):
        xc = x[x["country"] != c]
        cols = regs + [k for k in inter if not k.endswith("__" + c)]
        mc = PanelOLS(xc.set_index(["country", "t"])["ln_EMBI"], xc.set_index(["country", "t"])[cols],
                      entity_effects=True, check_rank=False).fit(cov_type="clustered", cluster_entity=True)
        bs.append(float(mc.params["T_c"])); ps.append(float(mc.pvalues["T_c"]))
        num(f"e1_ccep_T_c_sin_{c}", bs[-1]); num(f"e1_ccep_T_c_sin_{c}_p", ps[-1])
    num("e1_ccep_T_c_loo_min", min(bs)); num("e1_ccep_T_c_loo_max", max(bs))
    num("e1_ccep_T_c_loo_p_max", max(ps)); num("e1_ccep_T_c_loo_n_sig05", sum(p < 0.05 for p in ps))
    # CCE-MG
    filas = []
    for c, g in x.groupby("country"):
        if len(g) < 24:
            continue
        X = np.column_stack([np.ones(len(g)), g[regs].values, g[csa].values])
        b = np.linalg.lstsq(X, g["ln_EMBI"].values, rcond=None)[0]
        filas.append(b[1:4])
    F = np.array(filas)
    num("e1_ccemg_n_paises", len(F))
    for j, v in enumerate(regs):
        mu = F[:, j].mean(); se = F[:, j].std(ddof=1) / np.sqrt(len(F))
        num(f"e1_ccemg_{v}", mu); num(f"e1_ccemg_{v}_p", 2 * stats.t.sf(abs(mu / se), len(F) - 1))
        num(f"e1_ccemg_{v}_n_pos", int((F[:, j] > 0).sum()))
    print("  E1 listo", flush=True)


# ================================================================ E2. PMG
def panel_ardl(d, raw):
    r = raw.copy()
    r = r.sort_values(["country", "_qn"]); g = r.groupby("country")
    ok = (r["_qn"] - g["_qn"].shift(1)) == 1
    r["y"] = r["ln_EMBI"]; r["J"] = g["ln_JLoss"].shift(1).where(ok); r["D"] = g["D_pp"].shift(1).where(ok)
    for v in ("y", "J", "D"):                                   # sin la media transversal de cada trimestre
        r[v] = r[v] - r.groupby("_qn")[v].transform("mean")
    g = r.groupby("country")
    ok = (r["_qn"] - g["_qn"].shift(1)) == 1
    r["dy"] = g["y"].diff().where(ok); r["dJ"] = g["J"].diff().where(ok); r["dD"] = g["D"].diff().where(ok)
    r["y1"] = g["y"].shift(1).where(ok); r["J1"] = g["J"].shift(1).where(ok); r["D1"] = g["D"].shift(1).where(ok)
    keys = set(zip(d["country"], d["quarter"]))
    r = r[[k in keys for k in zip(r["country"], r["quarter"])]]
    return r.dropna(subset=["dy", "dJ", "dD", "y1", "J1", "D1"])


def pmg_fit(r):
    grupos = [g for _, g in r.groupby("country") if len(g) >= 12]

    def negll(th):
        ll = 0.0
        for g in grupos:
            ec = g["y1"] - th[0] * g["J1"] - th[1] * g["D1"]
            X = np.column_stack([ec, g["dJ"], g["dD"], np.ones(len(g))])
            e = g["dy"].values - X @ np.linalg.lstsq(X, g["dy"].values, rcond=None)[0]
            ll += -0.5 * len(g) * np.log(e @ e / len(g))
        return -ll
    res = optimize.minimize(negll, x0=np.array([0.1, 0.03]), method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
    th = res.x
    phis, mg = [], []
    for g in grupos:
        ec = g["y1"] - th[0] * g["J1"] - th[1] * g["D1"]
        X = np.column_stack([ec, g["dJ"], g["dD"], np.ones(len(g))])
        phis.append(np.linalg.lstsq(X, g["dy"].values, rcond=None)[0][0])
        X2 = np.column_stack([g["y1"], g["J1"], g["D1"], g["dJ"], g["dD"], np.ones(len(g))])
        b = np.linalg.lstsq(X2, g["dy"].values, rcond=None)[0]
        mg.append([-b[1] / b[0], -b[2] / b[0]] if b[0] < 0 else [np.nan, np.nan])
    return th, np.array(phis), np.array(mg), len(grupos)


def e2(d, raw):
    r = panel_ardl(d, raw)
    th, phis, mg, n = pmg_fit(r)
    num("e2_N", len(r)); num("e2_paises", n)
    num("e2_pmg_th_J", th[0]); num("e2_pmg_th_D", th[1]); num("e2_phi_medio", phis.mean())
    num("e2_phi_n_neg", int((phis < 0).sum()))
    mgm = np.nanmedian(mg, axis=0)
    num("e2_mg_th_J_mediana", mgm[0]); num("e2_mg_th_D_mediana", mgm[1])
    rng = np.random.default_rng(43); paises = r["country"].unique(); reps = []
    for _ in range(B):
        pick = rng.choice(paises, size=len(paises), replace=True)
        rb = pd.concat([r[r["country"] == c].assign(country=f"{c}_{k}") for k, c in enumerate(pick)], ignore_index=True)
        try:
            reps.append(pmg_fit(rb)[0])
        except Exception:
            pass
    reps = np.array(reps)
    for j, v in enumerate(("J", "D")):
        se = reps[:, j].std(ddof=1)
        num(f"e2_pmg_th_{v}_se", se); num(f"e2_pmg_th_{v}_p", 2 * stats.norm.sf(abs(th[j] / se)))
        num(f"e2_pmg_th_{v}_lo", np.quantile(reps[:, j], 0.025)); num(f"e2_pmg_th_{v}_hi", np.quantile(reps[:, j], 0.975))
    print("  E2 listo", flush=True)


# ================================================================ E3. pendientes con agrupación parcial
def e3(d):
    x = d.copy()
    for v in ("ln_EMBI", "J_c", "T_c"):
        x[v + "_dm"] = x[v] - x.groupby("quarter")[v].transform("mean")
    filas = []
    for c, g in x.groupby("country"):
        X = np.column_stack([np.ones(len(g)), g["J_c_dm"], g["T_c_dm"]])
        y = g["ln_EMBI_dm"].values
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        e = y - X @ b; s2 = e @ e / max(len(g) - 3, 1)
        V = s2 * np.linalg.inv(X.T @ X)
        filas.append((c, b[1], np.sqrt(V[1, 1]), b[2], np.sqrt(V[2, 2])))
    F = pd.DataFrame(filas, columns=["country", "bJ", "sJ", "bD", "sD"])

    def dl(b, s):
        w = 1 / s ** 2; mu_f = (w * b).sum() / w.sum()
        Q = (w * (b - mu_f) ** 2).sum(); k = len(b)
        tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
        wr = 1 / (s ** 2 + tau2); mu = (wr * b).sum() / wr.sum(); se = np.sqrt(1 / wr.sum())
        I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
        shr = tau2 / (tau2 + s ** 2) * b + s ** 2 / (tau2 + s ** 2) * mu
        return mu, se, np.sqrt(tau2), I2, shr
    for v in ("J", "D"):
        mu, se, tau, I2, shr = dl(F["b" + v].values, F["s" + v].values)
        num(f"e3_{v}_mu", mu); num(f"e3_{v}_p", 2 * stats.norm.sf(abs(mu / se))); num(f"e3_{v}_tau", tau); num(f"e3_{v}_I2", I2)
        for c, b0, b1 in zip(F["country"], F["b" + v], shr):
            num(f"e3_{v}_{c}_bruto", b0); num(f"e3_{v}_{c}_encogido", b1)
        m2 = F["country"] != "turkey"
        mu2, se2, *_ = dl(F.loc[m2, "b" + v].values, F.loc[m2, "s" + v].values)
        num(f"e3_{v}_mu_sin_turquia", mu2); num(f"e3_{v}_p_sin_turquia", 2 * stats.norm.sf(abs(mu2 / se2)))
        m3 = F["country"] != "poland"
        mu3, se3, *_ = dl(F.loc[m3, "b" + v].values, F.loc[m3, "s" + v].values)
        num(f"e3_{v}_mu_sin_polonia", mu3); num(f"e3_{v}_p_sin_polonia", 2 * stats.norm.sf(abs(mu3 / se3)))
    print("  E3 listo", flush=True)


# ================================================================ E4. VAR de panel mensual
def var_datos():
    s = p37.series(); e = p37.embi_mensual()
    x = s.merge(e, on=["country", "month"], how="inner").sort_values(["country", "month"])
    x["F"] = -x["DD_w"]; x["y"] = np.log(x["embi_cierre"])
    g = x.groupby("country")
    ok = (x["month"] - g["month"].shift(1)).apply(lambda v: getattr(v, "n", np.nan)) == 1
    x["dF"] = g["F"].diff().where(ok); x["dy"] = g["y"].diff().where(ok)
    for v in ("dF", "dy"):
        x[v] = x[v] - x.groupby("month")[v].transform("mean")          # sin la media transversal del mes
    g = x.groupby("country")
    for k in (1, 2, 3):
        x[f"dF_l{k}"] = g["dF"].shift(k); x[f"dy_l{k}"] = g["dy"].shift(k)
    return x.dropna(subset=["dF", "dy"] + [f"{v}_l{k}" for v in ("dF", "dy") for k in (1, 2, 3)])


def var_fit(x, orden=("dF", "dy"), H=12):
    lags = [f"{v}_l{k}" for k in (1, 2, 3) for v in ("dF", "dy")]
    W = x.copy()
    for c in ["dF", "dy"] + lags:                                    # EF de país
        W[c] = W[c] - W.groupby("country")[c].transform("mean")
    X = W[lags].values
    A = np.linalg.lstsq(X, W[["dF", "dy"]].values, rcond=None)[0]   # (6 x 2)
    U = W[["dF", "dy"]].values - X @ A
    S = np.cov(U.T)
    idx = [("dF", "dy").index(v) for v in orden]
    P = np.linalg.cholesky(S[np.ix_(idx, idx)])
    Pfull = np.zeros((2, 2)); Pfull[np.ix_(idx, idx)] = P              # columnas en el orden dado
    As = [A[2 * k:2 * k + 2, :].T for k in range(3)]                  # A_k: (2 x 2)
    Ph = [np.eye(2)]
    for h in range(1, H + 1):
        Ph.append(sum(As[k] @ Ph[h - k - 1] for k in range(3) if h - k - 1 >= 0))
    shock_F = 0                                                       # Pfull tiene las columnas en el orden original (dF, dy)
    irf = np.array([(Ph[h] @ Pfull)[:, shock_F] for h in range(H + 1)])   # respuesta de (dF, dy)
    cum_y = irf[:, 1].cumsum()
    mse = sum((Ph[h] @ Pfull) ** 2 for h in range(H))
    fevd_y_F = mse[1, shock_F] / mse[1, :].sum()
    return cum_y, fevd_y_F, np.sqrt(S[0, 0])


def e4():
    x = var_datos()
    num("e4_N", len(x))
    for orden, lab in ((("dF", "dy"), "Fprimero"), (("dy", "dF"), "Fsegundo")):
        cum, fevd, sdF = var_fit(x, orden)
        rng = np.random.default_rng(44); paises = x["country"].unique(); rc, rf = [], []
        for _ in range(B):
            pick = rng.choice(paises, size=len(paises), replace=True)
            xb = pd.concat([x[x["country"] == c].assign(country=f"{c}_{k}") for k, c in enumerate(pick)], ignore_index=True)
            a, b, _ = var_fit(xb, orden); rc.append(a); rf.append(b)
        rc = np.array(rc); rf = np.array(rf)
        for h in (0, 1, 3, 6, 12):
            num(f"e4_{lab}_cum_h{h}", cum[h] * 100)
            num(f"e4_{lab}_cum_h{h}_lo", np.quantile(rc[:, h], 0.025) * 100); num(f"e4_{lab}_cum_h{h}_hi", np.quantile(rc[:, h], 0.975) * 100)
        num(f"e4_{lab}_fevd12", fevd * 100)
        num(f"e4_{lab}_fevd12_lo", np.quantile(rf, 0.025) * 100); num(f"e4_{lab}_fevd12_hi", np.quantile(rf, 0.975) * 100)
    print("  E4 listo", flush=True)


def main():
    d, raw = base()
    out = os.path.join(HERE, "paper_p43_numeros.csv")
    guardar = lambda: pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    e1(d); guardar()
    e3(d); guardar()
    e4(); guardar()
    e2(d, raw); guardar()
    for k, v in NUM.items():
        if "_bruto" not in k and "_encogido" not in k:
            print(f"  {k:30s} {v: .4f}")
    for c in ("turkey", "poland", "brazil", "india"):
        print(c, round(NUM.get(f"e3_J_{c}_bruto", np.nan), 3), "->", round(NUM.get(f"e3_J_{c}_encogido", np.nan), 3))
    print("->", out)


if __name__ == "__main__":
    main()
