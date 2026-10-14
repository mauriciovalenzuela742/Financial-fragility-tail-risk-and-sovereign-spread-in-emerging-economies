# -*- coding: utf-8 -*-
"""
x7_sim_kernels.py -- EXPERIMENTO: tamaño, potencia y error de la varianza de cada kernel.

Reutiliza, sin modificarlos, los procesos generadores de p29_simulacion_v2.py:
  B  remuestreo por fecha con AR(2) por país (conserva la dependencia entre países), X fijo
  C  VAR de panel con retroalimentación (se regeneran spread, fragilidad y riesgo de cola)
en niveles y en primeras diferencias, para la fragilidad (b1) y el riesgo de cola (b2).

=========================== DECLARADO ANTES DE SIMULAR (2026-10-13) ===========================
Métodos (todos Driscoll-Kraay; ver x6_kernels_hac.py): bt_3 (el de la tesis), bt_and, bt_nw, qs_and,
qs_nw, pz_and, bt_pw, qs_pw; valores críticos fixed-b para bt_and y qs_and; y un barrido de ancho
fijo S = 2, 4, 8, 12, 16, 24 para Bartlett y QS con valores críticos normales y fixed-b.
Medidas: tamaño al 5 %; potencia frente al efecto estimado; potencia ajustada por tamaño (valor
crítico empírico); razón error estándar medio / desviación verdadera; sesgo y error cuadrático medio
relativo del estimador de la varianza (el criterio de optimalidad de Andrews, 1991).
Esperado: en diferencias todos coinciden; en niveles QS con ancho automático reduce el sobre-rechazo
de bt_3 pero no lo elimina, y supera a Bartlett con el mismo selector por poco.
=================================================================================================
Salida: experimentos/x7_sim_kernels.csv. No se integra a ningún documento.
"""
import os
import time

import numpy as np
import pandas as pd

import x0_comun as x0
import x6_kernels_hac as x6
import p29_simulacion_v2 as p29

S_SIM = int(os.environ.get("JLOSS_SIM", 1000))
BARRIDO = (2, 4, 8, 12, 16, 24)
NUM = {}
BASE = list(x6.METODOS)
SWEEP = [f"{k}_S{s}" for k in ("bt", "qs") for s in BARRIDO]
TODOS = BASE + SWEEP


def num(k, v):
    NUM[k] = float(v)
    return v


def una(P, Xw, yw, ki):
    """coeficiente, varianzas (ya escaladas) y anchos de todos los métodos."""
    XtXi = np.linalg.inv(Xw.T @ Xw)
    b = XtXi @ (Xw.T @ yw); e = yw - Xw @ b
    u = P.It @ ((Xw @ XtXi[ki]) * e)
    v = x6.varianzas(u); g = x6.autocov(u)
    out = [b[ki]] + [max(v[m][0], 0.0) * P.escala for m in BASE]
    out += [max(x6.lrv(g, k, s), 0.0) * P.escala for k in ("bt", "qs") for s in BARRIDO]
    out += [v[m][1] for m in BASE]
    return np.array(out)


def resumir(dgp, spec, lab, R0, R1, centro, T):
    """R0, R1: matrices (sim x columnas) bajo H0 y H1; centro: valor contra el que se contrasta H0."""
    pref = f"{dgp}_{spec}_{lab}"
    b0, b1 = R0[:, 0], R1[:, 0]
    V = b0.var()
    num(f"{pref}_sd_verdadera", np.sqrt(V)); num(f"{pref}_media_H0", b0.mean()); num(f"{pref}_centro", centro)
    nm = len(TODOS)
    for j, m in enumerate(TODOS):
        v0, v1 = R0[:, 1 + j], R1[:, 1 + j]
        t0 = np.abs(b0 - centro) / np.sqrt(np.clip(v0, 1e-30, None))
        t1 = np.abs(b1) / np.sqrt(np.clip(v1, 1e-30, None))
        num(f"{pref}_{m}_tamano", (t0 > 1.96).mean())
        num(f"{pref}_{m}_potencia", (t1 > 1.96).mean())
        num(f"{pref}_{m}_potencia_ajustada", (t1 > np.quantile(t0, 0.95)).mean())
        num(f"{pref}_{m}_ee_sobre_sd", np.sqrt(v0).mean() / np.sqrt(V))
        num(f"{pref}_{m}_var_sesgo_rel", v0.mean() / V - 1.0)
        num(f"{pref}_{m}_var_ecm_rel", ((v0 / V - 1.0) ** 2).mean())
        # valores críticos fixed-b
        if m in ("bt_and", "qs_and"):
            Sj = R0[:, 1 + nm + BASE.index(m)]; S1 = R1[:, 1 + nm + BASE.index(m)]
            cv0 = np.array([x6.fixedb_cv(m[:2], s / T) for s in Sj]); cv1 = np.array([x6.fixedb_cv(m[:2], s / T) for s in S1])
            num(f"{pref}_{m}_fb_tamano", (t0 > cv0).mean()); num(f"{pref}_{m}_fb_potencia", (t1 > cv1).mean())
        if m in SWEEP:
            cv = x6.fixedb_cv(m[:2], float(m.split("_S")[1]) / T)
            num(f"{pref}_{m}_fb_tamano", (t0 > cv).mean()); num(f"{pref}_{m}_fb_potencia", (t1 > cv).mean())
        if m in BASE and m != "bt_3":
            Sj = R0[:, 1 + nm + BASE.index(m)]
            num(f"{pref}_{m}_ancho_medio", Sj.mean()); num(f"{pref}_{m}_ancho_p90", np.quantile(Sj, 0.9))


def main():
    t0 = time.time()
    print(f"x7: S={S_SIM}", flush=True)
    assert not x0.NIV, "la simulación se corre en la forma logarítmica (la de p29)"
    d, dd, fd, m0, paises, q0, Tg, E = p29.preparar()
    PB = {spec: p29.preparar_B(E[spec], Tg) for spec in ("niv", "fd")}
    PC = p29.preparar_C(paises)
    ref = pd.read_csv(os.path.join(x0.BBG, "paper_inferencia_v2_numeros.csv"), index_col=0)["valor"]
    rng = np.random.default_rng(13)
    ACC = {}
    L = p29.QUEMA + Tg
    for s in range(S_SIM):
        for spec in ("niv", "fd"):
            e = E[spec]; P = e["P"]; pb = PB[spec]
            es = p29.simular_B(pb, p29.fechas_bloque(rng, L, pb["falta"], pb["obs"])[0], Tg)
            for c, caso in enumerate(pb["casos"]):
                ys = caso["fit"] + P.M @ es[c][e["pos"], P.ci]
                ACC.setdefault(("B", spec, caso["hip"], ("b1", "b2")[caso["ki"]]), []).append(una(P, e["Xw"], ys, caso["ki"]))
        fin = p29.fechas_bloque(rng, L, PC["falta"], PC["obs"])
        Zs = p29.simular_C(PC["var"]["C"], fin, Tg)
        ms = [p29.muestra_C(Zs[c], E) for c in range(3)]
        for spec in ("niv", "fd"):
            P = E[spec]["P"]
            for ki, lab in ((0, "b1"), (1, "b2")):
                Xa, ya = ms[0][spec]; Xn, yn = ms[ki + 1][spec]
                ACC.setdefault(("C", spec, "pot", lab), []).append(una(P, Xa, ya, ki))
                ACC.setdefault(("C", spec, "tam", lab), []).append(una(P, Xn, yn, ki))
        if (s + 1) % 100 == 0:
            print(f"   simulación {s + 1}/{S_SIM}  ({time.time() - t0:.0f} s)", flush=True)
    for dgp in ("B", "C"):
        for spec in ("niv", "fd"):
            T = E[spec]["P"].T
            for lab in ("b1", "b2"):
                R0 = np.array(ACC[(dgp, spec, "tam", lab)]); R1 = np.array(ACC[(dgp, spec, "pot", lab)])
                centro = 0.0 if dgp == "B" else float(ref.get(f"dgpC_{spec}_centro_{lab}", R0[:, 0].mean()))
                resumir(dgp, spec, lab, R0, R1, centro, T)
    num("S", S_SIM)
    x0.guardar(NUM, "x7_sim_kernels")
    # tabla corta en pantalla
    for dgp in ("B", "C"):
        for spec in ("niv", "fd"):
            print(f"\n  DGP {dgp}, {spec}: tamaño b1/b2 | potencia ajustada b1/b2 | ee/sd b1/b2 | ECM var b1/b2")
            for m in BASE + ["bt_S8", "qs_S8", "bt_S16", "qs_S16"]:
                f = lambda k: " / ".join(f"{NUM[f'{dgp}_{spec}_{l}_{m}_{k}']:.3f}" for l in ("b1", "b2"))
                print(f"   {m:8s} {f('tamano')} | {f('potencia_ajustada')} | {f('ee_sobre_sd')} | {f('var_ecm_rel')}")


if __name__ == "__main__":
    main()
