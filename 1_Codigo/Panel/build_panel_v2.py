# -*- coding: utf-8 -*-
import pyreadstat
import pandas as pd
import numpy as np

LATAM = ["brazil", "chile", "colombia", "mexico", "peru"]

EMBI_COLMAP = {
    "Brasil": "brazil", "Chile": "chile", "Colombia": "colombia",
    "México": "mexico", "Mexico": "mexico", "Perú": "peru", "Peru": "peru",
}

JLOSS_NAMEMAP = {
    "brasil": "brazil", "chile": "chile", "colombia": "colombia", "mexico": "mexico",
    "peru": "peru", "bulgaria": "bulgaria", "china": "china", "indonesia": "indonesia",
    "pakistan": "pakistan", "polonia": "poland", "sudafrica": "southafrica",
    "turquia": "turkey", "argentina": "argentina", "egipto": "egypt",
    "filipinas": "philippines", "malasia": "malaysia", "panama": "panama",
    "rusia": "russia", "venezuela": "venezuela",
}

TARGET15 = ["brazil", "bulgaria", "chile", "china", "colombia", "hungary",
            "india", "indonesia", "mexico", "pakistan", "peru", "poland",
            "southafrica", "southkorea", "turkey"]


def load_jloss():
    df, _ = pyreadstat.read_dta("Jloss.dta")
    df = df.dropna(subset=["jloss"]).copy()
    df["country"] = df["country"].str.lower().map(JLOSS_NAMEMAP)
    df = df.dropna(subset=["country"])
    df["time"] = df["time"].astype(int)
    df["year"] = df["time"] // 10
    df["q"] = df["time"] % 10
    df["quarter"] = df["year"].astype(str) + "Q" + df["q"].astype(str)
    out = df.rename(columns={"jloss": "JLoss"})[["country", "quarter", "JLoss"]]
    print(f"  JLoss   : {out.shape[0]} obs, {out['country'].nunique()} paises "
          f"-> {sorted(out['country'].unique())}")
    return out


def load_gar():
    g = pd.read_csv("gar_panel_all15.csv")
    g["country"] = g["country"].str.lower().str.replace(" ", "", regex=False)
    keep = [c for c in ["country", "quarter", "GaR", "prob_neg", "ES", "ER",
                        "mean", "std", "iqr_05_95", "skew", "kurt", "n_train"]
            if c in g.columns]
    g = g[keep]
    print(f"  GaR     : {g.shape[0]} obs, {g['country'].nunique()} paises")
    return g


def load_embi_latam():
    raw = pd.read_excel("Serie_Historica_Spread_del_EMBI.xlsx", header=1)
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
    out["embi_source"] = "BCRP_real"
    print(f"  EMBI LatAm (BCRP, real): {out.shape[0]} obs, "
          f"{sorted(out['country'].unique())}")
    return out


def load_embi_extended():
    e = pd.read_csv("EMBI_real_8countries_2006_2014.csv")
    e = e[e["freq"] == "quarterly"].copy()
    e = e.rename(columns={"period": "quarter"})[["country", "quarter", "EMBI_bps"]]
    e["embi_source"] = "GFSR_real"
    print(f"  EMBI extendido (GFSR, real): {e.shape[0]} obs, "
          f"{sorted(e['country'].unique())}")
    return e


def main():
    print("--- cargando fuentes ---")
    jloss = load_jloss()
    gar = load_gar()
    embi_latam = load_embi_latam()
    embi_ext = load_embi_extended()

    gar_latam = gar[gar["country"].isin(LATAM)]
    jloss_latam = jloss[jloss["country"].isin(LATAM)]

    panel_latam = (embi_latam.merge(jloss_latam, on=["country", "quarter"], how="inner")
                              .merge(gar_latam, on=["country", "quarter"], how="inner"))
    panel_latam["JLoss_x_GaR"] = panel_latam["JLoss"] * panel_latam["GaR"]
    panel_latam["t"] = pd.PeriodIndex(panel_latam["quarter"], freq="Q")
    panel_latam = panel_latam.sort_values(["country", "t"]).drop(columns=["t"]).reset_index(drop=True)
    panel_latam.to_csv("Panel_final_LatAm_v2.csv", index=False)

    print("\n=== NUCLEO LATAM v2 (EMBI real x JLoss x GaR all15) ===")
    print("shape:", panel_latam.shape)
    for c, g in panel_latam.groupby("country"):
        print(f"  {c:9s} n={len(g):3d}  {g['quarter'].min()} -> {g['quarter'].max()}")

    embi_all = pd.concat([embi_latam, embi_ext], ignore_index=True)
    panel_ext = (embi_all.merge(jloss, on=["country", "quarter"], how="inner")
                          .merge(gar, on=["country", "quarter"], how="inner"))
    panel_ext["JLoss_x_GaR"] = panel_ext["JLoss"] * panel_ext["GaR"]
    panel_ext["t"] = pd.PeriodIndex(panel_ext["quarter"], freq="Q")
    panel_ext = panel_ext.sort_values(["country", "t"]).drop(columns=["t"]).reset_index(drop=True)
    panel_ext.to_csv("Panel_extended_15paises.csv", index=False)

    print("\n=== PANEL EXTENDIDO (EMBI real x GaR x JLoss, todos los paises con interseccion) ===")
    print("shape:", panel_ext.shape)
    for c, g in panel_ext.groupby("country"):
        print(f"  {c:12s} n={len(g):3d}  {g['quarter'].min()} -> {g['quarter'].max()}  "
              f"fuente EMBI: {g['embi_source'].unique()}")

    faltan = sorted(set(TARGET15) - set(panel_ext["country"].unique()))
    print("\nPaises del panel de 15 SIN observaciones en el panel extendido:", faltan)


if __name__ == "__main__":
    main()
