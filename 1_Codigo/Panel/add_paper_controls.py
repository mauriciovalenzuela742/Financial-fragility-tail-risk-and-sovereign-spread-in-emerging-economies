# -*- coding: utf-8 -*-
"""
add_paper_controls.py
======================
Fusiona global_controls_quarterly.csv (salida de fetch_global_controls.py)
en las tres bases del panel y agrega las transformaciones log que usa el
paper de JLoss (Chari et al., 2024) para sus controles domesticos ya
disponibles (debt_gdp).

Correr DESPUES de fetch_global_controls.py, en el mismo directorio que:
    Panel_final_prebackup.csv, Panel_final.csv, Panel_extended_15paises.csv,
    global_controls_quarterly.csv
"""
import numpy as np
import pandas as pd

glob = pd.read_csv("global_controls_quarterly.csv")
keep_glob = ["quarter", "UST10Y_log", "US_HY_spread_log", "OnOffRun_spread_log"]
glob = glob[keep_glob]

for path in ["Panel_final_prebackup.csv", "Panel_final.csv", "Panel_extended_15paises.csv"]:
    d = pd.read_csv(path)
    d = d.merge(glob, on="quarter", how="left")
    if "debt_gdp" in d.columns:
        d["debt_gdp_log"] = np.log(d["debt_gdp"])
    d.to_csv(path, index=False)
    cov = d["UST10Y_log"].notna().mean() * 100
    print(f"{path}: {d.shape}  cobertura factores globales={cov:.0f}%")
