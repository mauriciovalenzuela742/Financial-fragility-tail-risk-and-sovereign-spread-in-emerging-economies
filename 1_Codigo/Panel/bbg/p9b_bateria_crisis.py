# -*- coding: utf-8 -*-
"""
p9b_bateria_crisis.py -- bateria de 24 regresiones (4 modelos anidados x 3 estructuras de
efectos fijos x 2 paneles de crisis) para la ecuacion de interaccion de crisis. Extiende la
logica de p8_bateria_regresiones.py (bateria base M1-M4) a la especificacion de
p9_crisis_interaccion.py (vector Backstop/EMstress) -- ESE SCRIPT NO SE MODIFICA, solo se
replica su logica de ajuste (dd, JLoss_c, D_c, JxD, bloques *_{nm}) para CM4.

Convencion: D = -GaR (pp). Vector de crisis: GFC (2008Q4-2009Q4) + COVID (2020Q1-2021Q4) +
estres EM (2015Q3-2016Q1). Companion: Backstop (GFC+COVID) vs EMstress (2015-16).

Modelos anidados (todos con los mismos 6 controles domesticos que la tabla ya publicada):

  CM1  EMBI ~ JLoss_c + JLoss_c x {dummies}                          (sin D, sin JxD)
  CM2  EMBI ~ D_c + D_c x {dummies}                                   (sin JLoss, sin JxD)
  CM3  EMBI ~ JLoss_c + D_c + (JLoss_c y D_c) x {dummies}             (niveles + su propia
                                                                        interaccion con crisis,
                                                                        SIN JxD ni JxD x crisis)
  CM4  EMBI ~ JLoss_c + D_c + JxD + (JxD, JLoss_c, D_c) x {dummies}   (= especificacion vigente
                                                                        de p9_crisis_interaccion.py,
                                                                        sin cambios)

Paneles de crisis:
  Panel A ("vector unico"):        dummies = {"cr": CRISIS_Q}
  Panel B ("Backstop/EMstress"):   dummies = {"bk": BACKSTOP_Q, "em": EM1516}

Efectos fijos: T (tiempo), P (pais), PT (pais+tiempo) -- mismo diccionario que p8.
Errores Driscoll-Kraay (kernel Bartlett) en todas, igual que p9.

Para cada uno de los terminos "base" del modelo (JLoss_c y/o D_c y/o JxD, segun corresponda)
se reporta ademas la suma base+crisis (metodo delta, Wald H0: suma=0) contra cada dummy del
panel -- para CM4 esto reproduce exactamente b3+b4 de p9_crisis_interaccion.py.

Salida -> bbg/bateria_crisis_bbg.csv (formato ancho, una fila por modelo x FE x panel = 24 filas).
"""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

from p2_regresiones import prep, CTRLS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

GFC = ["2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4"]
COVID = ["2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"]
EM1516 = ["2015Q3", "2015Q4", "2016Q1"]
CRISIS_Q = GFC + COVID + EM1516
BACKSTOP_Q = GFC + COVID

PANELS = [
    ("A_vector_unico", {"cr": CRISIS_Q}),
    ("B_backstop_emstress", {"bk": BACKSTOP_Q, "em": EM1516}),
]

FE_MAP = {"T": "TimeEffects", "P": "EntityEffects", "PT": "EntityEffects + TimeEffects"}

# prefijos "base" que participan de cada modelo (nombre logico -> nombre de columna base).
# el sufijo de interaccion con crisis sigue siempre el patron f"{prefijo}_{nm}", identico
# al usado en p9_crisis_interaccion.py (JLoss_{nm}, D_{nm}, JxD_{nm}).
MODEL_BASE = {
    "CM1": {"JLoss": "JLoss_c"},
    "CM2": {"D": "D_c"},
    "CM3": {"JLoss": "JLoss_c", "D": "D_c"},
    "CM4": {"JxD": "JxD"},
}


def _lincom(m, names):
    """coef, se, t, p (Wald H0: suma=0) de la suma de varios parametros (metodo delta)."""
    b = float(sum(m.params[n] for n in names))
    V = m.cov
    var = sum(float(V.loc[i, j]) for i in names for j in names)
    se = float(np.sqrt(var))
    t = b / se
    p = 2 * (1 - stats.norm.cdf(abs(t)))
    return b, se, t, p


def _get(m, n):
    if n in m.params.index:
        return dict(b=float(m.params[n]), se=float(m.std_errors[n]),
                    t=float(m.tstats[n]), p=float(m.pvalues[n]))
    return dict(b=np.nan, se=np.nan, t=np.nan, p=np.nan)


def _build_rhs(model, dummies):
    """Lista de terminos del lado derecho (sin controles ni FE) para `model`."""
    base = MODEL_BASE[model]
    if model == "CM1":
        rhs = ["JLoss_c"]
    elif model == "CM2":
        rhs = ["D_c"]
    elif model == "CM3":
        rhs = ["JLoss_c", "D_c"]
    elif model == "CM4":
        rhs = ["JLoss_c", "D_c", "JxD"]
    else:
        raise ValueError(model)

    for nm in dummies:
        if model == "CM1":
            rhs.append(f"JLoss_{nm}")
        elif model == "CM2":
            rhs.append(f"D_{nm}")
        elif model == "CM3":
            rhs += [f"JLoss_{nm}", f"D_{nm}"]
        elif model == "CM4":
            rhs += [f"JxD_{nm}", f"JLoss_{nm}", f"D_{nm}"]
    return rhs, base


def fit_crisis_model(d, model, dummies, fe, ctr):
    """Replica exacta de la logica de dd/_fit de p9_crisis_interaccion.py, parametrizada
    por modelo (CM1-CM4) y estructura de efectos fijos."""
    dd = d.dropna(subset=["_DV", "JLoss", "D_pp"] + ctr).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    for nm, qs in dummies.items():
        cr = dd["quarter"].isin(qs).astype(float)
        dd[f"JxD_{nm}"] = dd["JxD"] * cr
        dd[f"JLoss_{nm}"] = dd["JLoss_c"] * cr
        dd[f"D_{nm}"] = dd["D_c"] * cr

    rhs, base = _build_rhs(model, dummies)
    all_rhs = rhs + ctr
    eff = FE_MAP[fe]
    f = f"_DV ~ {' + '.join(all_rhs)} + {eff}"
    md = dd.set_index(["country", "t"])
    m = PanelOLS.from_formula(f, md).fit(cov_type="kernel", kernel="bartlett")
    return m, dd, base


def run():
    d = prep()
    d["D_pp"] = -d["GaR_pp"]
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    print(f"Panel: {len(d)} obs, {d['country'].nunique()} paises, "
          f"{d['quarter'].min()}..{d['quarter'].max()}, controles ({len(ctr)}): {ctr}\n")

    rows = []
    for panel_name, dummies in PANELS:
        for model in ("CM1", "CM2", "CM3", "CM4"):
            for fe in ("T", "P", "PT"):
                m, dd, base = fit_crisis_model(d, model, dummies, fe, ctr)
                obs_ent = dd.groupby("country").size()

                rec = dict(
                    panel=panel_name, modelo=model, fe=fe,
                    N=int(m.nobs),
                    paises=int(m.entity_info["total"]),
                    periodos=int(m.time_info["total"]),
                    obs_avg=float(obs_ent.mean()),
                    obs_min=int(obs_ent.min()),
                    obs_max=int(obs_ent.max()),
                    rsquared=float(m.rsquared),
                    rsquared_within=float(m.rsquared_within),
                    rsquared_between=float(m.rsquared_between),
                    f_stat=float(m.f_statistic.stat),
                    f_pval=float(m.f_statistic.pval),
                )

                # -- coeficientes "de nivel" presentes en este modelo --
                for coef_name in ("JLoss_c", "D_c", "JxD"):
                    if coef_name in m.params.index:
                        g = _get(m, coef_name)
                        rec[f"{coef_name}_b"] = g["b"]; rec[f"{coef_name}_se"] = g["se"]
                        rec[f"{coef_name}_t"] = g["t"]; rec[f"{coef_name}_p"] = g["p"]

                # -- bloques de interaccion con cada dummy de crisis + suma base+crisis --
                for nm, lbl in (("cr", "Crisis"), ("bk", "Backstop"), ("em", "EMstress")):
                    if nm not in dummies:
                        continue
                    for prefix, base_col in base.items():
                        crisis_col = f"{prefix}_{nm}"
                        g = _get(m, crisis_col)
                        rec[f"{crisis_col}_b"] = g["b"]; rec[f"{crisis_col}_se"] = g["se"]
                        rec[f"{crisis_col}_t"] = g["t"]; rec[f"{crisis_col}_p"] = g["p"]
                        if crisis_col in m.params.index:
                            sb, sse, st, sp = _lincom(m, [base_col, crisis_col])
                            rec[f"{prefix}_sum_{nm}_b"] = sb
                            rec[f"{prefix}_sum_{nm}_se"] = sse
                            rec[f"{prefix}_sum_{nm}_t"] = st
                            rec[f"{prefix}_sum_{nm}_p"] = sp   # Wald H0: base+crisis = 0
                rows.append(rec)

                head = f"[{panel_name:22s} | {model} | FE {fe:2s}] N={rec['N']}"
                print(head)
                for coef_name in ("JLoss_c", "D_c", "JxD"):
                    if f"{coef_name}_b" in rec:
                        print(f"    {coef_name:9s} = {rec[coef_name+'_b']:+.3f} "
                              f"(t={rec[coef_name+'_t']:+.2f}, p={rec[coef_name+'_p']:.3f})")
                for nm, lbl in (("cr", "Crisis"), ("bk", "Backstop"), ("em", "EMstress")):
                    if nm not in dummies:
                        continue
                    for prefix in base:
                        cc = f"{prefix}_{nm}"
                        if f"{cc}_b" in rec:
                            print(f"    {cc:12s} = {rec[cc+'_b']:+.3f} "
                                  f"(t={rec[cc+'_t']:+.2f}, p={rec[cc+'_p']:.3f})   "
                                  f"[{prefix} base+{lbl} = {rec[f'{prefix}_sum_{nm}_b']:+.3f}, "
                                  f"Wald p={rec[f'{prefix}_sum_{nm}_p']:.3f}]")
                print()

    df = pd.DataFrame(rows)
    out = os.path.join(HERE, "bateria_crisis_bbg.csv")
    df.to_csv(out, index=False)
    print(f"Guardado: {out}  ({len(df)} filas)")

    # ---------------- verificacion obligatoria ----------------
    # CM4 / PT / Panel B (Backstop-EMstress) debe reproducir la Tabla tab:crisis ya publicada
    # (crisis_interaccion_bbg.csv, grid="Backstop vs EMstress", controles="+6 controles", fe="PT"):
    #   b3 (JxD, fuera de crisis)      = +0.837473  (t=+2.023)
    #   b3+b4 Backstop (JxD_bk)        = -0.105021  (Wald p=0.2699)
    #   b3+b4 EMstress (JxD_em)        = +1.050632  (Wald p=0.000226)
    #   N = 614
    sel = df[(df["panel"] == "B_backstop_emstress") & (df["modelo"] == "CM4") & (df["fe"] == "PT")]
    r = sel.iloc[0]
    pub = dict(N=614, b3=0.837473, b3_t=2.023436,
               sum_bk=-0.105021, p_bk=0.2699,
               sum_em=1.050632, p_em=0.000226)
    mine = dict(N=int(r["N"]), b3=r["JxD_b"], b3_t=r["JxD_t"],
                sum_bk=r["JxD_sum_bk_b"], p_bk=r["JxD_sum_bk_p"],
                sum_em=r["JxD_sum_em_b"], p_em=r["JxD_sum_em_p"])
    print("\n" + "=" * 78)
    print("VERIFICACION -- CM4 / FE=PT / Panel B (Backstop-EMstress) vs Tabla tab:crisis")
    print("=" * 78)
    print(f"{'':28s}{'publicado':>16s}{'p9b (aqui)':>16s}")
    print(f"{'N':28s}{pub['N']:>16d}{mine['N']:>16d}")
    print(f"{'b3 (fuera de crisis)':28s}{pub['b3']:>16.3f}{mine['b3']:>16.3f}   (t_pub={pub['b3_t']:+.2f})")
    print(f"{'b3+b4 Backstop':28s}{pub['sum_bk']:>16.3f}{mine['sum_bk']:>16.3f}   "
          f"(Wald p_pub={pub['p_bk']:.3f}, p_aqui={mine['p_bk']:.3f})")
    print(f"{'b3+b4 EMstress':28s}{pub['sum_em']:>16.3f}{mine['sum_em']:>16.3f}   "
          f"(Wald p_pub={pub['p_em']:.4f}, p_aqui={mine['p_em']:.4f})")
    ok = (mine["N"] == pub["N"]
          and abs(mine["b3"] - pub["b3"]) < 5e-4
          and abs(mine["sum_bk"] - pub["sum_bk"]) < 5e-4
          and abs(mine["sum_em"] - pub["sum_em"]) < 5e-4)
    print("RESULTADO:", "OK -- coincide con la tabla publicada" if ok else "*** NO COINCIDE -- revisar ***")
    if not ok:
        raise SystemExit("Verificacion de replicacion fallo: CM4/PT/Panel B no coincide con tab:crisis")

    return df


if __name__ == "__main__":
    run()
