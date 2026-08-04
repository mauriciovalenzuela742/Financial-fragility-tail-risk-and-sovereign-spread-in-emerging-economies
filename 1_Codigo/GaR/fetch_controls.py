# -*- coding: utf-8 -*-
"""
fetch_controls.py
=================
Descarga los controles macro domesticos (pull factors) para el panel
EMBI x JLoss x GaR y los deja en formato de merge:

    controls_panel.csv  ->  columnas: country, quarter, <controles...>

Paises: brazil, chile, colombia, mexico, peru   |  Ventana: 2009Q4-2023Q4

ADVERTENCIA DE FRECUENCIA (leer antes de usar en la tesis)
----------------------------------------------------------
* Las series de WDI son ANUALES. Aqui se interpolan linealmente a trimestral.
  Esto es razonable para variables de stock/lentas (deuda/PIB, balance fiscal,
  reservas/PIB) pero introduce error de medicion en variables que se mueven
  intra-anual (inflacion, cuenta corriente). Para version final, sustituir por
  fuentes TRIMESTRALES nativas:
    - Inflacion YoY ........ IMF IFS (PCPI) o bancos centrales (mensual->trim)
    - Reservas ............. IMF IFS (RAXG_USD) o bancos centrales (mensual)
    - Cuenta corriente/PIB . IMF IFS BOP trimestral
    - Deuda/PIB ............ IMF Quarterly Public Sector Debt / bancos centrales
* REER: se baja de BIS (mensual, broad) -> promedio trimestral. Si la API de
  BIS cambia, usar el fallback de WDI (PX.REX.REER, anual interpolado).
* Factores GLOBALES (VIX, UST10Y): bajo efectos fijos de TIEMPO se absorben y
  NO hacen falta. Solo se necesitan en specs con efectos fijos de PAIS. VIX ya
  esta en el panel; UST10Y bajarlo de FRED (DGS10) con pandas_datareader.

REQUISITOS:  pip install wbgapi pandas requests
EJECUCION :  python fetch_controls.py
"""

import sys
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# 0. Parametros
# ----------------------------------------------------------------------
ISO = {"brazil": "BRA", "chile": "CHL", "colombia": "COL",
       "mexico": "MEX", "peru": "PER"}
YEAR_MIN, YEAR_MAX = 2009, 2024          # margen para interpolar bordes
Q_START, Q_END = "2009Q4", "2023Q4"      # ventana final exportada

# Indicadores WDI (anuales).  clave_salida : codigo_WDI
WDI = {
    "ca_gdp":      "BN.CAB.XOKA.GD.ZS",   # Cuenta corriente, % PIB
    "infl_yoy":    "FP.CPI.TOTL.ZG",      # Inflacion IPC, % anual
    "res_usd":     "FI.RES.TOTL.CD",      # Reservas totales (US$ corrientes)
    "gdp_usd":     "NY.GDP.MKTP.CD",      # PIB nominal (US$) -> para reservas/PIB
    "debt_gdp":    "GC.DOD.TOTL.GD.ZS",   # Deuda gob. central, % PIB (cobertura parcial)
    "fisc_bal":    "GC.NLD.TOTL.GD.ZS",   # Prestamo/endeudamiento neto, % PIB
    "reer_wdi":    "PX.REX.REER",         # REER (2010=100) anual  [fallback de BIS]
}


# ----------------------------------------------------------------------
# 1. Helpers
# ----------------------------------------------------------------------
def annual_to_quarterly(df_annual):
    """df_annual: index=year(int), columns=paises(iso minuscula? no: country).
    Devuelve serie trimestral interpolada linealmente.
    Estrategia: situar el valor anual en Q2 (mitad de anho) e interpolar."""
    frames = []
    for country in df_annual.columns:
        s = df_annual[country].dropna()
        if s.empty:
            continue
        # valor anual anclado al centro del anho (Q2) y se interpola
        idx = pd.PeriodIndex([f"{int(y)}Q2" for y in s.index], freq="Q")
        sq = pd.Series(s.values, index=idx)
        full = pd.period_range(f"{YEAR_MIN}Q1", f"{YEAR_MAX}Q4", freq="Q")
        sq = sq.reindex(full).astype(float).interpolate(
            method="linear", limit_direction="both")
        out = sq.reset_index()
        out.columns = ["t", "value"]
        out["country"] = country
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


# ----------------------------------------------------------------------
# 2. Descarga WDI via wbgapi
# ----------------------------------------------------------------------
def fetch_wdi():
    import wbgapi as wb
    economies = list(ISO.values())
    inv = {v: k for k, v in ISO.items()}        # ISO -> country
    out = {}
    for key, code in WDI.items():
        print(f"  WDI {key:10s} <- {code} ...", end="", flush=True)
        try:
            d = wb.data.DataFrame(code, economies,
                                  time=range(YEAR_MIN, YEAR_MAX + 1),
                                  skipBlanks=True, columns="series")
            # d: index = (economy, time) o similar; normalizamos
            d = d.reset_index()
            # columnas: 'economy','time', code
            d = d.rename(columns={code: "value"})
            d["year"] = d["time"].astype(str).str.extract(r"(\d{4})").astype(int)
            d["country"] = d["economy"].map(inv)
            wide = d.pivot_table(index="year", columns="country",
                                 values="value", aggfunc="first")
            out[key] = wide
            print(" ok")
        except Exception as e:
            print(f" FALLO ({str(e)[:50]})")
    return out


# ----------------------------------------------------------------------
# 3. Descarga REER mensual de BIS (broad) -> trimestral
#    API SDMX BIS: WS_EER, frecuencia M, tipo R (real), canasta B (broad)
#    Si falla, se usa el fallback WDI (PX.REX.REER anual).
# ----------------------------------------------------------------------
BIS_ISO = {"brazil": "BR", "chile": "CL", "colombia": "CO",
           "mexico": "MX", "peru": "PE"}


def fetch_bis_reer():
    import requests, io
    base = "https://stats.bis.org/api/v1/data/WS_EER/"
    rows = []
    for country, c2 in BIS_ISO.items():
        # key: FREQ.TYPE.BASKET.REF_AREA  =  M.R.B.<c2>
        key = f"M.R.B.{c2}"
        url = base + key + "/all?format=csv"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            # localizar columnas de tiempo/valor (nombres varian segun version)
            tcol = [c for c in df.columns if c.upper() in
                    ("TIME_PERIOD", "TIME", "PERIOD")][0]
            vcol = [c for c in df.columns if c.upper() in
                    ("OBS_VALUE", "VALUE")][0]
            df = df[[tcol, vcol]].rename(columns={tcol: "ym", vcol: "reer"})
            df["t"] = pd.PeriodIndex(pd.to_datetime(df["ym"]).dt.to_period("Q"))
            q = df.groupby("t", as_index=False)["reer"].mean()
            q["country"] = country
            rows.append(q)
            print(f"  BIS REER {country:9s} ok ({len(df)} obs mensuales)")
        except Exception as e:
            print(f"  BIS REER {country:9s} FALLO ({str(e)[:45]}) -> usar fallback WDI")
    if not rows:
        return None
    return pd.concat(rows, ignore_index=True)


# ----------------------------------------------------------------------
# 4. Ensamblar
# ----------------------------------------------------------------------
def main():
    print("== Descargando WDI ==")
    wdi = fetch_wdi()
    if not wdi:
        sys.exit("No se descargo ningun indicador WDI. Revisar conexion/wbgapi.")

    # interpolar cada indicador a trimestral
    panels = {}
    for key, wide in wdi.items():
        if key == "reer_wdi":
            continue  # se maneja al final como fallback
        panels[key] = annual_to_quarterly(wide).rename(columns={"value": key})

    # reservas / PIB (%)
    if "res_usd" in panels and "gdp_usd" in panels:
        m = panels["res_usd"].merge(panels["gdp_usd"], on=["country", "t"])
        m["res_gdp"] = 100.0 * m["res_usd"] / m["gdp_usd"]
        panels["res_gdp"] = m[["country", "t", "res_gdp"]]
        del panels["res_usd"], panels["gdp_usd"]

    # merge incremental de todos los controles WDI
    keys = list(panels.keys())
    ctrl = panels[keys[0]]
    for k in keys[1:]:
        ctrl = ctrl.merge(panels[k], on=["country", "t"], how="outer")

    # REER: BIS (preferente) o fallback WDI
    print("== Descargando REER (BIS) ==")
    bis = fetch_bis_reer()
    if bis is not None and len(bis):
        ctrl = ctrl.merge(bis.rename(columns={"reer": "reer"}),
                          on=["country", "t"], how="left")
    if "reer" not in ctrl.columns or ctrl["reer"].isna().all():
        print("  -> usando fallback REER de WDI (anual interpolado)")
        rwdi = annual_to_quarterly(wdi["reer_wdi"]).rename(columns={"value": "reer"})
        ctrl = ctrl.merge(rwdi, on=["country", "t"], how="left")

    # recortar ventana y formatear quarter
    ctrl["quarter"] = ctrl["t"].astype(str)
    qmask = (ctrl["t"] >= pd.Period(Q_START, "Q")) & (ctrl["t"] <= pd.Period(Q_END, "Q"))
    ctrl = ctrl[qmask].copy()

    cols = ["country", "quarter", "debt_gdp", "fisc_bal", "res_gdp",
            "ca_gdp", "infl_yoy", "reer"]
    cols = [c for c in cols if c in ctrl.columns]
    ctrl = ctrl[cols].sort_values(["country", "quarter"]).reset_index(drop=True)

    ctrl.to_csv("controls_panel.csv", index=False)
    print("\nGuardado controls_panel.csv  shape:", ctrl.shape)
    print("Cobertura no-nula por columna:")
    print((ctrl.notna().mean().round(2) * 100).astype(int).to_string())
    print("\nMuestra:")
    print(ctrl.head(8).to_string())


if __name__ == "__main__":
    main()