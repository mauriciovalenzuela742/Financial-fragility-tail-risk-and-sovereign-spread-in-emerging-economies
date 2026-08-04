# Runbook — obtener los resultados JLoss actualizados

Secuencia ejecutable de principio a fin. Corre en **su entorno con red abierta** (no en el
sandbox de Claude). Combina PD de mercado (listados) + PD contable calibrada (no listados) y
produce **dos series** de JLoss por la configuración doble de ρ (0.4 plano y ρ estimado).

Archivos que ya tiene: `JLoss_reconstruction_v8.ipynb`, `jloss_common.py`, `book_pd.py`,
`extract_chile.py`, `extract_brazil.py`, `extract_colombia.py`, `extract_peru.py`,
`extract_mexico.py`, `Panel_JLoss_v8.csv`.

---

## PASO 0 — Entorno
```bash
python -m venv venv && source venv/bin/activate
pip install pandas numpy scipy matplotlib seaborn requests openpyxl "xlrd>=2.0.1" yfinance
```
Registrar la API key gratuita de CMF (Chile) en api.cmfchile.cl → `export CMF_API_KEY=...`.

## PASO 1 — Fijar mapeos de cuentas (incluye net_income) y pregunta al profesor
1. **Pregunta al profesor (mañana):** cómo tratar la clasificación CMF de obligaciones por
   *instrumento* vs *madurez*. Con su respuesta se ajusta el `ACCOUNT_MAP` de Chile y, con el
   mismo criterio, el de los 4 países LatAm.
2. Correr los `--discover` para confirmar códigos/nombres reales:
   ```bash
   python extract_chile.py    --discover        # cuentas CMF (balance)
   python extract_brazil.py   --discover        # ListaDeRelatorio (Olinda)
   python extract_colombia.py --discover        # resource id del dataset Socrata
   ```
3. **Importante para el PD contable:** extender cada `ACCOUNT_MAP`/`CONCEPT_MAP`/`ROW_MAP` para
   capturar también **net_income** (del estado de resultados: CMF `er_institucion`, BCB relatorio
   de resultados, SFC/CNBV cuenta de resultado). El z-score lo necesita. Sin net_income, esos
   bancos no tendrán PD contable.

## PASO 2 — Extraer por país
```bash
python extract_chile.py    --start 1999 --end 2026
python extract_brazil.py   --start 2000 --end 2026
python extract_colombia.py --dataset <ID> --start 2000 --end 2026
# Perú/México: primero DESCARGAR los archivos (SBS .xls / export CNBV), luego:
python extract_peru.py   --dir ./sbs_xlsx     --start 2001 --end 2026
python extract_mexico.py --file ./cnbv.csv    --start 2000 --end 2026
```
Cada uno deja `balance_<país>.csv`, `mktcap_<país>.csv`, `coverage_<país>.csv`.

## PASO 3 — Consolidar al esquema v8
```python
import pandas as pd, glob
bal = pd.concat([pd.read_csv(f) for f in glob.glob('balance_*.csv')], ignore_index=True)
mkt = pd.concat([pd.read_csv(f) for f in glob.glob('mktcap_*.csv')],  ignore_index=True)
bal['date'] = pd.to_datetime(bal['date']); mkt['date'] = pd.to_datetime(mkt['date'])
# (opcional) anexar al histórico del proveedor para los periodos previos no recalculados
```

## PASO 4 — PD de mercado (bancos listados)
Usar la calibración del notebook v8 (`calc_merton_pd`: solver normalizado x₀=[1,1], DD lineal
KMV, σ_E·√4). Construir, por banco-trimestre listado, `sigma_E_q`, `mktcap_end`, `D_star=ST+0.5·LT`
desde `bal`+`mkt` (igual que la Parte B del v8) y:
```python
dm_listed['PD'] = dm_listed.apply(
    lambda r: calc_merton_pd(r['mktcap_end'], r['sigma_E_q'], r['D_star']), axis=1)
market_pd = dm_listed[['countryname','bankname','quarter','PD']]  # quarter->date al final
```

## PASO 5 — PD contable calibrada (bancos no listados)
```python
import book_pd as bp
book = bp.compute_book_pd(bal, window=8, min_obs=6,
                          net_income_is_ytd=True)   # True si el regulador publica YTD
# Puente de escala: usar los LISTADOS (tienen z contable Y EDF de mercado) para calibrar
listed = book.merge(market_pd, on=['countryname','bankname','date'], suffixes=('','_mkt'))
ab = bp.calibrate_book_to_market(listed['zscore'], listed['PD_mkt'])
book = bp.apply_book_calibration(book, ab)          # -> columna PD_cal (escala de mercado)
```
Si `ab is None` (pocos listados), `apply_book_calibration` cae a la cota de Chebyshev
(`1/(2z²)`), que nunca hace underflow. **Recomendado:** winsorizar `zscore` al p95 de los
listados antes de calibrar para evitar extrapolar a PD absurdamente bajas.

## PASO 6 — Combinar PDs (mercado prioriza; contable rellena no listados)
```python
combined = bp.merge_pds(market_pd, book, book_pd_col='PD_cal')
# combined: countryname, bankname, date, PD, pd_source
```
`pd_source` documenta el método por observación (requisito para el comité).

## PASO 7 — Motor JLoss con ρ doble
Unir `combined` con los pasivos (`liabilities = ST+LT`) por banco-trimestre y, por país-trimestre,
correr `compute_jloss` (del notebook v8, sin cambios) dos veces:
```python
import numpy as np
def jloss_panel(df_pd_liab, rho_mode):           # df: countryname,bankname,quarter,PD,total_liab
    rows=[]
    for (c,q), g in df_pd_liab.groupby(['countryname','quarter']):
        g=g[g['PD'].notna() & (g['total_liab']>0)]
        if len(g)<1: continue
        if rho_mode=='flat':
            rho=np.full(len(g),0.4)
        else:                                     # 'estimated': factor común sobre retornos de activos
            rho=estimate_rho(g)                   # ver PASO 7b
        jl=compute_jloss(g['PD'].values, rho, g['total_liab'].values)
        if np.isfinite(jl): rows.append({'countryname':c,'quarter':str(q),'JLoss':jl})
    return pd.DataFrame(rows)

jloss_flat = jloss_panel(panel_pd_liab, 'flat')        # serie comparable con el histórico
jloss_est  = jloss_panel(panel_pd_liab, 'estimated')   # serie mejorada
```

### PASO 7b — ρ estimado (factor común)
Para cada país: tomar los log-retornos de activos (de la calibración KMV de los listados; para no
listados, proxy con retornos de ROA), extraer el **primer componente principal** como factor
sistémico y fijar ρ_i = carga estandarizada del banco i sobre ese factor (clip a [0, 0.99]).
Contrastar con la correlación IRB de Basilea como referencia. Bancos sin retornos → ρ=0.4.

## PASO 8 — Ensamblar panel actualizado + QA + gráfico
```python
jloss_flat['rho']='flat'; jloss_est['rho']='estimated'
panel = pd.concat([jloss_flat, jloss_est], ignore_index=True)
panel['date']=pd.PeriodIndex(panel['quarter'],freq='Q').to_timestamp()
panel.to_csv('Panel_JLoss_v9.csv', index=False)
# QA: revisar coverage_*.csv (fracción de activos del sistema por trimestre) antes de interpretar
```
Reusar la celda de visualización del v8 (facetas por país), separando las dos series de ρ.

## PASO 9 — Robustez (para defender la mezcla de métodos)
1. **Solo-listados vs panel completo:** correr JLoss con `pd_source=='market_merton'` únicamente y
   comparar con el panel completo; cuantificar cuánto mueve la inclusión de no listados.
2. **ρ=0.4 vs ρ estimado:** la diferencia entre `jloss_flat` y `jloss_est` es la sensibilidad a la
   correlación.
3. **PD contable cruda vs calibrada vs Chebyshev:** reportar las tres para mostrar que los
   resultados no dependen del mapeo de escala elegido.
4. **Cobertura mínima:** fijar un umbral (p.ej. ≥60% de activos del sistema) por país-trimestre y
   marcar las observaciones que no lo cumplen.

---

### Notas de consistencia (para el comité)
- Mezclar PD de mercado y PD contable introduce heterogeneidad de método; mitigada por la
  calibración del PASO 5 y documentada por `pd_source`. La robustez del PASO 9 es la defensa.
- La serie `flat` (ρ=0.4, solo-mercado donde exista histórico) es la **comparable** con la
  reconstrucción v8; la serie `estimated` con PD combinada es la **métrica mejorada**.
- Mantener una sola unidad monetaria por país-trimestre (E y D en la misma escala). El JLoss final
  es un ratio (×100/ΣEAD), invariante a escala dentro de cada país-trimestre.
