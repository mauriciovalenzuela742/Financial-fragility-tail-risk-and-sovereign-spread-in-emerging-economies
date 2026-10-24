---
title: "Preregistro 8: valor razonable (Q2), cobertura condicional (Q4), nowcast mensual del GaR (Q6) y deuda × riesgo de cola en puntos básicos (Q5)"
subtitle: "Escrito el 23 de octubre de 2026, antes de estimar cualquiera de estas pruebas"
---

*Este documento fija las ramas restantes del plan de `4_Redaccion/evaluacion_quant.md`, después del
preregistro 7 (`preregistro_quant.md`, Q1 y Q3, ninguna hipótesis aprobada). Se commitea solo y precede a
`p61_valor_razonable.py`, `p63_cobertura.py`, `p64_nowcast_gar.py` y `p65_deuda_pb_mensual.py`. Las
métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA). Todo son asociaciones.*

**Lo que ya se vio antes de escribir este documento:**
- Los resultados de Q1 y Q3 (NUMEROS §36): la DD mensual no ordena los retornos entre países. La fragilidad
  alta ensancha la distribución de los cambios del spread, pero la coincidencia de los dos riesgos no la
  ensancha más.
- El PMG de la tesis: el riesgo de cola tiene una relación de largo plazo con el spread (0,067, §27).
- **Datos que se revisaron solo por su estructura** (columnas y fechas), sin estimar nada:
  - FCI mensual por país en `1_Codigo/GaR/individuals/<PAÍS>/FCI_<PAÍS>.csv`, hasta 2026-05;
  - crecimiento interanual trimestral y VIX en `GaR_panel_all18.xlsx`;
  - VIX diario en `2_Datos/VIX_History.csv`;
  - deuda trimestral `debt_q` en `resiliencia_trimestral_bbg.csv`.

**Q7 y Q8 no son factibles con los datos del repositorio**, y así se declara:
- **Q7** necesita los CDS de los bancos, que no se extrajeron de Bloomberg.
- **Q8** necesita las fechas de las calificaciones soberanas, que no están. Las fechas de programas del FMI
  tampoco están compiladas, y las líneas de respaldo ya se estudiaron en `p39` (9 eventos).

Quedan como trabajo futuro, con un preregistro propio si se consiguen los datos.

## 1. Bases comunes (las del preregistro 7)

- **Universo:** 13 economías.
- **Datos:** spread mensual de cierre s_{i,m} y retorno aproximado r = −7·Δs/1e4 + s/(12·1e4)
  (`p60.panel_mensual`). Evaluación desde 2015-01, con ventana expansiva y sin anticipación.
- **Rezagos de los fundamentos:**
  - JLoss y el riesgo de cola del trimestre q − 2;
  - la deuda del trimestre q − 4, como en la tesis;
  - la DD mensual con el balance desde t + 3.
- **Inferencia y reglas:**
  - semilla 20261023;
  - Newey–West con 6 rezagos;
  - Holm sobre la familia primaria Q2-H1, Q4-H1 y Q5-H1;
  - reporte salga como salga, en NUMEROS §37 y como extensión en la tesis y el paper;
  - desviaciones declaradas con su razón.

## 2. Q2 — Valor razonable y reversión del residuo

**Modelo.** Se reestima cada mes m, desde 2015-01, con todos los datos hasta m:

  ln s_{i,τ} = α_i + λ_τ + β₁ ln JLoss_{i,q(τ)−2} + β₂ D_{i,q(τ)−2} + β₃ deuda_{i,q(τ)−4} + e_{i,τ},

con efectos de país y de mes. El residuo ê_{i,m} es la "riqueza" del país al cierre de m: positivo indica
spread por sobre su valor razonable (barato).

**Pronóstico:**
- Δ̂ ln s_{i,m+1} = κ̂_m · ê_{i,m}, con κ̂_m de la regresión agrupada de Δ ln s_{i,τ+1} sobre ê_{i,τ},
  para τ ≤ m − 1.
- Los residuos históricos se calculan con el modelo estimado en m. Esto es una mirada hacia adelante en β,
  declarada; los resultados futuros que entran a κ̂ son solo los ya observados.

**Q2-H1.** El pronóstico mejora al de cambio cero (paseo aleatorio) para Δ ln s a un mes. Se contrasta con
la prueba de Clark y West (2007): el estadístico por país y mes se promedia por mes y se aplica un t de
Newey–West, unilateral.

**Secundarias:**
1. Horizonte de tres meses.
2. Vida media del residuo: mediana entre países de ln 0,5 / ln ρ̂_i, con ρ̂_i del AR(1) de ê.
3. Cartera larga en el tercil más barato y corta en el más caro, neta de 0,525 % por unidad de rotación,
   con la prueba de Sharpe de Ledoit–Wolf (`p60.ledoit_wolf`). Se compara con una cartera de carry (por el
   nivel de s) y una de momentum (por Δ ln s a tres meses).
4. Modelo sin la deuda.
5. Sin Turquía.

**Criterio de éxito:** p con Holm < 0,05 **y** vida media menor que seis meses.

**Consecuencia:**
- **Si pasa:** los fundamentos de la tesis definen un valor razonable con reversión explotable como
  pronóstico (sugerente, 13 países).
- **Si no pasa:** la relación de largo plazo de la tesis describe niveles, pero no pronostica los cambios
  del mes siguiente.

## 3. Q4 — Cobertura condicional al factor común

**Factor:** F_{i,m} = Δ ln del promedio simple de s de las otras doce economías, que aproxima el índice
EMBI. La variable a cubrir es y_{i,m} = Δ ln s_{i,m}.

**Modelos.** La razón de cobertura del mes m se estima solo con datos hasta m − 1. La pérdida es el
cuadrado del residuo cubierto, u = y − β̂·F.
- **(a) Beta fijo** por país, con toda la historia.
- **(b) Beta móvil** por país, con 36 meses.
- **(c) Beta condicional:** β_{i,m} = b_i + c₁·zDD_{i,m−1} + c₂·zDeuda_{i,q−4}. z son la −DD_lag y la
  deuda estandarizadas con la media y la desviación del panel hasta m − 1. Se estima por MCO agrupado de y
  sobre F interactuado con indicadoras de país y con zDD·F y zDeuda·F.

**Q4-H1.** La pérdida media de (c) es menor que la de (b). Se contrasta con la prueba de Diebold–Mariano
unilateral sobre la diferencia de pérdidas promediada por mes (Newey–West, 6).

**Secundarias:**
1. (c) frente a (a).
2. ΔVIX (log del cierre mensual) como factor.
3. Solo zDD y solo zDeuda.
4. Sin Turquía.
5. Los coeficientes c₁ y c₂ de toda la muestra, con errores agrupados por país.

**Criterio de éxito:** p con Holm < 0,05.

**Consecuencia:**
- **Si pasa:** la fragilidad o la deuda cambian la exposición de cada país al factor común lo suficiente
  para mejorar la cobertura.
- **Si no pasa:** la cobertura estándar de 36 meses basta.

## 4. Q6 — Nowcast mensual del riesgo de cola

**Modelo trimestral** (regresión cuantílica lineal, τ = 0,05, con indicadoras de país), reestimado en
ventana expansiva:

  Q₀,₀₅(g_{i,τ+1} | g_{i,τ−2}, FCI_{i,τ}, VIX_τ),

con g el crecimiento interanual (`GaR_panel_all18.xlsx`) y FCI y VIX en el último mes del trimestre τ. El
FCI viene de los archivos mensuales por país y el VIX es el promedio de los cierres diarios del mes.

**Nowcast en el mes m del trimestre q:**
- N_{i,m} = −100 · Q̂, en pp como D, con los coeficientes estimados usando solo los trimestres τ con
  g_{τ+1} publicado (τ + 1 ≤ q − 2).
- Regresores: FCI_{i,m}, VIX_m y g_{i,q−2}.

**Criterio de validación** (no entra en la familia de Holm). En los meses de fin de trimestre desde 2015,
la correlación entre N y el D oficial del panel del mismo trimestre es mayor que 0,9, **y** el error
absoluto mediano es menor que 0,5 pp. Se reportan también las correlaciones dentro de cada país.

**Consecuencia:**
- **Si valida:** el riesgo de cola puede seguirse mes a mes en tiempo real.
- **Si no valida:** el nowcast se reporta como una medida distinta del GaR oficial, y Q5 pasa a ser
  exploratoria.

## 5. Q5 — Deuda × riesgo de cola en puntos básicos, con frecuencia mensual

**Especificación.** Es la predicción del modelo de límite fiscal (`p59`, +91 pb por d.e. de deuda):

  s_{i,m} (pb) = α_i + λ_m + a₁·N_{i,m−1} + a₂·zDeuda_{i,q−4} + a₃·(N_{i,m−1} × zDeuda_{i,q−4}) + e,

con N centrado, zDeuda estandarizada y efectos de país y de mes. Muestra: de 2015-01 en adelante.

**Q5-H1:** a₃ > 0.
- **Inferencia:** *wild cluster bootstrap* por país (Webb, 999; `p32.wild`), con p unilateral igual a la
  mitad del bilateral cuando a₃ > 0 (1 − p/2 si a₃ < 0).
- **Condición:** a₃ > 0 en al menos 10 de las 13 exclusiones de un país.

**Secundarias:**
1. En cambios: Δs_{i,m} sobre ΔN_{i,m−1}, zDeuda y su producto.
2. En logaritmos.
3. Con el D trimestral oficial (q − 2) en lugar de N.
4. Sin Turquía.

**Criterio de éxito:** p con Holm < 0,05 y la condición de exclusiones. Si Q6 no valida, Q5 se reporta
como exploratoria, cualquiera sea su p.

**Consecuencia:**
- **Si pasa:** la interacción en puntos básicos que predice el modelo aparece con datos mensuales; se
  compara su magnitud con el rango del modelo (10 a 203 pb).
- **Si no pasa:** el modelo tampoco tiene respaldo en puntos básicos con datos mensuales.

## Referencias

- Clark, T. y West, K. (2007). Approximately normal tests for equal predictive accuracy in nested models.
  *Journal of Econometrics*, 138(1).
- Diebold, F. y Mariano, R. (1995). Comparing predictive accuracy. *Journal of Business & Economic
  Statistics*, 13(3).
- Ledoit, O. y Wolf, M. (2008). Robust performance hypothesis testing with the Sharpe ratio. *Journal of
  Empirical Finance*, 15(5).
