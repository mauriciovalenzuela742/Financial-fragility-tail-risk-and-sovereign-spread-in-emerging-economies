# Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano en economías emergentes

Tesis de Magíster en Economía Aplicada (Universidad de Chile; profesor guía J. F. Martínez, coguía
R. Fischer; comisión A. Corvalán). Chari et al. (2024) ya documentan la asociación entre fragilidad bancaria y spread
soberano. Sobre esa base, la tesis pregunta **qué agrega el riesgo económico doméstico —el riesgo de
cola del crecimiento— y qué ocurre cuando los dos riesgos se dan a la vez**: si sus efectos sobre el
spread se suman o se amplifican.

Las métricas no son propias. **`JLoss`** es de Chari et al. (2024), y el **`GaR`** (*Growth-at-Risk*)
es de Adrian, Boyarchenko y Giannone (2019), en la implementación de CEMLA (Ossandón Busch et al.,
2022). Lo propio es construir las series de las dos métricas con un protocolo homogéneo y cruzarlas.
Todos los coeficientes son **asociaciones, no efectos causales**.

> **Estado a 2026-10-28.**
> - Tesis compilada: [`4_Redaccion/tesis/main.pdf`](4_Redaccion/tesis/main.pdf) (165 pp.). El resumen y la
>   introducción son el texto oficial del autor. El resto se redactó con las pautas del *humanizer*, sin
>   cambiar cifras ni citas.
> - Paper empírico standalone: [`4_Redaccion/envios/paper_empirico/`](4_Redaccion/envios/paper_empirico/).
> - Evaluaciones con rúbrica: la última es [`evaluacion_decima.md`](4_Redaccion/evaluacion_decima.md) (6,6),
>   y la del texto oficial es [`evaluacion_resumen_intro_oficial.md`](4_Redaccion/evaluacion_resumen_intro_oficial.md).
> - **Análisis aparte, fuera de la tesis:** ESG soberano, gobernanza y el peso de los factores externos frente
>   a los domésticos (preregistro 9). Ver [`analisis_esg_lambda.md`](4_Redaccion/analisis_esg_lambda.md) y la
>   sección correspondiente más abajo.
> - **Explorador interactivo del panel** (página privada): ver la sección
>   [Explorador interactivo del panel](#explorador-interactivo-del-panel).

---

## Estado de la investigación

### Datos — un solo panel, fuente homogénea

| Insumo | Fuente | Cobertura efectiva |
|---|---|---|
| **JLoss** (Merton–KMV + punto de silla) | Bloomberg: balances + capitalización bursátil de 113 bancos | 20 economías, 2004–2026 |
| **Spread soberano** | **EMBI Global Diversified (J.P. Morgan)**. La serie del FMI (GFSR) completa Indonesia y Sudáfrica en 2010–2014. CDS soberano 5Y como robustez | 13 economías |
| **GaR** (cuantil 5 % del crecimiento, regresión cuantílica de panel en pseudo-tiempo real) | FCI de estadísticas nacionales + VIX | 17 economías |
| **Controles domésticos** (deuda, fiscal, reservas, CA, inflación, REER) | FMI WEO + Banco Mundial + BIS, anuales interpolados | — |
| **Gobernanza (WGI)** para la triple interacción institucional | Banco Mundial, *Worldwide Governance Indicators* (valor de 2018). Desde el 28-10-2026 reemplaza a la plantilla provisional de `instituciones.csv` | 17 economías |

**Muestra de estimación:** 13 economías, **N = 765** observaciones país-trimestre, 2004Q2–2026Q2
(`1_Codigo/Panel/bbg/Panel_bloomberg_embiext.csv`).
- Argentina entra solo como robustez, porque su GaR usa un FCI sin el bloque de tasas.
- Quedan fuera las economías cuyo `JLoss` no es válido a nivel país: Corea del Sur (*Korea discount*),
  Bulgaria (un banco cotizado) y Hungría (dos).

**Especificación principal:**
- Variable dependiente: `ln EMBI_it`.
- Regresores, centrados: `ln JLoss_i,t-1`, `D_i,t-1 = −GaR_i,t-1` y su producto.
- Efectos fijos de país y de tiempo, sin controles.
- Inferencia: errores de Driscoll–Kraay y *wild cluster bootstrap* por país (pesos de Webb).
- Todo se reestima además en niveles (puntos básicos).

### Resultados principales

**Deuda y riesgo de cola: una regularidad de la muestra (preregistros 1, 2, 5 y 6):** donde hay más deuda pública, el riesgo de
cola del crecimiento pesa más en el spread, como sugieren los modelos de incumplimiento soberano. Una d.e. más de
deuda eleva en un tercio la semielasticidad al riesgo de cola del trimestre siguiente y en un 70 % la del riesgo de
cola del año siguiente (este último, firme: 0,047; Holm 0,018). Ni el doom loop completo (deuda × fragilidad) ni
el pecado original (deuda en moneda extranjera) se confirman. Un modelo de límite fiscal calibrado (preregistro 6,
`p59`) predice la interacción en puntos básicos, no en logaritmos, donde predice el signo contrario. Con la inferencia conjunta sobre los cuatro
preregistros (`p56`), la interacción resiste una permutación de la deuda entre economías con el riesgo de cola
del año siguiente (p = 0,009), pero no con el del trimestre siguiente (p = 0,17), que pasa a sugerente.
Fuera de la muestra no se confirma (preregistro 5, `7df0427`): en Hungría y Corea el signo se repite, pero la
interacción es siete veces la original y la diferencia se rechaza (potencia 5 %); un instrumento de términos de
intercambio es débil para la interacción (F 9,7) y la estima nula. Es un resultado de la muestra original.

**Reproducción:** `python 1_Codigo/Panel/reproducir.py` regenera las cifras desde los CSV y verifica 140 cifras
canónicas (`verificar_canonicos.py`, también en la integración continua).

**Inferencia conjunta:** ocho preregistros, fechados en el historial antes de los datos, suman 23 hipótesis
primarias, que `p66` corrige en conjunto. El riesgo de cola del año siguiente (4,7 % por pp) es firme dentro de
su preregistro, pero no sobrevive a la corrección conjunta: Holm 0,08 sobre 14 hipótesis y 0,13 sobre 23.

Escala de evidencia:
- *Firme*: resiste el wild bootstrap o una permutación y no depende de un país.
- *Sugerente*: solo es significativo con Driscoll–Kraay, o depende de un país.
- *Exploratorio*: no estaba preespecificado y no pasa la corrección de Holm.

| Conclusión | Evidencia |
|---|---|
| **1. Los dos riesgos coinciden** más de lo esperado: hay 168 observaciones con ambos en su tercil alto, 1,2 veces lo esperado descontado el calendario común (p = 0,0002) y 1,9 veces lo esperado bajo independencia pura. Además, la fragilidad **antecede** al riesgo de cola (0,405; wild p = 0,024) y no al revés, sin depender de un país ni del bloque bursátil del FCI. | Firme (la precedencia, a un trimestre y no causal) |
| **2. Cuando coinciden, no hay evidencia de amplificación**: β₃ = −0,011 (DK p = 0,11; wild p = 0,89). Una prueba de equivalencia descarta una amplificación de más de un 35 % de la suma de las dos asociaciones, pero no una menor. | No hay evidencia |
| **3. El riesgo económico agrega poco, pero es un fundamento de largo plazo**: 0,037 sobre el modelo de Chari et al. No aparece en los cambios ni mejora el pronóstico. Con cargas heterogéneas sobre los factores comunes (CCE) resiste el wild bootstrap (p = 0,016) y la exclusión de cada país, y tiene una relación de largo plazo con el spread (PMG: 0,067; p = 0,006). | Firme como asociación de nivel |
| **4. Deuda y riesgo de cola: regularidad de la muestra, sin confirmación externa** (prueba preregistrada, commit `c492ca3`, datos trimestrales): una d.e. más de deuda eleva la semielasticidad de 0,032 a 0,043 (Holm p = 0,029; 13 de 13 sin cada país). Ninguna otra condición la modifica: ni la adecuación de reservas (Holm 0,29), ni la participación extranjera, ni el respaldo externo. El efecto directo de la fragilidad no se separa del canal fiscal. | Deuda: firme dentro de la muestra, sin confirmación externa (regularidad de la muestra); resto: no hay evidencia |
| **Extensiones (no preespecificadas):** a frecuencia mensual la fragilidad antecede al spread un mes; el instrumento granular es débil (F < 4); con 189 observaciones de EMBI imputado desde el CDS y con Argentina homologada nada cambia; las líneas swap de la Fed de 2020 bajaron el spread 20–22 pp, pero ninguna línea cambió la transmisión. | Ver `NUMEROS_CANONICOS_BBG.md` §21–25 |
| **Los bancos como unidad de análisis** (preregistro 3, commit `d73245f`): ninguna de las seis hipótesis pasa Holm (mínimo 0,88). La asociación se concentra en los dos bancos sistémicos de cada economía (0,062 frente a 0,022), sin significancia; las filiales pesan igual que los nacionales y más banca estatal va con menos transmisión. JLoss es robusto a tres calibraciones del motor (Spearman 0,92–0,97; β₁ > 0). | No hay evidencia de un canal bancario |
| **Umbrales de vigilancia** (preregistro 4, commit `7ad3810`): no hay un umbral de tensión financiera (p = 0,13) ni de deuda (0,26), y ningún indicador anticipa episodios de estrés fuera de la muestra (AUROC 0,49). Por país, los umbrales de deuda y de riesgo de cola no son comunes ni transferibles. Con más tensión, los riesgos domésticos pesan menos en el spread. | No hay evidencia de un umbral; la regla es continua |
| **Réplica de Chari et al.**: elasticidad de 0,099 (DK p = 0,003; wild p = 0,33) y de 0,107–0,164 con sus controles. Desaparece con los seis controles domésticos, y Turquía aporta el 70 % del coeficiente. | Sugerente |

Números canónicos completos y trazables:
[`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md)
(secciones 17 a 19 para la especificación vigente).

### Fronteras y limitaciones

- **Identificación:** la retroalimentación del spread hacia la fragilidad sesga los coeficientes de
  nivel. En una simulación sin efecto directo, la regresión entrega 0,066 para la fragilidad (dato:
  0,099) y 0,022 para el riesgo de cola (dato: 0,032). El IV *shift-share* no cierra la identificación:
  los instrumentos dan signos opuestos y la prueba de Sargan rechaza.
- **Pocos países:** con 13 clusters, Driscoll–Kraay rechaza una nula cierta entre el 20 y el 30 % de las
  veces. El wild bootstrap está bien calibrado, pero su potencia es de 35 % para la fragilidad y de 67 %
  para el riesgo de cola.
- **`JLoss` saturado:** el VaR99 satura la malla de pérdidas en el 98 % de las observaciones y el 23,7 %
  está en el piso (2,16). La métrica se lee como ordinal.
- **Fechado:** con datos trimestrales la fragilidad y el spread se mueven dentro del mismo trimestre.
  A frecuencia mensual (distancia al incumplimiento de Merton y EMBI diario), la fragilidad antecede al
  spread en un mes (0,013; wild p < 0,001; sin cada país), con una magnitud pequeña y sin dirección
  inversa. Es precedencia, no causalidad.
- **Simultaneidad concentrada:** 129 de las 168 observaciones conjuntas son de 2020 en adelante, aunque
  el exceso sobre el calendario viene de 2015–2019 y 2023–2026.
- **Controles:** son anuales interpolados y plausiblemente median el mecanismo ("mal control").

---

## Reproducir

Entorno: Python con `pandas`, `numpy`, `scipy`, `linearmodels`, `matplotlib`, `statsmodels`
(`1_Codigo/JLoss_reconstruction/JLoss-pipeline/venv` para el motor JLoss —
`requirements.txt` en esa carpeta—; `.venv` del root para el resto —`requirements.txt` en la
raíz—). MiKTeX o TeX Live completo para compilar la tesis. Requiere acceso de red solo si se
quiere **refrescar** IMF Datamapper / World Bank / BIS — los CSV ya extraídos están commiteados,
así que reproducir los números ya reportados **no** requiere red. Instructivo completo, con
qué pasos no son reproducibles sin Bloomberg Terminal/NLHPC y por qué:
[`4_Redaccion/REPRODUCIBILIDAD.md`](4_Redaccion/REPRODUCIBILIDAD.md).

```bash
# 1. JLoss desde Bloomberg (una vez extraídos los CSV crudos a Bloomberg_extraction/output/,
#    ya commiteados -- este paso NO requiere Bloomberg Terminal para reproducirse)
cd 1_Codigo/JLoss_reconstruction
mkdir -p _stage && for d in ../Bloomberg_extraction/output/*/; do c=$(basename "$d"); \
  cp "$d/balance_$c.csv" "$d/mktcap_$c.csv" _stage/; done
JLoss-pipeline/venv/Scripts/python.exe jloss_engine.py --indir _stage \
  --out jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv && rm -rf _stage

# 2. Panel + análisis (desde 1_Codigo/Panel/, con el .venv del root)
python bbg/p0_controles_all.py     # controles domésticos, todos los países (red: IMF/World Bank)
python bbg/p1_build_panels.py      # -> bbg/Panel_bloomberg.csv, panel_real_bbg.csv, cobertura (red: World Bank)
python bbg/p2_regresiones.py       # theta (M1/M2/M3), robustez, umbral, efecto marginal
python bbg/p6_concentracion_trimestral.py  # -> concentracion_trimestral_bbg.csv (HHI_q)
python bbg/p7_iv_dolar_bis.py      # instrumento dólar BIS -> usd_neer_bbg.csv (red: stats.bis.org)
python bbg/p7b_iv_commodity_tot.py # instrumento ToT commodities -> ctot_shock_bbg.csv (red: World Bank, frágil)
python bbg/p7c_iv_reforzado.py     # IV con los 3 instrumentos (OnOffRun, USD BIS, ToT)
python bbg/p3_causal_fase5.py      # batería causal (IV reforzado) + H4a/H4b (3 proxies de HHI)
python bbg/p5_robustez_arbitro.py  # ventanas móviles, placebo, país influyente, regresor generado, GMM
python bbg/p8_bateria_regresiones.py  # batería 4x3x2 estilo Chari et al. (2024)
python bbg/p9_crisis_interaccion.py   # Backstop vs EMstress (test de falsación, Sección 8 del EDA)
python bbg/p9_diag_ryr.py             # diagnóstico de endogeneidad Ryr <-> EMBI
python bbg/p9_robustez_gar_nocdiff.py # robustez: GaR reconstruido sin CDIFF
python bbg/p4_figuras.py           # figuras -> bbg/figuras/ y copia a 4_Redaccion/tesis/imagenes/

# 2e. Especificación vigente: log-log rezagada sobre Panel_bloomberg_embiext.csv (lo construye
#     p1_build_panels.py --embi-ext); JLOSS_FORMA=nivlag reestima todo en niveles (pb)
python bbg/p1_build_panels.py --embi-ext   # -> bbg/Panel_bloomberg_embiext.csv
python bbg/p12_tablas_latex_lnlag.py       # baterías 4x3x3 (tablas de la tesis)
python bbg/p13_figuras_paper.py            # figuras y efecto marginal del paper
python bbg/p14_arbitro_lnlag.py            # identificación: canal inverso, dinámica, LP, IV, réplica de Chari
python bbg/p15_comparacion_formas.py       # niveles frente a logaritmos (prueba PE, Box-Cox)
python bbg/p16_heterogeneidad.py           # agrupación ex post (exploratoria)
python bbg/p18_solapamiento_gar.py         # GaR frente a las variables financieras
python bbg/p19_resiliencia.py              # resiliencia de la política económica
# p21 a p31: fechado, potencia, estrés conjunto, medición, respaldo, participación extranjera, influencia
python bbg/p32_aporte_riesgo_cola.py       # información incremental, simultaneidad, bandas
python bbg/p33_simultaneidad_precedencia_tost.py  # nula de calendario, precedencia, equivalencia (TOST)

# 2b. Robustez a la censura del grid de JLoss (opcional, ~40 min de motor)
cd ../JLoss_reconstruction && python _engine_wide.py    # -> Panel_JLoss_wide.csv (grid [0.01,0.20])
cd ../Panel && python bbg/_robustez_widebounds.py       # -> robustez_widebounds_bbg.csv

# 2c. Bootstrap de regresor generado C1 (opcional, ~172 min en cluster -- ya ejecutado, ver
#     1_Codigo/GaR/individuals/nlhpc_gar_all18/gar_replicas_nlhpc.csv commiteado)
python bbg/p10_boot_gar.py segunda_etapa ../GaR/individuals/nlhpc_gar_all18/gar_replicas_nlhpc.csv

# 2d. Notebook EDA complementario (ejecutar con nbclient, no con `jupyter execute` -- ver instructivo)
python -c "import nbformat; from nbclient import NotebookClient; nb=nbformat.read('bbg/EDA_Panel_Final_bbg.ipynb', as_version=4); NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'bbg'}}).execute(); nbformat.write(nb, 'bbg/EDA_Panel_Final_bbg.ipynb')"

# 3. Documento de tesis (desde 4_Redaccion/tesis/)
latexmk -pdf main.tex             # -> main.pdf, 165 pp, compila sin errores (MiKTeX 25.12 / pdfTeX)

# 4. Análisis aparte ESG / lambda (preregistro 9; desde 1_Codigo/Panel/bbg/)
python p67_datos_esg.py      # WDI + WGI + Freedom House -> 2_Datos/esg_wb_anual.csv (red: World Bank)
python p68_indice_esg.py     # índices G y ESG (PCA) -> esg_indice_anual_bbg.csv, esg_trimestral_bbg.csv
python p69_esg_spread.py     # E1-E3 y exploratorio -> paper_p69_numeros.csv
python p70_lambda.py         # modelo lambda, E4-E5 y Holm -> paper_p70_numeros.csv (~30 min)
```

---

## Análisis aparte: ESG, gobernanza y λ·externo + (1−λ)·doméstico

El punto de partida es la tesis de Barneche, Grezzi y Panario (2024, ORT Uruguay), que relaciona un índice ESG
soberano con el EMBI, junto con Tebaldi, Nguyen y Zuluaga (2018). Tiene preregistro propio
([`preregistro_esg.md`](4_Redaccion/preregistro_esg.md), commit `81c2d9c`) y familia de Holm propia (E1–E5). No
entra en las 23 hipótesis de la tesis ni cambia sus cifras canónicas.

| | Resultado | Veredicto |
|---|---|---|
| Gobernanza (WGI) dentro del país | −0,33 por d.e.; wild p unilateral 0,016; 13 de 13 sin cada país; Holm 0,063 | Sugerente (lo más sólido) |
| Gobernanza × fragilidad | −0,15; Holm 0,063; cae sin Chile o sin Polonia | Sugerente y frágil |
| Índice ESG (réplica ORT) | −0,43; Holm 0,11; funciona solo por su componente de gobernanza | Sugerente |
| Peso de los factores externos (λ) | 0,48 [0,25; 0,57]; Shapley 0,44 | Lo global no domina |
| λ con la tensión global (VIX) | No sube (θ1 = −0,09; p 0,83) | No hay evidencia |

Ninguna hipótesis es firme. El informe completo, con las réplicas de ORT y de Tebaldi, está en
[`analisis_esg_lambda.md`](4_Redaccion/analisis_esg_lambda.md).

---

## Explorador interactivo del panel

[Explorador del panel JLoss–GaR](https://claude.ai/artifact/BKpAmnVmp3G6H2cRGdie4u): una página para
recorrer el panel trimestre a trimestre (2004–2026) con una barra de fechas común a todas las vistas.
Cada país tiene un color fijo.

- **Espacio 3D animado.** Los ejes se eligen entre 22 variables; por defecto son ln JLoss, D = −GaR y
  ln EMBI. Cada país deja una estela de hasta 8 trimestres.
- **Burbujas con estelas.** El tamaño de la burbuja es una tercera variable, por defecto deuda/PIB.
- **Mapa de calor país × trimestre**, en nivel o estandarizado dentro de cada país.
- **Cuadrícula de simultaneidad.** Terciles de JLoss y de D calculados dentro de cada país, junto con la
  serie de países en estrés conjunto.
- **Carrera de rankings** de la variable elegida.
- **Diccionario de datos y tabla de cobertura** por país. Las observaciones en la estimación suman 765,
  igual que en la tesis.

Los valores son del mismo trimestre (en las regresiones, ln JLoss y D entran rezagados un trimestre), y
los patrones son asociaciones. La página es **privada**: solo la puede abrir el autor y quienes él autorice,
porque incluye los niveles de EMBI y CDS, que son datos de proveedores (ver "Datos restringidos"). Los
datos salen de `Panel_bloomberg_embiext_arg.csv`, `esg_trimestral_bbg.csv` y
`2_Datos/participacion_extranjera.csv`.

## Estructura del repositorio

```
1_Codigo/
  Bloomberg_extraction/     Extracción xbbg de balances, mktcap y macro (20 países)
  JLoss_reconstruction/     Motor JLoss (jloss_engine.py) + salida jloss_bloomberg/
  GaR/                      Growth-at-Risk: motor CEMLA, FCI, insumos por país
  Panel/
    bbg/                    ← PIPELINE VIGENTE: p0..p5, panel único, números canónicos
    (legado)               construcción "dos bases" previa, notebooks EDA, análisis causal
  Stata_Sov_Risk/  v0/      Análisis predecesores (legado, no vigente)
2_Datos/                    Datos sueltos y paquetes portátiles
3_Marco_teorico/            Literatura de referencia (PDF)
4_Redaccion/
  tesis/                    ← TESIS VIGENTE: main.tex + capítulos + anexos (A matemático, B datos)
  envios/                   ← dos papers standalone para envío a revista + cartas + README
  CONTROL_DE_VERSIONES.md   fuente única de verdad sobre qué archivo es vigente por hilo
  modelo OI/                working paper del modelo teórico + apéndice
```

**Para cualquier duda de vigencia** (qué script, qué CSV, qué número es el actual):
[`4_Redaccion/CONTROL_DE_VERSIONES.md`](4_Redaccion/CONTROL_DE_VERSIONES.md).
`README_ORGANIZACION.md` (2026-07-25) describe la reorganización de carpetas pero está
**superado** en materia de resultados por este README y por `CONTROL_DE_VERSIONES.md`.

## Datos restringidos

Estos archivos se usaron en la tesis, pero no están en el repositorio porque sus proveedores no permiten
redistribuirlos. Quien tenga acceso puede regenerarlos o descargarlos y dejarlos en la misma ruta:

| Archivo (ruta local) | Proveedor | Cómo se obtiene |
|---|---|---|
| `1_Codigo/Bloomberg_extraction/output/<país>/` (capitalización diaria y balances por banco) | Bloomberg | `banks_bloomberg.py` / `extract_jloss_bloomberg.py` con Bloomberg Terminal |
| `1_Codigo/Bloomberg_extraction/output_macro/` (CDS soberano 5 años en `EMBI_<país>.csv`, volatilidad cambiaria, margen, ratings, VIX, UST10Y, HY) | Bloomberg (HY de ICE BofA; ratings de las agencias) | `gar_macro_bloomberg.py` con Bloomberg Terminal |
| `1_Codigo/Panel/bbg/banco_trimestral_bbg.csv` | Derivado banco por banco de Bloomberg | `p46_panel_bancos.py`, a partir de `output/` |
| `2_Datos/embi.xlsx`, `1_Codigo/Panel/Serie_Historica_Spread_del_EMBI.xlsx` | J.P. Morgan (EMBI Global Diversified) | Licencia de J.P. Morgan, directa o a través de Bloomberg |
| `2_Datos/vlab-srisk-all-20260728.csv` | NYU Stern V-Lab | Descarga en vlab.stern.nyu.edu |
| `1_Codigo/Stata_Sov_Risk/*.dta` | Análisis predecesor de procedencia no documentada; no se usa | No aplica |

Los paneles trimestrales que alimentan las regresiones (`Panel_bloomberg*.csv`) siguen en el repositorio,
así que `reproducir.py` y `verificar_canonicos.py` funcionan sin estos archivos. Los pasos que sí los
necesitan están en [`4_Redaccion/REPRODUCIBILIDAD.md`](4_Redaccion/REPRODUCIBILIDAD.md). Los archivos
salieron del árbol el 30-10-2026, pero siguen en los commits anteriores del historial, que no se reescribió
para no cambiar los hashes que fechan los preregistros.

## Licencia y cita

El código del autor se distribuye con licencia [MIT](LICENSE). La licencia no cubre los datos de terceros
que el repositorio incluye o deriva (J.P. Morgan, Bloomberg, V-Lab, Banco Mundial, Freedom House, FMI y
otros): cada uno conserva los términos de su fuente. Las métricas JLoss (Chari et al., 2024) y
Growth-at-Risk (Adrian, Boyarchenko y Giannone, 2019, con CEMLA) no son del autor. Para citar este trabajo,
use [`CITATION.cff`](CITATION.cff).

---

## Historial de la fase Bloomberg

| Commit | Contenido |
|---|---|
| `Agrega extracción Bloomberg (Fase 1)` … `Extiende el panel a 2004` | Extracción xbbg de 12 → 20 países |
| `Reancla la investigación empírica en datos Bloomberg` | JLoss + CDS soberano; primeras regresiones; H4b deja de sostenerse |
| `JLoss-pipeline: elimina PD contable del universo` | Decisión del comité (ago-2026): solo PD de mercado |
| `Reestructura la tesis como una sola investigación sobre un único panel` | Fin de la partición "núcleo LatAm / panel ampliado"; controles para todos los países; Anexo B de procedencia de datos |
| `Tesis: compilación limpia` | 0 warnings, 0 overfull boxes |
| `Revisión de árbitro: reconciliar cifras y batería de robustez` | Resumen del Cap. 2 realineado con el cuerpo; `p5_robustez_arbitro.py` (ventanas móviles, placebo, país influyente, regresor generado, GMM); reencuadre temporal a "post-GFC" |
| `Censura del VaR99 de JLoss` + `Robustez grid ancho — VERIFICADA` | El grid de pérdidas satura el VaR99 en el 98 % de las obs.; con grid ancho θ conserva magnitud y gana precisión (M2 p 0,056 → 0,032) |
| `Fase 2-3: prosa de artículo + empaquetado` | `paper2` §1 a prosa; H4b → "no identificado"; `4_Redaccion/envios/` con dos papers standalone |
| `Concentración trimestral + IV reforzado` | `HHI_q` de los mismos bancos que `JLoss` (H4b sigue no identificado); IV con exposición pre-2012 |
| `Reestructura el panel: EMBI como variable dependiente principal, CDS a robustez` | Variable dependiente = EMBI Global Diversified (Chari et al. 2024); CDS a robustez; el θ marginal negativo era específico del CDS |
| `Excluye Hungría; sección de heterogeneidad núcleo/convergencia` | Hungría fuera (2 bancos, `below_min` 89/89, mismo criterio que Bulgaria); panel de 13 países; hallazgo central pasa a ser la heterogeneidad: θ = −0,47 (p = 0,023) en el núcleo de 11 EM de financiamiento externo, no significativo al añadir Polonia e India; EMBI vs CDS dan el mismo θ sobre la misma submuestra |
| `Reescribe el paper empirico con la especificacion log-log rezagada…` | Especificación principal pasa a log-log con regresores rezagados un trimestre (como Chari et al., Tabla 4); niveles en pb en paralelo |
| `Integra Argentina al panel canonico…` | Argentina como robustez (GaR con FCI sin bloque de tasas) |
| `Reescribe la tesis como investigacion empirica unica…` | Sale el capítulo teórico de OI; batería de interacción de crisis |
| `Somete la especificacion principal a pruebas de arbitro…` / `Incorpora las pruebas del informe de árbitro…` | Dos rondas de arbitraje: fechado del spread, simulación de tamaño y potencia, participación extranjera preespecificada; el núcleo de 11 pasa a exploratorio; la conclusión pasa a "simultaneidad sin amplificación" |
| Evaluación experta (2026-10-21) | `p33`: simultaneidad con nula de calendario (1,2×), precedencia robusta a excluir países y al GaR sin bloque bursátil, prueba de equivalencia (se descarta amplificación > 35 % de la suma) |
| Evaluaciones séptima y octava (oct-2026) | Párrafo de vulnerabilidad → GaR reescrito; horizonte h = 1 justificado (panel trimestral, regresor rezagado un trimestre); nota 6,5 |
| `Deja oficiales la portada, el resumen y la introducción del autor` + pautas del *humanizer* (2026-10-27) | Texto oficial del autor con hallazgos corregidos; comisión: A. Corvalán; capítulos 2–7 y anexos redactados sin cambiar cifras ni citas |
| Preregistro 9 (`81c2d9c` … `65e89a0`, 2026-10-28) | Análisis aparte de ESG, gobernanza y λ; ninguna hipótesis firme |
| `Reemplaza la plantilla instituciones.csv por el WGI real de 2018` | La triple interacción institucional sigue sin ser significativa (EMBI +0,20, t 0,95) |
