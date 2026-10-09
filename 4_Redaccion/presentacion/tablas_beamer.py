# -*- coding: utf-8 -*-
"""
tablas_beamer.py -- versiones para la presentación de las baterías de la tesis.

Lee las tablas generadas por p12 (tablas_regresiones/tablas_regresiones_lnlag_embiext_t1.tex y
_t2.tex), conserva las 12 columnas y los coeficientes con sus estrellas, quita las filas de errores
estándar y escribe las etiquetas en palabras. Las cifras no se transcriben: salen de las mismas
tablas de la tesis. Salida: presentacion/tablas/{bat_A,bat_B,bat_C,crisis_unico,crisis_bkem}.tex (y *_ee.tex, con
errores estándar, para el respaldo),
que defensa.tex carga con \\input{tablas/...}.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "tablas_regresiones")
OUT = os.path.join(HERE, "tablas")

# etiquetas en palabras; se evalúan en orden (la primera que calce gana)
ETIQUETAS = [
    (r"\\times D_\{t-1\}\\times Backstop", r"Interacción $\times$ \textit{Backstop}, $\beta_4^{bk}$"),
    (r"\\times D_\{t-1\}\\times EMstress", r"Interacción $\times$ \textit{EMstress}, $\beta_4^{em}$"),
    (r"\\times D_\{t-1\}\\times Crisis", r"Interacción $\times$ crisis, $\beta_4$"),
    (r"^\$\\beta_3\+\\beta_4\^\{bk\}", r"\textbf{Bajo \textit{Backstop}}, $\beta_3+\beta_4^{bk}$"),
    (r"^\$\\beta_3\+\\beta_4\^\{em\}", r"\textbf{Bajo \textit{EMstress}}, $\beta_3+\beta_4^{em}$"),
    (r"^\$\\beta_3\+\\beta_4\$", r"\textbf{Interacción en crisis}, $\beta_3+\beta_4$"),
    (r"\\ln\(JLoss\)_\{t-1\}\\times Backstop", r"Fragilidad $\times$ \textit{Backstop}"),
    (r"\\ln\(JLoss\)_\{t-1\}\\times EMstress", r"Fragilidad $\times$ \textit{EMstress}"),
    (r"\\ln\(JLoss\)_\{t-1\}\\times Crisis", r"Fragilidad $\times$ crisis"),
    (r"D_\{t-1\}\\times Backstop", r"Riesgo de cola $\times$ \textit{Backstop}"),
    (r"D_\{t-1\}\\times EMstress", r"Riesgo de cola $\times$ \textit{EMstress}"),
    (r"D_\{t-1\}\\times Crisis", r"Riesgo de cola $\times$ crisis"),
    (r"\\ln\(JLoss\)_\{t-1\}\\times D_\{t-1\}", r"\textbf{Interacción}, $\beta_3$"),
    (r"^\$D_\{t-1\}=-GaR", r"Riesgo de cola, $\beta_2$"),
    (r"^\$\\ln\(JLoss\)_\{t-1\}\$", r"Fragilidad, $\beta_1$"),
    (r"^Observaciones", r"Observaciones"),
]


def etiqueta(label):
    for pat, nuevo in ETIQUETAS:
        if re.search(pat, label):
            return nuevo
    return None


def cuerpo(lines, con_ee=False):
    """filas de coeficientes (sin errores estándar salvo con_ee), con la fila [p=...] pegada a su suma."""
    out = []
    for ln in lines:
        s = ln.strip()
        if not s or "&" not in s:
            continue
        label, resto = s.split("&", 1)
        label = label.strip()
        if label == "":
            if "[p=" in resto:                       # p-valor de una suma beta3+beta4: se conserva
                out.append(" & " + resto.strip())
            if con_ee and "$(" in resto:              # fila de errores estándar: solo en el respaldo
                out.append(" & " + resto.strip())
            continue
        nuevo = etiqueta(label)
        if nuevo:
            out.append(nuevo + " & " + resto.strip())
    return out


DEC = re.compile(r"(-?\d+)\{,\}(\d{4,})")


def tres_decimales(fila):
    """redondea a 3 decimales los coeficientes (las láminas principales; el respaldo conserva 4)."""
    return DEC.sub(lambda m: f"{float(m.group(1) + '.' + m.group(2)):.3f}".replace(".", "{,}"), fila)


ENCABEZADO = r"""\begingroup\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.3}%%
\begin{adjustbox}{max width=0.97\textwidth}
\begin{tabular}{l c ccc ccc ccc cc}
\toprule
 & Ref. & \multicolumn{3}{c}{%(m)s1} & \multicolumn{3}{c}{%(m)s2} & \multicolumn{3}{c}{%(m)s3} & \multicolumn{2}{c}{%(m)s4} \\
\cmidrule(lr){2-2}\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-11}\cmidrule(lr){12-13}
Efectos fijos & PT & T & P & PT & T & P & PT & T & P & PT & T & P \\
 & (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) & (9) & (10) & (11) & (12) \\
\midrule
"""
PIE = r"""\bottomrule
\end{tabular}
\end{adjustbox}\endgroup
"""


def escribir(nombre, filas, prefijo):
    os.makedirs(OUT, exist_ok=True)
    txt = ENCABEZADO % {"m": prefijo}
    if not nombre.endswith("_ee.tex"):
        filas = [tres_decimales(f) for f in filas]
    for f in filas:
        if f.startswith("Observaciones"):
            txt += r"\addlinespace" + "\n"
        txt += f.replace("\\\\", "").rstrip() + r" \\" + "\n"
    txt += PIE
    with open(os.path.join(OUT, nombre), "w", encoding="utf-8") as fh:
        fh.write("% Generado por tablas_beamer.py a partir de las tablas de la tesis; no editar a mano.\n" + txt)
    print(nombre, len(filas), "filas")


def paneles(path):
    """divide una tabla de p12 en paneles según las filas \\multicolumn{13}{l}{\\textit{Panel ...}}."""
    lines = open(path, encoding="utf-8").read().split("\n")
    marcas = [i for i, l in enumerate(lines) if l.startswith(r"\multicolumn{13}{l}{\textit{Panel")]
    res = []
    for k, i in enumerate(marcas):
        j = marcas[k + 1] if k + 1 < len(marcas) else len(lines)
        bloque = []
        for l in lines[i + 1:j]:
            if l.startswith(r"\midrule") or l.startswith(r"\bottomrule"):
                break
            bloque.append(l)
        res.append(bloque)
    return res


def main():
    a, b, c = paneles(os.path.join(SRC, "tablas_regresiones_lnlag_embiext_t1.tex"))
    escribir("bat_A.tex", cuerpo(a), "M")
    escribir("bat_B.tex", cuerpo(b), "M")
    escribir("bat_C.tex", cuerpo(c), "M")
    unico, bkem = paneles(os.path.join(SRC, "tablas_regresiones_lnlag_embiext_t2.tex"))
    escribir("crisis_unico.tex", cuerpo(unico), "CM")
    escribir("crisis_bkem.tex", cuerpo(bkem), "CM")
    # versiones con errores estándar para el respaldo
    for nombre, bloque, pref in (("bat_A_ee.tex", a, "M"), ("bat_B_ee.tex", b, "M"), ("bat_C_ee.tex", c, "M"),
                                 ("crisis_unico_ee.tex", unico, "CM"), ("crisis_bkem_ee.tex", bkem, "CM")):
        escribir(nombre, cuerpo(bloque, con_ee=True), pref)


if __name__ == "__main__":
    main()
