"""
extract_pakistan.py — Inputs JLoss para Pakistan (Hito 4).

Fuente: SBP 'Financial Statements Analysis of the Financial Sector' (compendio trimestral) + estados de los bancos en PSX. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (PSX); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
DECISION DEL COMITE (ago-2026): no se usa PD contable. Los 19 bancos de abajo SI cotizan en la
PSX (confirmado via Bloomberg, ej. HBL/UBL/MCB/NBP/ABL/BAFL PA Equity) pero yfinance no tiene
cobertura confiable de precios para PSX -> sin market PD utilizable con esta fuente, quedan
FUERA del universo (no se sustituye por PD contable). Si se consigue el precio via Bloomberg u
otra fuente, se reincorporan con su ticker real en vez de None.
ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_pakistan.py --file ./pakistan_long.csv --start 2001 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "pakistan"

BANKMAP = {
    # Sin ticker de precio utilizable (ver nota arriba) -> universo vacio hasta conseguir
    # una fuente de precio distinta de yfinance para PSX. NO se completa con PD contable.
}

ACCOUNT_MAP = {
    "bonds": ['SUBORDINATED', 'TERM FINANCE CERTIFICATES', 'TFC', 'BONDS', 'DEBT SECURITIES'],
    "tot_asset": ['TOTAL ASSETS'],
    "equity": ['TOTAL EQUITY', 'SHARE CAPITAL AND RESERVES', 'NET ASSETS'],
}


def fetch_balances(export_file, start_year, end_year, col_code=None):
    df = pd.read_csv(export_file) if str(export_file).endswith(".csv") else pd.read_excel(export_file)
    df.columns = [str(c).strip().lower() for c in df.columns]
    rows = jc.transform_long_generic(df, BANKMAP, ACCOUNT_MAP, COUNTRY,
                                     col_bank="bank", col_account="account",
                                     col_period="period", col_value="value", col_code=col_code)
    bal = jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(rows))
    return bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="long-format (bank, account, period, value) ensamblado")
    ap.add_argument("--start", type=int, default=2001)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = fetch_balances(a.file, a.start, a.end)
    bal.to_csv(f"balance_{COUNTRY}.csv", index=False)
    jc.coverage_report(bal).to_csv(f"coverage_{COUNTRY}.csv", index=False)
    mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
    mkt.to_csv(f"mktcap_{COUNTRY}.csv", index=False)
    print(f"balances {len(bal)} | mktcap {len(mkt)} | bancos {bal['bankname'].nunique()}")


if __name__ == "__main__":
    main()
