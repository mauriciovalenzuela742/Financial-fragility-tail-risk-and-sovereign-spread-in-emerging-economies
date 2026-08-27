# Estado de la sesión — extracción Bloomberg para panel JLoss/GaR (Fase 1)

Última actualización: 2026-08-27. Este archivo es para retomar el trabajo otro día sin
tener que re-explicar todo desde cero.

## Qué es esto

Fase 1 del plan aprobado (ver `C:\Users\itau_lab\.claude\plans\perfecto-necesito-extraer-los-calm-hamster.md`):
construir, 100% desde cero vía Bloomberg Terminal (xbbg), los inputs JLoss (riesgo bancario,
Merton-KMV) y las variables macro/regresión de GaR para los **12 países "extractor listo,
sin datos"**: Argentina, China, Egipto, Indonesia, Malasia, Pakistán, Filipinas, Polonia,
Rusia, Sudáfrica, Turquía, Bulgaria.

Repo de la tesis (destino final del código): `https://github.com/mauriciovalenzuela742/Financial-fragility-tail-risk-and-sovereign-spread-in-emerging-economies`
Por instrucción explícita del usuario, se ignora el pipeline JLoss ya subido a ese repo
(carpetas `extract_<pais>.py` existentes) — solo se reutilizó el **schema/cabecera** de
`jloss_common.py` y el formato de CSV `DATES,<var>` de
`1_Codigo/GaR/extraction_individuals/*.py`.

## ESTADO: extracción EJECUTADA y verificada contra el Terminal real (2026-08-27)

Ya no es código "sin testear". Los dos scripts corrieron completos contra el Bloomberg
Terminal de esta máquina y escribieron datos.

### Salida JLoss — `bloomberg_extraction/output/<pais>/`

62 bancos, 3.912 filas de balance, 247.051 filas de mktcap, 2010→2026, **cero alertas de
coherencia contable** (sin equity > activos, sin pasivos negativos, sin mktcap ≤ 0).

| País | Bancos | balance | mktcap | Nota |
|---|---:|---:|---:|---|
| poland | 8 | 528 | 32.560 | |
| turkey | 8 | 536 | 33.432 | |
| china | 10 | 645 | 38.221 | |
| southafrica | 6 | 197 | 24.966 | **frecuencia semestral** |
| malaysia | 6 | 402 | 24.496 | |
| pakistan | 6 | 402 | 24.762 | |
| indonesia | 5 | 335 | 18.141 | |
| philippines | 5 | 335 | 20.310 | |
| argentina | 4 | 264 | 14.681 | |
| russia | 2 | 134 | 7.354 | **mktcap corta 2024-08-09** |
| bulgaria | 1 | 67 | 4.111 | below_min_banks 67/67 |
| egypt | 1 | 67 | 4.017 | below_min_banks 67/67 |

### Salida macro/GaR — `bloomberg_extraction/output_macro/`

- `GLOBAL/`: VIX (4.220), UST10Y (4.342), HY_SPREAD (4.196).
- por país: `EMBI_<pais>.csv` (CDS 5Y), `rating_<pais>.csv`, `fxvol_<pais>.csv` (67
  trimestres en todos salvo Rusia, 49), `prof_margin_<pais>.csv` (67 trimestres).
- Rating S&P resuelto para los 12 países (Rusia = `NR`, sin puntaje, correcto).

## Lo que hubo que arreglar para que esto corriera (todo verificado, no adivinado)

### xbbg 1.0 rompió la API de 0.7
El entorno tiene **xbbg 1.0.0**, que es una reescritura: devuelve un frame *largo* de
narwhals sobre pyarrow (`ticker, date, field, value`, todo string) en vez de un DataFrame
pandas ancho, y el kwarg `Per=` ya no existe (`BlpValidationError`). Se agregó una capa de
adaptación en `bloomberg_common.py` (`_XBBG_CALL`, `_to_wide`, `_PERIODICITY`) que pide
`backend="pandas"`, `format="long_typed"` y re-arma el formato ancho, de modo que el resto
del pipeline sigue viendo el contrato de siempre.
**Si esto se vuelve a romper, el sospechoso #1 es una actualización de xbbg.**

### Mnemónicos Bloomberg que estaban mal
| Estaba | Es | Efecto del error |
|---|---|---|
| `LT_DEBT` | `BS_LT_BORROW` | no es mnemónico válido; `bonds` (y toda la regla LP/CP) venía vacío |
| `RTG_SP_LT_FC_ISSUER_RATING` | `RTG_SP_LT_FC_ISSUER_CREDIT` | rating vacío en los 12 países |
| `BEBGHYCS Index` | `LF98OAS Index` | BAD_SEC; es el equivalente del FRED BAMLH0A0HYM2 del repo |

### Tickers de bancos desactualizados (`MARKET_STATUS = TKCH`)
| Era | Es | Efecto |
|---|---|---|
| `SPL PW` (Santander Polska) | `EBP PW` | **0 obs de mktcap**: el banco desaparecía del panel |
| `CHIB PM` (China Banking) | `CBC PM` | 0 obs de mktcap |
| `5F4 BU` (Fibank) | `FIB BU` | 5F4 daba mktcap en **BGN** contra balance en **EUR** → inflado ×1,95583 |

El CDS soberano de China no resuelve por nombre de emisor (`CHINA CDS USD SR 5Y Corp` →
BAD_SEC); sí por ticker Markit `CCHIN1U5 Curncy`. Está en `CDS_TICKER_OVERRIDE`.

### Frecuencia de reporte
Los 6 bancos sudafricanos reportan **semestralmente**: cualquier pedido trimestral vuelve
con las fechas pero sin datos. `_pull_fundamentals` ahora intenta trimestral y cae a
semestral por ticker. No se puede hardcodear por país: para GGAL (Argentina) el pedido
semestral devuelve 0. Además se cambió `periodicityAdjustment` de `CALENDAR` a `ACTUAL`
para fundamentales, lo que mejora cobertura (`BS_LT_BORROW` de BDO Unibank: 29 → 46).

### Dato corrupto puntual
`BS_TOT_ASSET = 0.0` para United Bank (Pakistán) en 2025-02-27, con equity de 275.289 en
la misma fila. Propagaba `total_liab` y `st_borrow` negativos. `finalize_balance` ahora lo
marca NaN. **`bonds == 0` sí es legítimo** (174 filas, banco sin deuda LP emitida) y no se toca.

## Limitaciones de los datos — decisiones metodológicas PENDIENTES del usuario

Ninguna de estas es un bug arreglable con mejor código. Hay que decidirlas:

1. **Sudáfrica queda en frecuencia semestral** mientras el resto del panel es trimestral.
   El motor JLoss agrupa por trimestre → la mitad de los trimestres quedarán vacíos.
   ¿Interpolar, arrastrar el último valor, o dejar el país en semestral?
2. **Rusia: la serie de mercado termina el 2024-08-09.** `MARKET_STATUS = PRNA` para SBER
   y VTBR — Bloomberg dejó de precificarlos por sanciones. Los fundamentales siguen, pero
   sin valor de mercado no hay Merton-KMV. ¿Panel truncado o país fuera?
3. **Rating S&P es un SNAPSHOT, no una serie.** `RTG_SP_LT_FC_ISSUER_CREDIT` vía `bdh`
   devuelve vacío en cualquier frecuencia. O sea: un solo rating para los 16 años del
   panel. Es débil justo para Turquía, Argentina y Rusia, que fueron degradadas varias
   veces en 2010-2026. Si la tesis lo necesita variando en el tiempo hay que traerlo de
   otra fuente (S&P directo, o `CRD<GO>` a mano).
4. **CDS 5Y sin cobertura utilizable en 5 países** (el security resuelve, no hay precios):
   - Polonia, Bulgaria, Rusia: solo 2012-07-13..2015-10-16
   - Pakistán: solo desde 2026-03-18
   - Egipto: 468 obs dispersas en 2010-2026
   Para Polonia sí existe `GTPLN10Y Govt`, así que un spread de bono soberano contra
   Bund/UST es la alternativa natural. Es decisión de la tesis.
5. **Bulgaria y Egipto tienen 1 solo banco cotizado; Rusia, 2.** `below_min_banks` marcará
   todos los trimestres. Es estructural del universo, no de los tickers.

## Entorno de ejecución

El proyecto PyCharm (`PythonProject`) tiene un `.venv` vacío. **El entorno correcto es
`bloomberg_env`** (conda), en `C:\Users\itau_lab\.conda\envs\bloomberg_env`, con
blpapi 3.26.2.1, xbbg 1.0.0, pandas 3.0.2. `conda` NO está en el PATH: usar
`C:\ProgramData\anaconda3\Scripts\conda.exe` o el intérprete directo
`C:\Users\itau_lab\.conda\envs\bloomberg_env\python.exe`.

Ojo: xbbg está instalado en el site-packages **de usuario**
(`C:\Users\itau_lab\AppData\Roaming\Python\Python313\site-packages`), no dentro del env.

```
cd bloomberg_extraction
python extract_jloss_bloomberg.py              # los 12 paises
python extract_jloss_bloomberg.py --country poland
python gar_macro_bloomberg.py                  # macro + global
```

## Pendiente al retomar

1. Decidir los 5 puntos metodológicos de arriba.
2. **Push**: hay commits locales listos en
   `C:\Users\itau_lab\PycharmProjects\Financial-fragility-tail-risk-and-sovereign-spread-in-emerging-economies`
   sin subir. `origin/main` sigue en `8576537`. Falta `git push` desde PyCharm — no hay
   credenciales de GitHub configuradas en este entorno.
3. Enchufar estos CSV al motor JLoss y al pipeline GaR aguas abajo (Fase 2).

## Preguntas ya resueltas (no volver a preguntar)

- Alcance: Fase 1 = los 12 países pendientes + variables macro/globales. Hungría/India/
  Tailandia y la decisión de "PD contable" quedan fuera, para una Fase 2 posterior.
- El JLoss ya subido al repo se ignora — todo se reconstruye desde cero vía Bloomberg,
  solo se reutiliza el schema/cabecera.
- Destino GitHub: repo de la tesis, no uno nuevo.
- Autenticación: Claude no pushea, prepara el commit y el usuario pushea desde PyCharm.
