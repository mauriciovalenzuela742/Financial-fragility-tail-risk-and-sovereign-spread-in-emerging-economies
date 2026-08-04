"""
fci_engine.py — Indice de Condiciones Financieras (FCI), porteo Python del
framework CEMLA C-GARP (fci_*.R). Replica fielmente la metodologia:

  series diarias (STX, Ryr, CPI domesticas + Rbs, CPIbs de EE.UU.)
    -> indicadores de estres diarios (VSTX, CMAX, VRyr, CDIFF)
    -> colapso a fin de mes
    -> rEER mensual -> (VEER, CUMUL)
    -> estandarizacion expansiva (method_b_max, timeFrame=120)
    -> subindices iSTX, iRyr, iEER
    -> correlaciones EWMA (lambda=0.85)
    -> FCI = forma cuadratica  I' C I   (estres financiero sistemico)

Convencion (igual que en R): durante el bloque diario/mensual de estres las
fechas se ordenan DESCENDENTE (fila 0 = mas reciente); el lag [k] vs [k+w] mira
hacia atras en el tiempo. La estandarizacion se hace en orden ASCENDENTE.

Insumos por pais (CSV, formato CEMLA):
  CPI*.csv, Ryr*.csv, STX*.csv : col DATES (DD/MM/YYYY) + col homonima (diaria)
  rEER*.csv                    : col DATES (YYYYMM)      + col rEER (mensual)
  Pais de referencia US: CPI*.csv y Ryr*.csv (diarias).
"""
import numpy as np
import pandas as pd

# ----------------------------- Parametros (defaults CEMLA) -------------------
LAG_TILDE = 260 * 10 - 1     # ventana sd rolling diaria (~10 anios)
LAG_PERIOD = 20              # ventana indicador de volatilidad (~1 mes)
LAG_WINDOW = 260 * 2         # ventana desempenio acumulado (~2 anios)
LAG_YEAR = 261               # ventana inflacion interanual (dias habiles)
LAG_TILDE_M = 119            # ventana sd rolling mensual (~10 anios)
LAG_MONTH = 1                # cambio mensual rEER
LAG_WINDOW_M = 6             # ventana acumulada rEER (semestre)
TIME_FRAME = 120             # ventana base de estandarizacion / corr EWMA
LAMBDA = 0.85               # suavizado EWMA


# ----------------------------- Utilidades ------------------------------------
def _interp_na(s):
    """Interpolacion lineal de NA internos + relleno de extremos (≈ imputeTS)."""
    return s.interpolate(method='linear', limit_direction='both')


def _first_na(v):
    """Primer indice NaN (equivalente a get_min_NA de R)."""
    idx = np.where(np.isnan(v))[0]
    return idx[0] if len(idx) else len(v)


def _roll_fwd(x, w, func):
    """out[k] = func(x[k:k+w]) para k=0..n-w; NaN despues. Datos descendentes,
    por lo que la ventana [k:k+w] mira hacia el pasado."""
    x = np.asarray(x, float); n = len(x)
    out = np.full(n, np.nan)
    if n < w:
        return out
    win = np.lib.stride_tricks.sliding_window_view(x, w)   # (n-w+1, w)
    out[:n - w + 1] = func(win, axis=1)
    return out


def _sd(a, axis):       # sd muestral (ddof=1), como R
    return np.std(a, axis=axis, ddof=1)


# ----------------------------- Carga e integracion ---------------------------
def business_days(d1, d2):
    """Rango de dias habiles (lun-vie) en orden DESCENDENTE."""
    d = pd.bdate_range(d1, d2)
    return pd.DatetimeIndex(d[::-1])


def _read_daily(path, name):
    df = pd.read_csv(path)
    df.columns = ['DATES', name]
    df['DATES'] = pd.to_datetime(df['DATES'], dayfirst=True, errors='coerce')
    return df.dropna(subset=['DATES'])


def _join(grid_df, series_df, name):
    """Merge sobre la grilla diaria, interpola, y NaN antes del primer dato."""
    out = grid_df.merge(series_df, on='DATES', how='left')
    out = out.sort_values('DATES', ascending=False).reset_index(drop=True)
    first = series_df['DATES'].min()
    out[name] = _interp_na(out[name])
    out.loc[out['DATES'] < first, name] = np.nan
    return out


# ----------------------------- Bloque bursatil (STX) -------------------------
def get_STX(dd, lagTilde=LAG_TILDE, lagPeriod=LAG_PERIOD, lagWindow=LAG_WINDOW):
    n = len(dd)
    rSTX = (dd['STX'] / dd['CPI']).to_numpy()
    lnSTX = np.full(n, np.nan)
    lnSTX[:n - 1] = np.log(rSTX[:n - 1] / rSTX[1:n])         # retorno diario real
    sd = _roll_fwd(lnSTX, lagTilde, _sd)
    m = _first_na(lnSTX) - 1                                  # ultimo dato valido
    if m - lagTilde >= 0:                                     # relleno de borde
        sd[m - lagTilde:m + 1] = np.nanstd(lnSTX[m - lagTilde:m + 1], ddof=1)
    lnSTX_t = lnSTX / sd
    VSTX = _roll_fwd(lnSTX_t, lagPeriod, lambda a, axis: np.sum(np.abs(a), axis)) / lagPeriod
    mx = _roll_fwd(rSTX, lagWindow, np.max)
    mr = _first_na(rSTX) - 1
    if mr - lagWindow + 1 >= 0:
        mx[mr - lagWindow + 1:mr + 1] = np.nanmax(rSTX[mr - lagWindow + 1:mr + 1])
    CMAX = 1 - (rSTX / mx)
    dd['VSTX'] = VSTX; dd['CMAX'] = CMAX
    return dd


# ----------------------------- Tasa real de referencia (US) ------------------
def get_Rbs_daily(dd, lagYear=LAG_YEAR):
    n = len(dd); Rbs = dd['Rbs'].to_numpy(); CPIbs = dd['CPIbs'].to_numpy()
    rRbs = np.full(n, np.nan)
    rRbs[:n - lagYear] = Rbs[:n - lagYear] - \
        (CPIbs[:n - lagYear] / CPIbs[lagYear:n] - 1) * 100
    dd['rRbs'] = rRbs
    return dd


# ----------------------------- Bloque tasa (Ryr) -----------------------------
def get_Ryr_daily(dd, lagTilde=LAG_TILDE, lagPeriod=LAG_PERIOD,
                  lagWindow=LAG_WINDOW, lagYear=LAG_YEAR):
    n = len(dd); Ryr = dd['Ryr'].to_numpy(); CPI = dd['CPI'].to_numpy()
    rRyr = np.full(n, np.nan)
    rRyr[:n - lagYear] = Ryr[:n - lagYear] - \
        (CPI[:n - lagYear] / CPI[lagYear:n] - 1) * 100
    chRyr = np.full(n, np.nan)
    chRyr[:n - 1] = rRyr[:n - 1] - rRyr[1:n]
    sd = _roll_fwd(chRyr, lagTilde, _sd)
    m = _first_na(chRyr) - 1
    if m - lagTilde >= 0:
        sd[m - lagTilde:m + 1] = np.nanstd(chRyr[m - lagTilde:m + 1], ddof=1)
    chRyr_t = chRyr / sd
    VRyr = _roll_fwd(chRyr_t, lagPeriod, lambda a, axis: np.sum(np.abs(a), axis)) / lagPeriod
    chSpread = rRyr - dd['rRbs'].to_numpy()
    mn = _roll_fwd(chSpread, lagWindow, np.min)
    ms = _first_na(chSpread) - 1
    if ms - lagWindow + 1 >= 0:
        mn[ms - lagWindow + 1:ms + 1] = np.nanmin(chSpread[ms - lagWindow + 1:ms + 1])
    CDIFF = chSpread - mn
    dd['VRyr'] = VRyr; dd['CDIFF'] = CDIFF
    return dd


# ----------------------------- Colapso diario -> mensual ---------------------
def to_monthly_eom(dd):
    ym = dd['DATES'].dt.year * 100 + dd['DATES'].dt.month
    eom = np.zeros(len(dd), bool); eom[0] = True
    eom[1:] = ym.to_numpy()[:-1] != ym.to_numpy()[1:]        # cambio de mes (desc)
    out = dd.loc[eom, ['DATES', 'VSTX', 'CMAX', 'VRyr', 'CDIFF']].copy()
    out['YM'] = out['DATES'].dt.year * 100 + out['DATES'].dt.month
    return out


# ----------------------------- Bloque rEER (mensual) -------------------------
def get_rEER(md, lagTildeMonth=LAG_TILDE_M, lagMonth=LAG_MONTH,
             lagWindowMonth=LAG_WINDOW_M):
    md = md.sort_values('DATES', ascending=False).reset_index(drop=True)
    n = len(md); rEER = md['rEER'].to_numpy()
    lnEER = np.full(n, np.nan)
    lnEER[:n - lagMonth] = np.log(rEER[:n - lagMonth]) - np.log(rEER[lagMonth:n])
    sd = _roll_fwd(lnEER, lagTildeMonth + 1, _sd)
    m = _first_na(lnEER) - 1
    if m - lagTildeMonth + 1 >= 0:
        sd[m - lagTildeMonth + 1:m + 1] = np.nanstd(lnEER[m - lagTildeMonth + 1:m + 1], ddof=1)
    VEER = np.abs(lnEER / sd)
    CUMUL = np.full(n, np.nan)
    CUMUL[:n - lagWindowMonth] = np.abs(rEER[:n - lagWindowMonth] - rEER[lagWindowMonth:n])
    md['VEER'] = VEER; md['CUMUL'] = CUMUL
    return md


# ----------------------------- Estandarizacion -------------------------------
def method_b_max(values, timeFrame=TIME_FRAME):
    """Escalado por maximo expandible: x[k]/max(x[1..k]). Datos ASCENDENTES."""
    v = np.asarray(values, float); n = len(v)
    out = np.full(n, np.nan)
    out[:timeFrame] = v[:timeFrame] / np.nanmax(v[:timeFrame])
    for k in range(timeFrame, n):
        out[k] = v[k] / np.nanmax(v[:k + 1])
    return out


def method_a_cdf(values, timeFrame=TIME_FRAME):
    """CDF empirica inversa expandible (Duprey 2019). Datos ASCENDENTES."""
    v = np.asarray(values, float); n = len(v)
    out = np.full(n, np.nan)
    base = v[:timeFrame]
    out[:timeFrame] = np.array([(base <= x).mean() for x in base])
    for k in range(timeFrame, n):
        out[k] = (v[:k + 1] <= v[k]).mean()
    return out


# ----------------------------- Correlacion EWMA ------------------------------
def corr_EWMA(I1, I2, lam=LAMBDA, timeFrame=TIME_FRAME):
    I1 = np.asarray(I1, float); I2 = np.asarray(I2, float); n = len(I1)
    s12 = np.cov(I1[:timeFrame], I2[:timeFrame], ddof=1)[0, 1]
    s11 = np.var(I1[:timeFrame], ddof=1); s22 = np.var(I2[:timeFrame], ddof=1)
    out = [s12 / np.sqrt(s11 * s22)]
    for k in range(1, n):
        s12 = lam * s12 + (1 - lam) * (I1[k] - .5) * (I2[k] - .5)
        s11 = lam * s11 + (1 - lam) * (I1[k] - .5) ** 2
        s22 = lam * s22 + (1 - lam) * (I2[k] - .5) ** 2
        out.append(s12 / np.sqrt(s11 * s22))
    return np.array(out)


# ----------------------------- Agregacion FCI (forma cuadratica) -------------
def FCIS(iSTX, iRyr, iEER, cSR, cSE, cRE):
    n = len(iSTX); fci = np.empty(n)
    for k in range(n):
        C = np.array([[1, cSR[k], cSE[k]],
                      [cSR[k], 1, cRE[k]],
                      [cSE[k], cRE[k], 1]])
        I = np.array([iSTX[k], iRyr[k], iEER[k]])
        fci[k] = I @ C @ I
    return fci


# ----------------------------- Orquestador por pais --------------------------
def compute_fci(country_dir, country, ref_dir, ref_country='US',
                initial='1990-01-01', final='2026-06-30',
                std_method='method_b_max'):
    """Calcula la serie FCI mensual de un pais. country_dir/ref_dir son carpetas
    con los CSV (CPI/Ryr/STX/rEER y CPI/Ryr de referencia). Devuelve DataFrame
    con DATES (fin de mes) y FCI."""
    import glob, os
    def find(folder, prefix):
        f = glob.glob(os.path.join(folder, f'{prefix}*'))
        if not f:
            raise FileNotFoundError(f'Falta {prefix}* en {folder}')
        return f[0]

    grid = pd.DataFrame({'DATES': business_days(initial, final)})
    STX = _read_daily(find(country_dir, 'STX'), 'STX')
    Ryr = _read_daily(find(country_dir, 'Ryr'), 'Ryr')
    CPI = _read_daily(find(country_dir, 'CPI'), 'CPI')
    Rbs = _read_daily(find(ref_dir, 'Ryr'), 'Rbs')
    CPIbs = _read_daily(find(ref_dir, 'CPI'), 'CPIbs')

    dd = grid.copy()
    for s, nm in [(STX, 'STX'), (CPI, 'CPI'), (Ryr, 'Ryr'),
                  (Rbs, 'Rbs'), (CPIbs, 'CPIbs')]:
        dd = _join(dd, s, nm)
    dd = dd.sort_values('DATES', ascending=False).reset_index(drop=True)

    dd = get_STX(dd)
    dd = get_Rbs_daily(dd)
    dd = get_Ryr_daily(dd)
    md_daily = to_monthly_eom(dd)

    # rEER mensual
    rEER = pd.read_csv(find(country_dir, 'rEER'))
    rEER.columns = ['YM', 'rEER']
    rEER['DATES'] = pd.to_datetime(rEER['YM'].astype(int).astype(str),
                                   format='%Y%m') + pd.offsets.MonthEnd(0)
    mgrid = pd.DataFrame({'DATES': pd.date_range(initial, final, freq='ME')})
    md = mgrid.merge(rEER[['DATES', 'rEER']], on='DATES', how='left')
    md = md.sort_values('DATES', ascending=False).reset_index(drop=True)
    md['rEER'] = _interp_na(md['rEER'])
    md.loc[md['DATES'] < rEER['DATES'].min(), 'rEER'] = np.nan
    md = get_rEER(md)
    md['YM'] = md['DATES'].dt.year * 100 + md['DATES'].dt.month

    # union mensual por YM
    idx = md_daily.merge(md[['YM', 'VEER', 'CUMUL']], on='YM', how='left')
    idx = idx.sort_values('DATES', ascending=False).reset_index(drop=True)
    # R (get_min_index, fci_wrapper.R) NO hace dropna global: trunca en la
    # primera fila (desde la mas reciente) que tenga algun NA y descarta todo
    # lo que sigue (mas antiguo). Un dropna fila-a-fila empalmaria meses no
    # contiguos si hay huecos internos, rompiendo la adyacencia que usan los
    # rolling/EWMA. Replicamos el truncamiento exacto de R:
    req_cols = ['VSTX', 'CMAX', 'VRyr', 'CDIFF', 'VEER', 'CUMUL']
    na_pos = np.where(idx[req_cols].isna().any(axis=1).to_numpy())[0]
    if len(na_pos):
        idx = idx.iloc[:na_pos[0]]
    idx = idx.sort_values('DATES').reset_index(drop=True)   # ASCENDENTE

    std = method_b_max if std_method == 'method_b_max' else method_a_cdf
    for col in ['VSTX', 'CMAX', 'VRyr', 'CDIFF', 'VEER', 'CUMUL']:
        idx[col] = std(idx[col].to_numpy())

    idx['iSTX'] = (idx['VSTX'] + idx['CMAX']) / 2
    idx['iRyr'] = (idx['VRyr'] + idx['CDIFF']) / 2
    idx['iEER'] = (idx['VEER'] + idx['CUMUL']) / 2

    cSR = corr_EWMA(idx['iSTX'], idx['iRyr'])
    cSE = corr_EWMA(idx['iSTX'], idx['iEER'])
    cRE = corr_EWMA(idx['iRyr'], idx['iEER'])

    idx['FCI'] = FCIS(idx['iSTX'].to_numpy(), idx['iRyr'].to_numpy(),
                      idx['iEER'].to_numpy(), cSR, cSE, cRE)
    idx['country'] = country
    return idx[['DATES', 'country', 'iSTX', 'iRyr', 'iEER', 'FCI']]


if __name__ == '__main__':
    import sys
    df = compute_fci(sys.argv[1], sys.argv[2], sys.argv[3])
    print(df.tail(12).to_string(index=False))
