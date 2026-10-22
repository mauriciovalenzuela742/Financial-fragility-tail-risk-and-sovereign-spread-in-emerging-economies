# -*- coding: utf-8 -*-
"""
p47_sensibilidad_motor.py -- mu2 del preregistro 3 (4_Redaccion/preregistro_micro.md, commit d73245f):
sensibilidad de JLoss a la calibración del motor. Tres variantes, todas con los mismos bancos e insumos:

  rho    : rho por banco y trimestre = correlación de sus retornos diarios con el índice de capitalización de
           los demás bancos de su país en los ocho trimestres previos, acotada a [0,05; 0,95] (la base usa
           0,4 para todos).
  dp     : punto de incumplimiento 0,5 x pasivos de corto plazo + 0,5 x largo plazo (la base: CP + 0,5 LP);
           los pasivos de corto plazo incluyen los depósitos.
  ancha  : malla de pérdidas [0,01; 0,20] (la base: [0,01; 0,048]), con India incluida.

La LGD homogénea no se prueba: JLoss es proporcional a ella (EL y las contribuciones al VaR escalan con la
exposición e = LGD x pasivos y la distribución relativa de pérdidas no cambia), de modo que ln JLoss solo se
desplaza en una constante.

Uso:  python p47_sensibilidad_motor.py calcular rho|dp|ancha   (lento; escribe jloss_variante_<v>.csv)
      python p47_sensibilidad_motor.py estimar                 (correlación de rangos y regresión principal)
Criterio mu2-H1: correlación de rangos con la base > 0,8 y beta1 > 0 en la principal, con cada variante.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))
JREC = os.path.abspath(os.path.join(HERE, "..", "..", "JLoss_reconstruction"))
sys.path.insert(0, JREC)

import numpy as np
import pandas as pd

BBG = os.path.abspath(os.path.join(HERE, "..", "..", "Bloomberg_extraction", "output"))
PAISES = ["brazil", "chile", "china", "colombia", "india", "indonesia", "malaysia", "mexico", "peru",
          "philippines", "poland", "southafrica", "turkey"]


def rho_por_banco(mk):
    """rho_{b,q}: correlación de los retornos diarios del banco con el índice (capitalización) de los demás
    bancos del país en los ocho trimestres previos al cierre de q."""
    mk = mk.dropna(subset=["mktcap"]); mk = mk[mk["mktcap"] > 0]
    w = mk.pivot_table(index="date", columns="bankname", values="mktcap").sort_index()
    r = np.log(w).diff()
    out = []
    q = w.index.to_period("Q")
    for qq in sorted(set(q)):
        fin = w.index[q == qq].max()
        ini = (qq - 8).start_time
        sl = r[(r.index > ini) & (r.index <= fin)]
        wts = w[(w.index > ini) & (w.index <= fin)].shift(1)
        for b in w.columns:
            otros = [c for c in w.columns if c != b]
            if not otros:
                continue
            idx = (sl[otros] * wts[otros]).sum(axis=1, min_count=1) / wts[otros].sum(axis=1, min_count=1)
            z = pd.concat([sl[b], idx], axis=1).dropna()
            if len(z) < 120:
                continue
            out.append({"bankname": b, "quarter": qq, "rho": float(np.clip(z.corr().iloc[0, 1], 0.05, 0.95))})
    return pd.DataFrame(out)


def calcular(var):
    import jloss_engine as je
    if var == "ancha":
        je.LOSS_SUP = 0.20
    out_f = os.path.join(HERE, f"jloss_variante_{var}.csv")
    hechos = set(pd.read_csv(out_f)["country"]) if os.path.exists(out_f) else set()
    for c in PAISES:
        if c in hechos:
            continue
        bal = pd.read_csv(os.path.join(BBG, c, f"balance_{c}.csv"))
        mk = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"))
        if var == "dp":
            bal["DP"] = 0.5 * bal["st_borrow"] + 0.5 * bal["lt_borrow"]
        dm = je.quarterly_inputs(bal, mk)
        dm["PD"] = [je.merton_pd(e, s, d) for e, s, d in zip(dm["mktcap_end"], dm["sigma_E_q"], dm["D_star"])]
        if var == "rho":
            mk["date"] = pd.to_datetime(mk["date"])
            rh = rho_por_banco(mk)
            dm = dm.merge(rh, on=["bankname", "quarter"], how="left")
        else:
            dm["rho"] = je.RHO_FLAT
        filas = []
        for q, g in dm.groupby("quarter"):
            g = g[g["PD"].notna() & g["total_liab"].notna() & (g["total_liab"] > 0) & g["rho"].notna()]
            if len(g) < 1:
                continue
            jl = je.compute_jloss(g["PD"].values, g["rho"].values, g["total_liab"].values)
            if jl is not None and np.isfinite(jl):
                filas.append({"country": c, "quarter": str(q), "JLoss_v": float(jl), "n_banks": len(g),
                              "rho_medio": float(g["rho"].mean())})
        pd.DataFrame(filas).to_csv(out_f, mode="a", header=not os.path.exists(out_f), index=False)
        print(f"  [{var}] {c}: {len(filas)} trimestres", flush=True)
    print(f"  [{var}] listo -> {out_f}")


def estimar():
    import p14_arbitro_lnlag as p14
    import p32_aporte_riesgo_cola as p32
    import p42_resiliencia_preregistrada as p42
    from scipy.stats import spearmanr
    NUM = p32.NUM
    d, raw = p14.base(); p14.check_principal(d)
    for var in ("rho", "dp", "ancha"):
        f = os.path.join(HERE, f"jloss_variante_{var}.csv")
        v = pd.read_csv(f)
        v["quarter"] = (pd.PeriodIndex(v["quarter"], freq="Q") + 1).astype(str)          # rezago de un trimestre
        x = d.merge(v[["country", "quarter", "JLoss_v"]], on=["country", "quarter"], how="left").dropna(subset=["JLoss_v"])
        x = x[x["JLoss_v"] > 0]
        NUM[f"{var}_N"] = len(x)
        NUM[f"{var}_spearman"] = spearmanr(x["JLoss_l1"], x["JLoss_v"]).correlation
        a = np.log(x["JLoss_l1"]) - np.log(x["JLoss_l1"]).groupby(x["country"]).transform("mean")
        b = np.log(x["JLoss_v"]) - np.log(x["JLoss_v"]).groupby(x["country"]).transform("mean")
        NUM[f"{var}_spearman_within"] = spearmanr(a, b).correlation
        for forma in ("log", "niv"):
            y = x.copy()
            y["ln_JLoss_l1"] = np.log(y["JLoss_v"]) if forma == "log" else y["JLoss_v"]
            if forma == "niv":
                y["ln_EMBI"] = y["EMBI_bps"]
            y = p42.centrar(y); rhs = ["J_c", "T_c", "JxT"]
            m = p42.fit(y, "ln_EMBI", rhs)
            for k, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
                NUM[f"{var}_{forma}_{lab}"] = float(m.params[k]); NUM[f"{var}_{forma}_{lab}_p_dk"] = float(m.pvalues[k])
            NUM[f"{var}_{forma}_b1_p_wild"] = p32.wild(y, "ln_EMBI", rhs, "J_c")
            NUM[f"{var}_{forma}_b3_p_wild"] = p32.wild(y, "ln_EMBI", rhs, "JxT")
        sat = None
        NUM[f"{var}_cumple"] = float(NUM[f"{var}_spearman"] > 0.8 and NUM[f"{var}_log_b1"] > 0)
        if var == "rho":
            NUM["rho_medio_bancos"] = float(v["rho_medio"].mean())
    out = os.path.join(HERE, "paper_p47_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, val in NUM.items():
        print(f"  {k:28s} {val: .4f}")
    print("->", out)


if __name__ == "__main__":
    if sys.argv[1] == "calcular":
        calcular(sys.argv[2])
    else:
        estimar()
