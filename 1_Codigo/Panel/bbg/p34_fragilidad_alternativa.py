# -*- coding: utf-8 -*-
"""
p34_fragilidad_alternativa.py -- la fragilidad bancaria medida sin la saturación de JLoss (mejora B6 de
4_Redaccion/evaluacion_experta.md). Se corren exactamente estas variantes y se reportan todas:

JLoss satura la cota de la malla de pérdidas en el 98 % de los país-trimestre y el 23,7 % de la
muestra está en su piso (2,16), de modo que su variación la gobierna la pérdida esperada, es decir, las
probabilidades de incumplimiento de Merton ponderadas por exposición. La especificación principal
(ln EMBI_t sobre la fragilidad_{t-1}, D_{t-1} y su producto, centrados, EF de país y de tiempo) se
reestima reemplazando ln JLoss_{t-1} por:

  1. ln PD_w: la probabilidad de incumplimiento de Merton/KMV media del sistema, ponderada por pasivos
     (en %). Es la pérdida esperada de JLoss dividida por la LGD, sin la componente inesperada que
     satura. Mismo motor (jloss_engine.quarterly_inputs + merton_pd) y mismos bancos que JLoss.
  2. -DD_w: menos la distancia al incumplimiento media ponderada por pasivos (DD = -Phi^{-1}(PD)),
     de modo que un valor mayor indica más fragilidad. No tiene piso ni techo.
  3. ln JLoss con la malla ancha [0,01; 0,20] (Panel_JLoss_wide.csv, de _engine_wide.py). Ese panel no
     incluye a India, por lo que se compara con la principal sobre la misma muestra sin India.

Para cada variante: coeficientes con p de Driscoll-Kraay, cluster por país y wild cluster bootstrap
(Webb, 999) para la fragilidad y la interacción; N; correlación con ln JLoss; fracción de la
variación within; y lo mismo en niveles (JLOSS_FORMA=nivlag: la medida entra sin logaritmo).

Simplificaciones (declaradas):
  - PD_w y DD_w no aplican el mínimo de bancos (igual que JLoss, que solo lo marca): las economías del
    panel ya lo cumplen.
  - La PD se acota a [1e-8, 1-1e-8] antes de invertirla para la DD.

Salida: bbg/fragilidad_alternativa_bbg.csv (series país-trimestre) y bbg/paper_p34_numeros.csv
(o _nivlag). Reutiliza p13, p14 y p32.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))
JREC = os.path.abspath(os.path.join(HERE, "..", "..", "JLoss_reconstruction"))
sys.path.insert(0, JREC)

import numpy as np
import pandas as pd
from scipy.stats import norm

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
BBG = os.path.abspath(os.path.join(HERE, "..", "..", "Bloomberg_extraction", "output"))
SERIES = os.path.join(HERE, "fragilidad_alternativa_bbg.csv")
NUM = p32.NUM


def num(k, v):
    NUM[k] = float(v)


# ================================================================ series
def construir_series(paises):
    import jloss_engine as je
    filas = []
    for c in paises:
        fb, fm = (os.path.join(BBG, c, f"{k}_{c}.csv") for k in ("balance", "mktcap"))
        if not (os.path.exists(fb) and os.path.exists(fm)):
            print(f"  {c}: sin archivos Bloomberg"); continue
        dm = je.quarterly_inputs(pd.read_csv(fb), pd.read_csv(fm))
        if dm.empty:
            continue
        dm["PD"] = [je.merton_pd(r["mktcap_end"], r["sigma_E_q"], r["D_star"], return_detail=True)[0]
                    for _, r in dm.iterrows()]
        dm = dm[dm["PD"].notna() & dm["total_liab"].notna() & (dm["total_liab"] > 0)].copy()
        dm["DD"] = -norm.ppf(np.clip(dm["PD"].astype(float), 1e-8, 1 - 1e-8))
        for q, g in dm.groupby("quarter"):
            w = g["total_liab"] / g["total_liab"].sum()
            filas.append({"country": c, "quarter": str(q), "PD_w": float((w * g["PD"]).sum() * 100),
                          "DD_w": float((w * g["DD"]).sum()), "n_banks_pd": len(g)})
        print(f"  {c}: {dm['quarter'].nunique()} trimestres", flush=True)
    out = pd.DataFrame(filas)
    out.to_csv(SERIES, index=False)
    return out


def series():
    if os.path.exists(SERIES):
        return pd.read_csv(SERIES)
    d0 = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    return construir_series(sorted(d0["country"].unique()))


def wide():
    w = pd.read_csv(os.path.join(JREC, "Panel_JLoss_wide.csv")).rename(columns={"countryname": "country"})
    return w[["country", "quarter", "JLoss"]].rename(columns={"JLoss": "JLoss_wide"})


# ================================================================ estimación
def rezagar(d, s, cols):
    """valor de cada columna en el trimestre anterior (mismo país), alineado con d."""
    s = s.copy()
    q = pd.PeriodIndex(s["quarter"], freq="Q")
    s["quarter"] = (q + 1).astype(str)                 # el dato de t-1 se asigna al trimestre t
    return d.merge(s[["country", "quarter"] + cols].rename(columns={c: c + "_l1" for c in cols}),
                   on=["country", "quarter"], how="left")


def estimar(d, col, pref, transform):
    x = d.dropna(subset=[col]).copy()
    if transform == "log":
        x = x[x[col] > 0]
        x["ln_JLoss_l1"] = x[col] if NIV else np.log(x[col])
    elif transform == "neg":
        x["ln_JLoss_l1"] = -x[col]
    else:
        x["ln_JLoss_l1"] = x[col]
    m, dd = p13.fit(x); mc, _ = p13.fit(x, cov="pais")
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", dd["country"].nunique())
    for k, v in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"{pref}_{k}", m.params[v]); num(f"{pref}_{k}_p_dk", m.pvalues[v]); num(f"{pref}_{k}_p_pais", mc.pvalues[v])
    for k, v in (("b1", "J_c"), ("b3", "JxT")):
        num(f"{pref}_{k}_p_wild", p32.wild(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], v))
    # b1 por d.e. within de la medida (comparable entre medidas)
    sw = float((dd["J_c"] - dd.groupby("country")["J_c"].transform("mean")).std())
    num(f"{pref}_sd_within", sw); num(f"{pref}_b1_por_sd", m.params["J_c"] * sw)
    num(f"{pref}_frac_within", float((dd["J_c"] - dd.groupby("country")["J_c"].transform("mean")).var() / dd["J_c"].var()))
    return dd


def main():
    print("p34: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    p14.check_principal(d)
    s = series()
    d = rezagar(d, s, ["PD_w", "DD_w"])
    d = rezagar(d, wide(), ["JLoss_wide"])
    out = os.path.join(HERE, f"paper_p34_numeros{SFX}.csv")
    d["JLoss_l1_ref"] = d["JLoss_l1"]
    base = estimar(d, "JLoss_l1_ref", "base", "log")
    for col in ("PD_w_l1", "DD_w_l1", "JLoss_wide_l1"):
        num(f"cobertura_{col}", d[col].notna().sum())
    lnj = np.log(d["JLoss_l1"])
    num("corr_lnJ_lnPD", np.corrcoef(lnj[d["PD_w_l1"] > 0], np.log(d.loc[d["PD_w_l1"] > 0, "PD_w_l1"]))[0, 1])
    num("corr_lnJ_negDD", d[["DD_w_l1"]].assign(l=lnj).dropna().corr().iloc[0, 1] * -1)
    num("corr_lnJ_lnJwide", np.corrcoef(lnj[d["JLoss_wide_l1"].notna()], np.log(d["JLoss_wide_l1"].dropna()))[0, 1])
    num("frac_piso_JLoss", float(((d["JLoss_l1"] - 2.16).abs() / 2.16 < 0.02).mean()))
    estimar(d, "PD_w_l1", "pd", "log")
    estimar(d, "DD_w_l1", "dd", "neg")
    sin_india = d[d["country"] != "india"]
    estimar(sin_india, "JLoss_l1_ref", "base_sinindia", "log")
    estimar(sin_india, "JLoss_wide_l1", "wide", "log")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:36s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
