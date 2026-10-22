# -*- coding: utf-8 -*-
"""
p56_inferencia_conjunta.py -- N6 de 4_Redaccion/plan_nota7.md: inferencia conjunta sobre los cuatro
preregistros y aleatorización del hallazgo central. Es una comprobación posterior y más exigente que las
de cada preregistro: no puede agregar hallazgos, solo quitarlos.

  (a) Las 14 hipótesis primarias de los cuatro preregistros, con el p unilateral que cada uno reportó:
        preregistro 1 (c492ca3): R-H2 reservas, R-H3 deuda x riesgo de cola           (paper_p42)
        preregistro 2 (f820594): R2-H1 doom loop, R2-H2 pecado original, R2-H3 D4      (paper_p45)
        preregistro 3 (d73245f): mu1-H1, mu1-H2, mu3-H1, mu3-H2, mu4-H1, mu5-H1         (paper_p51)
        preregistro 4 (7ad3810): P1 tensión, P2 deuda, P3 alerta temprana               (paper_p53)
      Corrección de Holm sobre las 14 (FWER, válida con cualquier dependencia) y Benjamini-Yekutieli
      (FDR, válida con cualquier dependencia); Benjamini-Hochberg como referencia. Romano-Wolf no se
      aplica: cada familia usa su propio bootstrap y no hay una distribución conjunta común.
  (b) Inferencia por aleatorización del hallazgo central: se asigna a cada país la trayectoria de deuda
      (DEBT, t-4) de otro país, con una permutación de los 13 (999 permutaciones), y se reestima el
      coeficiente de D_{t-1} x deuda (R-H3) y de D4_{t-1} x deuda; p unilateral = fracción de permutaciones
      con un coeficiente mayor o igual que el observado (incluido el observado).
Salida: bbg/paper_p56_numeros.csv.
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

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p45_macro_preregistrada as p45

NUM = p32.NUM
B = int(os.environ.get("P56_B", 999))


def num(k, v):
    NUM[k] = float(v)


def leer(f):
    return pd.read_csv(os.path.join(HERE, f), index_col=0)["valor"]


def holm(ps):
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden); acum = 0.0; out = {}
    for r, (k, p) in enumerate(orden):
        acum = max(acum, min(1.0, (m - r) * p)); out[k] = acum
    return out


def bh(ps, by=False):
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden)
    c = sum(1.0 / i for i in range(1, m + 1)) if by else 1.0
    q = [min(1.0, p * m * c / (r + 1)) for r, (k, p) in enumerate(orden)]
    for i in range(m - 2, -1, -1):
        q[i] = min(q[i], q[i + 1])
    return {k: q[i] for i, (k, _) in enumerate(orden)}


def familia_conjunta():
    v42, v45, v51, v53 = leer("paper_p42_numeros.csv"), leer("paper_p45_numeros.csv"), leer("paper_p51_numeros.csv"), leer("paper_p53_numeros.csv")
    ps = {"R-H2": v42["rh2_p_uni"], "R-H3": v42["rh3_p_uni"],
          "R2-H1": v45["r2h1_p_uni"], "R2-H2": v45["r2h2_p_uni"], "R2-H3": v45["r2h3_b2_p_uni"],
          "mu1-H1": v51["familia_mu1h1_p_uni"], "mu1-H2": v51["familia_mu1h2_p_uni"],
          "mu3-H1": v51["familia_mu3h1_p_uni"], "mu3-H2": v51["familia_mu3h2_p_uni"],
          "mu4-H1": v51["familia_mu4h1_p_uni"], "mu5-H1": v51["familia_mu5h1_p_uni"],
          "P1": v53["familia_P1_p"], "P2": v53["familia_P2_p"], "P3": v53["familia_P3_p"]}
    h, q_bh, q_by = holm(ps), bh(ps), bh(ps, by=True)
    filas = []
    for k in sorted(ps, key=ps.get):
        num(f"conj_{k}_p", ps[k]); num(f"conj_{k}_holm", h[k]); num(f"conj_{k}_bh", q_bh[k]); num(f"conj_{k}_by", q_by[k])
        filas.append((k, ps[k], h[k], q_bh[k], q_by[k]))
    num("conj_m", len(ps))
    num("conj_holm05", sum(v < 0.05 for v in h.values())); num("conj_by05", sum(v < 0.05 for v in q_by.values()))
    num("conj_bh05", sum(v < 0.05 for v in q_bh.values())); num("conj_bh10", sum(v < 0.10 for v in q_bh.values()))
    print(pd.DataFrame(filas, columns=["hipótesis", "p", "Holm", "BH", "BY"]).round(3).to_string(index=False))


# ================================================================ aleatorización
def aniquilador(x):
    D = np.column_stack([pd.get_dummies(x["country"]).values, pd.get_dummies(x["quarter"]).values]).astype(float)
    return np.eye(len(x)) - D @ np.linalg.pinv(D)


def coef(d, debt, tcol):
    """coeficiente de T x deuda (deuda estandarizada en la muestra), como p42.moderacion."""
    x = d.merge(debt, on=["country", "_qn"], how="inner").dropna(subset=["ln_EMBI", "ln_JLoss_l1", tcol, "DEBTp"])
    x = x.reset_index(drop=True)
    J = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean(); T = x[tcol] - x[tcol].mean()
    M_s = (x["DEBTp"] - x["DEBTp"].mean()) / x["DEBTp"].std()
    X = np.column_stack([J, T, J * T, M_s, T * M_s])
    A = aniquilador(x)
    b = np.linalg.lstsq(A @ X, A @ x["ln_EMBI"].values, rcond=None)[0]
    return float(b[4]), len(x)


def aleatorizacion(d, raw, tcol, pref, ref):
    deuda = raw[["country", "_qn", "DEBT"]].dropna().copy()
    deuda["_qn"] = deuda["_qn"] + 4                       # deuda en t-4
    paises = sorted(d["country"].unique())
    def asignar(perm):
        m = dict(zip(paises, perm)); out = []
        for c in paises:
            g = deuda[deuda["country"] == m[c]][["_qn", "DEBT"]].copy(); g["country"] = c; out.append(g)
        return pd.concat(out).rename(columns={"DEBT": "DEBTp"})
    b_obs, n_obs = coef(d, asignar(paises), tcol)
    num(f"{pref}_b_obs", b_obs); num(f"{pref}_N_obs", n_obs)
    assert abs(b_obs - ref) < 1e-6, (b_obs, ref)          # reproduce el coeficiente preregistrado
    rng = np.random.default_rng(31); bs = []
    for _ in range(B):
        bs.append(coef(d, asignar(list(rng.permutation(paises))), tcol)[0])
    bs = np.array(bs)
    num(f"{pref}_p_perm", (1 + np.sum(bs >= b_obs)) / (B + 1))
    num(f"{pref}_perm_p95", np.quantile(bs, 0.95)); num(f"{pref}_perm_media", bs.mean())


def main():
    familia_conjunta()
    d, raw = p42.preparar()
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    v42, v45 = leer("paper_p42_numeros.csv"), leer("paper_p45_numeros.csv")
    aleatorizacion(d, raw, "D_l1", "perm_rh3", v42["rh3_b"])
    aleatorizacion(d.dropna(subset=["D4_l1"]), raw, "D4_l1", "perm_rh3D4", v45["sec_rh3_D4_b"])
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p56_numeros.csv"))
    for k, v in NUM.items():
        if k.startswith("perm") or k.startswith("conj_") and k.endswith(("05", "10", "_m")):
            print(f"  {k:26s} {v: .4f}")


if __name__ == "__main__":
    main()
