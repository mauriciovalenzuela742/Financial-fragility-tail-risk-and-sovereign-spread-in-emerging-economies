# -*- coding: utf-8 -*-
"""
p67_datos_esg.py -- datos del preregistro 9 (4_Redaccion/preregistro_esg.md, commit 81c2d9c, anterior a
este script y a los datos).

  - Las 18 variables del índice ESG de Barneche, Grezzi y Panario (2024) desde la API del Banco Mundial:
    12 de WDI (source=2) y los seis WGI (source=3, códigos GOV_WGI_*.EST). CO2 per cápita con
    EN.GHG.CO2.PC.CE.AR5, porque la serie que usó ORT (EN.ATM.CO2E.PC) está descontinuada.
  - Variables de Tebaldi, Nguyen y Zuluaga (2018) para lo exploratorio: crecimiento del PIB, apertura y
    liberalización política de Freedom House, 8 - (PR + CL)/2 con las calificaciones 1-7
    (2_Datos/freedomhouse/FIW_ratings_1973-2024.xlsx, edición 2024 = año 2023).
  - 13 economías del panel más Argentina, años 2000-2025.

Reglas del preregistro (sección 2), aplicadas aquí en la serie anual:
  - vacíos intermedios: interpolación lineal entre años observados;
  - vacíos al final: se arrastra el último valor hasta tres años, con la marca <var>_arr = 1.
La transformación a trimestres (escalón con un año de rezago de publicación, o interpolación como robustez)
está en a_trimestral(), que usa p68.

Salida: 2_Datos/esg_wb_anual.csv (country, iso3, year, variables, marcas _arr).
"""
import json
import os
import time
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DATOS = os.path.join(ROOT, "2_Datos")
OUT = os.path.join(DATOS, "esg_wb_anual.csv")
FIW = os.path.join(DATOS, "freedomhouse", "FIW_ratings_1973-2024.xlsx")

ISO3 = {"brazil": "BRA", "chile": "CHL", "china": "CHN", "colombia": "COL", "india": "IND",
        "indonesia": "IDN", "malaysia": "MYS", "mexico": "MEX", "peru": "PER", "philippines": "PHL",
        "poland": "POL", "southafrica": "ZAF", "turkey": "TUR", "argentina": "ARG"}
FIW_NOMBRE = {"brazil": "Brazil", "chile": "Chile", "china": "China", "colombia": "Colombia",
              "india": "India", "indonesia": "Indonesia", "malaysia": "Malaysia", "mexico": "Mexico",
              "peru": "Peru", "philippines": "Philippines", "poland": "Poland",
              "southafrica": "South Africa", "turkey": "Turkey", "argentina": "Argentina"}
Y0, Y1 = 2000, 2025
ARRASTRE = 3

# nombre -> (código, source)
SERIES = {
    # E
    "energia":     ("EG.EGY.PRIM.PP.KD", 2),   # intensidad energética primaria (MJ / USD PPA 2017)
    "renovable":   ("EG.FEC.RNEW.ZS", 2),      # % del consumo final de energía
    "co2":         ("EN.GHG.CO2.PC.CE.AR5", 2),
    "bosque":      ("AG.LND.FRST.ZS", 2),
    "recursos":    ("NY.ADJ.DRES.GN.ZS", 2),   # agotamiento de recursos naturales, % INB
    "agua":        ("ER.H2O.FWST.ZS", 2),      # estrés hídrico
    # S
    "matricula":   ("SE.SEC.ENRR", 2),
    "salud":       ("SH.XPD.GHED.CH.ZS", 2),
    "vida":        ("SP.DYN.LE00.IN", 2),
    "paridad":     ("SE.ENR.PRIM.FM.ZS", 2),
    "vulnerable":  ("SL.EMP.VULN.ZS", 2),
    "mujer_hombre": ("SL.TLF.CACT.FM.ZS", 2),
    # G
    "voz":         ("GOV_WGI_VA.EST", 3),
    "estabilidad": ("GOV_WGI_PV.EST", 3),
    "efectividad": ("GOV_WGI_GE.EST", 3),
    "regulacion":  ("GOV_WGI_RQ.EST", 3),
    "ley":         ("GOV_WGI_RL.EST", 3),
    "corrupcion":  ("GOV_WGI_CC.EST", 3),
    # Tebaldi et al. (2018)
    "crecimiento": ("NY.GDP.MKTP.KD.ZG", 2),
    "apertura":    ("NE.TRD.GNFS.ZS", 2),
}


def wb_fetch(indicator, source, tries=4):
    iso = ";".join(ISO3.values())
    url = (f"https://api.worldbank.org/v2/country/{iso}/indicator/{indicator}"
           f"?source={source}&format=json&per_page=20000&date={Y0}:{Y1}")
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                data = json.load(r)
            rows = data[1] if isinstance(data, list) and len(data) > 1 and data[1] else []
            out = [(x["countryiso3code"], int(str(x["date"])[:4]), float(x["value"]))
                   for x in rows if x["value"] is not None]
            return pd.DataFrame(out, columns=["iso3", "year", "value"])
        except Exception as e:
            print(f"    [WB {indicator}] intento {k + 1}/{tries} falló: {str(e)[:70]}")
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"sin respuesta para {indicator}")


def freedom_house():
    """Liberalización política = 8 - (PR + CL)/2, por año bajo revisión."""
    d = pd.read_excel(FIW, sheet_name="Country Ratings, Statuses ", header=None)
    anios = d.iloc[1].ffill()
    out = []
    for c, nom in FIW_NOMBRE.items():
        fila = d[d[0].astype(str).str.strip() == nom]
        assert len(fila) == 1, nom
        fila = fila.iloc[0]
        for j in range(1, d.shape[1] - 2, 3):
            if str(d.iloc[2, j]).strip() != "PR":
                continue
            try:
                y = int(str(anios[j]).strip()[-4:])
                pr, cl = float(fila[j]), float(fila[j + 1])
            except ValueError:
                continue
            if Y0 <= y <= Y1:
                out.append((ISO3[c], y, 8 - (pr + cl) / 2))
    return pd.DataFrame(out, columns=["iso3", "year", "value"])


def completar(s):
    """Serie anual indexada por año (Y0..Y1): interpolación interior y arrastre final de hasta 3 años."""
    s = s.reindex(range(Y0, Y1 + 1))
    obs = s.dropna()
    arr = pd.Series(0, index=s.index)
    if obs.empty:
        return s, arr
    s = s.interpolate(limit_area="inside")
    ult = obs.index.max()
    for y in range(ult + 1, min(ult + ARRASTRE, Y1) + 1):
        s.loc[y] = obs.loc[ult]
        arr.loc[y] = 1
    return s, arr


def a_trimestral(anual, cols, modo="escalon"):
    """anual: country, year, cols -> country, quarter, cols, con un año de rezago de publicación.
    escalon: el valor del año y en los cuatro trimestres de y+1 (principal, sin anticipación).
    interp: el valor del año y anclado en el T3 de y+1 e interpolado (robustez)."""
    frames = []
    for c, g in anual.groupby("country"):
        g = g.set_index("year").sort_index()
        idx = pd.period_range(f"{Y0 + 1}Q1", f"{Y1 + 1}Q4", freq="Q")
        f = pd.DataFrame(index=idx, columns=cols, dtype=float)
        for col in cols:
            for y, v in g[col].items():
                if modo == "escalon":
                    f.loc[[p for p in idx if p.year == y + 1], col] = v
                else:
                    f.loc[pd.Period(f"{y + 1}Q3", freq="Q"), col] = v
            if modo == "interp":
                f[col] = f[col].astype(float).interpolate(limit_area="inside")
        f.insert(0, "country", c)
        f.insert(1, "quarter", idx.astype(str))
        frames.append(f.reset_index(drop=True))
    return pd.concat(frames, ignore_index=True)


def main():
    inv = {v: k for k, v in ISO3.items()}
    base = pd.MultiIndex.from_product([list(ISO3.values()), range(Y0, Y1 + 1)], names=["iso3", "year"])
    tab = pd.DataFrame(index=base)
    fuentes = {k: v for k, v in SERIES.items()}
    for nombre, (cod, src) in fuentes.items():
        r = wb_fetch(cod, src)
        print(f"  {nombre:13s} {cod:22s} n={len(r):4d} años {r['year'].min()}-{r['year'].max()}", flush=True)
        tab[nombre] = r.set_index(["iso3", "year"])["value"]
    fh = freedom_house()
    print(f"  {'libertad':13s} {'Freedom House':22s} n={len(fh):4d} años {fh['year'].min()}-{fh['year'].max()}")
    tab["libertad"] = fh.set_index(["iso3", "year"])["value"]

    out = []
    for iso, g in tab.groupby(level="iso3"):
        g = g.droplevel("iso3")
        fila = pd.DataFrame({"iso3": iso, "country": inv[iso], "year": range(Y0, Y1 + 1)})
        for col in g.columns:
            s, arr = completar(g[col])
            fila[col] = s.values
            fila[f"{col}_arr"] = arr.values
        out.append(fila)
    out = pd.concat(out, ignore_index=True)
    out.to_csv(OUT, index=False)
    vars_ = list(SERIES) + ["libertad"]
    print(f"-> {OUT}  ({len(out)} filas)")
    cob = out[out["year"].between(2003, 2025)].groupby("country")[vars_].apply(lambda x: x.notna().mean())
    print("Cobertura 2003-2025 (fracción de años con dato tras completar):")
    print(cob.round(2).T.to_string())


if __name__ == "__main__":
    main()
