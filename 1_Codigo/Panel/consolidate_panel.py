# -*- coding: utf-8 -*-
"""
consolidate_panel.py
====================
Consolida en UNA sola base las cuatro fuentes y deja el panel listo para
las regresiones:

    Panel_final.csv   (claves: country, quarter)

Coloca en una misma carpeta (DATA_DIR) los archivos:
    - EMBI .......... Serie_Historica_Spread_del_EMBI.xlsx   (diario)
    - GaR LATAM ..... gar_panel_latam.csv                    (trimestral)
    - JLoss ......... Jloss.dta                              (formato YYYYQ)
    - Controles ..... controls_panel.csv   (opcional; salida de fetch_controls.py)
    - VIX/g_GDP ..... GaR_test.xlsx         (opcional; aporta VIX y g_GDP)

El script detecta cada archivo por patron de nombre (no importa mayusculas
ni rutas). Ejecutar:

    python consolidate_panel.py            # usa la carpeta actual
    python consolidate_panel.py  C:\ruta\a\la\carpeta

REQUISITOS: pip install pandas numpy pyreadstat openpyxl
"""

import sys
import glob
import os
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
TARGET = ["brazil", "chile", "colombia", "mexico", "peru"]

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "."


def find(*patterns, required=True):
    """Devuelve la primera ruta que matchee alguno de los patrones (case-insensitive)."""
    files = glob.glob(os.path.join(DATA_DIR, "*"))
    low = {f: os.path.basename(f).lower() for f in files}
    for pat in patterns:
        for f, name in low.items():
            if pat.lower() in name:
                return f
    if required:
        raise FileNotFoundError(
            f"No se encontro ningun archivo que contenga {patterns} en {DATA_DIR}")
    return None


# ----------------------------------------------------------------------
# 1. JLoss  (Jloss.dta, formato time=YYYYQ)
# ----------------------------------------------------------------------
def load_jloss():
    import pyreadstat
    path = find("jloss.dta", "jloss")
    df, _ = pyreadstat.read_dta(path)
    df = df.dropna(subset=["jloss"]).copy()
    namemap = {"brasil": "brazil", "chile": "chile", "colombia": "colombia",
               "mexico": "mexico", "peru": "peru",
               "brazil": "brazil"}            # por si ya viene en ingles
    df["country"] = df["country"].str.lower().map(namemap)
    df = df[df["country"].isin(TARGET)].copy()
    df["year"] = (df["time"] // 10).astype(int)
    df["q"] = (df["time"] % 10).astype(int)
    df["quarter"] = df["year"].astype(str) + "Q" + df["q"].astype(str)
    out = df.rename(columns={"jloss": "JLoss"})[["country", "quarter", "JLoss"]]
    print(f"  JLoss   : {path}  ->  {out.shape[0]} obs")
    return out


# ----------------------------------------------------------------------
# 2. GaR 15 paises  (gar_panel_latam.csv, ya trimestral sumado a mas paises)
# ----------------------------------------------------------------------
def load_gar():
    path = find("gar_panel_latam", "gar_panel_all15", "gar_latam")
    g = pd.read_csv(path)
    g["country"] = g["country"].str.lower()
    keep = [c for c in ["country", "quarter", "GaR", "GaR_st",
                        "prob_neg", "ES", "skew", "std"] if c in g.columns]
    g = g[keep]
    g = g[g["country"].isin(TARGET)]
    print(f"  GaR     : {path}  ->  {g.shape[0]} obs")
    return g


# ----------------------------------------------------------------------
# 3. EMBI  (diario -> trimestral, promedio intra-trimestre, en pb)
# ----------------------------------------------------------------------
def load_embi():
    path = find("embi", "spread")
    raw = pd.read_excel(path, header=1)
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
    q["EMBI_bps"] = q["pct"] * 100.0          # puntos porcentuales -> puntos basicos
    out = q[["country", "quarter", "EMBI_bps"]]
    print(f"  EMBI    : {path}  ->  {out.shape[0]} obs (trimestral, pb)")
    return out


# ----------------------------------------------------------------------
# 4. Controles (opcional)
# ----------------------------------------------------------------------
def load_controls():
    path = find("controls_panel", "controls", required=False)
    if path is None:
        print("  Controles: (no encontrado, se omite)")
        return None
    c = pd.read_csv(path)
    c["country"] = c["country"].str.lower()
    print(f"  Controles: {path}  ->  {c.shape[0]} obs, cols {list(c.columns)[2:]}")
    return c


# ----------------------------------------------------------------------
# 5. VIX / g_GDP desde GaR_test.xlsx (opcional)
# ----------------------------------------------------------------------
def load_vix_ggdp():
    """VIX (factor global, solo necesario en spec FE-pais). Dos fuentes posibles:
    1) GaR_test.xlsx  -> VIX estandarizado por la plataforma CEMLA + g_GDP.
    2) VIX_History.csv (CBOE, diario) -> media trimestral del CLOSE (puntos indice).
    El VIX es comun a todos los paises en cada trimestre; se replica por pais."""
    # Opcion 1: GaR_test.xlsx (preferente: VIX exactamente como entro al GaR)
    path = find("gar_test", "gar test", required=False)
    if path is not None:
        d = pd.read_excel(path, sheet_name="Data")
        d["Date"] = pd.to_datetime(d["Date"], format="%d/%m/%Y", errors="coerce")
        d = d.dropna(subset=["Date"])
        d["country"] = d["Country"].str.lower()
        d["quarter"] = d["Date"].dt.to_period("Q").astype(str)
        out = d[d["country"].isin(TARGET)][["country", "quarter", "VIX", "g_GDP"]]
        print(f"  VIX/g_GDP: {path}  ->  {out.shape[0]} obs (VIX estandarizado CEMLA)")
        return out

    # Opcion 2: VIX_History.csv (CBOE, diario) -> trimestral
    path = find("vix_history", "vix", required=False)
    if path is None:
        print("  VIX/g_GDP: (ni GaR_test.xlsx ni VIX_History.csv; se omite VIX)")
        return None
    v = pd.read_csv(path)
    v["DATE"] = pd.to_datetime(v["DATE"], format="%m/%d/%Y", errors="coerce")
    v = v.dropna(subset=["DATE"])
    v["quarter"] = v["DATE"].dt.to_period("Q").astype(str)
    vq = v.groupby("quarter", as_index=False)["CLOSE"].mean().rename(
        columns={"CLOSE": "VIX"})
    # replicar el VIX (global) a cada pais del panel
    rep = pd.MultiIndex.from_product([TARGET, vq["quarter"]],
                                     names=["country", "quarter"]).to_frame(index=False)
    out = rep.merge(vq, on="quarter", how="left")
    print(f"  VIX     : {path}  ->  {vq.shape[0]} trimestres (media CBOE, pts indice)")
    return out


# ----------------------------------------------------------------------
# 6. Consolidar
# ----------------------------------------------------------------------
def main():
    print(f"Carpeta de datos: {os.path.abspath(DATA_DIR)}\n--- cargando fuentes ---")
    embi = load_embi()
    jl = load_jloss()
    gar = load_gar()
    ctrl = load_controls()
    vix = load_vix_ggdp()

    # nucleo: interseccion EMBI x JLoss x GaR (inner -> solo filas con las 3)
    panel = (embi.merge(jl, on=["country", "quarter"], how="inner")
                 .merge(gar, on=["country", "quarter"], how="inner"))

    # enriquecer (left: no perder filas del nucleo)
    if vix is not None:
        panel = panel.merge(vix, on=["country", "quarter"], how="left")
    if ctrl is not None:
        panel = panel.merge(ctrl, on=["country", "quarter"], how="left")

    # variables derivadas
    panel["JLoss_x_GaR"] = panel["JLoss"] * panel["GaR"]
    panel["t"] = pd.PeriodIndex(panel["quarter"], freq="Q")
    panel = panel.sort_values(["country", "t"]).drop(columns=["t"]).reset_index(drop=True)

    out_path = os.path.join(DATA_DIR, "Panel_final.csv")
    panel.to_csv(out_path, index=False)

    # reporte
    print("\n--- PANEL CONSOLIDADO ---")
    print("Guardado:", out_path, " shape:", panel.shape)
    print("Columnas:", list(panel.columns))
    print("\nCobertura por pais:")
    for c, g in panel.groupby("country"):
        print(f"  {c:9s} n={len(g):3d}  {g['quarter'].min()} -> {g['quarter'].max()}")
    print("\n% no-nulo por columna:")
    print((panel.notna().mean().round(2) * 100).astype(int).to_string())
    print("\nPrimeras filas:")
    cols_show = [c for c in ["country", "quarter", "EMBI_bps", "JLoss", "GaR",
                             "ES", "VIX", "debt_gdp", "fisc_bal"] if c in panel.columns]
    print(panel[cols_show].head(8).to_string())


if __name__ == "__main__":
    main()