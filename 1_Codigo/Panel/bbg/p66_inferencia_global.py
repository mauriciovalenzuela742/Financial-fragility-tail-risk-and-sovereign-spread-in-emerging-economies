# -*- coding: utf-8 -*-
"""
p66_inferencia_global.py -- corrección por comparaciones múltiples sobre las 23 hipótesis primarias de los
ocho preregistros (acción 2 de 4_Redaccion/evaluacion_sexta.md). Extiende la familia conjunta de p56 (14
hipótesis de los preregistros 1-4) con:
    preregistro 5 (7df0427): N2-H1 réplica externa, N1-H1 instrumento            (paper_p58, familia5)
    preregistro 6 (90f0adf): M6-H1 deuda x riesgo de cola en pb                   (paper_p59)
    preregistro 7 (d968986): Q1-H1, Q3-H1, Q3-H2                                  (paper_p60, paper_p62)
    preregistro 8 (fc920b3): Q2-H1, Q4-H1, Q5-H1                                  (paper_p61, p63, p65)
Holm (FWER) y Benjamini-Yekutieli (FDR), válidos con cualquier dependencia; Benjamini-Hochberg como
referencia. Usa el p unilateral que reportó cada preregistro. No puede agregar hallazgos: solo quitarlos.

Salida: bbg/paper_p66_numeros.csv.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pandas as pd

NUM = {}


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


def main():
    print("p66: corrección sobre las hipótesis primarias de los ocho preregistros")
    v56 = leer("paper_p56_numeros.csv")
    ps = {k[5:-2]: v56[k] for k in v56.index if k.startswith("conj_") and k.endswith("_p")}
    assert len(ps) == 14, len(ps)
    v58, v59 = leer("paper_p58_numeros.csv"), leer("paper_p59_numeros.csv")
    v60, v61, v62 = leer("paper_p60_numeros.csv"), leer("paper_p61_numeros.csv"), leer("paper_p62_numeros.csv")
    v63, v65 = leer("paper_p63_numeros.csv"), leer("paper_p65_numeros.csv")
    ps.update({"N2-H1": v58["familia5_N2-H1_p"], "N1-H1": v58["familia5_N1-H1_p"], "M6-H1": v59["m6_p_uni"],
               "Q1-H1": v60["q1h1_p"], "Q3-H1": v62["q3h1_c3_p"], "Q3-H2": v62["q3h2_dm_p"],
               "Q2-H1": v61["q2h1_p"], "Q4-H1": v63["q4h1_p"], "Q5-H1": v65["q5h1_p_uni"]})
    h, q_bh, q_by = holm(ps), bh(ps), bh(ps, by=True)
    filas = []
    for k in sorted(ps, key=ps.get):
        num(f"glob_{k}_p", ps[k]); num(f"glob_{k}_holm", h[k]); num(f"glob_{k}_bh", q_bh[k]); num(f"glob_{k}_by", q_by[k])
        filas.append((k, ps[k], h[k], q_bh[k], q_by[k]))
    num("glob_m", len(ps))
    num("glob_holm05", sum(v < 0.05 for v in h.values())); num("glob_by05", sum(v < 0.05 for v in q_by.values()))
    num("glob_bh05", sum(v < 0.05 for v in q_bh.values())); num("glob_bh10", sum(v < 0.10 for v in q_bh.values()))
    print(pd.DataFrame(filas, columns=["hipótesis", "p", "Holm", "BH", "BY"]).round(3).to_string(index=False))
    print(f"  bajo 0,05: Holm {int(NUM['glob_holm05'])}, BH {int(NUM['glob_bh05'])}, BY {int(NUM['glob_by05'])} de {len(ps)}")
    out = os.path.join(HERE, "paper_p66_numeros.csv")
    pd.Series(NUM).rename("valor").to_csv(out, header=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
