# -*- coding: utf-8 -*-
"""
p41_datos_resiliencia.py -- datos trimestrales de resiliencia según las reglas del preregistro
(4_Redaccion/preregistro_resiliencia.md, commit c492ca3, anterior a este script).

  - DEBT: deuda bruta del gobierno general, todos los instrumentos, valor nominal, % del PIB,
    trimestral (Banco Mundial, Quarterly Public Sector Debt, fuente 20, DP.DOD.DECT.CR.GG.Z1).
    Si falta, gobierno central (DP.DOD.DECT.CR.CG.Z1); si tampoco, la serie anual interpolada del
    panel (debt_gdp), marcada.
  - Reservas: FMI IFS/IRFCL era la fuente primaria, pero la API (api.imf.org) no expone en sus
    metadatos el código del indicador de reservas oficiales totales; se usa el respaldo preregistrado,
    Banco Mundial Global Economic Monitor (fuente 15, TOTRESV, mensual, USD), y se declara.
  - Deuda externa de corto plazo, todos los sectores e instrumentos, USD, trimestral (QEDS SDDS,
    fuente 22, DT.DOD.DSTC.CD.US; si falta, QEDS GDDS, fuente 23).
  - RA = ln(reservas del último mes del trimestre / deuda externa de corto plazo).

Salida: bbg/resiliencia_trimestral_bbg.csv, bbg/reservas_mensual_bbg.csv y la cobertura por país en
bbg/paper_p41_cobertura.csv. Requiere red; con las cachés presentes no la usa.
"""
import os
import json
import time
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_Q = os.path.join(HERE, "resiliencia_trimestral_bbg.csv")
OUT_M = os.path.join(HERE, "reservas_mensual_bbg.csv")
ISO = {"argentina": "ARG", "brazil": "BRA", "chile": "CHL", "china": "CHN", "colombia": "COL", "india": "IND",
       "indonesia": "IDN", "malaysia": "MYS", "mexico": "MEX", "peru": "PER", "philippines": "PHL",
       "poland": "POL", "southafrica": "ZAF", "turkey": "TUR"}
INV = {v: k for k, v in ISO.items()}


def wb(indicador, fuente, fechas):
    url = (f"https://api.worldbank.org/v2/country/{';'.join(ISO.values())}/indicator/{indicador}"
           f"?source={fuente}&format=json&per_page=20000&date={fechas}")
    for intento in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                d = json.loads(r.read().decode("utf-8"))
            break
        except Exception as e:
            print(f"  reintento {intento + 1} ({e})"); time.sleep(5)
    else:
        return pd.DataFrame(columns=["country", "periodo", "valor"])
    filas = d[1] if isinstance(d, list) and len(d) > 1 and d[1] else []
    out = []
    for r in filas:
        iso = r.get("countryiso3code") or r["country"]["id"]
        if r.get("value") is None or iso not in INV:
            continue
        out.append({"country": INV[iso], "periodo": r["date"], "valor": float(r["value"])})
    return pd.DataFrame(out)


def trimestre(s):
    s = str(s).replace(" ", "")
    return str(pd.Period(s.replace("Q", "Q"), freq="Q"))


def main():
    if os.path.exists(OUT_Q) and os.path.exists(OUT_M):
        print("cachés presentes; no se descarga"); return
    gg = wb("DP.DOD.DECT.CR.GG.Z1", 20, "2000Q1:2026Q4"); gg["fuente_debt"] = "QPSD_GG"
    cg = wb("DP.DOD.DECT.CR.CG.Z1", 20, "2000Q1:2026Q4"); cg["fuente_debt"] = "QPSD_CG"
    st = wb("DT.DOD.DSTC.CD.US", 22, "2000Q1:2026Q4"); st["fuente_st"] = "QEDS_SDDS"
    st2 = wb("DT.DOD.DSTC.CD.US", 23, "2000Q1:2026Q4"); st2["fuente_st"] = "QEDS_GDDS"
    rv = wb("TOTRESV", 15, "2000M01:2026M12")
    print(f"  QPSD GG {len(gg)}, CG {len(cg)}, QEDS SDDS {len(st)}, GDDS {len(st2)}, GEM reservas {len(rv)}")
    for df in (gg, cg, st, st2):
        if len(df):
            df["quarter"] = df["periodo"].map(trimestre)
    # reservas mensuales -> último mes del trimestre
    rv["month"] = pd.PeriodIndex(rv["periodo"].str.replace("M", "-"), freq="M")
    rv = rv.rename(columns={"valor": "reservas_musd"})[["country", "month", "reservas_musd"]].sort_values(["country", "month"])
    rv["month"] = rv["month"].astype(str)
    rv.to_csv(OUT_M, index=False)
    rq = rv.assign(quarter=pd.PeriodIndex(rv["month"], freq="M").asfreq("Q").astype(str)) \
           .groupby(["country", "quarter"])["reservas_musd"].last().reset_index().rename(columns={"reservas_musd": "reservas_usd"})
    # deuda: GG, si falta CG
    deb = gg.rename(columns={"valor": "debt_q"})[["country", "quarter", "debt_q", "fuente_debt"]]
    if len(cg):
        c2 = cg.rename(columns={"valor": "debt_q"})[["country", "quarter", "debt_q", "fuente_debt"]]
        deb = pd.concat([deb, c2[~c2.set_index(["country", "quarter"]).index.isin(deb.set_index(["country", "quarter"]).index)]])
    stq = st.rename(columns={"valor": "st_debt_usd"})[["country", "quarter", "st_debt_usd", "fuente_st"]]
    if len(st2):
        s2 = st2.rename(columns={"valor": "st_debt_usd"})[["country", "quarter", "st_debt_usd", "fuente_st"]]
        stq = pd.concat([stq, s2[~s2.set_index(["country", "quarter"]).index.isin(stq.set_index(["country", "quarter"]).index)]])
    q = rq.merge(stq, on=["country", "quarter"], how="outer").merge(deb, on=["country", "quarter"], how="outer")
    # GEM reporta las reservas en millones de USD; QEDS, la deuda en USD
    q["reservas_usd"] = q["reservas_usd"] * 1e6
    q["RA"] = np.log(q["reservas_usd"] / q["st_debt_usd"].where(q["st_debt_usd"] > 0))
    q = q.sort_values(["country", "quarter"])
    q.to_csv(OUT_Q, index=False)
    cob = q.groupby("country").agg(
        debt_desde=("quarter", lambda s: s[q.loc[s.index, "debt_q"].notna()].min()),
        debt_n=("debt_q", "count"), fuente_debt=("fuente_debt", lambda s: ",".join(sorted(set(s.dropna())))),
        RA_desde=("quarter", lambda s: s[q.loc[s.index, "RA"].notna()].min()), RA_n=("RA", "count"),
        res_n=("reservas_usd", "count"))
    cob.to_csv(os.path.join(HERE, "paper_p41_cobertura.csv"))
    print(cob.to_string())


if __name__ == "__main__":
    main()
