# -*- coding: utf-8 -*-
"""
p1_build_panels.py  --  Panel de regresiones anclado en Bloomberg
=================================================================
Reconstruye las dos bases de la tesis usando, como insumos primarios:
  - JLoss  : Panel_JLoss_v9_bloomberg.csv  (motor v8, PD Merton/KMV, datos Bloomberg)
  - EMBI   : CDS soberano 5Y de Bloomberg  (output_macro/<pais>/EMBI_<pais>.csv), pb
  - global : VIX, UST10Y, US HY spread de Bloomberg (output_macro/GLOBAL/)
  - GaR    : gar_panel_all17.csv  (regresion cuantilica CEMLA; sus insumos FCI son
             estadisticas nacionales -- CPI/PIB/bolsa/REER/10Y -- que NO forman parte
             de la extraccion Bloomberg y se mantienen; ver RESUMEN)
  - controles domesticos: controls_panel.csv  (5 LatAm, deuda/fiscal/reservas/CA/infl/reer)
  - HHI    : hhi_nivel.csv + hhi_anual.csv (+ GFDD via API para paises nuevos)

Salidas -> 1_Codigo/Panel/bbg/
  embi_bbg_quarterly.csv        CDS 5Y -> trimestral, todos los paises + flag de cobertura
  cobertura_embi_bbg.csv        ventana y n de trimestres por pais
  Panel_principal_bbg.csv       5 LatAm, con controles domesticos
  Panel_ampliado_bbg.csv        12 paises con CDS continuo 2004-2026 + GaR + JLoss
  panel_real_principal_bbg.csv  plantilla fase5 (H4a/H4b), 5 paises
  panel_real_ampliado_bbg.csv   plantilla fase5, subset con HHI disponible
"""
import json
import os
import urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)                      # 1_Codigo/Panel
COD = os.path.dirname(PANEL)                       # 1_Codigo
BBG_MACRO = os.path.join(COD, "Bloomberg_extraction", "output_macro")
JLOSS_BBG = os.path.join(COD, "JLoss_reconstruction", "jloss_bloomberg",
                         "Panel_JLoss_v9_bloomberg.csv")
OUT = HERE

LATAM = ["brazil", "chile", "colombia", "mexico", "peru"]
# paises con CDS Bloomberg continuo (>=60 trimestres, 2004->2026) e insumos GaR.
# southkorea EXCLUIDO: su valor de mercado del equity es ~4% del punto de default
# (E/D mediana 0.038 vs 0.15-0.34 en el resto del panel), reflejo del "Korea discount"
# estructural en la valoracion de los holdings bancarios (P/B ~0.3-0.5 persistente por
# gobernanza/payout, no por solvencia). El Merton-KMV lo lee como default inminente
# (PD mediana 0.55; JLoss 25-47) -> serie no comparable. La reconstruccion regulatoria
# v8 tampoco incluia Corea. Ver bbg/DIAGNOSTICO_COREA.md.
AMPLIADO = ["brazil", "chile", "china", "colombia", "indonesia", "malaysia", "mexico",
            "peru", "philippines", "southafrica", "turkey"]
EXCLUIDOS = {"southkorea": "E/D=0.038 (Korea discount); Merton PD no creible"}
MIN_Q_EMBI = 60          # trimestres minimos de CDS para considerar la serie utilizable

GFDD_ISO = {"malaysia": "MYS", "philippines": "PHL", "southkorea": "KOR",
            "india": "IND", "argentina": "ARG"}


# ----------------------------------------------------------------------
def embi_quarterly():
    """CDS 5Y diario (pb) -> media trimestral, por pais."""
    rows, cov = [], []
    for d in sorted(os.listdir(BBG_MACRO)):
        f = os.path.join(BBG_MACRO, d, f"EMBI_{d}.csv")
        if not os.path.isfile(f):
            continue
        s = pd.read_csv(f)
        s["DATES"] = pd.to_datetime(s["DATES"], dayfirst=True, errors="coerce")
        s = s.dropna(subset=["DATES", "EMBI"])
        s = s[s["EMBI"] > 0].sort_values("DATES")
        if s.empty:
            continue
        q = (s.set_index("DATES")["EMBI"].resample("QE").mean().dropna()
             .rename("EMBI_bps").reset_index())
        q["quarter"] = q["DATES"].dt.to_period("Q").astype(str)
        q["country"] = d
        rows.append(q[["country", "quarter", "EMBI_bps"]])
        cov.append(dict(country=d, primer=q["quarter"].min(), ultimo=q["quarter"].max(),
                        n_q=len(q), usable=len(q) >= MIN_Q_EMBI))
    embi = pd.concat(rows, ignore_index=True)
    covdf = pd.DataFrame(cov).sort_values("n_q", ascending=False)
    embi.to_csv(os.path.join(OUT, "embi_bbg_quarterly.csv"), index=False)
    covdf.to_csv(os.path.join(OUT, "cobertura_embi_bbg.csv"), index=False)
    print("EMBI Bloomberg (CDS 5Y) — cobertura trimestral:")
    print(covdf.to_string(index=False))
    return embi


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
    """VIX, UST10Y, US HY spread de Bloomberg -> trimestral."""
    g = os.path.join(BBG_MACRO, "GLOBAL")
    out = None
    for name, col in [("VIX", "VIX"), ("UST10Y", "UST10Y"), ("HY_SPREAD", "US_HY_spread")]:
        f = os.path.join(g, f"{name}.csv")
        s = pd.read_csv(f)
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
    # spread on/off-run: se conserva del archivo previo (no es Bloomberg-primario)
    prev = pd.read_csv(os.path.join(PANEL, "global_controls_quarterly.csv"))
    out = out.merge(prev[["quarter", "OnOffRun_spread", "OnOffRun_spread_log"]],
                    on="quarter", how="left")
    out.to_csv(os.path.join(OUT, "global_controls_bbg.csv"), index=False)
    return out


def load_controls():
    c = pd.read_csv(os.path.join(PANEL, "controls_panel.csv"))
    c["country"] = c["country"].str.lower()
    return c


def fetch_hhi_missing(countries):
    """GFDD.OI.01 (concentracion 3 bancos, %) via API World Bank para paises sin HHI local."""
    iso = ",".join(GFDD_ISO[c] for c in countries if c in GFDD_ISO)
    if not iso:
        return pd.DataFrame(columns=["country", "year", "HHI_anual"])
    url = (f"https://api.worldbank.org/v2/country/{iso.replace(',', ';')}"
           f"/indicator/GFDD.OI.01?format=json&per_page=600&date=2004:2023")
    try:
        r = json.load(urllib.request.urlopen(url, timeout=20))[1]
    except Exception as e:
        print(f"  [!] GFDD API fallo: {e}")
        return pd.DataFrame(columns=["country", "year", "HHI_anual"])
    inv = {v: k for k, v in GFDD_ISO.items()}
    rows = [dict(country=inv.get(x["countryiso3code"]), year=int(x["date"]),
                 HHI_anual=x["value"] / 100.0)
            for x in r if x["value"] is not None and x["countryiso3code"] in inv]
    return pd.DataFrame(rows)


def build_hhi():
    niv = pd.read_csv(os.path.join(PANEL, "hhi_nivel.csv"))
    niv["country"] = niv["country"].str.lower()
    anu = pd.read_csv(os.path.join(PANEL, "hhi_anual.csv"))
    anu["country"] = anu["country"].str.lower()
    missing = [c for c in AMPLIADO if c not in set(niv["country"])]
    extra = fetch_hhi_missing(missing)
    if not extra.empty:
        anu = pd.concat([anu, extra], ignore_index=True)
        niv2 = (extra.groupby("country")["HHI_anual"].median().rename("HHI").reset_index())
        niv = pd.concat([niv, niv2], ignore_index=True)
        print(f"  HHI via GFDD API para: {sorted(extra['country'].unique())}")
    return niv, anu


# ----------------------------------------------------------------------
def assemble(countries, embi, jl, gar, glob, controls, hhi_niv, with_controls):
    p = (embi[embi["country"].isin(countries)]
         .merge(jl, on=["country", "quarter"], how="inner")
         .merge(gar, on=["country", "quarter"], how="inner")
         .merge(glob, on="quarter", how="left"))
    if with_controls:
        p = p.merge(controls, on=["country", "quarter"], how="left")
    p = p.merge(hhi_niv.rename(columns={"HHI": "HHI_struct"}), on="country", how="left")
    p["GaR_pp"] = p["GaR"] * 100.0
    p["JLoss_x_GaR"] = (p["JLoss"] - p["JLoss"].mean()) * (p["GaR_pp"] - p["GaR_pp"].mean())
    p["pi"] = pd.PeriodIndex(p["quarter"], freq="Q")
    p = p.sort_values(["country", "pi"]).drop(columns="pi").reset_index(drop=True)
    return p


def to_template(panel, hhi_niv, hhi_anu, with_debt):
    """formato fase5: country,time,quarter,EMBI,JLoss,D,HHI,HHI_anual,debt,growth_q,gfac"""
    d = panel.copy()
    d["EMBI"] = d["EMBI_bps"]
    d["D"] = -d["GaR"]
    d = d.merge(hhi_niv.rename(columns={"HHI": "HHI"}), on="country", how="left")
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    d = d.merge(hhi_anu, on=["country", "year"], how="left")
    d["HHI_anual"] = d.groupby("country")["HHI_anual"].transform(
        lambda s: s.ffill().bfill())
    d["debt"] = d["debt_gdp"] if (with_debt and "debt_gdp" in d) else np.nan
    d["growth_q"] = np.nan
    d["gfac"] = d.get("VIX", np.nan)
    d["time"] = d.groupby("country").cumcount()
    cols = ["country", "time", "quarter", "EMBI", "JLoss", "D", "HHI", "HHI_anual",
            "debt", "growth_q", "gfac"]
    return d[cols].dropna(subset=["EMBI", "JLoss", "D"])


def main():
    print("=" * 72)
    embi = embi_quarterly()
    jl = load_jloss()
    gar = load_gar()
    glob = load_global_bbg()
    controls = load_controls()
    hhi_niv, hhi_anu = build_hhi()

    principal = assemble(LATAM, embi, jl, gar, glob, controls, hhi_niv, True)
    ampliado = assemble(AMPLIADO, embi, jl, gar, glob, controls, hhi_niv, False)
    principal.to_csv(os.path.join(OUT, "Panel_principal_bbg.csv"), index=False)
    ampliado.to_csv(os.path.join(OUT, "Panel_ampliado_bbg.csv"), index=False)

    tpl_p = to_template(principal, hhi_niv, hhi_anu, True)
    tpl_a = to_template(ampliado, hhi_niv, hhi_anu, False)
    tpl_p.to_csv(os.path.join(OUT, "panel_real_principal_bbg.csv"), index=False)
    tpl_a.to_csv(os.path.join(OUT, "panel_real_ampliado_bbg.csv"), index=False)

    print("\n--- Panel principal (Bloomberg) ---")
    for c, g in principal.groupby("country"):
        print(f"  {c:12s} n={len(g):3d}  {g['quarter'].min()}..{g['quarter'].max()}  "
              f"EMBI~{g['EMBI_bps'].mean():.0f}pb  JLoss~{g['JLoss'].mean():.2f}")
    print(f"  TOTAL {len(principal)} obs | con controles dom.: "
          f"{principal['debt_gdp'].notna().sum() if 'debt_gdp' in principal else 0}")
    print("\n--- Panel ampliado (Bloomberg) ---")
    for c, g in ampliado.groupby("country"):
        print(f"  {c:12s} n={len(g):3d}  {g['quarter'].min()}..{g['quarter'].max()}  "
              f"EMBI~{g['EMBI_bps'].mean():.0f}pb  JLoss~{g['JLoss'].mean():.2f}  "
              f"HHI={g['HHI_struct'].iloc[0] if g['HHI_struct'].notna().any() else 'NA'}")
    print(f"  TOTAL {len(ampliado)} obs, {ampliado['country'].nunique()} paises")
    print(f"\nTemplates fase5: principal={len(tpl_p)} filas, ampliado={len(tpl_a)} filas "
          f"({tpl_a['HHI'].notna().sum()} con HHI)")


if __name__ == "__main__":
    main()
