"""
jloss_engine.py — Motor JLoss reutilizable (pais-trimestre) para los extractores v8.

Consume los CSV que producen los extractores nuevos:
    balance_<pais>.csv : countryname, bankname, date, st_borrow, lt_borrow, total_liab [, DP]
    mktcap_<pais>.csv  : countryname, bankname, date, mktcap   (diario)

y entrega una MALLA TRIMESTRAL COMPLETA (sin trimestres omitidos silenciosamente:
los faltantes quedan como NaN explicito) mas un reporte de QA por pais.

Contiene:
  - Motor saddle-point validado contra MATLAB (<1e-6): copiado VERBATIM del
    notebook certificado v8. NO se modifico.
  - Solver Merton/KMV CORREGIDO: multi-arranque. El original usaba x0=[1,1]
    (igual que KMVOptsearch.m) pero, a diferencia de MATLAB, el port a Python
    verifica convergencia y descartaba como NaN todo lo no convergido. Con
    x0=[1,1] solo converge ~43% de los casos, y falla sistematicamente en los
    bancos MAS apalancados (E/D mediano 0.83 en las fallas vs 2.94 en los
    exitos) -> sesgo de seleccion justo en los bancos que mas contribuyen al
    riesgo sistemico. El multi-arranque (inicializacion KMV ingenua
    Va ~ E + D, sigma_A ~ sigma_E/v) sube la convergencia a ~83% y devuelve
    PD IDENTICAS donde el metodo original tambien converge (dif max 1.3e-9),
    por lo que no altera resultados validados: solo recupera los perdidos.

Uso:
    python jloss_engine.py --countries chile brazil peru mexico --indir . --out Panel_JLoss_v9.csv
    # o como libreria:
    from jloss_engine import build_country_jloss, build_panel
"""
import argparse
import glob
import os
import warnings

import numpy as np
import pandas as pd
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import brentq, fsolve
from scipy.stats import norm

# --------------------------------------------------------------------------
# Parametros del modelo (identicos a la corrida oficial de MATLAB)
# --------------------------------------------------------------------------
LGD = 0.45
LOSS_INF = 0.01
LOSS_SUP = 0.048
NUM_STEPS = 500
NUM_ORDER = 7
PERCENTILE = 0.99
R_FREE = 0.04
MERTON_T = 1.0
RHO_FLAT = 0.4          # rho oficial (rhos en jloss.mat es uniformemente 0.4)
MIN_RETURNS = 5         # retornos diarios minimos por trimestre para la vol realizada
MIN_BANKS = 3           # bancos minimos para considerar el JLoss "sistemico" (QA)
FFILL_LIMIT = 1         # trimestres maximos de arrastre del balance (evita datos rancios)


def ghi_py(n=NUM_ORDER):
    x, w = hermgauss(n)
    return np.column_stack([np.sqrt(2) * x, w / np.sqrt(np.pi)])


GH_ZZ = ghi_py()


# ==========================================================================
# Motor saddle-point — VERBATIM del notebook validado contra MATLAB (<1e-6).
# No modificar sin re-validar contra pd_indiv.mat.
# ==========================================================================
def cond_pd(pd_, rho, V):
    return float(norm.cdf((norm.ppf(np.clip(pd_, 1e-8, 1 - 1e-8)) - rho * V)
                          / np.sqrt(max(1 - rho ** 2, 1e-10))))


def K0(s, pc, a):
    t = 0.0
    for p, ai in zip(pc, a):
        sa = s * ai
        if sa > 500:
            t += sa + np.log(max(p, 1e-300))
        elif sa < -500:
            t += np.log(max(1 - p, 1e-300))
        else:
            t += np.log(1 - p + p * np.exp(sa))
    return t


def K1(s, pc, a):
    t = 0.0
    for p, ai in zip(pc, a):
        sa = s * ai
        if sa > 500:
            t += ai
        elif sa < -500:
            t += p * ai
        else:
            e = np.exp(sa)
            t += p * ai * e / (1 - p + p * e)
    return t


def K2(s, pc, a):
    t = 0.0
    for p, ai in zip(pc, a):
        sa = s * ai
        if abs(sa) > 500:
            continue
        e = np.exp(sa)
        d = 1 - p + p * e
        t += p * e * ai ** 2 / d - (p * e * ai / d) ** 2
    return t


def find_saddle(x, pc, a):
    try:
        lo = K1(-200, pc, a)
        hi = K1(200, pc, a)
        if x <= lo:
            return -200.0
        if x >= hi:
            return 200.0
        return brentq(lambda s: K1(s, pc, a) - x, -200, 200, xtol=1e-9, maxiter=200)
    except Exception:
        return np.nan


def get_prob_cdf(K0v, x, K2v, t):
    if K2v <= 0:
        return 0.5
    lam = abs(t) * np.sqrt(K2v)
    exp_ = K0v - t * x + 0.5 * t ** 2 * K2v
    if exp_ > 700:
        temp = 0.0
    elif exp_ < -700:
        temp = 1.0
    else:
        temp = np.exp(exp_) * norm.cdf(-lam)
    return float(np.clip(1.0 - temp if t > 0 else temp, 0.0, 1.0))


def loss_distrib_py(pds, rhos, a):
    N = len(pds)
    step = (LOSS_SUP - LOSS_INF) / NUM_STEPS
    xg = np.array([LOSS_INF + i * step for i in range(NUM_STEPS + 1)])
    pt = np.zeros(NUM_STEPS + 1)
    for k in range(len(GH_ZZ)):
        Vk, wk = GH_ZZ[k, 0], GH_ZZ[k, 1]
        pc = np.array([cond_pd(pds[j], rhos[j], Vk) for j in range(N)])
        for idx, x in enumerate(xg):
            t = find_saddle(x, pc, a)
            if np.isfinite(t):
                pt[idx] += wk * get_prob_cdf(K0(t, pc, a), x, K2(t, pc, a), t)
    return np.column_stack([xg, pt])


def find_var99(lp):
    xg = lp[:, 0]
    cd = np.maximum.accumulate(lp[:, 1])          # CDF monotona antes de interpolar
    if PERCENTILE <= cd[0]:
        return xg[0]
    if PERCENTILE >= cd[-1]:
        return xg[-1]
    idx = max(0, np.searchsorted(cd, PERCENTILE) - 1)
    d = cd[idx + 1] - cd[idx]
    if abs(d) < 1e-10:
        return xg[idx]
    return xg[idx] + (xg[idx + 1] - xg[idx]) / d * (PERCENTILE - cd[idx])


def loss_contrib_py(exs, pds, rhos, a, lp):
    N = len(pds)
    nt = 0.0
    ct = np.zeros(N)
    for k in range(len(GH_ZZ)):
        Vk, wk = GH_ZZ[k, 0], GH_ZZ[k, 1]
        pc = np.array([cond_pd(pds[j], rhos[j], Vk) for j in range(N)])
        t = find_saddle(lp, pc, a)
        if not np.isfinite(t):
            continue
        K0v = K0(t, pc, a)
        K1v = K1(t, pc, a)
        K2v = K2(t, pc, a)
        if K2v <= 0:
            continue
        ne = K0v - K1v * t
        if abs(ne) > 700:
            continue
        nc = wk * np.exp(ne) / np.sqrt(K2v)
        nt += nc
        for n in range(N):
            sa = t * a[n]
            if sa > 500:
                tp = 1.0
            elif sa < -500:
                tp = 0.0
            else:
                en = np.exp(sa)
                tp = pc[n] * en / (1 - pc[n] + pc[n] * en)
            ct[n] += nc * tp
    if abs(nt) < 1e-300:
        return np.zeros(N)
    return exs * ct / nt


def compute_jloss(pds, rhos, liabilities, lgd=LGD):
    pds = np.array(pds, float)
    rhos = np.array(rhos, float)
    liabilities = np.array(liabilities, float)
    v = (np.isfinite(pds) & np.isfinite(rhos) & np.isfinite(liabilities)
         & (liabilities > 0) & (pds > 0) & (pds < 1) & (rhos >= 0) & (rhos < 1))
    pds, rhos, liabilities = pds[v], rhos[v], liabilities[v]
    if len(pds) < 1:
        return np.nan
    exs = lgd * liabilities
    exs1 = exs * pds
    a = exs / exs.sum()
    EL = float(exs1.sum())
    lp = loss_distrib_py(pds, rhos, a)
    loss_perc = find_var99(lp)
    UL = float(np.real(loss_contrib_py(exs, pds, rhos, a, loss_perc).sum()))
    return float((EL + UL) * 100 / liabilities.sum())


# ==========================================================================
# Merton / KMV — solver CORREGIDO (multi-arranque)
# ==========================================================================
def _kmv_resid(x, EtoD, sigma_E, r=R_FREE, T=MERTON_T):
    """Sistema de KMVfun.m en variables normalizadas x=[Va/E, sigma_A]."""
    v, sa = x
    if v <= 1e-8 or sa <= 1e-8:
        return [1e6, 1e6]
    d1 = (np.log(v * EtoD) + (r + 0.5 * sa ** 2) * T) / (sa * np.sqrt(T))
    d2 = d1 - sa * np.sqrt(T)
    return [v * norm.cdf(d1) - np.exp(-r * T) * norm.cdf(d2) / EtoD - 1.0,
            norm.cdf(d1) * v * sa - sigma_E]


def merton_pd(E, sigma_E_q, D_star, r=R_FREE, T=MERTON_T, return_detail=False):
    """EDF de Merton/KMV con DD lineal (NO el d2 de Black-Scholes), como indivpds.m.

    sigma_E_q es la volatilidad TRIMESTRAL del equity; se anualiza con sqrt(4).
    Multi-arranque: parte de la aproximacion KMV ingenua (Va ~ E + D) y solo
    despues prueba el x0=[1,1] historico; devuelve el primero que converge con
    residuo <= 1e-3. Donde el metodo original converge, el resultado es identico.
    """
    fail = (np.nan, "input") if return_detail else np.nan
    if not (np.isfinite(E) and np.isfinite(sigma_E_q) and np.isfinite(D_star)):
        return fail
    if E <= 0 or sigma_E_q <= 0 or D_star <= 0:
        return fail
    sigma_E = sigma_E_q * np.sqrt(4.0)
    EtoD = E / D_star
    v0 = 1.0 + 1.0 / EtoD                      # Va ~ E + D  =>  v = Va/E = 1 + D/E
    starts = [[v0, sigma_E / v0],              # inicializacion KMV ingenua
              [1.0, 1.0],                      # x0 historico (KMVOptsearch.m)
              [v0, max(sigma_E, 0.05)],
              [max(v0, 1.5), 0.10]]
    for x0 in starts:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            x, _info, ier, _msg = fsolve(_kmv_resid, x0, args=(EtoD, sigma_E), full_output=True)
        v, sa = x
        if ier != 1 or v <= 0 or sa <= 0:
            continue
        if max(abs(np.array(_kmv_resid(x, EtoD, sigma_E)))) > 1e-3:
            continue
        Va = v * E
        DD = (Va - D_star) / (Va * sa)
        edf = float(norm.cdf(-DD))
        if 0.0 < edf < 1.0:
            return (edf, "ok") if return_detail else edf
    return (np.nan, "no_converge") if return_detail else np.nan


# ==========================================================================
# Construccion de insumos trimestrales
# ==========================================================================
def quarterly_inputs(balance, mktcap, min_returns=MIN_RETURNS, ffill_limit=FFILL_LIMIT):
    """Cruza balance y market cap a nivel banco-trimestre.

    Devuelve un DataFrame con sigma_E_q (vol realizada trimestral), mktcap_end,
    D_star (= ST + 0.5*LT) y total_liab (EAD).
    """
    mk = mktcap.copy()
    mk["date"] = pd.to_datetime(mk["date"])
    mk = mk.dropna(subset=["mktcap"])
    mk = mk[mk["mktcap"] > 0].sort_values(["bankname", "date"])
    if mk.empty:
        return pd.DataFrame()
    mk["ret"] = mk.groupby("bankname")["mktcap"].pct_change()
    mk["quarter"] = mk["date"].dt.to_period("Q")

    def _rvol(g):
        r = g["ret"].dropna()
        return float(np.sqrt((r ** 2).sum())) if len(r) >= min_returns else np.nan

    sig = (mk.groupby(["bankname", "countryname", "quarter"])
             .apply(_rvol, include_groups=False).reset_index(name="sigma_E_q"))
    mq = (mk.groupby(["bankname", "countryname", "quarter"])["mktcap"]
            .last().reset_index(name="mktcap_end"))

    bal = balance.copy()
    bal["date"] = pd.to_datetime(bal["date"])
    bal["quarter"] = bal["date"].dt.to_period("Q")
    if "DP" in bal.columns and bal["DP"].notna().any():
        bal["D_star"] = bal["DP"]
    else:
        bal["D_star"] = bal["st_borrow"] + 0.5 * bal["lt_borrow"]
    if "total_liab" not in bal.columns:
        bal["total_liab"] = bal["st_borrow"] + bal["lt_borrow"]

    balq = (bal.sort_values("date")
              .groupby(["bankname", "countryname", "quarter"])[["D_star", "total_liab"]]
              .last().reset_index())
    # malla completa banco x trimestre, con arrastre LIMITADO (no propaga datos rancios)
    if balq.empty:
        return pd.DataFrame()
    allq = pd.period_range(balq["quarter"].min(), balq["quarter"].max(), freq="Q")
    bks = balq[["bankname", "countryname"]].drop_duplicates()
    full = pd.DataFrame([(b, c, q) for b, c in bks.itertuples(index=False) for q in allq],
                        columns=["bankname", "countryname", "quarter"])
    balq = (full.merge(balq, on=["bankname", "countryname", "quarter"], how="left")
                .sort_values(["bankname", "quarter"]))
    balq[["D_star", "total_liab"]] = (balq.groupby(["bankname", "countryname"])
                                          [["D_star", "total_liab"]]
                                          .transform(lambda s: s.ffill(limit=ffill_limit)))
    balq = balq.dropna(subset=["D_star", "total_liab"])

    dm = (sig.merge(mq, on=["bankname", "countryname", "quarter"], how="inner")
             .merge(balq, on=["bankname", "countryname", "quarter"], how="left"))
    return dm


def build_country_jloss(balance, mktcap, rho=RHO_FLAT, min_banks=MIN_BANKS,
                        full_grid=True, verbose=True):
    """JLoss pais-trimestre en MALLA COMPLETA (trimestres sin dato -> NaN explicito)."""
    dm = quarterly_inputs(balance, mktcap)
    if dm.empty:
        return pd.DataFrame(), {"n_cells": 0, "pd_ok": 0, "conv_rate": np.nan}

    det = dm.apply(lambda r: merton_pd(r["mktcap_end"], r["sigma_E_q"], r["D_star"],
                                       return_detail=True), axis=1)
    dm["PD"] = [d[0] for d in det]
    dm["status"] = [d[1] for d in det]
    cand = dm[dm["sigma_E_q"].notna() & dm["D_star"].notna() & (dm["D_star"] > 0)
              & (dm["mktcap_end"] > 0)]
    conv = float(dm["PD"].notna().sum() / len(cand)) if len(cand) else np.nan

    rows = []
    for (country, quarter), g in dm.groupby(["countryname", "quarter"]):
        g = g[g["PD"].notna() & g["total_liab"].notna() & (g["total_liab"] > 0)]
        if len(g) < 1:
            continue
        jl = compute_jloss(g["PD"].values, np.full(len(g), rho), g["total_liab"].values)
        if jl is not None and np.isfinite(jl):
            rows.append({"countryname": country, "quarter": quarter, "JLoss": float(jl),
                         "n_banks": int(len(g)), "sys_liab": float(g["total_liab"].sum())})
    out = pd.DataFrame(rows)
    if out.empty:
        return out, {"n_cells": len(dm), "pd_ok": int(dm["PD"].notna().sum()), "conv_rate": conv}

    if full_grid:                                  # malla trimestral SIN huecos silenciosos
        frames = []
        for c, g in out.groupby("countryname"):
            idx = pd.period_range(g["quarter"].min(), g["quarter"].max(), freq="Q")
            gg = (g.set_index("quarter").reindex(idx)
                    .rename_axis("quarter").reset_index())
            gg["countryname"] = c
            frames.append(gg)
        out = pd.concat(frames, ignore_index=True)

    out["below_min_banks"] = out["n_banks"].notna() & (out["n_banks"] < min_banks)
    out["source"] = np.where(out["JLoss"].notna(), "merton", "missing")
    out = out.sort_values(["countryname", "quarter"]).reset_index(drop=True)
    qa = {"n_cells": len(dm), "pd_ok": int(dm["PD"].notna().sum()), "conv_rate": conv}
    if verbose:
        print(f"    celdas banco-trimestre={qa['n_cells']}  PD validas={qa['pd_ok']}  "
              f"convergencia={conv:.1%}" if np.isfinite(conv) else "    (sin candidatos)")
    return out, qa


def build_panel(countries, indir=".", rho=RHO_FLAT, min_banks=MIN_BANKS):
    """Recorre balance_<pais>.csv + mktcap_<pais>.csv y arma el panel completo."""
    frames, qas = [], []
    for c in countries:
        fb = os.path.join(indir, f"balance_{c}.csv")
        fm = os.path.join(indir, f"mktcap_{c}.csv")
        if not (os.path.exists(fb) and os.path.exists(fm)):
            print(f"  {c}: faltan archivos (balance/mktcap) -> omitido")
            continue
        print(f"  {c}:")
        bal = pd.read_csv(fb)
        mkt = pd.read_csv(fm)
        out, qa = build_country_jloss(bal, mkt, rho=rho, min_banks=min_banks)
        if out.empty:
            print(f"    sin JLoss calculable")
            continue
        frames.append(out)
        qa.update({"countryname": c})
        qas.append(qa)
    if not frames:
        return pd.DataFrame(), pd.DataFrame()
    panel = pd.concat(frames, ignore_index=True)
    panel["date"] = panel["quarter"].dt.to_timestamp()
    panel["quarter"] = panel["quarter"].astype(str)
    return panel, pd.DataFrame(qas)


def qa_report(panel):
    """Resumen de completitud por pais: trimestres con dato, huecos y bancos por trimestre."""
    rows = []
    for c, g in panel.groupby("countryname"):
        ok = g["JLoss"].notna()
        rows.append({
            "countryname": c,
            "q_total": len(g),
            "q_con_dato": int(ok.sum()),
            "cobertura": f"{ok.mean():.0%}",
            "primer": g.loc[ok, "quarter"].min() if ok.any() else None,
            "ultimo": g.loc[ok, "quarter"].max() if ok.any() else None,
            "n_banks_med": g.loc[ok, "n_banks"].median() if ok.any() else np.nan,
            "q_pocos_bancos": int(g["below_min_banks"].sum()),
        })
    return pd.DataFrame(rows).sort_values("cobertura")


def main():
    ap = argparse.ArgumentParser(description="Motor JLoss pais-trimestre (extractores v8).")
    ap.add_argument("--countries", nargs="+", default=None,
                    help="Paises a procesar. Por defecto: todos los balance_*.csv de --indir")
    ap.add_argument("--indir", default=".")
    ap.add_argument("--out", default="Panel_JLoss_v9.csv")
    ap.add_argument("--rho", type=float, default=RHO_FLAT)
    ap.add_argument("--min-banks", type=int, default=MIN_BANKS)
    a = ap.parse_args()

    countries = a.countries
    if not countries:
        countries = sorted(os.path.basename(f)[len("balance_"):-len(".csv")]
                           for f in glob.glob(os.path.join(a.indir, "balance_*.csv")))
    print(f"Procesando {len(countries)} paises: {', '.join(countries)}")
    panel, qas = build_panel(countries, indir=a.indir, rho=a.rho, min_banks=a.min_banks)
    if panel.empty:
        print("Panel vacio.")
        return
    panel.to_csv(os.path.join(a.indir, a.out), index=False)
    rep = qa_report(panel)
    rep.to_csv(os.path.join(a.indir, "qa_jloss.csv"), index=False)
    print(f"\nPanel: {len(panel)} filas ({panel['JLoss'].notna().sum()} con dato) -> {a.out}")
    print("\nQA de completitud:")
    print(rep.to_string(index=False))
    flag = rep[rep["q_pocos_bancos"] > 0]
    if len(flag):
        print(f"\nAVISO: {int(flag['q_pocos_bancos'].sum())} trimestres con menos de "
              f"{a.min_banks} bancos (JLoss poco representativo, revisar antes de usarlos).")


if __name__ == "__main__":
    main()
