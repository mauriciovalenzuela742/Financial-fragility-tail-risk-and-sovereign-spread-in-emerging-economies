"""
extract_russia.py — Inputs JLoss para Rusia (Hito 5).

Fuente: estados IFRS de los bancos cotizados en MOEX + Formulario 101 del Banco de Rusia (CBR)
para la historia profunda (balance de comprobación por cuenta, mensual). Sin API REST estándar:
ensamblar long-format (bank, account, period, value) desde los estados / el Form 101.

CAVEATS DE DISPONIBILIDAD (importantes para el comité):
  - El CBR SUSPENDIÓ la publicación de reportes por banco en 2022 y la REANUDÓ desde mayo de 2023
    (Form 101 balance de comprobación, 123 capital, 135 ratios). => hueco en 2022.
  - Los bancos sancionados (p.ej. Sberbank, VTB) pueden omitir información sensible a sanciones
    (divulgación en forma reducida). => cobertura parcial para esos bancos.
  - La cobertura de precios MOEX (.ME) en yfinance es poco fiable post-2022 => varios bancos caen a
    PD contable (book_pd).
  - Para la historia profunda vía Form 101, los bonos se identifican por PREFIJO de cuenta
    (520 obligaciones, 521-523 certificados/letras emitidas); ese mapeo por código requiere un paso
    adicional y debe confirmarse con el plan de cuentas del CBR.

Criterio del profesor (bonos vs resto): LP = deuda emitida (títulos/bonos + subordinada); CP = resto.

Uso:
    python extract_russia.py --file ./russia_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "russia"

BANKMAP = {
    "sberbank":             {"ticker": "SBER.ME", "names": ["SBERBANK", "SBER"]},
    "vtb":                  {"ticker": "VTBR.ME", "names": ["VTB"]},
    "bank_saint_petersburg":{"ticker": "BSPB.ME", "names": ["BANK SAINT PETERSBURG", "SAINT-PETERSBURG"]},
    "tinkoff":              {"ticker": "TCSG.ME", "names": ["TINKOFF", "TCS", "T-BANK"]},
    "sovcombank":           {"ticker": "SVCB.ME", "names": ["SOVCOMBANK"]},
    "moscow_credit_bank":   {"ticker": "CBOM.ME", "names": ["MOSCOW CREDIT BANK", "CREDIT BANK OF MOSCOW"]},
    "gazprombank":          {"ticker": None,      "names": ["GAZPROMBANK"]},   # no listado -> book PD
    "alfa_bank":            {"ticker": None,      "names": ["ALFA-BANK", "ALFA BANK"]},  # no listado
}

# Por NOMBRE (estados IFRS). Para Form 101, mapear por prefijo de cuenta 520-523 (ver caveats).
ACCOUNT_MAP = {
    "bonds": ["DEBT SECURITIES ISSUED", "BONDS ISSUED", "BONDS", "SUBORDINATED",
              "DEBT SECURITIES IN ISSUE", "520", "521", "522", "523"],
    "tot_asset": ["TOTAL ASSETS"],
    "equity": ["TOTAL EQUITY", "TOTAL SHAREHOLDERS' EQUITY", "EQUITY ATTRIBUTABLE"],
}
FORM101_BOND_PREFIXES = ("520", "521", "522", "523")   # obligaciones / certificados / letras emitidas


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
    print("NOTA: hueco 2022 (CBR) y divulgación reducida para sancionados; revisar cobertura.")


if __name__ == "__main__":
    main()
