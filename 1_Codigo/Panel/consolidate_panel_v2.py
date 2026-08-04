# -*- coding: utf-8 -*-
"""
consolidate_panel_v2.py
========================
Version generalizada a los 15 paises del panel GaR.
Consolida EMBI x GaR (JLoss pendiente, se deja hook para cuando este listo).

Uso:
    python consolidate_panel_v2.py [DATA_DIR]
"""
import sys
import glob
import os
import pandas as pd

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

TARGET = ["brazil", "bulgaria", "chile", "china", "colombia", "hungary",
          "india", "indonesia", "mexico", "pakistan", "peru", "poland",
          "southafrica", "southkorea", "turkey"]

EMBI_COLMAP = {  # columnas del excel BCRP -> clave estandar del panel
    "Brasil": "brazil", "Chile": "chile", "Colombia": "colombia",
    "México": "mexico", "Mexico": "mexico", "Perú": "peru", "Peru": "peru",
}


def find(*patterns, required=True):
    files = glob.glob(os.path.join(DATA_DIR, "*"))
    low = {f: os.path.basename(f).lower() for f in files}
    for pat in patterns:
        for f, name in low.items():
            if pat.lower() in name:
                return f
    if required:
        raise FileNotFoundError(f"No se encontro archivo para {patterns} en {DATA_DIR}")
    return None


def load_gar():
    path = find("gar_panel_all15", "gar_panel_latam", "gar_latam")
    g = pd.read_csv(path)
    g["country"] = g["country"].str.lower().str.replace(" ", "", regex=False)
    keep = [c for c in ["country", "quarter", "GaR", "prob_neg", "ES", "ER",
                        "mean", "std", "iqr_05_95", "skew", "kurt", "n_train"]
            if c in g.columns]
    g = g[keep]
    g = g[g["country"].isin(TARGET)]
    print(f"  GaR   : {path} -> {g.shape[0]} obs, {g['country'].nunique()} paises")
    return g


def load_embi():
    path = find("embi", "spread")
    raw = pd.read_excel(path, header=1)
    raw = raw.rename(columns={raw.columns[0]: "Fecha"})
    raw["Fecha"] = pd.to_datetime(raw["Fecha"], errors="coerce")
    raw = raw.dropna(subset=["Fecha"])
    present = {k: v for k, v in EMBI_COLMAP.items() if k in raw.columns}
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
    print(f"  EMBI  : {path} -> {out.shape[0]} obs, paises: {sorted(out['country'].unique())}")
    return out


def main():
    print(f"Carpeta: {os.path.abspath(DATA_DIR)}\n--- cargando ---")
    gar = load_gar()
    embi = load_embi()

    gar_countries = set(gar["country"].unique())
    embi_countries = set(embi["country"].unique())
    faltan = sorted(gar_countries - embi_countries)

    print("\n--- COBERTURA EMBI (excel BCRP) vs 15 paises del panel GaR ---")
    print(f"  Con EMBI  ({len(embi_countries)}): {sorted(embi_countries)}")
    print(f"  Sin EMBI  ({len(faltan)}): {faltan}")

    panel = embi.merge(gar, on=["country", "quarter"], how="inner")
    panel["t"] = pd.PeriodIndex(panel["quarter"], freq="Q")
    panel = panel.sort_values(["country", "t"]).drop(columns=["t"]).reset_index(drop=True)

    out_path = os.path.join(DATA_DIR, "Panel_partial_EMBI_GaR.csv")
    panel.to_csv(out_path, index=False)
    print(f"\nGuardado: {out_path}  shape={panel.shape}")
    print("\nCobertura por pais (panel parcial EMBI x GaR):")
    for c, g in panel.groupby("country"):
        print(f"  {c:12s} n={len(g):3d}  {g['quarter'].min()} -> {g['quarter'].max()}")


if __name__ == "__main__":
    main()
