---
title: "Ficha de lectura: Chari et al. (2024)"
subtitle: "EP7000 · Laboratorio 4 · Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano"
---

## Objetivo de lectura o tarea de escritura

**Estado de avance:** marco teórico redactado. La lectura busca el sustento teórico y empírico
fundamental de la propuesta.

**Propósito.** Es la fuente de la métrica de fragilidad bancaria ($JLoss$) y del resultado que la tesis
replica: que la fragilidad bancaria se asocia con el spread soberano en economías emergentes. Se lee
para (i) precisar la definición e interpretación de $JLoss$ (Sección 2.1.2 de la tesis); (ii) fijar qué
está ya establecido y qué no, para delimitar la brecha (Sección 2.4); y (iii) comparar la especificación
de los autores con la de la tesis (Capítulo 3 y réplica del Capítulo 4).

**Trabajo que se escribe a partir de ella.** El Capítulo 2 (Marco teórico) y la réplica del Capítulo 4.
Es un texto académico de tesis de magíster, en español, con citas autor–año.

## Datos de los autores

- **Anusha Chari.** University of North Carolina at Chapel Hill, Estados Unidos.
- **Felipe Garcés.** Banco Central de Chile.
- **Juan Francisco Martínez.** Itaú (Chile). Es además el profesor guía de esta tesis.
- **Patricio Valenzuela** (autor de correspondencia). Universidad de los Andes, Chile.

La afiliación es la que declara el artículo (p. 1).

## Referencia completa (APA 7)

Artículo de revista científica (AIC).

Chari, A., Garcés, F., Martínez, J. F., & Valenzuela, P. (2024). Sovereign credit spreads, banking
fragility, and global factors. *Journal of Financial Stability*, *72*, Artículo 101235.
https://doi.org/10.1016/j.jfs.2024.101235

## Resumen

El artículo estudia cómo se relacionan el riesgo de crédito soberano, la fragilidad del sistema bancario y
los factores financieros globales en un panel trimestral de economías emergentes. Para medir la
fragilidad construye $JLoss$, una métrica semiparamétrica que calcula la pérdida conjunta esperada del
sector bancario de cada país condicional a un evento sistémico. Encuentra dos resultados. Primero, $JLoss$
se asocia positivamente con el spread soberano (EMBI Global), aun controlando por los determinantes
habituales, por medidas de riesgo sistémico y por efectos fijos de país y de tiempo. Segundo, los países
con sistemas bancarios más frágiles están más expuestos a los factores financieros globales (VIX, tasa
del Tesoro, spread de alto rendimiento, iliquidez). Concluye que la estabilidad bancaria es una condición
para reducir el costo de endeudamiento soberano y la exposición al ciclo global.

## Palabras clave

Fragilidad bancaria · $JLoss$ · pérdida conjunta esperada · método de punto de silla · spread soberano
(EMBI) · factores financieros globales · economías emergentes · costo de rescate · efectos fijos de país y
tiempo.

## Ideas principales por apartado

1. **Motivación (pp. 1–2).** Las crisis de 2008–09 y del euro, con grandes pérdidas bancarias, ampliaron
   los spreads soberanos por la expectativa de apoyo público a los bancos. La literatura trata los
   fundamentos, los factores globales y la fragilidad bancaria como determinantes independientes. El
   artículo aporta (i) una medida nueva de fragilidad; (ii) evidencia para emergentes, no solo Europa;
   (iii) el canal por el cual la fragilidad amplifica los factores globales.
2. **La métrica $JLoss$ (pp. 2–6).** Probabilidades de incumplimiento por banco con un modelo tipo Merton
   (1974); exposición aproximada por los pasivos; pérdida dado incumplimiento de 45%; correlación de los
   retornos bancarios con un factor sistémico; agregación por punto de silla con siete nodos de cuadratura.
   Las pérdidas se acotan entre 1% y 4,8% (Tabla 1, p. 3). Se distingue de SRISK (que suma déficits sin
   correlación) y de CIMDO-copula (Segoviano y Goodhart, 2009).
3. **Datos (pp. 6–8).** Panel trimestral no balanceado de 19 emergentes; 1406 observaciones. Spread:
   EMBI Global (Bloomberg). Controles: calificación S&P, deuda/PIB, volatilidad cambiaria, margen bancario,
   PIB per cápita. Factores globales: VIX, tasa del Tesoro a 10 años, spread de alto rendimiento y
   diferencial *on/off-the-run*.
4. **Resultados (pp. 8–10).** Regresión log-log del spread sobre $JLoss$ rezagado, con efectos fijos de país
   y tiempo: duplicar $JLoss$ se asocia con un spread 22% mayor (13% con controles). Las interacciones con
   los factores globales son positivas: la fragilidad amplifica su efecto.
5. **Robustez (pp. 10–12).** Separa períodos de crisis y de calma, controla por no linealidades de los
   factores globales, por 20 medidas de riesgo sistémico y por la probabilidad media de incumplimiento, y
   usa el CDS soberano como variable dependiente. Los resultados se mantienen.
6. **Conclusión (pp. 12–14).** La estabilidad del sistema bancario reduce el riesgo soberano y su
   sensibilidad a los factores globales; recomienda políticas orientadas a esa estabilidad.

## Citas relevantes

> "The literature has recently emphasized that the primary factors that affect sovereign credit risk are
> macroeconomic fundamentals, global factors, and banking fragility, which have generally been treated as
> independent determinants of sovereign credit risk." (Chari et al., 2024, p. 1)

*Comentario.* Es el punto de partida del estado del arte: los tres bloques de determinantes se estudian
por separado. La tesis toma el mismo diagnóstico, pero cruza la fragilidad con un riesgo *doméstico*
(la cola del crecimiento), no con los globales.

> "Consistent with the idea that our metric (JLoss) can be understood as the direct cost of bailing out
> the whole banking sector, [...] our results indicate our metric of banking fragility is positively
> associated with sovereign credit spreads." (Chari et al., 2024, p. 2)

*Comentario.* Respalda la interpretación de $JLoss$ como pasivo contingente del soberano (costo esperado
del rescate), que es el pilar 2 del marco conceptual (Sección 2.1.2). Los autores la presentan como
*consistente* con los datos, no como un efecto identificado; la tesis mantiene esa cautela.

> "We employ the lagged value of JLoss to mitigate concerns associated with reverse causality."
> (Chari et al., 2024, p. 8)

*Comentario.* Justifica el rezago de un trimestre que usa la especificación principal de la tesis. La
tesis muestra después que el rezago no basta: la fragilidad y el spread se mueven dentro del mismo
trimestre, por lo que el rezago no asegura precedencia.

> "The identification assumption is that in the absence of domestic banking fragility, the sovereign bond
> spreads are exposed to similar global shocks." (Chari et al., 2024, p. 8)

*Comentario.* Es el supuesto que justifica los efectos fijos de tiempo, que la tesis también usa. Sirve
para explicar por qué el componente global común queda absorbido (Sección 2.2.1 de la tesis).

> "[...] countries with more fragile banking sectors are more exposed to global (exogenous) financial
> factors than those with more resilient banking sectors." (Chari et al., 2024, p. 10)

*Comentario.* Es la interacción que la tesis toma como contraste: Chari et al. interactúan $JLoss$ con
factores globales; la tesis la interactúa con el riesgo de cola doméstico (Sección 2.4, posicionamiento).

> "[...] rigorous research on the nexus between sovereign risk and bank risk in emerging markets is
> scant." (Chari et al., 2024, p. 12)

*Comentario.* Respalda el nicho: la evidencia del nexo es mayoritariamente europea. Se usa en el estado
del arte del nexo banca–soberano (Sección 2.2.3).

## Fuentes relacionadas

- **Antecedentes teóricos:** Merton (1974), base de las probabilidades de incumplimiento; Farhi y Tirole
  (2018) y Acharya, Drechsler y Schnabl (2014), sobre rescates y dilución.
- **Medidas de riesgo sistémico comparables:** Brownlees y Engle (2016, SRISK); Segoviano y Goodhart
  (2009, CIMDO); Huang, Zhou y Zhu (2009); Giglio, Kelly y Pruitt (2016).
- **Determinantes del spread:** González-Rozada y Levy Yeyati (2008); Longstaff et al. (2011); Hilscher y
  Nosbusch (2010); Miranda-Agrippino y Rey (2022).
- **Nexo empírico:** Mody y Sandri (2012); Dieckmann y Plank (2012); Kallestrup, Lando y Murgoci (2016);
  Fratzscher y Rieth (2019).
- **Complemento de la tesis:** Adrian, Boyarchenko y Giannone (2019), para el riesgo de cola del
  crecimiento que el artículo no considera.

## Evaluación final

**Pertinencia.** Muy alta. Es la fuente de la métrica y del resultado que la tesis replica, y define la
frontera desde la que se plantea la pregunta propia. Se ajusta por completo al objetivo de lectura.

**Validez.** Revista indexada de Elsevier con revisión por pares (recibido en 2022, revisado en 2023,
aceptado en 2024). Usa datos de fuentes estándar, efectos fijos de país y tiempo y una batería de
robustez amplia, y publica la métrica para uso externo.

**Límites que la tesis debe tener presentes.**

- Los coeficientes son asociaciones; el rezago de $JLoss$ no resuelve la simultaneidad.
- Hay inconsistencias menores de descripción. La muestra empieza en 2000:Q1 en la p. 2 y en 1999:Q1 en
  la p. 6. El texto dice 19 economías, pero la Tabla 3 lista 18.
- La cota superior de pérdidas de 4,8% (Tabla 1) genera un piso en la métrica: con LGD de 45%, $JLoss$ se
  amontona en $0{,}048 \times 0{,}45 \times 100 = 2{,}16$. La tesis lo documenta.
- Las tablas reportan errores estándar "robustos" sin indicar si se agrupan por país. Con pocos países y
  series persistentes, eso puede subestimar la incertidumbre. Por eso la tesis usa Driscoll–Kraay y
  *wild cluster bootstrap*.

**Dificultades.** El apartado metodológico es denso: punto de silla y cuadratura de Gauss–Hermite. Las
tablas de la versión en PDF se extraen mal.

**Conflicto de interés a declarar.** Uno de los autores es el profesor guía de la tesis. Eso no invalida
la fuente, pero refuerza la necesidad de que la réplica sea independiente y de reportar también lo que
no se replica (la tesis lo hace: con sus propios controles domésticos el coeficiente desaparece).

## Bonus track: evaluación de fuentes (Beas et al., 2008)

| Pregunta | Respuesta |
|---|---|
| **Nombre del artículo** | *Sovereign credit spreads, banking fragility, and global factors* |
| **Autores** | A. Chari, F. Garcés, J. F. Martínez y P. Valenzuela |
| ¿En qué plataforma está publicada? | *Journal of Financial Stability* (Elsevier), vía ScienceDirect, con DOI. |
| ¿Es una organización confiable? | Sí: revista académica con revisión por pares, especializada en estabilidad financiera. |
| ¿De qué año es? | 2024 (disponible en línea el 8 de febrero de 2024). |
| ¿Hay datos de la trayectoria de los autores? | Sí: pertenecen a una universidad estadounidense, al Banco Central de Chile, a la banca chilena y a una universidad chilena (p. 1). |
| ¿Pertenecen a alguna institución que corrobore sus datos? | Sí, las cuatro afiliaciones están declaradas en el artículo. |
| ¿Participan en encuentros donde discuten con otros expertos? | Sí: agradecen comentarios de la *First Conference on Financial Stability and Sustainability* (p. 1). |
| ¿Tiene algún sesgo? | No hay sesgo político ni valórico. Las recomendaciones de política se derivan de correlaciones, y uno de los autores es el profesor guía de esta tesis. |
| ¿Fundamenta sus afirmaciones con datos y referencias? | Sí: panel de 1406 observaciones, tablas de resultados y robustez. |
| ¿Incluye referencias bibliográficas? | Sí, una lista completa al final. |

*Uso en la tesis:* Secciones 2.1.2, 2.2.2, 2.2.3 y 2.4 del Capítulo 2; réplica del Capítulo 4.
