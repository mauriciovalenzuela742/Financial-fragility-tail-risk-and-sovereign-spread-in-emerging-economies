"""
extract_poland.py — Inputs JLoss para Poland (Hito 4).

Fuente: NBP/KNF (datos del sector) + estados IFRS de los bancos cotizados en GPW (WSE). Sin API REST por banco: ensamblar long-format desde KNF/NBP o los estados de los bancos.
Precios: yfinance (.WA (GPW)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.

ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_poland.py --file ./poland_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "poland"

BANKMAP = {
    "pko_bp": {"ticker": "PKO.WA", "names": ['PKO', 'POWSZECHNA KASA']},
    "pekao": {"ticker": "PEO.WA", "names": ['PEKAO']},
    "santander_polska": {"ticker": "SPL.WA", "names": ['SANTANDER']},
    "mbank": {"ticker": "MBK.WA", "names": ['MBANK', 'BRE BANK']},
    "ing_bsk": {"ticker": "ING.WA", "names": ['ING']},
    "millennium": {"ticker": "MIL.WA", "names": ['MILLENNIUM']},
    "alior": {"ticker": "ALR.WA", "names": ['ALIOR']},
    "handlowy": {"ticker": "BHW.WA", "names": ['HANDLOWY', 'CITI HANDLOWY']},
    "bnp_paribas_polska": {"ticker": "BNP.WA", "names": ['BNP PARIBAS']},
    "bos_bank": {"ticker": "BOS.WA", "names": ['BOS BANK', 'OCHRONY SRODOWISKA']},
}

ACCOUNT_MAP = {
    "bonds": ['DEBT SECURITIES ISSUED', 'EMISJI DLUZNYCH', 'DLUZNYCH PAPIEROW', 'SUBORDINATED', 'ZOBOWIAZANIA PODPORZADKOWANE'],
    "tot_asset": ['TOTAL ASSETS', 'AKTYWA RAZEM', 'SUMA AKTYWOW'],
    "equity": ['TOTAL EQUITY', 'KAPITAL WLASNY'],
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
