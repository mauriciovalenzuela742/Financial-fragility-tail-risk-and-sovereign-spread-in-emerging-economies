# -*- coding: utf-8 -*-
"""
x4_bandas_frecuencia.py -- EXPERIMENTO B3: ¿a qué frecuencia comueve cada riesgo con el spread?

Regresión por bandas de frecuencia (Engle, 1974). Ordena en una sola tabla lo que la segunda ronda
encontró por partes: la fragilidad comueve con el spread dentro del trimestre; el riesgo de cola
solo aparece en niveles.

=========================== DECLARADO ANTES DE ESTIMAR (2026-10-13) ===========================
 - Por país, sobre el tramo contiguo más largo de la muestra de estimación (mínimo 40 trimestres),
   se descomponen ln EMBI(t), ln JLoss(t-1) y D(t-1) en tres bandas:
       corta: 2 a 6 trimestres;  ciclo: 6 a 32 trimestres;  tendencia: el resto (más de 32).
   Filtro primario: pasa-banda de Christiano-Fitzgerald (dos lados).
   Control: descomposición de un solo lado con medias móviles (no usa datos futuros):
       corta = x - MM4;  ciclo = MM4 - MM16;  tendencia = MM16.
 - En cada banda: spread_banda sobre J_banda y D_banda, con efectos fijos de país y de tiempo,
   covarianza agrupada por país y p del wild cluster bootstrap (Webb, B = 999) por coeficiente.
 - Expectativa declarada: la fragilidad comueve en la banda corta; el riesgo de cola, si aparece,
   en la de ciclo o en la tendencia.
 - Variante: spread de cierre de trimestre en lugar del promedio (por el solapamiento de fechas).
 - Advertencia: los componentes filtrados están autocorrelacionados por construcción y la
   tendencia de 13 países tiene muy pocos grados de libertad efectivos; su inferencia es la menos
   confiable de las tres.
=================================================================================================
Salida: experimentos/x4_bandas.csv (y _nivlag). No se integra a ningún documento.
"""
import os

import numpy as np
import pandas as pd
from statsmodels.tsa.filters.cf_filter import cffilter

import x0_comun as x0

NUM = {}
B = 999
BANDAS = ("corta", "ciclo", "tendencia")


def num(k, v):
    NUM[k] = float(v)
    return v


def tramo_largo(g):
    q = pd.PeriodIndex(g["quarter"], freq="Q")
    qn = (q.year * 4 + q.quarter).to_numpy()
    cortes = np.where(np.diff(qn) != 1)[0] + 1
    tramos = np.split(np.arange(len(g)), cortes)
    return g.iloc[max(tramos, key=len)]


def cf(x):
    c1, _ = cffilter(x, low=2, high=6, drift=True)
    c2, _ = cffilter(x, low=6, high=32, drift=True)
    return {"corta": c1, "ciclo": c2, "tendencia": x - c1 - c2}


def mm(x):
    s = pd.Series(x)
    m4, m16 = s.rolling(4).mean(), s.rolling(16).mean()
    return {"corta": (s - m4).to_numpy(), "ciclo": (m4 - m16).to_numpy(), "tendencia": m16.to_numpy()}


def descomponer(dd, ycol, filtro):
    filas = []
    for c, g in dd.groupby("country"):
        g = tramo_largo(g.sort_values("quarter"))
        if len(g) < 40:
            continue
        partes = {v: filtro(g[col].to_numpy(float)) for v, col in (("y", ycol), ("J", "ln_JLoss_l1"), ("D", "D_l1"))}
        for b in BANDAS:
            filas.append(pd.DataFrame({"country": c, "quarter": g["quarter"].to_numpy(), "banda": b,
                                       "y": partes["y"][b], "J": partes["J"][b], "D": partes["D"][b]}))
    return pd.concat(filas, ignore_index=True).dropna()


def estimar(desc, pref):
    num(f"{pref}_paises", desc["country"].nunique())
    for b in BANDAS:
        s = desc[desc["banda"] == b]
        A, _ = x0.within(s, ["y", "J", "D"])
        g = pd.factorize(s["country"])[0]
        num(f"{pref}_{b}_N", len(s))
        num(f"{pref}_{b}_var_y_share", s["y"].var() / desc.groupby("banda")["y"].var().sum())
        for k, lab in enumerate(("J", "D")):
            bb, se = x0.t_cluster(A[:, 0], A[:, 1:], k, g)
            _, p = x0.wild_wald(A[:, 0], A[:, 1:], [k], g, B=B, seed=40 + k)
            num(f"{pref}_{b}_{lab}", bb); num(f"{pref}_{b}_{lab}_t_cluster", bb / se); num(f"{pref}_{b}_{lab}_p_wild", p)
        _, u = x0.ols(A[:, 0], A[:, 1:])
        num(f"{pref}_{b}_r2_within", 1 - (u ** 2).sum() / (A[:, 0] ** 2).sum())
        num(f"{pref}_{b}_corr_J_D", np.corrcoef(A[:, 1], A[:, 2])[0, 1])


def main():
    print("x4: forma", "niveles" if x0.NIV else "logs")
    dd = x0.datos()
    assert len(dd) == 765
    estimar(descomponer(dd, "ln_EMBI", cf), "cf")
    estimar(descomponer(dd, "ln_EMBI", mm), "mm")
    alt = pd.read_csv(os.path.join(x0.BBG, "embi_trimestral_alternativo.csv"))[["country", "quarter", "EMBI_eop5"]]
    de = dd.merge(alt, on=["country", "quarter"], how="left").dropna(subset=["EMBI_eop5"])
    de = de[de["EMBI_eop5"] > 0].copy()
    de["y_eop"] = de["EMBI_eop5"] if x0.NIV else np.log(de["EMBI_eop5"])
    estimar(descomponer(de, "y_eop", cf), "cf_cierre")
    sp = dd[dd["country"] != "poland"]
    estimar(descomponer(sp, "ln_EMBI", cf), "cf_sinpolonia")
    st = dd[dd["country"] != "turkey"]
    estimar(descomponer(st, "ln_EMBI", cf), "cf_sinturquia")
    for k, v in NUM.items():
        print(f"  {k:42s} {v: .4f}")
    x0.guardar(NUM, "x4_bandas")


if __name__ == "__main__":
    main()
