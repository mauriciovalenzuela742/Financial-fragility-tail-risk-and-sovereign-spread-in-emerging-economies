# -*- coding: utf-8 -*-
"""
p4_figuras.py -- figuras de la tesis, UN SOLO panel Bloomberg. Salida -> bbg/figuras/*.pdf (+.png)
Paleta validada (data-viz skill): azul #2a78d6, naranja #eb6834, rojo #e34948,
tinta #0b0b0b / #52514e, superficie #fcfcfb.
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figuras")
os.makedirs(FIG, exist_ok=True)
PANEL = os.path.dirname(HERE)
PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")
IMAGENES_TESIS = os.path.join(os.path.dirname(HERE), "..", "..",
                               "4_Redaccion", "tesis", "imagenes")

BLUE, ORANGE, RED = "#2a78d6", "#eb6834", "#e34948"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e7e6e2"
CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
    "font.size": 9, "axes.titlesize": 10, "legend.frameon": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _panel():
    d = pd.read_csv(PANEL_CSV)
    d["GaR_pp"] = d["GaR"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


def _fit(d, ctrls):
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"] + ctrls).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["GaR_c"] = dd["GaR_pp"] - dd["GaR_pp"].mean()
    dd["JxG"] = dd["JLoss_c"] * dd["GaR_c"]
    m = PanelOLS.from_formula(
        "EMBI_bps ~ JLoss_c + GaR_c + JxG + " + " + ".join(ctrls) + " + EntityEffects + TimeEffects",
        dd.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
    return m, dd


def _save(fig, name):
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=150, bbox_inches="tight")
    os.makedirs(IMAGENES_TESIS, exist_ok=True)
    fig.savefig(os.path.join(IMAGENES_TESIS, f"{name}.pdf"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}.pdf (+ copia en 4_Redaccion/tesis/imagenes/)")


def fig_cobertura():
    cov = pd.read_csv(os.path.join(HERE, "cobertura_panel_bbg.csv"))
    d = _panel()
    order = cov.sort_values("n_estimacion")["country"].tolist()
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for i, c in enumerate(order):
        g = d[d.country == c]
        cds = g.dropna(subset=["EMBI_bps"])
        est = g.dropna(subset=["EMBI_bps", "JLoss", "GaR"])
        ax.plot(g.dropna(subset=["JLoss"])["t"], [i] * g["JLoss"].notna().sum(), "|",
                color=GRID, ms=7, mew=2)
        ax.plot(cds["t"], [i] * len(cds), "|", color="#9ec5f4", ms=7, mew=2)
        ax.plot(est["t"], [i] * len(est), "|", color=BLUE, ms=7, mew=2)
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=8)
    ax.grid(axis="y", visible=False)
    ax.set_title("Cobertura del panel — gris: JLoss · celeste: + EMBI soberano · azul: muestra de estimación (EMBI+JLoss+GaR)")
    _save(fig, "fig_cobertura")


def fig_efecto_marginal():
    d = _panel()
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    m, dd = _fit(d, ctr)
    b1, th, V = m.params["JLoss_c"], m.params["JxG"], m.cov
    gs = np.linspace(dd["GaR_pp"].quantile(.05), dd["GaR_pp"].quantile(.95), 60)
    gc = gs - dd["GaR_pp"].mean()
    me = b1 + th * gc
    se = np.sqrt(V.loc["JLoss_c", "JLoss_c"] + gc**2 * V.loc["JxG", "JxG"]
                 + 2 * gc * V.loc["JLoss_c", "JxG"])
    fig, ax = plt.subplots(figsize=(6.6, 4))
    ax.axhline(0, color=INK2, lw=0.8)
    ax.fill_between(gs, me - 1.645 * se, me + 1.645 * se, color=BLUE, alpha=0.15, lw=0)
    ax.plot(gs, me, color=BLUE, lw=2.2)
    ax.invert_xaxis()
    ax.set_xlabel("GaR (cuantil 5 % del crecimiento, pp)")
    ax.set_ylabel(r"$\partial\,$EMBI$/\partial\,$JLoss  (pb por unidad)")
    ax.set_title("Efecto marginal de la fragilidad bancaria según el riesgo de cola (M2)")
    fig.text(0.5, -0.03, "Banda: IC 90 % (Driscoll–Kraay). Eje X invertido: cola más severa a la derecha.",
             ha="center", color=INK2, fontsize=8)
    _save(fig, "fig_efecto_marginal")


def fig_forest_theta():
    t = pd.read_csv(os.path.join(HERE, "tabla_theta_bbg.csv"))
    r = pd.read_csv(os.path.join(HERE, "robustez_bbg.csv"))
    rows = []
    for _, x in t.iterrows():
        rows.append((x["spec"], x["theta"], x.get("se", np.nan)))
    for _, x in r.iterrows():
        rows.append((x["spec"], x["theta"], x["se"]))
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(6.6, max(5, 0.26 * len(rows))))
    for i, (lab, th, se) in enumerate(rows):
        col = RED if th > 0 else BLUE
        if np.isfinite(se):
            ax.plot([th - 1.96 * se, th + 1.96 * se], [i, i], color=col, lw=1.4)
        ax.plot(th, i, "o", color=col, ms=5)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([x[0] for x in rows], fontsize=7.5)
    ax.set_xlabel(r"$\hat\theta$  (JLoss $\times$ GaR)")
    ax.set_title("Coeficiente de interacción θ por especificación y prueba de robustez")
    _save(fig, "fig_forest_theta")


def fig_umbral():
    u = pd.read_csv(os.path.join(HERE, "umbral_bbg.csv")).iloc[0]
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.bar([0], [u["efecto_severo"]], 0.5, color=RED, label="régimen cola severa")
    ax.bar([0.7], [u["efecto_benigno"]], 0.5, color=BLUE, label="régimen benigno")
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks([0, 0.7]); ax.set_xticklabels(["GaR ≤ γ̂", "GaR > γ̂"])
    ax.set_ylabel("efecto de JLoss sobre el EMBI (pb/unidad)")
    ax.legend()
    ax.set_title(f"Modelo de umbral de Hansen (γ̂ = {u['gamma']:+.1f} pp de GaR)")
    _save(fig, "fig_umbral")


def fig_jloss_paises():
    j = pd.read_csv(os.path.join(os.path.dirname(PANEL), "JLoss_reconstruction",
                                 "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv"))
    j["t"] = pd.PeriodIndex(j["quarter"], freq="Q").to_timestamp()
    cov = pd.read_csv(os.path.join(HERE, "cobertura_panel_bbg.csv"))
    cs = sorted(cov["country"])
    n = len(cs); ncol = 5; nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(11, 2.0 * nrow), sharex=True)
    for ax, c in zip(axes.ravel(), cs):
        g = j[j.countryname == c].sort_values("t")
        ax.plot(g["t"], g["JLoss"], color=BLUE, lw=1.4)
        ax.fill_between(g["t"], 0, g["JLoss"], color=BLUE, alpha=0.12, lw=0)
        ax.set_title(c, fontsize=8.5)
        ax.set_ylim(0, max(12, g["JLoss"].max() * 1.1))
    for ax in axes.ravel()[n:]:
        ax.set_visible(False)
    fig.suptitle("JLoss trimestral por país — datos Bloomberg (motor de punto de silla, ρ=0,4)",
                 y=1.005, fontsize=11)
    _save(fig, "fig_jloss_paises")


def fig_h4b():
    f = pd.read_csv(os.path.join(HERE, "fase5_bbg.csv"))
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    labs, b4s, los, his, cols = [], [], [], [], []
    for _, x in f.iterrows():
        ci = eval(x["ci90"])
        labs.append(f"Bloomberg: HHI {x['HHI']}")
        b4s.append(x["b4"]); los.append(ci[0]); his.append(ci[1])
        cols.append(RED if x["b4"] < 0 else BLUE)
    labs.append("v8 (regulatorio): HHI estructural"); b4s.append(720.7)
    los.append(np.nan); his.append(np.nan); cols.append("#888")
    y = np.arange(len(labs))
    for yi, b, lo, hi, cc in zip(y, b4s, los, his, cols):
        if np.isfinite(lo):
            ax.plot([lo, hi], [yi, yi], color=cc, lw=1.4)
        ax.plot(b, yi, "o", color=cc, ms=6)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(labs[::-1] if False else labs, fontsize=8)
    ax.set_xlabel(r"$\hat\beta_4$  (JLoss $\times$ D $\times$ HHI) — amplificación por concentración (H4b)")
    ax.set_title("H4b: la amplificación por concentración no se sostiene con datos Bloomberg")
    _save(fig, "fig_h4b")


def fig_concordancia():
    o = pd.read_csv(os.path.join(PANEL, "Panel_extended_15paises.csv"))
    o["country"] = o["country"].str.lower()
    j = pd.read_csv(os.path.join(os.path.dirname(PANEL), "JLoss_reconstruction",
                                 "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv"))
    j["country"] = j["countryname"].str.lower()
    m = o[["country", "quarter", "JLoss"]].merge(
        j[["country", "quarter", "JLoss"]], on=["country", "quarter"],
        suffixes=("_v8", "_bbg")).dropna()
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.scatter(m["JLoss_v8"], m["JLoss_bbg"], s=14, color=BLUE, alpha=0.5, lw=0)
    lim = [0, max(m["JLoss_v8"].max(), m["JLoss_bbg"].max()) * 1.05]
    ax.plot(lim, lim, color=INK2, lw=0.8, ls="--")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("JLoss v8 (regulatorio)"); ax.set_ylabel("JLoss Bloomberg")
    rho = m["JLoss_v8"].corr(m["JLoss_bbg"])
    ax.set_title(f"Concordancia JLoss regulatorio vs Bloomberg\n(r = {rho:.2f}, n = {len(m)})")
    _save(fig, "fig_concordancia_jloss")


GFC_Q = ["2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4"]
COVID_Q = ["2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"]
EM1516_Q = ["2015Q3", "2015Q4", "2016Q1"]              # estres EM 2015-16
BACKSTOP_Q = GFC_Q + COVID_Q                            # crisis con respaldo oficial masivo


def _fit_crisis(d, dummies, ctrls):
    """JLoss x D x vector-de-crisis, FE pais+tiempo, DK -- misma especificacion
    que p9_crisis_interaccion.py / celda 8 de EDA_Panel_Final_bbg.ipynb."""
    cc = [c for c in ctrls if c in d.columns and d[c].notna().sum() > 50]
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "D_pp"] + cc).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["D_c"] = dd["D_pp"] - dd["D_pp"].mean()
    dd["JxD"] = dd["JLoss_c"] * dd["D_c"]
    rhs = ["JLoss_c", "D_c", "JxD"]
    for nm, qs in dummies.items():
        cr = dd["quarter"].isin(qs).astype(float)
        dd[f"JxD_{nm}"] = dd["JxD"] * cr
        dd[f"JLoss_{nm}"] = dd["JLoss_c"] * cr
        dd[f"D_{nm}"] = dd["D_c"] * cr
        rhs += [f"JxD_{nm}", f"JLoss_{nm}", f"D_{nm}"]
    rhs += cc
    f = "EMBI_bps ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, dd.set_index(["country", "t"])).fit(
        cov_type="kernel", kernel="bartlett")
    return m, dd


def _lincom_crisis(m, names):
    """coef, se, p (Wald H0=0) de la suma de varios parametros (delta method)."""
    b = float(sum(m.params[n] for n in names))
    V = m.cov
    se = float(np.sqrt(sum(V.loc[i, j] for i in names for j in names)))
    p = 2 * (1 - stats.norm.cdf(abs(b / se)))
    return b, se, p


def fig_crisis_regimen():
    """Efecto marginal dEMBI/dJLoss vs D, por regimen de crisis (Backstop vs EMstress).
    Reproduce la especificacion de p9_crisis_interaccion.py (interaccion JLoss x D x
    vector-de-crisis, D=-GaR, FE pais+tiempo, errores Driscoll-Kraay bartlett):
    Backstop = GFC 2008Q4-2009Q4 + COVID 2020Q1-2021Q4 (respaldo oficial masivo);
    EMstress = 2015Q3-2016Q1 (sin respaldo)."""
    d = _panel()
    d["D_pp"] = -d["GaR_pp"]
    dat = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"]).copy()
    ctr = [c for c in CTRLS if c in dat.columns and dat[c].notna().sum() > 50]
    dummies = {"bk": BACKSTOP_Q, "em": EM1516_Q}
    m, dd = _fit_crisis(dat, dummies, ctr)

    b3 = m.params["JxD"]
    print(f"  fig_crisis_regimen: N={int(m.nobs)}, paises={int(m.entity_info.total)}")
    print(f"    b3 (fuera de crisis)      = {b3:+.3f}  (t={m.tstats['JxD']:+.2f}, "
          f"p={m.pvalues['JxD']:.3f})")
    for nm, lbl in (("bk", "Backstop"), ("em", "EMstress")):
        b4 = m.params[f"JxD_{nm}"]
        sb, sse, sp = _lincom_crisis(m, ["JxD", f"JxD_{nm}"])
        print(f"    b4 x {lbl:9s}            = {b4:+.3f}  (t={m.tstats[f'JxD_{nm}']:+.2f}, "
              f"p={m.pvalues[f'JxD_{nm}']:.3f})")
        print(f"    b3 + b4 ({lbl})           = {sb:+.3f}  (Wald p [H0: =0] = {sp:.3f})")

    V = m.cov
    Dbar = dat["D_pp"].mean()
    grid = np.linspace(dat["D_pp"].quantile(.05), dat["D_pp"].quantile(.95), 80)
    dev = grid - Dbar

    regimenes = [
        ("Fuera de crisis", ["JLoss_c"], ["JxD"], BLUE),
        ("Backstop (GFC + COVID)", ["JLoss_c", "JLoss_bk"], ["JxD", "JxD_bk"], RED),
        ("EMstress (2015-16)", ["JLoss_c", "JLoss_em"], ["JxD", "JxD_em"], ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.axhline(0, color=INK2, lw=0.8)
    for lab, lvl, itr, col in regimenes:
        me = sum(m.params[p] for p in lvl) + sum(m.params[p] for p in itr) * dev
        se = np.array([
            np.sqrt(
                sum(V.loc[i, j] for i in lvl for j in lvl)
                + 2 * dv * sum(V.loc[i, j] for i in lvl for j in itr)
                + dv ** 2 * sum(V.loc[i, j] for i in itr for j in itr)
            ) for dv in dev
        ])
        ax.fill_between(grid, me - 1.96 * se, me + 1.96 * se, color=col, alpha=0.12, lw=0)
        ax.plot(grid, me, color=col, lw=2.2, label=lab)
    ax.set_xlabel("D = -GaR (pp) — derecha = mayor riesgo de cola")
    ax.set_ylabel(r"$\partial\,$EMBI$/\partial\,$JLoss  (pb por unidad)")
    ax.set_title("Efecto marginal de la fragilidad bancaria según el riesgo de cola, por régimen\n"
                 "(la pendiente se aplana bajo Backstop; se mantiene bajo EMstress)")
    ax.legend(loc="upper left")
    fig.text(0.5, -0.03,
             "Banda: IC 95 % (Driscoll–Kraay). Interacción JLoss × D × vector-de-crisis, FE país+tiempo.",
             ha="center", color=INK2, fontsize=8)
    _save(fig, "fig_crisis_regimen")


def fig_gar_paises():
    """Evolucion de D = -GaR (pp) por pais, mismo estilo que fig_jloss_paises() pero
    restringido a los 13 paises del panel de estimacion vigente (n_estimacion > 0 en
    cobertura_panel_bbg.csv). Convencion D = -GaR: valores mas altos = cola mas severa."""
    d = _panel()
    d["D_pp"] = -d["GaR_pp"]
    cov = pd.read_csv(os.path.join(HERE, "cobertura_panel_bbg.csv"))
    cs = sorted(cov[cov["n_estimacion"] > 0]["country"])
    n = len(cs); ncol = 5; nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(11, 2.0 * nrow), sharex=True)
    for ax, c in zip(axes.ravel(), cs):
        g = d[d.country == c].dropna(subset=["D_pp"]).sort_values("t")
        ax.axhline(0, color=INK2, lw=0.6)
        ax.plot(g["t"], g["D_pp"], color=BLUE, lw=1.4)
        ax.fill_between(g["t"], 0, g["D_pp"], color=BLUE, alpha=0.12, lw=0)
        ax.set_title(c, fontsize=8.5)
    for ax in axes.ravel()[n:]:
        ax.set_visible(False)
    fig.suptitle("D = -GaR trimestral por país — riesgo de cola del crecimiento, datos Bloomberg "
                 f"(n = {n} países del panel de estimación)", y=1.005, fontsize=11)
    _save(fig, "fig_gar_paises")


def fig_comovimiento():
    """Co-movimiento agregado del panel: D=-GaR, JLoss y EMBI_bps, cada uno estandarizado
    (z-score sobre el panel completo pais-trimestre) y agregado con la mediana transversal
    por trimestre (mas robusta a la cola larga de JLoss que la media)."""
    d = _panel()
    d["D_pp"] = -d["GaR_pp"]

    def z(s):
        return (s - s.mean()) / s.std()

    d["D_z"] = z(d["D_pp"])
    d["JLoss_z"] = z(d["JLoss"])
    d["EMBI_z"] = z(d["EMBI_bps"])
    g = d.groupby("t")[["D_z", "JLoss_z", "EMBI_z"]].median().sort_index()
    g = g.dropna(how="all")

    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.axhline(0, color=INK2, lw=0.8)
    ax.plot(g.index, g["D_z"], color=BLUE, lw=1.8, label="D = -GaR (mediana, z-score)")
    ax.plot(g.index, g["JLoss_z"], color=ORANGE, lw=1.8, label="JLoss (mediana, z-score)")
    ax.plot(g.index, g["EMBI_z"], color=RED, lw=1.8, label="EMBI (mediana, z-score)")
    ax.set_ylabel("desviaciones estándar (mediana transversal por trimestre)")
    ax.set_title("Co-movimiento agregado del panel: riesgo de cola, fragilidad bancaria "
                 "y spread soberano")
    ax.legend(loc="upper left", fontsize=8.5)
    _save(fig, "fig_comovimiento")


def main():
    print("Figuras -> bbg/figuras/")
    fig_cobertura()
    fig_efecto_marginal()
    fig_forest_theta()
    fig_umbral()
    fig_jloss_paises()
    fig_h4b()
    fig_concordancia()
    fig_crisis_regimen()
    fig_gar_paises()
    fig_comovimiento()


if __name__ == "__main__":
    main()
