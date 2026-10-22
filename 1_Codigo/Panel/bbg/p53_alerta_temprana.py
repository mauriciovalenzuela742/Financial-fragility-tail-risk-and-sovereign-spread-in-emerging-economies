# -*- coding: utf-8 -*-
"""
p53_alerta_temprana.py -- U4 del preregistro 4 (4_Redaccion/preregistro_umbrales.md, commit 7ad3810):
alerta temprana de episodios de estrés soberano, umbrales de señal y semáforo; al final, Holm sobre la
familia primaria {P1, P2, P3} (P1 y P2 desde paper_p52_numeros.csv).

  Episodio: C_it = 1 si ln EMBI_it - ln EMBI_{i,t-4} supera el percentil 90 de esa variación en el país.
  Objetivo: Y_it = 1 si hay un episodio en t+1..t+4 (los cuatro observados); se excluyen las observaciones
  con C = 1 en t, t-1, t-2 o t-3 (sesgo post-crisis).
  Señales en t: ln JLoss_t, D_t, deuda_{t-1} (debt_q) y FCI_t, estandarizadas por país con media y
  desviación expansivas (mínimo 12 trimestres). Secundarias: -DD_t en lugar de JLoss; logit sin deuda.
  Logit agrupado sin efectos fijos. Fuera de la muestra: recursivo desde 2012T1; en t se estima con las
  observaciones de s <= t-4 (objetivo ya observado) y se predice t. AUROC con IC al 90 % y p unilateral
  frente a 0,5 por bootstrap de bloques de país (999): p = fracción de réplicas con AUROC <= 0,5.
  Umbrales: en cada t, el tau que minimiza L(mu) = mu T1 + (1-mu) T2 en el entrenamiento, mu = 0,5 y 0,7;
  fuera de la muestra se reportan T1, T2 y la utilidad relativa de Alessi-Detken. Semáforo: rojo si
  z >= tau(0,5); ámbar si tau(0,7) <= z < tau(0,5); verde si z < tau(0,7).
  Por país (descriptivo): AUROC dentro de la muestra del logit combinado donde haya >= 3 episodios.
  Menos de 20 episodios fuera de la muestra: P3 no evaluable.
Salida: bbg/paper_p53_numeros.csv y bbg/alerta_temprana_bbg.csv (predicciones fuera de la muestra).
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
import statsmodels.api as sm

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p52_umbrales as p52

NUM = p32.NUM
B = 999
INICIO = 2012 * 4 + 1


def num(k, v):
    NUM[k] = float(v)


def auc(y, s):
    y = np.asarray(y); s = np.asarray(s)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    r = pd.Series(np.concatenate([pos, neg])).rank().values
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def expansiva(s, minobs=12):
    v = s.values.astype(float); out = np.full(len(v), np.nan)
    for i in range(len(v)):
        h = v[:i + 1]; h = h[~np.isnan(h)]
        if len(h) >= minobs and not np.isnan(v[i]) and h.std() > 0:
            out[i] = (v[i] - h.mean()) / h.std()
    return pd.Series(out, index=s.index)


def panel():
    d, raw = p14.base()
    paises = sorted(d["country"].unique())
    r = raw[raw["country"].isin(paises)].copy().sort_values(["country", "_qn"])
    res = pd.read_csv(p42.RES); q = pd.PeriodIndex(res["quarter"], freq="Q"); res["_qn"] = q.year * 4 + q.quarter
    r = r.merge(p14.shift(res, "debt_q", 1, "debt_l1"), on=["country", "_qn"], how="left")
    f = p52.fci("GaR_panel_all18.xlsx", "FCI")
    r = r.merge(f[["country", "_qn", "FCI"]], on=["country", "_qn"], how="left")
    a = pd.read_csv(os.path.join(HERE, "fragilidad_alternativa_bbg.csv"))
    q = pd.PeriodIndex(a["quarter"], freq="Q"); a["_qn"] = q.year * 4 + q.quarter; a["FDD"] = -a["DD_w"]
    r = r.merge(a[["country", "_qn", "FDD"]], on=["country", "_qn"], how="left")
    # rejilla completa de trimestres por país, para que los desplazamientos respeten los huecos
    out = []
    for c, g in r.groupby("country"):
        full = pd.DataFrame({"_qn": np.arange(g["_qn"].min(), g["_qn"].max() + 1)})
        g = full.merge(g, on="_qn", how="left"); g["country"] = c
        g["dy4"] = g["ln_EMBI"] - g["ln_EMBI"].shift(4)
        g["C"] = (g["dy4"] > g["dy4"].quantile(0.90)).astype(float).where(g["dy4"].notna())
        fut = pd.concat([g["C"].shift(-h) for h in range(1, 5)], axis=1)
        g["Y"] = fut.max(axis=1).where(fut.notna().all(axis=1))
        pas = pd.concat([g["C"].shift(h) for h in range(0, 4)], axis=1)
        g["post"] = (pas.fillna(0).max(axis=1) > 0)
        for s, src in (("zJ", "ln_JLoss"), ("zD", "D_pp"), ("zDEBT", "debt_l1"), ("zFCI", "FCI"), ("zDD", "FDD")):
            g[s] = expansiva(g[src])
        out.append(g)
    return pd.concat(out, ignore_index=True)


def logit_fit(X, y):
    try:
        return sm.Logit(y, sm.add_constant(X, has_constant="add")).fit(disp=0, maxiter=200)
    except Exception:
        return None


def oos(p, sig, pref):
    x = p[(~p["post"]) & p["Y"].notna()].dropna(subset=sig).copy()
    num(f"{pref}_N", len(x)); num(f"{pref}_eventos", x["Y"].sum()); num(f"{pref}_paises", x["country"].nunique())
    m = logit_fit(x[sig].values, x["Y"].values)
    if m is not None:
        x["p_in"] = m.predict(sm.add_constant(x[sig].values, has_constant="add"))
        num(f"{pref}_auc_in", auc(x["Y"], x["p_in"]))
        for j, s in enumerate(sig):
            num(f"{pref}_coef_{s}", m.params[j + 1]); num(f"{pref}_p_{s}", m.pvalues[j + 1])
    preds = []
    for t in sorted(x.loc[x["_qn"] >= INICIO, "_qn"].unique()):
        tr = x[x["_qn"] <= t - 4]
        if tr["Y"].sum() < 5:
            continue
        mt = logit_fit(tr[sig].values, tr["Y"].values)
        if mt is None:
            continue
        te = x[x["_qn"] == t]
        pr = te[["country", "_qn", "Y"]].copy()
        pr["p"] = mt.predict(sm.add_constant(te[sig].values, has_constant="add"))
        for s in sig:   # umbrales por señal con el entrenamiento
            for mu in (0.5, 0.7):
                pr[f"tau_{s}_{mu}"] = umbral(tr[s].values, tr["Y"].values, mu)
            pr[s] = te[s].values
        preds.append(pr)
    P = pd.concat(preds, ignore_index=True)
    ev = int(P["Y"].sum())
    num(f"{pref}_oos_N", len(P)); num(f"{pref}_oos_eventos", ev)
    a = auc(P["Y"], P["p"]); num(f"{pref}_auc_oos", a)
    rng = np.random.default_rng(23); paises = P["country"].unique(); bs = []
    grupos = {c: P[P["country"] == c] for c in paises}
    for _ in range(B):
        s = pd.concat([grupos[c] for c in rng.choice(paises, len(paises))])
        bs.append(auc(s["Y"], s["p"]))
    bs = np.array(bs); bs = bs[~np.isnan(bs)]
    num(f"{pref}_auc_oos_lo90", np.quantile(bs, .05)); num(f"{pref}_auc_oos_hi90", np.quantile(bs, .95))
    num(f"{pref}_auc_oos_p", float(np.mean(bs <= 0.5)))
    num(f"{pref}_evaluable", float(ev >= 20))
    for s in sig:
        num(f"{pref}_auc_oos_{s}", auc(P["Y"], P[s]))
        for mu in (0.5, 0.7):
            sigl = (P[s] >= P[f"tau_{s}_{mu}"]).astype(float)
            T1 = float(((sigl == 0) & (P["Y"] == 1)).sum() / max(P["Y"].sum(), 1))
            T2 = float(((sigl == 1) & (P["Y"] == 0)).sum() / max((P["Y"] == 0).sum(), 1))
            L = mu * T1 + (1 - mu) * T2; Ur = (min(mu, 1 - mu) - L) / min(mu, 1 - mu)
            num(f"{pref}_{s}_mu{mu}_T1", T1); num(f"{pref}_{s}_mu{mu}_T2", T2); num(f"{pref}_{s}_mu{mu}_Ur", Ur)
        rojo = P[s] >= P[f"tau_{s}_0.5"]; amb = (P[s] >= P[f"tau_{s}_0.7"]) & ~rojo; verde = ~(rojo | amb)
        for lab, mk in (("rojo", rojo), ("ambar", amb), ("verde", verde)):
            num(f"{pref}_{s}_{lab}_frac", mk.mean())
            num(f"{pref}_{s}_{lab}_tasa_evento", P.loc[mk, "Y"].mean() if mk.any() else np.nan)
    return x, P


def umbral(z, y, mu):
    """tau que minimiza mu*T1 + (1-mu)*T2 en el entrenamiento (señal: z >= tau)."""
    cand = np.unique(np.quantile(z, np.linspace(0.02, 0.98, 97)))
    npos, nneg = max(y.sum(), 1), max((y == 0).sum(), 1)
    best, bt = np.inf, cand[0]
    for c in cand:
        s = z >= c
        L = mu * ((~s) & (y == 1)).sum() / npos + (1 - mu) * (s & (y == 0)).sum() / nneg
        if L < best:
            best, bt = L, c
    return bt


def familia():
    f52 = os.path.join(HERE, "paper_p52_numeros.csv")
    v = pd.read_csv(f52, index_col=0)["valor"]
    ps = {"P1": v["U1_p_bloques"], "P2": v["U2_p_bloques"], "P3": NUM["U4_auc_oos_p"]}
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden); acum = 0.0; h = {}
    for r, (k, p) in enumerate(orden):
        acum = max(acum, min(1.0, (m - r) * p)); h[k] = acum
    for k in ps:
        num(f"familia_{k}_p", ps[k]); num(f"familia_{k}_holm", h[k])
    for k, pref, S in (("P1", "U1", ["J_c", "T_c"]), ("P2", "U2", ["T_c"])):
        dirok = any(v[f"{pref}_{s}_dif"] > 0 and v[f"{pref}_{s}_p_uni"] < 0.10 and
                    v[f"{pref}_{s}_loo_pos"] == v[f"{pref}_loo_n"] for s in S)
        num(f"familia_{k}_firme", float(h[k] < 0.05 and dirok))
        num(f"familia_{k}_direccion_ok", float(dirok))
    num("familia_P3_firme", float(h["P3"] < 0.05 and NUM["U4_evaluable"] == 1))


def main():
    p = panel()
    x, P = oos(p, ["zJ", "zD", "zDEBT", "zFCI"], "U4")
    P.to_csv(os.path.join(HERE, "alerta_temprana_bbg.csv"), index=False)
    # por país, dentro de la muestra
    for c, g in x.groupby("country"):
        if g["Y"].sum() >= 3 and "p_in" in g:
            num(f"U4_auc_in_{c}", auc(g["Y"], g["p_in"]))
    num("U4_paises_auc_in", sum(1 for k in NUM if k.startswith("U4_auc_in_") and k != "U4_auc_in"))
    oos(p, ["zDD", "zD", "zDEBT", "zFCI"], "U4dd")
    oos(p, ["zJ", "zD", "zFCI"], "U4sindeuda")
    familia()
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p53_numeros.csv"))
    for k, v in NUM.items():
        print(f"  {k:34s} {v: .4f}")


if __name__ == "__main__":
    main()
