---
title: "Predefensa con el profesor guía"
subtitle: "Guion lámina por lámina: pregunta, resultado e interpretación"
---

*La exposición tiene 14 láminas y dura unos 25–30 minutos. El resto de la hora es para preguntas. El
anexo (31 láminas) no se expone: se abre cuando una pregunta lo pide. Versión ajustada tras la reunión
del 6 de noviembre de 2026 con el profesor guía.*

**Lo que pidió el profesor el 6-11 y dónde quedó**

| Pedido | Dónde quedó |
|---|---|
| Efecto del riesgo de cola en pb por una d.e. de la métrica | Láminas 8, 9, 13 y 14: una d.e. ≈ +10 %, unos 17 pb (15 pb con controles); con deuda, de 23 a 29 pb |
| Sacar al anexo lo que no es resultado ("no hay evidencia de otros canales") | Otros moderadores y el Panel B (sin crisis) pasaron al anexo |
| Resultados más claros, "en cajitas", con su interpretación | Cada lámina de resultados: arriba la pregunta, abajo una caja *Resultado* y una *Interpretación* |
| Conclusiones, política e investigación futura en una sola lámina | Lámina 14, con 5 resultados, 3 implicancias y 3 líneas futuras |
| Ordenar con puntos 1, 2… | Las hipótesis llevan la ecuación que las contrasta |
| Revisar las pruebas empíricas | Ver "Revisión de las pruebas" al final |
| 12–14 láminas | 14 |

**Antes de entrar**

- [ ] La presentación en PDF, en el computador y en un pendrive.
- [ ] La tesis en PDF abierta, por si pide una tabla completa.
- [ ] Cronómetro visible. Ensayar una vez en voz alta, explicando cada lámina en unos 30 segundos
      cuando el profesor lo pida ("más cortito").
- [ ] Saber de memoria la sección 1.

**Cómo está armado.** Primero numero las cinco ecuaciones y amarro cada hipótesis a una. Después
cada lámina de resultados tiene una franja arriba con la ecuación, el panel y **la pregunta** que
responde. Debajo va la tabla y, al pie, dos cajas: **Resultado** (qué encontré, con su $p$) e
**Interpretación** (qué significa, en puntos básicos cuando corresponde). El relato avanza de una
respuesta a la pregunta siguiente:

> ¿Cada riesgo se asocia con el spread? → ¿Resiste los controles? → ¿Qué agrega el riesgo económico? →
> ¿Coinciden? → Si coinciden, ¿se amplifican? → ¿La deuda cambia el peso del riesgo de cola?

**Cada lámina tiene:**

- **Propósito:** qué debe quedar claro.
- **Qué digo:** en primera persona. No se lee palabra por palabra.
- **Cómo leer:** adónde señalar.
- **Transición:** la frase que lleva a la lámina siguiente.
- **Si me pregunta:** la respuesta corta y la lámina del anexo.

\newpage

# 1. Lo que tengo que saber de memoria

**La pregunta:** sobre la fragilidad bancaria que ya documentan Chari et al. (2024), ¿qué agrega el
riesgo económico doméstico, y qué pasa cuando los dos riesgos se dan a la vez?

**Las cinco ecuaciones**

| | Ecuación | Prueba | Coeficiente |
|---|---|---|---|
| (1) | ln EMBI sobre ln JLoss, D y su producto, rezagados; EF país y tiempo | H1, H2, H3 | β1, β2, β3 |
| (2) | D sobre su rezago y ln JLoss rezagado (y la inversa) | precedencia | φ |
| (3) | ln EMBI sobre indicadores de tercil alto y su producto | H3 directa | a3 |
| (4) | (1) más deuda en t−4 y D × deuda | H4 | ψ |
| (5) | (1) más un moderador M y sus productos (anexo) | otros moderadores | λ1, λ2, λ3 |

**La magnitud, en puntos básicos (lo que pidió el profesor)**

El modelo está en logaritmos, así que el coeficiente es una semielasticidad: no se lee como puntos
básicos. La traducción es: coeficiente × una desviación estándar del riesgo de cola dentro del país
= cambio porcentual del spread; ese porcentaje × el spread medio (173 pb, media geométrica) = puntos
básicos.

| Especificación | Coeficiente | 1 d.e. de riesgo de cola | % del spread | pb |
|---|---|---|---|---|
| Panel A, referencia (N = 765) | 0,032 | 3,10 pp | +10 % | ≈ 17 |
| Panel C, seis controles (N = 649) | 0,028 | 3,17 pp | +9 % | ≈ 15 |
| H4 a un trimestre, deuda media | 0,043 | 3,13 pp | +13,5 % | ≈ 23 |
| H4 a un trimestre, una d.e. más de deuda | 0,054 | 3,13 pp | +17 % | ≈ 29 |
| H4 a un año, deuda media | 0,047 | 1,80 pp | +8,5 % | ≈ 15 |
| H4 a un año, una d.e. más de deuda | 0,080 | 1,80 pp | +14 % | ≈ 25 |

- Por punto porcentual de riesgo de cola: un 3,2 % del spread, unos 5,6 pb. Por eso antes decía
  "2–3 % por punto" y sonaba chico: el profesor tiene razón en que la unidad correcta es una d.e.
- Una d.e. de riesgo de cola equivale a 0,27 d.e. del logaritmo del spread dentro del país.
- Con el modelo en niveles (pb), una d.e. da 10 pb, pero no es significativo ($p=0{,}27$). Si me
  pregunta por qué difiere: los logaritmos pesan igual los cambios relativos de spreads bajos y altos;
  los niveles los dominan los países de spread alto. La prueba PE prefiere logaritmos.
- Fragilidad: una d.e. dentro del país, +5 % del spread (unos 9 pb).
- Riesgo de cola a un año: 4,7 % por punto, más que a un trimestre (3,2 %), pero por d.e. es un 8 %
  (unos 15 pb), algo menos, porque ese riesgo varía menos (d.e. 1,8 pp contra 3,1). No decir que "a
  un año pesa más" sin aclarar que es por punto.

**La historia en cinco resultados**

1. **Cada riesgo se asocia con un spread mayor** (1). Con los controles domésticos solo resiste el
   riesgo de cola: una d.e., unos 15–17 pb. La evidencia es sugerente (wild 0,33 y 0,20).
2. **Los dos riesgos coinciden** 1,2 veces lo esperado con el calendario común descontado, y la
   fragilidad antecede al riesgo de cola (2). Es el resultado firme.
3. **Cuando coinciden, no hay evidencia de que se amplifiquen** (1, 3). Es un no rechazo: se descarta
   más de un 35 % de la suma (unos 28 pb con los dos riesgos una d.e. arriba), no menos.
4. **Con más deuda, el riesgo de cola pesa más** (4): de unos 23 a unos 29 pb por d.e. Es una
   regularidad de la muestra: ni la réplica externa, ni el instrumento, ni el modelo la confirman.
5. **Reservas, respaldo externo y tenencia de la deuda no cambian la transmisión** (5; anexo).

**La frase que tiene que quedar:** *los dos riesgos llegan juntos, pero no se potencian. Vigilarlos
juntos se justifica; una exigencia adicional por su simultaneidad, no.*

**Escala de evidencia:** *firme* = resiste el wild bootstrap o la permutación y no depende de un
país; *sugerente* = solo Driscoll–Kraay, o depende de un país; *exploratorio* = no preespecificado y
no pasa Holm; *no hay evidencia*.

**Las cifras**

| Qué | Cifra |
|---|---|
| Muestra | 13 economías, 2004–2026, N = 765 (sin crisis 656; con controles 649) |
| Panel A, referencia | β1 0,099; β2 0,032; β3 −0,011; wild 0,33 / 0,20 / 0,89 |
| Panel B, sin crisis (anexo) | β1 0,087; β2 0,050; β3 0,005 |
| Panel C, seis controles | β1 −0,008 (p = 0,86); β2 0,028 (p = 0,046); mismas 649 obs. sin controles: 0,107 |
| Panel C, control por control | con un solo control la fragilidad sigue (solo deuda 0,077, p = 0,03; solo reservas 0,099); sin el tipo de cambio real, 0,064 (p = 0,13); solo los seis juntos la eliminan |
| Información incremental (N = 662) | β2 0,037; conjunta wild 0,041; R² 0,153 → 0,185 → 0,194 |
| Lo que no pasa | cambios a 4 trimestres 0,004 (0,13); proyecciones locales 0 de 9; fuera de muestra +3 % de error |
| Simultaneidad | 168 obs. (22,0 %); 87 bajo independencia (1,9 veces); 140,9 con el calendario común (1,2 veces; p = 0,0002); 13 de 13 |
| Precedencia | φ = 0,405 (wild 0,024); sin cada país 0,32–0,47; la inversa −0,006 |
| Concentración | 129 de las 168 coincidencias desde 2020 |
| Amplificación | β3 −0,011 (wild 0,89); a3 −0,077 (wild 0,23); TOST descarta > 35 % |
| H4, preregistro 1 | ψ = +0,011 por d.e. de deuda (0,043 → 0,054); Holm 0,029; 13 de 13 |
| H4, preregistro 2 | riesgo de cola a un año 0,047 (Holm 0,018); ψ = +0,033 (+70 %) |
| H4, en contra | 23 hipótesis: Holm 0,13 y 0,31; Hungría y Corea 0,22 (potencia 5 %); instrumento F 9,7 |
| Moderadores (anexo) | participación extranjera Holm 1,00; respaldo −0,004 (wild 0,90); reservas −0,247 (wild 0,08; preregistrada Holm 0,29); doom loop −0,053 |

**Vocabulario:** *amplificación* o *simultaneidad*, nunca "multiplicidad"; efectos *aditivos*;
*riesgo financiero* (JLoss) y *riesgo económico* (GaR). Son asociaciones: evito "reduce", "protege"
y "efecto de".

**Lo que NO debo decir:**

- Que las métricas son mías. JLoss es de Chari et al. (2024); el GaR, de Adrian et al. (2019) y el
  CEMLA. Mío es construir las series y cruzarlas.
- Que la amplificación "está descartada". No la encuentro, y se descarta solo una grande.
- Que la deuda "explica" la transmisión. Es una regularidad de la muestra.
- Que las reservas "atenúan" o "protegen".
- Que la deuda sola "absorbe" a la fragilidad: con la deuda como único control, la fragilidad sigue
  significativa. La absorben los seis controles juntos.

\newpage

# 2. Guion lámina por lámina (≈ 27 min)

## Apertura (≈ 6 min)

### 1. Portada (20 s)

**Qué digo:** "Mi tesis cruza dos riesgos de cola domésticos, el bancario y el del crecimiento, y
mira cómo se asocian con el spread soberano en 13 economías emergentes."

### 2. La pregunta (1 min 30 s)

**Propósito:** que quede la pregunta, en una frase.

**Qué digo:** "El spread es lo que paga un gobierno emergente sobre el Tesoro de Estados Unidos.
Chari et al. muestran que la fragilidad bancaria se asocia con él. El riesgo de cola del crecimiento
no se ha cruzado con la fragilidad. Mi pregunta tiene dos partes: qué agrega el riesgo económico, y
qué pasa cuando los dos riesgos se dan a la vez."

**Transición:** "¿Por qué podrían darse a la vez y llegar juntos al spread?"

### 3. El mecanismo (1 min 30 s)

**Propósito:** mostrar que los tres lados se mueven juntos. Por eso hablo de asociaciones.

**Qué digo:** "Bancos frágiles prestan menos y el crecimiento cae: es el acelerador financiero. Un
crecimiento débil deteriora a los bancos. Los dos llegan al spread: uno por el rescate esperado,
otro por la capacidad fiscal en la cola. Y el spread vuelve sobre los bancos. A la derecha, lo que
podría cambiar esa transmisión. La deuda pública es lo primero: de ahí sale H4."

**Cómo leer:** las flechas azules y luego la punteada.

**Si me pregunta** *¿y la causalidad?*: "No la reclamo. La retroalimentación sesga los coeficientes
de nivel; lo mido con una simulación (anexo, retroalimentación)."

### 4. Hipótesis (1 min)

**Qué digo:** "Cuatro hipótesis, cada una con su ecuación. Uno: la fragilidad eleva el spread. Dos:
el riesgo de cola también. Tres: juntos lo elevan más que la suma. Cuatro: con más deuda, el riesgo
de cola pesa más. Las otras condiciones van con la ecuación (5) y quedan en el anexo."

**Transición:** "Antes de las ecuaciones, las dos series."

### 5. Las dos variables en el tiempo (1 min)

**Qué digo:** "Mediana y rango intercuartil entre los 13 países. Lo sombreado son la crisis
financiera global, el estrés emergente de 2015–16 y la pandemia."

**Cómo leer:** las tres franjas grises. No comento nada más: la simultaneidad la muestro con la
ecuación (2).

**Si me pregunta** *¿y por país?*: los gráficos por país están en la tesis y en el visualizador; se
revisan con el profesor el viernes.

## Especificaciones (≈ 4 min)

### 6. Especificaciones (1)–(3) (2 min)

**Propósito:** que cada hipótesis quede atada a un coeficiente.

**Qué digo:** "La ecuación (1) es la principal: el logaritmo del spread sobre la fragilidad, el
riesgo de cola y su producto, todos rezagados un trimestre, con efectos fijos de país y de tiempo.
β1 es H1, β2 es H2 y β3 es H3. La (2) pregunta qué riesgo antecede al otro. La (3) contrasta H3 de
forma directa: indicadores de riesgo alto y su producto."

**Si me pregunta** *¿por qué logaritmos?*: "La prueba PE los prefiere, y JLoss es ordinal (anexo,
logaritmos vs. niveles)."

### 7. Especificaciones (4)–(5) e inferencia (2 min)

**Qué digo:** "La (4) es H4: la principal más la deuda de cuatro trimestres antes y su producto con
el riesgo de cola. Está preregistrada dos veces, con el riesgo de cola a un trimestre y a un año. La
(5) agrega otros moderadores; sus resultados van al anexo. Con 13 países, el criterio es el wild
bootstrap por país; la escala de abajo ordena todo lo que viene."

**Transición:** "Parto por la ecuación (1)."

## Resultados (≈ 13 min)

### 8. Ecuación (1) · Panel A (2 min 30 s)

**Propósito:** H1 y H2 tienen signo positivo; dar la magnitud en pb.

**Qué digo:** "En la muestra completa, la fragilidad y el riesgo de cola son positivos en todas las
columnas. La interacción es −0,011. Con el wild bootstrap, ninguno resiste: 0,33, 0,20 y 0,89. Por
eso digo 'sugerente'. ¿Cuánto es? Una desviación estándar de riesgo de cola dentro del país, unos
3 puntos de crecimiento en la cola, se asocia con un spread un 10 % mayor: unos 17 puntos básicos
sobre un spread medio de 173."

**Cómo leer:** la columna Ref., después la caja de interpretación.

**Si me pregunta** *¿depende de un país?*: "Sí: Turquía en la fragilidad y Polonia en el riesgo de
cola (anexo, pendientes por país y Polonia)."

**Si me pregunta** *¿y sin las crisis?*: "El mismo patrón: 0,087, 0,050 y una interacción de 0,005
(anexo, Panel B)."

### 9. Ecuación (1) · Panel C (2 min)

**Qué digo:** "Con los seis controles domésticos, la fragilidad cae a −0,008 y el riesgo de cola se
mantiene en 0,028: una d.e., unos 15 pb. No es la muestra: con las mismas 649 observaciones y sin
controles, la fragilidad da 0,107. Y no es un control en particular: con cualquiera de ellos solo,
la fragilidad sigue; la eliminan los seis juntos. El riesgo de cola, en cambio, trae información que
los fundamentos no tienen."

**Si me pregunta** *¿entonces no replicas a Chari?*: "Con sus controles sí: entre 0,107 y 0,164. Con
los míos no. Varios de esos controles son canales del propio mecanismo."

**Si dice** *los canales real y financiero quedan capturados por el GaR y la deuda*: "Es una lectura
posible para el conjunto, pero con la deuda como único control la fragilidad sigue significativa
(0,077); la absorben los seis juntos."

**Transición:** "Ahora, sobre el modelo de Chari, ¿qué agrega el riesgo económico?"

### 10. Ecuación (1) con controles de Chari · Información incremental (2 min)

**Propósito:** responder la primera parte de la pregunta.

**Qué digo:** "Parto del modelo de Chari et al. La fragilidad se mantiene en 0,137. Agregar el
riesgo de cola sube el R² dentro del país de 0,153 a 0,185, y la prueba conjunta resiste el wild
bootstrap: 0,041. Pero en cambios, en proyecciones locales y fuera de la muestra, no aparece. Agrega
en niveles; no anticipa los cambios."

**Cómo leer:** la fila del R², después la tabla de la derecha y las cajas.

**Transición:** "La segunda parte de la pregunta es qué pasa cuando los dos riesgos se dan a la vez.
Primero hay que ver si se dan a la vez."

### 11. Ecuación (2) · Coincidencia y precedencia (2 min 30 s)

**Propósito:** el resultado firme de la tesis.

**Qué digo:** "Ambos riesgos están en su tercil alto en 168 trimestres-país. Por azar esperaría 87.
Si descuento el calendario común, permutando entre países dentro de cada trimestre, espero 141: es
1,2 veces, con p = 0,0002. Pasa en los 13 países. Y la ecuación (2) dice que la fragilidad antecede
al riesgo de cola: 0,405, resiste el wild bootstrap y la exclusión de cada país. Al revés, nada."

**Cómo leer:** la fila de la permutación entre países, luego φ.

**Si me pregunta** *¿no es solo la pandemia?*: "En 2020–22 lo observado casi iguala lo esperado; el
exceso viene de 2015–19 y de 2023–26."

**Transición:** "Coinciden. Entonces, cuando coinciden, ¿el spread sube más que la suma?"

### 12. Ecuaciones (1) y (3) · Amplificación (2 min)

**Propósito:** H3 sin evidencia, dicho con precisión.

**Qué digo:** "La interacción de la (1) es −0,011, con p = 0,89. La prueba directa, la (3), da un
extra de −0,077 cuando los dos riesgos están altos. Lo mismo uno a cuatro trimestres adelante, con
cuartiles y con una forma funcional intermedia. Ninguna es positiva. Es un no rechazo: con los dos
riesgos una d.e. arriba la suma es de unos 28 pb, y descarto un extra de más de un 35 % de eso, no
uno menor."

**Si me pregunta** *¿y el signo negativo?*: "Es de Polonia; sin ella, +0,008. No lo leo como
atenuación (anexo, efecto marginal)."

**Transición:** "Si no se amplifican, ¿hay algo que cambie cuánto pesa cada riesgo? La teoría apunta
a la deuda."

### 13. Ecuación (4) · H4 (2 min)

**Propósito:** la regularidad más clara de la muestra, con sus límites a la vista y en pb.

**Qué digo:** "Con una desviación estándar más de deuda, unos 20 puntos del PIB, el peso del riesgo
de cola sube de 0,043 a 0,054. En puntos básicos: una d.e. de riesgo de cola pasa de unos 23 a unos
29 pb. Pasa Holm en su familia y se mantiene sin cada país. Con el riesgo de cola a un año es más
fuerte: un 70 % más, de 15 a 25 pb. Lo que no resiste: la corrección sobre los ocho preregistros, la
réplica en Hungría y Corea, el instrumento y el modelo de límite fiscal. Por eso digo 'en la
muestra'."

**Cómo leer:** las dos primeras filas, después la caja de interpretación.

**Transición:** "Junto todo en una lámina."

## Cierre (≈ 3 min)

### 14. Conclusiones, política e investigación futura (3 min)

**Propósito:** resultados, implicancias de política y líneas futuras en una sola lámina.

**Qué digo:** "Arriba a la izquierda, los cinco resultados, cada uno con su ecuación. Cada riesgo se
asocia con el spread; con controles solo resiste el riesgo de cola, unos 15 a 17 pb por d.e. Los dos
riesgos coinciden más que por azar y la fragilidad va primero: es lo firme. Cuando coinciden no se
amplifican. Con más deuda el riesgo de cola pesa más, solo en la muestra. Y las otras condiciones no
cambian la transmisión.

Para la política: los dos riesgos tienden a agravarse a la vez, así que vigilarlos en el mismo
tablero se justifica. Pero los datos no muestran que juntos cuesten más que la suma: una exigencia
adicional por la simultaneidad no tiene base aquí. Donde la deuda es alta, el riesgo de cola merece
más atención.

Lo que falta: más economías con EMBI directo y un GaR mensual, variación exógena en los bancos y más
eventos de respaldo externo."

**Cierre:** "Los dos riesgos llegan juntos, pero no se potencian."

\newpage

# 3. Anexo: qué lámina abrir ante cada pregunta

| Si pregunta por… | Abro |
|---|---|
| Sin los trimestres de crisis | H1 y H2 sin los trimestres de crisis (Panel B) |
| Reservas, respaldo, participación extranjera, doom loop | Otros moderadores (ecuación 5) |
| Cómo se construye JLoss / el GaR | Construcción de JLoss; Construcción del GaR |
| Errores estándar y escala de evidencia | Inferencia; Inferencia calibrada por simulación |
| Por qué no es una elasticidad común | La réplica y sus límites |
| Si la fragilidad va antes que el spread | La fragilidad y el spread se mueven en el mismo trimestre |
| Polonia y el riesgo de cola | El coeficiente del riesgo de cola depende de Polonia |
| Cuánta amplificación se descarta | Las bandas |
| Causalidad, retroalimentación | ¿Efecto o persistencia? |
| Crisis, Backstop / EMstress | Batería con vector de crisis; Lectura |
| Respaldo externo por país | Estrés conjunto y respaldo externo por país |
| Heterogeneidad, núcleo de 11 | Heterogeneidad por economía |
| Quién tiene la deuda | Participación extranjera |
| Reservas | Las reservas bajo escrutinio |
| Por qué el modelo no explica H4 | Un modelo de límite fiscal |
| Todo junto, con su grado de evidencia | Hallazgos y su grado de evidencia |
| Preregistros | Pruebas preregistradas; Preguntas de portafolio |
| Muestra, CDS, Argentina, logaritmos | Robustez; Logaritmos vs. niveles; Argentina |
| Limitaciones | Limitaciones |

# 4. Revisión de las pruebas (pedido del 6-11)

- **Magnitudes recalculadas** a partir del panel (`Panel_bloomberg_embiext.csv`) con la misma función
  de estimación de `p13_figuras_paper.py`: β2 = 0,0324 (N = 765) y 0,0281 con seis controles
  (N = 649), d.e. dentro del país del riesgo de cola 3,10 y 3,17 pp, spread medio geométrico 172–173
  pb, mediana 177 pb. Coinciden con las cifras canónicas (sección 17.4 de `NUMEROS_CANONICOS_BBG.md`).
- **Panel C, control por control:** ningún control solo elimina la fragilidad (solo deuda 0,077,
  p = 0,029; solo saldo fiscal 0,056, p = 0,12; solo tipo de cambio real 0,059, p = 0,18). Al quitar
  un control de los seis, la fragilidad solo se recupera en parte sin el tipo de cambio real (0,064,
  p = 0,13). El riesgo de cola se mantiene en casi todas las variantes (0,026–0,041).
- **Pendiente:** hablar con R. Fischer sobre la presentación antes del viernes, y llevar el
  visualizador para revisarlo con el profesor.
