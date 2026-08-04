"""
download_CPI_GDP.py
-------------------
Descarga CPI mensual y GDP trimestral (+ deriva gGDP) desde la API JSON
del IMF IFS para 14 países emergentes. Un único script, tres métricas.

Fuente: IMF International Financial Statistics (IFS)
        https://data.imf.org
API:    http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/

Series usadas:
  CPI  → frecuencia M, indicador PCPI_IX
           (Consumer Prices, All items, Index)
  GDP  → frecuencia Q, indicador NGDP_R_SA_XDC  [preferida]
           fallback: NGDP_R_XDC → NGDP_SA_XDC → NGDP_XDC
           (GDP Real SA, o nominal si SA no disponible, Domestic Currency)
  gGDP → derivado de GDP como (GDP_t / GDP_{t-4}) - 1  (variación YoY decimal)

Esquema de salida (igual que Chile):
  CPI:  DATES (DD/MM/YYYY último día del mes),  CPI  (nivel índice)
  GDP:  DATES (DD/MM/YYYY, día 1 del último mes del trimestre), GDP (moneda local)
  gGDP: DATES (igual que GDP),                  GDP  (tasa decimal)

Instalación previa:
    pip install requests pandas

Uso:
    python download_CPI_GDP.py

Salida:
    ./output_CPI/CPI_{PAÍS}.csv
    ./output_GDP/GDP_{PAÍS}.csv
    ./output_gGDP/gGDP_{PAÍS}.csv
"""

import os
import sys
import time
import calendar
from datetime import date

import requests
import pandas as pd

# ── Configuración ──────────────────────────────────────────────────────────────

IMF_BASE     = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS"
START_PERIOD = "1986-01"        # Ajustar si se necesita desde antes
REQUEST_DELAY = 3               # segundos entre llamadas (límite IMF: ~10 req/min)
TIMEOUT       = 60              # segundos por request

OUT_CPI  = "output_CPI"
OUT_GDP  = "output_GDP"
OUT_GGDP = "output_gGDP"

# Países: nombre → código ISO-2 IMF (coincide con ISO-2 estándar)
COUNTRIES = {
    "ARGENTINA":    "AR",
    "BULGARIA":     "BG",
    "CHINA":        "CN",
    "EGYPT":        "EG",
    "INDONESIA":    "ID",
    "MALAYSIA":     "MY",
    "PAKISTAN":     "PK",
    "PANAMA":       "PA",
    "PHILIPPINES":  "PH",
    "POLAND":       "PL",
    "RUSSIA":       "RU",
    "SOUTH_AFRICA": "ZA",
    "TURKEY":       "TR",
    "VENEZUELA":    "VE",
}

# Cascada de series para GDP (en orden de preferencia)
GDP_SERIES_PRIORITY = [
    "NGDP_R_SA_XDC",   # Real, Seasonally Adjusted, Domestic Currency ← ideal
    "NGDP_R_XDC",      # Real, not SA, Domestic Currency
    "NGDP_SA_XDC",     # Nominal, SA, Domestic Currency
    "NGDP_XDC",        # Nominal, not SA, Domestic Currency (último recurso)
]

# Notas sobre países problemáticos
COUNTRY_NOTES = {
    "AR": "⚠️  Argentina: CPI oficial manipulado 2007–2016 (INDEC). "
          "Considerar empalme con índice provincial (San Luis / CABA) para ese período.",
    "TR": "⚠️  Turquía: redenominación monetaria 2005 (1 TRY = 1,000,000 TRL). "
          "IMF IFS debería entregar la serie en TRY nuevo, pero verificar.",
    "VE": "⚠️  Venezuela: datos IMF IFS incompletos/discontinuos post-2015 "
          "por hiperinflación. Evaluar imputación o exclusión del panel.",
    "RU": "⚠️  Rusia: posibles brechas/rezagos en IFS post-2022.",
    "PK": "⚠️  Pakistán: GDP trimestral SA puede estar ausente en IFS. "
          "El script intentará series alternativas.",
}

# ── Helpers de fecha ──────────────────────────────────────────────────────────

def last_day_of_month(year: int, month: int) -> str:
    """Devuelve el último día del mes en formato DD/MM/YYYY."""
    day = calendar.monthrange(year, month)[1]
    return f"{day:02d}/{month:02d}/{year}"


def quarterly_to_date(period: str) -> str:
    """
    Convierte '2020-Q1' → '01/03/2020' (primer día del último mes del trimestre).
    Convención Chile: Q1→Mar, Q2→Jun, Q3→Sep, Q4→Dec
    """
    year, q = period.split("-Q")
    year = int(year)
    end_month = int(q) * 3         # Q1→3, Q2→6, Q3→9, Q4→12
    return f"01/{end_month:02d}/{year}"


def monthly_to_date(period: str) -> str:
    """
    Convierte '2020-01' → '31/01/2020' (último día del mes).
    """
    year, month = int(period[:4]), int(period[5:7])
    return last_day_of_month(year, month)


# ── API IMF IFS ───────────────────────────────────────────────────────────────

def imf_get(freq: str, countries_str: str, indicator: str) -> dict | None:
    """
    Llama a la API IMF IFS y devuelve el JSON parseado, o None si falla.
    countries_str: códigos separados por '+', ej. 'AR+BG+CN'
    """
    url = f"{IMF_BASE}/{freq}.{countries_str}.{indicator}?startPeriod={START_PERIOD}"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 404:
            return None          # Serie no disponible
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print(f"    Timeout para {indicator}.")
        return None
    except Exception as e:
        print(f"    Error en request: {e}")
        return None


def extract_series(json_data: dict) -> list[dict]:
    """
    Extrae lista de series del JSON IMF IFS.
    Maneja los casos: Series como dict (1 país) o lista (varios países).
    Devuelve lista de dicts con claves: ref_area, obs (lista de {period, value}).
    """
    try:
        ds = json_data["CompactData"]["DataSet"]
        raw = ds.get("Series", [])
    except (KeyError, TypeError):
        return []

    # Normalizar a lista
    if isinstance(raw, dict):
        raw = [raw]

    result = []
    for s in raw:
        ref_area = s.get("@REF_AREA", "??")
        obs_raw  = s.get("Obs", [])
        if isinstance(obs_raw, dict):
            obs_raw = [obs_raw]

        obs = []
        for o in obs_raw:
            period = o.get("@TIME_PERIOD", "")
            value  = o.get("@OBS_VALUE",  None)
            if period and value is not None:
                try:
                    obs.append({"period": period, "value": float(value)})
                except (ValueError, TypeError):
                    pass

        if obs:
            result.append({"ref_area": ref_area, "obs": obs})

    return result


# ── Descarga CPI (mensual) ────────────────────────────────────────────────────

def download_cpi(iso_codes: list[str]) -> dict[str, pd.DataFrame]:
    """
    Descarga PCPI_IX mensual para todos los países de una vez.
    Devuelve dict: iso_code → DataFrame con columnas DATES, CPI.
    """
    countries_str = "+".join(iso_codes)
    print(f"  → Descargando CPI (PCPI_IX, mensual) para {len(iso_codes)} países...")

    data = imf_get("M", countries_str, "PCPI_IX")
    if data is None:
        print("    ❌ Sin respuesta de la API para CPI.")
        return {}

    series_list = extract_series(data)
    if not series_list:
        print("    ❌ JSON recibido pero sin series extraíbles.")
        return {}

    result = {}
    for s in series_list:
        iso   = s["ref_area"]
        obs   = s["obs"]
        rows  = [{"DATES": monthly_to_date(o["period"]), "CPI": o["value"]}
                 for o in obs]
        df = pd.DataFrame(rows)
        df["_sort"] = pd.to_datetime(df["DATES"], format="%d/%m/%Y")
        df = df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
        result[iso] = df

    print(f"    ✓ CPI recibido para: {list(result.keys())}")
    return result


# ── Descarga GDP (trimestral, con fallback de series) ─────────────────────────

def download_gdp_single(freq: str, countries_str: str, indicator: str) -> list[dict]:
    """Intenta descargar una serie GDP y devuelve las series extraídas."""
    data = imf_get(freq, countries_str, indicator)
    if data is None:
        return []
    return extract_series(data)


def download_gdp(iso_codes: list[str]) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """
    Descarga GDP trimestral usando cascada de series.
    Devuelve:
      - dict: iso_code → DataFrame con columnas DATES, GDP
      - dict: iso_code → nombre de la serie efectivamente usada
    """
    print(f"  → Descargando GDP (trimestral) para {len(iso_codes)} países...")

    countries_str = "+".join(iso_codes)
    result       = {}   # iso → DataFrame
    series_used  = {}   # iso → indicador
    pending      = set(iso_codes)

    for indicator in GDP_SERIES_PRIORITY:
        if not pending:
            break

        pending_str = "+".join(sorted(pending))
        print(f"    Probando serie {indicator} para: {sorted(pending)}...")
        time.sleep(REQUEST_DELAY)

        series_list = download_gdp_single("Q", pending_str, indicator)

        for s in series_list:
            iso = s["ref_area"]
            if iso not in pending:
                continue
            obs = s["obs"]
            if not obs:
                continue

            rows = [{"DATES": quarterly_to_date(o["period"]), "GDP": o["value"]}
                    for o in obs
                    if "-Q" in o["period"]]

            if not rows:
                continue

            df = pd.DataFrame(rows)
            df["_sort"] = pd.to_datetime(df["DATES"], format="%d/%m/%Y")
            df = df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
            result[iso]      = df
            series_used[iso] = indicator
            pending.discard(iso)

        if series_list:
            found = [s["ref_area"] for s in series_list if s["ref_area"] in result]
            if found:
                print(f"    ✓ {indicator}: {found}")

    if pending:
        print(f"    ⚠️  Sin datos GDP para: {sorted(pending)}")

    return result, series_used


# ── Derivar gGDP ──────────────────────────────────────────────────────────────

def derive_ggdp(gdp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Deriva gGDP como variación interanual decimal: (GDP_t / GDP_{t-4}) - 1.
    Devuelve DataFrame con columnas DATES, GDP (misma columna que Chile).
    """
    df = gdp_df.copy()
    df["GDP"] = df["GDP"].astype(float)
    df["gGDP"] = df["GDP"] / df["GDP"].shift(4) - 1
    df = df.dropna(subset=["gGDP"])
    df = df.rename(columns={"gGDP": "GDP"})  # mismo nombre que en Chile
    return df[["DATES", "GDP"]].reset_index(drop=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for d in [OUT_CPI, OUT_GDP, OUT_GGDP]:
        os.makedirs(d, exist_ok=True)

    iso_codes   = list(COUNTRIES.values())
    iso_to_name = {v: k for k, v in COUNTRIES.items()}

    print(f"\n{'='*60}")
    print(f"  Descarga CPI + GDP + gGDP — IMF IFS — {len(COUNTRIES)} países")
    print(f"  Desde: {START_PERIOD}")
    print(f"{'='*60}\n")

    # ── CPI ───────────────────────────────────────────────────────────────────
    cpi_data = download_cpi(iso_codes)
    time.sleep(REQUEST_DELAY)

    cpi_ok, cpi_fail = [], []
    for iso in iso_codes:
        name = iso_to_name[iso]
        if iso in cpi_data and not cpi_data[iso].empty:
            df = cpi_data[iso]
            df.to_csv(os.path.join(OUT_CPI, f"CPI_{name}.csv"), index=False)
            n  = len(df)
            t0 = df["DATES"].iloc[0]
            t1 = df["DATES"].iloc[-1]
            print(f"  ✓ CPI_{name}: {n} obs  ({t0} → {t1})")
            cpi_ok.append(name)
            if iso in COUNTRY_NOTES:
                print(f"    {COUNTRY_NOTES[iso]}")
        else:
            print(f"  ✗ CPI_{name}: sin datos")
            cpi_fail.append(name)

    # ── GDP + gGDP ────────────────────────────────────────────────────────────
    print()
    gdp_data, series_used = download_gdp(iso_codes)
    print()

    gdp_ok, gdp_fail = [], []
    for iso in iso_codes:
        name = iso_to_name[iso]
        if iso in gdp_data and not gdp_data[iso].empty:
            df_gdp = gdp_data[iso]
            serie  = series_used.get(iso, "?")

            # Guardar GDP
            df_gdp.to_csv(os.path.join(OUT_GDP, f"GDP_{name}.csv"), index=False)

            # Derivar y guardar gGDP
            df_gg = derive_ggdp(df_gdp)
            df_gg.to_csv(os.path.join(OUT_GGDP, f"gGDP_{name}.csv"), index=False)

            n  = len(df_gdp)
            t0 = df_gdp["DATES"].iloc[0]
            t1 = df_gdp["DATES"].iloc[-1]
            print(f"  ✓ GDP_{name}: {n} obs  ({t0} → {t1})  [{serie}]")
            if iso in COUNTRY_NOTES:
                print(f"    {COUNTRY_NOTES[iso]}")
            gdp_ok.append(name)
        else:
            print(f"  ✗ GDP_{name}: sin datos en ninguna serie IFS")
            gdp_fail.append(name)

    # ── Resumen ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  CPI exportados  : {len(cpi_ok)}/14")
    print(f"  GDP exportados  : {len(gdp_ok)}/14  (gGDP derivado automáticamente)")
    if cpi_fail:
        print(f"  CPI pendientes : {', '.join(cpi_fail)}")
    if gdp_fail:
        print(f"  GDP pendientes : {', '.join(gdp_fail)}")
    print(f"\n  Series GDP usadas:")
    for iso, ind in series_used.items():
        print(f"    {iso_to_name.get(iso, iso):15s} → {ind}")
    print(f"{'='*60}\n")

    if cpi_fail or gdp_fail:
        print("  Alternativas para países sin datos en IFS:")
        print("  - Banco Mundial WDI: https://databank.worldbank.org/source/world-development-indicators")
        print("    CPI: indicador FP.CPI.TOTL (anual, base 2010=100)")
        print("    GDP: indicador NY.GDP.MKTP.KN (real, moneda local)")
        print("  - Para Venezuela/Argentina: ver notas en COUNTRY_NOTES en este script.")


if __name__ == "__main__":
    main()
