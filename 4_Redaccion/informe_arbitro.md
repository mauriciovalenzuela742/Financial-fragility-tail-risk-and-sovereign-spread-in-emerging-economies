---
title: "Informe de árbitro y respuesta"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — dos rondas de arbitraje, 13 de octubre de 2026"
---

*Revisión de la tesis como la haría un árbitro especializado en spreads soberanos e interpretación
de regresiones. La primera ronda (12 de octubre) planteó doce objeciones; la segunda (13 de octubre)
revisó las respuestas a la primera y encontró que varias no se sostenían. Cada objeción se respondió
con una prueba, y cada prueba se reporta salga como salga. Las cifras están en
`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`, secciones 17 (primera ronda) y 18 (segunda ronda).
Las métricas no son del autor: JLoss es de Chari et al. (2024) y el GaR, de Adrian, Boyarchenko y
Giannone (2019) con la plataforma de CEMLA; lo propio es construir las series de las dos métricas y
cruzarlas. Todo lo que sigue son asociaciones, no causalidad.*

# 1. Conclusión principal de la tesis tras las dos rondas

**Pregunta propia de la tesis.** Sobre la fragilidad bancaria que ya documentan Chari et al. (2024),
¿qué agrega el riesgo económico doméstico, y qué pasa cuando los dos riesgos se dan a la vez?

**Respuesta en una frase.** Los dos riesgos domésticos tienden a darse juntos ---y hay evidencia sugerente de que la fragilidad
bancaria antecede al deterioro de la cola del crecimiento---, pero cuando coinciden no hay evidencia de que se amplifiquen (no se puede descartar un extra de hasta un 30–40 % de la suma); el riesgo económico agrega información modesta y
solo en niveles a lo que ya explica la fragilidad; y ninguna de las condiciones estudiadas
(resiliencia, respaldo externo, quién tiene la deuda) modifica la transmisión de forma demostrable.

**Escala de evidencia** (la misma en todos los documentos): *firme* = resiste la inferencia exigente
(wild bootstrap o permutación) y no depende de un país; *sugerente* = significativo solo con
Driscoll–Kraay, o depende de un país; *exploratorio* = no estaba preespecificado y no pasa la
corrección por comparaciones múltiples; *no hay evidencia*.

Las cuatro conclusiones propias, en orden de importancia:

1. **La simultaneidad es un hecho (firme).** Con ambos riesgos en su tercil alto dentro de cada
   país hay 168 observaciones (22,0 %) frente a 87 esperadas si fueran independientes: 1,9 veces.
   Ocurre en los 13 países; la permutación por bloques da p = 0,001, también fuera de los trimestres
   de crisis (108 frente a 59,3). Los episodios conjuntos duran 2,71 trimestres en promedio (1,85
   por azar; p = 0,003). Hay evidencia sugerente (un rezago trimestral; 0,106 d.e.; sin prueba de excluir un país ni de fechas) de que la fragilidad antecede al riesgo de cola (0,405; wild p = 0,024) y no al
   revés (−0,006; p = 0,50). Salvedad: 129 de las 168 observaciones conjuntas son de 2020 en adelante. Neto del calendario común, la coincidencia es menor: dadas las frecuencias de cada año lo esperado es 132 (no 87), es decir, 1,3 veces; en 2020–22 lo observado (75) casi iguala a lo esperado (71,5), y el exceso viene de 2010–19 (25 frente a 9) y 2023–26 (54 frente a 38).
2. **Cuando coinciden, no hay evidencia de que se amplifiquen (no se descarta un extra de hasta un 30–40 % de la suma).** La interacción de la
   regresión principal es −0,011 (wild p = 0,89); el término de estrés conjunto es −0,077 (wild
   p = 0,23) y negativo en todos los horizontes hasta cuatro trimestres. No se escribe "descartada":
   los datos no permiten descartar un extra de hasta un 30–40 % de la suma de los dos efectos.
3. **El riesgo económico agrega poco a lo que explica la fragilidad (sugerente, solo en niveles).**
   Sobre la especificación al estilo de Chari, agregar el riesgo de cola da 0,037 (wild p = 0,066) y
   la prueba conjunta pasa el wild (p = 0,041). Pero no aparece en los cambios a cuatro trimestres,
   ni en las proyecciones locales (0 de 9 horizontes), ni entre países, y no mejora el pronóstico
   fuera de muestra (el error sube un 3 %). Sin Polonia cae a 0,007. Es una asociación modesta, de
   unos 0,02–0,03 por punto porcentual de riesgo de cola, presente en niveles en la mayoría de los
   países (10 de 13 pendientes positivas).
4. **Ninguna condición estudiada modifica la transmisión de forma demostrable.** La participación
   extranjera en la deuda, con hipótesis escritas antes de estimar, da nulo en las tres pruebas
   primarias. El respaldo externo medido por país no muestra desacople. Reservas × fragilidad y
   resiliencia previa × riesgo de cola pasan a exploratorias; la heterogeneidad del "núcleo de 11
   economías", también.

**La fragilidad bancaria no es el titular.** Que la fragilidad bancaria importa para el spread ya lo
establecen Chari et al. (2024). En la tesis aparece como *réplica independiente* y validación del
panel: la elasticidad es 0,099 (Driscoll–Kraay p = 0,003), entre 0,107 y 0,164 con los controles de
esos autores y 0,206 con el CDS, sobre una construcción de datos independiente. No puede ser la
conclusión principal por dos razones. Primera, no es un aporte propio. Segunda, la segunda ronda
delimitó su alcance: no es una elasticidad común (la homogeneidad de pendientes se rechaza y Turquía
aporta el 70 % del coeficiente; sin ella, 0,034 con p = 0,43), no resiste el wild bootstrap en
niveles (p = 0,33), no hay evidencia de que la fragilidad anteceda al spread (se mueven dentro del
mismo trimestre) y un VAR simulado sin efecto directo reproduce dos tercios del coeficiente (+0,066
frente a 0,099).

# 2. Qué cambió entre la primera y la segunda ronda

| Afirmación de la primera ronda | Prueba de la segunda ronda | Veredicto |
|---|---|---|
| "El cambio de la fragilidad anticipa el spread del trimestre siguiente" (0,037; wild 0,007) | Fechas: el EMBI del panel es el promedio del trimestre; se rehízo con el spread de cierre (`p27`) | **Retirada.** Prueba limpia 0,025 (wild 0,21); lo que hay es comovimiento dentro del mismo trimestre: 0,037 (wild 0,008) |
| "El spread responde al cambio y no al nivel" | Corrección de errores, proyecciones locales acumuladas y jackknife (`p28`) | **Retirada.** Los datos no informan: multiplicador de largo plazo −0,146, IC 95 % [−0,79; 0,50], que contiene el cero y el coeficiente estático |
| "Es el único coeficiente que resiste el wild bootstrap"; "son cuatro los resultados que resisten" | Revisión de cada uno con las pruebas nuevas | **Retiradas.** No hay un conteo de ese tipo; rige la escala de evidencia de la sección 1 |
| "Driscoll–Kraay sobre-rechaza 27–38 %; el wild detecta el efecto 17–28 % de las veces" | Simulación nueva con dependencia entre países y con retroalimentación (`p29`, S = 1000) | **Corregida.** Driscoll–Kraay 21–28 % de tamaño; wild 6–7 % de tamaño y 35 % / 67 % de potencia |
| "Las reservas atenúan el efecto de la fragilidad: el resultado de moderación más robusto" | Rezagos, versión ex ante, exclusión de países, placebos y Holm (`p31`) | **Exploratoria.** En logaritmos depende de Polonia; Holm 0,40 (0,22 en pb); la cuenta corriente y el tipo de cambio real "moderan" igual |
| "La resiliencia previa atenúa el riesgo de cola" (−0,028; wild 0,06) | Lo mismo (`p31`) | **Exploratoria.** "Ex ante" no lo es para 5 de 13 países; sin Polonia pierde significancia en logaritmos y en pb desaparece sin México |
| "La interacción en pb en diferencias (0,188) coincide con la implícita (0,19)" | Intervalo de la implícita | **Retirada** la palabra "coincide": el intervalo de la implícita es [0,01; 0,42] |
| "El respaldo externo no explica la amplificación" | Verificación de las ventanas de Chile y Perú | **Se mantiene.** Chile: acceso continuo confirmado; Perú, 2020Q2–2024Q2 |
| Participación extranjera en la deuda: pendiente | Base de Arslanalp y Tsuda (versión mayo 2026); hipótesis escritas antes de estimar (`p26`) | **Hecha: nulo.** h3 = −0,006 (wild 0,48; Holm 1,00), signo contrario al predicho |
| Heterogeneidad del "núcleo de 11 economías" (wild 0,015; Holm 0,005) | Consecuencia declarada de antemano en `p26` | **Exploratoria.** Se mantiene el número; grupo ex post que la participación extranjera no explica |
| "Polonia e India: economías de deuda local profunda" | Ranking descriptivo de participación extranjera | **Retirada** para Polonia (40 %, 4.ª de 13); vale para India (5 %). Se llama agrupación ex post |
| "Lo más firme es el efecto del cambio de la fragilidad" | Decisión de encuadre y pruebas de alcance (`p30`) | **Reemplazada.** La fragilidad es réplica de Chari et al.; lo firme es la simultaneidad |
| "Los dos riesgos son aditivos" | Bandas de aditividad y Box–Cox (`p32`) | **Se mantiene, acotada:** no hay evidencia de amplificación; no se puede descartar un extra de hasta 30–40 % de la suma |
| "Coinciden el doble de lo esperado" | Permutación por bloques, por país, por año, persistencia y precedencia (`p32`) | **Reforzada:** firme; concentrada después de 2020 |

# 3. Las doce objeciones de la primera ronda: estado actual

| # | Objeción | Respuesta de la primera ronda | Estado tras la segunda ronda |
|-|------|------|--------|
| 1 | La regresión en niveles puede ser espuria (ρ = 0,94) | Primeras diferencias: 0,037 (wild 0,007), leído como precedencia y como efecto del cambio (`p21`) | **Reabierta y corregida.** La lectura era un artefacto de fechas; ver objeciones A y B de la sección 4 |
| 2 | La vara de inferencia está mal calibrada | Simulación con 150 muestras (`p22`) | **Reemplazada** por `p29`; la regla "resiste el wild" se mantiene para niveles |
| 3 | La coincidencia se contrasta solo con un producto | Indicadores de estrés conjunto (`p23`): −0,077 (wild 0,23) | **Se mantiene** y se amplía: simultaneidad como hecho y bandas de aditividad (`p32`) |
| 4 | Búsqueda de especificación | Holm sobre seis contrastes (`p22`) | **Se mantiene:** Backstop 0,03 → 0,12; EMstress 0,08 → 0,24. Holm se extendió a reservas y a participación extranjera |
| 5 | "Aditivo" frente a "proporcional" | Recuadro de vocabulario | **Se mantiene.** Aditivo en logaritmos = proporcional en pb es álgebra de la forma funcional, no un hallazgo |
| 6 | Variable dependiente única | CDS a cinco años (`p24`): 0,206 | **Se mantiene** como parte de la réplica; con el CDS de cierre el comovimiento del mismo trimestre es 0,059 (wild 0,007) |
| 7 | Panel desbalanceado | Diez economías de historia larga (`p24`) | **Se mantiene.** Nada cambia tampoco sin las 40 observaciones empalmadas del FMI, sin trimestres con pocos bancos o desde 2010 |
| 8 | Índice de resiliencia ad hoc y endógeno | Componentes y clasificación ex ante (`p19`) | **Rebajada.** Índice: sugerente; reservas y resiliencia previa: exploratorias |
| 9 | Magnitud económica poco visible | Efectos por desviación estándar (`p24`) | **Corregida la unidad.** Una d.e. dentro del país; JLoss tiene piso; no se escribe "un 1 % más de JLoss" ni "duplicar JLoss" |
| 10 | El respaldo externo es una variable de fecha | Acceso por país y trimestre (`p25`) | **Se mantiene.** No hay desacople: −0,004 (wild 0,90). Chile confirmado |
| 11 | La heterogeneidad se definió ex post | Pendiente | **Cerrada:** participación extranjera preespecificada, nulo; la heterogeneidad pasa a exploratoria |
| 12 | El capítulo 4 no sigue el argumento | Reordenado | **Reordenado otra vez** según la jerarquía de la sección 1: réplica, aporte del riesgo económico, simultaneidad sin amplificación, resiliencia, crisis y respaldo, identificación e inferencia, robustez |

# 4. Las objeciones de la segunda ronda

| | Objeción | Qué se hizo | Resultado |
|-|-------|------|--------|
| A | **Fechas.** El EMBI es promedio trimestral y JLoss(t−1) usa precios de cierre de t−1: el cambio del promedio contiene mecánicamente lo ocurrido dentro de t−1 | Spread de cierre, de primer mes y parte mecánica; muestra común N = 708 (`p27`) | Prueba limpia: 0,025 (wild 0,21), nunca significativa al excluir un país o un año. Mismo trimestre: 0,037 (wild 0,008). La mitad del coeficiente original en logaritmos y el 80 % en pb es agregación temporal |
| B | **Nivel frente a cambio.** Con ρ = 0,94 los dos rezagos de signo opuesto son la regresión en diferencias reescrita | Corrección de errores con intervalos delta y de Fieller; proyecciones locales acumuladas; jackknife (`p28`) | Los datos no informan. Velocidad de ajuste 0,063 (p = 0,066); multiplicador de largo plazo −0,146 (ee 0,327); conjunto de Fieller no acotado en logaritmos (acotado en pb); ρ corregido 0,97–1,00 |
| C | **Diseño de la simulación.** El proceso generador de `p22` era el esquema del propio wild bootstrap, rompía la dependencia entre países y fijaba los regresores | Tres procesos generadores, S = 1000 (`p29`) | Driscoll–Kraay 21–28 %; wild 6–7 % y potencia 35 % / 67 %. En primeras diferencias todos entre 5 % y 9 % |
| D | **Turquía y Polonia.** La dependencia se reportaba sin explicarla | Pendientes por país, palanca, tendencias y factores globales por país, spreads bajos (`p30`) | Fragilidad: pendientes entre −0,84 y +0,97; homogeneidad rechazada; Turquía aporta el 70 %. Riesgo de cola: Polonia aporta el 71 %, en parte por el logaritmo de spreads muy bajos |
| E | **Piso de JLoss.** La métrica se amontona en 2,16 | Distribución, z dentro del país, indicador de piso (`p30`) | 23,7 % de las observaciones a menos de 2 % del piso; unidad correcta: una d.e. dentro del país (0,048; 12,8 pb) |
| F | **Sesgo de retroalimentación.** El spread afecta a la fragilidad futura | VAR de panel simulado sin efecto directo (`p29`, proceso C) | La regresión estática entrega en promedio +0,066 (dato 0,099) y +0,022 para el riesgo de cola (dato 0,032). Problema de identificación, no de errores estándar |
| G | **Reservas.** Familia amplia de pruebas, dato anual interpolado, dependencia de Polonia | Rezagos, ex ante, entre/dentro, exclusiones, placebos, Holm (`p31`) | Exploratorio (sección 5.6) |
| H | **Participación extranjera sin preespecificar** | Hipótesis, moderador primario, familia y criterio escritos en el script antes de estimar (`p26`) | Nulo en las tres primarias; la ex ante, signo contrario (wild 0,038) |
| I | **Qué agrega el riesgo de cola** a lo que ya se sabía por Chari et al. | Información incremental, cambios a cuatro trimestres, proyecciones locales, fuera de muestra, medidas alternativas (`p32`) | Sugerente, solo en niveles (sección 5.1) |

# 5. Detalle por tema

En todas las tablas, entre paréntesis van valores p; "DK" es Driscoll–Kraay y "wild", el wild
cluster bootstrap por país.

## 5.1 Qué agrega el riesgo económico

| | Logaritmos | Puntos básicos |
|---|---|---|
| Riesgo de cola agregado al modelo de Chari, N = 662 (DK / cluster / wild) | 0,037 (0,008 / 0,018 / 0,066) | 5,37 (0,031 / 0,028 / 0,145) |
| Prueba conjunta, riesgo de cola e interacción (DK / cluster / wild) | 0,0001 / 0,014 / 0,041 | 0,058 / 0,082 / 0,142 |
| R² dentro del país: sin / con riesgo de cola / con interacción | 0,153 / 0,185 / 0,194 | 0,218 / 0,239 / 0,239 |
| R² parcial del riesgo de cola dada la fragilidad / al revés | 0,037 / 0,018 | 0,026 / 0,103 |
| Sin controles, N = 765 (DK / wild) | 0,030 (0,068 / 0,17) | 3,52 (0,24 / 0,34) |
| Cambios a cuatro trimestres (DK / wild) | 0,004 (0,71 / 0,13) | 0,32 (0,85 / 0,77) |
| Proyecciones locales, horizontes significativos | 0 de 9 | 0 de 9 |
| Entre países (13 medias) | 0,052 (0,46) | 8,9 (0,47) |
| Fuera de muestra: error con fragilidad / con fragilidad y riesgo de cola | 0,1601 / 0,1650 (Clark–West 0,83) | 33,3 / 34,4 (Clark–West 0,88) |
| Sin Polonia | 0,007 (0,51) | 0,18 (0,95) |
| Sin las 36 observaciones bajo 60 pb / sin las 113 bajo 100 pb | 0,018 (0,11) / 0,002 (0,85) | 2,26 (0,41) / 0,25 (0,93) |
| Promedio de grupo, 10 países con T ≥ 40 | 0,033 (0,004) | 4,32 (0,025) |
| Con tendencias por país (DK / wild) | 0,035 (0,033 / 0,016) | 4,28 (0,19 / 0,13) |
| Probabilidad de crecimiento negativo | 0,193 (DK p = 0,33; wild 0,088); sin Polonia 0,202 (p = 0,17); interacción −0,342 (DK p = 0,028) |

Con esta medida el coeficiente no cae al excluir Polonia.

Fuera de muestra: ventana expansiva, un trimestre adelante, 540 pronósticos desde 2013Q2. Ningún
modelo le gana al spread rezagado (0,1559), tampoco con la fragilidad.

## 5.2 Simultaneidad y ausencia de amplificación

| Simultaneidad | Valor |
|---|---|
| Ambos riesgos en su tercil alto / esperadas si fueran independientes | 168 (22,0 %) / 87 |
| Países con más observaciones conjuntas que las esperadas | 13 de 13 |
| Permutación por bloques, 999 réplicas: media; p | 85,7; 0,001 |
| Fuera de los trimestres de crisis: observadas / media de la permutación; p | 108 / 59,3; 0,001 |
| Episodios; duración media / bajo permutación; p | 62; 2,71 / 1,85 trimestres; 0,003 |
| Fragilidad(t−1) sobre riesgo de cola(t) (DK / cluster / wild) | 0,405 (0,009 / 0,001 / 0,024) |
| Riesgo de cola(t−1) sobre fragilidad(t) (DK / cluster / wild) | −0,006 (0,50 / 0,47 / 0,48) |
| Correlación de los dos riesgos descontados los efectos fijos | 0,26 |
| 2009 / 2010–19 / 2020 / 2021 / 2022 / 2023 / 2024 / 2025 / 2026 | 14 / 25 / 29 / 17 / 29 / 20 / 15 / 13 / 6 |
| En trimestres de crisis / peso de esos trimestres en la muestra | 35,7 % / 14,2 % |

| Amplificación | Logaritmos | Puntos básicos |
|---|---|---|
| Interacción de la principal (DK / cluster / wild) | −0,011 (0,11 / 0,53 / 0,89) | +0,246 (0,34 / 0,42 / 0,49) |
| Estrés conjunto: fragilidad alta / cola alta / las dos (extra; wild) | 0,091 / 0,186 / −0,077 (0,23) | 24,2 / 24,8 / −3,4 (0,67) |
| Extra en t+1 … t+4 | −0,097 / −0,057 / −0,060 / −0,046 | −6,6 / −6,9 / −9,9 / −7,0 |
| Ambos riesgos una d.e. sobre su media: suma de los dos efectos | +16,4 % del spread | 28,4 pb |
| Extra por la interacción (estimación puntual) | −2,1 puntos | +3,0 pb |
| IC 95 % de la interacción: DK / cluster / wild invertido | [−0,025; 0,003] / [−0,050; 0,028] / [−0,054; 0,015] | [−0,26; 0,76] / [−0,42; 0,91] / [−0,45; 0,92] |
| Mayor extra que no se puede descartar: DK / wild / cluster | +0,5 / +2,9 / +5,3 puntos (3 % / 16 % / 29 % de la suma) | +9,1 / +11,1 / +11,0 pb (32 % / 39 % / 39 %) |
| Box–Cox λ = 0,44: interacción (DK / wild) | t = −0,19 (0,85 / 0,97) | --- |
| Interacción sin Polonia | +0,008 (0,19) | +0,471 (0,086) |

El signo negativo de la interacción en logaritmos es de Polonia (aporta −0,0165 de un total de
−0,0112): no se lee como atenuación. Dos señales débiles en sentido contrario, que se reportan: el
riesgo de cola pesa más cuando los bancos están fuera del piso de JLoss (umbral de 2 %: +7,5 pb, wild 0,036, y +0,026 en logaritmos, wild 0,11; umbral de 5 %: +5,3 pb y +0,009), y en cambios a cuatro trimestres en
pb la interacción es +0,358 (wild 0,011; 12 de 13 exclusiones), ausente en logaritmos (p = 0,77).

## 5.3 La fragilidad bancaria: réplica y alcance

| | Logaritmos | Puntos básicos |
|---|---|---|
| Elasticidad agrupada (DK / cluster / wild) | 0,099 (0,003 / 0,28 / 0,33) | 4,73 (<0,001 / --- / 0,31) |
| Con los controles de Chari et al. | 0,107 a 0,164 | --- |
| Con el CDS a cinco años | 0,206 (<0,001) | 7,45 (<0,001) |
| Pendientes por país: rango; positivas | −0,84 a +0,97; 8 de 13 | −39,0 a +40,7; 10 de 13 |
| Promedio de grupo (ee; p) | 0,106 (0,119; 0,39) | 4,01 (5,07; 0,44) |
| Homogeneidad: Pesaran–Yamagata Δ; Q | 15,4; 128,7 (<0,001) | 24,0; 256,5 (<0,001) |
| Turquía: variación de la fragilidad / aporte al coeficiente | 17 % / 70 % | 28 % / 83 % |
| Sin Turquía | 0,034 (0,43) | 0,63 (0,54) |
| Sin Turquía ni Polonia | 0,073 (0,039) | 0,96 (0,33) |
| Con tendencias por país (DK / wild) | 0,046 (0,135 / 0,68) | 4,54 (<0,001 / 0,41) |
| Con cargas de VIX y HY por país (DK / wild) | 0,070 (0,011 / 0,43) | 3,78 (<0,001 / 0,40) |
| Una d.e. dentro del país (z por país) (DK / wild) | 0,048 (0,023 / 0,18) | 12,8 (<0,001 / 0,17) |
| Con el spread de cierre (DK / wild) | 0,083 (0,015 / 0,40) | 4,42 (<0,001 / 0,39) |

Piso de JLoss: 2,16 (el techo de la malla de pérdidas). Percentiles 5 / 25 / 50 / 75 / 95: 2,16 /
2,21 / 2,67 / 4,84 / 13,92. El 23,7 % de las observaciones está a menos de 2 % del piso (32,4 % a
menos de 5 %): Malasia 60 %, Perú 58 %, Chile 49 %, Sudáfrica 38 %, Indonesia 34 %, México 29 %,
Colombia 26 %, Polonia 13 %, China 8 %, Turquía 2 %; Brasil, India y Filipinas 0 %.

## 5.4 Fechas y dinámica

| Cambio del spread, sobre el cambio de la fragilidad en t−1 (DK / wild) | Logaritmos | Puntos básicos |
|---|---|---|
| promedio(t) − promedio(t−1): versión de la primera ronda | 0,039 (0,001 / 0,0005) | 1,30 (0,008 / 0,051) |
| **cierre(t) − cierre(t−1): prueba limpia de precedencia** | **0,025 (0,22 / 0,21)** | **0,28 (0,71 / 0,58)** |
| primer mes(t) − cierre(t−1) | 0,000 (0,98 / 0,99) | 0,04 (0,85 / 0,91) |
| parte mecánica: cierre(t−1) − promedio(t−1) | 0,020 (0,008 / 0,001) | 1,03 (0,010 / 0,002) |
| **cierre(t−1) − cierre(t−2): mismo trimestre** | **0,037 (0,044 / 0,008)** | **2,64 (<0,001 / 0,008)** |
| CDS de cierre, mismo trimestre | 0,059 (0,011 / 0,007) | 3,49 (<0,001 / 0,008) |
| Prueba limpia: exclusiones de país / de año significativas | 0 de 13 / 0 de 23 | 0 de 13 / 0 de 23 |
| Mismo trimestre: exclusiones de país / de año significativas | 6 de 13 / 13 de 23 | 13 de 13 / 23 de 23 |
| Placebo de adelanto, cambio de la fragilidad en t+1 | nunca significativo | nunca significativo |
| Una d.e. del cambio de la fragilidad, mismo trimestre | 0,37: 1,4 % del spread (unos 2,7 pb) | 2,46: 6,5 pb |
| R² parcial, mismo trimestre | 0,8 % | 4,3 % |

| Nivel frente a cambio (spread promedio) | Logaritmos | Puntos básicos |
|---|---|---|
| Velocidad de ajuste | 0,063 (0,066) | 0,090 (<0,001) |
| Multiplicador de largo plazo de la fragilidad (ee) | −0,146 (0,327) | 1,96 (3,21) |
| IC 95 % | [−0,79; 0,50] | [−4,33; 8,26] |
| Coeficiente estático (dentro del intervalo) | 0,0985 | 4,73 |
| Conjunto de Fieller | no acotado | acotado |
| Respuesta acumulada, spread promedio: impacto; horizontes significativos | 0,038 (0,013); 1 de 9 | 1,12 (0,029); 3 de 9 |
| Respuesta acumulada, spread de cierre | nunca positiva y significativa; negativa en h = 6 y h = 8 (−0,072 y −0,073; p = 0,04) | 0 de 9 |
| Persistencia del choque de JLoss a ocho trimestres | 0,46 | 0,59 |

**Redacción:** la fragilidad bancaria y el spread se mueven dentro del mismo trimestre; no hay
evidencia de que la fragilidad anteceda al spread.

## 5.5 Inferencia

Tasa de rechazo al 5 % nominal, fragilidad / riesgo de cola (S = 1000, B = 199; en logaritmos).
B: remuestreo por fecha con AR(2) por país; C: VAR de panel con retroalimentación.

| Niveles | Tamaño B | Potencia B | Tamaño C, centrado | Rechazo de cero en C |
|---|---|---|---|---|
| Driscoll–Kraay | 28 % / 21 % | 70 % / 77 % | 18 % / 18 % | 42 % / 45 % |
| DK, banda larga y valores críticos fixed-b | 15 % / 11 % | 56 % / 66 % | 9 % / 10 % | 27 % / 29 % |
| Cluster por país, t(12) | 9 % / 8 % | 44 % / 70 % | 6 % / 14 % | 26 % / 24 % |
| Wild bootstrap por país | 6 % / 7 % | 35 % / 67 % | 5 % / 12 % | 24 % / 24 % |

| Primeras diferencias | Tamaño B | Potencia B (fragilidad) | Rechazo de cero en C |
|---|---|---|---|
| Driscoll–Kraay | 5 % / 6 % | 87 % | 29 % / 7 % |
| Cluster por país, t(12) | 6 % / 9 % | 84 % | 24 % / 7 % |
| Wild bootstrap por país | 6 % / 6 % | 81 % | 26 % / 4 % |

"Centrado" mide solo la calibración del error estándar. "Rechazo de cero en C" es la frecuencia con
que se rechaza el cero cuando el efecto directo es nulo pero hay retroalimentación: mezcla inferencia
e identificación. El error estándar de Driscoll–Kraay en niveles es 0,56–0,68 de la desviación
verdadera. Valores p reales de la principal (fragilidad / riesgo de cola / interacción):
Driscoll–Kraay 0,003 / 0,033 / 0,11; cluster t(12) 0,28 / 0,14 / 0,53; wild 0,33 / 0,20 / 0,89.

| Sesgo de retroalimentación (media del coeficiente con efecto directo nulo) | Fragilidad | Riesgo de cola |
|---|---|---|
| Niveles, con retroalimentación | +0,066 (d.e. 0,060; límite de panel largo 0,123) | +0,022 |
| Niveles, sin retroalimentación | +0,028 | +0,011 |
| Primeras diferencias, con retroalimentación | +0,019 | 0,000 |
| Dato (niveles / primeras diferencias) | 0,0985 / 0,037 | 0,032 / −0,002 |

**Regla:** en niveles, "resiste el wild bootstrap" es el criterio; "solo Driscoll–Kraay" rechaza una
hipótesis nula cierta entre el 20 % y el 30 % de las veces.

## 5.6 Condiciones que podrían modificar la transmisión

| Participación extranjera, familia primaria (DK / cluster / wild; Holm sobre wild) | Logaritmos | Puntos básicos |
|---|---|---|
| h1: fragilidad × participación | +0,037 (0,34 / 0,39 / 0,41; 1,00) | +3,38 (0,002 / 0,013 / 0,13; 0,40) |
| h2: riesgo de cola × participación | −0,001 (0,90 / 0,91 / 0,92; 1,00) | +1,51 (0,12 / 0,32 / 0,34; 0,69) |
| h3: interacción × participación | −0,006 (0,31 / 0,49 / 0,48; 1,00) | −0,33 (0,053 / 0,31 / 0,38; 0,69) |
| Secundaria ex ante, h3 (DK / wild) | −0,020 (0,005 / 0,038) | −0,38 (0,010 / 0,048) |
| Secundarias: rezago de 8 trimestres, h3 / sin crisis, h1 (wild) | −0,013 (0,19) / +0,069 (0,17) | −0,40 (0,15) / +3,28 (0,15) |

Datos: Arslanalp y Tsuda (FMI, versión de mayo de 2026), 13 países, 2004Q1–2025Q4. Moderador
primario: participación de no bancos extranjeros en la deuda total del gobierno, rezagada cuatro
trimestres y estandarizada (media 21,5; d.e. 14,4 puntos; 75 % de su varianza es entre países);
N = 762. Participación total media: Perú 64; Indonesia 50; Colombia 43; **Polonia 40** (rango 27–55);
México 39; Turquía 31; Chile 31; Sudáfrica 31; Filipinas 29; Malasia 24; Brasil 12; **India 5**;
China 3. Se reporta que en pb h1 es significativo con Driscoll–Kraay y con cluster (Holm 0,005 y
0,040) y no con el wild, que era el criterio declarado.

| Reservas/PIB × fragilidad (DK / cluster / wild) | Logaritmos | Puntos básicos |
|---|---|---|
| Contemporáneo | −0,247 (<0,001 / 0,048 / 0,08) | −11,3 (<0,001 / <0,001 / 0,04) |
| Reservas rezagadas 4 / 8 trimestres (wild) | −0,234 (0,051) / −0,190 (0,085) | −10,9 (0,020) / −10,3 (0,057) |
| Ex ante, invariante en el tiempo (wild) | −0,073 (0,30) | −4,35 (0,13) |
| Sin Polonia (cluster / wild) | −0,084 (0,19 / 0,30) | −9,5 (<0,001 / 0,08) |
| Exclusiones de país que pasan el wild al 5 % | 1 de 13 | 10 de 13 |
| Holm sobre 3 componentes × 2 riesgos (wild) | 0,40 | 0,22 |
| Placebo: cuenta corriente rezagada × fragilidad (wild) | −0,113 (0,040) | −4,08 (0,062) |
| Placebo: tipo de cambio real rezagado × fragilidad (wild) | +0,123 (0,019) | +3,62 (0,026) |
| De 9 moderadores placebo, significativos con DK / con wild | 7 / 2 | 6 / 2 |
| Observaciones con elasticidad implícita negativa y significativa | 23 % | 29 % |

| Resiliencia (DK / cluster / wild) | Logaritmos | Puntos básicos |
|---|---|---|
| Resiliencia previa × riesgo de cola | −0,028 (0,006 / 0,064 / 0,064) | −4,73 (0,019 / 0,18 / 0,15) |
| Lo mismo, fuera de crisis | −0,047 (<0,001 / 0,082 / 0,08) | −8,52 (<0,001 / 0,13 / 0,11) |
| Lo mismo, sin Polonia / sin México (DK) | −0,018 (0,11) / −0,024 (0,045) | −6,60 (0,004) / −1,58 (0,44) |
| Índice contemporáneo: efecto directo (DK / cluster) | −0,153 (0,001 / 0,38) | −3,5 (0,60 / 0,89) |
| Índice × riesgo de cola: fuera de crisis / en crisis (DK) | −0,024 (0,007) / −0,001 (0,86) | −4,25 (0,008) / +1,14 (0,10) |

| Respaldo externo por país (DK / wild) | Logaritmos | Puntos básicos |
|---|---|---|
| Interacción × acceso, muestra completa | −0,004 (0,86 / 0,90) | −1,02 (0,22 / 0,52) |
| Interacción × acceso, dentro de las crisis globales | +0,045 (0,030 / 0,22) | +0,14 (0,55 / 0,79) |
| Núcleo de 11 fuera de crisis: interacción (wild) | +0,034 (0,015) | +1,8 (0,002) |

Ventanas de respaldo: swap de la Fed, Brasil y México (2008Q4–2009Q4 y 2020Q1–2021Q4); Línea de
Crédito Flexible del FMI, México desde 2009Q2, Colombia 2009Q2–2025Q1, Polonia 2009Q2–2017Q3, Chile
desde 2020Q2 y Perú 2020Q2–2024Q2. Chile: en mayo de 2022 pasó a una Línea de Liquidez de Corto Plazo
y el 29 de agosto de 2022 el FMI aprobó una nueva Línea de Crédito Flexible y Chile canceló la
anterior (comunicado pr22294); el acceso se trata como continuo.

**Redacción defendible para las reservas:** el coeficiente de la fragilidad es menor donde hay más
reservas; la asociación es estable al rezagar las reservas y se mantiene en puntos básicos, pero en
logaritmos depende de Polonia, no pasa la corrección por comparaciones múltiples y otras variables
macroeconómicas muestran interacciones de fuerza similar; se trata como exploratoria. Sin lenguaje
causal ni de política sobre acumular reservas.

# 6. Qué queda abierto

1. **El titular debe acordarse con el profesor guía.** La jerarquía de la sección 1 cambia lo
   conversado el 9 de octubre y lo escrito tras la primera ronda.
2. **Rezago de publicación de los balances en la fecha de JLoss.** No se pudo verificar: las fechas de
   balance de la extracción son una malla trimestral (27 de febrero, mayo, agosto y noviembre) y el
   repositorio no guarda la fecha del periodo fiscal ni la de anuncio. Si el balance entra con un
   trimestre de rezago, "mismo trimestre" lo es para el precio y la volatilidad, no para el balance.
3. **La retroalimentación no la resuelve ningún error estándar.** En el VAR simulado sin efecto
   directo, todos los métodos rechazan el cero entre el 24 % y el 45 % de las veces en niveles, el
   wild incluido (24 %). "Resiste el wild bootstrap" protege del error estándar mal calibrado, no de
   este sesgo. Vale para los dos coeficientes de nivel y, en menor medida, para el comovimiento en
   diferencias de la fragilidad (+0,019 de sesgo frente a 0,037).
4. **No hay una hipótesis nula limpia con VAR(2) para la simulación en primeras diferencias.** El
   proceso C es un VAR(1); con retroalimentación, el tamaño en diferencias mezcla inferencia e
   identificación (29 % contra cero; 6 % centrado).
5. **Los valores críticos fixed-b no se verificaron con efectos fijos de tiempo.** Se obtuvieron
   simulando la distribución límite estándar.
6. **Las medidas "ex ante" no lo son para 5 de 13 países** (Brasil, Chile, Colombia, México y Perú
   usan sus primeros 16 trimestres, 2009Q4–2013Q3).
7. **Sin corrección por comparaciones múltiples en `p30`.** Son cerca de 60 regresiones de robustez;
   las señales aisladas (riesgo de cola fuera del piso, sin Turquía ni Polonia) se leen con esa reserva.
8. **La simultaneidad se concentra después de 2020:** 129 de 168 observaciones conjuntas; el 35,7 %
   cae en trimestres de crisis, que son el 14,2 % de la muestra. La permutación fuera de crisis la
   sostiene, pero el hecho descansa en pocos episodios comunes.
9. **La aditividad no está demostrada, solo no rechazada.** Las bandas admiten un extra de hasta un
   30–40 % de la suma, y en puntos básicos la estimación puntual es positiva (+3,0 pb).
10. **La preespecificación de la participación extranjera consta en el encabezado del script**, no
    en un registro externo con fecha (el script no estaba versionado antes de estimar). En puntos
    básicos, h1 es significativo con Driscoll–Kraay y con cluster.
11. **Los valores p del wild bootstrap varían en el segundo decimal entre scripts** según el número
    de réplicas (por ejemplo 0,89 y 0,90 para la interacción; 0,23 y 0,25 para el estrés conjunto).
12. **Por qué Turquía y Polonia.** Ahora está descrito (palanca, piso, spreads bajos), no explicado.
13. **No se puede cuantificar cuánto bajaría el spread si cae la fragilidad.**

# 7. Dónde quedó cada cosa

| Qué | Dónde |
|---|---|
| Código, primera ronda | `1_Codigo/Panel/bbg/p21_estacionariedad.py`, `p22_inferencia_potencia.py`, `p23_estres_conjunto.py`, `p24_robustez_medicion.py`, `p25_respaldo_externo.py`, `p19_resiliencia.py` |
| Código, segunda ronda | `p26_participacion_extranjera.py`, `p27_fd_tiempos.py`, `p28_dinamica_lp.py`, `p29_simulacion_v2.py`, `p30_influencia_paises.py`, `p31_reservas_placebo.py`, `p32_aporte_riesgo_cola.py` |
| Cifras, segunda ronda | `paper_aporte_numeros.csv`, `paper_tiempos_numeros.csv`, `paper_dinamica_numeros.csv`, `paper_influencia_numeros.csv`, `paper_participacion_numeros.csv`, `paper_reservas_numeros.csv` (cada uno con su gemelo `_nivlag` en puntos básicos) y `paper_inferencia_v2_numeros.csv`; columnas `clave`, `valor` |
| Cifras, primera ronda | `paper_estacionariedad_`, `paper_inferencia_`, `paper_estres_conjunto_`, `paper_medicion_`, `paper_resiliencia_`, `paper_respaldo_numeros.csv` |
| Resumen de cifras | `NUMEROS_CANONICOS_BBG.md`, §17 y §18 |
| Datos nuevos | `2_Datos/Database_For_Posting_EM_Frozen.xlsx`, `2_Datos/participacion_extranjera.csv`, `1_Codigo/Panel/bbg/embi_trimestral_alternativo.csv`, `respaldo_externo.csv` |
| Figuras | `4_Redaccion/envios/paper_empirico/figuras/`: `fig_aporte_cola`, `fig_lp_acumulada`, `fig_pendientes_pais`, `fig_reservas_efecto_marginal` (cada una `_lnlag` y `_nivlag`) y `fig_participacion_extranjera` |
| Fuente única del relato | Brief de la segunda ronda (13 de octubre de 2026): jerarquía, escala de evidencia y frases retiradas |
