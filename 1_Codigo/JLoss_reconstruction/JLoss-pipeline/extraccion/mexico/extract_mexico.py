"""
extract_mexico.py — Inputs JLoss para Mexico desde el Portafolio de Informacion de la CNBV.

Fuente balances: CNBV Portafolio de Informacion (portafolioinfo.cnbv.gob.mx), seccion
"Consultas y Exportacion". Entrega CSV/Excel de Balance General de Banca Multiple por periodo
(reporte R04 / "Principales Rubros del Balance General"). NO hay API REST documentada: se
exporta desde el portal o se descargan los archivos del portafolio (long o wide).
Fuente precios: yfinance, sufijo .MX (BMV). Solo bancos listados (pocos; varios son filiales
no listadas en Mexico -> cobertura parcial via matriz extranjera).

DECISION DEL COMITE (ago-2026): no se usa PD contable. BBVA Mexico, Banamex, Santander Mexico,
HSBC Mexico y Scotiabank Mexico (filiales sin ticker propio en BMV) quedan FUERA del universo.

ESTADO: scaffold. Asume export long-format (entidad, concepto, periodo, saldo).
CONFIRMAR nombres de columna/concepto del export vigente antes de la corrida masiva.

Uso:
    python extract_mexico.py --file ./cnbv_export.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "mexico"

# bankname_panel : {ticker .MX o matriz, clave CNBV, nombres (substring)}
BANKMAP = {
    "banorte":         {"ticker": "GFNORTEO.MX", "cnbv": "072", "names": ["BANORTE"]},
    "inbursa":         {"ticker": "GFINBURO.MX", "cnbv": "036", "names": ["INBURSA"]},
    "banco_bajio":     {"ticker": "BBAJIOO.MX",  "cnbv": "030", "names": ["BAJIO"]},
    "banregio":        {"ticker": "GFREGIO.MX",  "cnbv": "058", "names": ["BANREGIO", "REGIONAL DE MONTERREY"]},
}

# Conceptos del Balance General CNBV -> campos v8 (substring, mayusculas). CONFIRMAR.
CONCEPT_MAP = {
    "bonds": ["TITULOS DE CREDITO EMITIDOS", "OBLIGACIONES SUBORDINADAS"],
    "tot_asset": ["TOTAL ACTIVO", "ACTIVO TOTAL"],
    "equity":    ["CAPITAL CONTABLE", "TOTAL CAPITAL CONTABLE"],
}


def _classify(concept):
    c = str(concept).upper()
    for field, keys in CONCEPT_MAP.items():
        if any(k in c for k in keys):
            return field
    return None


def _match_bank(entidad):
    u = str(entidad).upper()
    for bankname, meta in BANKMAP.items():
        if any(n in u for n in meta["names"]):
            return bankname
    return None


def _parse_period(p):
    s = str(p).strip()
    for fmt in ("%Y%m", "%Y-%m", "%Y/%m"):
        try:
            return pd.to_datetime(s, format=fmt).replace(day=1)
        except ValueError:
            continue
    return pd.to_datetime(s).normalize().replace(day=1)


def transform_cnbv(df, col_entidad="entidad", col_concepto="concepto",
                   col_periodo="periodo", col_saldo="saldo"):
    """Export long-format CNBV -> filas v8, agregando por banco-periodo."""
    acc = {}
    for _, rec in df.iterrows():
        bankname = _match_bank(rec.get(col_entidad, ""))
        if bankname is None:
            continue
        bankname = jc.canonical_bankname(bankname)   # unifica variantes/typos CNBV
        field = _classify(rec.get(col_concepto, ""))
        if field is None:
            continue
        val = jc.to_float_latam(rec.get(col_saldo))
        if np.isnan(val):
            continue
        date = _parse_period(rec.get(col_periodo))
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


def fetch_balances(export_file, start_year, end_year):
    df = pd.read_csv(export_file) if export_file.endswith(".csv") else pd.read_excel(export_file)
    df.columns = [str(c).strip().lower() for c in df.columns]
    rows = transform_cnbv(df)
    bal = jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(rows))
    return bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="export CNBV (csv/xlsx) descargado del portafolio")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = fetch_balances(a.file, a.start, a.end)
    bal.to_csv("balance_mexico.csv", index=False)
    jc.coverage_report(bal).to_csv("coverage_mexico.csv", index=False)
    mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
    mkt.to_csv("mktcap_mexico.csv", index=False)
    print(f"balances {len(bal)} | mktcap {len(mkt)} | bancos {bal['bankname'].nunique()}")


if __name__ == "__main__":
    main()