# Números canónicos — panel único anclado en Bloomberg

*Generado el 2026-08-31, reestructurado 2026-09-01 (variable dependiente = EMBI) y
2026-09-02 (Hungría excluida por `below_min_banks`; 13 países). Re-ejecutando
`1_Codigo/Panel/bbg/p1..p7`. Fuente de verdad para toda prosa de la tesis. Sustituye a la
versión de dos bases y a `1_Codigo/Panel/NUMEROS_CANONICOS.md` (v8 regulatorio).*

**Regla de uso:** ningún coeficiente entra a la prosa sin trazarse a una fila de este documento.

> **Nota de parametrización (2026-09-07).** La prosa de la tesis (Cap. 2, introducción y
> discusión generales) y los `.Rmd` del panel reportan la interacción sobre **`D = −GaR`**
> ("riesgo de cola"; `D` mayor = peor), con coeficiente **`β₃ = coef(JLoss × D) = −θ`**
> (positivo cuando hay amplificación). Este documento y `bateria_bbg.csv` se mantienen en
> forma **`θ` (`JLoss × GaR`)**. Traducción: `β₃ = −θ`, `coef(D) = −coef(GaR)`; ninguna
> magnitud, `t` en valor absoluto, `p` ni `N` cambian. Las tablas de abajo NO se reescriben.

---

## ⚠ RE-EJECUCIÓN 2026-09-06 — GaR de 18 países (Rusia agregada al pool)

`gar_panel_all18.csv` reemplaza a `gar_panel_all17.csv`: Rusia entra a la regresión
cuantílica pooled (motor corrido en NLHPC, job 12748912). Efecto:

- **Muestra principal (EMBI): sin cambio** — 13 países, N = 721 (M1) / 614 (M2). Rusia no
  tiene EMBI Global Diversified de J.P. Morgan.
- **Muestra de robustez (CDS): 13 → 14 países.** Rusia aporta 10 trimestres
  (CDS+JLoss+GaR, 2013Q3–2015Q4). θ (DV=CDS): M1 sin controles −0,55 → **−0,615** (t=−2,26);
  con controles −0,38 → **−0,413** (t=−1,98).
- **Batería (Tabla 2.3), interacción M4:**

  | spec | θ antes (all17) | θ ahora (all18) |
  |---|---|---|
  | completa / FE país+tiempo | −0,136 (n.s.) | **−0,176** (n.s., t=−0,68) |
  | sin crisis / FE tiempo | −1,724*** | **−1,729*** |
  | sin crisis / FE país | −1,179*** | **−1,159*** |
  | sin crisis / FE país+tiempo | −1,190*** | **−1,171*** (p<0,001) |

- **Heterogeneidad (M2+6 controles, FE país+tiempo):**
  núcleo 11 EM −0,47 → **−0,49** (t=−2,59, p=0,010, N=479);
  núcleo Y sin crisis −0,94 → **−0,93** (t=−3,23, p=0,001, N=405);
  sin crisis (todos) −0,69 → **−0,68** (t=−2,17, p=0,031, N=519).
- **Definición de crisis:** sin COVID solo −0,81 → **−0,81** (p=0,022); sin GFC solo
  −0,20 → **−0,24** (n.s.).
- **GaR de los 13 países previos:** |Δ| mediana 0,000, p90 0,003, máx 0,019 (unidades de
  GaR, ~×100 para pp).

**Lectura:** meter a Rusia hace θ uniformemente ~0,02–0,03 más negativo, sin cambiar ninguna
conclusión cualitativa (muestra completa nula, sin-crisis fuerte, China pivote, núcleo).
**La prosa de la tesis y el artifact NO se actualizan todavía** — se hará en una sola pasada
junto con Argentina (bono 5Y, pendiente de Bloomberg). Las filas de abajo son todavía del
estado all17; usar la tabla de arriba para los números de la re-ejecución.

> **Decisión reafirmada (Parte D, 2026-09-16): sigue sin propagarse.** Todo el trabajo de
> esta sesión (interacción de crisis, endogeneidad `Ryr`, *bootstrap* C1, IV reforzado C2)
> se construyó también sobre la vigente base **all17** — la misma que documentan las tablas
> de abajo —, así que no hay mezcla de vintages dentro de la tesis. Razones para NO propagar
> todavía: (i) el efecto es cuantitativamente inmaterial (|Δθ| ≤ 0,03, ninguna conclusión
> cambia); (ii) Argentina sigue pendiente de Bloomberg, y el plan original ya era batchear
> ambas actualizaciones juntas; (iii) propagar ahora obligaría a re-correr TODO el *pipeline*
> — incluida la especificación de crisis, la robustez de `Ryr`, y el *bootstrap* de GaR que
> está a punto de correrse en NLHPC con la base all17 — por una corrección que no cambia
> ninguna lectura. **Próximo paso, cuando Argentina esté lista:** una sola re-ejecución
> completa de `bbg/p1..p10` sobre `gar_panel_all18.csv` + Argentina, reescribiendo esta
> sección superior y toda la prosa de `paper2_empirico.tex` en una sola pasada — no antes.

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

### Interacción de crisis — SIN botar trimestres (2026-09-10, indicación del coguía)

Especificación (D ≡ −GaR, toda la muestra):
`EMBI = a_i + g_t + b1·JLoss + b2·D + b3·(JLoss×D) + b4·(JLoss×D×Crisis) + b5·(JLoss×Crisis) + b6·(D×Crisis) + [X]`.
`b3` = complementariedad fuera de crisis; `b3+b4` = en crisis (predicción del coguía: `b3+b4 ≈ 0`).
Fuente: `p9_crisis_interaccion.py` = `crisis_interaccion.R` (coinciden a 4 decimales); DK
(`kernel bartlett` en Python / `vcovSCC` en R); FE país+tiempo (PT).
Convención: **estos coeficientes están en β₃ = coef(JLoss×D) = −θ** (positivo = complementariedad).

**Ventana de crisis:** GFC 2008Q4–2009Q4 (31 obs) + COVID 2020Q1–2021Q4 (80) + estrés EM
2015Q3–2016Q1 (27). *Backstop* = GFC + COVID (con respaldos Fed/FMI/QE). *EMstress* = 2015–16.

| Spec (PT) | N | β₃ (fuera crisis) | β₄ | β₃+β₄ | Wald p (H₀: β₃+β₄=0) |
|---|---|---|---|---|---|
| **Vector único**, +6 controles | 614 | **+0,811** (t=1,96, p=0,051) | −0,839 (t=−1,96) | −0,03 | **0,766** → no rechaza (se anula) |
| Vector único, sin controles | 721 | +0,951 (t=2,77, p=0,006) | −1,192 (t=−3,18) | −0,24 | 0,118 |
| **Backstop vs EMstress**, +6 controles | 614 | **+0,837** (t=2,02, p=0,044) | Backstop −0,942 (t=−2,23, p=0,026); EMstress +0,213 (t=0,43, n.s.) | Backstop −0,11; **EMstress +1,05** | Backstop **0,270** (se anula); EMstress **<0,001** (sigue presente) |
| Backstop vs EMstress, sin controles | 721 | +0,973 (t=2,82) | Backstop −1,294 (t=−3,19); EMstress −0,212 (n.s.) | Backstop −0,32; EMstress +0,76 | Backstop 0,044; EMstress 0,028 |

> **Lectura (headline).** La complementariedad (β₃ > 0) es real y significativa **fuera de
> crisis** —el nulo de la muestra completa (β₃ = +0,16) es un promedio de regímenes—, **se
> anula bajo `Backstop`** (GFC+COVID, β₃+β₄ ≈ 0, Wald no rechaza) y **sobrevive bajo
> `EMstress`** (2015–16, β₃+β₄ ≈ +1,0, Wald rechaza al 1 %). Test de falsación: el canal se
> apaga sólo donde hay respaldo oficial masivo, no en el estrés emergente sin respaldo.
> Reemplaza al corte por submuestra (batería Panel B) como resultado principal de la
> dimensión temporal; el Panel B queda como robustez.

FE sólo país (P): β₃ (Backstop vs EMstress, +6 ctrl) = +0,672 (t=1,84); Backstop β₄ = −0,725
(t=−1,97, p=0,049); EMstress β₄ = +0,766 (t=1,75, p=0,081). FE sólo tiempo (T): β₃ ≈ 0 (sin
FE de país domina la varianza transversal — spec no informativa para la interacción).

### ★ Batería de interacción de crisis (24 especificaciones) — `p9b_bateria_crisis.py` → `bateria_crisis_bbg.csv` (2026-09-22)

Extiende la lógica de la ★ BATERÍA DE REGRESIONES (arriba, `p8_bateria_regresiones.py`) a la
especificación de interacción de crisis de la sección anterior: cuatro modelos anidados
(**CM1** `JLoss` + su interacción con crisis; **CM2** `D` + su interacción; **CM3** ambos
niveles + sus interacciones, sin `JLoss×D`; **CM4** = la especificación ya publicada en
`tab:crisis`, con `JLoss×D` y su interacción con crisis) × 3 estructuras de efectos fijos
(T, P, PT) × 2 formas de codificar el vector de crisis (**Panel A**, un solo dummy `Crisis`;
**Panel B**, `Backstop` GFC+COVID vs `EMstress` 2015–16) = 24 filas del CSV, las mismas 6
controles domésticos y errores Driscoll–Kraay que `p9_crisis_interaccion.py`. A diferencia de
`bateria_bbg.csv` (que se mantiene en forma `θ`), **`bateria_crisis_bbg.csv` ya está en la
convención `D≡−GaR` / `β₃` de la prosa** (no requiere multiplicar por −1) — igual que
`crisis_interaccion_bbg.csv`, la fuente de `tab:crisis`.

**Verificación de consistencia (obligatoria, corrida por el propio script antes de guardar):**
la fila `CM4 / FE=PT / Panel B` reproduce **exacto** la Tabla `tab:crisis` ya publicada: β₃
(fuera de crisis) = +0,837 (t=+2,02); β₃+β₄ Backstop = −0,105 (Wald p=0,270); β₃+β₄ EMstress =
+1,051 (Wald p=0,000226). `p9b_bateria_crisis.py` aborta (`SystemExit`) si no coincide a 5e-4;
corrió limpio. N=614, 13 países, 88 períodos, entre 7 y 85 trimestres por país (promedio 47,2)
en las 24 especificaciones — constante, no varía por modelo ni por FE.

**Panel A — vector único de crisis** (columnas: CM1/T, CM1/P, CM1/PT, CM2/T, CM2/P, CM2/PT,
CM3/T, CM3/P, CM3/PT, CM4/T, CM4/P, CM4/PT):

| coef | CM1/T | CM1/P | CM1/PT | CM2/T | CM2/P | CM2/PT | CM3/T | CM3/P | CM3/PT | CM4/T | CM4/P | CM4/PT |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `JLoss` (fuera de crisis) | 2,09 | 4,36*** | 2,24* | | | | 2,87 | 3,30*** | 2,04* | 2,89 | 3,60*** | 2,51 |
| `D` (fuera de crisis) | | | | 2,75 | 10,06*** | 6,00*** | 4,08 | 8,88*** | 4,91** | 4,12 | 9,19*** | 5,57*** |
| `JLoss×D` = β₃ (fuera de crisis) | | | | | | | | | | 0,03 | 0,64* | **0,81\*** |
| Δ(`JLoss×D`)×Crisis = β₄ | | | | | | | | | | −0,43 | −0,63* | **−0,84\*** |
| β₃+β₄ (Wald *p*) | | | | | | | | | | −0,40 (0,091) | 0,01 (0,890) | **−0,03 (0,766)** |
| R²within | 0,03 | 0,40 | 0,38 | 0,02 | 0,44 | 0,42 | 0,14 | 0,47 | 0,45 | 0,14 | 0,48 | 0,45 |
| R²overall | 0,38 | 0,40 | 0,39 | 0,36 | 0,44 | 0,38 | 0,40 | 0,47 | 0,41 | 0,40 | 0,48 | 0,42 |

La columna **CM4/PT** (en negrita) es la fila "Vector único" ya publicada en `tab:crisis`
(+0,81/−0,84/−0,03, Wald *p*=0,77 ≈ 0,766 aquí con más decimales — la publicada redondea a 2).

**Panel B — Backstop (GFC+COVID) vs EMstress (2015–16)**:

| coef | CM1/T | CM1/P | CM1/PT | CM2/T | CM2/P | CM2/PT | CM3/T | CM3/P | CM3/PT | CM4/T | CM4/P | CM4/PT |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `JLoss` (fuera de crisis) | 2,12 | 4,36*** | 2,24* | | | | 2,83 | 3,19*** | 1,98* | 2,81 | 3,54*** | 2,51 |
| `D` (fuera de crisis) | | | | 2,71 | 10,51*** | 6,35*** | 4,02 | 9,30*** | 5,31*** | 4,03 | 9,49*** | 5,81*** |
| `JLoss×D` = β₃ (fuera de crisis) | | | | | | | | | | 0,07 | 0,67* | **0,84**** |
| Δ(`JLoss×D`)×Backstop = β₄(bk) | | | | | | | | | | −0,60 | −0,72** | **−0,94**** |
| β₃+β₄(bk) (Wald *p*) | | | | | | | | | | −0,54 (0,003) | −0,05 (0,621) | **−0,11 (0,270)** |
| Δ(`JLoss×D`)×EMstress = β₄(em) | | | | | | | | | | 1,49 | 0,56 | **0,21** |
| β₃+β₄(em) (Wald *p*) | | | | | | | | | | 1,56 (0,000) | 1,24 (0,000) | **1,05 (0,000)** |
| R²within | 0,03 | 0,40 | 0,38 | −0,04 | 0,45 | 0,41 | 0,12 | 0,48 | 0,45 | 0,12 | 0,49 | 0,46 |
| R²overall | 0,38 | 0,40 | 0,39 | 0,38 | 0,45 | 0,40 | 0,41 | 0,48 | 0,42 | 0,41 | 0,49 | 0,43 |

La columna **CM4/PT** (en negrita) es la fila "Backstop vs EMstress" ya publicada en
`tab:crisis`. Metadata de estilo `PanelOLS Estimation Summary` completa (F-statistic, su
*p*-valor, y R²*between*) por las 24 filas está en `bateria_crisis_bbg.csv` directamente
(columnas `f_stat`, `f_pval`, `rsquared_between`); se omite de las tablas de arriba y de la
Tabla nueva de la tesis por legibilidad: el F-statistic conjunto (incluye los 6 controles y los
efectos fijos, no solo la interacción) rechaza la hipótesis nula de no significancia conjunta
en las 24 especificaciones (F entre 24 y 59, *p*≈0 en todas); R²*between* toma valores muy
negativos bajo efectos fijos de entidad o bidireccionales (rango −9,3 a +0,32) — un artefacto
conocido de `linearmodels.PanelOLS` cuando casi toda la variación relevante ya la absorben los
efectos fijos, no una falla del ajuste, y no aporta a la lectura económica del capítulo.

**Lectura.** La batería confirma que el resultado central de `tab:crisis` (β₃>0 fuera de
crisis, se anula bajo *Backstop*, sobrevive bajo *EMstress*) no depende de qué estructura de
efectos fijos se use dentro de CM4: el signo y la magnitud de β₃ son estables entre FE de
tiempo, de país y bidireccionales (aunque solo bajo FE de país y bidireccionales alcanza
significancia convencional), y la cancelación bajo *Backstop* / supervivencia bajo *EMstress*
se replica bajo las tres. Los modelos CM1–CM3 muestran además que los canales de nivel
(`JLoss`, `D`) mantienen su signo y significancia al permitírseles variar con el vector de
crisis, antes de introducir la interacción completa en CM4 — la misma progresión anidada que
ya usa la ★ BATERÍA DE REGRESIONES. Prosa: `paper2_empirico.tex` (ahora fusionado en
`investigacion.tex`), sección de Resultados, "La interacción de crisis: sin botar trimestres" —
Tabla nueva "Batería de interacción de crisis" (estilo PanelOLS), presentada como resultado
central, con `tab:crisis` (fila CM4/PT) como su síntesis de lectura rápida.

### Modelo de umbral de Hansen (13 países)

*Corregido 2026-09-23 (revisión de árbitro, ronda 2): la fila anterior (γ̂=+0,06;
+5,88/+2,02 pb; LR=27,5) no coincidía con `umbral_bbg.csv` ni con `fig_umbral.pdf`, ambos ya
correctos — era un error de transcripción en este documento, no un problema de vigencia del
panel (`umbral_bbg.csv` se re-ejecutó sobre `Panel_bloomberg.csv` vigente y reproduce
exactamente el valor ya guardado, a 10 decimales). Verificado también contra
`investigacion.tex`, corregido en la misma revisión.*

γ̂ (GaR pp) = −0,18 (equivalentemente $D\gtrsim+0{,}18$); efecto de JLoss sobre el EMBI
**+6,06 pb** en cola severa (GaR ≤ γ̂) vs **+2,11** en régimen benigno; LR = 28,5. Persiste una
diferencia de régimen ~2,9×. Fuente: `bbg/p2_regresiones.py::umbral_hansen()` →
`umbral_bbg.csv`.

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
| **IV shift-share nivel — ToT commodities (C2, 2026-09-16)** | F 1ª etapa ≈ **0,03** (prácticamente nula para `JLoss`) |
| IV sobre-identificado (2 instrumentos, OnOffRun+USD) | Sargan p = **0,0003 → RECHAZA** validez conjunta |
| IV sobre-identificado (3 instrumentos, +ToT commodities) | Sargan p = **0,0014 → RECHAZA** validez conjunta |
| Triple interacción institucional (JxG × WGI) | +0,26 (t = +0,89), n.s. |

> **H1 (nivel):** respaldada por OLS (β1 = +2,79, t = 2,74) y proyecciones locales
> (+4,62, t = 2,85). La evidencia IV es **más débil que en el panel de CDS**: con 13 países
> el instrumento `OnOffRun` baja a F = 11,4 y su 2ª etapa no es significativa; el 2º
> instrumento da signo opuesto y Sargan rechaza. **El efecto de nivel no está causalmente
> cerrado con IV**; se apoya en OLS + proyecciones locales.

### IV reforzado — commodity ToT shift-share (C2, 2026-09-16, plan de árbitro)

Punto C2: intentar reforzar la IV con un instrumento **más exógeno por diseño** que los dos
existentes — su "participación" (share) NO se estima regresando `JLoss` contra el choque (como
`OnOffRun`/USD BIS), sino que viene de **datos comerciales pre-muestra**, exógenos por
construcción:

`CTOT_shock_{i,t} = Σ_k w_{i,k}(1998-2003) · log(P_{k,t})`

donde `w_{i,k}` = participación de exportaciones de mercancías del país `i` en 4 categorías
amplias (energía, minerales y metales, materias primas agrícolas, alimentos), promedio
**1998-2003** (Banco Mundial WDI, `TX.VAL.{FUEL,MMTL,AGRI,FOOD}.ZS.UN`), y `P_{k,t}` = índice de
precio mundial de esa categoría (World Bank Pink Sheet, "Monthly Indices"). Pesos usados (%,
`ctot_pesos_pre2004.csv`): Chile 41,9% metales, Colombia 37,2% energía, Perú 32,7% metales,
Indonesia 23,8% energía; China/Filipinas/México/Malasia con pesos comerciales bajos (<9% en
cada categoría) — la heterogeneidad de exposición identifica el diseño *shift-share*.
Construcción: `p7b_iv_commodity_tot.py` → `ctot_shock_bbg.csv` (mezclado en
`Panel_bloomberg.csv`). IV: `causal_core.iv_commodity_tot` / `iv_commodity_tot_plus_existentes`
→ `p7c_iv_reforzado.py` → `iv_reforzado_bbg.csv`.

**Resultado — primera etapa prácticamente NULA para `JLoss`:** `F ≈ 0,03` (correlación
*within*-país `CTOT_shock`↔`JLoss` ≈ −0,03), pese a que el mismo instrumento sí co-mueve con
el EMBI directamente (correlación *within* ≈ −0,16, signo esperado: mejores términos de
intercambio → menor spread). Añadido a los dos instrumentos existentes, la especificación
sobre-identificada de **3** instrumentos sigue **rechazando Sargan** (`p = 0,0014`, vs.
`p = 0,0003` con 2).

> **Lectura.** El choque de términos de intercambio por *commodities* es relevante para el
> **riesgo soberano agregado** (co-mueve con el EMBI) pero **no para la fragilidad bancaria
> específica** que mide `JLoss` — un resultado económicamente coherente (`JLoss` depende de
> apalancamiento/calidad de activos bancarios, no directamente del precio de las exportaciones
> del país) y no un artefacto de construcción (el instrumento tiene variación temporal *within*
> real, tabla de rangos en `ctot_shock_bbg.csv`). **No cierra la identificación causal del
> canal de nivel** — igual que los dos instrumentos anteriores. Conclusión de C2: **no forzar**
> más instrumentos; el peso de H1 sigue en OLS+EF y proyecciones locales (`paper2_empirico.tex`
> §6.8, ya reescrito con este resultado).

### H4a / H4b (triple interacción con concentración) — no identificados

β3 (JLoss×D, HHI centrado): estructural +32,5 (t = +0,55), anual +23,3 (t = +0,53) —**signo
predicho, no significativo**—, trimestral −4,0 (t = −0,12). β4 (JLoss×D×HHI): estructural
+139 (t = +0,39), anual +171 (t = +0,81), trimestral ≈ 0 (t = −0,54) — los tres con IC de
bootstrap de bloques cruzando el cero holgadamente. Sin respaldo y sin poder, igual que en el
panel de CDS. Detalle completo (IC90 bootstrap de bloques y P(β4>0), 13 países, panel EMBI
vigente): (`bbg/fase5_bbg.csv`, `p3_causal_fase5.py`, `fit_f5`, *cluster* por país, *bootstrap*
de bloques por país B=1000).

| HHI | N | β3 (JLoss×D) | t | β4 (JLoss×D×HHI) | t | P(β4>0) boot | IC90 boot bloques | rango LOO (β4) |
|---|---:|---:|---:|---:|---:|---:|---|---|
| estructural (GFDD, nivel) | 721 | **+32,5** | +0,55 | +139 | +0,39 | 43 % | (−715, +611) — incluye 0 | [−201, +368] |
| anual (GFDD, serie) | 721 | **+23,3** | +0,53 | +171 | +0,81 | 68 % | (−301, +620) — incluye 0 | [−45, +354] |
| trimestral (`HHI_q`) | 706 | **−4,0** | −0,12 | ≈0 (−0,02) | −0,54 | 54 % | (−0,07, +0,07) — incluye 0 | [≈0, ≈0] |

> Esta tabla es la fuente de `bbg/fase5_bbg.csv` leída en vivo (columnas `N`, `b3`, `t3`, `b4`,
> `t4`, `p_b4_pos`, `ci90`, `loo`): `N`=721/721/706, 13 países en las tres filas — confirmado
> que es el panel EMBI vigente (13 países, `EMBI_bps` como variable dependiente en
> `p3_causal_fase5.py::load_for_causal`), no un residuo del panel CDS de 14 países. La misma
> tabla, sin la columna `N` y con el resto de columnas idéntico, vivía antes solo en la
> Sección~6 (§ "Puente OI ↔ datos: H4a y H4b", parte legada del panel CDS de 14 países) — se
> replica aquí en la sección superior vigente porque es el detalle que cita la prosa de
> `paper2_empirico.tex` §7.4.

### Placebo temporal (destruir la estructura de GaR, B = 600)

Reshuffle global (null exacto): θ medio ≈ +0,01, P(placebo ≤ obs) = 0,12. Con θ observado
= −0,16 (n.s.), el placebo es **consistente con la no-significancia**: el observado no está
en la cola de la distribución nula.

### Regresor generado (GaR)

θ estable a perturbar GaR con ruido de hasta 25 % de su sd (−0,161); a 50 % atenúa a −0,151.
El error de medición **atenúa** — el θ verdadero es, si acaso, más negativo.

### Otras pruebas de robustez (M2, 13 países, panel EMBI vigente)

Fuente: `bbg/robustez_bbg.csv` (columnas `spec,theta,se,t,p,N,paises,b1,b2,R2w`; recordar
β3 = −θ al leer esta tabla en la convención `D=−GaR` de la prosa).

| Prueba | N | θ | β3 = −θ | t (β3) | p |
|---|---:|---:|---:|---:|---:|
| **sin deuda/PIB del vector de controles** | 614 | −0,1833 | **+0,18** | **+0,99** | 0,322 |

> La interacción se mantiene con el signo predicho al excluir la deuda/PIB del vector de
> controles domésticos: β3 = +0,18 (t = 0,99), esencialmente igual al β3 = +0,16 (t ≈ 0,7‑1,1
> según la especificación) de la Tabla de batería con el vector completo de 6 controles — el
> resultado no depende de qué control específico se incluya. Prosa:
> `paper2_empirico.tex`, "Otras pruebas" (§7.6, robustez).

### Endogeneidad `Ryr` ↔ EMBI (2026-09-10, indicación del coguía)

El rendimiento soberano 10Y (`Ryr`, moneda local) alimenta el FCI vía el subíndice de tasa
`iRyr = (VRyr + CDIFF)/2`. `CDIFF` = (yield real local − yield real EE.UU.) menos su mínimo
móvil de 2 años → el único objeto tipo-spread dentro del FCI (se solapa conceptualmente con
el EMBI, la DV). `p9_diag_ryr.py` traza la atenuación del vínculo con el EMBI en cada paso
(13 países del panel, N ≈ 701–721):

| paso de construcción | corr con EMBI (pooled) | corr within-país |
|---|---|---|
| `Ryr` (nivel, %) | 0,60 | 0,23 |
| `Ryr − Ryr_US` (spread crudo) | **0,68** | 0,37 |
| contribución tipo-`CDIFF` a `iRyr` (estandarizada) | **0,07** | −0,08 |
| `iRyr` (subíndice de tasa) | 0,14 | 0,12 |
| `iRyr` sin `CDIFF` | 0,06 | 0,20 |
| `FCI` | 0,22 | 0,23 |
| `FCI` sin `CDIFF` | 0,19 | 0,26 |
| `D = −GaR` (serie oficial) | 0,34 | 0,43 |

> **Lectura.** El spread crudo `Ryr − Ryr_US` sí co-mueve con el EMBI (0,68), pero la
> transformación de `CDIFF` (diferenciación + piso móvil + estandarización expansiva por
> máximo) lo convierte en un objeto casi **ortogonal al EMBI (0,07)**. La circularidad
> mecánica está en buena medida rota por la propia construcción del FCI antes de llegar al
> GaR. `corr(FCI, FCI_sin_CDIFF) = 0,91`; `corr(iRyr, iRyr_sin_CDIFF) = 0,52`. El EMBI y el
> CDS **nunca** entran al FCI ni al GaR (verificado en `fci_engine.py` / `gar_engine.py`).

**Robustez (rehacer el GaR sin `CDIFF`) — θ ES ROBUSTO.** `build_fci_no_cdiff.py` regenera el
FCI de los 18 países del pool con `iRyr = VRyr` (flag `drop_cdiff` en
`fci_engine.compute_fci`) → `GaR_panel_all18_noCDIFF.xlsx`. `gar_insample_robustez.py`
re-estima el GaR con un único ajuste sobre toda la muestra (in-sample, no ventana expansiva),
con y sin CDIFF → `gar_insample_{base,noCDIFF}.csv`. **`corr(GaR_sin_CDIFF, GaR_con_CDIFF) =
0,985`** (el FCI cambia con `corr = 0,91`, pero entra al GaR sólo como residuo ortogonalizado
al VIX con coeficiente pequeño). Re-estimación de `p2`/`p9` (`p9_robustez_gar_nocdiff.py` →
`robustez_gar_nocdiff.csv`):

| serie de GaR | β₃ muestra completa | β₃ fuera de crisis (spec crisis) | Backstop β₃+β₄ (Wald p) | EMstress β₃+β₄ (Wald p) |
|---|---|---|---|---|
| oficial (ventana expansiva, con CDIFF) | +0,19 (t=1,18, n.s.) | +0,84 (t=2,0) | −0,11 (0,27) | +1,05 (<0,001) |
| in-sample, con CDIFF | +0,22 (t=1,34, n.s.) | +0,82 (t=2,3) | −0,10 (0,21) | +1,03 (0,003) |
| **in-sample, SIN CDIFF** | **+0,23** (t=1,34, n.s.) | **+0,86** (t=2,8) | **−0,11** (0,15) | **+1,15** (0,001) |

> **Conclusión.** Quitar del GaR el único término que se solapa con el spread soberano
> (`CDIFF`) **no mueve ningún resultado**: β₃ muestra completa +0,19 → +0,23; β₃ fuera de
> crisis +0,84 → +0,86; la cancelación bajo `Backstop` y la supervivencia bajo `EMstress`
> se mantienen. La preocupación de endogeneidad es conceptualmente válida pero
> cuantitativamente inmaterial. La re-estimación completa en ventana expansiva
> (`phase2_gar_panel_all18_noCDIFF.py` + `run_gar_all18_noCDIFF.sbatch`, NLHPC) queda
> disponible pero, dado `corr = 0,985`, es muy improbable que cambie la conclusión.

### Bootstrap de regresor generado (C1, 2026-09-15/17) — COMPLETO, resultado: no cambia ninguna conclusión

Objetivo (punto C1 del plan de árbitro): un SE de `β₃` que propague el error de estimación de
la *primera etapa* del `GaR` (hoy el SE de Driscoll-Kraay trata al `GaR` como un dato fijo —
el problema clásico de *generated regressors*, Pagan 1984).

**Diseño — block bootstrap por país.** `c_hat(tau)`/`b_hat(tau)` (la función cuantil y la
pendiente sobre `g_GDP, VIX, FCI_VIX_res`) son parámetros **compartidos** entre los 18 países
del *pool* GaR; `a_hat_i` es específico de cada país y está bien identificado con ~125
trimestres propios (no es el objeto de incertidumbre que este bootstrap busca propagar). En
cada réplica: se remuestrean CON REEMPLAZO los 18 bloques-país completos (preservando su
estructura temporal interna), se re-ajusta el LP de regresión cuantílica de panel
(`gar_engine.fit_pfe`) → `c_hat*, b_hat*`; se proyecta el `GaR` de los 13 países del panel EMBI
usando `c_hat*, b_hat*` + su PROPIO `a_hat_i` (de la corrida real, sin remuestrear); se
re-estima `β₃` (M2, muestra completa) y `β₃+β₄` (Backstop/EMstress) sobre el panel Bloomberg
real con ese `GaR`-réplica. `sd(β₃*_{1..B})` = SE bootstrap.

**Validación de la aproximación de fidelidad reducida (`n_tau=19` en vez de 39, necesaria por
costo — el LP escala ~cuadrático en `n_tau`; 39→~250s/ajuste, 19→~57s/ajuste; `tau_min =
1/(19+1) = 0,05` coincide EXACTO con `GaR=Q(0,05)`, sin extrapolación):** un ajuste único (sin
remuestrear) a `n_tau=19` reproduce de cerca los números oficiales —

| | β₃ (M2, completa) | β₃ (fuera de crisis) | Backstop β₃+β₄ (p) | EMstress β₃+β₄ (p) |
|---|---|---|---|---|
| oficial (`n_tau=39`, GaR expansivo) | +0,16 (p=0,26) | +0,81 (p=0,051) | −0,03 (0,766) | +1,05 (<0,001) |
| ajuste único `n_tau=19` (in-sample) | +0,22 (t=1,34) | +0,82 (t=2,28) | −0,10 (0,206) | +1,03 (0,003) |

`1_Codigo/Panel/bbg/p10_boot_gar.py validar` → `bbg/gar_true_ntau19.csv`.

**Ejecución local — DESCARTADA.** La máquina de desarrollo (8GB RAM, ~570–850MB libres de
base con Chrome/VSCode/Claude Code/Defender/WSL ya corriendo) mató el proceso por falta de
memoria **3 veces** (4 *workers*, 2 *workers*, e incluso 1 solo proceso en serie — este último
murió en la primera réplica, justo después de que el mismo ajuste tuvo éxito como ancla,
señal de que es presión de memoria del sistema, no un defecto del script). B=200 con 4
*workers* alcanzó a completar 65/200 réplicas (48 min) antes de morir.

**Camino elegido: NLHPC, fidelidad completa (decisión del usuario, 2026-09-15).**
`1_Codigo/GaR/individuals/nlhpc_gar_all18/p10_boot_gar_nlhpc.py` (autocontenido, solo
`numpy/scipy/pandas/openpyxl` — no requiere `linearmodels`, que `venv_gar/` no tiene) +
`run_boot_gar_nlhpc.sbatch` (8 CPUs, 64GB, 24h, *checkpoint*/resume igual que
`run_gar_all18_noCDIFF.sbatch`). Corre SOLO la primera etapa (`n_tau=39`, B=500) y escribe
`gar_replicas_nlhpc.csv` (seed, country, quarter, GaR — una fila por país-trimestre-réplica).
La lógica de remuestreo/proyección fue verificada end-to-end con un *dry run* barato
(`n_tau=9`, réplica 0: 1400 filas, 18 países, esquema correcto). La segunda etapa
(`β₃/β₄` por réplica, trivial en tiempo/memoria) se corre LOCAL sobre el resultado:
`python 1_Codigo/Panel/bbg/p10_boot_gar.py segunda_etapa gar_replicas_nlhpc.csv` →
`bbg/boot_gar_bbg.csv` (mismo esquema que hubiera producido el bootstrap local).

**Ejecución en NLHPC — completa (job 13095760, 2026-09-17).** `sbatch run_boot_gar_nlhpc.sbatch`
en `~/nlhpc_gar_all18/`: **B=500 réplicas, fidelidad completa (n_tau=39), 8 *workers*, 500/500
sin errores**, 171,9 min (2h52m). `gar_replicas_nlhpc.csv` (700.000 filas) traído de vuelta;
segunda etapa corrida local (`p10_boot_gar.py segunda_etapa`, trivial en tiempo — segundos):

| Cantidad | Punto (vigente\*) | SE segunda etapa (DK/Wald) | SE *bootstrap* (1ª etapa, C1) | **SE combinado** | **p combinado** |
|---|---:|---:|---:|---:|---:|
| β₃ (M2, muestra completa) | +0,188 | 0,159 | 0,032 | **0,162** | **0,248** (vs. 0,239 sin corregir) |
| β₃ (fuera de crisis) | +0,838 | 0,414 | 0,087 | **0,423** | **0,048** (vs. 0,043) |
| β₃+β₄ *Backstop* | −0,105 | 0,095 | 0,023 | **0,098** | **0,284** (vs. 0,270) — no rechaza |
| β₃+β₄ *EMstress* | +1,051 | 0,283 | 0,159 | **0,324** | **0,0012** (vs. 0,0002) — sigue rechazando |

\* Punto estimado usando el `GaR` **vigente** de `Panel_bloomberg.csv` (ventana expansiva, con
Rusia en el *pool*, ver nota de vintage más abajo) — coincide con la fila "oficial (ventana
expansiva, con CDIFF)" de la tabla de robustez `Ryr` de arriba (+0,19 redondeado). `SE_combinado
= sqrt(SE_DK² + SE_boot²)` (Murphy–Topel/Pagan simplificado: como el diseño mantiene fija la
segunda etapa —el panel EMBI real— entre réplicas, `sd(β₃*)` aísla la varianza que aporta
*solo* la primera etapa, que se SUMA en cuadratura a la varianza de segunda etapa ya conocida,
no la reemplaza).

> **Conclusión de C1.** Propagar el error de estimación de la primera etapa del `GaR` **no
> cambia ninguna conclusión cualitativa**: la contribución de la primera etapa a la varianza
> total es pequeña frente a la de la segunda etapa (SE crece 2–15 % según la fila), y los
> cuatro `p`-valores se mueven en la tercera cifra decimal. β₃ en muestra completa sigue sin
> ser significativo; β₃ fuera de crisis sigue en el margen del 5 %; la cancelación bajo
> *Backstop* sigue sin rechazarse; la supervivencia bajo *EMstress* sigue siendo claramente
> significativa (p=0,0012). La inferencia DK/Wald ya reportada en el resto de este documento
> **no estaba subestimando de forma material** la incertidumbre por tratar al `GaR` como dato.

> **Nota de vintage (hallazgo de esta verificación, 2026-09-17).** Al anclar el punto estimado
> del bootstrap se confirmó DIRECTAMENTE (no solo por la nota de la re-ejecución de arriba) que
> `Panel_bloomberg.csv` **ya tiene el `GaR` de 18 países (con Rusia) desde antes de esta
> sesión** (`git log` → commit `d4fcdef`; `GaR` de `Panel_bloomberg.csv` es byte-idéntico a
> `gar_panel_all18.csv`). Por eso el β₃ M2 "vigente" (+0,188, re-ejecutando `p2_regresiones.py`
> en vivo) difiere ligeramente del que cita la tabla "★ Resultado central — H3" de abajo
> (+0,160) — esa tabla y la prosa de la tesis siguen sin actualizarse tras la re-ejecución
> 2026-09-06, tal como advierte la nota de arriba, con exactamente la magnitud de deriva que
> esa nota anticipaba (|Δ|≈0,03). No cambia la decisión de la Parte D (diferir la propagación
> hasta tener Argentina) ni ninguna conclusión — se deja registrado aquí porque el trabajo de
> C1 lo tocó directamente. Todo el trabajo de crisis-interacción y endogeneidad `Ryr` de esta
> sesión (secciones de arriba) ya usaba el `GaR` vigente (con Rusia) vía `gar_panel_all18.csv`,
> así que es internamente consistente con este resultado de C1.

Archivos: `1_Codigo/GaR/individuals/nlhpc_gar_all18/gar_replicas_nlhpc.csv` (primera etapa, 700k
filas) + `1_Codigo/Panel/bbg/boot_gar_bbg.csv` (segunda etapa, 500 filas: `seed,N,b3,t3,p3,...`).

### Coeficientes de control en M2 — advertencia

Bajo FE país + FE tiempo, los controles domésticos son interpolaciones lineales de datos
anuales; sus coeficientes **no tienen signo económico fiable** (deuda/PIB sale con signo
negativo, corr. within EMBI–deuda solo +0,10). Se reportan como controles, no se interpretan.

### Diagnósticos del panel (M2, 13 países, panel EMBI vigente)

Fuente: `bbg/diagnosticos_bbg.csv` (columnas `pesaran_CD,pesaran_p,AR1_resid,N,R2_within,R2_overall`).

| Diagnóstico | Valor | N |
|---|---:|---:|
| Prueba de Pesaran (CD, dependencia transversal) | CD = −1,07; p = 0,28 (no rechaza independencia) | 614 |
| Autocorrelación serial de primer orden de los residuos | ≈ 0,87 | 614 |
| R² *within* / *overall* (M2, FE país+tiempo) | 0,446 / −7,62 | 614 |

> La prueba de Pesaran no rechaza la independencia transversal de los residuos una vez
> incluidos los efectos fijos de tiempo; se mantienen de todos modos los errores de
> Driscoll–Kraay por la autocorrelación serial detectada. Prosa: `paper2_empirico.tex`
> §7.7 ("Controles macroeconómicos y diagnósticos del panel").

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

`EMBI = α_i + δ_t + β1·JLoss + β2·D + β3·(JLoss×D) + β4·(JLoss×D×HHI) + β·(JLoss×HHI) + β·(D×HHI) + …`,
`D = −GaR`, **HHI centrado** ⇒ β3 = complementariedad *en el HHI medio* (cantidad con sentido
económico; predicción del modelo OI: **β3 > 0**). Fuente: `bbg/fase5_bbg.csv`
(`p3_causal_fase5.py`, `fit_f5` con *cluster* por país; bootstrap de bloques por país B=1000).

| HHI | β3 (JLoss×D) | t | β4 (JLoss×D×HHI) | t | P(β4>0) boot | IC90 boot bloques | rango LOO (β4) |
|---|---:|---:|---:|---:|---:|---|---|
| estructural (GFDD, nivel) | **+32,5** | +0,55 | +139 | +0,39 | 43 % | (−715, +611) — incluye 0 | [−201, +368] |
| anual (GFDD, serie) | **+23,3** | +0,53 | +171 | +0,81 | 68 % | (−301, +620) — incluye 0 | [−45, +354] |
| trimestral (`HHI_q`, N=706, 13 países) | **−4,0** | −0,12 | ≈0 (−0,02) | −0,54 | 54 % | (−0,07, +0,07) — incluye 0 | [≈0, ≈0] |

> **H4a (predicción β3 > 0):** con la triple interacción incluida, β3 sale con el **signo
> predicho (positivo)** con los dos proxies del GFDD —+32,5 (estructural) y +23,3 (anual)—
> pero **no es significativo** (t ≈ 0,5); con la concentración trimestral es ≈ 0 (−4,0,
> t = −0,12). En esta parametrización **β3 no está identificado** (t < 1 en los tres casos).
> El test limpio de H4a es el término `JLoss × D` **sin** HHI (§1 y §"Heterogeneidad"):
> β3 = +0,16 en la muestra completa (n.s.) y **+0,47 (t = 2,29, p = 0,023) en el núcleo de
> 11 EM** — ahí sí con el signo del modelo y significativo.
> _Corrección 2026-09-07: la versión previa de esta sección decía "signo opuesto al
> predicho"; era un error — +32,5 y +23,3 tienen el mismo signo que la predicción β3 > 0.
> La lectura correcta es "no identificado / no significativo", no "signo equivocado"._
>
> **H4b (predicción β4 > 0): NO identificado.** El punto estimado de β4 es pequeño y no
> significativo con los tres proxies (+139, +171, ≈0; |t| < 1) y el IC90 del bootstrap de
> bloques por país cruza el cero holgadamente; P(β4>0) entre 43 % y 68 % — sin señal en
> ninguna dirección. Contrasta con la reconstrucción regulatoria v8 (+721, t = +2,98), de
> dispersión transversal de `JLoss` mucho mayor. La predicción distintiva del modelo de OI
> **no encuentra respaldo pero tampoco se rechaza**: no hay potencia con 13 *clusters* de
> país y un HHI casi invariante en el tiempo.
> (Redacción de prosa: "no identificado / impreciso", NO "significativo en la dirección
> equivocada" NI "signo empírico negativo".)

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
- **H4a (β3 > 0), triple interacción:** **no identificado** — con la triple interacción
  incluida (HHI centrado), β3 sale con el **signo predicho** pero no significativo con los
  dos proxies del GFDD (+32,5 y +23,3; |t| < 0,6) y ≈ 0 con la concentración trimestral
  (−4,0, t = −0,12). El test con potencia de H4a es `JLoss × D` **sin** HHI (§1 y
  "Heterogeneidad"): +0,16 completa (n.s.), **+0,47 (t = 2,29, p = 0,023) en el núcleo de
  11 EM**. Ver §6.
- **H4b (β4 > 0):** **no identificado** — el bootstrap de bloques por país deja el IC90
  cruzando el cero holgadamente con los tres proxies de concentración (β4 = +139, +171, ≈0;
  |t| < 1; P(β4>0) 43 %–68 %), incluida la concentración **trimestral** construida de los
  mismos bancos de `JLoss`. No se afirma dirección. Ver §6.

## 8. EMBI extendido — panel PARALELO, no canónico (2026-09-25)

`p1_build_panels.py --embi-ext` → `Panel_bloomberg_embiext.csv`, `embi_bbg_quarterly_embiext.csv`,
`cobertura_panel_bbg_embiext.csv`, `embi_empalme_diag_bbg.csv`. No toca el panel canónico
(el modo canónico reproduce las 35 columnas de `Panel_bloomberg.csv` idénticas).

- **Fuentes revisadas:** `2_Datos/embi.xlsx` ya era la fuente vigente (JPM EMBI GD diario).
  `2_Datos/EMBI_real_8countries_2006_2014.csv` (FMI GFSR, trimestral 2010Q1–2014Q4) se empalma
  **solo donde el xlsx no tiene dato**. `1_Codigo/Panel/Serie_Historica_Spread_del_EMBI.xlsx`
  (subíndices EMBI GD LatAm, en %) no aporta trimestres nuevos: LatAm ya está cubierta y
  Argentina no tiene GaR. El World Bank GEM ya no publica el EMBI por país (API revisada
  2026-09-25: 36 series, ninguna de spreads).
- **Empalme GFSR:** solape con el xlsx en 80 trimestres (China, Hungría, Polonia, Turquía);
  corr pooled **0,94** (0,82–0,90 por país), ratio mediano xlsx/GFSR **1,02** → sin reescalar.
- **Ganancia:** Indonesia y Sudáfrica +20 trimestres cada una (2010Q1–2014Q4). Pakistán y
  Bulgaria también se llenan pero no aportan (sin GaR en 2010–14 / excluida por JLoss).
  Muestra de estimación 721 → **761** (Tabla 1 niveles), 614 → **654** (crisis con controles).
- **Resultados en niveles (M4 / CM4, FE país+tiempo) vs canónico:** sin crisis β₃ = +1,182***
  (canónico +1,171***); completa +0,177 n.s. (+0,176); crisis vector único β₃ = +0,804*
  (+0,811*), β₃+β₄ = −0,045 (p=0,67); Backstop β₃+β₄ = −0,127 (p=0,26; canónico −0,105, p=0,27);
  EMstress +1,155 (p<0,001; canónico +1,051). **Ningún resultado cambia de lectura.**
- Estimar sobre este panel: `JLOSS_PANEL_CSV=<ruta>/Panel_bloomberg_embiext.csv python p11_tablas_latex.py`
  (y `p12_tablas_latex_lnlag.py`) → `4_Redaccion/tablas_regresiones/*_embiext.tex`.
- **Pendiente para cerrar el hueco grande** (IDN/PHL/ZAF 2004–2009 y 2015–2023Q2; India
  2007Q2–2012Q3): bajar de Bloomberg los subíndices J.P. Morgan EMBI GD por país y dejarlos en
  `2_Datos/embi_extra_<fuente>.csv` (`country,date,EMBI_bps`); `p1 --embi-ext` los toma solo,
  con prioridad sobre GFSR y el mismo diagnóstico de empalme.

## 9. EMBI Argentina en el panel CANÓNICO (2026-09-25)

La entrada §8 (misma fecha) descartó `Serie_Historica_Spread_del_EMBI.xlsx` para el panel
**paralelo** `--embi-ext` porque en ese momento Argentina no tenía GaR y por tanto no aportaba
a la muestra de estimación. Petición separada del usuario: agregar el EMBI de Argentina al
panel **canónico** igual, como paso preparatorio para incorporarla a las regresiones. Esto
**no** contradice §8: son dos peticiones distintas en el mismo día.

**Actualización (mismo día): el GaR también se integró.** `_merge_gar_argentina_sinRyr.py`
agregó las 84 filas de ARGENTINA de `gar_panel_all19_ARGsinRyr.csv` (GaR sin bloque Ryr,
ventana VSTX acortada — ver la sección de esta conversación / `_fci_sin_ryr.py`) a
`gar_panel_all18.csv` (el archivo que `p1_build_panels.py::load_gar()` lee), sin tocar las
filas de los 18 países existentes. Con EMBI + GaR ya presentes, **Argentina entra a la
muestra de estimación: 35 observaciones, 2017Q2–2025Q4** (`n_estimacion` pasó de 0 a 35;
la muestra principal EMBI+JLoss+GaR pasó de 721 a **756** obs, de 13 a **14** países).
Nótese que esta es la desviación metodológica documentada arriba (ventana ~9.4 años en vez
de ~10 años, solo para Argentina) — cualquier regresión que incluya a Argentina hereda esa
salvedad y debe mencionarla si se usa en la tesis.

- **Cambio en `p1_build_panels.py`:** nueva función `embi_argentina_quarterly()`, corre en el
  modo canónico (sin `--embi-ext`) además del paralelo. Fuente: columna `Argentina` de
  `Serie_Historica_Spread_del_EMBI.xlsx` (misma familia JPM EMBI Global Diversified subíndices
  que `2_Datos/embi.xlsx`, que no incluye Argentina en su recorte de países).
- **Escala:** el archivo está en **porcentaje**, no en pb. Verificado con Brasil y México
  (ambos presentes en los dos archivos, solape 2007-10-29..2025-12-17, n=4514 días): ratio
  mediano xlsx/serie-histórica = **100,00** (99,996–100,001), corr = **0,99999** en los dos
  países → se multiplica x100 sin reescalar. Diagnóstico: `embi_argentina_diag_bbg.csv`.
- **Cobertura resultante:** `EMBI_bps` Argentina 2007Q4–2025Q4 (73 trimestres, "continua").
  Valores en trimestres de crisis conocidos, para trazabilidad: 2008Q4 = 1697 pb (GFC),
  2014Q3 = 709 pb (default selectivo "Griesafault"), 2019Q3 = 1489 pb (shock post-PASO),
  2020Q2 = 3108 pb (pico COVID + renegociación de deuda), 2023Q3 = 2102 pb (sequía/crisis
  pre-Milei).
- **En este primer paso (solo EMBI) no cambió ningún número publicado:** Argentina aún no
  tenía GaR, así que `n_estimacion` seguía en 0 y ninguna fila de ningún otro país cambió
  (verificado celda a celda; las únicas discrepancias de texto eran ruido de re-serialización
  de punto flotante en `USD_NEER`/`CTOT_shock`/`JLoss_x_GaR`, revertidas a los valores ya
  committeados para mantener el diff acotado). Ver la actualización de arriba: el GaR se
  integró después, en el mismo día, y **eso sí** agrega 35 observaciones nuevas a la muestra
  de estimación principal.

**Segunda actualización (mismo día): controles domésticos + batería con Argentina.**
`p0_controles_all.py` se extendió (Argentina agregada a la lista `NEW`, ISO3=ARG) para traer
deuda/PIB y balance fiscal (IMF WEO), cuenta corriente y reservas/PIB (World Bank), e
inflación YoY / REER (desde `CPI_ARGENTINA.csv` / `rEER_ARGENTINA.csv`, mismo mecanismo que
el resto de `NEW`). Cobertura: debt_gdp/fisc_bal 108 trimestres (2000Q1 en adelante),
infl_yoy solo 35 (limitado por el mismo CPI oficial corto). Valores verificados por
plausibilidad histórica: deuda/PIB 147 % en 2002Q3 (post-default), 40 % en 2012Q3, 97 % en
2020Q1 (COVID); inflación 25–48 % interanual durante la crisis 2018–19, ~31–39 % en 2025–26.
Filas de los 17 países existentes: 0 diferencias tras re-ejecutar (mismo vintage IMF/WB).

Con EMBI + GaR + controles ya presentes, Argentina **entra también a la batería de crisis**
(`p9b_bateria_crisis.py`, que antes la excluía por completo al faltarle los 6 controles):
N pasa de 614 a **647** (+33 obs). Esto **sí cambia lectura** del resultado ya publicado en
`tab:crisis` (CM4, FE país+tiempo, Panel B Backstop/EMstress):

| | publicado (17 países) | con Argentina (N=647) |
|---|---|---|
| β₃ (JxD, fuera de crisis) | +0,837 (t=+2,02, p=0,044) | +0,609 (t=+0,49, **p=0,624 — ya no significativo**) |
| β₃+β₄ Backstop | −0,105 (p=0,270, n.s.) | +0,710 (p=0,124, sigue n.s., **cambia de signo**) |
| β₃+β₄ EMstress | +1,051 (p=0,0002) | +1,428 (**p=0,024, sigue significativo pero mucho más débil**) |

Mismo patrón en Panel A (vector único de crisis) y en las otras estructuras de FE (T, P): el
coeficiente "fuera de crisis" pierde significancia en FE=T y FE=PT; EMstress se mantiene
significativo en casi todas las combinaciones pero con p mayor; Backstop se vuelve
marginalmente significativo en FE=P (p=0,032) donde antes no lo era (p=0,62) — resultado
mixto, no unidireccional.

El chequeo de auto-verificación de `p9b_bateria_crisis.py` (comparación exacta con
`tab:crisis`) **falla intencionalmente** con esta muestra — es el comportamiento esperado al
cambiar deliberadamente la muestra, no un bug; el CSV se guarda de todas formas antes de la
verificación. `bateria_bbg.csv` y `bateria_crisis_bbg.csv` quedaron sobrescritos con estos
números (con Argentina); las versiones previas (17 países) se conservaron como
`_bateria_bbg_old.csv` / `_bateria_crisis_bbg_old.csv` para comparación. **Nada de esto se
propagó todavía a `4_Redaccion/` ni a `tab:crisis`** — requiere rerun explícito de
`p11_tablas_latex.py`/`p12_tablas_latex_lnlag.py` y una decisión editorial sobre si adoptar
esta muestra ampliada en la tesis.

## 10. Especificación PRINCIPAL del paper: log-log rezagada sobre el panel embiext (2026-09-29)

Base de `4_Redaccion/envios/paper_empirico/cuerpo.tex`, que es también el capítulo de la tesis
(`tesis/main.tex` lo incluye; `investigacion.tex` queda como versión anterior, sin compilar).
Panel: `Panel_bloomberg_embiext.csv` (13 países, sin Argentina; IDN/ZAF 2010–14 con FMI GFSR).

    ln EMBI_it = a_i + d_t + b1 ln JLoss_i,t-1 + b2 D_i,t-1 + b3 ln JLoss_i,t-1 x D_i,t-1 (+ w'X_it) + e
    D = -GaR (pp); ln JLoss y D centrados; DK (Bartlett).

Reproducir: `JLOSS_PANEL_CSV=<ruta>/Panel_bloomberg_embiext.csv python p12_tablas_latex_lnlag.py`
(Tablas 1–2, con Panel C de controles) y `python p13_figuras_paper.py` (20 figuras, cuadros
descriptivos y **`paper_lnlag_numeros.csv`, fuente de toda cifra del texto**).

| Cantidad (M4, FE país+tiempo) | Valor |
|---|---|
| Principal (Panel A col. 1, sin controles, N=765): b1 / b2 / b3 | +0,0985*** / +0,0324** / −0,0112 (p=0,112) |
| Sin crisis (Panel B, N=656) | +0,0866** / +0,0502*** / +0,0045 (p=0,67) |
| Con 6 controles (Panel C, N=649) | −0,0076 (p=0,86) / +0,0281** / −0,0065 |
| Misma muestra N=649 sin controles | b1 = +0,107 (p=0,008) → la absorción es de los controles, conjunta |
| Crisis CM4, Backstop b3+b4 | −0,0146 (p=0,03) |
| Crisis CM4, EMstress b3+b4 (FE PT / T / P) | +0,026 (p=0,08) / +0,036 (p=0,04) / +0,036 (p=0,001) |
| Complementariedad implícita en niveles con b3=0 | +0,19 pb [0,01; 0,42] |
| b3 niveles/logs × contemporáneo/rezagado, sin crisis | +1,18*** / +1,29*** / −0,005 / +0,0045 |

**Lectura:** H1 y H2 se sostienen sin controles; H3 en elasticidades no (la complementariedad en
pb es la de la forma multiplicativa). Lo que elimina la interacción de niveles es el logaritmo,
no el rezago. La amplificación adicional aparece solo en EMstress 2015–16.

## 11. Especificación log-log rezagada CON Argentina (panel embiext_arg, 2026-09-29)

`JLOSS_PANEL_SFX=_embiext_arg python p1_build_panels.py --embi-ext` → `Panel_bloomberg_embiext_arg.csv`
(panel extendido de §8 + Argentina de §9; 14 países). No reemplaza al panel del paper
(`Panel_bloomberg_embiext.csv`, 13 países, verificado byte-idéntico). Tablas:
`JLOSS_PANEL_CSV=<ruta>/Panel_bloomberg_embiext_arg.csv python p12_tablas_latex_lnlag.py` →
`4_Redaccion/tablas_regresiones/tablas_regresiones_lnlag_embiext_arg.tex` (+ `_t1`, `_t2`, pdf).

| M4, FE país+tiempo | sin Argentina (paper, §10) | con Argentina |
|---|---|---|
| Panel A (N) — b1 / b2 / b3 | 765 — +0,0985*** / +0,0324** / −0,0112 (p=0,11) | 799 — +0,0964*** / +0,0326** / −0,0082 (p=0,28) |
| Panel B sin crisis | +0,0866** / +0,0502*** / +0,0045 | 682 — +0,0889** / +0,0485*** / +0,0071 (p=0,57) |
| Panel C con controles | −0,0076 / +0,0281** / −0,0065 | 682 — −0,0392 (p=0,44) / +0,0267** / −0,0039 |
| CM4 Backstop b3+b4 (PT) | −0,0146 (p=0,03) | −0,0120 (p=0,03) |
| CM4 EMstress b3+b4 (PT / T / P) | +0,026 / +0,036 / +0,036 | +0,024 (p=0,13) / +0,055 (p=0,01) / +0,054 (p<0,001) |

**Lectura:** Argentina no cambia ninguna conclusión del paper. H1 y H2 igual; H3 sigue sin
sostenerse en promedio; Backstop sigue negativo. EMstress se refuerza con FE de tiempo y de país,
pero con FE país+tiempo pierde significancia (p=0,13). Argentina hereda la salvedad de su GaR
(sin bloque Ryr, ventana corta).

## 12. Pruebas de árbitro sobre la especificación principal (2026-09-30)

`python p14_arbitro_lnlag.py` (panel embiext, 13 países) → `paper_arbitro_numeros.csv` (todas las
cifras), `tabla_arbitro_resumen.tex`, `tabla_arbitro_chari.tex`, figuras `*_arb`. El paper
(`cuerpo.tex`) se reescribió con esta evidencia: las asociaciones se reportan como tales, no
como efectos causales.

| Prueba | Resultado |
|---|---|
| Validación del wild bootstrap contra `p2.wild_boot` | idéntico (p = 0,143) |
| Canal inverso: ln JLoss_t ~ ln EMBI_{t-1} | +0,171 (p=0,009) |
| + adelantos: ln JLoss_{t-1} / ln JLoss_{t+1} | +0,058 (p=0,18) / +0,051 (p=0,23) |
| + ln EMBI_{t-1}: b1 corto / ρ / largo plazo | +0,005 (p=0,76) / 0,94 / +0,078 (p=0,72) |
| Wild cluster bootstrap (Webb, G=13): b1 / b2 / b3 | p = 0,33 / 0,20 / 0,89 |
| Proyecciones locales ln JLoss_{t-1}, h=0..6 | todas n.s. |
| IV on/off, USD, CTOT (F≈9–11) | +0,35 / −2,18 / +0,15, todas n.s.; Sargan p<0,001 |
| Bootstrap del GaR (500 réplicas): p combinado b1/b2/b3 | 0,003 / 0,049 / 0,122 |
| Backstop b3+b4, cluster país | −0,015 (p=0,40) — no significativo |
| EMstress extendido (taper + 2015-16 + 2018) | +0,013 (p=0,25); permutación p=0,39 (lugar 20/51) |
| Controles en t−4: b1 | +0,062 (p=0,17) |
| Canal JLoss_{t-1} → fisc_bal / reer / inflación / deuda | −0,69*** / −4,79*** / +3,34*** / +3,79** |
| Tabla estilo Chari: ln JLoss_{t-1} en 6 columnas | 0,107–0,164, todas p<0,01 |
| PE: H0 lineal / H0 log | rechaza (p<0,001) / no rechaza (p=0,30) |
| Box–Cox λ | 0,44 [0,38; 0,50] (excluye 0 y 1) |
| JLoss malla ancha: b1 / percentil: b1 | +0,067 (p=0,22) / +0,266 (p=0,002) |

## 13. Robustez a la forma funcional: especificación en niveles (2026-10-03)

Misma muestra (embiext, 13 países, N=765) y mismos rezagos, con EMBI en pb y JLoss_{t-1} en niveles.
Reproducir: `p12_tablas_latex_lnlag.py --niveles` (tablas `tablas_regresiones_nivlag_embiext*`),
`JLOSS_FORMA=nivlag python p13_figuras_paper.py` (figuras `*_nivlag`, `paper_nivlag_numeros.csv`),
`JLOSS_FORMA=nivlag python p14_arbitro_lnlag.py` (`paper_arbitro_nivlag_numeros.csv`) y
`python p15_comparacion_formas.py` (`tabla_robustez_niveles.tex`). El modo por defecto (lnlag)
reproduce byte a byte sus salidas anteriores.

| Prueba | Log-log (principal) | Niveles (pb) |
|---|---|---|
| β1 / β2 / β3 principal | 0,0985*** / 0,0324** / −0,0112 | 4,73*** / 3,24 (p=0,27) / 0,246 (p=0,34) |
| β3 sin crisis | 0,0045 | 1,294*** |
| β1 con 6 controles / controles t−4 | −0,008 / 0,062 | 2,74*** / 4,27*** |
| Canal inverso | 0,171*** | 0,014*** (100 pb → +1,4 JLoss) |
| β1 dinámica corto / largo plazo | 0,005 / 0,078 | 0,49 (p=0,07) / 5,19 (p=0,11) |
| Wild bootstrap p (β1/β2/β3) | 0,33 / 0,20 / 0,89 | 0,31 / 0,42 / 0,49 |
| EMstress 2015-16 (DK / cluster) | 0,026 (0,08 / 0,11) | 1,21 (<0,001 / 0,009) |
| Permutación EMstress | p=0,39 | p=0,41 |
| Backstop (DK) | −0,015 (0,03) | −0,085 (0,46) |

**Lectura:** en niveles la fragilidad resiste los controles y la amplificación aparece sin crisis y
en EMstress (incluso con cluster país), pero ningún coeficiente resiste el wild bootstrap y EMstress
no se distingue de ventanas al azar. Conclusión del paper sin cambios; la absorción por controles
es propia de los logaritmos.

## 14. Heterogeneidad por tipo de economía en la especificación vigente (2026-10-07)

`python p16_heterogeneidad.py` (logs) y `JLOSS_FORMA=nivlag python p16_heterogeneidad.py` (niveles)
→ `paper_heterogeneidad_numeros.csv` / `_nivlag.csv`. Re-estima la prueba de `p5_robustez_arbitro.py`
§2b (núcleo de 11 emergentes de financiamiento externo vs. Polonia + India), que solo existía sobre el
panel anterior en niveles contemporáneos. Panel embiext, 13 países, rezagos de la principal, EF país +
tiempo; wild cluster bootstrap con pesos de Webb (G=11). La principal se reproduce (N=765, β3=−0,0112).

| M4 solo núcleo (11 países) | Log-log | Niveles (pb) |
|---|---|---|
| β3 muestra completa (N=621): DK / wild | +0,011 (p=0,16 / 0,12) | +0,78 (p=0,018 / 0,046) |
| β3 completa con 6 controles (N=515): DK / wild | +0,004 (0,25 / 0,39) | +0,53 (0,007 / 0,042) |
| β3 sin crisis (N=533): DK / wild | **+0,034 (p<0,001 / 0,015)** | **+1,79 (p<0,001 / 0,002)** |
| β3 sin crisis con 6 controles (N=442): DK / wild | +0,004 (0,59 / 0,68) | +0,81 (0,010 / 0,12) |
| β3 sin crisis, leave-one-country-out (rango; p máx.) | 0,018–0,039; 0,08 | 0,87–1,92; 0,08 |
| β3 Polonia+India (modelo con interacciones de grupo), sin crisis | −0,118 (p=0,002) | −1,82 (p=0,02) |

**Lectura:** la amplificación adicional que el panel completo no muestra aparece en el núcleo de
financiamiento externo fuera de las crisis con respaldo, y es la única que resiste el wild bootstrap
en ambas formas funcionales sin controles. Salvedades: el grupo de contraste se definió a partir de la
versión anterior (no ex ante), en logaritmos los controles domésticos la absorben, y con 11 clusters la
inferencia sigue siendo frágil. Se reporta como evidencia condicional, no como hallazgo robusto.

## 15. Solapamiento del GaR con las variables financieras (2026-10-11)

Observación del profesor guía en la predefensa (2026-10-09): el FCI del GaR usa variables
financieras que se cruzan con JLoss y con los factores globales. `python p18_solapamiento_gar.py`
→ `paper_solapamiento_numeros.csv`. Para la parte C: `build_fci_no_stx.py` (FCI sin bloque bursátil,
corr. media 0,87 con el FCI base) y `gar_insample_robustez.py GaR_panel_all18_noSTX.xlsx noSTX`
(en `1_Codigo/GaR/individuals/nlhpc_gar_all18/`). Principal: log-log rezagada, EF país + tiempo.

| Prueba | Resultado |
|---|---|
| R² within de D sobre factores globales (VIX, Tesoro, HY, on/off) | 0,34 |
| R² de D sobre EF país + tiempo | 0,82 |
| Correlación parcial D–ln JLoss tras EF / VIF | 0,26 / 1,07 |
| Principal (referencia): b1 / b2 / b3 | 0,0985 / 0,0324 (p=0,033) / −0,0112 |
| Dos etapas, D limpio de factores globales, EF país + tiempo | 0,110 / 0,0331 (p=0,027) / −0,016 (p=0,04) |
| Ídem con solo EF país (ref. sin limpiar: b2 = 0,0174, p=0,07) | 0,191 / 0,0127 (p=0,17) / −0,013 |
| Dos etapas, D limpio de ln JLoss, EF país + tiempo | 0,125 / 0,0346 (p=0,013) / −0,023 |
| GaR in-sample base vs. sin bloque bursátil: corr. de D | 0,98 |
| b2 con GaR in-sample base / sin bloque bursátil (N=773) | 0,0389 (p=0,040) / 0,0451 (p=0,050) |
| Ídem sin crisis (N=662) | 0,0684 (p<0,001) / 0,0835 (p<0,001) |

**Lectura:** con EF de tiempo los factores globales ya están absorbidos (el residuo deja b2 igual);
el riesgo de cola y la fragilidad comparten poca variación (VIF 1,07); y quitar el bloque bursátil
del FCI no cambia nada. Sin EF de tiempo, en cambio, parte de la asociación del riesgo de cola es
global: limpio de factores globales deja de ser significativo.

## 16. Resiliencia de la política económica como moderador (2026-10-11)

Hipótesis del profesor guía: a mayor resiliencia (menos deuda/PIB, mejor balance fiscal/PIB, más
reservas/PIB), menor efecto de la fragilidad y del riesgo de cola sobre el spread. `python
p19_resiliencia.py` (y `JLOSS_FORMA=nivlag`) → `paper_resiliencia_numeros.csv` / `_nivlag.csv`.
R = promedio de z-scores de (−deuda/PIB, balance fiscal/PIB, reservas/PIB), estandarizado; g1 = J×R,
g2 = D×R. EF país + tiempo, N=670. Corr(R, ln JLoss) = −0,43; corr(R, D) = −0,33.

| | Log-log | Niveles (pb) |
|---|---|---|
| Efecto directo de R | −0,153 (DK p=0,001; cluster 0,38) | −3,5 (n.s.) |
| g2: D×R (DK / cluster / wild) | −0,014 (0,056 / 0,35 / 0,46) | −1,88 (0,25 / 0,36 / 0,43) |
| g1: J×R (DK / cluster / wild) | +0,053 (0,11 / 0,33 / 0,42) | +4,70 (<0,001 / 0,006 / 0,22) |
| g2 fuera de crisis | −0,024 (p=0,007) | −4,25 (p=0,009) |
| g2 cambio en crisis (GFC+COVID) | +0,023 (p=0,006) | +5,39 (p<0,001) |
| g2 en crisis (neto) | −0,001 (p=0,86) | +1,14 (p=0,10) |
| g1 fuera de crisis / en crisis | +0,086 (0,017) / +0,115 (0,058) | +4,74 / +5,57 (ambos p<0,001) |
| Efecto directo de R fuera / en crisis | −0,141 / −0,330 (ambos p<0,001) | −5,6 (n.s.) / −25,8 (p<0,001) |
| R medido en t−4: g2 (DK / cluster / wild) | −0,028 (0,002 / 0,089 / 0,14) | −4,22 (0,020 / 0,063 / 0,14) |

**Lectura:** (i) la resiliencia atenúa el efecto del riesgo de cola **fuera de crisis**, y esa
atenuación desaparece en las crisis sistémicas (analogía del seguro: cuando el choque afecta a todos,
el resguardo propio no reduce la sensibilidad); (ii) el nivel de resiliencia sí baja el spread, más
aún en crisis; (iii) para la fragilidad bancaria la hipótesis no se cumple: su efecto es mayor, no
menor, en países más resilientes (compatible con que un rescate creíble traslada el riesgo bancario
al soberano; conjetura). Nada de esto resiste el wild bootstrap con 13 países: evidencia sugerente.

**Calificada por §18.6 (2026-10-13):** lo que queda del índice es sugerente (solo Driscoll–Kraay); la
versión por componentes y la "ex ante" pasan a exploratorias; el lenguaje "atenúa" y la analogía del
seguro se leen como asociación, no como hallazgo. Corrección: el p de cluster del efecto directo de R
(−0,153) es 0,38 (`mod_r_p_pais`); 0,35 corresponde a la variante con triple interacción (−0,162).


## 17. Informe de árbitro: pruebas adicionales (2026-10-12)

Doce objeciones de un árbitro (ver `4_Redaccion/informe_arbitro.md`). Cada script reproduce primero la
principal (N=765, β1=0,0985, β3=−0,0112) y acepta `JLOSS_FORMA=nivlag`. Regla: se reporta todo, salga
como salga.

### 17.1 Estacionariedad, primeras diferencias y dos rezagos — `p21_estacionariedad.py`

- Fisher-ADF por país: rechaza raíz unitaria para ln EMBI, ln JLoss y D (p<0,001). Restando la media
  transversal de cada trimestre: JLoss y D siguen rechazando; **el spread no (p=0,14)**.
- Pesaran CD sobre los residuos de la principal: 18,4 con EF de país; −4,9 con EF país+tiempo (p<0,001).

| Primeras diferencias (N=750) | Log-log | Niveles (pb) |
|---|---|---|
| Δ fragilidad, EF país+tiempo (DK / wild) | **0,0368 (0,002 / 0,007)** | 1,02 (0,044 / 0,10) |
| Δ riesgo de cola (DK / wild) | −0,0022 (0,54 / 0,24) | −0,47 (0,58 / 0,69) |
| Δ interacción (DK / wild) | 0,0015 (0,31 / 0,45) | **0,188 (<0,001 / 0,008)** |
| Δ fragilidad, solo EF tiempo / sin EF | 0,0375 / 0,104 (p=0,009) | 1,04 / 3,54 (p=0,014) |
| M3 (sin interacción): fragilidad / cola | 0,0378 (0,002) / −0,0016 | 1,30 (0,007) / −0,09 |
| ADL: ρ del spread rezagado | 0,937 | 0,910 |
| ADL: J en t−1 / t−2 / suma | +0,034 (0,043) / −0,043 (<0,001) / −0,009 (0,58) | +1,40 (0,003) / −1,22 (0,009) / +0,18 (0,52) |
| ADL: D en t−1 / t−2 / suma | 0,000 / 0,003 / 0,004 (0,23) | −0,11 / 0,08 / −0,03 |

**Lectura:** el spread responde al **cambio** de la fragilidad, no a su nivel (los dos rezagos tienen
signo opuesto y tamaño similar). Es el único coeficiente del panel completo que resiste el wild
bootstrap. El riesgo de cola **no** tiene efecto en diferencias. La interacción en pb en diferencias
(0,19) coincide con la complementariedad implícita en la forma proporcional (+0,19, §12).

**Reemplazada por §18.2 (2026-10-13):** la lectura "el spread responde al cambio y no al nivel" y la de
precedencia temporal quedan retiradas. El 0,037 mezcla agregación temporal (EMBI promedio del
trimestre) con comovimiento dentro del mismo trimestre; con el spread de cierre la prueba limpia da
0,025 (wild 0,21). Sobre nivel frente a cambio los datos no informan. "Coincide" (0,188 frente a
0,19) también se retira: el intervalo de la implícita es [0,01; 0,42].

### 17.2 Inferencia: errores alternativos, tamaño y potencia, Holm — `p22_inferencia_potencia.py`

| | p β1 | p β2 | p β3 | Tamaño β1 / β2 | Potencia β1 / β2 |
|---|---|---|---|---|---|
| Driscoll–Kraay | 0,003 | 0,033 | 0,11 | 38 % / 27 % | 59 % / 60 % |
| Cluster por país | 0,28 | 0,13 | 0,53 | 20 % / 17 % | 28 % / 36 % |
| Wild cluster bootstrap | 0,33 | 0,20 | 0,89 | 11 % / 13 % | 17 % / 28 % |
| Cluster por trimestre | <0,001 | 0,002 | 0,04 | — | — |
| Cluster país y trimestre | 0,27 | 0,13 | 0,52 | — | — |

Simulación: S=150 muestras, y* = ajuste + w_país × residuo (Rademacher por país), B=199 réplicas
internas; tamaño = rechazo al 5 % con el efecto quitado; potencia = con el efecto estimado. Error
estándar de cada frecuencia: hasta 4 pp. **DK sobre-rechaza (un tercio de las veces bajo H0); el wild
está mejor calibrado pero detecta el efecto estimado ~1 de cada 5 veces.** Regla de lectura: resiste
wild = evidencia fuerte; solo DK = sugerente.

Holm (familia de 6 contrastes de la interacción, p de DK → corregido): núcleo sin crisis 0,0008 →
0,005; contraste núcleo vs. Polonia+India sin crisis 0,0018 → 0,009; Backstop 0,03 → 0,12; EMstress
0,08 → 0,24; principal 0,11 → 0,24; núcleo muestra completa 0,16 → 0,24.

**Simulación reemplazada por §18.3 (2026-10-13):** el diseño de p22 coincidía con el esquema de
remuestreo del wild bootstrap, rompía la dependencia entre países y usaba S=150. Con la simulación
nueva (p29, S=1000): Driscoll–Kraay 21–28 % de tamaño; wild 6–7 % de tamaño y 35 % / 67 % de potencia.
Los p reales y la corrección de Holm de esta sección siguen vigentes. El cluster por trimestre no es
válido en niveles (el spread es persistente).

### 17.3 Estrés conjunto — `p23_estres_conjunto.py`

ln EMBI = EF + a1·AltaJ + a2·AltaD + a3·(AltaJ×AltaD); indicadores de tercil alto, rezagados.

| | a1 | a2 | a3 (DK / wild) | Obs. conjuntas (obs. / esperadas) |
|---|---|---|---|---|
| Terciles por país | 0,091 (0,062) | 0,186 (<0,001) | −0,077 (0,14 / 0,23) | 168 / 87 |
| Terciles del panel | 0,116 | 0,179 | −0,041 (0,52 / 0,70) | 121 / 85 |
| Cuartiles por país | 0,118 | 0,125 | −0,122 (0,07 / 0,23) | 115 / 49 |
| Terciles por país, sin crisis | 0,120 | 0,147 | −0,061 (0,28 / 0,41) | 139 / 76 |
| Niveles (pb), terciles por país | 24,2 | 24,8 | −3,4 (0,74 / 0,67) | 168 / 87 |

**Lectura:** los riesgos coinciden el doble de lo esperado por azar, pero la coincidencia no agrega
nada por sobre la suma (a3 ≤ 0, nunca significativo con wild). Efectos aditivos. **Calificada por §18.1 (2026-10-13):** no hay evidencia de amplificación; no se descarta un extra de hasta un 30–40 % de la suma.

### 17.4 Medición, composición y magnitud — `p24_robustez_medicion.py`

| | β1 | β2 | β3 |
|---|---|---|---|
| CDS 5 años (N=635, 12 países; corr ln CDS–ln EMBI 0,83) | 0,206 (<0,001) | 0,013 (0,24) | 0,016 (0,049) |
| EMBI en la muestra con CDS | 0,114 (<0,001) | 0,008 (0,50) | 0,010 (0,19) |
| Panel de historia larga (10 países, N=689) | 0,087 (0,013; wild 0,39) | 0,035 (0,029; wild 0,16) | −0,012 (0,09) |
| Sin India (N=710) | 0,087 (0,035) | 0,030 (0,048) | −0,012 |
| Niveles: CDS / EMBI muestra CDS | 7,45 / 5,72 (ambos <0,001) | 2,64 / −0,30 (n.s.) | 0,89 (0,016) / 0,75 (0,018) |

Leave-one-country-out de los efectos de nivel (figura `fig_loo_efectos_lnlag` / `_nivlag`):
- β1 entre 0,034 y 0,168; significativo al 5 % en 11 de 13. **Sin Turquía: 0,034 (p=0,43)**; sin
  Colombia 0,070 (p=0,10). En niveles: 12 de 13; sin Turquía 0,63 (p=0,54).
- β2 entre 0,007 y 0,042; 11 de 13. **Sin Polonia: 0,007 (p=0,51)**; sin Brasil 0,032 (p=0,067). En
  niveles nunca es significativo.

Magnitud (d.e. dentro del país: ln JLoss 0,52; D 3,10 pp; ln EMBI 0,376; EMBI 71 pb):
1 d.e. de fragilidad → +5,1 % del spread (0,14 d.e.), 18,3 pb; 1 d.e. de riesgo de cola → +10,0 %
(0,27 d.e.), 10,0 pb. R²: EF país 0,546; EF país+tiempo 0,690; con los dos riesgos 0,707; R² parcial
de ambos 0,054 (J 0,021; D 0,028); en niveles 0,099 (J 0,077; D 0,015).

### 17.5 Resiliencia por componente — `p19_resiliencia.py` (`variantes`)

| Moderador (por d.e.; wild entre paréntesis) | J×R log | D×R log | J×R pb | D×R pb |
|---|---|---|---|---|
| Reservas/PIB | **−0,247 (0,08; cluster 0,048)** | −0,001 (0,97) | **−11,33 (0,04)** | 0,05 (0,98) |
| Menor deuda/PIB | +0,107 (0,21) | −0,010 (0,06) | +4,55 (0,12) | −1,51 (0,17) |
| Balance fiscal/PIB | +0,048 (0,31) | +0,003 (0,36) | +3,81 (0,15) | +0,34 (0,71) |
| PC1 (58 % var.; cargas 0,69 / 0,70 / 0,18) | +0,094 (0,22) | −0,008 (0,32) | +4,50 (0,15) | −1,19 (0,38) |
| Alta resiliencia ex ante (indicador de país) | −0,022 (0,89) | **−0,028 (0,06)** | −7,86 (0,27) | −4,73 (0,15) |
| Ex ante, sin crisis (N=576) | −0,051 (0,71) | **−0,047 (0,08)** | −7,16 (0,24) | −8,52 (0,11) |

Ex ante: promedio 2004–07 del índice (8 países con datos; el resto, primeros 16 trimestres); alta =
sobre la mediana: Chile, China, Indonesia, Malasia, Perú, Sudáfrica. **Lectura:** las reservas
atenúan el efecto de la fragilidad (el resultado de moderación más robusto); la resiliencia previa
atenúa el del riesgo de cola; el espacio fiscal va en sentido contrario para la fragilidad.

**Reemplazada por §18.6 (2026-10-13):** la lectura de las reservas como "el resultado de moderación
más robusto" y el verbo "atenúan" quedan retirados. Reservas × fragilidad y resiliencia previa × riesgo
de cola pasan a **exploratorias** (placebos, Holm, dependencia de Polonia en logaritmos; "ex ante" no
lo es para 5 de 13 países).

### 17.6 Respaldo externo por país y fecha — `p25_respaldo_externo.py`, `respaldo_externo.csv`

Acc = 1 con línea swap de la Fed (Brasil, México: 2008Q4–2009Q4 y 2020Q1–2021Q4) o FCL del FMI
(México 2009Q2–; Colombia 2009Q2–2025Q1; Polonia 2009Q2–2017Q3; Chile 2020Q2–; Perú
2020Q2–2024Q2). 223 obs. con acceso, 6 países. Chile: acceso continuo confirmado (§18.7).

| (DK / wild) | a (acceso) | c1: J×Acc | c2: D×Acc | c3: J×D×Acc |
|---|---|---|---|---|
| Muestra completa, log | +0,196 (0,066) | +0,127 (0,14 / 0,58) | +0,002 (0,92 / 0,96) | −0,004 (0,86 / 0,90) |
| Solo FCL (208 obs.) | +0,228 (0,044) | +0,169 (0,052) | 0,000 | −0,004 |
| Dentro de GFC+COVID (N=109; 54 con acceso) | +0,553 (0,019) | +0,063 (0,78 / 0,80) | −0,018 (0,21 / 0,15) | +0,045 (0,03 / 0,22) |
| Muestra completa, pb | 7,9 | 1,51 | 6,19 (0,04 / 0,27) | −1,02 |
| Solo swap (26 obs., 2 países; no interpretable) | +0,279 | −0,365 | −0,018 | +0,044 |

**Lectura:** el respaldo medido por país no reproduce el desacople que sugería la variable de fecha
(Backstop). El acceso es endógeno (efecto directo positivo). La lectura "el respaldo externo apaga el
canal" queda como conjetura no corroborada.

### 17.7 Participación extranjera en la deuda — `p26_participacion_extranjera.py` (hecha: ver §18.5)

El script está listo, pero la base de Arslanalp y Tsuda (FMI, WP/14/39) no se pudo bajar de forma
automática (HTTP 403, 2026-10-12). Requiere `2_Datos/participacion_extranjera.csv` con columnas
`country, quarter, foreign_share`. No se imputa nada; sin ese archivo el script no estima.

**Hecho el 2026-10-13: ver §18.5** (base `Database_For_Posting_EM_Frozen.xlsx`, versión de mayo de 2026).


## 18. Segunda ronda de arbitraje (2026-10-13)

Segunda ronda sobre lo hecho en §17 (ver `4_Redaccion/informe_arbitro.md`). Decisión de encuadre: que
la fragilidad bancaria importa para el spread ya lo establecen Chari et al. (2024); en la tesis es
**réplica independiente y validación del panel**, no la conclusión principal. La pregunta propia es
qué agrega el riesgo económico (D ≡ −GaR) y qué pasa cuando los dos riesgos se dan a la vez. Cada
script reproduce primero la principal (N=765; β1=0,0985; β2=0,0324; β3=−0,0112) y acepta
`JLOSS_FORMA=nivlag`. Regla: se reporta todo, salga como salga.

Escala de evidencia (la misma en todos los documentos): **firme** = resiste wild bootstrap o
permutación y no depende de un país; **sugerente** = significativo solo con Driscoll–Kraay, o depende
de un país; **exploratorio** = no estaba preespecificado y no pasa la corrección por comparaciones
múltiples; **no hay evidencia**.

Nota sobre los p de wild bootstrap de la principal: 0,33 / 0,20 / 0,89 en `paper_arbitro_numeros.csv`
y `paper_inferencia_v2_numeros.csv`; 0,32 / 0,20 / 0,90 en `p30` y `p32` (B=999). Es error de
simulación del bootstrap, no un cambio; el texto usa 0,33 / 0,20 / 0,89.

### 18.1 Aporte del riesgo de cola y simultaneidad — `p32_aporte_riesgo_cola.py`

`paper_aporte_numeros.csv` / `_nivlag.csv`; figura `fig_aporte_cola_lnlag`. Wild con B=999.

**(a) Información incremental sobre la especificación al estilo de Chari** (fragilidad rezagada + sus
controles, EF de país y tiempo; N=662):

| | Log-log | Niveles (pb) |
|---|---|---|
| β2 al agregar D (DK / cluster / wild) | 0,037 (0,008 / 0,018 / 0,066) | 5,37 (0,031 / 0,028 / 0,145) |
| β1 antes → después de agregar D | 0,137 → 0,107 | 5,95 → 5,55 |
| Conjunta β2=β3=0 (DK / cluster F(2,12) / wild) | 0,0001 / 0,014 / 0,041 | 0,058 / 0,082 / 0,142 |
| R² dentro del país: J+controles → +D → +J×D | 0,153 → 0,185 → 0,194 | 0,218 → 0,239 → 0,239 |
| R² parcial de D dado J / de J dado D | 0,037 / 0,018 | 0,026 / 0,103 |
| Sin controles (N=765): β2 solo con D (DK / cluster / wild) | 0,030 (0,068 / 0,098 / 0,17) | 3,52 (0,24 / 0,25 / 0,34) |
| Sin controles: R² parcial de D | 0,022 | 0,010 |

**(b) Pruebas adecuadas a una variable lenta:**

| | Log-log | Niveles (pb) |
|---|---|---|
| Cambios a 4 trimestres (N=705): Δ4D (DK / wild) | 0,004 (0,71 / 0,13) | 0,32 (0,85 / 0,77) |
| Cambios a 4 trimestres: Δ4J (DK / wild) | 0,063 (0,017 / 0,067) | 2,42 (0,028 / 0,14) |
| Cambios a 4 trimestres: Δ4(J×D) (DK / wild) | −0,001 (0,77 / 0,90) | +0,358 (<0,001 / 0,011); 12 de 13 exclusiones |
| Proyecciones locales h=0…8: horizontes al 5 %, D / J | 0 de 9 / 1 de 9 | 0 de 9 / 3 de 9 |
| Entre países (13 medias): pendiente de D | 0,052 (p=0,46) | 8,9 (p=0,47) |
| Fuera de muestra, RECM: spread rezagado / AR / +J / +J+D | 0,1559 / 0,1576 / 0,1601 / 0,1650 | 32,2 / 33,0 / 33,3 / 34,4 |
| RECM(J+D) / RECM(J); Clark–West p unilateral | 1,031; 0,83 | 1,032; 0,88 |
| Principal sin Polonia: β2 | 0,007 (p=0,51) | 0,18 (p=0,95) |
| Expected Shortfall: β2 / sin Polonia | 0,037 (0,009) / 0,010 | 4,13 (0,16) / 0,99 |
| GaR t-sesgada: β2 / sin Polonia | 0,032 (0,038) / 0,007 | 3,09 (0,29) / 0,05 |
| Probabilidad de crecimiento negativo | 0,193 (DK p = 0,33; wild 0,088); sin Polonia 0,202 (p = 0,17); interacción −0,342 (DK p = 0,028) |

Con esta medida el coeficiente no cae al excluir Polonia.

Fuera de muestra: ventana expansiva, un trimestre adelante, 540 pronósticos en 53 trimestres desde
2013Q2, pendiente común con EF de país y sin EF de tiempo. Ningún modelo le gana al spread rezagado.

**(c) La simultaneidad como hecho** (terciles altos dentro de cada país; N=765):

| | Valor |
|---|---|
| Observaciones con ambos riesgos altos / esperadas bajo independencia | 168 (22,0 %) / 87,0 → 1,93 veces |
| Países con observado > esperado | 13 de 13 |
| Permutación por bloques (999; desplazamiento circular de D dentro del país) | media 85,7; p=0,001 |
| Fuera de los trimestres de crisis | 108 frente a 59,3; p=0,001 |
| Episodios conjuntos / duración media / bajo permutación | 62 / 2,71 trimestres / 1,85 (p=0,003) |
| J(t−1) → D(t), con rezago propio (DK / cluster / wild) | 0,405 (0,009 / 0,001 / 0,024); en niveles de JLoss 0,045 (0,018 / <0,001 / 0,012) |
| D(t−1) → J(t) (DK / cluster / wild) | −0,006 (0,50 / 0,47 / 0,48); en niveles −0,064 (0,37 / 0,19 / 0,19) |
| Correlación de J y D descontados los EF | 0,26 (0,20 con JLoss en niveles) |
| Por año: 2009 / 2010–19 / 2020 / 2021 / 2022 / 2023 / 2024 / 2025 / 2026 | 14 / 25 / 29 / 17 / 29 / 20 / 15 / 13 / 6 |
| De 2020 en adelante | 129 de 168 |
| Conjuntas en trimestres de crisis / peso de esos trimestres en la muestra | 35,7 % / 14,2 % |

**(d) Cuando coinciden, ¿se amplifican?**

| | Log-log | Niveles (pb) |
|---|---|---|
| β3 de la principal (DK / cluster / wild) | −0,011 (0,11 / 0,53 / 0,89) | +0,246 (0,34 / 0,42 / 0,49) |
| Estrés conjunto en t: término conjunto (DK / wild) | −0,077 (0,11 / 0,25) | −3,4 (0,73 / 0,67) |
| Estrés conjunto en t+1 … t+4: término conjunto | −0,097 / −0,057 / −0,060 / −0,046 (wild 0,17 a 0,37) | −6,6 / −6,9 / −9,9 / −7,0 (wild 0,27 a 0,51) |
| Ambos riesgos +1 d.e. dentro del país: suma de los dos | +16,4 % del spread | 28,4 pb |
| Extra por la interacción (estimación puntual) | −2,1 puntos | +3,0 pb |
| IC 95 % de β3: DK | [−0,025; 0,003] | [−0,264; 0,757] |
| IC 95 % de β3: cluster | [−0,050; 0,028] | [−0,421; 0,913] |
| IC 95 % de β3: wild invertido | [−0,054; 0,015] | [−0,448; 0,925] |
| Mayor extra no descartable: DK / wild / cluster | +0,5 / +2,9 / +5,3 puntos (3 % / 16 % / 29 % de la suma) | +9,1 / +11,1 / +11,0 pb (32 % / 39 % / 39 %) |
| Box–Cox λ=0,44: β3 (t; DK / cluster / wild) | −0,013 (t=−0,19; 0,85 / 0,93 / 0,97) | mayor extra con wild: +6,8 pb sobre 27,3 (25 %) |

El p de wild del estrés conjunto en t es 0,23 en `p23` (§17.3) y 0,25 en `p32` (B=999).

**Lectura:** la simultaneidad es un hecho **firme**: los dos riesgos altos coinciden 1,9 veces lo
esperado, en los 13 países, con permutación p=0,001 también fuera de las crisis; aparte, y solo como evidencia **sugerente**, la fragilidad antecede al riesgo de cola (0,405; wild 0,024) y no al revés. Neto del calendario común lo esperado es 132 (razón 1,27). Salvedad: 129 de las 168 observaciones
conjuntas son de 2020 en adelante. Cuando coinciden **no hay evidencia de amplificación**; los datos
no permiten descartar un extra de hasta un 30–40 % de la suma (no se escribe "descartada"). El riesgo
económico agrega poco a lo que explica la fragilidad (**sugerente, solo en niveles**): β2=0,037 con
wild 0,066 y conjunta con wild 0,041 en logaritmos, pero no aparece en cambios a cuatro trimestres ni
en proyecciones locales, no mejora el pronóstico (el error sube un 3 %), y sin Polonia cae a 0,007. En
puntos básicos ni β2 ni la conjunta pasan el wild (0,145 y 0,142).

### 18.2 Fechas y dinámica — `p27_fd_tiempos.py`, `p28_dinamica_lp.py`

`paper_tiempos_numeros.csv`, `paper_dinamica_numeros.csv` (y `_nivlag`);
`embi_trimestral_alternativo.csv`; figura `fig_lp_acumulada_lnlag`. El EMBI del panel es el promedio
de los días del trimestre; JLoss(t−1) usa capitalización de cierre y volatilidad realizada de t−1.
Cierre = media de los últimos 5 días hábiles. Muestra común N=708 (quedan fuera las 40 observaciones
empalmadas del FMI, sin dato diario).

| Variable dependiente, sobre ΔJ(t−1) (DK / wild) | Log-log | Niveles (pb) |
|---|---|---|
| promedio(t) − promedio(t−1) (versión de §17.1) | 0,039 (0,001 / 0,0005) | 1,30 (0,008 / 0,051) |
| **cierre(t) − cierre(t−1)** (prueba limpia de precedencia) | **0,025 (0,22 / 0,21)** | **0,28 (0,71 / 0,58)** |
| promedio(t) − cierre(t−1) | 0,019 (0,18 / 0,026) | 0,26 (0,57 / 0,55) |
| primer mes(t) − cierre(t−1) | 0,000 (0,98 / 0,99) | 0,04 (0,85 / 0,91) |
| parte mecánica: cierre(t−1) − promedio(t−1) | 0,020 (0,008 / 0,001) | 1,03 (0,010 / 0,002) |
| **mismo trimestre: cierre(t−1) − cierre(t−2)** | **0,037 (0,044 / 0,008)** | **2,64 (<0,001 / 0,008)** |
| CDS de cierre, mismo trimestre (N=595) | 0,059 (0,011 / 0,007) | 3,49 (<0,001 / 0,008) |
| CDS de cierre, prueba limpia (N=606) | 0,016 (0,30 / 0,43) | 0,52 (0,49 / 0,46) |

| Estabilidad (al 5 % con DK) | Log-log | Niveles (pb) |
|---|---|---|
| Prueba limpia: exclusiones de país / de año significativas | 0 de 13 / 0 de 23 | 0 de 13 / 0 de 23 |
| Prueba limpia sin Polonia | 0,007 (p=0,65) | 0,16 (p=0,82) |
| Mismo trimestre (N=699): exclusiones de país / de año | 6 de 13 / 13 de 23 | 13 de 13 / 23 de 23 |
| Mismo trimestre sin Turquía | 0,030 (p=0,15) | 2,13 (p=0,009) |
| Placebo de adelanto ΔJ(t+1): promedio / cierre / mismo trimestre | p=0,91 / 0,53 / 0,58 | p=0,75 / 0,65 / 0,63 |
| Parte mecánica / coeficiente de la versión de §17.1 | 52 % | 80 % |
| Una d.e. de ΔJ (mismo trimestre) | 0,37 → 1,4 % del spread (≈ 2,7 pb) | 2,46 → 6,5 pb |
| R² parcial de ΔJ (mismo trimestre) | 0,8 % | 4,3 % |

Principal en niveles con el spread de cierre (N=725; DK / wild): β1=0,083 (0,015 / 0,40); β2=0,036
(0,019 / 0,17); β3=−0,011 (0,18 / 0,85). En pb: 4,42 (<0,001 / 0,39); 3,72 (0,20 / 0,41); 0,16.

| Dinámica (spread promedio, N=750) | Log-log | Niveles (pb) |
|---|---|---|
| Velocidad de ajuste α | 0,063 (p=0,066) | 0,090 (p<0,001) |
| Multiplicador de largo plazo de la fragilidad θ (ee) | −0,146 (0,327) | 1,96 (3,21) |
| IC 95 % de θ (delta) | [−0,79; 0,50] | [−4,33; 8,26] |
| ¿Contiene el cero y el coeficiente estático? | Sí (estático 0,0985) | Sí (estático 4,73) |
| Conjunto de Fieller | no acotado | acotado |
| Multiplicador de largo plazo del riesgo de cola φ (ee) | 0,057 (0,051) | −0,29 (7,52) |
| ρ del spread corregido por jackknife de medio panel | 0,97 a 1,00 | 0,95 a 0,97 |
| LP acumulada de ΔJ, spread promedio: h=0 | 0,038 (p=0,013); 1 de 9 horizontes al 5 % | 1,12 (p=0,029); 3 de 9 |
| LP acumulada de ΔJ, spread de cierre | h=0: 0,030 (p=0,13); nunca positiva al 5 %; negativa al 5 % en h=6 (−0,072) y h=8 (−0,073) | h=0: 0,77 (p=0,29); 0 de 9 |
| LP acumulada de ΔD | 0 de 9 con promedio y con cierre | 0 de 9 con promedio y con cierre |
| Persistencia del choque de JLoss a h=8 | 0,46 | 0,59 |

**Lectura:** el resultado en diferencias de la primera ronda era en buena parte un artefacto de
fechas. La fragilidad bancaria y el spread **se mueven dentro del mismo trimestre** (0,037; wild
0,008; en pb en 13 de 13 países y 23 de 23 años; en logaritmos en 6 de 13 y 13 de 23); **no hay
evidencia de que la fragilidad anteceda al spread** (0,025; wild 0,21; ninguna exclusión lo cambia).
La mitad del coeficiente de §17.1 en logaritmos y el 80 % en pb es agregación temporal. **Nivel
frente a cambio: los datos no informan** (el intervalo del multiplicador de largo plazo contiene a la
vez el cero y el coeficiente estático). Con el spread de cierre en logaritmos la respuesta acumulada
es negativa y significativa en dos horizontes largos (h=6 y h=8), lo que se reporta. Para el riesgo
de cola la respuesta es plana en todo horizonte. No se pudo verificar el rezago de publicación de los
balances en la fecha de JLoss (el repositorio no guarda la fecha de periodo fiscal).

### 18.3 Simulación de inferencia v2 — `p29_simulacion_v2.py`

`paper_inferencia_v2_numeros.csv`; S=1000, B=199; solo en logaritmos. Procesos generadores: A (el de
p22: signos por país sobre el residuo); B (AR(2) por país y remuestreo de vectores de innovaciones
por fecha en bloques de 4 trimestres: conserva la dependencia entre países); C (VAR(1) de panel en
(y, J, D) con retroalimentación; se impone coeficiente nulo en la ecuación del spread y se regeneran
J y D); C0 (igual, sin retroalimentación). Tasa de rechazo al 5 % nominal, fragilidad / riesgo de cola.

| Niveles | Tamaño B | Potencia B | Tamaño C, centrado | Rechazo de cero en C | Tamaño A |
|---|---|---|---|---|---|
| Driscoll–Kraay | 28 % / 21 % | 70 % / 77 % | 18 % / 18 % | 42 % / 45 % | 35 % / 31 % |
| DK, banda larga y valores críticos fixed-b | 15 % / 11 % | 56 % / 66 % | 9 % / 10 % | 27 % / 29 % | 21 % / 23 % |
| Cluster por país, t(12) | 9 % / 8 % | 44 % / 70 % | 6 % / 14 % | 26 % / 24 % | 15 % / 20 % |
| Wild bootstrap por país | 6 % / 7 % | 35 % / 67 % | 5 % / 12 % | 24 % / 24 % | 9 % / 16 % |

| Primeras diferencias | Tamaño B | Potencia B (fragilidad) | Tamaño C, centrado | Rechazo de cero en C |
|---|---|---|---|---|
| Driscoll–Kraay | 5 % / 6 % | 87 % | 6 % / 7 % | 29 % / 7 % |
| Cluster por país, t(12) | 6 % / 9 % | 84 % | 5 % / 7 % | 24 % / 7 % |
| Wild bootstrap por país | 6 % / 6 % | 81 % | 5 % / 5 % | 26 % / 4 % |

| Otros | Fragilidad | Riesgo de cola |
|---|---|---|
| Error estándar DK / desviación Monte Carlo, niveles (B; C) | 0,56; 0,68 | 0,64; 0,68 |
| Error estándar de cluster t(12) / desviación, niveles (B) | 0,84 | 0,74 |
| Sesgo de retroalimentación en niveles (C): media del coeficiente bajo efecto directo nulo | +0,066 (d.e. 0,060; límite de panel largo 0,123); dato 0,0985 | +0,022 (límite 0,030); dato 0,032 |
| Lo mismo sin retroalimentación (C0) | +0,028 | +0,011 |
| Lo mismo en primeras diferencias (C) | +0,019 (d.e. 0,013); dato 0,037 | 0,000 |
| p reales de la principal: DK / cluster t(12) / wild | 0,003 / 0,28 / 0,33 | 0,033 / 0,14 / 0,20 |

"Centrado" = contra la media de muestra finita del estimador (mide solo la calibración del error
estándar). "Rechazo de cero en C" = contra cero cuando el efecto directo es nulo: mezcla inferencia e
identificación. p reales de β3: 0,11 / 0,53 / 0,89.

**Lectura:** en niveles el error estándar de Driscoll–Kraay es 0,56–0,68 de la desviación verdadera y
rechaza una hipótesis nula cierta entre el 20 % y el 30 % de las veces, aunque se conserve la
dependencia entre países; los valores críticos fixed-b no lo arreglan. El wild bootstrap por país es
el mejor calibrado (6–7 %; hasta 12 % con retroalimentación) y su potencia es 35 % (fragilidad) y
67 % (riesgo de cola), mayor que la de §17.2 (17 % / 28 %, con un diseño que lo desfavorecía). En
primeras diferencias todos los métodos están entre 5 % y 9 %. **Regla:** en niveles, "resiste el wild
bootstrap" es el criterio; "solo Driscoll–Kraay" es sugerente. **Límite que ningún error estándar
arregla:** con retroalimentación y sin efecto directo, la regresión estática entrega en promedio
+0,066 para la fragilidad y +0,022 para el riesgo de cola, y todos los métodos, incluido el wild,
rechazan el cero entre un cuarto y la mitad de las veces. Es un problema de identificación que vale
para los dos coeficientes de nivel y, en menor medida, para el de primeras diferencias de la
fragilidad (+0,019).

### 18.4 Países, piso de JLoss y forma funcional — `p30_influencia_paises.py`

`paper_influencia_numeros.csv` / `_nivlag.csv`; figura `fig_pendientes_pais_lnlag`. Wild con B=999.

| Heterogeneidad de la pendiente de la fragilidad | Log-log | Niveles (pb) |
|---|---|---|
| Pendientes por país: mínimo / máximo / positivas | −0,84 (Sudáfrica) / +0,97 (Indonesia) / 8 de 13 | −39,0 / +40,7 / 10 de 13 |
| Promedio de grupo (ee; p) | 0,106 (0,119; 0,39) | 4,01 (5,07; 0,44) |
| Homogeneidad: Pesaran–Yamagata Δ / Q | 15,4 / 128,7 (p<0,001) | 24,0 / 256,5 (p<0,001) |
| Turquía: variación de J / aporte a β1 | 17 % / 70 % | 28 % / 83 % |
| China: variación de J / aporte a β1 | 23 % / −17 % | 34 % / −9 % |
| β1 sin Turquía | 0,034 (p=0,43) | 0,63 (p=0,54) |
| β1 sin Turquía ni Polonia (N=613) | 0,073 (p=0,039) | 0,96 (p=0,33) |
| β1 con tendencias por país (DK / wild) | 0,046 (0,135 / 0,68) | 4,54 (<0,001 / 0,41) |
| β1 con cargas de VIX y HY por país (DK / wild) | 0,070 (0,011 / 0,43) | 3,78 (<0,001 / 0,40) |
| β1 sin Turquía: tendencias / VIX+HY / ambas | −0,033 / 0,012 / −0,039 | −0,10 / 0,41 / 0,09 |

| Riesgo de cola e interacción | Log-log | Niveles (pb) |
|---|---|---|
| Pendientes de D positivas / promedio de grupo, 13 países | 10 de 13 / 0,011 (ee 0,017; p=0,52) | 10 de 13 / 2,52 (p=0,30) |
| Promedio de grupo, 10 países con T ≥ 40 (ee; p) | 0,033 (0,008; 0,004) | 4,32 (1,61; 0,025) |
| Media ponderada por precisión / sin el más influyente | 0,023 / 0,022 | 2,56 / 2,18 |
| Homogeneidad de β2: Q (p) | 22,2 (0,035) | 22,3 (0,034) |
| Polonia: variación del spread / aporte a β2 | 47 % / 71 % | 17 % / 82 % |
| β2 con tendencias por país (DK / wild) | 0,035 (0,033 / 0,016) | 4,28 (0,19 / 0,13) |
| β2 sin las 36 obs. bajo 60 pb (26 de Polonia) (DK / wild) | 0,018 (0,11 / 0,26) | 2,26 (p=0,41) |
| β2 sin las 113 obs. bajo 100 pb (12 países) | 0,002 (p=0,85) | 0,25 (p=0,93) |
| β3 sin Polonia | +0,008 (p=0,19) | +0,471 (p=0,086) |
| Aporte de Polonia a β3 (total −0,0112) | −0,0165 | — |
| Box–Cox λ=0,44: β3 (DK / wild) | −0,013 (0,85 / 0,97) | — |

| El piso de JLoss (2,16 = 0,048 × 0,45 × 100) | Valor |
|---|---|
| Percentiles 5 / 25 / 50 / 75 / 95 de JLoss | 2,16 / 2,21 / 2,67 / 4,84 / 13,92 |
| Observaciones a menos de 2 % / 5 % / 10 % del piso | 23,7 % / 32,4 % / 39,1 % |
| Por país (2 %): Malasia / Perú / Chile / Sudáfrica / Indonesia / México / Colombia / Polonia / China / Turquía | 60 / 58 / 49 / 38 / 34 / 29 / 26 / 13 / 8 / 2 %; Brasil, India y Filipinas 0 % |
| β1 con z de JLoss dentro del país (DK / wild) | 0,048 (0,023 / 0,18); en pb 12,8 (<0,001 / 0,17) |
| D × fuera del piso, umbral 2 % (DK / wild) | +0,026 (0,020 / 0,11); en pb +7,5 (<0,001 / 0,036) |
| D × fuera del piso, umbral 5 % (DK) | +0,009 (0,45); en pb +5,3 (0,012) |
| Composición: sin FMI (N=725) / sin pocos bancos / desde 2010 | β1 0,086 / 0,099 / 0,083; β2 0,035 / 0,034 / 0,037; β3 −0,012 / −0,010 / −0,011 |

**Lectura:** la réplica de Chari et al. se sostiene en el promedio agrupado (0,099; con sus controles
0,107–0,164; con el CDS 0,206), pero **no es una elasticidad común**: la homogeneidad se rechaza, el
promedio de grupo no se distingue de cero y Turquía aporta el 70 % del coeficiente (sin ella 0,034).
El coeficiente del riesgo de cola depende de Polonia (71 %), en parte por el logaritmo de spreads muy
bajos; a su favor, 10 de 13 pendientes son positivas y resiste tendencias por país (wild 0,016). El
signo negativo de β3 es de Polonia y **no se lee como atenuación**. JLoss se amontona en su piso:
casi un cuarto de las observaciones no informa; la unidad correcta es una desviación estándar dentro
del país (≈ +5 % del spread; 12,8 pb), válida para los episodios fuera del piso. Señal débil en
sentido contrario: el riesgo de cola pesa más con los bancos fuera del piso, pero depende del umbral.
No hay corrección por comparaciones múltiples sobre las cerca de 60 regresiones de este script.

### 18.5 Participación extranjera — preespecificada — `p26_participacion_extranjera.py`

`paper_participacion_numeros.csv` / `_nivlag.csv`; figura `fig_participacion_extranjera`. Datos:
Arslanalp y Tsuda (FMI), versión de mayo de 2026 (`2_Datos/Database_For_Posting_EM_Frozen.xlsx` →
`2_Datos/participacion_extranjera.csv`), 13 países, 2004Q1–2025Q4, sin faltantes. Preespecificación
escrita en el encabezado del script antes de estimar: moderador primario F = participación de no
bancos extranjeros en la deuda total del gobierno, rezagada 4 trimestres y estandarizada (media 21,5;
d.e. 14,4 pp; 75 % de su varianza es entre países); familia primaria h1, h2, h3 con signo predicho
positivo, Holm sobre los tres y veredicto por wild bootstrap (B=1999); N=762.

| Familia primaria (DK / cluster / wild; Holm sobre wild) | Log-log | Niveles (pb) |
|---|---|---|
| h1: fragilidad × F | +0,037 (0,34 / 0,39 / 0,41; Holm 1,00) | +3,38 (0,002 / 0,013 / 0,13; Holm 0,40) |
| h2: riesgo de cola × F | −0,001 (0,90 / 0,91 / 0,92; Holm 1,00) | +1,51 (0,12 / 0,32 / 0,34; Holm 0,69) |
| h3: interacción × F | −0,006 (0,31 / 0,49 / 0,48; Holm 1,00) | −0,33 (0,053 / 0,31 / 0,38; Holm 0,69) |

| Secundarias (rotuladas; sin Holm; DK / wild) | Log-log | Niveles (pb) |
|---|---|---|
| Participación total: h1 / h2 / h3 | +0,035 (0,38 / 0,54) / −0,005 (0,37 / 0,41) / −0,006 (0,11 / 0,58) | +3,93 (<0,001 / 0,11) / +0,15 / −0,29 (0,009 / 0,47) |
| F ex ante (media 2004–07): h3 | −0,020 (0,005 / 0,038) | −0,38 (0,010 / 0,048) |
| Rezago de 8 trimestres: h3 | −0,013 (0,046 / 0,19) | −0,40 (0,022 / 0,15) |
| Sin trimestres de crisis (N=653): h1 / h3 | +0,069 (0,013 / 0,17) / −0,003 (0,63 / 0,87) | +3,28 (<0,001 / 0,15) / −0,58 (0,10 / 0,74) |
| Entre / dentro de países: h3 | −0,014 (0,051 / 0,085) / +0,028 (0,039 / 0,30) | −0,37 (0,040 / 0,22) / +0,06 (0,83 / 0,93) |

Hecho descriptivo, participación extranjera total media en la muestra (%): Perú 64; Indonesia 50;
Colombia 43; **Polonia 40** (rango 27–55; 4.ª de 13; 3.ª en no bancos con 29,5); México 39; Turquía 31;
Chile 31; Sudáfrica 31; Filipinas 29; Malasia 24; Brasil 12; **India 5**; China 3. Media del "núcleo de
11": 32,5; del grupo de contraste (Polonia e India): 22,7.

**Lectura:** ninguna de las tres hipótesis primarias es significativa con el veredicto declarado
(wild y Holm); h3 tiene signo contrario al predicho. Se reporta que en puntos básicos h1 es
significativo con Driscoll–Kraay y con cluster (Holm 0,005 y 0,040) y no con wild (0,13): sugerente
según la escala, no firme. La secundaria ex ante da h3 negativo con wild 0,038, signo contrario al
predicho. Consecuencia declarada de antemano: la heterogeneidad del "núcleo de 11 economías" pasa a
**exploratoria** (+0,034, wild 0,015; +1,8 pb, wild 0,002; Holm 0,005; §14 y §17.2). Es ausencia de
evidencia con intervalos anchos, no evidencia de un cero. La etiqueta "deuda local profunda" vale
para India, no para Polonia; el grupo "Polonia e India" es una **agrupación ex post**.

### 18.6 Reservas y resiliencia previa bajo escrutinio — `p31_reservas_placebo.py`

`paper_reservas_numeros.csv` / `_nivlag.csv`; figura `fig_reservas_efecto_marginal_lnlag`. g1 =
fragilidad × moderador; g2 = riesgo de cola × moderador; moderador estandarizado.

| Reservas/PIB × fragilidad (DK / cluster / wild) | Log-log | Niveles (pb) |
|---|---|---|
| Contemporáneo (N=670; reproduce §17.5) | −0,247 (<0,001 / 0,048 / 0,08) | −11,3 (<0,001 / <0,001 / 0,04) |
| Reservas rezagadas 4 trimestres (N=681) | −0,234 (<0,001 / 0,057 / 0,051) | −10,9 (<0,001 / <0,001 / 0,020) |
| Reservas rezagadas 8 trimestres (N=673) | −0,190 (<0,001 / 0,12 / 0,085) | −10,3 (<0,001 / 0,001 / 0,057) |
| Ex ante invariante, continua (N=765) | −0,073 (0,035 / 0,16 / 0,30) | −4,35 (<0,001 / <0,001 / 0,13) |
| Sin Polonia | −0,084 (<0,001 / 0,19 / 0,30) | −9,5 (<0,001 / <0,001 / 0,08) |
| Exclusiones de país que pasan el wild al 5 % / al 10 % | 1 de 13 / 10 de 13 | 10 de 13 / 13 de 13 |
| Entre países / dentro de países (wild) | −0,262 (0,13) / −0,270 (0,09) | −11,7 (0,026) / −10,7 (0,056) |
| Holm sobre 3 componentes × 2 riesgos (wild) | 0,40 | 0,22 |
| Observaciones con elasticidad de la fragilidad implícita negativa y significativa | 23 % | 29 % |
| Reservas (d.e.) donde la elasticidad implícita cruza cero | +0,08 | +0,09 |

| Moderadores placebo × fragilidad (DK / wild) | Log-log | Niveles (pb) |
|---|---|---|
| Cuenta corriente/PIB, contemporánea / rezagada 4 | −0,087 (0,049 / 0,084) / −0,113 (0,011 / 0,040) | −5,31 (<0,001 / 0,042) / −4,08 (0,004 / 0,062) |
| Tipo de cambio real, contemporáneo / rezagado 4 | +0,039 (0,048 / 0,33) / +0,123 (<0,001 / 0,019) | +0,08 (0,95 / 0,95) / +3,62 (0,028 / 0,026) |
| Inflación, contemporánea / rezagada 4 | −0,001 (0,96 / 0,99) / +0,024 (0,48 / 0,71) | +1,02 (0,005 / 0,26) / +2,91 (0,001 / 0,15) |
| Concentración bancaria (HHI): trimestral / rezagada 4 / estructural | +0,114 (<0,001 / 0,22) / +0,132 (<0,001 / 0,22) / +0,084 (0,013 / 0,39) | +2,02 (0,12 / 0,37) / +2,45 (0,10 / 0,30) / +1,81 (0,044 / 0,33) |
| De 9 placebos, significativos al 5 %: DK / cluster / wild | 7 / 3 / 2 | 6 / 4 / 2 |

| Resiliencia previa (indicador "ex ante") × riesgo de cola (DK / cluster / wild) | Log-log | Niveles (pb) |
|---|---|---|
| Muestra completa (N=670) | −0,028 (0,006 / 0,064 / 0,064) | −4,73 (0,019 / 0,18 / 0,15) |
| Sin trimestres de crisis (N=576) | −0,047 (<0,001 / 0,082 / 0,08) | −8,52 (<0,001 / 0,13 / 0,11) |
| Versión continua | −0,011 (0,014 / 0,10 / 0,084) | −1,69 (0,079 / 0,21 / 0,17) |
| Sin Polonia | −0,018 (0,11 / 0,16 / 0,15) | −6,60 (0,004 / 0,054 / 0,047) |
| Sin México | −0,024 (0,045 / 0,12 / 0,12) | −1,58 (0,44 / 0,52 / 0,45) |
| Exclusiones con signo negativo / que pasan el wild al 5 % | 13 de 13 / 3 de 13 | 13 de 13 / 4 de 13 |

"Ex ante" usa el promedio 2004–07 en 8 países; en Brasil, Chile, Colombia, México y Perú usa los
primeros 16 trimestres disponibles (y en India y China el promedio 2004–07 descansa en 3 y 6 trimestres
de reservas).

Lo que queda del índice contemporáneo (§16): efecto directo −0,153 (DK 0,001; cluster 0,38) y D×R
fuera de crisis −0,024 (DK 0,007), que en crisis es −0,001 (0,86): solo Driscoll–Kraay.

**Lectura:** reservas × fragilidad pasa a **exploratorio**. El coeficiente de la fragilidad es menor
donde hay más reservas; la asociación es estable al rezagar las reservas y se mantiene en puntos
básicos, pero en logaritmos depende de Polonia, no pasa la corrección por comparaciones múltiples y
otras variables macroeconómicas (cuenta corriente, tipo de cambio real) muestran interacciones de
fuerza similar; con Driscoll–Kraay 6–7 de 9 moderadores arbitrarios salen significativos. La
interacción lineal implica una elasticidad negativa y significativa para el 23–29 % de las
observaciones, lo que no es creíble. Sin lenguaje causal ni de política sobre acumular reservas.
Resiliencia previa × riesgo de cola: **exploratorio** (signo estable; sin Polonia pierde significancia
en logaritmos y sin México desaparece en pb; "ex ante" no lo es para 5 de 13 países). El índice
contemporáneo: **sugerente** (solo Driscoll–Kraay); la analogía del seguro queda como lectura, no
como hallazgo.

### 18.7 Respaldo externo: Chile confirmado — `p25_respaldo_externo.py`, `respaldo_externo.csv`

Ventanas definitivas: swap de la Fed, Brasil y México (2008Q4–2009Q4 y 2020Q1–2021Q4); Línea de
Crédito Flexible del FMI: México desde 2009Q2; Colombia 2009Q2–2025Q1; Polonia 2009Q2–2017Q3; Chile
desde 2020Q2; **Perú 2020Q2–2024Q2**. Chile: acceso continuo confirmado; en mayo de 2022 pasó a una
Línea de Liquidez de Corto Plazo y el 29 de agosto de 2022 el FMI aprobó una nueva Línea de Crédito
Flexible y Chile canceló la anterior (comunicado pr22294). 223 observaciones con acceso, 6 países.
Las fuentes de las ventanas no son todas anuncios oficiales (la de 2020 es del Programa de Estabilidad
Financiera de Yale).

| (DK / wild) | Log-log | Niveles (pb) |
|---|---|---|
| Interacción × acceso, muestra completa (N=765) | −0,004 (0,86 / 0,90) | −1,02 (0,22 / 0,52) |
| Fragilidad × acceso | +0,127 (0,14 / 0,58) | +1,51 (0,69 / 0,86) |
| Riesgo de cola × acceso | +0,002 (0,92 / 0,96) | +6,19 (0,042 / 0,27) |
| Interacción × acceso dentro de GFC+COVID (N=109; 54 con acceso) | +0,045 (0,030 / 0,22) | +0,14 (0,55 / 0,79) |
| Efecto directo del acceso | +0,196 (DK 0,066) | +7,9 (DK 0,48) |

**Lectura:** se mantiene la conclusión de §17.6: el respaldo medido por país no muestra desacople. Las
cifras no cambian con la confirmación de Chile (ya estaba codificado como continuo). Con Holm, los
contrastes por régimen de fecha quedan en Backstop 0,03 → 0,12 y EMstress 0,08 → 0,24 (§17.2). Ninguna
de las condiciones estudiadas (resiliencia, respaldo externo, quién tiene la deuda) modifica la
transmisión de forma demostrable.

## 19. Evaluación experta: simultaneidad con calendario, precedencia y equivalencia (2026-10-21)

Fuente: `p33_simultaneidad_precedencia_tost.py` → `paper_p33_numeros.csv` (log-log) y
`paper_p33_numeros_nivlag.csv` (niveles, `JLOSS_FORMA=nivlag`). Pruebas pedidas en
`4_Redaccion/evaluacion_experta.md` (mejoras A2, A3, B7); no estaban entre las fijadas antes de estimar.
Regresión principal verificada (N=765, b3=−0,0112).

**19.1 Simultaneidad con nula de calendario** (indicador de D permutado entre países dentro de cada
trimestre, 4 999 réplicas):

| Muestra | Observado | Esperado | Razón | p |
|---|---|---|---|---|
| Completa (N=765) | 168 | 140,9 | 1,19 | 0,0002 |
| Fuera de crisis (N=656) | 108 | 81,1 | 1,33 | 0,0002 |
| 2004–09 / 2010–14 / 2015–19 | 14 / 9 / 16 | 13,3 / 6,9 / 5,6 | 1,05 / 1,31 / 2,88 | 0,44 / 0,15 / 0,0002 |
| 2020–22 / 2023–26 | 75 / 54 | 74,4 / 40,7 | 1,01 / 1,33 | 0,47 / 0,0002 |

En niveles la razón es 1,20 (p=0,0002), con los mismos terciles.

**19.2 Precedencia ln JLoss_{t−1} → D_t** (rezago propio, EF país y tiempo):

| Variante | Coef. | p DK / cluster / wild |
|---|---|---|
| Base (N=752) | 0,405 | 0,0095 / 0,0011 / 0,024 |
| Sin cada país | 0,321 (sin Brasil) a 0,473 (sin Perú) | DK < 0,05 en 12 de 13 (sin Brasil 0,065); cluster < 0,05 en 13 |
| GaR base dentro de muestra | 0,301 | 0,012 / 0,0005 / 0,006 |
| GaR sin bloque bursátil (dentro de muestra) | 0,388 | 0,0001 / <0,0001 / 0,002 |
| 2 rezagos (suma; Wald) | 0,414 | 0,004 / 0,002 / 0,033 |
| 3 rezagos | 0,421 | 0,014 / 0,007 / 0,11 |
| 4 rezagos | 0,455 | 0,002 / 0,002 / 0,15 |
| Inversa D → ln JLoss, 2–4 rezagos (suma) | −0,007 a −0,012 | ninguna < 0,05 |

**19.3 Equivalencia (TOST) para b3** (escenario: ambos riesgos 1 d.e. within sobre su media; cota =
extremo superior del IC 90 %, como fracción de la suma de las dos asociaciones):

| | DK | Cluster t(12) | Wild invertido | MDE 80 % (DK / cluster) |
|---|---|---|---|---|
| Log-log (suma 0,152) | 0,4 % | 22 % | 13 % | 21 % / 58 % |
| Niveles (suma 28,4 pb) | 29 % | 34 % | 35 % | 31 % / 40 % |

**Lectura:** la simultaneidad sobrevive a una nula que conserva el calendario, pero su magnitud es 1,2
veces (no 1,9); el exceso viene de 2015–19 y 2023–26. La precedencia pasa la exclusión de cada país y
el GaR sin bloque bursátil: firme como precedencia estadística a un trimestre (no causal, no fechable
dentro del trimestre). Con los tres métodos y en las dos formas se rechaza una amplificación de más de
un 35 % de la suma; una menor no se puede descartar.

## 20. Fragilidad sin saturación: PD y DD de Merton (2026-10-21)

Fuente: `p34_fragilidad_alternativa.py` → `fragilidad_alternativa_bbg.csv` (series país-trimestre),
`paper_p34_numeros.csv` y `paper_p34_numeros_nivlag.csv`. Mejora B6 de `evaluacion_experta.md`; no
preespecificada. PD_w = PD de Merton/KMV media ponderada por pasivos (%); DD_w = distancia al
incumplimiento media ponderada por pasivos; mismo motor y bancos que JLoss.

| Medida (rezagada, centrada) | β1 log (DK / cluster / wild) | por d.e. within | β3 log (wild) | γ1 pb (wild) | γ3 pb (DK / wild) | corr. con ln JLoss | N |
|---|---|---|---|---|---|---|---|
| ln JLoss (base) | 0,099 (0,003 / 0,28 / 0,32) | 0,052 | −0,011 (0,90) | 4,73 (0,31) | 0,25 (0,34 / 0,47) | 1 | 765 |
| ln PD_w | 0,021 (<0,001 / 0,075 / 0,091) | 0,057 | 0,0005 (0,89) | 2,14 (0,30) | 0,11 (0,34 / 0,47) | 0,71 | 765 |
| −DD_w | 0,082 (<0,001 / 0,044 / 0,055) | 0,080 | 0,0001 (0,997) | 18,8 (0,048) | 1,87 (0,017 / 0,13) | 0,85 | 765 |
| ln JLoss malla ancha (sin India) | 0,067 (0,22 / 0,47 / 0,47) | 0,031 | 0,002 (0,99) | 4,10 (0,27) | 0,49 (0,0495 / 0,20) | 0,80 | 710 |
| ln JLoss base sin India | 0,087 (0,035 / 0,39 / 0,42) | 0,045 | −0,013 (0,89) | 5,28 (0,29) | 0,42 (0,16 / 0,36) | 1 | 710 |

**Lectura:** con la distancia al incumplimiento, que no tiene piso ni techo, la asociación de la
fragilidad es más nítida (wild 0,055 en logs; 0,048 en pb) con la misma magnitud por d.e. (~18 pb). La
interacción sigue en cero en logaritmos con todas las medidas; en pb es positiva con −DD_w solo con DK,
coherente con la proporcionalidad multiplicativa. La saturación atenúa la fragilidad, no explica la
ausencia de amplificación.

## 21. Instrumento granular (GIV) para la fragilidad (2026-10-21)

Fuente: `p36_giv_granular.py` → `giv_granular_bbg.csv`, `paper_p36_numeros.csv`. Mejora C9; no
preespecificada. z = retorno de capitalización de los bancos ponderado por pasivos (t−1) menos el de
igual peso, por país y trimestre (Gabaix y Koijen); (b) tras quitar la beta de cada banco sobre el
retorno medio del país. Regresión principal sin interacción, fragilidad_{t−1} instrumentada con z_{t−1}.

| Endógena / instrumento | 1ª etapa (F DK / F cluster) | Forma reducida (p DK / wild) | 2SLS (EE cluster) | MCO | N |
|---|---|---|---|---|---|
| ln JLoss / z_{t−1} | 0,79 (1,8 / 3,2) | 0,084 (0,79 / 0,81) | 0,107 (0,363) | 0,104 | 750 |
| ln JLoss / z(b)_{t−1} | 0,53 (0,8 / 1,2) | 0,092 (0,77 / 0,78) | 0,173 (0,511) | 0,104 | 750 |
| ln JLoss / z_{t−2} | 0,53 (1,0 / 3,0) | 0,305 (0,29 / 0,52) | 0,580 (0,884) | 0,102 | 747 |
| −DD_w / z_{t−1} | 1,32 (1,9 / 3,0) | 0,084 (0,79 / 0,81) | 0,064 (0,212) | 0,083 | 750 |

Exogeneidad: z_{t−1} sobre Δ ln EMBI_{t−1}: −0,021 (DK p = 0,041), es decir, el instrumento responde
al spread contemporáneo. Sistemas de 3 a 10 bancos (HHI de pasivos 0,17–0,41).
**Lectura:** instrumento débil (F < 4) y con dudas de exclusión; no identifica. El 2SLS coincide en
punto con el MCO pero con errores tres veces mayores.

## 22. Fragilidad y spread mensuales (2026-10-21)

Fuente: `p37_mensual_fechado.py` → `fragilidad_mensual_bbg.csv`, `paper_p37_numeros.csv`. Mejora C10;
no preespecificada. −DD_w mensual (mismo motor y bancos; vol. realizada de 3 meses; balance más
reciente) y EMBI diario (cierre = últimos 5 días hábiles). 13 economías, 2 655 país-meses, EF de país y
de mes, DK (ancho 6). Validación: corr. con el DD_w trimestral de p34 = 0,9993 (886 obs.).

| Prueba | Coeficiente | p |
|---|---|---|
| d(−DD)_{m−1} → d ln EMBI_m (rezago 1) | 0,0132 | DK 0,005 |
| Suma rezagos 1–3; Wald conjunto | 0,0272 | DK suma 0,017 / Wald 0,038; cluster suma 0,001; wild Wald < 0,001 |
| Sin cada país: suma; p del rezago 1 | 0,016 (sin Polonia) a 0,033 (sin Perú) | 13 de 13 < 0,05 (máx. 0,017) |
| Inversa d ln EMBI → d(−DD), suma; Wald | 0,029 | 0,87 / 0,29; wild 0,39 |
| Contemporánea d(−DD)_m | 0,0197 | DK 0,002; wild 0,001 |
| LP acumulada h = 0/1/2/3/4/5/6 | 0,020 / 0,021 / 0,021 / 0,027 / 0,011 / 0,012 / 0,014 | 0,002 / 0,005 / 0,004 / 0,001 / 0,20 / 0,13 / 0,08 |

d.e. de d(−DD) mensual = 0,43: una d.e. va seguida de un spread ~0,6 % mayor el mes siguiente y ~1,2 %
acumulado a tres meses.
**Lectura:** a frecuencia mensual la fragilidad antecede al spread, y no al revés, sin depender de un
país. La conclusión trimestral ("se mueven en el mismo trimestre") era una limitación de la frecuencia.
Es precedencia estadística, pequeña y no causal: puede reflejar que las acciones bancarias incorporan
antes la misma información.

## 23. Panel ampliado: EMBI desde el CDS y Argentina homologada (2026-10-21)

Fuente: `p38_panel_ampliado.py` → `paper_p38_numeros.csv`; GaR homologado:
`GaR/individuals/nlhpc_gar_all18/build_fci_no_ryr.py` → `GaR_panel_all19_noRyr.xlsx` →
`gar_insample_all19noRyr.csv` (FCI 2×2 STX+EER para las 19 economías; corr. con el FCI oficial 0,89 de
media, mín. 0,76 Turquía; corr. GaR base/homologado 0,986). Mejora C11; no preespecificada.

(a) ln EMBI = a_i + 0,616 ln CDS (pendiente común, 807 trimestres de solapamiento). Validación (intercepto
con los últimos 13 trimestres, pendiente sin el país, 10 economías): error absoluto mediano 0,175
log-puntos, corr. mediana 0,86; Indonesia 0,50 (corr. 0,65), China 0,39, Sudáfrica 0,20. Se agregan 189
observaciones (Indonesia 32 → 87, Filipinas 12 → 89, Sudáfrica 32 → 89). India sin CDS.

| Muestra | N | β1 (DK / wild) | β2 (DK / wild) | β3 (DK / wild) |
|---|---|---|---|---|
| Principal | 765 | 0,099 (0,003 / 0,32) | 0,032 (0,033 / 0,20) | −0,011 (0,11 / 0,90) |
| (a) Con EMBI imputado | 954 | 0,146 (<0,001 / 0,12) | 0,035 (0,060 / 0,075) | −0,011 (0,017 / 0,38) |
| (b) GaR base dentro de muestra, 13 | 773 | 0,096 (0,007 / 0,34) | 0,039 (0,040 / 0,017) | −0,006 (0,20 / 0,71) |
| (b) GaR homologado, 13 | 773 | 0,090 (0,006 / 0,40) | 0,038 (0,017 / 0,036) | −0,005 (0,25 / 0,69) |
| (b) GaR homologado, 14 (con Argentina, 35 obs.) | 808 | 0,099 (0,008 / 0,33) | 0,031 (0,040 / 0,13) | −0,002 (0,69 / 0,86) |

**Lectura:** ni más historia ni Argentina homologada cambian las conclusiones; la interacción sigue
sin ser positiva.

## 24. Estudio de eventos: líneas de respaldo (2026-10-21)

Fuente: `p39_eventos_respaldo.py` → `paper_p39_numeros.csv`. Mejora C12; no preespecificada. Nueve
eventos (Fed 29-oct-2008 y 19-mar-2020: Brasil, México; FCL: México 17-abr-2009, Polonia 6-may-2009,
Colombia 11-may-2009, Perú 28-may-2020, Chile 29-may-2020). Spread anormal = Δ ln EMBI del país menos
el medio de las economías sin respaldo ese día (pp, ×100). Placebo: 999 fechas del mismo país.

| Grupo | [−5,−1] | [0,+1] | [0,+5] | [0,+10] | Δβ banca–spread (placebo p) | Δβ relativo a controles (n > 0) |
|---|---|---|---|---|---|---|
| Fed (4) | −12,0 (0,013) | −12,9 (0,003) | −9,9 (0,006) | −2,0 (0,21) | +0,56 (0,005) | −0,23 (2 de 4) |
| FCL (5) | −1,2 (0,29) | +3,7 (0,96) | −0,03 (0,48) | +3,2 (0,85) | +0,90 (0,015) | +0,71 (2 de 5; Perú +4,5) |
| Todos (9) | −6,0 (0,030) | −3,7 (0,018) | −4,4 (0,029) | +0,9 (0,68) | +0,74 (0,004) | +0,29 (4 de 9) |

Por evento, Fed 2020: [0,+5] Brasil −22,1 (p 0,005), México −20,0 (p 0,004), sin caída previa
significativa; Fed 2008: caída en [0,+1] (−10,2 y −17,2) pero precedida por otra en [−5,−1] (p 0,008).
**Lectura:** las líneas swap de la Fed de 2020 bajaron el spread al anunciarse; las FCL no. La beta
banca–spread se acerca a cero tras los eventos, pero también en las economías sin línea: no hay
desacople específico del respaldo.

## 25. La interacción en la cola alta del spread: regresión cuantílica (2026-10-21)

Fuente: `p35_cuantilica_spread.py` → `paper_p35_numeros.csv`, figura `fig_cuantilica_lnlag`. Mejora B8;
no preespecificada. MMQR (Machado y Santos Silva, 2019) con EF de país y de tiempo; regresión
cuantílica con indicadoras de país y de tiempo; MMQR con −DD_w. Bootstrap de bloques de país (499
réplicas; 199 en la de indicadoras); p bilateral por la fracción de réplicas del lado opuesto de cero.

| τ | MMQR β1 | MMQR β2 | MMQR β3 (p) | Indicadoras β3 (p) | MMQR −DD_w: β1 (p) / β3 (p) |
|---|---|---|---|---|---|
| 0,10 | −0,012 | 0,053 | −0,024 (0,63) | +0,003 (0,96) | 0,051 (0,13) / −0,008 (0,73) |
| 0,25 | 0,039 | 0,044 | −0,018 (0,66) | +0,003 (0,98) | — / −0,004 (0,76) |
| 0,50 | 0,105 | 0,031 | −0,010 (0,69) | +0,002 (0,94) | 0,083 (0,032) / +0,000 (0,95) |
| 0,75 | 0,153 | 0,022 | −0,005 (0,72) | +0,001 (0,86) | — / +0,004 (0,61) |
| 0,90 | 0,189 | 0,016 | −0,001 (0,94) | −0,007 (0,95) | 0,106 (0,024) / +0,006 (0,43) |

Localización (= regresión principal): β1 0,099, β2 0,032, β3 −0,011; escala: 0,063, −0,012, 0,007.
**Lectura:** la amplificación no aparece en la cola alta del spread. La fragilidad pesa más cuando el
spread es alto (y con −DD_w es significativa en la mediana y en τ = 0,90); el riesgo de cola pesa algo
más cuando es bajo (sin significancia).

## 26. Resiliencia preregistrada con datos trimestrales (2026-10-21)

Preregistro: `4_Redaccion/preregistro_resiliencia.md`, commit `c492ca3`, anterior a los datos y a la
estimación. Datos: `p41_datos_resiliencia.py` → `resiliencia_trimestral_bbg.csv`. QPSD: deuda del gobierno
general (trimestral; central para Argentina, China y parte de Turquía; anual interpolada para Chile, India
y Malasia, el 27 % de las obs. de R-H1). Reservas: Banco Mundial GEM, mensual (el FMI no expuso el código
del indicador; respaldo preregistrado). Deuda externa de corto plazo: QEDS. RA = ln(reservas / deuda
externa CP), mediana por país de 0,02 (Turquía) a 1,94 (Perú). Estimación: `p42_resiliencia_preregistrada.py`
→ `paper_p42_numeros.csv`.

| Prueba | Coeficiente | p uni wild | Holm | DK (bi) | Sin cada país | Veredicto |
|---|---|---|---|---|---|---|
| R-H2 fragilidad × RA_{t−4} (λ < 0), N = 725 | −0,063 | 0,29 | 0,29 | 0,001 | 1 de 13 | no se sostiene (término de reservas: exploratorio) |
| R-H3 riesgo de cola × DEBT_{t−4} (ψ > 0), N = 719 | +0,011 | 0,015 | 0,029 | 0,17 | 13 de 13 (0,008–0,014) | **firme** |
| R-H1 efecto directo controlado (N = 634) | 0,002 [−0,19; 0,16] | 0,48 | — | — | — | no se separa del canal fiscal; total 0,101 (DK 0,013) |

Efecto directo de DEBT_{t−4}: +0,144 (DK < 0,001). Secundarias: fragilidad × reservas/PIB −0,238 (wild uni
0,070); RA_{t−8} −0,035 (0,41); DEBT_{t−8} +0,0075 (0,082); LP mensual, respuesta del spread a Δ(−DD) en
estado de reservas altas menos bajas: h0 +0,004 (wild 0,58), h3 +0,003 (0,84), ninguna h < 0,10.
**Lectura:** con una d.e. más de deuda (≈ 20 pp del PIB) la semielasticidad del spread al riesgo de cola
pasa de 0,032 a 0,043. La consecuencia preregistrada para R-H2 aplica: las reservas quedan exploratorias.

## 27. Revisión econométrica: CCE, PMG, coeficientes aleatorios y VAR mensual (2026-10-21)

Fuente: `p43_revision_econometrica.py` → `paper_p43_numeros.csv`. No preespecificada.

| Estimador | Fragilidad | Riesgo de cola | Interacción |
|---|---|---|---|
| CCEP (cargas por país; cluster / wild) | 0,129 (0,090 / 0,145) | 0,0245 (<0,001 / 0,016); sin cada país 0,018–0,028, p máx 0,005 | −0,017 (0,31 / 0,37) |
| CCE-MG (12 economías) | 0,167 (0,10) | 0,006 (0,71) | −0,037 (0,14) |
| PMG largo plazo (12; bootstrap 199) | 0,065 (0,62) | 0,067 (0,006; IC [0,010; 0,103]) | — |
| Coeficientes aleatorios (DL): media; I² | 0,122 (0,095); 93 % | 0,024 (0,005); 58 % | — |
| — sin Turquía / sin Polonia | 0,084 (0,18) / 0,120 (0,11) | 0,027 (0,003) / 0,022 (0,011) | — |

PMG: φ̄ = −0,091, negativa en 11 de 12. Encogimiento: Turquía 0,462 → 0,452; Polonia 0,164 → 0,142. VAR
mensual (2 603 obs.): respuesta acumulada del spread a un choque de 1 d.e. de fragilidad, con la fragilidad
primero: +0,70 % al impacto, +1,02 % a 3 meses, +0,79 % a 12; con la fragilidad segunda: 0 al impacto, +0,67 %
[0,37; 0,93] a 3 meses, +0,40 % [0,23; 0,52] a 12. Varianza del spread a 12 meses explicada por la fragilidad:
0,5 % [0,25; 1,6] (primera) y 0,3 % [0,12; 0,80] (segunda).
**Lectura:** el riesgo de cola pasa a firme como asociación de nivel con cargas heterogéneas y una relación de
largo plazo; la fragilidad no gana nada; la interacción sigue nula.
