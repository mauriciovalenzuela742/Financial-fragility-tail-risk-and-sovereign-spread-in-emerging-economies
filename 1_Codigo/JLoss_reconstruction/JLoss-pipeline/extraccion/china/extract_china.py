"""
extract_china.py — Inputs JLoss para China (Hito 5).

Fuente: NFRA/PBoC (agregado) + estados IFRS/CAS de los grandes bancos cotizados en HKEX/SSE. Sin API REST por banco: ensamblar long-format desde los estados de los bancos.
Precios: yfinance (.HK (HKEX) / .SS (SSE)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
\nChina es factible por la via de cotizados (Big Four + joint-stock con estados completos).
ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta y correr reconcile_bonds_vs_rest.

Uso:
    python extract_china.py --file ./china_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "china"

BANKMAP = {
    "icbc": {"ticker": "1398.HK", "names": ['INDUSTRIAL AND COMMERCIAL BANK', 'ICBC']},
    "ccb": {"ticker": "0939.HK", "names": ['CHINA CONSTRUCTION BANK']},
    "abc": {"ticker": "1288.HK", "names": ['AGRICULTURAL BANK OF CHINA']},
    "boc": {"ticker": "3988.HK", "names": ['BANK OF CHINA']},
    "bocom": {"ticker": "3328.HK", "names": ['BANK OF COMMUNICATIONS']},
    "cmb": {"ticker": "3968.HK", "names": ['CHINA MERCHANTS BANK']},
    "citic": {"ticker": "0998.HK", "names": ['CHINA CITIC BANK', 'CITIC BANK']},
    "minsheng": {"ticker": "1988.HK", "names": ['MINSHENG']},
    "psbc": {"ticker": "1658.HK", "names": ['POSTAL SAVINGS BANK']},
    "china_everbright": {"ticker": "6818.HK", "names": ['EVERBRIGHT']},
    "industrial_bank": {"ticker": "601166.SS", "names": ['INDUSTRIAL BANK CO']},
    "spdb": {"ticker": "600000.SS", "names": ['SHANGHAI PUDONG', 'SPD BANK']},
    "ping_an_bank": {"ticker": "000001.SZ", "names": ['PING AN BANK']},
}

ACCOUNT_MAP = {
    "bonds": ['DEBT SECURITIES ISSUED', 'BONDS PAYABLE', 'SUBORDINATED', 'CERTIFICATES OF DEPOSIT ISSUED'],
    "tot_asset": ['TOTAL ASSETS'],
    "equity": ['TOTAL EQUITY', "TOTAL SHAREHOLDERS' EQUITY", 'EQUITY ATTRIBUTABLE'],
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
