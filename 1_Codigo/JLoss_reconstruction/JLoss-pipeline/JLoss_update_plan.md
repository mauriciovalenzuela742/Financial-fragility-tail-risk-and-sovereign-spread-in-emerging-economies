# Actualización y mejora de la métrica JLoss — plan de extracción y especificación

## A. Métrica JLoss mejorada (qué se actualiza)

La métrica vigente: `JLoss = (EL + UL)·100/ΣEAD`, con UL = contribuciones marginales al VaR₉₉
por punto de silla; PD vía Merton de una pasada; σ_E realizada × √4; ρ = 0.4 plano; LGD = 0.45.
Mejoras propuestas, en orden de impacto sobre la calidad de la PD y del riesgo de cola:

1. **Calibración KMV iterativa (Moody's) del valor de activos.** Reemplazar el sistema de dos
   ecuaciones de una pasada por el algoritmo iterativo: dado σ_A, invertir la ecuación de equity
   período a período para obtener la serie V_{A,t}; re-estimar σ_A como volatilidad realizada de
   los log-retornos de activos; iterar hasta convergencia (|Δσ_A| < 1e-4). Es el estándar de
   Moody's-KMV y reduce el sesgo de la σ_A frente a la aproximación de una pasada.

2. **Volatilidad de equity EWMA(λ=0.94)** en lugar de √(Σr²)·√4. Captura el clustering de
   volatilidad y es justamente lo que esboza el propio `KMVcompute_jf.m` del proyecto
   (`Vol(i)=(1-λ)·r² + λ·Vol(i-1)`). Alternativa: GARCH(1,1) para colas más gruesas.

3. **Distancia a default y EDF.** Mantener la DD lineal de KMV
   $DD_t=(V_{A,t}-DP_t)/(V_{A,t}\,\sigma_A)$, $EDF_t=\Phi(-DD_t)$, para consistencia con la serie
   oficial; opcionalmente reportar también la versión con drift $\mu_A$ estimado.

4. **Correlación de activos ρ estimada** en vez de 0.4 plano. Especificación de un factor común:
   estimar la carga $\rho_i$ de los retornos de activos de cada banco sobre un factor sistémico
   (primer componente principal del panel de retornos de activos, o regresión sobre el índice
   bancario del país). Como referencia regulatoria, contrastar con la correlación IRB de Basilea
   $R(PD)=0.12\frac{1-e^{-50\,PD}}{1-e^{-50}}+0.24\left(1-\frac{1-e^{-50\,PD}}{1-e^{-50}}\right)$.
   **Entregar dos series:** ρ=0.4 (comparable con el histórico) y ρ estimado (métrica mejorada).

5. **LGD país/tiempo-variable** (sensibilidad). Mantener 0.45 como base y testear LGD alternativos
   (p.ej. proxies de tasa de recupero o LGD regulatorio) para robustez.

6. **Cobertura y representatividad.** Extender a 2026 y registrar, por país-trimestre, la
   **fracción de activos del sistema** cubierta por los bancos incluidos. JLoss es una métrica
   sistémica: bancos faltantes la sesgan. Reportar la cobertura es requisito para el comité.

Inputs requeridos por banco-trimestre (sin cambios de esquema): market cap E, retornos de equity
(→σ_E), deuda de corto y largo plazo (→DP = ST + 0.5·LT) y pasivos totales (→EAD).

---

## B. Mapa de fuentes públicas por país

Para cada país: (i) **balances bancarios** (regulador/superintendencia, nivel banco, histórico) y
(ii) **precios de equity** (bolsa / proveedor público; sólo bancos listados). Sólo Chile fue
verificado en profundidad (sección D); el resto es punto de partida y requiere
confirmación de endpoints al abordarlo.

| País | Balances (regulador, nivel banco) | Calidad pública | Precios equity |
|---|---|---|---|
| chile | **CMF Bancos API** (api.cmfchile.cl) | Alta (1995–) | Bolsa Santiago / Yahoo `.SN` |
| brazil | **BCB IF.data** (Banco Central do Brasil) | Alta | B3 / Yahoo `.SA` |
| mexico | **CNBV Portafolio de Información** / Banxico | Alta | BMV / Yahoo `.MX` |
| colombia | **Superfinanciera (SFC)** | Alta | BVC / Yahoo |
| peru | **SBS** (Superint. Banca y Seguros) | Muy alta | BVL / Yahoo |
| argentina | **BCRA** (Información de entidades) | Alta | BYMA / Yahoo `.BA` |
| south_africa | **SARB** (returns BA900) | Alta (sistema+banco) | JSE / Yahoo `.JO` |
| turkey | **BDDK** / **TBB** (Banks Assoc. of Turkey) | Muy alta (TBB) | BIST / Yahoo `.IS` |
| poland | **KNF** / NBP | Media-alta | GPW / Yahoo |
| bulgaria | **BNB** (Banca Nacional de Bulgaria) | Media | BSE-Sofia |
| indonesia | **OJK** / Bank Indonesia | Media-alta | IDX / Yahoo `.JK` |
| malaysia | **BNM** (Bank Negara Malaysia) | Media | Bursa / Yahoo `.KL` |
| philippines | **BSP** (Bangko Sentral) | Media | PSE / Yahoo |
| pakistan | **SBP** (State Bank of Pakistan) | Media | PSX |
| china | **NFRA** (ex-CBIRC) / PBoC | Baja a nivel banco (más agregado) | SSE/SZSE / HKEX |
| egypt | **CBE** (Central Bank of Egypt) | Baja a nivel banco | EGX |
| russia | **CBR** (Bank of Russia, formularios 101/102) | Históricamente alta; **acceso complicado post-2022** | MOEX |
| venezuela | **SUDEBAN** | Baja / discontinua | — |

**Gradiente de factibilidad pública (de mejor a peor):** LatAm (peru, mexico, colombia, brazil,
chile, argentina) y turkey/south_africa tienen micro-datos públicos por banco de buena calidad;
indonesia/malaysia/philippines/poland/pakistan/bulgaria son viables con más trabajo; china/egypt
quedan mayormente agregados; russia depende del acceso post-sanciones; venezuela es el caso límite.

---

## C. Hoja de ruta de extracción (ordenada)

**Principio:** un extractor por país que produzca el esquema v8 (`mktcap_*` y `balance_*`), un
mapeo banco→`bankname` consistente con el panel, y un log de cobertura. El motor `compute_jloss`
del notebook v8 no cambia; sólo se alimenta con datos nuevos/actualizados.

- **Hito 1 (template):** Chile end-to-end (sección D). Fija el patrón reusable: cliente de API,
  mapeo de cuentas, fetch de precios, transformación a esquema v8 y QA de cobertura.
- **Hito 2 (núcleo LatAm de alta calidad):** peru (SBS), mexico (CNBV), colombia (SFC),
  brazil (BCB IF.data). Misma plantilla, distinto cliente de API.
- **Hito 3 (alta calidad no-LatAm):** turkey (TBB), south_africa (SARB), argentina (BCRA).
- **Hito 4 (viables con esfuerzo):** poland, indonesia, malaysia, philippines, pakistan, bulgaria.
- **Hito 5 (limitados):** china, egypt, russia, venezuela — evaluar caso a caso; posiblemente
  mantener la serie histórica y documentar por qué no se actualizan a nivel banco.

Para cada país, el entregable es: `extract_<país>.py` + `bankmap_<país>.csv` (CMF/regulador →
ticker → bankname) + `coverage_<país>.csv` (fracción de activos del sistema por trimestre).

---

## D. Chile — estado (Hito 1)

Fuentes confirmadas (2026):
- **Balances:** API CMF Bancos. Endpoints: `instituciones_bancarias`, `bs_institucion(year,inst)`,
  `bs_lista_cuentas(year,month)`, `bs_historico_cuenta_institucion(periodo,month,cuenta,inst)`
  (periodo1 1995–2007, periodo2 2008, periodo3 2009–hoy). API key gratuita.
- **Precios:** sólo bancos listados (Banco de Chile, BCI, Santander-Chile, Itaú-CorpBanca,
  Security, BICE). Bolsa de Santiago o Yahoo `.SN`.

Entregable: `extract_chile.py` (probado en su lógica de transformación). Pasos para correrlo:
1. Registrar API key gratuita en api.cmfchile.cl → `export CMF_API_KEY=...`
2. `python extract_chile.py --discover` para fijar los códigos de cuenta reales en `ACCOUNT_MAP`
   y verificar los códigos de institución con `instituciones_bancarias()`.
3. `python extract_chile.py --start 1999 --end 2026` → `balance_chile.csv`, `mktcap_chile.csv`.
4. Concatenar al panel v8 (`balance_data_monthly` + `mktcap_long`) y re-correr la Parte B.

**Decisión de modelado pendiente (para el comité):** la CMF clasifica obligaciones por
*instrumento*, no por *madurez*. El `ACCOUNT_MAP` por defecto asigna obligaciones a la vista +
con bancos a `st_borrow`, y captaciones a plazo + deuda emitida + otras obligaciones financieras a
`lt_borrow`. Esta es la diferencia metodológica principal frente al esquema del proveedor original
y debe justificarse explícitamente (o refinarse con el detalle de madurez del Compendio de Normas
Contables) antes de fijar la serie chilena.

---

## E. Núcleo LatAm — estado de implementación (Hito 2)

Cuatro adaptadores construidos sobre `jloss_common.py` (esquema v8, fetch de precios yfinance,
reporte de cobertura). **Lógica de transformación probada con payloads simulados** que imitan la
estructura de cada fuente; las llamadas de red se ejecutan en su entorno. La estimación de ρ
(doble: 0.4 ∥ ρ estimado por factor común) vive en la capa de métrica, no en estos extractores.

| País | Módulo | Acceso | Estado | Confirmar en runtime |
|---|---|---|---|---|
| brazil | `extract_brazil.py` | **API OData** (Olinda IFData) | Listo (API directa) | `--discover` → fijar `RELATORIO_BALANCO`, `TipoInstituicao` y nombres de columna |
| colombia | `extract_colombia.py` | **API Socrata** (datos.gov.co) | Listo (falta `dataset_id`) | `--discover` → fijar el resource id de balances y nombres de columna SoQL |
| peru | `extract_peru.py` | Descarga (boletines SBS .xls) | Scaffold | descargar los .xls por periodo; confirmar etiquetas de fila del Balance General |
| mexico | `extract_mexico.py` | Descarga/exportación (CNBV Portafolio) | Scaffold | exportar el Balance General; confirmar nombres de `concepto`/columna |

**Diferencia operativa clave:** Brasil y Colombia son extracción directa por API (programable,
reproducible end-to-end). Perú y México requieren un paso manual de descarga/exportación previo
(no exponen API REST), tras el cual el parser incluido los transforma al esquema v8.

**Mapas de banco (listados, con ticker para market cap):**
- brazil: itau_unibanco (ITUB4), bradesco (BBDC4), banco_do_brasil (BBAS3), santander_brasil (SANB11), banrisul (BRSR6), abc_brasil (ABCB4), banco_bmg (BMGB4), banco_inter (INBR32) — sufijo `.SA`.
- colombia: bancolombia (CIB, NYSE), banco_de_bogota, davivienda, banco_occidente, bbva_colombia, banco_popular. Cobertura de precios parcial (varios no listan con buen histórico).
- peru: bcp (vía Credicorp `BAP`), bbva_peru, scotiabank_peru, interbank (vía IFS). Precios sólo vía holdings listados.
- mexico: banorte (GFNORTEO), bbva_mexico, banamex, santander_mexico, hsbc_mexico, scotiabank_mexico, inbursa (GFINBURO), banco_bajio (BBAJIOO), banregio (GFREGIO) — sufijo `.MX`; varias filiales no listan en México.

**Advertencia de cobertura de market cap.** El modelo de Merton necesita E (valor de mercado del
equity). Muchos bancos relevantes son filiales no listadas (p.ej. BBVA México, Banamex, BBVA Perú,
Scotiabank Perú). Para esos, la PD no es estimable por Merton con datos públicos de precio. Tres
opciones a discutir con el comité: (i) restringir el universo a bancos listados con E observable;
(ii) usar el equity contable (`equity_book`) y una volatilidad de activos imputada (PD contable,
no de mercado) para los no listados; (iii) usar la matriz cotizante como proxy. Mantener consistencia
con el tratamiento del histórico es prioritario.

**Flujo por país:** `python extract_<país>.py [...]` → `balance_<país>.csv` + `mktcap_<país>.csv`
+ `coverage_<país>.csv` → concatenar a `balance_data_monthly`/`mktcap_long` → re-correr Parte B del
notebook v8 (con las dos configuraciones de ρ para la serie comparable y la mejorada).

---

## F. Clasificación de madurez del punto de default — RESUELTO

**Criterio del profesor (adoptado):** bonos (deuda emitida) = largo plazo; todo el resto del pasivo
= corto plazo. Implementado en los cinco extractores vía `jloss_common.derive_st_lt_bonds_vs_rest`:
```
total_liab = tot_asset - equity_book
lt_borrow  = bonos (deuda emitida)
st_borrow  = total_liab - bonos          # "resto", por residuo -> reconcilia por construccion
DP         = st_borrow + 0.5*lt_borrow = total_liab - 0.5*bonos
```
Ventaja: la línea "deuda emitida" es una partida estándar y aislable en todas las cartas de cuentas,
de modo que el criterio es homogéneo entre países y reconcilia con la identidad contable
ST+LP = pasivo total.

**Verificación en dos países (lo solicitado):**
- *Chile (CMF):* `Instrumentos de deuda emitidos` (Nota 22; bonos, letras, bonos subordinados). Por
  regulación chilena el plazo de los bonos es > 1 año, lo que valida bonos = LP.
- *México (CNBV):* `Títulos de crédito emitidos` + `Obligaciones subordinadas en circulación`; el
  resto (captación a la vista/plazo, interbancarios, reportos) es corto plazo.
- Chequeo `reconcile_bonds_vs_rest`: ST+LP = pasivo total en el 100% de las filas en ambas
  estructuras; los bonos son ~6% del pasivo (mediana), por lo que DP ≈ pasivo total y resulta
  **poco sensible** al peso de LP (DP/pasivo entre 0.91 con peso 0 y 1.0 con peso 1).

**Sobre la idea de duration / modified duration:** no es modelable con datos públicos. La duration
modificada exige el calendario de flujos (cupones, vencimientos, tasas) instrumento por instrumento,
inexistente en los balances regulatorios. Se descarta.

**Mejora sugerida (sí accesible y con sentido):** donde el supervisor publica el desglose por
**vencimiento residual** (reportes de calce de plazos/liquidez; p.ej. México ya separa interbancarios
en corto/largo plazo), usar el corte real < / > 1 año vía `jloss_common.apply_residual_maturity`,
con bonos-vs-resto como regla universal de respaldo. Adicionalmente, reportar el JLoss bajo pesos de
LP en {0, 0.5, 1} como banda de sensibilidad: dado que los bonos son una fracción menor del pasivo,
se espera que el resultado sea robusto a esa elección, lo que es en sí un argumento de robustez ante
el comité.

---

## G. Hito 3 — alta calidad fuera de LatAm (Turquía, Sudáfrica, Argentina)

Tres adaptadores nuevos sobre `jloss_common`, mismo criterio bonos-vs-resto y esquema v8; lógica de
transformación probada con payloads simulados de cada fuente.

| País | Módulo | Fuente (nivel banco) | Acceso | Partida de bonos (LP) |
|---|---|---|---|---|
| turkey | `extract_turkey.py` | TBB (Asociación de Bancos de Turquía) | Descarga/consulta (trimestral) | Securities Issued + Subordinated Debt |
| south_africa | `extract_southafrica.py` | SARB BA900 Economic Returns | Descarga CSV/XML (mensual, por ítem) | ruta de **vencimiento residual** (BA900 trae madurez); bonos-vs-resto de respaldo |
| argentina | `extract_argentina.py` | BCRA Información de Entidades Financieras | Descarga datos abiertos `.7z` (`.txt`) | Obligaciones negociables + Obligaciones subordinadas |

**Mapas de banco (listados, ticker para market cap):**
- turkey (`.IS`): akbank (AKBNK), garanti_bbva (GARAN), isbank (ISCTR), yapi_kredi (YKBNK), vakifbank (VAKBN), halkbank (HALKB).
- south_africa (`.JO`): standard_bank (SBK), firstrand (FSR), absa (ABG), nedbank (NED), capitec (CPI), investec (INL).
- argentina (`.BA`/ADR): banco_galicia (GGAL), banco_macro (BMA), bbva_argentina (BBAR), banco_supervielle (SUPV); santander_arg y banco_nacion sin precio (no listados) → PD contable.

**Nota Sudáfrica.** El BA900 entrega el corte por madurez de forma nativa, por lo que el extractor
usa por defecto la ruta de **vencimiento residual** (`mode='maturity'`: CP = pasivos ≤1 año, LP = >1
año), que es estrictamente más preciso que bonos-vs-resto; se deja `mode='bonds'` como respaldo para
homogeneidad. Los conjuntos de números de ítem del BA900 quedan como placeholders a completar con el
*data guide* del formulario antes de la corrida (la lógica de agregación ya está probada).

**Pendiente de confirmar en runtime** (igual que en LatAm): nombres/códigos de cuenta del estado
financiero TBB, del diseño de registro BCRA y los números de ítem del BA900; y correr
`reconcile_bonds_vs_rest` por país tras la extracción real.

### Estado global del pipeline
- **Listos/probados (8 de 18):** chile, brazil, colombia, peru, mexico, turkey, south_africa, argentina.
- **Restan (Hito 4, viables con esfuerzo):** poland, indonesia, malaysia, philippines, pakistan, bulgaria.
- **Restan (Hito 5, limitados a nivel banco):** china, egypt, russia, venezuela — evaluar caso a caso;
  posiblemente conservar la serie histórica y documentar por qué no se actualizan a nivel banco.

---

## H. Hito 4 — viables con esfuerzo (Polonia, Indonesia, Malasia, Filipinas, Pakistán, Bulgaria)

Seis configuraciones **delgadas** sobre `jloss_common.transform_long_generic` (mismo criterio
bonos-vs-resto y esquema v8, sin duplicar lógica). Cada módulo define sólo `BANKMAP` y
`ACCOUNT_MAP`; consumen un export long-format (bank, account, period, value) ensamblado desde el
regulador y/o los estados de los bancos cotizados. Transform probada para los seis (mapeo, bonos,
reconciliación).

| País | Módulo | Fuente | Precios | Nota |
|---|---|---|---|---|
| poland | `extract_poland.py` | NBP/KNF + estados IFRS de bancos GPW | `.WA` | PKO, Pekao, Santander, mBank, ING, Millennium, Alior, Handlowy |
| indonesia | `extract_indonesia.py` | OJK SPI + IDX | `.JK` | BCA, BRI, Mandiri, BNI, CIMB Niaga, Danamon, BTN, Panin |
| malaysia | `extract_malaysia.py` | BNM + Bursa | `.KL` | Maybank, CIMB, Public, RHB, Hong Leong, AmBank, Alliance, Affin |
| philippines | `extract_philippines.py` | BSP Published SoC + PSE | `.PS` | BDO, Metrobank, BPI, PNB, Security, Chinabank, UnionBank, RCBC |
| pakistan | `extract_pakistan.py` | SBP FSA + PSX | (pobre en yf) | HBL, MCB, UBL, NBP, ABL, Alfalah, Meezan, SCB → mayoría a **PD contable** |
| bulgaria | `extract_bulgaria.py` | BNB + BSE-Sofia | (limitado) | FIBank cotiza; UniCredit/DSK/UBB/Postbank no listadas → **PD contable** |

Notas de modelado: en Filipinas, `Bills payable` es de corto plazo y **no** entra en bonos (sólo
`Bonds payable` + subordinada). En Pakistán y Bulgaria la cobertura pública de precios es pobre, así
que la mayor parte del universo cae a PD contable (`book_pd`), que para eso se construyó.

### Estado global del pipeline (14 de 18)
- **Listos/probados (14):** chile, brazil, colombia, peru, mexico, turkey, south_africa, argentina,
  poland, indonesia, malaysia, philippines, pakistan, bulgaria.
- **Restan (Hito 5, limitados a nivel banco):** china, egypt, russia, venezuela.

---

## I. Hito 5 — limitados a nivel banco (China, Egipto, Rusia, Venezuela)

| País | Módulo | Viabilidad | Ruta |
|---|---|---|---|
| china | `extract_china.py` | **Alta (vía cotizados)** | Big Four + joint-stock con estados completos (HKEX/SSE); NFRA/PBoC agregado de respaldo |
| egypt | `extract_egypt.py` | Parcial | CIB con liquidez sólida; resto (QNB Alahli, CA Egypt, HDB, Faisal, ADIB) → mayormente PD contable |
| russia | `extract_russia.py` | Condicionada | IFRS de cotizados MOEX + Form 101 del CBR; **hueco 2022**, divulgación reducida para sancionados, precios MOEX poco fiables post-2022 → varios a PD contable |
| venezuela | `extract_venezuela.py` | **No viable (stub)** | Hiperinflación/redenominaciones, distorsión cambiaria y SUDEBAN discontinuo → conservar serie histórica y documentar; por defecto no produce serie |

Notas:
- **China** resulta de hecho factible por la vía de cotizados (a diferencia de lo anticipado como
  "limitado"): los grandes bancos publican estados completos. Tickers `.HK` (más fiables en yfinance)
  con `.SS` como alternativa.
- **Rusia**: el CBR suspendió la publicación por banco en 2022 y la reanudó desde mayo 2023 (Form 101/
  123/135) con omisiones para sancionados. El extractor mapea bonos por nombre (IFRS) o por prefijo de
  cuenta del Form 101 (520–523: obligaciones/certificados/letras emitidas) para la historia profunda.
- **Venezuela**: el módulo deja la estructura lista pero por defecto no genera serie; si se requiere
  una observación reciente, usar solo PD contable sobre ratios en términos reales y marcarla como no
  comparable.

### Estado global del pipeline — COMPLETO (18 de 18)
chile, brazil, colombia, peru, mexico, turkey, south_africa, argentina, poland, indonesia, malaysia,
philippines, pakistan, bulgaria, china, egypt, russia, venezuela.

Todos producen el esquema v8 bajo el criterio bonos-vs-resto, con `coverage_<país>.csv` y transform
probada. Pendiente común: confirmar en runtime los nombres/códigos de cuenta por fuente y correr
`reconcile_bonds_vs_rest` por país en la validación general.

---

## J. Cobertura de la Tabla A.1 y Panamá (19 países)

Se agregó **Panamá** (faltaba; Superintendencia de Bancos de Panamá, mayoría a PD contable) y se
expandieron los mapas de bancos hasta **cubrir o superar** el conteo de la Tabla A.1 en los 19 países:

| País | Tabla A.1 | En el pipeline | País | Tabla A.1 | En el pipeline |
|---|---|---|---|---|---|
| argentina | 5 | 6 | pakistan | 20 | 20 |
| brazil | 11 | 11 | panama | 2 | 6 |
| bulgaria | 3 | 6 | peru | 5 | 5 |
| chile | 6 | 6 | philippines | 10 | 10 |
| china | 13 | 13 | poland | 10 | 10 |
| colombia | 6 | 6 | russia | 5 | 8 |
| egypt | 9 | 9 | south_africa | 3 | 6 |
| indonesia | 23 | 23 | turkey | 8 | 8 |
| malaysia | 7 | 8 | venezuela | 3 | 5 |
| mexico | 4 | 9 | | | |

Donde la cobertura pública de precios es nula/pobre (pakistan, panama, varios bancos menores de
egypt/indonesia/russia), el `ticker` queda en `None` y esos bancos usan **PD contable** (`book_pd`).

Corrección de matching: `match_bank_generic` ahora elige el match **más específico** (subcadena más
larga), no el primero, para evitar capturas erróneas por nombres anidados (p.ej. "Bank of China"
dentro de "Postal Savings Bank of China"). Verificado para los grandes bancos chinos.

---

## K. Corrección de fuente — Colombia (NO es Socrata)

Hallazgo en la corrida real: los datasets "Estados Financieros NIIF" de datos.gov.co (pfdp-zks5,
prwj-nzxa, etc.) son de la **Superintendencia de Sociedades** (empresas no financieras: taxonomía
corriente/no corriente, matrícula mercantil), **no de la SFC**. Verificado con una fila de muestra
(NIT 830010665 = SECOLINSA S.A.S., actividades inmobiliarias). Por tanto **no contienen bancos**.

Fuente correcta (bancos): **Superintendencia Financiera de Colombia (SFC)** →
"Estados Financieros de las entidades vigiladas bajo NIIF" → Estado de Situación Financiera (CUIF),
por entidad y mes, **descargable** desde superfinanciera.gov.co. `extract_colombia.py` se reescribió
para la vía de **descarga** (como Perú/México), con `BANKMAP` por nombre de banco y `ACCOUNT_MAP`
sobre las cuentas del CUIF (bonos = "Títulos de deuda emitidos"/"Instrumentos representativos de
deuda"/"Obligaciones subordinadas"). Se descartó la API Socrata para Colombia.

### Colombia — formato disponible: XBRL (no Excel)
En el portal de la SFC, para casi todos los bancos el Excel está "no enviado"; el formato
machine-readable disponible es **XBRL** (individual/separado) + PDF. Flujo:
1. Descargar el XBRL **Individual/Separado** de cada banco (Estado de Situación Financiera) por período.
2. `parse_sfc_xbrl.py --file <xbrl> --bank "<nombre>" --out <banco>_long.csv` → long-format.
3. Concatenar los CSV de todos los bancos y pasarlos a `extract_colombia.py --file <concat>.csv`.
Nota: los conceptos del XBRL pueden venir en inglés (ifrs-full: Assets/Equity/Liabilities) o como
extensión SFC (p.ej. TitulosDeDeudaEmitidos); tras correr `--list` se afina `ACCOUNT_MAP` con esos
nombres exactos.

---

## L. Colombia — pipeline de descarga completo (SFC Envíos NIIF)

Tres scripts encadenados (más `extract_colombia.py`):

1. **`download_sfc_xbrl.py`** — descarga masiva con Selenium del portal Envíos NIIF de la SFC.
   - Tipo de entidad = Establecimiento Bancario; reporte = "Informes intermedios" (meses 03/06/09,
     columna I-I) o "Informes de cierre" (mes 12, columna I-C); años 2015–2025.
   - Por banco de la tabla, baja el XBRL **Individual/Separado** a
     `<carpeta_banco>/<carpeta_banco>_individual_<YYYY>-<MM>.xbrl`. Reanudable (salta lo existente).
   - Selectores ADAPTATIVOS (por texto de opción) + `--debug` (vuelca selects y filas para confirmarlos).
   - Mapa de 30 bancos -> carpeta verificado contra los nombres oficiales del portal.
   - `pip install selenium requests` (Chrome instalado; Selenium 4 gestiona el driver).
2. **`build_colombia_long.py`** — recorre las carpetas, parsea cada XBRL (vía `parse_sfc_xbrl`) y
   arma un único `colombia_long.csv` (bank, account, period, value).
3. **`extract_colombia.py --file colombia_long.csv`** — aplica bonos-vs-resto y produce
   `balance_colombia.csv` + cobertura.

Comandos:
```
python download_sfc_xbrl.py --debug                 # confirmar selectores (no descarga)
python download_sfc_xbrl.py --years 2025 --headful --limit 3   # prueba mirando el navegador
python download_sfc_xbrl.py --years 2015-2025       # corrida completa (headless, reanudable)
python build_colombia_long.py --root .              # -> colombia_long.csv
python extract_colombia.py --file colombia_long.csv --start 2015 --end 2026
```
Nota: como no se pudo inspeccionar el DOM del portal desde el entorno de desarrollo, los selectores
del formulario/resultados pueden requerir un ajuste menor con la salida de `--debug` (que guarda
`debug_page.html`). La lógica pura (mapeo banco->carpeta, nombres, parseo XBRL, bonos-vs-resto) está
probada de punta a punta.

### L.1 Descargador en puro requests (recomendado): download_sfc_niif.py
El portal de Envíos NIIF es una app JSF/PrimeFaces en
`https://www.superfinanciera.gov.co/SuperfinancieraNIIF/generic/SendingNiifAllList2.xhtml`.
`download_sfc_niif.py` replica su protocolo sin navegador:
  GET (ViewState) -> POST búsqueda (entityType=1, reportType=intermedio|cierre, año, mes)
  -> por banco disponible, POST del diálogo (params s/p/u leídos del onclick) -> downloadServlet.do?path=base64 -> GET.
Detecta XBRL plano vs ZIP por magic bytes. Reanudable. Parseo verificado contra el HTML real capturado.
Comandos:
```
pip install requests
python download_sfc_niif.py --probe          # verifica búsqueda+diálogo (no descarga)
python download_sfc_niif.py --years 2015-2025 # descarga a <banco>/<banco>_individual_YYYY-MM.{xbrl,zip}
python build_colombia_long.py --root .
python extract_colombia.py --file colombia_long.csv --start 2015 --end 2026
```
Notas: `reportType_input` para diciembre se asume `cierre` (la captura confirmó `intermedio`); si
diciembre sale vacío, confirmar el valor en DevTools. El id del botón Buscar (`j_idt57`) se autodetecta.

---

## M. Hito 6 — Hungría, India, Corea del Sur (fuera del alcance original del plan; requeridos por el panel de 15 países del working paper)

Estos 3 países están en el panel GaR/EMBI de 15 países pero **no aparecían en ningún lugar del plan
original de 19** (secciones B–L). No hay código, mapeo de bancos ni investigación previa. Lo que
sigue es investigación nueva de fuentes; ningún extractor ha sido escrito ni probado todavía.

| País | Balances (regulador, nivel banco) | Calidad pública | Precios equity |
|---|---|---|---|
| hungary | **MNB** — *Aranykönyv* ("Libro de Oro") | Media (anual, no trimestral) | Bolsa de Budapest (BET); prácticamente solo OTP cotiza |
| india | **RBI** — *Statistical Tables Relating to Banks in India* | Alta (bank-wise, pero anual) | NSE/BSE; el mejor universo cotizante de los tres |
| south_korea | **FSS** — FISIS / DART | Alta (trimestral, por institución) | KRX; buen universo cotizante |

### M.1 Hungría — MNB *Aranykönyv*

- **Fuente:** Magyar Nemzeti Bank, portal `statisztika.mnb.hu`. La sección "Supervisory statistics"
  publica el *Aranykönyv* (Libro de Oro), un Excel descargable con balance por **institución
  individual** (ej. `statisztika.mnb.hu/timeseries/aranykonyv-2022.xls`), una edición por año.
- **Limitación clave:** el Aranykönyv es de frecuencia **anual**, no trimestral como el resto del
  panel. Hay que revisar si "Supervisory banking statistics (latest)" (`statisztika.mnb.hu/statistical-topics/supervisory-statistics/i_-financial-institutions/`)
  tiene una versión trimestral por institución, o si hay que interpolar/usar la anual como proxy con
  nota de limitación explícita para el comité.
- **Precios:** Bolsa de Budapest (BET). El sistema bancario húngaro está dominado por filiales de
  bancos extranjeros que **no cotizan por separado** en Budapest: Erste Bank Hungary, K&H (KBC),
  Raiffeisen Bank Hungary, UniCredit Bank Hungary, CIB Bank (Intesa). El único banco húngaro
  verdaderamente cotizado es **OTP Bank** (ticker `OTP.BD` / `OTP` en BET). El resto cae casi
  íntegramente a **PD contable** (`book_pd.py`), igual que Bulgaria y Pakistán — de hecho Hungría es
  probablemente el caso más limitado de los 15, más que Bulgaria.

### M.2 India — RBI *Statistical Tables Relating to Banks in India*

- **Fuente:** Reserve Bank of India, publicación anual `Statistical Tables Relating to Banks in
  India` (PDF/Excel en `rbi.org.in/Scripts/AnnualPublications.aspx?head=Statistical+Tables+Relating+to+Banks+in+India`).
  Contiene tablas **bank-wise** (por banco individual) de liabilities & assets, deposits, advances,
  NPAs, earnings — exactamente el nivel de detalle que necesita el motor JLoss. También existe el
  portal **DBIE** (`data.rbi.org.in/DBIE`) para series históricas, aunque agregadas por grupo de
  bancos más que por institución.
- **Limitación:** al igual que Hungría, la publicación bank-wise es **anual** (año fiscal indio,
  abril–marzo). Para frecuencia trimestral habría que recurrir directamente a los estados
  financieros trimestrales que cada banco listado presenta a BSE/NSE (vía sus propias relaciones de
  inversores o agregadores como screener.in) — más trabajo pero factible dado el buen universo
  cotizante.
- **Precios:** NSE/BSE. Es el mejor universo cotizante de los tres nuevos países — grandes bancos
  públicos y privados listados: State Bank of India (`SBIN.NS`), HDFC Bank (`HDFCBANK.NS`), ICICI
  Bank (`ICICIBANK.NS`), Axis Bank (`AXISBANK.NS`), Kotak Mahindra Bank (`KOTAKBANK.NS`), Punjab
  National Bank (`PNB.NS`), Bank of Baroda (`BANKBARODA.NS`), Canara Bank (`CANBK.NS`), IndusInd Bank
  (`INDUSINDBK.NS`), IDFC First Bank (`IDFCFIRSTB.NS`).

### M.3 Corea del Sur — FSS FISIS / DART

- **Fuente:** Financial Supervisory Service (FSS). Dos sistemas complementarios, ambos con interfaz
  en inglés:
  - **FISIS** (Financial Statistics Information System, `efisis.fss.or.kr`) — balance e income
    statement **por institución individual**, con buena frecuencia (trimestral).
  - **DART** (`englishdart.fss.or.kr`) — filings XBRL de compañías cotizadas, equivalente coreano a
    EDGAR/CVM/Olinda; fuente machine-readable para los bancos listados.
  De los tres países nuevos, Corea del Sur es el que más se parece en calidad/frecuencia al patrón de
  Turquía/Sudáfrica (Hito 3) — vale la pena tratarlo con la misma plantilla.
- **Precios:** KRX. Bancos principales cotizados: KB Financial Group (`105560.KS`), Shinhan Financial
  Group (`055550.KS`), Hana Financial Group (`086790.KS`), Woori Financial Group (`316140.KS`),
  Industrial Bank of Korea/IBK (`024110.KS`). NongHyup Financial Group es cooperativa y no cotiza —
  cae a PD contable.

### M.4 Prioridad sugerida

**Corea del Sur > India > Hungría**, en orden de facilidad/calidad de dato bank-level trimestral.
Corea del Sur tiene la mejor combinación fuente+frecuencia+cotizante. India tiene el mejor universo
cotizante pero la fuente regulatoria bank-wise es anual (requiere trabajo extra para trimestralizar).
Hungría es el caso más limitado: fuente anual y solo un banco realmente cotizado, así que la mayor
parte del sistema terminará en PD contable — comparable a Bulgaria/Pakistán pero peor en cobertura
de precios.

**Pendiente:** escribir `extract_hungary.py`, `extract_india.py`, `extract_southkorea.py` sobre
`jloss_common.py` (mismo criterio bonos-vs-resto, esquema v8) una vez confirmados los nombres/
códigos de cuenta exactos de cada fuente en runtime — igual que el resto del pipeline, no ejecutable
desde este entorno por la restricción de red del PASO 0.
