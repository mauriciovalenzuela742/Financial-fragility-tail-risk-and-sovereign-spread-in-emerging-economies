---
title: "Séptima evaluación: la tesis después de las correcciones de la sexta ronda"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lectura integral"
---

*Evaluación de la versión del commit `3ff5960` (empujado a `origin/master`), más la reescritura del párrafo
de vulnerabilidad macroeconómica de la introducción hecha en esta ronda. La tesis tiene 167 pp. Usa la
misma rúbrica de 8 criterios y pesos de `evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Esta ronda tiene dos preguntas:*
1. *¿quedaron bien aplicadas las cinco acciones de la sexta ronda?*
2. *¿cómo se explica el concepto de riesgo económico, y cómo se enlaza con el $GaR$? El autor señaló que
   el párrafo de vulnerabilidad de la introducción explicaba mal esa conexión.*

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA). Todo son asociaciones.*

---

# 1. Qué cambió desde la sexta ronda (6,42 → 6,5 reestimada)

| Cambio | Commit | Efecto |
|---|---|---|
| `p60`–`p66` en el comando único; 140 cifras canónicas (140 de 140 coinciden) | `247382d` | El comando único vuelve a cubrir todas las cifras de la tesis |
| Holm, BH y BY sobre las 23 hipótesis primarias | `247382d` | Solo el signo de la réplica externa queda bajo 0,05 con Holm (0,046), sin cambiar el veredicto; con BY, ninguna |
| Introducción con dos tipos de preregistro; Q3 en las conclusiones; Q1–Q6 en `preparacion_defensa.md` | `247382d` | Desaparece la promesa de una inferencia "sobre todos" sin respaldo |
| Anexo G propio para las preguntas de portafolio; resumen de ~410 palabras | `247382d` | El Anexo F vuelve a reunir solo lo que extiende la tesis |
| Lizarazo (2013) y Yue (2010) | `247382d` | Las extensiones del modelo quedan referenciadas |
| `tesis_latex.zip` autocontenido; PDF de 167 pp. actualizado | `9780161`, `3ff5960` | Entrega lista |

Verifiqué las cinco acciones en el texto y en el código. Están aplicadas como dice el registro de la sexta
ronda.

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | 6.ª reestimada |
|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,4 | 0,960 | 6,4 |
| 2 | Marco teórico y literatura | 10 % | 6,7 | 0,670 | 6,6 |
| 3 | Datos y construcción de las métricas | 15 % | 6,4 | 0,960 | 6,4 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,8 |
| 5 | Inferencia y robustez | 15 % | 7,0 | 1,050 | 7,0 |
| 6 | Interpretación | 15 % | 6,9 | 1,035 | 6,9 |
| 7 | Redacción, estructura y extensión | 5 % | 6,4 | 0,320 | 6,4 |
| 8 | Reproducibilidad y transparencia | 5 % | 7,0 | 0,350 | 7,0 |
| | **Nota ponderada** | | | **6,51** | 6,50 |

**Nota: 6,5 (6,51).** El marco sube una décima con la reescritura del párrafo de vulnerabilidad (sección 3).
La nota no sube más: lo que queda es de presentación, y la identificación sigue siendo el techo.

**Rango:**
- **6,4:** si la comisión pregunta por qué la deuda, que es el moderador con más evidencia, no aparece
  entre los moderadores que anuncia la introducción (3.3).
- **6,6:** con las acciones de la sección 5, en especial la conexión del resultado R2-H3 con la estructura
  temporal del $GaR$ (3.2).

**En una frase:** la contabilidad está cerrada. Lo que queda es explicar mejor por qué el $GaR$ es la medida
correcta del riesgo económico y por qué su horizonte importa, y eso la tesis ya lo tiene en sus propios
resultados.

---

# 3. Verificación

## 3.1 El párrafo de vulnerabilidad macroeconómica (corregido en esta ronda)

**El problema.** El párrafo original (`capitulos/01_introduccion.tex:39-50`) tenía dos mitades que no se
tocaban:
- la primera definía la vulnerabilidad como exposición a *shocks* más capacidad de resistirlos;
- la segunda saltaba a que las condiciones financieras predicen la cola izquierda del crecimiento.

El texto nunca decía por qué un cuantil del crecimiento mide esa exposición y esa capacidad. Además, la
definición no tenía cita, y la literatura de *Growth-at-Risk* aparecía como una herramienta, no como una
respuesta a un problema de medición.

**La corrección.** El párrafo nuevo sigue una cadena de cinco pasos:

| Paso | Contenido | Cita nueva |
|---|---|---|
| 1. Concepto | La vulnerabilidad combina exposición a *shocks* y capacidad de absorberlos | Briguglio et al. (2009) |
| 2. Medición tradicional | Indicadores por separado (déficit, deuda, reservas, crédito) en sistemas de alerta temprana: dicen cuán expuesta está la economía, no cuánto caería la actividad | Kaminsky, Lizondo y Reinhart (1998) |
| 3. El aporte de GaR | Lleva la vulnerabilidad a la distribución del crecimiento futuro. Una economía vulnerable no es la que espera crecer menos, sino aquella en que el escenario muy adverso es más probable y más profundo. Las condiciones financieras mueven sobre todo la cola izquierda | Adrian et al. (2019) |
| 4. El enlace | El cuantil bajo reúne los dos elementos de la definición: las condiciones financieras recogen la exposición acumulada, y la profundidad de la cola refleja cuánto amortigua la economía el golpe | — |
| 5. Dinámica y uso | Las condiciones laxas bajan el riesgo de cola de corto plazo y lo suben a dos o tres años. GaR se usa como herramienta del FMI y de la región, y la tesis adapta la plataforma de CEMLA | Adrian et al. (2022); Prasad et al. (2019); Ossandon Busch et al. (2022) |

El párrafo cierra con el puente al soberano (en la cola caen la recaudación y la capacidad de pago) y con
una frase explícita: "Por eso la tesis mide el riesgo económico doméstico con el $GaR$". Con eso, el
párrafo queda simétrico con el anterior, que va del *doom loop* a $JLoss$.

**Comprobaciones.**
- Las tres referencias nuevas están en `capitulos/referencias.tex`.
- La tesis compila con 167 pp., sin citas indefinidas.
- El párrafo dice que la tesis "adapta" la plataforma de CEMLA, no que la usa tal cual. Así coincide con
  la Sección `sec:gar`, que describe tres modificaciones.

## 3.2 La estructura temporal del GaR explica el resultado más firme sobre el riesgo de cola, y la tesis no lo conecta

Este es el hallazgo principal de la ronda.

**Qué dice la literatura.** Adrian et al. (2022), ahora citado en la introducción, muestran que el efecto
de las condiciones financieras sobre la cola del crecimiento cambia de signo con el horizonte:
- reducen el riesgo de cola en el corto plazo;
- lo aumentan a uno, dos y tres años.

**Qué dice la tesis.** Los resultados de la tesis dicen lo mismo desde el lado del spread:

| Horizonte del riesgo de cola | Resultado |
|---|---|
| Un trimestre, $D$ (especificación principal) | 2–3 % por punto porcentual; no mejora el pronóstico; la deuda × $D$ no es significativa (permutación, $p$ = 0,17) |
| Cuatro trimestres, $D4$ (R2-H3, `04_resultados.tex:511`) | **Evidencia firme:** 4,7 % por punto porcentual, pasa Holm y se mantiene sin cada una de las trece economías; la deuda × $D4$ es de 0,033 (wild $p$ = 0,005; DK $p$ = 0,033) |
| Ocho trimestres | Mayor aún por punto porcentual |

El riesgo económico que el mercado incorpora al spread es el de mediano plazo, y es en ese horizonte donde
la literatura de estructura temporal ubica la acumulación de vulnerabilidad.

**Qué falta.** Ni el marco (`02_marco_teorico.tex:28`, subsección del canal $GaR$) ni la sección de R2-H3
citan esa literatura. El resultado aparece como un hallazgo empírico aislado, cuando tiene una explicación
teórica disponible. Además, la elección de $h=1$ para la especificación principal (`03_metodologia.tex:160`)
queda sin justificación frente a esa literatura.

**Lo que preguntaría la comisión:** "si el horizonte que importa es el de un año, ¿por qué la
especificación principal usa el de un trimestre?". La respuesta honesta es que $h=1$ se fijó antes de R2-H3
siguiendo a la plataforma de CEMLA, y que R2-H3 se preregistró para probar el horizonte. Pero la tesis
debería decirlo.

## 3.3 La introducción no menciona la deuda entre los moderadores

`01_introduccion.tex`, párrafo que sigue a los objetivos: "se observan tres condiciones ---la resiliencia
de la política económica, el respaldo oficial externo y quién tiene la deuda soberana---, condiciones las
cuales se contrastan como moderadores".

Hay dos problemas:
- **Falta el nivel de la deuda pública.** Es el moderador con más evidencia (hallazgo 4, dos preregistros,
  permutación) y el que da lugar al modelo de límite fiscal. La lista menciona quién tiene la deuda, pero
  no cuánta hay.
- **La redacción** ("condiciones las cuales") es pesada.

Sugerencia: "La investigación contrasta cuatro condiciones como moderadores: el nivel de la deuda pública,
la resiliencia de la política económica, el respaldo oficial externo y quién tiene la deuda soberana".

## 3.4 Detalles menores

| # | Dónde | Qué |
|---|---|---|
| 1 | Objetivo específico 4 (`01_introduccion.tex`) | Habla de "interacción $JLoss\times GaR$", pero la especificación usa $D\equiv-GaR$. Convendría escribir $JLoss\times D$ o "fragilidad × riesgo de cola", para que el signo esperado no confunda |
| 2 | Objetivo específico 1 | "Una muestra amplia de economías emergentes": son trece. "Trece economías emergentes" es más preciso y no promete de más |
| 3 | Paper, subsección *Growth-at-Risk* (`cuerpo.tex:181`) | Tiene la misma debilidad del párrafo original: cita a Adrian et al. (2019) como resultado, sin el concepto ni la estructura temporal. Conviene reflejar 3.1 y 3.2 |
| 4 | Paper | La tabla de Argentina, generada automáticamente, sigue 13 pt sobre el alto de la página |
| 5 | Zenodo | Sigue sin activarse (lo debe hacer el autor) |

---

# 4. Evaluación por criterio

## 4.1 Contribución — 6,4

Sin cambios. La contribución se lee igual en todas partes: simultaneidad firme, sin amplificación grande, y
la regularidad de la deuda sin confirmar. Conectar R2-H3 con la estructura temporal (3.2) no agrega
evidencia, pero sí hace más legible el hallazgo sobre el riesgo económico.

## 4.2 Marco — 6,7

- **A favor:**
  - El concepto de riesgo económico tiene ahora una definición citada, una razón para medirlo con un
    cuantil del crecimiento y un puente explícito al soberano. Antes era el punto más débil de la
    introducción.
  - Las dos métricas quedan presentadas con la misma lógica: del mecanismo a la medida.
- **En contra:** la estructura temporal entró en la introducción, pero no en el marco ni en los
  resultados (3.2). Con eso, el criterio llegaría a 6,8.

## 4.3 Datos — 6,4

Sin cambios. Siguen pendientes el piso de JLoss y la falta de calificación soberana histórica.

## 4.4 Identificación — 5,8

Sin cambios. Es el techo estructural de la tesis, con trece economías y sin variación exógena.

## 4.5 Inferencia — 7,0

La corrección sobre las 23 hipótesis cerró lo que faltaba. No hay más que agregar dentro del repositorio.

## 4.6 Interpretación — 6,9

- **A favor:** sin contradicciones entre capítulos. La lectura de los preregistros quant es prudente.
- **En contra:** la omisión de la deuda en la lista de moderadores (3.3) y la elección de $h=1$ sin
  justificar frente a R2-H3 (3.2).

## 4.7 Estructura — 6,4

Sin cambios. El Anexo G separa bien lo que aplica la tesis de lo que la extiende. Los detalles de
redacción de 3.3 y 3.4 son menores.

## 4.8 Reproducibilidad — 7,0

El comando único y las 140 cifras canónicas cubren toda la tesis. Zenodo sigue pendiente, pero no depende
del repositorio.

---

# 5. Acciones, en orden de costo

| # | Acción | Costo | Efecto |
|---|---|---|---|
| 1 | Una o dos frases en el marco (subsección del canal $GaR$) con la estructura temporal de Adrian et al. (2022); una frase en R2-H3 que lea el resultado a la luz de esa literatura; una frase en la metodología que justifique $h=1$ como horizonte fijado de antemano y remita a R2-H3 | 45 min | Marco +0,1; interpretación +0,1 |
| 2 | Corregir la lista de moderadores de la introducción para incluir el nivel de la deuda (3.3) | 10 min | Interpretación (incluido en la anterior) |
| 3 | Objetivos 1 y 4: "trece economías" y "fragilidad × riesgo de cola" | 10 min | Estructura +0,1 |
| 4 | Reflejar 3.1 y 3.2 en la subsección *Growth-at-Risk* del paper | 30 min | Coherencia entre la tesis y el paper |
| 5 | Agregar a `preparacion_defensa.md` la pregunta "¿por qué un trimestre si el horizonte que importa es el año?" | 15 min | Defensa |

| Criterio | Hoy | Con las acciones 1–5 |
|---|---|---|
| Contribución | 6,4 | 6,4 |
| Marco | 6,7 | 6,8 |
| Datos | 6,4 | 6,4 |
| Identificación | 5,8 | 5,8 |
| Inferencia | 7,0 | 7,0 |
| Interpretación | 6,9 | 7,0 |
| Estructura | 6,4 | 6,5 |
| Reproducibilidad | 7,0 | 7,0 |
| **Ponderada** | **6,51** | **6,54** |

**El techo.** Sigue en la identificación (20 %) y en una contribución sin un resultado positivo nuevo sobre
el spread. Lo que queda por ganar es presentación.

**Para la defensa.** La conexión de 3.2 es un buen argumento para la comisión: el resultado más firme sobre
el riesgo económico (R2-H3) está en el horizonte donde la literatura ubica la vulnerabilidad. Dicho en una
frase: "el mercado cobra por la cola del próximo trimestre, pero cobra más por la del próximo año".
