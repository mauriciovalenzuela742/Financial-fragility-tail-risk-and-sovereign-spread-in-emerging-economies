"""
extract_bulgaria.py — Inputs JLoss para Bulgaria (Hito 4).

Fuente: BNB (Bulgarian National Bank) + Bolsa de Sofia. Mayoria de bancos son filiales no listadas -> PD contable. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (BSE-Sofia); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
\nMayoria filiales no listadas (UniCredit Bulbank, DSK, UBB, Postbank) -> PD contable; panel historico muy delgado.
ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_bulgaria.py --file ./bulgaria_long.csv --start 2005 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "bulgaria"

BANKMAP = {
    "fibank": {"ticker": "5F4.SF", "names": ['FIRST INVESTMENT BANK', 'FIBANK']},
    "ccb": {"ticker": None, "names": ['CENTRAL COOPERATIVE BANK']},
    "unicredit_bulbank": {"ticker": None, "names": ['UNICREDIT BULBANK']},
    "dsk": {"ticker": None, "names": ['DSK BANK', 'BANKA DSK']},
    "ubb": {"ticker": None, "names": ['UNITED BULGARIAN BANK', 'UBB']},
    "postbank": {"ticker": None, "names": ['POSTBANK', 'EUROBANK BULGARIA']},
}

ACCOUNT_MAP = {
    "bonds": ['DEBT SECURITIES ISSUED', 'SUBORDINATED', 'BONDS', 'ISSUED DEBT'],
    "tot_asset": ['TOTAL ASSETS'],
    "equity": ['TOTAL EQUITY', "SHAREHOLDERS' EQUITY"],
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
    ap.add_argument("--start", type=int, default=2005)
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
