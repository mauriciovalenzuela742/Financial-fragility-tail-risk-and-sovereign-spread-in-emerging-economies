# -*- coding: utf-8 -*-
"""
p33_simultaneidad_precedencia_tost.py -- tres pruebas pedidas por la evaluación experta del 21-oct-2026
(4_Redaccion/evaluacion_experta.md, mejoras A2, A3 y B7). Se corren exactamente estas y se reportan
todas, sea cual sea el resultado:

  1. Simultaneidad con una nula que conserva el calendario común. La permutación de p32 desplaza el
     indicador de D por separado en cada país: conserva la persistencia, pero rompe la alineación con
     el calendario, de modo que su nula ignora que los dos riesgos responden a choques comunes. Aquí el
     indicador de D se permuta ENTRE PAÍSES DENTRO DE CADA TRIMESTRE (4 999 réplicas): conserva
     exactamente cuántas economías tienen el riesgo de cola alto en cada trimestre. También fuera de
     los trimestres de crisis y por período.
  2. Precedencia de la fragilidad sobre el riesgo de cola, con las pruebas que el capítulo exige a los
     demás resultados: (a) la regresión cruzada de p32 (D_t sobre D_{t-1} y ln JLoss_{t-1}, EF de país
     y de tiempo) sin cada país; (b) con el GaR reconstruido sin el bloque bursátil del FCI
     (gar_insample_noSTX.csv), comparado con su par dentro de la muestra (gar_insample_base.csv),
     porque el FCI y JLoss comparten precios accionarios; (c) con dos a cuatro rezagos de cada
     riesgo (suma de los coeficientes cruzados y Wald conjunto).
  3. Equivalencia (TOST) para la interacción: el límite superior del IC 90 % de b3 es la mayor
     amplificación que se rechaza al 5 % en un contraste unilateral; se traduce, como en p32.bandas, a
     fracción de la suma de las dos asociaciones con ambos riesgos una d.e. within-país sobre su media,
     con DK, cluster por país (t con G-1 g.l.) y wild bootstrap invertido al 10 %. Se reporta además
     el efecto mínimo detectable al 5 % con potencia de 80 %.

Simplificaciones (declaradas):
  - La permutación dentro del trimestre no conserva la persistencia de cada serie (la de p32 sí): las
    dos nulas son complementarias, no sustitutas.
  - El GaR sin bloque bursátil existe solo en su versión dentro de la muestra (no en pseudo-tiempo
    real), por lo que se compara contra la versión base dentro de la muestra.
  - No hay prueba de fechado dentro del trimestre: el FCI es mensual pero el GaR es trimestral, y
    JLoss se calcula con el cierre del trimestre.

Salida: bbg/paper_p33_numeros.csv (o _nivlag). Reutiliza p13, p14 y p32.
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

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
R_PERM = 4999
GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
NUM = p32.NUM          # mismo diccionario: p32.num escribe aquí


def num(k, v):
    NUM[k] = float(v)


# ================================================================ 1. simultaneidad, nula de calendario
def indicadores(d):
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"]).sort_values(["country", "_qn"]).copy()
    for col, nom in (("ln_JLoss_l1", "AJ"), ("D_l1", "AD")):
        dd[nom] = (dd[col] > dd.groupby("country")[col].transform(lambda x: x.quantile(2 / 3))).astype(float)
    dd["crisis"] = dd["quarter"].isin(p13.CRISIS_BAT)
    dd["anio"] = dd["t"].dt.year
    return dd


def bloque_calendario(d, seed=21):
    dd = indicadores(d).reset_index(drop=True)
    aj, ad = dd["AJ"].values, dd["AD"].values
    obs = float((aj * ad).sum())
    per = pd.cut(dd["anio"], [2003, 2009, 2014, 2019, 2022, 2026],
                 labels=["2004-09", "2010-14", "2015-19", "2020-22", "2023-26"]).astype(str).values
    masks = {"todo": np.ones(len(dd), bool), "sincrisis": ~dd["crisis"].values}
    masks.update({f"per_{p}": per == p for p in np.unique(per)})
    grupos = [np.where(dd["quarter"].values == q)[0] for q in np.unique(dd["quarter"].values)]
    rng = np.random.default_rng(seed)
    sims = {k: np.empty(R_PERM) for k in masks}
    for r in range(R_PERM):
        a = ad.copy()
        for ix in grupos:
            a[ix] = a[rng.permutation(ix)]
        j = aj * a
        for k, m in masks.items():
            sims[k][r] = j[m].sum()
    num("cal_R", R_PERM)
    for k, m in masks.items():
        o = float((aj * ad)[m].sum())
        num(f"cal_{k}_obs", o); num(f"cal_{k}_esp", sims[k].mean())
        num(f"cal_{k}_razon", o / sims[k].mean() if sims[k].mean() > 0 else np.nan)
        num(f"cal_{k}_p_unilateral", (1 + (sims[k] >= o).sum()) / (R_PERM + 1))
        num(f"cal_{k}_N", m.sum())
    num("cal_obs_check", obs)


# ================================================================ 2. precedencia
def cruzada(x, pref, lags_J=("ln_JLoss_l1",), lags_D=("D_l1",), con_wild=True):
    """D_t sobre sus rezagos y los de ln JLoss; EF de país y tiempo. Con un rezago coincide con p32."""
    x = x.dropna(subset=["D_t", *lags_J, *lags_D])
    rhs = list(lags_D) + list(lags_J)
    m = p32.pfit(x, "D_t", rhs); mc = p32.pfit(x, "D_t", rhs, cov="pais")
    num(f"{pref}_N", m.nobs)
    if len(lags_J) == 1:
        c = lags_J[0]
        num(f"{pref}_b", m.params[c]); num(f"{pref}_p_dk", m.pvalues[c]); num(f"{pref}_p_pais", mc.pvalues[c])
        if con_wild:
            num(f"{pref}_p_wild", p32.wild(x, "D_t", rhs, c))
        return
    s = float(m.params[list(lags_J)].sum())
    a = np.zeros(len(rhs)); a[[rhs.index(c) for c in lags_J]] = 1.0
    for lab, mm in (("dk", m), ("pais", mc)):
        V = mm.cov.loc[rhs, rhs].values
        se = float(np.sqrt(a @ V @ a))
        num(f"{pref}_suma_b", s); num(f"{pref}_suma_p_{lab}", 2 * stats.norm.sf(abs(s / se)))
        bJ = mm.params[list(lags_J)].values; VJ = mm.cov.loc[list(lags_J), list(lags_J)].values
        w = float(bJ @ np.linalg.solve(VJ, bJ))
        num(f"{pref}_wald_p_{lab}", stats.chi2.sf(w, len(lags_J)))
    if con_wild:
        num(f"{pref}_wald_p_wild", p32.wb_run(p32.wb_prep(x, "D_t", rhs), list(lags_J))[0])


def con_gar_alternativo(d, raw, f):
    """reemplaza D (pp) en raw por el de otro archivo de GaR y reconstruye D_t y D_l1 sobre la misma muestra."""
    g = pd.read_csv(f); g["country"] = g["country"].str.lower()
    r = raw.drop(columns=["D_pp", "GaR"], errors="ignore").merge(g[["country", "quarter", "GaR"]], on=["country", "quarter"], how="left")
    r["D_pp"] = -r["GaR"] * 100.0
    x = d.drop(columns=["D_t", "D_l1"])
    for k, name in ((0, "D_t"), (1, "D_l1")):
        x = x.merge(p14.shift(r, "D_pp", k, name), on=["country", "_qn"], how="left")
    return x


def bloque_precedencia(d, raw):
    cruzada(d, "prec_base")
    for c in sorted(d["country"].unique()):
        cruzada(d[d["country"] != c], f"prec_sin_{c}", con_wild=False)
    bs = [NUM[f"prec_sin_{c}_b"] for c in sorted(d["country"].unique())]
    ps = [NUM[f"prec_sin_{c}_p_dk"] for c in sorted(d["country"].unique())]
    num("prec_loo_b_min", min(bs)); num("prec_loo_b_max", max(bs))
    num("prec_loo_p_dk_max", max(ps)); num("prec_loo_n_sig05", sum(p < 0.05 for p in ps))
    for lab, f in (("insample_base", "gar_insample_base.csv"), ("insample_noSTX", "gar_insample_noSTX.csv")):
        path = os.path.join(GARNC, f)
        if not os.path.exists(path):
            print(f"  (falta {f}: correr build_fci_no_stx.py y gar_insample_robustez.py)"); continue
        cruzada(con_gar_alternativo(d, raw, path), f"prec_{lab}")
    # dos a cuatro rezagos de cada riesgo
    x = d.copy()
    for k in (2, 3, 4):
        x = x.merge(p14.shift(raw, "ln_JLoss", k, f"Jq_l{k}"), on=["country", "_qn"], how="left")
        x = x.merge(p14.shift(raw, "D_pp", k, f"Dq_l{k}"), on=["country", "_qn"], how="left")
    for L in (2, 3, 4):
        lj = ["ln_JLoss_l1"] + [f"Jq_l{k}" for k in range(2, L + 1)]
        ld = ["D_l1"] + [f"Dq_l{k}" for k in range(2, L + 1)]
        cruzada(x, f"prec_L{L}", lags_J=lj, lags_D=ld)
        # dirección inversa con los mismos rezagos
        y = x.rename(columns={"D_t": "_D_t"}).rename(columns={"ln_JLoss_t": "D_t"})
        cruzada(y, f"prec_inv_L{L}", lags_J=ld, lags_D=lj, con_wild=False)


# ================================================================ 3. equivalencia (TOST)
def wild_ci90(dd, y, regs, key, b, se, npts=81, ancho=6.0):
    """IC 90 % por inversión del wild (p32.wild_ci al 10 %)."""
    P = p32.wb_prep(dd, y, regs)
    grid = b + se * np.linspace(-ancho, ancho, npts)
    ps = np.array([p32.wb_run(P, [key], null=[c])[0] for c in grid])
    ok = np.where(ps >= 0.10)[0]
    hi = ok.max()
    if hi + 1 >= npts:
        return float(grid[hi])
    return float(grid[hi] + (grid[hi + 1] - grid[hi]) * (ps[hi] - 0.10) / (ps[hi] - ps[hi + 1]))


def bloque_tost(d):
    m, dd = p13.fit(d); mc, _ = p13.fit(d, cov="pais")
    b1, b2, b3 = m.params["J_c"], m.params["T_c"], m.params["JxT"]
    sJ = float((dd["J_c"] - dd.groupby("country")["J_c"].transform("mean")).std())
    sD = float((dd["T_c"] - dd.groupby("country")["T_c"].transform("mean")).std())
    sep = b1 * sJ + b2 * sD
    G = dd["country"].nunique(); t90 = stats.t.ppf(0.95, G - 1)
    hi = {"dk": b3 + 1.645 * m.std_errors["JxT"], "pais": b3 + t90 * mc.std_errors["JxT"],
          "wild": wild_ci90(dd, "ln_EMBI", ["J_c", "T_c", "JxT"], "JxT", b3, mc.std_errors["JxT"])}
    num("tost_b3", b3); num("tost_suma_separados", sep); num("tost_sJ", sJ); num("tost_sD", sD)
    for k, h in hi.items():
        num(f"tost_b3_hi90_{k}", h)
        num(f"tost_cota_sobre_suma_{k}", h * sJ * sD / sep)      # menor margen que la equivalencia rechaza
    # efecto mínimo detectable (5 % bilateral, potencia 80 %) como fracción de la suma
    for k, se in (("dk", m.std_errors["JxT"]), ("pais", mc.std_errors["JxT"])):
        crit = 1.96 if k == "dk" else stats.t.ppf(0.975, G - 1)
        pw = 0.8416 if k == "dk" else stats.t.ppf(0.80, G - 1)
        num(f"tost_mde_{k}", (crit + pw) * se); num(f"tost_mde_sobre_suma_{k}", (crit + pw) * se * sJ * sD / sep)


def main():
    print("p33: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, _ = p14.check_principal(d)
    out = os.path.join(HERE, f"paper_p33_numeros{SFX}.csv")

    def guardar(msg):
        pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
        print(f"  {msg} ({len(NUM)} cifras)", flush=True)

    d = p32.agregar_rezagos(p14.cargar_bbg_macro(d), raw)
    bloque_calendario(d); guardar("1. simultaneidad con nula de calendario")
    bloque_precedencia(d, raw); guardar("2. precedencia")
    bloque_tost(d); guardar("3. equivalencia")
    for k, v in NUM.items():
        print(f"  {k:44s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
