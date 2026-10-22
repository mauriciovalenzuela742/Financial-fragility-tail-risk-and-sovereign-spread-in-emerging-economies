# -*- coding: utf-8 -*-
"""
p59_modelo.py -- N3 del preregistro 6 (4_Redaccion/preregistro_modelo.md, commit 90f0adf): modelo de límite
fiscal de dos períodos para el hallazgo central (riesgo de cola x deuda), calibración y prueba en niveles.

  Modelo: incumplimiento si g < g*(b) = (r b - ps)/(b + ps); pi = F(g*); spread
  s = (1 + r_f)(1 - R) pi / (1 - (1 - R) pi). F: normal partida en la mediana m, cola izquierda de escala
  sigma_L (alternativa: t de Student con 5 g.l., con la misma q05). D = -q05 = 1,645 sigma_L - m.
  Calibración: momentos de la muestra de la prueba D4 x deuda; ps tal que el spread del modelo en la media
  sea la media geométrica del EMBI. Predicciones: beta_log = dln s/dD, psi_log = d2 ln s/dD db x sd(b), y sus
  análogos en pb; en la media y en promedio sobre las observaciones; grilla R x r x familia.
  M6-H1 (python p59_modelo.py niveles): la prueba D4 x deuda con el spread en pb y JLoss en niveles
  (JLOSS_FORMA=nivlag), wild unilateral, sin cada país; secundarias con D_{t-1} y aleatorización de la deuda.
Salida: bbg/paper_p59_numeros.csv (y paper_p59n_numeros.csv, de la parte en niveles).
"""
import os
import subprocess
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) > 1 and sys.argv[1] == "niveles":
    os.environ["JLOSS_FORMA"] = "nivlag"
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from scipy import optimize, stats

import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p45_macro_preregistrada as p45

NUM = p32.NUM
Z05 = stats.norm.ppf(0.05)              # -1,645


def num(k, v):
    NUM[k] = float(v)


# ================================================================ modelo
def F(g, m, sL, fam):
    if fam == "normal":
        return stats.norm.cdf((g - m) / sL)
    k = sL * Z05 / stats.t.ppf(0.05, 5)  # escala de la t con la misma q05
    return stats.t.cdf((g - m) / k, 5)


def spread(b, D, m, ps, r, R, fam, rf=0.02):
    """b: deuda/PIB (fracción); D: riesgo de cola en pp; devuelve el spread en pb."""
    sL = (D / 100 + m) / (-Z05)
    gs = (r * b - ps) / (b + ps)
    pi = F(gs, m, sL, fam)
    return 1e4 * (1 + rf) * (1 - R) * pi / (1 - (1 - R) * pi)


def calibrar(b, D, m, s_obj, r, R, fam):
    f = lambda ps: np.log(spread(b, D, m, ps, r, R, fam)) - np.log(s_obj)
    return optimize.brentq(f, 1e-5, 0.5)


def derivadas(b, D, m, ps, r, R, fam, sd_b, hD=0.05, hb=0.005):
    s = lambda bb, DD: spread(bb, DD, m, ps, r, R, fam)
    ls = lambda bb, DD: np.log(s(bb, DD))
    bl = (ls(b, D + hD) - ls(b, D - hD)) / (2 * hD)
    bn = (s(b, D + hD) - s(b, D - hD)) / (2 * hD)
    pl = (ls(b + hb, D + hD) - ls(b + hb, D - hD) - ls(b - hb, D + hD) + ls(b - hb, D - hD)) / (4 * hD * hb) * sd_b
    pn = (s(b + hb, D + hD) - s(b + hb, D - hD) - s(b - hb, D + hD) + s(b - hb, D - hD)) / (4 * hD * hb) * sd_b
    return dict(beta_log=bl, beta_niv=bn, psi_log=pl, psi_niv=pn, s=s(b, D), pi=None)


def modelo():
    d, raw = p42.preparar()
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    x = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D4_l1", "DEBT_l4"]).copy()
    b, sd_b = x["DEBT_l4"].mean() / 100, x["DEBT_l4"].std() / 100
    D = x["D4_l1"].mean(); m = x["gar_mean"].mean(); s_obj = np.exp(x["ln_EMBI"].mean())
    num("cal_N", len(x)); num("cal_b", b); num("cal_sd_b", sd_b); num("cal_D4", D); num("cal_m", m)
    num("cal_s_obj", s_obj); num("cal_sigmaL", (D / 100 + m) / (-Z05))
    filas = []
    for fam in ("normal", "t5"):
        for R in (0.50, 0.63, 0.75):
            for r in (0.01, 0.03, 0.05):
                ps = calibrar(b, D, m, s_obj, r, R, fam)
                dv = derivadas(b, D, m, ps, r, R, fam, sd_b)
                gs = (r * b - ps) / (b + ps); sL = (D / 100 + m) / (-Z05)
                f = dict(fam=fam, R=R, r=r, ps=ps, z=(gs - m) / sL, **{k: v for k, v in dv.items() if v is not None})
                filas.append(f)
    G = pd.DataFrame(filas)
    G.to_csv(os.path.join(HERE, "modelo_grilla_bbg.csv"), index=False)
    base = G[(G["fam"] == "normal") & (G["R"] == 0.63) & (G["r"] == 0.03)].iloc[0]
    for k in ("ps", "z", "beta_log", "beta_niv", "psi_log", "psi_niv", "s"):
        num(f"mod_{k}", base[k])
    for k in ("beta_log", "beta_niv", "psi_log", "psi_niv"):
        num(f"mod_{k}_min", G[k].min()); num(f"mod_{k}_max", G[k].max())
        for fam in ("normal", "t5"):
            num(f"mod_{k}_{fam}_min", G[G["fam"] == fam][k].min()); num(f"mod_{k}_{fam}_max", G[G["fam"] == fam][k].max())
    # promedio sobre las observaciones, con el ps de la calibración base
    vals = []
    for bi, Di in zip(x["DEBT_l4"] / 100, x["D4_l1"]):
        if (Di / 100 + m) <= 0:
            continue
        try:
            vals.append(derivadas(bi, Di, m, base["ps"], 0.03, 0.63, "normal", sd_b))
        except Exception:
            continue
    V = pd.DataFrame(vals).replace([np.inf, -np.inf], np.nan).dropna(subset=["beta_log", "psi_log"])
    num("mod_obs_n", len(V))
    for k in ("beta_log", "beta_niv", "psi_log", "psi_niv"):
        num(f"mod_obs_{k}", V[k].mean()); num(f"mod_obs_{k}_pos", (V[k] > 0).mean())
        num(f"mod_obs_{k}_mediana", V[k].median())   # descriptiva: la media se dispara en las colas extremas
    print(G.round(4).to_string(index=False))


# ================================================================ prueba en niveles
def niveles():
    import p56_inferencia_conjunta as p56
    d, raw = p42.preparar()
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    for tcol, pref in (("D4_l1", "m6"), ("D_l1", "m6d1")):
        dd = d.dropna(subset=[tcol]).copy(); dd["D_l1"] = dd[tcol]
        p = p42.moderacion(dd, "DEBT_l4", "T_c", pref, +1, loo=(pref == "m6"))
        if pref == "m6":
            p56.NUM = NUM
            p56.aleatorizacion(d.dropna(subset=["D4_l1"]), raw, "D4_l1", "m6perm", NUM["m6_b"])
    num("m6_firme", float(NUM["m6_p_uni"] < 0.05 and NUM["m6_loo_ok"] == 13))
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p59n_numeros.csv"))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "niveles":
        niveles(); return
    modelo()
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "niveles"], cwd=os.path.dirname(HERE))
    if r.returncode != 0:
        sys.exit("falló la parte en niveles")
    v = pd.read_csv(os.path.join(HERE, "paper_p59n_numeros.csv"), index_col=0)["valor"]
    for k, val in v.items():
        if k.startswith("m6"):
            NUM[k] = float(val)
    # comparación
    num("cmp_psi_log_signo_igual", float(np.sign(NUM["mod_psi_log"]) == np.sign(0.0326)))
    num("cmp_psi_niv_en_rango", float(NUM["mod_psi_niv_min"] <= NUM["m6_b"] <= NUM["mod_psi_niv_max"]))
    num("cmp_beta_log_en_rango", float(NUM["mod_beta_log_min"] <= 0.0467 <= NUM["mod_beta_log_max"]))
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p59_numeros.csv"))
    for k, val in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:28s} {val: .4f}")


if __name__ == "__main__":
    main()
