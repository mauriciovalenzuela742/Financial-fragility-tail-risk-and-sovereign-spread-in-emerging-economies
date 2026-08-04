# -*- coding: utf-8 -*-
"""
fetch_global_controls.py
=========================
Replica los 3 factores GLOBALES usados como controles en Chari et al. (2024,
JFS) -- el paper de referencia de JLoss:

    1. 10-year U.S. Treasury rate        -> FRED DGS10
    2. U.S. High Yield spread            -> proxy: FRED BAMLH0A0HYM2
                                             (ICE BofA US HY OAS; el paper usa
                                             el indice propietario de JPMorgan,
                                             no disponible sin Bloomberg/JPM
                                             Markets -- se documenta el reemplazo)
    3. On/off-the-run 10Y Treasury spread -> on-the-run (DGS10) MENOS el
                                             rendimiento ajustado de la curva
                                             cupon-cero suavizada (Gurkaynak,
                                             Sack & Wright 2007, dataset
                                             oficial de la Fed: feds200628.csv)

Igual que el resto del pipeline (ver RUNBOOK.md, JLoss_update_plan.md), este
script NO corre dentro del sandbox de Claude por la restriccion de red; se
deja listo para correr en su entorno.

Salida: global_controls_quarterly.csv  (quarter, UST10Y, UST10Y_log,
        US_HY_spread, US_HY_spread_log, OnOffRun_spread, OnOffRun_spread_log)

REQUISITOS: pip install pandas requests
"""
import io
import numpy as np
import pandas as pd
import requests

START = "2003-01-01"   # margen antes de 2004Q1 para no perder el primer trimestre
END   = "2026-12-31"

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}&cosd={start}&coed={end}"
GSW_URL  = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"


def fred_series(series_id):
    url = FRED_CSV.format(id=series_id, start=START, end=END)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["DATE", series_id]
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
    return df.dropna(subset=["DATE"])


def gsw_10y():
    """Curva cupon-cero suavizada de Gurkaynak-Sack-Wright, columna SVENY10
    (10 anios). El CSV de la Fed trae ~50 lineas de metadata antes del
    encabezado real; se detecta automaticamente."""
    r = requests.get(GSW_URL, timeout=120)
    r.raise_for_status()
    text = r.text
    header_idx = next(i for i, line in enumerate(text.splitlines()) if line.startswith("Date,"))
    df = pd.read_csv(io.StringIO(text), skiprows=header_idx)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[["Date", "SVENY10"]].rename(columns={"Date": "DATE", "SVENY10": "GSW10Y"})
    df["GSW10Y"] = pd.to_numeric(df["GSW10Y"], errors="coerce")
    return df.dropna(subset=["DATE"])


def to_quarterly(df, date_col, value_col):
    d = df.copy()
    d["quarter"] = d[date_col].dt.to_period("Q").astype(str)
    return d.groupby("quarter", as_index=False)[value_col].mean()


def main():
    print("Descargando UST 10Y (DGS10)...")
    ust = fred_series("DGS10")
    ust_q = to_quarterly(ust, "DATE", "DGS10")

    print("Descargando proxy de US High Yield spread (BAMLH0A0HYM2, ICE BofA OAS)...")
    hy = fred_series("BAMLH0A0HYM2")
    hy_q = to_quarterly(hy, "DATE", "BAMLH0A0HYM2")

    print("Descargando curva GSW (Gurkaynak-Sack-Wright) para el spread on/off-the-run...")
    gsw = gsw_10y()
    onoff = ust.merge(gsw, on="DATE", how="inner")
    onoff["OnOffRun_spread"] = onoff["DGS10"] - onoff["GSW10Y"]
    onoff_q = to_quarterly(onoff, "DATE", "OnOffRun_spread")

    out = ust_q.merge(hy_q, on="quarter", how="outer").merge(onoff_q, on="quarter", how="outer")
    out = out.rename(columns={"DGS10": "UST10Y", "BAMLH0A0HYM2": "US_HY_spread"})
    out = out.sort_values("quarter")

    # log(x+1), igual que el paper ("the global factor variables are included
    # in the regressions as the natural logarithm of the variables plus one")
    for c in ["UST10Y", "US_HY_spread", "OnOffRun_spread"]:
        out[f"{c}_log"] = np.log(out[c] + 1)

    out.to_csv("global_controls_quarterly.csv", index=False)
    print("Guardado: global_controls_quarterly.csv")
    print(out.tail(10))


if __name__ == "__main__":
    main()
