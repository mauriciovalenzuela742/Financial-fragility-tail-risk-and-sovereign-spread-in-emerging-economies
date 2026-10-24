# -*- coding: utf-8 -*-
"""
p60_senal_dd.py -- Q1 del preregistro 7 (4_Redaccion/preregistro_quant.md, commit d968986): una señal
de valor relativo con la fragilidad bancaria mensual.

Cada mes se ordenan los países por el cambio de la distancia al incumplimiento del mes anterior
(z = DD_lag_{m-1} - DD_lag_{m-2}); largo en el tercio con mayor z, corto en el de menor z, igualmente
ponderados. Retorno de exceso aproximado r = -D*Ds/1e4 + s_{m-1}/(12*1e4), D = 7. Costos: la mitad de un
bid-ask de 15 pb (25 de sensibilidad) por la duración, por unidad de rotación en un sentido.

Q1-H1: Sharpe neto > 0 (Ledoit-Wolf 2008: bootstrap circular studentizado, bloques de 6, 4999 réplicas).

Sin anticipación: el balance con fecha en el mes t se usa desde t+3 (DD_lag, fragilidad_mensual_lag_bbg.csv).
También construye el panel mensual que usa p62 (panel_mensual).

Salida: bbg/paper_p60_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
from scipy.stats import norm

import p37_mensual_fechado as p37

SERIE_LAG = os.path.join(HERE, "fragilidad_mensual_lag_bbg.csv")
PANEL = os.path.join(HERE, "Panel_bloomberg_embiext.csv")
DUR = 7.0
COSTO = {15: 0.5 * 15 * DUR / 1e4, 25: 0.5 * 25 * DUR / 1e4}
INICIO = pd.Period("2015-01", freq="M")
SEMILLA = 20261023
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


# ================================================================ datos
def dd_mensual_lag(c):
    """p37.dd_mensual con el balance usado desde tres meses después de su fecha de cierre."""
    import jloss_engine as je
    mk = pd.read_csv(os.path.join(p37.BBG, c, f"mktcap_{c}.csv"), parse_dates=["date"])
    bal = pd.read_csv(os.path.join(p37.BBG, c, f"balance_{c}.csv"), parse_dates=["date"])
    mk = mk.dropna(subset=["mktcap"]); mk = mk[mk["mktcap"] > 0].sort_values(["bankname", "date"])
    mk["ret"] = mk.groupby("bankname")["mktcap"].pct_change()
    mk["month"] = mk["date"].dt.to_period("M")
    ss = mk.groupby(["bankname", "month"]).agg(r2=("ret", lambda r: float((r.dropna() ** 2).sum())),
                                               nr=("ret", lambda r: int(r.notna().sum())),
                                               E=("mktcap", "last")).reset_index()
    ss = ss.sort_values(["bankname", "month"])
    g = ss.groupby("bankname")
    ss["r2_3"] = g["r2"].transform(lambda s: s.rolling(3, min_periods=3).sum())
    ss["nr_3"] = g["nr"].transform(lambda s: s.rolling(3, min_periods=3).sum())
    ss["sigma_E_q"] = np.where(ss["nr_3"] >= je.MIN_RETURNS * 3, np.sqrt(ss["r2_3"]), np.nan)
    bal["D_star"] = bal["st_borrow"] + 0.5 * bal["lt_borrow"]
    bal["month"] = bal["date"].dt.to_period("M") + 3          # rezago de publicación preregistrado
    bm = bal.sort_values("date").groupby(["bankname", "month"])[["D_star", "total_liab"]].last().reset_index()
    x = ss.merge(bm, on=["bankname", "month"], how="left").sort_values(["bankname", "month"])
    x[["D_star", "total_liab"]] = x.groupby("bankname")[["D_star", "total_liab"]].transform(lambda s: s.ffill(limit=6))
    x = x.dropna(subset=["sigma_E_q", "D_star", "total_liab"])
    x = x[(x["total_liab"] > 0) & (x["D_star"] > 0)]
    x["PD"] = [je.merton_pd(e, s, dst) for e, s, dst in zip(x["E"], x["sigma_E_q"], x["D_star"])]
    x = x.dropna(subset=["PD"])
    x["DD"] = -norm.ppf(np.clip(x["PD"], 1e-8, 1 - 1e-8))
    out = x.groupby("month").apply(lambda h: pd.Series({
        "DD_lag": float((h["DD"] * h["total_liab"]).sum() / h["total_liab"].sum()), "n_bancos_lag": len(h)})).reset_index()
    out["country"] = c
    return out


def serie_lag():
    if os.path.exists(SERIE_LAG):
        s = pd.read_csv(SERIE_LAG); s["month"] = pd.PeriodIndex(s["month"], freq="M"); return s
    s = pd.concat([dd_mensual_lag(c) for c in p37.PAISES], ignore_index=True)
    s.to_csv(SERIE_LAG, index=False)
    return s


def panel_mensual():
    """country, month, s (pb, cierre), r (retorno de exceso aproximado), DD_lag, DD (p37), D_q2."""
    e = p37.embi_mensual()[["country", "month", "embi_cierre"]].rename(columns={"embi_cierre": "s"})
    e = e.sort_values(["country", "month"])
    prev = e.groupby("country")[["month", "s"]].shift(1)
    ok = (e["month"] - prev["month"]).apply(lambda d: getattr(d, "n", np.nan)) == 1
    e["s_l1"] = np.where(ok, prev["s"], np.nan)
    e["r"] = -DUR * (e["s"] - e["s_l1"]) / 1e4 + e["s_l1"] / (12 * 1e4)
    x = e.merge(serie_lag()[["country", "month", "DD_lag"]], on=["country", "month"], how="left")
    x = x.merge(p37.series()[["country", "month", "DD_w"]].rename(columns={"DD_w": "DD"}),
                on=["country", "month"], how="left")
    # riesgo de cola del trimestre q-2, con m dentro de q
    g = pd.read_csv(PANEL, usecols=["country", "quarter", "GaR_pp"]).dropna()
    g["q"] = pd.PeriodIndex(g["quarter"], freq="Q")
    g["D"] = -g["GaR_pp"]
    x["q2"] = x["month"].dt.asfreq("Q") - 2
    x = x.merge(g[["country", "q", "D"]].rename(columns={"q": "q2", "D": "D_q2"}), on=["country", "q2"], how="left")
    return x.sort_values(["country", "month"]).reset_index(drop=True)


def senal(x, col):
    """z_{i,m-1} = col_{m-1} - col_{m-2}, alineada en la fila del mes m."""
    x = x.sort_values(["country", "month"]).copy()
    g = x.groupby("country")
    l1, l2 = g[col].shift(1), g[col].shift(2)
    m1, m2 = g["month"].shift(1), g["month"].shift(2)
    cont = ((x["month"] - m1).apply(lambda d: getattr(d, "n", np.nan)) == 1) & \
           ((x["month"] - m2).apply(lambda d: getattr(d, "n", np.nan)) == 2)
    x["z"] = np.where(cont, l1 - l2, np.nan)
    return x


# ================================================================ cartera
def pesos(u, tipo):
    u = u.sort_values(["z", "country"], ascending=[False, True])
    n = len(u); w = pd.Series(0.0, index=u["country"].values)
    if tipo == "tercil":
        k = n // 3
        w.iloc[:k] = 1.0 / k; w.iloc[-k:] = -1.0 / k
    else:                                            # rango centrado, suma 0, suma |w| = 2
        rk = u["z"].rank(method="first").values - (n + 1) / 2
        w[:] = rk / np.abs(rk).sum() * 2
    return w


def cartera(x, costo, tipo="tercil", excluir=(), horizonte=1, desde=INICIO, hasta=None):
    x = x[~x["country"].isin(excluir)]
    meses = sorted(m for m in x["month"].unique() if m >= desde and (hasta is None or m <= hasta))
    por_mes = {m: g for m, g in x.groupby("month")}
    w_prev = pd.Series(dtype=float); out = []
    hist = {}                                        # pesos formados con la señal de cada mes
    for m in meses:
        g = por_mes[m]
        u = g.dropna(subset=["r", "z"])
        hist[m] = pesos(u, tipo) if len(u) >= 6 else None
        if horizonte == 1:
            w = hist[m]
        else:                                        # carteras superpuestas formadas en m, m-1, m-2
            ws = [hist.get(m - j) for j in range(horizonte)]
            ws = [v for v in ws if v is not None]
            disp = set(g.dropna(subset=["r"])["country"])
            w = None if not ws else (pd.concat(ws, axis=1).fillna(0).sum(axis=1) / horizonte)
            if w is not None:
                w = w[w.index.isin(disp)]
                if len(w) == 0 or (w.abs().sum() == 0):
                    w = None
        if w is None:
            out.append((m, 0.0, 0.0, 0.0)); w_prev = pd.Series(dtype=float); continue
        rr = g.set_index("country")["r"].reindex(w.index)
        bruto = float((w * rr).sum())
        idx = w.index.union(w_prev.index)
        rot = float((w.reindex(idx).fillna(0) - w_prev.reindex(idx).fillna(0)).abs().sum())
        out.append((m, bruto - costo * rot, bruto, rot))
        w_prev = w
    return pd.DataFrame(out, columns=["month", "R", "R_bruto", "rotacion"])


# ================================================================ inferencia del Sharpe
def _nw(z, L=6):
    z = z - z.mean(0); T = len(z); S = z.T @ z / T
    for l in range(1, L + 1):
        G = z[l:].T @ z[:-l] / T; S += (1 - l / (L + 1)) * (G + G.T)
    return S


def sharpe_se(r):
    r = np.asarray(r, float); T = len(r)
    m1, m2 = r.mean(), (r ** 2).mean(); s = np.sqrt(m2 - m1 ** 2)
    sr = m1 / s
    gr = np.array([m2 / s ** 3, -m1 / (2 * s ** 3)])
    V = gr @ _nw(np.column_stack([r, r ** 2])) @ gr / T
    return sr, np.sqrt(max(V, 1e-16))


def ledoit_wolf(r, b=6, nrep=4999, seed=SEMILLA):
    """H0: SR <= 0. Bootstrap circular por bloques, studentizado (Ledoit y Wolf, 2008)."""
    r = np.asarray(r, float); T = len(r)
    sr, se = sharpe_se(r)
    rng = np.random.default_rng(seed); tb = []
    nb = int(np.ceil(T / b))
    for _ in range(nrep):
        st = rng.integers(0, T, nb)
        idx = ((st[:, None] + np.arange(b)[None, :]) % T).ravel()[:T]
        srb, seb = sharpe_se(r[idx])
        tb.append((srb - sr) / seb)
    tb = np.array(tb)
    p = float((tb >= sr / se).mean())
    lo, hi = sr - np.quantile(tb, 0.95) * se, sr - np.quantile(tb, 0.05) * se
    a = np.sqrt(12)
    return dict(sr=sr * a, se=se * a, p=p, lo=lo * a, hi=hi * a, T=T)


def nw_media(y, X=None, L=6):
    """coeficientes y t de Newey-West (L rezagos) de y sobre [1, X]."""
    y = np.asarray(y, float)
    Z = np.ones((len(y), 1)) if X is None else np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]; e = y - Z @ b
    Q = np.linalg.inv(Z.T @ Z / len(y))
    V = Q @ _nw(Z * e[:, None], L) @ Q / len(y)
    return b, b / np.sqrt(np.diag(V))


# ================================================================ main
def reportar(pref, res):
    st = ledoit_wolf(res["R"].values)
    for k in ("sr", "se", "p", "lo", "hi", "T"):
        num(f"{pref}_{k}", st[k])
    num(f"{pref}_media_anual", res["R"].mean() * 12)
    num(f"{pref}_vol_anual", res["R"].std() * np.sqrt(12))
    num(f"{pref}_rotacion_media", res["rotacion"].mean())
    print(f"  {pref:<24} SR {st['sr']:+.2f} [{st['lo']:+.2f}; {st['hi']:+.2f}] p={st['p']:.3f} "
          f"media {res['R'].mean()*1200:+.2f}%/año T={st['T']}")
    return st


def main():
    print("p60: Q1, señal de valor relativo con la fragilidad bancaria")
    x = panel_mensual()
    xl = senal(x, "DD_lag")
    num("n_paises_mes_medio", xl[xl["month"] >= INICIO].dropna(subset=["r", "z"]).groupby("month").size().mean())

    prim = cartera(xl, COSTO[15])
    st = reportar("q1h1", prim)
    reportar("bruto", prim.assign(R=prim["R_bruto"]))
    reportar("neto25", cartera(xl, COSTO[25]))
    reportar("sin_turquia", cartera(xl, COSTO[15], excluir=("turkey",)))
    reportar("rango", cartera(xl, COSTO[15], tipo="rango"))
    reportar("h3", cartera(xl, COSTO[15], horizonte=3))
    reportar("dd_p37", cartera(senal(x, "DD"), COSTO[15]))
    reportar("sub_2015_2019", cartera(xl, COSTO[15], hasta=pd.Period("2019-12", freq="M")))
    reportar("sub_2020", cartera(xl, COSTO[15], desde=pd.Period("2020-01", freq="M")))

    # alfa frente al retorno equiponderado del universo
    ew = xl[xl["month"] >= INICIO].dropna(subset=["r"]).groupby("month")["r"].mean()
    a = prim.set_index("month").join(ew.rename("ew"), how="inner")
    b, t = nw_media(a["R"].values, a["ew"].values)
    num("alfa_anual", b[0] * 12); num("alfa_t", t[0]); num("beta_ew", b[1]); num("beta_t", t[1])
    print(f"  alfa {b[0]*1200:+.2f}%/año (t {t[0]:.2f}); beta {b[1]:+.2f} (t {t[1]:.2f})")

    # Fama-MacBeth
    pend = []
    for m, g in xl[xl["month"] >= INICIO].dropna(subset=["r", "z"]).groupby("month"):
        if len(g) >= 6:
            pend.append(np.polyfit(g["z"].values, g["r"].values, 1)[0])
    b, t = nw_media(np.array(pend))
    num("fm_pendiente", b[0]); num("fm_t", t[0]); num("fm_meses", len(pend))
    print(f"  Fama-MacBeth pendiente {b[0]:+.4f} (t NW {t[0]:.2f}, {len(pend)} meses)")

    num("q1h1_turquia_ok", float(NUM["sin_turquia_sr"] > 0))
    out = os.path.join(HERE, "paper_p60_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
