# -*- coding: utf-8 -*-
"""
p7b_iv_commodity_tot.py -- instrumento adicional para el IV de C2 (punto del
plan de arbitro): un shock de TERMINOS DE INTERCAMBIO por exposicion
sectorial a commodities, a la Gruss (2014) / Fernandez-Gonzalez-Rodriguez
(2018) -- el diseno estandar shift-share de la literatura de "commodity
super-cycle" para fragilidad bancaria/soberana en economias emergentes.

DISENO (mas limpio que los 2 instrumentos existentes en `causal_core.py`,
que estiman la exposicion phi_i REGRESANDO JLoss contra el shock global en el
pre-periodo -- un paso adicional de estimacion que introduce su propia
incertidumbre/circularidad). Aqui la "participacion" (share) es EXOGENA a
JLoss: viene de la composicion de EXPORTACIONES pre-muestra de cada pais
(World Bank WDI, promedio 1998-2003, ANTES del inicio de la muestra de
estimacion 2004Q1) en 4 categorias amplias de commodities. El "shock" es el
indice de precio MUNDIAL de esa categoria (World Bank Pink Sheet / CMO), la
misma fuente exogena para las 13 economias.

    CTOT_shock_{i,t} = sum_k  w_{i,k}(pre-2004)  *  log( P_{k,t} )

  w_{i,k}   = share de exportaciones de mercancias del pais i en la categoria
              k (fuel/energia, minerales y metales, materias primas
              agricolas, alimentos), promedio 1998-2003 (WDI TX.VAL.*.ZS.UN).
  P_{k,t}   = indice de precio mundial de la categoria k, World Bank Pink
              Sheet ("Monthly Indices": Energy, Metals & Minerals,
              Raw Materials, Food), agregado a trimestral (promedio), log.

Fuentes:
  - World Bank WDI API (indicadores TX.VAL.FUEL/MMTL/AGRI/FOOD.ZS.UN).
  - World Bank Pink Sheet (CMO-Historical-Data-Monthly.xlsx, hoja
    "Monthly Indices"), enlace resuelto dinamicamente desde la pagina
    "commodity-markets" (el nombre de archivo cambia de hash con cada
    actualizacion mensual).

Salida -> ctot_shock_bbg.csv (country, quarter, CTOT_shock, CTOT_shock_dlog)
       -> se mezcla en Panel_bloomberg.csv.
"""
import io
import os
import re
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

ISO3 = {
    "brazil": "BRA", "chile": "CHL", "china": "CHN", "colombia": "COL",
    "india": "IND", "indonesia": "IDN", "malaysia": "MYS", "mexico": "MEX",
    "peru": "PER", "philippines": "PHL", "poland": "POL",
    "southafrica": "ZAF", "turkey": "TUR",
}
WDI_IND = {
    "fuel": "TX.VAL.FUEL.ZS.UN",           # <-> Energy
    "mmtl": "TX.VAL.MMTL.ZS.UN",           # <-> Metals & Minerals
    "agri": "TX.VAL.AGRI.ZS.UN",           # <-> Raw Materials
    "food": "TX.VAL.FOOD.ZS.UN",           # <-> Food
}
CMO_COL = {"fuel": "Energy", "mmtl": "MetalsMinerals", "agri": "RawMaterials", "food": "Food"}
PRESAMPLE_YEARS = (1998, 2003)   # antes de 2004Q1 (inicio de la muestra de estimacion)


def fetch_wdi_shares():
    ctys = ";".join(ISO3.values())
    frames = []
    for cat, ind in WDI_IND.items():
        url = (f"https://api.worldbank.org/v2/country/{ctys}/indicator/{ind}"
               f"?date={PRESAMPLE_YEARS[0]}:{PRESAMPLE_YEARS[1]}&format=json&per_page=2000")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        import json
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        rows = data[1] if len(data) > 1 and data[1] else []
        d = pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]}
                          for r in rows if r["value"] is not None])
        d["cat"] = cat
        frames.append(d)
    long = pd.concat(frames, ignore_index=True)
    w = long.groupby(["iso3", "cat"])["value"].mean().unstack("cat")  # promedio pre-muestra
    inv = {v: k for k, v in ISO3.items()}
    w.index = w.index.map(inv.get)
    w = w.dropna(how="all")
    return w[["fuel", "mmtl", "agri", "food"]]


def fetch_cmo_prices():
    page = "https://www.worldbank.org/en/research/commodity-markets"
    req = urllib.request.Request(page, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r"https?://[^\"'\s]+CMO-Historical-Data-Monthly[^\"'\s]*\.xlsx", html)
    if not m:
        raise RuntimeError("No se encontro el enlace del Pink Sheet en la pagina de commodity-markets")
    url = m.group(0)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    d = pd.read_excel(io.BytesIO(raw), sheet_name="Monthly Indices", header=None)
    data = d.iloc[9:, [0, 2, 6, 10, 14]].copy()
    data.columns = ["month", "Energy", "Food", "RawMaterials", "MetalsMinerals"]
    data = data.dropna(subset=["month"])
    data["month"] = pd.to_datetime(data["month"], format="%YM%m")
    for c in ["Energy", "Food", "RawMaterials", "MetalsMinerals"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data["quarter"] = data["month"].dt.to_period("Q").astype(str)
    q = data.groupby("quarter", as_index=False)[["Energy", "Food", "RawMaterials", "MetalsMinerals"]].mean()
    for c in ["Energy", "Food", "RawMaterials", "MetalsMinerals"]:
        q[f"log_{c}"] = np.log(q[c])
    return q.sort_values("quarter"), url


def main():
    print("Descargando participaciones de exportacion pre-muestra (WDI, "
          f"{PRESAMPLE_YEARS[0]}-{PRESAMPLE_YEARS[1]}) ...")
    w = fetch_wdi_shares()
    print(w.round(1).to_string())
    missing = [c for c in ISO3 if c not in w.index or w.loc[c].isna().any()]
    if missing:
        print(f"  ADVERTENCIA -- sin datos WDI completos para: {missing} "
              f"(se completan con la media del resto)")
        w = w.reindex(list(ISO3.keys()))
        w = w.fillna(w.mean())

    print("\nDescargando precios de commodities (World Bank Pink Sheet) ...")
    q, src_url = fetch_cmo_prices()
    print(f"  fuente: {src_url}")
    print(f"  {q['quarter'].min()}..{q['quarter'].max()}, {len(q)} trimestres")

    rows = []
    for c, wc in w.iterrows():
        s = wc / 100.0   # WDI viene en % de exportaciones de mercancias
        z = (s["fuel"] * q["log_Energy"] + s["mmtl"] * q["log_MetalsMinerals"]
             + s["agri"] * q["log_RawMaterials"] + s["food"] * q["log_Food"])
        rows.append(pd.DataFrame({"country": c, "quarter": q["quarter"], "CTOT_shock": z}))
    out = pd.concat(rows, ignore_index=True).sort_values(["country", "quarter"])
    out["CTOT_shock_dlog"] = out.groupby("country")["CTOT_shock"].diff()
    out.to_csv(os.path.join(HERE, "ctot_shock_bbg.csv"), index=False)
    print(f"\nGuardado: bbg/ctot_shock_bbg.csv ({len(out)} filas, {out['country'].nunique()} paises)")

    pcsv = os.path.join(HERE, "Panel_bloomberg.csv")
    p = pd.read_csv(pcsv)
    p = p.drop(columns=[c for c in ("CTOT_shock", "CTOT_shock_dlog") if c in p.columns])
    p = p.merge(out, on=["country", "quarter"], how="left")
    p.to_csv(pcsv, index=False)
    print(f"Mezclado en Panel_bloomberg.csv: {p['CTOT_shock'].notna().sum()}/{len(p)} filas")

    # pesos usados, para trazabilidad en NUMEROS_CANONICOS_BBG.md
    w.round(1).to_csv(os.path.join(HERE, "ctot_pesos_pre2004.csv"))
    print("Guardado: bbg/ctot_pesos_pre2004.csv (pesos de exportacion pre-muestra usados)")


if __name__ == "__main__":
    main()
