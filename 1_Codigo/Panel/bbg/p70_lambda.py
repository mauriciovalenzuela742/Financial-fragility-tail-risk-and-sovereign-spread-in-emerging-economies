# -*- coding: utf-8 -*-
"""
p70_lambda.py -- E4, E5 y la corrección de Holm sobre E1-E5 del preregistro 9
(4_Redaccion/preregistro_esg.md, commit 81c2d9c, anterior a los datos y a este script).

  ln EMBI_it = a_i + beta [ lambda G^_t + (1 - lambda) Dom^_it ] + e_it
  G_t = sum_k w_k z_k: ln VIX, UST10Y (log), US HY (log), USD NEER (log), todos en t-1.
  Dom_it = sum_j v_j z_j: ln JLoss_{t-1}, D_{t-1}, deuda/PIB_{t-4}, -reservas/PIB_{t-4}, inflación_{t-4}, -G_{t-1}.
  z = estandarizada en la muestra; w, v >= 0 y suman uno (softmax); G^ y Dom^ = índice / su desviación
  estándar dentro del país; lambda logística; beta > 0. a_i se concentra restando la media por país de la
  predicción y del ln EMBI (sin efectos de tiempo, que absorberían G_t). MCO no lineales desde 20 puntos.
  Inferencia: bootstrap por bloques móviles de 8 trimestres sobre el eje del tiempo (499); sin cada país.
  E4: lambda > 0,5, p = fracción de lambda* <= 0,5.
  E5: lambda_t = logística(th0 + th1 z(ln VIX_{t-1})); razón de verosimilitud contra lambda fijo (chi2_1),
      p unilateral con la convención de p42. Sin cada país: bootstrap de 199 (E4) y la misma RV (E5).
  Validación previa: simulación con los regresores reales, lambda = 0,6 y pesos iguales (100 réplicas);
  Shapley del R2 dentro del país del modelo lineal con los mismos dos bloques.
  Holm sobre E1-E5 (E1-E3 de bbg/paper_p69_numeros.csv). Exploratorio: TCRE y crecimiento en el bloque
  doméstico; EMBI en puntos básicos.

Salida: bbg/paper_p70_numeros.csv.
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
from scipy import stats
from scipy.optimize import least_squares

import p14_arbitro_lnlag as p14
import p42_resiliencia_preregistrada as p42
import p69_esg_spread as p69

OUT = os.path.join(HERE, "paper_p70_numeros.csv")
P69 = os.path.join(HERE, "paper_p69_numeros.csv")
NUM = {}
SEED = 20261027
B = int(os.environ.get("P70_B", 499))
B_LOO = int(os.environ.get("P70_B_LOO", 199))
EXT = ["VIX_l1", "UST_l1", "HY_l1", "NEER_l1"]
DOM = ["lnJ_l1", "D_l1", "debt_l4", "mres_l4", "infl_l4", "mG_l1"]


def num(k, v):
    NUM[k] = float(v)


def guardar():
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)


# ================================================================ datos
def datos():
    d, raw = p69.preparar()
    raw = raw.copy()
    raw["lnVIX"] = np.log(raw["VIX"])
    for col, k, name in (("lnVIX", 1, "VIX_l1"), ("UST10Y_log", 1, "UST_l1"), ("US_HY_spread_log", 1, "HY_l1"),
                         ("USD_NEER_log", 1, "NEER_l1"), ("debt_gdp", 4, "debt_l4"), ("res_gdp", 4, "res_l4"),
                         ("infl_yoy", 4, "infl_l4"), ("reer", 1, "reer_l1")):
        d = d.merge(p14.shift(raw, col, k, name), on=["country", "_qn"], how="left")
    d["lnJ_l1"] = d["ln_JLoss_l1"]
    d["mres_l4"] = -d["res_l4"]
    d["mG_l1"] = -d["G_l1"]
    d["lnreer_l1"] = np.log(d["reer_l1"].where(d["reer_l1"] > 0))
    d["mcrec"] = -d["crec_c"]
    return d


class Modelo:
    """Prepara matrices para un conjunto de bloques; y y la predicción se transforman dentro del país."""

    def __init__(self, d, ext, dom, y="ln_EMBI"):
        x = d.dropna(subset=[y] + ext + dom).copy()
        self.x, self.ext, self.dom = x, ext, dom
        self.n = len(x)
        self.idx = pd.factorize(x["country"])[0]
        self.G = self.idx.max() + 1
        cnt = np.bincount(self.idx)
        self._cnt = cnt
        self.yw = self.within(x[y].values)
        Z = x[ext + dom].values
        Z = (Z - Z.mean(0)) / Z.std(0)
        self.Ze, self.Zd = Z[:, :len(ext)], Z[:, len(ext):]
        v = x["VIX_l1"].values
        self.zv = (v - v.mean()) / v.std()

    def within(self, a):
        m = np.bincount(self.idx, weights=a) / self._cnt
        return a - m[self.idx]

    @staticmethod
    def softmax(u):
        e = np.exp(np.concatenate([[0.0], u]) - np.max(np.concatenate([[0.0], u])))
        return e / e.sum()

    def partes(self, th, regimen=False):
        K, J = self.Ze.shape[1], self.Zd.shape[1]
        i = 0
        beta = np.exp(th[i]); i += 1
        if regimen:
            a0, a1 = th[i], th[i + 1]; i += 2
        else:
            a0, a1 = th[i], 0.0; i += 1
        w = self.softmax(th[i:i + K - 1]); i += K - 1
        v = self.softmax(th[i:i + J - 1])
        ge, gd = self.Ze @ w, self.Zd @ v
        ge = ge / self.within(ge).std(); gd = gd / self.within(gd).std()
        lam = 1 / (1 + np.exp(-(a0 + a1 * self.zv)))
        return beta, lam, w, v, ge, gd

    def resid(self, th, regimen=False):
        beta, lam, w, v, ge, gd = self.partes(th, regimen)
        return self.yw - self.within(beta * (lam * ge + (1 - lam) * gd))

    def ajustar(self, regimen=False, starts=20, seed=SEED, th0=None):
        K, J = self.Ze.shape[1], self.Zd.shape[1]
        p = 1 + (2 if regimen else 1) + (K - 1) + (J - 1)
        rng = np.random.default_rng(seed)
        inicios = [] if th0 is None else [np.asarray(th0, float)]
        while len(inicios) < starts:
            inicios.append(np.concatenate([[np.log(self.yw.std() * rng.uniform(0.2, 1.5))],
                                           rng.normal(0, 1.5, p - 1)]))
        best = None
        for t0 in inicios:
            try:
                r = least_squares(self.resid, t0, args=(regimen,), method="trf", max_nfev=4000)
            except Exception:
                continue
            if best is None or r.cost < best.cost:
                best = r
        return best

    def ssr(self, r):
        return 2 * r.cost


def lam_fijo(mod, r):
    return 1 / (1 + np.exp(-r.x[1]))


# ================================================================ bootstrap por bloques de tiempo
def bloques(d, rng, L=8):
    qs = np.array(sorted(d["quarter"].unique()))
    T = len(qs)
    sel = []
    while len(sel) < T:
        s = rng.integers(0, T - L + 1)
        sel.extend(qs[s:s + L])
    sel = sel[:T]
    partes = [d[d["quarter"] == q] for q in sel]
    return pd.concat(partes, ignore_index=True)


def boot_lambda(d, r0, Bn, seed, ext=EXT, dom=DOM):
    rng = np.random.default_rng(seed)
    out = []
    for b in range(Bn):
        db = bloques(d, rng)
        m = Modelo(db, ext, dom)
        if m.G < 3:
            continue
        r = m.ajustar(starts=4, seed=seed + b, th0=r0.x)
        if r is not None:
            out.append(lam_fijo(m, r))
    return np.array(out)


# ================================================================ Shapley
def r2_within(mod, cols_e, cols_d):
    Z = np.hstack([mod.Ze[:, cols_e], mod.Zd[:, cols_d]]) if (cols_e or cols_d) else None
    if Z is None or Z.shape[1] == 0:
        return 0.0
    Zw = np.column_stack([mod.within(Z[:, j]) for j in range(Z.shape[1])])
    b = np.linalg.lstsq(Zw, mod.yw, rcond=None)[0]
    e = mod.yw - Zw @ b
    return 1 - e.var() / mod.yw.var()


def shapley(mod, pref):
    E, D = list(range(mod.Ze.shape[1])), list(range(mod.Zd.shape[1]))
    rE, rD, rA = r2_within(mod, E, []), r2_within(mod, [], D), r2_within(mod, E, D)
    sE = 0.5 * (rE + (rA - rD)); sD = 0.5 * (rD + (rA - rE))
    num(f"{pref}_R2_ext", rE); num(f"{pref}_R2_dom", rD); num(f"{pref}_R2_todo", rA)
    num(f"{pref}_shapley_ext", sE / rA); num(f"{pref}_shapley_dom", sD / rA)
    # coeficientes lineales sin restringir (signo de cada variable)
    Z = np.hstack([mod.Ze, mod.Zd]); Zw = np.column_stack([mod.within(Z[:, j]) for j in range(Z.shape[1])])
    b = np.linalg.lstsq(Zw, mod.yw, rcond=None)[0]
    for c, bj in zip(mod.ext + mod.dom, b):
        num(f"{pref}_lineal_{c}", bj)


# ================================================================ simulación
def simulacion(mod, reps=100, lam=0.6, seed=SEED):
    rng = np.random.default_rng(seed)
    K, J = mod.Ze.shape[1], mod.Zd.shape[1]
    ge = mod.Ze @ np.full(K, 1 / K); gd = mod.Zd @ np.full(J, 1 / J)
    ge = ge / mod.within(ge).std(); gd = gd / mod.within(gd).std()
    Z = np.hstack([mod.Ze, mod.Zd]); Zw = np.column_stack([mod.within(Z[:, j]) for j in range(Z.shape[1])])
    e = mod.yw - Zw @ np.linalg.lstsq(Zw, mod.yw, rcond=None)[0]
    sig, beta = e.std(), 0.5 * mod.yw.std()
    senal = mod.within(beta * (lam * ge + (1 - lam) * gd))
    yw_real = mod.yw
    est = []
    for k in range(reps):
        mod.yw = senal + rng.normal(0, sig, mod.n)
        r = mod.ajustar(starts=6, seed=seed + k)
        est.append(lam_fijo(mod, r))
    mod.yw = yw_real
    est = np.array(est)
    num("sim_lambda_media", est.mean()); num("sim_lambda_sd", est.std())
    num("sim_lambda_p05", np.percentile(est, 5)); num("sim_lambda_p95", np.percentile(est, 95))
    num("sim_ok", float(abs(est.mean() - lam) <= 0.05))
    return est


# ================================================================ estimación
def estimar(d, ext, dom, pref, y="ln_EMBI", boot=0, seed=SEED):
    mod = Modelo(d, ext, dom, y=y)
    r = mod.ajustar()
    beta, lam, w, v, *_ = mod.partes(r.x)
    num(f"{pref}_N", mod.n); num(f"{pref}_paises", mod.G)
    num(f"{pref}_lambda", lam if np.isscalar(lam) else lam.mean()); num(f"{pref}_beta", beta)
    num(f"{pref}_ssr", mod.ssr(r)); num(f"{pref}_R2w", 1 - mod.ssr(r) / (mod.yw ** 2).sum())
    for c, wk in zip(ext, w):
        num(f"{pref}_w_{c}", wk)
    for c, vj in zip(dom, v):
        num(f"{pref}_v_{c}", vj)
    shapley(mod, pref)
    if boot:
        lb = boot_lambda(d, r, boot, seed, ext, dom)
        num(f"{pref}_boot_n", len(lb)); num(f"{pref}_lambda_ic05", np.percentile(lb, 2.5))
        num(f"{pref}_lambda_ic95", np.percentile(lb, 97.5)); num(f"{pref}_p_e4", np.mean(lb <= 0.5))
    return mod, r


def regimen(mod, r0, pref):
    th0 = np.concatenate([r0.x[:2], [0.0], r0.x[2:]])
    r1 = mod.ajustar(regimen=True, th0=th0)
    s0, s1 = mod.ssr(r0), mod.ssr(r1)
    lr = mod.n * np.log(s0 / s1)
    p_bi = stats.chi2.sf(max(lr, 0), 1)
    th1 = r1.x[2]
    k0, k1 = len(r0.x), len(r1.x)
    num(f"{pref}_th0", r1.x[1]); num(f"{pref}_th1", th1); num(f"{pref}_LR", lr); num(f"{pref}_p_LR", p_bi)
    num(f"{pref}_p_e5", p42.unilateral(p_bi, th1, +1))
    num(f"{pref}_BIC_fijo", mod.n * np.log(s0 / mod.n) + k0 * np.log(mod.n))
    num(f"{pref}_BIC_regimen", mod.n * np.log(s1 / mod.n) + k1 * np.log(mod.n))
    _, lam_t, *_ = mod.partes(r1.x, regimen=True)
    for q_ in (10, 50, 90):
        num(f"{pref}_lambda_t_p{q_}", np.percentile(lam_t, q_))
    return r1


def holm(ps):
    orden = sorted(ps, key=lambda k: ps[k])
    m, acum, out = len(ps), 0.0, {}
    for i, k in enumerate(orden):
        acum = max(acum, min(1.0, (m - i) * ps[k]))
        out[k] = acum
    return out


def main():
    print("p70: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), flush=True)
    d = datos()

    # validación previa a los datos reales
    m_sim = Modelo(d, EXT, DOM)
    simulacion(m_sim)
    guardar()
    print(f"  simulación: media lambda^ {NUM['sim_lambda_media']:.3f} (sd {NUM['sim_lambda_sd']:.3f}); "
          f"ok = {NUM['sim_ok']:.0f}", flush=True)

    # E4: lambda fijo
    mod, r0 = estimar(d, EXT, DOM, "lam", boot=B)
    guardar()
    print(f"  E4 lambda = {NUM['lam_lambda']:.3f} [{NUM['lam_lambda_ic05']:.3f}, {NUM['lam_lambda_ic95']:.3f}] "
          f"p {NUM['lam_p_e4']:.3f}; Shapley ext {NUM['lam_shapley_ext']:.3f}; N {NUM['lam_N']:.0f}", flush=True)
    # E5: lambda por régimen
    regimen(mod, r0, "lam")
    guardar()
    print(f"  E5 th1 = {NUM['lam_th1']:+.3f}  LR {NUM['lam_LR']:.2f}  p uni {NUM['lam_p_e5']:.3f}  "
          f"BIC fijo {NUM['lam_BIC_fijo']:.1f} régimen {NUM['lam_BIC_regimen']:.1f}", flush=True)

    # sin cada país
    ok4 = ok5 = 0
    for k, c in enumerate(sorted(d["country"].unique())):
        dc = d[d["country"] != c]
        mc, rc = estimar(dc, EXT, DOM, f"lam_sin_{c}", boot=B_LOO, seed=SEED + 100 * k)
        ok4 += int(NUM[f"lam_sin_{c}_lambda"] > 0.5 and NUM[f"lam_sin_{c}_p_e4"] < 0.10)
        regimen(mc, rc, f"lam_sin_{c}")
        ok5 += int(NUM[f"lam_sin_{c}_th1"] > 0 and NUM[f"lam_sin_{c}_p_e5"] < 0.10)
        guardar()
    num("e4_loo_ok", ok4); num("e5_loo_ok", ok5)

    # Holm sobre E1-E5
    p69n = pd.read_csv(P69, index_col=0)["valor"]
    ps = {"e1": p69n["e1_p_uni"], "e2": p69n["e2_p_uni"], "e3": p69n["e3_p_uni"],
          "e4": NUM["lam_p_e4"], "e5": NUM["lam_p_e5"]}
    loo = {"e1": p69n["e1_loo_ok"], "e2": p69n["e2_loo_ok"], "e3": p69n["e3_loo_ok"], "e4": ok4, "e5": ok5}
    ph = holm(ps)
    for k in ps:
        num(f"{k}_p_uni", ps[k]); num(f"{k}_p_holm", ph[k]); num(f"{k}_loo_ok", loo[k])
        num(f"{k}_firme", float(ph[k] < 0.05 and loo[k] == 13))
    guardar()

    # exploratorio
    estimar(d, EXT, DOM + ["lnreer_l1", "mcrec"], "lam_tcre_crec")
    estimar(d, EXT, DOM, "lam_pb", y="EMBI_bps")
    guardar()
    print(f"-> {OUT}")
    for k in ps:
        print(f"  {k}: p uni {ps[k]:.3f}  Holm {ph[k]:.3f}  sin cada país {loo[k]:.0f}/13  "
              f"firme {NUM[f'{k}_firme']:.0f}")
    print("  pesos externos:", ", ".join(f"{c} {NUM[f'lam_w_{c}']:.2f}" for c in EXT))
    print("  pesos domésticos:", ", ".join(f"{c} {NUM[f'lam_v_{c}']:.2f}" for c in DOM))
    print(f"  exploratorio: lambda con TCRE y crecimiento {NUM['lam_tcre_crec_lambda']:.3f}; "
          f"en pb {NUM['lam_pb_lambda']:.3f}")


if __name__ == "__main__":
    main()
