# -*- coding: utf-8 -*-
"""
analisis_jloss_bloomberg.py
===========================
Re-hace el panel de regresiones y el analisis principal sustituyendo el JLoss
antiguo (Jloss.dta / v8) por el JLoss recalculado con datos Bloomberg
(1_Codigo/JLoss_reconstruction/jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv).

NO regenera EMBI, GaR ni controles: toma los paneles finales tal como estan en
disco y solo intercambia la columna JLoss (merge country x quarter), recomputa
las interacciones y vuelve a estimar:

  1. theta (JLoss x GaR) -- M2 (FE pais+tiempo) y M3 (+ controles domesticos),
     errores Driscoll-Kraay (kernel bartlett), replicando NUMEROS_CANONICOS.md.
  2. H4a / H4b -- triple interaccion JLoss x D x HHI (logica de fase5_estimacion_real.py).

Salidas -> carpeta jloss_bloomberg_analisis/:
  Panel_final_all17_bbg.csv, Panel_extended_bbg.csv,
  panel_real_final17_bbg.csv, panel_real_ext11_bbg.csv,
  theta_comparacion.csv, fase5_comparacion.csv, RESUMEN.md
"""
import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

HERE = os.path.dirname(os.path.abspath(__file__))
JLOSS_BBG = os.path.normpath(os.path.join(
    HERE, "..", "JLoss_reconstruction", "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv"))
OUT = os.path.join(HERE, "jloss_bloomberg_analisis")
os.makedirs(OUT, exist_ok=True)

CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]


def load_jloss_bbg(drop_below_min=False):
    j = pd.read_csv(JLOSS_BBG)
    j["country"] = j["countryname"].str.lower()
    j = j.dropna(subset=["JLoss"])
    if drop_below_min and "below_min_banks" in j.columns:
        j = j[~j["below_min_banks"].fillna(False)]
    return j[["country", "quarter", "JLoss", "n_banks"]].rename(columns={"JLoss": "JLoss_bbg"})


def swap_jloss(panel_path, drop_below_min=False):
    """Devuelve el panel con JLoss viejo y JLoss_bbg lado a lado (solo filas con match)."""
    p = pd.read_csv(panel_path)
    p["country"] = p["country"].str.lower()
    j = load_jloss_bbg(drop_below_min)
    m = p.merge(j, on=["country", "quarter"], how="left")
    return m


# ----------------------------------------------------------------------
# 1. theta: JLoss x GaR  (M2 sin controles, M3 con controles)
# ----------------------------------------------------------------------
def fit_theta(df, jloss_col, use_ctrls, label):
    d = df.copy()
    d["GaR_pp"] = d["GaR"] * 100.0
    need = ["EMBI_bps", jloss_col, "GaR_pp"]
    ctrls = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 0] if use_ctrls else []
    if use_ctrls and not ctrls:
        return None  # no hay controles domesticos en esta base (M3 == M2)
    d = d.dropna(subset=need + ctrls).copy()
    if d["country"].nunique() < 2 or len(d) < 20:
        return None
    d["JLoss_c"] = d[jloss_col] - d[jloss_col].mean()
    d["GaR_c"] = d["GaR_pp"] - d["GaR_pp"].mean()
    d["JxG"] = d["JLoss_c"] * d["GaR_c"]
    rhs = ["JLoss_c", "GaR_c", "JxG"] + ctrls
    formula = f"EMBI_bps ~ {' + '.join(rhs)} + EntityEffects + TimeEffects"
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    m = PanelOLS.from_formula(formula, d.set_index(["country", "t"])).fit(
        cov_type="kernel", kernel="bartlett")
    return dict(label=label, N=int(m.nobs), paises=d["country"].nunique(),
                b_JLoss=m.params["JLoss_c"], b_GaR=m.params["GaR_c"],
                theta=m.params["JxG"], se_theta=m.std_errors["JxG"],
                t_theta=m.tstats["JxG"], p_theta=m.pvalues["JxG"])


def run_theta_block(name, panel_path, drop_below_min=False):
    m = swap_jloss(panel_path, drop_below_min)
    rows = []
    for spec, uc in [("M2 (FE pais+tiempo)", False), ("M3 (+controles dom.)", True)]:
        old = fit_theta(m, "JLoss", uc, f"{name} | {spec} | JLoss v8/dta")
        new = fit_theta(m, "JLoss_bbg", uc, f"{name} | {spec} | JLoss Bloomberg")
        for r in (old, new):
            if r:
                rows.append(r)
        if old and new:
            print(f"  {name:14s} {spec:22s}  theta  v8={old['theta']:+.4f} (t={old['t_theta']:+.2f}, N={old['N']})"
                  f"   bbg={new['theta']:+.4f} (t={new['t_theta']:+.2f}, N={new['N']})")
    return rows, m


# ----------------------------------------------------------------------
# 2. fase5 -- H4a/H4b, triple interaccion  (replica fase5_estimacion_real.py)
# ----------------------------------------------------------------------
XCOLS = ["JLoss_c", "D_c", "JL_D", "JL_D_H", "JL_H", "D_H"]


def prep_f5(df, jcol, hhicol):
    d = df.dropna(subset=["EMBI", jcol, "D", hhicol]).copy()
    d["JLoss_c"] = d[jcol] - d[jcol].mean()
    d["D_c"] = d["D"] - d["D"].mean()
    d["HHI_c"] = d[hhicol] - d[hhicol].mean()
    d["JL_D"] = d["JLoss_c"] * d["D_c"]
    d["JL_D_H"] = d["JL_D"] * d["HHI_c"]
    d["JL_H"] = d["JLoss_c"] * d["HHI_c"]
    d["D_H"] = d["D_c"] * d["HHI_c"]
    return d


def fit_f5(df, jcol, hhicol, use_debt):
    d = prep_f5(df, jcol, hhicol)
    ctrl = " + debt" if (use_debt and "debt" in d and d["debt"].notna().all()) else ""
    m = PanelOLS.from_formula(
        f"EMBI ~ {' + '.join(XCOLS)}{ctrl} + EntityEffects + TimeEffects",
        d.set_index(["country", "time"])).fit(cov_type="clustered", cluster_entity=True)
    return dict(N=int(m.nobs), paises=d["country"].nunique(),
                b3=m.params["JL_D"], t3=m.tstats["JL_D"],
                b4=m.params["JL_D_H"], t4=m.tstats["JL_D_H"])


def run_fase5_block(name, tmpl_path, use_debt):
    p = pd.read_csv(tmpl_path)
    p["country"] = p["country"].str.lower()
    m = p.merge(load_jloss_bbg(False), on=["country", "quarter"], how="left")
    m_dbm = p.merge(load_jloss_bbg(True).rename(columns={"JLoss_bbg": "JLoss_bbg_dbm"}),
                    on=["country", "quarter"], how="left")
    m["JLoss_bbg_dbm"] = m_dbm["JLoss_bbg_dbm"]
    rows = []
    for hhicol, lbl in [("HHI", "estructural"), ("HHI_anual", "anual")]:
        for jcol, tag in [("JLoss", "v8/dta"), ("JLoss_bbg", "Bloomberg"),
                          ("JLoss_bbg_dbm", "Bloomberg (>=3 bancos)")]:
            try:
                r = fit_f5(m, jcol, hhicol, use_debt)
                r.update(base=name, HHI=lbl, jloss=tag)
                rows.append(r)
            except Exception as ex:
                print(f"    [!] {name} {lbl} {tag}: {str(ex)[:70]}")
    for lbl in ["estructural", "anual"]:
        o = next((x for x in rows if x["HHI"] == lbl and x["jloss"] == "v8/dta"), None)
        n = next((x for x in rows if x["HHI"] == lbl and x["jloss"] == "Bloomberg"), None)
        if o and n:
            print(f"  {name:12s} HHI {lbl:11s}  b3 v8={o['b3']:+.2f}(t{o['t3']:+.2f}) bbg={n['b3']:+.2f}(t{n['t3']:+.2f})"
                  f"   |  b4 v8={o['b4']:+.0f}(t{o['t4']:+.2f}) bbg={n['b4']:+.0f}(t{n['t4']:+.2f})")
    return rows, m


def main():
    print(f"JLoss Bloomberg: {JLOSS_BBG}")
    jb = pd.read_csv(JLOSS_BBG)
    print(f"  {len(jb)} filas, {jb['countryname'].nunique()} paises, "
          f"{jb['quarter'].min()}..{jb['quarter'].max()}, "
          f"below_min_banks={int(jb['below_min_banks'].sum())}\n")

    print("=== 0. concordancia JLoss v8/dta  vs  Bloomberg (interseccion country x quarter) ===")
    diag = []
    for nm, f in [("all17", "Panel_final_all17.csv"), ("extendido", "Panel_extended_15paises.csv")]:
        mm = swap_jloss(os.path.join(HERE, f)).dropna(subset=["JLoss", "JLoss_bbg"])
        rho = mm["JLoss"].corr(mm["JLoss_bbg"])
        wrho = mm.groupby("country").apply(lambda g: g["JLoss"].corr(g["JLoss_bbg"])).mean()
        diag.append(dict(base=nm, n=len(mm), corr=rho, corr_within=wrho,
                         sd_v8=mm["JLoss"].std(), sd_bbg=mm["JLoss_bbg"].std()))
        print(f"  {nm:10s} n={len(mm)}  corr={rho:.3f}  corr_within_pais={wrho:.3f}  "
              f"sd: v8={mm['JLoss'].std():.2f} bbg={mm['JLoss_bbg'].std():.2f}")
    pd.DataFrame(diag).to_csv(os.path.join(OUT, "concordancia_jloss.csv"), index=False)

    print("\n=== 1. theta (JLoss x GaR)  --  v8/dta  vs  Bloomberg ===")
    trows = []
    tr, m_all17 = run_theta_block("all17 (5 LatAm)", os.path.join(HERE, "Panel_final_all17.csv"))
    trows += tr
    tr, m_ext = run_theta_block("extendido (11)", os.path.join(HERE, "Panel_extended_15paises.csv"))
    trows += tr
    pd.DataFrame(trows).to_csv(os.path.join(OUT, "theta_comparacion.csv"), index=False)
    m_all17.to_csv(os.path.join(OUT, "Panel_final_all17_bbg.csv"), index=False)
    m_ext.to_csv(os.path.join(OUT, "Panel_extended_bbg.csv"), index=False)

    print("\n=== 2. H4a/H4b (JLoss x D x HHI)  --  v8/dta  vs  Bloomberg ===")
    frows = []
    fr, pr17 = run_fase5_block("final17", os.path.join(HERE, "panel_real_final17.csv"), use_debt=True)
    frows += fr
    fr, pr11 = run_fase5_block("ext11", os.path.join(HERE, "panel_real_ext11.csv"), use_debt=False)
    frows += fr
    pd.DataFrame(frows).to_csv(os.path.join(OUT, "fase5_comparacion.csv"), index=False)
    pr17.to_csv(os.path.join(OUT, "panel_real_final17_bbg.csv"), index=False)
    pr11.to_csv(os.path.join(OUT, "panel_real_ext11_bbg.csv"), index=False)

    # ---- RESUMEN.md ----
    td = pd.DataFrame(trows)
    fd = pd.DataFrame(frows)
    with open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf-8") as fh:
        fh.write("# JLoss Bloomberg -> panel de regresiones y analisis principal\n\n")
        fh.write(f"Generado re-ejecutando `analisis_jloss_bloomberg.py`. "
                 f"JLoss nuevo: `Panel_JLoss_v9_bloomberg.csv` (motor v8, rho=0.4, PD Merton/KMV).\n\n")
        fh.write("## 1. theta = JLoss x GaR sobre EMBI\n\n")
        fh.write("| base | spec | fuente JLoss | N | theta | t | p |\n|---|---|---|---:|---:|---:|---:|\n")
        for _, r in td.iterrows():
            b, s, src = r["label"].split(" | ")
            fh.write(f"| {b} | {s} | {src} | {r['N']} | {r['theta']:+.4f} | {r['t_theta']:+.2f} | {r['p_theta']:.3f} |\n")
        fh.write("\n## 2. H4a (b3>0) / H4b (b4>0)\n\n")
        fh.write("| base | HHI | fuente JLoss | N | b3 | t3 | b4 | t4 |\n|---|---|---|---:|---:|---:|---:|---:|\n")
        for _, r in fd.iterrows():
            fh.write(f"| {r['base']} | {r['HHI']} | {r['jloss']} | {r['N']} | {r['b3']:+.2f} | {r['t3']:+.2f} "
                     f"| {r['b4']:+.1f} | {r['t4']:+.2f} |\n")
        fh.write("\n## 0. Concordancia JLoss v8/dta vs Bloomberg\n\n")
        fh.write("| base | n | corr | corr within-pais | sd v8 | sd bbg |\n|---|---:|---:|---:|---:|---:|\n")
        for d in diag:
            fh.write(f"| {d['base']} | {d['n']} | {d['corr']:.3f} | {d['corr_within']:.3f} "
                     f"| {d['sd_v8']:.2f} | {d['sd_bbg']:.2f} |\n")
        fh.write("\n## Referencia (NUMEROS_CANONICOS.md, JLoss v8)\n")
        fh.write("- theta M3 all17 = -0.338 (N=253, t=-2.22, p=0.028)\n")
        fh.write("- theta M2 extendido = -0.212 (N=374, t=-1.83, p=0.069)\n")
        fh.write("- b4 ext11 (HHI estructural) = +721 (t=2.98)\n")
    print(f"\nGuardado en {OUT}/")


if __name__ == "__main__":
    main()
