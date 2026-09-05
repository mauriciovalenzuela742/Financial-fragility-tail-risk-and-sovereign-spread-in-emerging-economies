# -*- coding: utf-8 -*-
"""
p0_controles_all.py -- controles macroeconomicos domesticos para TODOS los paises del
panel Bloomberg (hoy controls_panel.csv solo cubre los 5 LatAm).

Fuentes:
  deuda/PIB, balance fiscal/PIB, reservas/PIB, cuenta corriente/PIB  -> World Bank API (anual)
  inflacion YoY, REER                                                -> series de 1_Codigo/GaR/individuals/
                                                                       (mejor resolucion; respaldo WB)

Series anuales -> interpolacion lineal a trimestral (variables lento-moviles).
Si un indicador no responde para un pais, esa celda queda NaN (se reporta).

Salida -> bbg/controls_all_bbg.csv  (country, quarter, debt_gdp, fisc_bal, res_gdp,
                                     ca_gdp, infl_yoy, reer)  -- LatAm desde el CSV
                                     trimestral existente, el resto reconstruido aqui.
"""
import io
import json
import os
import time
import urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)
COD = os.path.dirname(PANEL)
GAR_IND = os.path.join(COD, "GaR", "individuals")
OUT = os.path.join(HERE, "controls_all_bbg.csv")

LATAM = ["brazil", "chile", "colombia", "mexico", "peru"]
NEW = ["china", "indonesia", "malaysia", "philippines", "southafrica", "turkey",
       "bulgaria", "hungary", "poland", "pakistan", "india", "russia"]

ISO3 = {"brazil": "BRA", "chile": "CHL", "china": "CHN", "colombia": "COL",
        "indonesia": "IDN", "malaysia": "MYS", "mexico": "MEX", "peru": "PER",
        "philippines": "PHL", "southafrica": "ZAF", "turkey": "TUR",
        "bulgaria": "BGR", "hungary": "HUN", "poland": "POL", "pakistan": "PAK",
        "india": "IND", "russia": "RUS"}

# deuda y balance fiscal: IMF WEO (mejor cobertura EM que WB)
IMF = {"debt_gdp": "GGXWDG_NGDP",          # deuda bruta del gobierno general, % PIB
       "fisc_bal": "GGXCNL_NGDP"}          # prestamo/endeudamiento neto gob. general, % PIB
# resto: World Bank API (anual)
WB = {"ca_gdp":   "BN.CAB.XOKA.GD.ZS",     # cuenta corriente, % PIB
      "res_cd":   "FI.RES.TOTL.CD",        # reservas totales, USD corrientes
      "gdp_cd":   "NY.GDP.MKTP.CD"}        # PIB, USD corrientes
YEARS = "2000:2026"


def imf_fetch(iso_list, indicator, tries=4):
    url = f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{'/'.join(iso_list)}"
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                v = json.load(r)["values"].get(indicator, {})
            out = [(iso, int(y), float(val)) for iso in iso_list
                   for y, val in v.get(iso, {}).items() if 2000 <= int(y) <= 2026]
            return pd.DataFrame(out, columns=["iso3", "year", "value"])
        except Exception as e:
            print(f"    [IMF {indicator}] intento {k+1}/{tries} fallo: {str(e)[:60]}")
            time.sleep(3 * (k + 1))
    return pd.DataFrame(columns=["iso3", "year", "value"])


def wb_fetch(iso_list, indicator, tries=4):
    iso = ";".join(iso_list)
    url = (f"https://api.worldbank.org/v2/country/{iso}/indicator/{indicator}"
           f"?format=json&per_page=20000&date={YEARS}")
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = json.load(r)
            rows = data[1] if isinstance(data, list) and len(data) > 1 else []
            out = [(x["countryiso3code"], int(x["date"]), x["value"])
                   for x in rows if x["value"] is not None]
            return pd.DataFrame(out, columns=["iso3", "year", "value"])
        except Exception as e:
            print(f"    [WB {indicator}] intento {k+1}/{tries} fallo: {str(e)[:60]}")
            time.sleep(3 * (k + 1))
    return pd.DataFrame(columns=["iso3", "year", "value"])


def annual_to_quarterly(df_year, col):
    """df_year: columns [country, year, value] -> country, quarter, value interpolado."""
    frames = []
    for c, g in df_year.groupby("country"):
        g = g.sort_values("year")
        idx = pd.period_range(f"{int(g['year'].min())}Q1",
                              f"{int(g['year'].max())}Q4", freq="Q")
        s = pd.Series(np.nan, index=idx)
        for _, r in g.iterrows():
            s.loc[pd.Period(f"{int(r['year'])}Q3", freq="Q")] = r["value"]  # ancla a mitad de anho
        s = s.interpolate(limit_area="inside").ffill(limit=2).bfill(limit=2)
        frames.append(pd.DataFrame({"country": c, "quarter": s.index.astype(str),
                                    col: s.values}))
    return pd.concat(frames, ignore_index=True)


def load_gar_series(country, var):
    """CPI_<C>.csv (mensual, DATES=dd/mm/yyyy) o rEER_<C>.csv (mensual, DATES=YYYYMM)."""
    f = os.path.join(GAR_IND, country.upper(), f"{var}_{country.upper()}.csv")
    if not os.path.isfile(f):
        return None
    d = pd.read_csv(f)
    col = d.columns[1]
    raw = d["DATES"].astype(str)
    if raw.str.match(r"^\d{6}$").all():
        d["date"] = pd.to_datetime(raw, format="%Y%m")
    else:
        d["date"] = pd.to_datetime(raw, dayfirst=True, errors="coerce")
    d = d.dropna(subset=["date", col]).sort_values("date")
    d["quarter"] = d["date"].dt.to_period("Q")
    q = d.groupby("quarter")[col].last()
    return q


def infl_reer_from_gar(countries):
    rows_i, rows_r = [], []
    for c in countries:
        cpi = load_gar_series(c, "CPI")
        if cpi is not None and len(cpi) > 4:
            yoy = (cpi / cpi.shift(4) - 1.0) * 100.0
            rows_i.append(pd.DataFrame({"country": c, "quarter": yoy.index.astype(str),
                                        "infl_yoy": yoy.values}))
        reer = load_gar_series(c, "rEER")
        if reer is not None:
            rows_r.append(pd.DataFrame({"country": c, "quarter": reer.index.astype(str),
                                        "reer": reer.values}))
    di = pd.concat(rows_i, ignore_index=True) if rows_i else pd.DataFrame(columns=["country", "quarter", "infl_yoy"])
    dr = pd.concat(rows_r, ignore_index=True) if rows_r else pd.DataFrame(columns=["country", "quarter", "reer"])
    return di, dr


def main():
    iso2c = {v: k for k, v in ISO3.items()}
    iso_new = [ISO3[c] for c in NEW]
    iso_all = [ISO3[c] for c in NEW + LATAM]     # LatAm tambien, para tapar huecos (p.ej. deuda Chile)

    print("IMF WEO -- deuda / balance fiscal (todos los paises) ...")
    raw = {k: imf_fetch(iso_all, v) for k, v in IMF.items()}
    print("World Bank -- cuenta corriente / reservas / PIB ...")
    raw.update({k: wb_fetch(iso_new, v) for k, v in WB.items()})
    for k, d in raw.items():
        d["country"] = d["iso3"].map(iso2c)
        print(f"  {k:8s}: {d['country'].nunique()} paises, {len(d)} obs anuales")

    # reservas/PIB = res_cd / gdp_cd * 100
    res = raw["res_cd"].merge(raw["gdp_cd"], on=["country", "year"], suffixes=("_res", "_gdp"))
    res["value"] = res["value_res"] / res["value_gdp"] * 100.0
    res = res[["country", "year", "value"]]

    parts = []
    for col, d in [("debt_gdp", raw["debt_gdp"]), ("fisc_bal", raw["fisc_bal"]),
                   ("ca_gdp", raw["ca_gdp"]), ("res_gdp", res)]:
        dd = d[["country", "year", "value"]].dropna()
        if dd.empty:
            print(f"  [!] {col}: sin datos -> columna NaN")
            continue
        parts.append(annual_to_quarterly(dd, col))

    wb_panel = None
    for p in parts:
        wb_panel = p if wb_panel is None else wb_panel.merge(p, on=["country", "quarter"], how="outer")

    di, dr = infl_reer_from_gar(NEW)
    new_panel = wb_panel.merge(di, on=["country", "quarter"], how="outer") \
                        .merge(dr, on=["country", "quarter"], how="outer")

    cols = ["country", "quarter", "debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]
    for c in cols:
        if c not in new_panel.columns:
            new_panel[c] = np.nan
    new_panel = new_panel[new_panel["country"].isin(NEW)]

    # LatAm: del CSV trimestral existente (mejor resolucion) + IMF anual para tapar huecos
    latam = pd.read_csv(os.path.join(PANEL, "controls_panel.csv"))
    latam["country"] = latam["country"].str.lower()
    for col in ("debt_gdp", "fisc_bal"):
        imf_q = annual_to_quarterly(raw[col][raw[col]["country"].isin(LATAM)][["country", "year", "value"]].dropna(), col)
        latam = latam.merge(imf_q, on=["country", "quarter"], how="left", suffixes=("", "_imf"))
        latam[col] = latam[col].fillna(latam[col + "_imf"])
        latam = latam.drop(columns=[col + "_imf"])

    full = pd.concat([latam[cols], new_panel[cols]], ignore_index=True)
    full = full.sort_values(["country", "quarter"]).reset_index(drop=True)
    full.to_csv(OUT, index=False)

    print(f"\nGuardado {OUT}  ({len(full)} filas, {full['country'].nunique()} paises)")
    print("\nCobertura por pais (trimestres con cada control):")
    g = full.groupby("country")[["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]].count()
    print(g.to_string())


if __name__ == "__main__":
    main()
