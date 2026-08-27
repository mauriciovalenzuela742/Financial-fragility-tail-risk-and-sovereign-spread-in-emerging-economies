# Estado de la sesión — extracción Bloomberg para el panel JLoss/GaR (20 países, 2004→2026)

Última actualización: 2026-08-27. Este archivo es para retomar el trabajo otro día sin
tener que re-explicar todo desde cero.

## Qué es esto

Construcción, 100% desde cero vía Bloomberg Terminal (xbbg), de los inputs JLoss (riesgo
bancario, Merton-KMV) y las variables macro/regresión de GaR, para la tesis "Financial
fragility, tail risk and sovereign spread in emerging economies".

Repo de la tesis: `https://github.com/mauriciovalenzuela742/Financial-fragility-tail-risk-and-sovereign-spread-in-emerging-economies`
El código y los datos viven en `1_Codigo/Bloomberg_extraction/`.

Se reutilizó solo el **schema/cabecera** de `jloss_common.py` (columnas
`BALANCE_COLS`/`MKTCAP_COLS`, regla LP/CP bonos-vs-resto) y el formato `DATES,<var>` de
`1_Codigo/GaR/extraction_individuals/*.py`. Las claves de `bankname` son las mismas que usa
`JLoss-pipeline/extraccion/<pais>/`, para que estos CSV empaten con el panel existente.

## ESTADO: extracción EJECUTADA y verificada contra el Terminal real

**20 países, 113 bancos, 8.611 filas de balance, 564.470 de mktcap, 2004→2026, cero alertas
de coherencia contable** (sin equity > activos, sin pasivos negativos, sin mktcap ≤ 0).
91 trimestres de panel.

| País | Grupo | Bancos | balance | mktcap | Nota |
|---|---|---:|---:|---:|---|
| india | Fase 2 | 13 | 802 | 72.739 | **sin CDS soberano** |
| brazil | LatAm | 11 | 855 | 48.009 | |
| china | Fase 1 | 10 | 735 | 43.543 | mktcap desde 2005-06 (H-shares) |
| southkorea | Fase 2 | 9 | 538 | 35.573 | **balance solo desde 2009** |
| poland | Fase 1 | 8 | 696 | 42.906 | CDS inutilizable |
| turkey | Fase 1 | 8 | 710 | 44.190 | |
| malaysia | Fase 1 | 6 | 546 | 33.394 | |
| pakistan | Fase 1 | 6 | 487 | 31.850 | CDS sin historia |
| southafrica | Fase 1 | 6 | 268 | 33.972 | **frecuencia semestral** |
| indonesia | Fase 1 | 5 | 434 | 23.961 | |
| mexico | LatAm | 5 | 385 | 21.586 | |
| philippines | Fase 1 | 5 | 455 | 27.682 | |
| argentina | Fase 1 | 4 | 336 | 19.163 | |
| chile | LatAm | 4 | 364 | 22.596 | |
| colombia | LatAm | 3 | 218 | 14.927 | |
| hungary | Fase 2 | 3 | 182 | 11.750 | CDS inutilizable |
| peru | LatAm | 3 | 273 | 16.890 | |
| russia | Fase 1 | 2 | 160 | 9.500 | **mktcap corta 2024-08-09** |
| bulgaria | Fase 1 | 1 | 77 | 4.741 | below_min_banks 77/77 |
| egypt | Fase 1 | 1 | 90 | 5.498 | below_min_banks 90/90 |

### Por qué 2004 y no 1997

Se midió empíricamente la profundidad disponible pidiendo desde 1990:

- **Macro** (VIX, UST10Y, tipos de cambio): 1990-1993. No es restricción.
- **HY spread**: 1994.
- **Insumos GaR ya existentes** (CPI, STX, rEER): 1970-1996; `Ryr` mediana 2003.
- **CDS soberano 5Y**: el más antiguo es 2000-10 (Sudáfrica, Turquía). El EMBI Global de
  JP Morgan (`JPEIGLSP Index`) tampoco existe antes de 2000-01.

O sea que **la restricción es la variable dependiente**, no los bancos: el mercado de CDS
soberanos de emergentes no existía antes de 2000. Un panel desde 1997 tendría 3-4 años sin
nada que explicar, y la cobertura bancaria se desploma (34 de 113 bancos, China 0).

**2004 deja la crisis financiera global de 2008 DENTRO de la muestra**, que era el hueco
serio del corte anterior en 2010 para una tesis sobre fragilidad y tail risk.

### Salida macro/GaR — `bloomberg_extraction/output_macro/`

- `GLOBAL/`: VIX (5.731), UST10Y (5.907), HY_SPREAD (5.698).
- por país: `EMBI_<pais>.csv` (CDS 5Y), `rating_<pais>.csv`, `fxvol_<pais>.csv`,
  `prof_margin_<pais>.csv`.
- Rating S&P resuelto para los 20 países (Rusia = `NR`, sin puntaje, correcto).

## Lo que hubo que arreglar (todo verificado, no adivinado)

### xbbg 1.0 rompió la API de 0.7
El entorno tiene **xbbg 1.0.0**, que es una reescritura: devuelve un frame *largo* de
narwhals sobre pyarrow (`ticker, date, field, value`, todo string) en vez de un DataFrame
pandas ancho, y el kwarg `Per=` ya no existe (`BlpValidationError`). Se agregó una capa de
adaptación en `bloomberg_common.py` (`_XBBG_CALL`, `_to_wide`, `_PERIODICITY`) que pide
`backend="pandas"`, `format="long_typed"` y re-arma el formato ancho.
**Si esto se vuelve a romper, el sospechoso #1 es una actualización de xbbg.**

### Mnemónicos Bloomberg que estaban mal
| Estaba | Es | Efecto del error |
|---|---|---|
| `LT_DEBT` | `BS_LT_BORROW` | no es mnemónico válido; `bonds` (y toda la regla LP/CP) venía vacío |
| `RTG_SP_LT_FC_ISSUER_RATING` | `RTG_SP_LT_FC_ISSUER_CREDIT` | rating vacío en los 12 países |
| `BEBGHYCS Index` | `LF98OAS Index` | BAD_SEC; equivale al FRED BAMLH0A0HYM2 del repo |

### Tickers desactualizados (`MARKET_STATUS = TKCH` / `DLST`)
Todos devolvían **0 observaciones de mktcap** mientras el balance salía completo, así que el
banco desaparecía del panel en silencio:

| Era | Es | País |
|---|---|---|
| `SPL PW` | `EBP PW` | Santander Polska |
| `CHIB PM` | `CBC PM` | China Banking Corp |
| `5F4 BU` | `FIB BU` | Fibank — además 5F4 daba mktcap en BGN contra balance en EUR (×1,95583) |
| `BSANTANDER CI` | `BSAN CI` | Santander Chile |
| `GFREGIO MM` | `RA MM` | Banregio → Regional SAB |
| `BCOLO CB` | `CIBEST CB` | Bancolombia → Grupo Cibest |
| `CONTINC1 PE` | `BBVAC1 PE` | BBVA Perú |
| `FHB HB` | `MBHJB HB` | MBH Mortgage Bank (Hungría) |

El CDS soberano de China no resuelve por nombre de emisor (BAD_SEC); sí por ticker Markit
`CCHIN1U5 Curncy`. Está en `CDS_TICKER_OVERRIDE`.

### Regla de moneda: siempre cotización LOCAL, nunca ADR
`BAP US`, `ITUB US`, `BBD US`, `CIB US`, `BSAC US` y otros cotizan en USD contra un balance
en moneda local (`EQY_FUND_CRNCY`); esa inconsistencia corrompe el Merton-KMV por un factor
de tipo de cambio. En los 113 bancos se verificó `CRNCY == EQY_FUND_CRNCY`.

### Frecuencia de reporte
Los 6 bancos sudafricanos reportan **semestralmente**: cualquier pedido trimestral vuelve con
las fechas pero sin datos. `_pull_fundamentals` intenta trimestral y cae a semestral por
ticker. No se puede hardcodear por país: para GGAL (Argentina) el pedido semestral da 0.
Además `periodicityAdjustment` pasó de `CALENDAR` a `ACTUAL` en fundamentales, lo que mejora
cobertura (`BS_LT_BORROW` de BDO Unibank: 29 → 46).

### Dato corrupto puntual
`BS_TOT_ASSET = 0.0` para United Bank (Pakistán) en 2025-02-27, con equity de 275.289 en la
misma fila. Propagaba `total_liab` y `st_borrow` negativos. `finalize_balance` lo marca NaN.
**`bonds == 0` sí es legítimo** (banco sin deuda LP emitida) y no se toca.

## Limitaciones de los datos — decisiones metodológicas PENDIENTES

Ninguna es un bug arreglable con mejor código:

1. **India no tiene CDS soberano.** `INDIA CDS USD SR 5Y Corp` no devuelve serie, y no es un
   problema de nomenclatura: India no emite deuda soberana en moneda dura de referencia. El
   proxy de spread tiene que salir del `GTINR10Y` contra el UST10Y.
2. **Corea del Sur: el balance solo llega a 2009**, aunque el mktcap llega a 2004. Los
   holdings financieros se formaron después (KB 2008, Hana 2005, BNK/DGB 2011, JB 2013,
   Woori 2014, Kakaobank 2021); solo Shinhan e IBK cotizan desde 2004. El Merton-KMV de
   Corea empieza efectivamente en 2009.
3. **Sudáfrica queda en frecuencia semestral** mientras el resto es trimestral. El motor
   JLoss agrupa por trimestre → la mitad quedará vacía. ¿Interpolar, arrastrar, o dejarla?
4. **Rusia: la serie de mercado termina el 2024-08-09.** `MARKET_STATUS = PRNA` para SBER y
   VTBR — Bloomberg dejó de precificarlos por sanciones. Sin valor de mercado no hay
   Merton-KMV. ¿Panel truncado o país fuera?
5. **Rating S&P es un SNAPSHOT, no una serie.** `RTG_SP_LT_FC_ISSUER_CREDIT` vía `bdh` vuelve
   vacío en cualquier frecuencia: un solo rating para todo el panel. Débil justo para
   Turquía, Argentina y Rusia, degradadas varias veces en el período.
6. **CDS sin cobertura utilizable en 6 países** (el security resuelve, no hay precios):
   Polonia, Bulgaria, Rusia y Hungría solo 2012-07..2015-10; Pakistán solo desde 2026-03;
   Egipto disperso. Los cuatro primeros son todos de Europa central/oriental — parece un
   hueco de licencia, no de mercado. Para Polonia y Hungría existe el bono genérico 10Y, así
   que un spread contra Bund/UST es la alternativa natural.
7. **Bancos cotizados insuficientes:** Bulgaria y Egipto tienen 1, Rusia 2, Hungría 3 (y
   Gránit solo desde 2024). `below_min_banks` marcará casi todos sus trimestres. Estructural
   del universo, no de los tickers.
8. **`grupo_aval` excluido** de Colombia: holding de bogota/popular/occidente/av_villas,
   duplicaría bancos ya presentes. **`bbva_peru` puede pasar de PD contable a PD de mercado**:
   entraba como `book` porque yfinance no lo tenía, Bloomberg sí, con 4.176 obs.

## Cobertura cruzada con el panel GaR

Con la Fase 2 (Corea, India, Hungría) el JLoss ya cubre los 17 países de `gar_panel_all17`,
más Argentina, Egipto y Rusia que el GaR no tiene. Del lado GaR quedan huecos ajenos a
Bloomberg: **Egipto no tiene carpeta en `GaR/individuals/`** y **Argentina no tiene `Ryr` ni
`FCI`**. Bloomberg no puede cerrarlos: no existe bono genérico 10Y ni para Argentina ni para
Egipto (`GTARS10Y`/`GTEGP10Y` sin serie). Sí cubre sus índices bursátiles (`MERVAL`,
`EGX30`). El script del repo ya los manda a "Capa 2, descarga manual".

## Entorno de ejecución

`.venv` del proyecto PyCharm está vacío. El entorno correcto es **`bloomberg_env`** (conda),
en `C:\Users\itau_lab\.conda\envs\bloomberg_env`, con blpapi 3.26.2.1, xbbg 1.0.0,
pandas 3.0.2. `conda` NO está en el PATH: usar el intérprete directo
`C:\Users\itau_lab\.conda\envs\bloomberg_env\python.exe`. Requiere el Terminal Bloomberg
abierto (BBComm activo). Ojo: xbbg está en el site-packages **de usuario**
(`C:\Users\itau_lab\AppData\Roaming\Python\Python313\site-packages`), no dentro del env.

```
cd bloomberg_extraction
python extract_jloss_bloomberg.py                 # los 20 paises, desde 2004
python extract_jloss_bloomberg.py --country india
python extract_jloss_bloomberg.py --start 2000-01-01   # otro corte
python gar_macro_bloomberg.py                     # macro + global
```

## Pendiente al retomar

1. Decidir los 8 puntos metodológicos de arriba.
2. Enchufar estos CSV al motor JLoss y al pipeline GaR aguas abajo.
3. Cerrar los huecos GaR de Egipto y Argentina por fuera de Bloomberg.

## Preguntas ya resueltas (no volver a preguntar)

- El JLoss ya subido al repo se ignora — todo se reconstruye desde Bloomberg, solo se
  reutiliza el schema/cabecera.
- Destino GitHub: repo de la tesis, no uno nuevo.
- Corte histórico: 2004 (ver la justificación arriba).
- Cotización local siempre, nunca ADR.
