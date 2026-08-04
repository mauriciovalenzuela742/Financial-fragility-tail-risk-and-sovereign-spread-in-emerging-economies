"""
download_Ryr.py
---------------
Descarga el rendimiento del bono soberano a 10 años (Ryr) para 14 países
emergentes y exporta al formato del esquema Chile: DATES,Ryr (DD/MM/YYYY).

Estrategia híbrida en dos capas:

  CAPA 1 — FRED API (automático, gratuito, mensual)
    Fuente: Federal Reserve Bank of St. Louis
    URL:    https://fred.stlouisfed.org
    API key gratuita en: https://fred.stlouisfed.org/docs/api/api_key.html
    Cubre: Bulgaria, China, Indonesia, Malaysia, Philippines,
           Poland, Russia, South Africa, Turkey (series mensuales OCDE)

  CAPA 2 — Investing.com CSV (manual, diario)
    Para países sin serie en FRED (Argentina, Egypt, Pakistan, Panama,
    Venezuela) O si prefieres frecuencia diaria para todos.
    Instrucciones de descarga al final del script.

Salida:
    ./output_Ryr/Ryr_{PAÍS}.csv

Instalación previa:
    pip install requests pandas

Uso:
    1. Pon tu FRED API key en la variable FRED_API_KEY (o deja "" para
       intentar sin key — funciona con límite de 120 req/min).
    2. python download_Ryr.py
    3. Para países que requieren Investing.com:
       descarga los CSV según instrucciones impresas y re-ejecuta
       con los archivos en ./investing_csv/
"""

import io
import os
import re
import time
from datetime import date

import pandas as pd
import requests

# ── Configuración ──────────────────────────────────────────────────────────────

FRED_API_KEY  = "636fea127605fe6647602872cfcbf0a0"              # Opcional pero recomendado (gratuito en fred.stlouisfed.org)
FRED_BASE     = "https://api.stlouisfed.org/fred/series/observations"
START_DATE    = "1993-01-01"
REQUEST_DELAY = 0.5             # segundos entre llamadas FRED
OUTPUT_DIR    = "output_Ryr"
INVESTING_DIR = "investing_csv" # Carpeta donde colocar los CSV de Investing.com

# ── Mapa de países ─────────────────────────────────────────────────────────────
#
# Serie FRED: patrón OECD MEI → IRLTLT01{ISO2}M156N (mensual)
#   o IRLTLT01{ISO2}Q156N (trimestral en algunos casos)
#
# Investing.com: slug para construir URL de descarga manual
#
COUNTRIES = {
    #  nombre          fred_series                   investing_slug                      notas
    "ARGENTINA":   ("IRLTLT01ARQ156N",           "argentina-10-year-bond-yield",     "⚠️ FRED solo trimestral; prefiere Investing.com para diario"),
    "BULGARIA":    ("IRLTLT01BGM156N",           "bulgaria-10-year-bond-yield",      ""),
    "CHINA":       ("IRLTLT01CNM156N",           "china-10-year-bond-yield",         ""),
    "EGYPT":       (None,                        "egypt-10-year-bond-yield",         "⚠️ No en FRED; requiere Investing.com (disponible desde ~2010)"),
    "INDONESIA":   ("IRLTLT01IDM156N",           "indonesia-10-year-bond-yield",     ""),
    "MALAYSIA":    ("IRLTLT01MYM156N",           "malaysia-10-year-bond-yield",      ""),
    "PAKISTAN":    (None,                        "pakistan-10-year-bond-yield",      "⚠️ No en FRED; requiere Investing.com"),
    "PANAMA":      (None,                        "panama-10-year-bond-yield",        "⚠️ No en FRED; bono USD; Investing.com desde ~2011"),
    "PHILIPPINES": ("IRLTLT01PHM156N",           "philippines-10-year-bond-yield",   ""),
    "POLAND":      ("IRLTLT01PLM156N",           "poland-10-year-bond-yield",        ""),
    "RUSSIA":      ("IRLTLT01RUM156N",           "russia-10-year-bond-yield",        "⚠️ FRED puede tener huecos post-2022"),
    "SOUTH_AFRICA":("IRLTLT01ZAM156N",           "south-africa-10-year-bond-yield",  ""),
    "TURKEY":      ("IRLTLT01TRM156N",           "turkey-10-year-bond-yield",        ""),
    "VENEZUELA":   (None,                        "venezuela-10-year-bond-yield",     "⚠️ No en FRED; datos muy escasos post-2017"),
}

# ── Helpers de fecha ──────────────────────────────────────────────────────────

def to_ddmmyyyy(date_str: str) -> str:
    """
    Convierte cualquier formato de fecha reconocible a DD/MM/YYYY.
    Maneja: YYYY-MM-DD, MM/DD/YYYY, 'Jun 25, 2026', 'Jun 25 2026', etc.
    """
    date_str = str(date_str).strip()

    # YYYY-MM-DD (FRED)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        y, m, d = date_str.split("-")
        return f"{d}/{m}/{y}"

    # Intentar pandas para el resto (Investing.com varía por locale)
    try:
        dt = pd.to_datetime(date_str, dayfirst=False)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return date_str  # devuelve sin convertir; se detectará después


# ── CAPA 1: FRED API ──────────────────────────────────────────────────────────

def fred_download(series_id: str) -> pd.DataFrame | None:
    """
    Descarga una serie FRED y devuelve DataFrame con columnas DATES, Ryr.
    DATES en formato DD/MM/YYYY.
    """
    params = {
        "series_id":         series_id,
        "observation_start": START_DATE,
        "observation_end":   date.today().isoformat(),
        "file_type":         "json",
        "sort_order":        "asc",
    }
    if FRED_API_KEY:
        params["api_key"] = FRED_API_KEY

    try:
        r = requests.get(FRED_BASE, params=params, timeout=30)
        if r.status_code == 400:
            # Serie no encontrada
            return None
        r.raise_for_status()
        obs = r.json().get("observations", [])
        if not obs:
            return None

        rows = []
        for o in obs:
            val = o.get("value", ".")
            if val == "." or val is None:
                continue                    # FRED usa "." para missing
            try:
                rows.append({
                    "DATES": to_ddmmyyyy(o["date"]),
                    "Ryr":   float(val),
                })
            except (ValueError, KeyError):
                continue

        if not rows:
            return None

        df = pd.DataFrame(rows)
        df["_sort"] = pd.to_datetime(df["DATES"], format="%d/%m/%Y")
        df = df.sort_values("_sort", ascending=False).drop(columns="_sort").reset_index(drop=True)
        return df

    except requests.exceptions.Timeout:
        print(f"    Timeout en FRED serie {series_id}.")
        return None
    except Exception as e:
        print(f"    Error FRED {series_id}: {e}")
        return None


# ── CAPA 2: Investing.com CSV parser ─────────────────────────────────────────

def parse_investing_csv(filepath: str) -> pd.DataFrame | None:
    """
    Parsea un CSV histórico descargado manualmente de Investing.com.

    Investing.com exporta en dos formatos posibles:
      A) "Date","Price","Open","High","Low","Change %"
         con fecha tipo "Jun 25, 2026"
      B) "Date","Price","Open","High","Low","Change %"
         con fecha tipo "06/25/2026" (MM/DD/YYYY)

    La columna "Price" es el rendimiento en %.
    """
    if not os.path.isfile(filepath):
        return None

    try:
        # Leer con distintos encodings comunes en Investing.com
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(filepath, encoding=enc, thousands=",")
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"    No se pudo decodificar {filepath}.")
            return None

        # Normalizar nombres de columna
        df.columns = df.columns.str.strip().str.replace('"', '')

        # Buscar columna de fecha
        date_col = next(
            (c for c in df.columns if c.lower() in ("date", "fecha", "dates")),
            None
        )
        if date_col is None:
            print(f"    No se encontró columna de fecha en {filepath}. Columnas: {df.columns.tolist()}")
            return None

        # Buscar columna de precio/yield
        price_col = next(
            (c for c in df.columns if c.lower() in ("price", "precio", "close", "cierre", "last")),
            None
        )
        if price_col is None:
            print(f"    No se encontró columna de precio en {filepath}. Columnas: {df.columns.tolist()}")
            return None

        # Limpiar y convertir precio
        df[price_col] = (
            df[price_col]
            .astype(str)
            .str.replace(",", "")
            .str.replace("%", "")
            .str.strip()
        )
        df["Ryr"] = pd.to_numeric(df[price_col], errors="coerce")
        df = df.dropna(subset=["Ryr"])

        # Convertir fechas
        df["DATES"] = df[date_col].apply(to_ddmmyyyy)

        # Verificar conversión (descartar filas con fechas inválidas)
        mask = df["DATES"].str.match(r"^\d{2}/\d{2}/\d{4}$", na=False)
        if mask.sum() < len(df) * 0.9:
            # Intentar con dayfirst=True
            df["DATES"] = pd.to_datetime(
                df[date_col], dayfirst=True, errors="coerce"
            ).dt.strftime("%d/%m/%Y")

        df = df.dropna(subset=["DATES"])
        df["_sort"] = pd.to_datetime(df["DATES"], format="%d/%m/%Y", errors="coerce")
        df = df.sort_values("_sort", ascending=False).drop(columns="_sort").reset_index(drop=True)

        return df[["DATES", "Ryr"]].reset_index(drop=True)

    except Exception as e:
        print(f"    Error parseando {filepath}: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INVESTING_DIR, exist_ok=True)

    need_investing = []   # países que requieren descarga manual

    print(f"\n{'='*60}")
    print(f"  Descarga Ryr (10Y Bond Yield) — {len(COUNTRIES)} países")
    print(f"  Desde: {START_DATE}")
    print(f"{'='*60}\n")

    for name, (fred_id, inv_slug, note) in COUNTRIES.items():

        out_path     = os.path.join(OUTPUT_DIR, f"Ryr_{name}.csv")
        inv_filename = os.path.join(INVESTING_DIR, f"{name}.csv")
        df_out       = None
        source_used  = None

        # ── Intentar Investing.com CSV si ya está descargado ─────────────────
        if os.path.isfile(inv_filename):
            df_inv = parse_investing_csv(inv_filename)
            if df_inv is not None and not df_inv.empty:
                df_out      = df_inv
                source_used = f"Investing.com ({inv_filename}) [diario]"

        # ── Si no, intentar FRED ──────────────────────────────────────────────
        if df_out is None and fred_id is not None:
            time.sleep(REQUEST_DELAY)
            df_fred = fred_download(fred_id)
            if df_fred is not None and not df_fred.empty:
                df_out      = df_fred
                source_used = f"FRED {fred_id} [mensual]"

        # ── Guardar o marcar pendiente ─────────────────────────────────────────
        if df_out is not None:
            df_out.to_csv(out_path, index=False)
            n  = len(df_out)
            t1 = df_out["DATES"].iloc[0]
            t0 = df_out["DATES"].iloc[-1]
            print(f"  ✓ {name:<15} {n:>5} obs  ({t0} → {t1})  ← {source_used}")
            if note:
                print(f"    {note}")
        else:
            status = "sin serie FRED + sin CSV Investing"
            if fred_id is None:
                status = "sin serie FRED → requiere Investing.com"
            print(f"  ✗ {name:<15} {status}")
            if note:
                print(f"    {note}")
            need_investing.append((name, inv_slug))

    # ── Instrucciones para descarga manual ───────────────────────────────────
    if need_investing:
        print(f"\n{'='*60}")
        print(f"  DESCARGA MANUAL REQUERIDA — Investing.com")
        print(f"{'='*60}")
        print(f"\n  Para cada país pendiente:")
        print(f"  1. Ir a la URL de Investing.com")
        print(f"  2. Click en 'Historical Data' (pestaña superior derecha)")
        print(f"  3. Seleccionar rango máximo disponible")
        print(f"  4. Click 'Download Data' (botón CSV)")
        print(f"  5. Renombrar el archivo y colocarlo en ./{INVESTING_DIR}/\n")

        for name, slug in need_investing:
            url      = f"https://www.investing.com/rates-bonds/{slug}-historical-data"
            filename = os.path.join(INVESTING_DIR, f"{name}.csv")
            print(f"  {name}")
            print(f"    URL:     {url}")
            print(f"    Guardar: {filename}\n")

        print(f"  Luego vuelve a ejecutar: python download_Ryr.py")
        print(f"  El script detectará los archivos nuevos automáticamente.\n")

        print(f"  ALTERNATIVA para países muy escasos (Venezuela, Argentina):")
        print(f"  Si Investing.com no tiene suficientes datos, considera:")
        print(f"  - Argentina: FRED IRLTLT01ARQ156N (trimestral desde OCDE)")
        print(f"    o usar el EMBI spread + US Treasury 10Y como proxy.")
        print(f"  - Venezuela: datos post-2017 prácticamente inexistentes;")
        print(f"    considerar excluir del panel o imputar con último valor.")

    print(f"\n{'='*60}")
    print(f"  Completado. CSVs en ./{OUTPUT_DIR}/")
    print(f"  Para países FRED: frecuencia mensual (último día del mes).")
    print(f"  Para países Investing.com: frecuencia diaria.")
    print(f"  Ambos formatos son compatibles con el esquema Chile.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
