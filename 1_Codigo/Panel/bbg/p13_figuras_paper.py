# -*- coding: utf-8 -*-
"""
p13_figuras_paper.py -- figuras y tablas descriptivas del paper empirico con la especificacion
PRINCIPAL log-log rezagada sobre el panel con EMBI extendido (Panel_bloomberg_embiext.csv):

    ln EMBI_{i,t} = a_i + d_t + b1 ln JLoss_{i,t-1} + b2 D_{i,t-1} + b3 ln JLoss_{i,t-1} x D_{i,t-1} + e
    D = -GaR (pp), ln JLoss y D centrados, errores Driscoll-Kraay (Bartlett).
    Regresion principal = columna (1) del Panel A de tablas_regresiones_lnlag_embiext.tex
    (sin controles); el Panel C (con los 6 controles) es robustez.

Reproduce, con datos actualizados, las 13 figuras del Avance 1 (2026-06-26) y actualiza las
figuras que el paper ya tenia (cobertura, JLoss/D por pais, co-movimiento, efecto marginal por
regimen de crisis, ventanas moviles). NO sobrescribe ninguna figura existente: todo se escribe
con sufijo _lnlag (regresiones) o _embiext (descriptivas) en 4_Redaccion/envios/paper_empirico/figuras/.

Salidas:
  figuras/*.pdf + *.png                     (paper_empirico/figuras)
  tablas_regresiones/tabla_descriptivos_embiext.tex   (Cuadros descriptivos 1-3 del Avance 1)
  bbg/paper_lnlag_numeros.csv               (toda cifra citada en el texto del paper)

Uso:  python p13_figuras_paper.py      (fija JLOSS_PANEL_CSV al panel embiext si no esta fijada)
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from linearmodels.panel import PanelOLS
from scipy import stats
from scipy.special import gammaln
from scipy.integrate import cumulative_trapezoid

import p4_figuras as p4                      # paleta y rcParams del resto de la tesis
import p9b_bateria_crisis as p9b
import p12_tablas_latex_lnlag as p12
from p2_regresiones import CTRLS

assert os.path.basename(os.environ["JLOSS_PANEL_CSV"]) == "Panel_bloomberg_embiext.csv", \
    "p13 se corre sobre el panel con EMBI extendido"

BLUE, ORANGE, RED, INK, INK2, GRID = p4.BLUE, p4.ORANGE, p4.RED, p4.INK, p4.INK2, p4.GRID
GREEN = "#2e9d6a"
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FIG = os.path.join(ROOT, "4_Redaccion", "envios", "paper_empirico", "figuras")
TAB = os.path.join(ROOT, "4_Redaccion", "tablas_regresiones")
os.makedirs(FIG, exist_ok=True)

GFC, COVID, EM1516 = p9b.GFC, p9b.COVID, p9b.EM1516
CRISIS_BAT = GFC + COVID                           # muestra "sin crisis" de la Tabla 1
NUCLEO_EXCL = ["poland", "india"]
NOMBRE = {"brazil": "Brasil", "chile": "Chile", "china": "China", "colombia": "Colombia",
          "india": "India", "indonesia": "Indonesia", "malaysia": "Malasia", "mexico": "México",
          "peru": "Perú", "philippines": "Filipinas", "poland": "Polonia",
          "southafrica": "Sudáfrica", "turkey": "Turquía", "russia": "Rusia", "egypt": "Egipto",
          "argentina": "Argentina", "pakistan": "Pakistán"}
NUM = {}                                           # cifras citadas en el texto -> csv


def num(key, value):
    NUM[key] = float(value)
    return value


def save(fig, name):
    fig.tight_layout()
    for ext in ("pdf", "png"):
        out = os.path.join(FIG, f"{name}.{ext}")
        fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}")


# ================================================================ datos
def datos():
    """Panel de estimacion de la especificacion principal: ln EMBI_t, ln JLoss_{t-1}, D_{t-1}
    (misma construccion de rezagos que p12._base_lag: exige trimestre anterior sin hueco)."""
    d = p12._base_lag()
    d = d.sort_values(["country", "quarter"]).copy()
    q = pd.PeriodIndex(d["quarter"], freq="Q")
    d["t"] = q.to_timestamp()
    d["D_l1"] = -d["GaR_pp_l1"]
    # rezagos adicionales que usan las figuras (mismo criterio de consecutividad)
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw["ES_pp"] = raw["ES"] * 100.0
    rq = pd.PeriodIndex(raw["quarter"], freq="Q")
    raw["_qn"] = rq.year * 4 + rq.quarter
    raw = raw.sort_values(["country", "_qn"])
    gr = raw.groupby("country")
    consec = (raw["_qn"] - gr["_qn"].shift(1)) == 1
    raw["ES_l1"] = gr["ES_pp"].shift(1).where(consec)
    raw["prob_neg_l1"] = gr["prob_neg"].shift(1).where(consec)
    d = d.merge(raw[["country", "quarter", "ES_l1", "prob_neg_l1"]], on=["country", "quarter"], how="left")
    d["DES_l1"] = -d["ES_l1"]      # cola con Expected Shortfall en forma D (mayor = cola mas adversa)
    return d


def fit(dd, fe="PT", tail="D_l1", ctr=(), cov="dk", extra=None):
    """M4 en forma D: ln EMBI ~ lnJ_c + T_c + lnJ_c*T_c (+ ctr) + FE. Devuelve (modelo, datos)."""
    ctr = list(ctr)
    dd = dd.dropna(subset=["ln_EMBI", "ln_JLoss_l1", tail] + ctr).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd[tail] - dd[tail].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    rhs = ["J_c", "T_c", "JxT"] + ctr + (extra or [])
    eff = {"T": "TimeEffects", "P": "EntityEffects", "PT": "EntityEffects + TimeEffects"}[fe]
    kw = (dict(cov_type="kernel", kernel="bartlett") if cov == "dk" else
          dict(cov_type="clustered", cluster_entity=True) if cov == "pais" else
          dict(cov_type="clustered", cluster_time=True))
    m = PanelOLS.from_formula(f"ln_EMBI ~ {' + '.join(rhs)} + {eff}",
                              dd.set_index(["country", "t"])).fit(**kw)
    return m, dd


def estimar_principal(d):
    m, dd = fit(d)
    # debe reproducir la columna (1) del Panel A de la Tabla 1 (p12 / p8.fit_one en forma GaR)
    assert int(m.nobs) == 765 and abs(m.params["JxT"] - (-0.0112)) < 5e-4, (m.nobs, m.params["JxT"])
    for k, n in (("b1", "J_c"), ("b2", "T_c"), ("b3", "JxT")):
        num(f"principal_{k}", m.params[n]); num(f"principal_{k}_se", m.std_errors[n])
        num(f"principal_{k}_p", m.pvalues[n])
    num("principal_N", m.nobs); num("principal_R2w", m.rsquared_within)
    return m, dd


# ================================================================ descriptivas
def fig_cobertura(d):
    cov = pd.read_csv(os.path.join(HERE, "cobertura_panel_bbg_embiext.csv"))
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw["t"] = pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()
    est_c = d.groupby("country").size()
    order = cov.assign(n=cov["country"].map(est_c).fillna(0)).sort_values("n")["country"].tolist()
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for i, c in enumerate(order):
        g = raw[raw.country == c]
        e = d[d.country == c]
        gf = g.dropna(subset=["EMBI_bps"])
        ext = gf[gf["embi_source"] != "JPM_GD_xlsx"]
        ax.plot(g.dropna(subset=["JLoss"])["t"], [i] * g["JLoss"].notna().sum(), "|", color=GRID, ms=7, mew=2)
        ax.plot(gf["t"], [i] * len(gf), "|", color="#9ec5f4", ms=7, mew=2)
        ax.plot(e["t"], [i] * len(e), "|", color=BLUE, ms=7, mew=2)
        if len(ext):
            ax.plot(ext["t"], [i + 0.32] * len(ext), "v", color=ORANGE, ms=3.5)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([f"{NOMBRE.get(c, c)} ({int(est_c.get(c, 0))})" for c in order], fontsize=8)
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Line2D([], [], color=GRID, marker="|", ls="", ms=9, mew=2.5, label="JLoss"),
                       Line2D([], [], color="#9ec5f4", marker="|", ls="", ms=9, mew=2.5, label="+ EMBI"),
                       Line2D([], [], color=BLUE, marker="|", ls="", ms=9, mew=2.5,
                              label="muestra de estimación (ln EMBI, rezagos de JLoss y D)"),
                       Line2D([], [], color=ORANGE, marker="v", ls="", ms=5,
                              label="EMBI completado con FMI (GFSR)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)
    ax.set_title(f"Cobertura del panel: {d.country.nunique()} economías, {len(d)} observaciones "
                 "país-trimestre (entre paréntesis, trimestres por país)", fontsize=9)
    num("muestra_N", len(d)); num("muestra_paises", d.country.nunique())
    save(fig, "fig_cobertura_embiext")


def gaps(g):
    """Reindexa un pais a todos los trimestres entre su primero y su ultimo, con NaN donde falta,
    para que las lineas y areas se corten en los huecos (IDN/ZAF 2015-2023) en vez de unirlos."""
    q = pd.PeriodIndex(g["quarter"], freq="Q")
    full = pd.period_range(q.min(), q.max(), freq="Q")
    g = g.set_index(q).reindex(full)
    g["t"] = full.to_timestamp()
    return g


def _grid(n, ncol=5, h=2.0, w=11.5):
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(w, h * nrow), sharex=True)
    return fig, axes.ravel()


def fig_jloss_d_paises(d):
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw["t"] = pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()
    raw["D_pp"] = -raw["GaR_pp"]
    cs = sorted(d.country.unique())
    for var, lab, name in (("JLoss", "JLoss trimestral por país", "fig_jloss_paises_embiext"),
                           ("D_pp", "D = −GaR trimestral por país (pp; más alto = cola más adversa)",
                            "fig_gar_paises_embiext")):
        fig, axes = _grid(len(cs))
        for ax, c in zip(axes, cs):
            g = raw[raw.country == c].dropna(subset=[var]).sort_values("t")
            ax.axhline(0, color=INK2, lw=0.5)
            ax.plot(g["t"], g[var], color=BLUE, lw=1.3)
            ax.fill_between(g["t"], 0, g[var], color=BLUE, alpha=0.12, lw=0)
            e = d[d.country == c]
            if len(e):
                ax.axvspan(e["t"].min(), e["t"].max(), color=ORANGE, alpha=0.06, lw=0)
            ax.set_title(NOMBRE[c], fontsize=8.5)
        for ax in axes[len(cs):]:
            ax.set_visible(False)
        fig.suptitle(lab + " — sombreado: ventana de estimación", y=1.005, fontsize=10.5)
        save(fig, name)


def fig_comovimiento(d):
    z = lambda s: (s - s.mean()) / s.std()
    g = d.assign(Dz=z(d["D_l1"]), Jz=z(d["ln_JLoss_l1"]), Ez=z(d["ln_EMBI"]))
    g = g.groupby("t")[["Dz", "Jz", "Ez"]].median().sort_index()
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.axhline(0, color=INK2, lw=0.8)
    for t0, t1 in ((GFC[0], GFC[-1]), (EM1516[0], EM1516[-1]), (COVID[0], COVID[-1])):
        ax.axvspan(pd.Period(t0).to_timestamp(), pd.Period(t1).to_timestamp("Q"), color=INK2, alpha=0.08, lw=0)
    ax.plot(g.index, g["Dz"], color=BLUE, lw=1.8, label="D$_{t-1}$ = −GaR$_{t-1}$")
    ax.plot(g.index, g["Jz"], color=ORANGE, lw=1.8, label="ln JLoss$_{t-1}$")
    ax.plot(g.index, g["Ez"], color=RED, lw=1.8, label="ln EMBI$_t$")
    ax.set_ylabel("z-score (mediana transversal por trimestre)")
    ax.set_title("Co-movimiento agregado: riesgo de cola, fragilidad bancaria y spread soberano "
                 "(sombreado: vector de crisis)", fontsize=9.5)
    ax.legend(loc="upper left", fontsize=8.5)
    for a, b in (("Dz", "Ez"), ("Jz", "Ez"), ("Dz", "Jz")):
        num(f"comov_corr_{a}_{b}", g[a].corr(g[b]))
    save(fig, "fig_comovimiento_embiext")


def fig_distribuciones(d):
    vs = [("EMBI_bps", "EMBI (pb)"), ("ln_EMBI", "ln EMBI"), ("JLoss_l1", "JLoss$_{t-1}$"),
          ("ln_JLoss_l1", "ln JLoss$_{t-1}$"), ("D_l1", "D$_{t-1}$ = −GaR (pp)"),
          ("ES_l1", "Expected Shortfall$_{t-1}$ (pp)")]
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.6))
    for ax, (v, lab) in zip(axes.ravel(), vs):
        s = d[v].dropna()
        ax.hist(s, bins=40, color=BLUE, alpha=0.75, density=True)
        kde = stats.gaussian_kde(s)
        xs = np.linspace(s.min(), s.max(), 200)
        ax.plot(xs, kde(xs), color=INK, lw=1.2)
        ax.axvline(s.mean(), color=RED, lw=1)
        ax.set_title(f"{lab}\nasimetría {stats.skew(s):+.2f} · curtosis {stats.kurtosis(s, fisher=False):.1f}",
                     fontsize=8.5)
        num(f"skew_{v}", stats.skew(s)); num(f"kurt_{v}", stats.kurtosis(s, fisher=False))
    fig.suptitle("Distribuciones univariadas de la muestra de estimación (línea roja = media)", y=1.01)
    save(fig, "fig_distribuciones_embiext")


CORR_VARS = [("ln_EMBI", "ln EMBI"), ("ln_JLoss_l1", "ln JLoss$_{t-1}$"), ("D_l1", "D$_{t-1}$"),
             ("ES_l1", "ES$_{t-1}$"), ("prob_neg_l1", "P(crec.<0)$_{t-1}$"), ("debt_gdp", "Deuda/PIB"),
             ("fisc_bal", "Bal. fiscal/PIB"), ("res_gdp", "Reservas/PIB"), ("ca_gdp", "C. corriente/PIB"),
             ("infl_yoy", "Inflación"), ("reer", "TCR"), ("VIX", "VIX")]


def fig_correlaciones(d):
    cols = [c for c, _ in CORR_VARS]
    C = d[cols].corr()
    mask = np.triu(np.ones_like(C, dtype=bool), 1)
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    im = ax.imshow(np.ma.array(C.values, mask=mask), cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(len(cols)):
        for j in range(i + 1):
            ax.text(j, i, f"{C.values[i, j]:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(C.values[i, j]) > 0.6 else INK)
    labs = [l for _, l in CORR_VARS]
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(labs, rotation=60, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(cols))); ax.set_yticklabels(labs, fontsize=7.5)
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Matriz de correlaciones (muestra de estimación)")
    num("corr_lnJ_fiscbal", C.loc["ln_JLoss_l1", "fisc_bal"]); num("corr_lnJ_D", C.loc["ln_JLoss_l1", "D_l1"])
    num("corr_D_ES", C.loc["D_l1", "ES_l1"]); num("corr_lnJ_reer", C.loc["ln_JLoss_l1", "reer"])
    save(fig, "fig_correlaciones_embiext")


def fig_comov_pais(d):
    cs = sorted(d.country.unique())
    fig, axes = _grid(len(cs), h=2.1)
    for ax, c in zip(axes, cs):
        g = gaps(d[d.country == c].sort_values("t"))
        for v, col, lab in (("ln_EMBI", RED, "ln EMBI"), ("ln_JLoss_l1", ORANGE, "ln JLoss$_{t-1}$"),
                            ("D_l1", BLUE, "D$_{t-1}$")):
            s = g[v]
            ax.plot(g["t"], (s - s.mean()) / s.std(), color=col, lw=1.1, label=lab)
        ax.axhline(0, color=INK2, lw=0.5)
        ax.set_title(NOMBRE[c], fontsize=8.5)
    for ax in axes[len(cs):]:
        ax.set_visible(False)
    axes[0].legend(fontsize=6.5, loc="upper left")
    fig.suptitle("Co-movimiento estandarizado por país (z-score dentro de cada país)", y=1.005, fontsize=10.5)
    save(fig, "fig_comov_pais_embiext")


def fig_skewt_chile():
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    ch = raw[raw.country == "chile"].dropna(subset=["GaR", "scale_st", "skew_st", "nu_st", "gar_mean"]).copy()

    def pdf(y, xi, om, al, nu):
        z = (y - xi) / om
        return (2 / om) * stats.t.pdf(z, nu) * stats.t.cdf(al * z * np.sqrt((nu + 1) / (z ** 2 + nu)), nu + 1)

    def xi_mean(mean, om, al, nu):
        delta = al / np.sqrt(1 + al ** 2)
        b = np.sqrt(nu / np.pi) * np.exp(gammaln((nu - 1) / 2) - gammaln(nu / 2))
        return mean - om * delta * b

    q_st = ch.loc[ch["GaR"].idxmin(), "quarter"]
    q_bn = ch.loc[(ch["GaR"] - ch["GaR"].median()).abs().idxmin(), "quarter"]
    y = np.linspace(-0.22, 0.15, 800)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for q, col, lab in ((q_bn, GREEN, f"Benigno ({q_bn})"), (q_st, RED, f"Estrés ({q_st})")):
        r = ch[ch.quarter == q].iloc[0]
        dens = pdf(y, xi_mean(r["gar_mean"], r["scale_st"], r["skew_st"], r["nu_st"]),
                   r["scale_st"], r["skew_st"], r["nu_st"])
        ax.plot(y * 100, dens / 100, color=col, lw=2, label=lab)
        tail = y <= r["GaR"]
        ax.fill_between(y[tail] * 100, dens[tail] / 100, color=col, alpha=0.25)
        ax.axvline(r["GaR"] * 100, color=col, ls="--", lw=1)
        ax.axvline(r["ES"] * 100, color=col, ls=":", lw=1)
        cdf = cumulative_trapezoid(dens, y, initial=0); cdf /= cdf[-1]
        num(f"skewt_{'estres' if col == RED else 'benigno'}_GaR_pp", r["GaR"] * 100)
        num(f"skewt_{'estres' if col == RED else 'benigno'}_q05_skewt_pp", y[np.searchsorted(cdf, 0.05)] * 100)
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set_xlabel("crecimiento trimestral del PIB un trimestre adelante (pp)")
    ax.set_ylabel("densidad condicional")
    ax.set_title("Densidad condicional skew-t del crecimiento — Chile\n"
                 "discontinua = GaR (cuantil 5 %); punteada = Expected Shortfall; área = 5 % de cola",
                 fontsize=9.5)
    ax.legend()
    save(fig, "fig_skewt_chile_embiext")


def fig_series_pais(d):
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw["t"] = pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()
    raw["D_pp"] = -raw["GaR_pp"]
    cs = sorted(d.country.unique())
    fig, axes = _grid(len(cs), h=2.3, w=13)
    for ax, c in zip(axes, cs):
        e = d[d.country == c]
        g = raw[(raw.country == c) & (raw.t >= e["t"].min() - pd.Timedelta(days=370))].sort_values("t")
        for t0, t1 in ((GFC[0], GFC[-1]), (EM1516[0], EM1516[-1]), (COVID[0], COVID[-1])):
            ax.axvspan(pd.Period(t0).to_timestamp(), pd.Period(t1).to_timestamp("Q"),
                       color=INK2, alpha=0.10, lw=0)
        ax.plot(g["t"], g["JLoss"], color=RED, lw=1.2)
        ax.tick_params(axis="y", colors=RED, labelsize=6)
        a2 = ax.twinx(); a2.plot(g["t"], g["D_pp"], color=GREEN, lw=1.0)
        a2.tick_params(axis="y", colors=GREEN, labelsize=6); a2.grid(False)
        a3 = ax.twinx(); a3.spines["right"].set_position(("outward", 22))
        a3.plot(g["t"], g["EMBI_bps"], color=BLUE, lw=1.0, ls="--")
        a3.tick_params(axis="y", colors=BLUE, labelsize=6); a3.grid(False)
        ax.set_title(NOMBRE[c], fontsize=8.5)
        ax.tick_params(axis="x", labelsize=6.5)
    for ax in axes[len(cs):]:
        ax.set_visible(False)
    fig.legend(handles=[Line2D([], [], color=RED, label="JLoss (eje izq.)"),
                        Line2D([], [], color=GREEN, label="D = −GaR, pp (eje der. interior)"),
                        Line2D([], [], color=BLUE, ls="--", label="EMBI, pb (eje der. exterior)")],
               loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Fragilidad, riesgo de cola y spread por país — sombreado: GFC, estrés EM 2015–16 y COVID",
                 y=1.005, fontsize=10.5)
    save(fig, "fig_series_pais_embiext")


def tabla_descriptivos(d):
    vs = [("EMBI_bps", "Spread EMBI (pb)"), ("ln_EMBI", r"$\ln$ EMBI"), ("JLoss_l1", r"$JLoss_{t-1}$"),
          ("ln_JLoss_l1", r"$\ln JLoss_{t-1}$"), ("D_l1", r"$D_{t-1}=-GaR_{t-1}$ (pp)"),
          ("ES_l1", r"\textit{Expected Shortfall}$_{t-1}$ (pp)"), ("debt_gdp", r"Deuda/PIB (\%)"),
          ("fisc_bal", r"Balance fiscal/PIB (\%)"), ("res_gdp", r"Reservas/PIB (\%)"),
          ("ca_gdp", r"Cuenta corriente/PIB (\%)"), ("infl_yoy", r"Inflación interanual (\%)"),
          ("reer", "TCR efectivo (índice)"), ("VIX", "VIX")]
    f = lambda x, k=2: f"{x:,.{k}f}".replace(",", "X").replace(".", "{,}").replace("X", ".")
    L = [r"\begin{table}[htbp]", r"\centering", r"\small",
         rf"\caption{{Estadísticos descriptivos de la muestra de estimación ({d.country.nunique()} economías, "
         rf"{d.quarter.min()}--{d.quarter.max()}, $N={len(d)}$)}}", r"\label{tab:descriptivos}",
         r"\begin{tabular}{lrrrrrr}", r"\toprule",
         r"Variable & $N$ & Media & Desv. & Mín & Mediana & Máx \\", r"\midrule"]
    for v, lab in vs:
        s = d[v].dropna()
        L.append(f"{lab} & {len(s)} & {f(s.mean())} & {f(s.std())} & {f(s.min())} & {f(s.median())} & {f(s.max())} \\\\")
    L += [r"\bottomrule", r"\end{tabular}",
          r"\par\smallskip\parbox{0.92\linewidth}{\footnotesize \textit{Nota:} $JLoss$, $D$ y ES rezagados "
          r"un trimestre, como entran a la regresión principal; controles contemporáneos (su $N$ es menor por "
          r"cobertura). Fuentes: EMBI Global Diversified (J.P.\ Morgan; Indonesia y Sudáfrica 2010--2014, "
          r"FMI GFSR); $JLoss$ y $GaR$, estimación propia sobre datos Bloomberg; controles, FMI y Banco Mundial.}",
          r"\end{table}", ""]
    # medias por pais
    L += [r"\begin{table}[htbp]", r"\centering", r"\small",
          r"\caption{Medias por país de la muestra de estimación}", r"\label{tab:mediaspais}",
          r"\begin{tabular}{lrrrrl}", r"\toprule",
          r"País & $N$ & EMBI (pb) & $JLoss_{t-1}$ & $D_{t-1}$ (pp) & Ventana \\", r"\midrule"]
    for c, g in d.groupby("country"):
        L.append(f"{NOMBRE[c]} & {len(g)} & {f(g.EMBI_bps.mean(), 0)} & {f(g.JLoss_l1.mean())} & "
                 f"{f(g.D_l1.mean())} & {g.quarter.min()}--{g.quarter.max()} \\\\")
        num(f"media_JLoss_{c}", g.JLoss_l1.mean()); num(f"media_EMBI_{c}", g.EMBI_bps.mean())
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    # within / between
    L += [r"\begin{table}[htbp]", r"\centering", r"\small",
          r"\caption{Descomposición de la varianza \textit{within/between}}", r"\label{tab:varianza}",
          r"\begin{tabular}{lrrr}", r"\toprule",
          r"Variable & Desv. total & Desv. \textit{within} & \textit{within}/total \\", r"\midrule"]
    for v, lab in vs:
        if v == "VIX":
            continue
        s = d[[v, "country"]].dropna()
        w = (s[v] - s.groupby("country")[v].transform("mean")).std()
        L.append(f"{lab} & {f(s[v].std())} & {f(w)} & {f(w / s[v].std())} \\\\")
        num(f"within_share_{v}", w / s[v].std())
    L += [r"\bottomrule", r"\end{tabular}",
          r"\par\smallskip\parbox{0.8\linewidth}{\footnotesize \textit{Nota:} la desviación \textit{within} "
          r"es la de la variable en desvíos respecto de la media de cada país; bajo efectos fijos de país es la "
          r"única variación que identifica los coeficientes.}", r"\end{table}"]
    for v in ("EMBI_bps", "JLoss_l1", "D_l1"):
        num(f"desc_media_{v}", d[v].mean()); num(f"desc_mediana_{v}", d[v].median())
        num(f"desc_max_{v}", d[v].max()); num(f"desc_min_{v}", d[v].min())
    out = os.path.join(TAB, "tabla_descriptivos_embiext.tex")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("  tabla_descriptivos_embiext.tex")


# ================================================================ regresion principal
def me_band(m, dev):
    V = m.cov
    me = m.params["J_c"] + m.params["JxT"] * dev
    se = np.sqrt(V.loc["J_c", "J_c"] + dev ** 2 * V.loc["JxT", "JxT"] + 2 * dev * V.loc["J_c", "JxT"])
    return me, se


def fig_efecto_marginal(m, dd):
    Dbar = dd["D_l1"].mean()
    grid = np.linspace(dd["D_l1"].quantile(.02), dd["D_l1"].quantile(.98), 100)
    me, se = me_band(m, grid - Dbar)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.axhline(0, color=INK2, lw=0.8)
    ax.fill_between(grid, me - 1.96 * se, me + 1.96 * se, color=BLUE, alpha=0.15, lw=0, label="IC 95 %")
    ax.plot(grid, me, color=BLUE, lw=2.2)
    for pc, col in ((10, GREEN), (50, ORANGE), (90, RED)):
        x = dd["D_l1"].quantile(pc / 100)
        y, s = me_band(m, np.array([x - Dbar]))
        ax.plot(x, y[0], "o", color=col, ms=6, zorder=5)
        ax.annotate(f"p{pc}: {y[0]:+.3f}", (x, y[0]), textcoords="offset points", xytext=(6, 6),
                    fontsize=8, color=col)
        num(f"me_p{pc}", y[0]); num(f"me_p{pc}_se", s[0]); num(f"me_p{pc}_D", x)
    ax.plot(dd["D_l1"], np.full(len(dd), ax.get_ylim()[0]), "|", color=INK2, alpha=0.3, ms=6)
    ax.set_xlabel("D$_{t-1}$ = −GaR$_{t-1}$ (pp) — derecha = cola más adversa")
    ax.set_ylabel(r"$\partial\,\ln$EMBI$/\partial\,\ln$JLoss$_{t-1}$  (elasticidad)")
    ax.set_title("Efecto marginal de la fragilidad bancaria según el riesgo de cola\n"
                 "(regresión principal: log-log rezagada, FE país + tiempo)", fontsize=9.5)
    ax.legend(loc="upper right", fontsize=8)
    save(fig, "fig_efecto_marginal_lnlag")


def fig_superficie(m, dd):
    jg = np.linspace(dd["ln_JLoss_l1"].quantile(.02), dd["ln_JLoss_l1"].quantile(.98), 120)
    dg = np.linspace(dd["D_l1"].quantile(.02), dd["D_l1"].quantile(.98), 120)
    JJ, DD = np.meshgrid(jg, dg)
    Jc, Dc = JJ - dd["ln_JLoss_l1"].mean(), DD - dd["D_l1"].mean()
    S = 100 * (m.params["J_c"] * Jc + m.params["T_c"] * Dc + m.params["JxT"] * Jc * Dc)
    fig, ax = plt.subplots(figsize=(7.8, 5.6))
    lim = np.abs(S).max()
    cf = ax.contourf(np.exp(JJ), DD, S, levels=18, cmap="RdYlBu_r", vmin=-lim, vmax=lim)
    cs = ax.contour(np.exp(JJ), DD, S, levels=10, colors="k", linewidths=0.5, alpha=0.5)
    ax.clabel(cs, inline=True, fontsize=7, fmt="%.0f")
    ax.scatter(np.exp(dd["ln_JLoss_l1"]), dd["D_l1"], s=6, color=INK, alpha=0.25)
    ax.set_xscale("log")
    ax.set_xlabel("JLoss$_{t-1}$ (escala logarítmica)")
    ax.set_ylabel("D$_{t-1}$ = −GaR (pp) — arriba = cola más adversa")
    ax.set_title("Superficie de complementariedad: aporte de JLoss, D y su interacción al spread\n"
                 "(% respecto del spread medio; iso-curvas paralelas = sin amplificación)", fontsize=9.5)
    fig.colorbar(cf, ax=ax, label="aporte al spread (%)")
    save(fig, "fig_superficie_lnlag")


def fig_binscatter(dd):
    g0 = dd.copy()
    g0["terc"] = pd.qcut(g0["D_l1"], 3, labels=["Benigno", "Intermedio", "Cola severa"])
    pal = {"Benigno": GREEN, "Intermedio": ORANGE, "Cola severa": RED}
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for terc, g in g0.groupby("terc", observed=True):
        g = g.copy()
        g["bin"] = pd.qcut(g["ln_JLoss_l1"].rank(method="first"), 8, labels=False)
        bs = g.groupby("bin").agg(J=("ln_JLoss_l1", "mean"), E=("ln_EMBI", "mean"))
        b = np.polyfit(g["ln_JLoss_l1"], g["ln_EMBI"], 1)
        xs = np.linspace(g["ln_JLoss_l1"].min(), g["ln_JLoss_l1"].quantile(.97), 50)
        ax.scatter(bs["J"], bs["E"], color=pal[terc], s=45, zorder=4)
        ax.plot(xs, np.polyval(b, xs), color=pal[terc], lw=2, label=f"{terc}: pendiente {b[0]:.2f}")
        num(f"binscatter_pendiente_{terc.replace(' ', '_')}", b[0])
    ax.set_xlabel("ln JLoss$_{t-1}$"); ax.set_ylabel("ln EMBI$_t$")
    ax.set_title("Binscatter de ln EMBI sobre ln JLoss$_{t-1}$ por tercil de D$_{t-1}$\n"
                 "(agrupado, sin efectos fijos; 8 bins por tercil)", fontsize=9.5)
    ax.legend(fontsize=8)
    save(fig, "fig_binscatter_lnlag")


def _within2(dd, cols):
    x = dd[cols].astype(float).copy()
    for _ in range(40):
        x = x - x.groupby(dd["country"].values).transform("mean")
        x = x - x.groupby(dd["quarter"].values).transform("mean")
    return x


def fig_umbral(dd):
    """Umbral de Hansen en logs: efecto de ln JLoss_{t-1} con regimen segun D_{t-1}
    (severo: D > gamma), controlando D linealmente; transformacion within bidireccional."""
    y = _within2(dd, ["ln_EMBI"]).values.ravel()
    Dw = _within2(dd, ["D_l1"]).values.ravel()
    q = dd["D_l1"].values
    J = dd["ln_JLoss_l1"].values

    def ssr(gam):
        hi = (q > gam).astype(float)
        Z = _within2(dd.assign(a=J * hi, b=J * (1 - hi)), ["a", "b"]).values
        X = np.column_stack([Z, Dw])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        e = y - X @ b
        return e @ e

    grid = np.quantile(q, np.linspace(.15, .85, 120))
    s = np.array([ssr(g) for g in grid])
    i = s.argmin(); gam = grid[i]; sig2 = s[i] / len(y)
    LR = (s - s[i]) / sig2
    Xl = np.column_stack([_within2(dd, ["ln_JLoss_l1"]).values.ravel(), Dw])
    b0 = np.linalg.lstsq(Xl, y, rcond=None)[0]
    LR_lin = ((y - Xl @ b0) @ (y - Xl @ b0) - s[i]) / sig2
    inside = grid[LR <= 7.35]
    hi = (dd["D_l1"] > gam).astype(float)
    d2 = dd.assign(J_sev=dd["ln_JLoss_l1"] * hi, J_ben=dd["ln_JLoss_l1"] * (1 - hi))
    m = PanelOLS.from_formula("ln_EMBI ~ J_sev + J_ben + D_l1 + EntityEffects + TimeEffects",
                              d2.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
    num("umbral_gamma_D", gam); num("umbral_ci_lo", inside.min()); num("umbral_ci_hi", inside.max())
    num("umbral_LR_linealidad", LR_lin); num("umbral_n_severo", hi.sum())
    for k in ("J_sev", "J_ben"):
        num(f"umbral_{k}", m.params[k]); num(f"umbral_{k}_se", m.std_errors[k]); num(f"umbral_{k}_p", m.pvalues[k])
    diff = m.params["J_sev"] - m.params["J_ben"]
    V = m.cov
    sd = np.sqrt(V.loc["J_sev", "J_sev"] + V.loc["J_ben", "J_ben"] - 2 * V.loc["J_sev", "J_ben"])
    num("umbral_diff", diff); num("umbral_diff_p", 2 * (1 - stats.norm.cdf(abs(diff / sd))))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [2, 1]})
    axes[0].plot(grid, LR, color=BLUE, lw=2)
    axes[0].axhline(7.35, color=RED, ls="--", lw=1, label="crítico 95 % (7,35)")
    axes[0].axvline(gam, color=INK, ls=":", lw=1)
    axes[0].axvspan(inside.min(), inside.max(), color=BLUE, alpha=0.10, label="IC 95 % del umbral")
    axes[0].set_xlabel("umbral candidato γ (D$_{t-1}$, pp)"); axes[0].set_ylabel("LR(γ)")
    axes[0].set_title(f"Perfil de razón de verosimilitud (γ̂ = {gam:.2f} pp)", fontsize=9.5)
    axes[0].legend(fontsize=8)
    vals = [m.params["J_sev"], m.params["J_ben"]]
    ses = [m.std_errors["J_sev"], m.std_errors["J_ben"]]
    axes[1].bar([0, 1], vals, yerr=[1.96 * s_ for s_ in ses], color=[RED, GREEN], capsize=4)
    axes[1].axhline(0, color=INK2, lw=0.6)
    axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(["cola severa\n(D > γ̂)", "benigno\n(D ≤ γ̂)"])
    for k, v in enumerate(vals):
        axes[1].annotate(f"{v:+.3f}", (k, v), ha="center", va="bottom" if v >= 0 else "top", fontsize=9)
    axes[1].set_ylabel("elasticidad de EMBI a JLoss$_{t-1}$")
    axes[1].set_title("Efecto por régimen (IC 95 %)", fontsize=9.5)
    save(fig, "fig_umbral_lnlag")


def fig_forest(d, m0):
    ctr = [c for c in CTRLS if d[c].notna().sum() > 50]
    rows = []

    def add(lab, m, k="JxT"):
        rows.append((lab, m.params[k], m.std_errors[k], int(m.nobs)))

    cr = d.quarter.isin(CRISIS_BAT)
    for fe, lfe in (("PT", "país+tiempo"), ("P", "país"), ("T", "tiempo")):
        add(f"Principal, FE {lfe}", fit(d, fe)[0])
    for fe, lfe in (("PT", "país+tiempo"), ("P", "país"), ("T", "tiempo")):
        add(f"Sin crisis, FE {lfe}", fit(d[~cr], fe)[0])
    for fe, lfe in (("PT", "país+tiempo"), ("P", "país"), ("T", "tiempo")):
        add(f"Con 6 controles, FE {lfe}", fit(d, fe, ctr=ctr)[0])
    add("Principal, cluster país", fit(d, cov="pais")[0])
    add("Principal, cluster tiempo", fit(d, cov="tiempo")[0])
    add("Cola = −Expected Shortfall", fit(d, tail="DES_l1")[0])
    add("Núcleo 11 EM (sin Polonia e India)", fit(d[~d.country.isin(NUCLEO_EXCL)])[0])
    add("Sin China", fit(d[d.country != "china"])[0])
    add("Solo EMBI J.P. Morgan (sin empalme FMI)", fit(d[d.embi_source == "JPM_GD_xlsx"])[0]
        if "embi_source" in d else fit(d)[0])
    for lab, b, se, n in rows:
        key = lab.replace(" ", "_").replace(",", "").replace("(", "").replace(")", "").replace("+", "")
        num(f"forest_{key}", b); num(f"forest_{key}_se", se); num(f"forest_{key}_N", n)
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(7.4, 0.36 * len(rows) + 1.2))
    for i, (lab, b, se, n) in enumerate(rows):
        col = BLUE if b > 0 else RED
        ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=col, lw=1.6)
        ax.plot(b, i, "o", color=col, ms=5)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{r[0]} (N={r[3]})" for r in rows], fontsize=7.8)
    ax.set_xlabel(r"$\hat\beta_3$  ($\ln JLoss_{t-1}\times D_{t-1}$), IC 95 %")
    ax.set_title("Coeficiente de interacción por especificación (azul: signo de amplificación)", fontsize=9.5)
    npos = sum(1 for r in rows if r[1] > 0)
    nsig = sum(1 for r in rows if abs(r[1] / r[2]) > 1.96)
    num("forest_n", len(rows)); num("forest_n_pos", npos); num("forest_n_sig5", nsig)
    save(fig, "fig_forest_lnlag")


def fig_loo(d, m0):
    rows = [("Panel completo", m0.params["JxT"], m0.std_errors["JxT"])]
    for c in sorted(d.country.unique()):
        m = fit(d[d.country != c])[0]
        rows.append((f"sin {NOMBRE[c]}", m.params["JxT"], m.std_errors["JxT"]))
        num(f"loo_{c}", m.params["JxT"]); num(f"loo_{c}_p", m.pvalues["JxT"])
    fig, ax = plt.subplots(figsize=(7, 5.2))
    ax.axvline(0, color=INK2, lw=0.8)
    for i, (lab, b, se) in enumerate(rows):
        col = INK if i == 0 else BLUE
        ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=col, lw=1.8)
        ax.plot(b, i, "o", color=col, ms=5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(r"$\hat\beta_3$ (interacción), IC 95 %")
    ax.set_title("Leave-one-country-out: regresión principal excluyendo cada país", fontsize=9.5)
    b = np.array([r[1] for r in rows[1:]])
    num("loo_min", b.min()); num("loo_max", b.max()); num("loo_n_neg", (b < 0).sum())
    save(fig, "fig_loo_lnlag")


def fig_ventanas(d):
    rows = []
    for y0 in range(2004, 2022):
        w = d[(d.t.dt.year >= y0) & (d.t.dt.year <= y0 + 4)]
        if w.country.nunique() < 5 or len(w) < 80:
            continue
        m = fit(w)[0]
        rows.append((f"{y0}–{y0 + 4}", y0 + 2.5, m.params["JxT"], m.std_errors["JxT"], int(m.nobs),
                     w.country.nunique()))
    t = pd.DataFrame(rows, columns=["lab", "mid", "b", "se", "N", "G"])
    fig, ax = plt.subplots(figsize=(8.4, 4))
    ax.axhline(0, color=INK2, lw=0.8)
    ax.fill_between(t["mid"], t["b"] - 1.96 * t["se"], t["b"] + 1.96 * t["se"], color=BLUE, alpha=0.15, lw=0)
    ax.plot(t["mid"], t["b"], "o-", color=BLUE, lw=1.6, ms=4)
    ax.set_xlabel("punto medio de la ventana de cinco años")
    ax.set_ylabel(r"$\hat\beta_3$ (IC 95 %)")
    ax.set_title("Coeficiente de interacción en ventanas móviles de cinco años (regresión principal)",
                 fontsize=9.5)
    for _, r in t.iterrows():
        num(f"ventana_{r['lab'].replace('–', '_')}", r["b"]); num(f"ventana_{r['lab'].replace('–', '_')}_t", r["b"] / r["se"])
    save(fig, "fig_ventanas_lnlag")


def fig_crisis_regimen():
    dc = p12.prep_cr()
    ctr = [c for c in CTRLS if c in dc.columns and dc[c].notna().sum() > 50]
    m, dd, _ = p9b.fit_crisis_model(dc, "CM4", {"bk": p9b.BACKSTOP_Q, "em": EM1516}, "PT", ctr)
    assert int(m.nobs) == 649
    V = m.cov
    Dbar = dd["D_pp"].mean()
    grid = np.linspace(dd["D_pp"].quantile(.05), dd["D_pp"].quantile(.95), 80)
    dev = grid - Dbar
    reg = [("Fuera de crisis", ["JLoss_c"], ["JxD"], BLUE),
           ("Backstop (GFC + COVID)", ["JLoss_c", "JLoss_bk"], ["JxD", "JxD_bk"], RED),
           ("EMstress (2015–16)", ["JLoss_c", "JLoss_em"], ["JxD", "JxD_em"], ORANGE)]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.axhline(0, color=INK2, lw=0.8)
    for lab, lv, it, col in reg:
        me = sum(m.params[p] for p in lv) + sum(m.params[p] for p in it) * dev
        se = np.sqrt(np.array([sum(V.loc[i, j] for i in lv for j in lv)
                               + 2 * x * sum(V.loc[i, j] for i in lv for j in it)
                               + x ** 2 * sum(V.loc[i, j] for i in it for j in it) for x in dev]))
        ax.fill_between(grid, me - 1.96 * se, me + 1.96 * se, color=col, alpha=0.12, lw=0)
        ax.plot(grid, me, color=col, lw=2.2, label=lab)
        b, s_ = p9b._lincom(m, lv)[:2]
        num(f"crisis_nivel_{lab.split()[0]}", b); num(f"crisis_nivel_{lab.split()[0]}_se", s_)
    ax.set_xlabel("D$_{t-1}$ = −GaR (pp) — derecha = cola más adversa")
    ax.set_ylabel(r"$\partial\,\ln$EMBI$/\partial\,\ln$JLoss$_{t-1}$")
    ax.set_title("Efecto marginal de la fragilidad según el riesgo de cola, por régimen de crisis\n"
                 "(CM4, FE país + tiempo, seis controles)", fontsize=9.5)
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "fig_crisis_regimen_lnlag")


def fig_contabilidad(m, dd, q0="2019Q4", q1="2020Q2"):
    b1, b2, b3 = m.params["J_c"], m.params["T_c"], m.params["JxT"]
    rows = []
    for c, g in dd.groupby("country"):
        a, b = g[g.quarter == q0], g[g.quarter == q1]
        if len(a) and len(b):
            a, b = a.iloc[0], b.iloc[0]
            rows.append(dict(c=NOMBRE[c], J=100 * b1 * (b.J_c - a.J_c), D=100 * b2 * (b.T_c - a.T_c),
                             I=100 * b3 * (b.J_c * b.T_c - a.J_c * a.T_c),
                             obs=100 * (b.ln_EMBI - a.ln_EMBI)))
    t = pd.DataFrame(rows).sort_values("obs")
    fig, ax = plt.subplots(figsize=(8.4, 0.42 * len(t) + 1.4))
    y = np.arange(len(t))
    for col, key, lab in ((RED, "J", "ln JLoss$_{t-1}$"), (GREEN, "D", "D$_{t-1}$"), ("#8e44ad", "I", "interacción")):
        pos = t[key].clip(lower=0); neg = t[key].clip(upper=0)
        left_p = t[[k for k in ("J", "D", "I")][: ["J", "D", "I"].index(key)]].clip(lower=0).sum(axis=1)
        left_n = t[[k for k in ("J", "D", "I")][: ["J", "D", "I"].index(key)]].clip(upper=0).sum(axis=1)
        ax.barh(y, pos, left=left_p, color=col, label=lab, height=0.6)
        ax.barh(y, neg, left=left_n, color=col, height=0.6)
    ax.plot(t["obs"], y, "D", color=INK, ms=5, label="Δ ln EMBI observado (× 100)")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(t["c"], fontsize=8)
    ax.set_xlabel("aporte al cambio del spread (log-puntos × 100 ≈ %)")
    ax.set_title(f"Contabilidad del spread en el choque COVID ({q0} → {q1})", fontsize=9.5)
    ax.legend(fontsize=7.5, loc="lower right")
    num("contab_obs_media", t["obs"].mean())
    num("contab_pred_media", (t.J + t.D + t.I).mean())
    num("contab_interaccion_media", t.I.mean())
    num("contab_D_media", t.D.mean()); num("contab_J_media", t.J.mean())
    save(fig, "fig_contabilidad_lnlag")


def fig_prima(m, dd):
    dd = dd.copy()
    dd["prima"] = 100 * m.params["JxT"] * dd["J_c"] * dd["T_c"]
    cs = sorted(dd.country.unique())
    fig, axes = _grid(len(cs), h=2.0)
    for ax, c in zip(axes, cs):
        g = gaps(dd[dd.country == c].sort_values("t"))
        ax.fill_between(g["t"], 0, g["prima"], where=g["prima"] >= 0, color=RED, alpha=0.6, lw=0)
        ax.fill_between(g["t"], 0, g["prima"], where=g["prima"] < 0, color=GREEN, alpha=0.55, lw=0)
        ax.axhline(0, color=INK2, lw=0.5)
        ax.set_title(NOMBRE[c], fontsize=8.5)
    for ax in axes[len(cs):]:
        ax.set_visible(False)
    fig.suptitle(r"Prima de amplificación $\hat\beta_3(\ln JLoss_c\times D_c)$ — % del spread atribuible a la "
                 "interacción (rojo: amplifica; verde: atenúa)", y=1.005, fontsize=10)
    num("prima_media_abs", dd["prima"].abs().mean()); num("prima_max", dd["prima"].max())
    num("prima_min", dd["prima"].min()); num("prima_share_pos", (dd["prima"] > 0).mean())
    save(fig, "fig_prima_lnlag")


def descomposicion_especificacion(d):
    """2x2: (niveles | logs) x (contemporaneo | rezagado) para el beta3 de M4, FE pais+tiempo, sin
    controles, en muestra completa y sin crisis. Aisla cual de los dos cambios de especificacion
    (log o rezago) mueve la interaccion respecto de la version en niveles contemporanea."""
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw = raw.dropna(subset=["EMBI_bps", "JLoss", "GaR"]).copy()
    raw["t"] = pd.PeriodIndex(raw["quarter"], freq="Q").to_timestamp()
    raw["lvl_EMBI"], raw["ln_EMBI_"] = raw["EMBI_bps"], np.log(raw["EMBI_bps"])
    raw["lvl_J"], raw["ln_J"], raw["D_"] = raw["JLoss"], np.log(raw["JLoss"]), -raw["GaR"] * 100
    lag = d.assign(lvl_EMBI=d["EMBI_bps"], ln_EMBI_=d["ln_EMBI"], lvl_J=d["JLoss_l1"],
                   ln_J=d["ln_JLoss_l1"], D_=d["D_l1"])
    out = []
    for tiempo, base in (("contemporaneo", raw), ("rezagado", lag)):
        for forma, y, x in (("niveles", "lvl_EMBI", "lvl_J"), ("logs", "ln_EMBI_", "ln_J")):
            for mu, sub in (("completa", base), ("sin_crisis", base[~base.quarter.isin(CRISIS_BAT)])):
                dd = sub.dropna(subset=[y, x, "D_"]).copy()
                dd["J_c"] = dd[x] - dd[x].mean(); dd["T_c"] = dd["D_"] - dd["D_"].mean()
                dd["JxT"] = dd["J_c"] * dd["T_c"]
                m = PanelOLS.from_formula(f"{y} ~ J_c + T_c + JxT + EntityEffects + TimeEffects",
                                          dd.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
                k = f"esp_{forma}_{tiempo}_{mu}"
                num(k, m.params["JxT"]); num(k + "_t", m.tstats["JxT"]); num(k + "_N", m.nobs)
                num(k + "_b1", m.params["J_c"]); num(k + "_b1_t", m.tstats["J_c"])
                out.append((k, m.params["JxT"], m.tstats["JxT"], int(m.nobs)))
    for r in out:
        print(f"  {r[0]:42s} b3={r[1]:+.4f} t={r[2]:+.2f} N={r[3]}")


def diagnostico_controles(d):
    """Por que ln JLoss pierde significancia con los 6 controles (Panel C): misma muestra sin
    controles, un control a la vez, todos menos uno, y controles rezagados un trimestre."""
    ctr = [c for c in CTRLS if d[c].notna().sum() > 50]
    s = d.dropna(subset=ctr)

    def rec(k, m):
        num(f"ctrl_{k}_b1", m.params["J_c"]); num(f"ctrl_{k}_b1_p", m.pvalues["J_c"])
        num(f"ctrl_{k}_b2", m.params["T_c"]); num(f"ctrl_{k}_b2_p", m.pvalues["T_c"])
        num(f"ctrl_{k}_b3", m.params["JxT"]); num(f"ctrl_{k}_b3_p", m.pvalues["JxT"]); num(f"ctrl_{k}_N", m.nobs)

    rec("misma_muestra_sin_ctrl", fit(s)[0])
    rec("todos", fit(d, ctr=ctr)[0])
    for c in ctr:
        rec(f"solo_{c}", fit(d, ctr=[c])[0])
        rec(f"sin_{c}", fit(d, ctr=[x for x in ctr if x != c])[0])
    dl = d.sort_values(["country", "quarter"]).copy()
    q = pd.PeriodIndex(dl["quarter"], freq="Q"); dl["_qn"] = q.year * 4 + q.quarter
    g = dl.groupby("country"); consec = (dl["_qn"] - g["_qn"].shift(1)) == 1
    for c in ctr:
        dl[c + "_l1"] = g[c].shift(1).where(consec)
    rec("rezagados", fit(dl, ctr=[c + "_l1" for c in ctr])[0])
    for c in ctr:
        num(f"corr_lnJ_{c}", s["ln_JLoss_l1"].corr(s[c]))


def complementariedad_implicita(m, dd):
    """Derivada cruzada en NIVELES implicada por el modelo log-log:
         S = exp(a + b1 J_c + b2 D_c + b3 J_c D_c),  J_c = ln JLoss_c
         dS/dJLoss        = S/JLoss * (b1 + b3 D_c)
         d2S/dJLoss dD    = S/JLoss * [b3 + (b1 + b3 D_c)(b2 + b3 J_c)]
       Con b3 = 0 se reduce a b1*b2*S/JLoss > 0: la forma log ya impone complementariedad en pb.
       Se evalua con el spread observado (pb) y JLoss_{t-1} en niveles, y se compara con el b3 de la
       especificacion en niveles (pb por unidad de JLoss por pp de D)."""
    b1, b2, b3 = m.params["J_c"], m.params["T_c"], m.params["JxT"]
    V = m.cov.loc[["J_c", "T_c", "JxT"], ["J_c", "T_c", "JxT"]].values
    S, J = dd["EMBI_bps"].values, dd["JLoss_l1"].values
    Jc, Dc = dd["J_c"].values, dd["T_c"].values

    def cruz(b):
        return S / J * (b[2] + (b[0] + b[2] * Dc) * (b[1] + b[2] * Jc))

    full = cruz([b1, b2, b3]); solo = cruz([b1, b2, 0.0])
    # IC de la media por simulacion de los coeficientes (normal con la matriz DK)
    rng = np.random.default_rng(13)
    draws = rng.multivariate_normal([b1, b2, b3], V, size=4000)
    sim = np.array([cruz(b).mean() for b in draws])
    sim0 = np.array([cruz([b[0], b[1], 0.0]).mean() for b in draws])
    num("implicita_media", full.mean()); num("implicita_mediana", np.median(full))
    num("implicita_ci_lo", np.percentile(sim, 2.5)); num("implicita_ci_hi", np.percentile(sim, 97.5))
    num("implicita_b3cero_media", solo.mean())
    num("implicita_b3cero_ci_lo", np.percentile(sim0, 2.5)); num("implicita_b3cero_ci_hi", np.percentile(sim0, 97.5))
    num("implicita_share_pos", (full > 0).mean())
    print(f"  derivada cruzada implicita (pb/unidad JLoss/pp D): media {full.mean():+.3f} "
          f"[{np.percentile(sim, 2.5):+.3f}, {np.percentile(sim, 97.5):+.3f}]; con b3=0: {solo.mean():+.3f} "
          f"[{np.percentile(sim0, 2.5):+.3f}, {np.percentile(sim0, 97.5):+.3f}]")


def main():
    print("p13: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]))
    d = datos()
    m0, dd = estimar_principal(d)
    d = dd  # muestra de estimacion de la regresion principal (N=765)
    print(f"  principal: N={int(m0.nobs)}  b1={m0.params['J_c']:+.4f}  b2={m0.params['T_c']:+.4f}  "
          f"b3={m0.params['JxT']:+.4f} (p={m0.pvalues['JxT']:.3f})")
    fig_cobertura(d)
    fig_jloss_d_paises(d)
    fig_comovimiento(d)
    fig_distribuciones(d)
    fig_correlaciones(d)
    fig_comov_pais(d)
    fig_skewt_chile()
    fig_series_pais(d)
    tabla_descriptivos(d)
    fig_efecto_marginal(m0, dd)
    fig_superficie(m0, dd)
    fig_binscatter(dd)
    fig_umbral(dd)
    fig_forest(d, m0)
    fig_loo(d, m0)
    fig_ventanas(d)
    fig_crisis_regimen()
    fig_contabilidad(m0, dd)
    fig_prima(m0, dd)
    descomposicion_especificacion(d)
    complementariedad_implicita(m0, dd)
    diagnostico_controles(d)
    out = os.path.join(HERE, "paper_lnlag_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    print(f"  {len(NUM)} cifras -> {os.path.basename(out)}")


if __name__ == "__main__":
    main()
