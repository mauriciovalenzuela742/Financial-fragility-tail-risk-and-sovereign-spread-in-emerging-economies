"""convergencia_motor.py -- respalda las cifras de la Sección de JLoss: convergencia del solver de Merton
con los datos de Bloomberg y bancos usados. Requiere los datos restringidos de Bloomberg_extraction/output.
Correr desde 1_Codigo: python JLoss_reconstruction/convergencia_motor.py
"""
import glob, os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, 'JLoss_reconstruction')
import jloss_engine as E
OUT = 'Bloomberg_extraction/output'
P = pd.read_csv('Panel/bbg/Panel_bloomberg_embiext.csv')
P['q'] = pd.PeriodIndex(P['quarter'], freq='Q')
P = P.sort_values(['country', 'q'])
g = P.groupby('country')
P['ok'] = P['EMBI_bps'].notna() & g['JLoss'].shift(1).notna() & g['GaR'].shift(1).notna() & (g['q'].shift(1) == P['q'] - 1)
excl = {'argentina'}
M = P[P['ok'] & ~P['country'].isin(excl)]
print('muestra', len(M), M['country'].nunique(), M['q'].min(), M['q'].max())
P['bm_lag'] = g['below_min_banks'].shift(1)
P['nb_lag'] = g['n_banks'].shift(1)
M = P[P['ok'] & ~P['country'].isin(excl)]
print('obs con <3 bancos en t-1:', int((M['nb_lag'] < 3).sum()), 'por pais', M[M['nb_lag'] < 3].groupby('country').size().to_dict())
print('bancos por trimestre en t-1: mediana por pais', M.groupby('country')['nb_lag'].median().to_dict())
paises = sorted(M['country'].unique())
filas = []
bancos = {}
for c in sorted(os.listdir(OUT)):
    fb, fm = f'{OUT}/{c}/balance_{c}.csv', f'{OUT}/{c}/mktcap_{c}.csv'
    if not (os.path.exists(fb) and os.path.exists(fm)):
        continue
    dm = E.quarterly_inputs(pd.read_csv(fb), pd.read_csv(fm))
    det = dm.apply(lambda r: E.merton_pd(r['mktcap_end'], r['sigma_E_q'], r['D_star'], return_detail=True), axis=1)
    dm['PD'] = [d[0] for d in det]
    cand = dm[dm['sigma_E_q'].notna() & dm['D_star'].notna() & (dm['D_star'] > 0) & (dm['mktcap_end'] > 0)]
    usados = dm[dm['PD'].notna() & dm['total_liab'].notna() & (dm['total_liab'] > 0)]
    bancos[c] = usados['bankname'].nunique()
    filas.append((c, len(dm), len(cand), int(cand['PD'].notna().sum()), usados['bankname'].nunique()))
T = pd.DataFrame(filas, columns=['pais', 'celdas', 'candidatas', 'pd_ok', 'bancos'])
T['conv'] = (T.pd_ok / T.candidatas).round(3)
print(T.to_string(index=False))
print('TOTAL conv', round(T.pd_ok.sum() / T.candidatas.sum(), 4), 'bancos', T.bancos.sum(), 'celdas', T.candidatas.sum())
S = T[T.pais.isin(paises)]
print('13 economias conv', round(S.pd_ok.sum() / S.candidatas.sum(), 4), 'bancos', S.bancos.sum(), 'candidatas', S.candidatas.sum())
print('min conv', S.sort_values('conv').head(3)[['pais', 'conv']].to_dict('records'))
