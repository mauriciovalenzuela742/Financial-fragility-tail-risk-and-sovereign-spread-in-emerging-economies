# Números canónicos — panel anclado en Bloomberg

*Generado el 2026-08-31 re-ejecutando `1_Codigo/Panel/bbg/p1..p4`. Sustituye, para toda
prosa de la tesis a partir de esta fecha, a `1_Codigo/Panel/NUMEROS_CANONICOS.md` (que
queda como registro de la versión con datos regulatorios, "v8").*

**Regla de uso (sin cambios):** ningún coeficiente entra a la prosa sin trazarse a una fila
de este documento.

---

## 0. Qué cambió respecto de la versión v8

| Insumo | v8 (regulatorio) | Esta versión (Bloomberg) |
|---|---|---|
| **JLoss** | balances de reguladores nacionales (CMF, CNBV, SBS, SARB…) | **Bloomberg Terminal** (xbbg): balances bancarios + capitalización bursátil diaria, 113 bancos, 20 países, 2004→2026. Motor `jloss_engine.py` sin cambios (Merton/KMV multi-arranque + punto de silla). |
| **EMBI** | JP Morgan EMBI Global (BCRP) + tablas GFSR del FMI | **CDS soberano 5Y de Bloomberg** (pb), media trimestral. |
| **Global** (VIX, UST10Y, US HY) | FRED / CBOE | **Bloomberg** (`GLOBAL/`). |
| **GaR** | regresión cuantílica CEMLA sobre FCI | **sin cambios** — sus insumos (IPC, PIB, bolsa, REER, 10Y) son estadísticas nacionales; Bloomberg no es fuente primaria de cuentas nacionales. Se documenta esta frontera. |
| **Concentración (HHI)** | GFDD 3/5 bancos | GFDD 3 bancos; para los países nuevos del panel se trajo vía API World Bank. |

**Concordancia JLoss v8 ↔ Bloomberg:** correlación intra-país ≈ 0,51–0,58; la serie
Bloomberg es mucho más homogénea entre países (desv. estándar transversal ≈ 2,5–4,1 vs 8,3
en v8). Con Bloomberg, **Brasil ya no es el valor extremo de fragilidad** (JLoss medio 4,9;
Turquía 9,6; China 6,8).

**Corea del Sur excluida del panel** (`bbg/DIAGNOSTICO_COREA.md`): su E/D_mercado ≈ 0,04
(vs 0,15–0,34 en el resto), reflejo del "Korea discount" estructural en la valoración de los
holdings bancarios; el Merton la lee como default inminente (PD mediana 0,55; JLoss 25–47).
La reconstrucción v8 tampoco la incluía.

---

## 1. Dos bases

| | Principal | Ampliada |
|---|---|---|
| Países | Brasil, Chile, Colombia, México, Perú | + China, Indonesia, Malasia, Filipinas, Sudáfrica, Turquía (**11**) |
| Ventana | 2006Q4–2026Q1 | 2004Q1–2026Q1 |
| N (M2, sin controles) | 363 | 809 |
| N (M3, con 6 controles domésticos) | 228 (deuda/PIB limita); 285 sin deuda | — (no hay controles domésticos) |
| EMBI | CDS 5Y Bloomberg | CDS 5Y Bloomberg |

Descriptivos (media / desv.): Principal — EMBI 133,2/68,7 pb; JLoss 3,62/2,54; GaR 0,002/0,035.
Ampliada — EMBI 147,8/100,9 pb; JLoss 4,17/4,11; GaR 0,014/0,040.

---

## 2. Mecanismo central: θ = JLoss × GaR sobre EMBI

Especificación: `EMBI = α_i + γ_t + β1·JLoss_c + β2·GaR_pp_c + θ·(JLoss_c×GaR_pp_c) + X + ε`,
JLoss y GaR (pp) centradas, errores Driscoll–Kraay (kernel Bartlett). `linearmodels.PanelOLS`.

### Base principal (5 LatAm)

| Spec | N | θ | t | p |
|---|---:|---:|---:|---:|
| M2 — FE país+tiempo, sin controles | 363 | **−0,325** | −0,89 | 0,376 |
| **M3 — FE país+tiempo, + 6 controles domésticos** | **228** | **−0,466** | **−2,15** | **0,033** |
| M3, errores cluster país | 228 | −0,466 | −3,37 | 0,001 |
| M3, errores cluster tiempo | 228 | −0,466 | −2,63 | 0,009 |

> **Número a citar como "M3, principal": θ = −0,466 (N=228, t=−2,15, p=0,033).**
> Con datos Bloomberg el resultado **depende de los controles**: M2 (sin controles) no es
> significativo. El ajuste dentro del panel es débil (R²_within < 0).

### Base ampliada (11 países, sin Corea)

| Spec | N | θ | t | p |
|---|---:|---:|---:|---:|
| **M2 — FE país+tiempo (única posible, sin controles)** | **809** | **−0,557** | **−2,25** | **0,025** |
| cluster país | 809 | −0,557 | −2,46 | 0,014 |
| cluster tiempo | 809 | −0,557 | −2,65 | 0,008 |
| cola = Expected Shortfall | 809 | −0,608 | −2,67 | — |

> **Número a citar como "M2, ampliada": θ = −0,557 (N=809, t=−2,25, p=0,025).**
> R²_within = 0,17 (sano). **Pero no sobrevive a excluir el período pre-COVID**
> (θ = +0,48, t=+0,79 con datos <2020): en la base ampliada el mecanismo es un fenómeno
> post-2020.

### Robustez (base principal, M3)

| Caso | N | θ | t |
|---|---:|---:|---:|
| sin COVID (<2020) | 164 | −1,134 | −3,95 |
| sin deuda/PIB (5 controles) | 285 | −0,468 | −1,41 |
| cola = Expected Shortfall | 228 | −0,461 | −2,09 |
| leave-one-out: rango de θ | — | [−0,55 (sin Colombia), −0,23 (sin Brasil)] | todos < 0 |

`sin méxico` θ=−0,28 (t=−1,79); `sin perú` θ=−0,54 (t=−0,82, IC ancho). Ningún país genera
el signo por sí solo; el pre-COVID lo intensifica.

### Robustez (base ampliada, M2), leave-one-country-out

θ negativo en 10 de 11 subconjuntos; única excepción `sin china` (θ=−0,12, t=−0,40).
Rango [−0,65 (sin Sudáfrica), −0,12 (sin China)].

---

## 3. No linealidad: modelo de umbral de panel (Hansen)

Variable de umbral q = GaR (pp). Efecto de JLoss sobre EMBI (pb/unidad) por régimen:

| Base | Umbral γ̂ (GaR pp) | Régimen cola severa (GaR ≤ γ̂) | Régimen benigno | LR |
|---|---:|---:|---:|---:|
| Principal | −3,29 | **+7,05** | +2,96 | 25,3 |
| Ampliada | +0,16 | **+14,39** | +6,07 | 89,4 |

El efecto de JLoss es 2–2,4× mayor en el régimen de cola severa: corrobora la no linealidad
sin imponer la forma funcional de la interacción.

### Efecto marginal ∂EMBI/∂JLoss (M3 principal / M2 ampliada)

| Percentil de GaR | Principal | Ampliada |
|---|---:|---:|
| p10 (cola severa) | +5,59 | +9,82 |
| p50 | +3,67 | +7,53 |
| p90 (benigno) | +1,91 | +5,40 |

Monótono decreciente en GaR: firma empírica de la complementariedad.

---

## 4. Identificación causal

| Método | Principal | Ampliada |
|---|---|---|
| **Wild cluster bootstrap** (999 rep.) | θ=−0,466; **p_wildboot = 0,058** (4 clusters) | θ=−0,557; **p_wildboot = 0,141** (11 clusters) |
| **IV shift-share (nivel)**, shock global | F 1ª etapa = **6,2** (VIX); dirección banco→soberano, débil | F 1ª etapa = **50,6** (on/off-run); efecto de nivel positivo, p=0,077 |
| Proyecciones locales (pico régimen severo) | +5,3 pb (se 1,1) en h=1 | +4,8 (se 1,5) en h=1; sin amplificación dinámica creciente |
| Triple interacción institucional (JxG×WGI) | +0,59 (t=1,08), n.s. | +0,04 (t=0,16), n.s. |

Lectura: el signo y la dirección de nivel (banco→soberano) son defendibles; la significancia
**puntual** de θ es frágil bajo inferencia robusta a pocos clusters (más en la ampliada).

---

## 5. Puente OI ↔ datos reales: H4a y H4b

Especificación `EMBI = α_i + δ_t + β1·JLoss + β2·D + β3·(JLoss×D) + β4·(JLoss×D×HHI) + …`,
con D = −GaR. H4a: β3 > 0. H4b: β4 > 0.

| Base | HHI | β3 (JLoss×D) | t | **β4 (JLoss×D×HHI)** | t | P(β4>0) boot | IC90% |
|---|---|---:|---:|---:|---:|---:|---|
| Principal (5) | estructural | +0,7 | +0,01 | **−173** | −0,35 | 44% | [−1303, +1967] |
| Principal (5) | anual | +18,4 | +0,51 | +113 | +0,31 | 71% | [−121, +1457] |
| **Ampliada (11)** | **estructural** | **+39,8** | **+1,48** | **−418** | **−2,11** | **13%** | **[−564, +248]** |
| Ampliada (11) | anual | +17,0 | +0,91 | **−262** | −2,10 | 33% | [−373, +389] |

> **H4a (complementariedad, β3>0):** débil. β3 ≈ 0 en la base principal; +40 (t=+1,48, no
> significativo) en la ampliada. El signo es el predicho pero la magnitud no se distingue de
> cero. (El canal se ve mejor en la parametrización de nivel θ = JLoss×GaR de la Sección 2,
> donde sí es significativo.)
>
> **H4b (amplificación por concentración, β4>0): NO se sostiene.** El punto estimado tiene
> **signo opuesto al predicho** y es **marginalmente significativo en esa dirección
> equivocada** en la base ampliada (β4 = −418, t = −2,11). Contrasta con la versión v8
> (+721, t=+2,98). Robusto a HHI anual (−262, t=−2,10) y a leave-one-out (rango
> [−471, −203], todos negativos). **La predicción distintiva del modelo teórico de OI no
> encuentra respaldo empírico con datos Bloomberg.**

### Por qué cae H4b (candidatos, no resueltos)

1. La serie JLoss Bloomberg es transversalmente **homogénea** (sd 2,5–4,1 vs 8,3 en v8):
   la triple interacción necesita dispersión entre países de la fragilidad, y Bloomberg la
   comprime. El +721 de v8 se apoyaba en la enorme dispersión regulatoria (Brasil ≈ 16).
2. El HHI de GFDD es casi invariante en el tiempo → la identificación de β4 descansa en
   ~11 valores transversales.
3. El canal de amplificación es genuinamente más débil de lo que sugiere la calibración
   del modelo (potencia MC 60–70% con N de este orden).

Distinguir entre 1–3 requiere HHI a frecuencia trimestral y/o ampliar el universo de países.

---

## 6. Resumen para la prosa

- **H1 (nivel, JLoss→EMBI):** respaldada; IV shift-share en la base ampliada (F=51) da
  dirección causal creíble.
- **H2 (GaR→EMBI):** β2 < 0 en todas las especificaciones (no tabulado en detalle aquí).
- **H3 / H4a (complementariedad θ<0):** respaldada en ambas bases bajo inferencia estándar
  (M3 principal p=0,033; M2 ampliada p=0,025) y corroborada por el modelo de umbral; con
  dos salvedades nuevas — en la principal necesita los controles domésticos, en la ampliada
  es post-COVID — y con significancia frágil bajo wild bootstrap.
- **H4b (amplificación por concentración β4>0):** **rechazada** — punto estimado de signo
  contrario, significativo en esa dirección en la base ampliada.
