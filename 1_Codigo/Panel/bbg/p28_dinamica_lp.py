# -*- coding: utf-8 -*-
"""
p28_dinamica_lp.py -- ¿el efecto de la fragilidad sobre el spread es de NIVEL (persistente) o transitorio?

Objeción de árbitro: con rho = 0,937 el ADL de p21 (J_{t-1}: +0,034; J_{t-2}: -0,043) es la regresión
en primeras diferencias reescrita, no evidencia independiente, y el multiplicador de largo plazo que
implica tiene un error estándar enorme: los datos pueden estar callados sobre el efecto de nivel en
vez de mostrar que no existe. Tres ejercicios, cada uno con el spread PROMEDIO trimestral (panel) y
con el spread de CIERRE (media de los últimos 5 días hábiles, construido en p27 desde 2_Datos/embi.xlsx):

  a. Forma de corrección de errores (el mismo ADL de p21, reparametrizado):
         D.y_t = -alfa (y_{t-1} - theta J_{t-2} - phi D_{t-2}) + a D.J_{t-1} + c D.D_{t-1} + EF
     Se estima lineal (D.y_t sobre y_{t-1}, J_{t-2}, D_{t-2}, D.J_{t-1}, D.D_{t-1}); alfa = -pi_y,
     theta = -pi_J/pi_y, phi = -pi_D/pi_y. Intervalos por método delta y por Fieller (inversión de la
     restricción lineal pi_J + theta0 pi_y = 0, que no se rompe cuando alfa es cercano a cero).
     Pruebas: theta = 0 y theta = coeficiente estático de la especificación principal (0,0985 en logs).
  b. Proyecciones locales ACUMULADAS: y_{t+h} - y_{t-1} sobre D.J_{t-1} y D.D_{t-1}, h = 0..8, con dos
     rezagos de D.y, D.J y D.D, EF dobles, DK con ancho max(4, h+1). Con el cierre, el primer rezago de
     D.y (cierre_{t-1} - cierre_{t-2}) es simultáneo a D.J_{t-1}: la respuesta es la del choque de
     fragilidad ortogonal al movimiento del spread del mismo trimestre; se reporta también sin ese
     control. Para leer la persistencia se estima además la respuesta de la propia fragilidad
     (J_{t+h} - J_{t-2} sobre D.J_{t-1}): si el impulso de J se deshace, el spread puede volver a cero
     aun habiendo efecto de nivel.
  c. Corrección de sesgo de Nickell por jackknife de medio panel en el tiempo (Dhaene y Jochmans, 2015):
     theta_c = 2 theta - (theta_1 + theta_2)/2, con mitades por país (principal) y con fecha de corte
     común (alternativa). Se reporta rho corregido y el multiplicador de largo plazo corregido; su error
     estándar es el del método delta con la covarianza de la muestra completa evaluada en el punto
     corregido (aproximación).

Salidas: bbg/paper_dinamica_numeros.csv (o _nivlag) y la figura fig_lp_acumulada_lnlag (o _nivlag).
Reutiliza p13 (datos, fit, save), p14 (base, DK) y p27 (medidas trimestrales, rezagos).
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
import matplotlib.pyplot as plt
from scipy import stats

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14
import p27_fd_tiempos as p27

NIV = p13.NIV
SFX = "_nivlag" if NIV else ""
H = 8
NUM = {}
L, F, est = p27.L, p27.F, p27.est


def num(k, v):
    NUM[k] = float(v)
    return v


def pz(z):
    return float(2 * stats.norm.sf(abs(z)))


# ================================================================ a. corrección de errores
def ecm(S, y, yl, pref, estaticos):
    regs = [yl, "J2", "D2", "dJ1", "dD1"]
    m = est(S, y, regs)
    b, V = m.params, m.cov
    al = -b[yl]
    num(f"{pref}_N", m.nobs); num(f"{pref}_alfa", al); num(f"{pref}_alfa_se", m.std_errors[yl])
    num(f"{pref}_alfa_p", m.pvalues[yl]); num(f"{pref}_rho", 1 - al)
    num(f"{pref}_vida_media_trim", np.log(0.5) / np.log(1 - al) if 0 < al < 1 else np.nan)
    for r, lab in (("dJ1", "a"), ("dD1", "c"), ("J2", "piJ"), ("D2", "piD")):
        num(f"{pref}_{lab}", b[r]); num(f"{pref}_{lab}_p", m.pvalues[r])
    for r, lab, b0 in (("J2", "theta", estaticos[0]), ("D2", "phi", estaticos[1])):
        th = -b[r] / b[yl]
        g = np.array([b[r] / b[yl] ** 2, -1 / b[yl]])
        se = float(np.sqrt(g @ V.loc[[yl, r], [yl, r]].to_numpy() @ g))
        num(f"{pref}_{lab}", th); num(f"{pref}_{lab}_se", se)
        num(f"{pref}_{lab}_ic_lo", th - 1.96 * se); num(f"{pref}_{lab}_ic_hi", th + 1.96 * se)
        num(f"{pref}_{lab}_p0_delta", pz(th / se)); num(f"{pref}_{lab}_pest_delta", pz((th - b0) / se))
        num(f"{pref}_{lab}_estatico", b0)

        V2 = V.loc[[yl, r], [yl, r]].to_numpy()
        br, by = float(b[r]), float(b[yl])

        def p_lin(t0):          # H0: pi + t0 * pi_y = 0  (equivale a theta = t0); vectorizada
            t0 = np.asarray(t0, float)
            v = t0 ** 2 * V2[0, 0] + 2 * t0 * V2[0, 1] + V2[1, 1]
            return 2 * stats.norm.sf(np.abs((br + t0 * by) / np.sqrt(v)))
        num(f"{pref}_{lab}_p0_lineal", float(p_lin(0.0))); num(f"{pref}_{lab}_pest_lineal", float(p_lin(b0)))
        # intervalo de Fieller: valores t0 no rechazados al 5 % en una malla amplia
        G = 200 * abs(b0)
        grid = np.linspace(-G, G, 80001)
        ok = p_lin(grid) > 0.05
        num(f"{pref}_{lab}_fieller_lo", grid[ok].min() if ok.any() else np.nan)
        num(f"{pref}_{lab}_fieller_hi", grid[ok].max() if ok.any() else np.nan)
        num(f"{pref}_{lab}_fieller_no_acotado", float(ok[0] or ok[-1]))
        # si el conjunto no es acotado, lo informativo es la región RECHAZADA (un intervalo o nada)
        num(f"{pref}_{lab}_fieller_rech_lo", grid[~ok].min() if (~ok).any() else np.nan)
        num(f"{pref}_{lab}_fieller_rech_hi", grid[~ok].max() if (~ok).any() else np.nan)
        num(f"{pref}_{lab}_fieller_frac_rechazada", float((~ok).mean()))
        num(f"{pref}_{lab}_fieller_malla", G)
        num(f"{pref}_{lab}_ic_contiene_estatico", float(p_lin(b0) > 0.05))
    return m


# ================================================================ b. proyecciones locales acumuladas
def lp(W, ycol, pref, ctl, fija=False):
    """y_{t+h} - y_{t-1} sobre dJ1 y dD1 (+ controles); devuelve la tabla por horizonte."""
    rows = []
    base = W[W["in_est"] & W["in_est_l1"]].copy()
    if fija:
        base = base[np.isfinite(L(W, ycol, -H))[base.index]]
    for h in range(H + 1):
        S = base.copy()
        S["yh"] = L(W, ycol, -h)[S.index] - L(W, ycol, 1)[S.index]
        m = est(S, "yh", ["dJ1", "dD1"] + ctl, bw=max(4, h + 1))
        rows.append((h, m.params["dJ1"], m.std_errors["dJ1"], m.pvalues["dJ1"],
                     m.params["dD1"], m.std_errors["dD1"], m.pvalues["dD1"], int(m.nobs)))
        num(f"{pref}_h{h}_J", m.params["dJ1"]); num(f"{pref}_h{h}_J_se", m.std_errors["dJ1"]); num(f"{pref}_h{h}_J_p", m.pvalues["dJ1"])
        num(f"{pref}_h{h}_D", m.params["dD1"]); num(f"{pref}_h{h}_D_se", m.std_errors["dD1"]); num(f"{pref}_h{h}_D_p", m.pvalues["dD1"])
        num(f"{pref}_h{h}_N", m.nobs)
    return pd.DataFrame(rows, columns=["h", "bJ", "seJ", "pJ", "bD", "seD", "pD", "N"])


def lp_propia(W, col, x, pref, ctl):
    """respuesta de la propia variable de riesgo: col_{t+h-1} - col_{t-2} sobre su cambio en t-1."""
    base = W[W["in_est"] & W["in_est_l1"]].copy()
    for h in range(H + 1):
        S = base.copy()
        S["xh"] = L(W, col, 1 - h)[S.index] - L(W, col, 2)[S.index]
        if h == 0:
            num(f"{pref}_h0", 1.0)
            continue
        m = est(S, "xh", [x] + ctl, bw=max(4, h + 1))
        num(f"{pref}_h{h}", m.params[x]); num(f"{pref}_h{h}_se", m.std_errors[x])


def figura(ta, te):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
    yl = "EMBI" if NIV else "ln EMBI"
    for ax, b, se, tit in ((axes[0], "bJ", "seJ", "Fragilidad bancaria: " + (r"$\Delta$JLoss$_{t-1}$" if NIV else r"$\Delta\ln$JLoss$_{t-1}$")),
                           (axes[1], "bD", "seD", r"Riesgo de cola: $\Delta D_{t-1}$")):
        ax.axhline(0, color=p13.INK2, lw=0.8)
        for t, col, lab, mk in ((ta, p13.BLUE, "spread promedio del trimestre", "o-"),
                                (te, p13.ORANGE, "spread de cierre del trimestre", "s--")):
            ax.fill_between(t.h, t[b] - 1.96 * t[se], t[b] + 1.96 * t[se], color=col, alpha=0.13, lw=0)
            ax.plot(t.h, t[b], mk, color=col, lw=1.8, ms=4.5, label=lab)
        ax.set_xlabel("horizonte h (trimestres)")
        ax.set_title(tit, fontsize=9.5)
        ax.set_xticks(range(H + 1))
    axes[0].set_ylabel(f"respuesta acumulada de {yl}$_{{t+h}}$ − {yl}$_{{t-1}}$ (IC 95 %)", fontsize=8.5)
    axes[0].legend(frameon=False, fontsize=8, loc="best")
    p13.save(fig, "fig_lp_acumulada_lnlag")


# ================================================================ c. jackknife de medio panel
def mitades(S, comun=False):
    S = S.sort_values(["country", "_qn"])
    if comun:
        corte = S["_qn"].median()
        a = S["_qn"] <= corte
    else:
        r = S.groupby("country").cumcount()
        n = S.groupby("country")["_qn"].transform("size")
        a = r < (n // 2)
    return S[a], S[~a]


def jack(S, y, regs, yl, sumar, pref):
    """sumar: regresores cuya suma dividida por (1 - rho) es el multiplicador de largo plazo."""
    S = S.dropna(subset=[y] + regs).copy()
    m = est(S, y, regs)

    def lr(b):
        return float(sum(b[r] for r in sumar) / (1 - b[yl]))
    num(f"{pref}_N", m.nobs); num(f"{pref}_rho", m.params[yl]); num(f"{pref}_lp", lr(m.params))
    for r in sumar:
        num(f"{pref}_{r}", m.params[r])
    for lab, comun in (("jk", False), ("jkc", True)):
        h1, h2 = mitades(S, comun)
        b1, b2 = est(h1, y, regs).params, est(h2, y, regs).params
        bc = 2 * m.params - (b1 + b2) / 2
        num(f"{pref}_{lab}_N1", len(h1)); num(f"{pref}_{lab}_N2", len(h2))
        num(f"{pref}_{lab}_rho_m1", b1[yl]); num(f"{pref}_{lab}_rho_m2", b2[yl])
        num(f"{pref}_{lab}_rho", bc[yl])
        for r in sumar:
            num(f"{pref}_{lab}_{r}", bc[r])
        num(f"{pref}_{lab}_suma", sum(bc[r] for r in sumar))
        if bc[yl] < 1:
            th = lr(bc)
            g = pd.Series(0.0, index=m.params.index)
            g[sumar] = 1 / (1 - bc[yl]); g[yl] = sum(bc[r] for r in sumar) / (1 - bc[yl]) ** 2
            se = float(np.sqrt(g.to_numpy() @ m.cov.to_numpy() @ g.to_numpy()))
            num(f"{pref}_{lab}_lp", th); num(f"{pref}_{lab}_lp_se", se); num(f"{pref}_{lab}_lp_p", pz(th / se))
            num(f"{pref}_{lab}_vida_media", np.log(0.5) / np.log(bc[yl]) if bc[yl] > 0 else np.nan)
        else:
            num(f"{pref}_{lab}_lp", np.nan); num(f"{pref}_{lab}_lp_se", np.nan); num(f"{pref}_{lab}_lp_p", np.nan)
            num(f"{pref}_{lab}_vida_media", np.inf)
    g = pd.Series(0.0, index=m.params.index)
    g[sumar] = 1 / (1 - m.params[yl]); g[yl] = sum(m.params[r] for r in sumar) / (1 - m.params[yl]) ** 2
    se = float(np.sqrt(g.to_numpy() @ m.cov.to_numpy() @ g.to_numpy()))
    num(f"{pref}_lp_se", se); num(f"{pref}_lp_p", pz(NUM[f"{pref}_lp"] / se))


# ================================================================ main
def main():
    print("p28: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    d, raw = p14.base()
    m0, dd = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4
    est0 = (float(m0.params["J_c"]), float(m0.params["T_c"]))
    num("principal_b1", est0[0]); num("principal_b2", est0[1])
    muJ, muD = dd["ln_JLoss_l1"].mean(), dd["D_l1"].mean()

    W = raw[raw["country"].isin(d["country"].unique())].copy()
    W["t"] = pd.PeriodIndex(W["quarter"], freq="Q").to_timestamp()
    W = W.merge(p27.medidas_embi()[["country", "quarter", "eop"]], on=["country", "quarter"], how="left")
    W = W.merge(dd[["country", "quarter"]].assign(in_est=True), on=["country", "quarter"], how="left")
    W["in_est"] = W["in_est"].fillna(False).astype(bool)
    W = W.sort_values(["country", "_qn"]).reset_index(drop=True)
    W["in_est_l1"] = pd.Series(L(W, "in_est", 1)).fillna(False).astype(bool).to_numpy()
    W["y"] = F(W["EMBI_bps"]); W["ye"] = F(W["eop"])
    W["J"] = W["ln_JLoss"]; W["D"] = W["D_pp"]
    for v in ("J", "D"):
        for k in (1, 2, 3):
            W[f"{v}{k}"] = L(W, v, k)
            W[f"d{v}{k}"] = L(W, v, k) - L(W, v, k + 1)
    for v in ("y", "ye"):
        W[f"{v}_l1"] = L(W, v, 1)
        W[f"d{v}"] = W[v] - L(W, v, 1)
        W[f"d{v}_l1"] = L(W, v, 1) - L(W, v, 2)
        W[f"d{v}_l2"] = L(W, v, 2) - L(W, v, 3)
    W["Jc"] = W["J1"] - muJ; W["Dc"] = W["D1"] - muD; W["JxD"] = W["Jc"] * W["Dc"]
    tes = W[W["in_est"] & W["in_est_l1"]].copy()

    # ---------- a. corrección de errores
    m = ecm(tes, "dy", "y_l1", "ecm_avg", est0)
    if not NIV:      # debe coincidir con el ADL de p21 (rho = 0,937; J_{t-1} = +0,034)
        assert abs(NUM["ecm_avg_rho"] - 0.9369) < 1e-3 and abs(NUM["ecm_avg_a"] - 0.0339) < 1e-3, (NUM["ecm_avg_rho"], NUM["ecm_avg_a"])
    ecm(tes, "dye", "ye_l1", "ecm_eop", est0)
    # misma muestra que el cierre, con el promedio (aísla el efecto de la medida del de la muestra)
    ecm(tes.dropna(subset=["dye", "ye_l1"]), "dy", "y_l1", "ecm_avg_mc", est0)

    # ---------- b. proyecciones locales acumuladas
    cJD = ["dJ2", "dJ3", "dD2", "dD3"]
    ta = lp(W, "y", "lp_avg", ["dy_l1", "dy_l2"] + cJD)
    te = lp(W, "ye", "lp_eop", ["dye_l1", "dye_l2"] + cJD)
    lp(W, "ye", "lp_eop_sinly", cJD)
    lp(W, "y", "lp_avg_sinly", cJD)
    lp(W, "ye", "lp_eop_sinctl", [])
    lp(W, "y", "lp_avg_fija", ["dy_l1", "dy_l2"] + cJD, fija=True)
    lp(W, "ye", "lp_eop_fija", ["dye_l1", "dye_l2"] + cJD, fija=True)
    lp_propia(W, "J", "dJ1", "lpJ", ["dJ2", "dJ3", "dD1", "dD2", "dD3"])
    lp_propia(W, "D", "dD1", "lpD", ["dD2", "dD3", "dJ1", "dJ2", "dJ3"])
    for pref, t in (("lp_avg", ta), ("lp_eop", te)):
        num(f"{pref}_J_pico_h", t.loc[t.bJ.idxmax(), "h"]); num(f"{pref}_J_pico", t.bJ.max())
        num(f"{pref}_J_h8_sobre_pico", t.bJ.iloc[-1] / t.bJ.max())
        num(f"{pref}_J_n_sig05", (t.pJ < 0.05).sum()); num(f"{pref}_D_n_sig05", (t.pD < 0.05).sum())
        for h in (4, 8):     # multiplicador dinámico: respuesta del spread / respuesta de la propia fragilidad
            num(f"{pref}_J_mult_h{h}", NUM[f"{pref}_h{h}_J"] / NUM[f"lpJ_h{h}"])
    figura(ta, te)
    print("  LP promedio:\n", ta.round(4).to_string(index=False))
    print("  LP cierre:\n", te.round(4).to_string(index=False))

    # ---------- c. jackknife de medio panel
    for lab, y, yl in (("avg", "y", "y_l1"), ("eop", "ye", "ye_l1")):
        S = tes if lab == "avg" else tes.dropna(subset=["ye", "ye_l1"])
        S = S[S["in_est"]]
        jack(S, y, [yl, "Jc", "Dc", "JxD"], yl, ["Jc"], f"jk_din_{lab}")           # dinámica de p14 (un rezago)
        jack(S, y, [yl, "J1", "J2", "D1", "D2"], yl, ["J1", "J2"], f"jk_adl_{lab}")  # ADL de p21 (dos rezagos)
        jack(S, y, [yl, "J1", "J2", "D1", "D2"], yl, ["D1", "D2"], f"jk_adlD_{lab}")
    # dinámica de p14 sobre su muestra completa (765 - sin rezago del spread)
    S = W[W["in_est"]].copy()
    jack(S, "y", ["y_l1", "Jc", "Dc", "JxD"], "y_l1", ["Jc"], "jk_p14")
    num("jk_T_medio", S.groupby("country").size().mean())
    num("jk_nickell_aprox", -(1 + NUM["jk_p14_rho"]) / S.groupby("country").size().mean())

    out = os.path.join(HERE, f"paper_dinamica_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        sys.stdout.buffer.write(f"  {k:34s} {v: .4f}\n".encode("ascii", "replace"))
    print("->", out)


if __name__ == "__main__":
    main()
