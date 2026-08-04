"""
gar_engine.py — Motor Growth-at-Risk (port Python del pipeline CEMLA C-GARP).
Reemplaza la dependencia de R/rqpd. Diseñado para estimación en VENTANA EXPANSIVA.

Estado de validación contra GaR_test.xlsx (selected_date=01/12/2023, h=1,
indep=g_GDP,VIX, orth FCI~VIX):
  - Etapa 1 (lead/orth/z-score):  max|diff| ~1e-15  (exacto).
  - Etapa 2 (estimador pfe, LP):  el LP HiGHS alcanza el OPTIMO GLOBAL exacto del
        estimador de efectos fijos compartidos (Koenker 2004). El objetivo es
        ESTRICTAMENTE menor que el de rqpd (2.40614 vs 2.40654): rqpd se detiene
        antes por tolerancia del Frisch-Newton. Coeficientes dentro de ~1e-3.
  - Etapa 3 (KDE->GaR): partes deterministas (raiz GaR, momentos, ES/LR) correctas.
        PENDIENTE: el selector de ancho de banda de ks::kde. Se retro-calculo un
        ancho efectivo h ~= 6.7 * sd(Q), estable entre paises. Parametro BW_MULT.
        Para fidelidad 1e-6 hay que portar ks::hpi; ver nota al pie.
"""
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import linprog, brentq
from scipy.interpolate import CubicSpline
from scipy.integrate import quad

# Constante calibrada del ancho de banda triweight (retro-calculo vs GaR_test).
BW_MULT = 6.7


def zscore(x):
    x = np.asarray(x, float)
    return (x - np.nanmean(x)) / np.nanstd(x, ddof=1)


def preprocess(panel, selected_date, dependent, independent,
               orth_dep, orth_ind, h):
    """Construye future_dep_var (lead h), residuos ortogonalizados y z-scores,
    por pais, restringiendo a Date <= selected_date. No mira datos futuros mas
    alla de la construccion del lead (que es la variable a predecir)."""
    orth_vars = [f'{d}_{i}_res' for d, i in zip(orth_dep, orth_ind)]
    my = panel.copy()
    my['_d'] = pd.to_datetime(my['Date'], format='%d/%m/%Y', errors='coerce')
    sd = pd.to_datetime(selected_date, format='%d/%m/%Y')
    my = my[my['_d'] <= sd].copy()
    out = []
    for c in my['N_Country'].unique():
        loc = my[my['N_Country'] == c].copy()
        for d, i, ov in zip(orth_dep, orth_ind, orth_vars):
            res = np.full(len(loc), np.nan)
            mask = loc[d].notna() & loc[i].notna()
            if mask.sum() > 1:
                X = np.c_[np.ones(mask.sum()), loc.loc[mask, i].values]
                beta, *_ = np.linalg.lstsq(X, loc.loc[mask, d].values, rcond=None)
                res[mask.values] = loc.loc[mask, d].values - X @ beta
            loc[ov] = res
        loc['future_dep_var'] = loc[dependent].shift(-h)   # lead crudo (sin z)
        for v in list(independent) + orth_vars:
            loc[v] = zscore(loc[v].values)
        out.append(loc)
    return pd.concat(out).drop(columns='_d'), orth_vars


def fit_pfe(est, p_names, n_tau=19):
    """Estimador de panel con efectos fijos compartidos (rqpd 'pfe') resuelto
    como UN programa lineal. Normalizacion: ultima categoria de pais = base
    (a_base = 0), intercepto por cuantil. Devuelve c_hat, b_hat, a_hat."""
    taus = np.arange(1, n_tau + 1) / (n_tau + 1)
    w = np.full(n_tau, 1 / n_tau)
    X = est[p_names].values
    y = est['future_dep_var'].values
    ci = est['N_Country'].astype(int).values
    countries = sorted(np.unique(ci)); base = countries[-1]
    free_c = [c for c in countries if c != base]
    a_index = {c: i for i, c in enumerate(free_c)}
    p = len(p_names); n = len(est)

    off_c = 0; off_b = n_tau; off_a = off_b + n_tau * p
    off_rp = off_a + len(free_c); off_rm = off_rp + n_tau * n
    nvar = off_rm + n_tau * n

    cost = np.zeros(nvar)
    rows = []; cols = []; vals = []; beq = np.zeros(n_tau * n); r = 0
    for k in range(n_tau):
        tk = taus[k]
        for j in range(n):
            rows.append(r); cols.append(off_c + k); vals.append(1.0)
            for jj in range(p):
                rows.append(r); cols.append(off_b + k * p + jj); vals.append(X[j, jj])
            if ci[j] != base:
                rows.append(r); cols.append(off_a + a_index[ci[j]]); vals.append(1.0)
            rp = off_rp + k * n + j; rm = off_rm + k * n + j
            rows.append(r); cols.append(rp); vals.append(1.0)
            rows.append(r); cols.append(rm); vals.append(-1.0)
            beq[r] = y[j]; cost[rp] = w[k] * tk; cost[rm] = w[k] * (1 - tk); r += 1

    Aeq = sparse.csr_matrix((vals, (rows, cols)), shape=(n_tau * n, nvar))
    bounds = [(None, None)] * off_rp + [(0, None)] * (2 * n_tau * n)
    sol = linprog(cost, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    if sol.status != 0:
        raise RuntimeError(f'LP no convergio: {sol.message}')
    c_hat = sol.x[off_c:off_c + n_tau]
    b_hat = sol.x[off_b:off_b + n_tau * p].reshape(n_tau, p)
    a_hat = {base: 0.0}
    for c in free_c:
        a_hat[c] = sol.x[off_a + a_index[c]]
    return c_hat, b_hat, a_hat


def _triw_pdf(data, h):
    data = np.asarray(data, float); n = len(data)
    def fhat(x):
        x = np.atleast_1d(x).astype(float); out = np.zeros_like(x)
        for d in data:
            u = (x - d) / h; m = np.abs(u) < 1
            out[m] += (35 / 32) * (1 - u[m] ** 2) ** 3
        return out / (n * h)
    return fhat


def gar_distribution(Q, probability=0.05, bw_mult=BW_MULT,
                     x_min=-100.0, x_max=100.0, n_grid=5000):
    """Ajusta la distribucion condicional por KDE triweight sobre los cuantiles
    Q (vector tau) y extrae GaR, prob de crecimiento negativo, ES, ER y momentos.
    Ancho de banda: h = bw_mult * sd(Q)  (calibrado vs ks::kde)."""
    Q = np.asarray(Q, float)
    if np.isnan(Q).any():
        return {k: np.nan for k in
                ['GaR', 'prob_neg', 'ES', 'ER', 'mean', 'std', 'skew', 'kurt']}
    h = bw_mult * np.std(Q, ddof=1)
    xg = np.linspace(x_min, x_max, n_grid)
    fv = _triw_pdf(Q, h)(xg)
    Fv = np.concatenate([[0], np.cumsum((fv[:-1] + fv[1:]) / 2 * np.diff(xg))])
    PDF = CubicSpline(xg, fv); CDF = CubicSpline(xg, Fv)

    def _root(level, lo, hi):
        """uniroot robusto: si el nivel no esta bracketeado en el soporte
        (distribucion muy desplazada), devuelve la frontera de masa en vez de
        fallar. Evita interrumpir la serie en trimestres extremos (p.ej. COVID)."""
        flo, fhi = CDF(lo) - level, CDF(hi) - level
        if flo > 0:           # toda la masa por encima del nivel -> cuantil <= lo
            return float(lo)
        if fhi < 0:           # toda la masa por debajo -> cuantil >= hi
            return float(hi)
        return brentq(lambda x: CDF(x) - level, lo, hi, xtol=1e-4)

    GaR = _root(probability, x_min, x_max)
    up = _root(1 - probability, (x_min + x_max) / 2, x_max)
    mu = quad(lambda x: x * PDF(x), x_min, x_max, limit=200)[0]
    var = quad(lambda x: (x - mu) ** 2 * PDF(x), x_min, x_max, limit=200)[0]
    sd = np.sqrt(var)
    m3 = quad(lambda x: (x - mu) ** 3 * PDF(x), x_min, x_max, limit=200)[0]
    m4 = quad(lambda x: (x - mu) ** 4 * PDF(x), x_min, x_max, limit=200)[0]
    ES = (1 / probability) * quad(lambda x: x * PDF(x), x_min, GaR, limit=200)[0]
    ER = (1 / probability) * quad(lambda x: x * PDF(x), up, x_max, limit=200)[0]
    return {'GaR': GaR, 'prob_neg': float(CDF(0)), 'ES': ES, 'ER': ER,
            'mean': mu, 'std': sd, 'skew': m3 / sd ** 3, 'kurt': m4 / sd ** 4}


def gar_from_quantiles(Q, taus, probability=0.05):
    """Metodo DIRECTO (recomendado): lee el GaR y la cola directamente de la
    funcion cuantil estimada, sin KDE ni ancho de banda.

    - rearrangement (Chernozhukov, Fernandez-Val & Galichon 2010): se ordena Q
      para garantizar monotonicidad (corrige cruces de cuantiles).
    - GaR  = Q(probability), interpolado sobre la rejilla de taus.
    - prob_neg = tau tal que Q(tau)=0  (inversa de la funcion cuantil).
    - ES   = (1/p) * integral_0^p Q(tau) dtau, con la cola por debajo del menor
      tau extrapolada linealmente hasta tau=0 (transparente; para mayor finura
      basta aumentar n_tau).
    - mean = integral_0^1 Q(tau) dtau (trapecio sobre la rejilla, extremos
      extrapolados). skew/kurt: medidas robustas (Bowley / Moors), sin densidad.
    """
    Q = np.asarray(Q, float)
    if np.isnan(Q).any():
        return {k: np.nan for k in ['GaR', 'prob_neg', 'ES', 'ER',
                                    'mean', 'std', 'skew', 'kurt']}
    taus = np.asarray(taus, float)
    order = np.argsort(taus); taus = taus[order]; Q = np.sort(Q[order])  # rearrange

    GaR = float(np.interp(probability, taus, Q))
    ER = float(np.interp(1 - probability, taus, Q))
    # prob de crecimiento negativo = tau donde el cuantil cruza 0
    if Q[0] >= 0:
        prob_neg = 0.0
    elif Q[-1] <= 0:
        prob_neg = 1.0
    else:
        prob_neg = float(np.interp(0.0, Q, taus))
    # rejilla aumentada con extremos extrapolados linealmente a tau=0 y tau=1
    tg = np.concatenate(([0.0], taus, [1.0]))
    q0 = Q[0] - (Q[1] - Q[0]) / (taus[1] - taus[0]) * taus[0]
    q1 = Q[-1] + (Q[-1] - Q[-2]) / (taus[-1] - taus[-2]) * (1 - taus[-1])
    qg = np.concatenate(([q0], Q, [q1]))
    # ES: media de la cola izquierda hasta el nivel probability
    lo = tg <= probability
    t_es = np.concatenate((tg[lo], [probability]))
    q_es = np.concatenate((qg[lo], [GaR]))
    ES = float(np.trapezoid(q_es, t_es) / probability)
    mean = float(np.trapezoid(qg, tg))
    # dispersion y forma robustas (cuantil-based)
    q05, q25, q50, q75, q95 = [float(np.interp(p, taus, Q))
                               for p in (.05, .25, .5, .75, .95)]
    iqr = q75 - q25
    iqr_05_95 = q95 - q05                          # anchura de cola (dispersion)
    std = iqr / 1.349                              # escala robusta ~ sd normal
    skew = (q75 + q25 - 2 * q50) / iqr if iqr > 0 else np.nan   # Bowley
    e1, e7 = [float(np.interp(p, taus, Q)) for p in (1/8, 7/8)]
    e3, e5 = [float(np.interp(p, taus, Q)) for p in (3/8, 5/8)]
    kurt = ((e7 - e5) + (e3 - e1)) / iqr if iqr > 0 else np.nan  # Moors
    return {'GaR': GaR, 'prob_neg': prob_neg, 'ES': ES, 'ER': ER,
            'mean': mean, 'std': std, 'iqr_05_95': iqr_05_95,
            'skew': skew, 'kurt': kurt}


def _skewt_pdf(xg, xi, om, al, nu):
    """Densidad skew-t de Azzalini & Capitanio (2003)."""
    from scipy import stats
    z = (xg - xi) / om
    return (2 / om) * stats.t.pdf(z, nu) * \
        stats.t.cdf(al * z * np.sqrt((nu + 1) / (z ** 2 + nu)), nu + 1)


def _skewt_quantiles(taus, xi, om, al, nu, span=8.0, ngrid=800):
    xg = np.linspace(xi - span * om, xi + span * om, ngrid)
    pdf = _skewt_pdf(xg, xi, om, al, nu)
    cdf = np.concatenate([[0], np.cumsum((pdf[:-1] + pdf[1:]) / 2 * np.diff(xg))])
    cdf /= cdf[-1]
    return np.interp(taus, cdf, xg)


def gar_from_skewt(Q, taus, probability=0.05, anchor=(0.05, 0.25, 0.75, 0.95)):
    """Metodo de ROBUSTEZ (Adrian, Boyarchenko & Giannone 2019): ajusta una
    skew-t a los cuantiles QR minimizando la distancia cuadratica en los taus
    ancla, y deriva GaR, dispersion y asimetria de la distribucion ajustada.
    Devuelve tambien los parametros estructurales (escala om = anchura de cola;
    nu = fatness; al = asimetria)."""
    from scipy import optimize, special
    Q = np.asarray(Q, float)
    if np.isnan(Q).any():
        return {k: np.nan for k in ['GaR_st', 'mean_st', 'std_st', 'scale_st',
                                    'alpha_st', 'nu_st', 'skew_st', 'sse_st']}
    taus = np.asarray(taus, float); Qs = np.sort(Q)
    qa = np.interp(anchor, taus, Qs)
    iqr = qa[2] - qa[1] if qa[2] > qa[1] else np.std(Q, ddof=1)

    def obj(p):
        xi, lom, al, lnu = p
        qm = _skewt_quantiles(np.array(anchor), xi, np.exp(lom), al,
                              2.1 + np.exp(lnu))
        return np.sum((qm - qa) ** 2)

    x0 = [np.median(Q), np.log(max(iqr / 1.35, 1e-4)), 0.0, np.log(8.0)]
    r = optimize.minimize(obj, x0, method='Nelder-Mead',
                          options={'xatol': 1e-6, 'fatol': 1e-12, 'maxiter': 600})
    xi, lom, al, lnu = r.x; om = np.exp(lom); nu = 2.1 + np.exp(lnu)
    GaR_st = float(_skewt_quantiles(np.array([probability]), xi, om, al, nu)[0])
    d = al / np.sqrt(1 + al ** 2)
    c = np.sqrt(nu / np.pi) * np.exp(special.gammaln((nu - 1) / 2) -
                                     special.gammaln(nu / 2))
    mean = xi + om * d * c if nu > 1 else np.nan
    var = om ** 2 * (nu / (nu - 2) - (d * c) ** 2) if nu > 2 else np.nan
    std = np.sqrt(var) if (var == var and var > 0) else np.nan
    return {'GaR_st': GaR_st, 'mean_st': mean, 'std_st': std, 'scale_st': om,
            'alpha_st': al, 'nu_st': nu, 'skew_st': d, 'sse_st': r.fun}


def estimate_at(panel, selected_date, dependent='g_GDP',
                independent=('g_GDP', 'VIX'), orth_dep=('FCI',),
                orth_ind=('VIX',), h=1, n_tau=19, probability=0.05,
                method='quantile'):
    """Snapshot completo en una fecha: devuelve un DataFrame por pais con el GaR
    y la distribucion condicional. Para la serie en ventana expansiva, llamar
    esta funcion sobre cada fecha de corte del panel."""
    est_all, orth_vars = preprocess(panel, selected_date, dependent,
                                    list(independent), list(orth_dep),
                                    list(orth_ind), h)
    p_names = list(independent) + orth_vars
    est = est_all[est_all[['future_dep_var'] + p_names].notna().all(axis=1)].copy()
    c_hat, b_hat, a_hat = fit_pfe(est, p_names, n_tau)
    taus = np.arange(1, n_tau + 1) / (n_tau + 1)
    top = est_all[est_all['Date'] == selected_date].sort_values('N_Country')
    recs = []
    for _, row in top.iterrows():
        c = int(row['N_Country']); xv = row[p_names].values.astype(float)
        if np.isnan(xv).any():
            d = {'GaR': np.nan}
        else:
            Q = c_hat + (xv @ b_hat.T) + a_hat[c]
            if method == 'kde':
                d = gar_distribution(Q, probability)
            else:
                d = gar_from_quantiles(Q, taus, probability)
                if method == 'both':
                    d.update(gar_from_skewt(Q, taus, probability))
        recs.append({'date': selected_date, 'country': row['Country'], **d})
    return pd.DataFrame(recs)


if __name__ == '__main__':
    panel = pd.read_excel('GaR_panel.xlsx', sheet_name='Panel')
    print(estimate_at(panel, '01/12/2023').to_string(index=False))

# -----------------------------------------------------------------------------
# NOTA DE CALIBRACION (etapa 3):
# ks::kde usa por defecto el ancho plug-in ks::hpi (Wand & Jones 1994, 2 etapas)
# y, para kernel="triw", un reescalado canonico del ancho gaussiano. El retro-
# calculo sobre GaR_test arroja h_efectivo ~= 6.7*sd(Q), estable entre paises.
# Dos caminos para cerrar la etapa 3:
#   (A) Portar ks::hpi exacto (validar contra R o contra las 5 filas de
#       Distribution results de GaR_test) -> fidelidad 1e-6.
#   (B) Fijar BW_MULT como regla metodologica documentada en el paper. La serie
#       GaR de la tesis solo requiere consistencia interna + metodologia
#       declarada, no replicar bit a bit el ejemplo CEMLA.
# -----------------------------------------------------------------------------
