"""
phase2_gar_panel.py — Construccion de la SERIE GaR_{i,t} en ventana expansiva.

Envuelve gar_engine.estimate_at sobre cada fecha de corte trimestral del panel.
En cada corte t se re-estiman los coeficientes cuantilicos SOLO con datos hasta t
(pseudo real-time, sin look-ahead) y se extrae la distribucion condicional de
cada pais en t. Salida estandarizada: gar_panel_<tag>.csv (formato largo), lista
para hacer merge por (country, quarter) con Panel_JLoss_v7.csv.

Uso:
    python phase2_gar_panel.py
"""
import time
import numpy as np
import pandas as pd
from gar_engine import estimate_at, preprocess

# --- Configuracion (alineada con la metodologia CEMLA / config del test) -------
SOURCE_FILE = 'GaR_panel.xlsx'
SHEET = 'Panel'
DEPENDENT = 'g_GDP'
INDEPENDENT = ('g_GDP', 'VIX')      # FCI entra ortogonalizado
ORTH_DEP, ORTH_IND = ('FCI',), ('VIX',)
H = 1                                # horizonte (trimestres, lead de g_GDP)
N_TAU = 39                            # rejilla fina: tau incluye 0.025 y 0.05
PROBABILITY = 0.05                   # nivel GaR / ES
MIN_TRAIN_OBS = 40                   # tamano minimo de muestra de estimacion
OUT_TAG = 'latam'
# ------------------------------------------------------------------------------


def quarterly_dates(panel):
    d = pd.to_datetime(panel['Date'], format='%d/%m/%Y')
    return [ts.strftime('%d/%m/%Y') for ts in sorted(d.unique())]


def feasible(panel, selected_date):
    """Tamano de la muestra de estimacion en el corte (todas las vars notna)."""
    est_all, orth_vars = preprocess(panel, selected_date, DEPENDENT,
                                    list(INDEPENDENT), list(ORTH_DEP),
                                    list(ORTH_IND), H)
    cols = ['future_dep_var'] + list(INDEPENDENT) + orth_vars
    return int(est_all[cols].notna().all(axis=1).sum())


def build_series(panel, verbose=True, checkpoint=None):
    dates = quarterly_dates(panel)
    done = set()
    if checkpoint:
        import os
        if os.path.exists(checkpoint):
            done = set(pd.read_csv(checkpoint)['date'].unique())
    rows = []
    t0 = time.time()
    for k, sd in enumerate(dates):
        if sd in done:
            continue
        n = feasible(panel, sd)
        if n < MIN_TRAIN_OBS:
            continue
        try:
            df = estimate_at(panel, sd, DEPENDENT, INDEPENDENT,
                             ORTH_DEP, ORTH_IND, H, N_TAU, PROBABILITY,
                             method='both')
        except Exception as e:
            if verbose:
                print(f'  [skip {sd}] {type(e).__name__}: {e}', flush=True)
            continue
        df['n_train'] = n
        rows.append(df)
        if checkpoint:                       # persistencia incremental
            import os
            df.to_csv(checkpoint, mode='a', header=not os.path.exists(checkpoint),
                      index=False)
        if verbose:
            print(f'  {sd}  n_train={n:4d}  paises_con_GaR={df["GaR"].notna().sum()}'
                  f'  ({k+1}/{len(dates)})  [{time.time()-t0:5.1f}s]', flush=True)
    if checkpoint and not rows:
        return pd.read_csv(checkpoint)
    out = pd.concat(([pd.read_csv(checkpoint)] if checkpoint and done else []) + rows,
                    ignore_index=True)
    return out
    # quarter en formato YYYYQq para el merge
    dd = pd.to_datetime(out['date'], format='%d/%m/%Y')
    out['quarter'] = dd.dt.year.astype(str) + 'Q' + dd.dt.quarter.astype(str)
    out['country'] = out['country'].str.title()   # 'BRAZIL' -> 'Brazil'
    cols = ['country', 'quarter', 'date', 'GaR', 'GaR_st', 'prob_neg', 'ES',
            'mean', 'std', 'iqr_05_95', 'scale_st', 'skew', 'skew_st', 'nu_st',
            'n_train']
    return out[cols].sort_values(['country', 'date']).reset_index(drop=True)


if __name__ == '__main__':
    panel = pd.read_excel(SOURCE_FILE, sheet_name=SHEET)
    print('Construyendo serie GaR en ventana expansiva...', flush=True)
    ckpt = f'_ckpt_{OUT_TAG}.csv'
    series = build_series(panel, checkpoint=ckpt)
    # post-proceso: quarter + title-case + columnas finales
    dd = pd.to_datetime(series['date'], format='%d/%m/%Y')
    series['quarter'] = dd.dt.year.astype(str) + 'Q' + dd.dt.quarter.astype(str)
    series['country'] = series['country'].str.title()
    cols = ['country', 'quarter', 'date', 'GaR', 'GaR_st', 'prob_neg', 'ES',
            'mean', 'std', 'iqr_05_95', 'scale_st', 'skew', 'skew_st', 'nu_st',
            'n_train']
    series = series[cols].sort_values(['country', 'date']).reset_index(drop=True)
    out_path = f'gar_panel_{OUT_TAG}.csv'
    series.to_csv(out_path, index=False)
    print(f'\nGuardado: {out_path}  ({len(series)} filas, '
          f'{series["country"].nunique()} paises, '
          f'{series["quarter"].nunique()} trimestres)', flush=True)
