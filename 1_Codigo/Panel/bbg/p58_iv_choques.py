# -*- coding: utf-8 -*-
"""
p58_iv_choques.py -- N1 del preregistro 5 (4_Redaccion/preregistro_n1n2.md, commit 7df0427): choques de
términos de intercambio de materias primas como instrumento del riesgo de cola de mediano plazo, y Holm de
la familia {N2-H1, N1-H1}.

  Instrumento: Z_{t-1} = CTOT_{t-1} - CTOT_{t-5} (ctot_shock_bbg.csv: índice de precios de materias primas
  ponderado por la canasta exportadora de 1998-2003), estandarizado.
  N1-H1: ln EMBI = b1 J + b2 T + d M + psi T*M + EF país + EF tiempo, con T = D4_{t-1} y T*M endógenas,
  instrumentos Z y Z*M (exactamente identificado); J*T se omite. 2SLS tras la transformación within
  bidireccional (proyección exacta sobre las indicadoras); errores de Driscoll-Kraay.
  Fuerza: F condicional de Sanderson-Windmeijer (2016) por endógena, con varianza agrupada por país;
  débil si alguno < 10 (entonces N1-H1 entra a la familia con p = 1).
  p unilateral de psi: bootstrap de pares por país (999), fracción de (psi* - psi) >= psi.
  Secundarias: forma reducida (Z*M < 0), primera etapa (Z sobre D4, < 0), T = D_{t-1}, proyecciones locales
  con instrumento a h = 0, 4 y 8.
Salida: bbg/paper_p58_numeros.csv.
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
B = int(os.environ.get("P58_B", 999))


def num(k, v):
    NUM[k] = float(v)


def aniquilador(x):
    D = np.column_stack([pd.get_dummies(x["g"]).values, pd.get_dummies(x["quarter"]).values]).astype(float)
    return np.eye(len(x)) - D @ np.linalg.pinv(D)


def preparar(tcol):
    d, raw = p42.preparar()
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    c = pd.read_csv(os.path.join(HERE, "ctot_shock_bbg.csv"))
    q = pd.PeriodIndex(c["quarter"], freq="Q"); c["_qn"] = q.year * 4 + q.quarter
    c = c.sort_values(["country", "_qn"])
    c["Z4"] = c.groupby("country")["CTOT_shock"].diff(4)
    d = d.merge(p14.shift(c, "Z4", 1, "Z_l1"), on=["country", "_qn"], how="left")
    for h in (4, 8):
        d = d.merge(p14.shift(raw, "ln_EMBI", -h, f"ln_EMBI_f{h}"), on=["country", "_qn"], how="left")
    d["ln_EMBI_f0"] = d["ln_EMBI"]
    x = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", tcol, "DEBT_l4", "Z_l1"]).reset_index(drop=True)
    x["J"] = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean()
    x["T"] = x[tcol] - x[tcol].mean()
    x["M"] = (x["DEBT_l4"] - x["DEBT_l4"].mean()) / x["DEBT_l4"].std()
    x["TM"] = x["T"] * x["M"]
    x["Z"] = (x["Z_l1"] - x["Z_l1"].mean()) / x["Z_l1"].std()
    x["ZM"] = x["Z"] * x["M"]
    x["g"] = x["country"]
    return x


def tsls(x, y="ln_EMBI", exo=("J", "M"), endo=("T", "TM"), inst=("Z", "ZM"), dk=True):
    x = x.dropna(subset=[y]).reset_index(drop=True)
    A = aniquilador(x)
    Y = A @ x[y].values; Xe = A @ x[list(exo)].values; Xn = A @ x[list(endo)].values; Zi = A @ x[list(inst)].values
    X = np.column_stack([Xn, Xe]); W = np.column_stack([Zi, Xe])
    Pw = W @ np.linalg.pinv(W.T @ W) @ W.T
    Xh = Pw @ X
    b = np.linalg.solve(Xh.T @ X, Xh.T @ Y)
    out = dict(b=b, n=len(x), x=x)
    if dk:
        e = Y - X @ b
        Ainv = np.linalg.inv(Xh.T @ Xh)
        h = Xh * e[:, None]
        tq = x["quarter"].values; uq = np.unique(tq)
        S = np.array([h[tq == q].sum(0) for q in uq])
        L = int(np.floor(4 * (len(uq) / 100) ** (2 / 9)))
        Om = S.T @ S
        for l in range(1, L + 1):
            G = S[l:].T @ S[:-l]; Om += (1 - l / (L + 1)) * (G + G.T)
        V = Ainv @ Om @ Ainv
        out["se"] = np.sqrt(np.diag(V))
    return out


def f_sw(x, exo=("J", "M"), endo=("T", "TM"), inst=("Z", "ZM")):
    """F condicional de Sanderson-Windmeijer por endógena, con varianza agrupada por país."""
    A = aniquilador(x)
    Xe = A @ x[list(exo)].values; Zi = A @ x[list(inst)].values
    W = np.column_stack([Zi, Xe]); L, K = len(inst), len(endo)
    res = {}
    for j, en in enumerate(endo):
        otros = [e for e in endo if e != en]
        # 2SLS de X_j sobre X_{-j} instrumentadas por Z
        Xj = A @ x[en].values; Xo = A @ x[otros].values
        Xr = np.column_stack([Xo, Xe])
        Pw = W @ np.linalg.pinv(W.T @ W) @ W.T
        Xh = Pw @ Xr
        dlt = np.linalg.solve(Xh.T @ Xr, Xh.T @ Xj)
        eps = Xj - Xr @ dlt
        # regresión de eps sobre Z (y exógenas), Wald agrupado por país sobre los coeficientes de Z
        g = np.linalg.lstsq(W, eps, rcond=None)[0]; u = eps - W @ g
        WWi = np.linalg.inv(W.T @ W)
        meat = np.zeros((W.shape[1], W.shape[1]))
        for c in x["g"].unique():
            m = (x["g"] == c).values; s = W[m].T @ u[m]; meat += np.outer(s, s)
        G = x["g"].nunique(); n = len(x)
        V = WWi @ meat @ WWi * (G / (G - 1)) * ((n - 1) / (n - W.shape[1]))
        gz = g[:L]; Vz = V[:L, :L]
        res[en] = float(gz @ np.linalg.solve(Vz, gz) / (L - K + 1))
    return res


def boot_pares(x, psi, rng):
    paises = x["country"].unique(); grupos = {c: x[x["country"] == c] for c in paises}; out = []
    for _ in range(B):
        s = rng.choice(paises, len(paises))
        xb = pd.concat([grupos[c].assign(g=f"{c}_{k}") for k, c in enumerate(s)], ignore_index=True)
        try:
            out.append(tsls(xb, dk=False)["b"][1])
        except np.linalg.LinAlgError:
            continue
    out = np.array(out)
    return float(np.mean(out - psi >= psi)), float(out.std())


def bloque(tcol, pref, principal=False):
    x = preparar(tcol)
    num(f"{pref}_N", len(x)); num(f"{pref}_paises", x["country"].nunique())
    r = tsls(x)
    for k, nm in enumerate(("T", "TM", "J", "M")):
        num(f"{pref}_{nm}", r["b"][k]); num(f"{pref}_{nm}_se_dk", r["se"][k])
    psi = float(r["b"][1])
    F = f_sw(x)
    num(f"{pref}_F_T", F["T"]); num(f"{pref}_F_TM", F["TM"])
    debil = min(F.values()) < 10
    num(f"{pref}_debil", float(debil))
    # primera etapa y forma reducida (secundarias)
    fs = tsls(x, y="T", exo=("J", "M", "Z", "ZM"), endo=(), inst=())
    num(f"{pref}_fs_Z", fs["b"][2]); num(f"{pref}_fs_Z_se_dk", fs["se"][2])
    rf = tsls(x, y="ln_EMBI", exo=("J", "M", "Z", "ZM"), endo=(), inst=())
    num(f"{pref}_rf_ZM", rf["b"][3]); num(f"{pref}_rf_ZM_se_dk", rf["se"][3])
    num(f"{pref}_rf_Z", rf["b"][2]); num(f"{pref}_rf_Z_se_dk", rf["se"][2])
    if principal:
        p, se_b = boot_pares(x, psi, np.random.default_rng(58))
        num(f"{pref}_p_uni", p); num(f"{pref}_se_boot", se_b)
        pos = 0
        for c in sorted(x["country"].unique()):
            bc = tsls(x[x["country"] != c].reset_index(drop=True), dk=False)["b"][1]
            num(f"{pref}_sin_{c}", bc); pos += int(bc > 0)
        num(f"{pref}_loo_pos", pos); num(f"{pref}_loo_n", x["country"].nunique())
        num(f"{pref}_firme_criterio", float(not debil and psi > 0 and p < 0.05 and pos == x["country"].nunique()))
        for h in (0, 4, 8):
            rh = tsls(x, y=f"ln_EMBI_f{h}")
            num(f"{pref}_lp{h}_psi", rh["b"][1]); num(f"{pref}_lp{h}_se_dk", rh["se"][1]); num(f"{pref}_lp{h}_N", rh["n"])
        return (1.0 if debil else p)
    return None


def main():
    p1 = bloque("D4_l1", "N1", principal=True)
    bloque("D_l1", "N1d1")
    # familia {N2-H1, N1-H1}
    v57 = pd.read_csv(os.path.join(HERE, "paper_p57_numeros.csv"), index_col=0)["valor"]
    ps = {"N2-H1": float(v57["N2_p_uni"]), "N1-H1": p1}
    orden = sorted(ps.items(), key=lambda z: z[1]); m = len(orden); acum = 0.0
    for r, (k, p) in enumerate(orden):
        acum = max(acum, min(1.0, (m - r) * p)); num(f"familia5_{k}_holm", acum); num(f"familia5_{k}_p", p)
    num("familia5_N2_firme", float(NUM["familia5_N2-H1_holm"] < 0.05 and v57["N2_replica"] == 1))
    num("familia5_N1_firme", float(NUM["familia5_N1-H1_holm"] < 0.05 and NUM["N1_firme_criterio"] == 1))
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p58_numeros.csv"))
    for k, v in NUM.items():
        if "_sin_" not in k:
            print(f"  {k:26s} {v: .4f}")


if __name__ == "__main__":
    main()
