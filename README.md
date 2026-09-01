# Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano en economías emergentes

Tesis de Magíster en Economía Aplicada (Universidad de Chile). Investiga por qué la
**coincidencia** de fragilidad bancaria sistémica y riesgo a la baja del crecimiento amplifica
el spread soberano de las economías emergentes por encima de la suma de sus efectos
individuales, desde dos aristas:

- **Capítulo empírico** — estima el término de interacción `JLoss × GaR` sobre el spread
  soberano (**EMBI Global Diversified**, siguiendo a Chari et al. 2024) en un panel de
  economías emergentes.
- **Capítulo teórico (organización industrial)** — modelo de competencia bancaria à la Cournot
  del que esa complementariedad es una predicción de primer orden, con una predicción
  distintiva adicional: la amplificación por concentración bancaria.

> **Estado a 2026-09-02.** La variable dependiente del capítulo empírico es el **EMBI Global
> Diversified** (como en Chari et al. 2024); el CDS soberano 5Y queda como serie de robustez.
> Hungría sale del panel por el mismo criterio de bancos mínimos que ya excluía a Bulgaria.
> **Panel de 13 países.** Documento de tesis compilado y limpio:
> [`4_Redaccion/tesis/main.pdf`](4_Redaccion/tesis/main.pdf) (82 pp). Los dos capítulos se
> preparan además como envíos separados a revista — ver
> [`4_Redaccion/envios/`](4_Redaccion/envios/).

---

## Estado de la investigación

### Datos — un solo panel, fuente homogénea

| Insumo | Fuente | Cobertura efectiva |
|---|---|---|
| **JLoss** (fragilidad, motor de punto de silla / Merton–KMV) | Bloomberg: balances + capitalización bursátil de 113 bancos | 20 economías, 2004–2026 |
| **Spread soberano** | **EMBI Global Diversified (J.P. Morgan)**, principal; CDS soberano 5Y USD de Bloomberg, robustez | 9 países con historia continua + 4 parciales |
| **GaR** (riesgo de cola, regresión cuantílica de panel, marco CEMLA) | insumos FCI de estadísticas nacionales (Bloomberg no publica cuentas nacionales) | 17 economías |
| **Controles domésticos** (deuda, fiscal, reservas, CA, inflación, REER) | IMF WEO + World Bank + BIS, para **todos** los países del panel | — |
| **HHI** (concentración bancaria) | World Bank GFDD + serie trimestral de bancos Bloomberg | — |

**Muestra de estimación:** 13 países, N = 721 (M1) / 614 (M2) observaciones trimestrales.
**Exclusiones (3), por JLoss no válido a nivel país — bancos cotizados insuficientes:** Corea
del Sur (*Korea discount* → Merton lee incumplimiento inminente), Bulgaria (un solo banco
cotizado) y **Hungría** (2 bancos, `below_min_banks` en 89/89 trimestres). Ver
[`1_Codigo/Panel/bbg/DIAGNOSTICO_COREA.md`](1_Codigo/Panel/bbg/DIAGNOSTICO_COREA.md).

### Resultados principales

| Hipótesis | Resultado |
|---|---|
| **H1** — nivel: `JLoss → spread` | **Respaldada** por MCO con efectos fijos (β₁ = +2,8, t = 2,7) y proyecciones locales (+4,6 pb, t = 2,9, pico en h = 1). El IV *shift-share* sobre el panel de 13 países es más débil que en la versión con CDS (F ≈ 11, 2ª etapa no significativa); un 2º instrumento da signo opuesto y Sargan rechaza. **El canal causal de nivel no está cerrado por IV.** |
| **H2** — nivel: `GaR → spread` | Respaldada — β₂ = −4,3 (t = −2,3): un `GaR` más negativo se asocia con mayor spread. |
| **H3 / complementariedad** — θ (interacción `JLoss × GaR`) < 0 | **Condicional.** Sobre la muestra completa de 13 países, θ = −0,16 (**no significativo**, p = 0,26; wild boot 0,14). **No es la métrica del spread:** EMBI y CDS dan el mismo θ (≈ −0,7, p ≈ 0,05) sobre la misma submuestra. Es la **composición de la muestra**. |
| **Heterogeneidad — el hallazgo central** | En el **núcleo de 11 economías emergentes de financiamiento externo**, θ = **−0,47** (t = −2,29, **p = 0,023**; wild boot 0,015). Se diluye al añadir Polonia e India (mercados de deuda local profundos). La diferencia de grupo no es significativa (p = 0,23) — solo 2 países en el grupo de contraste. El modelo de umbral de Hansen corrobora la no linealidad (+5,9 vs +2,0 pb por régimen, LR = 27). |
| **Frontera temporal** | Fenómeno **pre-pandemia**: θ base = −1,0 (p = 0,057), el término post-2020 (+1,0) lo compensa. Negativo y significativo en la ventana móvil 2012–2016. |
| **H4a** — β₃ (parametrización directa de la triple interacción) | Signo **contrario** al predicho, no significativo. Sólo el θ de nivel sin HHI recupera el signo del modelo. |
| **H4b** — amplificación por concentración | **No identificada** con ninguno de tres proxies de HHI (estructural, anual, trimestral). El punto estimado no tiene signo estable entre proxies; el bootstrap de bloques cruza el cero holgadamente con todos. |

Números canónicos completos y trazables:
[`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md).
Batería de robustez de árbitro: [`1_Codigo/Panel/bbg/p5_robustez_arbitro.py`](1_Codigo/Panel/bbg/p5_robustez_arbitro.py).

### Fronteras y limitaciones del resultado

Lo que la evidencia **respalda con solidez** son los canales de **nivel** (H1, H2). La
complementariedad (H3) es **condicional** — significativa en el núcleo de economías de
financiamiento externo, no en el conjunto del panel. Las fronteras honestas:

- **La complementariedad no es significativa sobre la muestra completa** (θ = −0,16, p = 0,26).
  Solo lo es sobre el núcleo de 11 economías de financiamiento externo (θ = −0,47, p = 0,023);
  con solo 2 economías (Polonia, India) en el grupo de contraste, la diferencia entre grupos
  no alcanza un contraste estadístico formal (p = 0,23).
- **Identificación temporal acotada:** fenómeno pre-pandemia; la señal se concentra en la
  ventana 2012–2016.
- **Corte transversal efectivo:** 9 de 13 países casi no tienen variación de `JLoss`; sin
  China θ cae a −0,05.
- **Identificación causal de nivel no cerrada por IV** sobre esta muestra reducida (F ≈ 11,
  2ª etapa n.s.; 2º instrumento con signo opuesto; Sargan rechaza). H1 se apoya en MCO con
  efectos fijos y proyecciones locales.
- **`JLoss` ordinal, no cardinal:** la censura de la malla de pérdidas satura el VaR99 en el
  ~98 % de las observaciones; se interpreta como ranking de fragilidad relativa.
- **Regresores generados:** `JLoss` y `GaR` son estimados; la inferencia que los trata como
  datos subestima la varianza de θ (el sesgo de medición atenúa, así que θ es un límite
  conservador).
- **Controles domésticos interpolados de series anuales:** sus coeficientes bajo FE
  bidireccionales no tienen signo económico fiable; se incluyen como controles, no se
  interpretan.
- **H4b sin identificar** con ninguno de los tres proxies de concentración.

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
latexmk -pdf main.tex             # -> main.pdf, 82 pp, compila sin warnings
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
| `Concentración trimestral + IV reforzado` | `HHI_q` de los mismos bancos que `JLoss` (H4b sigue no identificado); IV con exposición pre-2012 |
| `Reestructura el panel: EMBI como variable dependiente principal, CDS a robustez` | Variable dependiente = EMBI Global Diversified (Chari et al. 2024); CDS a robustez; el θ marginal negativo era específico del CDS |
| `Excluye Hungría; sección de heterogeneidad núcleo/convergencia` | Hungría fuera (2 bancos, `below_min` 89/89, mismo criterio que Bulgaria); panel de 13 países; hallazgo central pasa a ser la heterogeneidad: θ = −0,47 (p = 0,023) en el núcleo de 11 EM de financiamiento externo, no significativo al añadir Polonia e India; EMBI vs CDS dan el mismo θ sobre la misma submuestra |
