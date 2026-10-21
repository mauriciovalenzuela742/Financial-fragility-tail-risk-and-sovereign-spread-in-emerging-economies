# -*- coding: utf-8 -*-
"""
p29_simulacion_v2.py -- simulación de tamaño y potencia v2: ¿qué vara de inferencia corresponde?

Objeción de árbitro a p22: aquel proceso generador (y* = ajuste + w_país x residuo, X fijo) es el
propio esquema de remuestreo del wild cluster bootstrap (lo favorece), destruye la dependencia
transversal, mantiene fijos los regresores pese a la retroalimentación spread -> fragilidad y no da
evidencia de tamaño para la especificación en primeras diferencias. Aquí:

  1. Implementaciones propias en numpy (transformación within bidireccional exacta para el panel no
     balanceado, MCO, Driscoll-Kraay con núcleo de Bartlett y el ancho de banda por defecto de
     linearmodels, cluster por país, doble cluster y wild cluster bootstrap restringido con pesos de
     Webb vectorizado en B), VALIDADAS contra linearmodels y contra p14.wild_boot.
  2. Procesos generadores:
       A. el de p22 (referencia): Rademacher por país sobre el residuo, X fijo.
       B. "criba con el corte transversal intacto": se impone la hipótesis, se toman los residuos
          restringidos, AR(2) por país, y se remuestrean VECTORES de innovaciones por fecha en
          bloques móviles de 4 trimestres (las mismas fechas para todos los países); X fijo.
       C. "VAR de panel con retroalimentación": VAR(1) con efectos fijos de país (y de trimestre al
          estimar; el efecto de tiempo se remuestrea como choque común de la fecha) en (y, J, D); se
          impone la nula en la ecuación de y, se remuestrean vectores de innovaciones por fecha y se
          REGENERAN J y D además de y. C0 = igual pero sin retroalimentación de y hacia J y D.
  3. Métodos al 5 %: DK con valores críticos normales; DK con valores críticos fixed-b (Kiefer y
     Vogelsang, 2005; se obtienen simulando la distribución límite con movimientos brownianos
     discretizados); DK con ancho de banda largo (0,2 T) y fixed-b; cluster por país sin corrección
     y normal (lo que reporta linearmodels, usado en p22); cluster por país CR1 con t(G-1); wild
     cluster bootstrap restringido por país (Webb). En primeras diferencias además: cluster por
     tiempo, doble cluster y wild bootstrap por trimestre.
  4. Especificación en niveles y en primeras diferencias; tamaño y potencia para b1 y b2; sesgo
     medio bajo H0 y razón entre el error estándar medio y la desviación Monte Carlo.

Elecciones documentadas:
  - Panel no balanceado al remuestrear por fecha: si en la fecha sorteada el país no tiene
    innovación, se usa la innovación de ese país en una fecha propia sorteada al azar (conserva su
    varianza; solo esa celda pierde el vínculo transversal).
  - AR(2) por país: si la raíz mayor supera 0,98 se contraen los coeficientes hasta 0,98.
  - En C la hipótesis nula es "coeficiente nulo en la ecuación de y del VAR" (no causalidad). Como
    el spread es persistente y sus innovaciones están correlacionadas con las de J y D, el
    coeficiente ESTÁTICO de la especificación principal no converge a cero bajo esa nula: se calcula
    su valor pseudo-verdadero con un panel simulado muy largo y se reportan dos tamaños: contra
    cero ("tam", mezcla inferencia e identificación) y contra el pseudo-verdadero ("tampt", solo
    inferencia más sesgo de muestra finita) y contra la media de muestra finita del estimador,
    obtenida en un piloto independiente ("tamc": solo calibración del error estándar).
  - El VAR es lineal: en C el coeficiente verdadero de la interacción es cero; la interacción se
    recalcula con J y D simulados y entra a la regresión como en la principal.

Salida: bbg/paper_inferencia_v2_numeros.csv; avance en bbg/_p29.log. No modifica ningún archivo.
"""
import os
import sys
import time
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # un solo hilo: la máquina se comparte con otras corridas
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy import stats

import p13_figuras_paper as p13
import p14_arbitro_lnlag as p14

S = int(os.environ.get("JLOSS_SIM", 1000))       # simulaciones
B = int(os.environ.get("JLOSS_SIM_B", 199))      # réplicas del wild bootstrap dentro de cada una
BLOQUE = 4                                       # largo del bloque móvil (trimestres)
QUEMA = 100                                      # períodos de calentamiento de las recursiones
TLARGO, RLARGO = 3000, 8                         # panel largo para el valor pseudo-verdadero
REGS = ["J_c", "T_c", "JxT"]
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
LOG = os.path.join(HERE, "_p29.log")
OUT = os.path.join(HERE, "paper_inferencia_v2_numeros.csv")
NUM = {}
COLS = ["b", "beta0", "se_dk", "se_dkl", "se_cln", "se_cl", "p_w", "se_t", "se_tw", "p_wt"]


def num(k, v):
    NUM[k] = float(v)
    return v


def log(msg):
    with open(LOG, "a", encoding="ascii", errors="replace") as fh:
        fh.write(msg + "\n"); fh.flush()
    print(msg, flush=True)


# ================================================================ 1. álgebra propia
class Panel:
    """estructura fija de un panel no balanceado: proyector within bidireccional e indicadoras."""

    def __init__(self, ci, qn):
        self.ci = np.asarray(ci); self.N = len(ci); self.G = int(self.ci.max()) + 1
        self.fechas, self.ti = np.unique(qn, return_inverse=True); self.T = len(self.fechas)
        n = np.arange(self.N)
        Dm = np.zeros((self.N, self.G + self.T)); Dm[n, self.ci] = 1.0; Dm[n, self.G + self.ti] = 1.0
        self.M = np.eye(self.N) - Dm @ np.linalg.pinv(Dm)      # aniquilador exacto de los EF
        self.Ic = np.zeros((self.G, self.N)); self.Ic[self.ci, n] = 1.0
        self.It = np.zeros((self.T, self.N)); self.It[self.ti, n] = 1.0
        self.neff = self.G + self.T - 1
        self.escala = self.N / (self.N - self.neff - 3)        # ajuste de linearmodels (EF y k = 3 regresores)
        self.bw = int(np.floor(4 * (self.T / 100) ** (2 / 9))) # ancho por defecto de linearmodels
        self.Ml = int(round(0.2 * self.T))                     # ancho largo: 0,2 T (pesos 1 - j/Ml)
        self.b_def = (self.bw + 1) / self.T; self.b_lar = self.Ml / self.T


def _bartlett(u, M):
    """varianza de largo plazo (sin dividir) de la serie escalar u con pesos 1 - j/M, j < M."""
    v = u @ u
    for j in range(1, M):
        v += 2.0 * (1.0 - j / M) * (u[j:] @ u[:-j])
    return v


def wild_rapido(Xw, XtXi, y0, ki, Ind, W):
    """wild cluster bootstrap restringido (H0: coef ki = 0 sobre y0), vectorizado en B.
    Ind: indicadoras cluster x obs; W: pesos B x G. Devuelve (p, t_obs)."""
    N, k = Xw.shape
    keep = [i for i in range(k) if i != ki]
    Xr = Xw[:, keep]
    f = Xr @ np.linalg.solve(Xr.T @ Xr, Xr.T @ y0); r = y0 - f
    Pf = Ind @ (Xw * f[:, None]); R = Ind @ (Xw * r[:, None])               # G x k
    Q = (Ind @ (Xw[:, :, None] * Xw[:, None, :]).reshape(N, k * k)).reshape(-1, k, k)
    bs = (Pf.sum(0)[None, :] + W @ R) @ XtXi                                # B x k
    s = Pf[None] + W[:, :, None] * R[None] - np.einsum("gij,bj->bgi", Q, bs)
    a = XtXi[ki]
    tb = bs[:, ki] / np.sqrt(((s @ a) ** 2).sum(1))
    b = XtXi @ (Xw.T @ y0); e = y0 - Xw @ b
    t_obs = b[ki] / np.sqrt((((Ind @ (Xw * e[:, None])) @ a) ** 2).sum())
    return float(np.mean(np.abs(tb) >= abs(t_obs))), float(t_obs)


def inferir(P, Xw, yw, ki, beta0, rng, fd=False, nB=None):
    """MCO sobre datos ya transformados y todos los errores estándar del coeficiente ki.
    Devuelve un vector en el orden de COLS."""
    nB = nB or B
    N, k = Xw.shape
    XtXi = np.linalg.inv(Xw.T @ Xw)
    b = XtXi @ (Xw.T @ yw); e = yw - Xw @ b
    a = XtXi[ki]
    xe = (Xw @ a) * e                                # contribución escalar de cada observación
    ut = P.It @ xe; uc = P.Ic @ xe
    v_dk = _bartlett(ut, P.bw + 1) * P.escala
    v_dkl = _bartlett(ut, P.Ml) * P.escala
    mc = uc @ uc
    v_cln = mc * P.escala                                        # linearmodels (sin corrección G)
    v_cl = mc * P.G / (P.G - 1) * (N - 1) / (N - k)              # CR1, como causal_core.cluster_se
    y0 = yw - beta0 * Xw[:, ki]
    p_w, _ = wild_rapido(Xw, XtXi, y0, ki, P.Ic, rng.choice(WEBB, size=(nB, P.G)))
    out = [b[ki], beta0, np.sqrt(v_dk), np.sqrt(v_dkl), np.sqrt(v_cln), np.sqrt(v_cl), p_w,
           np.nan, np.nan, np.nan]
    if fd:
        mt = ut @ ut
        v_t = mt * P.T / (P.T - 1) * (N - 1) / (N - k)
        v_tw = (mc + mt - xe @ xe) * P.escala                    # doble cluster (Cameron et al.)
        if v_tw <= 0:                                            # no definida positiva: se usa la mayor
            v_tw = max(mc, mt) * P.escala
            NUM["doble_no_positiva"] = NUM.get("doble_no_positiva", 0.0) + 1.0
        p_wt, _ = wild_rapido(Xw, XtXi, y0, ki, P.It, rng.choice(WEBB, size=(nB, P.T)))
        out[7:] = [np.sqrt(v_t), np.sqrt(v_tw), p_wt]
    return np.array(out, dtype=float)


def fixedb_sim(b, n=500, reps=60000, seed=5):
    """|t| bajo la distribución límite fixed-b (Bartlett, modelo con media estimada), simulada con
    paseos gaussianos discretizados de n pasos: t = raiz(n) media / raiz(HAC con M = b n)."""
    rng = np.random.default_rng(seed)
    M = max(1, int(round(b * n))); out = []
    for _ in range(reps // 5000):
        v = rng.standard_normal((5000, n)); m = v.mean(1); v -= m[:, None]
        om = (v * v).sum(1)
        for j in range(1, M):
            om += 2.0 * (1.0 - j / M) * (v[:, j:] * v[:, :-j]).sum(1)
        out.append(np.abs(np.sqrt(n) * m / np.sqrt(om / n)))
    return np.sort(np.concatenate(out))


def kv_poly(b):
    """aproximación polinómica de Kiefer y Vogelsang (2005), Bartlett, cuantil 97,5 % (de memoria;
    solo se imprime como contraste: los valores críticos usados son los simulados)."""
    return 1.9600 + 2.9694 * b + 0.4160 * b ** 2 - 0.5324 * b ** 3


# ================================================================ datos
def preparar():
    d = p13.datos()
    m0, dd = p13.fit(d)
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] + 0.0112) < 5e-4, (m0.nobs, m0.params["JxT"])
    q = pd.PeriodIndex(dd["quarter"], freq="Q")
    dd["_qn"] = q.year * 4 + q.quarter
    dd = dd.sort_values(["country", "_qn"]).reset_index(drop=True)
    paises = sorted(dd["country"].unique())
    dd["_ci"] = dd["country"].map({c: i for i, c in enumerate(paises)})
    g = dd.groupby("country")
    consec = (dd["_qn"] - g["_qn"].shift(1)) == 1
    for c in ["ln_EMBI"] + REGS:
        dd["d_" + c] = (dd[c] - g[c].shift(1)).where(consec)
    fd = dd.dropna(subset=["d_ln_EMBI", "d_J_c", "d_T_c", "d_JxT"]).copy()
    q0 = int(dd["_qn"].min()) - 1                       # la malla empieza un trimestre antes (rezago)
    Tg = int(dd["_qn"].max()) - q0 + 1
    E = {}
    for spec, df, y, regs in (("niv", dd, "ln_EMBI", REGS), ("fd", fd, "d_ln_EMBI", ["d_" + r for r in REGS])):
        P = Panel(df["_ci"].to_numpy(), df["_qn"].to_numpy())
        Xr = df[regs].to_numpy(float); yr = df[y].to_numpy(float)
        Xw = P.M @ Xr; yw = P.M @ yr
        XtXi = np.linalg.inv(Xw.T @ Xw); bh = XtXi @ (Xw.T @ yw)
        E[spec] = dict(P=P, df=df, y=y, regs=regs, Xw=Xw, yw=yw, XtXi=XtXi, bh=bh, e=yw - Xw @ bh,
                       pos=df["_qn"].to_numpy() - q0, fd=(spec == "fd"))
    E["fd"]["cur"] = fd.index.to_numpy(); E["fd"]["prev"] = fd.index.to_numpy() - 1
    assert (dd["_ci"].to_numpy()[E["fd"]["prev"]] == dd["_ci"].to_numpy()[E["fd"]["cur"]]).all()
    return d, dd, fd, m0, paises, q0, Tg, E


# ================================================================ validación
def validar(dd, fd, E, FB):
    log("== validacion contra linearmodels y p14.wild_boot (datos reales)")
    rng = np.random.default_rng(0)
    peor = 0.0
    for spec, df in (("niv", dd), ("fd", fd)):
        e = E[spec]; P = e["P"]
        idx = df.set_index(["country", "t"])
        F = f"{e['y']} ~ {' + '.join(e['regs'])} + EntityEffects + TimeEffects"
        ref = {"se_dk": PanelOLS.from_formula(F, idx).fit(**p14.DK),
               "se_dkl": PanelOLS.from_formula(F, idx).fit(cov_type="kernel", kernel="bartlett", bandwidth=P.Ml - 1),
               "se_cln": PanelOLS.from_formula(F, idx).fit(cov_type="clustered", cluster_entity=True)}
        if spec == "fd":
            ref["se_tw"] = PanelOLS.from_formula(F, idx).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        for ki, lab in enumerate(("b1", "b2", "b3")):
            r = dict(zip(COLS, inferir(P, e["Xw"], e["yw"], ki, 0.0, rng, fd=e["fd"])))
            n_ = e["regs"][ki]
            db = abs(r["b"] / ref["se_dk"].params[n_] - 1); peor = max(peor, db)
            txt = f"  {spec} {lab}: b={r['b']:+.6f} (dif.rel {db:.1e})"
            for k_, m in ref.items():
                dr = abs(r[k_] / m.std_errors[n_] - 1); peor = max(peor, dr)
                txt += f" | {k_}={r[k_]:.6f} vs {m.std_errors[n_]:.6f} ({dr:.1e})"
            log(txt)
            num(f"real_{spec}_b_{lab}", r["b"])
            # p-valores de cada método sobre los datos reales
            t = {k_: r["b"] / r[k_] for k_ in COLS if k_.startswith("se_") and np.isfinite(r[k_])}
            num(f"real_{spec}_p_dk_{lab}", 2 * stats.norm.sf(abs(t["se_dk"])))
            num(f"real_{spec}_p_dkfb_{lab}", np.mean(FB[(spec, "def")] >= abs(t["se_dk"])))
            num(f"real_{spec}_p_dklfb_{lab}", np.mean(FB[(spec, "lar")] >= abs(t["se_dkl"])))
            num(f"real_{spec}_p_paisn_{lab}", 2 * stats.norm.sf(abs(t["se_cln"])))
            num(f"real_{spec}_p_pais_{lab}", 2 * stats.t.sf(abs(t["se_cl"]), P.G - 1))
            if spec == "fd":
                num(f"real_{spec}_p_tiempo_{lab}", 2 * stats.t.sf(abs(t["se_t"]), P.T - 1))
                num(f"real_{spec}_p_doble_{lab}", 2 * stats.t.sf(abs(t["se_tw"]), P.G - 1))
                pt_, _ = wild_rapido(e["Xw"], e["XtXi"], e["yw"], ki, P.It,
                                     np.random.default_rng(7).choice(WEBB, size=(1999, P.T)))
                num(f"real_{spec}_p_wildt_{lab}", pt_)
        num(f"real_{spec}_N", P.N); num(f"real_{spec}_T", P.T); num(f"real_{spec}_bw", P.bw)
        num(f"real_{spec}_bw_largo", P.Ml - 1)
        # wild bootstrap: mismas 1.999 réplicas y semilla que p14 (pesos de Webb)
        for ki, lab in enumerate(("b1", "b2", "b3")):
            if spec == "fd" and ki == 2:
                continue
            p_ref, t_ref = p14.wild_boot(df, e["y"], e["regs"], e["regs"][ki], B=1999, seed=7, weights="webb")
            W = np.random.default_rng(7).choice(WEBB, size=(1999, P.G))
            p_mio, t_mio = wild_rapido(e["Xw"], e["XtXi"], e["yw"], ki, P.Ic, W)
            t_mio /= np.sqrt(P.G / (P.G - 1) * (P.N - 1) / (P.N - 3))    # p14 reporta el t con ajuste CR1
            tol = 4 * np.sqrt(2 * max(p_ref, 0.01) * (1 - p_ref) / 1999) + 1e-3
            log(f"  {spec} {lab}: wild p propio={p_mio:.4f} p14={p_ref:.4f} (tol MC {tol:.4f}) | "
                f"t cluster propio={t_mio:.6f} p14={t_ref:.6f}")
            assert abs(p_mio - p_ref) < tol and abs(t_mio / t_ref - 1) < 1e-6, (spec, lab, p_mio, p_ref)
            num(f"val_{spec}_wild_propio_{lab}", p_mio); num(f"val_{spec}_wild_p14_{lab}", p_ref)
            num(f"real_{spec}_p_wild_{lab}", p_mio)
    num("val_peor_dif_relativa", peor)
    assert peor < 1e-6, peor
    log(f"  peor diferencia relativa (coeficientes y errores estandar) = {peor:.2e}  -> OK")


# ================================================================ remuestreo por fecha
def fechas_bloque(rng, L, falta, obs):
    """índices de fecha (L x G): bloques móviles de BLOQUE trimestres comunes a todos los países;
    donde el país no tiene innovación en la fecha sorteada se usa una fecha propia al azar."""
    Ts, G = falta.shape
    ini = rng.integers(0, Ts - BLOQUE + 1, size=int(np.ceil(L / BLOQUE)))
    idx = (ini[:, None] + np.arange(BLOQUE)[None, :]).ravel()[:L]
    fin = np.repeat(idx[:, None], G, axis=1)
    for g in range(G):
        m = falta[idx, g]
        if m.any():
            fin[m, g] = obs[g][rng.integers(0, len(obs[g]), size=int(m.sum()))]
    return fin, idx


# ---------------------------------------------------------------- DGP B
def preparar_B(e, Tg):
    """por caso (coeficiente, hipótesis): ajuste restringido, AR(2) por país e innovaciones."""
    P = e["P"]; casos = []
    for ki in (0, 1):
        for hip, beta0 in (("tam", 0.0), ("pot", e["bh"][ki])):
            keep = [i for i in range(3) if i != ki]
            Xr = e["Xw"][:, keep]; y0 = e["yw"] - beta0 * e["Xw"][:, ki]
            f = Xr @ np.linalg.solve(Xr.T @ Xr, Xr.T @ y0)
            r = y0 - f
            Rg = np.full((Tg, P.G), np.nan); Rg[e["pos"], P.ci] = r
            phi = np.zeros((P.G, 2)); Eta = np.full((Tg, P.G), np.nan)
            for g in range(P.G):
                x = Rg[:, g]
                ok = np.zeros(Tg, bool); ok[2:] = np.isfinite(x[2:]) & np.isfinite(x[1:-1]) & np.isfinite(x[:-2])
                t = np.where(ok)[0]
                Z = np.column_stack([x[t - 1], x[t - 2]])
                ph = np.linalg.lstsq(Z, x[t], rcond=None)[0]
                rho = np.abs(np.roots([1.0, -ph[0], -ph[1]])).max()
                if rho > 0.98:                               # se contrae a la región estacionaria
                    c = 0.98 / rho; ph = np.array([ph[0] * c, ph[1] * c * c])
                    NUM["dgpB_ar2_contraidos"] = NUM.get("dgpB_ar2_contraidos", 0.0) + 1.0
                phi[g] = ph; Eta[t, g] = x[t] - Z @ ph
            casos.append(dict(ki=ki, hip=hip, fit=f + beta0 * e["Xw"][:, ki], phi=phi, Eta=Eta))
    falta = ~np.isfinite(casos[0]["Eta"])
    for c in casos:                                           # mismo patrón de faltantes en los 4 casos
        assert (falta == ~np.isfinite(c["Eta"])).all()
        c["Eta"] = np.nan_to_num(c["Eta"])
    return dict(casos=casos, falta=falta, obs=[np.where(~falta[:, g])[0] for g in range(P.G)],
                Eta=np.stack([c["Eta"] for c in casos]), phi=np.stack([c["phi"] for c in casos]))


def simular_B(pb, fin, Tg):
    """errores AR(2) reconstruidos recursivamente para los 4 casos a la vez: (4, Tg, G)."""
    G = fin.shape[1]; L = fin.shape[0]
    Es = pb["Eta"][:, fin, np.arange(G)[None, :]]             # 4 x L x G
    p1, p2 = pb["phi"][:, :, 0], pb["phi"][:, :, 1]
    out = np.empty_like(Es); e1 = np.zeros_like(p1); e2 = np.zeros_like(p1)
    for t in range(L):
        e0 = p1 * e1 + p2 * e2 + Es[:, t]
        out[:, t] = e0; e2 = e1; e1 = e0
    return out[:, L - Tg:]


# ---------------------------------------------------------------- DGP C
def preparar_C(paises):
    """VAR(1) de panel con EF de país y de trimestre en z = (ln EMBI, ln JLoss, D), todos los datos de
    los 13 países. Los EF de trimestre hacen que la matriz A sea la dinámica "dentro de cada fecha",
    la que identifica la especificación principal; el efecto de tiempo estimado no se descarta: es un
    choque común f_t que se remuestrea con la misma fecha sorteada que las innovaciones u_it, de modo
    que se conservan el choque común y la dependencia transversal restante. Si un país no tiene
    innovación en la fecha sorteada recibe el f_t de esa fecha y un u_it de una fecha propia al azar.
    Las fechas sin ningún dato se omiten (los bloques corren sobre las fechas con datos).
    Configuraciones: 0 = alternativa (sin restricción), 1 = nula en J, 2 = nula en D; variante C0
    excluye además el spread rezagado de las ecuaciones de J y D (sin retroalimentación)."""
    raw = p14.raw_panel()
    raw = raw[raw["country"].isin(paises)].sort_values(["country", "_qn"]).reset_index(drop=True)
    cols = ["ln_EMBI", "ln_JLoss", "D_pp"]
    g = raw.groupby("country")
    consec = (raw["_qn"] - g["_qn"].shift(1)) == 1
    for c in cols:
        raw[c + "_l"] = g[c].shift(1).where(consec)
    v = raw.dropna(subset=cols + [c + "_l" for c in cols]).copy()
    ci = v["country"].map({c: i for i, c in enumerate(paises)}).to_numpy()
    Z0 = v[cols].to_numpy(float); Z1 = v[[c + "_l" for c in cols]].to_numpy(float)
    G = len(paises)
    Pv = Panel(ci, v["_qn"].to_numpy())
    Z0d = Pv.M @ Z0; Z1d = Pv.M @ Z1                           # within bidireccional (país y trimestre)
    pos = Pv.ti; Tv = Pv.T                                     # fechas con datos, en orden
    Dm = np.zeros((Pv.N, G + Tv)); Dm[np.arange(Pv.N), ci] = 1.0; Dm[np.arange(Pv.N), G + pos] = 1.0
    Dp = np.linalg.pinv(Dm)
    falta = np.ones((Tv, G), bool); falta[pos, ci] = False
    var = {}
    for variante in ("C", "C0"):
        As, Us, Cs, Fs = [], [], [], []
        for cfg in range(3):
            A = np.zeros((3, 3))
            for k in range(3):
                inc = [0, 1, 2]
                if k == 0 and cfg > 0:
                    inc.remove(cfg)                 # nula: J (1) o D (2) fuera de la ecuación de y
                if k > 0 and variante == "C0":
                    inc.remove(0)                   # sin retroalimentación del spread
                A[k, inc] = np.linalg.lstsq(Z1d[:, inc], Z0d[:, k], rcond=None)[0]
            assert np.abs(np.linalg.eigvals(A)).max() < 1, "VAR no estacionario"
            # z_t - A z_{t-1} = c_i + f_t + u_it: se separan el efecto de país, el choque común de
            # la fecha (f_t, igual para todos los países) y la innovación idiosincrásica u_it
            W_ = Z0 - Z1 @ A.T
            th = Dp @ W_
            U = np.zeros((Tv, G, 3)); U[pos, ci] = W_ - Dm @ th
            As.append(A); Us.append(U); Cs.append(th[:G]); Fs.append(th[G:])
        var[variante] = dict(A=np.stack(As), U=np.stack(Us), c=np.stack(Cs), F=np.stack(Fs))
    A = var["C"]["A"][0]
    log("== VAR(1) de panel con EF de pais y de tiempo, z = (ln EMBI, ln JLoss, D); N = %d" % len(v))
    for k, n_ in enumerate(("y", "J", "D")):
        log("   ec. %s: %+.4f y(-1) %+.4f J(-1) %+.4f D(-1)" % (n_, A[k, 0], A[k, 1], A[k, 2]))
        for j, m_ in enumerate(("y", "J", "D")):
            num(f"var_A_{n_}_{m_}", A[k, j])
    log("   mayor raiz = %.4f" % np.abs(np.linalg.eigvals(A)).max())
    num("var_N", len(v)); num("var_raiz_max", np.abs(np.linalg.eigvals(A)).max())
    R = np.corrcoef((Z0d - Z1d @ A.T).T)
    num("var_corr_uy_uJ", R[0, 1]); num("var_corr_uy_uD", R[0, 2])
    log("   corr. contemporanea de innovaciones: (y,J) = %+.3f, (y,D) = %+.3f" % (R[0, 1], R[0, 2]))
    return dict(var=var, G=G, falta=falta, obs=[np.where(~falta[:, g_])[0] for g_ in range(G)])


def simular_C(pv, fi, Tsal):
    """simula las 3 configuraciones a la vez; devuelve niveles (3, Tsal, G, 3)."""
    fin, idx = fi
    L, G = fin.shape
    Us = pv["U"][:, fin, np.arange(G)[None, :], :] + pv["F"][:, idx][:, :, None, :]   # 3 x L x G x 3
    At = np.transpose(pv["A"], (0, 2, 1))
    dev = np.zeros((3, G, 3)); out = np.empty((3, Tsal, G, 3))
    for t in range(L):
        dev = dev @ At + pv["c"] + Us[:, t]
        if t >= L - Tsal:
            out[:, t - (L - Tsal)] = dev
    return out


def muestra_C(Z, E):
    """de los niveles simulados (Tg, G, 3) a las dos especificaciones sobre las celdas reales."""
    en, ef = E["niv"], E["fd"]
    ci, pos = en["P"].ci, en["pos"]
    y = Z[pos, ci, 0]; J = Z[pos - 1, ci, 1]; D = Z[pos - 1, ci, 2]
    J = J - J.mean(); D = D - D.mean()
    X = np.column_stack([J, D, J * D])
    dX = X[ef["cur"]] - X[ef["prev"]]; dy = y[ef["cur"]] - y[ef["prev"]]
    return {"niv": (en["P"].M @ X, en["P"].M @ y), "fd": (ef["P"].M @ dX, ef["P"].M @ dy)}


def pseudo_verdadero(pc, variante, rng):
    """valor al que converge el coeficiente estático (niveles y diferencias) en cada configuración:
    panel balanceado de 13 países y TLARGO trimestres, RLARGO repeticiones."""
    pv = pc["var"][variante]
    res = np.zeros((RLARGO, 3, 2, 3))                          # rep x cfg x spec x coef

    def dm(a):
        return a - a.mean(0, keepdims=True) - a.mean(1, keepdims=True) + a.mean()

    for r in range(RLARGO):
        fin = fechas_bloque(rng, QUEMA + TLARGO + 1, pc["falta"], pc["obs"])
        Zs = simular_C(pv, fin, TLARGO + 1)
        for cfg in range(3):
            Z = Zs[cfg]
            y = Z[1:, :, 0]; J = Z[:-1, :, 1]; D = Z[:-1, :, 2]
            J = J - J.mean(); D = D - D.mean()
            Xs = [J, D, J * D]
            for s_, (yy, XX) in enumerate(((y, Xs), (np.diff(y, axis=0), [np.diff(x, axis=0) for x in Xs]))):
                Xm = np.column_stack([dm(x).ravel() for x in XX])
                res[r, cfg, s_] = np.linalg.lstsq(Xm, dm(yy).ravel(), rcond=None)[0]
    return res.mean(0), res.std(0, ddof=1) / np.sqrt(RLARGO)


def centro_finito(pc, variante, E, Tg, rng, R=400):
    """media de muestra finita del coeficiente bajo H0 (piloto independiente de R réplicas): centra
    el contraste "tamc", que aísla la calibración del error estándar del sesgo del estimador."""
    acc = np.zeros((R, 2, 2))                                   # rep x spec x coef
    for r in range(R):
        Zs = simular_C(pc["var"][variante], fechas_bloque(rng, QUEMA + Tg, pc["falta"], pc["obs"]), Tg)
        for ki in (0, 1):
            m = muestra_C(Zs[ki + 1], E)
            for s_, spec in enumerate(("niv", "fd")):
                Xw, yw = m[spec]
                acc[r, s_, ki] = np.linalg.solve(Xw.T @ Xw, Xw.T @ yw)[ki]
    return acc.mean(0)


# ================================================================ simulación
def resumir(ACC, E, CV, s_hechas):
    """tasas de rechazo, errores Monte Carlo, sesgo y razones se/sd a partir de lo acumulado."""
    for (dgp, spec, hip, lab), filas in ACC.items():
        a = np.array(filas); r = dict(zip(COLS, a.T)); P = E[spec]["P"]
        d = r["b"] - r["beta0"]
        rech = {"dk": np.abs(d / r["se_dk"]) > 1.959964,
                "dkfb": np.abs(d / r["se_dk"]) > CV[(spec, "def")],
                "dklfb": np.abs(d / r["se_dkl"]) > CV[(spec, "lar")],
                "paisn": np.abs(d / r["se_cln"]) > 1.959964,
                "pais": np.abs(d / r["se_cl"]) > stats.t.ppf(0.975, P.G - 1),
                "wild": r["p_w"] < 0.05}
        ses = {"dk": "se_dk", "dkl": "se_dkl", "paisn": "se_cln", "pais": "se_cl"}
        if spec == "fd":
            rech["tiempo"] = np.abs(d / r["se_t"]) > stats.t.ppf(0.975, P.T - 1)
            rech["doble"] = np.abs(d / r["se_tw"]) > stats.t.ppf(0.975, P.G - 1)
            rech["wildt"] = r["p_wt"] < 0.05
            ses.update(tiempo="se_t", doble="se_tw")
        for met, v in rech.items():
            p = v.mean()
            num(f"dgp{dgp}_{spec}_{hip}_{met}_{lab}", p)
            num(f"dgp{dgp}_{spec}_{hip}_{met}_{lab}_ee", np.sqrt(p * (1 - p) / len(v)))
        num(f"dgp{dgp}_{spec}_{hip}_media_{lab}", r["b"].mean())
        if hip == "tam":
            sd = r["b"].std(ddof=1)
            num(f"dgp{dgp}_{spec}_sesgo_{lab}", r["b"].mean())            # verdadero bajo la nula = 0
            num(f"dgp{dgp}_{spec}_sesgo_{lab}_ee", sd / np.sqrt(len(d)))
            num(f"dgp{dgp}_{spec}_sd_{lab}", sd)
            for met, k_ in ses.items():
                num(f"dgp{dgp}_{spec}_razon_{met}_{lab}", r[k_].mean() / sd)
    num("S", s_hechas); num("B", B)
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)


def main():
    open(LOG, "w").close()
    t0 = time.time()
    log(f"p29: panel {os.path.basename(os.environ['JLOSS_PANEL_CSV'])} | S={S}, B={B}")
    d, dd, fd, m0, paises, q0, Tg, E = preparar()
    for spec in ("niv", "fd"):
        P = E[spec]["P"]
        log(f"  {spec}: N={P.N}, G={P.G}, T={P.T}, bw={P.bw} (b={P.b_def:.4f}), bw largo={P.Ml - 1} "
            f"(b={P.b_lar:.4f}), coef = " + ", ".join(f"{x:+.4f}" for x in E[spec]["bh"]))
    assert E["niv"]["P"].N == 765 and abs(E["niv"]["bh"][2] + 0.0112) < 5e-4 and E["fd"]["P"].N == 750

    # valores críticos fixed-b simulados
    FB, CV = {}, {}
    for spec in ("niv", "fd"):
        P = E[spec]["P"]
        for k_, b in (("def", P.b_def), ("lar", P.b_lar)):
            FB[(spec, k_)] = fixedb_sim(b)
            CV[(spec, k_)] = float(np.quantile(FB[(spec, k_)], 0.95))
            num(f"fixedb_{spec}_{k_}_b", b); num(f"fixedb_{spec}_{k_}_cv", CV[(spec, k_)])
            num(f"fixedb_{spec}_{k_}_cv_polinomio_kv", kv_poly(b))
            log(f"  fixed-b {spec} {k_}: b={b:.4f}  cv simulado={CV[(spec, k_)]:.3f}  polinomio KV={kv_poly(b):.3f}")
    validar(dd, fd, E, FB)

    PB = {spec: preparar_B(E[spec], Tg) for spec in ("niv", "fd")}
    for spec in ("niv", "fd"):
        ph = PB[spec]["phi"][0]
        log(f"  DGP B {spec}: AR(2) por pais (caso H0 b1), suma media de coeficientes = {ph.sum(1).mean():.3f}, "
            f"max = {ph.sum(1).max():.3f}")
        num(f"dgpB_{spec}_ar_suma_media", ph.sum(1).mean())
    PC = preparar_C(paises)
    PT = {}
    rngL = np.random.default_rng(29)
    for variante in ("C", "C0"):
        m, ee = pseudo_verdadero(PC, variante, rngL)
        PT[variante] = m
        for s_, spec in enumerate(("niv", "fd")):
            for ki, lab in enumerate(("b1", "b2")):
                num(f"dgp{variante}_{spec}_pseudo_{lab}", m[ki + 1, s_, ki])
                num(f"dgp{variante}_{spec}_pseudo_{lab}_ee", ee[ki + 1, s_, ki])
                num(f"dgp{variante}_{spec}_pseudo_alt_{lab}", m[0, s_, ki])
                log(f"  DGP {variante} {spec} {lab}: pseudo-verdadero bajo H0 = {m[ki + 1, s_, ki]:+.5f} "
                    f"(ee {ee[ki + 1, s_, ki]:.5f}); bajo H1 = {m[0, s_, ki]:+.5f}")
    CEN = {v_: centro_finito(PC, v_, E, Tg, rngL) for v_ in ("C", "C0")}
    for v_ in ("C", "C0"):
        for s_, spec in enumerate(("niv", "fd")):
            for ki, lab in enumerate(("b1", "b2")):
                num(f"dgp{v_}_{spec}_centro_{lab}", CEN[v_][s_, ki])
    log(f"  preparacion lista en {time.time() - t0:.0f} s; empieza la simulacion")

    rng = np.random.default_rng(11)
    ACC = {}

    def reg(dgp, spec, hip, lab, v):
        ACC.setdefault((dgp, spec, hip, lab), []).append(v)

    L = QUEMA + Tg
    t1 = time.time()
    for s in range(S):
        # ---- A: el de p22 (Rademacher por país sobre el residuo no restringido, X fijo)
        w = rng.choice([-1.0, 1.0], size=len(paises))
        for spec in ("niv", "fd"):
            e = E[spec]; P = e["P"]
            base = e["Xw"] @ e["bh"] + P.M @ (w[P.ci] * e["e"])
            for ki, lab in ((0, "b1"), (1, "b2")):
                reg("A", spec, "pot", lab, inferir(P, e["Xw"], base, ki, 0.0, rng, e["fd"]))
                reg("A", spec, "tam", lab, inferir(P, e["Xw"], base - e["bh"][ki] * e["Xw"][:, ki], ki, 0.0, rng, e["fd"]))
        # ---- B: criba AR(2) con vectores de innovaciones por fecha, X fijo
        for spec in ("niv", "fd"):
            e = E[spec]; P = e["P"]; pb = PB[spec]
            es = simular_B(pb, fechas_bloque(rng, L, pb["falta"], pb["obs"])[0], Tg)
            for c, caso in enumerate(pb["casos"]):
                ys = caso["fit"] + P.M @ es[c][e["pos"], P.ci]
                reg("B", spec, caso["hip"], ("b1", "b2")[caso["ki"]],
                    inferir(P, e["Xw"], ys, caso["ki"], 0.0, rng, e["fd"]))
        # ---- C y C0: VAR de panel, se regeneran y, J y D
        fin = fechas_bloque(rng, L, PC["falta"], PC["obs"])
        for variante in ("C", "C0"):
            Zs = simular_C(PC["var"][variante], fin, Tg)
            ms = [muestra_C(Zs[c], E) for c in range(3)]
            for s_, spec in enumerate(("niv", "fd")):
                P = E[spec]["P"]; f_ = E[spec]["fd"]
                for ki, lab in ((0, "b1"), (1, "b2")):
                    Xa, ya = ms[0][spec]; Xn, yn = ms[ki + 1][spec]
                    reg(variante, spec, "pot", lab, inferir(P, Xa, ya, ki, 0.0, rng, f_))
                    reg(variante, spec, "tam", lab, inferir(P, Xn, yn, ki, 0.0, rng, f_))
                    reg(variante, spec, "tampt", lab,
                        inferir(P, Xn, yn, ki, PT[variante][ki + 1, s_, ki], rng, f_))
                    reg(variante, spec, "tamc", lab, inferir(P, Xn, yn, ki, CEN[variante][s_, ki], rng, f_))
        if (s + 1) % 50 == 0:
            resumir(ACC, E, CV, s + 1)
            g = NUM.get
            log(f"   simulacion {s + 1}/{S} ({time.time() - t1:.0f} s) | tam niv b1 dk/wild: "
                f"A {g('dgpA_niv_tam_dk_b1'):.3f}/{g('dgpA_niv_tam_wild_b1'):.3f}  "
                f"B {g('dgpB_niv_tam_dk_b1'):.3f}/{g('dgpB_niv_tam_wild_b1'):.3f}  "
                f"C(c) {g('dgpC_niv_tamc_dk_b1'):.3f}/{g('dgpC_niv_tamc_wild_b1'):.3f}")
    resumir(ACC, E, CV, S)
    num("segundos", time.time() - t0)
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(OUT)

    # ---- tablas en pantalla
    for dgp in ("A", "B", "C", "C0"):
        for spec in ("niv", "fd"):
            mets = ["dk", "dkfb", "dklfb", "paisn", "pais", "wild"] + (["tiempo", "doble", "wildt"] if spec == "fd" else [])
            log(f"== DGP {dgp} | {spec} | rechazo al 5 % (b1 / b2), ee MC entre parentesis")
            for hip in ("tam", "tampt", "tamc", "pot"):
                if f"dgp{dgp}_{spec}_{hip}_dk_b1" not in NUM:
                    continue
                for met in mets:
                    k1, k2 = f"dgp{dgp}_{spec}_{hip}_{met}_b1", f"dgp{dgp}_{spec}_{hip}_{met}_b2"
                    log(f"   {hip:6s} {met:7s} {NUM[k1]:.3f} ({NUM[k1 + '_ee']:.3f}) / {NUM[k2]:.3f} ({NUM[k2 + '_ee']:.3f})")
            for lab in ("b1", "b2"):
                pre = f"dgp{dgp}_{spec}"
                txt = f"   {lab}: media H0 = {NUM[pre + '_sesgo_' + lab]:+.5f} (ee {NUM[pre + '_sesgo_' + lab + '_ee']:.5f}), sd = {NUM[pre + '_sd_' + lab]:.5f}"
                if pre + "_pseudo_" + lab in NUM:
                    txt += f", pseudo-verdadero = {NUM[pre + '_pseudo_' + lab]:+.5f}"
                txt += f", media H1 = {NUM[pre + '_pot_media_' + lab]:+.5f} | se/sd: "
                txt += ", ".join(f"{m_} {NUM[pre + '_razon_' + m_ + '_' + lab]:.2f}"
                                 for m_ in ("dk", "dkl", "paisn", "pais", "tiempo", "doble")
                                 if pre + "_razon_" + m_ + "_" + lab in NUM)
                log(txt)
    log(f"-> {OUT}  ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
