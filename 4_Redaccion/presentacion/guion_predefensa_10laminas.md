---
title: "Predefensa en 10 láminas"
subtitle: "Guion, respuesta a las observaciones del profesor guía y pruebas a revisar — 13 de octubre de 2026"
---

*Versión corta que pidió el profesor Martínez en la reunión del 9 de octubre: máximo 9–10 láminas
con pregunta, hipótesis, metodología, resultado e implicancia. Archivo: `predefensa.tex` (10 láminas
+ 20 de anexo y las referencias; 33 páginas). La presentación larga (`defensa.tex`, 61 páginas: 41 de
exposición y 20 de respaldo) tiene el mismo relato, con más detalle. Tiempo: unos 15 minutos de
exposición.*

**Vocabulario que debo cuidar** (lo corrigió el profesor):

- **Amplificación** (o simultaneidad), nunca "multiplicidad".
- Efectos **aditivos** cuando cada riesgo sube el spread por separado y la suma no se potencia.
- **Riesgo financiero** = fragilidad bancaria (JLoss). **Riesgo económico** = cola del crecimiento (GaR).
- Son **asociaciones**; no digo "reduce", "protege", "anticipa" ni "efecto de".
- Las métricas no son mías: JLoss es de Chari et al. (2024) y el GaR de Adrian, Boyarchenko y
  Giannone (2019). Lo mío es **construir las series de las dos métricas** y cruzarlas.

**La escala de evidencia, la misma en todo:** *firme* (resiste el wild bootstrap o la permutación y
no depende de un país); *sugerente* (solo Driscoll–Kraay, o depende de un país); *exploratorio* (no
estaba preespecificado y no pasa la corrección por comparaciones múltiples); *no hay evidencia*.

# 0. Nota honesta para la reunión: el titular cambió dos veces

Lo digo yo antes de que lo pregunte.

| Fecha | Titular | Por qué se cayó |
|---|---|---|
| 9 de octubre | "El riesgo económico sobrevive a las variables financieras" | En la primera revisión no apareció en diferencias ni con el CDS, y su coeficiente depende de Polonia. |
| 12 de octubre | "El cambio de la fragilidad bancaria es lo que mueve el spread" | Era en parte un artefacto de fechas: el EMBI del panel es el promedio del trimestre y JLoss usa el cierre. Con el spread de cierre a cierre el coeficiente es 0,025 (wild p = 0,21). |
| Hoy | Cuatro conclusiones propias sobre el cruce de los dos riesgos; la fragilidad queda como réplica de Chari et al. | — |

**Qué digo:** "Profesor, el titular cambió dos veces en una semana y prefiero explicarlo yo. Cada
cambio vino de una prueba que el resultado anterior no pasó; no cambié la pregunta ni los datos. Y
hay una decisión de fondo: que la fragilidad bancaria importa para el spread ya lo establecieron
ustedes en Chari et al. (2024), así que no puede ser la conclusión de mi tesis. Lo propio es el
cruce con el riesgo económico, y eso es lo que ahora encabeza."

**Qué aprendí del proceso:** las conclusiones de hoy son más modestas, pero cada una pasó por la
prueba que botó a las anteriores (fechas del spread, exclusión de países, wild bootstrap, corrección
por comparaciones múltiples, placebos).

# 1. Guion lámina por lámina

### 1. Portada (15 s)
"Presento la tesis *Fragilidad bancaria sistémica y riesgo de cola del crecimiento: determinantes
del spread soberano en economías emergentes*."

### 2. La pregunta (1 min 30 s)
**Qué digo:** "El spread soberano es la prima que exige el mercado por el riesgo de que un gobierno
no pague. Estudio dos riesgos domésticos de cola: uno **financiero**, la fragilidad del sistema
bancario, que mido con JLoss; y uno **económico**, la cola adversa del crecimiento, que mido con el
Growth-at-Risk. Que la fragilidad bancaria se asocia con el spread ya lo documentan Chari y
coautores. La brecha: no se han cruzado simultáneamente los dos riesgos de cola domésticos. Mi
pregunta es qué agrega el riesgo económico a lo que ya explica la fragilidad, y qué pasa cuando los
dos se dan a la vez."

**Si me pregunta** por qué digo "económico": porque JLoss también es un riesgo de cola; lo que
distingue al GaR es que es de la actividad económica, no del sistema financiero.

**Si me pregunta** por qué la fragilidad no es mi conclusión: porque ya está en Chari et al. (2024).
La replico con datos construidos de forma independiente y delimito su alcance, pero el hallazgo no
es mío.

### 3. El mecanismo (1 min 30 s)
**Cómo leer:** el triángulo: primero la línea de arriba, después las dos flechas azules.

**Qué digo:** "El mecanismo es un triángulo, no una secuencia. Los dos riesgos se relacionan entre
sí: un sistema bancario frágil da menos crédito y eso deprime el crecimiento ---el acelerador
financiero de Bernanke, Gertler y Gilchrist---, y un crecimiento débil deteriora a los bancos. Y
ambos se trasladan al spread: la fragilidad, como rescate esperado; la cola del crecimiento, por la
capacidad fiscal. ¿Qué podría contener esa transmisión? El respaldo oficial ---el banco central con
sus reservas y las líneas externas--- y quién tiene la deuda. Las tres cosas las medí y las
contrasté como moderadores: reservas, acceso a respaldo país por país y participación extranjera.
Como todo ocurre a la vez, hablo de asociaciones, no de causalidad."

**Cambio respecto del 9 de octubre:** antes decía que el respaldo "no entra como regresor, lo
absorben los efectos fijos". Ya no es así: ahora se mide y se contrasta.

### 4. Hipótesis de trabajo (1 min)
**Qué digo:** "Tres hipótesis. H1, canal bancario: la fragilidad bancaria sistémica eleva el spread
soberano. H2, canal de crecimiento: un mayor riesgo de cola del crecimiento eleva el spread
soberano. H3, amplificación: la coincidencia de ambos riesgos eleva el spread más que la suma de las
dos asociaciones. Además se contrasta si tres condiciones ---resiliencia, respaldo externo y quién
tiene la deuda--- modifican la transmisión."

### 5. Las dos variables en el tiempo (1 min 30 s)
**Cómo leer:** la línea es la mediana entre países; la banda, el rango entre el 25 % y el 75 %; lo
sombreado, las crisis.

**Qué digo:** "Antes de las regresiones, las series. A la izquierda JLoss, la pérdida conjunta
esperada del sistema bancario, calculada con 113 bancos de Bloomberg. A la derecha el riesgo de
cola, que es el cuantil 5 % del crecimiento con el signo invertido. Las dos tienen sentido
económico: son bajas y estables en tiempos normales y saltan en la crisis financiera global y en la
pandemia. Ya aquí se ve el primer resultado: tienden a moverse juntas."

**Si me pregunta** por un país: en el anexo están la construcción de cada una y, en la tesis, las
series por país.

**Si me pregunta** por el piso de JLoss: la métrica se amontona en 2,16; el 24 % de las observaciones
está a menos de 2 % de ese piso (Malasia 60 %, Perú 58 %, Chile 49 %) y ahí no informa. Lámina 16.

### 6. Metodología (1 min 30 s)
**Qué digo:** "Regreso el logaritmo del EMBI sobre el logaritmo de JLoss y el riesgo de cola, ambos
rezagados un trimestre, y su producto, con efectos fijos de país y de tiempo. Beta tres es la
interacción: positiva es amplificación; cero, efectos aditivos. Dos cosas de método que importan
para leer los resultados. Primera: la inferencia está calibrada con una simulación. Con 13 países,
Driscoll–Kraay rechaza de más en niveles, así que mi criterio es el wild cluster bootstrap por país.
Segunda: la prueba de la participación extranjera en la deuda la preespecifiqué: fijé las
hipótesis, el moderador y la familia de contrastes antes de estimar, y corrijo por comparaciones
múltiples con Holm. Además uso permutación, cambios, proyecciones locales y pronóstico fuera de
muestra."

**Si me pregunta** por la simulación: 1.000 paneles simulados que conservan la dependencia entre
países. En niveles, cuando no hay efecto, Driscoll–Kraay rechaza el 28 % y el 21 % de las veces
(debería ser 5 %); el wild bootstrap, 6 % y 7 %. Su potencia es 35 % para la fragilidad y 67 % para
el riesgo de cola. Lámina 19.

**Si me pregunta** si el wild bootstrap basta: no. Calibra el error estándar, pero no protege del
sesgo de retroalimentación: en un panel simulado donde la fragilidad no tiene efecto directo y el
spread retroalimenta, el wild rechaza "cero" el 24 % de las veces. Por eso resistir el wild es
necesario, no suficiente, y lo que solo lo pasa en niveles lo llamo sugerente.

**Si me pregunta** qué significa preespecificada: que las hipótesis, el moderador (participación de
no bancos extranjeros en la deuda del gobierno, rezagada cuatro trimestres) y la consecuencia de
cada resultado quedaron escritos antes de correr la regresión. Límite que debo decir: consta en el
encabezado del script, no en un registro externo con fecha.

### 7. Resultado 1: los dos riesgos coinciden más de lo que explicaría el azar (2 min 30 s)
**Cómo leer:** arriba, "Observado" contra "Por azar". Abajo, las dos filas del rezago cruzado: la
primera es significativa y la segunda no.

**Qué digo:** "Primer resultado, y el más firme. Defino que un riesgo está alto cuando está en su
tercil superior dentro de cada país. Los dos están altos a la vez en 168 observaciones, el 22 %; si
fueran independientes serían 87: casi el doble. Neto del calendario común (frecuencias de cada año): 132 esperadas, 1,3 veces. Pasa en los 13 países. Una permutación por bloques
dentro de cada país da 86 en promedio, con p de 0,001, y lo mismo fuera de los trimestres de
crisis: 108 frente a 59. Y los episodios conjuntos duran más que por azar: 2,7 trimestres frente a
1,9. Segundo dato, que califico de sugerente: la fragilidad de un trimestre se asocia con más
riesgo de cola el trimestre siguiente, 0,405 con wild de 0,024, y al revés no: −0,006. Es coherente
con el acelerador financiero."

**Conclusión directa:** la simultaneidad es un hecho (firme); hay indicios de que la fragilidad
antecede al riesgo económico (sugerente).

**Lo que debo decir con honestidad:** la simultaneidad proviene de pocos episodios comunes: 129 de
las 168 observaciones son de 2020 en adelante y el 35,7 % cae en trimestres de crisis (que son el
14,2 % de la muestra). Y la precedencia descansa en un rezago trimestral, equivale a 0,1
desviaciones estándar y no la sometí a la exclusión de países ni a la prueba de fechas.

**Si me pregunta** si es solo la pandemia: no. En 2020–22 lo observado (29, 17 y 29) casi iguala a
lo esperado (27, 16 y 28); el exceso viene de 2015–19 y de 2023–26. Y fuera de los trimestres de
crisis la permutación sigue en p = 0,001.

**Si me pregunta** cuánto se correlacionan: descontados los efectos fijos, 0,26.

### 8. Resultado 2: cuando coinciden, no hay evidencia de que se amplifiquen (2 min 30 s)
**Cómo leer:** la tabla tiene cuatro pruebas distintas; en todas, la estimación es negativa y el p
es alto. El bloque azul dice cuánta amplificación podría estar escondida.

**Qué digo:** "Segundo resultado. Que coincidan no significa que se potencien. La interacción de la
regresión principal es −0,011, con wild de 0,89. Con indicadores de estrés: la fragilidad alta se
asocia con +0,09 de spread, la cola alta con +0,19, y las dos a la vez agregan −0,08, no
significativo; lo mismo uno a cuatro trimestres adelante. Y con una forma funcional intermedia
entre logaritmos y niveles, tampoco. Ahora, no rechazar no es demostrar. Por eso calculé las bandas:
con los dos riesgos una desviación estándar sobre su media, la suma de las dos asociaciones es un
16 % de spread, unos 28 puntos básicos. El intervalo más ancho admite un extra de 5 puntos, un 29 %
de la suma; en puntos básicos, 11 sobre 28. Entonces la frase exacta es: no hay evidencia de
amplificación, y los datos no permiten descartar un extra de hasta un 30 o 40 % de la suma."

**Conclusión directa:** no hay evidencia de amplificación; no se puede descartar un extra de hasta
un 30–40 % de la suma.

**Si me pregunta** por qué no digo que la amplificación está descartada: porque el intervalo no lo
permite. Con 13 países las bandas son anchas, y en puntos básicos la estimación puntual incluso es
positiva (+3 pb sobre 28). Es un no rechazo.

**Si me pregunta** por el signo negativo: es de Polonia. Sin ella la interacción es +0,008
(p = 0,19). No lo leo como atenuación.

**Si me pregunta** qué significa "aditivo" en logaritmos: aditivo en logaritmos es proporcional en
puntos básicos. Es álgebra de la forma funcional, no un hallazgo, y no lo llamo amplificación.

**Si me pregunta** si hay algo en contra: dos señales débiles, que reporto. Fuera del piso de JLoss
el riesgo de cola pesa +7,5 pb más (wild 0,036) con un umbral de 2 %, pero en logaritmos no (0,11)
y con un umbral de 5 % se debilita. Y en cambios a cuatro trimestres en puntos básicos la
interacción es +0,358 (wild 0,011), ausente en logaritmos.

### 9. Resultados 3 y 4: el riesgo económico agrega poco; ninguna condición cambia la transmisión (2 min 30 s)
**Cómo leer:** a la izquierda, arriba lo que el riesgo de cola agrega al modelo de Chari y abajo las
pruebas que no pasa. A la derecha, las tres condiciones, cada una con su veredicto.

**Qué digo:** "Tercer resultado, en dos partes. Primera: tomo el modelo al estilo de Chari
---fragilidad rezagada con sus controles--- y le agrego el riesgo de cola. El coeficiente es 0,037;
la prueba conjunta con la interacción da un wild de 0,041, y el R² dentro del país sube de 0,153 a
0,185 (0,194 con la interacción). Pero no pasa las pruebas propias de una variable lenta: en cambios a cuatro trimestres es
0,004; en proyecciones locales, ningún horizonte de nueve; fuera de muestra, agregarlo sube el
error de pronóstico un 3 %; y sin Polonia cae a 0,007. Es una asociación modesta, de 0,02 a 0,03
por punto, en niveles y en 10 de 13 países: sugerente. Segunda parte: ¿alguna condición cambia la
transmisión? La participación extranjera en la deuda, que era la prueba preespecificada: no. El
respaldo externo medido país por país ---swap de la Fed, línea flexible del FMI---: no. Y las
reservas: el coeficiente de la fragilidad es menor donde hay más reservas, pero es exploratorio."

**Conclusión directa:** el riesgo económico agrega información modesta y solo en niveles; ninguna
condición estudiada modifica la transmisión de forma demostrable.

**Si me pregunta** qué es nuevo respecto de Chari: el cruce. Ellos cruzan la fragilidad con factores
globales; yo, con el riesgo de cola doméstico. Lo nuevo es que coinciden, que hay indicios de que la
fragilidad antecede al riesgo de cola, que no hay evidencia de amplificación y que el riesgo
económico agrega poco.

**Si me pregunta** por qué el wild de 0,041 no es evidencia limpia: porque el wild no protege del
sesgo de retroalimentación. En la simulación sin efecto directo, el coeficiente del riesgo de cola
sale +0,022 en promedio, y el dato es 0,032.

**Si me pregunta** por el fuera de muestra: es evidencia débil en cualquier dirección; el diseño no
tiene efectos de tiempo y el GaR no se reestima recursivamente. Ningún modelo le gana al spread
rezagado, tampoco con la fragilidad.

**Si me pregunta** por qué falló la prueba de la participación extranjera: las tres hipótesis dan
+0,037, −0,001 y −0,006, con wild entre 0,41 y 0,92 y Holm de 1,00; la tercera tiene el signo
contrario al predicho. Es ausencia de evidencia con intervalos anchos, no evidencia de un cero: el
75 % de la variación del moderador es entre países y son 13. En puntos básicos la primera es
sugerente (+3,38; Driscoll–Kraay 0,002; wild 0,13). La consecuencia la había declarado antes: la
heterogeneidad del "núcleo de 11 economías" pasa a exploratoria. Lámina 26.

**Si me pregunta** por Polonia: tiene el 40 % de su deuda en manos de no residentes, la cuarta más
alta de las 13. La etiqueta de "deuda local profunda" la retiré: valía para India (5 %), no para
Polonia. El grupo "Polonia e India" es una agrupación ex post.

**Si me pregunta** por qué las reservas son exploratorias: el coeficiente es −0,247 (wild 0,08) y
resiste rezagar las reservas cuatro y ocho trimestres; en puntos básicos es más firme (−11,3; wild
0,04; sin Polonia −9,5, wild 0,08). Pero en logaritmos depende de Polonia (sin ella −0,084, wild
0,30); con Holm queda en 0,40 y 0,22; los placebos ---cuenta corriente y tipo de cambio real
rezagados--- "moderan" igual o más; y la interacción lineal implica una elasticidad negativa para
el 23 % de las observaciones, que no es creíble. Lámina 27. No sustenta recomendar reservas.

**Si me pregunta** quiénes tuvieron respaldo: swap de la Fed, Brasil y México (2008Q4–2009Q4 y
2020Q1–2021Q4); Línea de Crédito Flexible del FMI, México desde 2009Q2, Colombia 2009Q2–2025Q1,
Polonia 2009Q2–2017Q3, Chile desde 2020Q2 y Perú 2020Q2–2024Q2. Son 223 observaciones de seis
países. Interacción × acceso: −0,004 (wild 0,90); dentro de las crisis, +0,045 (wild 0,22).

**Si me pregunta** por la resiliencia como seguro: el índice se asocia con menor spread (−0,153) y
con un coeficiente del riesgo de cola menor fuera de crisis (−0,024) y no en crisis (−0,001), pero
solo con Driscoll–Kraay (cluster 0,38): sugerente. La analogía del seguro queda como lectura, no
como hallazgo.

### 10. Conclusiones e implicancias (1 min 30 s)
**Qué digo:** "Cuatro conclusiones. Uno: la simultaneidad es un hecho; los dos riesgos coinciden
casi el doble de lo esperado por azar, y hay indicios de que la fragilidad antecede al riesgo de
cola. Dos: cuando coinciden, no hay evidencia de que se amplifiquen, aunque no se puede descartar
un extra de hasta un 30 o 40 % de la suma. Tres: el riesgo económico agrega poco a lo que ya
explica la fragilidad, solo en niveles. Cuatro: ninguna condición estudiada ---resiliencia,
respaldo externo, quién tiene la deuda--- modifica la transmisión de forma demostrable. Y la
réplica: la asociación entre fragilidad y spread replica a Chari y coautores con sus controles,
pero no es una elasticidad común ni hay precedencia temporal. La implicancia es prudente: vigilar
los dos riesgos juntos se justifica porque tienden a agravarse a la vez; no hay base para una prima
adicional por la simultaneidad, ni para recomendar reservas, ni para diferenciar por quién tiene la
deuda."

**Si me pregunta** qué pasó con el resultado en diferencias del 12 de octubre: era en parte
agregación temporal. Con el spread de cierre a cierre, el coeficiente es 0,025 (wild 0,21) y nunca
es significativo al excluir un país o un año. Lo que sí hay es movimiento dentro del mismo
trimestre: 0,037 (wild 0,008), robusto en puntos básicos (13 de 13 países, 23 de 23 años) y menos
en logaritmos (6 de 13 y 13 de 23; sin Turquía 0,030, p = 0,15). La fragilidad y el spread se
mueven en el mismo trimestre; no hay evidencia de que la fragilidad anteceda al spread. Lámina 17.

**Si me pregunta** por qué "no es una elasticidad común": las pendientes por país van de −0,84 a
+0,97, se rechaza la homogeneidad y Turquía aporta el 70 % del coeficiente (sin ella 0,034,
p = 0,43). Y con los seis controles domésticos de la tesis el coeficiente es −0,008. Lámina 16.

\newpage

# 2. Cómo se atendió cada observación del profesor

| Observación (9 de octubre) | Qué se hizo |
|---|---|
| Máximo 9–10 láminas; el resto, anexo | `predefensa.tex`: 10 láminas + anexo |
| Riesgo financiero vs. riesgo económico | Lámina 2; tesis y paper, mecanismo y marco conceptual |
| La brecha: "no se han cruzado simultáneamente…" | Lámina 2; tesis, sección de alcances y contribución |
| Triángulo en vez de secuencia; acelerador financiero | Lámina 3; figura en tesis y paper; referencia BGG (1996) |
| El respaldo es el banco central; no estaba en las regresiones | Lámina 3; ahora se mide: reservas, acceso por país y participación extranjera (tesis, secciones de resiliencia y de crisis, respaldo externo y quién tiene la deuda) |
| Gráficos de GaR y JLoss antes de las regresiones | Lámina 5 (figura 2004–2026) |
| "Amplificación", no "multiplicidad"; efectos aditivos | Todo el guion; tesis, marco conceptual (fija el vocabulario) |
| Solapamiento / endogeneidad del FCI; dos etapas | Tesis, sección de solapamiento dentro de "Qué se puede afirmar" |
| Resiliencia (deuda, balance fiscal, reservas) | Tesis, sección de resiliencia de la política económica; lámina 9 y anexo (lámina 27) |
| Crisis vs. no crisis: ¿sigue funcionando el resguardo? | Tesis, sección de crisis; anexo (láminas 20–23) |
| La tabla del vector único "está enredada" | Pasa al anexo |
| Correlación, no causalidad | Lámina 3 ("Alcance") y lámina 10 |

# 3. Las cifras, de memoria

| Qué | Cifra |
|---|---|
| Muestra | 13 economías, 2004–2026, N = 765 |
| Simultaneidad | 168 observaciones (22,0 %) frente a 87; 1,9 veces; 13 de 13 países |
| Coincidencia neta del calendario común | 168 frente a 132 esperadas (1,3 veces) |
| Permutación | media 85,7; p = 0,001; fuera de crisis 108 frente a 59,3 |
| Episodios conjuntos | 62; 2,71 trimestres frente a 1,85 (p = 0,003) |
| Fragilidad(t−1) → riesgo de cola(t) | 0,405 (wild 0,024); al revés −0,006 |
| Salvedad | 129 de 168 desde 2020; 35,7 % en trimestres de crisis |
| Interacción β3 | −0,011 (Driscoll–Kraay 0,11; wild 0,89) |
| Estrés conjunto | +0,091, +0,186 y extra −0,077 (wild 0,23) |
| Bandas | suma +16,4 % (28 pb); extra máximo +5,3 puntos (29 %); en pb +11 sobre 28 (39 %) |
| Riesgo de cola sobre el modelo de Chari | 0,037 (wild 0,066); conjunta wild 0,041; R² 0,153 → 0,185 (0,194 con la interacción) |
| Pero | cambios 0,004; proyecciones locales 0 de 9; fuera de muestra +3 % de error; sin Polonia 0,007 |
| Participación extranjera | +0,037 / −0,001 / −0,006; Holm 1,00 |
| Respaldo externo por país | −0,004 (wild 0,90) |
| Reservas × fragilidad | −0,247 (wild 0,08); Holm 0,40; sin Polonia −0,084 |
| Réplica de Chari | 0,099; 0,107–0,164 con sus controles; CDS 0,206; sin Turquía 0,034 |
| Fechas | cierre a cierre 0,025 (wild 0,21); mismo trimestre 0,037 (wild 0,008) |
| Wild bootstrap en niveles (β1 / β2 / β3) | 0,33 / 0,20 / 0,89 |
| Simulación, tamaño en niveles | Driscoll–Kraay 28 % / 21 %; wild 6 % / 7 % |

# 4. Las estimaciones de la segunda ronda, en simple

**Simultaneidad.** Terciles definidos dentro de cada país. Observado 168; esperado 87. La
permutación desplaza circularmente el riesgo de cola dentro de cada país (999 réplicas), así
conserva la persistencia de cada serie.

**Bandas de aditividad.** Intervalo de 95 % de β3: Driscoll–Kraay [−0,025; 0,003]; cluster por país
[−0,050; 0,028]; wild invertido [−0,054; 0,015]. Mayor extra no descartable: +0,5, +5,3 y +2,9
puntos de spread (3 %, 29 % y 16 % de la suma).

**Información incremental.** Sobre fragilidad rezagada y los controles de Chari (N = 662): β2 =
0,037; R² parcial del riesgo de cola 0,037 (el de la fragilidad dado el riesgo de cola, 0,018). Sin
controles (N = 765): 0,030 (wild 0,17). Fuera de muestra: ventana expansiva, un trimestre
adelante, 540 pronósticos desde 2013Q2; raíz del error cuadrático medio 0,1601 → 0,1650.

**Fechas.** Muestra común N = 708. Promedio a promedio (versión del 12 de octubre): 0,039. Cierre a
cierre: 0,025 (wild 0,21). Primer mes menos cierre anterior: 0,000. Parte mecánica (cierre menos
promedio del mismo trimestre): 0,020, la mitad del coeficiente en logaritmos y el 80 % en puntos
básicos. Mismo trimestre: 0,037 (wild 0,008); en pb 2,64.

**Retroalimentación.** En un panel simulado donde la fragilidad no tiene efecto directo, la
regresión en niveles entrega +0,066 en promedio (dato: 0,099); para el riesgo de cola, +0,022
(dato: 0,032). Vale para los dos coeficientes de nivel, y también para los cambios (+0,019 frente a
0,037).

**Inferencia.**

| Niveles | Rechaza sin efecto (debería ser 5 %) | Potencia |
|---|---|---|
| Driscoll–Kraay | 28 % / 21 % | 70 % / 77 % |
| Cluster por país, t(12) | 9 % / 8 % | 44 % / 70 % |
| Wild bootstrap por país | 6 % / 7 % | 35 % / 67 % |

(fragilidad / riesgo de cola; 1.000 simulaciones. En primeras diferencias todos rechazan entre 5 % y
9 %.)

# 5. Pruebas para revisar con el profesor de econometría

1. **Simulación de tamaño y potencia:** tres procesos generadores (el original; remuestreo por fecha
   con AR(2) por país; VAR de panel con retroalimentación). ¿Está bien planteada? ¿Hay un proceso
   mejor para un panel de 13 países?
2. **Sesgo de retroalimentación:** el wild bootstrap no lo corrige. ¿Conviene un estimador que sí,
   o basta con declararlo y graduar la evidencia?
3. **Fechas:** spread promedio del trimestre frente a spread de cierre. ¿La prueba de cierre a
   cierre es la correcta para la precedencia?
4. **Bandas de aditividad:** intervalo invertido del wild bootstrap para β3. ¿Es la forma correcta
   de reportar cuánta amplificación no se descarta?
5. **Permutación por bloques** para la simultaneidad: ¿el desplazamiento circular dentro de cada
   país es suficiente, dado que el exceso viene de pocos episodios comunes?
6. **Preespecificación** de la prueba de participación extranjera: consta en el encabezado del
   script. ¿Hace falta un registro externo?
7. **Comparaciones múltiples:** Holm sobre cada familia. ¿Las familias están bien definidas?
8. **Dependencia de un país:** Turquía (fragilidad) y Polonia (riesgo de cola, reservas). ¿Reportar
   la regresión sin ellos junto a la principal?

# 6. Pendientes para el seguimiento del viernes 16

- [ ] Contarle al profesor Martínez que el titular cambió dos veces y por qué (sección 0).
- [ ] Pedirle su acuerdo con que la fragilidad quede como réplica de Chari et al. y no como
      conclusión.
- [ ] Confirmar con el programa quién figura como guía y quién como coguía (por ahora: guía J. F.
      Martínez, coguía R. Fischer).
- [ ] Reunión con el profesor de econometría (sección 5).
- [x] Base de participación extranjera en la deuda (Arslanalp y Tsuda, FMI, versión de mayo de
      2026) bajada y prueba preespecificada corrida.
- [x] Fechas de la línea del FMI de Chile verificadas: acceso continuo desde 2020Q2 (en mayo de 2022
      pasó a una Línea de Liquidez de Corto Plazo y el 29 de agosto de 2022 el FMI aprobó una nueva
      Línea de Crédito Flexible).
- [ ] Llevar la tesis con los cambios y la presentación de 10 láminas.
- [ ] Planificar los seguimientos; meta de defensa: primera semana de diciembre.
