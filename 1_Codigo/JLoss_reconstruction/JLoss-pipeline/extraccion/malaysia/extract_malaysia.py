"""
extract_malaysia.py — Inputs JLoss para Malaysia (Hito 4).

Fuente: BNM (boletin estadistico) + estados de los bancos cotizados en Bursa Malaysia. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (.KL (Bursa)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.

ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_malaysia.py --file ./malaysia_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "malaysia"

BANKMAP = {
    "maybank": {"ticker": "1155.KL", "names": ['MAYBANK', 'MALAYAN BANKING']},
    "cimb": {"ticker": "1023.KL", "names": ['CIMB']},
    "public_bank": {"ticker": "1295.KL", "names": ['PUBLIC BANK']},
    "rhb": {"ticker": "1066.KL", "names": ['RHB']},
    "hong_leong": {"ticker": "5819.KL", "names": ['HONG LEONG']},
    "ambank": {"ticker": "1015.KL", "names": ['AMMB', 'AMBANK']},
    "alliance": {"ticker": "2488.KL", "names": ['ALLIANCE']},
    "affin": {"ticker": "5185.KL", "names": ['AFFIN']},
}

ACCOUNT_MAP = {
    "bonds": ['DEBT SECURITIES ISSUED', 'SUBORDINATED', 'RECOURSE OBLIGATIONS', 'BONDS', 'SUKUK', 'MEDIUM TERM NOTES'],
    "tot_asset": ['TOTAL ASSETS'],
    "equity": ['TOTAL EQUITY', "SHAREHOLDERS' EQUITY", 'SHAREHOLDERS FUNDS'],
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
