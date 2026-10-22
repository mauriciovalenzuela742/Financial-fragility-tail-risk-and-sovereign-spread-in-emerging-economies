# -*- coding: utf-8 -*-
"""
p42_resiliencia_preregistrada.py -- pruebas preregistradas de resiliencia
(4_Redaccion/preregistro_resiliencia.md, commit c492ca3, anterior a este script y a los datos).

  R-H1: efecto directo controlado (EDC) de ln JLoss_{t-1}, neto del canal fiscal, por g-estimación
        secuencial (Acharya, Blackwell y Sen, 2016). Etapa 1: ln EMBI_t sobre ln JLoss_{t-1}, D_{t-1},
        mediadores (balance fiscal_t, DEBT_t) y confusores intermedios (inflación_t, TCR_t), EF de
        país y tiempo. Etapa 2: (ln EMBI_t - mediadores x gamma) sobre ln JLoss_{t-1}, D_{t-1} y los
        seis controles en t-4, EF de país y tiempo. Bootstrap de bloques por país (999) sobre ambas
        etapas; p unilateral = fracción de réplicas con EDC <= 0. Se reportan el efecto total y la
        fracción mediada.
  R-H2: base + RA_{t-4} + ln JLoss_{t-1} x RA_{t-4}; predicción lambda < 0.
  R-H3: base + DEBT_{t-4} + D_{t-1} x DEBT_{t-4}; predicción psi > 0.
  Familia primaria {lambda, psi}: p unilateral del wild cluster bootstrap (Webb, 999) y Holm.
  p unilateral: el wild de p32 es bilateral (Wald); con el signo predicho, p/2; con el contrario,
  1 - p/2 (convención declarada aquí, no en el preregistro).
  Veredicto "firme": Holm < 0,05 y, sin cada país, mismo signo con p unilateral (wild) < 0,10 en las 13.
  Secundarias: reservas/PIB en lugar de RA; moderadores en t-8; niveles (pb); proyecciones locales
  mensuales dependientes del estado de reservas (RA del trimestre anterior sobre la mediana de su país).

DEBT = deuda del gobierno general trimestral (QPSD); si falta, central; si falta, la anual interpolada
(Chile, India y Malasia), marcada. Moderadores estandarizados en la muestra de estimación.

Salida: bbg/paper_p42_numeros.csv. Reutiliza p13, p14, p32, p37.
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
from linearmodels.panel import PanelOLS

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p37_mensual_fechado as p37
from causal_core import demean2

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
NUM = p32.NUM
B_BOOT = 999
RES = os.path.join(HERE, "resiliencia_trimestral_bbg.csv")
CTR_L4 = ["debt_gdp_l4", "fisc_bal_l4", "res_gdp_l4", "ca_gdp_l4", "infl_yoy_l4", "reer_l4"]


def num(k, v):
    NUM[k] = float(v)


def unilateral(p_bi, b, signo):
    return p_bi / 2 if np.sign(b) == signo else 1 - p_bi / 2


def preparar():
    d, raw = p14.base()
    p14.check_principal(d)
    r = pd.read_csv(RES)
    q = pd.PeriodIndex(r["quarter"], freq="Q"); r["_qn"] = q.year * 4 + q.quarter
    raw = raw.merge(r[["country", "_qn", "RA", "debt_q"]], on=["country", "_qn"], how="left")
    raw["DEBT"] = raw["debt_q"].fillna(raw["debt_gdp"])
    raw["DEBT_anual"] = raw["debt_q"].isna() & raw["debt_gdp"].notna()
    for col in ("RA", "DEBT", "res_gdp"):
        for k in (4, 8):
            if f"{col}_l{k}" in d.columns:          # p14.base ya trae los seis controles en t-4
                continue
            d = d.merge(p14.shift(raw, col, k, f"{col}_l{k}"), on=["country", "_qn"], how="left")
    d = d.merge(p14.shift(raw, "DEBT", 0, "DEBT_t"), on=["country", "_qn"], how="left")
    d = d.merge(p14.shift(raw, "DEBT_anual", 0, "DEBT_anual_t"), on=["country", "_qn"], how="left")
    return d, raw


def centrar(x):
    x = x.copy()
    x["J_c"] = x["ln_JLoss_l1"] - x["ln_JLoss_l1"].mean()
    x["T_c"] = x["D_l1"] - x["D_l1"].mean()
    x["JxT"] = x["J_c"] * x["T_c"]
    return x


def fit(x, y, rhs, cov="dk"):
    kw = dict(p14.DK) if cov == "dk" else dict(cov_type="clustered", cluster_entity=True)
    return PanelOLS.from_formula(f"{y} ~ {' + '.join(rhs)} + EntityEffects + TimeEffects",
                                 x.set_index(["country", "t"])).fit(**kw)


# ================================================================ R-H2 / R-H3
def moderacion(d, mod, riesgo, pref, signo, loo=True):
    x = centrar(d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1", mod]))
    x["M_s"] = (x[mod] - x[mod].mean()) / x[mod].std()
    x["IxM"] = x[riesgo] * x["M_s"]
    rhs = ["J_c", "T_c", "JxT", "M_s", "IxM"]
    m = fit(x, "ln_EMBI", rhs); mc = fit(x, "ln_EMBI", rhs, "pais")
    b = float(m.params["IxM"])
    pw = p32.wild(x, "ln_EMBI", rhs, "IxM")
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", x["country"].nunique())
    num(f"{pref}_b", b); num(f"{pref}_p_dk", m.pvalues["IxM"]); num(f"{pref}_p_pais", mc.pvalues["IxM"])
    num(f"{pref}_p_wild_bi", pw); num(f"{pref}_p_uni", unilateral(pw, b, signo))
    num(f"{pref}_directo", m.params["M_s"]); num(f"{pref}_directo_p_dk", m.pvalues["M_s"])
    if loo:
        ok = 0; bs = []
        for c in sorted(x["country"].unique()):
            xc = x[x["country"] != c]
            mcc = fit(xc, "ln_EMBI", rhs); bc = float(mcc.params["IxM"])
            pc = unilateral(p32.wild(xc, "ln_EMBI", rhs, "IxM"), bc, signo)
            bs.append(bc); ok += int(np.sign(bc) == signo and pc < 0.10)
            num(f"{pref}_sin_{c}_b", bc); num(f"{pref}_sin_{c}_p_uni", pc)
        num(f"{pref}_loo_ok", ok); num(f"{pref}_loo_b_min", min(bs)); num(f"{pref}_loo_b_max", max(bs))
    return unilateral(pw, b, signo)


# ================================================================ R-H1
def g_estimacion(x):
    med = ["fisc_bal", "DEBT_t"]; conf = ["infl_yoy", "reer"]
    e1 = fit(x, "ln_EMBI", ["J_c", "T_c"] + med + conf)
    g = e1.params[med]
    x = x.assign(Ytil=x["ln_EMBI"] - x[med].values @ g.values)
    e2 = fit(x, "Ytil", ["J_c", "T_c"] + CTR_L4)
    return float(e2.params["J_c"]), g


def rh1(d):
    cols = ["ln_EMBI", "ln_JLoss_l1", "D_l1", "fisc_bal", "DEBT_t", "infl_yoy", "reer"] + CTR_L4
    x = centrar(d.dropna(subset=cols)).reset_index(drop=True)
    edc, g = g_estimacion(x)
    tot = fit(x, "ln_EMBI", ["J_c", "T_c"])
    num("rh1_N", len(x)); num("rh1_paises", x["country"].nunique())
    num("rh1_edc", edc); num("rh1_total", tot.params["J_c"]); num("rh1_total_p_dk", tot.pvalues["J_c"])
    num("rh1_frac_mediada", 1 - edc / tot.params["J_c"])
    num("rh1_gamma_fisc_bal", g["fisc_bal"]); num("rh1_gamma_debt", g["DEBT_t"])
    num("rh1_obs_debt_anual", float(x["DEBT_anual_t"].fillna(False).astype(bool).mean()))
    rng = np.random.default_rng(42); paises = x["country"].unique(); reps = []
    for _ in range(B_BOOT):
        pick = rng.choice(paises, size=len(paises), replace=True)
        xb = pd.concat([x[x["country"] == c].assign(country=f"{c}_{k}") for k, c in enumerate(pick)], ignore_index=True)
        try:
            xb = centrar(xb); reps.append(g_estimacion(xb)[0])
        except Exception:
            continue
    reps = np.array(reps)
    num("rh1_nboot", len(reps)); num("rh1_edc_lo", np.quantile(reps, 0.025)); num("rh1_edc_hi", np.quantile(reps, 0.975))
    num("rh1_p_uni", (reps <= 0).mean())
    print(f"  R-H1: EDC = {edc:.4f} [{np.quantile(reps, .025):.3f}; {np.quantile(reps, .975):.3f}], p uni = {(reps <= 0).mean():.3f}; total {tot.params['J_c']:.4f}", flush=True)


# ================================================================ LP mensual por estado de reservas
def lp_estado(raw_res):
    s = p37.series(); e = p37.embi_mensual()
    x = s.merge(e, on=["country", "month"], how="inner").sort_values(["country", "month"])
    x["F"] = -x["DD_w"]; x["y"] = np.log(x["embi_cierre"])
    x["t"] = x["month"].dt.to_timestamp(); x["quarter"] = x["month"].astype(str)
    g = x.groupby("country")
    consec = (x["month"] - g["month"].shift(1)).apply(lambda v: getattr(v, "n", np.nan)) == 1
    x["dy"] = g["y"].diff().where(consec); x["dF"] = g["F"].diff().where(consec)
    for k in (1, 2, 3):
        x[f"dy_l{k}"] = g["dy"].shift(k); x[f"dF_l{k}"] = g["dF"].shift(k)
    for h in range(0, 7):
        x[f"cy{h}"] = g["y"].shift(-h) - g["y"].shift(1)
    r = pd.read_csv(RES)[["country", "quarter", "RA"]].dropna()
    med = r.groupby("country")["RA"].median()
    r["alto"] = (r["RA"] > r["country"].map(med)).astype(float)
    r["q_sig"] = (pd.PeriodIndex(r["quarter"], freq="Q") + 1).astype(str)        # se conoce en el trimestre siguiente
    x["q"] = x["month"].dt.asfreq("Q").astype(str)
    x = x.merge(r[["country", "q_sig", "alto"]].rename(columns={"q_sig": "q"}), on=["country", "q"], how="left")
    x["dFxA"] = x["dF"] * x["alto"]
    ctrl = ["dy_l1", "dy_l2", "dy_l3", "dF_l1", "dF_l2", "dF_l3"]
    num("lp_N_meses", x.dropna(subset=["alto", "dF"]).shape[0])
    for h in range(0, 7):
        z = x.dropna(subset=[f"cy{h}", "dF", "alto"] + ctrl)
        m = PanelOLS.from_formula(f"cy{h} ~ dF + dFxA + alto + {' + '.join(ctrl)} + EntityEffects + TimeEffects",
                                  z.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett", bandwidth=max(6, h + 1))
        num(f"lp_h{h}_bajo", m.params["dF"]); num(f"lp_h{h}_alto", m.params["dF"] + m.params["dFxA"])
        num(f"lp_h{h}_dif", m.params["dFxA"]); num(f"lp_h{h}_dif_p_dk", m.pvalues["dFxA"])
        if h in (0, 3):
            num(f"lp_h{h}_dif_p_wild", p32.wild(z, f"cy{h}", ["dF", "dFxA", "alto"] + ctrl, "dFxA"))


def main():
    print("p42: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = preparar()
    out = os.path.join(HERE, f"paper_p42_numeros{SFX}.csv")
    guardar = lambda: pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    # familia primaria
    p2 = moderacion(d, "RA_l4", "J_c", "rh2", -1)
    p3 = moderacion(d, "DEBT_l4", "T_c", "rh3", +1)
    ps = sorted([("rh2", p2), ("rh3", p3)], key=lambda z: z[1])
    holm = {ps[0][0]: min(1, 2 * ps[0][1]), ps[1][0]: min(1, max(2 * ps[0][1], ps[1][1]))}
    for k, v in holm.items():
        num(f"{k}_p_holm", v)
    for k in ("rh2", "rh3"):
        firme = NUM[f"{k}_p_holm"] < 0.05 and NUM[f"{k}_loo_ok"] == 13
        num(f"{k}_firme", float(firme))
    guardar(); print(f"  R-H2 lambda = {NUM['rh2_b']:.4f} (p uni {p2:.3f}; Holm {NUM['rh2_p_holm']:.3f}); "
                     f"R-H3 psi = {NUM['rh3_b']:.4f} (p uni {p3:.3f}; Holm {NUM['rh3_p_holm']:.3f})", flush=True)
    if not NIV:
        rh1(d); guardar()
        # secundarias
        moderacion(d, "res_gdp_l4", "J_c", "sec_resgdp", -1, loo=False)
        moderacion(d, "RA_l8", "J_c", "sec_rh2_l8", -1, loo=False)
        moderacion(d, "DEBT_l8", "T_c", "sec_rh3_l8", +1, loo=False)
        lp_estado(raw); guardar()
    for k, v in NUM.items():
        if not "_sin_" in k:
            print(f"  {k:28s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
