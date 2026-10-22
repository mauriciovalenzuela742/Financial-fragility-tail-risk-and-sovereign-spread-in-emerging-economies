# -*- coding: utf-8 -*-
"""
p38_panel_ampliado.py -- más economías y más historia (mejora C11 de 4_Redaccion/evaluacion_experta.md).
Se corren exactamente estos dos ejercicios y se reportan todos:

(a) EMBI imputado desde el CDS. Indonesia, Filipinas y Sudáfrica tienen EMBI de J.P. Morgan solo desde
    2023Q3 (y del FMI en 2010-2014), pero CDS soberano a cinco años de Bloomberg desde 2004. Se imputa
    ln EMBI = a_i + b ln CDS, con pendiente común estimada sobre todas las economías con ambas series y
    un intercepto por país estimado en sus trimestres de solapamiento; solo se llenan trimestres sin
    EMBI. Validación: en cada economía con al menos 30 trimestres de solapamiento se estima el
    intercepto con sus últimos 13 trimestres (lo que tiene Filipinas) y la pendiente sin ella, y se
    predicen los trimestres anteriores (correlación y error absoluto mediano en log-puntos). India no
    tiene CDS y no se puede completar. La regresión principal se reestima sobre el panel ampliado.
(b) Argentina con un GaR homologado. Se usa el GaR dentro de la muestra calculado con un FCI sin el
    bloque de tasas para las 19 economías del pool (build_fci_no_ryr.py + gar_insample_robustez.py ->
    gar_insample_all19noRyr.csv): Argentina, que no tiene rendimiento soberano local, queda con el mismo
    índice que las demás. Regresión principal con 13 economías y con 14 (Argentina), y como referencia
    con el GaR base dentro de la muestra (con tasas) sobre las 13.

Simplificaciones: la imputación supone que la relación EMBI-CDS es estable en el tiempo dentro de cada
país; el GaR dentro de la muestra no es pseudo-tiempo real (se compara solo entre versiones dentro de
la muestra); la ventana de estandarización de VSTX de Argentina sigue siendo más corta.

Salida: bbg/paper_p38_numeros.csv. Reutiliza p13, p32.
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

import p13_figuras_paper as p13
import p32_aporte_riesgo_cola as p32

PANEL_ARG = os.path.join(HERE, "Panel_bloomberg_embiext_arg.csv")
GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
EXCL = {"southkorea", "bulgaria", "hungary"}
NUM = p32.NUM


def num(k, v):
    NUM[k] = float(v)


def muestra(raw, embi_col="EMBI_bps", gar=None):
    d = raw.copy()
    if gar is not None:
        d = d.drop(columns=["GaR"]).merge(gar[["country", "quarter", "GaR"]], on=["country", "quarter"], how="left")
    q = pd.PeriodIndex(d["quarter"], freq="Q"); d["_qn"] = q.year * 4 + q.quarter
    d = d.sort_values(["country", "_qn"]); g = d.groupby("country")
    ok = (d["_qn"] - g["_qn"].shift(1)) == 1
    d["JLoss_l1"] = g["JLoss"].shift(1).where(ok)
    d["D_l1"] = -(g["GaR"].shift(1) * 100).where(ok)
    d = d.dropna(subset=[embi_col, "JLoss_l1", "D_l1"]).copy()
    d = d[(d[embi_col] > 0) & (d["JLoss_l1"] > 0)]
    d["ln_EMBI"] = np.log(d[embi_col]); d["ln_JLoss_l1"] = np.log(d["JLoss_l1"])
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


def principal(d, pref):
    m, dd = p13.fit(d); mc, _ = p13.fit(d, cov="pais")
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", dd["country"].nunique())
    for k, v in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"{pref}_{k}", m.params[v]); num(f"{pref}_{k}_p_dk", m.pvalues[v]); num(f"{pref}_{k}_p_pais", mc.pvalues[v])
        num(f"{pref}_{k}_p_wild", p32.wild(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], v))


# ================================================================ (a) EMBI desde el CDS
def imputar(raw):
    d = raw.copy()
    ov = d.dropna(subset=["EMBI_bps", "CDS_bps"])
    ov = ov[(ov["EMBI_bps"] > 0) & (ov["CDS_bps"] > 0)].copy()
    ov["le"], ov["lc"] = np.log(ov["EMBI_bps"]), np.log(ov["CDS_bps"])

    def pendiente(o):
        w = o.assign(le=o["le"] - o.groupby("country")["le"].transform("mean"),
                     lc=o["lc"] - o.groupby("country")["lc"].transform("mean"))
        return float((w["le"] * w["lc"]).sum() / (w["lc"] ** 2).sum())

    b = pendiente(ov); num("imp_pendiente", b); num("imp_N_solape", len(ov))
    # validación: intercepto con los últimos 13 trimestres, pendiente sin el país
    errs, cors = [], []
    for c, g in ov.groupby("country"):
        if len(g) < 30:
            continue
        g = g.sort_values("quarter")
        bc = pendiente(ov[ov["country"] != c])
        ult, ant = g.tail(13), g.iloc[:-13]
        a = float((ult["le"] - bc * ult["lc"]).mean())
        pred = a + bc * ant["lc"]
        e = float(np.median(np.abs(pred - ant["le"]))); r = float(np.corrcoef(pred, ant["le"])[0, 1])
        errs.append(e); cors.append(r)
        num(f"imp_valid_{c}_eam", e); num(f"imp_valid_{c}_corr", r)
    num("imp_valid_eam_mediana", np.median(errs)); num("imp_valid_corr_mediana", np.median(cors))
    num("imp_valid_n_paises", len(errs))
    a_i = (ov["le"] - b * ov["lc"]).groupby(ov["country"]).mean()
    d["EMBI_imp"] = d["EMBI_bps"]
    llenar = d["EMBI_bps"].isna() & d["CDS_bps"].gt(0) & d["country"].isin(a_i.index)
    d.loc[llenar, "EMBI_imp"] = np.exp(d.loc[llenar, "country"].map(a_i) + b * np.log(d.loc[llenar, "CDS_bps"]))
    d["imputado"] = llenar
    return d


def main():
    raw = pd.read_csv(PANEL_ARG)
    raw = raw[~raw["country"].isin(EXCL)].copy()
    base = muestra(raw[raw["country"] != "argentina"])
    principal(base, "base")
    assert int(NUM["base_N"]) == 765 and abs(NUM["base_b3"] + 0.0112) < 5e-4, (NUM["base_N"], NUM["base_b3"])
    # (a)
    r13 = raw[raw["country"] != "argentina"]
    imp = imputar(r13)
    amp = muestra(imp, embi_col="EMBI_imp")
    amp_ids = set(zip(amp["country"], amp["quarter"])) - set(zip(base["country"], base["quarter"]))
    num("amp_obs_nuevas", len(amp_ids))
    for c in ("indonesia", "philippines", "southafrica"):
        num(f"amp_{c}_N", (amp["country"] == c).sum()); num(f"base_{c}_N", (base["country"] == c).sum())
    principal(amp, "amp")
    # (b) GaR homologado sin bloque de tasas
    f = os.path.join(GARNC, "gar_insample_all19noRyr.csv")
    gh = pd.read_csv(f); gh["country"] = gh["country"].str.lower()
    gb = pd.read_csv(os.path.join(GARNC, "gar_insample_base.csv")); gb["country"] = gb["country"].str.lower()
    principal(muestra(r13, gar=gb), "ins_base13")
    principal(muestra(r13, gar=gh), "ins_noryr13")
    principal(muestra(raw, gar=gh), "ins_noryr14")
    x = muestra(raw, gar=gh); num("ins_noryr14_arg_N", (x["country"] == "argentina").sum())
    j = gb.merge(gh, on=["country", "quarter"], suffixes=("_b", "_h"))
    j = j[j["country"].isin(set(base["country"]))]
    num("corr_gar_base_noryr", j[["GaR_b", "GaR_h"]].corr().iloc[0, 1])
    out = os.path.join(HERE, "paper_p38_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:30s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
