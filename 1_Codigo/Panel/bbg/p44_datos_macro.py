# -*- coding: utf-8 -*-
"""
p44_datos_macro.py -- datos de las pruebas macro preregistradas (4_Redaccion/preregistro_macro.md, commit
f820594, anterior a este script):

  - FXDEBT / LCDEBT: deuda bruta del gobierno general en moneda extranjera / local, % del PIB, trimestral
    (Banco Mundial QPSD, fuente 20: DP.DOD.DECF.CR.GG.Z1 y DP.DOD.DECN.CR.GG.Z1).
  - Régimen cambiario: clasificación gruesa mensual de Ilzetzki, Reinhart y Rogoff
    (2_Datos/irr/ERA_Classification_Monthly_1940-2025.xlsx, hoja "Coarse"); se toma el último mes de
    cada trimestre; flexible = categorías 3 y 4.

Salida: bbg/macro_trimestral_bbg.csv y la cobertura en bbg/paper_p44_cobertura.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p41_datos_resiliencia as p41

OUT = os.path.join(HERE, "macro_trimestral_bbg.csv")
IRR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos", "irr", "ERA_Classification_Monthly_1940-2025.xlsx"))
NOMBRES = {"argentina": "Argentina", "brazil": "Brazil", "chile": "Chile", "china": "China", "colombia": "Colombia",
           "india": "India", "indonesia": "Indonesia", "malaysia": "Malaysia", "mexico": "Mexico", "peru": "Peru",
           "philippines": "Philippines", "poland": "Poland", "southafrica": "South Africa", "turkey": "Turk"}


def irr():
    raw = pd.read_excel(IRR, sheet_name="Coarse", header=None)
    nombres = (raw.iloc[4].fillna("").astype(str) + " " + raw.iloc[5].fillna("").astype(str)).str.strip()
    fechas = raw.iloc[7:, 1].astype(str)
    filas = []
    for c, patron in NOMBRES.items():
        cols = [j for j, n in enumerate(nombres) if j >= 2 and n.lower().startswith(patron.lower())]
        if not cols:
            print(f"  IRR: sin columna para {c}"); continue
        j = cols[0]
        s = pd.to_numeric(raw.iloc[7:, j], errors="coerce")
        for f, v in zip(fechas, s):
            if "M" not in f or pd.isna(v):
                continue
            a, m = f.split("M")
            filas.append({"country": c, "month": pd.Period(year=int(a), month=int(m), freq="M"), "coarse": float(v),
                          "irr_nombre": nombres[j]})
    d = pd.DataFrame(filas)
    d["quarter"] = d["month"].dt.asfreq("Q").astype(str)
    q = d.sort_values("month").groupby(["country", "quarter"]).agg(coarse=("coarse", "last"), irr_nombre=("irr_nombre", "first")).reset_index()
    q["flexible"] = q["coarse"].isin([3, 4]).astype(float)
    return q


def main():
    if os.path.exists(OUT):
        print("caché presente"); return
    fx = p41.wb("DP.DOD.DECF.CR.GG.Z1", 20, "2000Q1:2026Q4").rename(columns={"valor": "fxdebt"})
    lc = p41.wb("DP.DOD.DECN.CR.GG.Z1", 20, "2000Q1:2026Q4").rename(columns={"valor": "lcdebt"})
    for d in (fx, lc):
        d["quarter"] = d["periodo"].map(p41.trimestre)
    q = fx[["country", "quarter", "fxdebt"]].merge(lc[["country", "quarter", "lcdebt"]], on=["country", "quarter"], how="outer")
    q = q.merge(irr(), on=["country", "quarter"], how="outer").sort_values(["country", "quarter"])
    q = q[q["quarter"] >= "2000Q1"]
    q.to_csv(OUT, index=False)
    cob = q.groupby("country").agg(fx_n=("fxdebt", "count"), lc_n=("lcdebt", "count"), irr_n=("coarse", "count"),
                                   irr_nombre=("irr_nombre", "first"), flexible_media=("flexible", "mean"))
    cob.to_csv(os.path.join(HERE, "paper_p44_cobertura.csv"))
    print(cob.to_string())


if __name__ == "__main__":
    main()
