---
title: "Octava evaluación: la tesis después de las correcciones de la séptima ronda"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lectura integral"
---

*Evaluación de la versión del commit `8a43ce9` (empujado a `origin/master`). La tesis tiene 167 pp. y el paper
147. Usa la misma rúbrica de 8 criterios y pesos de `evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Esta ronda tiene dos preguntas:*
1. *¿la idea del horizonte del riesgo de cola, que entró en la séptima ronda, quedó integrada de punta a
   punta?*
2. *¿las frases nuevas dicen exactamente lo que respaldan los datos y las fuentes?*

*Esta ronda revisa también lo que escribí en la ronda anterior, con el mismo rigor que el resto.*

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA). Todo son asociaciones.*

---

# 1. Qué cambió desde la séptima ronda (6,51 → 6,54 reestimada)

| Cambio | Commit | Efecto |
|---|---|---|
| Párrafo de vulnerabilidad: concepto → medición tradicional → cuantil condicional → estructura temporal | `f7e2eb2` | El riesgo económico queda definido y enlazado con el $GaR$ |
| Estructura temporal del $GaR$ en el marco, la metodología y R2-H3 (tesis y paper) | `8a43ce9` | R2-H3 deja de ser un hallazgo aislado |
| La deuda entre los moderadores; objetivos 1 y 4 precisados; subsección GaR del paper; pregunta 12 de la defensa | `8a43ce9` | Coherencia |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | 7.ª reestimada |
|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,4 | 0,960 | 6,4 |
| 2 | Marco teórico y literatura | 10 % | 6,7 | 0,670 | 6,8 |
| 3 | Datos y construcción de las métricas | 15 % | 6,4 | 0,960 | 6,4 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,8 |
| 5 | Inferencia y robustez | 15 % | 7,0 | 1,050 | 7,0 |
| 6 | Interpretación | 15 % | 6,8 | 1,020 | 7,0 |
| 7 | Redacción, estructura y extensión | 5 % | 6,4 | 0,320 | 6,5 |
| 8 | Reproducibilidad y transparencia | 5 % | 7,0 | 0,350 | 7,0 |
| | **Nota ponderada** | | | **6,49** | 6,54 |

**Nota: 6,5 (6,49).** Baja cinco centésimas respecto de la reestimación de la séptima ronda. No es que la tesis
empeorara, sino que la reestimación anterior fue optimista: la idea del horizonte entró en tres capítulos,
pero no en los cuatro lugares donde se resume el riesgo económico (resumen, introducción, discusión y
conclusiones). Además, dos de las frases nuevas afirman más de lo que el repositorio documenta (3.2).

**Rango:**
- **6,4:** si la comisión nota que el resumen trata a Ossandon Busch como dos autores (3.1), o pregunta de
  dónde sale que el horizonte de un trimestre "sigue a CEMLA" (3.2).
- **6,6:** con las acciones de la sección 5, que toman menos de dos horas.

**En una frase:** la idea del horizonte es buena y está bien respaldada por R2-H3, pero hay que contarla con
su salvedad (no sobrevive a la corrección conjunta) y llevarla a los resúmenes de la tesis.

---

# 3. Verificación

## 3.1 Error de autoría en el resumen

`main.tex:87`, contribución (iii): "una réplica y ampliación del procedimiento de **Ossandón y Busch (2022)**".

La referencia es Ossandon Busch, M., Sánchez-Martínez, J. M., et al. (2022). "Ossandon Busch" es el apellido
de un solo autor, y el artículo tiene cinco. El cuerpo lo cita bien (`\citet{OssandonBusch2022}` produce
"Ossandon Busch et al. (2022)"), pero el resumen está escrito a mano. Es la primera página que lee la
comisión, y uno de sus miembros podría conocer a los autores.

**Corrección:** "Ossandon Busch et al.\ (2022)", sin tilde, igual que en la bibliografía.

## 3.2 Dos frases nuevas afirman más de lo que el repositorio documenta

Lo escribí en la ronda anterior y debo corregirlo.

**(a) "El horizonte de un trimestre se fijó al inicio de la investigación, siguiendo la plataforma de CEMLA"**
(`03_metodologia.tex`, Sección `sec:gar`, y en el paper). Lo documentado es solo lo siguiente:
- el código fija `H = 1` (`1_Codigo/GaR/phase2_gar_panel.py:24`);
- R2-H3 se preregistró después (`f820594`).

Nada en el repositorio dice que $h=1$ se eligiera "siguiendo a CEMLA", y la plataforma de Ossandon Busch et al.
(2022) admite varios horizontes. Hay que reemplazar la frase por la razón verdadera. Si la razón es que el panel
es trimestral y el regresor entra con un trimestre de rezago, hay que decir eso. Si la razón es que se replicó
la especificación de la plataforma, hay que citar la página.

**(b) El horizonte de Adrian et al. (2022)** aparece de dos formas distintas:
- la introducción dice que las condiciones laxas elevan el riesgo de cola "a dos o tres años";
- el marco y el paper dicen "a uno, dos y tres años".

Hay que unificarlo y verificarlo contra el artículo. Una formulación segura, que no compromete años exactos,
es: "reducen el riesgo de cola en el corto plazo y lo elevan en el mediano plazo".

## 3.3 El horizonte quedó integrado a medias

El marco, la metodología y R2-H3 dicen ahora que el horizonte que importa es más largo que un trimestre. Pero
los cuatro lugares donde la tesis resume el riesgo económico siguen describiéndolo solo con el horizonte de
un trimestre:

| Dónde | Qué dice | Qué falta |
|---|---|---|
| Resumen (`main.tex:85`), "Tercera" | "Asociación modesta y de largo plazo [...] de un 2–3 % por punto porcentual" | Que a un año es mayor (4,7 %), en 13 de 13 economías |
| Introducción, hallazgo tercero (`01_introduccion.tex`) | Igual | Igual |
| Discusión (`05_discusion.tex:13`) | "No aparece en los cambios a cuatro trimestres" | Matizar. R2-H3 (`04_resultados.tex:511`) muestra que, con el $GaR$ estimado en toda la muestra, sí aparece (*wild* $p$ = 0,006), aunque no con Driscoll–Kraay |
| Conclusión tercera (`06_conclusiones.tex:9`) | Igual que el resumen | Igual |

Un lector que lea solo el resumen y las conclusiones no se entera de que la tesis tiene un resultado
preregistrado más fuerte sobre el riesgo económico que el de la especificación principal.

## 3.4 La salvedad de R2-H3 tiene que viajar con el resultado

R2-H3 es "evidencia firme" según la escala de la tesis, porque resiste el *wild bootstrap* y la exclusión de cada
país, y pasa Holm dentro de su preregistro. Pero no sobrevive a las correcciones más exigentes:

| Corrección | $p$ de R2-H3 |
|---|---|
| Sin corregir | 0,006 |
| Holm, en la familia del preregistro 2 | 0,018 |
| Holm conjunto sobre 14 hipótesis (`p56`) | 0,08 |
| Holm global sobre 23 hipótesis (`p66`) | 0,13 |

La sección de inferencia conjunta lo dice (`04_resultados.tex:547`). Sin embargo, las frases nuevas no lo dicen:
- la pregunta 12 de `preparacion_defensa.md` responde "firme, 13 de 13" sin la salvedad;
- la frase de R2-H3 ("Es el patrón que anticipa la estructura temporal...") también va sin ella.

Si la comisión pregunta por la corrección conjunta y la respuesta corta no la menciona, parece que se ocultó.

**Corrección:** agregar "aunque no sobrevive a la corrección sobre todas las hipótesis (0,13)" en las dos
partes.

## 3.5 Detalles menores

| # | Dónde | Qué |
|---|---|---|
| 1 | Paper | La tabla de Argentina, generada automáticamente, sigue 13 pt sobre el alto de la página |
| 2 | Zenodo | Sigue sin activarse (lo debe hacer el autor) |
| 3 | `preparacion_defensa.md`, sección 5 | La lista de cifras que memorizar no incluye el 4,7 % de R2-H3 ni sus $p$ corregidos |

---

# 4. Evaluación por criterio

## 4.1 Contribución — 6,4

Sin cambios. Si el horizonte llega a los resúmenes (3.3), la contribución sobre el riesgo económico se lee
mejor: "modesta a un trimestre, mayor a un año". Pero eso no es evidencia nueva.

## 4.2 Marco — 6,7

- **A favor:** el concepto de riesgo económico y su enlace con el $GaR$ están bien construidos en la
  introducción, en el marco y en el paper.
- **En contra:** la cita de la estructura temporal tiene una formulación inconsistente entre capítulos y sin
  verificar (3.2 b). La reestimación de 6,8 suponía que esa conexión estaba cerrada.

## 4.3 Datos — 6,4

Sin cambios.

## 4.4 Identificación — 5,8

Sin cambios. Es el techo estructural de la tesis.

## 4.5 Inferencia — 7,0

Sin cambios. La corrección conjunta existe y está reportada. El problema de 3.4 es de comunicación, no de
inferencia.

## 4.6 Interpretación — 6,8

- **A favor:** la lectura de R2-H3 a la luz de la estructura temporal es correcta y útil.
- **En contra:**
  - una justificación sin respaldo documental (3.2 a);
  - la salvedad de la corrección conjunta no acompaña las frases nuevas (3.4);
  - los resúmenes no recogen el horizonte (3.3).
  Baja dos décimas respecto de la reestimación.

## 4.7 Estructura — 6,4

El error de autoría del resumen (3.1) es pequeño, pero está en la primera página. Baja una décima respecto de
la reestimación.

## 4.8 Reproducibilidad — 7,0

Sin cambios.

---

# 5. Acciones, en orden de costo

| # | Acción | Costo | Efecto |
|---|---|---|---|
| 1 | Resumen: "Ossandon Busch et al.\ (2022)" | 2 min | Estructura +0,1 |
| 2 | Reemplazar "siguiendo la plataforma de CEMLA" por la razón documentada de $h=1$ (tesis y paper); el autor confirma cuál fue | 15 min | Interpretación +0,1 |
| 3 | Unificar el horizonte de Adrian et al. (2022) en "corto plazo / mediano plazo" en la introducción, el marco y el paper | 10 min | Marco +0,1 |
| 4 | Agregar la salvedad de la corrección conjunta (0,08 sobre 14; 0,13 sobre 23) a la frase de R2-H3 y a la pregunta 12; agregar R2-H3 a las cifras que memorizar | 15 min | Interpretación +0,1 |
| 5 | Una cláusula sobre el horizonte de un año en el resumen, la introducción (hallazgo tercero), la discusión y la conclusión tercera, con su salvedad; matizar "no aparece en los cambios a cuatro trimestres" | 45 min | Interpretación (incluido en la anterior); contribución legible |

| Criterio | Hoy | Con las acciones 1–5 |
|---|---|---|
| Contribución | 6,4 | 6,4 |
| Marco | 6,7 | 6,8 |
| Datos | 6,4 | 6,4 |
| Identificación | 5,8 | 5,8 |
| Inferencia | 7,0 | 7,0 |
| Interpretación | 6,8 | 7,0 |
| Estructura | 6,4 | 6,5 |
| Reproducibilidad | 7,0 | 7,0 |
| **Ponderada** | **6,49** | **6,54** |

**El techo.** Sigue en la identificación (20 %) y en una contribución sin un resultado positivo nuevo que
sobreviva a la corrección conjunta.

**Para la defensa.** Para la pregunta 12, una respuesta honesta y corta: "A un año, el riesgo de cola pesa el
doble que a un trimestre, en las trece economías, como anticipa la literatura de estructura temporal del
GaR. Pero no sobrevive a la corrección sobre las 23 hipótesis, así que lo presento como evidencia firme
dentro de su preregistro y no como hallazgo central".

---

# 6. Registro de aplicación (27 de octubre de 2026)

| # | Estado | Qué se hizo |
|---|---|---|
| 1 | Hecho | Resumen: "Ossandon Busch et al.\ (2022)" |
| 2 | Hecho | Metodología (tesis y paper): el horizonte de un trimestre se eligió porque el panel es trimestral y el riesgo de cola entra con un trimestre de rezago, de modo que $D_{t-1}$ es la cola del crecimiento del mismo trimestre del spread. El autor confirmó la razón. La pregunta 12 de la defensa usa la misma razón |
| 3 | Hecho | Adrian et al. (2022), unificado como "lo reducen en el corto plazo y lo elevan en el mediano plazo" en la introducción, el marco y el paper |
| 4 | Hecho | Salvedad de la corrección conjunta en R2-H3 (Holm 0,13 sobre 23), en la conclusión 3 de la síntesis y en la pregunta 12; R2-H3 agregada a las cifras que memorizar |
| 5 | Hecho | El horizonte de un año, con su salvedad, en el resumen de la tesis y del paper, el hallazgo tercero de la introducción, la discusión y la conclusión tercera. Matizado "no aparece en los cambios a cuatro trimestres" (solo con el $GaR$ en pseudo tiempo real) en la discusión y en la introducción del paper |

La tesis compila con 167 pp. y el paper con 147, sin referencias indefinidas. El PDF y `tesis_latex.zip` quedaron
regenerados. Siguen pendientes la tabla de Argentina del paper y Zenodo.

**Nota reestimada: 6,5 (6,54)** (6,4 contribución; 6,8 marco; 6,4 datos; 5,8 identificación; 7,0 inferencia; 7,0
interpretación; 6,5 estructura; 7,0 reproducibilidad).
