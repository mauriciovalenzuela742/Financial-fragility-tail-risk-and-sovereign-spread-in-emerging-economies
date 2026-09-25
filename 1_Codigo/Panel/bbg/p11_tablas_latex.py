# -*- coding: utf-8 -*-
"""
p11_tablas_latex.py -- exporta a LaTeX (formato Chari et al. 2024, Tabla 4: coeficiente con
estrellas y error estandar entre parentesis, N, R2, filas de efectos fijos SI/NO) las dos
baterias vigentes. No modifica p8 ni p9b: reutiliza sus funciones de ajuste tal cual.

  Tabla 1 (tab:bateria-se)  -- columna (1) = especificacion de referencia
                               EMBI = a_i + d_t + b1 JLoss + b2 D + b3 JLoss x D + e   (M4, FE pais+tiempo)
                               columnas (2)-(12) = resto de la bateria p8 (M1-M4 x FE T/P/PT).
                               Panel A muestra completa, Panel B sin trimestres de crisis.
  Tabla 2 (tab:crisis-se)   -- columna (1) = Ecuacion eq:crisisint (CM4, FE pais+tiempo)
                               columnas (2)-(12) = resto de la bateria p9b (CM1-CM4 x FE T/P/PT).
                               Panel A vector unico, Panel B Backstop/EMstress.

Convencion D = -GaR: los coeficientes de GaR e interaccion de p8 se multiplican por -1
(el error estandar no cambia), igual que en la Tabla tab:bateria de la tesis.

Salida -> 4_Redaccion/tablas_regresiones/tablas_regresiones.tex (documento compilable)
"""
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore")

import p8_bateria_regresiones as p8
import p9b_bateria_crisis as p9b
from p2_regresiones import prep as prep_ctrl, CTRLS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "4_Redaccion", "tablas_regresiones"))

# orden de columnas: (1) referencia, luego el resto de la grilla agrupada por modelo
FES = ("T", "P", "PT")


def col_order(models):
    ref = (models[-1], "PT")
    rest = [(m, fe) for m in models for fe in FES if (m, fe) != ref]
    return [ref] + rest


# ---------------------------------------------------------------- formato
DEC = 3  # decimales de coeficientes y errores estandar (p12 usa 4)

def num(x, dec=3):
    s = f"{x:.{dec}f}".replace("-", "-")
    s = s.replace(".", "{,}")
    return f"${s}$" if x >= 0 else f"${s}$"


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def cell_b(b, p, dec=None):
    dec = DEC if dec is None else dec
    if b is None or np.isnan(b):
        return ""
    st = stars(p)
    s = f"{b:.{dec}f}".replace(".", "{,}")
    return f"${s}^{{{st}}}$" if st else f"${s}$"


def cell_se(se, dec=None):
    dec = DEC if dec is None else dec
    if se is None or np.isnan(se):
        return ""
    return f"$({se:.{dec}f})$".replace(".", "{,}")


def cell_p(p):
    if p is None or np.isnan(p):
        return ""
    return "$[p<0{,}001]$" if p < 0.001 else f"$[p={p:.3f}]$".replace(".", "{,}")


def row(label, cells):
    return f"{label} & " + " & ".join(cells) + r" \\"


def header(cols, model_lbl):
    """Encabezado: (1) referencia | bloques por modelo."""
    n = len(cols)
    lines = []
    groups = []  # (label, start, end) 1-indexed de columnas de datos
    groups.append(("Referencia", 1, 1))
    i = 2
    for m in model_lbl:
        k = sum(1 for c in cols[1:] if c[0] == m)
        groups.append((m, i, i + k - 1))
        i += k
    top = " & ".join(
        [rf"\multicolumn{{{e - s + 1}}}{{c}}{{{g}}}" for g, s, e in groups])
    lines.append(f"& {top} \\\\")
    lines.append("".join(rf"\cmidrule(lr){{{s + 1}-{e + 1}}}" for _, s, e in groups))
    lines.append("& " + " & ".join(f"({j})" for j in range(1, n + 1)) + r" \\")
    return lines


def fe_rows(cols):
    pais = ["SÍ" if fe in ("P", "PT") else "NO" for _, fe in cols]
    tiempo = ["SÍ" if fe in ("T", "PT") else "NO" for _, fe in cols]
    return [row("EF de país", pais), row("EF de tiempo", tiempo)]


# ---------------------------------------------------------------- especificacion
# Una "spec" define datos y etiquetas. Los datos deben traer las columnas que usan las funciones
# de ajuste de p8 (EMBI_bps, JLoss, GaR_pp) y de p9b (_DV, JLoss, D_pp); una spec alternativa
# (p12: log-log rezagada) solo reemplaza el contenido de esas columnas.
def _prep_crisis_niveles():
    d = prep_ctrl()
    d["D_pp"] = -d["GaR_pp"]
    return d


LEVELS = dict(
    prep_bat=p8.prep,
    prep_cr=_prep_crisis_niveles,
    dv="EMBI (pb)",
    jl="$JLoss$", dd="$D=-GaR$", jxd=r"$JLoss\times D$",
    cap_bat="Spread soberano, fragilidad bancaria y riesgo de cola",
    cap_cr="Spread soberano e interacción con el vector de crisis",
    lab_bat="tab:bateria-se", lab_cr="tab:crisis-se",
    intro_bat=(
        r"La tabla reporta estimaciones de panel "
        r"del spread soberano (EMBI Global Diversified, puntos básicos) sobre la fragilidad bancaria sistémica "
        r"($JLoss$), el riesgo de cola del crecimiento ($D=-GaR$, percentil 5\% del crecimiento con signo "
        r"invertido, en puntos porcentuales; un $D$ mayor indica una cola más adversa) y su interacción. "
        r"La columna (1) es la especificación que se busca contrastar, "
        r"$\mathrm{EMBI}_{i,t}=\alpha_i+\delta_t+\beta_1 JLoss_{i,t}+\beta_2 D_{i,t}+\beta_3(JLoss\times D)_{i,t}+\varepsilon_{i,t}$, "
        r"con efectos fijos de país y de tiempo."),
    intro_cr=(
        r"La columna (1) es la Ecuación de "
        r"interacción de crisis completa, "
        r"$\mathrm{EMBI}_{i,t}=\alpha_i+\delta_t+\beta_1 JLoss+\beta_2 D+\beta_3(JLoss\times D)"
        r"+\beta_4(JLoss\times D\times Crisis)+\beta_5(JLoss\times Crisis)+\beta_6(D\times Crisis)+\omega'X_{i,t}+\varepsilon_{i,t}$, "
        r"con efectos fijos de país y de tiempo."),
    jm="JLoss", dm="D",  # nombres (modo matematico) para las filas de interaccion con crisis
    extra_note="", extra_note_cr="",
    src_bat=r"\texttt{p8\_bateria\_regresiones.py}",
    src_cr=r"\texttt{p9b\_bateria\_crisis.py}",
)


# ---------------------------------------------------------------- Tabla 1
def tabla_bateria(spec=LEVELS):
    d = spec["prep_bat"]()
    samples = {"completa": d, "sin crisis": d[~d["quarter"].isin(p8.CRISIS_Q)].copy()}
    models = ["M1", "M2", "M3", "M4"]
    cols = col_order(models)
    res = {}
    for sname, ds in samples.items():
        for m in models:
            for fe in FES:
                r = p8.fit_one(ds, m, fe)
                # D = -GaR  =>  coef(D) = -coef(GaR); coef(JLoss x D) = -coef(JLoss x GaR)
                for k in ("GaR", "Int"):
                    r[k]["b"] = -r[k]["b"]
                res[(sname, m, fe)] = r

    L = []
    L += [r"\begin{landscape}", r"\begin{table}", r"\centering", r"\footnotesize",
          r"\setlength{\tabcolsep}{3.2pt}", r"\renewcommand{\arraystretch}{1.08}",
          rf"\caption[{spec['cap_bat']}]{{\textbf{{{spec['cap_bat']}.}}}}",
          rf"\label{{{spec['lab_bat']}}}",
          r"\begin{tabular}{l c ccc ccc ccc cc}",
          r"\toprule",
          spec["dv"]]
    L += header(cols, models)
    L.append(r"\midrule")

    panels = [("completa", r"\textit{Panel A. Muestra completa}"),
              ("sin crisis", r"\textit{Panel B. Sin trimestres de crisis (excluye 2008Q4--2009Q4 y 2020Q1--2021Q4)}")]
    for pi, (sname, title) in enumerate(panels):
        if pi:
            L.append(r"\midrule")
        L.append(rf"\multicolumn{{{len(cols) + 1}}}{{l}}{{{title}}} \\[2pt]")
        for key, lbl in (("JLoss", spec["jl"]), ("GaR", spec["dd"]), ("Int", spec["jxd"])):
            L.append(row(lbl, [cell_b(res[(sname, m, fe)][key]["b"], res[(sname, m, fe)][key]["p"])
                               for m, fe in cols]))
            L.append(row("", [cell_se(res[(sname, m, fe)][key]["se"]) for m, fe in cols]))
        L.append(r"\addlinespace")
        L.append(row("Observaciones", [str(res[(sname, m, fe)]["N"]) for m, fe in cols]))
        L.append(row("Países", [str(res[(sname, m, fe)]["paises"]) for m, fe in cols]))
        L.append(row(r"$R^2$ \textit{within}",
                     [num(res[(sname, m, fe)]["r2w"]) for m, fe in cols]))
    L.append(r"\midrule")
    L += fe_rows(cols)
    L.append(row("Controles domésticos", ["NO"] * len(cols)))
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")
    L.append(
        r"\par\smallskip\parbox{\linewidth}{\scriptsize \textit{Nota:} " + spec["intro_bat"] + spec["extra_note"] +
        r" Las columnas (2)--(12) completan la batería de cuatro modelos "
        r"anidados (M1: $JLoss$; M2: $D$; M3: $JLoss+D$; M4: $JLoss+D+JLoss\times D$) bajo efectos fijos solo de "
        r"tiempo, solo de país, o de ambos. $JLoss$ y $D$ están centrados en su media muestral; $JLoss\times D$ "
        r"es el producto de ambos centrados. Sin controles domésticos. Errores estándar de Driscoll--Kraay "
        r"(kernel de Bartlett) entre paréntesis. ***, ** y * indican significancia al 1\%, 5\% y 10\%, "
        r"respectivamente. Fuente: " + spec["src_bat"] + ".}")
    L += [r"\end{table}", r"\end{landscape}"]
    return "\n".join(L), res


# ---------------------------------------------------------------- Tabla 2
def tabla_crisis(spec=LEVELS):
    d = spec["prep_cr"]()
    J, D = spec["jm"], spec["dm"]
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    models = ["CM1", "CM2", "CM3", "CM4"]
    cols = col_order(models)

    fits = {}
    for pname, dummies in p9b.PANELS:
        for m in models:
            for fe in FES:
                mod, dd, _ = p9b.fit_crisis_model(d, m, dummies, fe, ctr)
                fits[(pname, m, fe)] = mod

    def g(mod, n):
        if n in mod.params.index:
            return float(mod.params[n]), float(mod.std_errors[n]), float(mod.pvalues[n])
        return np.nan, np.nan, np.nan

    def coef_rows(pname, name, lbl):
        vals = [g(fits[(pname, m, fe)], name) for m, fe in cols]
        return [row(lbl, [cell_b(b, p) for b, _, p in vals]),
                row("", [cell_se(se) for _, se, _ in vals])]

    def sum_rows(pname, nm, lbl):
        cells_b, cells_se, cells_p = [], [], []
        for m, fe in cols:
            mod = fits[(pname, m, fe)]
            if "JxD" in mod.params.index and f"JxD_{nm}" in mod.params.index:
                b, se, _, p = p9b._lincom(mod, ["JxD", f"JxD_{nm}"])
                cells_b.append(cell_b(b, p)); cells_se.append(cell_se(se)); cells_p.append(cell_p(p))
            else:
                cells_b.append(""); cells_se.append(""); cells_p.append("")
        return [row(lbl, cells_b), row("", cells_se), row("", cells_p)]

    L = []
    L += [r"\begin{landscape}", r"\begin{table}", r"\centering", r"\scriptsize",
          r"\setlength{\tabcolsep}{2.8pt}", r"\renewcommand{\arraystretch}{0.86}",
          rf"\caption[{spec['cap_cr']}]{{\textbf{{{spec['cap_cr']}.}}}}",
          rf"\label{{{spec['lab_cr']}}}",
          r"\begin{tabular}{l c ccc ccc ccc cc}",
          r"\toprule",
          spec["dv"]]
    L += header(cols, models)
    L.append(r"\midrule")

    common = [("JLoss_c", spec["jl"]), ("D_c", spec["dd"]), ("JxD", spec["jxd"] + r" ($\beta_3$)")]
    # Panel A
    pA = "A_vector_unico"
    L.append(rf"\multicolumn{{{len(cols) + 1}}}{{l}}{{\textit{{Panel A. Vector único de crisis}} "
             r"($Crisis$: 2008Q4--2009Q4, 2015Q3--2016Q1, 2020Q1--2021Q4)} \\[2pt]")
    for n, lbl in common:
        L += coef_rows(pA, n, lbl)
    L += coef_rows(pA, "JLoss_cr", rf"${J}\times Crisis$")
    L += coef_rows(pA, "D_cr", rf"${D}\times Crisis$")
    L += coef_rows(pA, "JxD_cr", rf"${J}\times {D}\times Crisis$ ($\beta_4$)")
    L += sum_rows(pA, "cr", r"$\beta_3+\beta_4$")
    L.append(r"\addlinespace")
    L.append(row("Observaciones", [str(int(fits[(pA, m, fe)].nobs)) for m, fe in cols]))
    L.append(row(r"$R^2$ \textit{within}", [num(float(fits[(pA, m, fe)].rsquared_within)) for m, fe in cols]))
    # Panel B
    pB = "B_backstop_emstress"
    L.append(r"\midrule")
    L.append(rf"\multicolumn{{{len(cols) + 1}}}{{l}}{{\textit{{Panel B. Backstop (2008Q4--2009Q4, 2020Q1--2021Q4) "
             r"vs.\ EMstress (2015Q3--2016Q1)}} \\[2pt]")
    for n, lbl in common:
        L += coef_rows(pB, n, lbl)
    L += coef_rows(pB, "JLoss_bk", rf"${J}\times Backstop$")
    L += coef_rows(pB, "D_bk", rf"${D}\times Backstop$")
    L += coef_rows(pB, "JxD_bk", rf"${J}\times {D}\times Backstop$ ($\beta_4^{{bk}}$)")
    L += coef_rows(pB, "JLoss_em", rf"${J}\times EMstress$")
    L += coef_rows(pB, "D_em", rf"${D}\times EMstress$")
    L += coef_rows(pB, "JxD_em", rf"${J}\times {D}\times EMstress$ ($\beta_4^{{em}}$)")
    L += sum_rows(pB, "bk", r"$\beta_3+\beta_4^{bk}$")
    L += sum_rows(pB, "em", r"$\beta_3+\beta_4^{em}$")
    L.append(r"\addlinespace")
    L.append(row("Observaciones", [str(int(fits[(pB, m, fe)].nobs)) for m, fe in cols]))
    L.append(row(r"$R^2$ \textit{within}", [num(float(fits[(pB, m, fe)].rsquared_within)) for m, fe in cols]))
    L.append(r"\midrule")
    L += fe_rows(cols)
    L.append(row("Controles domésticos", ["SÍ"] * len(cols)))
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")
    L.append(
        r"\par\smallskip\parbox{\linewidth}{\scriptsize \textit{Nota:} " + spec["intro_cr"] + spec["extra_note_cr"] +
        r" Las columnas (2)--(12) completan la batería de cuatro modelos "
        r"anidados: CM1, $JLoss$ y su interacción con el vector de crisis; CM2, lo mismo con $D$; CM3, ambos "
        r"niveles y sus interacciones, sin $JLoss\times D$; CM4, la especificación completa. $Crisis$ sola "
        r"queda absorbida por los efectos fijos de tiempo cuando estos se incluyen. $\beta_3$ mide la "
        r"complementariedad fuera de crisis y $\beta_3+\beta_4$ dentro de crisis (error estándar por método "
        r"delta; entre corchetes, $p$ del test de Wald $H_0\!:\beta_3+\beta_4=0$). Todas las columnas incluyen "
        r"seis controles domésticos (deuda/PIB, balance fiscal/PIB, reservas/PIB, cuenta corriente/PIB, "
        r"inflación y tipo de cambio real efectivo). $JLoss$ y $D$ centrados. Errores estándar de "
        r"Driscoll--Kraay entre paréntesis. ***, ** y * indican significancia al 1\%, 5\% y 10\%, "
        r"respectivamente. Fuente: " + spec["src_cr"] + ".}")
    L += [r"\end{table}", r"\end{landscape}"]
    return "\n".join(L), fits


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{booktabs}
\usepackage{pdflscape}
\usepackage{amsmath}

\begin{document}
"""


def panel_variant(spec):
    """Si JLOSS_PANEL_CSV apunta al panel con EMBI extendido, devuelve (sufijo, spec ajustada)."""
    if os.path.basename(p8.PANEL_CSV) == "Panel_bloomberg.csv":
        return "", spec
    nota = (r" EMBI de Indonesia y Sudáfrica en 2010Q1--2014Q4 completado con la serie trimestral "
            r"del FMI (GFSR), sin reescalar (correlación 0,94 y ratio mediano 1,02 frente a J.P.\ Morgan "
            r"en 80 trimestres de solape); resto de la muestra idéntico al panel principal.")
    nota_cr = r" EMBI de Indonesia y Sudáfrica 2010Q1--2014Q4 completado con FMI (GFSR)."
    lab_bat = spec["lab_bat"] + "-embiext"
    spec = dict(spec, lab_bat=lab_bat, lab_cr=spec["lab_cr"] + "-embiext",
                cap_bat=spec["cap_bat"] + " (EMBI extendido)", cap_cr=spec["cap_cr"] + " (EMBI extendido)",
                extra_note=spec["extra_note"] + nota,
                extra_note_cr=spec["extra_note_cr"].replace(spec["lab_bat"], lab_bat) + nota_cr)
    return "_embiext", spec


def write_tex(name, t1, t2):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, name)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(PREAMBLE + "\n" + t1 + "\n\n\\clearpage\n\n" + t2 + "\n\n\\end{document}\n")
    print("Guardado:", out)


def run():
    sfx, spec = panel_variant(LEVELS)
    t1, r1 = tabla_bateria(spec)
    t2, f2 = tabla_crisis(spec)

    if not sfx:
        # verificacion contra los CSV canonicos (bateria_bbg.csv, GaR all18; ver NUMEROS_CANONICOS_BBG.md)
        ref = r1[("sin crisis", "M4", "PT")]["Int"]["b"]
        assert abs(ref - 1.171261) < 5e-4, ref
        b, _, _, p = p9b._lincom(f2[("B_backstop_emstress", "CM4", "PT")], ["JxD", "JxD_em"])
        assert abs(b - 1.050632) < 5e-4, b
        assert int(f2[("B_backstop_emstress", "CM4", "PT")].nobs) == 614

    write_tex(f"tablas_regresiones{sfx}.tex", t1, t2)
    return r1, f2


if __name__ == "__main__":
    run()
