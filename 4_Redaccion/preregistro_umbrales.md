---
title: "Preregistro 4: umbrales de vigilancia (tensión financiera, deuda, riesgo de cola y alerta temprana)"
subtitle: "Escrito el 22 de octubre de 2026, antes de estimar cualquiera de los modelos que fija"
---

*Este documento fija las hipótesis de las mejoras U1–U6 de `4_Redaccion/evaluacion_macroprudencial.md`,
incluida la comparación entre los umbrales agrupados y los umbrales de cada economía por separado. Se
commitea solo y precede a los scripts `p52`–`p55`. Antes de escribirlo solo se verificó la cobertura de
los datos: fechas y número de trimestres por país con el FCI, con el FCI sin el bloque de tasas y con la
deuda trimestral, sin estimar nada. Todo son asociaciones, no causalidad: un umbral describe dónde cambia
la asociación, no una política óptima ni un efecto causal. Las métricas no son del autor (JLoss: Chari et
al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA).*

**Lo que ya se vio:**
- Hay un umbral de Hansen con el riesgo de cola D_{t−1} como variable de umbral sobre la pendiente de la
  fragilidad: γ = 0,12; 0,141 frente a 0,079; diferencia p = 0,08; LR = 6,0, bajo el valor crítico. En
  niveles, LR = 26,0 y 4,4 pb (p = 0,028).
- La deuda amplifica la transmisión del riesgo de cola de forma continua (R-H3, firme; con D4, 0,033).
- Ninguno de los dos riesgos mejora el pronóstico del **nivel** del spread fuera de la muestra.
- El FCI nunca se usó como variable de umbral ni como moderador. La deuda no se usó como umbral. No se
  calculó ningún AUROC.

**Cobertura verificada (muestra principal, N = 765, con la variable de umbral disponible):** Brasil 74,
Chile 74, China 78, Colombia 69, India 54, México 76, Perú 65, Polonia 88, Turquía 62, Malasia 39,
Indonesia 31, Sudáfrica 31 y Filipinas 11. El FCI sin el bloque de tasas tiene la misma cobertura.

## 1. Datos y definiciones

- **Panel y especificación principal:** `p14.base()` con `check_principal` (N = 765; β1 = 0,0985,
  β2 = 0,0324, β3 = −0,0112), con efectos fijos de país y de tiempo. J = ln JLoss_{t−1}, T = D_{t−1} y
  J×T, centrados como en `p42.centrar`.
- **Tensión financiera:** FCI_{t−1}, el índice de condiciones financieras domésticas de cada país que
  alimenta el GaR (`GaR_panel_all18.xlsx`, columna `FCI`; un valor mayor indica más tensión). Es
  trimestral y se fecha por el trimestre de la columna `Date`.
- **Variantes del FCI:**
  - sin el bloque de tasas (`GaR_panel_all19_noRyr.xlsx`), para evitar la circularidad con el spread;
  - en percentil propio de cada país, en rango de toda la muestra y, como versión operativa, en rango
    expansivo con un mínimo de 12 trimestres;
  - ortogonalizado respecto del VIX con una regresión por país.
- **Deuda:** deuda del gobierno general sobre PIB trimestral (`resiliencia_trimestral_bbg.csv`, `debt_q`),
  en t−4.
- **Riesgo de cola a un año:** D4 de `gar_insample_h4.csv`, como en el preregistro 2.
- **DD de Merton por país:** `fragilidad_alternativa_bbg.csv`, de `p34`.

## 2. Modelo de umbral agrupado (U1, U2 y U3)

**Especificación.** Para una variable de umbral q y un conjunto S de regresores con pendiente por régimen,
con H = 1[q > γ]:

ln EMBI_it = Σ_{x∈S} (β_x^alto · x·H + β_x^bajo · x·(1−H)) + (regresores sin cambio de régimen) + δ·H + φ·q + α_i + λ_t + ε_it

Se incluyen q en forma lineal y el indicador de régimen H, para que el umbral no capture un efecto de
nivel de la propia variable.

**Estimación:**
- Transformación within bidireccional, como `p13._within2`.
- γ por mínimos cuadrados concentrados en una malla de hasta 200 valores entre los percentiles 15 y 85 de
  q.
- Cada régimen debe tener al menos el 15 % de las observaciones y observaciones de al menos tres países.

**Inferencia:**
- **Linealidad:** sup-LR = (SSR_lineal − SSR(γ̂))/σ̂², con p del bootstrap de Hansen (1999) por bloques de
  país: se remuestrean países completos con sus residuos del modelo lineal, regresores fijos, 999
  réplicas. Como variante, wild por país con pesos de Rademacher.
- **Intervalo de γ:** inversión del LR con los valores críticos de Hansen (2000): 7,35 al 95 % y 5,94 al
  90 %.
- **Diferencia de pendientes por régimen:** p de wild por país (Webb, 999) en la dirección predicha, y
  también con Driscoll–Kraay.
- **Exclusión de cada país:** se reestiman γ y la diferencia.

**Las tres pruebas:**

| | Variable de umbral q | S (con régimen) | Sin régimen | Predicción |
|---|---|---|---|---|
| **U1** | FCI_{t−1} | J y T | J×T | Con más tensión pesan más: β_J^alto > β_J^bajo o β_T^alto > β_T^bajo |
| **U2** | deuda_{t−4} | T | J, J×T | β_T^alto > β_T^bajo |
| **U3** | D_{t−1} | J | T (lineal) | β_J^alto > β_J^bajo (rehace el modelo ya publicado, ahora con bootstrap) |

## 3. Umbrales país por país y comparación con el agrupado

**Muestra.** Se estima por país solo donde hay al menos 50 trimestres con la variable de umbral: Brasil,
Chile, China, Colombia, India, México, Perú, Polonia y Turquía, nueve economías. Las otras cuatro se
declaran sin muestra suficiente. Para la deuda vale el mismo umbral de 50.

**Especificación por país:**
- La variable dependiente es ln EMBI_t − λ̂_t, con λ̂_t, los efectos de tiempo de la regresión principal
  lineal agrupada, para descontar el componente global con la misma regla que el panel.
- **Variante:** ln EMBI_t con controles globales sin régimen: ln VIX_{t−1}, ln UST10Y_{t−1} y ln
  US HY_{t−1}.
- Lleva constante, q lineal, H, y los mismos S y regresores sin régimen que en el agrupado.
- La malla va entre los percentiles 15 y 85 del q del país, con al menos 10 observaciones por régimen.

**Inferencia por país:**
- Intervalo de γ_i por inversión del LR (Hansen, 2000), con el LR escalado por η̂², la corrección por
  heterocedasticidad de ese trabajo, al 90 % y al 95 %.
- Como alternativa, un intervalo percentil de bootstrap por bloques móviles (bloque de 4 trimestres, 999
  réplicas).
- Linealidad con el bootstrap de regresores fijos de Hansen (1996), 999 réplicas.
- Holm sobre los nueve países, dentro de cada variable de umbral.

**Comparación (fijada de antemano):**
- **C1:** cuántas de las nueve economías contienen el γ̂ agrupado en su intervalo al 90 %. Para el FCI la
  comparación se hace también en percentiles propios, porque el nivel del FCI de cada país puede no ser
  comparable.
- **C2:** prueba de umbral común con pendientes propias de cada país. Se compara Σ_i SSR_i(γ̃), con γ̃
  común que minimiza la suma, contra Σ_i SSR_i(γ̂_i). El estadístico es F_H = [Σ SSR_i(γ̃) − Σ
  SSR_i(γ̂_i)] / [Σ SSR_i(γ̂_i) / N], con p de wild bootstrap bajo el modelo de umbral común (Rademacher
  por observación dentro de cada país, 499 réplicas).
- **C3:** los γ̂_i en percentil propio: rango, mediana y dispersión, comparados con el umbral agrupado de
  la variante en percentiles.
- **C4:** pendientes por régimen de cada país y su media de grupo (con error estándar de la dispersión),
  comparadas con las agrupadas.
- **C5, solo para la deuda:** como la deuda cambia lento, su umbral por país puede ser un quiebre en el
  tiempo. Se compara el SSR del umbral con el de un modelo de quiebre en una fecha, con la misma malla
  (15–85 % de la muestra del país). Si el quiebre ajusta igual o mejor, el umbral de deuda de ese país no
  se distingue de un cambio en el tiempo.

**Lectura fijada:**
- El umbral agrupado se presenta como **umbral común** solo si C1 da 6 o más de 9 y C2 no rechaza al
  10 %.
- Si no, se presenta como el promedio de umbrales distintos, y la regla de vigilancia (U7) se expresa en
  **percentiles propios** de cada economía. Esa regla es común solo si los γ̂_i en percentil (C3) caen en
  un rango de 30 puntos percentiles o menos; si no, se declara que no hay un umbral transferible.

## 4. Alerta temprana (U4)

- **Episodio de estrés soberano:** C_it = 1 si ln EMBI_it − ln EMBI_{i,t−4} supera el percentil 90 de esa
  variación en el país.
- **Objetivo:** Y_it = 1 si hay un episodio en t+1 a t+4. Se excluyen las observaciones con C = 1 en t,
  t−1, t−2 o t−3, para evitar el sesgo post-crisis.
- **Señales en t:** ln JLoss_t, D_t, deuda_{t−1} (por el rezago de publicación) y FCI_t. Cada una se
  estandariza por país con media y desviación expansivas (mínimo de 12 trimestres). Como secundaria se
  usa −DD_t en lugar de JLoss.
- **Modelo combinado:** logit agrupado con las cuatro señales y sin efectos fijos, por los pocos eventos
  por país.
- **Fuera de la muestra:**
  - recursivo desde 2012T1;
  - en cada t se estima con las observaciones cuyo objetivo ya se observa (hasta t−4) y se predice t;
  - AUROC sobre las predicciones fuera de la muestra, con intervalo al 90 % y p unilateral frente a 0,5
    por bootstrap de bloques de país (999).
- **Umbrales de cada señal:**
  - se fijan con los datos de entrenamiento, minimizando L(μ) = μ·T1 + (1−μ)·T2, con μ = 0,5 y μ = 0,7;
    T1 es la fracción de episodios no anticipados y T2 la de falsas alarmas;
  - se evalúan fuera de la muestra con T1, T2 y la utilidad relativa de Alessi y Detken (2011).
- **Semáforo:** rojo si la señal supera τ(0,5); ámbar entre τ(0,7) y τ(0,5); verde bajo τ(0,7).
- **Por país,** de forma descriptiva: AUROC dentro de la muestra donde haya al menos 3 episodios.
- **Si hay menos de 20 episodios fuera de la muestra,** P3 se declara no evaluable y U4 se reporta solo
  como descriptivo.

## 5. Familia primaria, corrección y veredicto

| | Prueba | Estadístico | Dirección |
|---|---|---|---|
| **P1** | U1, umbral de tensión financiera agrupado | p bootstrap de la linealidad | — |
| **P2** | U2, umbral de deuda agrupado | p bootstrap de la linealidad | — |
| **P3** | U4, AUROC del logit combinado fuera de la muestra | p unilateral frente a 0,5 | > 0,5 |

- **Holm** sobre las tres.
- **Firme** exige tres condiciones:
  - p de Holm < 0,05;
  - en P1 y P2, que la diferencia de pendientes tenga el signo predicho, con p unilateral de wild < 0,10,
    para al menos uno de los regresores de S;
  - que ese signo se mantenga sin cada país.
- **Sugerente:** pasa sin Holm o solo con Driscoll–Kraay.
- Lo demás, **no hay evidencia**.

**Secundarias** (sin Holm, reportadas todas):
- U1 con las tres variantes del FCI y con la DD en lugar de JLoss;
- U2 con D4;
- U3;
- todo el bloque país por país (sección 3);
- el semáforo por señal;
- U5 y U6.

**Potencia** (diagnóstico): simulación con el modelo lineal estimado más un efecto de umbral en el que la
pendiente del régimen alto duplica la del bajo, con γ en la mediana de q; 200 réplicas. Se reporta la tasa
de rechazo del bootstrap de linealidad, agrupado y por país.

## 6. Secundarias adicionales

- **U5 (iMaPP):** índice acumulado de endurecimientos macroprudenciales en t−4 (Alam et al., 2019), total
  y separado en medidas de capital y liquidez bancarias y en medidas de crédito a hogares, como moderador
  con `p42.moderacion`:
  - las de capital, sobre J (predicción: atenúan, coeficiente < 0);
  - las de crédito, sobre T (predicción: atenúan).
  Si la base no es accesible, se declara.
- **U6 (medidas sistémicas):** MES (5 % de los peores días del índice) y ΔCoVaR por país con los retornos
  diarios de los bancos de JLoss. Se reportan la correlación de rangos con JLoss y el umbral U1
  reestimado con cada una en lugar de J.

## 7. Consecuencias fijadas de antemano

- **P1 firme:** la tesis agrega una "zona de tensión", con su semielasticidad y la fracción de trimestres de
  cada país en ella. La conclusión 2 se matiza: no hay amplificación multiplicativa en promedio, pero la
  transmisión cambia con el estado del sistema financiero.
- **P1 no firme:** la tesis dice que la transmisión no cambia de régimen con la tensión financiera
  doméstica, con la potencia que entregue la simulación.
- **P2 firme:** la implicancia `05_discusion.tex:27` se reescribe con el umbral de deuda y su intervalo.
- **P2 no firme:** se mantiene la amplificación continua (R-H3) y se declara que no hay un umbral de deuda
  detectable.
- **P3 firme:** el semáforo entra en la discusión.
- **P3 no firme:** el semáforo queda en el anexo como exploratorio, y la conclusión "ninguno de los dos
  riesgos pronostica el spread" se extiende a los episodios.
- **Bloque país por país:** la lectura de la sección 3 decide si la regla de U7 usa un nivel común,
  percentiles propios o ninguno.
- **Los resultados se reportan salgan como salgan,** en la tesis, el paper y las láminas.

## 8. Código

| Script | Contenido |
|---|---|
| `p52_umbrales.py` | U1–U3 agrupados y por país, C1–C5 y la simulación de potencia. Generaliza `p13.fig_umbral` a cualquier q y a S de más de un regresor |
| `p53_alerta_temprana.py` | U4 |
| `p54_imapp.py` | U5 |
| `p55_medidas_sistemicas.py` | U6 |

Las salidas van a `bbg/paper_p52…p55_numeros.csv` y a NUMEROS §31.
