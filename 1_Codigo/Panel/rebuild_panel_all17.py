# -*- coding: utf-8 -*-
"""
rebuild_panel_all17.py
======================
Version NO DESTRUCTIVA de la consolidacion de la base "LatAm larga" usando el
panel GaR de 17 paises (gar_panel_all17.csv) en vez de all15.

Reproduce la cadena:
    consolidate_panel.py  ->  patch_chile_debt.py  ->  add_paper_controls.py

pero escribe a archivos *_all17 y NO sobrescribe ninguna salida all15
(Panel_final.csv, Panel_final_prebackup.csv quedan intactos).

Salidas:
    Panel_final_all17.csv            (analogo a Panel_final.csv, base LatAm larga)
    Panel_final_prebackup_all17.csv  (respaldo pre-parche Chile)

Uso:
    python rebuild_panel_all17.py
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
GAR_FILE = "gar_panel_all17.csv"          # <-- unico cambio de fondo vs all15
TARGET = ["brazil", "chile", "colombia", "mexico", "peru"]


def p(*a):
    return os.path.join(DATA_DIR, *a)


# ----------------------------------------------------------------------
# 1. JLoss
# ----------------------------------------------------------------------
def load_jloss():
    import pyreadstat
    df, _ = pyreadstat.read_dta(p("Jloss.dta"))
    df = df.dropna(subset=["jloss"]).copy()
    namemap = {"brasil": "brazil", "chile": "chile", "colombia": "colombia",
               "mexico": "mexico", "peru": "peru", "brazil": "brazil"}
    df["country"] = df["country"].str.lower().map(namemap)
    df = df[df["country"].isin(TARGET)].copy()
    df["year"] = (df["time"] // 10).astype(int)
    df["q"] = (df["time"] % 10).astype(int)
    df["quarter"] = df["year"].astype(str) + "Q" + df["q"].astype(str)
    out = df.rename(columns={"jloss": "JLoss"})[["country", "quarter", "JLoss"]]
    print(f"  JLoss   : {out.shape[0]} obs")
    return out


# ----------------------------------------------------------------------
# 2. GaR (all17)
# ----------------------------------------------------------------------
def load_gar():
    g = pd.read_csv(p(GAR_FILE))
    g["country"] = g["country"].str.lower().str.replace(" ", "", regex=False)
    keep = [c for c in ["country", "quarter", "GaR", "GaR_st",
                        "prob_neg", "ES", "skew", "std"] if c in g.columns]
    g = g[keep]
    g = g[g["country"].isin(TARGET)]
    print(f"  GaR     : {GAR_FILE} -> {g.shape[0]} obs (5 LatAm de 17)")
    return g


# ----------------------------------------------------------------------
# 3. EMBI (BCRP, diario -> trimestral, pb)
# ----------------------------------------------------------------------
def load_embi():
    raw = pd.read_excel(p("Serie_Historica_Spread_del_EMBI.xlsx"), header=1)
    raw = raw.rename(columns={raw.columns[0]: "Fecha"})
    raw["Fecha"] = pd.to_datetime(raw["Fecha"], errors="coerce")
    raw = raw.dropna(subset=["Fecha"])
    cmap = {"Brasil": "brazil", "Chile": "chile", "Colombia": "colombia",
            "México": "mexico", "Mexico": "mexico", "Perú": "peru", "Peru": "peru"}
    present = {k: v for k, v in cmap.items() if k in raw.columns}
    for k in present:
        raw[k] = pd.to_numeric(raw[k], errors="coerce")
    raw["quarter"] = raw["Fecha"].dt.to_period("Q").astype(str)
    long = raw.melt(id_vars=["quarter"], value_vars=list(present),
                    var_name="cty", value_name="pct")
    long["country"] = long["cty"].map(present)
    q = (long.dropna(subset=["pct"])
             .groupby(["country", "quarter"], as_index=False)["pct"].mean())
    q["EMBI_bps"] = q["pct"] * 100.0
    out = q[["country", "quarter", "EMBI_bps"]]
    print(f"  EMBI    : {out.shape[0]} obs (trimestral, pb)")
    return out


def load_controls():
    path = p("controls_panel.csv")
    if not os.path.exists(path):
        print("  Controles: (no encontrado, se omite)")
        return None
    c = pd.read_csv(path)
    c["country"] = c["country"].str.lower()
    print(f"  Controles: {c.shape[0]} obs, cols {list(c.columns)[2:]}")
    return c


def load_vix_ggdp():
    path = p("GaR_test.xlsx")
    if os.path.exists(path):
        d = pd.read_excel(path, sheet_name="Data")
        d["Date"] = pd.to_datetime(d["Date"], format="%d/%m/%Y", errors="coerce")
        d = d.dropna(subset=["Date"])
        d["country"] = d["Country"].str.lower()
        d["quarter"] = d["Date"].dt.to_period("Q").astype(str)
        out = d[d["country"].isin(TARGET)][["country", "quarter", "VIX", "g_GDP"]]
        print(f"  VIX/g_GDP: {out.shape[0]} obs (VIX estandarizado CEMLA)")
        return out
    print("  VIX/g_GDP: (GaR_test.xlsx no encontrado; se omite)")
    return None


# ----------------------------------------------------------------------
# 4. Parche deuda Chile (no toca prebackup all15)
# ----------------------------------------------------------------------
def patch_chile(panel):
    path = p("PEM_FP_DP.xlsx")
    if not os.path.exists(path) or "debt_gdp" not in panel.columns:
        print("  Parche Chile: omitido (falta PEM_FP_DP.xlsx o columna debt_gdp)")
        return panel
    ch = pd.read_excel(path, sheet_name="Cuadro", header=2)
    ch = ch.rename(columns={ch.columns[0]: "date", ch.columns[1]: "debt_chile"})
    ch = ch.dropna(subset=["date"]).copy()
    ch["date"] = pd.to_datetime(ch["date"], errors="coerce")
    ch = ch.dropna(subset=["date"])
    ch["quarter"] = ch["date"].dt.to_period("Q").astype(str)
    ch["debt_chile"] = pd.to_numeric(ch["debt_chile"], errors="coerce")
    ch = ch[["quarter", "debt_chile"]]
    before = panel[panel["country"] == "chile"]["debt_gdp"].isna().sum()
    panel = panel.merge(ch, on="quarter", how="left")
    mask = (panel["country"] == "chile") & (panel["debt_gdp"].isna())
    panel.loc[mask, "debt_gdp"] = panel.loc[mask, "debt_chile"]
    panel = panel.drop(columns=["debt_chile"])
    after = panel[panel["country"] == "chile"]["debt_gdp"].isna().sum()
    print(f"  Parche Chile: debt_gdp vacio antes={before} despues={after}")
    return panel


# ----------------------------------------------------------------------
# 5. Controles globales del paper (Chari et al. 2024)
# ----------------------------------------------------------------------
def add_global_controls(panel):
    path = p("global_controls_quarterly.csv")
    if not os.path.exists(path):
        print("  Controles globales: (global_controls_quarterly.csv no encontrado; se omite)")
        return panel
    g = pd.read_csv(path)
    keep = [c for c in ["quarter", "UST10Y_log", "US_HY_spread_log",
                        "OnOffRun_spread_log"] if c in g.columns]
    panel = panel.merge(g[keep], on="quarter", how="left")
    if "debt_gdp" in panel.columns:
        panel["debt_gdp_log"] = np.log(panel["debt_gdp"])
    cov = panel["UST10Y_log"].notna().mean() * 100 if "UST10Y_log" in panel else 0
    print(f"  Controles globales: cobertura factores globales={cov:.0f}%")
    return panel


# ----------------------------------------------------------------------
# 6. profit_margin + indices compuestos (replica el enriquecimiento del
#    notebook: X_dom_idx / X_global_idx que usan las regresiones del Rmd)
# ----------------------------------------------------------------------
def add_indices(panel):
    pm_path = p("profit_margin_1999_2011.csv")
    if os.path.exists(pm_path):
        pm = pd.read_csv(pm_path)
        pm["country"] = pm["country"].str.lower()
        panel = panel.merge(pm, on=["country", "quarter"], how="left")
        print(f"  profit_margin: cobertura {panel['profit_margin'].notna().sum()}/{len(panel)}")
    else:
        panel["profit_margin"] = np.nan
        print("  profit_margin: (archivo no encontrado; columna vacia)")

    def z(s):
        return (s - s.mean()) / s.std()

    # X_dom_idx = promedio de z-scores de debt_gdp_log y profit_margin
    if {"debt_gdp_log", "profit_margin"}.issubset(panel.columns):
        panel["X_dom_idx"] = np.nanmean(
            np.c_[z(panel["debt_gdp_log"]), z(panel["profit_margin"])], axis=1)
    # X_global_idx = promedio de z-scores de UST10Y_log y OnOffRun_spread_log
    if {"UST10Y_log", "OnOffRun_spread_log"}.issubset(panel.columns):
        panel["X_global_idx"] = np.nanmean(
            np.c_[z(panel["UST10Y_log"]), z(panel["OnOffRun_spread_log"])], axis=1)
    nd = panel["X_dom_idx"].notna().sum() if "X_dom_idx" in panel else 0
    ng = panel["X_global_idx"].notna().sum() if "X_global_idx" in panel else 0
    print(f"  Indices: X_dom_idx validos={nd}  X_global_idx validos={ng}")
    return panel


def main():
    print(f"Carpeta: {DATA_DIR}\n--- cargando fuentes ---")
    embi = load_embi()
    jl = load_jloss()
    gar = load_gar()
    ctrl = load_controls()
    vix = load_vix_ggdp()

    panel = (embi.merge(jl, on=["country", "quarter"], how="inner")
                 .merge(gar, on=["country", "quarter"], how="inner"))
    if vix is not None:
        panel = panel.merge(vix, on=["country", "quarter"], how="left")
    if ctrl is not None:
        panel = panel.merge(ctrl, on=["country", "quarter"], how="left")

    panel["JLoss_x_GaR"] = panel["JLoss"] * panel["GaR"]
    panel["t"] = pd.PeriodIndex(panel["quarter"], freq="Q")
    panel = panel.sort_values(["country", "t"]).drop(columns=["t"]).reset_index(drop=True)

    # respaldo pre-parche (no toca los archivos all15)
    panel.to_csv(p("Panel_final_prebackup_all17.csv"), index=False)
    panel = patch_chile(panel)
    panel = add_global_controls(panel)
    panel = add_indices(panel)

    out = p("Panel_final_all17.csv")
    panel.to_csv(out, index=False)

    print("\n--- PANEL LATAM LARGA (all17) ---")
    print("Guardado:", out, " shape:", panel.shape)
    print("Columnas:", list(panel.columns))
    for c, g in panel.groupby("country"):
        print(f"  {c:9s} n={len(g):3d}  {g['quarter'].min()} -> {g['quarter'].max()}")


if __name__ == "__main__":
    main()
