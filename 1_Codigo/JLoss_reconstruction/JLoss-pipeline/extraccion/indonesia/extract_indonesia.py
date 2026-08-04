"""
extract_indonesia.py — Inputs JLoss para Indonesia (Hito 4).

Fuente: OJK 'Statistik Perbankan Indonesia' + estados de los bancos cotizados en IDX. Sin API REST por banco: ensamblar long-format.
Precios: yfinance (.JK (IDX)); solo bancos listados.
Criterio del profesor (bonos vs resto): LP = deuda emitida (titulos/bonos + subordinada); CP = resto.

ESTADO: configuracion delgada sobre jloss_common (long-format -> bonos-vs-resto). CONFIRMAR en
runtime los nombres de cuenta del estado financiero / regulador y correr reconcile_bonds_vs_rest.

Uso:
    python extract_indonesia.py --file ./indonesia_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "indonesia"

BANKMAP = {
    "bca": {"ticker": "BBCA.JK", "names": ['BANK CENTRAL ASIA', 'BCA']},
    "bri": {"ticker": "BBRI.JK", "names": ['RAKYAT INDONESIA', 'BRI']},
    "mandiri": {"ticker": "BMRI.JK", "names": ['MANDIRI']},
    "bni": {"ticker": "BBNI.JK", "names": ['NEGARA INDONESIA', 'BNI']},
    "bsi": {"ticker": "BRIS.JK", "names": ['SYARIAH INDONESIA']},
    "cimb_niaga": {"ticker": "BNGA.JK", "names": ['CIMB NIAGA']},
    "ocbc_nisp": {"ticker": "NISP.JK", "names": ['OCBC NISP']},
    "btn": {"ticker": "BBTN.JK", "names": ['TABUNGAN NEGARA', 'BTN']},
    "danamon": {"ticker": "BDMN.JK", "names": ['DANAMON']},
    "jago": {"ticker": "ARTO.JK", "names": ['BANK JAGO', 'JAGO']},
    "btpn_syariah": {"ticker": "BTPS.JK", "names": ['BTPN SYARIAH']},
    "bjb": {"ticker": "BJBR.JK", "names": ['JAWA BARAT', 'BJB']},
    "bjtim": {"ticker": "BJTM.JK", "names": ['JAWA TIMUR']},
    "panin": {"ticker": "PNBN.JK", "names": ['PAN INDONESIA', 'PANIN']},
    "mega": {"ticker": "MEGA.JK", "names": ['BANK MEGA']},
    "permata": {"ticker": "BNLI.JK", "names": ['PERMATA']},
    "maybank_indonesia": {"ticker": "BNII.JK", "names": ['MAYBANK INDONESIA', 'BANK INTERNASIONAL INDONESIA']},
    "btpn": {"ticker": "BTPN.JK", "names": ['BTPN']},
    "bukopin": {"ticker": "BBKP.JK", "names": ['BUKOPIN', 'KB BUKOPIN']},
    "woori_saudara": {"ticker": "SDRA.JK", "names": ['WOORI SAUDARA', 'BANK SAUDARA']},
    "mayapada": {"ticker": "MAYA.JK", "names": ['MAYAPADA']},
    "victoria": {"ticker": "BVIC.JK", "names": ['BANK VICTORIA']},
    "artha_graha": {"ticker": "INPC.JK", "names": ['ARTHA GRAHA']},
}

ACCOUNT_MAP = {
    "bonds": ['SURAT BERHARGA YANG DITERBITKAN', 'SECURITIES ISSUED', 'OBLIGASI', 'BONDS', 'PINJAMAN SUBORDINASI', 'SUBORDINATED'],
    "tot_asset": ['TOTAL ASET', 'TOTAL ASSETS', 'JUMLAH ASET'],
    "equity": ['TOTAL EKUITAS', 'TOTAL EQUITY', 'JUMLAH EKUITAS'],
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
