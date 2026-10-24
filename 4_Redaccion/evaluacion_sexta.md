---
title: "Sexta evaluación: la tesis después de las correcciones de la comisión y de las ocho ramas quant"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lectura integral"
---

*Evaluación de la versión del commit `e2dc9ce` (empujado a `origin/master`). La tesis tiene 167 pp.:
cuerpo en las pp. 1–90 (resultados, pp. 34–74) y anexos desde la p. 91 (Anexo F, extensiones, desde la
p. 137). Usa la misma rúbrica de 8 criterios y pesos de `evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Las rondas anteriores fueron la econométrica, la macro, la micro, la macroprudencial, la de la comisión y
la quant. Esta vuelve a la lectura integral de la comisión, con tres preguntas:*
1. *¿se aplicaron bien las correcciones de la quinta ronda?*
2. *¿cómo cambian la tesis los preregistros 7 y 8 (Q1–Q6)?*
3. *¿queda algo que la comisión pueda encontrar contradictorio?*

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA). Todo son asociaciones. Este documento no modifica la tesis.*

---

# 1. Qué cambió desde la quinta ronda (6,35)

| Cambio | Commit | Efecto |
|---|---|---|
| La deuda × riesgo de cola dice "regularidad de la muestra" en la apertura del capítulo, la Tabla de veredictos, la síntesis y la discusión | `60797c0` | Desaparece la doble lectura del resultado |
| La sección de la deuda pasa a ser la 4.4, después de la simultaneidad | `60797c0` | El capítulo sigue el orden de firmeza que declara el resumen |
| Corrección del indicador de crisis en las columnas con solo efectos fijos de país | `60797c0` | Error de código corregido; la lectura no cambia |
| Contribuciones unificadas (seis en las tres listas); resumen de 658 a 505 palabras | `60797c0` | Coherencia |
| Versión corta de la predefensa | `cbbc1b1`, `9868ab7` | Mejor comunicación |
| Preregistro 7 (Q1, Q3) y preregistro 8 (Q2, Q4, Q5, Q6), integrados en el Anexo F, la síntesis y la discusión | `d968986`–`e2dc9ce` | Ninguna hipótesis pasa; Q3 extiende "simultaneidad sin amplificación" a la cola de los cambios |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | Comisión (5.ª) | Quant (6.ª) |
|---|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,4 | 0,960 | 6,3 | 5,9 |
| 2 | Marco teórico y literatura | 10 % | 6,5 | 0,650 | 6,5 | 6,0 |
| 3 | Datos y construcción de las métricas | 15 % | 6,4 | 0,960 | 6,3 | 6,4 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,8 | 5,6 |
| 5 | Inferencia y robustez | 15 % | 6,9 | 1,035 | 6,9 | 6,9 |
| 6 | Interpretación | 15 % | 6,7 | 1,005 | 6,5 | 6,3 |
| 7 | Redacción, estructura y extensión | 5 % | 6,2 | 0,310 | 5,9 | 6,2 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,8 | 0,340 | 6,9 | 7,0 |
| | **Nota ponderada** | | | **6,42** | 6,35 | 6,3 |

**Nota: 6,4 (6,42).** Sube algo respecto de la quinta ronda, porque las correcciones eliminaron las
contradicciones y el capítulo sigue ahora el orden que el resumen declara. No sube más por dos razones:
- los preregistros 7 y 8 no agregaron ningún resultado positivo;
- al agregarlos quedaron tres cabos sueltos nuevos (sección 3) que bajan la reproducibilidad y la
  inferencia.

**Rango:**
- **6,2:** si la comisión nota que la introducción promete una inferencia conjunta "sobre todos" los
  preregistros y que los scripts nuevos no están en el comando único.
- **6,5:** con las acciones de la sección 5, que son de bajo costo.

**En una frase:** la tesis está coherente de punta a punta. Lo que le falta ya no es corregir
contradicciones, sino cerrar la contabilidad de lo que agregó en los últimos dos días.

---

# 3. Verificación: lo que quedó suelto al agregar los preregistros 7 y 8

## 3.1 La inferencia conjunta ya no cubre "todos" los preregistros

`capitulos/01_introduccion.tex:180-182` dice que la tesis "evalúa con ocho preregistros [...] las
condiciones que podrían modificar la transmisión, y reporta cada resultado salga como salga, con una
inferencia conjunta sobre todos ellos". Hay dos problemas.

**El alcance de la corrección.** La corrección conjunta (`p56`, Sección `sec:inferencia-conjunta`) cubre las
14 hipótesis de los **cuatro primeros** preregistros. Los demás tienen correcciones propias o ninguna:

| Preregistro | Hipótesis primarias | Corrección |
|---|---|---|
| 5 (N1, N2) | 2 | Criterios propios, sin Holm conjunto |
| 6 (el modelo) | 1 | Ninguna |
| 7 | 3 | Holm propio |
| 8 | 3 | Holm propio |

Con 23 hipótesis primarias en ocho preregistros, la pregunta obvia de la comisión es si algo sobrevive a
una corrección sobre todas. Hay que calcularlo, no suponerlo:
- ninguna de las 14 primeras quedaba bajo 0,05 con Holm;
- el instrumento (0,46), el modelo en pb (0,09) y las seis quant tienen p altos;
- pero el coeficiente de la réplica externa tiene p = 0,002, aunque la réplica falló por la diferencia de
  magnitud con la original. Con 23 pruebas, 0,002 × 23 = 0,046 quedaría en el límite.

La tesis no lo calcula ni lo dice.

**El objeto de los preregistros 7 y 8.** No evalúan "condiciones que podrían modificar la transmisión", sino
preguntas de pronóstico y de riesgo de portafolio. La frase debería distinguir los dos tipos.

## 3.2 Los scripts nuevos no están en el comando único ni en las cifras canónicas

- `reproducir.py` llega hasta `p59`. `p60` a `p65` no están en `PASOS`.
- `canonicos_esperados.json` congela 104 cifras, ninguna de NUMEROS §36–§37.
- `REPRODUCIBILIDAD.md` no los menciona.

Hasta ahora, la tesis podía afirmar que **todas** sus cifras se regeneran con un comando y se verifican
automáticamente. Desde el preregistro 7 eso ya no es cierto: el Anexo F cita cifras que el comando único
no regenera.

## 3.3 Las conclusiones no recogen los preregistros 7 y 8

`capitulos/06_conclusiones.tex` resume los preregistros 3 y 4, pero no el 7 ni el 8. Q3 es relevante para la
segunda conclusión: la coincidencia de los dos riesgos tampoco ensancha la distribución de los cambios del
spread, y la fragilidad alta por sí sola sí lo hace. Una frase en la segunda conclusión bastaría. Lo mismo
vale para `preparacion_defensa.md`: ni la lista de cifras que memorizar ni las preguntas difíciles incluyen
Q1–Q6, y la comisión podría preguntar "¿y sirve para algo práctico?".

## 3.4 Detalles menores

| # | Dónde | Qué |
|---|---|---|
| 1 | `04_resultados.tex:820` | "Tres de las extensiones refuerzan conclusiones del capítulo" está bien, pero el párrafo no dice nada de la del preregistro 8 (que no refuerza ni cambia nada). Agregar media frase |
| 2 | Resumen (`main.tex`) | 505 palabras; sigue sobre las 350–400 habituales |
| 3 | Anexo F | Diez extensiones en 30 páginas (pp. 137–167). Las dos quant podrían ir a un anexo propio ("Preguntas de portafolio"), para separar lo que extiende la tesis de lo que la aplica |
| 4 | Paper | Una tabla de Argentina generada automáticamente se pasa 13 pt del alto de la página |
| 5 | Marco teórico | No se agregaron las referencias para las extensiones del modelo que sugirió la quinta ronda (Lizarazo, 2013; Yue, 2010) |

---

# 4. Evaluación por criterio

## 4.1 Contribución — 6,4

- **A favor:**
  - Con las correcciones, la contribución se lee igual en todas partes: simultaneidad firme, sin
    amplificación grande y la regularidad de la deuda sin confirmar.
  - Q3 suma un hecho nuevo y acotado: la coincidencia tampoco ensancha la cola de los cambios del spread, y
    la fragilidad alta sí lo hace.
- **En contra:** ninguna de las seis hipótesis quant pasó. La contribución empírica nueva sigue siendo un
  resultado nulo bien acotado y un hecho sobre los regresores.

## 4.2 Marco — 6,5

Sin cambios. El modelo de límite fiscal sigue siendo el aporte principal. Q5 confirma que tampoco tiene
respaldo en puntos básicos con datos mensuales, y el marco no agrega las extensiones que podrían
explicarlo.

## 4.3 Datos — 6,4

Suma una DD mensual con el rezago de publicación del balance (`fragilidad_mensual_lag_bbg.csv`), que cierra
la principal duda de anticipación. El nowcast del GaR (Q6) no validó (correlación 0,42), y eso se reporta
como tal. Siguen pendientes el piso de JLoss y la falta de calificación soberana histórica.

## 4.4 Identificación — 5,8

Sin cambios. Es el techo estructural de la tesis con trece economías y sin variación exógena.

## 4.5 Inferencia — 6,9

- **A favor:** cada preregistro nuevo trae su corrección de Holm, su *bootstrap* y la prueba de Sharpe de
  Ledoit–Wolf.
- **En contra:** falta la corrección sobre las 23 hipótesis primarias (3.1). Con ella, este criterio
  llegaría a 7,0.

## 4.6 Interpretación — 6,7

- **A favor:**
  - Las contradicciones de la quinta ronda desaparecieron.
  - La lectura de Q1–Q6 es prudente y útil: "los fundamentos describen niveles, no pronostican cambios".
- **En contra:** la frase de la introducción (3.1) y la ausencia de Q3 en las conclusiones (3.3).

## 4.7 Estructura — 6,2

- **A favor:** el capítulo de resultados sigue ahora el orden de firmeza, y la versión corta de las láminas
  comunica bien.
- **En contra:** la tesis creció de 162 a 167 pp., y el Anexo F reúne diez extensiones de naturaleza muy
  distinta.

## 4.8 Reproducibilidad — 6,8

Baja una décima por 3.2. El comando único y la verificación automática dejaron de cubrir todas las cifras de
la tesis. Sigue pendiente activar Zenodo.

---

# 5. Acciones, en orden de costo

| # | Acción | Costo | Efecto |
|---|---|---|---|
| 1 | Agregar `p60`–`p65` a `reproducir.py`; congelar las cifras primarias de NUMEROS §36–§37 en `canonicos_esperados.json`; un paso en `REPRODUCIBILIDAD.md` | 1 hora | Reproducibilidad 6,8 → 7,0 |
| 2 | Corrección de Holm, BH y BY sobre las 23 hipótesis primarias de los ocho preregistros (extender `p56`); una línea en la Sección `sec:inferencia-conjunta` y en la introducción | 2 horas | Inferencia 6,9 → 7,0; interpretación +0,1 |
| 3 | Corregir la frase de la introducción (3.1); una frase con Q3 en la segunda conclusión; Q1–Q6 en `preparacion_defensa.md` (cifras y una pregunta difícil) | 1 hora | Interpretación +0,1 |
| 4 | Pasar Q1–Q6 a un Anexo G propio ("Preguntas de portafolio") y el resumen a ~400 palabras | 2 horas | Estructura +0,2 |
| 5 | Referencias para las extensiones del modelo (Lizarazo, 2013; Yue, 2010) | 30 min | Marco +0,1 |

| Criterio | Hoy | Con las acciones 1–5 |
|---|---|---|
| Contribución | 6,4 | 6,4 |
| Marco | 6,5 | 6,6 |
| Datos | 6,4 | 6,4 |
| Identificación | 5,8 | 5,8 |
| Inferencia | 6,9 | 7,0 |
| Interpretación | 6,7 | 6,9 |
| Estructura | 6,2 | 6,4 |
| Reproducibilidad | 6,8 | 7,0 |
| **Ponderada** | **6,42** | **6,50** |

**El techo.** Está en la identificación (20 %) y en una contribución sin un resultado positivo nuevo sobre el
spread. Las ocho ramas quant eran la última vía, dentro del repositorio, para mover la contribución, y
ninguna pasó. Lo que queda por ganar es contabilidad y presentación, no evidencia.

**Para la defensa.** El mejor uso del tiempo ya no es otra prueba, sino:
- ensayar el mensaje de `preparacion_defensa.md`;
- tener una respuesta corta a "¿sirve para algo práctico?": "probé seis preguntas de portafolio con
  preregistro y ninguna pasó; la fragilidad sirve para medir el riesgo, no para pronosticar el spread".

---

# 6. Registro de aplicación (24 de octubre de 2026)

| # | Estado | Qué se hizo |
|---|---|---|
| 1 | Hecho | `p60`–`p66` en `reproducir.py`; 36 cifras nuevas congeladas (140 en total, 140 de 140 coinciden); Paso 2h en `REPRODUCIBILIDAD.md` |
| 2 | Hecho | `p66_inferencia_global.py`: Holm, BH y BY sobre las 23 hipótesis primarias (NUMEROS §38). Bajo 0,05 con Holm, solo el signo de la réplica externa (0,046), sin cambiar su veredicto; con BY, ninguna. Párrafo nuevo en la Sección `sec:inferencia-potencia` de la tesis y del paper |
| 3 | Hecho | Introducción corregida (dos tipos de preregistro, corrección sobre las 23); Q3 en la segunda conclusión; Q1–Q6 en `preparacion_defensa.md` (pregunta 11 y dos cifras) |
| 4 | Hecho | Q1–Q6 pasan al Anexo G ("Preguntas de portafolio"); el de IA pasa a ser el H. Resumen de 505 a ~410 palabras |
| 5 | Hecho | Lizarazo (2013) y Yue (2010) citadas en las extensiones del modelo, en la tesis y el paper |

Pendiente: la tabla de Argentina del paper (generada automáticamente) sigue 13 pt sobre el alto de la página,
y Zenodo sigue sin activarse.

**Nota reestimada: 6,5** (6,4 contribución; 6,6 marco; 6,4 datos; 5,8 identificación; 7,0 inferencia; 6,9
interpretación; 6,4 estructura; 7,0 reproducibilidad).
