# -*- coding: utf-8 -*-
"""
p4_figuras.py -- figuras de la tesis, panel Bloomberg. Salida -> bbg/figuras/*.pdf (+ .png)
Paleta validada (data-viz skill): azul #2a78d6, naranja #eb6834, rojo #e34948,
gris midpoint #f0efec, tinta #0b0b0b / #52514e, superficie #fcfcfb.
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figuras")
os.makedirs(FIG, exist_ok=True)
PANEL = os.path.dirname(HERE)

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


def _prep(fn):
    d = pd.read_csv(os.path.join(HERE, fn))
    d["GaR_pp"] = d["GaR"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    return d


def _fit(d, ctrls):
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"] + ctrls).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["GaR_c"] = dd["GaR_pp"] - dd["GaR_pp"].mean()
    dd["JxG"] = dd["JLoss_c"] * dd["GaR_c"]
    rhs = ["JLoss_c", "GaR_c", "JxG"] + ctrls
    m = PanelOLS.from_formula(
        "EMBI_bps ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects",
        dd.set_index(["country", "t"])).fit(cov_type="kernel", kernel="bartlett")
    return m, dd


# ----------------------------------------------------------------------
def fig_efecto_marginal():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6), sharey=True)
    for ax, (fn, ctr, ttl) in zip(axes, [
            ("Panel_principal_bbg.csv", CTRLS, "Panel principal (5 LatAm, M3)"),
            ("Panel_ampliado_bbg.csv", [], "Panel ampliado (11 países, M2)")]):
        d = _prep(fn)
        m, dd = _fit(d, ctr)
        b1, th = m.params["JLoss_c"], m.params["JxG"]
        V = m.cov
        gs = np.linspace(dd["GaR_pp"].quantile(.05), dd["GaR_pp"].quantile(.95), 60)
        gc = gs - dd["GaR_pp"].mean()
        me = b1 + th * gc
        se = np.sqrt(V.loc["JLoss_c", "JLoss_c"] + gc**2 * V.loc["JxG", "JxG"]
                     + 2 * gc * V.loc["JLoss_c", "JxG"])
        ax.axhline(0, color=INK2, lw=0.8)
        ax.fill_between(gs, me - 1.645 * se, me + 1.645 * se, color=BLUE, alpha=0.15, lw=0)
        ax.plot(gs, me, color=BLUE, lw=2)
        ax.invert_xaxis()  # GaR mas negativo (cola severa) a la derecha
        ax.set_title(ttl, color=INK)
        ax.set_xlabel("GaR (cuantil 5% del crecimiento, pp)")
    axes[0].set_ylabel(r"$\partial\,$EMBI$/\partial\,$JLoss  (pb por unidad)")
    fig.suptitle("Efecto marginal de la fragilidad bancaria según el riesgo de cola",
                 y=1.02, fontsize=11)
    fig.text(0.5, -0.04, "Banda: IC 90% (errores Driscoll–Kraay). Eje X invertido: "
             "cola más severa a la derecha.", ha="center", color=INK2, fontsize=8)
    _save(fig, "fig_efecto_marginal")


def fig_forest_theta():
    t = pd.read_csv(os.path.join(HERE, "tabla_theta_bbg.csv"))
    r = pd.read_csv(os.path.join(HERE, "robustez_bbg.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.6), sharex=True)
    for ax, base, ttl in zip(axes, ["principal", "ampliado"],
                             ["Panel principal (5 LatAm)", "Panel ampliado (11 países)"]):
        tt = t[t.base == base]
        rr = r[r.base == base]
        rows = []
        for _, x in tt.iterrows():
            rows.append((x["spec"], x["theta"], x.get("se", np.nan)))
        for _, x in rr.iterrows():
            rows.append((x["caso"], x["theta"], x["se"]))
        rows = rows[::-1]
        y = np.arange(len(rows))
        for i, (lab, th, se) in enumerate(rows):
            col = RED if th > 0 else BLUE
            if np.isfinite(se):
                ax.plot([th - 1.96 * se, th + 1.96 * se], [i, i], color=col, lw=1.4)
            ax.plot(th, i, "o", color=col, ms=5)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([x[0] for x in rows], fontsize=7.5)
        ax.set_title(ttl, color=INK)
        ax.set_xlabel(r"$\hat\theta$  (JLoss $\times$ GaR)")
    fig.suptitle("Coeficiente de interacción θ por especificación y prueba de robustez",
                 y=1.01, fontsize=11)
    _save(fig, "fig_forest_theta")


def fig_umbral():
    u = pd.read_csv(os.path.join(HERE, "umbral_bbg.csv"))
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    x = np.arange(len(u))
    w = 0.36
    ax.bar(x - w/2, u["efecto_severo"], w, color=RED, label="régimen cola severa")
    ax.bar(x + w/2, u["efecto_benigno"], w, color=BLUE, label="régimen benigno")
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{b}\n(umbral GaR={g:+.1f} pp)" for b, g in zip(u["base"], u["gamma"])])
    ax.set_ylabel("efecto de JLoss sobre EMBI (pb/unidad)")
    ax.legend()
    ax.set_title("Modelo de umbral de panel (Hansen): efecto de JLoss por régimen de GaR")
    _save(fig, "fig_umbral")


def fig_jloss_paises():
    j = pd.read_csv(os.path.join(os.path.dirname(PANEL), "JLoss_reconstruction",
                                 "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv"))
    j["t"] = pd.PeriodIndex(j["quarter"], freq="Q").to_timestamp()
    cs = ["brazil", "chile", "china", "colombia", "indonesia", "malaysia",
          "mexico", "peru", "philippines", "southafrica", "turkey"]
    fig, axes = plt.subplots(3, 4, figsize=(10, 6.2), sharex=True)
    for ax, c in zip(axes.ravel(), cs):
        g = j[j.countryname == c].sort_values("t")
        ax.plot(g["t"], g["JLoss"], color=BLUE, lw=1.5)
        ax.fill_between(g["t"], 0, g["JLoss"], color=BLUE, alpha=0.12, lw=0)
        ax.set_title(c, fontsize=9)
        ax.set_ylim(0, max(12, g["JLoss"].max() * 1.1))
    for ax in axes.ravel()[len(cs):]:
        ax.set_visible(False)
    fig.suptitle("JLoss trimestral por país — datos Bloomberg (motor v8, ρ=0,4)", y=1.01,
                 fontsize=11)
    _save(fig, "fig_jloss_paises")


def fig_h4b():
    f = pd.read_csv(os.path.join(HERE, "fase5_bbg.csv"))
    fig, ax = plt.subplots(figsize=(7, 3.2))
    labs, b4s, los, his, cols = [], [], [], [], []
    ref = [("v8: ampliado estructural", 720.7, 2.98), ]
    for _, x in f.iterrows():
        ci = eval(x["ci90"])
        labs.append(f"bbg: {x['base']} {x['HHI']}")
        b4s.append(x["b4"]); los.append(ci[0]); his.append(ci[1])
        cols.append(RED if x["b4"] < 0 else BLUE)
    labs.append("v8 (regulatorio): ampliado estructural"); b4s.append(720.7)
    los.append(np.nan); his.append(np.nan); cols.append("#888")
    y = np.arange(len(labs))[::-1]
    for yi, b, lo, hi, cc in zip(y, b4s, los, his, cols):
        if np.isfinite(lo):
            ax.plot([lo, hi], [yi, yi], color=cc, lw=1.4)
        ax.plot(b, yi, "o", color=cc, ms=6)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y[::-1] if False else np.arange(len(labs)))
    ax.set_yticks(np.arange(len(labs))); ax.set_yticklabels(labs[::-1], fontsize=8)
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


def fig_cobertura():
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2))
    for ax, fn, ttl in zip(axes, ["Panel_principal_bbg.csv", "Panel_ampliado_bbg.csv"],
                           ["Panel principal", "Panel ampliado"]):
        d = _prep(fn)
        cs = sorted(d["country"].unique())
        for i, c in enumerate(cs):
            g = d[d.country == c]
            ax.plot(g["t"], [i] * len(g), "|", color=BLUE, ms=8, mew=1.4)
        ax.set_yticks(range(len(cs))); ax.set_yticklabels(cs, fontsize=8)
        ax.set_title(ttl, color=INK)
        ax.grid(axis="y", visible=False)
    fig.suptitle("Cobertura efectiva del panel (trimestres con EMBI, JLoss y GaR)", y=1.0,
                 fontsize=11)
    _save(fig, "fig_cobertura")


def _save(fig, name):
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}.pdf")


def main():
    print("Figuras -> bbg/figuras/")
    fig_cobertura()
    fig_efecto_marginal()
    fig_forest_theta()
    fig_umbral()
    fig_jloss_paises()
    fig_h4b()
    fig_concordancia()


if __name__ == "__main__":
    main()
