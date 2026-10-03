# -*- coding: utf-8 -*-
"""
p15_comparacion_formas.py -- tabla de robustez a la forma funcional: la especificacion principal
(log-log rezagada) frente a la misma especificacion en NIVELES (EMBI en pb, JLoss_{t-1} en niveles),
prueba por prueba. No estima nada: lee las cifras que ya escribieron p13 y p14 en ambos modos.

Entradas: paper_lnlag_numeros.csv, paper_nivlag_numeros.csv        (p13, JLOSS_FORMA=lnlag/nivlag)
          paper_arbitro_numeros.csv, paper_arbitro_nivlag_numeros.csv (p14, idem)
Salida:   4_Redaccion/tablas_regresiones/tabla_robustez_niveles.tex
          bbg/paper_comparacion_formas.csv (las mismas cifras, para citarlas en el texto)
"""
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "4_Redaccion", "tablas_regresiones"))


def leer(nombre):
    return pd.read_csv(os.path.join(HERE, nombre), index_col=0)["valor"].to_dict()


F = {"log": {**leer("paper_lnlag_numeros.csv"), **leer("paper_arbitro_numeros.csv")},
     "niv": {**leer("paper_nivlag_numeros.csv"), **leer("paper_arbitro_nivlag_numeros.csv")}}


def p_de(b, se):
    return 2 * (1 - stats.norm.cdf(abs(b / se)))


def star(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def fmt(x, dec):
    return f"{x:.{dec}f}".replace("-", "−").replace(".", "{,}").replace("−", "-")


# (rotulo, clave del coeficiente o None, clave del p o funcion)
FILAS = [
    ("Especificación principal", None, None),
    (r"\quad $\beta_1$ (fragilidad)", "principal_b1", "principal_b1_p"),
    (r"\quad $\beta_2$ (riesgo de cola)", "principal_b2", "principal_b2_p"),
    (r"\quad $\beta_3$ (interacción)", "principal_b3", "principal_b3_p"),
    (r"\quad $\beta_3$ sin trimestres de crisis", "forest_Sin_crisis_FE_paístiempo", "se:forest_Sin_crisis_FE_paístiempo_se"),
    (r"\quad $\beta_1$ con los seis controles", "ctrl_todos_b1", "ctrl_todos_b1_p"),
    (r"\quad $\beta_3$ con los seis controles", "ctrl_todos_b3", "ctrl_todos_b3_p"),
    ("Causalidad inversa y dinámica", None, None),
    (r"\quad canal inverso: fragilidad$_t$ sobre spread$_{t-1}$", "arb_inverso_b", "arb_inverso_p"),
    (r"\quad $\beta_1$ con el spread rezagado (corto plazo)", "arb_din_b1", "arb_din_b1_p"),
    (r"\quad $\beta_1$ de largo plazo", "arb_din_lp", "arb_din_lp_p"),
    (r"\quad $\beta_1$ con la fragilidad adelantada", "arb_lead_b1", "arb_lead_b1_p"),
    (r"\quad proyección local $h=0$ / $h=4$ (fragilidad)", "lp", None),
    (r"Inferencia con 13 \textit{clusters} (\textit{wild bootstrap}, $p$)", None, None),
    (r"\quad $\beta_1$ / $\beta_2$ / $\beta_3$", "wb", None),
    ("Variables instrumentales (fragilidad)", None, None),
    (r"\quad on/off-the-run", "arb_iv_onoff_b", "arb_iv_onoff_p"),
    (r"\quad dólar amplio", "arb_iv_usd_b", "arb_iv_usd_p"),
    (r"\quad términos de intercambio", "arb_iv_ctot_b", "arb_iv_ctot_p"),
    (r"\quad Sargan (sobreidentificada, $p$)", "sargan", None),
    (r"Regresor generado (500 réplicas del $GaR$, $p$ combinado)", None, None),
    (r"\quad $\beta_1$ / $\beta_2$ / $\beta_3$", "bg", None),
    ("Régimen de crisis (CM4, efectos fijos de país y de tiempo)", None, None),
    (r"\quad \textit{Backstop}, $\beta_3+\beta_4$ (Driscoll--Kraay)", "arb_crisis_em1516_PT_bk", "arb_crisis_em1516_PT_bk_p"),
    (r"\quad \textit{Backstop}, $\beta_3+\beta_4$ (\textit{cluster} país)", "arb_crisis_cluster_bk", "arb_crisis_cluster_bk_p"),
    (r"\quad \textit{EMstress} 2015--16, $\beta_3+\beta_4$ (Driscoll--Kraay)", "arb_crisis_em1516_PT_em", "arb_crisis_em1516_PT_em_p"),
    (r"\quad \textit{EMstress} 2015--16, $\beta_3+\beta_4$ (\textit{cluster} país)", "arb_crisis_cluster_em", "arb_crisis_cluster_em_p"),
    (r"\quad \textit{EMstress} ampliado (\textit{taper}, 2015--16, 2018)", "arb_crisis_ext_PT_em", "arb_crisis_ext_PT_em_p"),
    (r"\quad permutación de ventanas de 3 trimestres ($p$)", "perm", None),
    ("Controles y medición", None, None),
    (r"\quad $\beta_1$ en la batería estilo Chari (rango, 6 columnas)", "chari", None),
    (r"\quad $\beta_1$ con controles en $t-4$", "arb_ctrl_l4_b1", "arb_ctrl_l4_b1_p"),
    (r"\quad $\beta_1$ con $JLoss$ en percentiles", "arb_rank_b1", "arb_rank_b1_p"),
    (r"\quad $\beta_1$ con malla de pérdidas ancha", "arb_wide_b1", "arb_wide_b1_p"),
]


def celda(f, clave, pclave, dec):
    d = F[f]
    if clave == "lp":
        return (f"${fmt(d['arb_lp_h0_J'], dec)}$ / ${fmt(d['arb_lp_h4_J'], dec)}$",
                f"${fmt(d['arb_lp_h0_J_p'], 3)}$ / ${fmt(d['arb_lp_h4_J_p'], 3)}$")
    if clave == "wb":
        return "", " / ".join(f"${fmt(d[f'arb_wb_{k}_webb'], 3)}$" for k in ("b1", "b2", "b3"))
    if clave == "bg":
        return "", " / ".join(f"${fmt(d[f'arb_bootgar_{k}_p_comb'], 3)}$" for k in ("b1", "b2", "b3"))
    if clave == "sargan":
        return "", f"${fmt(d['arb_iv_todos_sargan_p'], 3)}$"
    if clave == "perm":
        return "", f"${fmt(d['arb_perm_p'], 3)}$"
    if clave == "chari":
        bs = [d[f"arb_chari{i}_J"] for i in range(1, 7)]
        ps = [d[f"arb_chari{i}_J_p"] for i in range(1, 7)]
        return f"${fmt(min(bs), dec)}$ a ${fmt(max(bs), dec)}$", f"$\\leq {fmt(max(ps), 3)}$"
    b = d[clave]
    p = p_de(b, d[pclave[3:]]) if pclave.startswith("se:") else d[pclave]
    s = star(p)
    return (f"${fmt(b, dec)}^{{{s}}}$" if s else f"${fmt(b, dec)}$"), f"${fmt(p, 3)}$"


def main():
    L = [r"\begin{table}[htbp]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{4pt}",
         r"\caption[Robustez a la forma funcional: logaritmos y niveles]{Robustez a la forma funcional: la "
         r"especificación principal en logaritmos y en niveles, prueba por prueba}",
         r"\label{tab:robustez-niveles}",
         r"\begin{adjustbox}{max width=\linewidth}",
         r"\begin{tabular}{lcccc}", r"\toprule",
         r" & \multicolumn{2}{c}{Log-log rezagada (principal)} & \multicolumn{2}{c}{Niveles rezagada (pb)} \\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
         r"Prueba & Coeficiente & $p$ & Coeficiente & $p$ \\", r"\midrule"]
    out = []
    for lab, clave, pclave in FILAS:
        if clave is None:
            L.append(rf"\multicolumn{{5}}{{l}}{{\textit{{{lab}}}}} \\")
            continue
        cl, pl = celda("log", clave, pclave, 4)
        cn, pn = celda("niv", clave, pclave, 3)
        L.append(f"{lab} & {cl} & {pl} & {cn} & {pn} \\\\")
        out.append(dict(prueba=lab, log_coef=cl, log_p=pl, niv_coef=cn, niv_p=pn))
    L += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}",
          r"\par\smallskip\parbox{0.95\linewidth}{\scriptsize \textit{Nota:} misma muestra (13 economías, "
          r"$N=765$ en la regresión principal), mismos rezagos, efectos fijos de país y de tiempo y errores de "
          r"Driscoll--Kraay salvo indicación. En logaritmos, $\beta_1$ es una elasticidad, $\beta_2$ una "
          r"semielasticidad y $\beta_3$ el cambio de la elasticidad por punto porcentual de $D$; en niveles, "
          r"$\beta_1$ está en puntos básicos por unidad de $JLoss$, $\beta_2$ en puntos básicos por punto "
          r"porcentual de $D$ y $\beta_3$ en puntos básicos por unidad de $JLoss$ y punto porcentual de $D$. "
          r"Los coeficientes no son comparables entre columnas; sí lo son su signo y su significancia. "
          r"Fuente: \texttt{p15\_comparacion\_formas.py} sobre \texttt{p13} y \texttt{p14} en ambos modos.}",
          r"\end{table}"]
    with open(os.path.join(TAB, "tabla_robustez_niveles.tex"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    pd.DataFrame(out).to_csv(os.path.join(HERE, "paper_comparacion_formas.csv"), index=False)
    print("  tabla_robustez_niveles.tex")


if __name__ == "__main__":
    main()
