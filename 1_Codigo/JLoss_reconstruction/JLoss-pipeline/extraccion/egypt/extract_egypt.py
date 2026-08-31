"""
extract_egypt.py — Inputs JLoss para Egypt (Hito 5).

Fuente: CBE (agregado) + estados de los bancos cotizados en EGX. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (.CA (EGX)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.
DECISION DEL COMITE (ago-2026): no se usa PD contable. Los 9 bancos de BANKMAP ya tienen ticker
de mercado; National Bank of Egypt y Banque Misr (los dos mas grandes del sistema) son estatales
y no cotizan -> quedan fuera del universo, no hay PD contable de respaldo para ellos.
ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta y correr reconcile_bonds_vs_rest.

Uso:
    python extract_egypt.py --file ./egypt_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "egypt"

BANKMAP = {
    "cib": {"ticker": "COMI.CA", "names": ['COMMERCIAL INTERNATIONAL BANK', 'CIB']},
    "qnb_alahli": {"ticker": "QNBA.CA", "names": ['QNB ALAHLI', 'QNB AL AHLI']},
    "credit_agricole_egypt": {"ticker": "CIEB.CA", "names": ['CREDIT AGRICOLE EGYPT']},
    "hdb": {"ticker": "HDBK.CA", "names": ['HOUSING AND DEVELOPMENT BANK', 'HOUSING & DEVELOPMENT']},
    "faisal_islamic": {"ticker": "FAIT.CA", "names": ['FAISAL ISLAMIC']},
    "adib_egypt": {"ticker": "ADIB.CA", "names": ['ABU DHABI ISLAMIC']},
    "export_development": {"ticker": "EXPA.CA", "names": ['EXPORT DEVELOPMENT']},
    "suez_canal_bank": {"ticker": "CANA.CA", "names": ['SUEZ CANAL BANK']},
    "al_baraka_egypt": {"ticker": "SAUD.CA", "names": ['AL BARAKA', 'ALBARAKA']},
}

ACCOUNT_MAP = {
    "bonds": ['BONDS', 'DEBT SECURITIES ISSUED', 'SUBORDINATED', 'LONG TERM LOANS'],
    "tot_asset": ['TOTAL ASSETS'],
    "equity": ['TOTAL EQUITY', "TOTAL SHAREHOLDERS' EQUITY"],
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
