---
title: "Predefensa con el profesor guía"
subtitle: "Guion detallado lámina por lámina, preguntas probables y decisiones a pedir — 13 de octubre de 2026"
---

*Presento la defensa completa al profesor guía como si fuera la predefensa. Tengo **una hora**:
unos **50 minutos de exposición** y el resto para preguntas. Él va a interrumpir y probar la
econometría; el objetivo es exponer con claridad y salir con decisiones.*

**Antes de entrar**

- [ ] La presentación nueva (61 páginas: 41 de exposición y 20 de respaldo) en PDF, en el computador
      y en un pendrive.
- [ ] La tesis en PDF abierta, por si pide una tabla completa, y esta guía impresa.
- [ ] Cronómetro visible. Ensayar una vez en voz alta midiendo los tiempos por sección.
- [ ] Saber de memoria la sección 1.

**Cómo usar este guion.** Cada lámina tiene hasta cinco partes:

- **Propósito:** qué debe quedar claro al terminarla.
- **Qué digo:** el texto, en primera persona. No hay que leerlo palabra por palabra.
- **Cómo leer:** en las tablas y figuras, adónde señalar.
- **Transición:** la frase que lleva a la lámina siguiente.
- **Si me pregunta:** la respuesta corta a la pregunta más probable en ese punto.

\newpage

# 1. Lo que tengo que saber de memoria

**La pregunta propia de la tesis:** sobre la fragilidad bancaria que ya documentan Chari et al.
(2024), ¿qué agrega el riesgo económico doméstico, y qué pasa cuando los dos riesgos se dan a la vez?

**La historia en cuatro conclusiones y una réplica**

1. **La simultaneidad es un hecho** (firme): los dos riesgos domésticos coinciden 1,9 veces lo
   esperado por azar, en los 13 países. Hay indicios (sugerente) de que la fragilidad bancaria
   antecede al deterioro de la cola del crecimiento, y no al revés.
2. **Cuando coinciden, no hay evidencia de que se amplifiquen**: sus asociaciones con el spread se
   suman. Siempre con la salvedad: los datos no permiten descartar un extra de hasta un 30–40 % de
   la suma.
3. **El riesgo económico agrega poco** a lo que explica la fragilidad (sugerente, solo en niveles):
   0,02–0,03 por punto; no mejora el pronóstico ni aparece en los cambios.
4. **Ninguna condición estudiada** ---resiliencia, respaldo externo, quién tiene la deuda---
   modifica la transmisión de forma demostrable.
5. **Réplica, no conclusión:** la asociación fragilidad–spread replica a Chari et al. con sus
   controles, pero no es una elasticidad común ni hay precedencia temporal.

**La escala de evidencia (una sola):** *firme* = resiste el wild bootstrap o la permutación y no
depende de un país; *sugerente* = solo Driscoll–Kraay, o depende de un país; *exploratorio* = no
estaba preespecificado y no pasa la corrección por comparaciones múltiples; *no hay evidencia*.

**Las cifras**

| Qué | Cifra |
|---|---|
| Muestra | 13 economías, 2004Q2–2026Q2, N = 765 (14 y 799 con Argentina) |
| Simultaneidad | 168 obs. (22,0 %) frente a 87; 1,9 veces; 13 de 13 países |
| Coincidencia neta del calendario común | 168 frente a 132 esperadas (1,3 veces) |
| Permutación por bloques | media 85,7; p = 0,001; fuera de crisis 108 frente a 59,3 (p = 0,001) |
| Episodios conjuntos | 62; duran 2,71 trimestres frente a 1,85 (p = 0,003) |
| Fragilidad(t−1) → riesgo de cola(t) | 0,405 (Driscoll–Kraay 0,009; wild 0,024); al revés −0,006 |
| Salvedad de la simultaneidad | 129 de 168 desde 2020; 35,7 % en crisis (14,2 % de la muestra) |
| Interacción (β3) | −0,011 (Driscoll–Kraay 0,11; wild 0,89); sin Polonia +0,008 |
| Estrés conjunto | +0,091, +0,186 y extra −0,077 (wild 0,23) |
| Bandas | suma +16,4 % (28,4 pb); extra máximo +0,5 / +2,9 / +5,3 puntos (3 % / 16 % / 29 %); en pb +11 (39 %) |
| Riesgo de cola sobre el modelo de Chari (N = 662) | 0,037 (wild 0,066); conjunta wild 0,041; R² 0,153 → 0,185 → 0,194 |
| Riesgo de cola: lo que no pasa | cambios a 4 trimestres 0,004; proyecciones locales 0 de 9; fuera de muestra +3 % de error; sin Polonia 0,007 (p = 0,51) |
| Riesgo de cola: a favor | 10 de 13 pendientes positivas; promedio de grupo 0,033 (p = 0,004); ponderada 0,023 |
| Participación extranjera (preespecificada) | +0,037 / −0,001 / −0,006; wild 0,41 / 0,92 / 0,48; Holm 1,00 |
| Respaldo externo por país | interacción × acceso −0,004 (wild 0,90); en crisis +0,045 (wild 0,22) |
| Reservas × fragilidad | −0,247 (wild 0,08); −11,3 pb (wild 0,04); Holm 0,40 / 0,22; sin Polonia −0,084 |
| Resiliencia (índice) | directa −0,153 (cluster 0,38); × cola fuera de crisis −0,024, en crisis −0,001 |
| Núcleo de 11, sin crisis | +0,034 (wild 0,015) y +1,8 pb (wild 0,002): exploratorio |
| Vector de crisis (CM4, col. 1) | Backstop −0,015; EMstress +0,026; con Holm 0,12 y 0,24 |
| Réplica de Chari | 0,099 (Driscoll–Kraay 0,003; wild 0,33); 0,107–0,164 con sus controles; CDS 0,206 |
| Límites de la réplica | pendientes −0,84 a +0,97; sin Turquía 0,034 (p = 0,43); con controles domésticos −0,008 |
| Piso de JLoss | 2,16; 23,7 % de las obs. a menos de 2 % del piso |
| Fechas | cierre a cierre 0,025 (wild 0,21); mismo trimestre 0,037 (wild 0,008) |
| Retroalimentación | spread → JLoss 0,17 (p = 0,009); sesgo simulado +0,066 (dato 0,099) y +0,022 (dato 0,032) |
| Wild bootstrap en niveles (β1 / β2 / β3) | 0,33 / 0,20 / 0,89 |
| Simulación, tamaño en niveles | Driscoll–Kraay 28 % / 21 %; wild 6 % / 7 %; potencia del wild 35 % / 67 % |

**Regla de lectura de la inferencia:** en niveles, resistir el wild bootstrap es necesario, no
suficiente (no protege del sesgo de retroalimentación). Solo Driscoll–Kraay rechaza una hipótesis
nula cierta entre el 20 % y el 30 % de las veces.

**Vocabulario (lo corrigió el profesor guía):** *amplificación* o *simultaneidad*, nunca
"multiplicidad"; efectos *aditivos*; *riesgo financiero* (JLoss) y *riesgo económico* (GaR). Son
asociaciones: evito "reduce", "atenúa", "protege", "anticipa" y "efecto de".

**Lo que NO debo decir:**

- Que las métricas son mías (mía es la construcción de las series y su cruce).
- Que la fragilidad bancaria es mi hallazgo, ni "lo más firme".
- Que la amplificación "está descartada" (es un no rechazo).
- Que "el cambio de la fragilidad anticipa el spread" o que "el spread responde al cambio y no al
  nivel" (era un artefacto de fechas).
- Que las reservas "atenúan" o "protegen", o que son el resultado de moderación más robusto.
- "Deuda local profunda" para Polonia; que la amplificación "aparece sin respaldo externo".
- Que el riesgo económico "importa por sí mismo" o "sobrevive".

\newpage

# 2. Guion lámina por lámina (≈ 50 min)

## Motivación y pregunta (≈ 8 min)

### 1. Portada (20 s)
**Qué digo:** "Buenos días, profesor. Presento *Fragilidad bancaria sistémica y riesgo de cola del
crecimiento: determinantes del spread soberano en economías emergentes*. Lo voy a exponer como si
fuera la defensa, y le agradecería que me interrumpa cuando quiera."

### 2. Índice (20 s)
**Qué digo:** "Son cinco partes: motivación, medición y estrategia, datos, resultados y
conclusiones. Los resultados parten de la réplica de Chari y coautores, que es mi punto de partida,
y después van las cuatro conclusiones propias."

### 3. Qué es el spread y sus dos pilares (2 min 30 s)
**Propósito:** definir el spread, situar la tesis entre las dos grandes explicaciones de la
literatura y mostrar la brecha que llena.

**Qué digo (versión para exponer):** "Primero, qué es el spread soberano: es la diferencia entre lo
que rinde la deuda en dólares de un gobierno emergente y lo que rinden los bonos del Tesoro de
Estados Unidos de plazo similar. Es la prima que exige el mercado por el riesgo de que ese país no
pague, y la mido con el EMBI Global Diversified de J.P. Morgan, en puntos básicos.

La literatura explica esa prima con dos pilares. El primero son los **fundamentos domésticos**:
Edwards, Hilscher y Nosbusch, Uribe y Yue. El segundo son los **factores globales**: Calvo,
Leiderman y Reinhart; Longstaff y coautores; Miranda-Agrippino y Rey.

Yo mido el pilar doméstico con dos riesgos de cola: uno **financiero**, la fragilidad bancaria, con
JLoss; y uno **económico**, la cola del crecimiento, con el GaR. El pilar global lo absorbo con
efectos fijos de tiempo. Y la brecha es esta: Chari y coautores (2024) ya documentan que la
fragilidad bancaria se asocia con el spread y la cruzan con factores globales; lo que no se ha
hecho es cruzar simultáneamente los dos riesgos de cola domésticos. Ese cruce es lo que estudio."

**Transición:** "¿Por qué tendrían que relacionarse? Por el mecanismo."

**Si me pregunta por los autores: qué aportó cada uno y con qué método**

*Pilar 1: fundamentos domésticos (factores pull)*

- **Edwards (1984), *American Economic Review*.**
  - *Pregunta:* ¿qué determina el precio al que los países en desarrollo se endeudan en el
    exterior?
  - *Método:* un modelo de riesgo de incumplimiento en el que el prestamista cobra una prima según
    la probabilidad de que el país no pague. Lo lleva a los datos regresando el logaritmo del spread
    de los préstamos bancarios a gobiernos de países en desarrollo, sobre la tasa LIBOR, entre 1976 y
    1980, contra indicadores macroeconómicos de cada país: deuda/PIB, servicio de la deuda,
    reservas, inversión y cuenta corriente.
  - *Hallazgo:* más deuda eleva el spread; más reservas e inversión lo reducen. Fue de los primeros
    en mostrar que el mercado distingue a los deudores según sus fundamentos.
  - *Conexión conmigo:* fundó la idea de que el spread mide riesgo de incumplimiento y depende de
    variables domésticas; mis controles (deuda, reservas, cuenta corriente) vienen de esta tradición.
- **Hilscher y Nosbusch (2010), *Review of Finance*.**
  - *Pregunta:* ¿cuánto de la variación de los spreads emergentes explican los fundamentos
    macroeconómicos?
  - *Método:* un modelo estructural tipo Merton, en el que el país incumple si su capacidad de pago
    cae bajo un umbral, de modo que importan tanto el nivel como la volatilidad de los fundamentos.
    Lo estiman con un panel de spreads EMBI de economías emergentes entre mediados de los noventa y
    mediados de los dos mil.
  - *Hallazgo:* los fundamentos explican una parte importante de los spreads, y la **volatilidad
    de los términos de intercambio** es especialmente relevante, más allá de su nivel.
  - *Conexión conmigo:* muestra que el **riesgo** de los fundamentos, no solo su nivel, se cobra en
    el spread. Es la misma lógica del GaR: lo que importa es la cola de la distribución del
    crecimiento, no su promedio.
- **Uribe y Yue (2006), *Journal of International Economics*.**
  - *Pregunta:* ¿el spread mueve al ciclo económico de los emergentes, o el ciclo mueve al spread?
  - *Método:* un VAR de panel con datos trimestrales de siete emergentes (entre ellos Argentina,
    Brasil, México, Perú y Sudáfrica) desde mediados de los noventa, con la tasa de interés de
    EE.UU., el spread del país, el producto, la inversión y la balanza comercial, identificado con un
    orden recursivo. Lo complementan con un modelo teórico de economía pequeña y abierta.
  - *Hallazgo:* la relación va en **ambas direcciones**. Los spreads reaccionan a las condiciones
    domésticas y, a la vez, sus choques afectan la actividad; además amplifican los choques de la
    tasa de EE.UU. Los choques de la tasa externa explican cerca de una quinta parte de los ciclos.
  - *Conexión conmigo:* adelanta mi principal problema de identificación: el spread y sus
    determinantes se retroalimentan. Por eso rezago los regresores y pruebo el canal inverso.

*Pilar 2: factores globales (factores push)*

- **Calvo, Leiderman y Reinhart (1996), *Journal of Economic Perspectives*** (sobre su trabajo de
  1993 en el *IMF Staff Papers*).
  - *Pregunta:* ¿por qué llegaron tantos capitales a América Latina y Asia a comienzos de los
    noventa?
  - *Método:* análisis del co-movimiento entre países. En el trabajo de 1993 extraen componentes
    principales de las reservas y los tipos de cambio reales de países latinoamericanos y muestran
    que el factor común se mueve con variables de EE.UU., como las tasas de interés. El artículo de
    1996 sintetiza esa evidencia.
  - *Hallazgo:* gran parte de los flujos se explica por factores **externos (push)** ---la caída de
    las tasas en EE.UU. y la recesión en los países desarrollados---, no solo por las reformas
    domésticas (pull). Advierten que lo que entra por factores externos puede salir de golpe.
  - *Conexión conmigo:* es el origen de la distinción push/pull que ordena mi lámina.
- **Longstaff, Pan, Pedersen y Singleton (2011), *American Economic Journal: Macroeconomics*.**
  - *Pregunta:* ¿cuán "soberano" es realmente el riesgo de crédito soberano?
  - *Método:* datos mensuales de CDS soberanos de 26 países entre 2000 y 2010. Usan componentes
    principales para medir cuánto se mueven juntos, regresiones contra variables locales (bolsa,
    tipo de cambio, reservas) y globales (bolsa de EE.UU., VIX, spreads de alto rendimiento), y un
    modelo de valoración que separa la probabilidad de incumplimiento de la prima de riesgo.
  - *Hallazgo:* el riesgo soberano es **mayoritariamente común**: un solo componente explica la
    mayor parte de la variación, y las variables globales explican más que las locales. Una parte
    importante del spread es prima de riesgo y no probabilidad de incumplimiento.
  - *Conexión conmigo:* justifica los efectos fijos de tiempo, que absorben todo ese componente
    común; mi variación identificadora es la doméstica, dentro de cada país.
- **Miranda-Agrippino y Rey (2022), *Handbook of International Economics*** (síntesis de su
  trabajo de 2020 en la *Review of Economic Studies*).
  - *Pregunta:* ¿existe un ciclo financiero global y qué lo mueve?
  - *Método:* un modelo de factores dinámicos sobre cientos de precios de activos riesgosos de todo
    el mundo para extraer un factor común, y un VAR bayesiano para estimar cómo responde ese factor
    a choques de política monetaria de EE.UU. identificados con alta frecuencia.
  - *Hallazgo:* un solo **factor global** explica una fracción importante de los precios de riesgo
    del mundo, y la política monetaria de la Fed lo mueve: cuando la Fed endurece, caen los precios
    de riesgo, se contrae el crédito y suben las primas.
  - *Conexión conmigo:* es la versión moderna del pilar global y la razón por la que no basta con
    controlar el VIX: los efectos fijos de tiempo capturan todo el ciclo común.

*La brecha*

- **Chari, Garcés, Martínez y Valenzuela (2024), *Journal of Financial Stability*.**
  - *Pregunta:* ¿la fragilidad del sistema bancario se traslada al spread soberano de los
    emergentes?
  - *Método:* construyen JLoss con datos de mercado de los bancos: probabilidades de incumplimiento
    tipo Merton agregadas por punto de silla. Estiman regresiones de panel del spread EMBI con JLoss
    rezagado y controles que agregan progresivamente, y estudian cómo la relación cambia con los
    factores financieros globales.
  - *Hallazgo:* mayor fragilidad bancaria se asocia con spreads más altos, y esa relación depende
    del entorno financiero global.
  - *Conexión conmigo:* es el trabajo más cercano. Uso su métrica y su estructura de batería, y
    replico su asociación con datos construidos de forma independiente. La diferencia: ellos cruzan
    la fragilidad con factores **globales**; yo la cruzo con el riesgo de cola **doméstico** del
    crecimiento. Ese cruce es la brecha que lleno.

**Si me pregunta cómo se relacionan los dos pilares:** no compiten; se complementan. Los factores
globales mueven a todos los emergentes juntos, y yo los absorbo con efectos fijos de tiempo. Lo que
queda es la variación doméstica, que es justamente donde operan la fragilidad bancaria y el riesgo
de cola de cada país.

**Si me pregunta por qué no incluyo el VIX:** los efectos fijos de tiempo absorben todo choque común,
incluido el VIX; en la réplica de Chari los incluyo explícitamente y el resultado no cambia.

*Nota para mí:* si pide cifras exactas de un paper (coeficientes, porcentajes de varianza), decir
que lo verifico en el original en vez de improvisar.

### 4. El mecanismo: un triángulo y el balance de fuerzas (2 min)
**Propósito:** que se entienda que los dos riesgos se relacionan entre sí y que ambos llegan al
spread, y anticipar el problema de identificación.

**Cómo leer:** primero la línea de arriba (sin flechas), después las dos flechas azules y al final
la punteada.

**Qué digo:** "El mecanismo es un triángulo, no una secuencia. Los dos riesgos se relacionan entre
sí: un sistema bancario frágil da menos crédito y eso deprime el crecimiento ---el acelerador
financiero de Bernanke, Gertler y Gilchrist---, y un crecimiento débil deteriora a los bancos. Y
ambos se trasladan al spread: la fragilidad, como rescate esperado, que es un pasivo contingente del
fisco; la cola del crecimiento, por la capacidad fiscal. A la derecha: qué podría contener esa
transmisión. Las reservas, que son la capacidad del banco central; el respaldo externo, es decir un
swap de la Reserva Federal o una línea del FMI; y quién tiene la deuda. Las tres las medí y las
contrasté como moderadores. La flecha punteada es la retroalimentación: un spread más alto daña a
los bancos. Por eso hablo de asociaciones, no de causalidad."

**Transición:** "Con esto, la pregunta."

**Si me pregunta** por el acelerador financiero: Bernanke, Gertler y Gilchrist (1996) muestran que
el deterioro de los balances encarece el financiamiento y contrae el crédito, lo que amplifica los
choques a la actividad. No estimo esa relación de forma estructural; encuentro un indicio
compatible con ella (lámina 23).

**Cambio respecto del 9 de octubre:** antes decía que el respaldo "no entra como regresor". Ahora
se mide y se contrasta.

### 5. Pregunta e hipótesis (1 min 15 s)
**Qué digo:** "La pregunta: sobre la fragilidad bancaria que ya documentan Chari y coautores, ¿qué
agrega el riesgo económico doméstico, y qué pasa cuando los dos riesgos se dan a la vez? H1, canal
bancario: la fragilidad bancaria sistémica eleva el spread soberano. H2, canal de crecimiento: un
mayor riesgo de cola del crecimiento eleva el spread soberano. H3, amplificación: la coincidencia de
ambos riesgos eleva el spread más que la suma de las dos asociaciones. Además se contrasta si tres
condiciones ---resiliencia, respaldo externo y quién tiene la deuda--- modifican la transmisión. Un matiz: aditivo en logaritmos es proporcional
en puntos básicos. Esa complementariedad es álgebra de la forma funcional y no la llamo
amplificación; H3 exige una interacción positiva."

**Si me pregunta** de dónde sale la forma proporcional: de un modelo de intensidad de incumplimiento
(Duffie y Singleton, 1999). Si el spread es proporcional a una intensidad que depende de JLoss y de
D de forma multiplicativa, en pb el efecto cruzado es positivo sin necesidad de interacción.

### 6. Objetivos (45 s)
**Qué digo:** "El objetivo general es evaluar la relación conjunta de los dos riesgos con el spread
y si su coincidencia la amplifica. Los específicos son cuatro: construir las series de las dos
métricas, cuantificar la asociación de la fragilidad en puntos básicos y elasticidades, la del
riesgo de cola en puntos básicos, y contrastar la complementariedad. Al final vuelvo a cada uno."

### 7. Qué aporta esta tesis (2 min)
**Propósito:** dejar claro, desde el inicio, qué es propio y qué no.

**Qué digo:** "Quiero ser preciso con el aporte. Las métricas no son mías: JLoss es la de Chari et
al. (2024), y el GaR es el de Adrian, Boyarchenko y Giannone (2019), que implemento con la
plataforma de CEMLA. Y que la fragilidad bancaria importa para el spread ya lo establecen Chari y
coautores: aquí es el punto de partida. El aporte tiene cuatro partes. Uno: la construcción
homogénea y reproducible de las series de las dos métricas para 13 economías, con 113 bancos y un
solo protocolo de Bloomberg. Dos: una réplica independiente de Chari y la delimitación de su
alcance: no es una elasticidad común y no hay precedencia temporal. Tres, lo central: el primer
cruce de la fragilidad bancaria con el riesgo de cola doméstico; documenta que coinciden, que hay
indicios de que la fragilidad antecede al riesgo de cola, que no hay evidencia de que se amplifiquen
y que el riesgo económico agrega poco. Cuatro: una batería de pruebas que muestra qué no se puede
afirmar con 13 países."

**Transición:** "Paso a cómo se construyen las dos medidas."

**Si me pregunta** qué cambié respecto de Chari: la parametrización es la misma; lo que hice fue
reimplementarla, ampliarla a más bancos y economías con una fuente homogénea, y cruzarla con el GaR.

## Medición y estrategia (≈ 8 min)

### 8. Construcción de JLoss (2 min)
**Propósito:** que se entienda qué mide JLoss y por qué entra en logaritmos.

**Cómo leer:** los cuatro pasos en orden; la leyenda de abajo define cada letra.

**Qué digo:** "JLoss es la pérdida conjunta esperada del sistema bancario ante un evento sistémico,
como porcentaje de la exposición. Se construye en cuatro pasos. Uno: la probabilidad de
incumplimiento de cada banco con un modelo de Merton–KMV. Dos: esas probabilidades se condicionan a
un factor sistémico del país ---el retorno bursátil--- con la fórmula de Vasicek. Tres: la
distribución de pérdidas del sistema se agrega por el método de punto de silla. Cuatro: JLoss es la
pérdida esperada más la inesperada al 99 %, sobre la exposición total, con una pérdida en caso de
incumplimiento de 45 %. Un detalle importante: la cota de la malla de pérdidas está activa en el
98 % de los casos, así que JLoss funciona como una medida ordinal y entra en logaritmos."

**Si me pregunta** por el piso: la métrica se amontona en 2,16, que es 0,048 × 0,45 × 100. El 23,7 %
de las observaciones está a menos de 2 % de ese piso (Malasia 60 %, Perú 58 %, Chile 49 %; Brasil,
India y Filipinas, 0 %). En el piso la variable no informa: la asociación es de los episodios fuera
de él (láminas 19 y 56).

### 9. Construcción del GaR (1 min 30 s)
**Qué digo:** "El GaR es el cuantil 5 % de la distribución del crecimiento un trimestre adelante.
Primero construyo un índice de condiciones financieras tipo CISS, con tensión accionaria, de tasas
y cambiaria, en términos reales. Después estimo una regresión cuantílica de panel del crecimiento
futuro sobre el crecimiento actual, el índice financiero sin el componente del VIX, el VIX y un
efecto fijo de país. Lo estimo en pseudo–tiempo real: en cada fecha uso solo la información
disponible hasta ella. En la tesis uso D, que es menos el GaR: mayor D significa una cola más
adversa. La figura muestra Chile: en 2020Q2 el cuantil 5 % cae a −13,4 puntos."

**Si me pregunta** si el GaR es circular con el EMBI: el EMBI no entra al cálculo; el único
componente con forma de spread aporta 0,07 al índice y sin él el GaR correlaciona 0,985 con el
oficial.

### 10. Especificación principal y batería (2 min)
**Propósito:** que quede claro qué es cada coeficiente y qué es cada columna de las tablas.

**Qué digo:** "La especificación principal regresa el logaritmo del EMBI sobre el logaritmo de JLoss
y D, ambos rezagados un trimestre, y su producto, con efectos fijos de país y de tiempo. Beta uno
es la elasticidad a la fragilidad; beta dos, la semielasticidad al riesgo de cola; beta tres, la
interacción: si es positiva, hay amplificación. Siguiendo a Chari, estimo una batería: cuatro
modelos anidados por tres estructuras de efectos fijos y tres muestras: completa, sin crisis y con
controles."

**Si me pregunta** por qué no hay controles en la principal: porque balance fiscal, inflación o tipo
de cambio son plausiblemente canales del mecanismo. Los agrego como robustez (Panel C), y ahí la
fragilidad se diluye: −0,008.

### 11. Especificación con el vector de crisis (1 min 30 s)
**Qué digo:** "Excluir los trimestres de crisis supone que el mecanismo cambia en ellos. La prueba
más exigente es mantener toda la muestra e interactuar con un indicador de crisis. Uso dos
versiones: un vector único ---crisis financiera global, estrés emergente de 2015–16 y pandemia--- y
su descomposición en *Backstop*, la crisis global y la pandemia, con respaldo oficial a escala global (solo Brasil y México tuvieron swap de la Fed), y
*EMstress*, 2015–16, sin un respaldo comparable."

### 12. Inferencia: cómo mido la incertidumbre (1 min 30 s)
**Qué digo:** "Antes de los resultados, cómo mido la incertidumbre, porque ahí se juega cada
conclusión. Las tablas reportan Driscoll–Kraay. Pero con 13 países esos errores son optimistas, así
que cada resultado lo someto a errores agrupados por país y a un wild cluster bootstrap por país.
Con una simulación de 1.000 paneles medí cuánto rechaza de más cada método: en niveles, el criterio
es el wild bootstrap. Para la simultaneidad uso una permutación por bloques, y para las familias de
contrastes, la corrección de Holm. La prueba de la participación extranjera la preespecifiqué. Y
abajo está la escala con la que califico todo: firme, sugerente, exploratorio o no hay evidencia."

**Si me pregunta** por qué hice cada prueba: cada una ataca una amenaza concreta.

- **Canal inverso** (JLoss sobre el spread rezagado): mide la retroalimentación. Resultado: 0,17
  (p = 0,009).
- **Fechas del spread** (promedio frente a cierre): separa la precedencia de la agregación
  temporal. Resultado: de cierre a cierre no hay precedencia (0,025; wild 0,21).
- **Cambios y proyecciones locales:** las pruebas adecuadas a variables lentas. Resultado: el riesgo
  de cola no aparece; la fragilidad, solo en el impacto con el spread promedio.
- **Fuera de muestra:** ¿mejora el pronóstico? No (evidencia débil en cualquier dirección).
- **Wild cluster bootstrap** (pesos de Webb): la corrección estándar con pocos clusters (Cameron,
  Gelbach y Miller, 2008). Resultado en niveles: 0,33 / 0,20 / 0,89.
- **Simulación con retroalimentación:** mide el sesgo que ningún error estándar corrige. Resultado:
  +0,066 y +0,022 sin efecto directo.
- **Permutación:** para la simultaneidad (p = 0,001) y para el episodio *EMstress* (lugar 20 de 51).
- **Regresor generado:** el GaR es una estimación; propagar su error con 500 réplicas no cambia las
  conclusiones.

## Datos (≈ 2 min)

### 13. El panel (1 min)
**Qué digo:** "El panel tiene 13 economías emergentes y 765 observaciones país–trimestre entre
2004 y 2026. Argentina tiene las tres series, pero su GaR se estimó con menos información, así que
la uso como robustez. Corea, Bulgaria y Hungría quedan fuera porque su JLoss no es válido a nivel
país."

### 14. Descriptivos y las dos variables en el tiempo (1 min 30 s)
**Cómo leer:** la línea es la mediana entre países; la banda, el rango entre el 25 % y el 75 %; lo
sombreado, las crisis.

**Qué digo:** "Antes de las regresiones, las series. El spread promedia 198 puntos básicos, y más
del 80 % de la variación de JLoss y del riesgo de cola es dentro de cada país. En la figura, a la
izquierda JLoss y a la derecha el riesgo de cola: son bajas y estables en tiempos normales y saltan
en la crisis financiera global y en la pandemia. Su correlación en el panel es 0,16 ---0,26
descontados los efectos fijos---: aportan información distinta, pero tienden a moverse juntas."

## Resultados I — punto de partida: réplica de Chari et al. y validación del panel (≈ 9 min)

### 15. Réplica · Panel A: muestra completa (2 min)
**Propósito:** mostrar que el panel reproduce la asociación de Chari et al.; no es el hallazgo de la
tesis.

**Cómo leer:** la columna (1) es la referencia: M4 con efectos fijos de país y tiempo.

**Qué digo:** "Parto por la réplica. Cada columna es una regresión; la (1), la referencia, es el
modelo completo con efectos fijos de país y tiempo. La fragilidad tiene una elasticidad de 0,099; el
riesgo de cola, una semielasticidad de 0,032; y la interacción, −0,011, no significativa. La
fragilidad es positiva en las nueve columnas en que aparece. Esto es lo que ya sabíamos por Chari y
coautores; me sirve para validar que mi construcción de las series reproduce su resultado."

**Conclusión directa:** el panel reproduce la asociación fragilidad–spread; la interacción nunca es
significativamente positiva.

### 16. Réplica · Panel B: sin trimestres de crisis (1 min)
**Qué digo:** "Sin la crisis financiera global ni la pandemia el patrón se mantiene: fragilidad
0,087, riesgo de cola 0,050, y la interacción 0,005, indistinguible de cero."

### 17. Réplica · Panel C: con seis controles domésticos (1 min 15 s)
**Qué digo:** "Con los seis controles domésticos ---deuda, balance fiscal, reservas, cuenta
corriente, inflación y tipo de cambio real--- la fragilidad deja de ser significativa: −0,008. El
riesgo de cola se mantiene en 0,028. Es un matiz que debo decir siempre: la réplica vale con los
controles de Chari, no con los seis controles domésticos de mi tesis."

**Si me pregunta** por qué se diluye: los controles son plausiblemente canales (la fragilidad
rezagada los predice), pero no puedo descartar un fundamento común.

### 18. Lectura de la batería (1 min 30 s)
**Qué digo:** "En magnitudes: una elasticidad de 0,10. La unidad correcta es una desviación
estándar dentro del país, que equivale a un 5 % más de spread, unos 13 puntos básicos. Con los
controles de Chari la elasticidad está entre 0,107 y 0,164, y con el CDS en vez del EMBI, 0,206: se
replica con una construcción de datos independiente. Para el riesgo de cola, una desviación
estándar dentro del país es un 10 % más de spread. Dos advertencias: ninguno de los tres coeficientes de la regresión principal resiste el wild bootstrap, y la interacción nunca es significativamente positiva."

**Si me pregunta** por qué no digo "un 1 % más de JLoss": porque JLoss tiene un piso y un cuarto de
las observaciones está pegado a él; la unidad honesta es la desviación estándar dentro del país.

**Transición:** "Ahora, los límites de esa réplica."

### 19. La réplica y sus límites: no es una elasticidad común (1 min 30 s)
**Cómo leer:** cada fila es la pendiente de un país con su intervalo; a la izquierda la fragilidad,
a la derecha el riesgo de cola. La línea negra es el coeficiente agrupado.

**Qué digo:** "Estimé la pendiente país por país. Para la fragilidad van de −0,84 a +0,97; ocho de
trece son positivas; el promedio de grupo es 0,106 y no es significativo, y la homogeneidad se
rechaza. Turquía tiene el 17 % de la variación de la fragilidad y aporta el 70 % del coeficiente:
sin ella cae a 0,034. Y el piso de JLoss: un cuarto de las observaciones está pegado a él y ahí la
métrica no informa. Entonces: la asociación existe en promedio, pero no es una elasticidad común a
las 13 economías."

**Conclusión directa:** se replica a Chari, pero no como una elasticidad común.

### 20. La fragilidad y el spread se mueven en el mismo trimestre (2 min)
**Propósito:** explicar por qué se cayó el titular del 12 de octubre.

**Cómo leer:** la primera fila es la versión de la primera ronda; la segunda, la prueba limpia; la
última, el mismo trimestre.

**Qué digo:** "Esta lámina reemplaza al resultado en primeras diferencias que mostré la vez pasada.
El EMBI del panel es el promedio de los días del trimestre, y JLoss rezagado usa el cierre del
trimestre anterior. Entonces, cuando regreso el cambio del spread promedio sobre el cambio rezagado
de la fragilidad, parte de lo que mido es agregación temporal. La prueba limpia de precedencia es
de cierre a cierre: 0,025, con wild de 0,21; nunca es significativo al excluir un país o un año. La
parte mecánica ---cierre menos promedio del mismo trimestre--- explica la mitad del coeficiente en
logaritmos y el 80 % en puntos básicos. Lo que sí hay es movimiento dentro del mismo trimestre:
0,037, con wild de 0,008. Es robusto en puntos básicos, en 13 de 13 países y 23 de 23 años; en
logaritmos, en 6 de 13 y 13 de 23."

**Conclusión directa:** la fragilidad bancaria y el spread se mueven dentro del mismo trimestre; no
hay evidencia de que la fragilidad anteceda al spread.

**Si me pregunta** por la magnitud: una desviación estándar del cambio de ln JLoss (0,37) se asocia
con un 1,4 % de spread, unos 2,7 puntos básicos.

**Si me pregunta** si importa el nivel o el cambio: los datos no informan. En un modelo de
corrección de errores el multiplicador de largo plazo es −0,146 con un intervalo de −0,79 a 0,50,
que contiene tanto el cero como el coeficiente estático.

## Resultados II — qué agrega el riesgo económico (≈ 4 min)

### 21. Qué agrega el riesgo económico a lo que explica la fragilidad (2 min 30 s)
**Cómo leer:** la tabla va de izquierda a derecha: solo fragilidad, más el riesgo de cola, más la
interacción. La última fila es el R². El bloque rojo son las pruebas que no pasa.

**Qué digo:** "Aquí empieza lo propio. Tomo el modelo al estilo de Chari ---fragilidad rezagada con
sus controles--- y le agrego el riesgo de cola. El coeficiente es 0,037, con wild de 0,066; la
prueba conjunta con la interacción da 0,041, y el R² dentro del país sube de 0,153 a 0,185 (0,194 con la interacción). Hasta
ahí, agrega información. Pero el riesgo de cola es una variable lenta, y no pasa las pruebas
adecuadas a una variable lenta: en cambios a cuatro trimestres es 0,004; en proyecciones locales,
ningún horizonte de nueve; entre países, nada; y fuera de muestra, agregarlo sube el error de
pronóstico un 3 %. Además, el wild bootstrap no protege del sesgo de retroalimentación: en la
simulación sin efecto directo el coeficiente sale +0,022, y el dato es 0,032."

**Conclusión directa:** una asociación modesta, de 0,02 a 0,03 por punto porcentual de riesgo de
cola, que no mejora el pronóstico del spread ni aparece en los cambios. Sugerente.

**Si me pregunta** por el fuera de muestra: ventana expansiva, un trimestre adelante, 540
pronósticos desde 2013Q2; la raíz del error cuadrático medio pasa de 0,1601 a 0,1650 (Clark–West p = 0,83).
El diseño no tiene efectos de tiempo y el GaR no se reestima recursivamente: es evidencia débil.
Ningún modelo le gana al spread rezagado, tampoco con la fragilidad.

### 22. El coeficiente del riesgo de cola depende de Polonia (1 min 30 s)
**Cómo leer:** cada fila es la regresión principal sin un país; a la derecha, el riesgo de cola.

**Qué digo:** "Sin Polonia el coeficiente cae a 0,007, con cualquier medida de la cola. Polonia
aporta el 71 % del coeficiente, y en parte es un efecto del logaritmo de spreads muy bajos: en
2020–22 su spread estuvo entre 15 y 30 puntos básicos. Sin las 36 observaciones bajo 60 puntos, el
coeficiente es 0,018. A su favor: 10 de 13 pendientes por país son positivas; el promedio de grupo
en los diez países de historia larga es 0,033 y significativo; y la media ponderada por precisión
es 0,023 con o sin Polonia."

**Si me pregunta** si el riesgo de cola cuenta dos veces lo financiero: no. Limpio de los factores
globales el coeficiente queda igual, y sin el bloque bursátil del índice financiero, en 0,045
(lámina 58).

## Resultados III — la simultaneidad (≈ 3 min)

### 23. Los dos riesgos coinciden más de lo que explicaría el azar (3 min)
**Propósito:** la primera conclusión, y la más firme.

**Cómo leer:** arriba, "Observado" contra "Por azar". Abajo, las dos filas del rezago cruzado.

**Qué digo:** "Defino que un riesgo está alto cuando está en su tercil superior dentro de cada
país. Los dos están altos a la vez en 168 observaciones, el 22 %; si fueran independientes serían
87: casi el doble. Neto del calendario común (frecuencias de cada año): 132 esperadas, 1,3 veces. Ocurre en los 13 países. Una permutación por bloques, que desplaza el riesgo de
cola dentro de cada país y conserva su persistencia, da 86 en promedio: p de 0,001. Fuera de los
trimestres de crisis, 108 frente a 59. Y los episodios conjuntos duran más: 2,7 trimestres frente a
1,9. Segundo dato: la fragilidad de un trimestre se asocia con más riesgo de cola el siguiente,
0,405 con wild de 0,024, y al revés no. Es coherente con el acelerador financiero, pero lo califico
de sugerente: descansa en un rezago trimestral y equivale a 0,1 desviaciones estándar."

**Conclusión directa:** la simultaneidad es un hecho (firme); la precedencia de la fragilidad sobre
el riesgo de cola es sugerente.

**Lo que debo decir con honestidad:** proviene de pocos episodios comunes: 129 de las 168
observaciones son de 2020 en adelante, y el 35,7 % cae en trimestres de crisis.

**Si me pregunta** si es solo la pandemia: no. En 2020–22 lo observado (29, 17 y 29) casi iguala a
lo esperado (27, 16 y 28); el exceso viene de 2015–19 y de 2023–26.

**Transición:** "Coinciden. ¿Se potencian?"

## Resultados IV — sin amplificación (≈ 4 min)

### 24. Cuando coinciden, no hay evidencia de que se amplifiquen (2 min)
**Cómo leer:** cinco pruebas distintas; en todas la estimación es negativa y el p es alto.

**Qué digo:** "La interacción de la regresión principal es −0,011, con wild de 0,89. Con
indicadores de estrés: la fragilidad alta se asocia con +0,09, la cola alta con +0,19, y las dos a
la vez agregan −0,08, no significativo; lo mismo uno a cuatro trimestres adelante y con cuartiles.
Con una forma funcional intermedia entre logaritmos y niveles, tampoco. El signo negativo es de
Polonia: sin ella la interacción es +0,008; no lo leo como atenuación. Y reporto dos señales
débiles en contra: fuera del piso de JLoss el riesgo de cola pesa 7,5 puntos básicos más, pero solo
con un umbral y no en logaritmos; y en cambios a cuatro trimestres en puntos básicos hay una
interacción positiva, ausente en logaritmos."

**Si me pregunta** qué significa "aditivo" en logaritmos: proporcional en puntos básicos. Es
álgebra de la forma funcional, no un hallazgo.

### 25. Las bandas: cuánta amplificación no se puede descartar (2 min)
**Cómo leer:** la cifra grande es la suma de las dos asociaciones; cada fila de la tabla, el mayor
extra que admite un intervalo de 95 %.

**Qué digo:** "No rechazar no es demostrar, así que calculé cuánta amplificación podría estar
escondida. Con los dos riesgos una desviación estándar sobre su media, la suma de las dos
asociaciones es un 16,4 % de spread, 28 puntos básicos. La interacción estimada resta 2,1 puntos.
El mayor extra que no se puede descartar es 0,5 puntos con Driscoll–Kraay, 2,9 con el wild
bootstrap y 5,3 con errores agrupados por país: un 29 % de la suma. En puntos básicos, 11 sobre 28:
un 39 %. La frase exacta: no hay evidencia de amplificación; los datos no permiten descartar un
extra de hasta un 30 o 40 % de la suma."

**Conclusión directa:** no afirmo que la amplificación esté descartada.

**Si me pregunta** por la estimación en puntos básicos: es positiva, +3 puntos sobre 28, y no
significativa.

## Resultados V — resiliencia de la política económica (≈ 4 min)

### 26. El índice de resiliencia (2 min)
**Cómo leer:** la fila "fuera de crisis" contra la fila "en crisis"; después la resiliencia previa
con su p de wild bootstrap.

**Qué digo:** "Construí un índice de resiliencia con deuda, balance fiscal y reservas. Más
resiliencia, menor spread; y fuera de las crisis el coeficiente del riesgo de cola es menor donde
hay más resiliencia, y en las crisis no. Pero eso solo pasa con Driscoll–Kraay; con errores
agrupados por país el p es 0,38: sugerente. La analogía del seguro ---paga menos prima el mejor
resguardado, salvo cuando el choque les pega a todos--- queda como lectura, no como hallazgo. La
resiliencia que el país tenía antes de la muestra tiene signo estable, pero sin Polonia pierde
significancia, y no es realmente previa para cinco de los trece países: exploratorio."

**Si me pregunta** por qué menos deuda va con un coeficiente mayor de la fragilidad (+0,107): no
tengo una explicación contrastable; lo reporto.

**Si me pregunta** por los cinco países: Brasil, Chile, Colombia, México y Perú usan sus primeros 16
trimestres (2009Q4–2013Q3) en vez de 2004–07.

### 27. Las reservas bajo escrutinio (2 min)
**Cómo leer:** las tres primeras filas muestran que resiste los rezagos; las tres siguientes, dónde
se debilita; las dos últimas son placebos.

**Qué digo:** "El coeficiente de la fragilidad es menor donde hay más reservas: −0,247 por
desviación estándar, con wild de 0,08, y es estable al rezagar las reservas cuatro y ocho
trimestres. En puntos básicos es más firme. Pero cuatro cosas me impiden llamarlo resultado. En
logaritmos depende de Polonia: sin ella es −0,084. No pasa la corrección de Holm sobre la familia
que examiné: 0,40 y 0,22. Los placebos: la cuenta corriente y el tipo de cambio real rezagados
'moderan' igual o más. Y la interacción lineal implica una elasticidad negativa para el 23 % de las
observaciones, lo que no es creíble. Lo trato como exploratorio, sin lenguaje causal ni de política
sobre acumular reservas."

## Resultados VI — crisis, heterogeneidad, quién tiene la deuda y respaldo externo (≈ 8 min)

### 28. Batería con vector de crisis · vector único (1 min 30 s)
**Cómo leer:** columna (1), las filas en negrita: la interacción fuera de crisis (β3) y en crisis
(β3+β4) con su p entre corchetes. Todas las columnas tienen controles.

**Qué digo:** "Ahora interactúo con el vector de crisis. Fuera de crisis la interacción es 0,012,
no significativa. Dentro de las crisis es −0,012. Mezclar todas las crisis junta episodios muy
distintos; por eso lo descompongo."

### 29. Backstop vs. EMstress (1 min 30 s)
**Qué digo:** "Bajo *Backstop* ---la crisis global y la pandemia--- la interacción es −0,015; bajo
*EMstress* ---2015–16--- es +0,026. Al pie de la letra, es el patrón que esperaría el mecanismo."

### 30. Lectura: el patrón esperado, pero sin robustez (1 min 15 s)
**Cómo leer:** primero la lista, después el histograma: la línea roja es 2015–16 en medio de la
distribución.

**Qué digo:** "Pero el panel no sostiene esa lectura. Con la corrección de Holm los p pasan a 0,12
y 0,24. Con errores agrupados por país, 0,40 y 0,11. En el *taper tantrum* de 2013 y en 2018 no
aparece. Y en la permutación el episodio real queda en el lugar 20 de 51 ventanas."

### 31. Heterogeneidad por economía: agrupación ex post, exploratoria (1 min 30 s)
**Cómo leer:** la columna "Sin crisis" de log-log y de niveles; después la fila de controles.

**Qué digo:** "En un grupo de once economías, fuera de crisis, la interacción es 0,034 en
logaritmos y 1,8 puntos básicos, y resiste el wild bootstrap. Mantengo el número, pero lo rotulo
exploratorio por tres razones: el grupo lo definí después de ver los datos; en logaritmos los
controles lo absorben; y la variable que debía explicarlo ---la participación extranjera en la
deuda--- no lo hace, como muestro ahora."

**Si me pregunta** por Polonia e India: es una agrupación ex post. La etiqueta de "deuda local
profunda" la retiré: vale para India (5 % en manos de no residentes), no para Polonia (40 %).

### 32. Participación extranjera en la deuda: prueba preespecificada (2 min)
**Cómo leer:** a la izquierda, el ranking de los 13 países; a la derecha, las tres hipótesis con su
p de wild bootstrap y de Holm.

**Qué digo:** "Esta es la única prueba que preespecifiqué: fijé las hipótesis, el moderador y la
familia antes de estimar. El moderador es la participación de no bancos extranjeros en la deuda del
gobierno, de Arslanalp y Tsuda, rezagada cuatro trimestres. Las tres hipótesis ---que modifica la
asociación de la fragilidad, la del riesgo de cola y la interacción--- dan +0,037, −0,001 y −0,006;
ninguna pasa el wild bootstrap, y con Holm quedan en 1,00. La tercera tiene el signo contrario al
predicho. Es ausencia de evidencia con intervalos anchos, no evidencia de un cero. Y un hecho
descriptivo que corrige mi relato anterior: Polonia tiene el 40 % de su deuda en manos de no
residentes, la cuarta más alta; China y Brasil, que estaban en el 'núcleo', son de las más bajas."

**Conclusión directa:** quién tiene la deuda no modifica la transmisión de forma demostrable, y la
heterogeneidad del núcleo de 11 pasa a exploratoria, como declaré de antemano.

**Si me pregunta** qué significa preespecificada: que lo que iba a concluir con cada resultado
estaba escrito antes de correr la regresión. Límite: consta en el encabezado del script, no en un
registro externo con fecha.

**Si me pregunta** por puntos básicos: la primera hipótesis es sugerente (+3,38; Driscoll–Kraay
0,002; cluster 0,013; wild 0,13). Según el criterio que declaré, no pasa.

**Si me pregunta** por qué falló: el 75 % de la variación del moderador es entre países, y son 13.

### 33. Respaldo externo por país: no hay desacople (1 min 30 s)
**Cómo leer:** la tercera columna: cuánto cambia la interacción cuando el país tiene acceso.

**Qué digo:** "Hasta la primera ronda el respaldo era una variable de fecha, igual para todos. Armé
quién tenía, en cada trimestre, un swap con la Reserva Federal o una Línea de Crédito Flexible del
FMI: seis países, 223 observaciones. Con acceso, ni cada riesgo ni la interacción pesan menos:
−0,004, con wild de 0,90. Dentro de las crisis globales la interacción es incluso mayor en los
países con acceso, +0,045, no significativa con wild. No hay desacople. Y el acceso no es exógeno:
se pide y se otorga según el riesgo."

**Si me pregunta** por las fechas: swap de la Fed, Brasil y México (2008Q4–2009Q4 y 2020Q1–2021Q4);
línea flexible, México desde 2009Q2, Colombia 2009Q2–2025Q1, Polonia 2009Q2–2017Q3, Chile desde
2020Q2 y Perú 2020Q2–2024Q2. Las fechas de Chile están verificadas: acceso continuo.

## Resultados VII — qué se puede afirmar (≈ 4 min)

### 34. ¿Efecto o persistencia? La retroalimentación (2 min)
**Cómo leer:** la figura son proyecciones locales acumuladas; azul, con el spread promedio;
naranja, con el de cierre.

**Qué digo:** "El rezago hace a los regresores predeterminados, no exógenos. El spread de ayer
predice la fragilidad de hoy con una elasticidad de 0,17. Para ver cuánto pesa eso, simulé un panel
con esa retroalimentación donde la fragilidad no tiene ningún efecto directo sobre el spread: la
regresión en niveles entrega, en promedio, +0,066. Mi dato es 0,099. Para el riesgo de cola, +0,022
frente a 0,032. Es un problema de identificación, no de errores estándar, y vale para los dos
coeficientes de nivel. En la figura: la respuesta a la fragilidad solo es significativa en el
impacto y con el spread promedio; con el de cierre nunca es positiva y significativa. Para el
riesgo de cola es plana."

**Si me pregunta** por la persistencia: el coeficiente autorregresivo corregido está entre 0,97 y
1,00 con el spread promedio (0,96–0,98 con el de cierre).

**Si me pregunta** si el sesgo es solo de niveles: no. En diferencias el coeficiente simulado de la
fragilidad promedia +0,019 frente a 0,037 en el dato; el movimiento del mismo trimestre también
está sujeto a él.

### 35. Inferencia calibrada por simulación (2 min)
**Cómo leer:** la primera columna debería ser 5 %; la segunda, alta. La fila en negrita es el wild
bootstrap.

**Qué digo:** "Simulé 1.000 paneles que conservan la dependencia entre países. En niveles, cuando
no hay efecto, Driscoll–Kraay rechaza el 28 % y el 21 % de las veces, y los valores críticos
corregidos no lo arreglan. El wild bootstrap por país rechaza 6 % y 7 %: es el mejor calibrado, con
una potencia de 35 % para la fragilidad y 67 % para el riesgo de cola. En primeras diferencias
todos rechazan entre 5 % y 9 %. Pero hay un límite: el wild calibra el error estándar, no corrige
el sesgo. Con retroalimentación y sin efecto directo, rechaza 'cero' el 24 % de las veces. Por eso
mi regla: en niveles, resistir el wild bootstrap es necesario, no suficiente."

**Si me pregunta** por la simulación de la primera ronda: tenía un diseño que desfavorecía al wild
(potencia de 17 % y 28 %). La nueva la reemplaza.

**Si me pregunta** por las variables instrumentales: signo inestable y Sargan rechaza; no ayudan.

## Conclusiones (≈ 6 min)

### 36. Respuesta a la pregunta (1 min 30 s)
**Qué digo:** "Vuelvo a la pregunta. Uno: la simultaneidad es un hecho; los dos riesgos coinciden
casi el doble de lo esperado, y hay indicios de que la fragilidad antecede al riesgo de cola. Dos:
cuando coinciden, no hay evidencia de que se amplifiquen, aunque no se puede descartar un extra de
hasta un 30 o 40 % de la suma. Tres: el riesgo económico agrega poco a lo que explica la
fragilidad, solo en niveles. Cuatro: ninguna condición estudiada modifica la transmisión de forma
demostrable. Y la réplica: la asociación entre fragilidad y spread replica a Chari y coautores con
sus controles, pero no es una elasticidad común ni hay precedencia temporal."

### 37. Hallazgos y su grado de evidencia (1 min 30 s)
**Cómo leer:** la tercera columna, con la misma escala de toda la tesis. Arriba lo propio; abajo,
la réplica.

**Qué digo:** "Resumo cada hallazgo con su cifra y su grado de evidencia. Firme: la simultaneidad.
Sugerente: la precedencia de la fragilidad sobre el riesgo de cola, lo que agrega el riesgo de cola
en niveles y el índice de resiliencia. Exploratorio: las reservas, la resiliencia previa y la
amplificación en el núcleo de once economías. No hay evidencia: de amplificación ---con la salvedad
del 30 al 40 %---, del riesgo de cola en cambios o fuera de muestra, de la participación extranjera,
del respaldo externo ni de la asimetría entre crisis. Y abajo, la réplica: la asociación en niveles
es sugerente, no hay evidencia de que la fragilidad anteceda al spread, y el movimiento en el mismo
trimestre resiste el wild bootstrap en puntos básicos, pero también está sujeto al sesgo de retroalimentación."

### 38. Implicancias (1 min)
**Qué digo:** "Las implicancias son prudentes. Lo respaldado: vigilar los dos riesgos juntos se
justifica, porque tienden a agravarse a la vez y hay indicios de que la fragilidad bancaria
antecede al deterioro de la cola del crecimiento. Sin base en estos datos: una prima adicional por
la simultaneidad, recomendar la acumulación de reservas o diferenciar por quién tiene la deuda. Y
no permite cuantificar cuánto bajaría el spread si cae la fragilidad."

### 39. Limitaciones y trabajo futuro (1 min)
**Qué digo:** "Las limitaciones: 13 países, con los que en niveles solo el wild bootstrap está bien
calibrado y su potencia es limitada; cada coeficiente de nivel depende de un país y tiene sesgo de
retroalimentación; el piso de JLoss deja sin información a un cuarto de las observaciones; la
simultaneidad se concentra desde 2020; y los datos trimestrales no separan la precedencia dentro
del trimestre. El trabajo futuro: más economías; spreads y fragilidad de mayor frecuencia; una
métrica de fragilidad sin piso, con una malla de pérdidas más ancha; variación exógena bancaria; y
un estudio de eventos en torno a los anuncios de líneas de respaldo."

### 40. Conclusión (30 s)
**Qué digo:** Leer las cuatro frases y la réplica, y cerrar con: "El aporte es el primer cruce de
los dos riesgos domésticos y saber qué se puede afirmar, y qué no, con 13 países."

### 41. Gracias
**Qué digo:** "Muchas gracias. Quedo atento a sus comentarios." La lámina solo dice "Gracias".

*Respaldo (42–61): no se presenta; se usa para responder. Taller I (42); baterías con errores
estándar: Panel A (43), B (44), C (45), vector único (46), Backstop vs. EMstress (47); la
elasticidad no crece con el riesgo de cola (48); robustez a la muestra y a la medición (49); logs
vs. niveles (50); niveles prueba por prueba (51); heterogeneidad en niveles (52); Argentina (53);
Hansen (54); leave-one-out y ventanas (55); medición de JLoss y GaR (56); COVID (57); solapamiento
del riesgo de cola (58); referencias (59–61).*

\newpage

# 3. Preguntas probables del profesor guía

*Responder en una o dos frases y, si insiste, ir a la lámina de respaldo. Es probable que conozca
JLoss y Chari et al. (2024) en detalle: espera preguntas finas sobre la métrica.*

**¿Las métricas son suyas?** No: JLoss es de Chari et al. (2024) y el GaR de Adrian et al. (2019),
con la plataforma de CEMLA. Lo mío es construir las series de las dos métricas y cruzarlas
(lámina 7).

**¿Por qué "la fragilidad bancaria importa" no es su conclusión?** Porque eso ya lo establecen
Chari et al. (2024). En mi tesis aparece como réplica independiente y validación del panel. Además,
la réplica tiene límites que yo mismo documento: no es una elasticidad común, depende de Turquía y
no hay precedencia temporal (láminas 18–20).

**¿Qué es nuevo respecto de Chari et al.?** El cruce con el riesgo de cola doméstico. Ellos cruzan
la fragilidad con factores globales. Lo nuevo: que los dos riesgos coinciden más que por azar; que
hay indicios de que la fragilidad antecede al riesgo de cola; que no hay evidencia de que se
amplifiquen; y que el riesgo económico agrega poco. Y la delimitación del alcance de su resultado.

**¿Qué cambió desde el 9 y el 12 de octubre?** El titular, dos veces. El 9 era "el riesgo económico
sobrevive"; el 12, "el cambio de la fragilidad". El primero no pasó las pruebas en cambios ni la
exclusión de Polonia; el segundo era en parte un artefacto de fechas. El relato de hoy abre con el
cruce de los dos riesgos, que es lo propio, y deja la fragilidad como réplica.

**¿Qué pasó con el resultado en primeras diferencias?** Era en parte agregación temporal: el EMBI
del panel es el promedio del trimestre y JLoss rezagado usa el cierre. De cierre a cierre el
coeficiente es 0,025 (wild 0,21) y nunca es significativo al excluir un país o un año. Lo que hay es
movimiento dentro del mismo trimestre (lámina 20).

**¿La simultaneidad no es solo el COVID?** No. Fuera de los trimestres de crisis la permutación
sigue en p = 0,001 (108 frente a 59). En 2020–22 lo observado casi iguala a lo esperado; el exceso
viene de 2015–19 y de 2023–26. Sí reconozco que proviene de pocos episodios comunes: 129 de 168
observaciones son de 2020 en adelante (lámina 23).

**¿Por qué no dice que la amplificación está descartada?** Porque es un no rechazo. Los intervalos
admiten un extra de hasta un 29 % de la suma en logaritmos y un 39 % en puntos básicos, y en puntos
básicos la estimación puntual es positiva (lámina 25).

**¿Entonces el riesgo económico no importa?** Agrega poco: una asociación modesta en niveles, en 10
de 13 países, con wild de 0,066 y prueba conjunta de 0,041 sobre el modelo de Chari. Pero no aparece
en cambios ni en proyecciones locales, no mejora el pronóstico y sin Polonia cae a 0,007
(láminas 21 y 22).

**¿El riesgo de cola no cuenta dos veces lo financiero?** No: limpio de factores globales el
coeficiente queda igual (0,033) y sin el bloque bursátil del índice, en 0,045 (lámina 58).

**¿Por qué falló la prueba de la participación extranjera, y qué significa preespecificada?**
Preespecificada: hipótesis, moderador, familia y consecuencias escritas antes de estimar (en el
encabezado del script). Falló porque ninguna de las tres interacciones pasa el wild bootstrap (Holm
1,00) y la tercera tiene el signo contrario. Con 13 países y un moderador cuya variación es en un
75 % entre países, los intervalos son anchos: es ausencia de evidencia, no evidencia de un cero
(lámina 32).

**¿Por qué las reservas son exploratorias?** En logaritmos dependen de Polonia; no pasan Holm (0,40
y 0,22); los placebos (cuenta corriente y tipo de cambio real rezagados) dan interacciones de fuerza
similar; e implican una elasticidad negativa para el 23 % de las observaciones. En puntos básicos
son más firmes, pero no alcanza para una recomendación (lámina 27).

**¿Qué pasa con la resiliencia como seguro?** Queda como lectura. El índice se asocia con menor
spread y con un coeficiente menor del riesgo de cola fuera de crisis, pero solo con Driscoll–Kraay:
sugerente (lámina 26).

**¿El respaldo externo apaga el canal?** No hay evidencia. Medido por país ---swap de la Fed y línea
flexible del FMI---, la transmisión no es menor con acceso (−0,004; wild 0,90). El acceso es
endógeno y son seis países (lámina 33).

**El núcleo de 11 economías, ¿no es búsqueda de especificación?** Sí, y por eso lo rotulo
exploratorio: grupo ex post, los controles lo absorben en logaritmos y la variable que debía
explicarlo no lo hace (lámina 31).

**¿Por qué log-log y no niveles, como en el Informe de Taller?** Porque las series son muy
asimétricas y JLoss es ordinal; la prueba PE prefiere logaritmos. Reporto todo también en niveles
(láminas 50 y 51).

**¿Qué significa "aditivo" en un modelo en logaritmos?** Proporcional en puntos básicos. Es álgebra
de la forma funcional; no lo llamo amplificación.

**¿Por qué no hay controles en la regresión principal?** Porque son plausiblemente canales del
mecanismo. Pero lo digo: con los seis controles domésticos la fragilidad es −0,008 (p = 0,86).

**¿El rezago resuelve la endogeneidad?** No. El spread retroalimenta a la fragilidad (0,17) y, en
una simulación sin efecto directo, la regresión en niveles entrega +0,066. Por eso no hablo de
efectos causales (lámina 34).

**¿Por qué Driscoll–Kraay y además wild bootstrap?** Porque en niveles Driscoll–Kraay rechaza una
hipótesis nula cierta entre el 20 % y el 30 % de las veces; el wild bootstrap por país está bien
calibrado (6–7 %). Pero no protege del sesgo de retroalimentación (lámina 35).

**¿No hizo demasiadas pruebas?** Sí hice muchas; por eso corrijo con Holm cada familia, preespecifiqué
la de participación extranjera y rotulo como exploratorio lo que no estaba preespecificado y no
pasa la corrección.

**¿Los resultados dependen de un país?** Los coeficientes de nivel, sí: Turquía para la fragilidad y
Polonia para el riesgo de cola y las reservas en logaritmos. La simultaneidad no: ocurre en los 13.

**¿Por qué JLoss es ordinal, y qué es el piso?** La cota de la malla de pérdidas (4,8 %) está activa
en el 98 % de los casos, y la métrica se amontona en 2,16. Un cuarto de las observaciones está
pegado a ese piso (lámina 56).

**¿El GaR no está contaminado por el spread?** El EMBI no entra al cálculo; sin el único componente
tipo spread, el GaR correlaciona 0,985 con el oficial.

**¿Por qué Argentina no está en la muestra principal?** Su GaR se estimó sin el bloque de tasas y con
una ventana más corta. Como robustez no cambia nada (lámina 53).

**Si nada es causal, ¿cuál es el aporte?** La construcción homogénea de las series para 13 países,
la réplica independiente de Chari y su delimitación, el primer cruce con el riesgo de cola
doméstico y una batería de pruebas que muestra qué no se puede afirmar con 13 países.

# 4. Cómo se atendió cada observación del profesor

| Observación (9 de octubre) | Qué se hizo |
|---|---|
| Máximo 9–10 láminas; el resto, anexo | `predefensa.tex`: 10 láminas + anexo |
| Riesgo financiero vs. riesgo económico | Lámina 3; tesis, mecanismo y marco conceptual |
| La brecha: "no se han cruzado simultáneamente…" | Lámina 3; tesis, sección de alcances y contribución |
| Triángulo en vez de secuencia; acelerador financiero | Lámina 4; tesis, sección del mecanismo |
| El respaldo es el banco central; no estaba en las regresiones | Lámina 4; ahora se mide (láminas 27, 32 y 33); tesis, secciones de resiliencia y de crisis, respaldo externo y quién tiene la deuda |
| Gráficos de GaR y JLoss antes de las regresiones | Lámina 14 |
| "Amplificación", no "multiplicidad"; efectos aditivos | Todo el guion; tesis, marco conceptual |
| Solapamiento / endogeneidad del FCI | Lámina 58; tesis, sección de solapamiento |
| Resiliencia (deuda, balance fiscal, reservas) | Láminas 26 y 27; tesis, sección de resiliencia de la política económica |
| Crisis vs. no crisis | Láminas 28–30; tesis, sección de crisis |
| Correlación, no causalidad | Láminas 4, 34 y 38 |

# 5. Decisiones que debo pedirle

1. **¿La tesis está lista para defender?** Si no, qué falta y con qué plazo.
2. **Encuadre:** ¿de acuerdo con que el titular sean las cuatro conclusiones sobre el cruce de los
   dos riesgos, y que la fragilidad quede como réplica de Chari et al.?
3. **Heterogeneidad por economía:** ¿la dejo como exploratoria en Resultados o la bajo a un anexo?
4. **Reservas:** ¿de acuerdo con reportarlas como exploratorias, sin recomendación de política?
5. **Argentina:** ¿se queda como robustez?
6. **Presentación:** ¿cuánto tiempo tendré en la defensa? ¿Qué láminas sacaría?
7. **Paper:** ¿vale la pena enviarlo con este relato? ¿A qué revista?
8. **Calendario:** entrega final, comisión y fecha de defensa.

# 6. Para cerrar la reunión

- [ ] Veredicto: lista / lista con cambios / falta trabajo.
- [ ] Lista de cambios pedidos, con prioridad.
- [ ] Decisiones 2 a 5 tomadas.
- [ ] Duración de la defensa y láminas a recortar.
- [ ] Fechas: entrega, comisión, defensa.

**Pendientes:** la base de participación extranjera (Arslanalp y Tsuda, FMI) y las fechas de la
línea del FMI de Chile ya están resueltas.

**Notas:**

\vspace{5cm}
