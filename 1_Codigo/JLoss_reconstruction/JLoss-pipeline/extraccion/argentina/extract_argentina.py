"""
extract_argentina.py — Inputs JLoss para Argentina desde el BCRA.

Fuente balances: BCRA "Información de Entidades Financieras" — datos abiertos en archivo .7z con
.txt por entidad/período (estados contables), más páginas por entidad. NO hay API REST: descarga
del .7z y parseo de los .txt (el .7z incluye un PDF con el diseño de registro). Plan de cuentas BCRA.
Fuente precios: yfinance, sufijo .BA (BYMA) o ADR. Solo bancos listados.

Criterio del profesor (bonos vs resto): LP = obligaciones negociables + obligaciones subordinadas;
CP = resto.

DECISIÓN DEL COMITÉ (ago-2026): no se usa PD contable. Santander Argentina y Banco Nación (sin
ticker) quedan FUERA del universo.

ESTADO: scaffold. Asume que los .txt se han parseado a long-format (entidad, cuenta, período, valor).
CONFIRMAR los códigos/nombres de cuenta del diseño de registro BCRA antes de la corrida masiva.

Uso:
    python extract_argentina.py --file ./bcra_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "argentina"

# bankname_panel : {ticker .BA / ADR, código BCRA, nombres (substring, mayúsculas)}
BANKMAP = {
    "banco_galicia":     {"ticker": "GGAL.BA", "bcra": "00007", "names": ["GALICIA"]},
    "banco_macro":       {"ticker": "BMA.BA",  "bcra": "00285", "names": ["MACRO"]},
    "bbva_argentina":    {"ticker": "BBAR.BA", "bcra": "00017", "names": ["BBVA", "FRANCES", "FRANCÉS"]},
    "banco_supervielle": {"ticker": "SUPV.BA", "bcra": "00027", "names": ["SUPERVIELLE"]},
}

# Cuentas del estado contable BCRA -> campos v8 (substring, mayúsculas). CONFIRMAR.
ACCOUNT_MAP = {
    "bonds": ["OBLIGACIONES NEGOCIABLES", "OBLIGACIONES SUBORDINADAS", "TITULOS DE DEUDA",
              "TÍTULOS DE DEUDA"],
    "tot_asset": ["TOTAL ACTIVO", "TOTAL DEL ACTIVO", "ACTIVO TOTAL"],
    "equity":    ["PATRIMONIO NETO", "TOTAL PATRIMONIO NETO"],
}


def _classify(name):
    c = str(name).upper()
    for field, keys in ACCOUNT_MAP.items():
        if any(k in c for k in keys):
            return field
    return None


def _match_bank(entity, code=None):
    if code is not None:
        for bankname, meta in BANKMAP.items():
            if str(code).zfill(5) == meta.get("bcra"):
                return bankname
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


def transform_bcra(df, col_entity="entidad", col_account="cuenta", col_period="periodo",
                   col_value="valor", col_code="codigo"):
    """Long-format BCRA -> filas v8 (bonos-vs-resto), agregando por banco-período."""
    acc = {}
    for _, rec in df.iterrows():
        bankname = _match_bank(rec.get(col_entity, ""), rec.get(col_code))
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
        acc[key][field] = acc[key].get(field, 0.0) + val
    rows = []
    for (bankname, date), f in acc.items():
        row = jc.empty_balance_row(COUNTRY, bankname, date)
        row.update({"bonds": f.get("bonds", np.nan),
                    "tot_asset": f.get("tot_asset", np.nan), "equity_book": f.get("equity", np.nan)})
        rows.append(row)
    return rows


def fetch_balances(long_file, start_year, end_year):
    df = pd.read_csv(long_file) if long_file.endswith(".csv") else pd.read_excel(long_file)
    df.columns = [str(c).strip().lower() for c in df.columns]
    bal = jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(transform_bcra(df)))
    return bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="long-format parseado de los .txt del .7z BCRA")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = fetch_balances(a.file, a.start, a.end)
    bal.to_csv("balance_argentina.csv", index=False)
    jc.coverage_report(bal).to_csv("coverage_argentina.csv", index=False)
    mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
    mkt.to_csv("mktcap_argentina.csv", index=False)
    print(f"balances {len(bal)} | mktcap {len(mkt)} | bancos {bal['bankname'].nunique()}")


if __name__ == "__main__":
    main()
