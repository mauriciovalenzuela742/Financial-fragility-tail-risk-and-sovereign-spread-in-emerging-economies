# -*- coding: utf-8 -*-
"""
p65_deuda_pb_mensual.py -- Q5 del preregistro 8 (4_Redaccion/preregistro_quant2.md, commit fc920b3): la
interacción deuda x riesgo de cola en puntos básicos, con frecuencia mensual (la predicción del modelo de
límite fiscal, p59: +91 pb por d.e. de deuda).

    s_{i,m} (pb) = a_i + l_m + a1 N_{i,m-1} + a2 zDeuda_{q-4} + a3 N_{i,m-1} x zDeuda_{q-4} + e
N: nowcast mensual del riesgo de cola (p64), centrado; zDeuda estandarizada. Desde 2015-01.
Q5-H1: a3 > 0, wild cluster bootstrap por país (Webb, 999), unilateral; condición: a3 > 0 en >= 10 de 13
exclusiones. Si Q6 no valida, Q5 es exploratoria.

Salida: bbg/paper_p65_numeros.csv (y la corrección de Holm de la familia Q2-H1, Q4-H1, Q5-H1).
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd

import p32_aporte_riesgo_cola as p32
import p60_senal_dd as p60
import p61_valor_razonable as p61
import p62_cola_cambios as p62
from causal_core import demean2

NUM = {}


def num(k, v):
    NUM[k] = float(v)
    return v


def datos():
    x = p61.fundamentos()
    n = pd.read_csv(os.path.join(HERE, "gar_nowcast_mensual.csv"))
    n["month"] = pd.PeriodIndex(n["month"], freq="M")
    x = x.merge(n[["country", "month", "N"]], on=["country", "month"], how="left")
    g = x.groupby("country")
    ok = (x["month"] - g["month"].shift(1)).apply(lambda d: getattr(d, "n", np.nan)) == 1
    x["N_l1"] = np.where(ok, g["N"].shift(1), np.nan)
    x["dN_l1"] = np.where(ok, g["N"].shift(1) - g["N"].shift(2), np.nan)
    x["ds"] = x["s"] - x["s_l1"]
    return x


def preparar(x, tail="N_l1", y="s", excluir=()):
    d = x[(x["month"] >= p60.INICIO) & ~x["country"].isin(excluir)].dropna(subset=[y, tail, "debt_q4"]).copy()
    d["T_c"] = d[tail] - d[tail].mean()
    d["zD"] = (d["debt_q4"] - d["debt_q4"].mean()) / d["debt_q4"].std()
    d["TxD"] = d["T_c"] * d["zD"]
    return d


def ajuste(d, y="s"):
    regs = ["T_c", "zD", "TxD"]
    Y = demean2(d, [y], iters=40)[y].values
    X = demean2(d, regs, iters=40).values
    return np.linalg.lstsq(X, Y, rcond=None)[0]


def prueba(x, pref, tail="N_l1", y="s", excluir=(), exclusiones=False):
    d = preparar(x, tail, y, excluir)
    b = ajuste(d, y)
    pw = p32.wild(d, y, ["T_c", "zD", "TxD"], "TxD")
    p_uni = pw / 2 if b[2] > 0 else 1 - pw / 2
    num(f"{pref}_a1", b[0]); num(f"{pref}_a2", b[1]); num(f"{pref}_a3", b[2])
    num(f"{pref}_p_uni", p_uni); num(f"{pref}_N", len(d))
    txt = f"  {pref:<14} N={len(d)}  a1 {b[0]:+.2f}  a3 {b[2]:+.3f} (wild uni {p_uni:.3f})"
    if exclusiones:
        pos = sum(ajuste(preparar(x, tail, y, excluir + (c,)), y)[2] > 0 for c in sorted(d["country"].unique()))
        num(f"{pref}_exclusiones_pos", pos)
        txt += f"  positiva en {pos} de {d['country'].nunique()} exclusiones"
    print(txt)
    return p_uni


def main():
    print("p65: Q5, deuda x riesgo de cola en puntos básicos, mensual")
    x = datos()
    p5 = prueba(x, "q5h1", exclusiones=True)
    prueba(x, "cambios", tail="dN_l1", y="ds")
    x["ln_s_"] = np.log(x["s"]); prueba(x, "logaritmos", y="ln_s_")
    prueba(x, "D_oficial", tail="D_q2")
    prueba(x, "sin_turquia", excluir=("turkey",))
    # Holm de la familia del preregistro 8
    p61n = pd.read_csv(os.path.join(HERE, "paper_p61_numeros.csv"), index_col=0)["valor"]
    p63n = pd.read_csv(os.path.join(HERE, "paper_p63_numeros.csv"), index_col=0)["valor"]
    p64n = pd.read_csv(os.path.join(HERE, "paper_p64_numeros.csv"), index_col=0)["valor"]
    adj = p62.holm(np.array([p61n["q2h1_p"], p63n["q4h1_p"], p5]))
    for k, v in zip(("q2h1", "q4h1", "q5h1"), adj):
        num(f"holm_{k}", v)
    num("q2h1_pasa", float(adj[0] < 0.05 and p61n["vida_media_meses"] < 6))
    num("q4h1_pasa", float(adj[1] < 0.05))
    num("q5h1_pasa", float(adj[2] < 0.05 and NUM["q5h1_exclusiones_pos"] >= 10 and p64n["q6_valida"] == 1))
    print(f"  Holm: Q2-H1 {adj[0]:.3f}  Q4-H1 {adj[1]:.3f}  Q5-H1 {adj[2]:.3f}  (pasan: "
          f"{int(NUM['q2h1_pasa'])}, {int(NUM['q4h1_pasa'])}, {int(NUM['q5h1_pasa'])}; Q6 valida: {int(p64n['q6_valida'])})")
    out = os.path.join(HERE, "paper_p65_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
