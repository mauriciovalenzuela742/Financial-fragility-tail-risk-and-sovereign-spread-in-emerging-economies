# -*- coding: utf-8 -*-
"""
p11b_tablas_latex_conargentina.py -- EXPLORATORIO, no vigente. Genera un PDF standalone,
mismo formato que p11_tablas_latex.py (Chari et al. 2024, Tabla 4), pero con Argentina
incluida en el panel (EMBI desde Serie_Historica_Spread_del_EMBI.xlsx, GaR sin bloque Ryr
con ventana VSTX acortada, controles domesticos via IMF/WB -- ver NUMEROS_CANONICOS_BBG.md
secciones 9-10 para la justificacion y trazabilidad completa de cada pieza).

No modifica p11_tablas_latex.py ni su assert de replicacion contra los 17 paises: reutiliza
sus funciones de armado de tabla (tabla_bateria/tabla_crisis/write_tex) directamente sobre el
Panel_bloomberg.csv YA VIGENTE en disco (que a la fecha de este script ya incluye a Argentina;
ver el mismo NUMEROS_CANONICOS_BBG.md). No se propone como reemplazo de
tablas_regresiones.tex -- es un documento aparte, NO referenciado por la tesis, para revision.

Salida -> 4_Redaccion/tablas_regresiones/tablas_regresiones_conargentina.tex (+ pdf via latexmk)
"""
import os
import warnings

warnings.filterwarnings("ignore")

import p11_tablas_latex as p11

NOTA_BAT = (
    r" Incluye Argentina (14 países en total, antes 13): EMBI desde la serie histórica de "
    r"subíndices JPM EMBI GD (no está en el \texttt{embi.xlsx} canónico); GaR calculado sin el "
    r"bloque tasa/Ryr del FCI (Argentina no tiene esa serie) y con la ventana de estandarización "
    r"acortada a $\sim$9,4 años (el CPI oficial argentino solo cubre desde dic-2016) -- desviación "
    r"metodológica documentada, no aplicada a los otros 13 países. Ver "
    r"\texttt{NUMEROS\_CANONICOS\_BBG.md}, \S9--\S10. \textbf{Este documento es exploratorio: "
    r"aún no está integrado a la tesis.}")
NOTA_CR = (
    r" Incluye Argentina (antes excluida de esta batería por falta de controles domésticos; "
    r"ver \texttt{NUMEROS\_CANONICOS\_BBG.md} \S10). \textbf{Exploratorio, no integrado a la tesis.}")


def spec_con_argentina():
    spec = dict(p11.LEVELS)
    spec.update(
        lab_bat=spec["lab_bat"] + "-conarg",
        lab_cr=spec["lab_cr"] + "-conarg",
        cap_bat=spec["cap_bat"] + " (con Argentina, exploratorio)",
        cap_cr=spec["cap_cr"] + " (con Argentina, exploratorio)",
        extra_note=spec["extra_note"] + NOTA_BAT,
        extra_note_cr=spec["extra_note_cr"] + NOTA_CR,
    )
    return spec


def run():
    spec = spec_con_argentina()
    t1, r1 = p11.tabla_bateria(spec)
    t2, f2 = p11.tabla_crisis(spec)

    n_bat = int(r1[("completa", "M4", "PT")]["N"])
    n_cr = int(f2[("B_backstop_emstress", "CM4", "PT")].nobs)
    print(f"Bateria principal: N={n_bat} (14 paises esperados)")
    print(f"Bateria de crisis: N={n_cr} (647 esperado)")

    p11.write_tex("tablas_regresiones_conargentina.tex", t1, t2)


if __name__ == "__main__":
    run()
