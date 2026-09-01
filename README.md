# Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano en economías emergentes

Tesis de Magíster en Economía Aplicada (Universidad de Chile). Investiga por qué la
**coincidencia** de fragilidad bancaria sistémica y riesgo a la baja del crecimiento amplifica
el spread soberano de las economías emergentes por encima de la suma de sus efectos
individuales, desde dos aristas:

- **Capítulo empírico** — estima el término de interacción `JLoss × GaR` sobre el CDS
  soberano en un panel de economías emergentes.
- **Capítulo teórico (organización industrial)** — modelo de competencia bancaria à la Cournot
  del que esa complementariedad es una predicción de primer orden, con una predicción
  distintiva adicional: la amplificación por concentración bancaria.

> **Estado a 2026-09-01.** Toda la evidencia empírica está reanclada en datos de **Bloomberg**
> y estructurada como **una sola investigación sobre un único panel**. Tras una revisión de
> árbitro senior (batería de robustez ampliada, reconciliación de cifras, censura de la
> métrica de fragilidad), documento de tesis compilado y limpio:
> [`4_Redaccion/tesis/main.pdf`](4_Redaccion/tesis/main.pdf) (80 pp). Los dos capítulos se
> preparan además como envíos separados a revista — ver
> [`4_Redaccion/envios/`](4_Redaccion/envios/).

---

## Estado de la investigación

### Datos — un solo panel, fuente homogénea

| Insumo | Fuente | Cobertura efectiva |
|---|---|---|
| **JLoss** (fragilidad, motor de punto de silla / Merton–KMV) | Bloomberg: balances + capitalización bursátil de 113 bancos | 20 economías, 2004–2026 |
| **Spread soberano** | Bloomberg: **CDS soberano 5Y USD, exclusivamente** (celda vacía si no hay dato) | 11 países con historia continua + 3 parciales |
| **GaR** (riesgo de cola, regresión cuantílica de panel, marco CEMLA) | insumos FCI de estadísticas nacionales (Bloomberg no publica cuentas nacionales) | 17 economías |
| **Controles domésticos** (deuda, fiscal, reservas, CA, inflación, REER) | IMF WEO + World Bank + BIS, para **todos** los países del panel | — |
| **HHI** (concentración bancaria) | World Bank GFDD | — |

**Muestra de estimación:** 14 países, ~838 observaciones trimestrales.
**Exclusiones (2), por JLoss no válido a nivel país:** Corea del Sur (*Korea discount* →
Merton lee incumplimiento inminente) y Bulgaria (un solo banco cotizado). Ver
[`1_Codigo/Panel/bbg/DIAGNOSTICO_COREA.md`](1_Codigo/Panel/bbg/DIAGNOSTICO_COREA.md).

### Resultados principales

| Hipótesis | Resultado |
|---|---|
| **H1** — nivel: `JLoss → spread` | Respaldada con **instrumento fuerte** — IV *shift-share* (spread de liquidez de fondeo, exposición pre-2012): F = 21,6, β = +17,5 pb (**p = 0,001**), dirección banco→soberano. Un segundo instrumento (dólar efectivo amplio, BIS) también tiene primera etapa fuerte (F = 23,7) pero no corrobora la magnitud solo (p = 0,46), y combinar ambos **rechaza Sargan** (p = 0,003) — no conjuntamente válidos; se reporta el de mejor exclusión como principal. |
| **H3 / complementariedad** — θ (interacción `JLoss × GaR`) < 0 | **Signo y forma respaldados** — θ = −0,35; efecto marginal creciente y modelo de umbral de Hansen lo corrobora (+8,1 vs +2,3 pb por régimen). θ **invariante** a la medida de cola (GaR q05 / skew-t / ES). Significancia **marginal**: p = 0,056 (Driscoll–Kraay), 0,035 (*wild cluster bootstrap*), 0,001 (*cluster* por país); placebo de reasignación → p ≈ 0,05. |
| **Frontera temporal** | **Regularidad post-crisis financiera global**, no artefacto de COVID: θ positivo/nulo en 2006–2011, negativo y significativo en **todas** las ventanas móviles de 5 años que empiezan en 2012. El pre-2020 de muestra completa es n.s. sólo por promediar con 2004–2011; no hay quiebre discreto en 2020. |
| **Corte transversal efectivo** | La significancia descansa en **China**: sin China θ = −0,17 (n.s.); sin China+Turquía θ ≈ 0. 9 de 13 países casi no tienen variación de `JLoss`. |
| **Robustez a la censura de `JLoss`** | La cota del grid de pérdidas (4,8 % de la exposición) satura el VaR99 en el **98 %** de las observaciones. Recalculando con grid ancho `[0,01, 0,20]` (`JLoss` ×2,8, corr 0,92): **θ conserva la magnitud y gana precisión** — M2 θ = −0,330 (p = 0,032), M1 θ = −0,572 (p = 0,010). La censura sesgaba *en contra* del hallazgo. |
| **Regresor generado** | `JLoss` y `GaR` son estimados; el error de medición atenúa. θ estable a perturbar `GaR` hasta 25 % de su desviación. |
| **H4a** — β₃ > 0 (parametrización directa de la triple interacción) | Signo **contrario** al predicho, no significativo (+56). Sólo el θ de nivel sin HHI recupera el signo del modelo. |
| **H4b** — β₄ > 0: amplificación por concentración | **No identificada** con ninguno de tres proxies de HHI. GFDD estructural: β₄ = −392 (t = −2,34), IC90 (−627, +212). **Concentración trimestral** (construida de los mismos bancos que `JLoss`, corr 0,62 con GFDD): β₄ = −0,114 (t = −2,75, el más negativo), IC90 (−0,144, **+0,013**) — cruza el cero por un margen mínimo. La variación temporal real no rescata la predicción; si acaso refuerza que el signo empírico es negativo. |

Números canónicos completos y trazables:
[`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md).
Batería de robustez de árbitro: [`1_Codigo/Panel/bbg/p5_robustez_arbitro.py`](1_Codigo/Panel/bbg/p5_robustez_arbitro.py).

### Fronteras y limitaciones del resultado

Lo que la evidencia **respalda** es el **signo y la forma** de la complementariedad, no una
magnitud puntual. Las fronteras honestas:

- **Restricción de exclusión del IV (H1).** El efecto causal de nivel `JLoss → spread` se
  apoya en un instrumento cuya validez no se puede verificar directamente. El *shift-share*
  con el spread de liquidez de fondeo bancario es fuerte (F = 21,6) y significativo
  (p = 0,001), pero un **segundo** instrumento igualmente fuerte —el choque del dólar
  efectivo amplio (BIS)— no corrobora la magnitud al usarse solo, y la especificación
  sobre-identificada con ambos **rechaza el test de Sargan (p = 0,003)**: los dos
  instrumentos no identifican el mismo parámetro, luego al menos uno viola la exclusión. Se
  reporta el de mejor argumento de exclusión (opera sobre el costo de fondeo bancario, no
  sobre el soberano directamente) como el más creíble, pero **el efecto de nivel no está
  causalmente cerrado**. El capítulo teórico hereda la misma dificultad: su estrategia de
  instrumentos de competencia se anuncia pero no se implementa.
- **Significancia marginal de θ:** p ≈ 0,05 bajo las tres formas de inferencia principales.
- **Identificación acotada:** regularidad post-GFC (no antes de 2012) y sostenida por pocos
  países con variación real de `JLoss` (sin China deja de ser significativa).
- **`JLoss` ordinal, no cardinal:** la censura de la malla de pérdidas comprime el nivel
  ×2,8 (el signo y la inferencia se preservan; la magnitud en niveles no es interpretable).
- **Regresores generados:** `JLoss` y `GaR` son estimados; la inferencia que los trata como
  datos subestima la varianza de θ (el sesgo de medición atenúa, así que θ es un límite
  conservador).
- **H4b sin identificar** con ninguno de los tres proxies de concentración, incluida la
  serie trimestral construida para este propósito.

---

## Reproducir

Entorno: Python con `pandas`, `numpy`, `scipy`, `linearmodels`, `matplotlib`
(`1_Codigo/JLoss_reconstruction/JLoss-pipeline/venv` para el motor JLoss; `.venv` del proyecto
para las regresiones). Requiere acceso de red para IMF WEO / World Bank / GFDD.

```bash
# 1. JLoss desde Bloomberg (una vez extraídos los CSV crudos a Bloomberg_extraction/output/)
cd 1_Codigo/JLoss_reconstruction
mkdir -p _stage && for d in ../Bloomberg_extraction/output/*/; do c=$(basename "$d"); \
  cp "$d/balance_$c.csv" "$d/mktcap_$c.csv" _stage/; done
JLoss-pipeline/venv/Scripts/python.exe jloss_engine.py --indir _stage \
  --out jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv && rm -rf _stage

# 2. Panel + análisis (desde 1_Codigo/Panel/)
python bbg/p0_controles_all.py     # controles domésticos, todos los países
python bbg/p1_build_panels.py      # -> bbg/Panel_bloomberg.csv, panel_real_bbg.csv, cobertura
python bbg/p2_regresiones.py       # theta (M1/M2/M3), robustez, umbral, efecto marginal
python bbg/p6_concentracion_trimestral.py  # -> concentracion_trimestral_bbg.csv (HHI_q)
python bbg/p7_iv_dolar_bis.py      # instrumento dólar BIS -> usd_neer_bbg.csv (red: stats.bis.org)
python bbg/p3_causal_fase5.py      # batería causal (IV reforzado) + H4a/H4b (3 proxies de HHI)
python bbg/p5_robustez_arbitro.py  # ventanas móviles, placebo, país influyente, regresor generado, GMM
python bbg/p4_figuras.py           # figuras -> bbg/figuras/ (se copian a 4_Redaccion/tesis/imagenes/)

# 2b. Robustez a la censura del grid de JLoss (opcional, ~40 min de motor)
cd ../JLoss_reconstruction && python _engine_wide.py    # -> Panel_JLoss_wide.csv (grid [0.01,0.20])
cd ../Panel && python bbg/_robustez_widebounds.py       # -> robustez_widebounds_bbg.csv

# 3. Documento de tesis (desde 4_Redaccion/tesis/)
latexmk -pdf main.tex             # -> main.pdf, 80 pp, compila sin warnings
```

---

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
| `Concentración trimestral + IV reforzado` | `HHI_q` de los mismos bancos que `JLoss` (H4b sigue no identificado, margen mínimo); IV con exposición pre-2012 pasa de F≈9,5 a F=21,6 (p=0,001); segundo instrumento (dólar BIS) rechaza Sargan al combinarse |
