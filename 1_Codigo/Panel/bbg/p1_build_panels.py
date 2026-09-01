# -*- coding: utf-8 -*-
"""
p1_build_panels.py  --  UN SOLO panel de regresiones.

Variable dependiente PRINCIPAL: el spread EMBI Global Diversified (J.P. Morgan), en pb,
siguiendo a Chari et al. (2024). El CDS soberano a 5 años de Bloomberg se conserva como
serie secundaria para robustez.

Insumos primarios:
  - EMBI   : 2_Datos/embi.xlsx  (spread EMBI Global por pais, diario 2000-2026) -> EMBI_bps
  - CDS 5Y : output_macro/<pais>/EMBI_<pais>.csv (Bloomberg) -> CDS_bps  (robustez)
  - JLoss  : Panel_JLoss_v9_bloomberg.csv  (motor v8/v9, PD Merton/KMV, datos Bloomberg)
  - global : VIX, UST10Y, US HY spread de Bloomberg (output_macro/GLOBAL/)
  - GaR    : gar_panel_all17.csv  (regresion cuantilica CEMLA; insumos FCI = estadisticas
             nacionales, ver Anexo B)
  - controles domesticos: controls_all_bbg.csv (p0, los 16 paises)
  - HHI    : hhi_nivel.csv + hhi_anual.csv (+ GFDD via API para los paises nuevos)

El panel incluye TODAS las economias de las que hay datos. Un pais sin EMBI o sin GaR
aparece en el roster pero no aporta filas a la estimacion. Corea del Sur y Bulgaria quedan
EXCLUIDAS: JLoss no valido a nivel pais (ver DIAGNOSTICO_COREA.md).

Salidas -> 1_Codigo/Panel/bbg/
  embi_bbg_quarterly.csv        EMBI + CDS -> trimestral, por pais + flag de cobertura
  cobertura_panel_bbg.csv       por pais: JLoss / GaR / EMBI_q / CDS_q / en_estimacion
  Panel_bloomberg.csv           EL panel (country, quarter, EMBI_bps, CDS_bps, JLoss, GaR...,
                                6 controles, VIX/UST10Y/HY, HHI_struct)
  panel_real_bbg.csv            plantilla fase5 (H4a/H4b): country,time,quarter,EMBI,JLoss,D,
                                HHI,HHI_anual,debt,growth_q,gfac
"""
import json
import os
import urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)
COD = os.path.dirname(PANEL)
BBG_MACRO = os.path.join(COD, "Bloomberg_extraction", "output_macro")
JLOSS_BBG = os.path.join(COD, "JLoss_reconstruction", "jloss_bloomberg",
                         "Panel_JLoss_v9_bloomberg.csv")
EMBI_XLSX = os.path.join(COD, "..", "2_Datos", "embi.xlsx")
OUT = HERE

# nombre de columna (xlsx, en espanol) -> country (en ingles, minusculas)
EMBI_MAP = {
    "Brasil": "brazil", "Chile": "chile", "China": "china", "Colombia": "colombia",
    "Hungria": "hungary", "India": "india", "Malasia": "malaysia", "Mexico": "mexico",
    "Peru": "peru", "Polonia": "poland", "Rumania": "romania", "Turquia": "turkey",
    "Filipinas": "philippines", "Indonesia": "indonesia", "Sudafrica": "southafrica",
}

EXCLUIDOS = {
    "southkorea": "JLoss no valido: E/D mercado ~0.04 (Korea discount), Merton PD ~0.55, "
                  "JLoss 25-47 (ver DIAGNOSTICO_COREA.md)",
    "bulgaria": "JLoss no sistemico: 1 banco cotizado (FIBank), 76/76 trimestres "
                "below_min_banks, JLoss mediana 29 -- no es una medida a nivel pais",
}
MIN_Q_CDS_UTIL = 60          # umbral para marcar la serie de CDS como "continua"
GFDD_ISO = {"malaysia": "MYS", "philippines": "PHL", "southkorea": "KOR",
            "india": "IND", "argentina": "ARG", "egypt": "EGY", "russia": "RUS",
            "hungary": "HUN", "pakistan": "PAK"}


# ----------------------------------------------------------------------
def cds_quarterly():
    """CDS 5Y diario (pb) -> media trimestral, por pais. Serie SECUNDARIA (robustez)."""
    rows = []
    for d in sorted(os.listdir(BBG_MACRO)):
        f = os.path.join(BBG_MACRO, d, f"EMBI_{d}.csv")   # el archivo se llama EMBI_ pero contiene CDS
        if not os.path.isfile(f):
            continue
        s = pd.read_csv(f)
        s["DATES"] = pd.to_datetime(s["DATES"], dayfirst=True, errors="coerce")
        s = s.dropna(subset=["DATES", "EMBI"])
        s = s[s["EMBI"] > 0].sort_values("DATES")
        if s.empty:
            continue
        q = (s.set_index("DATES")["EMBI"].resample("QE").mean().dropna()
             .rename("CDS_bps").reset_index())
        q["quarter"] = q["DATES"].dt.to_period("Q").astype(str)
        q["country"] = d
        rows.append(q[["country", "quarter", "CDS_bps"]])
    return pd.concat(rows, ignore_index=True)


def embi_quarterly():
    """Spread EMBI Global Diversified diario (pb) -> media trimestral, por pais.
    Variable dependiente PRINCIPAL (Chari et al. 2024)."""
    x = pd.read_excel(EMBI_XLSX)
    x = x.rename(columns={"Fecha": "date"})
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"])
    x["quarter"] = x["date"].dt.to_period("Q").astype(str)
    cols = [c for c in x.columns if c in EMBI_MAP]
    q = x.groupby("quarter")[cols].mean().reset_index()
    q = q.rename(columns=EMBI_MAP)
    long = (q.melt(id_vars="quarter", var_name="country", value_name="EMBI_bps")
            .dropna(subset=["EMBI_bps"]))
    long = long[long["EMBI_bps"] > 0]

    cds = cds_quarterly()
    both = long.merge(cds, on=["country", "quarter"], how="outer").sort_values(["country", "quarter"])
    both.to_csv(os.path.join(OUT, "embi_bbg_quarterly.csv"), index=False)

    cov = []
    for c, g in both.groupby("country"):
        ne, nc = int(g["EMBI_bps"].notna().sum()), int(g["CDS_bps"].notna().sum())
        cov.append(dict(country=c, embi_q=ne, cds_q=nc,
                        embi_primer=g.loc[g["EMBI_bps"].notna(), "quarter"].min(),
                        embi_ultimo=g.loc[g["EMBI_bps"].notna(), "quarter"].max(),
                        embi_cobertura=("continua" if ne >= MIN_Q_CDS_UTIL else
                                        "rala" if ne >= 5 else "sin serie"),
                        cds_cobertura=("continua" if nc >= MIN_Q_CDS_UTIL else
                                       "rala" if nc >= 5 else "sin serie")))
    covdf = pd.DataFrame(cov).sort_values("embi_q", ascending=False)
    return both[["country", "quarter", "EMBI_bps", "CDS_bps"]], covdf


def load_jloss():
    j = pd.read_csv(JLOSS_BBG)
    j["country"] = j["countryname"].str.lower()
    j = j.dropna(subset=["JLoss"])
    return j[["country", "quarter", "JLoss", "n_banks", "below_min_banks"]]


def load_gar():
    g = pd.read_csv(os.path.join(PANEL, "gar_panel_all17.csv"))
    g["country"] = g["country"].str.lower()
    keep = [c for c in ["country", "quarter", "GaR", "ES", "prob_neg", "skew", "std",
                        "GaR_st", "n_train"] if c in g.columns]
    return g[keep].dropna(subset=["GaR"])


def load_global_bbg():
    g = os.path.join(BBG_MACRO, "GLOBAL")
    out = None
    for name, col in [("VIX", "VIX"), ("UST10Y", "UST10Y"), ("HY_SPREAD", "US_HY_spread")]:
        s = pd.read_csv(os.path.join(g, f"{name}.csv"))
        dcol = s.columns[0]
        s[dcol] = pd.to_datetime(s[dcol], dayfirst=True, errors="coerce")
        s = s.dropna()
        vcol = s.columns[1]
        q = (s.set_index(dcol)[vcol].resample("QE").mean().dropna().rename(col).reset_index())
        q["quarter"] = q[dcol].dt.to_period("Q").astype(str)
        q = q[["quarter", col]]
        out = q if out is None else out.merge(q, on="quarter", how="outer")
    out["UST10Y_log"] = np.log(out["UST10Y"])
    out["US_HY_spread_log"] = np.log(out["US_HY_spread"])
    prev = pd.read_csv(os.path.join(PANEL, "global_controls_quarterly.csv"))
    out = out.merge(prev[["quarter", "OnOffRun_spread", "OnOffRun_spread_log"]],
                    on="quarter", how="left")
    out.to_csv(os.path.join(OUT, "global_controls_bbg.csv"), index=False)
    return out


def load_controls():
    c = pd.read_csv(os.path.join(HERE, "controls_all_bbg.csv"))
    c["country"] = c["country"].str.lower()
    return c


def fetch_hhi_missing(countries):
    iso = "/".join(GFDD_ISO[c] for c in countries if c in GFDD_ISO)
    if not iso:
        return pd.DataFrame(columns=["country", "year", "HHI_anual"])
    url = (f"https://api.worldbank.org/v2/country/{iso.replace('/', ';')}"
           f"/indicator/GFDD.OI.01?format=json&per_page=600&date=2000:2023")
    try:
        r = json.load(urllib.request.urlopen(url, timeout=25))[1]
    except Exception as e:
        print(f"  [!] GFDD API fallo: {e}")
        return pd.DataFrame(columns=["country", "year", "HHI_anual"])
    inv = {v: k for k, v in GFDD_ISO.items()}
    rows = [dict(country=inv.get(x["countryiso3code"]), year=int(x["date"]),
                 HHI_anual=x["value"] / 100.0)
            for x in r if x["value"] is not None and x["countryiso3code"] in inv]
    return pd.DataFrame(rows)


def build_hhi(roster):
    niv = pd.read_csv(os.path.join(PANEL, "hhi_nivel.csv")); niv["country"] = niv["country"].str.lower()
    anu = pd.read_csv(os.path.join(PANEL, "hhi_anual.csv")); anu["country"] = anu["country"].str.lower()
    missing = [c for c in roster if c not in set(niv["country"])]
    extra = fetch_hhi_missing(missing)
    if not extra.empty:
        anu = pd.concat([anu, extra], ignore_index=True)
        niv2 = extra.groupby("country")["HHI_anual"].median().rename("HHI").reset_index()
        niv = pd.concat([niv, niv2], ignore_index=True)
        print(f"  HHI via GFDD API para: {sorted(extra['country'].unique())}")
    still = [c for c in roster if c not in set(niv['country'])]
    if still:
        print(f"  [!] sin HHI: {still}")
    return niv, anu


# ----------------------------------------------------------------------
def main():
    print("=" * 72)
    embi, cov = embi_quarterly()
    jl = load_jloss()
    gar = load_gar()
    glob = load_global_bbg()
    controls = load_controls()

    jl_c = set(jl["country"]) - set(EXCLUIDOS)
    gar_c = set(gar["country"]) - set(EXCLUIDOS)
    # roster: toda economia con JLoss (no excluida). Se listan aunque no aporten a la estimacion.
    roster = sorted(jl_c)
    hhi_niv, hhi_anu = build_hhi(roster)

    # --- panel: JLoss x quarter para todo el roster, con lo demas mergeado (NaN donde falte) ---
    p = jl[jl["country"].isin(roster)].copy()
    p = p.merge(gar, on=["country", "quarter"], how="left")
    p = p.merge(embi, on=["country", "quarter"], how="left")          # EMBI_bps / CDS_bps NaN si faltan
    p = p.merge(glob, on="quarter", how="left")
    p = p.merge(controls, on=["country", "quarter"], how="left")
    p = p.merge(hhi_niv.rename(columns={"HHI": "HHI_struct"}), on="country", how="left")
    p["GaR_pp"] = p["GaR"] * 100.0
    jc, gc = p["JLoss"].mean(), p["GaR_pp"].mean()
    p["JLoss_x_GaR"] = (p["JLoss"] - jc) * (p["GaR_pp"] - gc)
    p["pi"] = pd.PeriodIndex(p["quarter"], freq="Q")
    p = p.sort_values(["country", "pi"]).drop(columns="pi").reset_index(drop=True)
    p.to_csv(os.path.join(OUT, "Panel_bloomberg.csv"), index=False)

    # --- cobertura por pais ---
    est = p.dropna(subset=["EMBI_bps", "JLoss", "GaR"])       # muestra de estimacion: EMBI + JLoss + GaR
    est_cds = p.dropna(subset=["CDS_bps", "JLoss", "GaR"])    # muestra de robustez con CDS
    covrows = []
    for c in roster:
        g = p[p.country == c]
        e = est[est.country == c]
        cc = cov[cov.country == c]
        covrows.append(dict(
            country=c, jloss_q=int(g["JLoss"].notna().sum()),
            gar_q=int(g["GaR"].notna().sum()),
            embi_q=int(cc["embi_q"].iloc[0]) if len(cc) else 0,
            cds_q=int(cc["cds_q"].iloc[0]) if len(cc) else 0,
            embi_cobertura=cc["embi_cobertura"].iloc[0] if len(cc) else "sin serie",
            n_estimacion=len(e),
            n_est_cds=len(est_cds[est_cds.country == c]),
            ventana_est=f"{e['quarter'].min()}..{e['quarter'].max()}" if len(e) else "-"))
    covdf = pd.DataFrame(covrows).sort_values("n_estimacion", ascending=False)
    covdf.to_csv(os.path.join(OUT, "cobertura_panel_bbg.csv"), index=False)

    # --- plantilla fase5 (un solo archivo) ---
    d = p.copy()
    d["EMBI"] = d["EMBI_bps"]
    d["D"] = -d["GaR"]
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    d = d.merge(hhi_niv.rename(columns={"HHI": "HHI"}), on="country", how="left")
    d = d.merge(hhi_anu, on=["country", "year"], how="left")
    d["HHI_anual"] = d.groupby("country")["HHI_anual"].transform(lambda s: s.ffill().bfill())
    d["debt"] = d["debt_gdp"]
    d["growth_q"] = np.nan
    d["gfac"] = d["VIX"]
    d["time"] = d.groupby("country").cumcount()
    tcols = ["country", "time", "quarter", "EMBI", "JLoss", "D", "HHI", "HHI_anual",
             "debt", "growth_q", "gfac"]
    d[tcols].dropna(subset=["EMBI", "JLoss", "D"]).to_csv(
        os.path.join(OUT, "panel_real_bbg.csv"), index=False)

    # --- reporte ---
    print(f"\nPanel_bloomberg.csv: {len(p)} filas (roster {len(roster)} paises)")
    print(f"  Estimacion principal (EMBI+JLoss+GaR): {len(est)} obs, {est.country.nunique()} paises")
    print(f"  Robustez con CDS (CDS+JLoss+GaR):      {len(est_cds)} obs, {est_cds.country.nunique()} paises")
    print(f"Excluido: {', '.join(EXCLUIDOS)}")
    print("\nCobertura por pais:")
    print(covdf.to_string(index=False))
    print("\nEconomias en el roster sin aporte a la estimacion:")
    for _, r in covdf[covdf.n_estimacion == 0].iterrows():
        motivo = "sin EMBI" if r["embi_q"] == 0 else ("sin GaR" if r["gar_q"] == 0 else "sin solape")
        print(f"  {r['country']:12s} ({motivo})")


if __name__ == "__main__":
    main()
