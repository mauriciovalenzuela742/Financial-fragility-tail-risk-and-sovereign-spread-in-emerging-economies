# -*- coding: utf-8 -*-
"""
x1_comprobaciones.py -- tres comprobaciones que pidió la auditoría final (2026-10-13).

  1. Simultaneidad neta del calendario común: lo esperado dadas las frecuencias de cada trimestre,
     una permutación que conserva el tiempo (permuta países dentro de cada trimestre) y la
     coincidencia con indicadores sobre series sin el promedio transversal de cada trimestre.
  2. Precedencia fragilidad(t-1) -> riesgo de cola(t): excluir un país, sin efectos de tiempo, con
     tendencias por país, con dos rezagos, con JLoss en z por país y como indicador fuera del piso,
     y con el GaR reconstruido SIN el bloque bursátil del índice de condiciones financieras.
  3. EMBI diario de Polonia en 2020-2022 y la principal sin esos trimestres.

Salida: experimentos/x1_comprobaciones.csv. No se integra a ningún documento.
"""
import os

import numpy as np
import pandas as pd

import x0_comun as x0

NUM = {}
R = 999


def num(k, v):
    NUM[k] = float(v)
    return v


def terciles(dd, col, nom):
    dd[nom] = (dd[col] > dd.groupby("country")[col].transform(lambda x: x.quantile(2 / 3))).astype(float)


def rachas(a):
    out, n = [], 0
    for v in a:
        if v:
            n += 1
        elif n:
            out.append(n); n = 0
    if n:
        out.append(n)
    return out


def simultaneidad(dd, pref):
    obs = (dd["AJ"] * dd["AD"]).sum()
    esp_pais = dd.groupby("country").apply(lambda x: len(x) * x["AJ"].mean() * x["AD"].mean()).sum()
    esp_trim = dd.groupby("quarter").apply(lambda x: len(x) * x["AJ"].mean() * x["AD"].mean()).sum()
    num(f"{pref}_obs", obs); num(f"{pref}_esp_pais", esp_pais); num(f"{pref}_razon_pais", obs / esp_pais)
    num(f"{pref}_esp_trimestre", esp_trim); num(f"{pref}_razon_trimestre", obs / esp_trim)
    rng = np.random.default_rng(11)
    # (a) permutación que conserva el tiempo: dentro de cada trimestre se permuta el indicador de D entre países
    grupos = [(x["AJ"].to_numpy(), x["AD"].to_numpy()) for _, x in dd.groupby("quarter")]
    sim = np.array([sum((aj * rng.permutation(ad)).sum() for aj, ad in grupos) for _ in range(R)])
    num(f"{pref}_permtiempo_media", sim.mean()); num(f"{pref}_permtiempo_q95", np.quantile(sim, .95))
    num(f"{pref}_permtiempo_p", (1 + (sim >= obs).sum()) / (R + 1))
    # (b) permutación por bloques dentro del país (la de p32), para comparar
    series = [(x["AJ"].to_numpy(), x["AD"].to_numpy()) for _, x in dd.groupby("country")]
    sim = np.array([sum((aj * np.roll(ad, rng.integers(1, len(ad)))).sum() for aj, ad in series) for _ in range(R)])
    num(f"{pref}_permpais_media", sim.mean()); num(f"{pref}_permpais_p", (1 + (sim >= obs).sum()) / (R + 1))
    return obs


def bloque_simultaneidad(d):
    dd = d.copy()
    terciles(dd, "ln_JLoss_l1", "AJ"); terciles(dd, "D_l1", "AD")
    simultaneidad(dd, "sim")
    dd["anio"] = dd["t"].dt.year
    per = {"2004_08": (2004, 2008), "2009": (2009, 2009), "2010_14": (2010, 2014), "2015_19": (2015, 2019),
           "2020_22": (2020, 2022), "2023_26": (2023, 2026)}
    for k, (a, b) in per.items():
        x = dd[dd["anio"].between(a, b)]
        num(f"sim_per_{k}_obs", (x["AJ"] * x["AD"]).sum())
        num(f"sim_per_{k}_esp_anio", x.groupby("anio").apply(lambda z: len(z) * z["AJ"].mean() * z["AD"].mean()).sum())
        num(f"sim_per_{k}_esp_trim", x.groupby("quarter").apply(lambda z: len(z) * z["AJ"].mean() * z["AD"].mean()).sum())
    sc = dd[~dd["quarter"].isin(x0.p13.CRISIS_BAT)]
    simultaneidad(sc, "sim_sincrisis")
    # indicadores sobre series SIN el promedio transversal de cada trimestre
    dm = d.copy()
    for c in ("ln_JLoss_l1", "D_l1"):
        dm[c + "_dm"] = dm[c] - dm.groupby("quarter")[c].transform("mean")
    n_q = dm.groupby("quarter")["country"].transform("size")
    dm = dm[n_q >= 5].copy()                       # trimestres con al menos cinco países
    terciles(dm, "ln_JLoss_l1_dm", "AJ"); terciles(dm, "D_l1_dm", "AD")
    num("simdm_N", len(dm))
    simultaneidad(dm, "simdm")
    simultaneidad(dm[~dm["quarter"].isin(x0.p13.CRISIS_BAT)], "simdm_sincrisis")
    ls = [l for _, x in dm.groupby("country") for l in rachas((x["AJ"] * x["AD"]).to_numpy())]
    num("simdm_racha_media", np.mean(ls) if ls else 0)
    num("simdm_corr_AJ_AD", np.corrcoef(dm["AJ"], dm["AD"])[0, 1])


def panel_cruzado(gar_alt=None):
    """panel país-trimestre con J y D contemporáneos y dos rezagos (trimestres consecutivos)."""
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    if gar_alt is not None:
        raw = raw.drop(columns=["GaR"]).merge(gar_alt, on=["country", "quarter"], how="left")
    q = pd.PeriodIndex(raw["quarter"], freq="Q")
    raw["_qn"] = q.year * 4 + q.quarter
    raw = raw.sort_values(["country", "_qn"])
    raw["J"] = raw["JLoss"] if x0.NIV else np.log(raw["JLoss"])
    raw["Jraw"] = raw["JLoss"]
    raw["D"] = -raw["GaR"] * 100.0
    g = raw.groupby("country")
    for L in (1, 2):
        ok = (raw["_qn"] - g["_qn"].shift(L)) == L
        for c in ("J", "D", "Jraw"):
            raw[f"{c}_l{L}"] = g[c].shift(L).where(ok)
    return raw


def cruzada(p, y, x, propio, pref, tiempo=True, tend=False, lag2=False, wild=True):
    cols = [x, propio] + ([x.replace("_l1", "_l2"), propio.replace("_l1", "_l2")] if lag2 else [])
    s = p.dropna(subset=[y] + cols).copy()
    extra = None
    if tend:
        tt = (s["_qn"] - s["_qn"].min()).to_numpy(float)
        extra = pd.get_dummies(s["country"]).to_numpy(float) * tt[:, None]
    A, _ = x0.within(s, [y] + cols, tiempo=tiempo, extra=extra)
    g = pd.factorize(s["country"])[0]
    b, se = x0.t_cluster(A[:, 0], A[:, 1:], 0, g)
    num(f"{pref}_b", b); num(f"{pref}_t_cluster", b / se); num(f"{pref}_N", len(s))
    if wild:
        _, pw = x0.wild_wald(A[:, 0], A[:, 1:], [0], g, B=R)
        num(f"{pref}_p_wild", pw)
    return b, b / se


def bloque_precedencia(d):
    paises = sorted(d["country"].unique())
    p = panel_cruzado(); p = p[p["country"].isin(paises)]
    cruzada(p, "D", "J_l1", "D_l1", "prec_JD")                 # fragilidad -> riesgo de cola
    cruzada(p, "J", "D_l1", "J_l1", "prec_DJ")                 # riesgo de cola -> fragilidad
    cruzada(p, "D", "J_l1", "D_l1", "prec_JD_sinEFtiempo", tiempo=False)
    cruzada(p, "D", "J_l1", "D_l1", "prec_JD_tendencias", tend=True)
    cruzada(p, "D", "J_l1", "D_l1", "prec_JD_2rezagos", lag2=True)
    cruzada(p, "J", "D_l1", "J_l1", "prec_DJ_tendencias", tend=True)
    bs, ts = [], []
    for c in paises:
        b, t = cruzada(p[p["country"] != c], "D", "J_l1", "D_l1", f"prec_JD_sin_{c}", wild=False)
        bs.append(b); ts.append(t)
    num("prec_JD_loo_min", min(bs)); num("prec_JD_loo_max", max(bs))
    num("prec_JD_loo_sig5_t12", sum(abs(t) > 2.179 for t in ts))      # t(12) al 5 %
    # JLoss en z por país y como indicador fuera del piso
    pz = p.copy()
    lj = np.log(pz["Jraw_l1"])
    pz["Jz_l1"] = (lj - lj.groupby(pz["country"]).transform("mean")) / lj.groupby(pz["country"]).transform("std")
    pz["Jfuera_l1"] = (pz["Jraw_l1"] > x0.PISO).astype(float).where(pz["Jraw_l1"].notna())
    cruzada(pz, "D", "Jz_l1", "D_l1", "prec_JzD")
    cruzada(pz, "D", "Jfuera_l1", "D_l1", "prec_JfueraD")
    # GaR sin el bloque bursátil del FCI (in-sample), frente al in-sample base (misma estimación)
    carp = os.path.abspath(os.path.join(x0.BBG, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
    for lab, arch in (("base", "gar_insample_base.csv"), ("noSTX", "gar_insample_noSTX.csv")):
        f = os.path.join(carp, arch)
        if not os.path.exists(f):
            print("   falta", f); continue
        g = pd.read_csv(f)
        if "GaR" not in g.columns:
            cand = [c for c in g.columns if c.lower().startswith("gar")]
            g = g.rename(columns={cand[0]: "GaR"})
        pa = panel_cruzado(g[["country", "quarter", "GaR"]]); pa = pa[pa["country"].isin(paises)]
        cruzada(pa, "D", "J_l1", "D_l1", f"prec_JD_insample_{lab}")
        cruzada(pa, "J", "D_l1", "J_l1", f"prec_DJ_insample_{lab}")


def bloque_polonia(d):
    f = os.path.abspath(os.path.join(x0.BBG, "..", "..", "..", "2_Datos", "embi.xlsx"))
    x = pd.read_excel(f).rename(columns={"Fecha": "date"})
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"])
    col = [c for c in x.columns if "pol" in str(c).lower()]
    print("   columnas de Polonia en embi.xlsx:", col)
    s = x.set_index("date")[col[0]].dropna()
    s = s["2020-07-01":"2022-12-31"]
    q = s.groupby(s.index.to_period("Q"))
    tab = pd.DataFrame({"media": q.mean(), "min": q.min(), "max": q.max(), "dias": q.size(),
                        "distintos": q.nunique(), "no_positivos": q.apply(lambda v: (v <= 0).sum()),
                        "igual_al_anterior": q.apply(lambda v: (v.diff() == 0).sum())})
    print(tab.round(2).to_string())
    for per, r in tab.iterrows():
        for k in tab.columns:
            num(f"pol_{per}_{k}", r[k])
    num("pol_total_no_positivos", (s <= 0).sum()); num("pol_min_diario", s.min())
    malos = [str(pq) for pq in pd.period_range("2020Q4", "2022Q3", freq="Q")]
    for lab, dd in (("todo", d), ("sin_pol_2020Q4_2022Q3", d[~((d["country"] == "poland") & d["quarter"].isin(malos))]),
                    ("sin_polonia", d[d["country"] != "poland"])):
        m, _ = x0.p13.fit(dd)
        for n_, c in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"pol_{lab}_{c}", m.params[n_]); num(f"pol_{lab}_{c}_p_dk", m.pvalues[n_])
        num(f"pol_{lab}_N", m.nobs)


def main():
    print("x1: forma", "niveles" if x0.NIV else "logs")
    d = x0.datos()
    assert len(d) == 765
    bloque_simultaneidad(d)
    bloque_precedencia(d)
    bloque_polonia(d)
    for k, v in NUM.items():
        print(f"  {k:44s} {v: .4f}")
    x0.guardar(NUM, "x1_comprobaciones")


if __name__ == "__main__":
    main()
