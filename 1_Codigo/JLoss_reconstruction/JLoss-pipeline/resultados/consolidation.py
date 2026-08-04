import pandas as pd, glob
bal = pd.concat([pd.read_csv(f) for f in glob.glob('balance_*.csv')], ignore_index=True)
mkt = pd.concat([pd.read_csv(f) for f in glob.glob('mktcap_*.csv')],  ignore_index=True)
bal['date'] = pd.to_datetime(bal['date']); mkt['date'] = pd.to_datetime(mkt['date'])
bal.to_csv('balance_all.csv', index=False); mkt.to_csv('mktcap_all.csv', index=False)
print('consolidado:', bal['countryname'].nunique(), 'paises,', len(bal), 'filas de balance')