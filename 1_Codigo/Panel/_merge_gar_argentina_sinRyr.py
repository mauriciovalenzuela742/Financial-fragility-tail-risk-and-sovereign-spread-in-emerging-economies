# -*- coding: utf-8 -*-
"""
_merge_gar_argentina_sinRyr.py -- integra el GaR de ARGENTINA (calculado sin el
bloque tasa/Ryr del FCI, ventana VSTX acortada a ~9.4 anios por la corta
historia del CPI oficial argentino) al panel CANONICO gar_panel_all18.csv.

Fuente: 1_Codigo/GaR/individuals/nlhpc_gar_all18/gar_panel_all19_ARGsinRyr.csv,
la re-estimacion conjunta (18 paises + ARGENTINA) del estimador cuantilico
pooled (fit_pfe). Ver NUMEROS_CANONICOS_BBG.md para la justificacion completa
de la desviacion metodologica (drop del bloque Ryr completo + ventana corta).

Solo AGREGA filas de ARGENTINA -- las de los 18 paises existentes en
gar_panel_all18.csv no se tocan (se verifico por separado que la diferencia
maxima al re-estimar con Argentina en el pool es |0.00043| GaR, inmaterial,
igual precedente que al agregar Rusia).

Idempotente: si ya existen filas de ARGENTINA en gar_panel_all18.csv, las
reemplaza en vez de duplicarlas.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))          # .../1_Codigo/Panel
GAR_ALL18 = os.path.join(HERE, "gar_panel_all18.csv")
GAR_ALL19_ARG = os.path.join(HERE, "..", "GaR", "individuals", "nlhpc_gar_all18",
                             "gar_panel_all19_ARGsinRyr.csv")


def main():
    base = pd.read_csv(GAR_ALL18)
    base = base[base["country"] != "ARGENTINA"].copy()   # idempotente

    src = pd.read_csv(GAR_ALL19_ARG)
    arg = src[src["country"] == "ARGENTINA"].copy()
    assert len(arg), "no se encontraron filas de ARGENTINA en el CSV fuente"

    cols = base.columns.tolist()
    assert set(cols) == set(arg.columns), (set(cols) ^ set(arg.columns))
    arg = arg[cols]

    out = pd.concat([base, arg], ignore_index=True)
    out.to_csv(GAR_ALL18, index=False)
    n_gar = arg["GaR"].notna().sum()
    print(f"ARGENTINA: {len(arg)} filas agregadas a gar_panel_all18.csv "
          f"({n_gar} con GaR no-nulo, {arg['quarter'].min()}..{arg['quarter'].max()})")
    print(f"gar_panel_all18.csv: {len(out)} filas totales, {out['country'].nunique()} paises")


if __name__ == "__main__":
    main()
