# -*- coding: utf-8 -*-
r"""
armar_zip.py -- arma tesis_latex.zip, autocontenido para compilar en Overleaf o Prism:
  main.tex, umemoria.cls, anexoB_datos.tex, capitulos/*.tex, tablas/*.tex (las que la tesis usa, desde
  ../tablas_regresiones) e imagenes/* (las figuras que la tesis incluye, desde imagenes/ o desde las del paper).
En la copia de main.tex, \tablasdir apunta a tablas/ y \graphicspath solo a imagenes/.

  python armar_zip.py
"""
import os
import re
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
TABLAS = os.path.join(AQUI, "..", "tablas_regresiones")
FIGS = [os.path.join(AQUI, "imagenes"), os.path.join(AQUI, "..", "envios", "paper_empirico", "figuras")]
SALIDA = os.path.join(AQUI, "tesis_latex.zip")


def leer(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main():
    main_tex = leer(os.path.join(AQUI, "main.tex"))
    entradas = re.findall(r"\\input\{([^}]+)\}", main_tex)
    tex = {"main.tex": None, "anexoB_datos.tex": os.path.join(AQUI, "anexoB_datos.tex")}
    for e in entradas:
        if e.startswith("capitulos/"):
            tex[e + ".tex"] = os.path.join(AQUI, e + ".tex")
    fuentes = [main_tex, leer(os.path.join(AQUI, "umemoria.cls"))] + [leer(p) for k, p in tex.items() if p]
    todo = "\n".join(fuentes)
    tablas = sorted(set(re.findall(r"\\tablasdir/([A-Za-z0-9_]+)", todo)))
    figs = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", todo)))
    copia = main_tex.replace(r"\newcommand{\tablasdir}{../tablas_regresiones}", r"\newcommand{\tablasdir}{tablas}")
    copia = re.sub(r"\\graphicspath\{.*\}", r"\\graphicspath{{imagenes/}}", copia, count=1)
    faltan = []
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("main.tex", copia)
        z.write(os.path.join(AQUI, "umemoria.cls"), "umemoria.cls")
        for k, p in tex.items():
            if p:
                z.write(p, k)
        for t in tablas:
            z.write(os.path.join(TABLAS, t + ".tex"), f"tablas/{t}.tex")
        for f in figs:
            base = os.path.basename(f) if os.path.splitext(f)[1] else os.path.basename(f) + ".pdf"
            ruta = next((os.path.join(d, base) for d in FIGS if os.path.exists(os.path.join(d, base))), None)
            if ruta is None:
                faltan.append(f); continue
            z.write(ruta, f"imagenes/{os.path.basename(base)}")
    print(f"{SALIDA}: {len(tex)} tex, {len(tablas)} tablas, {len(figs) - len(faltan)} figuras")
    if faltan:
        print("FALTAN:", faltan)


if __name__ == "__main__":
    main()
