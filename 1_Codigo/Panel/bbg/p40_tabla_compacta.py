# -*- coding: utf-8 -*-
"""
p40_tabla_compacta.py -- tabla compacta de la regresión principal para el cuerpo del capítulo de
resultados (la batería completa de 36 regresiones pasa al anexo).

Cuatro modelos anidados ---ln JLoss_{t-1} solo (M1), D_{t-1} solo (M2), ambos (M3) y ambos con su
producto (M4)--- con efectos fijos de país y de tiempo, sobre la muestra completa (N = 765), en
logaritmos (ln EMBI) y en niveles (EMBI en puntos básicos, JLoss en niveles). Regresores centrados,
como en p13.fit. Errores de Driscoll-Kraay (estrellas) y p del wild cluster bootstrap por país (Webb,
999 réplicas) debajo de cada coeficiente.

Salida: 4_Redaccion/tablas_regresiones/tabla_principal_compacta.tex y bbg/paper_p40_numeros.csv.
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
import p32_aporte_riesgo_cola as p32

OUT_TEX = os.path.abspath(os.path.join(HERE, "..", "..", "..", "4_Redaccion", "tablas_regresiones",
                                       "tabla_principal_compacta.tex"))
NUM = p32.NUM
MODELOS = {"M1": ["J_c"], "M2": ["T_c"], "M3": ["J_c", "T_c"], "M4": ["J_c", "T_c", "JxT"]}


def num(k, v):
    NUM[k] = float(v)


def preparar(d, niveles):
    x = d.copy()
    if niveles:
        x["ln_EMBI"] = x["EMBI_bps"]; x["ln_JLoss_l1"] = x["JLoss_l1"]
    x = x.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).copy()
    x["J_c"] = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean()
    x["T_c"] = x["D_l1"] - x["D_l1"].mean()
    x["JxT"] = x["J_c"] * x["T_c"]
    return x


def estrellas(p):
    return "^{***}" if p < 0.01 else "^{**}" if p < 0.05 else "^{*}" if p < 0.10 else ""


def fmt(v, dec):
    s = f"{v:.{dec}f}".replace(".", "{,}")
    return s.replace("-", "-")


def estimar(x, pref):
    res = {}
    for m, regs in MODELOS.items():
        r = PanelOLS.from_formula(f"ln_EMBI ~ {' + '.join(regs)} + EntityEffects + TimeEffects",
                                  x.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
        res[m] = {"N": int(r.nobs), "r2w": float(r.rsquared_within)}
        for v in regs:
            pw = p32.wild(x, "ln_EMBI", regs, v)
            res[m][v] = (float(r.params[v]), float(r.pvalues[v]), pw)
            num(f"{pref}_{m}_{v}", r.params[v]); num(f"{pref}_{m}_{v}_p_dk", r.pvalues[v]); num(f"{pref}_{m}_{v}_p_wild", pw)
        num(f"{pref}_{m}_N", r.nobs); num(f"{pref}_{m}_r2w", r.rsquared_within)
    return res


def bloque(res, titulo, dec):
    filas = [rf"\multicolumn{{5}}{{l}}{{\textit{{{titulo}}}}} \\"]
    nombres = {"J_c": r"Fragilidad bancaria ($\beta_1$)", "T_c": r"Riesgo de cola, $D_{t-1}$ ($\beta_2$)",
               "JxT": r"Interacción ($\beta_3$)"}
    for v, nom in nombres.items():
        c, w = [], []
        for m in MODELOS:
            if v in res[m]:
                b, p, pw = res[m][v]
                c.append(f"${fmt(b, dec)}{estrellas(p)}$"); w.append(f"$[{fmt(pw, 2)}]$")
            else:
                c.append(""); w.append("")
        filas.append(rf"\quad {nom} & " + " & ".join(c) + r" \\")
        filas.append(r"\quad & " + " & ".join(w) + r" \\")
    filas.append(r"\quad $R^2$ dentro del país & " + " & ".join(f"${fmt(res[m]['r2w'], 3)}$" for m in MODELOS) + r" \\")
    return filas


def main():
    d = p13.datos()
    lg = estimar(preparar(d, False), "log")
    nv = estimar(preparar(d, True), "niv")
    assert lg["M4"]["N"] == 765 and abs(lg["M4"]["JxT"][0] + 0.0112) < 5e-4, lg["M4"]
    assert abs(nv["M4"]["JxT"][0] - 0.2464) < 5e-4, nv["M4"]
    L = [r"\begin{table}[htbp]", r"\centering", r"\small",
         r"\caption[Regresión principal]{Regresión principal: cuatro modelos anidados con efectos fijos de país y de tiempo ($N=765$)}",
         r"\label{tab:principal-compacta}", r"\begin{adjustbox}{max width=\linewidth}",
         r"\begin{tabular}{l cccc}", r"\toprule", r" & M1 & M2 & M3 & M4 \\", r"\midrule"]
    L += bloque(lg, r"A. Logaritmos: $\ln$ EMBI sobre $\ln JLoss_{t-1}$ y $D_{t-1}$", 3)
    L += [r"\addlinespace"]
    L += bloque(nv, r"B. Niveles: EMBI en puntos básicos sobre $JLoss_{t-1}$ y $D_{t-1}$", 2)
    L += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}",
          r"\par\smallskip\parbox{0.95\linewidth}{\footnotesize \textit{Nota:} Regresores rezagados un trimestre y centrados en su media; efectos fijos de país y de tiempo; muestra completa sin controles. Estrellas según errores de Driscoll--Kraay (***, ** y * al 1\%, 5\% y 10\%); entre corchetes, $p$ del \textit{wild cluster bootstrap} por país (pesos de Webb, 999 réplicas). La columna M4 del Panel A es la regresión principal, la ecuación~\eqref{eq:principal}. La batería completa ---tres estructuras de efectos fijos y tres muestras--- está en la Tabla~\ref{tab:bateria-lnlag-embiext} del Anexo~\ref{chap:anexo-robustez}. Fuente: \texttt{p40\_tabla\_compacta.py}.}",
          r"\end{table}"]
    open(OUT_TEX, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    out = os.path.join(HERE, "paper_p40_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for m in MODELOS:
        print(m, {k: (round(v[0], 4), round(v[2], 3)) for k, v in lg[m].items() if isinstance(v, tuple)},
              {k: (round(v[0], 3), round(v[2], 3)) for k, v in nv[m].items() if isinstance(v, tuple)})
    print("->", OUT_TEX)


if __name__ == "__main__":
    main()
