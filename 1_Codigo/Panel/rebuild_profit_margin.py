# -*- coding: utf-8 -*-
"""
rebuild_profit_margin.py
=========================
Reconstruye 'profit margin' del sector bancario (control del paper de JLoss,
Chari et al. 2024) desde los archivos crudos del pipeline matlab viejo:

    matlab/data_banks_avgprofitmargin.xls  (matriz quarter_date x countries)

La estructura de filas/columnas se recupero leyendo matlab/a_extrae_data_bancos.m
(que arma la matriz como matrix_profit_marginavg_ready(:,i) para el pais i) y
cruzando contra las variables 'quarter_date' (52 trimestres, 1999Q1-2011Q4) y
'countries' (28 paises, mismo orden de columnas) guardadas en
output_v0/data_pds_processed_allcountries.mat.

LIMITACION IMPORTANTE: esta serie termina en 2011Q4 (fin de la ventana del
pipeline matlab original). No cubre 2012 en adelante -- para esos anios hace
falta una fuente nueva (WDI/IMF FSI a nivel pais, o la extraccion nueva del
JLoss-pipeline una vez que produzca net_income/net_revenue por banco).

Salida: profit_margin_1999_2011.csv  (country, quarter, profit_margin)
"""
import numpy as np
import pandas as pd
import scipy.io as sio

MAT_PATH = "../output_v0/data_pds_processed_allcountries.mat"
XLS_PATH = "data_banks_avgprofitmargin.xls"

NAMEMAP = {"south_africa": "southafrica"}


def main():
    m = sio.loadmat(MAT_PATH, variable_names=["quarter_date", "countries"])
    quarter_date = m["quarter_date"].ravel().astype(int).tolist()
    countries = [m["countries"][0, i][0] for i in range(m["countries"].shape[1])]

    d = pd.read_excel(XLS_PATH, sheet_name="Hoja1", header=None)
    assert d.shape == (len(quarter_date), len(countries)), \
        f"Forma inesperada {d.shape}, se esperaba ({len(quarter_date)}, {len(countries)})"
    d.columns = countries
    d.index = quarter_date
    d.index.name = "time"
    d = d.reset_index().melt(id_vars="time", var_name="country", value_name="profit_margin")

    # 0 = relleno de MATLAB (sin dato), no un profit margin real de 0%
    d.loc[d["profit_margin"] == 0, "profit_margin"] = np.nan
    d = d.dropna(subset=["profit_margin"])

    d["country"] = d["country"].map(lambda c: NAMEMAP.get(c, c))
    d["year"] = d["time"] // 10
    d["q"] = d["time"] % 10
    d["quarter"] = d["year"].astype(str) + "Q" + d["q"].astype(str)
    out = d[["country", "quarter", "profit_margin"]].sort_values(["country", "quarter"])
    out.to_csv("profit_margin_1999_2011.csv", index=False)
    print(f"Guardado: profit_margin_1999_2011.csv  ({out.shape[0]} obs, "
          f"{out['country'].nunique()} paises, 1999Q1-2011Q4)")


if __name__ == "__main__":
    main()
