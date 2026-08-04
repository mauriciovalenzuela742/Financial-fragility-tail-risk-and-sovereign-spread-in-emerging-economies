"""
extract_pakistan.py — Inputs JLoss para Pakistan (Hito 4).

Fuente: SBP 'Financial Statements Analysis of the Financial Sector' (compendio trimestral) + estados de los bancos en PSX. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (PSX); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
\nCobertura de precios via yfinance pobre para PSX: tickers=None -> estos bancos caen a PD contable (book_pd).
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
    "hbl": {"ticker": None, "names": ['HABIB BANK', 'HBL']},
    "mcb": {"ticker": None, "names": ['MCB BANK', 'MUSLIM COMMERCIAL']},
    "ubl": {"ticker": None, "names": ['UNITED BANK', 'UBL']},
    "nbp_pak": {"ticker": None, "names": ['NATIONAL BANK OF PAKISTAN']},
    "abl": {"ticker": None, "names": ['ALLIED BANK', 'ABL']},
    "bafl": {"ticker": None, "names": ['BANK ALFALAH', 'ALFALAH']},
    "meezan": {"ticker": None, "names": ['MEEZAN']},
    "scb_pak": {"ticker": None, "names": ['STANDARD CHARTERED']},
    "bank_al_habib": {"ticker": None, "names": ['BANK AL HABIB', 'AL HABIB']},
    "faysal": {"ticker": None, "names": ['FAYSAL']},
    "askari": {"ticker": None, "names": ['ASKARI']},
    "soneri": {"ticker": None, "names": ['SONERI']},
    "js_bank": {"ticker": None, "names": ['JS BANK']},
    "bop": {"ticker": None, "names": ['BANK OF PUNJAB', 'PUNJAB']},
    "bok": {"ticker": None, "names": ['BANK OF KHYBER', 'KHYBER']},
    "habib_metro": {"ticker": None, "names": ['HABIB METROPOLITAN', 'HABIBMETRO']},
    "bankislami": {"ticker": None, "names": ['BANKISLAMI', 'BANK ISLAMI']},
    "summit": {"ticker": None, "names": ['SUMMIT BANK']},
    "samba_pak": {"ticker": None, "names": ['SAMBA']},
    "sindh_bank": {"ticker": None, "names": ['SINDH BANK']},
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
