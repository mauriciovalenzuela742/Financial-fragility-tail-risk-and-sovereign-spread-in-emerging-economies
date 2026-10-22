---
title: "Preregistro 6: un modelo cuantitativo de límite fiscal para el hallazgo central (N3)"
subtitle: "Escrito el 22 de octubre de 2026, antes de resolver el modelo con números y antes de la prueba en niveles"
---

*Este documento fija el modelo, su calibración, las predicciones que se comparan con los datos y una prueba
empírica nueva que el modelo sugiere (N3 de `4_Redaccion/plan_nota7.md`). Se commitea solo y precede a
`p59_modelo.py`. Antes de escribirlo solo se verificó que el crecimiento de los paneles del GaR es
interanual, de modo que el GaR y D4 están en puntos porcentuales de crecimiento anual. Las métricas no son
del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA).*

**Lo que ya se vio:**
- **En logaritmos:** D4 × deuda = 0,033 por desviación estándar de deuda (firme en la muestra, sin réplica
  externa concluyente). El riesgo de cola a un año tiene una semielasticidad de 0,047.
- **En puntos básicos:** la interacción con la deuda nunca se estimó.

## 1. El modelo

Es un modelo de límite fiscal de dos períodos, en la línea de Eaton y Gersovitz (1981), Bi (2012) y Ghosh
et al. (2013).
- **Deuda y servicio:** el gobierno debe b (deuda/PIB) y paga una tasa real r.
- **Crecimiento:** el crecimiento del año siguiente, g, se distribuye con mediana m y una cola izquierda de
  escala σ_L (una normal partida en la mediana: F(g) = Φ((g − m)/σ_L) bajo m).
- **Incumplimiento:** ocurre si el superávit primario que estabiliza la deuda supera la capacidad fiscal
  ps̄. Es decir, si (r − g)·b/(1 + g) > ps̄, lo que equivale a g < g*(b) = (r·b − ps̄)/(b + ps̄).
- **Probabilidad de incumplimiento:** π = F(g*(b)).
- **Spread:** con inversionistas neutrales al riesgo y una recuperación R,
  s = (1 + r_f)·(1 − R)·π / (1 − (1 − R)·π).
- **Riesgo de cola:** D = −q05 = 1,645·σ_L − m. Un aumento del riesgo de cola, con la mediana fija, es un
  aumento de σ_L, lo que coincide con el hallazgo de Adrian et al. (2019) de que se mueve la cola, no la
  mediana.

**Predicciones derivadas antes de calibrar** (con la cola izquierda normal y z = (g* − m)/σ_L < 0):
- **P-log:** ∂ln π/∂σ_L = −z·φ(z)/(σ_L·Φ(z)), que es decreciente en z. Como g* crece con b, el modelo
  predice que la semielasticidad del spread al riesgo de cola **cae** con la deuda: interacción negativa en
  logaritmos. Lo contrario de lo que estima la tesis.
- **P-nivel:** ∂π/∂σ_L = −z·φ(z)/σ_L, cuya derivada respecto de g* es φ(z)·(z² − 1)/σ_L². Es positiva
  mientras z < −1, es decir, mientras la probabilidad de incumplimiento sea menor que 16 %. El modelo
  predice una interacción **positiva en puntos básicos**.

## 2. Calibración (fijada)

**Momentos de la muestra de la prueba D4 × deuda** (N = 719):
- b = la deuda media en t−4, con su desviación estándar para expresar la interacción por desviación
  estándar.
- −q05 = la media de D4.
- m = la media de la media condicional del crecimiento (`gar_mean`).
- σ_L = (m − q05)/1,645.

**Parámetros:**
- r = 3 % real; r_f = 2 %.
- R = 0,63: el recorte medio de 37 % de Cruces y Trebesch (2013).
- ps̄ se calibra para que el spread del modelo, en la media, sea igual a la media geométrica del EMBI de la
  muestra.

**Predicciones** (derivadas numéricas centradas):
- β_log = ∂ln s/∂D y ψ_log = ∂²ln s/∂D∂b × sd(b);
- β_niv = ∂s/∂D en pb por punto porcentual y ψ_niv = ∂²s/∂D∂b × sd(b).
- Se evalúan en la media y en promedio sobre las observaciones, con la b y la D4 de cada una.

**Sensibilidad:**
- R ∈ {0,50; 0,63; 0,75} y r ∈ {1 %; 3 %; 5 %}, recalibrando ps̄ en cada caso;
- como alternativa, una cola izquierda t de Student con 5 grados de libertad (cola gruesa).

El rango de las predicciones sobre esa grilla es el "rango del modelo".

## 3. Comparación y prueba empírica nueva

**Comparación** con lo ya estimado:
- β_log frente a 0,047;
- ψ_log frente a 0,033.

Se reporta si la estimación cae dentro del rango del modelo y si el signo coincide.

**M6-H1 (prueba nueva, primaria):** la interacción en puntos básicos es positiva.
- **Especificación:** la misma regresión de la prueba D4 × deuda (`p42.moderacion`), con el spread en
  puntos básicos y JLoss en niveles (la forma en niveles de la tesis, `JLOSS_FORMA=nivlag`).
- **Inferencia:** p unilateral del wild por país (Webb, 999) y exclusión de cada país.
- **Firme:** p < 0,05 y el signo positivo con p < 0,10 sin cada una de las 13 economías.

**Secundarias:**
- M6-H1 con D_{t−1};
- la aleatorización de la deuda entre economías (999), como en `p56`;
- la comparación de ψ_niv estimado con el rango del modelo.

## 4. Consecuencias fijadas

- **Signos del modelo confirmados en los datos:** si el modelo predice ψ_log < 0 y ψ_niv > 0, y M6-H1 es
  firme, la tesis dice que el modelo de límite fiscal explica la amplificación en puntos básicos y **no** la
  de logaritmos. La interacción en logaritmos queda sin explicación teórica en ese modelo y se discuten las
  candidatas: aversión al riesgo de los inversionistas, recuperación que cae con la deuda y colas más
  gruesas.
- **M6-H1 no firme:** el modelo tampoco tiene respaldo en niveles, y se dice.
- **Magnitudes:** si la estimación cae fuera del rango del modelo, se dice cuánto y en qué dirección.
- Todo se reporta salga como salga.

## 5. Código

`1_Codigo/Panel/bbg/p59_modelo.py`: resolución y calibración del modelo, la grilla de sensibilidad, M6-H1 y
sus secundarias. Salida: `bbg/paper_p59_numeros.csv` y NUMEROS §34.
