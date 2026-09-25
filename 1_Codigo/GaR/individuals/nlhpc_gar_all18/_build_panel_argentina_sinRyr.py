# -*- coding: utf-8 -*-
"""
_build_panel_argentina_sinRyr.py -- EXPLORATORIO, no vigente.

Agrega ARGENTINA (N_Country=19) al pool de GaR_panel_all18.xlsx, usando:
  - g_GDP: individuals/ARGENTINA/gGDP_ARGENTINA.csv (crecimiento trimestral, IMF IFS)
  - FCI:   1_Codigo/GaR/_FCI_ARGENTINA_sinRyr_EXPLORATORIO.csv (bloque tasa/Ryr
           eliminado por completo -- Argentina no tiene archivo Ryr -- y con la
           ventana de estandarizacion VSTX acortada a ~9.4 anios, ya que el CPI
           oficial de Argentina solo cubre desde dic-2016; ver _fci_sin_ryr.py)
  - VIX:   pegado por fecha desde la serie global ya presente en el panel
           (identica para todos los paises en la misma fecha).

Salida: GaR_panel_all19_ARGsinRyr.xlsx (NO reemplaza GaR_panel_all18.xlsx).
Esto es una desviacion metodologica documentada (ventana VSTX mas corta para
un solo pais) -- no se propone como reemplazo del pool canonico de 18 paises,
solo para responder la pregunta puntual de si Argentina podria tener un GaR
propio sin el bloque Ryr.
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))              # .../GaR/individuals/nlhpc_gar_all18
GAR_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))      # .../1_Codigo/GaR
IND = os.path.join(GAR_ROOT, "individuals")

XLSX_IN = os.path.join(HERE, "GaR_panel_all18.xlsx")
XLSX_OUT = os.path.join(HERE, "GaR_panel_all19_ARGsinRyr.xlsx")
FCI_ARG_CSV = os.path.join(GAR_ROOT, "_FCI_ARGENTINA_sinRyr_EXPLORATORIO.csv")


def quarterly_fci(fci_m):
    f = fci_m.copy()
    f["DATES"] = pd.to_datetime(f["DATES"])
    f["m"] = f["DATES"].dt.month
    f = f[f["m"].isin([3, 6, 9, 12])].copy()
    f["Date"] = pd.to_datetime(dict(year=f["DATES"].dt.year, month=f["m"], day=1))
    return f.set_index("Date")["FCI"]


def main():
    panel = pd.read_excel(XLSX_IN, sheet_name="Panel")
    n_countries_existing = panel["N_Country"].max()
    print(f"Panel base: {len(panel)} filas, {panel['Country'].nunique()} paises "
          f"(N_Country max = {n_countries_existing}).")

    ggdp = pd.read_csv(os.path.join(IND, "ARGENTINA", "gGDP_ARGENTINA.csv"))
    ggdp.columns = ["Date", "g_GDP"]
    ggdp["Date"] = pd.to_datetime(ggdp["Date"], dayfirst=True)

    fci_m = pd.read_csv(FCI_ARG_CSV)
    fci_q = quarterly_fci(fci_m)
    print(f"g_GDP ARGENTINA: {ggdp['Date'].min().date()} .. {ggdp['Date'].max().date()} "
          f"({len(ggdp)} trimestres)")
    print(f"FCI ARGENTINA (sin Ryr, trimestral): {fci_q.index.min().date()} .. "
          f"{fci_q.index.max().date()} ({len(fci_q)} trimestres)")

    # VIX global: identico para todos los paises en la misma fecha -> tomar de cualquiera
    vix = panel[["Date", "VIX"]].drop_duplicates(subset="Date").copy()
    vix["_d"] = pd.to_datetime(vix["Date"], format="%d/%m/%Y")
    vix_map = vix.set_index("_d")["VIX"]

    arg = pd.DataFrame({"Date": ggdp["Date"]})
    arg["Country"] = "ARGENTINA"
    arg["N_Country"] = int(n_countries_existing) + 1
    arg["g_GDP"] = ggdp["g_GDP"].to_numpy()
    arg["VIX"] = arg["Date"].map(vix_map)
    arg["FCI"] = arg["Date"].map(fci_q)

    n_fci = arg["FCI"].notna().sum()
    n_vix = arg["VIX"].notna().sum()
    print(f"Filas ARGENTINA construidas: {len(arg)}  (FCI no-nulo: {n_fci}, VIX no-nulo: {n_vix})")
    if n_vix < len(arg):
        missing = arg.loc[arg["VIX"].isna(), "Date"]
        print(f"  AVISO: {len(missing)} fechas de ARGENTINA sin VIX en el panel global "
              f"(fuera del rango cubierto por VIX): {missing.min().date()}..{missing.max().date()}")

    arg["Date"] = arg["Date"].dt.strftime("%d/%m/%Y")
    out = pd.concat([panel, arg[["Date", "Country", "N_Country", "g_GDP", "VIX", "FCI"]]],
                    ignore_index=True)
    out.to_excel(XLSX_OUT, sheet_name="Panel", index=False)
    print(f"\nEscrito: {XLSX_OUT}  ({len(out)} filas, {out['Country'].nunique()} paises)")


if __name__ == "__main__":
    main()
