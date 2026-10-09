---
title: "Predefensa con el profesor guía"
subtitle: "Guion detallado lámina por lámina, preguntas probables y decisiones a pedir"
---

*Presento la defensa completa al profesor guía como si fuera la predefensa. Tengo **una hora**:
unos **50 minutos de exposición** y el resto para preguntas. Él va a interrumpir y probar la
econometría; el objetivo es exponer con claridad y salir con decisiones.*

**Antes de entrar**

- [ ] La presentación nueva (51 láminas: 35 de exposición y 16 de respaldo) en PDF, en el computador y
      en un pendrive.
- [ ] La tesis en PDF abierta, por si pide una tabla completa, y esta guía impresa.
- [ ] Cronómetro visible. Ensayar una vez en voz alta midiendo los tiempos por sección.
- [ ] Saber de memoria la página 2.

**Cómo usar este guion.** Cada lámina tiene cinco partes:

- **Propósito:** qué debe quedar claro al terminarla.
- **Qué digo:** el texto, en primera persona. No hay que leerlo palabra por palabra.
- **Cómo leer:** en las tablas y figuras, adónde señalar.
- **Transición:** la frase que lleva a la lámina siguiente.
- **Si me pregunta:** la respuesta corta a la pregunta más probable en ese punto.

\newpage

# 1. Lo que tengo que saber de memoria

**La historia en tres frases**

1. Estudio si la **fragilidad bancaria** y el **riesgo de cola del crecimiento** encarecen juntos la
   deuda soberana de 13 economías emergentes.
2. Ambos se **asocian** con un spread mayor, pero no se puede leer como **causal**: el spread
   también deteriora la fragilidad y ambos son muy persistentes.
3. La **amplificación** no aparece en promedio, sino **fuera de crisis con respaldo oficial y en
   economías de financiamiento externo**: evidencia **condicional**, no robusta.

**Las cifras**

| Qué | Cifra |
|---|---|
| Muestra | 13 economías, 2004Q2–2026Q2, N = 765 (14 y 799 con Argentina) |
| Fragilidad → spread (β1) | 0,0985: duplicar JLoss ≈ +7 %; ≈ 4,7 pb por unidad en niveles |
| Riesgo de cola → spread (β2) | 0,0324: +1 pp de D ≈ +3,3 % de spread |
| Interacción promedio (β3) | −0,011 (p = 0,11); complementariedad implícita +0,19 pb |
| Retroalimentación spread → JLoss | 0,17 (p = 0,009); persistencia ρ = 0,94 |
| Wild bootstrap (β1 / β2 / β3) | p = 0,33 / 0,20 / 0,89 |
| Vector de crisis (CM4, col. 1) | Backstop −0,015 (p = 0,03; cluster 0,40); EMstress +0,026 (p = 0,08) |
| Permutación de EMstress | lugar 20 de 51, p = 0,39 |
| Núcleo de 11, sin crisis | +0,034 (wild p = 0,015) y +1,8 pb (wild p = 0,002) |

**Las tres salvedades del resultado condicional:** el grupo se definió *ex post*; en logaritmos los
controles lo absorben; 11 *clusters* son pocos.

**Lo que NO debo decir:** que las métricas son mías (son de Chari et al. y de Adrian et al.; mía es
su construcción), que la fragilidad *causa* el spread, ni que la amplificación está *demostrada*.

\newpage

# 2. Guion lámina por lámina (≈ 50 min)

## Motivación y pregunta (≈ 8 min)

### 1. Portada (20 s)
**Qué digo:** "Buenos días, profesor. Presento *Fragilidad bancaria sistémica y riesgo de cola del
crecimiento: determinantes del spread soberano en economías emergentes*. Lo voy a exponer como si
fuera la defensa, y le agradecería que me interrumpa cuando quiera."

### 2. Índice (20 s)
**Qué digo:** "Son cinco partes: motivación, medición y estrategia, datos, resultados y
conclusiones. El centro está en los resultados: la batería principal y la batería con el vector de
crisis."

### 3. Dos pilares del spread soberano emergente (1 min 30 s)
**Propósito:** situar la tesis en la literatura y mostrar la brecha.

**Qué digo:** "La literatura explica el spread soberano de los emergentes con dos pilares. El
primero son los fundamentos domésticos ---Edwards, Hilscher y Nosbusch, Uribe y Yue---: deuda,
crecimiento, reservas. El segundo son los factores globales ---Calvo, Leiderman y Reinhart,
Longstaff et al., Miranda-Agrippino y Rey---: el apetito global por riesgo mueve a todos los
emergentes juntos. Yo mido lo doméstico con dos variables: la fragilidad bancaria, con JLoss, y el
riesgo de cola del crecimiento, con el GaR. Lo global lo absorbo con efectos fijos de tiempo. La
brecha es esta: Chari et al. (2024) cruzan la fragilidad bancaria con factores globales; nadie la
ha cruzado con el riesgo de cola doméstico."

**Transición:** "¿Por qué tendrían que interactuar? Por el mecanismo."

**Si me pregunta** por qué no incluyo el VIX: los efectos fijos de tiempo absorben todo choque
común, incluido el VIX; en la réplica de Chari los incluyo explícitamente y el resultado no cambia.

### 4. El mecanismo y el balance de fuerzas (2 min)
**Propósito:** que se entienda por qué la coincidencia debería amplificar, y anticipar el problema
de identificación.

**Cómo leer:** el diagrama de arriba hacia abajo; después, la flecha punteada.

**Qué digo:** "Un estado adverso del crecimiento encarece el rescate bancario esperado. Ese rescate
esperado es lo que mide JLoss: un pasivo contingente del fisco, el *bailout put* de Farhi y Tirole
y la dilución de Acharya, Drechsler y Schnabl. El mercado lo cobra en el spread. A la derecha está
el balance de fuerzas: abren la brecha los bancos frágiles, la cola adversa y la deuda en manos
extranjeras; la contienen el respaldo oficial ---la Fed, el FMI--- y un mercado local de deuda
profundo. Y la flecha punteada es clave: un spread más alto deprecia los bonos que tienen los
bancos y los hace más frágiles. Esa causalidad inversa es mi principal problema de identificación,
y vuelve más adelante."

**Transición:** "Con esto, la pregunta."

### 5. Pregunta e hipótesis (1 min 15 s)
**Qué digo:** "La pregunta es si el mercado penaliza de forma no lineal la coincidencia de
fragilidad bancaria y cola adversa. H1: la fragilidad eleva el spread. H2: el riesgo de cola lo
eleva. H3: su coincidencia lo amplifica. Un matiz que ordena todo lo demás: si ambos riesgos escalan
la misma probabilidad de incumplimiento, en puntos básicos ya se potencian; eso es la versión
proporcional, que no necesita una interacción. La versión exigente de H3 es una amplificación
adicional: un coeficiente de interacción positivo en logaritmos."

**Si me pregunta** de dónde sale la versión proporcional: de un modelo de intensidad de
incumplimiento (Duffie y Singleton, 1999). Si el spread es proporcional a una intensidad que
depende de JLoss y de D de forma multiplicativa, el efecto cruzado en pb es positivo sin necesidad
de interacción.

### 6. Objetivos (45 s)
**Qué digo:** "El objetivo general es evaluar el impacto conjunto y no lineal de ambos riesgos. Los
específicos son cuatro: construir las series, cuantificar el efecto de la fragilidad en puntos
básicos y elasticidades, el del riesgo de cola en puntos básicos, y contrastar la
complementariedad. Al final vuelvo a cada uno."

### 7. Qué aporta esta tesis (2 min)
**Propósito:** dejar claro, desde el inicio, qué es propio y qué no.

**Qué digo:** "Quiero ser preciso con el aporte. Las métricas no son mías: JLoss es la de Chari et
al. (2024), y el GaR es el de Adrian, Boyarchenko y Giannone (2019), que implemento con la
plataforma de CEMLA. Lo propio es la construcción: reimplementé JLoss en Python, lo validé contra el
código original y lo calculé para 113 bancos extraídos con un mismo protocolo de Bloomberg; y estimé
el GaR en pseudo–tiempo real para todo el panel. Sobre eso, el aporte tiene tres partes. Conceptual:
unir el nexo banca–soberano y el growth-at-risk en un solo mecanismo. Empírica: el primer cruce de
la fragilidad bancaria con el riesgo de cola doméstico, una réplica independiente de Chari, y la
delimitación de cuándo y dónde aparece la amplificación. Y metodológica: un pipeline reproducible."

**Transición:** "Paso a cómo se construyen las dos medidas."

**Si me pregunta** qué cambié respecto de Chari: la parametrización es la misma; lo que hice fue
reimplementarla, ampliarla a más bancos y economías con una fuente homogénea, y cruzarla con el GaR.

## Medición y estrategia (≈ 9 min)

### 8. Construcción de JLoss (2 min)
**Propósito:** que se entienda qué mide JLoss y por qué entra en logaritmos.

**Cómo leer:** los cuatro pasos en orden; la leyenda de abajo define cada letra.

**Qué digo:** "JLoss es la pérdida conjunta esperada del sistema bancario ante un evento sistémico,
como porcentaje de la exposición. Se construye en cuatro pasos. Uno: la probabilidad de
incumplimiento de cada banco con un modelo de Merton–KMV; el punto de incumplimiento D\* es la
deuda de corto plazo más la mitad de la de largo plazo, y la probabilidad es la normal evaluada en
menos la distancia al incumplimiento. Dos: esas probabilidades se condicionan a un factor sistémico
del país ---el retorno bursátil--- con la fórmula de Vasicek, donde rho es la correlación de cada
banco con ese factor. Tres: la distribución de pérdidas del sistema se agrega por el método de
punto de silla. Cuatro: JLoss es la pérdida esperada más la inesperada al 99 %, sobre la exposición
total, con una pérdida en caso de incumplimiento de 45 %. Un detalle importante: la cota de la malla
de pérdidas está activa en el 98 % de los casos, así que JLoss funciona como una medida ordinal; por
eso entra en logaritmos, que son invariantes a la escala."

**Si me pregunta** por qué ordinal: la componente inesperada queda evaluada en la cota (4,8 %), así
que la variación la gobiernan las probabilidades de incumplimiento. En percentiles la asociación se
mantiene (lámina 48).

### 9. Construcción del GaR (1 min 30 s)
**Qué digo:** "El GaR es el cuantil 5 % de la distribución del crecimiento un trimestre adelante.
Primero construyo un índice de condiciones financieras tipo CISS, con tensión accionaria, de tasas
y cambiaria; replica la salida de referencia de CEMLA con correlación 0,9995. Después estimo una
regresión cuantílica de panel del crecimiento futuro sobre el crecimiento actual, el índice
financiero sin el componente del VIX, el VIX y un efecto fijo de país. El GaR es el cuantil 5 %, y
lo estimo en pseudo–tiempo real: en cada fecha uso solo la información disponible hasta ella. En la
tesis uso D, que es menos el GaR: mayor D significa una cola más adversa. La figura muestra Chile:
en 2020Q2 la distribución se desplaza y el cuantil 5 % cae a −13,4 puntos."

**Si me pregunta** si el GaR es circular con el EMBI: el EMBI no entra al cálculo; el único
componente con forma de spread aporta 0,07 al índice y sin él el GaR correlaciona 0,985 con el
oficial.

### 10. Especificación principal y batería (2 min)
**Propósito:** que quede claro qué es cada coeficiente y qué es cada columna de las tablas.

**Cómo leer:** la ecuación, su leyenda, y abajo cómo se arma la batería.

**Qué digo:** "La especificación principal regresa el logaritmo del EMBI sobre el logaritmo de JLoss
y D, ambos rezagados un trimestre, y su producto, con efectos fijos de país, alfa, y de tiempo,
delta. Beta uno es la elasticidad a la fragilidad; beta dos, la semielasticidad al riesgo de cola;
beta tres, la interacción: si es positiva, hay amplificación adicional. Rezago por la causalidad
inversa, y logaritmos porque las series son muy asimétricas y así los coeficientes son
elasticidades. Siguiendo a Chari, estimo una batería: cuatro modelos anidados ---M1 solo
fragilidad, M2 solo riesgo de cola, M3 ambos, M4 ambos con la interacción--- por tres estructuras de
efectos fijos ---tiempo, país y ambos--- y tres muestras: completa, sin crisis y con controles."

**Si me pregunta** por qué no hay controles en la principal: porque balance fiscal, inflación o tipo
de cambio son plausiblemente canales del mecanismo; condicionar en ellos mediría el efecto neto de
sus propios canales. Los agrego como robustez (Panel C).

### 11. Especificación con el vector de crisis (2 min)
**Propósito:** explicar el test de falsación antes de mostrar sus tablas.

**Qué digo:** "Excluir los trimestres de crisis supone que el mecanismo cambia en ellos. La prueba
más exigente es mantener toda la muestra e interactuar con un indicador de crisis C. Beta tres
pasa a ser la interacción fuera de crisis, y beta tres más beta cuatro la interacción dentro de la
crisis; beta cinco y seis son los cambios de la fragilidad y de la cola en crisis, y X son seis
controles domésticos. Uso dos versiones del vector. La primera, un vector único: GFC, estrés
emergente de 2015–16 y COVID. La segunda lo descompone como test de falsación: *Backstop*, la GFC y
el COVID, con líneas swap de la Fed y financiamiento del FMI; y *EMstress*, 2015–16, sin un respaldo
comparable. Si el respaldo oficial apaga el canal, la amplificación debería desaparecer bajo
*Backstop* y sobrevivir bajo *EMstress*."

### 12. Inferencia: cómo mido la incertidumbre (1 min 30 s)
**Qué digo:** "Antes de los resultados, cómo mido la incertidumbre, porque es donde se juega la
conclusión. La referencia son errores de Driscoll–Kraay, robustos a heterocedasticidad, a la
autocorrelación del spread y a choques comunes entre países. Como contraste, errores agrupados por
país. Pero con solo 13 países los errores asintóticos son optimistas, así que cada resultado central
lo someto a un wild cluster bootstrap con pesos de Webb, que es la corrección estándar con pocos
clusters: un resultado es robusto solo si resiste esa prueba. Además propago el error del GaR, que
es una estimación, y aplico pruebas de identificación: canal inverso, dinámica, proyecciones
locales, instrumentos y permutación."

## Datos (≈ 2 min)

### 13. El panel (1 min)
**Qué digo:** "El panel tiene 13 economías emergentes y 765 observaciones país–trimestre entre
2004 y 2026. En azul, la muestra de estimación. Argentina tiene las tres series, pero su GaR se
estimó con menos información, así que la uso como robustez. Corea, Bulgaria y Hungría quedan fuera
porque su JLoss no es válido a nivel país: en Corea el valor de mercado de la banca está muy por
debajo de su punto de incumplimiento, y en Bulgaria y Hungría cotizan uno o dos bancos."

### 14. Descriptivos y co-movimiento (1 min)
**Qué digo:** "El spread promedia 198 puntos básicos. Más del 80 % de la variación de JLoss y del
riesgo de cola es dentro de cada país, así que los efectos fijos de país no se comen la
identificación. La correlación entre ambos es 0,16: aportan información distinta. Y en la figura,
las tres series se mueven juntas en 2008–09 y 2020, que es la motivación directa de la interacción."

## Resultados I — la batería principal (≈ 8 min)

### 15. Panel A: muestra completa (2 min 30 s)
**Propósito:** mostrar que ambos riesgos se asocian con el spread en toda la batería y que la
interacción nunca es positiva y significativa.

**Cómo leer:** la columna (1) es la referencia: M4 con efectos fijos de país y tiempo. Leer fila por
fila. Después, recorrer M1 a M4 para mostrar estabilidad.

**Qué digo:** "Esta es la tabla central de la tesis. Cada columna es una regresión. La (1), la
referencia, es el modelo completo con efectos fijos de país y tiempo. La fragilidad tiene una
elasticidad de 0,099, significativa al 1 %; el riesgo de cola, una semielasticidad de 0,032,
significativa al 5 %; y la interacción, −0,011, no significativa. Ahora miren la batería completa:
la fragilidad es positiva y significativa al 1 % en las nueve columnas en que aparece, entre 0,10 y
0,25; es mayor con solo efectos de tiempo porque parte de la asociación es entre países. El riesgo
de cola es positivo en todas. Y la interacción, en las columnas 11 y 12, también es negativa y no
significativa."

**Si me pregunta** por qué la columna (1) y no otra: es la especificación de Chari, con efectos fijos
bidireccionales, que absorben tanto lo permanente de cada país como lo común a todos en cada
trimestre.

### 16. Panel B: sin trimestres de crisis (1 min 30 s)
**Qué digo:** "Si saco la GFC y el COVID, el patrón se mantiene: fragilidad 0,087, significativa;
riesgo de cola 0,050, significativo al 1 %; y la interacción pasa a positiva, 0,005, pero
indistinguible de cero. Es decir, las crisis no son las que generan la asociación."

### 17. Panel C: con seis controles domésticos (1 min 30 s)
**Qué digo:** "Con los seis controles ---deuda, balance fiscal, reservas, cuenta corriente,
inflación y tipo de cambio real--- la fragilidad deja de ser significativa: −0,008 en la columna 1.
El riesgo de cola se mantiene, 0,028. Esto no lo explica la muestra: sobre las mismas 649
observaciones sin controles, la fragilidad es 0,107. Lo absorben los controles, y la fragilidad
rezagada los predice: anticipa un balance fiscal más deficitario, más inflación, una apreciación
real menor y más deuda. Es lo que esperaríamos si fueran los canales por los que opera la
fragilidad."

**Si me pregunta** si no es un fundamento común: no lo puedo descartar; con los controles medidos
cuatro trimestres antes la elasticidad es 0,062, menor y no significativa.

### 18. Lectura de la batería principal (2 min)
**Qué digo:** "En magnitudes: una elasticidad de 0,10 quiere decir que duplicar JLoss se asocia con
un spread cerca de 7 % mayor; en niveles son unos 4,7 puntos básicos por unidad de JLoss. Cada punto
de riesgo de cola se asocia con un spread 3,3 % mayor. Con los controles de Chari, la elasticidad de
la fragilidad está entre 0,107 y 0,164, del orden de lo que reportan: los replico con datos
construidos de forma independiente. Y la interacción nunca es significativamente positiva."

**Transición:** "Esto es el promedio. La siguiente pregunta es si la interacción cambia en las
crisis."

## Resultados II — la batería con el vector de crisis (≈ 7 min)

### 19. Vector único (2 min 30 s)
**Cómo leer:** columna (1), las filas en negrita: la interacción fuera de crisis (β3) y en crisis
(β3+β4) con su p entre corchetes. Todas las columnas tienen controles.

**Qué digo:** "Ahora interactúo con el vector de crisis. En la columna de referencia, fuera de
crisis la interacción es 0,012, no significativa. Dentro de las crisis, beta tres más beta cuatro es
−0,012, significativa al 5 %: en las crisis, la interacción es negativa. Con solo efectos de tiempo,
columna 11, es −0,025; con solo efectos de país, columna 12, desaparece. Mezclar todas las crisis en
un solo vector, sin embargo, junta episodios muy distintos. Por eso lo descompongo."

### 20. Backstop vs. EMstress (2 min 30 s)
**Cómo leer:** columna (1), las dos últimas filas en negrita.

**Qué digo:** "Al separar las crisis, bajo *Backstop* ---la GFC y el COVID, con respaldo oficial---
la interacción es −0,015, significativa al 5 %. Bajo *EMstress* ---2015–16, sin respaldo--- es
+0,026, significativa al 10 %. Con solo efectos de país, columna 12, la de *EMstress* es 0,036 y
significativa al 1 %. Al pie de la letra, es exactamente el patrón del mecanismo: la amplificación
aparece cuando el soberano enfrenta el estrés sin respaldo y desaparece cuando la Fed y el FMI
intervienen."

### 21. Lectura: el patrón esperado, pero sin robustez (2 min)
**Cómo leer:** primero la lista, después el histograma: la línea roja es 2015–16 en medio de la
distribución.

**Qué digo:** "Pero tres pruebas indican que el panel no sostiene esa lectura. Con errores agrupados
por país, ninguna suma es significativa: p de 0,40 y 0,11. Si el mecanismo opera en el estrés sin
respaldo, debería aparecer también en el *taper tantrum* de 2013 y en la venta de emergentes de
2018: no aparece. Y la permutación: reemplazo 2015–16 por cada una de las 51 ventanas de tres
trimestres fuera de *Backstop*; el episodio real queda en el lugar 20. Una de cada tres ventanas al
azar produce una amplificación igual o mayor."

**Transición:** "Queda la pregunta de fondo: ¿estas asociaciones son efectos?"

## Resultados III — qué se puede afirmar (≈ 6 min)

### 22. ¿Efecto o persistencia? (2 min)
**Qué digo:** "El rezago hace a los regresores predeterminados, pero no exógenos. Primero, la
retroalimentación: el spread de ayer predice la fragilidad de hoy con una elasticidad de 0,17, mayor
que la de la dirección que busco. Segundo, el spread es muy persistente, 0,94 trimestral; si agrego
el spread rezagado, el efecto de la fragilidad cae a 0,005. Tercero, las proyecciones locales ---la
figura--- son planas en todos los horizontes."

**Si me pregunta** por el sesgo de Nickell: con unos 88 trimestres el sesgo es del orden de 1/T; el
colapso del coeficiente no es un artefacto.

### 23. Inferencia: qué resiste y qué no (2 min)
**Cómo leer:** columna "Lectura", de arriba hacia abajo.

**Qué digo:** "Con wild cluster bootstrap sobre 13 países, ni la fragilidad (p = 0,33) ni el riesgo
de cola (p = 0,20) son significativos. Driscoll–Kraay es estable frente al ancho de banda, pero
optimista con pocos países. Las variables instrumentales ---liquidez del Tesoro, dólar amplio y
términos de intercambio, con exposiciones pre-muestra--- tienen primeras etapas razonables, pero
dan +0,35, −2,18 y +0,15, y Sargan las rechaza: no identifican el mismo parámetro. Y el GaR como
regresor generado no es el problema. Conclusión: las asociaciones existen, pero no se pueden leer
como causales."

### 24. En promedio, no hay amplificación adicional (2 min)
**Cómo leer:** la recta del efecto marginal baja de izquierda a derecha.

**Qué digo:** "Si hubiera amplificación, la elasticidad a la fragilidad crecería con el riesgo de
cola. No crece: es 0,145 en el percentil 10 de D, 0,098 en la mediana y 0,054 en el percentil 90. En
puntos básicos sí se potencian, +0,19, pero esa es la complementariedad que ya implica la forma
proporcional. Y la interacción significativa que tenía la versión anterior en niveles: lo que la
elimina es el logaritmo, no el rezago."

**Transición:** "Si no aparece en promedio, ¿aparece en algún lugar?"

## Resultados IV — dónde aparece (≈ 6 min)

### 25. Dónde sí aparece (1 min 30 s)
**Cómo leer:** el gráfico de abajo hacia arriba. Los puntos grises son el panel completo; los
azules, el núcleo; el rojo, Polonia e India.

**Qué digo:** "Separo las economías según quién fija el precio de su deuda. Las once del núcleo se
financian con inversionistas extranjeros; Polonia e India tienen mercados locales profundos. En el
panel completo la interacción es cero. En el núcleo, fuera de las crisis con respaldo, es +0,034 y
el intervalo no toca el cero. En Polonia e India, al revés."

### 26. Heterogeneidad por tipo de economía (2 min)
**Cómo leer:** la columna "Sin crisis" de log-log y de niveles; después la fila de controles.

**Qué digo:** "En el núcleo y sin crisis la interacción es 0,034 en logaritmos y 1,8 puntos básicos
en niveles, y es la única amplificación de toda la tesis que resiste el wild bootstrap: p de 0,015 y
0,002. Excluyendo un país a la vez se mantiene positiva. Pero con los seis controles, en logaritmos
cae a 0,004. Las once economías son Brasil, Chile, China, Colombia, Filipinas, Indonesia, Malasia,
México, Perú, Sudáfrica y Turquía."

### 27. Cómo leer este hallazgo (1 min 30 s)
**Qué digo:** "Lo digo explícitamente: es un hallazgo condicional. Lo respalda que resiste el wild
bootstrap, que aparece en ambas formas funcionales, que sobrevive a excluir cada país y que el grupo
de contraste va en sentido opuesto. Lo limita que el grupo lo definí después de ver la versión
anterior, así que la significancia está sobrestimada por la búsqueda de especificación; que en logs
los controles lo absorben; que son 11 países; y que 2015–16 no pasa la permutación. Por eso lo
presento como una hipótesis bien delimitada, no como un hallazgo robusto."

### 28. Robustez (1 min)
**Qué digo:** "Las conclusiones no dependen de la muestra: con Argentina, con el Expected Shortfall
en vez del GaR, sin los trimestres de EMBI empalmados del FMI o excluyendo cada país, nada cambia. En
puntos básicos la evidencia es más favorable, pero tampoco resiste el wild bootstrap."

## Conclusiones (≈ 6 min)

### 29. Respuesta a la pregunta (1 min 15 s)
**Qué digo:** "Vuelvo a los objetivos. Uno: las series están construidas y validadas para 13
emergentes. Dos: la fragilidad se asocia con el spread, 0,10 o 4,7 puntos básicos, pero no de forma
causal. Tres: el riesgo de cola, +3,3 % por punto, tampoco de forma causal. Cuatro: la
complementariedad es proporcional en promedio y la adicional solo aparece condicionalmente. ¿Penaliza
el mercado la coincidencia de forma no lineal? No en general. Sí, condicionalmente."

### 30. Hallazgos específicos y su grado de evidencia (1 min 30 s)
**Cómo leer:** la tercera columna: establecida, no establecida, no robusta o condicional.

**Qué digo:** "Resumo cada hallazgo con su cifra y su grado de evidencia. Establecido: las dos
asociaciones, la réplica de Chari, la absorción por los controles y la retroalimentación. No
establecido: el efecto causal. No hay amplificación en promedio. No robustas: las asimetrías por
crisis. Condicional: la amplificación en el núcleo sin crisis y el contraste de Polonia e India."

### 31. Dónde buscar la amplificación (1 min 30 s)
**Qué digo:** "Esta es la caracterización. Cuándo: fuera de las crisis con respaldo oficial
masivo, cuando coinciden fragilidad alta y cola adversa sin un prestamista de última instancia.
Dónde: en las once economías cuya deuda la compran inversionistas extranjeros, no en Polonia ni en
India. Por qué: porque ese inversionista es sensible al riesgo del rescate y lo traslada al precio.
Qué vigilar: JLoss y el GaR juntos, y la participación extranjera en la deuda. Qué falta para
confirmarlo: un grupo definido de antemano, más países y más episodios sin respaldo."

### 32. Implicancias (45 s)
**Qué digo:** "Lo respaldado: monitorear JLoss y el GaR juntos, porque ambos adelantan un spread más
alto. Si lo condicional se confirma, convendría focalizar la regulación en esos casos en lugar de
una exigencia uniforme. Lo que no permite: decir cuánto bajaría el spread si cae la fragilidad."

### 33. Limitaciones y trabajo futuro (45 s)
**Qué digo:** "Las limitaciones son 13 países, una relación de doble vía, la heterogeneidad
definida ex post y una medida ordinal. El trabajo futuro: más países, la participación extranjera
medida de antemano, variación exógena bancaria y datos de mayor frecuencia."

### 34. Conclusión (30 s)
**Qué digo:** Leer las tres frases y cerrar con: "El aporte es saber dónde buscar la amplificación y
qué haría falta para confirmarla."

### 35. Gracias
**Qué digo:** "Muchas gracias. Quedo atento a sus comentarios."

*Respaldo (36–51): no se presenta; se usa para responder. Taller I (36); baterías con errores
estándar: Panel A (37), B (38), C (39), vector único (40), Backstop vs. EMstress (41); logs vs.
niveles (42); niveles prueba por prueba (43); heterogeneidad en niveles (44); Argentina (45); Hansen
(46); leave-one-out y ventanas (47); medición de JLoss y GaR (48); COVID (49); referencias (50–51).*

\newpage

# 3. Preguntas probables del profesor guía

*Responder en una o dos frases y, si insiste, ir a la lámina de respaldo. Es probable que conozca
JLoss y Chari et al. (2024) en detalle: espera preguntas finas sobre la métrica.*

**¿Las métricas son suyas?** No: JLoss es de Chari et al. (2024) y el GaR de Adrian et al. (2019),
con la plataforma de CEMLA. Lo mío es la construcción homogénea, la reimplementación validada y el
cruce de ambas (lámina 7).

**¿Por qué log-log y no niveles, como en el Informe de Taller?** Porque las series son muy
asimétricas y JLoss es ordinal; la prueba PE prefiere logs. Reporto todo también en niveles
(láminas 42 y 43): la evidencia es más favorable, pero tampoco resiste el wild bootstrap.

**¿Por qué no hay controles en la regresión principal?** Porque son plausiblemente canales del
mecanismo: la fragilidad rezagada los predice. Con controles en t−4 la elasticidad es 0,062 (n.s.).

**¿El rezago resuelve la endogeneidad?** No del todo: elimina la causalidad inversa más directa, pero
el spread es persistente (0,94) y se retroalimenta (0,17). Por eso no hablo de efectos causales.

**¿No es un problema el sesgo de Nickell?** Con T ≈ 88 trimestres el sesgo es del orden de 1/T.

**¿Por qué Driscoll–Kraay y además wild bootstrap?** DK es robusto a autocorrelación y dependencia
transversal, pero con 13 clusters es optimista. El wild bootstrap con pesos de Webb corrige eso.

**¿Por qué la columna (1) de la batería tiene efectos fijos bidireccionales?** Es la especificación
de Chari y absorbe tanto lo permanente de cada país como lo común en cada trimestre. El resto de la
batería muestra que el signo no depende de esa elección.

**¿Por qué la batería de crisis tiene controles y la principal no?** Porque el vector de crisis es
una prueba más exigente sobre la misma muestra con controles (649 obs.); la principal se reporta sin
ellos por el argumento de mal control.

**¿Por qué fallaron los instrumentos?** Son choques macro-agregados; mueven más que la fragilidad
bancaria. Haría falta un instrumento específicamente bancario.

**El núcleo de 11 economías, ¿no es búsqueda de especificación?** Sí, en parte, y lo digo en la
lámina 27. Por eso es condicional, y propongo un moderador continuo medido ex ante: la participación
extranjera en la deuda.

**¿Por qué JLoss es ordinal?** La cota de la malla de pérdidas (4,8 %) está activa en el 98 % de los
casos; la variación viene de las probabilidades de incumplimiento (lámina 48).

**¿El GaR no está contaminado por el spread?** El EMBI no entra al cálculo; sin el único componente
tipo spread, el GaR correlaciona 0,985 con el oficial.

**¿Por qué Argentina no está en la muestra principal?** Su GaR se estimó sin el bloque de tasas y con
una ventana más corta. Como robustez no cambia nada (lámina 45).

**Si nada es causal, ¿cuál es el aporte?** La construcción homogénea de las series para 13 países, la
réplica independiente de Chari, el primer cruce con el riesgo de cola doméstico y la delimitación de
dónde aparece la amplificación.

# 4. Decisiones que debo pedirle

1. **¿La tesis está lista para defender?** Si no, qué falta y con qué plazo.
2. **Encuadre:** ¿de acuerdo con "asociación, no causalidad; amplificación condicional"?
3. **Heterogeneidad por economía:** ¿la dejo en Resultados o la bajo a robustez por ser *ex post*?
4. **Argentina:** ¿se queda como robustez o la homologo e incorporo a la muestra principal?
5. **Forma funcional:** ¿logs como principal y niveles en paralelo?
6. **Presentación:** ¿cuánto tiempo tendré en la defensa? ¿Qué láminas sacaría?
7. **Paper:** ¿vale la pena enviarlo? ¿A qué revista?
8. **Calendario:** entrega final, comisión y fecha de defensa.

# 5. Para cerrar la reunión

- [ ] Veredicto: lista / lista con cambios / falta trabajo.
- [ ] Lista de cambios pedidos, con prioridad.
- [ ] Decisiones 2 a 5 tomadas.
- [ ] Duración de la defensa y láminas a recortar.
- [ ] Fechas: entrega, comisión, defensa.

**Notas:**

\vspace{5cm}
