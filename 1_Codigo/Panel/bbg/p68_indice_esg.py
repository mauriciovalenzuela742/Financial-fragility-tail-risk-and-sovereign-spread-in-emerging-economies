# -*- coding: utf-8 -*-
"""
p68_indice_esg.py -- índices del preregistro 9 (4_Redaccion/preregistro_esg.md, sección 2).

  G (principal): primer componente principal de los seis WGI estandarizados en el panel país-año
    2003-2025 de las 13 economías; orientado a mayor = mejor gobernanza.
  ESG (réplica de Barneche, Grezzi y Panario, 2024): variables orientadas a mayor = mejor (1/x para
    intensidad energética, CO2 y agotamiento; 100 - x para empleo vulnerable), ln(x) o ln(x + 1 + |mín|) si
    hay valores <= 0, estandarización, PCA por dimensión con el conjunto final de ORT (E sin bosque ni agua),
    primer componente orientado y ESG = sum_d (lambda_d / sum lambda) C_d.
  Robustez: pesos iguales entre dimensiones (ESG_eq); cargas ajustadas solo con 2003-2012 (G_pre, ESG_pre).
  Argentina se proyecta con las cargas de las 13 (no entra al ajuste).
  KMO por variable y global (numpy). Fracción de la varianza dentro del país (panel país-año).

Salidas: bbg/esg_indice_anual_bbg.csv, bbg/esg_trimestral_bbg.csv (escalón con un año de rezago de
publicación; sufijo _int = interpolación) y bbg/paper_p68_numeros.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p67_datos_esg as p67

OUT_A = os.path.join(HERE, "esg_indice_anual_bbg.csv")
OUT_Q = os.path.join(HERE, "esg_trimestral_bbg.csv")
OUT_N = os.path.join(HERE, "paper_p68_numeros.csv")
NUM = {}
FIT = (2003, 2025)
PANEL13 = [c for c in p67.ISO3 if c != "argentina"]

DIM = {"E": ["renovable", "co2", "recursos", "energia"],          # conjunto final de ORT (sin bosque ni agua)
       "S": ["matricula", "salud", "vida", "paridad", "mujer_hombre", "vulnerable"],
       "G": ["voz", "estabilidad", "corrupcion", "ley", "efectividad", "regulacion"]}
INVERSA = ("energia", "co2", "recursos", "agua")
EXTRA = ["libertad", "crecimiento", "apertura"]


def num(k, v):
    NUM[k] = float(v)


def orientar(a):
    a = a.copy()
    for c in INVERSA:
        a[c] = 1.0 / a[c].where(a[c] != 0)
    a["vulnerable"] = 100.0 - a["vulnerable"]
    return a


def log_ort(s):
    return np.log(s + 1 + abs(s.min())) if (s <= 0).any() else np.log(s)


def kmo(R):
    Ri = np.linalg.inv(R)
    P = -Ri / np.sqrt(np.outer(np.diag(Ri), np.diag(Ri)))
    np.fill_diagonal(P, 0); R0 = R.copy(); np.fill_diagonal(R0, 0)
    r2, p2 = (R0 ** 2), (P ** 2)
    return r2.sum(0) / (r2.sum(0) + p2.sum(0)), r2.sum() / (r2.sum() + p2.sum())


def pca1(X, pref, cols):
    """X: DataFrame estandarizado sin faltantes. Devuelve (cargas, valor propio, media, sd) del 1er componente."""
    R = np.corrcoef(X.values, rowvar=False)
    val, vec = np.linalg.eigh(R)
    v = vec[:, -1] * (1 if vec[:, -1].sum() >= 0 else -1)
    k_var, k_tot = kmo(R)
    num(f"{pref}_n", len(X)); num(f"{pref}_eig1", val[-1]); num(f"{pref}_var1", val[-1] / val.sum())
    num(f"{pref}_kmo", k_tot)
    for c, l, kv in zip(cols, v, k_var):
        num(f"{pref}_carga_{c}", l); num(f"{pref}_kmo_{c}", kv)
    return v, val[-1]


def puntaje(a, cols, ventana, pref, usar_log):
    """Estandariza con la ventana de ajuste (13 economías), PCA y puntaje para todas las filas."""
    Z = a[cols].copy()
    if usar_log:
        for c in cols:
            Z[c] = log_ort(Z[c])
    m = a["country"].isin(PANEL13) & a["year"].between(*ventana)
    mu, sd = Z[m].mean(), Z[m].std()
    Z = (Z - mu) / sd
    ok = m & Z.notna().all(axis=1)
    v, eig = pca1(Z[ok], pref, cols)
    return Z.values @ v, eig


def frac_dentro(a, col):
    x = a[a["country"].isin(PANEL13) & a["year"].between(*FIT)][["country", col]].dropna()
    tot = x[col].var(ddof=0)
    dentro = (x[col] - x.groupby("country")[col].transform("mean")).var(ddof=0)
    return dentro / tot


def main():
    a = pd.read_csv(p67.OUT)
    a = orientar(a)
    out = a[["country", "iso3", "year"]].copy()
    for ventana, suf in ((FIT, ""), ((2003, 2012), "_pre")):
        # G principal: WGI estandarizados, sin logaritmo
        out[f"G{suf}"], _ = puntaje(a, DIM["G"], ventana, f"G{suf}", usar_log=False)
        # réplica ORT por dimensión
        comp, eig = {}, {}
        for d, cols in DIM.items():
            comp[d], eig[d] = puntaje(a, cols, ventana, f"ORT{suf}_{d}", usar_log=True)
            out[f"C_{d}{suf}"] = comp[d]
        w = {d: eig[d] / sum(eig.values()) for d in DIM}
        for d in DIM:
            num(f"ORT{suf}_peso_{d}", w[d])
        out[f"ESG{suf}"] = sum(w[d] * comp[d] for d in DIM)
        if not suf:
            out["ESG_eq"] = sum(comp[d] for d in DIM) / 3
    # marcas de arrastre
    arr = {d: a[[f"{c}_arr" for c in cols]].max(axis=1) for d, cols in DIM.items()}
    out["G_arr"] = arr["G"]
    out["ESG_arr"] = pd.concat(arr.values(), axis=1).max(axis=1)
    for c in EXTRA:
        out[c] = a[c]; out[f"{c}_arr"] = a[f"{c}_arr"]
    for c in ("G", "ESG", "C_E", "C_S", "C_G", "libertad"):
        num(f"frac_dentro_{c}", frac_dentro(out, c))
    num("corr_G_libertad", out[out["country"].isin(PANEL13)][["G", "libertad"]].corr().iloc[0, 1])
    num("corr_G_ESG", out[out["country"].isin(PANEL13)][["G", "ESG"]].corr().iloc[0, 1])
    out.to_csv(OUT_A, index=False)

    cols = ["G", "ESG", "ESG_eq", "C_E", "C_S", "C_G", "G_pre", "ESG_pre", "libertad", "crecimiento",
            "apertura", "G_arr", "ESG_arr"]
    qe = p67.a_trimestral(out, cols, "escalon")
    qi = p67.a_trimestral(out, ["G", "ESG"], "interp").rename(columns={"G": "G_int", "ESG": "ESG_int"})
    q = qe.merge(qi, on=["country", "quarter"], how="left")
    q.to_csv(OUT_Q, index=False)
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT_N)

    print(f"-> {OUT_A}\n-> {OUT_Q}\n-> {OUT_N}")
    for d in DIM:
        print(f"  {d}: n={NUM[f'ORT_{d}_n']:.0f}  valor propio {NUM[f'ORT_{d}_eig1']:.3f} "
              f"({NUM[f'ORT_{d}_var1']:.1%})  KMO {NUM[f'ORT_{d}_kmo']:.3f}  peso {NUM[f'ORT_peso_{d}']:.3f}")
        print("     cargas:", ", ".join(f"{c} {NUM[f'ORT_{d}_carga_{c}']:.3f}" for c in DIM[d]))
    print(f"  G principal: valor propio {NUM['G_eig1']:.3f} ({NUM['G_var1']:.1%}), KMO {NUM['G_kmo']:.3f}")
    print("  fracción de la varianza dentro del país:",
          ", ".join(f"{c} {NUM[f'frac_dentro_{c}']:.2f}" for c in ("G", "ESG", "C_E", "C_S", "C_G", "libertad")))
    print(f"  corr(G, libertad) {NUM['corr_G_libertad']:.2f}; corr(G, ESG) {NUM['corr_G_ESG']:.2f}")


if __name__ == "__main__":
    main()
