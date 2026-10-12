# -*- coding: utf-8 -*-
"""
armar_zips_prism.py -- paquetes autocontenidos para subir a Prism.

  python armar_zips_prism.py defensa      -> presentacion/defensa_latex.zip
  python armar_zips_prism.py predefensa   -> presentacion/predefensa_latex.zip
  python armar_zips_prism.py tesis        -> tesis/tesis_latex.zip
  python armar_zips_prism.py paper        -> envios/paper_empirico_prism.zip
  python armar_zips_prism.py todos

Cada zip lleva el .tex principal con las rutas apuntando dentro del zip (imagenes/, tablas/), los
archivos que carga y solo las figuras y tablas que usa. Conviene descomprimirlo en una carpeta
limpia y compilar para verificarlo.
"""
import os
import re
import sys
import zipfile

R = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(R, "envios", "paper_empirico", "figuras")
TAB = os.path.join(R, "tablas_regresiones")
INC = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
INP_TAB = re.compile(r"\\input\{\\tablasdir/([^}]+)\}")


def leer(p):
    return open(p, encoding="utf-8").read()


def figura(nombre, extra=()):
    """ruta de una figura: primero en las carpetas extra, después en las del paper."""
    for carpeta in tuple(extra) + (FIG,):
        for cand in (nombre, nombre + ".pdf", nombre + ".png"):
            p = os.path.join(carpeta, cand)
            if os.path.exists(p):
                return cand, p
    raise FileNotFoundError(nombre)


def fijar(texto, prefijo, nueva):
    lineas = texto.split("\n")
    k = next(i for i, l in enumerate(lineas) if l.startswith(prefijo))
    lineas[k] = nueva
    return "\n".join(lineas)


def deck(nombre):
    P = os.path.join(R, "presentacion")
    src = leer(os.path.join(P, nombre + ".tex"))
    zp = os.path.join(P, nombre + "_latex.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(nombre + ".tex", fijar(src, "\\graphicspath", "\\graphicspath{{imagenes/}}"))
        z.write(os.path.join(P, "tesis_beamer.sty"), "tesis_beamer.sty")
        for f in sorted(set(INC.findall(src))):
            n, p = figura(f)
            z.write(p, "imagenes/" + n)
        for t in sorted(set(re.findall(r"\\input\{(tablas/[^}]+)\}", src))):
            z.write(os.path.join(P, t), t)
    return zp


def tesis():
    T = os.path.join(R, "tesis")
    main = fijar(leer(os.path.join(T, "main.tex")), "\\graphicspath", "\\graphicspath{{imagenes/}}")
    main = fijar(main, "\\newcommand{\\tablasdir}", "\\newcommand{\\tablasdir}{tablas}   % paquete autocontenido")
    fuentes = ["anexoB_datos.tex"] + ["capitulos/" + f for f in sorted(os.listdir(os.path.join(T, "capitulos")))
                                      if f.endswith(".tex")]
    textos = {s: leer(os.path.join(T, s)) for s in fuentes}
    todo = "\n".join(textos.values())
    zp = os.path.join(T, "tesis_latex.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("main.tex", main)
        z.write(os.path.join(T, "umemoria.cls"), "umemoria.cls")
        z.write(os.path.join(T, "imagenes", "escudoU2014.pdf"), "imagenes/escudoU2014.pdf")
        for s, t in textos.items():
            z.writestr(s, t)
        for t in sorted(set(INP_TAB.findall(todo))):
            z.write(os.path.join(TAB, t + ".tex"), f"tablas/{t}.tex")
        for f in sorted(set(INC.findall(todo))):
            n, p = figura(f, extra=(os.path.join(T, "imagenes"),))
            z.write(p, "imagenes/" + n)
    return zp


def paper():
    D = os.path.join(R, "envios", "paper_empirico")
    cuerpo = leer(os.path.join(D, "cuerpo.tex"))
    main = fijar(leer(os.path.join(D, "main.tex")), "\\graphicspath", "\\graphicspath{{figuras/}}")
    main = fijar(main, "\\newcommand{\\tablasdir}",
                 "\\newcommand{\\tablasdir}{tablas}   % paquete autocontenido: tablas/ y figuras/ junto a main.tex")
    zp = os.path.join(R, "envios", "paper_empirico_prism.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("main.tex", main)
        z.writestr("cuerpo.tex", cuerpo)
        for t in sorted(set(INP_TAB.findall(cuerpo))):
            z.write(os.path.join(TAB, t + ".tex"), f"tablas/{t}.tex")
        for f in sorted(set(INC.findall(cuerpo))):
            n, p = figura(f)
            z.write(p, "figuras/" + n)
    return zp


TAREAS = {"defensa": lambda: deck("defensa"), "predefensa": lambda: deck("predefensa"),
          "tesis": tesis, "paper": paper}

if __name__ == "__main__":
    cual = sys.argv[1] if len(sys.argv) > 1 else "todos"
    for k in (TAREAS if cual == "todos" else [cual]):
        zp = TAREAS[k]()
        print(f"{k:10s} -> {os.path.relpath(zp, R)}  ({len(zipfile.ZipFile(zp).namelist())} archivos)")
