# Números canónicos — panel único anclado en Bloomberg

*Generado el 2026-08-31, reestructurado 2026-09-01 (variable dependiente = EMBI) y
2026-09-02 (Hungría excluida por `below_min_banks`; 13 países). Re-ejecutando
`1_Codigo/Panel/bbg/p1..p7`. Fuente de verdad para toda prosa de la tesis. Sustituye a la
versión de dos bases y a `1_Codigo/Panel/NUMEROS_CANONICOS.md` (v8 regulatorio).*

**Regla de uso:** ningún coeficiente entra a la prosa sin trazarse a una fila de este documento.

---

## ★ DISEÑO VIGENTE (2026-09-02): DV = EMBI, 13 países, CDS a robustez

**Variable dependiente principal: spread EMBI Global Diversified (J.P. Morgan), en pb**, como
en Chari et al. (2024). Fuente: `2_Datos/embi.xlsx` (diario 2000–2026). El CDS soberano 5Y de
Bloomberg queda como serie de **robustez**.

**Exclusiones (3), por `JLoss` no válido a nivel país — no por dato faltante:**
- **southkorea**: E/D de mercado ≈ 0,04 (*Korea discount*), Merton PD ≈ 0,55, JLoss 25–47.
- **bulgaria**: 1 banco cotizado (FIBank), 76/76 trimestres `below_min_banks`, JLoss mediana 29.
- **hungary** *(nuevo)*: mediana 2 bancos cotizados (OTP dominante), `below_min_banks` en
  **89/89 trimestres** — mismo criterio que Bulgaria. Antes entraba porque el EMBI le daba
  serie larga (89 trim.), pero su JLoss no es una medida sistémica de país.

**Muestra de estimación (EMBI + JLoss + GaR): N = 721 (M1) / N = 614 (M2), 13 países.**
`brazil, chile, china, colombia, india, indonesia, malaysia, mexico, peru, philippines,
poland, southafrica, turkey`. Cobertura: 9 países con EMBI continuo desde 2004–2010;
`india` 54 trim. (EMBI desde 2012Q4); `indonesia/philippines/southafrica` 11 trim. cada uno
(EMBI desde 2023Q3, aunque su CDS es largo).

---

### ★ BATERÍA DE REGRESIONES (esqueleto del Cap. 2) — `p8_bateria_regresiones.py` → `bateria_bbg.csv`

Estilo Chari et al.: 4 modelos anidados (M1 JLoss; M2 GaR; M3 ambos; M4 + interacción)
× 3 efectos fijos (T = tiempo; P = país; PT = país+tiempo) × 2 muestras. Sin controles.
Errores Driscoll–Kraay. Tabla 2.3 de la tesis (apaisada).

**Panel A — muestra completa (N = 721, 13 países)**

| coef | M1/T | M1/P | M1/PT | M2/T | M2/P | M2/PT | M3/T | M3/P | M3/PT | M4/T | M4/P | M4/PT |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| JLoss | +7,4*** | +8,1*** | +5,0*** | | | | +8,5*** | +6,1*** | +4,6*** | +8,5*** | +6,1*** | +4,6*** |
| GaR   | | | | −7,9*** | −9,1*** | −5,7* | −10,1*** | −6,0*** | −3,8 | −10,1*** | −5,6*** | −3,6 |
| JLoss×GaR | | | | | | | | | | **−0,08** | **−0,16** | **−0,14** |
| (t interacción) | | | | | | | | | | (−0,2) | (−0,7) | (−0,6) |
| R²within | 0,20 | 0,21 | 0,18 | 0,17 | 0,17 | 0,15 | 0,19 | 0,27 | 0,25 | 0,19 | 0,27 | 0,25 |

**Panel B — sin trimestres de crisis (N = 610; excluye 2008Q4–2009Q4 y 2020Q1–2021Q4)**

| coef | M1/T | M1/P | M1/PT | M2/T | M2/P | M2/PT | M3/T | M3/P | M3/PT | M4/T | M4/P | M4/PT |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| JLoss | +6,7*** | +7,0*** | +4,6*** | | | | +8,1*** | +5,1*** | +3,8*** | +8,3*** | +5,5*** | +4,3*** |
| GaR   | | | | −9,2*** | −10,5*** | −9,1*** | −11,2*** | −7,3*** | −7,2** | −10,8*** | −6,8*** | −6,0** |
| **JLoss×GaR** | | | | | | | | | | **−1,72*** ** | **−1,18*** ** | **−1,19*** ** |
| (t interacción) | | | | | | | | | | (−4,4) | (−4,2) | (−3,5) |
| R²within | 0,15 | 0,15 | 0,13 | 0,13 | 0,14 | 0,13 | 0,14 | 0,20 | 0,20 | 0,17 | 0,24 | 0,23 |

**Lecturas:**
1. **H1 (JLoss → EMBI):** +4,6 a +8,5 pb, *** en las 12 columnas de cada panel. Robusto a modelo y a efectos fijos; la magnitud decrece de forma ordenada al añadir FE.
2. **H2 (GaR → EMBI):** negativo, *** con FE de tiempo o de país; marginal (t≈−1,2) sólo con FE bidireccionales en muestra completa; recupera significancia sin crisis.
3. **H3 (interacción):** −0,08 a −0,16 (**n.s.**) en la muestra completa bajo cualquier FE; **−1,19 (PT) a −1,72 (T), todos *** ** sin los trimestres de crisis.

**Inferencia de la interacción M4/PT:**

| muestra | θ | DK p | cluster país p | cluster tiempo p | wild boot p | N |
|---|---:|---:|---:|---:|---:|---:|
| completa | −0,136 | 0,569 | 0,661 | 0,384 | 0,669 | 721 |
| sin crisis (GFC+COVID) | **−1,190** | **0,0004** | **0,015** | **0,0004** | 0,127 | 610 |
| sin COVID solo | −0,806 | 0,039 | — | — | — | 641 |
| sin GFC solo | −0,195 | 0,459 | — | — | — | 690 |

> COVID hace la mayor parte del enmascaramiento; sacar ambas crisis da el resultado más limpio.
> Bajo *wild cluster bootstrap* (13 clusters) la dimensión temporal queda marginal (p = 0,13);
> la dimensión transversal (núcleo, p_wb = 0,015) sí sobrevive.

**Combinando ambas dimensiones (M2 + 6 controles):**
- Sin crisis: θ = −0,687 (t = −1,94, p = 0,053, N = 519)
- Núcleo 11 EM **y** sin crisis: **θ = −0,938 (t = −2,94, p = 0,0035, N = 405)**

**Lectura económica unificada:** la complementariedad aparece cuando el mercado espera que el
pasivo contingente bancario recaiga sobre un soberano **no respaldado**, cuya deuda se fija al
margen por inversores de cartera extranjeros sensibles al riesgo. No ocurre (i) donde la deuda
la tienen inversores domésticos de horizonte largo (Polonia, India), ni (ii) en las crisis con
líneas de swap de la Fed, financiamiento del FMI y compras de bancos centrales domésticos.

---

### Resultado central — H3 (θ = JLoss × GaR)

| Spec | N | θ | t (DK) | p (DK) | p (wild boot) |
|---|---:|---:|---:|---:|---:|
| M1 — FE país+tiempo, sin controles | 721 | −0,136 | −0,57 | 0,569 | 0,669 |
| **M2 — FE país+tiempo, + 6 controles** | **614** | **−0,160** | **−1,13** | **0,258** | **0,138** |
| M3 — FE país + factores globales (sin FE tiempo) | 614 | +0,019 | +0,20 | 0,840 | 0,111 |
| M2, cluster país | 614 | −0,160 | −1,43 | 0,153 | — |
| M2, cluster tiempo | 614 | −0,160 | −1,53 | 0,126 | — |
| M2, cola = Expected Shortfall | 614 | −0,185 | −1,33 | 0,184 | — |
| M2, cola = GaR skew-t (ABG2019) | 614 | −0,155 | −1,11 | 0,268 | — |
| **robustez: DV = CDS 5Y (M2)** | 724 | **−0,380** | **−2,00** | **0,046** | — |
| robustez: DV = CDS 5Y (M1) | 824 | −0,553 | −2,23 | 0,026 | — |

> **En la muestra completa de 13 países, θ es negativo pero no significativo** (M2: −0,160,
> p = 0,26; wild boot p = 0,14). β1 (nivel de JLoss) = **+2,79 (t = +2,74)** y β2 (GaR) =
> **−4,33 (t = −2,25)**: los efectos de primer orden sí se identifican. La interacción, no.

### EMBI vs CDS: la elección de la métrica NO cambia el resultado

En la **muestra común** (mismos 606 país-trimestre con EMBI y CDS disponibles, único cambio =
la variable dependiente), M1 sin controles:

| DV | θ | t | p |
|---|---:|---:|---:|
| EMBI | −0,655 | −2,00 | 0,046 |
| CDS  | −0,763 | −1,98 | 0,048 |

Correlación EMBI–CDS en el panel = **0,86**. **El EMBI da el mismo θ que el CDS cuando la
muestra es idéntica.** Lo que mueve el resultado entre el panel de CDS (θ = −0,35, p = 0,056)
y el de EMBI de 13 países (θ = −0,16) es la **composición de la muestra**: el CDS de
Bloomberg venía truncado para Polonia (2012Q3–2015Q4, 14 trim.) y ausente para India,
mientras el EMBI les da 89 y 54 trimestres.

### Heterogeneidad: núcleo de EM de financiamiento externo vs. Polonia + India

`p5_robustez_arbitro.py`, bloque 2b. Polonia e India tienen mercados de deuda local profundos
y baja dependencia de flujos de cartera externos.

| Spec | θ | t | p | N |
|---|---:|---:|---:|---:|
| **M2 re-estimado solo en el núcleo (11 EM)** | **−0,472** | **−2,29** | **0,023** | 479 |
| interacción de grupo: θ del núcleo | −0,476 | −2,13 | 0,034 | 614 |
| interacción de grupo: diferencia Polonia+India | +0,364 | +1,20 | 0,229 | 614 |
| interacción de grupo: θ Polonia+India (neto) | −0,112 | — | — | 614 |
| wild bootstrap, núcleo 11 | — | — | **0,015** | 479 |
| jackknife de 2 países (78 pares) | [−0,47, +0,06] | — | 99 % < 0; 18 % con p<0,10 | — |
| sin Polonia | −0,285 | −1,88 | 0,060 | 529 |
| sin China | −0,048 | −0,38 | 0,704 | 538 |

> **La complementariedad se identifica en el núcleo de 11 EM de alto rendimiento**
> (θ = −0,47, p = 0,023; wild boot p = 0,015) **y se diluye al añadir Polonia e India**. El
> punto estimado del grupo Polonia+India es ≈ 0 (−0,11), pero la diferencia de grupo no es
> estadísticamente significativa (p = 0,23) — con solo 2 países en ese grupo no puede serlo.
> Lectura honesta: **heterogeneidad de régimen sugerida por los puntos estimados, no un
> contraste nítido**. El signo de θ es negativo en 99 % de los jackknife de 2 países; la
> significancia depende de qué 2 países se excluyan (y descansa en China).

### Temporalidad: fenómeno pre-pandemia, más marcado post-GFC

- **Interacción con dummy post-2020:** θ base (pre-2020) = **−1,014 (t = −1,90, p = 0,057)**;
  término JxG × D(post-2020) = **+0,989 (t = +1,55, p = 0,12)** — el período post-COVID
  compensa casi por completo la complementariedad pre-pandemia.
- **Ventanas móviles de 5 años:** 2009–2013 **+0,73 (p = 0,04)**; 2012–2016 **−0,65
  (p = 0,02)**; 2015–2019 −0,53 (p = 0,13); 2018–2022 −0,13 (p = 0,05); 2021–2025 −0,05 (n.s.).
- `sin 2020–2021` (mantiene pre-2020 + 2022+): θ = **−0,719 (t = −2,14)**.

### Modelo de umbral de Hansen (13 países)

γ̂ (GaR pp) = +0,06; efecto de JLoss sobre el EMBI **+5,88 pb** en cola severa vs **+2,02** en
régimen benigno; LR = 27,5. Persiste una diferencia de régimen ~2,9×.

### Efecto marginal ∂EMBI/∂JLoss (M2)

| Percentil de GaR | ∂EMBI/∂JLoss (pb/unidad) | se |
|---|---:|---:|
| p10 (cola severa, GaR = −2,15) | +3,43 | 1,33 |
| p50 (GaR = +1,96) | +2,77 | 1,01 |
| p90 (benigno, GaR = +6,06) | +2,11 | 0,97 |

Monótono decreciente en GaR (consistente con θ < 0), pendiente modesta; el IC90 del tramo de
cola severa apenas excluye el cero.

### Identificación causal (13 países, `causal_bbg.csv`)

| Método | Resultado |
|---|---|
| Wild cluster bootstrap (M2) | θ = −0,160; p_wildboot = 0,138 |
| **Proyecciones locales (nivel, pico)** | **+4,62 pb (t = +2,85)** en h = 1 — respalda H1 (JLoss → EMBI) |
| IV shift-share nivel — `OnOffRun_spread_log`, exp. pre-2012 | β_JLoss_IV = +7,46; F 1ª etapa = **11,4**; p = 0,34 (n.s.) |
| IV shift-share nivel — shock USD amplio (BIS) | β_JLoss_IV = −12,50 (signo opuesto); F = 37,8; p = 0,43 |
| IV sobre-identificado (2 instrumentos) | Sargan p = **0,0003 → RECHAZA** validez conjunta |
| Triple interacción institucional (JxG × WGI) | +0,26 (t = +0,89), n.s. |

> **H1 (nivel):** respaldada por OLS (β1 = +2,79, t = 2,74) y proyecciones locales
> (+4,62, t = 2,85). La evidencia IV es **más débil que en el panel de CDS**: con 13 países
> el instrumento `OnOffRun` baja a F = 11,4 y su 2ª etapa no es significativa; el 2º
> instrumento da signo opuesto y Sargan rechaza. **El efecto de nivel no está causalmente
> cerrado con IV**; se apoya en OLS + proyecciones locales.

### H4b (amplificación por concentración) — no identificado

β4 (JLoss×D×HHI): estructural +122 (t = +0,37), anual +152 (t = +0,73), trimestral ≈ 0
(t = −0,41) — los tres con IC de bootstrap de bloques cruzando el cero holgadamente. Sin
respaldo y sin poder, igual que en el panel de CDS.

### Placebo temporal (destruir la estructura de GaR, B = 600)

Reshuffle global (null exacto): θ medio ≈ +0,01, P(placebo ≤ obs) = 0,12. Con θ observado
= −0,16 (n.s.), el placebo es **consistente con la no-significancia**: el observado no está
en la cola de la distribución nula.

### Regresor generado (GaR)

θ estable a perturbar GaR con ruido de hasta 25 % de su sd (−0,161); a 50 % atenúa a −0,151.
El error de medición **atenúa** — el θ verdadero es, si acaso, más negativo.

### Coeficientes de control en M2 — advertencia

Bajo FE país + FE tiempo, los controles domésticos son interpolaciones lineales de datos
anuales; sus coeficientes **no tienen signo económico fiable** (deuda/PIB sale con signo
negativo, corr. within EMBI–deuda solo +0,10). Se reportan como controles, no se interpretan.

---

*Lo que sigue (§0–§7) fue escrito para el panel con CDS de 14 países. Se conserva como
referencia y porque varias cifras estructurales (censura de JLoss, exposición del IV) valen
para ambas series. **Para prosa, usar SIEMPRE las tablas de esta sección superior.***

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
| HHI (estructural/anual) | World Bank GFDD `GFDD.OI.01` |
| HHI trimestral (`HHI_q`) | **NUEVO** — `p6_concentracion_trimestral.py` sobre los mismos balances Bloomberg que `JLoss` (113 bancos); corr con GFDD en la muestra de estimación = 0,62 |

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
| **IV shift-share — efecto de NIVEL, `OnOffRun_spread_log`, exposición pre-2012** | β_JLoss_IV = **+17,49 pb/unidad**, **p = 0,001**; **F 1ª etapa = 21,6** — instrumento **fuerte**, no "débil-a-límite". Ver nota sobre `pre_year` abajo. |
| IV shift-share — efecto de NIVEL, shock USD amplio (BIS, exposición pre-2012) | β_JLoss_IV = +6,27, **p = 0,458** (n.s.); F 1ª etapa = 23,7 (fuerte, pero 2ª etapa no significativa) |
| **IV sobre-identificado (2 instrumentos: OnOffRun + USD amplio)** | β_JLoss_IV = +11,45, p = 0,048; F conjunto = 16,3; **Sargan stat = 9,06, p = 0,0026 → RECHAZA H0 de validez conjunta**. Los dos instrumentos no identifican el mismo parámetro — no reportar el sobre-identificado como estimación principal. |
| IV shift-share — interacción (2 endógenos, 2º instrumento débil; "con cautela") | θ_IV = +7,96 (se 45,7), no informativo (no se usa en prosa como resultado principal) |
| Proyecciones locales (pico régimen severo) | +4,35 pb (se 2,22) en h = 1; sin amplificación dinámica creciente |
| Triple interacción institucional (JxG × WGI) | −0,013 (t = −0,10), n.s. |

> **Nota sobre `pre_year` (elección del corte para estimar la exposición φ_país,
> verificado 2026-09-01, `p7_iv_dolar_bis.py` + `causal_core.iv_shiftshare_overid`):**
> la versión original usaba `pre_year=2016` (arbitrario) y daba F≈9,5 ("débil-a-límite").
> Se recalibró a `pre_year=2012` —el mismo quiebre de régimen post-GFC ya establecido en
> §2/§7bis para θ— y el instrumento original resultó **fuerte** (F=21,6, no débil). Grid
> de verificación (F por `pre_year`, no es un óptimo elegido ad hoc): 2010→9,2/15,8;
> 2012→**21,6/23,7**; 2014→12,9/19,3 (OnOffRun/USD) — fuerte en toda la vecindad, no un
> artefacto de un corte puntual. **Instrumento recomendado para prosa: `OnOffRun_spread_log`
> con `pre_year=2012`** (F=21,6, β=+17,5, p=0,001) — mejor restricción de exclusión
> (spread de liquidez de fondeo bancario) que el shock del dólar (afecta el soberano por
> canales no bancarios: reservas, deuda externa, importaciones). El fallo de Sargan al
> combinar ambos es evidencia honesta de que **no son conjuntamente válidos**; se reporta
> como límite de la estrategia, no se oculta.

---

## 6. Puente OI ↔ datos: H4a y H4b

`CDS = α_i + δ_t + β1·JLoss + β2·D + β3·(JLoss×D) + β4·(JLoss×D×HHI) + …`, D = −GaR.

| HHI | β3 (JLoss×D) | t | **β4 (JLoss×D×HHI)** | t agrup. | P(β4>0) boot bloques | **IC90 boot bloques** | rango LOO |
|---|---:|---:|---:|---:|---:|---|---|
| estructural (GFDD, nivel) | +56,3 | +1,72 | **−392** | −2,34 | 12 % | **(−627, +212)** — incluye 0 | [−491, −236] |
| anual (GFDD, serie) | +24,5 | +1,08 | −268 | −2,14 | 30 % | (−387, +345) — incluye 0 | [−286, −45] |
| **trimestral** (`HHI_q`, verificado 2026-09-01, N=773, 13 países) | −5,5 | −0,17 | **−0,114** | **−2,75** | **9 %** | **(−0,144, +0,013)** — incluye 0 por muy poco | [≈0, ≈0] |

> **H4a (β3 > 0):** signo **opuesto** al predicho, no significativo (+56, t = 1,72). Con la
> concentración trimestral (variación temporal real, no proxy anual casi invariante) β3
> también cambia de signo y pierde toda precisión (−5,5, t=−0,17). Sólo el θ de nivel *sin*
> HHI (§1) tiene el signo predicho.
> **H4b (β4 > 0): NO identificado, y el test más potente lo confirma.** Con `HHI_q`
> —concentración trimestral construida de los mismos 113 bancos que `JLoss`, corr 0,62 con
> el GFDD anual— el IC90 del bootstrap de bloques es (−0,144, +0,013): **todavía cruza el
> cero, pero por un margen mínimo**, con el t agrupado más negativo de los tres (−2,75) y la
> P(β4>0) más baja (9 %). La concentración trimestral **no rescata la predicción del
> modelo** — si acaso, aporta más evidencia (aunque no concluyente al 90%) de que el signo
> empírico es negativo, no que sea únicamente un problema de falta de variación temporal
> en el proxy de concentración. Contrasta con la versión v8 regulatoria (+721, t = +2,98),
> de dispersión transversal de `JLoss` mucho mayor. **La predicción distintiva del modelo de
> OI sigue sin encontrar respaldo, ahora con un proxy de concentración mejor identificado.**
> (Redacción de prosa: "no identificado / imprecise", NO "significativo en la dirección
> equivocada".)

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

- **H1 (nivel, JLoss→CDS):** respaldada con un instrumento **fuerte** — IV shift-share
  (`OnOffRun_spread_log`, exposición pre-2012): F = 21,6, β_JLoss = +17,5 pb (**p = 0,001**),
  dirección banco→soberano. Un segundo instrumento (shock USD amplio BIS) tiene primera etapa
  igual de fuerte (F=23,7) pero efecto no significativo solo (p=0,46), y combinar ambos
  **rechaza Sargan** (p=0,003) — no son conjuntamente válidos; se reporta el de mejor
  restricción de exclusión (`OnOffRun`, spread de liquidez de fondeo bancario) como principal.
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
  cruzando el cero con los tres proxies de concentración (GFDD estructural, GFDD anual y la
  nueva concentración **trimestral** de los mismos bancos de `JLoss`); con la serie trimestral
  el margen es mínimo (IC90 −0,144/+0,013) y la P(β4>0) más baja (9 %), pero no cruza el
  umbral de significancia. No se afirma dirección.
