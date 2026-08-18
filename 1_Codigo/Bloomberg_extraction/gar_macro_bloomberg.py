"""
gar_macro_bloomberg.py — variables macro/globales y de regresion por pais (runbook §1
y §3) para los 12 paises de Fase 1, via Bloomberg.

NO repite lo que ya existe: los CSV CPI_<PAIS>.csv / GDP_<PAIS>.csv / STX_<PAIS>.csv /
Ryr_<PAIS>.csv / rEER_<PAIS>.csv de 1_Codigo/GaR/individuals/<PAIS>/ ya vienen de fuentes
gratuitas (ver reference/GaR_extraction_individuals/*.py) — antes de correr este script,
auditar si esos archivos ya estan vigentes para el pais que te interesa; este script solo
cubre lo que el runbook marca como exclusivamente Bloomberg (o sin fuente gratuita clara):
  - Spread EMBI / CDS soberano 5Y (pais)
  - Rating S&P (pais, convertido a escala 21-1 con RATING_SCALE)
  - Volatilidad cambiaria trimestral (pais, calculada de USD<CCY> Curncy)
  - VIX, UST 10Y, HY spread (global, una sola vez)
  - Margen de utilidad del sistema bancario (pais) — se calcula aparte, de los mismos
    bancos ya extraidos por extract_jloss_bloomberg.py (ver compute_country_prof_margin).

CORRE FUERA DEL SANDBOX DEL AGENTE — ejecutar en PyCharm con el Bloomberg Terminal abierto.

Uso:
    python gar_macro_bloomberg.py --global-only
    python gar_macro_bloomberg.py --country turkey
    python gar_macro_bloomberg.py                      # todos los paises de Fase 1 + global
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

import bloomberg_common as bc
from banks_bloomberg import BANKS, CDS_ISSUER_NAME, COUNTRY_INDEX, EXECUTION_ORDER, GLOBAL_TICKERS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_macro")
DEFAULT_START = "2010-01-01"


def fetch_global(start_date: str, end_date: str):
    """VIX, UST10Y: series diarias, formato DATES,<var> (mismo esquema que STX/Ryr)."""
    out_dir = os.path.join(OUTPUT_DIR, "GLOBAL")
    os.makedirs(out_dir, exist_ok=True)

    for name, ticker in [("VIX", GLOBAL_TICKERS["vix"]), ("UST10Y", GLOBAL_TICKERS["ust10y"])]:
        res = bc.bdh_pull(ticker, ["PX_LAST"], start_date, end_date, freq="D")
        df = res.get(ticker)
        if df is None or df.empty:
            print(f"[GLOBAL] sin datos para {ticker}")
            continue
        df = df.copy()
        df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
        df = df.reset_index().rename(columns={df.columns[0]: "date"})
        bc.write_dates_series_csv(df, "date", "PX_LAST", os.path.join(out_dir, f"{name}.csv"), name)

    # HY spread: campo marcado "verificar" en el runbook — confirmar con FLDS antes de usar
    hy_ticker = GLOBAL_TICKERS["hy_spread"]
    bc.verify_fields(hy_ticker, ["PX_LAST"])
    res = bc.bdh_pull(hy_ticker, ["PX_LAST"], start_date, end_date, freq="D")
    df = res.get(hy_ticker)
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
        df = df.reset_index().rename(columns={df.columns[0]: "date"})
        bc.write_dates_series_csv(df, "date", "PX_LAST", os.path.join(out_dir, "HY_SPREAD.csv"), "HY_SPREAD")
    else:
        print(f"[GLOBAL] AVISO: sin datos para HY spread ({hy_ticker}) — usar sustituto "
              f"FRED BAMLH0A0HYM2 ya usado en el repo, o confirmar mnemonico via FLDS<GO>.")


def fetch_country_embi_rating_fxvol(country: str, start_date: str, end_date: str):
    """EMBI/CDS, rating S&P y volatilidad cambiaria — solo lo que el runbook marca como
    variables de pais no cubiertas por las fuentes gratuitas ya existentes."""
    idx = COUNTRY_INDEX.get(country)
    if not idx:
        print(f"[{country}] no esta en COUNTRY_INDEX — se omite.")
        return
    out_dir = os.path.join(OUTPUT_DIR, country)
    os.makedirs(out_dir, exist_ok=True)

    # --- CDS soberano 5Y como sustituto de EMBI (mnemonico exacto a confirmar en SECF) ---
    # Usa el nombre corto del EMISOR (convencion Bloomberg/Markit), no el codigo de moneda.
    cds_name = CDS_ISSUER_NAME.get(country)
    cds_ticker = f"{cds_name} CDS USD SR 5Y Corp" if cds_name else None
    df = None
    if cds_ticker is None:
        print(f"[{country}] sin nombre de emisor CDS definido en CDS_ISSUER_NAME — se omite EMBI/CDS "
              f"(se sigue con rating y volatilidad cambiaria).")
    else:
        bc.verify_fields(cds_ticker, ["PX_LAST"])
        res = bc.bdh_pull(cds_ticker, ["PX_LAST"], start_date, end_date, freq="D")
        df = res.get(cds_ticker)
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
        df = df.reset_index().rename(columns={df.columns[0]: "date"})
        bc.write_dates_series_csv(df, "date", "PX_LAST", os.path.join(out_dir, f"EMBI_{country}.csv"), "EMBI")
    elif cds_ticker is not None:
        print(f"[{country}] sin datos de CDS/EMBI ({cds_ticker}) — verificar ticker en el terminal.")

    # --- Rating S&P: BDP sobre el generico soberano, campo a confirmar con FLDS ---
    sov_ticker = idx.get("sov10y")
    if sov_ticker:
        bc.verify_fields(sov_ticker, ["RTG_SP_LT_FC_ISSUER_RATING"])
        rt = bc.bdp_pull(sov_ticker, ["RTG_SP_LT_FC_ISSUER_RATING"])
        if not rt.empty and "RTG_SP_LT_FC_ISSUER_RATING" in rt.columns:
            notch = rt["RTG_SP_LT_FC_ISSUER_RATING"].iloc[0]
            score = bc.RATING_SCALE.get(str(notch).strip().upper())
            pd.DataFrame([{"notch": notch, "rating_score": score}]).to_csv(
                os.path.join(out_dir, f"rating_{country}.csv"), index=False)
            print(f"[{country}] rating S&P = {notch} -> {score}")
        else:
            print(f"[{country}] sin rating S&P disponible para {sov_ticker} — confirmar campo/licencia.")
    else:
        print(f"[{country}] sin bono soberano 10Y generico definido — {idx.get('sov_note', '')}")

    # --- Volatilidad cambiaria trimestral ---
    fxvol = bc.daily_fx_vol_quarterly(idx["fx"], start_date, end_date)
    if not fxvol.empty:
        fxvol.to_csv(os.path.join(out_dir, f"fxvol_{country}.csv"), index=False)
        print(f"[{country}] volatilidad cambiaria: {len(fxvol)} trimestres")


def compute_country_prof_margin(country: str, jloss_output_dir: str):
    """Margen de utilidad agregado del sistema = net_income / net_rev agregados,
    tomado del balance_<pais>.csv ya escrito por extract_jloss_bloomberg.py
    (no se pide aparte a Bloomberg, per runbook §1)."""
    balance_path = os.path.join(jloss_output_dir, country, f"balance_{country}.csv")
    if not os.path.exists(balance_path):
        print(f"[{country}] balance_{country}.csv no existe todavia — correr "
              f"extract_jloss_bloomberg.py primero para poder calcular el margen agregado.")
        return
    df = pd.read_csv(balance_path, parse_dates=["date"])
    df["quarter"] = df["date"].dt.to_period("Q")
    g = df.groupby("quarter").agg(net_income=("net_income", "sum"), net_rev=("net_rev", "sum"))
    with np.errstate(divide="ignore", invalid="ignore"):
        g["prof_margin_system"] = g["net_income"] / g["net_rev"]
    out_dir = os.path.join(OUTPUT_DIR, country)
    os.makedirs(out_dir, exist_ok=True)
    g.reset_index().to_csv(os.path.join(out_dir, f"prof_margin_{country}.csv"), index=False)
    print(f"[{country}] margen de utilidad del sistema: {len(g)} trimestres")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--country", default=None)
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument("--global-only", action="store_true")
    ap.add_argument("--jloss-output-dir",
                     default=os.path.join(os.path.dirname(__file__), "output"),
                     help="Carpeta output/ de extract_jloss_bloomberg.py (para el margen agregado).")
    args = ap.parse_args()

    fetch_global(args.start, args.end)
    if args.global_only:
        return

    countries = [args.country] if args.country else EXECUTION_ORDER
    for country in countries:
        print(f"\n{'='*70}\n{country.upper()} — variables macro\n{'='*70}")
        fetch_country_embi_rating_fxvol(country, args.start, args.end)
        compute_country_prof_margin(country, args.jloss_output_dir)


if __name__ == "__main__":
    main()
