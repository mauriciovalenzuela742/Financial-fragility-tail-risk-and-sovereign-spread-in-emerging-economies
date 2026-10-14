# Ingeniería de variables — experimento del 13 de octubre de 2026 (NO integrado)

**Estado:** exploratorio. Nada de esto está en la tesis, el paper ni las láminas.

**Idea.** Reconstruir cada regresor desde sus ingredientes para que mida lo que la teoría dice que
debería medir, y ver si la evidencia cambia.

**Archivos.**
- `f0_construir_features.py` → `features_panel.csv` (1.156 país-trimestres, 104 columnas) y
  `features_diccionario.md` (definición, fuente y cobertura de cada variable).
- `f1_evaluar.py` → `f1_resultados.csv` (94 especificaciones), `f1_seleccion.csv`,
  `f1_atenuacion.csv`.

**Protocolo** (declarado en el encabezado de `f1_evaluar.py` antes de estimar): ln EMBI con efectos
fijos de país y tiempo, variables rezagadas un trimestre; por especificación, coeficiente con wild
bootstrap por país (B = 999), ganancia de R² sobre la base en la misma muestra, estabilidad al
excluir cada país, error fuera de muestra (bloques de tiempo, país fuera, y reserva 2023Q3+) y un p
corregido por todo lo probado (máximo |t| bajo 199 permutaciones). Regresión base reproducida:
N = 765; 0,0985 / 0,0324 / −0,0112.

---

## Resultado general

**Ninguna variable construida mejora de forma demostrable a las dos originales.**

- El |t| que habría que superar para no ser azar, dado que se probaron 81 variables, es **4,50**.
  El mayor |t| observado es 2,6. Ningún p corregido baja de 0,66.
- Fuera de muestra, ninguna especificación mejora a la base en más de 2 % (las razones van de 0,98
  a 1,04), y eso incluye la muestra de reserva.
- **Los placebos rinden igual que las variables "con teoría".** El tipo de cambio real, transformado
  igual que la fragilidad, llega a t = −2,05 (y a −5,6 sin Polonia). Si una variable sin relación
  teórica produce estadísticos de ese tamaño, los de las demás no se pueden leer como hallazgos.
- En la selección por LASSO, el placebo del tipo de cambio real entra el 82 % de las veces: la
  selección automática no es confiable en este panel.

Lo valioso del ejercicio no es una variable ganadora, sino **cuatro diagnósticos** sobre qué miden
de verdad los dos regresores de la tesis.

---

## Los cuatro diagnósticos

### 1. El "riesgo de cola" es, en la práctica, el crecimiento esperado (F5)
Descomposición exacta: D = (−media condicional) + (media − cuantil 5 %).

| Componente | Coeficiente | p wild | Lectura |
|---|---|---|---|
| D completo (base) | 0,030 | 0,17 | referencia |
| Solo la media (con signo cambiado) | 0,028 | 0,26 | casi igual que D |
| Distancia a la baja, dada la media (**primaria**) | 0,040 | 0,43 | no se distingue de cero |
| Media, dada la distancia a la baja | 0,029 | 0,22 | — |
| Distancia al alza (placebo de simetría) | −0,001 | 1,00 | nula, como debía |
| Dispersión / asimetría / profundidad de la cola | — | 0,36 a 0,72 | nulas |

La correlación entre D y la media con signo cambiado es **0,95**; con la distancia a la baja, 0,51.
Reemplazar D por solo la media deja el ajuste igual (ΔR² = −0,003).

**Lectura.** Lo que la tesis llama riesgo de cola del crecimiento se mueve casi enteramente con el
crecimiento esperado. El panel no permite separar "la cola" de "la media": la forma de la
distribución (dispersión, asimetría, profundidad) no agrega nada. El placebo al alza sale nulo, lo
que descarta que sea solo incertidumbre, pero no rescata la lectura de cola. **Es el hallazgo más
importante del ejercicio para la redacción de la tesis.**

### 2. Parte de la asociación del riesgo de cola viene del bloque de tasas del índice financiero (F6)
Con el GaR estimado en muestra (comparación igual a igual):

| Regresor | Coeficiente | p wild | Exclusiones significativas |
|---|---|---|---|
| Riesgo de cola en muestra, base | 0,037 | 0,013 | 12 de 13 |
| **Sin el diferencial de tasas reales** (**primaria**) | 0,016 | 0,060 | 2 de 13 |
| Sin el bloque bursátil | 0,045 | 0,073 | 1 de 13 |
| Bloque de tasas del índice financiero | 0,362 | 0,049 | 9 de 13 |
| Bloque bursátil | 0,169 | 0,55 | 0 de 13 |
| Bloque cambiario | 0,298 | 0,057 | 0 de 13 |
| Índice financiero completo, sin regresión cuantílica | 0,085 | 0,14 | 0 de 13 |

**Lectura.** Al quitar el diferencial de tasas reales entre el país y EE.UU. el coeficiente cae a
menos de la mitad y pierde estabilidad. De los tres bloques del índice, el de tasas es el que se
asocia con el spread. Como la tasa local a diez años y el spread soberano son parientes cercanos,
una parte de la asociación del riesgo de cola es circular. (El GaR en muestra usa información
futura; por eso su p de 0,013 no es comparable con el de la tesis, que usa el de tiempo real.)

### 3. La fragilidad no es volatilidad de mercado disfrazada, pero tampoco gana al abrirla (F1–F4)

| Variable | Coeficiente | p wild | ΔR² sobre la base | Lectura |
|---|---|---|---|---|
| JLoss (base) | 0,097 | 0,32 | — | referencia (sin interacción) |
| **Costo del rescate en % del PIB** (F1, primaria) | 0,084 | 0,25 | −0,002 | no mejora |
| Tamaño del sistema, dado JLoss | 0,009 | 0,98 | 0,000 | el tamaño no agrega |
| **Malla ancha** (F2, primaria; 12 países) | 0,066 | 0,41 | −0,005 | no mejora |
| Percentil por país | 0,233 | 0,071 | +0,008 | marginal |
| Duración del episodio fuera del piso | 0,084 | 0,097 | +0,035 | marginal; 5 de 13 exclusiones |
| **Fracción de pasivos en bancos en estrés** (F3, primaria) | 0,154 | 0,14 | −0,002 | no mejora |
| Distancia al incumplimiento media | −0,130 | 0,083 | +0,013 | signo correcto; marginal |
| Apalancamiento / volatilidad de la banca | 0,197 / 0,077 | 0,25 / 0,15 | +0,015 | — |
| **Volatilidad de la banca en exceso de la bolsa** (F4, primaria) | −0,014 | 0,92 | −0,013 | nula |
| JLoss, controlando por volatilidad y retorno de la bolsa | 0,099 | 0,33 | +0,015 | **no cambia** |
| Retorno de la banca en exceso de la bolsa | −0,263 | 0,067 | — | signo correcto; marginal |

**Lectura.**
- Buena noticia para la tesis: el coeficiente de JLoss **no se mueve** al controlar por la
  volatilidad y el retorno de la bolsa local (0,099 frente a 0,097). No es la bolsa disfrazada.
- Mala noticia: ninguna reconstrucción lo mejora. Ni escalar por el tamaño del sistema bancario
  frente al PIB (la unidad que pide la teoría del pasivo contingente), ni la malla ancha, ni los
  ingredientes banco por banco, ni la cola del sistema.
- Las únicas variantes con algo de señal son ordinales o de duración (percentil, trimestres fuera
  del piso), lo que refuerza lo ya dicho en la tesis: JLoss informa como ordenamiento, no como nivel.

### 4. El riesgo de cola se estima con un error del tamaño de la señal que identifica la regresión (F7)
- Desviación estándar del riesgo de cola entre las 500 réplicas: **1,87 pp** en promedio.
- Variación del riesgo de cola que usa la regresión (neta de efectos de país y tiempo): **1,55 pp**.
- Razón error / señal: **1,2**.

La corrección clásica por error de medición no se puede aplicar (exigiría que el error fuera menor
que la señal). **Lectura.** La regresión identifica el coeficiente del riesgo de cola con una
variación que es del mismo orden que su error de estimación. Explica por qué ese coeficiente es tan
frágil y por qué suavizarlo ayuda algo: la media móvil de 4 trimestres da 0,054 (p wild 0,15;
ΔR² +0,023), el mayor aumento de ajuste del ejercicio, coherente con el experimento de bandas de
frecuencia.

---

## Lo demás, en breve

**F8 · Simultaneidad con otras formas.** Ninguna muestra amplificación: mínimo de los dos riesgos
−0,043 (p 0,53); producto de rangos 0,225 (p 0,18); interacción secuenciada −0,013 (p 0,83); costo
del rescate × riesgo de cola −0,001 (p 0,52). El factor común de los dos riesgos sí se asocia con
el spread (0,087; p 0,085; 6 de 13 exclusiones) y su divergencia no (p 0,80): **es otra forma de
decir que los efectos se suman.** La parte del riesgo de cola predicha por la fragilidad pasada no
se distingue del resto (p 0,54): no hay evidencia de que el canal pase por el crecimiento.

**F9 · Variable dependiente.** Ninguna transformación del spread quita la dependencia de Polonia.

| Medida del spread | β2 | p wild | β2 sin Polonia |
|---|---|---|---|
| Logaritmo (tesis) | 0,032 | 0,20 | 0,007 |
| Spread propio del país (neto de VIX y alto rendimiento por país) | 0,033 | 0,14 | 0,012 |
| Seno hiperbólico inverso | 0,032 | 0,20 | 0,007 |
| Box–Cox 0,44 | 0,237 | 0,32 | 0,024 |
| ln(EMBI + 50) | 0,021 | 0,25 | 0,004 |
| Recortado al 1 %–99 % | 0,034 | 0,18 | 0,008 |
| Cierre de trimestre | 0,036 | 0,18 | 0,010 |
| Puntos básicos | 2,87 | 0,55 | −0,79 |

Para la fragilidad ocurre lo mismo con Turquía: el coeficiente cae a 0,01–0,04 sin ella con
cualquier medida.

**F10 · Memoria.** El máximo de fragilidad de los últimos cuatro trimestres no agrega (p 0,37 solo;
0,61 dado JLoss). Los cambios y brechas del riesgo de cola tienen signo negativo y no son
significativos.

**Placebos.** Tipo de cambio real estandarizado: −0,050 (p 0,31); su máximo de 4 trimestres: −0,621
(t = −2,05; p 0,12; t = −5,6 sin Polonia); mínimo con el riesgo de cola: −0,048 (p 0,43).

---

## Qué significa para la tesis (si se decidiera incorporar algo)

1. **Cambiar el nombre no, pero sí la precisión:** donde la tesis dice "riesgo de cola del
   crecimiento", convendría reconocer que en este panel esa medida se mueve casi por completo con el
   crecimiento esperado, y que la forma de la cola no agrega información (diagnóstico 1).
2. **Declarar la circularidad parcial** con el bloque de tasas del índice financiero (diagnóstico 2).
3. **Usar a favor** que JLoss no es la volatilidad de la bolsa (diagnóstico 3).
4. **Explicar la fragilidad del coeficiente del riesgo de cola** por su error de estimación
   (diagnóstico 4).
5. Nada de esto cambia las cuatro conclusiones; las vuelve más precisas y, en el caso del riesgo de
   cola, más modestas.

## Límites
- 94 especificaciones sobre 765 observaciones y 13 países: por eso el veredicto se basa en el
  máximo-t por permutación y en los placebos, no en los p individuales.
- El PIB nominal se aproximó (crecimiento interanual acumulado × IPC), definido hasta una constante
  por país; el tamaño del sistema salta cuando entra o sale un banco de la muestra.
- La distancia al incumplimiento es la versión ingenua, no la del motor de JLoss.
- En las medidas fuera de muestra los efectos fijos se descuentan sobre la muestra completa.
- La alineación de fechas de la sorpresa de crecimiento es un supuesto.
- No se corrió la versión en puntos básicos de cada familia; los puntos básicos entran solo como
  variable dependiente alternativa (F9).
