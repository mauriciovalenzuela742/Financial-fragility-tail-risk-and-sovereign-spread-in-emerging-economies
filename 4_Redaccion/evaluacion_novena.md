---
title: "Novena evaluación: la tesis con el texto oficial del autor, la pasada de estilo y el WGI real"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lectura integral"
---

*Evaluación de la versión del commit `05b31bb` (en `origin/master`). La tesis tiene 165 pp. Usa la misma
rúbrica de 8 criterios y pesos de `evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Esta ronda tiene tres preguntas:*
1. *¿El texto oficial del autor (resumen e introducción) deja a la tesis igual de bien presentada?*
2. *¿La pasada de redacción con las pautas del humanizer introdujo errores o inconsistencias?*
3. *¿Qué cambia con el reemplazo de la plantilla de gobernanza por el WGI real?*

*El análisis aparte de ESG y λ (preregistro 9) no forma parte de la tesis y no se evalúa como tal; solo se
menciona como respaldo para la defensa.*

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con
CEMLA). Todo son asociaciones.*

---

# 1. Qué cambió desde la octava ronda (6,54 reestimada)

| Cambio | Commit | Efecto |
|---|---|---|
| Portada, resumen e introducción oficiales del autor; la comisión pasa a ser solo A. Corvalán | `9e22a44` | El resumen dice ahora lo que muestran los datos. La introducción pierde el párrafo de datos y la Sección 1.3 (hallazgos y contribuciones) |
| Capítulos 2 a 7 y anexos redactados con las pautas del humanizer | `e0dba9f` … `5200305` | Prosa más directa. Un script verificó que no cambiara ninguna cifra, cita, referencia ni término de la escala de evidencia |
| `instituciones.csv`: el WGI real de 2018 reemplaza a la plantilla | `57c5d44` | El Anexo B ya no tiene datos marcados como provisionales. La triple interacción sigue sin ser significativa |
| README al día | `05b31bb` | Transparencia |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | 8.ª reestimada |
|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,3 | 0,945 | 6,4 |
| 2 | Marco teórico y literatura | 10 % | 6,8 | 0,680 | 6,8 |
| 3 | Datos y construcción de las métricas | 15 % | 6,5 | 0,975 | 6,4 |
| 4 | Estrategia empírica e identificación | 20 % | 5,8 | 1,160 | 5,8 |
| 5 | Inferencia y robustez | 15 % | 7,0 | 1,050 | 7,0 |
| 6 | Interpretación | 15 % | 6,9 | 1,035 | 7,0 |
| 7 | Redacción, estructura y extensión | 5 % | 6,5 | 0,325 | 6,5 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,8 | 0,340 | 7,0 |
| | **Nota ponderada** | | | **6,51** | 6,54 |

**Nota: 6,5 (6,51).** Queda prácticamente igual. Los datos suben una décima por el WGI real, y la prosa se lee
mejor. Bajan tres criterios:
- **Contribución:** la introducción ya no anuncia qué se encontró ni qué aporta la tesis (3.1).
- **Interpretación:** "amplificación" se usa para dos cosas distintas (3.2).
- **Transparencia:** el anexo de IA quedó desactualizado justo después de la pasada de estilo (3.3).

**Rango:**
- **6,4:** si la comisión lee la palabra "amplificación por la deuda" como una contradicción del hallazgo
  central.
- **6,6:** con las acciones de la sección 5, que toman unas dos horas.

**En una frase:** la tesis no perdió sustancia con el texto oficial ni con la pasada de estilo. Lo que hay que
cuidar es que el lector sepa desde la introducción qué se encontró, y que el anexo de IA declare lo que se
hizo.

---

# 3. Verificación

## 3.1 La introducción ya no anuncia los hallazgos ni las contribuciones

El autor decidió quitar la Sección 1.3 y el párrafo de datos y método, y es una decisión legítima. Pero tiene
un costo:
- La introducción termina en los objetivos y en el párrafo de organización, así que quien llega al
  Capítulo 2 no sabe la muestra, el método ni el resultado.
- En el modelo CARS que la propia introducción declara seguir, el tercer paso ("ocupar el nicho") incluye
  anunciar los hallazgos principales y su valor.
- Las seis contribuciones siguen en la tesis, pero solo en el último párrafo de las conclusiones
  (`06_conclusiones.tex:17`). El resumen tampoco las nombra.

**Propuesta, que respeta la decisión del autor:** no restituir 1.3. Basta con tres o cuatro oraciones al final
de 1.2, antes del párrafo de organización:
1. la muestra (13 economías, 2004–2026, N = 765);
2. la respuesta en una línea (los riesgos coinciden, pero no se amplifican);
3. las contribuciones en una enumeración corrida.

El texto queda del autor, y la comisión sabe desde la página 3 qué se encontró.

**Detalle de la misma introducción:** "estas dos literaturas **no** se han cruzado" (`01_introduccion.tex:64`)
es una afirmación absoluta. El marco (`02_marco_teorico.tex:99`) es más prudente, y la versión anterior decía
"casi no". Con un solo trabajo que las cruce, la comisión puede objetarla. Conviene volver a "casi no se han
cruzado".

## 3.2 "Amplificación" designa dos cosas distintas

En la tesis, **amplificación** es H3: que la coincidencia de los dos riesgos eleve el spread más que la suma.
El hallazgo central es que no hay evidencia de ella. Pero la misma palabra se usa para la interacción de la
deuda con el riesgo de cola, en una docena de lugares:

| Dónde | Frase |
|---|---|
| `04_resultados.tex:415` y `:837` | "si la deuda pública amplifica la transmisión del riesgo de cola" |
| `04_resultados.tex:511` | "la amplificación por la deuda se fortalece con el horizonte que importa" |
| `04_resultados.tex:513` | "la amplificación por la deuda no se concentra en la deuda en moneda extranjera" |
| `05_discusion.tex:15` | "un instrumento de términos de intercambio no muestra la amplificación" |
| `05_discusion.tex:19` | "en parte, la amplificación del riesgo de cola por la deuda" |
| `06_conclusiones.tex:17` | "por qué la deuda parece amplificar la transmisión del riesgo de cola" |

Un lector que lea la conclusión ("no hay evidencia de amplificación") y después "la amplificación por la deuda
se fortalece" ve una contradicción, aunque no la hay. La octava ronda ya corrigió un caso aislado ("la deuda
amplifica") y quedaron los demás.

**Corrección:** reservar "amplificación" para H3 y decir, para la deuda, que **intensifica** la transmisión
del riesgo de cola o que la eleva. Son cambios de una palabra, y ninguna cifra cambia.

## 3.3 El anexo de IA quedó desactualizado

El Instructivo 17/2026 pide declarar el uso de IA en los componentes fundamentales y describir cómo se
verificó. El anexo (`anexo_ia.tex:12`) dice que el repositorio registra 107 cambios hasta el 14 de octubre, 99
de ellos con coautoría de la herramienta.

**Lo que no refleja:**
- *Las cifras:* hoy son 163 cambios hasta el 28 de octubre, 155 de ellos con la coautoría declarada.
- *La pasada de estilo:* el texto de los capítulos 2 a 7 y de los anexos se reescribió con la herramienta
  siguiendo las pautas de un modelo de "humanización" de texto (jialinyyzz/humanizer). Esas pautas se
  aplicaron a mano, y un script verificó que no cambiara ninguna cifra ni cita. La fila "Redacción" de la
  Tabla del anexo habla de "borradores y reescrituras", pero no lo menciona.

Las herramientas de "humanización" se asocian con ocultar el uso de IA. Lo que protege al autor es
declararlo con su propósito (legibilidad y variedad de las oraciones) y con su verificación (el script de
fidelidad). Si la comisión se entera por otra vía, el problema no es la herramienta, sino la omisión.

**Corrección:**
- actualizar las cifras y la fecha;
- agregar en la fila "Redacción" la pasada de estilo, con su verificación;
- agregar un prompt representativo de esa tarea.

## 3.4 El WGI real

`instituciones.csv` usaba valores aproximados del WGI 2018, marcados "verificar", y el Anexo B lo declaraba
provisional. Ahora usa los valores del Banco Mundial (`GOV_WGI_RL.EST` y `GOV_WGI_GE.EST`). La triple
interacción institucional sigue sin ser significativa:

| Variable dependiente | Plantilla | WGI real |
|---|---|---|
| EMBI | +0,26 (t = 0,89) | +0,20 (t = 0,95) |
| CDS | −0,013 (t = −0,10) | −0,16 (t = −1,21) |

Era el único dato del Anexo B sin fuente verificada.

**Hallazgo lateral, sin efecto en la tesis:** `causal_bbg.csv` es anterior a la integración de Argentina al
panel (`10f64ea`). Si se corre `p3_causal_fase5.py` completo, cambian las otras filas de esa batería. Ninguna
de esas cifras está en `verificar_canonicos.py` ni en el texto de la tesis, pero `NUMEROS_CANONICOS_BBG.md`
las cita. Conviene anotar ahí la fecha y la muestra con que se generaron.

## 3.5 La pasada de estilo

**Lo que se verificó:**
- El script de fidelidad compara, en cada archivo, cifras, claves de cita, referencias, rótulos, entornos y
  términos de la escala de evidencia. No hay diferencias, salvo una referencia que se perdió y se restituyó.
- La tesis compila sin referencias indefinidas, y `verificar_canonicos.py` da 140 de 140.

**Lectura de una muestra** (resultados de R2-H3, discusión y conclusiones): la prosa es más directa y la
escala de evidencia está intacta, sin oraciones que digan más que antes. El único problema que la lectura
encontró es el de 3.2, que es anterior a la pasada.

**Tipografía:** el signo de porcentaje va pegado a la cifra en unos 370 lugares ("4,7\%") y con espacio fino
en unos 15 ("2--3\,\%"). La norma RAE pide espacio, aunque la convención en economía tolera ambos. Lo que sí
conviene es elegir una forma, y la más barata es la mayoritaria.

## 3.6 El resumen

El resumen oficial corregido cumple:
- da la muestra;
- dice la respuesta sin exagerarla;
- lleva la salvedad del horizonte de un año;
- atribuye bien las dos métricas.

**Dos detalles menores:**
1. Dice "mayor con el horizonte de un año" sin la cifra. "4,7 %" cabe en tres caracteres y es la cifra que la
   comisión va a preguntar.
2. Usa "vulnerabilidad macroeconómica" en la hipótesis y "riesgo económico" en los hallazgos sin enlazarlos.
   La introducción explica que el riesgo económico es la vulnerabilidad medida con el GaR, pero el resumen se
   lee solo. Basta con "vulnerabilidad macroeconómica (el riesgo económico, medido con el GaR)" en la primera
   mención.

## 3.7 Pendientes que vienen de antes

| # | Qué | Estado |
|---|---|---|
| 1 | La tabla de Argentina del paper excede la página en 13 pt | Pendiente |
| 2 | Zenodo (DOI del repositorio) | Pendiente; lo activa el autor |

---

# 4. Evaluación por criterio

## 4.1 Contribución — 6,3

Las contribuciones son las mismas, pero hoy solo aparecen al final (3.1). Baja una décima respecto de la
reestimación. Vuelve a 6,4 con el párrafo breve de 3.1.

## 4.2 Marco — 6,8

Sin cambios. La pasada de estilo dejó el marco más legible sin tocar sus fuentes.

## 4.3 Datos — 6,5

Sube una décima: el WGI real elimina el último dato marcado como provisional en el Anexo B (3.4).

## 4.4 Identificación — 5,8

Sin cambios. Sigue siendo el techo estructural de la tesis.

## 4.5 Inferencia — 7,0

Sin cambios.

## 4.6 Interpretación — 6,9

- **A favor:** el resumen ya no contradice los resultados.
- **En contra:** el doble uso de "amplificación" (3.2) puede hacer que un lector vea una contradicción con el
  hallazgo central. Baja una décima.

## 4.7 Estructura — 6,5

La prosa mejora con la pasada de estilo, pero la introducción sin hallazgos y la tipografía mixta compensan.
Queda igual.

## 4.8 Reproducibilidad y transparencia — 6,8

La reproducibilidad está intacta (140 de 140). La transparencia baja dos décimas porque el anexo de IA no
declara la pasada de estilo y sus cifras están desactualizadas (3.3). Es lo más importante de esta ronda, no
por la nota, sino por la integridad.

---

# 5. Acciones, en orden de costo

| # | Acción | Costo | Efecto |
|---|---|---|---|
| 1 | "no se han cruzado" → "casi no se han cruzado" (introducción) | 1 min | Estructura (incluido en 6) |
| 2 | Resumen: la cifra del horizonte de un año (4,7 %) y el enlace entre vulnerabilidad y riesgo económico | 5 min | Interpretación (incluido en 3) |
| 3 | Reservar "amplificación" para H3; para la deuda, "intensifica" o "eleva", en los ~12 lugares de 3.2 | 30 min | Interpretación +0,1 |
| 4 | Anexo de IA: cifras al 28 de octubre, la pasada de estilo con su verificación y un prompt representativo; una línea en la declaración preliminar | 30 min | Transparencia +0,2 |
| 5 | Al final de 1.2: muestra, respuesta y contribuciones en tres o cuatro oraciones (texto a aprobar por el autor) | 20 min | Contribución +0,1 |
| 6 | Tipografía del signo de porcentaje unificada | 15 min | Estructura +0,1 |
| 7 | Nota en NUMEROS sobre la fecha y la muestra de `causal_bbg.csv` | 5 min | — |

| Criterio | Hoy | Con las acciones 1–7 |
|---|---|---|
| Contribución | 6,3 | 6,4 |
| Marco | 6,8 | 6,8 |
| Datos | 6,5 | 6,5 |
| Identificación | 5,8 | 5,8 |
| Inferencia | 7,0 | 7,0 |
| Interpretación | 6,9 | 7,0 |
| Estructura | 6,5 | 6,6 |
| Reproducibilidad | 6,8 | 7,0 |
| **Ponderada** | **6,51** | **6,56** |

**El techo.** Sigue en la identificación (20 %) y en una contribución sin un resultado positivo nuevo que
sobreviva a la corrección conjunta. El análisis aparte de gobernanza no lo cambia, porque tampoco pasa su
corrección, pero da una respuesta preparada si la comisión pregunta por las instituciones: la gobernanza se
asocia con spreads menores dentro del país (Holm 0,063), y el ESG ambiental y social no.

**Para la defensa.** Si alguien pregunta por qué "la deuda amplifica" si "no hay amplificación", la respuesta
corta es: "Son dos preguntas distintas. La amplificación de la tesis es la de los dos riesgos juntos, y no
aparece. La deuda intensifica la transmisión del riesgo de cola en esta muestra, pero no se confirma fuera de
ella". Después de la acción 3, la pregunta ya no debería surgir.
