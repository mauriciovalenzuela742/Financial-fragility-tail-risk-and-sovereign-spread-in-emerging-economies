# -*- coding: utf-8 -*-
"""
p57_replica_externa.py -- N2 del preregistro 5 (4_Redaccion/preregistro_n1n2.md, commit 7df0427): réplica del
hallazgo central (D4 x deuda) fuera de la muestra, en Hungría y Corea del Sur.

  Datos: JLoss del motor de producción (jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv; Hungría tiene una
  mediana de 2 bancos, bajo el mínimo del panel principal: se declara); spread: EMBI de Hungría
  (2_Datos/embi.xlsx) y CDS a 5 años de Corea (output_macro/southkorea), promedio trimestral; D (pseudo
  tiempo real, gar_panel_all18.csv) y D4 (gar_insample_h4.csv), D = -GaR x 100; deuda: QPSD gobierno general,
  si falta gobierno central, si falta la anual interpolada (Hungría: controls_all_bbg.csv; Corea: las
  observaciones anuales de QPSD, porque la base del FMI no es accesible; se declara). Deuda en t-4.
  N2-H1: y = ln spread - lambda_t (efectos de tiempo de la misma regresión en el panel original), sobre J, T,
  JxT, M, TxM y efectos fijos de país; J y T centrados y M estandarizada con los momentos del original.
  Bootstrap por bloques móviles de 4 trimestres (999): p unilateral = fracción de (psi* - psi) >= psi.
  Diferencia con el original: z con el error bootstrap y el DK del original.
  Secundarias: T = D_{t-1}; cada economía (HAC); controles globales en lugar de lambda_t; observaciones con
  CDS de Indonesia, Filipinas y Sudáfrica fuera de la muestra principal. Potencia: 500 simulaciones con
  psi = original y residuos remuestreados por bloques.
Salida: bbg/paper_p57_numeros.csv y bbg/replica_externa_bbg.csv.
"""
import json
import os
import sys
import urllib.request
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

import p14_arbitro_lnlag as p14
import p32_aporte_riesgo_cola as p32
import p42_resiliencia_preregistrada as p42
import p45_macro_preregistrada as p45

NUM = p32.NUM
B = int(os.environ.get("P57_B", 999))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JL = os.path.join(ROOT, "1_Codigo", "JLoss_reconstruction", "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv")
MAC = os.path.join(ROOT, "1_Codigo", "Bloomberg_extraction", "output_macro")
GARP = os.path.join(ROOT, "1_Codigo", "Panel", "gar_panel_all18.csv")
SERIE = os.path.join(HERE, "replica_externa_bbg.csv")
NUEVAS = {"hungary": "HUN", "southkorea": "KOR"}


def num(k, v):
    NUM[k] = float(v)


def qn(q):
    p = pd.PeriodIndex(q, freq="Q")
    return p.year * 4 + p.quarter


def wb_q(iso, ind):
    url = f"https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?source=20&format=json&per_page=500&date=2000Q1:2026Q4"
    with urllib.request.urlopen(url, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8"))
    return pd.DataFrame([{"quarter": x["date"], "v": x["value"]} for x in (d[1] or []) if x["value"] is not None])


# ================================================================ datos de las economías nuevas
def construir():
    if os.path.exists(SERIE):
        return pd.read_csv(SERIE)
    jl = pd.read_csv(JL); jl = jl[jl["countryname"].isin(NUEVAS)].rename(columns={"countryname": "country"})
    filas = []
    for c, iso in NUEVAS.items():
        if c == "hungary":
            e = pd.read_excel(os.path.join(ROOT, "2_Datos", "embi.xlsx"))[["Fecha", "Hungria"]].dropna()
            e["quarter"] = pd.PeriodIndex(pd.to_datetime(e["Fecha"]), freq="Q").astype(str)
            sp = e.groupby("quarter")["Hungria"].mean().rename("spread")
            fuente = "EMBI"
        else:
            e = pd.read_csv(os.path.join(MAC, c, f"EMBI_{c}.csv"))
            e["quarter"] = pd.PeriodIndex(pd.to_datetime(e["DATES"], format="%d/%m/%Y"), freq="Q").astype(str)
            sp = e.groupby("quarter")["EMBI"].mean().rename("spread")
            fuente = "CDS"
        g = wb_q(iso, "DP.DOD.DECT.CR.GG.Z1"); g["fuente_deuda"] = "QPSD_GG"
        k = wb_q(iso, "DP.DOD.DECT.CR.CG.Z1"); k["fuente_deuda"] = "QPSD_CG"
        deuda = pd.concat([g, k[~k["quarter"].isin(g["quarter"])]]).set_index("quarter")
        x = pd.DataFrame({"quarter": pd.period_range("2003Q1", "2026Q3", freq="Q").astype(str)})
        x["country"] = c
        x = x.merge(sp.reset_index(), on="quarter", how="left")
        x = x.merge(jl[jl["country"] == c][["quarter", "JLoss", "n_banks"]], on="quarter", how="left")
        x = x.merge(deuda[["v", "fuente_deuda"]].rename(columns={"v": "debt_q"}).reset_index(), on="quarter", how="left")
        x["fuente_spread"] = fuente
        filas.append(x)
    x = pd.concat(filas, ignore_index=True)
    # deuda anual de respaldo: Hungría desde controls_all_bbg; Corea, interpolación de sus observaciones QPSD
    ctr = pd.read_csv(os.path.join(HERE, "controls_all_bbg.csv"))[["country", "quarter", "debt_gdp"]]
    x = x.merge(ctr, on=["country", "quarter"], how="left")
    x["DEBT"] = x["debt_q"]
    for c in NUEVAS:
        m = x["country"] == c
        if x.loc[m, "debt_q"].notna().sum() >= 50:
            continue
        s = x.loc[m, "debt_q"].copy()
        if x.loc[m, "debt_gdp"].notna().sum() > 0:
            s = s.fillna(x.loc[m, "debt_gdp"])
        x.loc[m, "DEBT"] = s.interpolate(limit_area="inside").values
        x.loc[m & x["debt_q"].isna() & x["DEBT"].notna(), "fuente_deuda"] = "anual_interpolada"
    # GaR: D (pseudo tiempo real) y D4
    gp = pd.read_csv(GARP); gp["country"] = gp["country"].str.lower().str.replace(" ", "")
    gp["quarter"] = pd.PeriodIndex(pd.to_datetime(gp["date"], format="%d/%m/%Y"), freq="Q").astype(str)
    gp["D"] = -gp["GaR"] * 100
    x = x.merge(gp[["country", "quarter", "D"]], on=["country", "quarter"], how="left")
    g4 = p45.gar_alt("gar_insample_h4.csv")[["country", "quarter", "Dalt"]].rename(columns={"Dalt": "D4"})
    x = x.merge(g4, on=["country", "quarter"], how="left")
    x.to_csv(SERIE, index=False)
    return x


def rezagar(x):
    x = x.copy(); x["_qn"] = qn(x["quarter"])
    out = []
    for c, g in x.groupby("country"):
        g = g.sort_values("_qn").set_index("_qn")
        g["J"] = np.log(g["JLoss"].where(g["JLoss"] > 0)).shift(1)
        g["T1"] = g["D"].shift(1); g["T4"] = g["D4"].shift(1); g["M"] = g["DEBT"].shift(4)
        g["y_raw"] = np.log(g["spread"].where(g["spread"] > 0))
        out.append(g.reset_index())
    return pd.concat(out, ignore_index=True)


# ================================================================ panel original: lambda_t y momentos
def original(tcol):
    d, raw = p42.preparar()
    d = p45.con_D(d, "gar_insample_h4.csv", "D4")
    x = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", tcol, "DEBT_l4"]).reset_index(drop=True)
    mom = dict(J=x["ln_JLoss_l1"].mean(), T=x[tcol].mean(), M=x["DEBT_l4"].mean(), Ms=x["DEBT_l4"].std())
    J = x["ln_JLoss_l1"] - mom["J"]; T = x[tcol] - mom["T"]; M = (x["DEBT_l4"] - mom["M"]) / mom["Ms"]
    X = np.column_stack([J, T, J * T, M, T * M])
    C = pd.get_dummies(x["country"]).values.astype(float); Q = pd.get_dummies(x["quarter"])
    Z = np.column_stack([X, C, Q.values[:, 1:].astype(float)])
    b = np.linalg.lstsq(Z, x["ln_EMBI"].values, rcond=None)[0]
    lam = pd.Series(np.concatenate([[0.0], b[5 + C.shape[1]:]]), index=Q.columns)
    xx = x.assign(J_c=J, T_c=T, JxT=J * T, M_s=M, TxM=T * M)
    m = PanelOLS.from_formula("ln_EMBI ~ J_c + T_c + JxT + M_s + TxM + EntityEffects + TimeEffects",
                              xx.set_index(["country", "t"])).fit(**p14.DK)
    return lam, mom, float(m.params["TxM"]), float(m.std_errors["TxM"]), d, raw


def disenio(z, mom, tcol, extra=()):
    J = z["J"] - mom["J"]; T = z[tcol] - mom["T"]; M = (z["M"] - mom["M"]) / mom["Ms"]
    cols = [J, T, J * T, M, T * M] + [z[e] for e in extra]
    C = pd.get_dummies(z["country"]).values.astype(float)
    return np.column_stack(cols + [C]).astype(float)


def bloques(z, X, y, rng, nb=B):
    qs = np.sort(z["_qn"].unique()); idx = {q: np.where(z["_qn"].values == q)[0] for q in qs}
    nblk = int(np.ceil(len(qs) / 4)); out = []
    for _ in range(nb):
        st = rng.integers(0, len(qs) - 3, size=nblk)
        sel = np.concatenate([np.concatenate([idx[qs[s + k]] for k in range(4)]) for s in st])
        Xb = X[sel]; keep = Xb[:, 5:].sum(0) > 0
        bb = np.linalg.lstsq(np.column_stack([Xb[:, :5], Xb[:, 5:][:, keep]]), y[sel], rcond=None)[0]
        out.append(bb[4])
    return np.array(out)


def estimar(z, mom, lam, tcol, pref, psi_o, se_o, extra=(), usar_lam=True, boot=True):
    z = z.copy()
    z["y"] = z["y_raw"] - z["quarter"].map(lam) if usar_lam else z["y_raw"]
    z = z.dropna(subset=["y", "J", tcol, "M"] + list(extra)).reset_index(drop=True)
    X = disenio(z, mom, tcol, extra); y = z["y"].values
    b = np.linalg.lstsq(X, y, rcond=None)[0]; psi = float(b[4])
    num(f"{pref}_N", len(z)); num(f"{pref}_paises", z["country"].nunique()); num(f"{pref}_psi", psi)
    for c, g in z.groupby("country"):
        num(f"{pref}_T_{c}", len(g)); num(f"{pref}_q0_{c}", g["_qn"].min()); num(f"{pref}_q1_{c}", g["_qn"].max())
    if boot:
        bs = bloques(z, X, y, np.random.default_rng(57))
        se = float(bs.std()); p = float(np.mean(bs - psi >= psi))
        zdif = (psi - psi_o) / np.sqrt(se ** 2 + se_o ** 2)
        num(f"{pref}_se_boot", se); num(f"{pref}_p_uni", p)
        num(f"{pref}_ci90_lo", np.quantile(bs, .05)); num(f"{pref}_ci90_hi", np.quantile(bs, .95))
        num(f"{pref}_dif_z", zdif); num(f"{pref}_dif_p", 2 * (1 - __import__("scipy").stats.norm.cdf(abs(zdif))))
        rep = psi > 0 and p < 0.05 and abs(zdif) < 1.645
        norep = psi <= 0 or abs(zdif) >= 1.645          # el preregistro da precedencia a "no replica"
        num(f"{pref}_replica", float(rep)); num(f"{pref}_no_replica", float(norep))
        num(f"{pref}_parcial", float(not rep and not norep))
    return z, X, y, b


def potencia(z, X, y, b, psi_o, se_o, pref, reps=500):
    rng = np.random.default_rng(91)
    e = y - X @ b; b0 = b.copy(); b0[4] = psi_o
    bs = bloques(z, X, y, np.random.default_rng(57), nb=199)
    se = float(bs.std())
    qs = np.sort(z["_qn"].unique()); idx = {q: np.where(z["_qn"].values == q)[0] for q in qs}
    ok = 0; sims = []
    for _ in range(reps):
        # residuos por bloques de 4 trimestres, conservando la alineación entre países
        perm = np.concatenate([qs[s:s + 4] for s in rng.integers(0, len(qs) - 3, size=int(np.ceil(len(qs) / 4)))])[:len(qs)]
        es = np.zeros(len(y))
        for q_dst, q_src in zip(qs, perm):
            di, si = idx[q_dst], idx[q_src]
            m = min(len(di), len(si)); es[di[:m]] = e[si[:m]]
        ys = X @ b0 + es
        ps = np.linalg.lstsq(X, ys, rcond=None)[0][4]
        sims.append(ps)
        ok += int(ps / se > 1.645 and abs(ps - psi_o) / np.sqrt(se ** 2 + se_o ** 2) < 1.645)
    num(f"{pref}_potencia", ok / reps); num(f"{pref}_potencia_se", se)
    num(f"{pref}_potencia_sim_media", np.mean(sims)); num(f"{pref}_potencia_sim_sd", np.std(sims))
    num(f"{pref}_potencia_solo_signif", float(np.mean(np.array(sims) / se > 1.645)))


def main():
    x = rezagar(construir())
    glob_ = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])[["quarter", "VIX", "UST10Y_log", "US_HY_spread_log"]].dropna().drop_duplicates("quarter")
    glob_["lnVIX"] = np.log(glob_["VIX"]); glob_["_qn"] = qn(glob_["quarter"]); glob_ = glob_.sort_values("_qn")
    for c in ("lnVIX", "UST10Y_log", "US_HY_spread_log"):
        glob_[c + "_l1"] = glob_[c].shift(1)
    x = x.merge(glob_[["_qn", "lnVIX_l1", "UST10Y_log_l1", "US_HY_spread_log_l1"]], on="_qn", how="left")
    for c in NUEVAS:
        g = x[x["country"] == c]
        num(f"datos_{c}_nbancos_mediana", g["n_banks"].median())
        num(f"datos_{c}_deuda_anual", (g["fuente_deuda"] == "anual_interpolada").sum())
    for tcol, pref in (("T4", "N2"), ("T1", "N2d1")):
        lam, mom, psi_o, se_o, d, raw = original("D4_l1" if tcol == "T4" else "D_l1")
        num(f"{pref}_psi_original", psi_o); num(f"{pref}_se_original", se_o)
        z, X, y, b = estimar(x, mom, lam, tcol, pref, psi_o, se_o)
        if pref == "N2":
            potencia(z, X, y, b, psi_o, se_o, pref)
            for c in NUEVAS:          # cada economía por separado (HAC)
                zc = z[z["country"] == c]
                if len(zc) < 20:
                    continue
                Xc = disenio(zc, mom, tcol)[:, :6]; Xc[:, 5] = 1.0
                mc = sm.OLS(zc["y"].values, Xc).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
                num(f"N2_{c}_psi", mc.params[4]); num(f"N2_{c}_p_bil", mc.pvalues[4]); num(f"N2_{c}_N", len(zc))
            estimar(x, mom, lam, tcol, "N2glob", psi_o, se_o, extra=("lnVIX_l1", "UST10Y_log_l1", "US_HY_spread_log_l1"), usar_lam=False)
            # observaciones con CDS de Indonesia, Filipinas y Sudáfrica fuera de la muestra principal
            r = raw.copy(); r = r[r["country"].isin(["indonesia", "philippines", "southafrica"])]
            r = r.merge(p45.gar_alt("gar_insample_h4.csv")[["country", "_qn", "Dalt"]], on=["country", "_qn"], how="left")
            princ = set(zip(d["country"], d["_qn"]))
            r = r.rename(columns={"CDS_bps": "spread", "D_pp": "D", "Dalt": "D4"})
            r["quarter"] = r["quarter"].astype(str)
            rr = rezagar(r[["country", "quarter", "spread", "JLoss", "D", "D4", "DEBT"]])
            rr = rr[[(c, q) not in princ for c, q in zip(rr["country"], rr["_qn"])]]
            estimar(rr, mom, lam, tcol, "N2cds", psi_o, se_o)
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(os.path.join(HERE, "paper_p57_numeros.csv"))
    for k, v in NUM.items():
        print(f"  {k:30s} {v: .4f}")


if __name__ == "__main__":
    main()
