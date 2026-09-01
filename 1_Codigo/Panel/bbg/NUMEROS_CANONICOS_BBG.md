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

Descriptivos (muestra de estimación, N≈838): CDS 149/102 pb; JLoss 4,1/4,1 (sd transversal
≈4, vs 8,3 regulatorio); deuda/PIB 46/20; balance fiscal −3,0/2,3; reservas/PIB 19/9;
CA/PIB −1,1/3,0; inflación 5,6/8,4.

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
| **IV shift-share (nivel)** | F 1ª etapa ≈ **9,5** (débil-a-límite); efecto de nivel sensible a la especificación → sugestivo, no concluyente |
| Proyecciones locales (pico régimen severo) | +4,3 pb (se 2,2) en h = 1; sin amplificación dinámica creciente |
| Triple interacción institucional (JxG × WGI) | −0,013 (t = −0,13), n.s. |

---

## 6. Puente OI ↔ datos: H4a y H4b

`CDS = α_i + δ_t + β1·JLoss + β2·D + β3·(JLoss×D) + β4·(JLoss×D×HHI) + …`, D = −GaR.

| HHI | β3 (JLoss×D) | t | **β4 (JLoss×D×HHI)** | t | P(β4>0) boot | IC90% | LOO |
|---|---:|---:|---:|---:|---:|---|---|
| estructural | +56,3 | +1,72 | **−392** | −2,34 | 12 % | [−491, −236] | todos < 0 |
| anual | +24,5 | +1,08 | −268 | −2,14 | 30 % | [−286, −45] | — |

> **H4a (β3 > 0):** signo predicho, **no significativo** (+56, t = 1,72).
> **H4b (β4 > 0): NO se sostiene.** β4 = −392 (t = −2,34): **signo opuesto al predicho y
> significativo en esa dirección**, negativo en todas las submuestras leave-one-out. Contrasta
> con la versión v8 regulatoria (+721, t = +2,98). **La predicción distintiva del modelo de OI
> no encuentra respaldo empírico con datos homogéneos.**

Explicación más probable (`paper1_oi.tex` §5.4): la serie JLoss de Bloomberg es
transversalmente comprimida (sd ≈4 vs 8,3), y la triple interacción necesita la dispersión
entre países de la fragilidad que la homogeneización elimina; el HHI del GFDD es además casi
invariante en el tiempo.

---

## 7. Resumen para la prosa

- **H1 (nivel, JLoss→CDS):** plausible; IV shift-share débil-a-límite (F ≈ 9,5).
- **H2 (GaR→CDS):** β2 < 0.
- **H3 (complementariedad, θ < 0):** **signo y forma respaldados** (efecto marginal + umbral);
  significancia **marginal** (p ≈ 0,056 DK, 0,035 wild boot, 0,001 cluster país). Identificación
  **concentrada en episodios de estrés recientes**; antes de 2020 el signo se mantiene pero la
  interacción no se distingue de cero.
- **H4a (β3 > 0):** signo predicho, no significativo.
- **H4b (β4 > 0):** **rechazada** — signo contrario, significativo en esa dirección.
