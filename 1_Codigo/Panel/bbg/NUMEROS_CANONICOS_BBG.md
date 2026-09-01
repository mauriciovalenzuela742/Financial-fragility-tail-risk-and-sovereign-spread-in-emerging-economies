# Números canónicos — panel único anclado en Bloomberg

*Generado el 2026-08-31 (v3, panel único, 14 países) re-ejecutando `1_Codigo/Panel/bbg/p0..p4`.
Fuente de verdad para toda prosa de la tesis. Sustituye a la versión de dos bases y a
`1_Codigo/Panel/NUMEROS_CANONICOS.md` (v8 regulatorio).*

**Regla de uso:** ningún coeficiente entra a la prosa sin trazarse a una fila de este documento.

---

## 0. Diseño

**Un solo panel.** No hay partición "núcleo LatAm / panel ampliado". El panel incluye *todas*
las economías con `JLoss` disponible; la variable dependiente es el **CDS soberano 5Y de
Bloomberg y solo eso** — donde no hay CDS la celda queda vacía (no se rellena con EMBI de
bonos ni proxies).

| Insumo | Fuente |
|---|---|
| JLoss (motor de punto de silla) | Bloomberg (balances + capitalización bursátil, 113 bancos) |
| Spread soberano | Bloomberg CDS 5Y USD |
| VIX, UST10Y, US HY OAS | Bloomberg |
| GaR | regresión cuantílica CEMLA; FCI = estadísticas nacionales (Anexo B) |
| Controles domésticos (6, **todos los países**) | IMF WEO (`GGXWDG_NGDP`, `GGXCNL_NGDP`), World Bank (`BN.CAB.XOKA.GD.ZS`, `FI.RES.TOTL.CD`), CPI/REER de `GaR/individuals/` |
| HHI | World Bank GFDD `GFDD.OI.01` |

**Exclusiones (2), por `JLoss` no válido a nivel país — no por dato faltante:**
- **southkorea**: E/D mercado ≈ 0,04 (*Korea discount*), Merton PD ≈ 0,55, JLoss 25–47.
- **bulgaria**: 1 banco cotizado (FIBank), 76/76 trimestres `below_min_banks`, JLoss mediana 29.

**Roster: 18 economías. Muestra de estimación (CDS + JLoss + GaR): 838 obs, 14 países.**

| Aporte | Países | n_est |
|---|---|---|
| CDS continuo 2004–2026 | southafrica (89), philippines (89), indonesia (86), china (79), mexico (77), brazil (75), chile (75), colombia (70), peru (66), turkey (63), malaysia (40) | 819 |
| CDS solo 2012Q3–2015Q4 | hungary (14), poland (14) | 28 |
| CDS ~1 trimestre | pakistan (1) | 1 |
| En el roster, sin aporte | argentina/egypt/russia (sin GaR), india (sin CDS) | 0 |

Descriptivos (muestra de estimación, N=838, 14 países):

| Variable | Media | Desv. | Mín | Máx |
|---|---:|---:|---:|---:|
| CDS soberano 5Y (pb) | 148,6 | 101,8 | 11 | 780 |
| JLoss | 4,13 | 4,06 | 1,43 | 28,97 |
| GaR (q05, fracción; más negativo = más riesgo) | +0,014 | 0,039 | −0,228 | +0,140 |
| GaR_pp (pp) | +1,42 | 3,90 | −22,8 | +14,0 |
| ES (Expected Shortfall, fracción) | +0,007 | 0,041 | −0,245 | +0,120 |
| deuda gob. gral./PIB (%) | 46 | 20 | | |
| balance fiscal/PIB (%) | −3,0 | 2,3 | | |
| reservas/PIB (%) | 19 | 9 | | |
| CA/PIB (%) | −1,1 | 3,0 | | |
| inflación YoY (%) | 5,6 | 8,4 | | |

**JLoss — estructura transversal (clave para la identificación de θ y β4):** la mediana por
país va de 2,18 (Perú) a 11,58 (Pakistán), pero **9 de 14 países se agrupan en 2,2–2,6**; la
variación entre países la aportan sobre todo Pakistán (11,6), Turquía (6,0), Brasil (4,0) y
China (3,8). sd transversal ≈4 (vs 8,3 en la reconstrucción regulatoria v8).

**Censura del VaR99 (verificado 2026-09-01, `_diag_censura.py`, 6 países):** el grid de
pérdidas del motor es `[0,010, 0,048]` de la exposición y `find_var99` interpola "sin
extrapolación". El VaR99 **se clipa a 0,048 en el 98,3 % de los país-trimestre** (p50 = p90 =
p99 = max = 0,0480). Es decir: la componente de pérdida inesperada (UL) de JLoss se evalúa
en un nivel de estrés **fijo** (4,8 % de la exposición) para casi todas las observaciones, no
en el verdadero percentil 99. Consecuencias: (i) la variación transversal de JLoss la manda
la **pérdida esperada** (EL, diferencias de PD de Merton), no la forma de la cola; (ii) la
cola sistémica está comprimida por arriba — coherente con el sd transversal bajo y con que
H4b (que necesita variación de forma de cola × concentración) no se identifique; (iii) es la
calibración declarada como "consistente con Chari et al." — no un error de la reconstrucción
Bloomberg.

**Robustez grid ancho — VERIFICADA sobre los 14 países de estimación (2026-09-01,
`_engine_wide.py` + splice, `Panel_JLoss_wide.csv`):** con grid `[0,01, 0,20]` en vez de
`[0,01, 0,048]`, JLoss sube **~2,8×** de forma heterogénea entre países, `corr(base, wide) =
0,919` (838 obs). Re-estimando θ con esa serie corregida:

| Spec | θ base | t | p | θ WIDE | t | p |
|---|---:|---:|---:|---:|---:|---:|
| M1 | −0,543 | −2,20 | 0,028 | **−0,572** | **−2,57** | **0,010** |
| M2 | −0,354 | −1,91 | 0,056 | **−0,330** | **−2,15** | **0,032** |

> **θ NO se reduce con el grid ancho** (contra lo que sugeriría un reescalado uniforme): el
> factor de escala varía entre países, y tras la transformación \textit{within} + centrado el
> coeficiente **conserva su magnitud y GANA precisión** (M2: p 0,056 → 0,032; M1: 0,028 →
> 0,010). La censura de la cola, de haber sesgado algo, **sesgaba en contra del hallazgo**.
> Los resultados de la tesis se reportan sobre la calibración base (Chari et al.); la serie
> ancha es una robustez. JLoss se interpreta **ordinalmente**, no en niveles.

---

## 1. Mecanismo central: θ = JLoss × GaR sobre el CDS soberano

`CDS = α_i + γ_t + β1·JLoss_c + β2·GaR_pp_c + θ·(JLoss_c×GaR_pp_c) + X + ε`, JLoss y GaR (pp)
centradas, errores Driscoll–Kraay (kernel Bartlett), `linearmodels.PanelOLS`.

| Spec | N | θ | t (DK) | p (DK) | p (wild boot) |
|---|---:|---:|---:|---:|---:|
| M1 — FE país+tiempo, sin controles | 838 | **−0,543** | −2,20 | 0,028 | 0,127 |
| **M2 — FE país+tiempo, + 6 controles** | **738** | **−0,354** | **−1,91** | **0,056** | **0,035** |
| M3 — FE país + factores globales explícitos (sin FE tiempo) | 738 | −0,339 | −1,65 | 0,100 | 0,039 |
| M2, errores cluster país | 738 | −0,354 | −3,39 | **0,001** | — |
| M2, errores cluster tiempo | 738 | −0,354 | −2,27 | **0,023** | — |

> **Número central (M2): θ = −0,354 (N=738, 13 países — Pakistán aporta 1 obs y se pierde en
> M2). Significancia marginal bajo DK (p=0,056) y bajo wild bootstrap (p=0,035); convencional
> bajo clustering por país (p=0,001) y tiempo (p=0,023).** Signo robusto a la especificación.
> R²_within = 0,18.

**Coeficientes de los 6 controles en M2** (verificado 2026-08-31; DK):
deuda gobierno general/PIB **+2,32 (t=4,54)**, inflación interanual **+3,04 (t=2,71)**,
REER **−2,52 (t=−6,81)** — los tres con el signo esperado y significativos; balance
fiscal/PIB −1,06 (n.s.), reservas/PIB −0,53 (n.s.) — signo esperado, no significativos;
CA/PIB +1,03 (n.s.) — único signo contraintuitivo, no significativo.

---

## 2. Robustez

| Caso | N | θ | t |
|---|---:|---:|---:|
| **pre-2020 (< 2020Q1)** | 529 | **−0,388** | **−1,02** |
| solo 2020–2026 | 209 | −0,245 | −1,81 |
| sin 2020–2021 (mantiene pre-2020 + 2022+) | 650 | −1,109 | −3,53 |
| cola = Expected Shortfall | 738 | −0,390 | −2,10 |
| **JLoss malla ancha [0,01, 0,20]** (corrige censura del VaR99) | 738 | **−0,330** | **−2,15** (p=0,032) |
| sin deuda/PIB (5 controles) | 738 | −0,335 | −2,49 |
| leave-one-country-out: rango de θ | — | [−0,41 (sin Turquía), −0,17 (sin China)] | todos < 0 |

> **Hallazgo prominente (decisión de estructura): la interacción no se identifica antes de
> 2020** (θ = −0,39 pero t = −1,02: conserva el signo, no se distingue de cero). Se identifica
> en 2020–2026 y, sobre todo, en el tramo 2022–2026 (ciclo de alzas de tasas): excluyendo solo
> 2020–2021 la interacción se intensifica a θ = −1,11 (t = −3,53). Leave-one-out: θ negativo en
> las 14 submuestras; más influyentes China (−0,17, t=−1,33) y Sudáfrica (−0,36, t=−1,39).

---

## 3. Efecto marginal ∂CDS/∂JLoss (M2)

| Percentil de GaR | ∂CDS/∂JLoss (pb/unidad) | se |
|---|---:|---:|
| p10 (cola severa) | +4,58 | 1,33 |
| p50 | +3,11 | 1,22 |
| p90 (benigno) | +1,84 | 1,48 |

Monótono decreciente en GaR; la banda IC90 excluye el cero en el tramo de cola severa.

---

## 4. Modelo de umbral de panel (Hansen)

Variable de umbral q = GaR (pp). γ̂ ≈ −0,15 pp. Efecto de JLoss sobre el CDS (pb/unidad):

| Régimen | efecto |
|---|---:|
| cola severa (GaR ≤ γ̂) | **+8,1** |
| benigno (GaR > γ̂) | +2,3 |

LR = 80,0. El efecto de la fragilidad es ~3,5× mayor en el régimen de cola severa.

---

## 5. Identificación causal

| Método | Resultado |
|---|---|
| **Wild cluster bootstrap** (M2, 999 rep., 13 clusters) | θ = −0,354; **p_wildboot = 0,035** |
| **IV shift-share — efecto de NIVEL** (instrumento = `OnOffRun_spread_log` × exposición pre-muestral; 1 endógeno `JLoss_c`) | β_JLoss_IV = **+32,6 pb/unidad**, **p = 0,038**; **F 1ª etapa ≈ 9,5** (límite convencional). Dirección banco→soberano respaldada; primera etapa en el límite ⇒ sugestivo, no concluyente. |
| IV shift-share — interacción (2 endógenos, 2º instrumento débil; "con cautela") | θ_IV = −5,25 (no se usa en prosa como resultado principal) |
| Proyecciones locales (pico régimen severo) | +4,35 pb (se 2,22) en h = 1; sin amplificación dinámica creciente |
| Triple interacción institucional (JxG × WGI) | −0,013 (t = −0,10), n.s. |

---

## 6. Puente OI ↔ datos: H4a y H4b

`CDS = α_i + δ_t + β1·JLoss + β2·D + β3·(JLoss×D) + β4·(JLoss×D×HHI) + …`, D = −GaR.

| HHI | β3 (JLoss×D) | t | **β4 (JLoss×D×HHI)** | t agrup. | P(β4>0) boot bloques | **IC90 boot bloques** | rango LOO |
|---|---:|---:|---:|---:|---:|---|---|
| estructural | +56,3 | +1,72 | **−392** | −2,34 | 12 % | **(−627, +212)** — incluye 0 | [−491, −236] |
| anual | +24,5 | +1,08 | −268 | −2,14 | 30 % | (−387, +345) — incluye 0 | [−286, −45] |

> **H4a (β3 > 0):** signo **opuesto** al predicho, no significativo (+56, t = 1,72). Sólo el θ
> de nivel *sin* HHI (§1) tiene el signo predicho.
> **H4b (β4 > 0): NO identificado.** El t agrupado es −2,34, pero el **bootstrap de bloques por
> país —la inferencia que corresponde con 13 clusters y un HHI casi invariante en el tiempo—
> deja el IC90 cruzando el cero** (P(β4>0) = 12 %). El coeficiente no respalda ni refuta la
> predicción. Contrasta con la versión v8 regulatoria (+721, t = +2,98), de dispersión
> transversal mucho mayor. **La predicción distintiva del modelo de OI no puede contrastarse
> con potencia sobre este panel.** (Redacción de prosa: "no identificado / imprecise", NO
> "significativo en la dirección equivocada".)

Explicación más probable (`paper1_oi.tex` §5.4): la serie JLoss de Bloomberg es
transversalmente comprimida (sd ≈4 vs 8,3), y la triple interacción necesita la dispersión
entre países de la fragilidad que la homogeneización elimina; el HHI del GFDD es además casi
invariante en el tiempo.

---

## 7bis. Batería de robustez de árbitro (`p5_robustez_arbitro.py` → `robustez_arbitro_bbg.csv`)

**Invariancia de la cola (M2):** θ = −0,354 con GaR q05 directo (p = 0,056); θ = −0,354 con
GaR skew-t de ABG2019 (p = 0,051); θ = −0,390 con Expected Shortfall (p = 0,036). El resultado
**no depende de la especificación de la primera etapa de GaR**.

**Ventanas móviles de 5 años** (M2, θ del término JLoss×GaR):

| Ventana | θ | t | Lectura |
|---|---:|---:|---|
| 2006–2010 | +1,08 | +0,83 | GFC: positivo, no significativo |
| 2009–2013 | +0,28 | +0,47 | ≈ cero |
| 2012–2016 | **−1,23** | **−3,34** | crisis euro / taper / EM 2015 |
| 2015–2019 | −0,39 | −1,65 | |
| 2018–2022 | −0,17 | −2,15 | |
| 2021–2025 | −0,27 | −3,06 | |

> **Reencuadre temporal (importante):** la complementariedad es un fenómeno **post-GFC**:
> ausente o positiva en 2006–2011, se vuelve negativa y significativa **desde 2012** y es
> estable hasta 2025. El estimador pre-2020 de muestra completa es no significativo (θ = −0,39,
> t = −1,02) **sólo porque promedia la señal post-2012 con el período nulo 2004–2011**. No hay
> quiebre discreto en 2020: al interactuar JLoss×GaR con una dummy post-2020, el término extra
> es +0,46 (t = 0,82, n.s.). La lectura "artefacto de COVID" **no se sostiene**; la correcta es
> "regularidad post-GFC, identificada fuera de tiempos tranquilos".

**Placebo (destruir la estructura de GaR, B = 600):**

| Diseño | θ medio placebo | P(placebo ≤ obs) |
|---|---:|---:|
| A. reshuffle global de GaR (null exacto) | −0,005 | **0,053** |
| B. permutar GaR dentro de país | −0,274 | 0,29 |
| C. intercambiar series GaR entre países | +0,04 | 0,12 |

> El placebo de referencia (A, null exacto) deja el θ observado en el **percentil 5** → p ≈ 0,05,
> consistente con la inferencia analítica. El diseño B "filtra" (θ medio −0,27) porque la
> posición transversal de GaR está correlacionada con la de JLoss y los EF bidireccionales no
> la absorben del todo: **parte de la identificación proviene de covariación entre países, no
> solo de la sincronía intra-país.** (Caveat para prosa.)

**Regresor generado (GaR):** perturbando GaR con ruido N(0, s):

| s (fracción de sd(GaR) = 3,90 pp) | θ medio | P(θ ≥ 0) |
|---|---:|---:|
| 0 % | −0,354 | 0,00 |
| 10 % (0,39 pp) | −0,353 | 0,00 |
| 25 % (0,98 pp) | −0,339 | 0,00 |
| 50 % (1,95 pp) | −0,290 | 0,00 |

> θ es estable a perturbaciones de hasta el 25 % de sd(GaR); a 50 % atenúa a −0,29 (signo
> intacto). El error de medición **atenúa** → el θ verdadero es, si acaso, mayor. **Pendiente:**
> bootstrap que re-estime la regresión cuantílica de GaR por réplica (inviable en este pase por
> costo del LP en ventana expansiva; ~45.000 solves).

**País influyente (M2, DK):**

| Excluye | θ | t | p |
|---|---:|---:|---:|
| — (M2) | −0,354 | −1,91 | 0,056 |
| China | −0,172 | −1,33 | 0,18 |
| Sudáfrica | −0,360 | −1,39 | 0,17 |
| China + Sudáfrica | −0,279 | −1,68 | 0,094 |
| Turquía | −0,410 | −3,25 | 0,001 |
| **Turquía + China** | **−0,068** | **−0,31** | **0,75** |
| Brasil | −0,305 | −1,77 | 0,078 |
| jackknife de 2 países (91 pares) | [−0,49, −0,07] | | 100 % < 0; 75 % con p < 0,10 |

> **Vulnerabilidad principal:** el signo es negativo en las 91 submuestras de 2 países, pero
> **la significancia descansa en China** (y, para el nivel de JLoss, en Turquía y Brasil). El
> diagnóstico por país lo explica: 9 de 13 países tienen JLoss mediana 2,2–2,6 y máximo < 18;
> **China (máx 29), Turquía (máx 28) y Brasil (máx 15,5) aportan casi toda la variación de
> fragilidad.** El θ se identifica de ~4 países con movimiento real de JLoss + los episodios de
> estrés. "14 países" sobreestima el corte transversal efectivo.

**GMM dinámico:** T = 88, N = 13 ⇒ sesgo de Nickell ≈ 1,1 % (despreciable). AB/system-GMM
(diseñado para N grande, T chico) **no es apropiado**; su test de Hansen da p = 1,00
(sobre-identificación no informativa, 100 instrumentos). Devuelve JxG = −0,25 (p ≈ 0,007),
AR(2) p = 0,74 — confirma el signo, sin peso inferencial. La conclusión es que **el estimador
estático de EF bidireccionales es el apropiado** dada la forma del panel.

---

## 7. Resumen para la prosa

- **H1 (nivel, JLoss→CDS):** respaldada — IV shift-share da β_JLoss = +32,6 pb (p = 0,038),
  dirección banco→soberano; primera etapa en el límite (F ≈ 9,5) ⇒ sugestivo, no concluyente.
- **H2 (GaR→CDS):** β2 < 0.
- **H3 (complementariedad, θ < 0):** **signo y forma respaldados** — θ = −0,354, invariante a
  la medida de cola (GaR q05 / skew-t / ES), al efecto marginal y al modelo de umbral.
  Significancia **marginal** (p ≈ 0,056 DK, 0,035 wild boot, 0,051 con GaR skew-t, 0,001 cluster
  país); placebo de null exacto → p ≈ 0,05.
  - **Temporalidad:** fenómeno **post-GFC**, no artefacto de COVID. Positivo/nulo 2006–2011,
    negativo y significativo en todas las ventanas de 5 años que empiezan en 2012+. El pre-2020
    de muestra completa es n.s. sólo por promediar con 2004–2011.
  - **Corte transversal efectivo:** la significancia descansa en **China** (sin China → n.s.;
    sin China+Turquía → θ ≈ 0). 9 de 13 países casi no tienen variación de JLoss.
  - **Regresor generado:** θ estable a perturbar GaR hasta 25 % de su sd; el sesgo de medición
    atenúa. Bootstrap completo de 1ª etapa pendiente.
- **H4a (β3 > 0):** signo opuesto al predicho, no significativo.
- **H4b (β4 > 0):** **no identificado** — el bootstrap de bloques por país deja el IC90
  cruzando el cero. No se afirma dirección.
