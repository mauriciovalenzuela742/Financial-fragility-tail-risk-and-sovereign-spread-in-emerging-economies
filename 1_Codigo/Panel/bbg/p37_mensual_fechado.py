# -*- coding: utf-8 -*-
"""
p37_mensual_fechado.py -- fragilidad y spread en frecuencia mensual: ¿qué antecede a qué dentro del
trimestre? (mejora C10 de 4_Redaccion/evaluacion_experta.md). Se corren exactamente estas pruebas y se
reportan todas:

Con datos trimestrales la fragilidad y el spread se mueven dentro del mismo trimestre y no se puede
ordenar qué ocurre primero. Aquí ambas series se construyen por mes:
  - Fragilidad: distancia al incumplimiento de Merton media ponderada por pasivos (-DD_w, como en
    p34), con el mismo motor (jloss_engine.merton_pd) y los mismos bancos: capitalización del último
    día del mes, volatilidad realizada de los últimos tres meses (la volatilidad "trimestral" que
    espera el motor) y el balance más reciente disponible (arrastre de hasta seis meses). No se
    calcula JLoss mensual: satura y su costo es alto; p34 muestra que la DD lleva la misma señal.
  - Spread: EMBI Global Diversified diario (2_Datos/embi.xlsx), promedio de los últimos cinco días
    hábiles del mes (cierre) y promedio del mes.

Pruebas (13 economías del panel, EF de país y de mes, errores de Driscoll-Kraay; wild bootstrap por
país para los coeficientes clave):
  1. Validación: el -DD_w del último mes de cada trimestre contra el trimestral de p34.
  2. Precedencia de la fragilidad sobre el spread: d ln EMBI_m (cierre) sobre tres rezagos propios y
     tres rezagos de d(-DD_w); suma de los rezagos cruzados y Wald conjunto. Y la dirección inversa.
  3. Asociación contemporánea: d ln EMBI_m sobre d(-DD_w)_m del mismo mes.
  4. Proyecciones locales acumuladas: ln EMBI_{m+h} - ln EMBI_{m-1} sobre d(-DD_w)_m, h = 0..6,
     controlando por tres rezagos de ambas diferencias.

Salida: bbg/fragilidad_mensual_bbg.csv y bbg/paper_p37_numeros.csv. Reutiliza p32, p34.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "JLoss_reconstruction")))

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm
from linearmodels.panel import PanelOLS

import p32_aporte_riesgo_cola as p32
import p34_fragilidad_alternativa as p34

BBG = p34.BBG
SERIE = os.path.join(HERE, "fragilidad_mensual_bbg.csv")
EMBI_XLSX = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos", "embi.xlsx"))
PAISES = {"brazil": "Brasil", "chile": "Chile", "china": "China", "colombia": "Colombia",
          "india": "India", "indonesia": "Indonesia", "malaysia": "Malasia", "mexico": "Mexico",
          "peru": "Peru", "philippines": "Filipinas", "poland": "Polonia", "southafrica": "Sudafrica",
          "turkey": "Turquia"}
NUM = p32.NUM
DK = dict(cov_type="kernel", kernel="bartlett", bandwidth=6)


def num(k, v):
    NUM[k] = float(v)


# ================================================================ series mensuales
def dd_mensual(c):
    import jloss_engine as je
    mk = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"), parse_dates=["date"])
    bal = pd.read_csv(os.path.join(BBG, c, f"balance_{c}.csv"), parse_dates=["date"])
    mk = mk.dropna(subset=["mktcap"]); mk = mk[mk["mktcap"] > 0].sort_values(["bankname", "date"])
    mk["ret"] = mk.groupby("bankname")["mktcap"].pct_change()
    mk["month"] = mk["date"].dt.to_period("M")
    ss = mk.groupby(["bankname", "month"]).agg(r2=("ret", lambda r: float((r.dropna() ** 2).sum())),
                                               nr=("ret", lambda r: int(r.notna().sum())),
                                               E=("mktcap", "last")).reset_index()
    ss = ss.sort_values(["bankname", "month"])
    g = ss.groupby("bankname")
    ss["r2_3"] = g["r2"].transform(lambda s: s.rolling(3, min_periods=3).sum())
    ss["nr_3"] = g["nr"].transform(lambda s: s.rolling(3, min_periods=3).sum())
    ss["sigma_E_q"] = np.where(ss["nr_3"] >= je.MIN_RETURNS * 3, np.sqrt(ss["r2_3"]), np.nan)
    bal["D_star"] = bal["st_borrow"] + 0.5 * bal["lt_borrow"]
    bal["month"] = bal["date"].dt.to_period("M")
    bm = bal.sort_values("date").groupby(["bankname", "month"])[["D_star", "total_liab"]].last().reset_index()
    x = ss.merge(bm, on=["bankname", "month"], how="left").sort_values(["bankname", "month"])
    x[["D_star", "total_liab"]] = x.groupby("bankname")[["D_star", "total_liab"]].transform(lambda s: s.ffill(limit=6))
    x = x.dropna(subset=["sigma_E_q", "D_star", "total_liab"])
    x = x[(x["total_liab"] > 0) & (x["D_star"] > 0)]
    x["PD"] = [je.merton_pd(e, s, dst) for e, s, dst in zip(x["E"], x["sigma_E_q"], x["D_star"])]
    x = x.dropna(subset=["PD"])
    x["DD"] = -norm.ppf(np.clip(x["PD"], 1e-8, 1 - 1e-8))
    out = x.groupby("month").apply(lambda h: pd.Series({
        "DD_w": float((h["DD"] * h["total_liab"]).sum() / h["total_liab"].sum()), "n_bancos": len(h)})).reset_index()
    out["country"] = c
    return out


def series():
    if os.path.exists(SERIE):
        s = pd.read_csv(SERIE); s["month"] = pd.PeriodIndex(s["month"], freq="M"); return s
    s = pd.concat([dd_mensual(c) for c in PAISES], ignore_index=True)
    s.to_csv(SERIE, index=False)
    return s


def embi_mensual():
    e = pd.read_excel(EMBI_XLSX); e["Fecha"] = pd.to_datetime(e["Fecha"])
    filas = []
    for c, col in PAISES.items():
        s = e[["Fecha", col]].dropna().rename(columns={col: "embi"})
        s["month"] = s["Fecha"].dt.to_period("M")
        g = s.groupby("month")["embi"]
        filas.append(pd.DataFrame({"country": c, "embi_cierre": g.apply(lambda v: v.tail(5).mean()),
                                   "embi_prom": g.mean()}).reset_index())
    return pd.concat(filas, ignore_index=True)


# ================================================================ estimación
def fit(x, y, rhs, cov="dk"):
    kw = dict(DK) if cov == "dk" else dict(cov_type="clustered", cluster_entity=True)
    return PanelOLS.from_formula(f"{y} ~ {' + '.join(rhs)} + EntityEffects + TimeEffects",
                                 x.set_index(["country", "t"])).fit(**kw)


def suma_wald(m, cruz, pref):
    b = m.params[cruz].values; V = m.cov.loc[cruz, cruz].values
    a = np.ones(len(cruz)); s = float(a @ b); se = float(np.sqrt(a @ V @ a))
    num(f"{pref}_suma", s); num(f"{pref}_suma_p", 2 * stats.norm.sf(abs(s / se)))
    num(f"{pref}_wald_p", stats.chi2.sf(float(b @ np.linalg.solve(V, b)), len(cruz)))


def main():
    print("p37: fragilidad y spread mensuales")
    s = series()
    e = embi_mensual()
    x = s.merge(e, on=["country", "month"], how="inner").sort_values(["country", "month"])
    x["F"] = -x["DD_w"]
    x["y"] = np.log(x["embi_cierre"]); x["yp"] = np.log(x["embi_prom"])
    x["t"] = x["month"].dt.to_timestamp()
    x["quarter"] = x["month"].astype(str)          # identificador de periodo que usa causal_core.demean2
    g = x.groupby("country")
    consec = (x["month"] - g["month"].shift(1)).apply(lambda v: getattr(v, "n", np.nan)) == 1
    x["dy"] = g["y"].diff().where(consec); x["dF"] = g["F"].diff().where(consec)
    for k in (1, 2, 3):
        x[f"dy_l{k}"] = g["dy"].shift(k); x[f"dF_l{k}"] = g["dF"].shift(k)
    for h in range(0, 7):
        x[f"cy{h}"] = g["y"].shift(-h) - g["y"].shift(1)
    num("N_meses", len(x)); num("paises", x["country"].nunique())
    # 1. validación contra p34 (último mes del trimestre)
    q = p34.series(); q["quarter"] = q["quarter"].astype(str)
    v = x[x["month"].dt.month.isin([3, 6, 9, 12])].copy(); v["quarter"] = v["month"].dt.asfreq("Q").astype(str)
    v = v.merge(q, on=["country", "quarter"], suffixes=("", "_q")).dropna(subset=["DD_w", "DD_w_q"])
    num("valid_corr_DD", np.corrcoef(v["DD_w"], v["DD_w_q"])[0, 1]); num("valid_N", len(v))
    # 2. precedencia
    cruz = ["dF_l1", "dF_l2", "dF_l3"]; prop = ["dy_l1", "dy_l2", "dy_l3"]
    z = x.dropna(subset=["dy"] + cruz + prop)
    m = fit(z, "dy", prop + cruz); suma_wald(m, cruz, "prec_F_a_y")
    num("prec_F_a_y_N", m.nobs)
    num("prec_F_a_y_wald_p_wild", p32.wb_run(p32.wb_prep(z, "dy", prop + cruz), cruz)[0])
    for k in cruz:
        num(f"prec_F_a_y_{k}", m.params[k]); num(f"prec_F_a_y_{k}_p", m.pvalues[k])
    sumas = []
    for c in sorted(z["country"].unique()):        # sin cada país
        mc = fit(z[z["country"] != c], "dy", prop + cruz)
        sumas.append((c, float(mc.params[cruz].sum()), float(mc.params["dF_l1"]), float(mc.pvalues["dF_l1"])))
        num(f"prec_F_a_y_sin_{c}_suma", sumas[-1][1]); num(f"prec_F_a_y_sin_{c}_l1_p", sumas[-1][3])
    num("prec_F_a_y_loo_suma_min", min(s[1] for s in sumas)); num("prec_F_a_y_loo_suma_max", max(s[1] for s in sumas))
    num("prec_F_a_y_loo_l1_p_max", max(s[3] for s in sumas))
    num("prec_F_a_y_loo_l1_n_sig05", sum(s[3] < 0.05 for s in sumas))
    mcl = fit(z, "dy", prop + cruz, cov="pais"); suma_wald(mcl, cruz, "prec_F_a_y_cluster")
    z2 = x.dropna(subset=["dF"] + cruz + prop)
    m2 = fit(z2, "dF", cruz + prop); suma_wald(m2, prop, "prec_y_a_F")
    num("prec_y_a_F_wald_p_wild", p32.wb_run(p32.wb_prep(z2, "dF", cruz + prop), prop)[0])
    # 3. contemporánea
    z3 = x.dropna(subset=["dy", "dF"] + cruz + prop)
    m3 = fit(z3, "dy", ["dF"] + prop + cruz)
    num("contemp_b", m3.params["dF"]); num("contemp_p_dk", m3.pvalues["dF"])
    num("contemp_p_wild", p32.wild(z3, "dy", ["dF"] + prop + cruz, "dF"))
    sw = float(z3["dF"].std()); num("contemp_b_por_sd", m3.params["dF"] * sw)
    # 4. proyecciones locales acumuladas
    for h in range(0, 7):
        zh = x.dropna(subset=[f"cy{h}", "dF"] + cruz + prop)
        mh = PanelOLS.from_formula(f"cy{h} ~ dF + {' + '.join(prop + cruz)} + EntityEffects + TimeEffects",
                                   zh.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett",
                                                                      bandwidth=max(6, h + 1))
        num(f"lp_h{h}_b", mh.params["dF"]); num(f"lp_h{h}_p", mh.pvalues["dF"])
    out = os.path.join(HERE, "paper_p37_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, val in NUM.items():
        print(f"  {k:30s} {val: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
