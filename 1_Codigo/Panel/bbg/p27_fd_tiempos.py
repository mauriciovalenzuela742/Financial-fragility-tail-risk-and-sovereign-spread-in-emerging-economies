# -*- coding: utf-8 -*-
"""
p27_fd_tiempos.py -- ¿la fragilidad bancaria ANTICIPA al spread o se mueven dentro del mismo trimestre?

Objeción de árbitro al resultado en primeras diferencias de p21 (D.ln EMBI_t sobre D.ln JLoss_{t-1}:
0,037; p DK = 0,002; p wild = 0,007): el EMBI del panel es un PROMEDIO TRIMESTRAL, de modo que
D.promedio_t = promedio_t - promedio_{t-1} contiene mecánicamente los movimientos del spread ocurridos
DENTRO del trimestre t-1 (entre su promedio y su cierre), el mismo trimestre en que cambia JLoss_{t-1}
(agregación temporal, Working 1960). Este script separa la parte genuinamente predictiva de la mecánica.

CÓMO SE FORMA EL VALOR TRIMESTRAL DEL PANEL (p1_build_panels.embi_quarterly, panel embiext):
  - Fuente primaria 2_Datos/embi.xlsx: spread EMBI Global Diversified DIARIO (pb), 2000-01-03 a
    2026-07-16, una columna por país. El valor del panel es la MEDIA ARITMÉTICA de todos los días con
    dato del trimestre calendario (x.groupby("quarter").mean()); embi_source = "JPM_GD_xlsx".
  - Países con historia diaria completa desde 2000: Brasil, Chile, China, Colombia, Malasia, México,
    Perú, Polonia, Turquía. India empieza el 2012-10-31 (2012Q4 promedia solo noviembre-diciembre y no
    tiene "primer mes"). Filipinas, Indonesia y Sudáfrica solo tienen diario desde el 2023-07-27
    (2023Q3 es un trimestre parcial, sin "primer mes").
  - Con --embi-ext los trimestres sin dato diario se completan con 2_Datos/EMBI_real_8countries_2006_2014.csv
    (FMI, GFSR; embi_source = "GFSR"): Indonesia y Sudáfrica 2010Q1-2014Q4, 20 trimestres cada una, UN
    valor por trimestre, sin reescalar (embi_empalme_diag_bbg.csv). Para esas 40 observaciones NO hay
    dato diario: no se puede saber si son promedio o cierre ni construir medidas alternativas, y quedan
    fuera de la muestra común de este script. Filipinas no tiene tramo GFSR en la muestra de estimación.
  - El promedio del panel incluye los días con spread <= 0: Polonia tiene 19 (2021-02-25 a 2022-09-19,
    mínimo -36 pb) y 500 días bajo 30 pb; ahí el logaritmo exagera los cambios (cierre de 24 a 66 pb en
    2022). Por eso la batería quita Polonia 2021-2023 (2023 entra por los rezagos) y la forma en niveles
    sirve de contraste. Las medidas alternativas replican ese criterio (no filtran días <= 0).
  - 2026Q3 es un trimestre INCOMPLETO en el panel (datos hasta el 16 de julio): su "promedio" es el de
    11 días de julio. Aquí su cierre se declara faltante (no existe todavía).
  - El CDS a 5 años (CDS_bps) también es media trimestral de datos diarios (output_macro/<pais>/EMBI_<pais>.csv).

MEDIDAS TRIMESTRALES ALTERNATIVAS (en memoria y en embi_trimestral_alternativo.csv; NO se escriben al panel):
  avg  promedio de todos los días del trimestre (debe coincidir con EMBI_bps del panel),
  eop  cierre: media de los últimos 5 días hábiles con dato del trimestre (exige trimestre completo:
       último dato a 10 días o menos del fin de trimestre),
  m1   promedio del primer mes del trimestre (exige al menos 10 días con dato en ese mes).

QUÉ FECHAS ENTRAN EN JLoss DEL TRIMESTRE t (leído en 1_Codigo/JLoss_reconstruction/jloss_engine.py,
función quarterly_inputs, y en 1_Codigo/Bloomberg_extraction/bloomberg_common.py):
  - Capitalización bursátil: mktcap_end = ÚLTIMO dato diario del trimestre t (groupby(quarter).last()),
    es decir, el cierre del trimestre.
  - Volatilidad del patrimonio: volatilidad REALIZADA del trimestre t, raíz de la suma de retornos
    diarios al cuadrado de la capitalización dentro del trimestre (mínimo 5 retornos), anualizada con
    raíz de 4 en merton_pd. Ventana = los ~65 días hábiles del propio trimestre t.
  - Balance (D_star, total_liab): último registro del banco cuya columna `date` cae en el trimestre t,
    con arrastre máximo de un trimestre (FFILL_LIMIT = 1). En los CSV de Bloomberg esas fechas NO son
    fin de trimestre: son 27-feb, 27-may, 27-ago y 27-nov en 19 de 20 países (mediana de 92 días entre
    registros; Sudáfrica reporta semestral con fechas de fin de periodo). Son la malla trimestral que
    devuelve bdh con periodicidad QUARTERLY/ACTUAL anclada en la fecha final de la extracción
    (2026-08-27), no fechas de publicación. Lo que NO pude determinar con certeza desde el código es qué
    periodo fiscal contiene cada registro: lo más probable es que el valor fechado 27-ago (trimestre Q3)
    sea el último balance disponible a esa fecha, o sea el de cierre de junio (Q2), lo que implicaría
    un rezago de balance de un trimestre; el repositorio no guarda la fecha de periodo fiscal ni la de
    anuncio, así que no se puede verificar sin el Terminal.
  Consecuencia para los tiempos: JLoss_{t-1} queda fechado al CIERRE del trimestre t-1 (precio) con
  volatilidad acumulada durante t-1; D.JLoss_{t-1} recoge lo ocurrido dentro de t-1. La prueba limpia de
  anticipación es por tanto cierre_t - cierre_{t-1} sobre D.JLoss_{t-1}; el placebo de simultaneidad es
  cierre_{t-1} - cierre_{t-2} sobre D.JLoss_{t-1}. El riesgo de cola usa un índice de condiciones
  financieras de fin de mes (GaR/fci_engine.to_monthly_eom), o sea que D_{t-1} también es de cierre.

Bloques (especificación con EF de país y de tiempo, DK Bartlett; wild cluster bootstrap Webb):
  a. medidas trimestrales y cotejo con el panel;
  b. tabla en primeras diferencias con cinco variables dependientes (más la parte mecánica
     cierre_{t-1} - promedio_{t-1}, que con promedio_t - cierre_{t-1} suma exactamente D.promedio_t);
  c. robustez de tres especificaciones (tesis, limpia de cierre, simultánea);
  d. especificación PRINCIPAL en niveles con el spread de cierre;
  f. magnitud.

Salida: bbg/paper_tiempos_numeros.csv (o _nivlag) y bbg/embi_trimestral_alternativo.csv.
Reutiliza p13 (datos, fit) y p14 (base, wild_boot, DK).
"""
import os
import sys
import time
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
import p1_build_panels as p1
from causal_core import demean2

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
ROOT = p13.ROOT
GLOBAL = os.path.join(ROOT, "1_Codigo", "Bloomberg_extraction", "output_macro")
CRISIS = ["2008Q3", "2008Q4", "2009Q1", "2009Q2", "2020Q1", "2020Q2"]
NUM = {}
T0 = time.time()


def num(k, v):
    NUM[k] = float(v)
    return v


def F(x):
    """transformación de la forma funcional: logaritmo (principal) o nivel (JLOSS_FORMA=nivlag)."""
    return x if NIV else np.log(x.where(x > 0))


# ================================================================ a. medidas trimestrales
def trimestral(s, date, positivos=True):
    """s: Serie diaria; devuelve promedio, cierre (últimos 5 días) y primer mes, por trimestre.
    positivos=False replica p1.embi_quarterly: promedia TODOS los días, incluidos los de spread <= 0."""
    t = pd.DataFrame({"date": date, "v": s}).dropna()
    if positivos:
        t = t[t["v"] > 0]
    t = t.sort_values("date")
    t["q"] = t["date"].dt.to_period("Q")
    rows = []
    for q, g in t.groupby("q"):
        ult = g["date"].max()
        completo = (q.end_time.normalize() - ult).days <= 10
        m1 = g[g["date"].dt.month == q.start_time.month]["v"]
        rows.append(dict(quarter=str(q), avg=g["v"].mean(), n_dias=len(g), fecha_ultima=ult.date(),
                         eop=g["v"].tail(5).mean() if completo and len(g) >= 5 else np.nan,
                         m1=m1.mean() if len(m1) >= 10 else np.nan))
    return pd.DataFrame(rows)


def medidas_embi():
    x = pd.read_excel(p1.EMBI_XLSX).rename(columns={"Fecha": "date"})
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"])
    out = []
    for col, c in p1.EMBI_MAP.items():
        if col in x.columns:
            out.append(trimestral(x[col], x["date"], positivos=False).assign(country=c))
    return pd.concat(out, ignore_index=True)


def medidas_csv(path, col):
    s = pd.read_csv(path)
    s["DATES"] = pd.to_datetime(s["DATES"], dayfirst=True, errors="coerce")
    s = s.dropna()
    return trimestral(s[col], s["DATES"])


def medidas_cds(paises):
    out = []
    for c in paises:
        f = os.path.join(GLOBAL, c, f"EMBI_{c}.csv")       # el archivo se llama EMBI_ pero contiene CDS
        if os.path.isfile(f):
            out.append(medidas_csv(f, "EMBI").assign(country=c))
    return pd.concat(out, ignore_index=True)


# ================================================================ utilitarios de estimación
def L(W, col, k):
    """valor de `col` en el trimestre t-k del mismo país (k<0 adelanto); NaN si hay hueco."""
    s = W.set_index(["country", "_qn"])[col]
    idx = pd.MultiIndex.from_arrays([W["country"].to_numpy(), W["_qn"].to_numpy() - k])
    return s.reindex(idx).to_numpy()


def est(S, y, regs, bw=None):
    S = S.dropna(subset=[y] + regs)
    kw = dict(p14.DK) if bw is None else dict(p14.DK, bandwidth=bw)
    return PanelOLS(S.set_index(["country", "t"])[y], S.set_index(["country", "t"])[regs],
                    entity_effects=True, time_effects=True, drop_absorbed=True).fit(**kw)


def wb(S, y, regs, key, B=999):
    p, _ = p14.wild_boot(S.dropna(subset=[y] + regs), y, regs, key, B=B, weights="webb")
    return p


def r2_parcial(S, y, regs, key):
    """R2 parcial de `key` tras efectos fijos dobles y el resto de regresores."""
    S = S.dropna(subset=[y] + regs)
    Z = demean2(S, [y] + regs, iters=40)
    def ssr(cols):
        if not cols:
            return float((Z[y] ** 2).sum())
        X = Z[cols].to_numpy()
        b = np.linalg.lstsq(X, Z[y].to_numpy(), rcond=None)[0]
        return float(((Z[y].to_numpy() - X @ b) ** 2).sum())
    return 1.0 - ssr(regs) / ssr([r for r in regs if r != key])


def fila(pref, S, y, regs, noms, boot=None, B=999):
    """estima, guarda coeficiente y p DK de cada regresor nombrado y, si se pide, p wild."""
    m = est(S, y, regs)
    num(f"{pref}_N", m.nobs)
    for r, lab in noms.items():
        num(f"{pref}_{lab}", m.params[r]); num(f"{pref}_{lab}_p", m.pvalues[r])
        if boot and r in boot:
            num(f"{pref}_{lab}_p_wild", wb(S, y, regs, r, B=B))
    return m


# ================================================================ c. robustez
def robustez(S, y, xJ, xD, pref, ylag, gfac, extra_din):
    """batería sobre y ~ xJ + xD + EF dobles. Guarda el coeficiente de xJ (b) y el de xD (c)."""
    regs = [xJ, xD]
    nm = {xJ: "b", xD: "c"}
    S = S.dropna(subset=[y] + regs).copy()
    fila(f"{pref}_base", S, y, regs, nm)
    # adelantos (y, en las especificaciones rezagadas, el cambio contemporáneo)
    m = est(S, y, regs + extra_din)
    num(f"{pref}_lead_N", m.nobs); num(f"{pref}_lead_b", m.params[xJ]); num(f"{pref}_lead_b_p", m.pvalues[xJ])
    for r in extra_din:
        num(f"{pref}_lead_{r}", m.params[r]); num(f"{pref}_lead_{r}_p", m.pvalues[r])
    # rezago de la variable dependiente
    fila(f"{pref}_lagy", S, y, regs + [ylag], dict(nm, **{ylag: "rho"}))
    # cargas por país sobre los factores globales (contemporáneas; luego también rezagadas)
    paises = sorted(S["country"].unique())
    for lab, cols in (("fac", gfac[:2]), ("fac2", gfac)):
        X = S.copy(); nuevos = []
        for g in cols:
            for c in paises:
                X[f"{g}__{c}"] = X[g] * (X["country"] == c); nuevos.append(f"{g}__{c}")
        X = X.dropna(subset=cols)
        m = est(X, y, regs + nuevos)
        num(f"{pref}_{lab}_N", m.nobs)
        num(f"{pref}_{lab}_b", m.params[xJ]); num(f"{pref}_{lab}_b_p", m.pvalues[xJ])
        num(f"{pref}_{lab}_c", m.params[xD]); num(f"{pref}_{lab}_c_p", m.pvalues[xD])
    # sin crisis
    fila(f"{pref}_sincrisis", S[~S["quarter"].isin(CRISIS)], y, regs, nm)
    # sin Polonia 2021-2022: spread de 15-30 pb con días <= 0, donde el logaritmo exagera los cambios
    pol = (S["country"] == "poland") & S["t"].dt.year.isin([2021, 2022, 2023])
    num(f"{pref}_pol2122_quitadas", int(pol.sum()))
    fila(f"{pref}_sinpol2122", S[~pol], y, regs, nm)
    # dejar un país fuera
    bs, ps = [], []
    for c in paises:
        m = est(S[S["country"] != c], y, regs)
        bs.append(m.params[xJ]); ps.append(m.pvalues[xJ])
        if c in ("turkey", "poland"):
            num(f"{pref}_loo_sin_{c}_b", m.params[xJ]); num(f"{pref}_loo_sin_{c}_b_p", m.pvalues[xJ])
    num(f"{pref}_loo_min", min(bs)); num(f"{pref}_loo_max", max(bs)); num(f"{pref}_loo_n", len(bs))
    num(f"{pref}_loo_sig05", sum(p < 0.05 for p in ps)); num(f"{pref}_loo_sig10", sum(p < 0.10 for p in ps))
    num(f"{pref}_loo_pmax", max(ps))
    # dejar un año fuera
    bs, ps = [], []
    for a in sorted(S["t"].dt.year.unique()):
        m = est(S[S["t"].dt.year != a], y, regs)
        bs.append(m.params[xJ]); ps.append(m.pvalues[xJ])
    num(f"{pref}_loy_min", min(bs)); num(f"{pref}_loy_max", max(bs)); num(f"{pref}_loy_n", len(bs))
    num(f"{pref}_loy_sig05", sum(p < 0.05 for p in ps)); num(f"{pref}_loy_sig10", sum(p < 0.10 for p in ps))
    num(f"{pref}_loy_pmax", max(ps)); num(f"{pref}_loy_anio_pmax", sorted(S["t"].dt.year.unique())[int(np.argmax(ps))])
    # sin observaciones con JLoss en su piso (tres definiciones)
    for lab in ("piso", "masa216", "pisopais"):
        f = f"{lab}_{xJ}"
        num(f"{pref}_{lab}_quitadas", int(S[f].sum()))
        fila(f"{pref}_sin{lab}", S[~S[f]], y, regs, nm)


# ================================================================ main
def main():
    print("p27: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, dd = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4
    paises = sorted(d["country"].unique())
    muJ, muD = dd["ln_JLoss_l1"].mean(), dd["D_l1"].mean()

    # ---------- a. medidas trimestrales
    alt = medidas_embi()
    cds = medidas_cds(paises).rename(columns={"avg": "CDS_avg_diario", "eop": "CDS_eop5"})
    W = raw[raw["country"].isin(paises)].copy()
    W["t"] = pd.PeriodIndex(W["quarter"], freq="Q").to_timestamp()
    W = W.merge(alt, on=["country", "quarter"], how="left")
    W = W.merge(cds[["country", "quarter", "CDS_avg_diario", "CDS_eop5"]], on=["country", "quarter"], how="left")
    W = W.merge(dd[["country", "quarter"]].assign(in_est=True), on=["country", "quarter"], how="left")
    W["in_est"] = W["in_est"].fillna(False).astype(bool)
    W = W.sort_values(["country", "_qn"]).reset_index(drop=True)
    cols = ["country", "quarter", "EMBI_bps", "embi_source", "avg", "eop", "m1", "n_dias", "fecha_ultima",
            "CDS_bps", "CDS_eop5"]
    if not NIV:
        (W[cols].rename(columns={"EMBI_bps": "EMBI_panel", "avg": "EMBI_avg_diario", "eop": "EMBI_eop5",
                             "m1": "EMBI_m1", "CDS_bps": "CDS_panel"})
         .dropna(subset=["EMBI_panel", "EMBI_avg_diario"], how="all")
         .to_csv(os.path.join(HERE, "embi_trimestral_alternativo.csv"), index=False))

    e = W[W["in_est"]]
    x = e[e["embi_source"] == "JPM_GD_xlsx"].dropna(subset=["avg"])
    num("a_est_N", len(e)); num("a_est_xlsx", (e["embi_source"] == "JPM_GD_xlsx").sum())
    num("a_est_gfsr", (e["embi_source"] == "GFSR").sum())
    num("a_avg_corr_panel", np.corrcoef(x["avg"], x["EMBI_bps"])[0, 1])
    num("a_avg_maxgap_pb", (x["avg"] - x["EMBI_bps"]).abs().max())
    num("a_est_con_eop", e["eop"].notna().sum()); num("a_est_con_m1", e["m1"].notna().sum())
    num("a_est_trim_incompletos", (e["avg"].notna() & e["eop"].isna()).sum())
    num("a_corr_eop_avg", e[["eop", "avg"]].corr().iloc[0, 1]); num("a_corr_m1_avg", e[["m1", "avg"]].corr().iloc[0, 1])
    num("a_dias_mediana", x["n_dias"].median())
    print("  observaciones GFSR en la muestra:", e[e.embi_source == "GFSR"].groupby("country")["quarter"].agg(["min", "max", "count"]).to_dict("index"))
    print("  sin cierre con promedio:", e[e["avg"].notna() & e["eop"].isna()][["country", "quarter"]].values.tolist())
    print("  sin primer mes con promedio:", e[e["avg"].notna() & e["m1"].isna()][["country", "quarter"]].values.tolist())
    c2 = e.dropna(subset=["CDS_bps", "CDS_avg_diario"])
    num("a_cds_corr_panel", np.corrcoef(c2["CDS_bps"], c2["CDS_avg_diario"])[0, 1])

    # ---------- variables
    W["y"] = F(W["EMBI_bps"]); W["ye"] = F(W["eop"]); W["ym"] = F(W["m1"])
    W["cy"] = F(W["CDS_bps"]); W["ce"] = F(W["CDS_eop5"])
    W["J"] = W["ln_JLoss"]; W["D"] = W["D_pp"]
    W["X"] = (W["J"] - muJ) * (W["D"] - muD)
    for v in ("J", "D", "X"):
        W[f"d{v}1"] = L(W, v, 1) - L(W, v, 2)          # cambio en t-1
        W[f"d{v}0"] = W[v] - L(W, v, 1)                # cambio contemporáneo
        W[f"d{v}f"] = L(W, v, -1) - W[v]               # cambio adelantado
    W["dy_avg"] = W["y"] - L(W, "y", 1)                # tesis
    W["dy_eop"] = W["ye"] - L(W, "ye", 1)              # cierre a cierre
    W["dy_avg_eop"] = W["y"] - L(W, "ye", 1)           # promedio_t menos cierre_{t-1}
    W["dy_m1_eop"] = W["ym"] - L(W, "ye", 1)           # primer mes_t menos cierre_{t-1}
    W["dy_plac"] = L(W, "ye", 1) - L(W, "ye", 2)       # placebo: mismo trimestre que D.J_{t-1}
    W["dy_mec"] = L(W, "ye", 1) - L(W, "y", 1)         # parte mecánica: cierre_{t-1} - promedio_{t-1}
    W["dy_avg_l1"] = L(W, "dy_avg", 1); W["dy_eop_l1"] = L(W, "dy_eop", 1)
    W["dcy"] = W["cy"] - L(W, "cy", 1); W["dce"] = W["ce"] - L(W, "ce", 1)
    W["in_est_l1"] = pd.Series(L(W, "in_est", 1)).fillna(False).astype(bool).to_numpy()
    # factores globales: promedio trimestral (panel) y cierre (diario de Bloomberg)
    g = W[["_qn", "quarter", "VIX", "US_HY_spread"]].drop_duplicates("_qn").sort_values("_qn")
    for nm_, f_, c_ in (("VIX", "VIX.csv", "VIX"), ("HY", "HY_SPREAD.csv", "HY_SPREAD")):
        q = medidas_csv(os.path.join(GLOBAL, "GLOBAL", f_), c_)[["quarter", "eop"]].rename(columns={"eop": nm_ + "_eop"})
        g = g.merge(q, on="quarter", how="left")
    g = g.set_index("_qn")
    for nm_, col in (("vix_avg", "VIX"), ("hy_avg", "US_HY_spread"), ("vix_eop", "VIX_eop"), ("hy_eop", "HY_eop")):
        s = F(g[col])
        ds = s - s.reindex(s.index - 1).to_numpy()
        W["d_" + nm_] = W["_qn"].map(ds)
        W["d_" + nm_ + "_l1"] = W["_qn"].map(pd.Series(ds.to_numpy(), index=ds.index + 1))
    # pisos de JLoss
    JL = W["JLoss"]
    jmin = JL[W["in_est"] | W["in_est_l1"]].min()
    num("piso_min_panel", JL.min()); num("piso_min_muestra", jmin)
    W["f_piso"] = JL <= 1.02 * JL.min()
    W["f_masa216"] = (JL / 2.16 - 1).abs() < 0.002          # 2,16 = 0,048 x 0,45 x 100: techo de la malla VaR
    W["f_pisopais"] = JL <= 1.02 * JL.groupby(W["country"]).transform("min")
    for lab in ("piso", "masa216", "pisopais"):
        a0 = W["f_" + lab].astype(float)
        W["_a"] = a0
        l1, l2 = np.nan_to_num(L(W, "_a", 1)), np.nan_to_num(L(W, "_a", 2))
        W[f"{lab}_dJ1"] = (l1 + l2) > 0
        W[f"{lab}_dJ0"] = (a0.to_numpy() + l1) > 0
        num(f"{lab}_obs_nivel_muestra", int(W.loc[W["in_est"], "_a"].pipe(lambda s: np.nan_to_num(L(W, "_a", 1))[W["in_est"].to_numpy()].sum())))
    W = W.drop(columns="_a")

    tes = W[W["in_est"] & W["in_est_l1"]].copy()
    com = tes.dropna(subset=["dy_avg", "dy_eop", "dy_avg_eop", "dy_m1_eop", "dy_plac", "dy_mec", "dJ1", "dD1", "dX1"]).copy()
    num("b_N_tesis", len(tes.dropna(subset=["dy_avg", "dJ1", "dD1", "dX1"]))); num("b_N_comun", len(com))
    num("b_paises_comun", com["country"].nunique())
    print("  muestra comun por pais:", com.groupby("country").size().to_dict())

    # ---------- b. tabla en primeras diferencias
    R2, R3 = ["dJ1", "dD1"], ["dJ1", "dD1", "dX1"]
    n2, n3 = {"dJ1": "b1", "dD1": "b2"}, {"dJ1": "b1", "dD1": "b2", "dX1": "b3"}
    # réplica de p21 (muestra de la tesis, con interacción) como control de construcción
    m = fila("b_tesis_full_int", tes, "dy_avg", R3, n3)
    if not NIV:
        assert abs(m.params["dJ1"] - 0.0368) < 5e-4, m.params["dJ1"]
    fila("b_tesis_full", tes, "dy_avg", R2, n2, boot=R2, B=1999)
    deps = (("avg", "dy_avg", 1999), ("eop", "dy_eop", 1999), ("avg_eop", "dy_avg_eop", 999),
            ("m1_eop", "dy_m1_eop", 999), ("plac", "dy_plac", 1999), ("mec", "dy_mec", 999))
    for lab, y, B in deps:
        fila(f"b_{lab}", com, y, R2, n2, boot=R2, B=B)
        fila(f"b_{lab}_int", com, y, R3, n3, boot=["dJ1", "dX1"], B=999)
        num(f"b_{lab}_sd_y", demean2(com, [y], iters=40)[y].std())
        print(f"  [b] {lab:8s} b1={NUM[f'b_{lab}_b1']: .4f} pDK={NUM[f'b_{lab}_b1_p']:.3f} pW={NUM[f'b_{lab}_b1_p_wild']:.3f}"
              f" | b2={NUM[f'b_{lab}_b2']: .4f} pDK={NUM[f'b_{lab}_b2_p']:.3f}  ({time.time() - T0:.0f}s)")
    # cierre_t - cierre_{t-1} sobre el cambio contemporáneo y el rezagado a la vez
    S = tes.dropna(subset=["dy_eop", "dJ0", "dD0", "dJ1", "dD1"])
    R4 = ["dJ0", "dJ1", "dD0", "dD1"]
    fila("b_eop_ambos", S, "dy_eop", R4, {"dJ0": "J0", "dJ1": "J1", "dD0": "D0", "dD1": "D1"}, boot=R4, B=999)
    fila("b_eop_cont", S, "dy_eop", ["dJ0", "dD0"], {"dJ0": "J0", "dD0": "D0"}, boot=["dJ0", "dD0"], B=1999)
    fila("b_avg_ambos", S, "dy_avg", R4, {"dJ0": "J0", "dJ1": "J1", "dD0": "D0", "dD1": "D1"})
    # muestra máxima de cada medida (sin exigir la muestra común)
    fila("b_eop_max", tes, "dy_eop", R2, n2)
    fila("b_avg_sin_gfsr", tes[(tes["embi_source"] == "JPM_GD_xlsx") & (pd.Series(L(W, "embi_source", 1), index=W.index).reindex(tes.index) == "JPM_GD_xlsx")],
         "dy_avg", R2, n2)
    num("b_avg_gfsr_quitadas", NUM["b_tesis_full_N"] - NUM["b_avg_sin_gfsr_N"])
    print(f"  [b] listo ({time.time() - T0:.0f}s)")

    # ---------- c. robustez
    robustez(com, "dy_avg", "dJ1", "dD1", "c_avg", "dy_avg_l1",
             ["d_vix_avg", "d_hy_avg", "d_vix_avg_l1", "d_hy_avg_l1"], ["dJ0", "dD0", "dJf", "dDf"])
    robustez(com, "dy_eop", "dJ1", "dD1", "c_eop", "dy_eop_l1",
             ["d_vix_eop", "d_hy_eop", "d_vix_eop_l1", "d_hy_eop_l1"], ["dJ0", "dD0", "dJf", "dDf"])
    robustez(tes.dropna(subset=["dy_eop", "dJ0", "dD0"]), "dy_eop", "dJ0", "dD0", "c_cont", "dy_eop_l1",
             ["d_vix_eop", "d_hy_eop", "d_vix_eop_l1", "d_hy_eop_l1"], ["dJ1", "dD1", "dJf", "dDf"])
    # CDS como variable dependiente (promedio del panel y cierre construido del diario)
    fila("c_cds_avg", tes, "dcy", R2, n2, boot=["dJ1"], B=999)
    fila("c_cds_eop", tes, "dce", R2, n2, boot=["dJ1"], B=999)
    fila("c_cds_eop_cont", tes, "dce", ["dJ0", "dD0"], {"dJ0": "J0", "dD0": "D0"}, boot=["dJ0"], B=999)
    print(f"  [c] listo ({time.time() - T0:.0f}s)")

    # ---------- d. especificación principal en niveles con el spread de cierre
    dl = d.merge(W[["country", "quarter", "ye", "ym"]], on=["country", "quarter"], how="left")
    for lab, col, sub, B in (("avg", "ln_EMBI", ["ye"], 999), ("eop", "ye", ["ye"], 1999),
                             ("m1", "ym", ["ym"], 999), ("avg_m1", "ln_EMBI", ["ym"], 0)):
        x = dl.dropna(subset=sub).copy()
        x["ln_EMBI"] = x[col]
        m, xx = p13.fit(x)
        num(f"d_{lab}_N", m.nobs)
        for r, k in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
            num(f"d_{lab}_{k}", m.params[r]); num(f"d_{lab}_{k}_se", m.std_errors[r]); num(f"d_{lab}_{k}_p", m.pvalues[r])
            if B:
                num(f"d_{lab}_{k}_p_wild", wb(xx, "ln_EMBI", ["J_c", "T_c", "JxT"], r, B=B))
        print(f"  [d] {lab:6s} N={int(m.nobs)} b1={m.params['J_c']: .4f} ({m.pvalues['J_c']:.3f}) "
              f"b2={m.params['T_c']: .4f} ({m.pvalues['T_c']:.3f}) b3={m.params['JxT']: .4f} ({m.pvalues['JxT']:.3f})")
    for r, k in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"d_principal_{k}", m0.params[r]); num(f"d_principal_{k}_p", m0.pvalues[r])

    # ---------- f. magnitud
    # desviación estándar within-país (se resta solo la media de cada país)
    Zc = com[["dJ1", "dy_avg", "dy_eop"]] - com.groupby("country")[["dJ1", "dy_avg", "dy_eop"]].transform("mean")
    sdJ = Zc["dJ1"].std()
    num("f_sd_dJ_within", sdJ); num("f_absmed_dJ", com["dJ1"].abs().median()); num("f_absmean_dJ", com["dJ1"].abs().mean())
    num("f_sd_dJ_2way", demean2(com, ["dJ1"], iters=40)["dJ1"].std())
    num("f_embi_medio_pb", com["EMBI_bps"].mean()); num("f_embi_mediano_pb", com["EMBI_bps"].median())
    for lab, y, pref in (("avg", "dy_avg", "b_avg"), ("eop", "dy_eop", "b_eop"), ("plac", "dy_plac", "b_plac")):
        b = NUM[f"{pref}_b1"]
        ef = b * sdJ
        num(f"f_{lab}_efecto_1sd", ef)
        num(f"f_{lab}_efecto_pb", ef if NIV else ef * com["EMBI_bps"].mean())
        num(f"f_{lab}_efecto_pct", (ef / com["EMBI_bps"].mean() if NIV else ef) * 100)
        sdy = (com[y] - com.groupby("country")[y].transform("mean")).std()
        num(f"f_{lab}_sd_dy_within", sdy); num(f"f_{lab}_efecto_en_sd", ef / sdy)
        num(f"f_{lab}_r2parcial_dJ", r2_parcial(com, y, R2, "dJ1")); num(f"f_{lab}_r2parcial_dD", r2_parcial(com, y, R2, "dD1"))
    S = tes.dropna(subset=["dy_eop", "dJ0", "dD0"])
    num("f_cont_r2parcial_dJ", r2_parcial(S, "dy_eop", ["dJ0", "dD0"], "dJ0"))
    num("f_cont_efecto_1sd", NUM["b_eop_cont_J0"] * sdJ)

    out = os.path.join(HERE, f"paper_tiempos_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        sys.stdout.buffer.write(f"  {k:34s} {v: .4f}\n".encode("ascii", "replace"))
    print("->", out, f"({time.time() - T0:.0f}s)")


if __name__ == "__main__":
    main()
