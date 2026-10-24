# -*- coding: utf-8 -*-
"""
p64_nowcast_gar.py -- Q6 del preregistro 8 (4_Redaccion/preregistro_quant2.md, commit fc920b3): un nowcast
mensual del riesgo de cola.

Modelo trimestral (regresión cuantílica lineal, tau = 0,05, indicadoras de país), en ventana expansiva:
    Q_0.05(g_{i,t+1} | g_{i,t-2}, FCI_{i,t}, VIX_t)
con g el crecimiento interanual (GaR_panel_all18.xlsx), FCI del último mes del trimestre (archivos mensuales
por país) y VIX promedio de los cierres diarios del mes. Nowcast en el mes m del trimestre q, con los
trimestres t tales que t+1 <= q-2: N = -100 * Q_hat(g_{q-2}, FCI_m, VIX_m), en pp como D.

Validación (no entra en Holm): en los fines de trimestre desde 2015, corr(N, D oficial) > 0,9 y error
absoluto mediano < 0,5 pp. Salida: bbg/gar_nowcast_mensual.csv y bbg/paper_p64_numeros.csv.
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

import p60_senal_dd as p60

GAR = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals"))
XLSX = os.path.join(GAR, "nlhpc_gar_all18", "GaR_panel_all18.xlsx")
VIX = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos", "VIX_History.csv"))
SALIDA = os.path.join(HERE, "gar_nowcast_mensual.csv")
PAISES = {"brazil": "BRAZIL", "chile": "CHILE", "china": "CHINA", "colombia": "COLOMBIA", "india": "INDIA",
          "indonesia": "INDONESIA", "malaysia": "MALAYSIA", "mexico": "MEXICO", "peru": "PERU",
          "philippines": "PHILIPPINES", "poland": "POLAND", "southafrica": "SOUTHAFRICA", "turkey": "TURKEY"}
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def fci_mensual():
    filas = []
    for c, C in PAISES.items():
        f = pd.read_csv(os.path.join(GAR, C, f"FCI_{C}.csv"))
        f["month"] = pd.to_datetime(f["DATES"], format="%d/%m/%Y").dt.to_period("M")
        filas.append(f.groupby("month")["FCI"].last().rename("FCI").reset_index().assign(country=c))
    return pd.concat(filas, ignore_index=True)


def vix_mensual():
    v = pd.read_csv(VIX); v["month"] = pd.to_datetime(v["DATE"], format="%m/%d/%Y").dt.to_period("M")
    return v.groupby("month")["CLOSE"].mean().rename("VIX")


def crecimiento():
    g = pd.read_excel(XLSX, sheet_name="Panel")
    g["q"] = pd.to_datetime(g["Date"], format="%d/%m/%Y").dt.to_period("Q")
    inv = {v: k for k, v in PAISES.items()}
    g = g[g["Country"].isin(inv)].assign(country=lambda d: d["Country"].map(inv))
    return g[["country", "q", "g_GDP"]].dropna()


def main():
    print("p64: Q6, nowcast mensual del riesgo de cola")
    fci, vix, g = fci_mensual(), vix_mensual(), crecimiento()
    # muestra trimestral de estimación
    fq = fci.assign(q=fci["month"].dt.asfreq("Q"))
    fq = fq[fq["month"].dt.month.isin([3, 6, 9, 12])][["country", "q", "FCI"]]
    vq = vix.reset_index(); vq = vq[vq["month"].dt.month.isin([3, 6, 9, 12])]
    vq = vq.assign(q=vq["month"].dt.asfreq("Q"))[["q", "VIX"]]
    T = fq.merge(vq, on="q").merge(g, on=["country", "q"])
    gg = g.set_index(["country", "q"])["g_GDP"]
    T["g_l2"] = [gg.get((c, q - 2), np.nan) for c, q in zip(T["country"], T["q"])]
    T["g_f1"] = [gg.get((c, q + 1), np.nan) for c, q in zip(T["country"], T["q"])]
    T = T.dropna(subset=["g_l2", "g_f1", "FCI", "VIX"])
    paises = sorted(PAISES)

    def dis(d):
        D = pd.get_dummies(pd.Categorical(d["country"], categories=paises), drop_first=True, dtype=float)
        D.index = d.index
        return sm.add_constant(pd.concat([d[["g_l2", "FCI", "VIX"]], D], axis=1), has_constant="add")

    # nowcast mensual
    M = fci.merge(vix.reset_index(), on="month")
    M["q"] = M["month"].dt.asfreq("Q")
    M["g_l2"] = [gg.get((c, q - 2), np.nan) for c, q in zip(M["country"], M["q"])]
    M = M[(M["month"] >= p60.INICIO)].dropna(subset=["g_l2", "FCI", "VIX"])
    M["N"] = np.nan
    for q in sorted(M["q"].unique()):
        tr = T[T["q"] + 1 <= q - 2]
        res = sm.QuantReg(tr["g_f1"].values, dis(tr).values).fit(q=0.05, max_iter=5000)
        idx = M.index[M["q"] == q]
        M.loc[idx, "N"] = -100 * (dis(M.loc[idx]).values @ res.params)
    M[["country", "month", "N", "FCI", "VIX"]].assign(month=lambda d: d["month"].astype(str)).to_csv(SALIDA, index=False)
    # validación frente al D oficial del mismo trimestre
    of = pd.read_csv(p60.PANEL, usecols=["country", "quarter", "GaR_pp"]).dropna()
    of["q"] = pd.PeriodIndex(of["quarter"], freq="Q"); of["D"] = -of["GaR_pp"]
    v = M[M["month"].dt.month.isin([3, 6, 9, 12])].merge(of[["country", "q", "D"]], on=["country", "q"]).dropna(subset=["N", "D"])
    corr = float(np.corrcoef(v["N"], v["D"])[0, 1]); mae = float((v["N"] - v["D"]).abs().median())
    num("q6_corr", corr); num("q6_mae_mediano", mae); num("q6_N", len(v))
    num("q6_valida", float(corr > 0.9 and mae < 0.5))
    cp = v.groupby("country").apply(lambda h: np.corrcoef(h["N"], h["D"])[0, 1] if len(h) > 5 else np.nan)
    num("q6_corr_dentro_mediana", cp.median()); num("q6_corr_dentro_min", cp.min())
    num("q6_media_N", v["N"].mean()); num("q6_media_D", v["D"].mean())
    print(f"  validación: corr {corr:.3f}; error absoluto mediano {mae:.2f} pp (N={len(v)}); "
          f"corr dentro del país mediana {cp.median():.2f} (mín {cp.min():.2f}); valida: {bool(NUM['q6_valida'])}")
    print(f"  media N {v['N'].mean():.2f} frente a D {v['D'].mean():.2f}")
    out = os.path.join(HERE, "paper_p64_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}, {SALIDA}")


if __name__ == "__main__":
    main()
