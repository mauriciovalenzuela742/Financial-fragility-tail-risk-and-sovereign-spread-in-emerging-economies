# Experimentos del 13 de octubre de 2026 — NO integrados

**Estado:** exploratorio. Nada de esta carpeta está en la tesis, el paper, las láminas ni en
`NUMEROS_CANONICOS_BBG.md`. Se deja registrado para decidir después si algo se incorpora.

Todos los scripts parten del panel de la especificación principal (N = 765; β1 = 0,0985;
β2 = 0,0324; β3 = −0,0112) y corren en logaritmos y en puntos básicos (`JLOSS_FORMA=nivlag`).
Inferencia: covarianza agrupada por país y wild cluster bootstrap restringido (Webb, B = 999).
Las hipótesis y el contraste de cada experimento están escritos en el encabezado de su script antes
del código de estimación.

| Script | Qué hace | Salida |
|---|---|---|
| `x0_comun.py` | utilidades (efectos fijos, Wald agrupado, wild bootstrap conjunto) | — |
| `x1_comprobaciones.py` | tres comprobaciones que pidió la auditoría final | `x1_comprobaciones*.csv` |
| `x2_fourier_superficie.py` | forma flexible de Fourier para la superficie del spread | `x2_fourier*.csv` |
| `x3_fase_ciclo.py` | transmisión según la fase del ciclo financiero global | `x3_fase_ciclo*.csv`, `x3_fase_global.csv` |
| `x4_bandas_frecuencia.py` | regresión por bandas de frecuencia | `x4_bandas*.csv` |
| `x5_kernel_rff.py` | características aleatorias de Fourier (kernel) + ridge | `x5_kernel*.csv` |

Para reproducir: desde esta carpeta, `../../../../.venv/Scripts/python.exe x4_bandas_frecuencia.py`
(y lo mismo con `JLOSS_FORMA=nivlag`).

---

## Resumen en cinco líneas

1. **Lo más útil es la descomposición por frecuencias (x4).** La fragilidad bancaria comueve con el
   spread en la banda corta (2–6 trimestres) y el riesgo de cola en la banda de ciclo (6–32
   trimestres). Es la primera prueba en que el riesgo económico aparece con la inferencia exigente
   (wild p = 0,016) y sin depender de Turquía.
2. **La aditividad se mantiene con una forma flexible (x2) y con un kernel (x5)**, pero no del todo:
   sin Polonia, la prueba de Fourier rechaza la separabilidad (wild p = 0,009).
3. **La transmisión no cambia con la fase del ciclo financiero global (x3)** en logaritmos; en
   puntos básicos hay un indicio para la fragilidad (wild p = 0,038).
4. **Un modelo no lineal no predice mejor que el lineal (x5).** De hecho el lineal apenas mejora a
   los efectos fijos solos.
5. **Las tres dudas de la auditoría (x1):** la simultaneidad sobrevive al calendario común, pero es
   de 1,2–1,3 veces y no de 1,9; la precedencia fragilidad → riesgo de cola no viene del bloque
   bursátil, pero se debilita con tendencias por país; el EMBI de Polonia tiene días negativos en
   2021–22 y esos ocho trimestres explican el signo negativo de la interacción.

---

## x1 · Comprobaciones de la auditoría

### Simultaneidad neta del calendario común
| | Observado | Esperado | Razón | p de permutación |
|---|---|---|---|---|
| Independencia dentro de cada país (lo reportado en la tesis) | 168 | 87,0 | 1,93 | 0,001 (bloques por país) |
| **Dadas las frecuencias de cada trimestre** | 168 | 140,9 | **1,19** | **0,001** (permuta países dentro del trimestre; percentil 95 = 147) |
| Fuera de trimestres de crisis, por trimestre | 108 | 81,1 | 1,33 | 0,001 |
| **Indicadores sobre series sin el promedio de cada trimestre** (N = 744) | 109 | 84,0 | **1,30** | 0,001 por tiempo; 0,007 por país |
| Ídem, fuera de crisis | 88 | 68,8 | 1,28 | 0,001; 0,017 |

Por período (observado / esperado dadas las frecuencias de cada trimestre): 2009: 14 / 13,3;
2010–14: 9 / 6,9; 2015–19: 16 / 5,6; 2020–22: 75 / 74,4; 2023–26: 54 / 40,7.

**Lectura.** Los dos riesgos *domésticos* coinciden más que por azar también después de quitar lo
común a todos los países: el resultado sigue firme. Pero la magnitud correcta es **1,2–1,3 veces**;
el "1,9 veces" mezcla la coincidencia doméstica con el hecho de que 2020–22 fue malo para todos.
Con series sin el componente común, los episodios duran 1,8 trimestres (no 2,7).

### Precedencia fragilidad(t−1) → riesgo de cola(t)
Regresión de D(t) sobre J(t−1) y D(t−1), efectos fijos de país y tiempo, todos los trimestres
disponibles de los 13 países (N = 964; la tesis reporta 0,405 sobre la muestra de estimación).

| Variante | Coeficiente | t agrupado | p wild |
|---|---|---|---|
| Base | 0,333 | 2,60 | 0,060 |
| Dirección inversa, D(t−1) → J(t) | −0,005 | −0,76 | 0,47 |
| Sin efectos fijos de tiempo | 1,156 | 6,07 | 0,001 |
| **Con tendencias por país** | 0,248 | 1,46 | **0,20** |
| Con dos rezagos de cada uno | 0,357 | 2,39 | 0,051 |
| Excluir un país: rango | 0,26 a 0,40 | 10 de 13 con \|t\| > 2,18 | — |
| JLoss en z por país | 0,189 | 1,98 | 0,071 |
| JLoss como indicador fuera del piso | −0,059 | −0,45 | 0,66 |
| GaR en muestra, con bloque bursátil | 0,221 | 2,23 | 0,059 |
| **GaR en muestra, SIN bloque bursátil** | 0,296 | 2,99 | **0,019** |

**Lectura.** La precedencia no es un artefacto de que JLoss y el índice financiero compartan
información bursátil: sin ese bloque es más fuerte. Es estable al excluir países y la dirección
inversa nunca aparece. Pero pierde significancia con tendencias por país y no existe como "salir
del piso". **Sugerente** es la etiqueta correcta. En puntos básicos el patrón es el mismo (wild
0,068; sin bloque bursátil 0,022; con tendencias 0,25).

### EMBI de Polonia
Datos diarios de `2_Datos/embi.xlsx`:

| Trimestre | Media | Mínimo | Máximo | Días no positivos |
|---|---|---|---|---|
| 2020Q4 | 18,1 | 12 | 26 | 0 |
| 2021Q1 | 15,0 | −1 | 23 | 1 |
| 2021Q2 | 15,7 | 8 | 21 | 0 |
| 2021Q3 | 15,3 | 7 | 23 | 0 |
| 2021Q4 | 32,2 | 10 | 58 | 0 |
| 2022Q1 | 27,4 | −3 | 78 | 3 |
| 2022Q2 | 36,4 | 2 | 100 | 0 |
| 2022Q3 | 21,7 | −36 | 97 | 15 |

No hay piso ni recorte: son cotizaciones reales (11 a 48 valores distintos por trimestre); el 15,000
de 2021Q1 es coincidencia. El problema es otro: spreads cercanos a cero y a veces **negativos**
(19 días), donde el logaritmo exagera cualquier movimiento.

| Muestra | β1 | β2 | β3 |
|---|---|---|---|
| Completa (765) | 0,099 (p = 0,003) | 0,032 (p = 0,033) | −0,011 (p = 0,11) |
| **Sin Polonia 2020Q4–2022Q3 (757)** | 0,117 (p < 0,001) | **0,030 (p = 0,024)** | **−0,001 (p = 0,90)** |
| Sin Polonia (676) | 0,121 (p < 0,001) | 0,007 (p = 0,51) | +0,008 (p = 0,19) |

**Lectura.** Esos ocho trimestres explican todo el signo negativo de la interacción, pero **no** el
coeficiente del riesgo de cola, que queda igual sin ellos. La dependencia del riesgo de cola respecto
de Polonia viene del resto de la serie polaca, no de un problema de datos. Es una razón para
reportar la principal sin esos ocho trimestres como robustez.

---

## x4 · Regresión por bandas de frecuencia (Engle, 1974)

Diez países con al menos 40 trimestres contiguos. Cada serie se separa en banda corta (2–6
trimestres), de ciclo (6–32) y tendencia (más de 32) con el filtro de Christiano–Fitzgerald; en cada
banda se regresa el spread sobre la fragilidad y el riesgo de cola con efectos fijos de país y
tiempo. Entre paréntesis, p del wild bootstrap.

| Banda | % de la varianza del spread | Fragilidad | Riesgo de cola | R² dentro |
|---|---|---|---|---|
| **Corta (2–6 trim.)** | 3 % | **0,037 (0,010)** | −0,006 (0,29) | 0,019 |
| **Ciclo (6–32 trim.)** | 14 % | 0,078 (0,13) | **0,018 (0,016)** | 0,049 |
| Tendencia (> 32 trim.) | 84 % | 0,052 (0,78) | 0,097 (0,22) | 0,143 |

Robustez del resultado de cada banda:

| Variante | Fragilidad, banda corta | Riesgo de cola, banda de ciclo |
|---|---|---|
| Filtro de un solo lado (medias móviles) | 0,046 (0,068) | 0,044 (0,065) |
| Spread de cierre de trimestre | 0,021 (0,25) | 0,010 (0,081) |
| Sin Polonia | 0,028 (0,030) | 0,014 (0,072) |
| Sin Turquía | 0,039 (0,011) | 0,018 (0,030) |
| En puntos básicos | 1,15 (0,12) | 3,74 (0,045) |

Otros: con el spread de cierre, la fragilidad aparece en la banda de ciclo (0,107; wild 0,046); sin
Polonia, también (0,116; wild 0,006).

**Lectura.** Se cumple lo declarado de antemano: cada riesgo comueve con el spread a su propia
frecuencia. La fragilidad, en movimientos de menos de año y medio (y ahí no depende de Turquía, a
diferencia del coeficiente en niveles). El riesgo económico, en el ciclo de 1,5 a 8 años: por eso no
aparecía en cambios trimestrales ni en proyecciones locales y sí "en niveles". La tendencia, que es
el 84 % de la varianza del spread, no identifica nada: ahí estaba el coeficiente frágil de la
regresión en niveles.

**Salvedades.** El filtro primario usa datos futuros; con el filtro de un solo lado los dos
resultados quedan al 7 %. Con el spread de cierre la fragilidad de banda corta se pierde (coherente
con el problema de fechas ya detectado). Sin Polonia el riesgo de cola baja a p = 0,07. Los
componentes filtrados están autocorrelacionados por construcción. Es **sugerente**, no firme.

---

## x2 · Forma flexible de Fourier

Prueba de separabilidad aditiva: todos los términos cruzados (el producto J×D más senos y cosenos
de la suma y la diferencia) iguales a cero.

| | Términos cruzados (p wild) | Parte aditiva no lineal (p wild) | R² dentro: lineal → Fourier aditivo → completo |
|---|---|---|---|
| **K = 1 (primaria), logs** | **0,23** | 0,035 | 0,048 → 0,077 → 0,086 |
| K = 2, logs | 0,097 | 0,40 | 0,048 → 0,095 → 0,107 |
| K = 1, puntos básicos | 0,54 | 0,093 | — |
| K = 1, sin trimestres de crisis | 0,12 | 0,063 | 0,097 → 0,131 → 0,147 |
| K = 1, observaciones fuera del piso | 0,20 | 0,046 | 0,045 → 0,080 → 0,091 |
| **K = 1, sin Polonia** | **0,009** (0,006 en pb) | 0,10 | 0,061 → 0,101 → 0,125 |

"Extra" de la superficie con ambos riesgos una desviación estándar sobre su media, frente a mover
cada uno por separado: −0,088 (ee 0,104) con K = 1; sin Polonia +0,030 (ee 0,045). Suma lineal de
los dos efectos: 0,16.

Prueba de cordura con datos simulados (200 muestras): sin interacción la prueba rechaza el 4,5 % de
las veces (correcto); con una interacción sembrada de +0,034 la detecta el 44 % (82 % en pb).

**Lectura.** En la especificación primaria no se rechaza la aditividad, tampoco con una forma no
lineal: confirma la conclusión de la tesis. Dos matices que conviene no esconder: (i) cada riesgo
por separado **no es lineal** (p = 0,035), lo que es coherente con el piso de JLoss; (ii) **sin
Polonia la separabilidad se rechaza** con claridad, aunque el "extra" en el punto de +1 d.e. no es
significativo, de modo que la no aditividad está en otra zona de la superficie. Es una señal
exploratoria de interacción fuera de Polonia, en la misma dirección que las ya reportadas (fuera
del piso × riesgo de cola; cambios a cuatro trimestres en pb).

---

## x3 · Fase del ciclo financiero global

Coeficientes que giran con la fase: β(φ) = b₀ + b_s·sen φ + b_c·cos φ. Contraste: b_s = b_c = 0.

| Ciclo | Fragilidad | Riesgo de cola | Interacción | Los seis juntos |
|---|---|---|---|---|
| VIX + alto rendimiento, 6–32 trim. (primario), logs | 0,36 | 0,42 | 0,74 | 0,54 |
| Solo VIX | 0,78 | 0,43 | 0,66 | 0,84 |
| Solo alto rendimiento | 0,67 | 0,82 | 0,64 | 0,87 |
| Banda de 6–40 trimestres | 0,20 | 0,33 | 0,71 | 0,67 |
| Sin Polonia | 0,36 | 0,32 | 0,80 | 0,58 |
| **Primario, en puntos básicos** | **0,038** | 0,16 | 0,22 | 0,051 |

(p del wild bootstrap.) En logaritmos, la elasticidad de la fragilidad sería 0,070 en el máximo de
estrés y 0,115 en el mínimo; la del riesgo de cola, 0,041 y 0,025. Ninguna diferencia es
significativa.

**Lectura.** La transmisión no cambia con la fase del ciclo financiero global en logaritmos. Es la
versión continua, y sin fechas elegidas a mano, del resultado ya reportado: las asimetrías por
régimen de crisis no son un hallazgo. En puntos básicos hay un indicio de que el coeficiente de la
fragilidad varía con la fase, que es lo esperable si el efecto es proporcional y el spread es más
alto en estrés: no es evidencia de un mecanismo distinto.

---

## x5 · Kernel con características aleatorias de Fourier

Raíz del error cuadrático medio fuera de muestra, relativa al modelo lineal aditivo (menor que 1 =
mejor que el lineal). Promedio de cinco semillas.

| Modelo | Bloques de tiempo, logs | Dejar un país fuera, logs | Bloques de tiempo, pb | País fuera, pb |
|---|---|---|---|---|
| Lineal con producto J×D | 1,003 | 1,015 | 1,024 | 1,009 |
| Kernel aditivo | 1,002 | 1,017 | 0,993 | 1,029 |
| Kernel conjunto | 1,002 | 1,035 | 0,988 | 1,042 |
| Kernel conjunto frente a aditivo | 1,000 | 1,017 | 0,995 | 1,012 |

El lineal aditivo apenas mejora a los efectos fijos solos: 0,3053 frente a 0,3104 por bloques de
tiempo (1,6 %) y 0,3099 frente a 0,3104 dejando un país fuera (0,2 %).

Prueba de cordura: con una interacción sembrada de +0,034 el kernel conjunto le gana al aditivo
(0,94) y con el triple, con claridad (0,78); sin interacción sembrada, no (0,99). El método detecta
una interacción cuando existe.

**Lectura.** Ni una forma no lineal general ni permitir cualquier interacción mejora la predicción:
la linealidad y la aditividad bastan para predecir. El resultado de fondo es más incómodo: los dos
riesgos casi no agregan capacidad predictiva fuera de muestra sobre los efectos fijos, y nada cuando
se predice un país no visto. Refuerza que las asociaciones son modestas y específicas de cada país.

---

## Qué cambiaría en la tesis si se incorporan

| Resultado | Efecto sobre el relato actual |
|---|---|
| Bandas de frecuencia (x4) | **Refuerza y ordena.** Daría al riesgo económico su primer resultado con la inferencia exigente ("comueve con el spread en la banda de ciclo") y explicaría por qué no aparece en cambios. Candidato claro a incorporar, con sus salvedades. |
| Simultaneidad neta del calendario (x1) | **Corrige una cifra.** "1,9 veces" debería acompañarse siempre de "1,2–1,3 veces neto del calendario común" (hoy la tesis dice 1,3 con el cálculo por año; por trimestre es 1,2). |
| Precedencia sin bloque bursátil (x1) | **Sostiene** la etiqueta "sugerente" y responde la objeción más probable. |
| Polonia 2020Q4–2022Q3 (x1) | **Matiza.** El signo negativo de la interacción es de ocho trimestres con spreads cercanos a cero; el riesgo de cola no depende de ellos. |
| Fourier (x2) y kernel (x5) | **Confirman** la aditividad sin imponer la forma; agregan que cada riesgo no es lineal y que sin Polonia la separabilidad se rechaza (exploratorio). |
| Fase del ciclo (x3) | **Confirma** que las asimetrías por crisis no son un hallazgo. |

## Límites de estos experimentos
- Son muchas pruebas nuevas sobre los mismos 765 datos y 13 países; ninguna corrige por
  comparaciones múltiples entre experimentos.
- Los filtros de x3 y x4 usan datos futuros (la versión de un solo lado de x4 da resultados al 7 %).
- En x5 los efectos fijos se quitan sobre la muestra completa antes de validar.
- x4 usa 10 de los 13 países (los que tienen 40 trimestres contiguos).
- La simulación de cordura de x2 usa 200 muestras.
