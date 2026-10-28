# -*- coding: utf-8 -*-
"""
p69_esg_spread.py -- E1-E3 y lo exploratorio del preregistro 9 (4_Redaccion/preregistro_esg.md,
commit 81c2d9c, anterior a los datos y a este script).

  Base B: ln EMBI = a_i + d_t + b1 J_c + b2 T_c + b3 J_c T_c (muestra de la principal, p14.base, N = 765).
  E1: B + ESG_s (ESG_{t-1}); predicción < 0.      E2: B + G_s (G_{t-1}); predicción < 0.
  E3: B + G_s + J_c G_s; predicción del término de interacción < 0.
  Moderadores estandarizados en la muestra de estimación; DK de referencia; p del wild cluster bootstrap
  (p32.wild, Webb, 999), unilateral con la convención de p42; sin cada país (13 submuestras).
  La corrección de Holm sobre E1-E5 la hace p70, que lee este archivo.

  Exploratorio: Mundlak (media por país y desviación, efectos de tiempo, cluster país); efectos fijos de
  país de B sobre el G medio (13 puntos); dimensiones E y S; D x G; libertad política (Freedom House) en
  lugar de G; réplica de la especificación de ORT (trimestral y anual) y de Tebaldi et al. (2018) (LSDV
  trimestral y GMM de sistema anual con instrumentos colapsados); robustez del índice (interpolación,
  cargas 2003-2012, pesos iguales, hasta 2021Q4, sin valores arrastrados, con Argentina); triple
  interacción de p3_causal_fase5 con el WGI real en lugar de la plantilla instituciones.csv.

Salida: bbg/paper_p69_numeros.csv.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, PANEL)

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

import p12_tablas_latex_lnlag as p12
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p67_datos_esg as p67

NUM = p32.NUM
OUT = os.path.join(HERE, "paper_p69_numeros.csv")
ESG_Q = os.path.join(HERE, "esg_trimestral_bbg.csv")
ESG_A = os.path.join(HERE, "esg_indice_anual_bbg.csv")
ARG_CSV = os.path.join(HERE, "Panel_bloomberg_embiext_arg.csv")
RHS0 = ["J_c", "T_c", "JxT"]
COLS = ["G", "ESG", "ESG_eq", "C_E", "C_S", "G_pre", "ESG_pre", "G_int", "ESG_int", "libertad",
        "G_arr", "ESG_arr"]


def num(k, v):
    NUM[k] = float(v)


def guardar():
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)


def con_esg(d):
    e = pd.read_csv(ESG_Q)
    q = pd.PeriodIndex(e["quarter"], freq="Q"); e["_qn"] = q.year * 4 + q.quarter
    for c in COLS:
        d = d.merge(p14.shift(e, c, 1, f"{c}_l1"), on=["country", "_qn"], how="left")
    a = pd.read_csv(ESG_A)[["country", "year", "crecimiento", "apertura"]]
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    return d.merge(a.rename(columns={"crecimiento": "crec_c", "apertura": "aper_c"}),
                   on=["country", "year"], how="left")


def preparar():
    d, raw = p14.base()
    p14.check_principal(d)
    return con_esg(d), raw


def directo(d, mod, pref, signo, loo=True):
    """B + M_s: coeficiente de M_s, p DK, p cluster país, wild unilateral y sin cada país."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod]))
    x["M_s"] = (x[mod] - x[mod].mean()) / x[mod].std()
    rhs = RHS0 + ["M_s"]
    m = p42.fit(x, "ln_EMBI", rhs); mc = p42.fit(x, "ln_EMBI", rhs, "pais")
    b = float(m.params["M_s"])
    pw = p32.wild(x, "ln_EMBI", rhs, "M_s")
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_b", b); num(f"{pref}_se_dk", m.std_errors["M_s"]); num(f"{pref}_p_dk", m.pvalues["M_s"])
    num(f"{pref}_p_pais", mc.pvalues["M_s"]); num(f"{pref}_p_wild_bi", pw)
    num(f"{pref}_p_uni", p42.unilateral(pw, b, signo)); num(f"{pref}_b3", m.params["JxT"])
    if loo:
        ok, bs = 0, []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]
            bc = float(p42.fit(xc, "ln_EMBI", rhs).params["M_s"])
            pc = p42.unilateral(p32.wild(xc, "ln_EMBI", rhs, "M_s"), bc, signo)
            bs.append(bc); ok += int(np.sign(bc) == signo and pc < 0.10)
            num(f"{pref}_sin_{c}_b", bc); num(f"{pref}_sin_{c}_p_uni", pc)
        num(f"{pref}_loo_ok", ok); num(f"{pref}_loo_b_min", min(bs)); num(f"{pref}_loo_b_max", max(bs))
    return NUM[f"{pref}_p_uni"]


# ================================================================ exploratorio
def mundlak(d, mod, pref):
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod]))
    s = x[mod].std()
    x["M_media"] = x.groupby("country")[mod].transform("mean") / s
    x["M_desv"] = x[mod] / s - x["M_media"]
    m = PanelOLS.from_formula("ln_EMBI ~ 1 + J_c + T_c + JxT + M_media + M_desv + TimeEffects",
                              x.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    for k in ("M_media", "M_desv"):
        num(f"{pref}_{k}_b", m.params[k]); num(f"{pref}_{k}_p", m.pvalues[k])
    num(f"{pref}_N", m.nobs)


def segundo_paso(d):
    """Efectos fijos de país de B (con efectos de tiempo) sobre el G y el ESG medios: 13 puntos."""
    x = p42.centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]))
    m = PanelOLS.from_formula("ln_EMBI ~ J_c + T_c + JxT + EntityEffects + TimeEffects",
                              x.set_index(["country", "t"])).fit(**p14.DK)
    ef = m.estimated_effects.groupby(level=0).mean().iloc[:, 0]
    a = pd.read_csv(ESG_A)
    a = a[a["year"].between(2003, 2025)].groupby("country")[["G", "ESG"]].mean()
    for col in ("G", "ESG"):
        z = pd.concat([ef.rename("ef"), a[col]], axis=1, join="inner").dropna()
        r = sm.OLS(z["ef"], sm.add_constant((z[col] - z[col].mean()) / z[col].std())).fit(cov_type="HC1")
        num(f"fondo_{col}_b", r.params.iloc[1]); num(f"fondo_{col}_p", r.pvalues.iloc[1])
        num(f"fondo_{col}_R2", r.rsquared); num(f"fondo_{col}_n", len(z))
        num(f"fondo_{col}_corr", z.corr().iloc[0, 1])


def replica_ort(d, raw):
    """EMBI en tanto por uno sobre su rezago, reservas, deuda, inflación, crecimiento y ESG del año anterior;
    efectos fijos de país, sin efectos de tiempo, errores agrupados por país."""
    r = con_esg(raw.copy().assign(t=pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()))
    r = r.sort_values(["country", "_qn"])
    e = pd.read_csv(ESG_Q); q = pd.PeriodIndex(e["quarter"], freq="Q"); e["_qn"] = q.year * 4 + q.quarter
    r = r.merge(p14.shift(e, "ESG", 0, "ESG_t"), on=["country", "_qn"], how="left")   # = ESG del año y-1
    r["y"] = r["EMBI_bps"] / 1e4
    r = r.merge(p14.shift(r[["country", "_qn", "y"]], "y", 1, "y_l1"), on=["country", "_qn"], how="left")
    rhs = ["y_l1", "res_gdp", "debt_gdp", "infl_yoy", "crec_c", "ESG_t"]
    x = r.dropna(subset=["y"] + rhs)
    m = PanelOLS.from_formula(f"y ~ 1 + {' + '.join(rhs)} + EntityEffects",
                              x.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    num("ort_q_esg_b", m.params["ESG_t"]); num("ort_q_esg_p", m.pvalues["ESG_t"]); num("ort_q_N", m.nobs)
    # anual: promedios por país-año, ESG del año anterior
    a = x.groupby(["country", "year"])[["y", "res_gdp", "debt_gdp", "infl_yoy", "crec_c", "ESG_t"]].mean()
    a = a.reset_index().sort_values(["country", "year"])
    a["y_l1"] = a.groupby("country")["y"].shift(1).where(a.groupby("country")["year"].diff() == 1)
    a = a.dropna(subset=["y_l1"])
    a["t"] = pd.to_datetime(a["year"].astype(str) + "-01-01")
    ma = PanelOLS.from_formula(f"y ~ 1 + {' + '.join(rhs)} + EntityEffects",
                               a.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    num("ort_a_esg_b", ma.params["ESG_t"]); num("ort_a_esg_p", ma.pvalues["ESG_t"]); num("ort_a_N", ma.nobs)
    # misma especificación anual con efectos de tiempo (lo que ORT no incluye)
    mt = PanelOLS.from_formula(f"y ~ {' + '.join(rhs)} + EntityEffects + TimeEffects",
                               a.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    num("ort_a_te_esg_b", mt.params["ESG_t"]); num("ort_a_te_esg_p", mt.pvalues["ESG_t"])


def replica_tebaldi(d, raw):
    r = con_esg(raw.copy().assign(t=pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()))
    r["ln_reer"] = np.log(r["reer"].where(r["reer"] > 0))
    r = r.merge(p14.shift(r[["country", "_qn", "ln_EMBI"]], "ln_EMBI", 1, "lnE_l1"),
                on=["country", "_qn"], how="left")
    rhs = ["lnE_l1", "crec_c", "ln_reer", "aper_c", "libertad_l1"]
    x = r.dropna(subset=["ln_EMBI"] + rhs)
    m = PanelOLS.from_formula(f"ln_EMBI ~ 1 + {' + '.join(rhs)} + EntityEffects",
                              x.set_index(["country", "t"])).fit(cov_type="clustered", cluster_entity=True)
    for k in rhs:
        num(f"teb_q_{k}_b", m.params[k]); num(f"teb_q_{k}_p", m.pvalues[k])
    num("teb_q_N", m.nobs)
    # anual, GMM de sistema con instrumentos colapsados (pydynpd)
    try:
        from pydynpd import regression
        a = x.groupby(["country", "year"])[["ln_EMBI", "crec_c", "ln_reer", "aper_c", "libertad_l1"]].mean()
        a = a.reset_index().rename(columns={"libertad_l1": "libertad"})
        a["id"] = a["country"].astype("category").cat.codes + 1
        cmd = ("ln_EMBI L1.ln_EMBI crec_c ln_reer aper_c libertad | gmm(ln_EMBI, 2:3) "
               "iv(crec_c ln_reer aper_c libertad) | collapse")
        res = regression.abond(cmd, a[["id", "year", "ln_EMBI", "crec_c", "ln_reer", "aper_c", "libertad"]],
                               ["id", "year"])
        tab = res.models[0].regression_table
        for _, fila in tab.iterrows():
            k = str(fila["variable"]).replace(".", "_")
            num(f"teb_gmm_{k}_b", fila["coefficient"]); num(f"teb_gmm_{k}_p", fila["p_value"])
        num("teb_gmm_N", res.models[0].num_obs); num("teb_gmm_instr", res.models[0].z_information.num_instr)
        num("teb_gmm_hansen_p", res.models[0].hansen.p_value)
    except Exception as e:                                        # se declara en el informe
        print(f"  GMM anual no estimado: {str(e)[:120]}")
        num("teb_gmm_ok", 0)


def base_argentina():
    viejo_env, viejo_p12 = os.environ["JLOSS_PANEL_CSV"], p12.PANEL_CSV
    os.environ["JLOSS_PANEL_CSV"], p12.PANEL_CSV = ARG_CSV, ARG_CSV
    try:
        d, _ = p14.base()
    finally:
        os.environ["JLOSS_PANEL_CSV"], p12.PANEL_CSV = viejo_env, viejo_p12
    return con_esg(d)


def triple_wgi_real():
    import causal_core as cc
    import p3_causal_fase5 as p3
    tmp = p3.load_for_causal()
    try:
        P = cc.load(tmp); ctr = cc.ctrls_in(P)
        sal = {"plantilla": cc.triple_institucional(P, inst_file=os.path.join(PANEL, "instituciones.csv"),
                                                     ctrls=ctr)}
        an = pd.read_csv(p67.OUT)
        for etiqueta, sub in (("real2018", an[an["year"] == 2018][["country", "ley"]]),
                              ("realmedia", an[an["year"].between(2003, 2025)].groupby("country", as_index=False)
                               ["ley"].mean())):
            f = os.path.join(HERE, f"_wgi_{etiqueta}.csv")
            sub.rename(columns={"ley": "rule_of_law"}).to_csv(f, index=False)
            try:
                sal[etiqueta] = cc.triple_institucional(P, inst_file=f, ctrls=ctr)
            finally:
                os.remove(f)
        for k, ti in sal.items():
            b, se, t = ti["JxG_I"]
            num(f"triple_{k}_b", b); num(f"triple_{k}_t", t); num(f"triple_{k}_n", ti["_meta"]["n"])
            num(f"triple_{k}_paises", ti["_meta"]["paises"])
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    print("p69: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), flush=True)
    d, raw = preparar()
    num("muestra_N", len(d))
    for c in ("ESG_l1", "G_l1"):
        num(f"cobertura_{c}", d[c].notna().sum())
    # fracción de la varianza dentro del país en la muestra de estimación
    for c in ("G_l1", "ESG_l1"):
        x = d[["country", c]].dropna()
        num(f"frac_dentro_muestra_{c}", (x[c] - x.groupby("country")[c].transform("mean")).var() / x[c].var())

    # ---------------- familia primaria (Holm en p70)
    p1 = directo(d, "ESG_l1", "e1", -1)
    p2 = directo(d, "G_l1", "e2", -1)
    p3 = p42.moderacion(d, "G_l1", "J_c", "e3", -1)
    guardar()
    print(f"  E1 ESG  b = {NUM['e1_b']:+.4f}  p DK {NUM['e1_p_dk']:.3f}  wild uni {p1:.3f}  "
          f"loo {NUM['e1_loo_ok']:.0f}/13  N {NUM['e1_N']:.0f}")
    print(f"  E2 G    b = {NUM['e2_b']:+.4f}  p DK {NUM['e2_p_dk']:.3f}  wild uni {p2:.3f}  "
          f"loo {NUM['e2_loo_ok']:.0f}/13  N {NUM['e2_N']:.0f}")
    print(f"  E3 JxG  b = {NUM['e3_b']:+.4f}  p DK {NUM['e3_p_dk']:.3f}  wild uni {p3:.3f}  "
          f"loo {NUM['e3_loo_ok']:.0f}/13  N {NUM['e3_N']:.0f}", flush=True)

    # ---------------- exploratorio
    for mod, pref in (("G_l1", "mund_G"), ("ESG_l1", "mund_ESG"), ("libertad_l1", "mund_lib")):
        mundlak(d, mod, pref)
    segundo_paso(d)
    for mod, pref in (("C_E_l1", "dimE"), ("C_S_l1", "dimS"), ("libertad_l1", "lib")):
        directo(d, mod, pref, -1, loo=False)
    p42.moderacion(d, "G_l1", "T_c", "dxg", -1, loo=False)
    p42.moderacion(d, "libertad_l1", "J_c", "lib_mod", -1, loo=False)
    for mod in ("G_int", "ESG_int", "G_pre", "ESG_pre", "ESG_eq"):
        directo(d, f"{mod}_l1", f"rob_{mod}", -1, loo=False)
    hasta21 = d[pd.PeriodIndex(d["quarter"], freq="Q") <= pd.Period("2021Q4", freq="Q")]
    sin_arr = d[(d["G_arr_l1"] == 0) & (d["ESG_arr_l1"] == 0)]
    for sub, suf in ((hasta21, "h2021"), (sin_arr, "sinarr")):
        directo(sub, "G_l1", f"rob_G_{suf}", -1, loo=False)
        directo(sub, "ESG_l1", f"rob_ESG_{suf}", -1, loo=False)
        p42.moderacion(sub, "G_l1", "J_c", f"rob_e3_{suf}", -1, loo=False)
    da = base_argentina()
    for mod, pref in (("G_l1", "rob_G_arg"), ("ESG_l1", "rob_ESG_arg")):
        directo(da, mod, pref, -1, loo=False)
    p42.moderacion(da, "G_l1", "J_c", "rob_e3_arg", -1, loo=False)
    guardar()
    replica_ort(d, raw)
    replica_tebaldi(d, raw)
    triple_wgi_real()
    guardar()
    print(f"-> {OUT}")
    claves = ["mund_G_M_media_b", "mund_G_M_media_p", "mund_G_M_desv_b", "mund_G_M_desv_p",
              "fondo_G_b", "fondo_G_p", "fondo_G_R2", "dimE_b", "dimE_p_uni", "dimS_b", "dimS_p_uni",
              "lib_b", "lib_p_uni", "dxg_b", "dxg_p_uni", "lib_mod_b", "lib_mod_p_uni",
              "ort_q_esg_b", "ort_q_esg_p", "ort_a_esg_b", "ort_a_esg_p", "ort_a_te_esg_b", "ort_a_te_esg_p",
              "teb_q_libertad_l1_b", "teb_q_libertad_l1_p", "triple_plantilla_b", "triple_plantilla_t",
              "triple_real2018_b", "triple_real2018_t", "triple_realmedia_b", "triple_realmedia_t"]
    for k in claves:
        if k in NUM:
            print(f"  {k:28s} {NUM[k]:+.4f}")


if __name__ == "__main__":
    main()
