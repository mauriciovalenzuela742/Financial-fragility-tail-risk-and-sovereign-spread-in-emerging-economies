"""
extract_southafrica.py — Inputs JLoss para Sudáfrica desde los retornos BA900 del SARB.

Cadena: zips/CSV mensuales del BA900 -> ba900_parse -> 3 outputs.
Acepta en --dir: zips mensuales (BA900_YYYY-MM-DD_*.zip, un CSV por banco nombrado {code}.csv)
y/o CSV sueltos. El período se lee SIEMPRE del contenido (fila 'Date').

Decisiones (ver QC):
  - Universo núcleo = 6 grandes listados (SBK/FSR/ABG/NED/CPI/INL .JO) -> todos PD de MERCADO.
    Concentran ~90% de los activos del sistema; el resto (sucursales extranjeras, mutual banks)
    es marginal para ΣEAD.
  - Split: bonos-vs-resto (LP = item 68 'Debt securities'; CP = total_liab - LP). La madurez de
    depósitos del BA900 solo llega a '>6 meses' -> sin corte limpio a 1 año; bonos-vs-resto
    mantiene homogeneidad con el resto del panel.
  - Matching por CÓDIGO de institución (estable para los 6 grandes en 2013-2026).
  - net_income no aplica (PD de mercado): columna NaN para paridad de esquema.

Outputs: balance_south_africa.csv, coverage_south_africa.csv, mktcap_south_africa.csv

Uso:
    python extract_southafrica.py --dir ./ba900_raw --start 2008 --end 2026
"""
import argparse, glob, io, os, re, zipfile
import pandas as pd
import ba900_parse as ba

COUNTRY = "south_africa"

BANKMAP = {
    "standard_bank": {"ticker": "SBK.JO", "code": "416061", "names": ["STANDARD BANK OF S A", "STANDARD BANK"]},
    "firstrand":     {"ticker": "FSR.JO", "code": "416053", "names": ["FIRSTRAND", "FIRST RAND"]},
    "absa":          {"ticker": "ABG.JO", "code": "34118",  "names": ["ABSA"]},
    "nedbank":       {"ticker": "NED.JO", "code": "416088", "names": ["NEDBANK"]},
    "capitec":       {"ticker": "CPI.JO", "code": "333107", "names": ["CAPITEC"]},
    "investec":      {"ticker": "INL.JO", "code": "25054",  "names": ["INVESTEC"]},
}
CODE2BANK = {v["code"]: k for k, v in BANKMAP.items()}
TOL = 100.0  # R'000; identidad activo == pasivo + patrimonio (holgura de redondeo)


def _bank_from(code, institution):
    if code in CODE2BANK:
        return CODE2BANK[code]
    u = (institution or "").upper()
    for k, meta in BANKMAP.items():
        if any(n in u for n in meta["names"]):
            return k
    return None


def _row_from_text(text, code, mode):
    date, inst, items, mat = ba.parse_ba900_any(text)
    bank = _bank_from(code, inst)
    if bank is None or date is None:
        return None
    f = ba.extract_fields(items, mat, mode=mode)
    if not f["tot_asset"]:
        return None
    return {"countryname": COUNTRY, "bankname": bank, "pd_source": "market",
            "date": pd.Timestamp(date), "tot_asset": f["tot_asset"],
            "total_liab": f["total_liab"], "equity": f["equity"],
            "st_borrow": f["st_borrow"], "lt_borrow": f["lt_borrow"],
            "net_income": pd.NA}


def _iter_sources(src_dir):
    """Yield (code, text) para cada banco: XML de la API, CSV sueltos y CSV dentro de zips."""
    for z in sorted(glob.glob(os.path.join(src_dir, "*.zip"))):
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                stem = os.path.splitext(os.path.basename(name))[0]
                if not name.lower().endswith(".csv") or stem.upper() == "TOTAL":
                    continue
                m = re.match(r"(\d+)", stem)
                yield (m.group(1) if m else stem, zf.read(name).decode("latin-1"))
    for p in sorted(glob.glob(os.path.join(src_dir, "*.xml")) + glob.glob(os.path.join(src_dir, "*.csv"))):
        stem = os.path.basename(p)
        if stem.upper().startswith("TOTAL"):
            continue
        m = re.match(r"(\d+)", stem)
        with open(p, encoding="latin-1") as fh:
            yield (m.group(1) if m else stem, fh.read())


def build_balance(src_dir, start, end, mode="bonds"):
    rows = []
    for code, text in _iter_sources(src_dir):
        if code not in CODE2BANK:
            continue  # solo núcleo (evita parsear ~30 bancos chicos por mes)
        r = _row_from_text(text, code, mode)
        if r:
            rows.append(r)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).drop_duplicates(["bankname", "date"], keep="last")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df = df[(df["year"] >= start) & (df["year"] <= end)]
    df["id_fail"] = (df["tot_asset"] - (df["total_liab"] + df["equity"])).abs() > TOL
    cols = ["countryname", "bankname", "pd_source", "date", "year", "month",
            "tot_asset", "total_liab", "equity", "st_borrow", "lt_borrow", "net_income", "id_fail"]
    return df[cols].sort_values(["bankname", "date"]).reset_index(drop=True)


def coverage_report(b):
    if b.empty:
        return pd.DataFrame()
    return (b.groupby(["bankname", "pd_source"])
              .agg(n_periodos=("date", "nunique"), desde=("date", "min"),
                   hasta=("date", "max"), id_fails=("id_fail", "sum"))
              .reset_index().sort_values("desde"))


def fetch_mktcap(start, end):
    schema = ["bankname", "countryname", "date", "mktcap"]
    try:
        import yfinance as yf
    except ImportError:
        print("  [WARN] yfinance no instalado; mktcap vacío."); return pd.DataFrame(columns=schema)
    rows = []
    for key, meta in BANKMAP.items():
        tk = meta["ticker"]
        try:
            t = yf.Ticker(tk)
            px = t.history(start=f"{start}-01-01", end=f"{end}-12-31")["Close"]
            sh = t.get_shares_full(start=f"{start}-01-01")
            if px.empty or sh is None or sh.empty:
                continue
            sh = sh[~sh.index.duplicated(keep="last")]
            m = px.to_frame("px").join(sh.rename("sh").reindex(px.index, method="ffill")).dropna()
            m["mktcap"] = m["px"] * m["sh"]   # ZAR (acciones); balance en R'000 -> escalar en el motor
            rows += [{"bankname": key, "countryname": COUNTRY, "date": d.date(),
                      "mktcap": float(v)} for d, v in m["mktcap"].items()]
        except Exception as e:
            print(f"  [WARN] mktcap {key} ({tk}): {e}")
    return pd.DataFrame(rows, columns=schema)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="./ba900_raw")
    ap.add_argument("--start", type=int, default=2008)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--mode", default="bonds", choices=["bonds", "maturity"])
    a = ap.parse_args()
    bal = build_balance(a.dir, a.start, a.end, mode=a.mode)
    bal.to_csv(f"balance_{COUNTRY}.csv", index=False)
    cov = coverage_report(bal); cov.to_csv(f"coverage_{COUNTRY}.csv", index=False)
    mkt = fetch_mktcap(a.start, a.end); mkt.to_csv(f"mktcap_{COUNTRY}.csv", index=False)
    nf = int(bal["id_fail"].sum()) if not bal.empty else 0
    print(f"balance {len(bal)} | bancos {bal['bankname'].nunique() if not bal.empty else 0} "
          f"| id_fails {nf} | coverage {len(cov)} | mktcap {len(mkt)}")


if __name__ == "__main__":
    main()