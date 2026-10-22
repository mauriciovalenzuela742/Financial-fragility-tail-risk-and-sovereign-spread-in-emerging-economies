---
title: "Preregistro 5: réplica externa del hallazgo central (N2) y choques exógenos al riesgo de cola (N1)"
subtitle: "Escrito el 22 de octubre de 2026, antes de construir los datos de las economías nuevas y antes de estimar"
---

*Este documento fija las pruebas N1 y N2 de `4_Redaccion/plan_nota7.md`. Se commitea solo y precede a los
scripts `p57` y `p58`. Antes de escribirlo solo se verificó qué datos existen, sin estimar nada:
- **Hungría:** EMBI diario 2000–2026 en `2_Datos/embi.xlsx`, 3 bancos en Bloomberg, GaR en los paneles del
  GaR y deuda trimestral del gobierno general (QPSD, 106 trimestres).
- **Corea del Sur:** CDS soberano 2004–2026 (`output_macro/southkorea`), 9 bancos, GaR y solo 14 trimestres
  de deuda QPSD.
- **Bulgaria:** queda fuera, con un banco y CDS hasta 2012.
- **Instrumento:** el choque de términos de intercambio de materias primas (`ctot_shock_bbg.csv`) cubre las
  trece economías del panel, no Hungría ni Corea.

Todo son asociaciones salvo lo que el instrumento identifique bajo sus supuestos, que se declaran. Las
métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA).*

**Lo que ya se vio:**
- En el panel de 13 economías, D4_{t−1} × deuda_{t−4} = 0,033 (wild 0,005; DK 0,033; permutación de la
  deuda 0,009).
- D_{t−1} × deuda = 0,011 (permutación 0,17, sugerente).
- Con Holm sobre las 14 hipótesis de los preregistros 1–4, ninguna bajo 0,05.
- El instrumento *shift-share* para la fragilidad falló (signos opuestos, Sargan rechaza). Nunca se estimó
  un instrumento para el riesgo de cola.

## 1. N2 — Réplica externa en Hungría y Corea del Sur

**Datos (p57):**
- **JLoss:** con el mismo motor y protocolo (`jloss_engine`: `quarterly_inputs`, `merton_pd` y
  `compute_jloss`), con los bancos de `Bloomberg_extraction/output/{hungary,southkorea}`.
- **Spread:**
  - Hungría: EMBI de `2_Datos/embi.xlsx`, columna `Hungria`.
  - Corea: CDS a 5 años de Bloomberg, porque no tiene EMBI.
  - Promedio trimestral de los días, como en `p1_build_panels.py`.
- **Riesgo de cola:** D4 de `gar_insample_h4.csv` y D (pseudo tiempo real) de `gar_panel_all18.csv`, con el
  mismo signo (D = −GaR × 100).
- **Deuda:** gobierno general QPSD; si falta, gobierno central QPSD; si falta, la serie anual de deuda/PIB
  del FMI interpolada, como el `DEBT` de `p42`. En t−4.

**Especificación primaria (N2-H1),** la de la prueba que resistió la inferencia conjunta:
- **Variable dependiente:** y_it = ln spread_it − λ̂_t, donde λ̂_t son los efectos de tiempo de la misma
  regresión estimada en el panel original de 13 economías. Así se descuenta el componente global con la
  misma regla, sin estimar efectos de tiempo con dos economías.
- **Regresión:**

  y_it = β1 J_it + β2 T_it + β3 J_it·T_it + δ M_it + ψ T_it·M_it + α_i + ε_it

  con J = ln JLoss_{t−1}, T = D4_{t−1}, M = deuda_{t−4} y efectos fijos de país.
- **Centrado y estandarización con los momentos del panel original:** J y T se centran con sus medias
  originales, y M se estandariza con la media y la desviación del original. Así ψ es directamente
  comparable con 0,033.

**Inferencia:**
- Bootstrap por bloques móviles en el tiempo (bloques de 4 trimestres que remuestrean juntos los trimestres
  de las dos economías; 999 réplicas). p unilateral = fracción de réplicas con ψ* ≤ 0, centrado en ψ̂.
- Como referencia, errores de Driscoll–Kraay.

**Criterio de éxito (fijado):**
- **Réplica:** ψ̂ > 0 con p unilateral < 0,05, y la diferencia con el original (ψ̂ − 0,033) no se rechaza al
  10 % (prueba z con ambos errores estándar).
- **Réplica parcial:** ψ̂ > 0 con p < 0,10, o la diferencia no se rechaza pero ψ̂ no es significativo.
- **No replica:** ψ̂ ≤ 0, o la diferencia se rechaza al 10 %.

**Potencia (diagnóstico):** simulación con ψ = 0,033 y los residuos y regresores de la muestra nueva
(bootstrap por bloques; 500 réplicas). Se reporta la tasa de éxito. Si la potencia es menor que 0,5, la
tesis lo dice junto al resultado.

**Secundarias:**
- La misma regresión con T = D_{t−1} (el riesgo de cola del trimestre siguiente).
- Cada economía por separado (con HAC).
- Controles globales (ln VIX, ln UST10Y, ln US HY, en t−1) en lugar de λ̂_t.
- **Observaciones nuevas de economías conocidas:** Indonesia, Filipinas y Sudáfrica con su CDS en los
  trimestres en que no tienen EMBI en la muestra principal. Es la misma especificación, con λ̂_t del
  original y efectos fijos de país.

## 2. N1 — Choques de términos de intercambio como instrumento del riesgo de cola

**Instrumento.** Z_{i,t−1} = CTOT_{i,t−1} − CTOT_{i,t−5}: el cambio a cuatro trimestres del índice de
precios de materias primas ponderado por la canasta exportadora de 1998–2003 (`ctot_shock_bbg.csv`,
Gruss, 2014). Es un diseño *shift-share*: las participaciones son predeterminadas y los precios son
mundiales. Un alza de los precios de lo que exporta la economía debería reducir su riesgo de cola del año
siguiente.

**Especificación primaria (N1-H1),** en el panel de 13 economías con la muestra de la prueba D4 × deuda:

ln EMBI_it = β1 J + β2 T + δ M + ψ T·M + α_i + λ_t + ε_it

- T = D4_{t−1}; M = deuda_{t−4} estandarizada.
- T y T·M son endógenas, con los instrumentos Z y Z·M. Es un modelo exactamente identificado.
- El término J·T de la principal se omite, porque contiene a T y su coeficiente es nulo; se declara.

**Fuerza del instrumento (requisito previo):**
- F condicional de Sanderson y Windmeijer (2016) para cada endógena, con errores agrupados por país.
- **Si alguno es menor que 10, el instrumento se declara débil y N1 no identifica,** sea cual sea la
  estimación de 2SLS. Igual se reportan la forma reducida y la estimación.

**Inferencia:**
- 2SLS con errores de Driscoll–Kraay.
- p unilateral de ψ por bootstrap de pares por país (999 réplicas): la fracción de réplicas con ψ* ≤ 0,
  centrada.

**Criterio de éxito:** instrumento fuerte (los dos F ≥ 10), ψ̂ > 0 con p unilateral < 0,05, y el signo se
mantiene sin cada país.

**Supuestos que se declaran:**
- **Exclusión:** el choque de precios de materias primas afecta al spread solo a través del riesgo de cola
  y de su interacción con la deuda. Es un supuesto fuerte: los precios de las materias primas también
  mueven los ingresos fiscales y la cuenta corriente. Por eso, si N1 tiene éxito, se lee como "la deuda
  amplifica la respuesta del spread a los choques de crecimiento que vienen de los precios de las
  materias primas", no como un efecto causal aislado del GaR.
- **Exogeneidad de las participaciones:** las canastas son anteriores a la muestra (1998–2003).

**Secundarias:**
- La forma reducida: ln EMBI sobre Z y Z·M, con la predicción de que el coeficiente de Z·M sea negativo.
- La primera etapa: Z sobre D4, con la predicción de un signo negativo.
- N1 con T = D_{t−1}.
- Proyecciones locales con instrumento a h = 0, 4 y 8 trimestres para ψ.

## 3. Familia, corrección y consecuencias

- **Familia primaria:** {N2-H1, N1-H1}, con Holm sobre los dos p unilaterales. N1-H1 entra con p = 1 si el
  instrumento es débil.
- **Firme:** pasa Holm y cumple su criterio de éxito.
- **Consecuencias (fijadas):**
  - **N2 replica:** la tesis presenta el hallazgo central a un año como replicado fuera de la muestra, en
    dos economías que no se usaron para descubrirlo, con la potencia que entregue la simulación.
  - **N2 no replica:** la tesis lo dice en el resumen, la introducción y las conclusiones, y el hallazgo
    central queda como resultado de la muestra original.
  - **N1 firme:** la conclusión se reformula como amplificación de choques de crecimiento exógenos, con el
    supuesto de exclusión explícito.
  - **N1 débil o no firme:** se declara que el instrumento no identifica y la identificación sigue siendo
    la de las secciones anteriores.
- Los resultados se reportan salgan como salgan, en la tesis, el paper y las láminas.

## 4. Código

| Script | Contenido |
|---|---|
| `p57_replica_externa.py` | Datos de Hungría y Corea (JLoss, spread, GaR, deuda), N2-H1, secundarias y potencia |
| `p58_iv_choques.py` | N1-H1, F de Sanderson–Windmeijer, forma reducida, proyecciones locales con instrumento y Holm de la familia |

Las salidas van a `bbg/paper_p57_numeros.csv` y `bbg/paper_p58_numeros.csv`, y a NUMEROS §33.
