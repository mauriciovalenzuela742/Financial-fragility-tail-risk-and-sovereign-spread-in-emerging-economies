---
title: "Evaluación de la versión reencuadrada, leída como la leería la comisión"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, quinta ronda"
---

*Evaluación de la versión del commit `7f47e6b`: tesis de 162 pp., de las cuales 83 son de cuerpo
(capítulos 1–7, pp. 1–83; resultados, pp. 34–73). Usa la misma rúbrica de 8 criterios y pesos de
`evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Las rondas anteriores leyeron la tesis cada una desde una disciplina: econométrica, macro, micro y
macroprudencial. Esta la lee como la leería la comisión el día de la defensa, de principio a fin, con dos
preguntas: si el documento cuenta una sola historia coherente y si cada afirmación respeta el grado de
evidencia que la propia tesis le asigna.*

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019,
con la plataforma de CEMLA). Todo son asociaciones, no causalidad. Este documento no modifica la tesis.*

---

# 1. Plan de evaluación

| # | Pregunta | Cómo se revisa |
|---|---|---|
| 1 | ¿El resumen, la introducción, los resultados, la discusión y las conclusiones cuentan la misma historia? | Comparar, frase por frase, las cuatro respuestas y las contribuciones en cada lugar |
| 2 | ¿Cada resultado lleva en todas partes la etiqueta de la escala de evidencia que le corresponde? | Buscar en todo el texto cada afirmación sobre deuda × riesgo de cola, fragilidad y riesgo de cola |
| 3 | ¿El orden del documento sigue el orden de firmeza que el propio documento declara? | Comparar el orden de las secciones del Capítulo 4 con el del resumen |
| 4 | ¿Las cifras coinciden con las canónicas? | Cotejar con `NUMEROS_CANONICOS_BBG.md` |
| 5 | ¿Qué cambió en los criterios desde la última nota (6,4 en `plan_nota7.md`)? | El reencuadre (`7f47e6b`) y la preparación de la defensa |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | Econométrica | Macro | Micro | Macroprud. |
|---|---|---|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,3 | 0,945 | 6,3 | 6,6 | 6,2 | 6,3 |
| 2 | Marco teórico y literatura | 10 % | 6,5 | 0,650 | 6,2 | 6,4 | 5,9 | 5,8 |
| 3 | Datos y construcción de las métricas | 15 % | 6,3 | 0,945 | 6,2 | 6,2 | 6,2 | 6,3 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,7 | 5,9 | 5,7 | 5,7 |
| 5 | Inferencia y robustez | 15 % | 6,9 | 1,035 | 6,8 | 6,8 | 6,8 | 6,9 |
| 6 | Interpretación | 15 % | 6,5 | 0,975 | 6,5 | 6,5 | 6,5 | 6,4 |
| 7 | Redacción, estructura y extensión | 5 % | 5,9 | 0,295 | 5,4 | 5,8 | 5,7 | 5,6 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,9 | 0,345 | 6,8 | 6,9 | 6,9 | 6,9 |
| | **Nota ponderada** | | | **6,35** | 6,2 | 6,4 | 6,2 | 6,2 |

Las columnas de comparación usan las notas reestimadas de cada ronda, anteriores a N1–N3 y al reencuadre.

**Nota: 6,4 (6,35).** Es la misma que estimó `plan_nota7.md` después de N3. El reencuadre no sube la nota
por sí solo. Lo que hace es volver defendible una tesis cuyo resultado más probado no se confirmó.

**Rango:**
- **6,1:** si la comisión lee primero el Capítulo 4 y encuentra que abre con el resultado más débil y que,
  en la síntesis, ese resultado sigue titulado como "la deuda pública amplifica" (sección 3).
- **6,5–6,6:** si se corrigen los residuos de la sección 3 y la defensa oral transmite el mensaje de
  `preparacion_defensa.md`.

**En una frase:** la tesis ya dice lo correcto en el resumen, la introducción y las conclusiones, pero el
Capítulo 4 y una implicancia todavía dicen lo anterior. Una comisión que lea con cuidado verá dos versiones
del mismo resultado.

---

# 3. Verificación de coherencia: lo que el reencuadre no alcanzó

Esta es la sección más útil antes de la defensa. Cada punto cita el lugar exacto. Los puntos 1 a 6 se
repiten en el paper (`envios/paper_empirico/cuerpo.tex:72`, `:1165`, `:2141`, `:2151`, `:2183`).

## 3.1 El resultado de deuda × riesgo de cola sigue afirmado como firme en cinco lugares

El resumen, la introducción, la discusión y las conclusiones lo llaman "una regularidad de la muestra que
nada confirma por ahora". Estos cinco pasajes no se actualizaron:

| # | Dónde | Qué dice | Qué debería decir |
|---|---|---|---|
| 1 | `capitulos/04_resultados.tex:5` (apertura del capítulo) | "Cuarta, la deuda pública amplifica la transmisión del riesgo de cola, en una prueba preregistrada" | La cuarta respuesta del resumen: regularidad de la muestra, sin confirmación externa |
| 2 | `capitulos/04_resultados.tex:31` (Tabla `tab:veredictos`, fila de moderadores) | Veredicto "Deuda: firme"; ninguna fila menciona la réplica, el instrumento ni el modelo | "Firme en la muestra a un año; sugerente a un trimestre; no replica, instrumento débil, el modelo predice el signo contrario", o una fila propia |
| 3 | `capitulos/04_resultados.tex:819` (Síntesis) | "La deuda amplifica la transmisión del riesgo de cola de mediano plazo con evidencia firme" | "Con más deuda, el riesgo de cola del año siguiente pesa más en el spread dentro de la muestra" |
| 4 | `capitulos/04_resultados.tex:829` (Síntesis, título de la Conclusión 4) | "La deuda pública amplifica la transmisión del riesgo de cola; ninguna otra condición la modifica" | El título de la discusión: "Con más deuda, el riesgo de cola pesa más en la muestra, pero nada lo confirma fuera de ella" |
| 5 | `capitulos/04_resultados.tex:837` (Síntesis) | "la deuda pública amplifica la transmisión del riesgo de cola de forma firme" | Lo mismo, con el matiz de la inferencia conjunta y de N1–N3 |

**Implicancia relacionada.** `capitulos/05_discusion.tex:29` ("El espacio fiscal importa para el riesgo
económico") dice: "La asociación es preregistrada y robusta a la exclusión de países, pero sigue siendo una
asociación". No menciona que la réplica, el instrumento y el modelo no la confirman. La implicancia
siguiente (`:31`, "regla continua") se apoya en ella, así que también debería condicionarla: "si la
regularidad se confirma con más economías".

**Por qué importa.** El verbo "amplifica" sugiere un mecanismo, y la tesis evita la causalidad en todo lo
demás. Además, la comisión puede preguntar por qué la síntesis contradice el resumen. Es la pregunta 2 de
`preparacion_defensa.md`, y conviene que el texto no la provoque.

## 3.2 El capítulo de resultados no sigue el orden que el resumen declara

El resumen y la introducción ordenan las respuestas por firmeza: simultaneidad, sin amplificación, riesgo
económico y, al final, deuda. El Capítulo 4, en cambio, abre con la deuda (Sección 4.1,
`04_resultados.tex:42`) "porque es la que más pruebas preregistradas recibió". Un lector que lea en orden
encuentra primero 14 páginas sobre el resultado que la tesis termina llamando la regularidad menos
confirmada, y la pregunta de la tesis (H3) recién en la Sección 4.4.

Al hacer N4 tenía sentido abrir con la deuda, cuando era "el hallazgo central". Después de N1–N3 dejó de
tenerlo. Hay dos opciones:
- **(a) Mover la Sección 4.1 después de "Simultaneidad sin amplificación".** El cambio es mecánico y se
  resuelve con referencias cruzadas.
- **(b) Mantener el orden y reescribir el párrafo de apertura** (`:5`) para decir que se empieza por la
  deuda por ser la pregunta más probada, no la más firme, y anunciar desde la primera frase cuál es la
  respuesta.

Se recomienda (a): es lo que la comisión espera de una tesis cuya pregunta es la amplificación.

## 3.3 Contradicciones de etiqueta y de cifra

| # | Dónde | Problema |
|---|---|---|
| 6 | `04_resultados.tex:847` frente a `:27` | El objetivo específico 3 dice que el riesgo de cola es "evidencia sugerente y solo en niveles". La Tabla de veredictos dice "Firme como asociación de nivel con factores comunes heterogéneos". Hay que unificar: firme con CCE y sugerente con la especificación principal |
| 7 | `04_resultados.tex:21` | En la Tabla de veredictos, el *wild* p de la fragilidad es 0,32. La cifra canónica es 0,33 (`NUMEROS_CANONICOS_BBG.md:1122`), la misma que usan `:846` y el resto del texto |
| 8 | `04_resultados.tex:45` | "Ambos parten de la regresión principal": no queda un sujeto plural en el párrafo (es un residuo de cuando la sección tenía dos preregistros) |
| 9 | Contribuciones | El resumen enumera cinco (i–v). La introducción enumera seis e incluye la réplica de Ossandón y Busch. Las conclusiones dicen "séxtuple", pero su sexta es "la demostración de qué se puede afirmar con trece países" y no incluyen a Ossandón y Busch. Las tres listas deberían ser la misma |

## 3.4 Extensión y forma

- **El resumen tiene 658 palabras** y repite "Los coeficientes son asociaciones, no efectos causales" al
  principio y al final del segundo párrafo. Un resumen de magíster rara vez pasa de 300 a 400 palabras. Se
  puede reducir a la pregunta, los datos, las cuatro respuestas en una línea cada una y las contribuciones.
- **La metodología describe análisis que ya están en anexos.** Las subsecciones de crisis, heterogeneidad
  y resiliencia (`03_metodologia.tex:217`, `:229` y `:246`) ocupan espacio en el cuerpo para resultados que
  se movieron al Anexo E. Bastaría una frase con remisión a cada una.

---

# 4. Evaluación por criterio

## 4.1 Pregunta, relevancia y contribución — 6,3

- **A favor:**
  - La pregunta original (H3) tiene una respuesta acotada y honesta: no hay amplificación grande, se
    descarta más de un 35 % de la suma y los riesgos coinciden.
  - El reencuadre convierte la cadena de pruebas fallidas en una contribución metodológica explícita, la
    quinta (`01_introduccion.tex:180`).
  - La sexta, que la predicción de los modelos de incumplimiento sobre deuda y riesgo de cola es en puntos
    básicos y no en logaritmos, es un resultado nuevo y útil para quien estime estas regresiones.
- **En contra:**
  - Lo más firme son un hecho sobre los regresores (la simultaneidad) y un resultado nulo bien acotado (la
    equivalencia). Ninguno de los dos es una relación nueva con el spread.
  - La regularidad de deuda × riesgo de cola, que era lo que podía subir este criterio, quedó sin
    confirmar.
- **Sin cambio respecto de la última ronda.** El reencuadre no agrega contribución, pero evita que la
  comisión descuente una contribución que el texto prometía y no sostenía.

## 4.2 Marco teórico y literatura — 6,5

- **A favor:**
  - El modelo de límite fiscal (`02_marco_teorico.tex:37`) le da a la tesis un modelo propio, con una
    predicción derivada y contrastada. Reemplaza con ventaja al Cournot eliminado.
  - Que el modelo prediga el signo contrario en logaritmos está bien explicado con la intuición de la cola
    normal.
- **En contra:**
  - La literatura macroprudencial y de alerta temprana sigue corta para una tesis que tiene un preregistro
    de umbrales.
  - Las tres candidatas para explicar la interacción en logaritmos (recuperación que cae con la deuda,
    aversión al riesgo, colas gruesas) se enumeran, pero no se citan modelos que las contengan (por
    ejemplo, Lizarazo, 2013, para la aversión al riesgo; Yue, 2010, para la recuperación endógena).
    Agregar dos o tres referencias es barato.

## 4.3 Datos y construcción de las métricas — 6,3

- Sin cambios: construcción homogénea, comparación con MES y ΔCoVaR, réplica con la DD de Merton.
- Siguen pendientes el piso de JLoss (23,7 % de las observaciones), los controles anuales interpolados y la
  falta de calificación soberana histórica (`05_discusion.tex:42`, `:51`).

## 4.4 Estrategia empírica e identificación — 5,8

- **A favor:** N1 fue un intento serio de identificación, con un umbral de debilidad fijado de antemano
  y declarado como no alcanzado. La simulación de retroalimentación cuantifica el sesgo en vez de solo
  mencionarlo.
- **En contra:** Ningún resultado sobre el spread está identificado. Con trece economías y sin variación
  exógena, este criterio no puede pasar de 6,0. Es el techo estructural de la tesis, y la tesis lo declara
  bien.

## 4.5 Inferencia y robustez — 6,9

- La inferencia conjunta sobre 14 hipótesis, la permutación de la deuda, la potencia simulada y la escala
  de evidencia están al nivel de un buen artículo aplicado.
- Baja de 7,0 a 6,9 por los puntos 1 a 7 de la sección 3: la etiqueta de evidencia, que es la herramienta
  central de la tesis, no se aplica igual en todo el texto.

## 4.6 Interpretación — 6,5

- **A favor:**
  - El párrafo "Cómo leer estos resultados" (`05_discusion.tex:19`) es exactamente lo que una comisión
    quiere oír.
  - Las implicancias distinguen bien lo que se puede y lo que no se puede recomendar.
  - Las limitaciones son completas.
- **En contra:** Los residuos de la sección 3.1 dan dos lecturas del mismo resultado en el mismo capítulo.
  Con la sección 3 corregida, este criterio sube a 6,8.

## 4.7 Redacción, estructura y extensión — 5,9

- **A favor:**
  - El cuerpo bajó a 83 páginas, con extensiones y moderadores en los anexos E y F.
  - La Tabla de veredictos al inicio del Capítulo 4 orienta bien la lectura.
- **En contra:**
  - El capítulo de resultados tiene 40 páginas y no sigue el orden que el resumen declara (3.2).
  - El resumen duplica la extensión habitual (3.4).
  - Párrafos de más de 300 palabras en la Síntesis y en la Discusión.
- **Si se hacen 3.2 y 3.4,** el criterio sube a ~6,4.

## 4.8 Reproducibilidad y transparencia — 6,9

- **A favor:** un comando, 104 cifras congeladas, integración continua, seis preregistros fechados y una
  declaración de disponibilidad de datos.
- **En contra:**
  - Falta activar Zenodo para el DOI.
  - La corrida completa de `reproducir.py` no termina en una máquina con poca memoria (p32 está marcado
    como lento). Conviene decirlo en la defensa si preguntan, junto con el tiempo y la memoria que exige.

---

# 5. Qué subiría la nota, en orden de costo

| # | Acción | Costo | Efecto en la nota |
|---|---|---|---|
| 1 | Corregir los residuos de la sección 3.1 y 3.3 (puntos 1–9) en la tesis, el paper y las láminas | ½ día | Interpretación 6,5 → 6,8; inferencia 6,9 → 7,0; contribución +0,1 (+0,07 ponderado) |
| 2 | Mover la Sección 4.1 después de la simultaneidad (3.2) | ½ día | Estructura +0,3; interpretación +0,1 |
| 3 | Resumen de 350–400 palabras (3.4) | 2 horas | Estructura +0,2 |
| 4 | Dos o tres referencias para las extensiones del modelo (4.2) | 2 horas | Marco +0,1 |
| 5 | Activar Zenodo y publicar una *release* | 30 min (el autor) | Reproducibilidad 7,0 |

**Con las acciones 1 a 5:**

| Criterio | Hoy | Con las acciones 1–5 |
|---|---|---|
| Contribución | 6,3 | 6,4 |
| Marco | 6,5 | 6,6 |
| Datos | 6,3 | 6,3 |
| Identificación | 5,8 | 5,8 |
| Inferencia | 6,9 | 7,0 |
| Interpretación | 6,5 | 6,9 |
| Estructura | 5,9 | 6,4 |
| Reproducibilidad | 6,9 | 7,0 |
| **Ponderada** | **6,35** | **6,48** |

El techo sigue en la identificación (20 %) y en una contribución sin un resultado confirmado sobre el
spread. Ninguna redacción mueve eso. Lo que sí está al alcance es que la comisión no encuentre nada que
contradiga el mensaje de la defensa.

**Sobre la defensa oral.** La nota final de la comisión incluye la defensa, y ahí `preparacion_defensa.md`
pesa más que cualquiera de estas acciones. Una exposición que transmita el mensaje en una frase y responda
la V25 ("si casi nada se confirma, ¿cuál es su contribución?") sin ponerse a la defensiva puede compensar
varias décimas del documento.

---

# 6. Registro de aplicación (23 de octubre de 2026)

| # | Estado | Qué se hizo |
|---|---|---|
| 3.1 (puntos 1–5) e implicancia | Hecho | La deuda × riesgo de cola dice "regularidad de la muestra, sin confirmación externa" en la apertura del capítulo, la Tabla de veredictos (fila propia, con réplica, instrumento y modelo), la Síntesis y la discusión; la regla continua queda condicionada a que la regularidad se confirme. También en el paper y las láminas |
| 3.2 | Hecho | La sección de la deuda pasa a ser la 4.4, después de la simultaneidad; el capítulo abre con la réplica de Chari et al. |
| 3.3 (puntos 6–9) | Hecho | Riesgo de cola unificado (sugerente en la principal, firme con CCE); *wild* p de 0,33 en la Tabla de veredictos y nota sobre el remuestreo en la tabla compacta; "Ambos parten" corregido; las tres listas de contribuciones son las mismas seis |
| 3.4 | En parte | Resumen de 658 a ~500 palabras. La metodología sigue describiendo crisis, heterogeneidad y resiliencia, porque los anexos citan sus ecuaciones |
| Efectos fijos de tiempo | Hecho | En la tabla de crisis, las columnas con solo efectos fijos de país omitían el indicador de crisis por sí solo, que solo los efectos de tiempo absorben; se corrigió el código y se regeneraron las tablas (NUMEROS §35). El texto atribuía la caída del coeficiente de la fragilidad con efectos bidireccionales solo a la parte transversal; ahora reporta las tres estructuras |
