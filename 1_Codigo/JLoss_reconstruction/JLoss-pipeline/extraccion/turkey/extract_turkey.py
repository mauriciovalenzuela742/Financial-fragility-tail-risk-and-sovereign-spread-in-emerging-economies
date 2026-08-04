"""
extract_turkey.py — Inputs JLoss para Turquía desde la Asociación de Bancos de Turquía (TBB).

Fuente balances: TBB (tbb.org.tr) — "Statistical Reports" / "Data Query System". Estados
financieros por banco, trimestrales, descargables (Excel/consulta). NO hay API REST: descarga
por período. Sigue el plan único de cuentas de la BDDK.
Fuente precios: yfinance, sufijo .IS (BIST). Solo bancos listados.

Criterio del profesor (bonos vs resto): LP = títulos emitidos + deuda subordinada; CP = resto.

ESTADO: scaffold. Asume export long-format (banco, cuenta, período, valor) tras la descarga.
CONFIRMAR nombres de cuenta del estado financiero TBB vigente (TR/EN) antes de la corrida masiva.

Uso:
    python extract_turkey.py --file ./tbb_export.csv --start 2002 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "turkey"

# bankname_panel : {ticker .IS, nombres TBB (substring, mayúsculas, TR/EN)}
BANKMAP = {
    "akbank": {"ticker": "AKBNK.IS", "names": ['AKBANK']},
    "garanti_bbva": {"ticker": "GARAN.IS", "names": ['GARANTI', 'GARANTİ']},
    "isbank": {"ticker": "ISCTR.IS", "names": ['IS BANKASI', 'İŞ BANKASI', 'ISBANK', 'TURKIYE IS BANKASI']},
    "yapi_kredi": {"ticker": "YKBNK.IS", "names": ['YAPI VE KREDI', 'YAPI KREDI', 'YAPI VE KREDİ']},
    "vakifbank": {"ticker": "VAKBN.IS", "names": ['VAKIFBANK', 'VAKIFLAR BANKASI']},
    "halkbank": {"ticker": "HALKB.IS", "names": ['HALKBANK', 'HALK BANKASI']},
    "tskb": {"ticker": "TSKB.IS", "names": ['TSKB', 'SINAI KALKINMA']},
    "sekerbank": {"ticker": "SKBNK.IS", "names": ['SEKERBANK', 'ŞEKERBANK']},
}

# Cuentas del balance (pasivo) -> campos v8 (substring, mayúsculas; TR/EN). CONFIRMAR.
ACCOUNT_MAP = {
    "bonds": ["SECURITIES ISSUED", "MARKETABLE SECURITIES ISSUED", "IHRAC EDILEN MENKUL",
              "İHRAÇ EDİLEN MENKUL", "MENKUL KIYMET IHRAC", "SUBORDINATED", "SERMAYE BENZERI",
              "SERMAYE BENZERİ"],
    "tot_asset": ["TOTAL ASSETS", "TOPLAM AKTIFLER", "TOPLAM AKTİFLER", "TOPLAM VARLIKLAR"],
    "equity":    ["SHAREHOLDERS' EQUITY", "TOTAL EQUITY", "OZKAYNAKLAR", "ÖZKAYNAKLAR"],
}


def _classify(name):
    c = str(name).upper()
    for field, keys in ACCOUNT_MAP.items():
        if any(k in c for k in keys):
            return field
    return None


def _match_bank(entity):
    u = str(entity).upper()
    for bankname, meta in BANKMAP.items():
        if any(n in u for n in meta["names"]):
            return bankname
    return None


def _parse_period(p):
    s = str(p).strip()
    for fmt in ("%Y%m", "%Y-%m", "%Y/%m", "%Y-%m-%d"):
        try:
            return pd.to_datetime(s, format=fmt).replace(day=1)
        except ValueError:
            continue
    return pd.to_datetime(s).normalize().replace(day=1)


def transform_tbb(df, col_bank="bank", col_account="account", col_period="period", col_value="value"):
    """Export long-format TBB -> filas v8 (bonos-vs-resto), agregando por banco-período."""
    acc = {}
    for _, rec in df.iterrows():
        bankname = _match_bank(rec.get(col_bank, ""))
        if bankname is None:
            continue
        field = _classify(rec.get(col_account, ""))
        if field is None:
            continue
        val = jc.to_float_latam(rec.get(col_value))
        if np.isnan(val):
            continue
        date = _parse_period(rec.get(col_period))
        key = (bankname, date)
        acc.setdefault(key, {})
        # 'bonds' acumula títulos emitidos + subordinada (ambos caen en la lista 'bonds')
        acc[key][field] = acc[key].get(field, 0.0) + val
    rows = []
    for (bankname, date), f in acc.items():
        row = jc.empty_balance_row(COUNTRY, bankname, date)
        row.update({"bonds": f.get("bonds", np.nan),
                    "tot_asset": f.get("tot_asset", np.nan), "equity_book": f.get("equity", np.nan)})
        rows.append(row)
    return rows


def fetch_balances(export_file, start_year, end_year):
    df = pd.read_csv(export_file) if export_file.endswith(".csv") else pd.read_excel(export_file)
    df.columns = [str(c).strip().lower() for c in df.columns]
    bal = jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(transform_tbb(df)))
    return bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="export TBB (csv/xlsx) descargado")
    ap.add_argument("--start", type=int, default=2002)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = fetch_balances(a.file, a.start, a.end)
    bal.to_csv("balance_turkey.csv", index=False)
    jc.coverage_report(bal).to_csv("coverage_turkey.csv", index=False)
    mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
    mkt.to_csv("mktcap_turkey.csv", index=False)
    print(f"balances {len(bal)} | mktcap {len(mkt)} | bancos {bal['bankname'].nunique()}")


if __name__ == "__main__":
    main()
