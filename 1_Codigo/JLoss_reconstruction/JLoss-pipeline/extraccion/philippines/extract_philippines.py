"""
extract_philippines.py — Inputs JLoss para Philippines (Hito 4).

Fuente: BSP 'Published Statement of Condition' + estados de los bancos cotizados en PSE. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (.PS (PSE)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
\nOJO: 'Bills payable' es de CORTO plazo, NO es bono; el mapeo bonds usa solo 'Bonds payable'+subordinada.
ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_philippines.py --file ./philippines_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "philippines"

BANKMAP = {
    "bdo": {"ticker": "BDO.PS", "names": ['BDO', 'BANCO DE ORO']},
    "metrobank": {"ticker": "MBT.PS", "names": ['METROBANK', 'METROPOLITAN BANK']},
    "bpi": {"ticker": "BPI.PS", "names": ['BANK OF THE PHILIPPINE ISLANDS', 'BPI']},
    "pnb": {"ticker": "PNB.PS", "names": ['PHILIPPINE NATIONAL BANK']},
    "security_bank": {"ticker": "SECB.PS", "names": ['SECURITY BANK']},
    "chinabank": {"ticker": "CHIB.PS", "names": ['CHINA BANK', 'CHINABANK']},
    "unionbank": {"ticker": "UBP.PS", "names": ['UNION BANK', 'UNIONBANK']},
    "rcbc": {"ticker": "RCB.PS", "names": ['RCBC', 'RIZAL COMMERCIAL']},
    "aub": {"ticker": "AUB.PS", "names": ['ASIA UNITED BANK']},
    "eastwest": {"ticker": "EW.PS", "names": ['EASTWEST', 'EAST WEST']},
}

ACCOUNT_MAP = {
    "bonds": ['BONDS PAYABLE', 'SUBORDINATED', 'DEBT SECURITIES ISSUED', 'NOTES PAYABLE'],
    "tot_asset": ['TOTAL ASSETS', 'TOTAL RESOURCES'],
    "equity": ['TOTAL EQUITY', 'TOTAL CAPITAL'],
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
    ap.add_argument("--start", type=int, default=2000)
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
