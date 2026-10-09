# -*- coding: utf-8 -*-
"""
p17_fig_heterogeneidad.py -- figura de coeficientes para la presentación: la interacción
ln JLoss_{t-1} x D_{t-1} (beta3) con IC 95 % (Driscoll-Kraay) en el panel completo y en el núcleo
de 11 economías de financiamiento externo, con y sin crisis, y en Polonia + India.
JLOSS_FORMA=nivlag la repite en niveles (pb). Reutiliza p13 (datos, fit, save, paleta) y la
interacción de grupo de p16; las cifras coinciden con paper_heterogeneidad_numeros*.csv.

Salida: paper_empirico/figuras/fig_heterogeneidad_lnlag.{pdf,png} (o _nivlag).
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import pandas as pd
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p16_heterogeneidad as p16

NIV = p13.NIV
Z = 1.96


def contraste(d):
    """beta3 + theta3 (Polonia + India) del modelo con interacciones de grupo, con su EE."""
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    dd["conv"] = dd["country"].isin(p16.CONV).astype(float)
    for c in ("J_c", "T_c", "JxT"):
        dd[c + "_conv"] = dd[c] * dd["conv"]
    m = PanelOLS.from_formula(
        "ln_EMBI ~ J_c + T_c + JxT + J_c_conv + T_c_conv + JxT_conv + EntityEffects + TimeEffects",
        dd.set_index(["country", "t"])).fit(**p14.DK)
    w = pd.Series(0.0, index=m.params.index); w[["JxT", "JxT_conv"]] = 1.0
    return float(w @ m.params), float((w @ m.cov @ w) ** 0.5)


def main():
    d = p13.datos()
    sin = d[~d["quarter"].isin(p13.CRISIS_BAT)]
    core = lambda x: x[~x["country"].isin(p16.CONV)]
    filas = []
    for lab, dk, grupo in (("Panel (13), muestra completa", d, "panel"),
                           ("Panel (13), sin crisis", sin, "panel"),
                           ("Núcleo (11), muestra completa", core(d), "nucleo"),
                           ("Núcleo (11), sin crisis", core(sin), "nucleo")):
        m, _ = p13.fit(dk)
        filas.append((lab, m.params["JxT"], m.std_errors["JxT"], grupo))
    b, se = contraste(sin)
    filas.append(("Polonia e India, sin crisis", b, se, "contraste"))
    ref = 0.2464 if NIV else -0.0112
    assert abs(filas[0][1] - ref) < 5e-4, filas[0][1]

    col = {"panel": p13.INK2, "nucleo": p13.BLUE, "contraste": p13.RED}
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for k, (lab, b, se, g) in enumerate(reversed(filas)):
        ax.errorbar(b, k, xerr=Z * se, fmt="o", color=col[g], ecolor=col[g], capsize=3, lw=1.6, ms=6)
        ax.text(b, k + 0.22, f"{b:+.3f}".replace(".", ",") if not NIV else f"{b:+.2f}".replace(".", ","),
                ha="center", va="bottom", fontsize=8, color=col[g])
    ax.axvline(0, color=p13.INK, lw=0.8)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([f[0] for f in reversed(filas)])
    ax.set_xlabel("interacción $\\beta_3$ " + ("(pb por unidad de JLoss y pp de D)" if NIV else
                                               "(cambio de la elasticidad por pp de D)") + ", IC 95 %")
    ax.set_title("Dónde aparece la amplificación", fontsize=10)
    ax.set_ylim(-0.6, len(filas) - 0.3)
    p13.save(fig, "fig_heterogeneidad_lnlag")
    for lab, b, se, _ in filas:
        print(f"  {lab:32s} {b:+.4f} (EE {se:.4f})")


if __name__ == "__main__":
    main()
