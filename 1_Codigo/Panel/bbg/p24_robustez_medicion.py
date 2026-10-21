# -*- coding: utf-8 -*-
"""
p24_robustez_medicion.py -- medición del spread, composición del panel y magnitud económica.

Objeciones de árbitro sobre la especificación PRINCIPAL (log-log rezagada, panel embiext):
  1. Variable dependiente única: se repite con el CDS soberano a 5 años (columna CDS_bps).
  2. Panel desbalanceado: se repite sobre los diez países de historia larga (sin Filipinas,
     Indonesia ni Sudáfrica, cuyos EMBI son cortos o empalmados).
  3. Magnitud: efecto de una desviación estándar within-país de cada riesgo y cuánto de la variación
     del spread explican los dos riesgos frente a los efectos fijos (R2 parciales).

Salida: bbg/paper_medicion_numeros.csv (o _nivlag). Reutiliza p13 y p14.
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

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
CORTOS = ["philippines", "indonesia", "southafrica"]
NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def guardar(m, pref):
    num(f"{pref}_N", m.nobs)
    for n_, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_p", m.pvalues[n_])


def fig_loo_efectos(m0, loo, ees):
    """coeficiente de cada riesgo en la regresión principal excluyendo un país a la vez."""
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.2), sharey=True)
    labs = ["Panel completo"] + ["sin " + p13.NOMBRE[c] for c in loo["pais"]]
    for ax, col, k, v, tit in ((axs[0], "b1", 0, "J_c", "Fragilidad bancaria"), (axs[1], "b2", 1, "T_c", "Riesgo de cola")):
        bs = [m0.params[v]] + list(loo[col]); ss = [m0.std_errors[v]] + [e[k] for e in ees]
        ax.axvline(0, color=p13.INK2, lw=0.8)
        for i, (b, se) in enumerate(zip(bs, ss)):
            c_ = p13.INK if i == 0 else (p13.RED if abs(b / se) < 1.96 else p13.BLUE)
            ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=c_, lw=1.8)
            ax.plot(b, i, "o", color=c_, ms=5)
        ax.set_title(tit, fontsize=10)
        ax.set_xlabel("coeficiente (pb), IC 95 %" if NIV else "coeficiente, IC 95 %")
    axs[0].set_yticks(range(len(labs))); axs[0].set_yticklabels(labs, fontsize=8); axs[0].invert_yaxis()
    p13.save(fig, "fig_loo_efectos_lnlag")


def main():
    print("p24: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d = p13.datos()
    m0, dd = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4
    guardar(m0, "principal")

    # 1. CDS como variable dependiente (misma muestra de regresores, donde hay CDS)
    c = d[d["CDS_bps"] > 0].copy()
    num("cds_corr_ln_embi", float(np.corrcoef(np.log(c["CDS_bps"]), np.log(c["EMBI_bps"]))[0, 1]))
    me, _ = p13.fit(c); guardar(me, "embi_muestra_cds")
    c["ln_EMBI"] = c["CDS_bps"] if NIV else np.log(c["CDS_bps"])
    mc, _ = p13.fit(c); guardar(mc, "cds")
    num("cds_paises", c["country"].nunique())

    # 2. panel de historia larga
    larg = d[~d["country"].isin(CORTOS)]
    ml, ddl = p13.fit(larg); guardar(ml, "largo"); num("largo_paises", larg["country"].nunique())
    for n_, lab in (("J_c", "b1"), ("T_c", "b2")):
        p, _ = p14.wild_boot(ddl, "ln_EMBI", ["J_c", "T_c", "JxT"], n_, weights="webb")
        num(f"largo_{lab}_p_wild", p)

    # 2b. leave-one-country-out de los efectos de nivel (b1 y b2)
    filas, ees = [], []
    for pais in sorted(d["country"].unique()):
        m, _ = p13.fit(d[d["country"] != pais])
        filas.append((pais, m.params["J_c"], m.pvalues["J_c"], m.params["T_c"], m.pvalues["T_c"]))
        ees.append((m.std_errors["J_c"], m.std_errors["T_c"]))
        print(f"    sin {pais:12s} b1={m.params['J_c']:+.4f} (p={m.pvalues['J_c']:.3f})  b2={m.params['T_c']:+.4f} (p={m.pvalues['T_c']:.3f})")
    loo = pd.DataFrame(filas, columns=["pais", "b1", "p1", "b2", "p2"])
    num("loo_b1_min", loo["b1"].min()); num("loo_b1_max", loo["b1"].max()); num("loo_b1_n_sig5", (loo["p1"] < 0.05).sum())
    num("loo_b2_min", loo["b2"].min()); num("loo_b2_max", loo["b2"].max()); num("loo_b2_n_sig5", (loo["p2"] < 0.05).sum())
    fig_loo_efectos(m0, loo, ees)
    sin_india = d[d["country"] != "india"]
    mi, _ = p13.fit(sin_india); guardar(mi, "sin_india")

    # 3. magnitud: desviaciones estándar within-país y R2 parciales
    sdw = {c_: float((dd[c_] - dd.groupby("country")[c_].transform("mean")).std()) for c_ in ("J_c", "T_c", "ln_EMBI")}
    num("sd_within_J", sdw["J_c"]); num("sd_within_D", sdw["T_c"]); num("sd_within_spread", sdw["ln_EMBI"])
    num("efecto_1sd_J", m0.params["J_c"] * sdw["J_c"]); num("efecto_1sd_D", m0.params["T_c"] * sdw["T_c"])
    num("efecto_1sd_J_en_sd_spread", m0.params["J_c"] * sdw["J_c"] / sdw["ln_EMBI"])
    num("efecto_1sd_D_en_sd_spread", m0.params["T_c"] * sdw["T_c"] / sdw["ln_EMBI"])
    idx = dd.set_index(["country", "t"])

    def r2(rhs):
        return float(PanelOLS.from_formula(f"ln_EMBI ~ {rhs} + EntityEffects + TimeEffects", idx).fit().rsquared_inclusive)

    r_fe, r_all = r2("1"), r2("J_c + T_c + JxT")
    num("r2_solo_EF", r_fe); num("r2_completo", r_all)
    num("r2_parcial_ambos", (r_all - r_fe) / (1 - r_fe))
    num("r2_parcial_J", (r_all - r2("T_c")) / (1 - r2("T_c")))
    num("r2_parcial_D", (r_all - r2("J_c")) / (1 - r2("J_c")))
    r_p = float(PanelOLS.from_formula("ln_EMBI ~ 1 + EntityEffects", idx).fit().rsquared_inclusive)
    num("r2_solo_EF_pais", r_p)

    out = os.path.join(HERE, f"paper_medicion_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:30s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
