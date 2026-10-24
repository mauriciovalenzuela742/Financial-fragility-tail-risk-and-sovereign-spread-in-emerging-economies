# -*- coding: utf-8 -*-
"""
p61_valor_razonable.py -- Q2 del preregistro 8 (4_Redaccion/preregistro_quant2.md, commit fc920b3): un
valor razonable del spread con los fundamentos de la tesis y la reversión de su residuo.

Cada mes m (desde 2015-01) se estima, con datos hasta m,
    ln s = a_i + l_t + b1 ln JLoss_{q-2} + b2 D_{q-2} + b3 deuda_{q-4} + e     (EF de país y de mes)
y se pronostica d ln s_{m+1} = kappa_m * e_{i,m}, con kappa de la regresión agrupada de d ln s_{t+1} sobre
e_t para t <= m-1. Q2-H1: Clark-West frente al cambio cero (unilateral, NW 6 sobre el promedio mensual).

También construye los fundamentos mensuales que usan p63 y p65 (fundamentos()).
Salida: bbg/paper_p61_numeros.csv.
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
from scipy.stats import norm

import p60_senal_dd as p60
from causal_core import demean2

RESIL = os.path.join(HERE, "resiliencia_trimestral_bbg.csv")
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def fundamentos():
    """panel mensual de p60 + ln JLoss_{q-2} y deuda_{q-4}."""
    x = p60.panel_mensual()
    q = x["month"].dt.asfreq("Q")
    j = pd.read_csv(p60.PANEL, usecols=["country", "quarter", "JLoss"]).dropna()
    j["qq"] = pd.PeriodIndex(j["quarter"], freq="Q"); j["lnJ"] = np.log(j["JLoss"].where(j["JLoss"] > 0))
    x["qq"] = q - 2
    x = x.merge(j[["country", "qq", "lnJ"]].rename(columns={"lnJ": "lnJ_q2"}), on=["country", "qq"], how="left")
    dbt = pd.read_csv(RESIL, usecols=["country", "quarter", "debt_q"]).dropna()
    dbt["qq"] = pd.PeriodIndex(dbt["quarter"], freq="Q")
    x["qq"] = q - 4
    x = x.merge(dbt[["country", "qq", "debt_q"]].rename(columns={"debt_q": "debt_q4"}), on=["country", "qq"], how="left")
    x["ln_s"] = np.log(x["s"])
    x["quarter"] = x["month"].astype(str)          # demean2 usa la columna 'quarter' como tiempo
    return x.drop(columns="qq").sort_values(["country", "month"]).reset_index(drop=True)


def adelanto(x, col, h):
    """col en m+h, alineado en m, solo si los meses son consecutivos."""
    g = x.groupby("country")
    v, mm = g[col].shift(-h), g["month"].shift(-h)
    ok = (mm - x["month"]).apply(lambda d: getattr(d, "n", np.nan)) == h
    return np.where(ok, v, np.nan)


def residuos(x, regs, hasta):
    d = x[(x["month"] <= hasta)].dropna(subset=["ln_s"] + regs).copy()
    Y = demean2(d, ["ln_s"], iters=40)["ln_s"].values
    X = demean2(d, regs, iters=40).values
    b = np.linalg.lstsq(X, Y, rcond=None)[0]
    return pd.Series(Y - X @ b, index=d.index), b


def clark_west(x, regs, h=1, excluir=()):
    x = x[~x["country"].isin(excluir)].copy()
    x["fut"] = adelanto(x, "ln_s", h) - x["ln_s"]
    meses = sorted(m for m in x["month"].unique() if m >= p60.INICIO)
    filas = []
    for m in meses:
        e, _ = residuos(x, regs, m)
        d = x.loc[e.index].assign(e=e.values)
        # kappa con los resultados ya observados: t + h <= m
        tr = d[(d["month"] <= m - h)].dropna(subset=["fut"])
        if len(tr) < 50:
            continue
        kappa = float((tr["e"] * tr["fut"]).sum() / (tr["e"] ** 2).sum())
        te = d[(d["month"] == m)].dropna(subset=["fut"])
        for _, r in te.iterrows():
            f = kappa * r["e"]; y = r["fut"]
            filas.append((m, r["country"], y, f, y ** 2 - ((y - f) ** 2 - f ** 2), kappa))
    f = pd.DataFrame(filas, columns=["month", "country", "y", "f", "cw", "kappa"])
    cw = f.groupby("month")["cw"].mean()
    b, t = p60.nw_media(cw.values)
    return dict(t=float(t[0]), p=float(norm.sf(t[0])), n=len(f), meses=len(cw),
                kappa=float(f["kappa"].iloc[-1]), r2oos=float(1 - ((f["y"] - f["f"]) ** 2).sum() / (f["y"] ** 2).sum()))


def vida_media(x, regs):
    e, _ = residuos(x, regs, x["month"].max())
    d = x.loc[e.index].assign(e=e.values).sort_values(["country", "month"])
    vm = []
    for c, g in d.groupby("country"):
        l1 = g["e"].shift(1); ok = (g["month"] - g["month"].shift(1)).apply(lambda z: getattr(z, "n", np.nan)) == 1
        a, b = g["e"][ok].values, l1[ok].values
        if len(a) > 24:
            rho = float((a * b).sum() / (b ** 2).sum())
            if 0 < rho < 1:
                vm.append(np.log(0.5) / np.log(rho))
    return float(np.median(vm)), len(vm)


def cartera_desde(x, zcol):
    """z alineada en el mes siguiente para p60.cartera."""
    x = x.sort_values(["country", "month"]).copy()
    g = x.groupby("country")
    prev, mm = g[zcol].shift(1), g["month"].shift(1)
    ok = (x["month"] - mm).apply(lambda d: getattr(d, "n", np.nan)) == 1
    x["z"] = np.where(ok, prev, np.nan)
    return p60.cartera(x, p60.COSTO[15])


def main():
    print("p61: Q2, valor razonable y reversión del residuo")
    x = fundamentos()
    R3 = ["lnJ_q2", "D_q2", "debt_q4"]
    r = clark_west(x, R3)
    for k, v in r.items():
        num(f"q2h1_{k}", v)
    print(f"  Q2-H1 Clark-West t={r['t']:.2f} p={r['p']:.3f} (N={r['n']}, {r['meses']} meses; kappa final {r['kappa']:+.3f}; R2 OOS {r['r2oos']:+.4f})")
    vm, nv = vida_media(x, R3)
    num("vida_media_meses", vm); num("vida_media_paises", nv)
    print(f"  vida media del residuo: {vm:.1f} meses ({nv} países)")
    for pref, kw in (("h3", dict(h=3)), ("sin_deuda", dict()), ("sin_turquia", dict(excluir=("turkey",)))):
        regs = ["lnJ_q2", "D_q2"] if pref == "sin_deuda" else R3
        rr = clark_west(x, regs, **kw)
        for k, v in rr.items():
            num(f"{pref}_{k}", v)
        print(f"  {pref:<12} Clark-West t={rr['t']:.2f} p={rr['p']:.3f} R2 OOS {rr['r2oos']:+.4f}")
    # carteras: barato/caro (residuo recursivo), carry y momentum
    eres = []
    for m in sorted(mm for mm in x["month"].unique() if mm >= p60.INICIO - 1):
        e, _ = residuos(x, R3, m)
        eres.append(pd.DataFrame({"idx": e.index, "e": e.values})[x.loc[e.index, "month"].values == m])
    er = pd.concat(eres).set_index("idx")["e"]
    x["e_rec"] = er.reindex(x.index)
    x["carry"] = x["s"]
    g = x.groupby("country")
    x["mom"] = -(x["ln_s"] - np.where((x["month"] - g["month"].shift(3)).apply(lambda d: getattr(d, "n", np.nan)) == 3,
                                      g["ln_s"].shift(3), np.nan))
    for pref, col in (("cartera_valor", "e_rec"), ("cartera_carry", "carry"), ("cartera_momentum", "mom")):
        st = p60.ledoit_wolf(cartera_desde(x, col)["R"].values)
        for k in ("sr", "p", "lo", "hi"):
            num(f"{pref}_{k}", st[k])
        print(f"  {pref:<18} SR {st['sr']:+.2f} [{st['lo']:+.2f}; {st['hi']:+.2f}] p={st['p']:.3f}")
    out = os.path.join(HERE, "paper_p61_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
