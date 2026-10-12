# -*- coding: utf-8 -*-
"""
p18_solapamiento_gar.py -- solapamiento entre el riesgo de cola (GaR) y las variables financieras.

Observacion del profesor guia (predefensa, 2026-10-09): el FCI que alimenta el GaR se construye con
variables financieras (bolsa, tasas, tipo de cambio) que se cruzan con JLoss (volatilidad accionaria
de los bancos) y con los factores financieros globales; parte de la varianza del riesgo de cola
podria estar explicada por regresores del lado derecho. Tres respuestas sobre la especificacion
PRINCIPAL (log-log rezagada, panel embiext, 13 paises):

  A. Diagnosticos: cuanto de D_{t-1} explican los factores globales, los efectos fijos y ln JLoss.
  B. Regresion en dos etapas: se limpia D_{t-1} de las variables financieras y se usa el residuo.
       B1. D ~ factores globales (VIX, Tesoro 10A, high yield, on/off-the-run) + EF pais
       B2. D ~ ln JLoss + EF pais + EF tiempo   (los EF de tiempo ya absorben todo factor global)
  C. GaR reconstruido SIN el bloque bursatil del FCI (build_fci_no_stx.py + gar_insample_robustez.py),
     comparado contra el GaR in-sample base (misma estimacion, con el bloque).

Salida: bbg/paper_solapamiento_numeros.csv. Reutiliza p13 (datos, fit) y p14 (base, shift).
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14

GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
GLOB = ["VIX", "UST10Y_log", "US_HY_spread_log", "OnOffRun_spread_log"]
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def fe_fit(dd, formula):
    return PanelOLS.from_formula(formula, dd.set_index(["country", "t"])).fit(**p14.DK)


def r2w(m):
    return float(m.rsquared_within)


def principal(dd, tail, pref, fe="PT"):
    """M4 con la cola `tail` (ya construida); guarda b1, b2, b3 y sus p."""
    m, _ = p13.fit(dd, fe=fe, tail=tail)
    num(f"{pref}_N", m.nobs)
    for n, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"{pref}_{lab}", m.params[n]); num(f"{pref}_{lab}_p", m.pvalues[n])
    return m


# ------------------------------------------------------------------ A y B
def dos_etapas():
    d, raw = p14.base()
    for g in GLOB:                      # factores globales en t-1, alineados con D_{t-1}
        if g + "_l1" not in d.columns:
            d = d.merge(p14.shift(raw, g, 1, g + "_l1"), on=["country", "_qn"], how="left")
    gl = [g + "_l1" for g in GLOB]
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + gl).copy()
    num("A_N", len(dd))

    # A. cuanta varianza de D explican los factores globales / el tiempo / la fragilidad
    m_g = fe_fit(dd, "D_l1 ~ " + " + ".join(gl) + " + EntityEffects")
    num("A_R2within_D_globales", r2w(m_g))
    m_t = fe_fit(dd, "D_l1 ~ 1 + EntityEffects + TimeEffects")
    num("A_R2_D_EFpais_tiempo", float(m_t.rsquared_inclusive))
    m_j = fe_fit(dd, "D_l1 ~ ln_JLoss_l1 + EntityEffects + TimeEffects")
    num("A_coef_D_sobre_lnJLoss", m_j.params["ln_JLoss_l1"]); num("A_coef_D_sobre_lnJLoss_p", m_j.pvalues["ln_JLoss_l1"])
    num("A_R2within_D_lnJLoss", r2w(m_j))
    # correlacion entre los dos regresores tras quitar EF de pais y tiempo -> VIF
    res = pd.DataFrame({
        "D": fe_fit(dd, "D_l1 ~ 1 + EntityEffects + TimeEffects").resids,
        "J": fe_fit(dd, "ln_JLoss_l1 ~ 1 + EntityEffects + TimeEffects").resids})
    r = float(res.corr().iloc[0, 1])
    num("A_corr_parcial_D_lnJLoss", r); num("A_VIF", 1.0 / (1.0 - r * r))
    num("A_corr_simple_D_lnJLoss", float(dd[["D_l1", "ln_JLoss_l1"]].corr().iloc[0, 1]))

    # referencia: la principal sobre esta misma muestra
    principal(dd, "D_l1", "ref_PT")
    principal(dd, "D_l1", "ref_P", fe="P")

    # B1. D limpio de factores globales (EF pais) -> segunda etapa con EF pais y con EF pais+tiempo
    dd = dd.set_index(["country", "t"])
    dd["D_res_glob"] = m_g.resids
    dd["D_res_J"] = m_j.resids
    dd = dd.reset_index()
    principal(dd, "D_res_glob", "B1_P", fe="P")
    principal(dd, "D_res_glob", "B1_PT")
    # B2. D limpio de ln JLoss (y de los EF) -> segunda etapa con EF pais+tiempo
    principal(dd, "D_res_J", "B2_PT")


# ------------------------------------------------------------------ C
def panel_con_gar(gar):
    """panel de estimacion de la principal con una serie alternativa de GaR (misma logica de rezagos
    que p12._base_lag / p13.datos)."""
    d = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    g = gar.copy(); g["country"] = g["country"].str.lower()
    d = d.drop(columns=["GaR"]).merge(g[["country", "quarter", "GaR"]], on=["country", "quarter"], how="left")
    d["GaR_pp"] = d["GaR"] * 100.0
    q = pd.PeriodIndex(d["quarter"], freq="Q")
    d["_qn"] = q.year * 4 + q.quarter
    d = d.sort_values(["country", "_qn"]).copy()
    gr = d.groupby("country")
    consec = (d["_qn"] - gr["_qn"].shift(1)) == 1
    d["JLoss_l1"] = gr["JLoss"].shift(1).where(consec)
    d["GaR_pp_l1"] = gr["GaR_pp"].shift(1).where(consec)
    d = d.dropna(subset=["EMBI_bps", "JLoss_l1", "GaR_pp_l1"]).copy()
    d["ln_EMBI"] = np.log(d["EMBI_bps"]); d["ln_JLoss_l1"] = np.log(d["JLoss_l1"])
    d["D_l1"] = -d["GaR_pp_l1"]
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


def sin_bursatil():
    f_base = os.path.join(GARNC, "gar_insample_base.csv")
    f_nostx = os.path.join(GARNC, "gar_insample_noSTX.csv")
    if not os.path.exists(f_nostx):
        print("  (falta gar_insample_noSTX.csv: correr build_fci_no_stx.py y gar_insample_robustez.py)")
        return
    base, nostx = pd.read_csv(f_base), pd.read_csv(f_nostx)
    db, dn = panel_con_gar(base), panel_con_gar(nostx)
    j = db[["country", "quarter", "D_l1"]].merge(dn[["country", "quarter", "D_l1"]],
                                                 on=["country", "quarter"], suffixes=("_b", "_n"))
    num("C_corr_D_base_noSTX", float(j[["D_l1_b", "D_l1_n"]].corr().iloc[0, 1]))
    for lab, dd in (("C_base", db), ("C_noSTX", dn)):
        principal(dd, "D_l1", lab)
        sin = dd[~dd["quarter"].isin(p13.CRISIS_BAT)]
        principal(sin, "D_l1", lab + "_sincrisis")
        num(lab + "_corr_D_lnJLoss", float(dd[["D_l1", "ln_JLoss_l1"]].corr().iloc[0, 1]))


def main():
    print("p18: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]))
    dos_etapas()
    sin_bursatil()
    out = os.path.join(HERE, "paper_solapamiento_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:34s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
