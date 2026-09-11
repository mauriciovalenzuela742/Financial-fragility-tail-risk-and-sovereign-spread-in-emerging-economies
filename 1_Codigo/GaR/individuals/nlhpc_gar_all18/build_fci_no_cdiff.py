# -*- coding: utf-8 -*-
"""
build_fci_no_cdiff.py -- robustez de endogeneidad Ryr <-> EMBI.

Recalcula el FCI de los 18 paises del pool GaR SIN el termino CDIFF (el
diferencial de yields reales local - EE.UU., el unico objeto tipo-spread dentro
del FCI, que se solapa conceptualmente con el EMBI). iRyr pasa de
(VRyr + CDIFF)/2 a solo VRyr (volatilidad del cambio del yield real).

Salida:
  GaR_panel_all18_noCDIFF.xlsx   (mismo formato que GaR_panel_all18.xlsx, FCI reemplazado)
  _fci_cdiff_diag.csv            (corr FCI base vs noCDIFF por pais)

Luego: correr phase2 sobre el xlsx nuevo para obtener gar_panel_all18_noCDIFF.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GAR_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # .../1_Codigo/GaR
sys.path.insert(0, GAR_ROOT)
import fci_engine as fe  # noqa: E402

XLSX_IN = os.path.join(HERE, "GaR_panel_all18.xlsx")
XLSX_OUT = os.path.join(HERE, "GaR_panel_all18_noCDIFF.xlsx")
IND = os.path.join(GAR_ROOT, "individuals")
US = os.path.join(IND, "US")
INITIAL, FINAL = "1990-01-01", "2026-05-31"


def quarterly_from_monthly(fci_m):
    """FCI mensual (fin de mes) -> serie por trimestre, con la fecha estilo xlsx
    (primer dia del ultimo mes del trimestre: YYYY-{03,06,09,12}-01)."""
    f = fci_m.copy()
    f["m"] = f["DATES"].dt.month
    f = f[f["m"].isin([3, 6, 9, 12])].copy()
    f["Date"] = pd.to_datetime(dict(year=f["DATES"].dt.year, month=f["m"], day=1))
    return f.set_index("Date")["FCI"]


def main():
    panel = pd.read_excel(XLSX_IN, sheet_name="Panel")
    panel["_d"] = pd.to_datetime(panel["Date"], format="%d/%m/%Y")
    countries = sorted(panel["Country"].dropna().unique())
    print(f"Panel: {len(countries)} paises, {panel['_d'].min().date()}..{panel['_d'].max().date()}")

    diag = []
    new_fci = {}
    for c in countries:
        cdir = os.path.join(IND, c)
        if not os.path.isdir(cdir):
            print(f"  {c:14s} SIN CARPETA -> se deja el FCI original")
            continue
        try:
            base = fe.compute_fci(cdir, c, US, initial=INITIAL, final=FINAL,
                                  drop_cdiff=False)
            nocd = fe.compute_fci(cdir, c, US, initial=INITIAL, final=FINAL,
                                  drop_cdiff=True)
        except Exception as e:
            print(f"  {c:14s} ERROR compute_fci: {e} -> FCI original")
            continue
        qb = quarterly_from_monthly(base)
        qn = quarterly_from_monthly(nocd)
        j = pd.concat([qb.rename("base"), qn.rename("nocd")], axis=1).dropna()
        r = j["base"].corr(j["nocd"])
        r_stress = j.loc[j["base"] > j["base"].quantile(0.80)].corr().iloc[0, 1]
        diag.append(dict(country=c, n=len(j), corr=r, corr_top20pct=r_stress,
                         mean_base=j["base"].mean(), mean_nocd=j["nocd"].mean()))
        new_fci[c] = qn
        print(f"  {c:14s} n={len(j):3d}  corr(FCI, FCI_noCDIFF) = {r:.3f}  "
              f"(cola 20% sup: {r_stress:.3f})")

    dd = pd.DataFrame(diag)
    dd.to_csv(os.path.join(HERE, "_fci_cdiff_diag.csv"), index=False)
    print(f"\nPooled corr (media ponderada por n): "
          f"{np.average(dd['corr'], weights=dd['n']):.3f}   "
          f"min por pais: {dd['corr'].min():.3f} ({dd.loc[dd['corr'].idxmin(),'country']})")

    # --- reemplazar la columna FCI y escribir el xlsx nuevo ---
    out = panel.copy()
    for c, qn in new_fci.items():
        mask = out["Country"] == c
        out.loc[mask, "FCI"] = out.loc[mask, "_d"].map(qn)
    out = out.drop(columns="_d")
    out.to_excel(XLSX_OUT, sheet_name="Panel", index=False)
    n_filled = out["FCI"].notna().sum()
    print(f"\nEscrito: {XLSX_OUT}  ({n_filled} FCI no-nulos de {len(out)} filas)")
    print("Siguiente: phase2 con SOURCE_FILE = GaR_panel_all18_noCDIFF.xlsx")


if __name__ == "__main__":
    main()
