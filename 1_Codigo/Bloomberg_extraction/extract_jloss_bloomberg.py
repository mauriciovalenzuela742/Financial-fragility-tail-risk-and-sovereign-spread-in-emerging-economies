"""
extract_jloss_bloomberg.py — extractor JLoss Fase 1, 100% Bloomberg, para los 12 paises
"extractor listo, sin datos" del runbook (Argentina, China, Egipto, Indonesia, Malasia,
Pakistan, Filipinas, Polonia, Rusia, Sudafrica, Turquia, Bulgaria).

No depende del pipeline JLoss subido al repo (ignorado por instruccion explicita) —
solo reutiliza el contrato de columnas (BALANCE_COLS/MKTCAP_COLS) y la regla LP/CP
(derive_st_lt_bonds_vs_rest) definidos en bloomberg_common.py.

Requisitos:
    pip install xbbg pandas numpy
    Bloomberg Terminal abierto en esta maquina (BBComm activo).
CORRE FUERA DEL SANDBOX DEL AGENTE — ejecutar en PyCharm, en un terminal normal.

Uso:
    python extract_jloss_bloomberg.py                  # todos los paises de Fase 1, en orden
    python extract_jloss_bloomberg.py --country chile   # un solo pais (debe estar en BANKS)
    python extract_jloss_bloomberg.py --start 2015-01-01 --end 2026-06-30
    python extract_jloss_bloomberg.py --verify-only     # solo corre FLDS-check, no tira historial

Salida (una carpeta por pais, junto a este script):
    output/<pais>/balance_<pais>.csv   (BALANCE_COLS)
    output/<pais>/mktcap_<pais>.csv    (MKTCAP_COLS, diario)
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

import bloomberg_common as bc
from banks_bloomberg import BANKS, EXECUTION_ORDER

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
MIN_BANKS = 3          # bancos con dato de mercado minimos por trimestre (igual al motor JLoss)
DEFAULT_START = "2010-01-01"


def compute_prof_margin(balance_df: pd.DataFrame) -> pd.DataFrame:
    """prof_margin = net_income / net_rev por banco-trimestre (no es un campo Bloomberg
    aparte — se calcula de lo que ya se extrajo, igual que indica el runbook §1)."""
    df = balance_df.copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        df["prof_margin"] = df["net_income"] / df["net_rev"]
    df["prof_margin"] = df["prof_margin"].replace([np.inf, -np.inf], np.nan)
    return df


def check_below_min_banks(mktcap_df: pd.DataFrame, min_banks: int = MIN_BANKS) -> pd.DataFrame:
    """Replica el chequeo --check del motor JLoss: marca trimestres con menos de
    MIN_BANKS bancos con precio de mercado."""
    if mktcap_df.empty:
        return pd.DataFrame(columns=["quarter", "n_banks", "below_min_banks"])
    df = mktcap_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["quarter"] = df["date"].dt.to_period("Q")
    g = df.groupby("quarter")["bankname"].nunique().reset_index(name="n_banks")
    g["below_min_banks"] = g["n_banks"] < min_banks
    return g


def run_country(country: str, start_date: str, end_date: str, verify_only: bool = False):
    bankmap = BANKS.get(country)
    if not bankmap:
        print(f"[{country}] no esta definido en banks_bloomberg.BANKS — se omite.")
        return

    print(f"\n{'='*70}\n{country.upper()} — {len(bankmap)} bancos\n{'='*70}")

    # FLDS-check sobre un ticker de muestra antes de tirar el historial completo
    sample_ticker = next(iter(bankmap.values()))["ticker"]
    bc.verify_fields(sample_ticker, ["BS_TOT_ASSET", "TOTAL_EQUITY", "BS_LT_BORROW",
                                      "NET_INCOME", "SALES_REV_TURN", "CUR_MKT_CAP"])
    if verify_only:
        return

    balance_raw = bc.fetch_balance_bloomberg(bankmap, country, start_date, end_date)
    if balance_raw.empty:
        print(f"[{country}] sin datos de balance — revisar tickers/licencia. Se omite el pais.")
        return
    balance = bc.derive_st_lt_bonds_vs_rest(balance_raw)
    balance = compute_prof_margin(balance)
    balance = balance[bc.BALANCE_COLS]  # DP se descarta del CSV, igual que en el repo

    mktcap = bc.fetch_mktcap_bloomberg(bankmap, country, start_date, end_date)

    out_dir = os.path.join(OUTPUT_DIR, country)
    os.makedirs(out_dir, exist_ok=True)
    balance_path = os.path.join(out_dir, f"balance_{country}.csv")
    mktcap_path = os.path.join(out_dir, f"mktcap_{country}.csv")
    balance.to_csv(balance_path, index=False)
    mktcap.to_csv(mktcap_path, index=False)
    print(f"[{country}] escrito {balance_path} ({len(balance)} filas) y "
          f"{mktcap_path} ({len(mktcap)} filas)")

    cov = check_below_min_banks(mktcap)
    if not cov.empty:
        n_below = int(cov["below_min_banks"].sum())
        if n_below:
            print(f"[{country}] AVISO: {n_below}/{len(cov)} trimestres con menos de "
                  f"{MIN_BANKS} bancos con precio de mercado (below_min_banks).")
        else:
            print(f"[{country}] cobertura OK en los {len(cov)} trimestres con dato.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--country", default=None, help="Un solo pais (default: todos, en EXECUTION_ORDER)")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument("--verify-only", action="store_true",
                     help="Solo corre el chequeo FLDS por pais, no tira el historial completo.")
    args = ap.parse_args()

    countries = [args.country] if args.country else EXECUTION_ORDER
    for country in countries:
        run_country(country, args.start, args.end, verify_only=args.verify_only)


if __name__ == "__main__":
    main()
