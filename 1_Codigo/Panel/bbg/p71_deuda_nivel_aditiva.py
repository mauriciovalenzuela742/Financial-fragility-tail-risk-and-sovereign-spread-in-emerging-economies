# -*- coding: utf-8 -*-
"""
p71_deuda_nivel_aditiva.py -- especificación (4) tras la reunión del 12-11-2026 (no preespecificado).

Tres preguntas del profesor guía:
  1. ¿Deuda/PIB o nivel de deuda? Se repite la ecuación (4) con el nivel de la deuda del gobierno
     general en USD, ln(deuda USD) = ln(DEBT/100 x PIB nominal USD), en lugar de DEBT (% del PIB).
     PIB nominal en USD: Banco Mundial WDI NY.GDP.MKTP.CD (anual), interpolado log-linealmente a
     trimestres (valor anual en el Q4). Se valida contra la deuda QPSD en USD (DP.DOD.DECT.CR.GG.CD;
     si falta, CG.CD) donde existe.
  2. Versión aditiva: ln EMBI = a_i + d_t + b1 ln JLoss_{t-1} + b2 D_{t-1} + k Deuda_{t-4} + e
     (D y la deuda como sumandos, como en la (1)), luego + interacción de la (1) y luego + D x Deuda.
  3. Rezago: la (4) con la deuda en t-1, t-4 y t-8.

Mismo diseño que p42 (R-H3): regresores centrados, moderador estandarizado en la muestra, EF país y
tiempo, Driscoll-Kraay y wild cluster bootstrap por país (Webb, 999; bilateral).

Salida: bbg/paper_p71_numeros.csv y las cachés bbg/pib_usd_wdi.csv y bbg/deuda_usd_qpsd.csv.
Reutiliza p41, p42, p32.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import numpy as np
import pandas as pd

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p41_datos_resiliencia as p41
import p42_resiliencia_preregistrada as p42

PIB = os.path.join(HERE, "pib_usd_wdi.csv")
DEU_USD = os.path.join(HERE, "deuda_usd_qpsd.csv")
OUT = os.path.join(HERE, "paper_p71_numeros.csv")
NUM = {}


def num(k, v):
    NUM[k] = float(v)


def pib_trimestral():
    if os.path.exists(PIB):
        a = pd.read_csv(PIB)
    else:
        a = p41.wb("NY.GDP.MKTP.CD", 2, "2000:2026"); a.to_csv(PIB, index=False)
    a["_qn"] = a["periodo"].astype(int) * 4 + 4
    qn_full = np.arange(2000 * 4 + 1, 2026 * 4 + 5)
    out = []
    for c, g in a.groupby("country"):
        g = g.sort_values("_qn")
        # Interpolación log-lineal entre los Q4; fuera del rango, el valor más cercano
        v = np.exp(np.interp(qn_full, g["_qn"], np.log(g["valor"])))
        out.append(pd.DataFrame({"country": c, "_qn": qn_full, "pib_usd": v}))
    return pd.concat(out, ignore_index=True)


def deuda_usd_qpsd():
    if os.path.exists(DEU_USD):
        return pd.read_csv(DEU_USD)
    gg = p41.wb("DP.DOD.DECT.CR.GG.CD", 20, "2000Q1:2026Q4")
    cg = p41.wb("DP.DOD.DECT.CR.CG.CD", 20, "2000Q1:2026Q4")
    x = pd.concat([gg.assign(pri=0), cg.assign(pri=1)]).sort_values("pri")
    x = x.drop_duplicates(["country", "periodo"]).drop(columns="pri")
    q = pd.PeriodIndex(x["periodo"].str.replace(" ", ""), freq="Q"); x["_qn"] = q.year * 4 + q.quarter
    x = x.rename(columns={"valor": "deuda_usd_qpsd"})[["country", "_qn", "deuda_usd_qpsd"]]
    x.to_csv(DEU_USD, index=False)
    return x


def preparar():
    d, raw = p42.preparar()
    raw = raw.merge(pib_trimestral(), on=["country", "_qn"], how="left")
    raw["lnDEUSD"] = np.log(raw["DEBT"] / 100 * raw["pib_usd"])
    raw = raw.merge(deuda_usd_qpsd(), on=["country", "_qn"], how="left")
    v = raw.dropna(subset=["lnDEUSD", "deuda_usd_qpsd"])
    v = v[v["deuda_usd_qpsd"] > 0].copy()
    v["lnq"] = np.log(v["deuda_usd_qpsd"])
    num("valid_N", len(v)); num("valid_paises", v["country"].nunique())
    num("valid_corr_ln", np.corrcoef(v["lnDEUSD"], v["lnq"])[0, 1])
    dm = v["lnDEUSD"] - v.groupby("country")["lnDEUSD"].transform("mean")
    dq = v["lnq"] - v.groupby("country")["lnq"].transform("mean")
    num("valid_corr_dentro", np.corrcoef(dm, dq)[0, 1])
    for col in ("lnDEUSD", "DEBT"):
        for k in (1, 4, 8):
            nm = f"{col}_l{k}"
            if nm not in d.columns:
                d = d.merge(p14.shift(raw, col, k, nm), on=["country", "_qn"], how="left")
    return d


def modelos(d, mod, pref, wild=True):
    """A aditiva; B + JxT (la (1) con la deuda); C + D x Deuda (la (4))."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod]))
    x["M_s"] = (x[mod] - x[mod].mean()) / x[mod].std()
    x["TxM"] = x["T_c"] * x["M_s"]
    num(f"{pref}_N", len(x)); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_sd_mod", x[mod].std())
    specs = {"A": ["J_c", "T_c", "M_s"], "B": ["J_c", "T_c", "JxT", "M_s"],
             "C": ["J_c", "T_c", "JxT", "M_s", "TxM"]}
    for s, rhs in specs.items():
        m = p42.fit(x, "ln_EMBI", rhs)
        for v in rhs:
            num(f"{pref}_{s}_{v}", m.params[v]); num(f"{pref}_{s}_{v}_p_dk", m.pvalues[v])
        num(f"{pref}_{s}_r2w", m.rsquared_within)
        if wild:
            for v in [v for v in ("T_c", "M_s", "TxM") if v in rhs]:
                num(f"{pref}_{s}_{v}_p_wild", p32.wild(x, "ln_EMBI", rhs, v))


def simple(d, mod, pref):
    """Pedido del 14-11-2026: ln EMBI sobre D = -GaR, la deuda y D x deuda, sin la fragilidad.
    S1: D; S2: D + deuda; S3: D + deuda + D x deuda. Misma muestra que la (4)."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod]))
    x["M_s"] = (x[mod] - x[mod].mean()) / x[mod].std()
    x["TxM"] = x["T_c"] * x["M_s"]
    num(f"{pref}_N", len(x))
    for s, rhs in {"S1": ["T_c"], "S2": ["T_c", "M_s"], "S3": ["T_c", "M_s", "TxM"]}.items():
        m = p42.fit(x, "ln_EMBI", rhs)
        num(f"{pref}_{s}_r2w", m.rsquared_within)
        for v in rhs:
            num(f"{pref}_{s}_{v}", m.params[v]); num(f"{pref}_{s}_{v}_p_dk", m.pvalues[v])
            num(f"{pref}_{s}_{v}_p_wild", p32.wild(x, "ln_EMBI", rhs, v))
        if s == "S3":
            loo = [float(p42.fit(x[x["country"] != c], "ln_EMBI", rhs).params["TxM"])
                   for c in sorted(x["country"].unique())]
            num(f"{pref}_S3_TxM_loo_min", min(loo)); num(f"{pref}_S3_TxM_loo_max", max(loo))
            num(f"{pref}_S3_TxM_loo_pos", sum(b > 0 for b in loo))


def completa(d, ctr, pref, mod="DEBT_l4"):
    """Pedido del 14-11-2026: la (1) completa (ln JLoss, D, ln JLoss x D) más deuda y D x deuda,
    sin controles (como el Panel A) y con los seis controles (como el Panel C). En la misma muestra,
    la (1) sin la deuda (base) para ver si el coeficiente de D crece al agregarla."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod] + ctr))
    x["M_s"] = (x[mod] - x[mod].mean()) / x[mod].std()
    x["TxM"] = x["T_c"] * x["M_s"]
    num(f"{pref}_N", len(x))
    base = ["J_c", "T_c", "JxT"] + ctr
    for s, rhs in {"base": base, "mas_deuda": base + ["M_s"], "completa": base + ["M_s", "TxM"]}.items():
        m = p42.fit(x, "ln_EMBI", rhs)
        num(f"{pref}_{s}_r2w", m.rsquared_within)
        for v in [v for v in ("J_c", "T_c", "JxT", "M_s", "TxM") if v in rhs]:
            num(f"{pref}_{s}_{v}", m.params[v]); num(f"{pref}_{s}_{v}_p_dk", m.pvalues[v])
            if v in ("T_c", "M_s", "TxM", "J_c", "JxT"):
                num(f"{pref}_{s}_{v}_p_wild", p32.wild(x, "ln_EMBI", rhs, v))
        if s == "completa":
            loo = [float(p42.fit(x[x["country"] != c], "ln_EMBI", rhs).params["TxM"])
                   for c in sorted(x["country"].unique())]
            num(f"{pref}_TxM_loo_min", min(loo)); num(f"{pref}_TxM_loo_max", max(loo))
            num(f"{pref}_TxM_loo_pos", sum(b > 0 for b in loo))


def main():
    print("p71: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]))
    d = preparar()
    ctr_c = [c for c in p14.CTRLS if d[c].notna().sum() > 50]
    completa(d, [], "compA")
    completa(d, ctr_c, "compC")
    completa(d, [c for c in p42.CTR_L4 if c in d.columns], "compC_l4")
    simple(d, "DEBT_l4", "simple_ratio")
    simple(d, "lnDEUSD_l4", "simple_nivel")
    modelos(d, "DEBT_l4", "ratio_l4")
    modelos(d, "lnDEUSD_l4", "nivel_l4")
    for k in (1, 8):
        modelos(d, f"DEBT_l{k}", f"ratio_l{k}")
        modelos(d, f"lnDEUSD_l{k}", f"nivel_l{k}", wild=False)
    # Razón y nivel juntos: con EF de país, el nivel neto de la razón es el ln del PIB en USD
    z = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", "DEBT_l4", "lnDEUSD_l4"]))
    for c in ("DEBT_l4", "lnDEUSD_l4"):
        z[c + "_s"] = (z[c] - z[c].mean()) / z[c].std()
    z["TxR"] = z["T_c"] * z["DEBT_l4_s"]; z["TxN"] = z["T_c"] * z["lnDEUSD_l4_s"]
    rhs = ["J_c", "T_c", "JxT", "DEBT_l4_s", "lnDEUSD_l4_s", "TxR", "TxN"]
    m = p42.fit(z, "ln_EMBI", rhs)
    for v in rhs:
        num(f"ambas_{v}", m.params[v]); num(f"ambas_{v}_p_dk", m.pvalues[v])
    num("ambas_N", len(z))
    num("corr_razon_nivel_dentro", np.corrcoef(
        z["DEBT_l4"] - z.groupby("country")["DEBT_l4"].transform("mean"),
        z["lnDEUSD_l4"] - z.groupby("country")["lnDEUSD_l4"].transform("mean"))[0, 1])
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)
    for k, v in NUM.items():
        print(f"  {k:34s} {v: .4f}")
    print("->", OUT)


if __name__ == "__main__":
    main()
