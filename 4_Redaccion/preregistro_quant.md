---
title: "Preregistro 7: una señal de valor relativo con la fragilidad bancaria (Q1) y la cola de los cambios del spread bajo simultaneidad (Q3)"
subtitle: "Escrito el 23 de octubre de 2026, antes de construir cualquier retorno y antes de estimar"
---

*Este documento fija las dos primeras ramas del plan de `4_Redaccion/evaluacion_quant.md`:*
- *Q1: ¿la fragilidad bancaria ordena a los países según su retorno del mes siguiente?*
- *Q3: ¿la coincidencia de los dos riesgos ensancha la cola de los cambios del spread, aunque no suba su
  nivel?*

*Para cada una fija los datos, las especificaciones, la inferencia, el criterio de éxito y la consecuencia
de cada resultado. Se commitea solo y precede a `p60_senal_dd.py` y `p62_cola_cambios.py`. Las métricas no
son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA). Una señal
rentable sería una asociación predictiva, no un efecto causal.*

**Lo que ya se vio antes de escribir este documento:**
- **En la muestra** (NUMEROS §22, `p37_mensual_fechado.py`): d(−DD) del mes anterior se asocia con
  d ln EMBI del mes siguiente (0,0132, DK 0,005; suma de tres rezagos 0,027, *wild* < 0,001; 13 de 13 sin
  cada país). Una desviación estándar ≈ +0,6 % de spread al mes siguiente.
- **Regresión cuantílica trimestral** del nivel del spread (§25, `p35`): la fragilidad pesa más en el
  cuantil alto. La interacción no aparece en ningún cuantil. Nunca se estimó sobre cambios ni con el
  indicador de estrés conjunto.
- **Datos:** de `2_Datos/embi.xlsx` solo se miraron los nombres de las columnas y el rango de fechas
  (2000-01-03 a 2026-07-17). De `fragilidad_mensual_bbg.csv`, solo sus columnas. **No se ha construido
  ningún retorno, ningún portafolio ni ningún cuantil de cambios del spread.**

## 1. Datos y construcción comunes

**Universo.** Las 13 economías del panel principal: Brasil, Chile, China, Colombia, India, Indonesia,
Malasia, México, Perú, Filipinas, Polonia, Sudáfrica y Turquía. Hungría y Rumania están en `embi.xlsx`,
pero quedan fuera: Hungría se usó en la réplica externa (N2).

**Spread mensual.** s_{i,m} es el EMBI de cierre del mes, el promedio de los últimos cinco días hábiles
(como `p37.embi_mensual`), en pb.

**Retorno mensual de exceso, aproximado:**

  r_{i,m} = −D · (s_{i,m} − s_{i,m−1}) / 10 000 + s_{i,m−1} / (12 · 10 000),

con una duración D = 7 años igual para todos los países. Es una aproximación declarada: no hay índices de
retorno total por país en el repositorio. Si se consiguen los índices JPM EMBI GD de retorno total por
país, se reporta la versión con ellos como secundaria, sin cambiar la primaria.

**Fragilidad mensual sin anticipación (DD_lag).** Es la DD ponderada por pasivos de `p37.dd_mensual`, con
un cambio: un balance con fecha de cierre en el mes t solo se usa desde el mes t + 3, para cubrir el
rezago de publicación, que no se pudo verificar. La DD de `p37`, que usa el balance del mismo mes, se
reporta como secundaria.

**Riesgo de cola mensual.** D_{i,q−2} = −GaR del trimestre q − 2, con el mes m dentro del trimestre q, de
`gar_insample` en pseudo tiempo real. Se usa q − 2 y no q − 1 porque el crecimiento del trimestre anterior
se publica con rezago (como en `p45b_rezago_gar.py`).

**Muestra de evaluación:** de enero de 2015 al último mes con EMBI. Los umbrales y las estimaciones usan
solo la información disponible hasta el mes anterior, en ventana expansiva desde el inicio de cada serie.

**Costos de transacción.** Un bid-ask de 15 pb de spread en el caso base y de 25 pb como sensibilidad.
Cada operación paga la mitad: costo por unidad de rotación en un sentido = 0,5 × bid-ask × D / 10 000
(0,525 % en el caso base).

## 2. Q1 — Señal de valor relativo con la fragilidad bancaria

**Señal.** Al cierre del mes m − 1:

  z_{i,m−1} = DD_lag_{i,m−1} − DD_lag_{i,m−2},

es decir, el cambio de la distancia al incumplimiento. Un valor alto indica que los bancos mejoran.

**Portafolio:**
- **Universo de cada mes:** los países con s en m − 1 y en m y con z en m − 1. Si son menos de 6, el mes
  no se opera (retorno 0, sin costo).
- **Patas:** con n países, k = ⌊n/3⌋. Largo en los k de mayor z, corto en los k de menor z, igualmente
  ponderados: +1/k y −1/k.
- **Retorno:** R_m = Σ w_{i,m} r_{i,m} − costo_m, con costo_m = c · Σ_i |w_{i,m} − w_{i,m−1}|.
- Los empates se rompen por orden alfabético.

**Hipótesis primaria (Q1-H1).** El Sharpe anualizado de R_m, neto de costos en el caso base, es mayor que
cero.

**Inferencia:**
- prueba de Ledoit y Wolf (2008) para un Sharpe, con *bootstrap* circular studentizado por bloques de 6
  meses (4 999 réplicas);
- p unilateral, e IC del 90 %.

**Secundarias** (se reportan todas):
1. Sharpe bruto, y neto con 25 pb.
2. Sin Turquía.
3. Ponderación por rango (pesos proporcionales al rango centrado de z, que suman cero y cuya suma de
   valores absolutos es dos).
4. Horizonte de tres meses, con tres carteras superpuestas (Jegadeesh y Titman, 1993).
5. Alfa respecto del retorno equiponderado del universo, con errores de Newey–West de 6 rezagos.
6. Regresión de Fama–MacBeth de r_{i,m} sobre z_{i,m−1}, con errores de Newey–West.
7. Señal con la DD de `p37` (sin el rezago del balance).
8. Subperíodos 2015–2019 y 2020 en adelante.

**Criterio de éxito.** Q1-H1 tiene un p con corrección de Holm (sección 4) menor que 0,05 **y** el Sharpe
neto sin Turquía es positivo.

**Consecuencia fijada:**
- **Si pasa:** la precedencia mensual de la fragilidad es una señal de valor relativo **sugerente**,
  limitada a 13 países y con retornos aproximados. No se describe como estrategia operable ni como efecto
  causal.
- **Si no pasa:** se reporta que la precedencia mensual es estadística, pero no explotable neta de costos
  con la amplitud disponible.
- **En ambos casos:** el texto de la tesis sobre la precedencia mensual no cambia de grado.

## 3. Q3 — ¿La simultaneidad ensancha la cola de los cambios del spread?

**Indicadores de cada riesgo** (sin anticipación, en ventana expansiva por país, con al menos 36 meses de
historia):
- AltaJ_{i,m−1} = 1 si −DD_lag_{i,m−1} supera el percentil 2/3 de su propio país con los datos hasta
  m − 1. Es el mismo tercil alto de `p23_estres_conjunto.py`, pero sin mirar el futuro.
- AltaD_{i,m} = 1 si D_{i,q−2} supera el percentil 2/3 de los D de su país hasta q − 2.
- Conj_{i,m} = AltaJ × AltaD.

**Q3-H1 (escala).** Es una regresión cuantílica por momentos (MMQR; Machado y Santos Silva, 2019), con la
implementación de `p35_cuantilica_spread.py`:

  Δ ln s_{i,m} = α_i + δ_m + a₁AltaJ + a₂AltaD + a₃Conj + (σ_i + c₁AltaJ + c₂AltaD + c₃Conj)·U_{i,m},

con efectos de país y de mes en la localización y efectos de país en la escala.
- **Hipótesis:** c₃ > 0. La coincidencia ensancha la distribución de los cambios más allá de lo que
  ensancha cada riesgo por separado.
- **Inferencia:** *bootstrap* por bloques de país (999 réplicas), con p unilateral igual a la fracción de
  réplicas con c₃ ≤ 0.
- **Se reportan además:** c₁, c₂ y los cuantiles τ = 0,05; 0,50 y 0,95 implícitos.

**Q3-H2 (VaR condicional).** Pronóstico fuera de la muestra del VaR al 95 % del retorno r_{i,m}, de enero
de 2015 en adelante, reestimado cada mes con datos hasta m − 1.
- **Modelo condicional:** regresión cuantílica (τ = 0,05) de r_{i,m} sobre AltaJ, AltaD y Conj, con
  indicadoras de país. Sin efectos de mes, porque no se conocen de antemano.
- **Comparadores:**
  - (a) VaR histórico de 60 meses por país;
  - (b) VaR normal con varianza EWMA (λ = 0,97 mensual), por país.
- **Hipótesis:** la pérdida cuantílica (*tick loss*) media del modelo condicional es menor que la del
  EWMA. Se contrasta con la prueba de Diebold y Mariano, unilateral, con errores de Newey–West de 6
  rezagos sobre la serie de diferencias de pérdida agregada por mes.
- **Condición necesaria:** el modelo condicional no rechaza la cobertura condicional de Christoffersen
  (1998), con p > 0,05 sobre el panel apilado. Se reporta también la prueba de Kupiec.

**Secundarias:**
1. Horizonte de tres meses (Δ ln s de m − 1 a m + 2).
2. Sin 2020–2021.
3. Los indicadores con los terciles de toda la muestra, como en la tesis.
4. VaR al 99 %.
5. Comparación con el VaR histórico.
6. MMQR sin efectos de mes.

**Criterio de éxito:**
- Q3-H1 tiene un p con Holm menor que 0,05.
- Q3-H2 tiene un p con Holm menor que 0,05 y cumple la condición necesaria.

**Consecuencia fijada:**
- **Si Q3-H1 pasa:** la tesis puede decir que la simultaneidad no sube el nivel del spread, pero sí
  ensancha la distribución de sus cambios. Se reporta como sugerente si no resiste sin 2020–2021.
- **Si Q3-H2 pasa:** la simultaneidad es útil para medir el riesgo, no solo para describirlo.
- **Si ninguna pasa:** se reporta que la simultaneidad tampoco se asocia con una cola más ancha, y la
  conclusión de la tesis ("simultaneidad sin amplificación") queda igual.

## 4. Inferencia conjunta y reglas

- **Familia primaria:** Q1-H1, Q3-H1 y Q3-H2, con la corrección de Holm (1979) sobre los tres p
  unilaterales. Las secundarias no se corrigen y se leen como descriptivas.
- **Semillas:** 20261023 para todos los *bootstraps*.
- **Reporte:** todo resultado se reporta, salga como salga, con cifras en `NUMEROS_CANONICOS_BBG.md` (§36)
  y texto en la tesis y el paper como extensión preregistrada.
- **Desviaciones:** cualquier cambio necesario para que el código funcione (por ejemplo, un país sin
  balance suficiente para DD_lag, o un mes sin EMBI) se declara al reportar, con su razón. No se cambia
  ninguna decisión de esta lista después de ver un retorno.

## Referencias

- Christoffersen, P. (1998). Evaluating interval forecasts. *International Economic Review*, 39(4).
- Diebold, F. y Mariano, R. (1995). Comparing predictive accuracy. *Journal of Business & Economic
  Statistics*, 13(3).
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of
  Statistics*, 6(2).
- Jegadeesh, N. y Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*,
  48(1).
- Kupiec, P. (1995). Techniques for verifying the accuracy of risk measurement models. *Journal of
  Derivatives*, 3(2).
- Ledoit, O. y Wolf, M. (2008). Robust performance hypothesis testing with the Sharpe ratio. *Journal of
  Empirical Finance*, 15(5).
- Machado, J. y Santos Silva, J. (2019). Quantiles via moments. *Journal of Econometrics*, 213(1).
