# -*- coding: utf-8 -*-
"""
p9_diag_ryr.py -- diagnostico de endogeneidad Ryr <-> EMBI.

Traza como se ATENUA el vinculo entre el rendimiento soberano 10Y (Ryr, insumo
del FCI que alimenta el GaR) y el EMBI (variable dependiente) en cada paso de
construccion:

  Ryr(nivel) -> (Ryr - Ryr_US) -> CDIFF ~ (iRyr - iRyr_noCDIFF) -> iRyr
             -> FCI -> [GaR, insample]

Correlacion con el EMBI en cada paso, pooled y within-pais (demediado). Solo los
13 paises del panel de estimacion.

Salida -> bbg/diag_ryr_embi.csv  +  consola.
"""
import os
import sys
import glob

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GAR = os.path.abspath(os.path.join(HERE, "..", "..", "GaR"))
IND = os.path.join(GAR, "individuals")
US = os.path.join(IND, "US")
sys.path.insert(0, GAR)
import fci_engine as fe  # noqa: E402

PANEL = pd.read_csv(os.path.join(HERE, "Panel_bloomberg.csv"))
PANEL = PANEL.dropna(subset=["EMBI_bps", "JLoss", "GaR"]).copy()
COUNTRIES = sorted(PANEL["country"].unique())          # 13 del panel
NAME = {c: c.upper().replace("SOUTHAFRICA", "SOUTHAFRICA") for c in COUNTRIES}

INITIAL, FINAL = "1999-01-01", "2026-05-31"


def _read_daily(path, name):
    d = pd.read_csv(path); d.columns = ["DATES", name]
    d["DATES"] = pd.to_datetime(d["DATES"], dayfirst=True, errors="coerce")
    return d.dropna(subset=["DATES"])


def quarter_key(ts):
    ts = pd.Timestamp(ts)
    return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"


def country_series(c):
    cdir = os.path.join(IND, NAME[c])
    if not os.path.isdir(cdir):
        return None
    # Ryr local y US -> spread crudo (nivel), trimestral
    ry = _read_daily(glob.glob(os.path.join(cdir, "Ryr*"))[0], "Ryr")
    ru = _read_daily(glob.glob(os.path.join(US, "Ryr*"))[0], "RyrUS")
    r = ry.merge(ru, on="DATES", how="inner")
    r["spread_raw"] = r["Ryr"] - r["RyrUS"]
    r["q"] = r["DATES"].map(quarter_key)
    rq = r.groupby("q").agg(Ryr=("Ryr", "mean"), spread_raw=("spread_raw", "mean"))
    # FCI con y sin CDIFF -> iRyr, iRyr_noCDIFF, FCI, FCI_noCDIFF (mensual -> trim.)
    try:
        b = fe.compute_fci(cdir, NAME[c], US, initial=INITIAL, final=FINAL, drop_cdiff=False)
        n = fe.compute_fci(cdir, NAME[c], US, initial=INITIAL, final=FINAL, drop_cdiff=True)
    except Exception as e:
        print(f"  {c}: compute_fci ERROR {e}")
        return None
    for df, tag in ((b, ""), (n, "_noCDIFF")):
        df["q"] = df["DATES"].map(quarter_key)
    bq = b[b["DATES"].dt.month.isin([3, 6, 9, 12])].groupby("q").agg(
        iRyr=("iRyr", "last"), FCI=("FCI", "last"))
    nq = n[n["DATES"].dt.month.isin([3, 6, 9, 12])].groupby("q").agg(
        iRyr_noCDIFF=("iRyr", "last"), FCI_noCDIFF=("FCI", "last"))
    m = rq.join(bq, how="outer").join(nq, how="outer").reset_index()
    m["country"] = c
    m["cdiff_contrib"] = m["iRyr"] - m["iRyr_noCDIFF"]   # ~ CDIFF estandarizado / 2
    return m


def corrs(df, x, y="EMBI_bps"):
    d = df.dropna(subset=[x, y])
    if len(d) < 30:
        return np.nan, np.nan, len(d)
    pooled = d[x].corr(d[y])
    dw = d.copy()
    dw[x + "_w"] = dw[x] - dw.groupby("country")[x].transform("mean")
    dw[y + "_w"] = dw[y] - dw.groupby("country")[y].transform("mean")
    within = dw[x + "_w"].corr(dw[y + "_w"])
    return pooled, within, len(d)


def main():
    parts = [s for c in COUNTRIES if (s := country_series(c)) is not None]
    S = pd.concat(parts, ignore_index=True)
    emb = PANEL[["country", "quarter", "EMBI_bps", "GaR"]].rename(columns={"quarter": "q"})
    emb["D"] = -emb["GaR"] * 100
    D = S.merge(emb, on=["country", "q"], how="inner")
    D.to_csv(os.path.join(HERE, "diag_ryr_embi.csv"), index=False)

    print(f"Paises: {D['country'].nunique()}   obs con EMBI: {D['EMBI_bps'].notna().sum()}\n")
    print(f"{'paso de construccion':32s} {'corr pooled':>12s} {'corr within':>12s} {'N':>6s}")
    print("-" * 66)
    for lbl, col in [
        ("Ryr (nivel, %)",                 "Ryr"),
        ("Ryr - Ryr_US (spread crudo)",    "spread_raw"),
        ("contribucion tipo-CDIFF a iRyr", "cdiff_contrib"),
        ("iRyr (subindice de tasa)",       "iRyr"),
        ("iRyr sin CDIFF",                 "iRyr_noCDIFF"),
        ("FCI",                            "FCI"),
        ("FCI sin CDIFF",                  "FCI_noCDIFF"),
        ("D = -GaR (serie oficial)",       "D"),
    ]:
        p, w, n = corrs(D, col)
        print(f"{lbl:32s} {p:>12.3f} {w:>12.3f} {n:>6d}")

    # cuanto se mueve el FCI al quitar CDIFF
    dd = D.dropna(subset=["FCI", "FCI_noCDIFF"])
    print(f"\ncorr(FCI, FCI_noCDIFF)            = {dd['FCI'].corr(dd['FCI_noCDIFF']):.3f}")
    print(f"corr(iRyr, iRyr_noCDIFF)          = "
          f"{D.dropna(subset=['iRyr','iRyr_noCDIFF']).pipe(lambda x: x['iRyr'].corr(x['iRyr_noCDIFF'])):.3f}")
    print("\nGuardado: bbg/diag_ryr_embi.csv")


if __name__ == "__main__":
    main()
