---
title: "Predefensa con el profesor guía"
subtitle: "Guion lámina por lámina: ecuación, panel y conclusión"
---

*La exposición tiene 18 láminas y dura unos 30–35 minutos. El resto de la hora es para preguntas. El
anexo (29 láminas) no se expone: se abre cuando una pregunta lo pide.*

**Antes de entrar**

- [ ] La presentación en PDF, en el computador y en un pendrive.
- [ ] La tesis en PDF abierta, por si pide una tabla completa.
- [ ] Cronómetro visible. Ensayar una vez en voz alta.
- [ ] Saber de memoria la sección 1.

**Cómo está armado.** Primero numero las cinco ecuaciones. Después cada lámina de resultados tiene
una franja arriba con tres cosas: la ecuación que uso, el panel que muestro y lo que concluyo de ese
panel. Debajo va la tabla y una línea con la razón. El relato avanza de una conclusión a la pregunta
siguiente:

> ¿Cada riesgo se asocia con el spread? → ¿Qué agrega el riesgo económico? → ¿Coinciden? → Si
> coinciden, ¿se amplifican? → ¿Qué cambia la transmisión: la deuda, otra cosa?

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
| (5) | (1) más un moderador M y sus productos | otros moderadores | λ1, λ2, λ3 |

**La historia en seis conclusiones**

1. **Cada riesgo se asocia con un spread mayor** (1). La fragilidad replica a Chari et al. con sus
   controles. La evidencia es sugerente: con el wild bootstrap, p = 0,33 y 0,20.
2. **El riesgo económico agrega poco:** 2–3 % de spread por punto, en niveles. No aparece en cambios
   ni mejora el pronóstico.
3. **Los dos riesgos coinciden** 1,2 veces lo esperado con el calendario común descontado, y la
   fragilidad antecede al riesgo de cola (2). Es el resultado firme.
4. **Cuando coinciden, no hay evidencia de que se amplifiquen** (1, 3). Es un no rechazo: se descarta
   más de un 35 % de la suma, no menos.
5. **Con más deuda, el riesgo de cola pesa más** (4). Es una regularidad de la muestra: ni la réplica
   externa, ni el instrumento, ni el modelo la confirman.
6. **Ninguna otra condición cambia la transmisión** (5).

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
| Panel B, sin crisis | β1 0,087; β2 0,050; β3 0,005 |
| Panel C, seis controles | β1 −0,008 (p = 0,86); β2 0,028 (p = 0,046); mismas 649 obs. sin controles: 0,107 |
| Información incremental (N = 662) | β2 0,037; conjunta wild 0,041; R² 0,153 → 0,185 → 0,194 |
| Lo que no pasa | cambios a 4 trimestres 0,004 (0,13); proyecciones locales 0 de 9; fuera de muestra +3 % de error |
| Simultaneidad | 168 obs. (22,0 %); 87 bajo independencia (1,9 veces); 140,9 con el calendario común (1,2 veces; p = 0,0002); 13 de 13 |
| Precedencia | φ = 0,405 (wild 0,024); sin cada país 0,32–0,47; la inversa −0,006 |
| Concentración | 129 de las 168 coincidencias desde 2020 |
| Amplificación | β3 −0,011 (wild 0,89); a3 −0,077 (wild 0,23); TOST descarta > 35 % |
| H4, preregistro 1 | ψ = +0,011 por d.e. de deuda (0,043 → 0,054); Holm 0,029; 13 de 13 |
| H4, preregistro 2 | riesgo de cola a un año 0,047 (Holm 0,018); ψ = +0,033 (+70 %) |
| H4, en contra | 23 hipótesis: Holm 0,13 y 0,31; Hungría y Corea 0,22 (potencia 5 %); instrumento F 9,7 |
| Moderadores | participación extranjera Holm 1,00; respaldo −0,004 (wild 0,90); reservas −0,247 (wild 0,08; preregistrada Holm 0,29); doom loop −0,053 |

**Vocabulario:** *amplificación* o *simultaneidad*, nunca "multiplicidad"; efectos *aditivos*;
*riesgo financiero* (JLoss) y *riesgo económico* (GaR). Son asociaciones: evito "reduce", "protege"
y "efecto de".

**Lo que NO debo decir:**

- Que las métricas son mías. JLoss es de Chari et al. (2024); el GaR, de Adrian et al. (2019) y el
  CEMLA. Mío es construir las series y cruzarlas.
- Que la amplificación "está descartada". No la encuentro, y se descarta solo una grande.
- Que la deuda "explica" la transmisión. Es una regularidad de la muestra.
- Que las reservas "atenúan" o "protegen".

\newpage

# 2. Guion lámina por lámina (≈ 32 min)

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

**Qué digo:** "Cuatro hipótesis. H1 y H2: cada riesgo eleva el spread. H3: juntos lo elevan más que
la suma. H4: con más deuda, el riesgo de cola pesa más."

**Transición:** "Antes de las ecuaciones, las dos series."

### 5. Las dos variables en el tiempo (1 min)

**Qué digo:** "Mediana y rango intercuartil entre los 13 países. Lo sombreado son la crisis
financiera global, el estrés emergente de 2015–16 y la pandemia."

**Cómo leer:** las tres franjas grises. No comento nada más: la simultaneidad la muestro con la
ecuación (2).

## Especificaciones (≈ 4 min)

### 6. Especificaciones (1)–(3) (2 min)

**Propósito:** que cada hipótesis quede atada a un coeficiente.

**Qué digo:** "La ecuación (1) es la principal: el logaritmo del spread sobre la fragilidad, el
riesgo de cola y su producto, todos rezagados un trimestre, con efectos fijos de país y de tiempo.
β1 es H1, β2 es H2 y β3 es H3. La estimo en tres paneles: completa, sin crisis y con controles. La
(2) pregunta qué riesgo antecede al otro. La (3) contrasta H3 de forma directa: indicadores de
riesgo alto y su producto."

**Si me pregunta** *¿por qué logaritmos?*: "La prueba PE los prefiere, y JLoss es ordinal (anexo,
logaritmos vs. niveles)."

### 7. Especificaciones (4)–(5) e inferencia (2 min)

**Qué digo:** "La (4) es H4: la principal más la deuda de cuatro trimestres antes y su producto con
el riesgo de cola. Está preregistrada dos veces, con el riesgo de cola a un trimestre y a un año. La
(5) agrega otro moderador: participación extranjera, respaldo, reservas o deuda en moneda
extranjera. Con 13 países, el criterio es el wild bootstrap por país; la escala de abajo ordena
todo lo que viene."

**Transición:** "Parto por la ecuación (1)."

## Resultados (≈ 17 min)

### 8. Ecuación (1) · Panel A (2 min 30 s)

**Propósito:** H1 y H2 tienen signo positivo, pero la evidencia es sugerente.

**Qué digo:** "En la muestra completa, la fragilidad y el riesgo de cola son positivos en todas las
columnas. La interacción es −0,011. Con el wild bootstrap, ninguno resiste: 0,33, 0,20 y 0,89. Por
eso digo 'sugerente'."

**Cómo leer:** la columna Ref., después la fila de la interacción.

**Si me pregunta** *¿depende de un país?*: "Sí: Turquía en la fragilidad y Polonia en el riesgo de
cola (anexo, pendientes por país y Polonia)."

### 9. Ecuación (1) · Panel B (1 min)

**Qué digo:** "Sin los trimestres de crisis, el patrón es el mismo: 0,087, 0,050 y una interacción
de 0,005. No son las crisis las que lo producen."

### 10. Ecuación (1) · Panel C (1 min 30 s)

**Qué digo:** "Con los seis controles domésticos, la fragilidad cae a −0,008 y el riesgo de cola
se mantiene en 0,028. No es la muestra: con las mismas 649 observaciones y sin controles, la
fragilidad da 0,107."

**Si me pregunta** *¿entonces no replicas a Chari?*: "Con sus controles sí: entre 0,107 y 0,164. Con
los míos no. Varios de esos controles son canales del propio mecanismo."

**Transición:** "Ahora, sobre el modelo de Chari, ¿qué agrega el riesgo económico?"

### 11. Ecuación (1) con controles de Chari · Información incremental (2 min)

**Propósito:** responder la primera parte de la pregunta.

**Qué digo:** "Parto del modelo de Chari et al. La fragilidad se mantiene en 0,137. Agregar el
riesgo de cola sube el R² dentro del país de 0,153 a 0,185, y la prueba conjunta resiste el wild
bootstrap: 0,041. Pero en cambios, en proyecciones locales y fuera de la muestra, no aparece. Agrega
en niveles; no mejora el pronóstico."

**Cómo leer:** la fila del R², después la tabla de la derecha.

**Transición:** "La segunda parte de la pregunta es qué pasa cuando los dos riesgos se dan a la vez.
Primero hay que ver si se dan a la vez."

### 12. Ecuación (2) · Coincidencia y precedencia (2 min 30 s)

**Propósito:** el resultado firme de la tesis.

**Qué digo:** "Ambos riesgos están en su tercil alto en 168 trimestres-país. Por azar esperaría 87.
Si descuento el calendario común, permutando entre países dentro de cada trimestre, espero 141: es
1,2 veces, con p = 0,0002. Pasa en los 13 países. Y la ecuación (2) dice que la fragilidad antecede
al riesgo de cola: 0,405, resiste el wild bootstrap y la exclusión de cada país. Al revés, nada. Un
dato más: 129 de las 168 coincidencias son de 2020 en adelante."

**Cómo leer:** la fila de la permutación entre países, luego φ.

**Si me pregunta** *¿no es solo la pandemia?*: "En 2020–22 lo observado casi iguala lo esperado; el
exceso viene de 2015–19 y de 2023–26."

**Transición:** "Coinciden. Entonces, cuando coinciden, ¿el spread sube más que la suma?"

### 13. Ecuaciones (1) y (3) · Amplificación (2 min 30 s)

**Propósito:** H3 sin evidencia, dicho con precisión.

**Qué digo:** "La interacción de la (1) es −0,011, con p = 0,89. La prueba directa, la (3), da un
extra de −0,077 cuando los dos riesgos están altos. Lo mismo uno a cuatro trimestres adelante, con
cuartiles y con una forma funcional intermedia. Ninguna es positiva. Es un no rechazo: descarto una
amplificación de más de un 35 % de la suma, no una menor. Abajo dejo las dos señales en contra.
Ninguna resiste en logaritmos."

**Si me pregunta** *¿y el signo negativo?*: "Es de Polonia; sin ella, +0,008. No lo leo como
atenuación (anexo, efecto marginal)."

**Transición:** "Si no se amplifican, ¿hay algo que cambie cuánto pesa cada riesgo? La teoría apunta
a la deuda."

### 14. Ecuación (4) · H4 (2 min 30 s)

**Propósito:** la regularidad más clara de la muestra, con sus límites a la vista.

**Qué digo:** "Con una desviación estándar más de deuda, el peso del riesgo de cola sube de 0,043 a
0,054. Pasa Holm en su familia y se mantiene sin cada país. Con el riesgo de cola a un año es más
fuerte: +0,033, un 70 % más. Ahora lo que no resiste: la corrección sobre los ocho preregistros, la
réplica en Hungría y Corea, el instrumento y el modelo de límite fiscal. Por eso digo 'en la
muestra'."

**Cómo leer:** las dos primeras filas, después las tres últimas.

**Transición:** "¿Y las otras condiciones?"

### 15. Ecuación (5) · Otros moderadores (1 min 30 s)

**Qué digo:** "Participación extranjera, respaldo externo, reservas, doom loop, deuda en moneda
extranjera. Ninguna pasa el criterio exigente. Las reservas son exploratorias: dependen de Polonia y
la versión preregistrada no las confirma. Con 13 países es ausencia de evidencia, no evidencia de un
cero."

**Transición:** "Junto todo."

## Cierre (≈ 4 min)

### 16. Conclusiones (2 min 30 s)

**Propósito:** que el resumen siga el mismo hilo de los resultados.

**Qué digo:** "Seis conclusiones, cada una con su ecuación. Cada riesgo se asocia con el spread,
aunque la evidencia es sugerente. El riesgo económico agrega poco, y solo en niveles. Los dos riesgos
coinciden más que por azar, y la fragilidad va primero: es lo firme. Cuando coinciden no se
amplifican. Con más deuda el riesgo de cola pesa más, solo en la muestra. Y ninguna otra condición
cambia la transmisión."

**Lo que tengo que subrayar:** por qué importa. "Esto le sirve a quien vigila la estabilidad
financiera y la deuda. Los dos riesgos tienden a agravarse a la vez, así que mirarlos por separado
subestima cuándo llegan juntos. Pero los datos no muestran que juntos cuesten más que la suma. Una
regla que pida más capital o más reservas por la simultaneidad no tiene base aquí. Lo que sí tiene
base es vigilarlos en el mismo tablero, con más atención donde hay más deuda."

### 17. La frase (30 s)

**Qué digo:** la leo y hago una pausa. "Los dos riesgos llegan juntos, pero no se potencian. Vigilarlos
juntos se justifica; una exigencia adicional por su simultaneidad, no."

**Lo que tengo que subrayar:** es la respuesta a la pregunta de la lámina 2. La primera mitad viene de
la ecuación (2); la segunda, de la (1) y la (3).

### 18. Trabajos futuros (1 min)

**Qué digo:** "Lo que falta: más economías con EMBI directo, frecuencia diaria y un GaR mensual, la
distancia al incumplimiento como medida principal, variación exógena en los bancos y más eventos de
respaldo."

\newpage

# 3. Anexo: qué lámina abrir ante cada pregunta

| Si pregunta por… | Abro |
|---|---|
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
