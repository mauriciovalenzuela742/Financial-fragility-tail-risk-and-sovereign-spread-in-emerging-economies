# -*- coding: utf-8 -*-
"""
build_fci_no_ryr.py -- GaR homologado para incorporar a Argentina (mejora C11 de
4_Redaccion/evaluacion_experta.md).

Argentina no tiene serie de rendimiento soberano local (Ryr), de modo que su FCI se calculó sin el bloque
de tasas (_fci_sin_ryr.py) y su GaR no es comparable con el del resto. Aquí se homologa al revés: se
recalcula el FCI de los 18 países del pool SIN el bloque de tasas ---forma cuadrática 2x2 sobre
[iSTX, iEER] con su correlación EWMA, la misma estructura que el de Argentina--- y se agrega Argentina
con el FCI de GaR_panel_all19_ARGsinRyr.xlsx. Los subíndices salen de fci_engine.compute_fci, sin
modificar el motor. La única diferencia que persiste es la ventana de estandarización de VSTX de
Argentina (~9,4 años, por la cobertura de su IPC oficial); se declara.

Salida:
  GaR_panel_all19_noRyr.xlsx  (mismo formato que GaR_panel_all18.xlsx)
  _fci_ryr_diag.csv           (corr FCI base vs noRyr por país)

Luego: python gar_insample_robustez.py GaR_panel_all19_noRyr.xlsx all19noRyr
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GAR_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GAR_ROOT)
sys.path.insert(0, HERE)
import fci_engine as fe  # noqa: E402
from build_fci_no_cdiff import quarterly_from_monthly, IND, US, INITIAL, FINAL  # noqa: E402

XLSX_18 = os.path.join(HERE, "GaR_panel_all18.xlsx")
XLSX_ARG = os.path.join(HERE, "GaR_panel_all19_ARGsinRyr.xlsx")
XLSX_OUT = os.path.join(HERE, "GaR_panel_all19_noRyr.xlsx")


def fci_sin_tasas(idx):
    """FCI = I'CI con I = [iSTX, iEER] y C = [[1, cSE], [cSE, 1]] (sin iRyr)."""
    s = idx["iSTX"].to_numpy(); e = idx["iEER"].to_numpy()
    c = fe.corr_EWMA(s, e)
    out = idx[["DATES"]].copy()
    out["FCI"] = s * s + e * e + 2 * c * s * e
    return out


def main():
    panel = pd.read_excel(XLSX_ARG, sheet_name="Panel")       # 18 países + Argentina (FCI sin Ryr)
    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    countries = sorted(c for c in panel["Country"].dropna().unique() if str(c).upper() != "ARGENTINA")
    diag, new_fci = [], {}
    for c in countries:
        cdir = os.path.join(IND, c)
        try:
            base = fe.compute_fci(cdir, c, US, initial=INITIAL, final=FINAL)
        except Exception as e:
            print(f"  {c:14s} ERROR compute_fci: {e} -> se excluye del pool homologado")
            new_fci[c] = None
            continue
        qb = quarterly_from_monthly(base[["DATES", "FCI"]])
        qn = quarterly_from_monthly(fci_sin_tasas(base))
        j = pd.concat([qb.rename("base"), qn.rename("noryr")], axis=1).dropna()
        r = j["base"].corr(j["noryr"])
        diag.append(dict(country=c, n=len(j), corr=r))
        new_fci[c] = qn
        print(f"  {c:14s} n={len(j):3d}  corr(FCI, FCI_noRyr) = {r:.3f}")
    dd = pd.DataFrame(diag)
    dd.to_csv(os.path.join(HERE, "_fci_ryr_diag.csv"), index=False)
    print(f"\nCorr media ponderada por n: {np.average(dd['corr'], weights=dd['n']):.3f}   "
          f"min: {dd['corr'].min():.3f} ({dd.loc[dd['corr'].idxmin(), 'country']})")
    out = panel.copy()
    for c, qn in new_fci.items():
        mask = out["Country"] == c
        out.loc[mask, "FCI"] = np.nan if qn is None else out.loc[mask, "_d"].map(qn)
    out.drop(columns="_d").to_excel(XLSX_OUT, sheet_name="Panel", index=False)
    print(f"Escrito: {XLSX_OUT}")


if __name__ == "__main__":
    main()
