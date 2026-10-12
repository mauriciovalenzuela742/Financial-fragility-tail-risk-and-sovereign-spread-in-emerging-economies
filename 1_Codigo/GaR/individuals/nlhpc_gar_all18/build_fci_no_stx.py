# -*- coding: utf-8 -*-
"""
build_fci_no_stx.py -- robustez de solapamiento GaR <-> JLoss.

JLoss se construye con la volatilidad del precio de las acciones bancarias; el FCI que alimenta
el GaR tiene un bloque bursatil (VSTX, CMAX). Para descartar que la asociacion del riesgo de cola
con el spread venga de esa informacion compartida, se recalcula el FCI de los 18 paises del pool
SIN el bloque bursatil: forma cuadratica 2x2 sobre [iRyr, iEER] con su correlacion EWMA (misma
logica que _fci_sin_ryr.py, que quita el bloque de tasas). Los subindices salen de
fci_engine.compute_fci, sin modificar el motor.

Salida:
  GaR_panel_all18_noSTX.xlsx   (mismo formato que GaR_panel_all18.xlsx, FCI reemplazado)
  _fci_stx_diag.csv            (corr FCI base vs noSTX por pais)

Luego: python gar_insample_robustez.py GaR_panel_all18_noSTX.xlsx noSTX
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GAR_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # .../1_Codigo/GaR
sys.path.insert(0, GAR_ROOT)
sys.path.insert(0, HERE)
import fci_engine as fe  # noqa: E402
from build_fci_no_cdiff import quarterly_from_monthly, IND, US, INITIAL, FINAL  # noqa: E402

XLSX_IN = os.path.join(HERE, "GaR_panel_all18.xlsx")
XLSX_OUT = os.path.join(HERE, "GaR_panel_all18_noSTX.xlsx")


def fci_sin_bursatil(idx):
    """FCI = I'CI con I = [iRyr, iEER] y C = [[1, cRE], [cRE, 1]] (sin iSTX)."""
    r = idx["iRyr"].to_numpy(); e = idx["iEER"].to_numpy()
    c = fe.corr_EWMA(r, e)
    out = idx[["DATES"]].copy()
    out["FCI"] = r * r + e * e + 2 * c * r * e
    return out


def main():
    panel = pd.read_excel(XLSX_IN, sheet_name="Panel")
    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    countries = sorted(panel["Country"].dropna().unique())
    diag, new_fci = [], {}
    for c in countries:
        cdir = os.path.join(IND, c)
        if not os.path.isdir(cdir):
            print(f"  {c:14s} SIN CARPETA -> se deja el FCI original")
            continue
        try:
            base = fe.compute_fci(cdir, c, US, initial=INITIAL, final=FINAL)
        except Exception as e:
            print(f"  {c:14s} ERROR compute_fci: {e} -> FCI original")
            continue
        qb = quarterly_from_monthly(base[["DATES", "FCI"]])
        qn = quarterly_from_monthly(fci_sin_bursatil(base))
        j = pd.concat([qb.rename("base"), qn.rename("nostx")], axis=1).dropna()
        r = j["base"].corr(j["nostx"])
        diag.append(dict(country=c, n=len(j), corr=r))
        new_fci[c] = qn
        print(f"  {c:14s} n={len(j):3d}  corr(FCI, FCI_noSTX) = {r:.3f}")
    dd = pd.DataFrame(diag)
    dd.to_csv(os.path.join(HERE, "_fci_stx_diag.csv"), index=False)
    print(f"\nCorr media ponderada por n: {np.average(dd['corr'], weights=dd['n']):.3f}   "
          f"min: {dd['corr'].min():.3f} ({dd.loc[dd['corr'].idxmin(), 'country']})")
    out = panel.copy()
    for c, qn in new_fci.items():
        mask = out["Country"] == c
        out.loc[mask, "FCI"] = out.loc[mask, "_d"].map(qn)
    out.drop(columns="_d").to_excel(XLSX_OUT, sheet_name="Panel", index=False)
    print(f"Escrito: {XLSX_OUT}")


if __name__ == "__main__":
    main()
