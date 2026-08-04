"""
download_rEER.py  (v2 — corregido para nueva estructura BIS data.bis.org)
-------------------------------------------------------------------------
Descarga el Real Effective Exchange Rate (REER, canasta amplia / Broad)
mensual desde el BIS para 14 países emergentes y exporta al formato
del esquema Chile: DATES,rEER (formato YYYYMM).

Fuente: BIS Effective Exchange Rates
        https://data.bis.org/topics/EER/data
Dataset: WS_EER  |  Clave: M.R.B.{ISO2}

Estrategia en tres capas (se prueba en orden):
  1. API BIS v2  →  stats.bis.org/api/v2  (SDMX, CSV)
  2. Bulk ZIP    →  data.bis.org/static/bulk/WS_EER_csv_flat.zip
                    (descarga ~4 MB, todos los países de una vez)
  3. Manual      →  instrucciones impresas si todo lo anterior falla

Instalación previa:
    pip install requests pandas

Uso:
    python download_rEER.py

Salida:
    ./output_rEER/rEER_{PAÍS}.csv
"""

import io
import os
import sys
import time
import zipfile

import pandas as pd
import requests

# ── Configuración ──────────────────────────────────────────────────────────────

START_PERIOD = "1994-01"    # Igual que serie Chile (199401)
OUTPUT_DIR   = "output_rEER"
TIMEOUT      = 90           # segundos (el ZIP pesa ~4 MB)

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

# ── URLs BIS (corregidas) ──────────────────────────────────────────────────────

# API v2 — SDMX REST, respuesta en CSV
# Documentación: https://stats.bis.org/api-doc/v2/
BIS_API_V2 = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/{key}"

# Bulk download ZIP — CSV plano con todas las series EER
BIS_BULK_ZIP = "https://data.bis.org/static/bulk/WS_EER_csv_flat.zip"

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_yyyymm(period_str: str) -> str:
    """Convierte '2020-01' → '202001' (formato esquema Chile rEER)."""
    return str(period_str).replace("-", "")


def build_dataframes(df_raw: pd.DataFrame,
                     iso_codes: list[str],
                     iso_to_name: dict[str, str]) -> dict[str, pd.DataFrame]:
    """
    A partir de un DataFrame con columnas REF_AREA / TIME_PERIOD / OBS_VALUE
    (insensible a mayúsculas), filtra los países objetivo y devuelve
    dict: iso → DataFrame con columnas DATES, rEER listos para exportar.
    """
    # Normalizar nombres de columna a mayúsculas
    df_raw.columns = df_raw.columns.str.strip().str.upper()

    # Renombrar variantes comunes del BIS flat CSV
    rename_map = {
        "REF_AREA":   "REF_AREA",
        "REFERENCE AREA": "REF_AREA",
        "TIME_PERIOD": "TIME_PERIOD",
        "TIME PERIOD": "TIME_PERIOD",
        "OBS_VALUE":  "OBS_VALUE",
        "VALUE":      "OBS_VALUE",
    }
    df_raw = df_raw.rename(columns={k: v for k, v in rename_map.items() if k in df_raw.columns})

    required = {"REF_AREA", "TIME_PERIOD", "OBS_VALUE"}
    missing  = required - set(df_raw.columns)
    if missing:
        print(f"    Columnas faltantes en CSV: {missing}")
        print(f"    Columnas disponibles: {df_raw.columns.tolist()[:10]}")
        return {}

    # Filtrar: Real (R), Broad (B), mensual (M) y países objetivo
    for col, val in [("EER_TYPE", "R"), ("BASKET", "B"), ("FREQ", "M")]:
        if col in df_raw.columns:
            df_raw = df_raw[df_raw[col].str.strip().str.upper() == val]

    df_raw = df_raw[df_raw["REF_AREA"].str.strip().str.upper().isin(iso_codes)]

    # Filtrar desde START_PERIOD
    start_ym = START_PERIOD.replace("-", "")
    df_raw   = df_raw[df_raw["TIME_PERIOD"].str.replace("-", "") >= start_ym]

    result = {}
    for iso in iso_codes:
        sub = df_raw[df_raw["REF_AREA"].str.strip().str.upper() == iso].copy()
        if sub.empty:
            continue

        sub["OBS_VALUE"] = pd.to_numeric(sub["OBS_VALUE"], errors="coerce")
        sub = sub.dropna(subset=["OBS_VALUE"])
        sub["DATES"]     = sub["TIME_PERIOD"].str.replace("-", "")
        sub = sub.sort_values("DATES").reset_index(drop=True)
        result[iso] = sub[["DATES", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "rEER"})

    return result


# ── Capa 1: API BIS v2 ─────────────────────────────────────────────────────────

def download_via_api_v2(iso_codes: list[str]) -> pd.DataFrame | None:
    """
    Llama a la API SDMX v2 del BIS en formato CSV.
    Parámetros: M (mensual), R (real), B (broad), países concatenados con +
    """
    key = "M.R.B." + "+".join(iso_codes)
    url = BIS_API_V2.format(key=key)
    params = {
        "startPeriod": START_PERIOD,
        "format":      "csv",
    }
    print(f"  [Capa 1] API BIS v2...")
    print(f"  URL: {url}")
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT,
                         headers={"Accept": "text/csv, application/csv"})
        if r.status_code in (404, 400):
            print(f"    HTTP {r.status_code} — serie no encontrada en API v2.")
            return None
        r.raise_for_status()
        if not r.text.strip():
            print("    Respuesta vacía.")
            return None
        df = pd.read_csv(io.StringIO(r.text))
        print(f"    ✓ API v2 OK — {len(df)} filas")
        return df
    except Exception as e:
        print(f"    Error API v2: {e}")
        return None


# ── Capa 2: Bulk ZIP ───────────────────────────────────────────────────────────

def download_via_bulk_zip(iso_codes: list[str]) -> pd.DataFrame | None:
    """
    Descarga el ZIP completo de EER del BIS (~4 MB) y extrae el CSV plano.
    Contiene todas las series EER (real + nominal, broad + narrow, todos los países).
    """
    print(f"  [Capa 2] Bulk ZIP BIS...")
    print(f"  URL: {BIS_BULK_ZIP}")
    try:
        r = requests.get(BIS_BULK_ZIP, timeout=TIMEOUT,
                         headers={"User-Agent": "Mozilla/5.0 (research)"})
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            names = z.namelist()
            print(f"    Archivos en ZIP: {names}")

            # Buscar el CSV plano (normalmente el único .csv)
            csv_name = next((n for n in names if n.endswith(".csv")), None)
            if csv_name is None:
                print("    No se encontró CSV en el ZIP.")
                return None

            print(f"    Leyendo: {csv_name}")
            with z.open(csv_name) as f:
                df = pd.read_csv(f, low_memory=False)

        print(f"    ✓ ZIP OK — {len(df)} filas, columnas: {df.columns.tolist()[:8]}")
        return df

    except Exception as e:
        print(f"    Error ZIP: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    iso_codes   = list(COUNTRIES.values())
    iso_to_name = {v: k for k, v in COUNTRIES.items()}

    print(f"\n{'='*60}")
    print(f"  Descarga rEER (BIS Broad REER) — {len(COUNTRIES)} países")
    print(f"  Desde: {START_PERIOD}")
    print(f"  Salida: ./{OUTPUT_DIR}/")
    print(f"{'='*60}\n")

    # ── Intentar capas en orden ───────────────────────────────────────────────
    df_raw = download_via_api_v2(iso_codes)

    if df_raw is None or df_raw.empty:
        print()
        df_raw = download_via_bulk_zip(iso_codes)

    if df_raw is None or df_raw.empty:
        print(f"\n  ❌ No se pudo descargar automáticamente.")
        print(f"\n  → DESCARGA MANUAL:")
        print(f"    1. Ir a: https://data.bis.org/bulkdownload")
        print(f"    2. Sección 'Effective exchange rates'")
        print(f"    3. Descargar: 'Effective exchange rates (CSV, flat)'")
        print(f"    4. Descomprimir y guardar el CSV como: eer_flat.csv")
        print(f"    5. Ejecutar: parse_manual('eer_flat.csv')")
        sys.exit(1)

    # ── Construir DataFrames por país ─────────────────────────────────────────
    print()
    country_dfs = build_dataframes(df_raw, iso_codes, iso_to_name)

    found, missing = [], []
    for iso in iso_codes:
        name = iso_to_name[iso]
        if iso in country_dfs and not country_dfs[iso].empty:
            df_out   = country_dfs[iso]
            out_path = os.path.join(OUTPUT_DIR, f"rEER_{name}.csv")
            df_out.to_csv(out_path, index=False)
            t0, t1 = df_out["DATES"].iloc[0], df_out["DATES"].iloc[-1]
            print(f"  ✓ {name:<15} {len(df_out):>4} obs  ({t0} → {t1})")
            found.append(name)
        else:
            print(f"  ✗ {name:<15} sin datos en la respuesta BIS")
            missing.append(name)

    print(f"\n{'='*60}")
    print(f"  Exportados: {len(found)}/14")
    if missing:
        print(f"  Sin datos:  {', '.join(missing)}")
        print(f"  (Venezuela y Panama tienen cobertura limitada en BIS REER)")
    print(f"{'='*60}\n")


# ── Función auxiliar para parseo manual ───────────────────────────────────────

def parse_manual(filepath: str):
    """
    Parsea el CSV plano descargado manualmente desde data.bis.org/bulkdownload.
    Llama desde Python:
        from download_rEER import parse_manual
        parse_manual("eer_flat.csv")
    """
    iso_to_name = {v: k for k, v in COUNTRIES.items()}
    iso_codes   = list(COUNTRIES.values())

    print(f"Leyendo {filepath}...")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  {len(df)} filas, columnas: {df.columns.tolist()[:10]}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    country_dfs = build_dataframes(df, iso_codes, iso_to_name)

    for iso, df_out in country_dfs.items():
        name     = iso_to_name[iso]
        out_path = os.path.join(OUTPUT_DIR, f"rEER_{name}.csv")
        df_out.to_csv(out_path, index=False)
        print(f"  ✓ {name}: {len(df_out)} obs  ({df_out['DATES'].iloc[0]} → {df_out['DATES'].iloc[-1]})")


if __name__ == "__main__":
    main()