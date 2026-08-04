"""
download_STX.py
---------------
Descarga índices bursátiles diarios para 14 países emergentes usando yfinance
y los exporta al formato del esquema Chile: DATES,STX (DD/MM/YYYY).

Instalación previa:
    pip install yfinance pandas

Uso:
    python download_STX.py

Salida:
    Un CSV por país en la carpeta ./output_STX/
    Ejemplo: STX_ARGENTINA.csv
"""

import yfinance as yf
import pandas as pd
import os
from datetime import date

# ── Configuración ──────────────────────────────────────────────────────────────

START_DATE  = "1993-01-01"          # Igual que serie Chile; yfinance trunca si no hay datos
END_DATE    = date.today().isoformat()
OUTPUT_DIR  = "output_STX"

# Diccionario: nombre_país → ticker Yahoo Finance
COUNTRIES = {
    "ARGENTINA":    "^MERV",        # S&P MERVAL
    "BULGARIA":     "^SOFIX",       # SOFIX Sofia — puede fallar; ver nota (1)
    "CHINA":        "000001.SS",    # SSE Composite
    "EGYPT":        "^CASE",        # EGX 30
    "INDONESIA":    "^JKSE",        # IDX Composite
    "MALAYSIA":     "^KLSE",        # FTSE Bursa Malaysia KLCI
    "PAKISTAN":     "^KSE",         # KSE-100
    "PANAMA":       None,           # BVP sin ticker en Yahoo — ver nota (2)
    "PHILIPPINES":  "PSEI.PS",      # PSEi
    "POLAND":       "^WIG",         # WIG Warsaw
    "RUSSIA":       "IMOEX.ME",     # MOEX Russia Index — ver nota (3)
    "SOUTH_AFRICA": "^JN0U.JO",     # JSE All Share
    "TURKEY":       "XU100.IS",     # BIST 100
    "VENEZUELA":    "^IBC",         # IBC Caracas — ver nota (4)
}

# ── Notas sobre casos especiales ───────────────────────────────────────────────
# (1) BULGARIA / SOFIX: si ^SOFIX falla en yfinance, descargar manualmente desde
#     Investing.com → https://www.investing.com/indices/sofix-historical-data
#     El archivo Investing.com usa formato: Date,Price,Open,High,Low,Vol.,Change%
#     Usar la función parse_investing_csv() incluida al final de este script.
#
# (2) PANAMA / BVP: la Bolsa de Valores de Panamá no tiene ticker en Yahoo Finance.
#     Descargar desde: https://www.bvp.com.pa/Estadisticas/Mercado
#     El índice general BVP tiene muy baja liquidez y frecuencia irregular.
#
# (3) RUSSIA / IMOEX: Yahoo Finance puede tener huecos post-febrero 2022 debido a
#     suspensión de operaciones MOEX. Datos hasta ~Feb 2022 son fiables.
#     Fuente alternativa: moex.com/ru/index/IMOEX/history/
#
# (4) VENEZUELA / IBC: serie muy irregular post-2017 (hiperinflación, suspensiones).
#     Verificar manualmente la calidad antes de usar en el panel.

# ── Funciones ─────────────────────────────────────────────────────────────────

def download_and_format(country: str, ticker: str) -> pd.DataFrame | None:
    """Descarga serie diaria de cierre y la formatea al esquema Chile."""
    print(f"  Descargando {country} ({ticker})...", end=" ", flush=True)
    try:
        raw = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            progress=False,
            auto_adjust=True,
        )
        if raw.empty:
            print("SIN DATOS — verificar ticker o fuente alternativa.")
            return None

        # Extraer precio de cierre (Close)
        close = raw[["Close"]].copy()

        # Aplanar MultiIndex si lo hay
        if isinstance(close.columns, pd.MultiIndex):
            close.columns = ["Close"]

        close = close.dropna()
        close = close.sort_index(ascending=False)  # Más reciente primero (igual que Chile)

        # Formatear fecha DD/MM/YYYY
        close.index = pd.to_datetime(close.index)
        close["DATES"] = close.index.strftime("%d/%m/%Y")
        close = close.rename(columns={"Close": "STX"})
        close = close[["DATES", "STX"]]

        n = len(close)
        print(f"OK — {n} observaciones ({close['DATES'].iloc[-1]} → {close['DATES'].iloc[0]})")
        return close

    except Exception as e:
        print(f"ERROR — {e}")
        return None


def parse_investing_csv(filepath: str, country: str) -> pd.DataFrame | None:
    """
    Parsea un CSV descargado manualmente de Investing.com.
    Formato Investing.com: "Date","Price","Open","High","Low","Vol.","Change %"
    Úsala para Bulgaria (SOFIX) u otros índices no disponibles en yfinance.

    Ejemplo de uso:
        df = parse_investing_csv("SOFIX Historical Data.csv", "BULGARIA")
        if df is not None:
            df.to_csv("output_STX/STX_BULGARIA.csv", index=False)
    """
    try:
        raw = pd.read_csv(filepath, thousands=",")
        raw["DATES"] = pd.to_datetime(raw["Date"], format="%m/%d/%Y", dayfirst=False)
        raw = raw.sort_values("DATES", ascending=False)
        raw["DATES"] = raw["DATES"].dt.strftime("%d/%m/%Y")

        # "Price" puede venir como string con comas
        raw["STX"] = pd.to_numeric(
            raw["Price"].astype(str).str.replace(",", ""), errors="coerce"
        )

        result = raw[["DATES", "STX"]].dropna().reset_index(drop=True)
        print(f"  Parseado {country} desde {filepath}: {len(result)} obs.")
        return result
    except Exception as e:
        print(f"  ERROR parseando {filepath}: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    failed = []

    print(f"\n{'='*60}")
    print(f"  Descarga STX — {len(COUNTRIES)} países")
    print(f"  Rango: {START_DATE} → {END_DATE}")
    print(f"  Salida: ./{OUTPUT_DIR}/")
    print(f"{'='*60}\n")

    for country, ticker in COUNTRIES.items():
        if ticker is None:
            print(f"  {country}: sin ticker en Yahoo Finance — descarga manual requerida.")
            failed.append(country)
            continue

        df = download_and_format(country, ticker)

        if df is not None:
            out_path = os.path.join(OUTPUT_DIR, f"STX_{country}.csv")
            df.to_csv(out_path, index=False)
        else:
            failed.append(country)

    print(f"\n{'='*60}")
    print(f"  Completado.")
    if failed:
        print(f"  ⚠️  Requieren descarga manual: {', '.join(failed)}")
        print(f"     Usar parse_investing_csv() para archivos de Investing.com.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()


# ── Uso de parse_investing_csv (ejemplo) ──────────────────────────────────────
# Si descargaste manualmente el SOFIX desde Investing.com, ejecuta esto
# en un script separado o en Jupyter:
#
# from download_STX import parse_investing_csv
# import os
#
# df_bg = parse_investing_csv("SOFIX Historical Data.csv", "BULGARIA")
# if df_bg is not None:
#     os.makedirs("output_STX", exist_ok=True)
#     df_bg.to_csv("output_STX/STX_BULGARIA.csv", index=False)
#
# df_pa = parse_investing_csv("BVP Historical Data.csv", "PANAMA")
# if df_pa is not None:
#     df_pa.to_csv("output_STX/STX_PANAMA.csv", index=False)
