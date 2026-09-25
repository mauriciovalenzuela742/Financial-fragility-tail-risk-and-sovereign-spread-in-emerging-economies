# -*- coding: utf-8 -*-
"""
p12_tablas_latex_lnlag.py -- EXPLORATORIO. Mismas dos tablas de p11_tablas_latex.py (bateria
M1-M4 y bateria de crisis CM1-CM4, 3 estructuras de FE, formato Chari) pero con la
especificacion log-log rezagada al estilo de Chari et al. (2024, Tabla 4: "JLoss, Lag = 1"):

    ln(EMBI)_{i,t} = a_i + d_t + b1 ln(JLoss)_{i,t-1} + b2 D_{i,t-1} + b3 ln(JLoss)_{i,t-1} x D_{i,t-1} + e

  - DV: ln(EMBI_bps).
  - JLoss: ln(JLoss) rezagado un trimestre.
  - GaR: rezagado un trimestre y en NIVELES (pp), como D = -GaR. GaR puede ser negativo, asi que
    ln(GaR) no esta definido para buena parte de la muestra.
  - El rezago exige que el trimestre anterior exista para el mismo pais (sin huecos); si falta,
    la observacion sale de la muestra.
  - Controles domesticos (tabla de crisis) y dummies de crisis: contemporaneos (trimestre t),
    igual que en p9b.

Reutiliza sin cambios los ajustes de p8.fit_one y p9b.fit_crisis_model: solo se reemplaza el
contenido de las columnas que esas funciones leen (EMBI_bps/JLoss/GaR_pp y _DV/JLoss/D_pp).

Salida -> 4_Redaccion/tablas_regresiones/tablas_regresiones_lnlag.tex
"""
import os

import numpy as np
import pandas as pd

import p11_tablas_latex as p11
from p2_regresiones import PANEL_CSV


def _base_lag():
    d = pd.read_csv(PANEL_CSV)
    d["GaR_pp"] = d["GaR"] * 100.0
    q = pd.PeriodIndex(d["quarter"], freq="Q")
    d["_qn"] = q.year * 4 + q.quarter
    d = d.sort_values(["country", "_qn"]).copy()
    g = d.groupby("country")
    consec = (d["_qn"] - g["_qn"].shift(1)) == 1
    d["JLoss_l1"] = g["JLoss"].shift(1).where(consec)
    d["GaR_pp_l1"] = g["GaR_pp"].shift(1).where(consec)
    d = d.dropna(subset=["EMBI_bps", "JLoss_l1", "GaR_pp_l1"]).copy()
    assert (d["EMBI_bps"] > 0).all() and (d["JLoss_l1"] > 0).all(), "ln() no definido"
    d["ln_EMBI"] = np.log(d["EMBI_bps"])
    d["ln_JLoss_l1"] = np.log(d["JLoss_l1"])
    return d.drop(columns="_qn")


def prep_bat():
    """Columnas que lee p8.fit_one: EMBI_bps, JLoss, GaR_pp (t entero, como p8.prep)."""
    d = _base_lag()
    d["EMBI_bps"] = d["ln_EMBI"]
    d["JLoss"] = d["ln_JLoss_l1"]
    d["GaR_pp"] = d["GaR_pp_l1"]
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").astype("int64")
    return d


def prep_cr():
    """Columnas que lee p9b.fit_crisis_model: _DV, JLoss, D_pp (t timestamp, como p2.prep)."""
    d = _base_lag()
    d["_DV"] = d["ln_EMBI"]
    d["JLoss"] = d["ln_JLoss_l1"]
    d["D_pp"] = -d["GaR_pp_l1"]
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


EXTRA = (r" Especificación log-log rezagada al estilo de Chari et al.\ (2024): la variable dependiente es "
         r"$\ln(\mathrm{EMBI})$, $JLoss$ entra como $\ln(JLoss)$ rezagado un trimestre y $D$ como $-GaR$ "
         r"rezagado un trimestre y en niveles (el $GaR$ puede ser negativo, por lo que no admite logaritmo). "
         r"El coeficiente de $\ln(JLoss)_{t-1}$ es una elasticidad (cambio porcentual del spread ante un "
         r"cambio de 1\% en $JLoss$); el de $D_{t-1}$, una semielasticidad (cambio en log-puntos del spread "
         r"por punto porcentual de $D$). Se exige que el trimestre anterior exista para el mismo país.")
EXTRA_CR = (r" $\ln\mathrm{EMBI}$ como variable dependiente; $\ln(JLoss)$ y $D=-GaR$ (pp, en niveles) "
            r"rezagados un trimestre, como en la Tabla~\ref{tab:bateria-lnlag}.")

LNLAG = dict(
    p11.LEVELS,
    prep_bat=prep_bat,
    prep_cr=prep_cr,
    dv=r"$\ln(\mathrm{EMBI})$",
    jl=r"$\ln(JLoss)_{t-1}$", dd=r"$D_{t-1}=-GaR_{t-1}$", jxd=r"$\ln(JLoss)_{t-1}\times D_{t-1}$",
    cap_bat="Spread soberano, fragilidad bancaria y riesgo de cola: log-log rezagada",
    cap_cr="Spread soberano e interacción con el vector de crisis: log-log rezagada",
    lab_bat="tab:bateria-lnlag", lab_cr="tab:crisis-lnlag",
    intro_bat=(
        r"La tabla reporta estimaciones de panel del logaritmo del spread soberano (EMBI Global "
        r"Diversified) sobre la fragilidad bancaria sistémica ($JLoss$), el riesgo de cola del crecimiento "
        r"($D=-GaR$, percentil 5\% del crecimiento con signo invertido, en puntos porcentuales) y su "
        r"interacción. La columna (1) es la especificación que se busca contrastar, "
        r"$\ln\mathrm{EMBI}_{i,t}=\alpha_i+\delta_t+\beta_1\ln JLoss_{i,t-1}+\beta_2 D_{i,t-1}"
        r"+\beta_3(\ln JLoss_{i,t-1}\times D_{i,t-1})+\varepsilon_{i,t}$, con efectos fijos de país y de tiempo."),
    intro_cr=(
        r"La columna (1) es la Ecuación de interacción de crisis completa en la versión log-log rezagada, "
        r"$\ln\mathrm{EMBI}_{i,t}=\alpha_i+\delta_t+\beta_1\ln JLoss_{t-1}+\beta_2 D_{t-1}+\beta_3(\ln JLoss_{t-1}\times D_{t-1})"
        r"+\beta_4(\ln JLoss_{t-1}\times D_{t-1}\times Crisis_t)+\beta_5(\ln JLoss_{t-1}\times Crisis_t)"
        r"+\beta_6(D_{t-1}\times Crisis_t)+\omega'X_{i,t}+\varepsilon_{i,t}$, con efectos fijos de país y de "
        r"tiempo; controles y vector de crisis contemporáneos."),
    jm=r"\ln(JLoss)_{t-1}", dm="D_{t-1}",
    extra_note=EXTRA, extra_note_cr=EXTRA_CR,
    src_bat=r"\texttt{p12\_tablas\_latex\_lnlag.py} (ajuste de \texttt{p8\_bateria\_regresiones.py})",
    src_cr=r"\texttt{p12\_tablas\_latex\_lnlag.py} (ajuste de \texttt{p9b\_bateria\_crisis.py})",
)


def run():
    p11.DEC = 4  # coeficientes de D e interaccion del orden de 0,01
    sfx, spec = p11.panel_variant(LNLAG)
    t1, r1 = p11.tabla_bateria(spec)
    t2, f2 = p11.tabla_crisis(spec)
    p11.write_tex(f"tablas_regresiones_lnlag{sfx}.tex", t1, t2)

    # resumen en consola: columna de referencia y M4/CM4 por FE
    for s in ("completa", "sin crisis"):
        for fe in p11.FES:
            r = r1[(s, "M4", fe)]
            print(f"M4 {s:10s} {fe:2s} N={r['N']}  lnJ={r['JLoss']['b']:+.3f} (p={r['JLoss']['p']:.3f})"
                  f"  D={r['GaR']['b']:+.4f} (p={r['GaR']['p']:.3f})  JxD={r['Int']['b']:+.4f} (p={r['Int']['p']:.3f})")
    for pn, nms in (("A_vector_unico", ["cr"]), ("B_backstop_emstress", ["bk", "em"])):
        for fe in p11.FES:
            m = f2[(pn, "CM4", fe)]
            line = f"CM4 {pn:20s} {fe:2s} N={int(m.nobs)}  b3={m.params['JxD']:+.4f} (p={m.pvalues['JxD']:.3f})"
            for nm in nms:
                b, _, _, p = p11.p9b._lincom(m, ["JxD", f"JxD_{nm}"])
                line += f"  b3+b4[{nm}]={b:+.4f} (p={p:.3f})"
            print(line)


if __name__ == "__main__":
    run()
