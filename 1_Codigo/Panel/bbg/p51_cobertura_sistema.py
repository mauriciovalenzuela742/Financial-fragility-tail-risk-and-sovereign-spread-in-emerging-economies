# -*- coding: utf-8 -*-
"""
p51_cobertura_sistema.py -- mu6 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f) y
resumen de la familia primaria.

  mu6 (secundaria): (a) la regresión principal exigiendo al menos 3, 4 y 5 bancos cotizados por
       economía-trimestre; (b) cobertura aproximada de los bancos cotizados: sus activos sobre el crédito de
       los bancos al sector privado (GFDD.DI.02 x PIB en moneda local, Banco Mundial), promedio por país.
       Es una cota (activos > crédito) y descriptiva; los balances de Bloomberg están en millones de moneda
       local.
  Familia primaria: Holm sobre los seis p unilaterales (mu1-H1, mu1-H2, mu3-H1, mu3-H2, mu4-H1, mu5-H1),
       leídos de paper_p46/p48/p49/p50_numeros.csv; veredicto "firme" como en el preregistro.
Salida: bbg/paper_p51_numeros.csv y bbg/cobertura_bancos_bbg.csv. Requiere red para (b).
"""
import os
import sys
import json
import urllib.request
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p46_panel_bancos as p46

NUM = p32.NUM
ISO = {"brazil": "BRA", "chile": "CHL", "china": "CHN", "colombia": "COL", "india": "IND", "indonesia": "IDN",
       "malaysia": "MYS", "mexico": "MEX", "peru": "PER", "philippines": "PHL", "poland": "POL",
       "southafrica": "ZAF", "turkey": "TUR"}
COB = os.path.join(HERE, "cobertura_bancos_bbg.csv")


def wb_anual(ind):
    url = f"https://api.worldbank.org/v2/country/{';'.join(ISO.values())}/indicator/{ind}?format=json&per_page=5000&date=2004:2024"
    with urllib.request.urlopen(url, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8"))
    inv = {v: k for k, v in ISO.items()}
    return pd.DataFrame([{"country": inv[x["countryiso3code"]], "anio": int(x["date"]), ind: x["value"]}
                         for x in d[1] if x["value"] is not None and x["countryiso3code"] in inv])


def cobertura(b):
    if os.path.exists(COB):
        return pd.read_csv(COB)
    a = b.assign(anio=b["quarter"].str[:4].astype(int))
    a = a[a["quarter"].str.endswith("Q4")].groupby(["country", "anio"])["tot_asset"].sum().reset_index()
    w = wb_anual("GFDD.DI.02").merge(wb_anual("NY.GDP.MKTP.CN"), on=["country", "anio"])
    a = a.merge(w, on=["country", "anio"], how="inner")
    a["cobertura_cota"] = a["tot_asset"] * 1e6 / (a["GFDD.DI.02"] / 100 * a["NY.GDP.MKTP.CN"]) * 100
    a.to_csv(COB, index=False)
    return a


def holm(ps):
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden); acum = 0.0; out = {}
    for r, (k, p) in enumerate(orden):
        acum = max(acum, min(1.0, (m - r) * p)); out[k] = acum
    return out


def main():
    b = p46.panel()
    d, raw = p14.base(); p14.check_principal(d)
    # (a) umbral de bancos
    nb = b.groupby(["country", "quarter"])["bankname"].size().rename("nb").reset_index()
    nb["quarter"] = (pd.PeriodIndex(nb["quarter"], freq="Q") + 1).astype(str)
    dd = d.merge(nb, on=["country", "quarter"], how="left")
    for k in (3, 4, 5):
        x = p42.centrar(dd[dd["nb"] >= k].dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]))
        rhs = ["J_c", "T_c", "JxT"]; m = p42.fit(x, "ln_EMBI", rhs)
        NUM[f"mu6_min{k}_N"] = float(m.nobs); NUM[f"mu6_min{k}_paises"] = float(x["country"].nunique())
        for v, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            NUM[f"mu6_min{k}_{lab}"] = float(m.params[v]); NUM[f"mu6_min{k}_{lab}_p_dk"] = float(m.pvalues[v])
        NUM[f"mu6_min{k}_b1_p_wild"] = p32.wild(x, "ln_EMBI", rhs, "J_c")
    # (b) cobertura
    try:
        c = cobertura(b)
        for pais, v in c.groupby("country")["cobertura_cota"].median().items():
            NUM[f"mu6_cobertura_{pais}"] = float(v)
    except Exception as e:
        print("  cobertura no disponible:", e)
    # familia primaria
    leer = lambda f: pd.read_csv(os.path.join(HERE, f), index_col=0)["valor"]
    v46, v48, v49, v50 = leer("paper_p46_numeros.csv"), leer("paper_p48_numeros.csv"), leer("paper_p49_numeros.csv"), leer("paper_p50_numeros.csv")
    ps = {"mu1h1": v46["mu1h1_p_uni"], "mu1h2": v46["mu1h2_p_uni"], "mu3h1": v48["mu3h1_p_uni"],
          "mu3h2": v48["mu3h2_p_uni"], "mu4h1": v49["mu4h1_p_uni"], "mu5h1": v50["mu5h1_p_uni"]}
    loo = {"mu1h1": (v46["mu1h1_loo_ok"], v46["mu1h1_loo_n"]), "mu1h2": (v46["mu1h2_loo_ok"], v46["mu1h2_loo_n"]),
           "mu3h1": (v48["mu3h1_loo_ok"], v48["mu3h1_loo_n"]), "mu3h2": (v48["mu3h2_loo_ok"], v48["mu3h2_paises"]),
           "mu4h1": (v49["mu4h1_loo_ok"], v49["mu4h1_paises"]), "mu5h1": (v50["mu5h1_loo_ok"], v50["mu5h1_paises"])}
    for k, ph in holm(ps).items():
        NUM[f"familia_{k}_p_uni"] = float(ps[k]); NUM[f"familia_{k}_p_holm"] = float(ph)
        NUM[f"familia_{k}_firme"] = float(ph < 0.05 and loo[k][0] == loo[k][1])
    out = os.path.join(HERE, "paper_p51_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, val in NUM.items():
        print(f"  {k:28s} {val: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
