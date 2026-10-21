---
title: "Evaluación experta de la tesis"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — rúbrica, nota y propuesta de mejoras (21 de octubre de 2026)"
---

*Evaluación hecha como la haría un economista de la comisión, sobre la versión vigente de la tesis
(`4_Redaccion/tesis/main.pdf`, 126 pp., compilada el 21-oct-2026; commit `c39d1c5`). Las métricas no
son del autor: JLoss es de Chari et al. (2024) y el GaR, de Adrian, Boyarchenko y Giannone (2019) con la
plataforma de CEMLA. Todo lo que se evalúa son asociaciones, no efectos causales. Las cifras nuevas de
este informe se calcularon con scripts independientes del pipeline (sección 3) y no se han incorporado a
la tesis.*

---

# 1. Estándar de evaluación

**Pauta oficial.** No encontré publicada la pauta de evaluación de tesis del Magíster en Economía
Aplicada (Departamento de Ingeniería Industrial, FCFM). Lo único disponible en línea son manuales
antiguos de los magísteres de la Facultad de Economía y Negocios (2013 y 2015), que exigen una tesis
"de la calidad de un artículo para una revista académica con comité editorial". Uso por eso una
**rúbrica proxy**, en la escala chilena de 1,0 a 7,0 con aprobación en 4,0, y conviene confirmarla con
la coordinación del programa.

| # | Criterio | Peso |
|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % |
| 2 | Marco teórico y literatura | 10 % |
| 3 | Datos y construcción de las métricas | 15 % |
| 4 | Estrategia empírica e identificación | 20 % |
| 5 | Inferencia y robustez | 15 % |
| 6 | Interpretación: conclusiones proporcionales a la evidencia | 15 % |
| 7 | Redacción, estructura y extensión | 5 % |
| 8 | Reproducibilidad y transparencia | 5 % |

Niveles: 7,0 excepcional o publicable · 6,0 muy bueno · 5,0 bueno con debilidades relevantes ·
4,0 suficiente · <4,0 insuficiente.

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte |
|---|---|---|---|---|
| 1 | Pregunta y contribución | 15 % | 5,8 | 0,87 |
| 2 | Marco teórico y literatura | 10 % | 6,0 | 0,60 |
| 3 | Datos y métricas | 15 % | 5,8 | 0,87 |
| 4 | Estrategia e identificación | 20 % | 5,5 | 1,10 |
| 5 | Inferencia y robustez | 15 % | 6,8 | 1,02 |
| 6 | Interpretación | 15 % | 6,2 | 0,93 |
| 7 | Redacción y estructura | 5 % | 5,3 | 0,27 |
| 8 | Reproducibilidad | 5 % | 6,8 | 0,34 |
| | **Nota ponderada del documento** | | | **6,0** |

**Rango según cómo lo lea la comisión y qué se mejore antes de diciembre:**

- **Pesimista (5,5):** la comisión pondera la ausencia de resultados identificados y la saturación de JLoss.
- **Central (6,0):** el documento actual.
- **Optimista (6,5):** se ejecutan las mejoras A1–A5 y B6–B7 de la sección 6.

**En una frase:** en rigor inferencial y transparencia, la tesis está muy por sobre el estándar de un
magíster. Su contribución sustantiva queda acotada porque la hipótesis central (amplificación) no se
sostiene, H1 y H2 no se distinguen del sesgo de retroalimentación y la métrica de fragilidad está
saturada. La comisión premiará la honestidad, pero preguntará qué se aprende en positivo.

---

# 3. Verificación empírica independiente

Escribí scripts propios que no reutilizan el código del proyecto (en el scratchpad de la sesión; no
están en el repositorio) sobre `1_Codigo/Panel/bbg/Panel_bloomberg_embiext.csv`, excluyendo Argentina,
Corea, Bulgaria y Hungría.

| Qué | Tesis | Réplica | Veredicto |
|---|---|---|---|
| N, países, ventana | 765, 13, 2004Q2–2026Q2 | 765, 13, 2004Q2–2026Q2 | ✔ |
| β₁ ln JLoss (DK p) | 0,0985 (0,003) | 0,0985 (0,003) | ✔ |
| β₂ D (DK p) | 0,032 (0,033) | 0,0324 (0,033) | ✔ |
| β₃ interacción (DK p) | −0,011 (0,11) | −0,0112 (0,112) | ✔ |
| Niveles γ₁, γ₂, γ₃ | 4,7; 3,2 (p 0,27); 0,25 (p 0,34) | 4,73; 3,24 (0,268); 0,246 (0,344) | ✔ solo con regresores **centrados** |
| Observaciones cerca del piso 2,16 | 23,7 % | 22,5 % (criterio ±2 %) | ✔ (diferencia de criterio) |
| Precedencia ln JLoss→D | 0,405 (DK 0,009) | 0,412 (DK 0,009) | ✔ |

**Revisión del código.** El wild cluster bootstrap (`p32_aporte_riesgo_cola.py:98`) es correcto:
restringido bajo la nula, con pesos de Webb, Wald cluster con corrección G/(G−1) y efectos fijos
parcializados por FWL. La permutación de la simultaneidad (`p32_aporte_riesgo_cola.py:451`) desplaza
circularmente el indicador de D **por separado en cada país**. Eso conserva la persistencia, pero rompe
la alineación con el calendario común, y es la debilidad del punto 4.1.

**Tres pruebas nuevas que cambian la lectura** (no están en la tesis):

1. **Simultaneidad con una nula que conserva el calendario.** Al permutar el indicador de D entre países
   dentro de cada trimestre (4.999 réplicas), lo esperado es 140,8, no 87. La razón es **1,19** y
   p = 0,0002. **La simultaneidad sobrevive, pero su magnitud honesta es de 1,2–1,3 veces, no "el
   doble".**
2. **Precedencia sin un país a la vez.** El coeficiente va de 0,33 (sin Brasil, p = 0,063) a 0,48 (sin
   Perú) y es significativo al 5 % en 12 de las 13 exclusiones.
3. **Precedencia con el GaR sin bloque bursátil** (`gar_insample_noSTX.csv`): 0,387 (p < 0,001), frente
   a 0,309 con la versión base dentro de la muestra. **La precedencia no la explican los precios
   accionarios que comparten el FCI y JLoss.** Quedan dos de los tres límites que la tesis declara: el
   rezago único y el fechado dentro del trimestre.

---

# 4. Evaluación por criterio

## 4.1 Pregunta y contribución — 5,8
- **A favor:** la pregunta es relevante y original. Cruzar la fragilidad bancaria con la cola doméstica
  del crecimiento en el precio soberano es un cruce real, y la brecha está bien argumentada
  (`01_introduccion.tex:52-59`).
- **En contra:** la pregunta se reformuló después de los resultados. De "¿la coincidencia amplifica el
  spread?" pasó a "¿qué agrega el riesgo económico y qué pasa cuando coinciden?". El historial (README,
  `Defensa_preguntas.md`) muestra que el hallazgo original, θ en el núcleo de 11, se abandonó. La tesis
  lo declara (`03_metodologia.tex:195,226`), pero la contribución queda en "réplica + documentación de
  simultaneidad + nulos informativos".
- **Lo que más rinde:** la simultaneidad y la precedencia fragilidad→cola, que salieron mejor paradas de
  lo que la tesis dice (sección 3), son la contribución positiva más defendible y hoy están
  subvendidas.

## 4.2 Marco teórico — 6,0
- **Fortaleza destacada:** la derivación desde los modelos de intensidad (Duffie–Singleton) de que la
  aditividad en logaritmos equivale a proporcionalidad en pb, de modo que la amplificación exige β₃>0
  en log-log (`02_marco_teorico.tex:84-101`). Es un aporte conceptual fino que la comisión va a notar.
- **Debilidades:**
  - La lectura de Farhi–Tirole como "producto y no suma" (`02_marco_teorico.tex:20`) es más fuerte que
    lo que el modelo entrega en forma reducida.
  - La literatura es poco reciente: aparte de Chari et al., casi no hay referencias de 2023 en
    adelante.
  - Falta el marco **Debt-at-Risk** del FMI (Fiscal Monitor, oct. 2024), que lleva la lógica de riesgo
    de cola a la dinámica de deuda soberana. Debilita la frase "su conexión con el precio del riesgo
    soberano está inexplorada" (`02_marco_teorico.tex:66`).

## 4.3 Datos y métricas — 5,8
- **A favor:**
  - El esfuerzo de construcción es grande y bien validado: 113 bancos de Bloomberg con un mismo
    protocolo y el motor reimplementado y validado contra MATLAB.
  - El FCI reproduce a CEMLA (0,9995).
  - La validación del empalme EMBI–GFSR también es sólida (correlación 0,94, razón mediana 1,02).
- **En contra (el problema más serio del documento):**
  - El VaR99 satura la malla en el 98 % de las observaciones y el 22–24 % está en el piso de 2,16. En
    Perú, Malasia y Chile ronda la mitad de la muestra (58 %, 48 % y 45 %).
  - JLoss funciona, en la práctica, como un índice de la pérdida esperada, es decir, de las PD de
    Merton ponderadas. La tesis lo declara con honestidad (`03_metodologia.tex:147`), pero no extrae la
    consecuencia natural: probar la PD/DD media directamente o la malla ancha en la especificación
    principal.
- **Menor:**
  - Los controles son anuales interpolados.
  - El EMBI de Indonesia y Sudáfrica viene en 20 de 32 trimestres del FMI.
  - Filipinas aporta solo 12 trimestres.

## 4.4 Estrategia e identificación — 5,5
- **A favor:**
  - La especificación es coherente con la hipótesis: rezagos justificados, EF bidireccionales y la
    batería de Chari.
  - La discusión del "mal control" es correcta.
  - El fechado del spread (promedio frente a cierre) es una prueba de muy buen nivel.
- **En contra:**
  - La simulación VAR propia muestra que la retroalimentación por sí sola produce coeficientes del
    tamaño observado: 0,066 frente a 0,099 en H1 y 0,022 frente a 0,032 en H2
    (`04_resultados.tex`, sección de identificación).
  - El IV shift-share falla (signos opuestos, Sargan rechaza).
  - Con los 6 controles, H1 desaparece (−0,008).
  - En suma, no hay ningún resultado sobre el spread que esté identificado. El guía dijo en la
    predefensa que la causalidad no es requisito, y eso evita que la nota baje más. Pero un 7 exige al
    menos un diseño con variación plausiblemente exógena.

## 4.5 Inferencia y robustez — 6,8
Es lo mejor del trabajo y supera lo habitual incluso en papers publicados:
- simulación propia de tamaño y potencia con tres procesos generadores, que fija la regla de lectura;
- wild cluster bootstrap con Webb;
- Holm en tres familias;
- una prueba **preespecificada** con su consecuencia fijada de antemano;
- bandas de aditividad que convierten el nulo en un intervalo informativo;
- Box–Cox y fixed-b.

**Descuento:** la nula de la permutación de la simultaneidad no conserva el calendario común (sección
3). Hay además un riesgo de "jardín de senderos" por la cantidad de familias de pruebas (más de 30),
aunque la escala firme/sugerente/exploratorio lo mitiga.

## 4.6 Interpretación — 6,2
- **A favor:** el lenguaje es disciplinado (asociaciones, "no se rechaza" frente a "se descarta",
  aditivo frente a amplificación) y cada conclusión lleva su salvedad.
- **Sobreafirmado:**
  - "Los dos riesgos coinciden el doble de lo esperado" (`04_resultados.tex:327`) y el "1,9 veces" como
    cifra principal, cuando la cifra neta del calendario es de 1,2–1,3.
  - **Error factual:** la introducción describe el 1,3 como lo esperado "si se controlan los períodos
    de crisis" (`01_introduccion.tex:158`). En realidad es neto de las frecuencias de cada año, y fuera
    de las crisis la razón es 1,8.
- **Subafirmado:** la precedencia fragilidad→cola se califica de "sugerente" por no tener exclusión de
  país; esa prueba ahora existe y la pasa, como también la del GaR sin bloque bursátil.

## 4.7 Redacción y estructura — 5,3
- 126 pp. y unas 35 mil palabras en los capítulos. El de resultados (1.131 líneas de LaTeX) tiene 8
  secciones y más de 20 subsecciones, y las salvedades se repiten casi literalmente en el resumen, la
  introducción, la síntesis, la discusión y las conclusiones.
- Hay un desajuste de estructura: el marco plantea tres hipótesis (H1–H3), pero los resultados se
  organizan en "cuatro conclusiones" que no se corresponden una a una con ellas.
- Detalles:
  - falta un signo de puntuación en el resumen (`main.tex:85`: "es un hecho} los dos riesgos");
  - hay líneas en blanco sobrantes en el resumen;
  - la ecuación de niveles (`03_metodologia.tex:190`) no declara que los regresores van centrados,
    algo necesario para leer γ₁ y γ₂.

## 4.8 Reproducibilidad — 6,8
- Las cifras centrales se replicaron exactamente con código independiente, el pipeline está documentado
  y cada número cita su fuente.
- **Descuento:** documentos públicos desactualizados que un evaluador puede abrir:
  - el `README.md` raíz (N=721, "θ=−0,47 en el núcleo de 11 — el hallazgo central", IV con F≈11);
  - `4_Redaccion/Defensa_preguntas.md` (θ=−0,26, capítulo del modelo OI que ya no existe).

---

# 5. Preguntas probables de la comisión (no cubiertas en `Defensa_preguntas.md`, que está desactualizado)

1. **"Si H3 no se sostiene y H1–H2 no se distinguen del sesgo, ¿qué aprendemos en positivo?"**
   Respuesta: (i) los dos riesgos coinciden más que por azar incluso neto del calendario (1,2×,
   p = 0,0002); (ii) la fragilidad antecede a la cola del crecimiento, robusto a excluir países y a
   quitar el bloque bursátil; (iii) la amplificación mayor al 30–40 % de la suma queda descartada.
2. **"Si JLoss satura en el 98 % de los casos, ¿por qué no usar directamente la PD media de Merton?"**
   (Hoy no hay respuesta empírica: es la mejora B6.)
3. **"¿La simultaneidad no es solo 2020?"** Respuesta: en 2020–22 lo observado ≈ lo esperado según el
   calendario, y el exceso viene de 2015–19 y 2023–26.
4. **"¿Por qué cambió de CDS a EMBI, de niveles a logs y de contemporáneo a rezago? ¿Cuál fue primero?"**
   (Mejora A4.)
5. **"Turquía aporta el 70 % de β₁ y Polonia el signo de β₃: ¿hay un resultado común?"**
6. **"¿Qué diferencia hay entre su resultado de aditividad y la proporcionalidad mecánica del logaritmo?"**
   (Fortaleza: la respuesta del marco es muy buena.)
7. **"El pronóstico fuera de muestra no usa el GaR recursivo ni EF de tiempo: ¿por qué incluirlo?"**
8. **"¿Cómo se relaciona su trabajo con Debt-at-Risk del FMI?"**
9. **"La prueba preespecificada está registrada en el encabezado del código y no en un registro externo
   fechado. ¿Cómo lo acredita?"** (Corrección del 21-oct: el historial de git **no** la respalda,
   porque `p26_participacion_extranjera.py` se commiteó por primera vez el 21-oct junto con sus
   resultados. La respuesta honesta es reconocerlo; ver `Defensa_preguntas.md`, V11.)
10. **"La precedencia JLoss→GaR: ¿es acelerador financiero o el suavizamiento EWMA del FCI?"** (Mejora
    B7: queda descartado el bloque bursátil; falta el fechado.)

---

# 6. Propuesta de mejoras

Prioridad = impacto en la nota ÷ costo. Plazo: primera semana de diciembre de 2026. Rige la regla del
proyecto: cada prueba se reporta salga como salga y, si debilita una conclusión, se corrige en la tesis,
el paper y las láminas.

## A. Bajo costo, antes de la defensa (redacción y coherencia) — impacto estimado +0,2 a +0,3

| # | Mejora | Ataca | Archivos | Costo |
|---|---|---|---|---|
| A1 | Jerarquizar resultados: un resultado por hipótesis en el cuerpo, el resto de la batería al anexo, y una tabla única "hipótesis → prueba → veredicto" que alinee H1–H3 con las cuatro conclusiones | 4.7 | `04_resultados.tex`, `anexo_tablas.tex`, `05_discusion.tex` | 2–3 días |
| A2 | Recalibrar la simultaneidad: cifra principal 1,2–1,3× con la permutación dentro del trimestre (p = 0,0002); corregir "el doble" y la frase errónea sobre las crisis | 4.6, 4.5 | `main.tex` (resumen), `01_introduccion.tex:158`, `04_resultados.tex:327`, síntesis, `05`, `06`, `defensa.tex:474`; agregar la permutación a `p32_aporte_riesgo_cola.py` | 1 día |
| A3 | Formalizar la "no amplificación" con una prueba de equivalencia (TOST) contra un margen declarado (p. ej., 40 % de la suma) y el efecto mínimo detectable | 4.5, 4.6 | `p32_aporte_riesgo_cola.py` (función `bandas`), `04_resultados.tex` | 0,5 día |
| A4 | Recuadro con la cronología de decisiones de especificación (CDS→EMBI, niveles→logs, contemporáneo→rezago, núcleo de 11 → exploratorio, prueba preespecificada del 13-oct), con commits y fechas | 4.1 | `03_metodologia.tex` | 0,5 día |
| A5 | Actualizar `README.md` y `Defensa_preguntas.md` a la versión vigente; corregir el resumen (puntuación, líneas en blanco) y declarar el centrado en la ecuación de niveles | 4.7, 4.8 | `README.md`, `Defensa_preguntas.md`, `main.tex:85`, `03_metodologia.tex:190` | 1 día |
| A6 | Agregar Debt-at-Risk (FMI 2024) y literatura reciente del nexo banca–soberano en emergentes; matizar "inexplorada" | 4.2 | `02_marco_teorico.tex`, `referencias.tex` | 1 día |

## B. Costo medio, antes de la defensa si el tiempo alcanza (econometría) — impacto estimado +0,2 a +0,3

| # | Mejora | Ataca | Archivos | Costo |
|---|---|---|---|---|
| B6 | **Fragilidad sin saturación:** reestimar la principal con (a) el JLoss de malla ancha (`_engine_wide.py` → `_robustez_widebounds.py`, hoy solo en niveles) en log-log y (b) la PD o DD media de Merton ponderada por activos; tratar el piso con un indicador "en piso" interactuado o con estimación censurada | 4.3 | nuevo `p33_fragilidad_alternativa.py`; `04_resultados.tex` (sección de robustez a la medición) | 3–4 días |
| B7 | **Ascender la precedencia fragilidad→cola:** incorporar las dos pruebas de la sección 3 (exclusión de un país, GaR sin bloque bursátil) y agregar la prueba de fechas (JLoss de mitad de trimestre, o DD con precios del primer mes) y 2–4 rezagos | 4.1, 4.6 | `p32_aporte_riesgo_cola.py` (función `bloque_simultaneidad`), `04_resultados.tex:329` | 2 días |
| B8 | **Amplificación en la cola del spread:** regresión cuantílica de panel del ln EMBI (Machado–Santos Silva, ya citado) con la interacción en τ = 0,75 y 0,9, que son los estados que predice la teoría. Revisar primero el experimento no lineal del commit `e98e42b` | 4.4 | nuevo script; `04_resultados.tex` | 2–3 días |

## C. Para el paper o una extensión posterior a la tesis — alto costo y alto impacto en la contribución

| # | Mejora | Ataca |
|---|---|---|
| C9 | **Instrumento granular (Gabaix–Koijen):** choques idiosincrásicos a los retornos de los bancos grandes, con los 113 bancos de `Bloomberg_extraction/output/`, como variación de la fragilidad que no pasa por el spread. Es la mejora con más potencial para pasar de asociaciones a efectos | 4.4 |
| C10 | **Frecuencia mensual:** JLoss mensual desde la capitalización diaria y el EMBI diario. Multiplica T, resuelve el fechado y ordena los movimientos dentro del trimestre | 4.4, 4.6 |
| C11 | **Más países y más historia:** completar el EMBI de Indonesia, Filipinas, Sudáfrica e India antes de 2012 y homologar el GaR de Argentina | 4.3, 4.5 |
| C12 | **Estudio de eventos** en torno a los anuncios de líneas swap y FCL | 4.4 |

**Ruta recomendada hasta diciembre:** A2 y A5 primero (corrigen errores visibles, 2 días); después A1,
A3 y A4; si queda tiempo, B7 (la mitad ya está hecha) y B6 (responde la pregunta más probable sobre la
métrica). B8 y el bloque C quedan para el paper.

---

# 7. Registro de aplicación (21 de octubre de 2026)

| # | Estado | Qué se hizo | Resultado |
|---|---|---|---|
| A1 | **Parcial** | Tabla única "hipótesis → prueba → veredicto" al inicio de los resultados (`tab:veredictos`, tesis y paper) | El capítulo sigue largo; queda pendiente decidir qué secciones pasan al anexo |
| A2 | Hecho | `p33`: permutación dentro del trimestre; texto corregido en el resumen, la introducción (error del "1,3 = crisis"), los resultados, la discusión, las conclusiones, el paper, la carta y las láminas | 1,19× (p = 0,0002); fuera de crisis 1,33×; 2015–19 2,9×; 2020–22 1,01× |
| A3 | Hecho | TOST en `p33`; párrafo en las bandas; "no se descarta 30–40 %" reemplazado en todos los documentos | Se rechaza una amplificación de más de un 35 % de la suma (logaritmos: 0,4 / 13 / 22 %; pb: 29 / 34 / 35 %) |
| A4 | Hecho | Recuadro de cronología en la metodología (párrafo en el paper) | **Hallazgo:** `p26` (prueba "preespecificada") se commiteó por primera vez el 21-oct; el repositorio no acredita la fecha del 13-oct. Se declaró en la cronología y en las limitaciones |
| A5 | Hecho | README reescrito; `Defensa_preguntas.md` con la sección V vigente (A–G quedan como archivo); resumen corregido; centrado declarado en la ecuación de niveles | — |
| A6 | Hecho | Debt-at-Risk (FMI 2024) y Gelos et al. (2022) en el marco | "Inexplorada" matizado |
| B6 | Hecho | `p34`: PD y DD de Merton ponderadas por pasivos, y malla ancha | Con −DD_w, β₁ wild 0,055 (pb: 0,048), frente a 0,32 con JLoss; β₃ sigue nulo en logaritmos. La malla ancha (sin India) debilita β₁ |
| B7 | Hecho | Exclusión de un país, GaR sin bloque bursátil y 2–4 rezagos en `p33` | Precedencia firme a un trimestre (0,32–0,47; 0,388 sin el bloque); con 3–4 rezagos el wild no rechaza |
| B8, C9–C12 | Pendiente | — | — |

Cifras registradas en `NUMEROS_CANONICOS_BBG.md`, §19 y §20. La tesis (130 pp.), el paper (114 pp.) y
las láminas (61) compilan sin referencias indefinidas.

**Nota reestimada tras la aplicación (mismo método de la sección 2):**
- Contribución: 5,8 → 6,0.
- Marco: 6,0 → 6,2.
- Datos: 5,8 → 6,1.
- Interpretación: 6,2 → 6,5.
- Estructura: 5,3 → 5,6.
- Identificación (5,5), inferencia (6,8) y reproducibilidad (6,8): sin cambio.

**Nota ponderada: 6,2.** El techo sigue fijado por la identificación y por la extensión del capítulo de
resultados.

## Fuentes de la sección 1 y 4.2
- [Manual del alumno, Magíster en Economía, U. de Chile (2013)](https://econ.uchile.cl/uploads/userfiles/files/Manual%20Alumno%20Magister%20Economia%202013.pdf)
- [Manual de inducción MAE, U. de Chile (2015)](https://econ.uchile.cl/uploads/userfiles/files/Manual%20Inducci%C3%B3n%20MAE%202015(1).pdf)
- [FMI, Fiscal Monitor, octubre 2024, anexos en línea (Debt-at-Risk)](https://imf.org/-/media/Files/Publications/fiscal-monitor/2024/October/English/onlineannexes.ashx)
