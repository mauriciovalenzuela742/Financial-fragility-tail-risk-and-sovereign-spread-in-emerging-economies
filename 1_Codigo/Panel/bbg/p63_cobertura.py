# -*- coding: utf-8 -*-
"""
p63_cobertura.py -- Q4 del preregistro 8 (4_Redaccion/preregistro_quant2.md, commit fc920b3): una razón de
cobertura condicional a la fragilidad y la deuda.

y = d ln s_{i,m}; F = d ln del promedio de s de las otras doce economías (aproxima el índice EMBI).
La razón del mes m se estima con datos hasta m-1; pérdida = (y - b F)^2.
  (a) beta fijo por país, toda la historia;  (b) beta móvil de 36 meses por país;
  (c) b_i + c1 zDD_{m-1} + c2 zDeuda_{q-4}, MCO agrupado (z estandarizadas con el panel hasta m-1).
Q4-H1: pérdida de (c) < (b), Diebold-Mariano unilateral sobre el promedio mensual (NW 6).

Salida: bbg/paper_p63_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

import p60_senal_dd as p60
import p61_valor_razonable as p61

VIX = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos", "VIX_History.csv"))
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def datos():
    x = p61.fundamentos()
    x["y"] = x["ln_s"] - np.log(x["s_l1"])
    # factor común sin el propio país: promedio de s de los demás con dato en m y m-1
    par = x.dropna(subset=["s", "s_l1"])
    tot = par.groupby("month").agg(S=("s", "sum"), S1=("s_l1", "sum"), n=("s", "size"))
    x = x.merge(tot, left_on="month", right_index=True, how="left")
    ok = x["s"].notna() & x["s_l1"].notna()
    num_m = np.where(ok, x["S"] - x["s"], x["S"]); num_1 = np.where(ok, x["S1"] - x["s_l1"], x["S1"])
    n = np.where(ok, x["n"] - 1, x["n"])
    x["F"] = np.where(n >= 5, np.log(num_m / n) - np.log(num_1 / n), np.nan)
    # VIX: cierre del último día del mes
    v = pd.read_csv(VIX); v["DATE"] = pd.to_datetime(v["DATE"], format="%m/%d/%Y")
    v["month"] = v["DATE"].dt.to_period("M")
    vm = v.groupby("month")["CLOSE"].last()
    x["dvix"] = x["month"].map(np.log(vm) - np.log(vm.shift(1)))
    x["mDD"] = x.groupby("country")["DD_lag"].shift(1) * -1          # -DD_lag en m-1
    return x.drop(columns=["S", "S1", "n"])


def perdidas(x, fac="F", zs=("mDD", "debt_q4"), excluir=()):
    x = x[~x["country"].isin(excluir)].dropna(subset=["y", fac] + list(zs)).copy()
    meses = sorted(m for m in x["month"].unique() if m >= p60.INICIO)
    out = []
    for m in meses:
        tr = x[x["month"] < m]; te = x[x["month"] == m]
        if len(te) == 0:
            continue
        mu, sd = tr[list(zs)].mean(), tr[list(zs)].std()
        for _, r in te.iterrows():
            g = tr[tr["country"] == r["country"]]
            if len(g) < 24:
                continue
            ba = float((g["y"] * g[fac]).sum() / (g[fac] ** 2).sum())
            gb = g.tail(36)
            bb = float((gb["y"] * gb[fac]).sum() / (gb[fac] ** 2).sum())
            out.append(dict(month=m, country=r["country"], y=r["y"], f=r[fac], ba=ba, bb=bb,
                            **{f"z_{z}": (r[z] - mu[z]) / sd[z] for z in zs}))
        # (c) agrupado con datos hasta m-1
        paises = sorted(tr["country"].unique())
        Z = pd.DataFrame({f"b_{c}": (tr["country"] == c).astype(float) * tr[fac] for c in paises})
        for z in zs:
            Z[f"c_{z}"] = ((tr[z] - mu[z]) / sd[z]) * tr[fac]
        coef = np.linalg.lstsq(Z.values, tr["y"].values, rcond=None)[0]
        cf = dict(zip(Z.columns, coef))
        for o in out:
            if o["month"] == m and "bc" not in o:
                o["bc"] = cf.get(f"b_{o['country']}", 0.0) + sum(cf[f"c_{z}"] * o[f"z_{z}"] for z in zs)
    d = pd.DataFrame(out)
    for k in ("ba", "bb", "bc"):
        d[f"L_{k}"] = (d["y"] - d[k] * d["f"]) ** 2
    return d


def dm(d, base, mod="L_bc"):
    s = (d[base] - d[mod]).groupby(d["month"]).mean()
    b, t = p60.nw_media(s.values)
    return float(b[0]), float(t[0]), float(norm.sf(t[0])), len(s)


def reportar(pref, d, base="L_bb"):
    dif, t, p, T = dm(d, base)
    num(f"{pref}_dm_dif", dif); num(f"{pref}_dm_t", t); num(f"{pref}_p", p); num(f"{pref}_meses", T)
    num(f"{pref}_N", len(d))
    for k in ("L_ba", "L_bb", "L_bc"):
        num(f"{pref}_{k}", d[k].mean())
    print(f"  {pref:<16} N={len(d)} meses={T}  pérdida a/b/c {d['L_ba'].mean()*1e4:.2f}/{d['L_bb'].mean()*1e4:.2f}/"
          f"{d['L_bc'].mean()*1e4:.2f} (x1e-4)  DM c vs {base[2:]}: t={t:.2f} p={p:.3f}")
    return p


def main():
    print("p63: Q4, cobertura condicional al factor común")
    x = datos()
    d = perdidas(x)
    reportar("q4h1", d)
    reportar("vs_fijo", d, base="L_ba")
    reportar("vix", perdidas(x, fac="dvix"))
    reportar("solo_dd", perdidas(x, zs=("mDD",)))
    reportar("solo_deuda", perdidas(x, zs=("debt_q4",)))
    reportar("sin_turquia", perdidas(x, excluir=("turkey",)))
    # coeficientes de toda la muestra, errores agrupados por país
    s = x.dropna(subset=["y", "F", "mDD", "debt_q4"]).copy()
    for z in ("mDD", "debt_q4"):
        s[f"c_{z}"] = ((s[z] - s[z].mean()) / s[z].std()) * s["F"]
    D = pd.get_dummies(s["country"], dtype=float).mul(s["F"], axis=0)
    X = pd.concat([D, s[["c_mDD", "c_debt_q4"]]], axis=1)
    res = sm.OLS(s["y"].values, X.values).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(s["country"])[0]})
    for j, z in enumerate(("c_mDD", "c_debt_q4")):
        k = X.shape[1] - 2 + j
        num(f"{z}_coef", res.params[k]); num(f"{z}_p", res.pvalues[k])
    print(f"  toda la muestra: c_DD {res.params[-2]:+.3f} (p {res.pvalues[-2]:.3f}); c_deuda {res.params[-1]:+.3f} (p {res.pvalues[-1]:.3f}); beta medio {D.columns.size and res.params[:-2].mean():.2f}")
    out = os.path.join(HERE, "paper_p63_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
