---
title: "Evaluación macroeconómica de la tesis"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lente de un macroeconomista (21 de octubre de 2026)"
---

*Evaluación de la versión del commit `c3dbc1b`: tesis de 144 pp. con el capítulo de resultados en 44 pp.
y las baterías en el Anexo D. Usa la misma rúbrica que `evaluacion_experta.md` (proxy de la pauta del
Magíster en Economía Aplicada, escala de 1,0 a 7,0) y cambia la pregunta de fondo. La evaluación anterior
juzgaba sobre todo la econometría; esta pregunta si la tesis dice algo creíble y útil sobre la
determinación del riesgo soberano en economías emergentes. Las métricas no son del autor (JLoss: Chari
et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA) y todo son asociaciones, no causalidad.*

---

# 1. Nota

| # | Criterio | Peso | Nota | Aporte | Antes (econometría) |
|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,3 | 0,945 | 6,3 |
| 2 | Marco teórico y literatura | 10 % | 6,0 | 0,600 | 6,2 |
| 3 | Datos y construcción de las métricas | 15 % | 6,0 | 0,900 | 6,2 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,7 |
| 5 | Inferencia y robustez | 15 % | 6,8 | 1,020 | 6,8 |
| 6 | Interpretación | 15 % | 6,3 | 0,945 | 6,5 |
| 7 | Redacción, estructura y extensión | 5 % | 5,8 | 0,290 | 5,4 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,9 | 0,345 | 6,8 |
| | **Nota ponderada** | | | **6,2** | 6,2 |

**Rango:**
- **5,8:** si la comisión tiene un macroeconomista que lea el GaR a un trimestre como un mal proxy del
  riesgo de solvencia.
- **6,6:** si la tesis reencuadra su contribución en torno al resultado deuda × riesgo de cola (sección 3,
  M1–M2).

**En una frase:** la econometría es de primer nivel para un magíster, pero el hallazgo más valioso para
un macroeconomista es el que la tesis todavía trata como secundario. Donde hay más deuda pública, la
cola adversa del crecimiento pesa más en el precio de la deuda. Es exactamente lo que predicen los
modelos de incumplimiento soberano, y la tesis aún no lo conecta con ellos.

---

# 2. Evaluación por criterio, desde la macroeconomía

## 2.1 Pregunta y contribución — 6,3
- La pregunta original (bancos frágiles × cola del crecimiento) es interesante, pero en la teoría de
  riesgo soberano la interacción natural es otra: **deuda × crecimiento**. En Eaton–Gersovitz, Arellano
  (2008) y Aguiar–Gopinath (2006), el spread es convexo en la deuda y en el producto, y el incentivo a
  no pagar crece cuando coinciden mucha deuda y malas perspectivas de crecimiento.
- La prueba preregistrada encuentra justamente eso (R-H3: +0,011 por d.e. de deuda; Holm 0,029; 13 de
  13 sin cada país). Es el resultado más publicable de la tesis.
- Hoy aparece como la conclusión 4, después de tres conclusiones mayoritariamente nulas o modestas.

## 2.2 Marco teórico — 6,0
- **A favor:** la derivación desde la intensidad de incumplimiento (Duffie–Singleton) que separa la
  aditividad en logaritmos de la amplificación sigue siendo un aporte fino.
- **Faltan los modelos cuantitativos de incumplimiento soberano** (Arellano, 2008; Aguiar y Gopinath,
  2006; Mendoza y Yue, 2012). Darían el fundamento de R-H3 y de la relación de largo plazo entre el
  spread y el riesgo de cola (PMG: 0,067).
- **Falta el pecado original** (Eichengreen y Hausmann): la moneda de la deuda decide si la cola del
  crecimiento se traduce en problemas de pago.
- **Falta el ciclo financiero global** (Rey, 2013; Miranda-Agrippino y Rey, 2022) como marco de por qué
  los efectos fijos de tiempo no bastan. La propia tesis muestra con el CCE que las cargas sobre los
  factores comunes difieren entre países.
- **Doom loop:** Farhi–Tirole predice que el pasivo contingente bancario pesa más con un soberano
  endeudado (deuda × fragilidad), y la tesis no lo prueba.

## 2.3 Datos y métricas — 6,0
- **El GaR mide el riesgo equivocado para la solvencia.** Es el cuantil 5 % del crecimiento a **un
  trimestre**, condicionado en un índice de condiciones financieras. La sostenibilidad de la deuda
  depende del crecimiento a 3–5 años (r − g), y el GaR de corto plazo es sobre todo un termómetro de
  condiciones financieras. Que no aparezca en los cambios ni mejore el pronóstico es coherente con eso:
  mide tensión financiera de corto plazo, no capacidad de pago.
- **El rótulo "riesgo económico" sobrevende la variable.** Con el FCI como único condicionante del
  cuantil, el GaR es "riesgo de crecimiento inducido por condiciones financieras". Conviene decirlo.
- **Los datos trimestrales de deuda (QPSD) son un avance**, pero faltan para Chile, India y Malasia (27 %
  de las observaciones de R-H1 con la serie anual).
- **Faltan la calificación soberana histórica**, la composición por moneda de la deuda y los términos
  de intercambio. Son los tres determinantes macro del spread más citados.
- JLoss saturado; la distancia al incumplimiento de Merton funciona mejor (anexo).

## 2.4 Estrategia e identificación — 5,8
- **Bien resueltos:** el CCE (cargas heterogéneas), el PMG (largo plazo), el fechado mensual y el
  estudio de eventos (las swap de 2020 bajaron el spread 20–22 pp).
- **Lo que un macroeconomista objetaría:**
  1. La deuda en R-H3 es endógena al ciclo; la variación de la deuda dentro del país no está aislada de
     las recesiones que también mueven el GaR.
  2. El modelo no separa los componentes global e idiosincrásico del spread (Longstaff et al., 2011),
     algo estándar en esta literatura.
  3. No hay ninguna fuente de variación exógena macro (por ejemplo, choques de términos de intercambio
     como instrumento del crecimiento, del tipo usado en la literatura de commodities).

## 2.5 Inferencia y robustez — 6,8
Sin cambios respecto de la evaluación anterior: simulación de tamaño y potencia, wild bootstrap, Holm,
equivalencia, preregistro acreditado por git. Es lo mejor del trabajo.

## 2.6 Interpretación — 6,3
- **A favor:** el vocabulario es disciplinado, y las implicancias de política ahora incluyen el espacio
  fiscal, que es la lectura correcta de R-H3.
- **En contra:**
  - La palabra "riesgo económico" para el GaR de corto plazo (2.3).
  - La conclusión de que el riesgo de cola "agrega poco" convive mal con su relación de largo plazo
    robusta. En macro, un fundamento de largo plazo que no predice el próximo trimestre no es poco: es
    lo esperable de un fundamento.
  - Las implicancias no distinguen regímenes cambiarios ni la moneda de la deuda.

## 2.7 Estructura — 5,8
- **Mejoró:** el capítulo de resultados pasó de 62 a 44 pp. y las baterías están en el anexo.
- **Sigue largo:** la tesis tiene 144 pp. El orden de las conclusiones no sigue la importancia
  macroeconómica de los hallazgos.

## 2.8 Reproducibilidad — 6,9
Datos trimestrales con caché commiteada, preregistro anterior a los datos, pipeline documentado.

---

# 3. Mejoras propuestas desde la macroeconomía (priorizadas)

| # | Mejora | Por qué | Costo |
|---|---|---|---|
| M1 | **Reencuadrar la contribución:** el hallazgo central es deuda × riesgo de cola; la pregunta bancos × cola queda como hipótesis inicial no confirmada. Reordenar el resumen, la introducción y las conclusiones | Es el resultado firme, preregistrado y con fundamento teórico | 1–2 días |
| M2 | **Anclar R-H3 en los modelos de incumplimiento soberano** (Arellano, 2008; Aguiar–Gopinath, 2006): un párrafo de marco y una predicción explícita | Convierte un hallazgo empírico en la confirmación de una predicción | 1 día |
| M3 | **GaR de mediano plazo:** reestimar el GaR a 4 y 8 trimestres (Adrian et al. muestran una estructura temporal) y repetir H2/R-H3 | Mide el crecimiento que importa para la sostenibilidad; podría explicar por qué el GaR a un trimestre no aparece en cambios | 3–5 días (motor GaR existente; h es un parámetro) |
| M4 | **Composición por moneda de la deuda** (QPSD la desagrega) como moderador de R-H3, preregistrado | Pecado original: la deuda en dólares debería amplificar más | 2 días |
| M5 | **Descomponer el spread** en componente global (factor común del EMBI) e idiosincrásico, y regresar el idiosincrásico | Estándar en la literatura (Longstaff et al.); aísla el riesgo doméstico | 1–2 días |
| M6 | **Doom loop completo:** deuda × fragilidad, preregistrado | Es la predicción de Farhi–Tirole que la tesis cita y no prueba | 1 día |
| M7 | **Calificación soberana histórica** (S&P/Moody's por trimestre) como control y moderador | El determinante más citado; falta en la réplica de Chari et al. | 2 días (dato a conseguir) |
| M8 | **Régimen cambiario** (Ilzetzki–Reinhart–Rogoff) y **exportadores de materias primas** como cortes | Validez externa e implicancias de política diferenciadas | 2 días |
| M9 | **Renombrar** "riesgo económico" como "riesgo de crecimiento inducido por condiciones financieras" o explicar su alcance | Precisión conceptual frente a un macroeconomista | 0,5 días |

**Ruta recomendada antes de diciembre:** M1, M2 y M9 (redacción, 3 días); M6 y M4 preregistradas (datos
ya disponibles o casi); M3 si el tiempo alcanza, porque es la que más puede cambiar la lectura del riesgo
de cola. M5, M7 y M8 quedan para el paper.

**Nota esperada con M1–M4 y M9:** en torno a 6,5. El techo restante es la identificación, que en esta
literatura rara vez se resuelve en una tesis de magíster.

---

# 4. Registro de aplicación (21 de octubre de 2026)

Preregistro 2: `preregistro_macro.md`, commit `f820594`, anterior a los datos. Cifras en
`NUMEROS_CANONICOS_BBG.md`, §28.

| # | Estado | Resultado |
|---|---|---|
| M1 | Hecho | "Hallazgo central" (deuda × riesgo de cola) al frente del resumen, la introducción (quinta contribución), la síntesis, las conclusiones, el paper y las láminas |
| M2 | Hecho | Subsección "Deuda, crecimiento e incumplimiento soberano" (Eaton–Gersovitz, Arellano, Aguiar–Gopinath, Eichengreen–Hausmann, Rey) e hipótesis H4 en el marco |
| M3 | Hecho (preregistrado) | El riesgo de cola a cuatro trimestres es **firme** (0,047; Holm 0,018; 13 de 13); D4 × deuda = 0,033, significativo también con DK; en cambios aparece con el wild (0,006), no con DK |
| M4 | Hecho (preregistrado) | El pecado original no se confirma (−0,004; 8 economías); si algo, pesa más la deuda en moneda local |
| M5 | Hecho (secundaria) | El componente global explica el 70 % de la varianza; sobre el idiosincrásico, la fragilidad sigue siendo solo DK |
| M6 | Hecho (preregistrado) | El doom loop completo no se confirma (−0,053) |
| M7 | No factible | Bloomberg en el repo solo trae la calificación actual; hace falta la histórica de S&P o Moody's |
| M8 | Hecho (secundaria) | El régimen cambiario flexible no modera ninguna transmisión |
| M9 | Hecho, con ajuste | Se mantiene el término "riesgo económico" (regla del proyecto) y se precisa su alcance en el recuadro de vocabulario |

**Nota reestimada (misma rúbrica):**
- Contribución: 6,3 → 6,6, porque el hallazgo central queda reencuadrado y preregistrado dos veces.
- Marco: 6,0 → 6,4, porque ahora está anclado en la teoría del incumplimiento soberano.
- Datos: 6,0 → 6,2, por el GaR de mediano plazo y la deuda por moneda.
- Identificación: 5,8 → 5,9.
- Interpretación: 6,3 → 6,5.
- Inferencia (6,8), estructura (5,8) y reproducibilidad (6,9): sin cambio.

**Nota ponderada: 6,4** (0,99 + 0,64 + 0,93 + 1,18 + 1,02 + 0,975 + 0,29 + 0,345).
