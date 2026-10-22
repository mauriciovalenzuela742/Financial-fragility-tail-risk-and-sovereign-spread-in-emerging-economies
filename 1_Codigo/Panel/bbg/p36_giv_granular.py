# -*- coding: utf-8 -*-
"""
p36_giv_granular.py -- variable instrumental granular para la fragilidad bancaria (mejora C9 de
4_Redaccion/evaluacion_experta.md). Se corren exactamente estas variantes y se reportan todas:

Instrumento (Gabaix y Koijen, 2024, "Granular Instrumental Variables", JPE): en cada economía y
trimestre, el retorno accionario de los bancos ponderado por tamaño menos el de igual ponderación,
    z_ct = sum_b S_b,t-1 r_bt - (1/n_ct) sum_b r_bt,
con S la participación del banco en los pasivos del sistema en t-1 y r el retorno logarítmico
trimestral de su capitalización bursátil. Cualquier choque común a los bancos de un país (incluida
una noticia soberana que los afecte por igual) se cancela en la diferencia; queda la parte
idiosincrásica de los bancos grandes, que mueve la fragilidad del sistema por su peso. Variante (b):
antes de agregar, se quita a cada banco su carga sobre el retorno medio de su país (beta estimada en
toda la muestra), como en la extracción de factores de Gabaix y Koijen.

Especificación: la regresión principal sin interacción (ln EMBI_t sobre fragilidad_{t-1} y D_{t-1},
EF de país y de tiempo), con la fragilidad instrumentada por z_{c,t-1}; la fragilidad es ln JLoss o
-DD_w (p34). Se reportan: primera etapa (coeficiente, F con DK y con cluster), forma reducida (p DK,
cluster y wild bootstrap; es la prueba de Anderson-Rubin con un instrumento), 2SLS (cluster por país)
y la versión con z_{c,t-2}.

Supuesto de exclusión (declarado): z no afecta al spread salvo por la fragilidad. Lo violaría que
los bancos grandes tengan una exposición soberana distinta de la de los chicos (un choque al spread
movería más su retorno). Por eso se reporta además la correlación de z_{c,t-1} con el cambio del
spread en t-1 (prueba de que el instrumento no responde al spread contemporáneo).

Simplificaciones: retornos de capitalización (incluyen emisiones y recompras; se recortan al 1 % y
99 %); bancos con al menos 8 trimestres; economías-trimestre con al menos 3 bancos.

Salida: bbg/giv_granular_bbg.csv y bbg/paper_p36_numeros.csv. Reutiliza p13, p14, p32, p34.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p34_fragilidad_alternativa as p34
from causal_core import demean2

BBG = p34.BBG
SERIE = os.path.join(HERE, "giv_granular_bbg.csv")
NUM = p32.NUM


def num(k, v):
    NUM[k] = float(v)


# ================================================================ instrumento
def retornos_y_pesos(c):
    m = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"), parse_dates=["date"])
    b = pd.read_csv(os.path.join(BBG, c, f"balance_{c}.csv"), parse_dates=["date"])
    m["quarter"] = m["date"].dt.to_period("Q")
    mq = (m.dropna(subset=["mktcap"]).sort_values("date")
            .groupby(["bankname", "quarter"])["mktcap"].last().reset_index())
    mq = mq[mq["mktcap"] > 0]
    mq = mq.sort_values(["bankname", "quarter"])
    g = mq.groupby("bankname")
    consec = (mq["quarter"] - g["quarter"].shift(1)).apply(lambda x: getattr(x, "n", np.nan)) == 1
    mq["r"] = np.log(mq["mktcap"]).groupby(mq["bankname"]).diff().where(consec)
    b["quarter"] = b["date"].dt.to_period("Q")
    bq = (b.dropna(subset=["total_liab"]).sort_values("date")
            .groupby(["bankname", "quarter"])["total_liab"].last().reset_index())
    x = mq.merge(bq, on=["bankname", "quarter"], how="left").sort_values(["bankname", "quarter"])
    x["total_liab"] = x.groupby("bankname")["total_liab"].ffill(limit=4)
    x["liab_l1"] = x.groupby("bankname")["total_liab"].shift(1)
    x["country"] = c
    return x


def construir_instrumento(paises):
    x = pd.concat([retornos_y_pesos(c) for c in paises], ignore_index=True)
    x = x.dropna(subset=["r", "liab_l1"])
    lo, hi = x["r"].quantile([0.01, 0.99])
    x["r"] = x["r"].clip(lo, hi)
    x = x[x.groupby("bankname")["r"].transform("size") >= 8]
    x["n"] = x.groupby(["country", "quarter"])["r"].transform("size")
    x = x[x["n"] >= 3].copy()
    x["S"] = x["liab_l1"] / x.groupby(["country", "quarter"])["liab_l1"].transform("sum")
    x["rbar"] = x.groupby(["country", "quarter"])["r"].transform("mean")
    # (b) quitar la carga de cada banco sobre el retorno medio de su país
    def resid(g):
        v = np.var(g["rbar"])
        beta = np.cov(g["r"], g["rbar"])[0, 1] / v if v > 0 else 1.0
        return g["r"] - beta * g["rbar"]
    x["u"] = x.groupby("bankname", group_keys=False).apply(resid)
    agg = x.groupby(["country", "quarter"]).apply(lambda g: pd.Series({
        "z_giv": float((g["S"] * g["r"]).sum() - g["r"].mean()),
        "z_giv_b": float((g["S"] * g["u"]).sum() - g["u"].mean()),
        "n_bancos": len(g), "hhi_S": float((g["S"] ** 2).sum())})).reset_index()
    agg["quarter"] = agg["quarter"].astype(str)
    agg.to_csv(SERIE, index=False)
    return agg


def instrumento():
    if os.path.exists(SERIE):
        return pd.read_csv(SERIE)
    d0 = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    return construir_instrumento(sorted(d0["country"].unique()))


# ================================================================ estimación
def rezago_k(d, s, cols, k):
    s = s.copy()
    s["quarter"] = (pd.PeriodIndex(s["quarter"], freq="Q") + k).astype(str)
    return d.merge(s[["country", "quarter"] + cols].rename(columns={c: f"{c}_l{k}" for c in cols}),
                   on=["country", "quarter"], how="left")


def iv(d, endog, z, pref):
    x = d.dropna(subset=["ln_EMBI", endog, "D_l1", z]).copy()
    num(f"{pref}_N", len(x)); num(f"{pref}_paises", x["country"].nunique())
    # primera etapa y forma reducida con DK, cluster y wild
    fs = p32.pfit(x, endog, [z, "D_l1"]); fsc = p32.pfit(x, endog, [z, "D_l1"], cov="pais")
    num(f"{pref}_fs_b", fs.params[z]); num(f"{pref}_fs_F_dk", (fs.params[z] / fs.std_errors[z]) ** 2)
    num(f"{pref}_fs_F_pais", (fsc.params[z] / fsc.std_errors[z]) ** 2)
    rf = p32.pfit(x, "ln_EMBI", [z, "D_l1"]); rfc = p32.pfit(x, "ln_EMBI", [z, "D_l1"], cov="pais")
    num(f"{pref}_rf_b", rf.params[z]); num(f"{pref}_rf_p_dk", rf.pvalues[z]); num(f"{pref}_rf_p_pais", rfc.pvalues[z])
    num(f"{pref}_rf_p_wild", p32.wild(x, "ln_EMBI", [z, "D_l1"], z))
    num(f"{pref}_fs_p_wild", p32.wild(x, endog, [z, "D_l1"], z))
    # 2SLS sobre datos within (EF de país y de tiempo absorbidos), cluster por país
    w = demean2(x, ["ln_EMBI", endog, "D_l1", z], iters=40)
    res = IV2SLS(w["ln_EMBI"], w[["D_l1"]], w[[endog]], w[[z]]).fit(
        cov_type="clustered", clusters=x["country"].astype("category").cat.codes.values)
    num(f"{pref}_iv_b", res.params[endog]); num(f"{pref}_iv_se_pais", res.std_errors[endog])
    num(f"{pref}_iv_p_pais", res.pvalues[endog])
    ols = p32.pfit(x, "ln_EMBI", [endog, "D_l1"])
    num(f"{pref}_ols_b", ols.params[endog])


def main():
    print("p36: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]))
    d, raw = p14.base()
    p14.check_principal(d)
    s = p34.series()
    d = p34.rezagar(d, s, ["PD_w", "DD_w"])
    d["negDD_l1"] = -d["DD_w_l1"]
    z = instrumento()
    num("z_obs", len(z)); num("z_sd", z["z_giv"].std()); num("z_corr_ab", z[["z_giv", "z_giv_b"]].corr().iloc[0, 1])
    for k in (1, 2):
        d = rezago_k(d, z, ["z_giv", "z_giv_b"], k)
    # ¿responde el instrumento al spread contemporáneo? z_{t-1} vs cambio del spread en t-1
    d = p32.agregar_rezagos(p14.cargar_bbg_macro(d), raw)
    d["dEMBI_l1"] = d["ln_EMBI_l1"] - d["y_l2"]
    x = d.dropna(subset=["z_giv_l1", "dEMBI_l1"])
    m = p32.pfit(x, "z_giv_l1", ["dEMBI_l1"])
    num("exog_z_sobre_dspread_b", m.params["dEMBI_l1"]); num("exog_z_sobre_dspread_p_dk", m.pvalues["dEMBI_l1"])
    for endog, en in (("ln_JLoss_l1", "jl"), ("negDD_l1", "dd")):
        for zz, zn in (("z_giv_l1", "a"), ("z_giv_b_l1", "b"), ("z_giv_l2", "a2")):
            iv(d, endog, zz, f"{en}_{zn}")
    out = os.path.join(HERE, "paper_p36_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        print(f"  {k:30s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
