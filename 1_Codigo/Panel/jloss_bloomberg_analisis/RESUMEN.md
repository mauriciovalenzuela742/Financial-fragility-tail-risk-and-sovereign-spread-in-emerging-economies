# JLoss Bloomberg -> panel de regresiones y analisis principal

Generado re-ejecutando `analisis_jloss_bloomberg.py`. JLoss nuevo: `Panel_JLoss_v9_bloomberg.csv` (motor v8, rho=0.4, PD Merton/KMV).

## 1. theta = JLoss x GaR sobre EMBI

| base | spec | fuente JLoss | N | theta | t | p |
|---|---|---|---:|---:|---:|---:|
| all17 (5 LatAm) | M2 (FE pais+tiempo) | JLoss v8/dta | 281 | -0.3592 | -2.82 | 0.005 |
| all17 (5 LatAm) | M2 (FE pais+tiempo) | JLoss Bloomberg | 281 | -0.8260 | -2.04 | 0.042 |
| all17 (5 LatAm) | M3 (+controles dom.) | JLoss v8/dta | 253 | -0.3378 | -2.22 | 0.028 |
| all17 (5 LatAm) | M3 (+controles dom.) | JLoss Bloomberg | 253 | -0.8544 | -2.21 | 0.028 |
| extendido (11) | M2 (FE pais+tiempo) | JLoss v8/dta | 374 | -0.2122 | -1.83 | 0.069 |
| extendido (11) | M2 (FE pais+tiempo) | JLoss Bloomberg | 374 | -0.6648 | -1.89 | 0.060 |

## 2. H4a (b3>0) / H4b (b4>0)

| base | HHI | fuente JLoss | N | b3 | t3 | b4 | t4 |
|---|---|---|---:|---:|---:|---:|---:|
| final17 | estructural | v8/dta | 281 | +54.11 | +1.63 | -363.0 | -0.47 |
| final17 | estructural | Bloomberg | 281 | +65.95 | +2.47 | -247.8 | -0.55 |
| final17 | estructural | Bloomberg (>=3 bancos) | 270 | +95.06 | +2.69 | -370.3 | -0.97 |
| final17 | anual | v8/dta | 252 | +30.85 | +1.21 | +437.4 | +2.08 |
| final17 | anual | Bloomberg | 252 | +98.26 | +2.21 | +245.9 | +0.88 |
| final17 | anual | Bloomberg (>=3 bancos) | 246 | +100.15 | +2.15 | +178.9 | +0.42 |
| ext11 | estructural | v8/dta | 374 | -16.98 | -0.68 | +720.7 | +2.98 |
| ext11 | estructural | Bloomberg | 374 | +37.37 | +1.32 | +68.1 | +0.20 |
| ext11 | estructural | Bloomberg (>=3 bancos) | 355 | +62.83 | +1.31 | -15.8 | -0.04 |
| ext11 | anual | v8/dta | 345 | +4.36 | +0.18 | +383.4 | +4.47 |
| ext11 | anual | Bloomberg | 345 | +86.10 | +2.11 | +200.8 | +0.85 |
| ext11 | anual | Bloomberg (>=3 bancos) | 331 | +93.24 | +1.90 | +92.4 | +0.27 |

## 0. Concordancia JLoss v8/dta vs Bloomberg

| base | n | corr | corr within-pais | sd v8 | sd bbg |
|---|---:|---:|---:|---:|---:|
| all17 | 293 | 0.554 | 0.507 | 8.26 | 2.58 |
| extendido | 395 | 0.215 | 0.579 | 7.26 | 5.04 |

## Referencia (NUMEROS_CANONICOS.md, JLoss v8)
- theta M3 all17 = -0.338 (N=253, t=-2.22, p=0.028)
- theta M2 extendido = -0.212 (N=374, t=-1.83, p=0.069)
- b4 ext11 (HHI estructural) = +721 (t=2.98)
