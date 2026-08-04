"""
extract_panama.py — Inputs JLoss para Panamá (SBP).

Cadena: download_sbp.py -> archivos crudos por banco -> sbp_parse -> 3 outputs.
Acepta dos nomenclaturas en --raw:
  balance_{key}_{año}.xlsx / estado_{key}_{año}.xlsx   (download_sbp.py)
  RE-BALANCE-BANCO-en-{slug}.xlsx / RE-ESTADO-BANCO-en-{slug}.xlsx   (descarga manual)
El año se lee SIEMPRE del contenido del archivo (no del nombre).

Decisiones (ver QC): universo = SBN (Oficiales + Lic. General; sin Lic. Internacional);
LP = OBLIGACIONES, CP = DEPOSITOS + OTROS PASIVOS; PD contable para todos.

Outputs:
  balance_panama.csv  (countryname,bankname,pd_source,date,year,month,tot_asset,total_liab,
                       equity,st_borrow,lt_borrow,net_income,id_fail)
  coverage_panama.csv (QC por banco: n_periodos,desde,hasta,id_fails)
  mktcap_panama.csv   (vacío salvo tickers activos)

Uso:
    python extract_panama.py --raw ./sbp_raw --start 2018 --end 2026
"""
import argparse, glob, os, re
import pandas as pd
import sbp_parse as sp

COUNTRY = "panama"

BANKMAP = {k: {"ticker": None, "pd_source": "book"} for k in [
    "banco_nacional", "caja_ahorros", "banco_general", "banistmo", "bac_panama",
    "global_bank", "banesco", "bancolombia_pa", "multibank", "credicorp_bank",
    "mercantil", "metrobank", "towerbank", "aliado", "st_george", "unibank", "bct_bank"]}
# "bladex": {"ticker": "BLX", "pd_source": "market"}  # opcional NYSE

DL_RE = re.compile(r"^(balance|estado)_(.+)_(\d{4})\.xls[x]?$", re.I)
RAW_RE = re.compile(r"^RE-(BALANCE|ESTADO)-BANCO-en-(.+)\.xls[x]?$", re.I)


def _scan(raw_dir):
    """Devuelve ([(key,path) balances], [(key,path) estados])."""
    bal, est = [], []
    for p in sorted(glob.glob(os.path.join(raw_dir, "*.xls*"))):
        name = os.path.basename(p)
        m = DL_RE.match(name)
        if m:
            section, key = m.group(1).lower(), m.group(2)
            (bal if section == "balance" else est).append((key, p)); continue
        m = RAW_RE.match(name)
        if m:
            section = m.group(1).lower()  # balance / estado
            key = sp.SLUG2KEY.get(m.group(2).lower())
            if key is None:
                print(f"  [skip] slug desconocido: {name}"); continue
            (bal if section == "balance" else est).append((key, p))
    return bal, est


def build_balance(raw_dir, start, end):
    bal_files, est_files = _scan(raw_dir)
    est_idx = {}
    for key, p in est_files:
        if key not in BANKMAP:
            continue
        try:
            ni = sp.parse_netincome(p, bank_key=key)
        except Exception as e:
            print(f"  [WARN] estado {key}: {e}"); continue
        if ni is None or ni.empty:
            continue
        yr = int(ni["date"].astype("datetime64[ns]").dt.year.mode().iloc[0])
        est_idx[(key, yr)] = ni

    frames = []
    for key, p in bal_files:
        if key not in BANKMAP:
            print(f"  [skip] {key} fuera del universo SBN núcleo"); continue
        try:
            b = sp.parse_balance(p, bank_key=key)
        except Exception as e:
            print(f"  [WARN] balance {key}: {e}"); continue
        if b.empty:
            continue
        b["date"] = pd.to_datetime(b["date"])
        yr = int(b["date"].dt.year.mode().iloc[0])
        ni = est_idx.get((key, yr))
        if ni is not None:
            ni = ni.copy(); ni["date"] = pd.to_datetime(ni["date"])
            b = b.merge(ni[["bankname", "date", "net_income_flow"]],
                        on=["bankname", "date"], how="left")
        if "net_income_flow" not in b.columns:
            b["net_income_flow"] = pd.NA
        frames.append(b)

    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(["bankname", "date"], keep="last")  # evita dobles descargas
    df["countryname"] = COUNTRY
    df["pd_source"] = df["bankname"].map(lambda k: BANKMAP.get(k, {}).get("pd_source", "book"))
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df = df.rename(columns={"tot_liab": "total_liab", "st_debt": "st_borrow",
                            "lt_debt": "lt_borrow", "net_income_flow": "net_income"})
    df = df[(df["year"] >= start) & (df["year"] <= end)]
    cols = ["countryname", "bankname", "pd_source", "date", "year", "month",
            "tot_asset", "total_liab", "equity", "st_borrow", "lt_borrow", "net_income", "id_fail"]
    return df[cols].sort_values(["bankname", "date"]).reset_index(drop=True)


def coverage_report(b):
    if b.empty:
        return pd.DataFrame()
    return (b.dropna(subset=["tot_asset"])
              .groupby(["bankname", "pd_source"])
              .agg(n_periodos=("date", "nunique"), desde=("date", "min"),
                   hasta=("date", "max"), id_fails=("id_fail", "sum"))
              .reset_index().sort_values("desde"))


def fetch_mktcap(b, start, end):
    listed = {k: v["ticker"] for k, v in BANKMAP.items() if v.get("ticker")}
    schema = ["bankname", "countryname", "date", "mktcap"]
    if not listed:
        return pd.DataFrame(columns=schema)
    try:
        import yfinance as yf
    except ImportError:
        print("  [WARN] yfinance no instalado; mktcap vacío."); return pd.DataFrame(columns=schema)
    rows = []
    for key, tk in listed.items():
        try:
            t = yf.Ticker(tk)
            px = t.history(start=f"{start}-01-01", end=f"{end}-12-31")["Close"]
            sh = t.get_shares_full(start=f"{start}-01-01")
            if px.empty or sh is None or sh.empty:
                continue
            sh = sh[~sh.index.duplicated(keep="last")]
            m = px.to_frame("px").join(sh.rename("sh").reindex(px.index, method="ffill")).dropna()
            m["mktcap"] = m["px"] * m["sh"]
            rows += [{"bankname": key, "countryname": COUNTRY, "date": d.date(),
                      "mktcap": float(v)} for d, v in m["mktcap"].items()]
        except Exception as e:
            print(f"  [WARN] mktcap {key} ({tk}): {e}")
    return pd.DataFrame(rows, columns=schema)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--start", type=int, default=2018)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = build_balance(a.raw, a.start, a.end)
    bal.to_csv(f"balance_{COUNTRY}.csv", index=False)
    cov = coverage_report(bal); cov.to_csv(f"coverage_{COUNTRY}.csv", index=False)
    mkt = fetch_mktcap(bal, a.start, a.end); mkt.to_csv(f"mktcap_{COUNTRY}.csv", index=False)
    nf = int(bal["id_fail"].sum()) if not bal.empty else 0
    print(f"balance {len(bal)} filas | bancos {bal['bankname'].nunique() if not bal.empty else 0} "
          f"| id_fails {nf} | coverage {len(cov)} | mktcap {len(mkt)}")


if __name__ == "__main__":
    main()