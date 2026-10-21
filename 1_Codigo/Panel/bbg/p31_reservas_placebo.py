# -*- coding: utf-8 -*-
"""
p31_reservas_placebo.py -- el moderador reservas/PIB bajo escrutinio.

En p19 la moderación reservas/PIB x fragilidad (g1 = -0,247 por d.e.; DK p<0,001; cluster país
p=0,048; wild p=0,08) se presentó como el resultado de moderación más robusto. Objeciones de árbitro:
  - reservas/PIB es un dato anual interpolado linealmente (los trimestres usan el cierre de año
    futuro) y entra contemporáneo;
  - la familia examinada fue de al menos 3 componentes x 2 riesgos x 2 formas funcionales;
  - depende de Polonia;
  - -0,247 contra una elasticidad media de 0,10 implica elasticidad negativa por sobre +0,4 d.e.

    ln EMBI = a_i + d_t + b1 J + b2 D + b3 JxD + r R + g1 J*R + g2 D*R + e      (R estandarizado)

Bloques, todos con p de Driscoll-Kraay, cluster por país y wild cluster bootstrap (Webb):
  (a) contemporáneo (reproduce p19: muestra con los tres componentes, N=670);
  (b) reservas rezagadas 4 y 8 trimestres;
  (c) reservas ex ante invariantes (media del país 2004-2007, o los primeros 16 trimestres
      disponibles), efecto directo absorbido; continua y dicotómica (sobre la mediana);
  (d) descomposición entre/dentro de países;
  (e) dejar un país fuera para (a) y (b, rezago 4);
  (f) efecto marginal de la fragilidad en el soporte de las reservas (figura);
  (g) moderadores PLACEBO del panel: cuenta corriente/PIB, inflación, tipo de cambio real,
      concentración bancaria (HHI trimestral y HHI estructural invariante);
  (h) p ajustados de Holm sobre la familia {reservas, deuda, balance fiscal} x {fragilidad, cola};
  (x) lo mismo, (a), (b) y (e), para resiliencia ex ante x riesgo de cola (g2 = -0,028 en p19).

Salida: bbg/paper_reservas_numeros.csv (o _nivlag) y fig_reservas_efecto_marginal_lnlag. Reutiliza
p13, p14 y p19 sin modificarlos.
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
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p19_resiliencia as p19

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = {}
CLU = dict(cov_type="clustered", cluster_entity=True)
COMP = p19.COMP
COLS3 = [c for c, _ in COMP]
B_TIT, B_SEC = 1999, 999
OUT = os.path.join(HERE, f"paper_reservas_numeros{SFX}.csv")


def num(k, v):
    NUM[k] = float(v)
    return v


def guardar(msg):
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)
    print(f"  {msg} ({len(NUM)} cifras)", flush=True)


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0.0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1.0, run)
    return adj


def fit(dd, rhs, kw=p14.DK):
    return PanelOLS.from_formula("ln_EMBI ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects",
                                 dd.set_index(["country", "t"])).fit(**kw)


def moderar(d, col, pref, absorbido=False, B=B_SEC, claves=("JxR", "TxR"), estandarizar=True, wild=True):
    """misma especificación que p19.moderar_con, con B elegible. Devuelve (modelo DK, datos)."""
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", col]).copy()
    dd["R"] = (dd[col] - dd[col].mean()) / dd[col].std() if estandarizar else dd[col]
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    dd["JxR"] = dd["J_c"] * dd["R"]; dd["TxR"] = dd["T_c"] * dd["R"]
    rhs = ["J_c", "T_c", "JxT", "JxR", "TxR"] + ([] if absorbido else ["R"])
    m = fit(dd, rhs); mc = fit(dd, rhs, CLU)
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", dd["country"].nunique())
    num(f"{pref}_b1", m.params["J_c"]); num(f"{pref}_b2", m.params["T_c"])
    for n, lab in (("JxR", "g1"), ("TxR", "g2")):
        num(f"{pref}_{lab}", m.params[n]); num(f"{pref}_{lab}_se_dk", m.std_errors[n])
        num(f"{pref}_{lab}_p_dk", m.pvalues[n]); num(f"{pref}_{lab}_p_pais", mc.pvalues[n])
        if wild and n in claves:
            p, _ = p14.wild_boot(dd, "ln_EMBI", rhs, n, B=B, weights="webb")
            num(f"{pref}_{lab}_p_wild", p)
    return m, dd


def entre_dentro(d, col, pref, B=B_SEC):
    """R = media del país (entre) + desviación (dentro), ambas en unidades de la d.e. total."""
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", col]).copy()
    s = dd[col].std(); mp = dd.groupby("country")[col].transform("mean")
    dd["Rb"] = (mp - dd[col].mean()) / s; dd["Rw"] = (dd[col] - mp) / s
    num(f"{pref}_var_entre_share", ((mp - dd[col].mean()) ** 2).sum() / ((dd[col] - dd[col].mean()) ** 2).sum())
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    for a in ("b", "w"):
        dd[f"JxR{a}"] = dd["J_c"] * dd[f"R{a}"]; dd[f"TxR{a}"] = dd["T_c"] * dd[f"R{a}"]
    rhs = ["J_c", "T_c", "JxT", "JxRb", "TxRb", "Rw", "JxRw", "TxRw"]
    m = fit(dd, rhs); mc = fit(dd, rhs, CLU)
    num(f"{pref}_N", m.nobs)
    for n, lab in (("JxRb", "g1_entre"), ("TxRb", "g2_entre"), ("JxRw", "g1_dentro"), ("TxRw", "g2_dentro")):
        num(f"{pref}_{lab}", m.params[n]); num(f"{pref}_{lab}_p_dk", m.pvalues[n]); num(f"{pref}_{lab}_p_pais", mc.pvalues[n])
        p, _ = p14.wild_boot(dd, "ln_EMBI", rhs, n, B=B, weights="webb")
        num(f"{pref}_{lab}_p_wild", p)


def loo(d, col, pref, lab="g1", absorbido=False, estandarizar=True):
    """deja un país fuera; resume rango, cuántos significativos al 5 % y los casos sin Polonia / Turquía."""
    clave = "JxR" if lab == "g1" else "TxR"
    filas = []
    for c in sorted(d.dropna(subset=[col])["country"].unique()):
        moderar(d[d["country"] != c], col, f"{pref}_sin_{c}", absorbido=absorbido, claves=(clave,), estandarizar=estandarizar)
        k = f"{pref}_sin_{c}_{lab}"
        filas.append((c, NUM[k], NUM[k + "_p_dk"], NUM[k + "_p_pais"], NUM[k + "_p_wild"]))
    t = pd.DataFrame(filas, columns=["pais", "b", "p_dk", "p_pais", "p_wild"]).set_index("pais")
    num(f"{pref}_loo_n", len(t)); num(f"{pref}_loo_min", t["b"].min()); num(f"{pref}_loo_max", t["b"].max())
    for tipo in ("dk", "pais", "wild"):
        num(f"{pref}_loo_n_sig5_{tipo}", (t["p_" + tipo] < 0.05).sum())
        num(f"{pref}_loo_n_sig10_{tipo}", (t["p_" + tipo] < 0.10).sum())
    num(f"{pref}_loo_n_signo_negativo", (t["b"] < 0).sum())
    print(f"   LOO {pref} ({lab}):"); print(t.round(4).to_string(), flush=True)
    return t


def efecto_marginal(m, dd, pref):
    """d ln EMBI / d J = b1 + g1 R (con D en su media), en percentiles de R estandarizado."""
    V = m.cov; b1, g1 = m.params["J_c"], m.params["JxR"]

    def me(r):
        r = np.asarray(r, float)
        return b1 + g1 * r, np.sqrt(V.loc["J_c", "J_c"] + r ** 2 * V.loc["JxR", "JxR"] + 2 * r * V.loc["J_c", "JxR"])
    for pc in (10, 25, 50, 75, 90):
        r = dd["R"].quantile(pc / 100); e, s = me([r])
        num(f"{pref}_p{pc}_R", r); num(f"{pref}_p{pc}", e[0]); num(f"{pref}_p{pc}_lo", e[0] - 1.96 * s[0]); num(f"{pref}_p{pc}_hi", e[0] + 1.96 * s[0])
    cruce = -b1 / g1
    num(f"{pref}_cruce_R", cruce); num(f"{pref}_share_obs_negativo", (dd["R"] > cruce).mean() if g1 < 0 else (dd["R"] < cruce).mean())
    e, s = me(dd["R"].values)
    num(f"{pref}_share_obs_negativo_sig", ((e + 1.96 * s) < 0).mean()); num(f"{pref}_share_obs_positivo_sig", ((e - 1.96 * s) > 0).mean())
    return me


def figura_me(m, dd):
    me = efecto_marginal(m, dd, "me")
    grid = np.linspace(dd["R"].quantile(.01), dd["R"].quantile(.99), 120)
    e, s = me(grid)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.axhline(0, color=p13.INK2, lw=0.8)
    ax.fill_between(grid, e - 1.96 * s, e + 1.96 * s, color=p13.BLUE, alpha=0.15, lw=0, label="IC 95 % (Driscoll–Kraay)")
    ax.plot(grid, e, color=p13.BLUE, lw=2.2)
    for pc in (10, 25, 50, 75, 90):
        r = NUM[f"me_p{pc}_R"]; v = NUM[f"me_p{pc}"]
        ax.plot(r, v, "o", color=p13.ORANGE, ms=5, zorder=5)
        ax.annotate(f"p{pc}", (r, v), textcoords="offset points", xytext=(5, 6), fontsize=8, color=p13.ORANGE)
    ax.plot(dd["R"], np.full(len(dd), ax.get_ylim()[0]), "|", color=p13.INK2, alpha=0.3, ms=6)
    ax.set_xlabel("reservas/PIB (desviaciones estándar respecto de la media muestral)")
    ax.set_ylabel(p13.LAB["me"])
    ax.set_title("Efecto marginal de la fragilidad bancaria según las reservas internacionales\n"
                 f"(moderación contemporánea, {p13.LAB['spec']}, FE país + tiempo)", fontsize=9.5)
    ax.legend(fontsize=8, loc="upper right")
    p13.save(fig, "fig_reservas_efecto_marginal_lnlag")


def exante_pais(raw, paises, col):
    """media del país 2004-2007 de `col`; si falta, primeros 16 trimestres disponibles."""
    r = raw.dropna(subset=[col]); r = r[r["country"].isin(paises)].sort_values(["country", "quarter"])
    pre = r[(r["quarter"] >= "2004Q1") & (r["quarter"] <= "2007Q4")].groupby("country").agg(v=(col, "mean"), n=(col, "size"))
    falt = [p_ for p_ in paises if p_ not in pre.index]
    alt = r[r["country"].isin(falt)].groupby("country").head(16).groupby("country").agg(
        v=(col, "mean"), n=(col, "size"), q0=("quarter", "min"), q1=("quarter", "max"))
    return pre, alt


def exante_resiliencia(dd3):
    """clasificación ex ante de p19.variantes (misma lógica, sin editar p19): índice de los tres
    componentes promediado en 2004-2007 (o primeros 16 trimestres); alta = sobre la mediana."""
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"]).dropna(subset=COLS3)
    raw = raw[raw["country"].isin(dd3["country"].unique())].sort_values(["country", "quarter"])
    for c, s in COMP:
        raw["z_" + c] = s * (raw[c] - raw[c].mean()) / raw[c].std()
    raw["R0"] = raw[["z_" + c for c, _ in COMP]].mean(axis=1)
    pre = raw[raw["quarter"] <= "2007Q4"].groupby("country")["R0"].mean()
    falt = [p_ for p_ in dd3["country"].unique() if p_ not in pre.index]
    if falt:
        pre = pd.concat([pre, raw[raw["country"].isin(falt)].groupby("country").head(16).groupby("country")["R0"].mean()])
    return pre, falt


def main():
    print("p31: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, _ = p14.check_principal(d)
    num("principal_N", m0.nobs); num("principal_b1", m0.params["J_c"]); num("principal_b2", m0.params["T_c"]); num("principal_b3", m0.params["JxT"])
    for k in (8,):                                             # rezago 8 de los componentes (p14.base trae el 4)
        for c in COLS3:
            d = d.merge(p14.shift(raw, c, k, f"{c}_l{k}"), on=["country", "_qn"], how="left")
    d3 = d.dropna(subset=COLS3).copy()                          # muestra de p19.variantes (tres componentes)
    paises = sorted(d["country"].unique())

    # ---------------- (a) contemporáneo: reproduce p19 con la función de p19 y con la propia
    p19.moderar_con(d3, "res_gdp", "p19a")
    for k, v in p19.NUM.items():
        num(k, v)
    moderar(d3, "res_gdp", "a", B=B_TIT)
    assert abs(NUM["a_g1"] - NUM["p19a_g1"]) < 1e-10 and abs(NUM["a_g1_p_wild"] - NUM["p19a_g1_p_wild"]) < 1e-12
    if not NIV:
        assert int(NUM["a_N"]) == 670 and abs(NUM["a_g1"] + 0.247) < 0.002, NUM["a_g1"]
    num("res_media", d3["res_gdp"].mean()); num("res_de", d3["res_gdp"].std())
    guardar("(a) contemporaneo")

    # ---------------- (b) rezagos 4 y 8
    moderar(d, "res_gdp_l4", "b_l4"); moderar(d, "res_gdp_l8", "b_l8")
    moderar(d3.dropna(subset=["res_gdp_l4"]), "res_gdp_l4", "b_l4_m3")     # misma muestra de (a) con rezago disponible
    guardar("(b) rezagos")

    # ---------------- (c) ex ante invariante
    pre, alt = exante_pais(raw, paises, "res_gdp")
    print("   reservas ex ante 2004-07:", pre.round(2).to_dict()); print("   primeros 16 trimestres:"); print(alt.round(2).to_string())
    num("c_paises_con_2004_07", len(pre)); num("c_paises_primeros16", len(alt))
    for c in pre.index:
        num(f"c_exante_{c}", pre.loc[c, "v"]); num(f"c_exante_{c}_usa0407", 1); num(f"c_exante_{c}_n", pre.loc[c, "n"])
    for c in alt.index:
        num(f"c_exante_{c}", alt.loc[c, "v"]); num(f"c_exante_{c}_usa0407", 0); num(f"c_exante_{c}_n", alt.loc[c, "n"])
    ex = pd.concat([pre["v"], alt["v"]])
    d["res_exante"] = d["country"].map(ex); d["res_exante_alta"] = d["country"].map((ex > ex.median()).astype(float))
    num("c_n_alta", (ex > ex.median()).sum())
    print("   reservas ex ante altas:", sorted(ex[ex > ex.median()].index))
    moderar(d, "res_exante", "c_cont", absorbido=True)
    moderar(d, "res_exante_alta", "c_dic", absorbido=True, estandarizar=False)
    moderar(d[d["country"].isin(pre.index)], "res_exante", "c_cont_solo0407", absorbido=True)
    guardar("(c) ex ante")

    # ---------------- (d) entre / dentro
    entre_dentro(d3, "res_gdp", "d"); entre_dentro(d, "res_gdp_l4", "d_l4")
    guardar("(d) entre/dentro")

    # ---------------- (e) dejar un país fuera
    loo(d3, "res_gdp", "e_a"); loo(d, "res_gdp_l4", "e_l4")
    guardar("(e) LOO")

    # ---------------- (f) efecto marginal
    m, dd = moderar(d3, "res_gdp", "f", wild=False)
    figura_me(m, dd)
    ml, ddl = moderar(d, "res_gdp_l4", "f_l4", wild=False)
    efecto_marginal(ml, ddl, "me_l4")
    guardar("(f) efecto marginal")

    # ---------------- (g) placebos
    hq = pd.read_csv(os.path.join(HERE, "concentracion_trimestral_bbg.csv"))[["country", "quarter", "HHI_q"]]
    d = d.merge(hq, on=["country", "quarter"], how="left")
    hq["_qn"] = pd.PeriodIndex(hq["quarter"], freq="Q").year * 4 + pd.PeriodIndex(hq["quarter"], freq="Q").quarter + 4
    d = d.merge(hq.rename(columns={"HHI_q": "HHI_q_l4"})[["country", "_qn", "HHI_q_l4"]], on=["country", "_qn"], how="left")
    plac = [("ca_gdp", False), ("ca_gdp_l4", False), ("infl_yoy", False), ("infl_yoy_l4", False), ("reer", False),
            ("reer_l4", False), ("HHI_q", False), ("HHI_q_l4", False), ("HHI_struct", True)]
    for col, absb in plac:
        moderar(d, col, "g_" + col, absorbido=absb)
    for lab in ("g1", "g2"):
        for tipo in ("dk", "pais", "wild"):
            ps = [NUM[f"g_{c}_{lab}_p_{tipo}"] for c, _ in plac]
            num(f"g_n_sig5_{lab}_{tipo}", sum(p < 0.05 for p in ps)); num(f"g_n_sig10_{lab}_{tipo}", sum(p < 0.10 for p in ps))
        # cuántos placebos igualan o superan la evidencia de las reservas contemporáneas
        for tipo in ("dk", "pais", "wild"):
            num(f"g_n_supera_reservas_{lab}_{tipo}", sum(NUM[f"g_{c}_{lab}_p_{tipo}"] <= NUM[f"a_g1_p_{tipo}"] for c, _ in plac))
    num("g_n_placebos", len(plac))
    guardar("(g) placebos")

    # ---------------- (h) Holm sobre la familia {reservas, deuda, balance fiscal} x {fragilidad, cola}
    for c, s in COMP:                                           # idéntico a p19.variantes, parte 1
        d3["R_" + c] = s * d3[c]
        moderar(d3, "R_" + c, "h_" + c, B=B_TIT)
    fam = [(c, lab) for c in COLS3 for lab in ("g1", "g2")]
    for tipo in ("wild", "dk", "pais"):
        adj = holm([NUM[f"h_{c}_{lab}_p_{tipo}"] for c, lab in fam])
        for (c, lab), a in zip(fam, adj):
            num(f"h_{c}_{lab}_p_{tipo}_holm", a)
    try:                                                        # control contra lo publicado por p19
        ref = pd.read_csv(os.path.join(HERE, f"paper_resiliencia_numeros{SFX}.csv"), index_col="clave")["valor"]
        num("h_max_dif_con_p19", max(abs(ref[f"comp_{c}_{lab}_p_wild"] - NUM[f"h_{c}_{lab}_p_wild"]) for c, lab in fam))
    except Exception as e:
        print("   sin comparacion con paper_resiliencia_numeros:", repr(e)[:80])
    guardar("(h) Holm")

    # ---------------- (x) resiliencia ex ante x riesgo de cola
    prex, falt = exante_resiliencia(d3)
    alta = (prex > prex.median()).astype(float)
    print("   resiliencia ex ante alta:", sorted(alta[alta > 0].index), "| sin 2004-07:", sorted(falt))
    num("x_paises_con_2004_07", len(prex) - len(falt)); num("x_n_alta", alta.sum())
    d3["R_exante_alta"] = d3["country"].map(alta); d3["R_exante"] = d3["country"].map(prex)
    moderar(d3, "R_exante_alta", "x_a", absorbido=True, B=B_TIT, estandarizar=False)          # (a) reproduce p19
    if not NIV:
        assert abs(NUM["x_a_g2"] + 0.0283) < 0.001, NUM["x_a_g2"]
    moderar(d3, "R_exante", "x_cont", absorbido=True)                                          # continuo en vez de dicotómico
    for suf, pref in (("", "x_b_t"), ("_l4", "x_b_l4"), ("_l8", "x_b_l8")):                    # (b) índice variable, t / t-4 / t-8
        s_ = d.dropna(subset=[c + suf for c in COLS3]).copy()
        z = [sg * (s_[c + suf] - s_[c + suf].mean()) / s_[c + suf].std() for c, sg in COMP]
        s_["R_idx"] = sum(z) / len(z)
        moderar(s_, "R_idx", pref)
    loo(d3, "R_exante_alta", "x_e", lab="g2", absorbido=True, estandarizar=False)             # (e) clasificación fija
    guardar("(x) resiliencia ex ante")

    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:40s} {v: .4f}")
    print("->", OUT)


if __name__ == "__main__":
    main()
