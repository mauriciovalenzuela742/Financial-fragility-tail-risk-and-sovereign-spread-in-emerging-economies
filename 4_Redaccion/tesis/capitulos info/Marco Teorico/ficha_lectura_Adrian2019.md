---
title: "Ficha de lectura: Adrian, Boyarchenko y Giannone (2019)"
subtitle: "EP7000 · Laboratorio 4 · Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano"
---

## Objetivo de lectura o tarea de escritura

**Estado de avance:** marco teórico redactado. La lectura busca el sustento teórico fundamental de la
propuesta.

**Propósito.** Es la fuente del concepto de *Growth-at-Risk* ($GaR$), la medida de riesgo económico de la
tesis: la cola izquierda de la distribución condicional del crecimiento. Se lee para (i) fundamentar por
qué importa la cola y no la media (Sección 2.1.3 de la tesis); (ii) justificar el método (regresión
cuantílica sobre condiciones financieras y ajuste de una *skew-t*), que la tesis aplica con la plataforma
de CEMLA (Sección 3.3); y (iii) ubicar la brecha: esta literatura no llega al spread soberano.

**Trabajo que se escribe a partir de ella.** El Capítulo 2 (pilar del riesgo de cola y estado del arte del
*Growth-at-Risk*) y la sección metodológica del $GaR$.

## Datos de los autores

- **Tobias Adrian.** Fondo Monetario Internacional (al publicar; antes, Banco de la Reserva Federal de
  Nueva York).
- **Nina Boyarchenko.** Banco de la Reserva Federal de Nueva York.
- **Domenico Giannone.** Banco de la Reserva Federal de Nueva York.

Afiliaciones según la portada interior de la versión de trabajo leída.

## Referencia completa (APA 7)

Artículo de revista científica (AIC). La tesis cita la versión publicada:

Adrian, T., Boyarchenko, N., & Giannone, D. (2019). Vulnerable growth. *American Economic Review*,
*109*(4), 1263–1289. https://doi.org/10.1257/aer.20161923

**Versión leída.** Las páginas de las citas corresponden a la versión de trabajo disponible en
`3_Marco_teorico/`. Antes de citar textualmente en la tesis, hay que confirmar la página en la versión
publicada.

Adrian, T., Boyarchenko, N., & Giannone, D. (2017). *Vulnerable growth* (Staff Report No. 794, revisado en
noviembre de 2017). Federal Reserve Bank of New York.

## Resumen

El artículo modela toda la distribución del crecimiento futuro del PIB de Estados Unidos, no solo su
media, en función de las condiciones económicas y financieras actuales. Estima los cuantiles condicionales
por regresión cuantílica sobre el crecimiento actual y el índice de condiciones financieras de la Fed de
Chicago (NFCI), y los suaviza ajustando cada trimestre una distribución *t* asimétrica. El hallazgo
central es una asimetría: los cuantiles bajos varían mucho con las condiciones financieras, mientras los
altos son estables. El riesgo a la baja del crecimiento sube cuando las condiciones financieras se
endurecen, y el riesgo al alza casi no cambia. Los autores lo atribuyen a mecanismos de amplificación del
sector financiero y advierten que la relación también podría no ser causal.

## Palabras clave

*Growth-at-Risk* · riesgo a la baja · distribución condicional del crecimiento · regresión cuantílica ·
condiciones financieras (NFCI) · distribución *t* asimétrica · entropía relativa · *expected shortfall* ·
amplificación financiera.

## Ideas principales por apartado

1. **Introducción (pp. 1–6).** Los pronósticos puntuales ignoran los riesgos alrededor de la media. Al
   modelar toda la distribución, los cuantiles bajos responden a las condiciones financieras y los altos
   no. El método tiene dos etapas: regresión cuantílica y ajuste de una *skew-t*.
2. **Condiciones económicas, financieras y crecimiento (pp. 6–9).** Usa el NFCI (105 indicadores
   financieros) y el PIB real desde 1973. Las pendientes del NFCI cambian mucho entre cuantiles. Las del
   crecimiento actual son estables, por lo que las condiciones económicas no informan sobre las colas.
3. **Cuantificar la vulnerabilidad (pp. 9–15).** La *skew-t* convierte los cuantiles en una densidad
   condicional. La vulnerabilidad se mide con la entropía relativa (a la baja y al alza) y con el
   *expected shortfall* y su contraparte, el *expected longrise*. Las medidas a la baja se mueven con las
   condiciones financieras; las al alza son estables.
4. **Robustez (pp. 15–19).** Las estimaciones fuera de muestra se parecen a las dentro de muestra y están
   bien calibradas en la cola izquierda. El patrón se mantiene con métodos totalmente paramétricos y no
   paramétricos.
5. **Implicaciones teóricas (pp. 19–22).** Los modelos con fricciones financieras resueltos en primer orden
   no generan esta asimetría. Los modelos no lineales con restricciones del intermediario (Brunnermeier y
   Sannikov, 2014; He y Krishnamurthy) sí la generan. La media y la volatilidad condicionales se correlacionan
   negativamente, en línea con la "paradoja de la volatilidad".
6. **Conclusión (pp. 22–23).** Toda la distribución del crecimiento cambia en el tiempo, y su cola izquierda
   depende de las condiciones financieras. Medir la vulnerabilidad ayuda a cuantificar el costo de las
   decisiones de política monetaria.

## Citas relevantes

> "Our main finding is that the estimated lower quantiles of the distribution of future GDP growth exhibit
> strong variation as a function of current financial conditions, while the upper quantiles are stable
> over time." (Adrian et al., 2017, p. 1)

*Comentario.* Es la idea central del pilar 3 de la tesis (Sección 2.1.3): lo que se mueve con las
condiciones financieras es la cola izquierda. Justifica medir el riesgo económico con el cuantil 5% y no
con el crecimiento esperado.

> "This asymmetry in the evolution of the conditional distribution of future GDP growth indicates that
> downside risk to growth varies much more strongly over time than upside risk." (Adrian et al., 2017,
> p. 2)

*Comentario.* Respalda que el riesgo relevante para un acreedor, cuyo pago tiene un perfil de tipo opción,
sea la cola adversa. Es el puente entre el $GaR$ y el precio de la deuda soberana que propone la tesis.

> "[...] economic conditions are uninformative for predicting tail outcomes." (Adrian et al., 2017, p. 8)

*Comentario.* Explica por qué el $GaR$ se construye sobre un índice de condiciones financieras y no solo
sobre el crecimiento pasado. Es relevante para la tesis porque significa que el $GaR$ contiene
información financiera. La tesis lo discute al preguntar si el $GaR$ es circular respecto del EMBI
(Sección 3.3.3).

> "The relationship between financial conditions and downside risk to GDP growth could instead be
> non-causal, with financial conditions merely providing a better signal of negative shocks to the
> economy." (Adrian et al., 2017, p. 4)

*Comentario.* Los propios autores reconocen que la relación puede no ser causal. Respalda la cautela de la
tesis: los coeficientes son asociaciones.

> "[...] the non-linear amplification channel created by constraints on the intermediary sector."
> (Adrian et al., 2017, p. 20)

*Comentario.* Conecta el riesgo de cola con la fragilidad del sector financiero. Es la base para afirmar,
en la Sección 2.1.4, que el riesgo financiero y el riesgo económico se relacionan entre sí.

## Fuentes relacionadas

- **Método:** Koenker y Bassett (1978), regresión cuantílica; Azzalini y Capitanio (2003), distribución
  *skew-t*; Giglio, Kelly y Pruitt (2016), riesgo sistémico y cola de la actividad real.
- **Teoría de la amplificación:** Bernanke, Gertler y Gilchrist (1999), acelerador financiero; Brunnermeier
  y Sannikov (2014); He y Krishnamurthy (2013).
- **Aplicaciones de política:** Prasad et al. (2019), adopción por el FMI; Ossandon Busch et al. (2022),
  plataforma de CEMLA para América Latina, base de la estimación de la tesis.
- **Condiciones financieras:** Hatzius et al. (2010); Brave y Butters (2012).
- **Complemento de la tesis:** Chari et al. (2024), que mide el riesgo financiero que la tesis cruza con
  el $GaR$.

## Evaluación final

**Pertinencia.** Muy alta. Define el concepto y el método de la métrica de riesgo económico. Responde al
objetivo de lectura en lo conceptual y en lo metodológico.

**Validez.** Publicado en la *American Economic Review*, una de las revistas de economía de mayor
prestigio. Los autores son investigadores de la Reserva Federal de Nueva York y del FMI. El trabajo pasó
por revisión de editor y árbitros, que se agradecen en la versión leída. Es la referencia que adoptaron el
FMI y los bancos centrales.

**Límites que la tesis debe tener presentes.**

- La evidencia es para Estados Unidos, con un índice de 105 indicadores. En emergentes, el índice de
  condiciones financieras es más pobre: en la tesis tiene tres bloques (accionario, de tasas y
  cambiario), con dos indicadores cada uno, y la estimación depende de la plataforma de CEMLA.
- La relación puede no ser causal, como reconocen los autores.
- El artículo no trata el riesgo soberano: el paso del $GaR$ al spread es la contribución de la tesis, no
  de esta fuente.
- La versión leída es la de trabajo, no la publicada, lo que obliga a verificar páginas antes de citar.

**Dificultades.** Hay conceptos técnicos (entropía relativa, transformada integral de probabilidad) y
fórmulas que el PDF extrae mal. La organización interna es clara y el texto es extenso.

## Bonus track: evaluación de fuentes (Beas et al., 2008)

| Pregunta | Respuesta |
|---|---|
| **Nombre del artículo** | *Vulnerable Growth* |
| **Autores** | T. Adrian, N. Boyarchenko y D. Giannone |
| ¿En qué plataforma está publicada? | *American Economic Review* (American Economic Association), con DOI. La versión de trabajo está en la serie *Staff Reports* de la Fed de Nueva York. |
| ¿Es una organización confiable? | Sí: revista con revisión por pares, de las más citadas de la disciplina. |
| ¿De qué año es? | 2019 (versión de trabajo de 2016, revisada en 2017). |
| ¿Hay datos de la trayectoria de los autores? | Sí: investigadores de la Reserva Federal de Nueva York y del FMI (portada interior). |
| ¿Pertenecen a alguna institución que corrobore sus datos? | Sí: Fed de Nueva York y FMI. |
| ¿Participan en encuentros donde discuten con otros expertos? | Sí: agradecen comentarios de CFE-CMStatistics 2015, el NBER EF&G, el BCE, SED 2017 y ESSFM 2017, entre otros. |
| ¿Tiene algún sesgo? | No hay sesgo político ni valórico. La mirada es de banca central, centrada en Estados Unidos. Advierten que la relación puede no ser causal y que no representan la posición de sus instituciones. |
| ¿Fundamenta sus afirmaciones con datos y referencias? | Sí: datos públicos (FRED, BEA, Fed de Chicago), pruebas fuera de muestra y métodos alternativos. |
| ¿Incluye referencias bibliográficas? | Sí, una lista completa al final. |

*Uso en la tesis:* Secciones 2.1.3, 2.1.4 y 2.2.4 del Capítulo 2; Sección 3.3 (estimación del $GaR$).
