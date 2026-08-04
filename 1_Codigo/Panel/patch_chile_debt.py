# -*- coding: utf-8 -*-
"""
patch_chile_debt.py
===================
Inserta la serie de Deuda Bruta Gobierno Central (% del PIB) de Chile, del Banco
Central de Chile (serie F051.D7.PPB.C.Z.Z.T), en la columna debt_gdp de
Panel_final.csv. Solo rellena las filas de Chile (que venían vacías por falta de
cobertura WDI); no toca los demás países.

Entradas (mismo directorio):
    Panel_final.csv
    PEM_FP_DP.xlsx        (export del BCCh; hoja 'Cuadro')

Salida:
    Panel_final.csv       (sobrescrito; respaldo en Panel_final_prebackup.csv)

REQUISITOS: pip install pandas openpyxl
"""

import pandas as pd
import shutil

PANEL = "Panel_final.csv"
DEBT_XLSX = "PEM_FP_DP.xlsx"

# 1. Serie de deuda de Chile (% PIB)
ch = pd.read_excel(DEBT_XLSX, sheet_name="Cuadro", header=2)
ch = ch.rename(columns={ch.columns[0]: "date", ch.columns[1]: "debt_chile"})
ch = ch.dropna(subset=["date"]).copy()
ch["date"] = pd.to_datetime(ch["date"], errors="coerce")
ch = ch.dropna(subset=["date"])
ch["quarter"] = ch["date"].dt.to_period("Q").astype(str)
ch["debt_chile"] = pd.to_numeric(ch["debt_chile"], errors="coerce")
ch = ch[["quarter", "debt_chile"]]

# 2. Panel
p = pd.read_csv(PANEL)
shutil.copy(PANEL, "Panel_final_prebackup.csv")          # respaldo

n_missing_before = p[p["country"] == "chile"]["debt_gdp"].isna().sum()

# 3. Rellenar SOLO Chile, solo donde está vacío
p = p.merge(ch, on="quarter", how="left")
mask = (p["country"] == "chile") & (p["debt_gdp"].isna())
p.loc[mask, "debt_gdp"] = p.loc[mask, "debt_chile"]
p = p.drop(columns=["debt_chile"])

# 4. Reporte y guardado
n_missing_after = p[p["country"] == "chile"]["debt_gdp"].isna().sum()
p.to_csv(PANEL, index=False)

print(f"Chile: filas debt_gdp vacías  antes={n_missing_before}  después={n_missing_after}")
print(f"Cobertura global debt_gdp: {p['debt_gdp'].notna().mean()*100:.0f}%  "
      f"({p['debt_gdp'].notna().sum()}/{len(p)})")
print("\nChile debt_gdp (muestra):")
print(p[p.country == "chile"][["quarter", "debt_gdp"]].head(6).to_string(index=False))
print("\nGuardado:", PANEL, " | respaldo: Panel_final_prebackup.csv")