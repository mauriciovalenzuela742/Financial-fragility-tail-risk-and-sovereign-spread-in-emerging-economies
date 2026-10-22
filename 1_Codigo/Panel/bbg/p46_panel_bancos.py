# -*- coding: utf-8 -*-
"""
p46_panel_bancos.py -- mu1 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f): los bancos
como unidad de análisis.

Construye el panel banco-trimestre (bbg/banco_trimestral_bbg.csv) con el mismo motor de JLoss
(quarterly_inputs + merton_pd): DD de Merton, F = -DD, peso sistémico S (participación en los pasivos de
los bancos cotizados del país), apalancamiento (pasivos / activos) y propiedad (2_Datos/propiedad_bancos.csv).

  mu1-H1: dF_{b,t} = a_b + d_{c,t} + beta (dln EMBI_{c,t} x S_{b,t-1}) + g S_{b,t-1} + l Apal_{b,t-1} + e,
          EF de banco y de país-trimestre; beta > 0.
  mu1-H2: regresión principal con F_sist (-DD ponderado por pasivos de los dos bancos con más pasivos) y
          F_marg (el resto), economías-trimestre con >= 3 bancos, rezagados un trimestre, cada uno con su
          producto con D_{t-1}; b_sist - b_marg > 0, estimado como el coeficiente de F_sist en la regresión
          sobre F_sist y (F_sist + F_marg).
  Secundaria: mu1-H1 con la indicadora de banco estatal en lugar de S.
Inferencia: wild cluster bootstrap por país (Webb, 999), p unilateral en la dirección predicha; errores
agrupados en dos dimensiones (banco y país-trimestre) como referencia; sin cada país.
Holm se aplica sobre la familia completa en p51 (resumen del preregistro 3).

Salida: bbg/banco_trimestral_bbg.csv y bbg/paper_p46_numeros.csv.
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
from scipy.stats import norm
from linearmodels.panel import PanelOLS

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
from causal_core import demean2

NUM = p32.NUM
BBG = os.path.abspath(os.path.join(HERE, "..", "..", "Bloomberg_extraction", "output"))
PROP = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos", "propiedad_bancos.csv"))
SERIE = os.path.join(HERE, "banco_trimestral_bbg.csv")
PAISES = ["brazil", "chile", "china", "colombia", "india", "indonesia", "malaysia", "mexico", "peru",
          "philippines", "poland", "southafrica", "turkey"]


def num(k, v):
    NUM[k] = float(v)


# ================================================================ datos
def propiedad():
    p = pd.read_csv(PROP)
    p["desde"] = p["desde"].fillna("1990Q1"); p["hasta"] = p["hasta"].fillna("2030Q4")
    return p


def asignar_propiedad(x, p):
    x = x.merge(p[["bankname", "propiedad", "desde", "hasta"]], on="bankname", how="left")
    x = x[(x["quarter"] >= x["desde"]) & (x["quarter"] <= x["hasta"])]
    return x.drop(columns=["desde", "hasta"])


def construir():
    import jloss_engine as je
    filas = []
    for c in PAISES:
        bal = pd.read_csv(os.path.join(BBG, c, f"balance_{c}.csv"))
        mk = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"))
        dm = je.quarterly_inputs(bal, mk)
        dm["PD"] = [je.merton_pd(e, s, d) for e, s, d in zip(dm["mktcap_end"], dm["sigma_E_q"], dm["D_star"])]
        bal["date"] = pd.to_datetime(bal["date"]); bal["quarter"] = bal["date"].dt.to_period("Q")
        act = bal.sort_values("date").groupby(["bankname", "quarter"])["tot_asset"].last().reset_index()
        dm = dm.merge(act, on=["bankname", "quarter"], how="left")
        dm["country"] = c
        filas.append(dm)
        print(f"  {c}: {dm['PD'].notna().sum()} banco-trimestres con PD", flush=True)
    x = pd.concat(filas, ignore_index=True)
    x = x[x["PD"].notna() & (x["total_liab"] > 0)].copy()
    x["DD"] = -norm.ppf(np.clip(x["PD"], 1e-8, 1 - 1e-8)); x["F"] = -x["DD"]
    x["quarter"] = x["quarter"].astype(str)
    x["S"] = x["total_liab"] / x.groupby(["country", "quarter"])["total_liab"].transform("sum")
    x["apal"] = x["total_liab"] / x["tot_asset"]
    x["n_bancos"] = x.groupby(["country", "quarter"])["bankname"].transform("size")
    x = asignar_propiedad(x, propiedad())
    cols = ["country", "bankname", "quarter", "PD", "DD", "F", "S", "apal", "total_liab", "tot_asset", "mktcap_end",
            "n_bancos", "propiedad"]
    x[cols].sort_values(["country", "bankname", "quarter"]).to_csv(SERIE, index=False)
    return x[cols]


def panel():
    return pd.read_csv(SERIE) if os.path.exists(SERIE) else construir()


# ================================================================ mu1-H1
def wild_fe(x, y, regs, key, ent, tim):
    """wild cluster bootstrap por país sobre datos con EF (ent, tim) absorbidos."""
    yv = demean2(x, [y], ent=ent, tim=tim, iters=50)[y].values
    X = demean2(x, regs, ent=ent, tim=tim, iters=50).values
    cl = x["country"].values; uniq, idx = np.unique(cl, return_inverse=True)
    P = dict(y=yv, X=X, cl=cl, uniq=uniq, idx=idx, regs=list(regs))
    return p32.wb_run(P, [key])[0]


def h1(b, emb, mod, pref, signo=+1, loo=True):
    x = b.copy()
    q = pd.PeriodIndex(x["quarter"], freq="Q"); x["_qn"] = q.year * 4 + q.quarter
    x = x.sort_values(["bankname", "_qn"]); g = x.groupby("bankname")
    ok = (x["_qn"] - g["_qn"].shift(1)) == 1
    x["dF"] = g["F"].diff().where(ok)
    x["M_l1"] = g[mod].shift(1).where(ok); x["apal_l1"] = g["apal"].shift(1).where(ok)
    x = x.merge(emb, on=["country", "quarter"], how="inner").dropna(subset=["dF", "M_l1", "apal_l1", "dlnEMBI"])
    lo, hi = x["dF"].quantile([0.005, 0.995]); x = x[(x["dF"] >= lo) & (x["dF"] <= hi)]
    x["cq"] = x["country"] + "_" + x["quarter"]
    x["cq_id"] = pd.Categorical(x["cq"]).codes
    x["IxM"] = x["dlnEMBI"] * x["M_l1"]
    regs = ["IxM", "M_l1", "apal_l1"]
    pi = x.set_index(["bankname", "cq_id"])
    clus = pd.DataFrame({"b": pd.Categorical(x["bankname"]).codes, "t": pd.Categorical(x["cq"]).codes}, index=pi.index)
    m = PanelOLS(pi["dF"], pi[regs], entity_effects=True, time_effects=True).fit(cov_type="clustered", clusters=clus)
    bb = float(m.params["IxM"]); pw = wild_fe(x, "dF", regs, "IxM", "bankname", "cq")
    num(f"{pref}_N", m.nobs); num(f"{pref}_bancos", x["bankname"].nunique()); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_b", bb); num(f"{pref}_p_2vias", m.pvalues["IxM"]); num(f"{pref}_p_wild_bi", pw)
    num(f"{pref}_p_uni", p42.unilateral(pw, bb, signo))
    num(f"{pref}_sd_mod", x["M_l1"].std()); num(f"{pref}_sd_dlnEMBI", x["dlnEMBI"].std())
    if loo:
        ok_ = 0; bs = []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]; pc_ = xc.set_index(["bankname", "cq_id"])
            mc = PanelOLS(pc_["dF"], pc_[regs], entity_effects=True, time_effects=True).fit()
            bc = float(mc.params["IxM"]); pcu = p42.unilateral(wild_fe(xc, "dF", regs, "IxM", "bankname", "cq"), bc, signo)
            ok_ += int(np.sign(bc) == signo and pcu < 0.10); bs.append(bc)
            num(f"{pref}_sin_{c}_b", bc); num(f"{pref}_sin_{c}_p_uni", pcu)
        num(f"{pref}_loo_ok", ok_); num(f"{pref}_loo_n", len(bs)); num(f"{pref}_loo_min", min(bs)); num(f"{pref}_loo_max", max(bs))
    return p42.unilateral(pw, bb, signo)


# ================================================================ mu1-H2 / mu3-H1 (dos grupos)
def dos_grupos(d, grupos, pref, loo=True):
    """grupos: DataFrame country, quarter, FA, FB (fragilidad de cada grupo en el trimestre). Se rezaga."""
    g = grupos.copy()
    g["quarter"] = (pd.PeriodIndex(g["quarter"], freq="Q") + 1).astype(str)
    x = d.merge(g, on=["country", "quarter"], how="inner").dropna(subset=["ln_EMBI", "FA", "FB", "D_l1"]).copy()
    for v in ("FA", "FB"):
        x[v + "_c"] = x[v] - x[v].mean()
    x["T_c"] = x["D_l1"] - x["D_l1"].mean()
    x["SUMA"] = x["FA_c"] + x["FB_c"]
    x["AxT"] = x["FA_c"] * x["T_c"]; x["BxT"] = x["FB_c"] * x["T_c"]
    rhs = ["FA_c", "SUMA", "T_c", "AxT", "BxT"]
    m = p42.fit(x, "ln_EMBI", rhs); mc = p42.fit(x, "ln_EMBI", rhs, "pais")
    dif = float(m.params["FA_c"]); pw = p32.wild(x, "ln_EMBI", rhs, "FA_c")
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_dif", dif); num(f"{pref}_p_dk", m.pvalues["FA_c"]); num(f"{pref}_p_pais", mc.pvalues["FA_c"])
    num(f"{pref}_p_wild_bi", pw); num(f"{pref}_p_uni", p42.unilateral(pw, dif, +1))
    m2 = p42.fit(x, "ln_EMBI", ["FA_c", "FB_c", "T_c", "AxT", "BxT"])
    num(f"{pref}_bA", m2.params["FA_c"]); num(f"{pref}_bB", m2.params["FB_c"])
    num(f"{pref}_bA_p_dk", m2.pvalues["FA_c"]); num(f"{pref}_bB_p_dk", m2.pvalues["FB_c"])
    num(f"{pref}_corr_AB", np.corrcoef(x["FA"], x["FB"])[0, 1])
    if loo:
        ok_ = 0; bs = []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]
            mcc = p42.fit(xc, "ln_EMBI", rhs); bc = float(mcc.params["FA_c"])
            pcu = p42.unilateral(p32.wild(xc, "ln_EMBI", rhs, "FA_c"), bc, +1)
            ok_ += int(bc > 0 and pcu < 0.10); bs.append(bc)
        num(f"{pref}_loo_ok", ok_); num(f"{pref}_loo_n", len(bs)); num(f"{pref}_loo_min", min(bs)); num(f"{pref}_loo_max", max(bs))
    return p42.unilateral(pw, dif, +1)


def fragilidad_grupos(b, regla):
    filas = []
    for (c, q), g in b.groupby(["country", "quarter"]):
        if regla == "sistemicos":
            if len(g) < 3:
                continue
            g = g.sort_values("total_liab", ascending=False)
            A, Bg = g.iloc[:2], g.iloc[2:]
        else:                                  # nacionales frente a filiales extranjeras
            A, Bg = g[g["propiedad"].isin(["estatal", "privado"])], g[g["propiedad"] == "extranjero"]
            if len(A) == 0 or len(Bg) == 0:
                continue
        w = lambda h: float((h["F"] * h["total_liab"]).sum() / h["total_liab"].sum())
        filas.append({"country": c, "quarter": q, "FA": w(A), "FB": w(Bg)})
    return pd.DataFrame(filas)


def main():
    b = panel()
    num("panel_obs", len(b)); num("panel_bancos", b["bankname"].nunique())
    for k, v in b["propiedad"].value_counts().items():
        num(f"panel_obs_{k}", v)
    d, raw = p14.base(); p14.check_principal(d)
    r = raw.sort_values(["country", "_qn"]); gr = r.groupby("country")
    ok = (r["_qn"] - gr["_qn"].shift(1)) == 1
    r["dlnEMBI"] = gr["ln_EMBI"].diff().where(ok)
    emb = r[["country", "quarter", "dlnEMBI"]].dropna()
    out = os.path.join(HERE, "paper_p46_numeros.csv")
    guardar = lambda: pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    p1 = h1(b, emb, "S", "mu1h1"); guardar()
    print(f"  mu1-H1 beta = {NUM['mu1h1_b']:.3f} (uni {p1:.3f})", flush=True)
    p2 = dos_grupos(d, fragilidad_grupos(b, "sistemicos"), "mu1h2"); guardar()
    print(f"  mu1-H2 dif = {NUM['mu1h2_dif']:.3f} (uni {p2:.3f})", flush=True)
    b2 = b.copy(); b2["estatal"] = (b2["propiedad"] == "estatal").astype(float)
    h1(b2, emb, "estatal", "sec_mu1h1_estatal", loo=False); guardar()
    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
