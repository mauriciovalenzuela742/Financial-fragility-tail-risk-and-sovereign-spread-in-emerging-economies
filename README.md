# Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano en economías emergentes

Tesis de Magíster en Economía Aplicada (Universidad de Chile). Investiga por qué la
**coincidencia** de fragilidad bancaria sistémica y riesgo a la baja del crecimiento amplifica
el spread soberano de las economías emergentes por encima de la suma de sus efectos
individuales, desde dos aristas:

- **Capítulo empírico** — estima el término de interacción $JLoss \times GaR$ sobre el CDS
  soberano en un panel de economías emergentes.
- **Capítulo teórico (organización industrial)** — modelo de competencia bancaria à la Cournot
  del que esa complementariedad es una predicción de primer orden, con una predicción
  distintiva adicional: la amplificación por concentración bancaria.

> **Estado a 2026-08-31.** Toda la evidencia empírica está reanclada en datos de **Bloomberg**
> y estructurada como **una sola investigación sobre un único panel**. Documento de tesis
> compilado y limpio: [`4_Redaccion/tesis/main.pdf`](4_Redaccion/tesis/main.pdf) (74 pp).

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
| **H1** — nivel: $JLoss \to$ spread | Plausible; IV *shift-share* débil-a-límite ($F \approx 9{,}5$). |
| **H3 / complementariedad** — $\theta$ (interacción $JLoss \times GaR$) $< 0$ | **Signo y forma respaldados** — $\hat\theta = -0{,}35$; efecto marginal de la fragilidad creciente a medida que empeora el riesgo de cola; modelo de umbral de Hansen lo corrobora ($+8{,}1$ vs $+2{,}3$ pb por régimen). Significancia **marginal**: $p = 0{,}056$ (Driscoll–Kraay), $0{,}035$ (*wild cluster bootstrap*), $0{,}001$ (*cluster* por país). |
| **Frontera temporal** | La interacción **no se identifica antes de 2020** ($t = -1{,}02$); descansa en los episodios de estrés macrofinanciero recientes. |
| **H4a** — $\beta_3 > 0$ (parametrización directa de la triple interacción) | Signo predicho, no significativo. |
| **H4b** — $\beta_4 > 0$: amplificación por concentración | **Rechazada** — $\hat\beta_4 = -392$ ($t = -2{,}34$): signo contrario al predicho y significativo en esa dirección. Contrasta con la reconstrucción previa con datos regulatorios ($+721$); la explicación más probable es que homogeneizar la métrica de fragilidad comprime la dispersión transversal sobre la que se identifica ese término. |

Números canónicos completos y trazables:
[`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md).

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
python bbg/p3_causal_fase5.py      # batería causal + H4a/H4b
python bbg/p4_figuras.py           # figuras -> bbg/figuras/ (se copian a 4_Redaccion/tesis/imagenes/)

# 3. Documento de tesis (desde 4_Redaccion/tesis/)
latexmk -pdf main.tex             # -> main.pdf, 74 pp, compila sin warnings
```

---

## Estructura del repositorio

```
1_Codigo/
  Bloomberg_extraction/     Extracción xbbg de balances, mktcap y macro (20 países)
  JLoss_reconstruction/     Motor JLoss (jloss_engine.py) + salida jloss_bloomberg/
  GaR/                      Growth-at-Risk: motor CEMLA, FCI, insumos por país
  Panel/
    bbg/                    ← PIPELINE VIGENTE: p0..p4, panel único, números canónicos
    (legado)               construcción "dos bases" previa, notebooks EDA, análisis causal
  Stata_Sov_Risk/  v0/      Análisis predecesores (legado, no vigente)
2_Datos/                    Datos sueltos y paquetes portátiles
3_Marco_teorico/            Literatura de referencia (PDF)
4_Redaccion/
  tesis/                    ← TESIS VIGENTE: main.tex + capítulos + anexos (A matemático, B datos)
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
