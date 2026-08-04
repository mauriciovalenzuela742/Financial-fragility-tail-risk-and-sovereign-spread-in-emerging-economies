"""
build_panel.py — Ensambla el panel final país-trimestre del paper JLoss, etapa 1:
  - EMBI spread  : J.P. Morgan EMBI Global, vía API del Global Economic Monitor (GEM) del Banco Mundial
  - Controles globales : VIX, U.S. Treasury 10Y, High Yield spread, vía FRED (CSV sin API key)
y los une con tu panel de JLoss (Panel_JLoss_v8.csv) por country-quarter.

Todo desde fuentes GRATIS, solo con `requests` (FRED no requiere clave usando fredgraph.csv;
el Banco Mundial tampoco). Frecuencias diarias/mensuales se colapsan a TRIMESTRAL (promedio).

Uso:
    python build_panel.py --discover                          # lista indicadores EMBI del GEM
    python build_panel.py --jloss Panel_JLoss_v8.csv --start 2000 --end 2026
"""
import argparse, io, sys
import pandas as pd
import numpy as np
import requests

WB_API = "https://api.worldbank.org/v2"
GEM_SOURCE = 15  # Global Economic Monitor
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"

# Controles globales (FRED series id -> nombre de columna del panel)
FRED_SERIES = {
    "VIXCLS": "vix",                # CBOE Volatility Index
    "DGS10": "ust10y",              # U.S. Treasury 10Y constant maturity
    "BAMLH0A0HYM2": "hy_spread",    # ICE BofA US High Yield OAS
}

# País del panel JLoss -> ISO3 (para el EMBI del Banco Mundial)
COUNTRY_ISO = {
    "argentina": "ARG", "brazil": "BRA", "bulgaria": "BGR", "chile": "CHL",
    "china": "CHN", "colombia": "COL", "egypt": "EGY", "indonesia": "IDN",
    "malaysia": "MYS", "mexico": "MEX", "pakistan": "PAK", "panama": "PAN",
    "peru": "PER", "philippines": "PHL", "poland": "POL", "russia": "RUS",
    "south_africa": "ZAF", "turkey": "TUR", "venezuela": "VEN",
}
ISO_COUNTRY = {v: k for k, v in COUNTRY_ISO.items()}


# --------------------------------------------------------------------------- utilidades
def _to_quarter_period(s):
    """Parsea fechas del Banco Mundial ('2020M03','2020Q2','2020') o ISO a Period trimestral."""
    s = str(s).strip()
    if "M" in s:
        y, m = s.split("M"); return pd.Period(f"{y}-{int(m):02d}", freq="M").asfreq("Q")
    if "Q" in s:
        return pd.Period(s, freq="Q")
    if len(s) == 4 and s.isdigit():
        return pd.Period(f"{s}-12", freq="M").asfreq("Q")
    return pd.Period(pd.to_datetime(s), freq="Q")


def daily_csv_to_quarterly(text, valname):
    """CSV de FRED (1ª col fecha, 2ª col valor; '.'=NaN) -> promedio trimestral."""
    df = pd.read_csv(io.StringIO(text))
    df.columns = ["date", valname]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[valname] = pd.to_numeric(df[valname].replace(".", np.nan), errors="coerce")
    df = df.dropna(subset=["date"])
    df["quarter"] = df["date"].dt.to_period("Q")
    return df.groupby("quarter")[valname].mean().reset_index()


# --------------------------------------------------------------------------- World Bank GEM
def wb_get(path, params):
    p = {"format": "json", "per_page": 20000, **params}
    r = requests.get(f"{WB_API}/{path}", params=p, timeout=60)
    r.raise_for_status()
    js = r.json()
    return js[1] if isinstance(js, list) and len(js) > 1 else []


def discover_embi_indicators():
    """Lista los indicadores del GEM cuyo nombre menciona EMBI / bond spread."""
    rows = wb_get("indicator", {"source": GEM_SOURCE, "per_page": 2000})
    out = []
    for it in rows or []:
        name = (it.get("name") or "")
        if any(k in name.upper() for k in ("EMBI", "BOND SPREAD", "STRIPPED")):
            out.append((it.get("id"), name))
    return out


def fetch_embi(indicator, isos, start, end):
    """EMBI mensual por país -> trimestral. Devuelve country-quarter-embi_spread."""
    frames = []
    for iso in isos:
        rows = wb_get(f"country/{iso}/indicator/{indicator}",
                      {"source": GEM_SOURCE, "frequency": "M", "date": f"{start}M01:{end}M12"})
        recs = [(r["date"], r["value"]) for r in (rows or []) if r.get("value") is not None]
        if not recs:
            continue
        d = pd.DataFrame(recs, columns=["date", "embi_spread"])
        d["quarter"] = d["date"].map(_to_quarter_period)
        d = d.groupby("quarter")["embi_spread"].mean().reset_index()
        d["countryname"] = ISO_COUNTRY.get(iso, iso.lower())
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else \
        pd.DataFrame(columns=["countryname", "quarter", "embi_spread"])


# --------------------------------------------------------------------------- FRED globales
def fetch_fred_globals(start, end):
    out = None
    for sid, col in FRED_SERIES.items():
        r = requests.get(FRED_CSV, params={"id": sid, "cosd": f"{start}-01-01", "coed": f"{end}-12-31"},
                         timeout=60)
        r.raise_for_status()
        q = daily_csv_to_quarterly(r.text, col)
        out = q if out is None else out.merge(q, on="quarter", how="outer")
    return out.sort_values("quarter").reset_index(drop=True) if out is not None else pd.DataFrame()


# --------------------------------------------------------------------------- panel JLoss
def load_jloss(path):
    j = pd.read_csv(path)
    j.columns = [c.strip().lower() for c in j.columns]
    if "quarter" in j.columns:
        j["quarter"] = j["quarter"].map(_to_quarter_period)
    elif "date" in j.columns:
        j["quarter"] = pd.to_datetime(j["date"]).dt.to_period("Q")
    else:
        raise ValueError("el panel JLoss necesita columna 'quarter' o 'date'")
    j["countryname"] = j["countryname"].str.strip().str.lower().str.replace(" ", "_")
    return j[["countryname", "quarter", "jloss"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jloss", default="Panel_JLoss_v8.csv")
    ap.add_argument("--embi-indicator", default=None,
                    help="código del indicador EMBI en el GEM; si se omite, se auto-descubre")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="panel_partial.csv")
    ap.add_argument("--discover", action="store_true", help="solo listar indicadores EMBI del GEM")
    a = ap.parse_args()

    if a.discover:
        for code, name in discover_embi_indicators():
            print(f"  {code:30s} {name}")
        return

    indicator = a.embi_indicator
    if not indicator:
        cands = discover_embi_indicators()
        if not cands:
            sys.exit("No encontré indicador EMBI en el GEM; usa --discover y pasa --embi-indicator.")
        indicator = cands[0][0]
        print(f"EMBI auto-detectado: {indicator} ({cands[0][1]})")

    jloss = load_jloss(a.jloss)
    isos = [COUNTRY_ISO[c] for c in jloss["countryname"].unique() if c in COUNTRY_ISO]
    embi = fetch_embi(indicator, isos, a.start, a.end)
    glob = fetch_fred_globals(a.start, a.end)

    panel = jloss.merge(embi, on=["countryname", "quarter"], how="left")
    panel = panel.merge(glob, on="quarter", how="left")        # globales: se difunden a todos los países
    panel = panel.sort_values(["countryname", "quarter"]).reset_index(drop=True)
    panel.to_csv(a.out, index=False)

    cols = [c for c in ["jloss", "embi_spread", "vix", "ust10y", "hy_spread"] if c in panel.columns]
    print(f"{a.out}: {len(panel)} filas | países={panel['countryname'].nunique()} | "
          f"trimestres={panel['quarter'].nunique()}")
    print("cobertura no-nula:")
    for c in cols:
        print(f"  {c:12s} {panel[c].notna().mean()*100:5.1f}%")
    print("\nTable 2 (parcial):")
    print(panel[cols].describe().T[["count", "mean", "std", "min", "max"]].round(3).to_string())


if __name__ == "__main__":
    main()