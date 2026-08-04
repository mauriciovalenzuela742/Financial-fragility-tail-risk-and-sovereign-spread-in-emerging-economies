# Plan de trabajo — Arista de Organización Industrial

## Modelo teórico formal: competencia bancaria, fragilidad sistémica ($JLoss$), riesgos a la baja ($GaR$) y spread soberano ($EMBI$)

**Documento de gestión de investigación.** Objetivo: construir un modelo teórico formal *nuevo* en el que la estructura de mercado bancario (intensidad de competencia) sea el parámetro profundo que gobierna la cadena $\text{estructura} \rightarrow JLoss \rightarrow GaR \rightarrow EMBI$, generando predicciones testeables que posteriormente se contrastarán con los datos disponibles (balances CMF, Merton/saddle-point, regresiones cuantílicas, EMBI). El plan está diseñado para avanzar de forma **ordenada** (fases secuenciales con dependencias explícitas) y **teóricamente verificable** (cada resultado tiene un criterio de validación interno antes de pasar a la fase siguiente).

---

## 0. Delimitación y contribución marginal

### 0.1 Pregunta de investigación de la arista OI
¿Cómo la intensidad de competencia bancaria determina, en equilibrio, la forma de la **cola conjunta de pérdidas** del sistema ($JLoss$) y, a través de ella, la magnitud del riesgo de crecimiento a la baja ($GaR$) y su transmisión al riesgo soberano ($EMBI$) en economías en desarrollo?

### 0.2 Hipótesis teórica central
La competencia opera sobre el riesgo sistémico por **dos canales de signo opuesto** (efecto margen vs. efecto risk-shifting), pero —a diferencia de la literatura de OI bancaria estándar, centrada en el riesgo *individual*— la estructura de mercado afecta además la **correlación de exposiciones** entre bancos. Por tanto la concentración no solo desplaza la probabilidad de default individual, sino que **engrosa la cola conjunta** ($JLoss$), amplificando el traspaso $JLoss \rightarrow GaR \rightarrow EMBI$.

### 0.3 Contribución respecto a la literatura existente
- Frente a Keeley (1990) y Boyd–De Nicoló (2005): se integran ambos canales en un mismo equilibrio, en la línea de Martínez-Miera y Repullo (2010), pero el objeto de interés deja de ser el riesgo individual y pasa a ser el **riesgo de cola conjunta** ($JLoss$).
- Frente a Martínez-Miera y Repullo (2010): se endogeniza la **correlación** entre carteras como función de la estructura de mercado, no solo la probabilidad de default puntual.
- Frente a la literatura de $GaR$ (Adrian, Boyarchenko y Giannone, 2019): se aporta un **microfundamento de OI** para el determinante financiero que desplaza el cuantil inferior del PIB.
- Frente a la literatura de *doom loop* soberano-bancario (Acharya, Drechsler y Schnabl, 2014; Farhi–Tirole, 2018): se conecta el lazo con la **estructura competitiva** aguas arriba, cerrando la cadena hasta el $EMBI$.

**Novedad defendible ante el estándar exigido:** el modelo produce una predicción *distinguible* de la de MMR —la posición del mínimo de fragilidad y la sensibilidad de la cola dependen de un parámetro de correlación endógeno a la estructura de mercado— y esa predicción es contrastable con los datos que ya se poseen.

---

## 1. Fase I — Andamiaje teórico y posicionamiento (Pilares)

**Objetivo.** Delimitar con precisión el gap y fijar las piezas que el modelo debe reproducir y superar.

**Tres pilares a sistematizar:**

1. **OI bancaria y estabilidad (competencia-fragilidad vs. competencia-estabilidad).** Keeley (1990, charter value); Allen y Gale (2000, 2004); Boyd y De Nicoló (2005, risk-shifting); Martínez-Miera y Repullo (2010, relación en U); Vives (2016, síntesis); indicadores de competencia (Lerner, Boone, H-estadístico de Panzar-Rosse, HHI).
2. **Riesgo sistémico y $JLoss$.** Modelo de Merton (1974) y distancia al default; medidas de pérdida conjunta / systemic expected shortfall (Acharya et al., 2017, SES/SRISK; Adrian y Brunnermeier, 2016, CoVaR); aproximación de punto de silla para la distribución de pérdidas de cartera (Martin, Thompson y Browne, 2001; Gordy, 2002).
3. **Riesgos a la baja y lazo soberano.** $GaR$ y densidades cuantílicas del PIB (Adrian, Boyarchenko y Giannone, 2019); nexo soberano-bancario y *doom loop* (Acharya, Drechsler y Schnabl, 2014; Brunnermeier et al., 2016; Farhi y Tirole, 2018).

**Entregable.** Nota de posicionamiento (2–3 pp.) con la tabla del gap: qué microfunda cada pilar, qué deja abierto, y qué eslabón aporta la arista OI.

**Criterio de verificación teórica de la fase.** El gap debe ser expresable como una **proposición aún no demostrada** en la literatura citada (i.e., ningún paper de la lista deriva $\partial JLoss/\partial(\text{competencia})$ con correlación endógena). Si el gap ya está cubierto por un paper existente, se reformula el ángulo antes de avanzar.

---

## 2. Fase II — Arquitectura del modelo

**Objetivo.** Fijar primitivos, agentes, *timing* y concepto de equilibrio, de modo que el modelo sea el más simple capaz de generar la no linealidad buscada (regla 7 del CLAUDE.md: no sobre-especificar).

### 2.1 Decisión de estructura de competencia (elegir una, con fallback)
| Opción | Ventaja | Costo | Recomendación |
|---|---|---|---|
| **Cournot en préstamos** (n bancos / variación conjetural), estilo MMR | Anidamiento directo con MMR; comparative statics limpias en $n$ | Correlación debe añadirse *ad hoc* | **Base recomendada** |
| **Salop circular** (diferenciación espacial, costo de transporte $t$, entrada endógena) | Micro-funda entrada/salida y poder de mercado; $t$ como parámetro continuo | Álgebra más pesada | Extensión / robustez |
| **Monti-Klein** (banco con poder de mercado en depósitos y préstamos) | Traspaso de tasas explícito (útil para el canal EMBI) | Menos natural para $n$ bancos y correlación | Bloque auxiliar del pass-through |

### 2.2 Primitivos (versión base, Cournot)
- $n$ bancos con responsabilidad limitada y seguro de depósitos (⇒ incentivo a risk-shifting).
- Cada banco elige volumen de préstamo $l_i$ y un nivel de **riesgo/monitoreo** $r_i$ de su cartera.
- Los préstamos default con probabilidad $p(R_L, r_i)$, creciente en la tasa de préstamo de equilibrio $R_L$ (canal risk-shifting del prestatario, Boyd–De Nicoló) y en $r_i$.
- Retornos correlacionados por un **factor común** $z$ con carga $\beta(\cdot)$; la correlación de default $\rho$ entre bancos es función de la **homogeneidad de carteras**, que a su vez depende de la estructura de mercado.
- Margen de intermediación / charter value $\phi(R_L)$ decreciente en competencia (canal Keeley).

### 2.3 Timing
1. Estructura de mercado dada por $n$ (o $t$ en Salop).
2. Bancos compiten à la Cournot y fijan $(l_i, r_i)$.
3. Se realiza el factor común $z$; ocurren defaults; se materializa la pérdida conjunta.
4. Cierre macro: la pérdida agregada golpea la oferta de crédito y el PIB; el fisco absorbe el costo de rescate; se determina el $EMBI$.

### 2.4 Concepto de equilibrio
Equilibrio de Nash simétrico en $(l, r)$; existencia y unicidad vía condiciones de primer y segundo orden; entrada libre (opcional) que fija $n^*$ por condición de beneficio cero.

**Entregable.** Documento de especificación del modelo (primitivos, ecuaciones de pago, definición de equilibrio) en LaTeX.

**Criterio de verificación teórica de la fase.**
- **Casos límite:** $n \to \infty$ (competencia perfecta, margen $\to 0$) y $n = 1$ (monopolio) deben recuperar benchmarks conocidos.
- **Anidamiento:** al fijar $\rho$ exógena y constante, el modelo debe **colapsar exactamente** a la estructura de Martínez-Miera y Repullo (2010). Si no anida, hay un error de especificación.

**Dependencia:** requiere Fase I cerrada.

---

## 3. Fase III — Derivación de resultados a nivel bancario y agregación a $JLoss$

**Objetivo.** Obtener las comparative statics del riesgo individual y, sobre todo, del riesgo de cola conjunta respecto a la competencia.

### 3.1 Riesgo individual (recuperar la U)
Resolver el equilibrio simétrico y derivar $\partial p^*/\partial n$. Resultado esperado (Proposición 1): **la probabilidad de default individual es U-shaped en la competencia**, por la tensión margen (Keeley) vs. risk-shifting (Boyd–De Nicoló), replicando MMR como caso particular.

$$
\underbrace{\frac{\partial p^*}{\partial n}}_{\text{neto}} = \underbrace{\frac{\partial p^*}{\partial R_L}\frac{\partial R_L}{\partial n}}_{\text{efecto risk-shifting}(-)} + \underbrace{\frac{\partial p^*}{\partial \phi}\frac{\partial \phi}{\partial n}}_{\text{efecto margen}(+)}
$$

### 3.2 Agregación a $JLoss$ (aporte propio)
Definir la pérdida sistémica $L = \sum_i \lambda_i \, \mathbb{1}\{\text{default}_i\}$ y su cola vía aproximación de punto de silla. El objeto central es la **cola conjunta**:

$$
JLoss_\alpha = \mathrm{ES}_\alpha(L) \;=\; \mathbb{E}\!\left[\,L \mid L \ge \mathrm{VaR}_\alpha(L)\,\right],
\qquad JLoss_\alpha = f\big(p^*(n),\, \rho(n),\, n\big).
$$

**Proposición 2 (novedad).** Si la correlación endógena $\rho(n)$ es **decreciente en la competencia** (más bancos ⇒ carteras más diferenciadas ⇒ menor correlación), entonces el mínimo de $JLoss_\alpha$ está **desplazado hacia mayor competencia** respecto al mínimo del riesgo individual $p^*$. Formalmente, incluso donde $\partial p^*/\partial n = 0$, se tiene $\partial JLoss_\alpha/\partial n < 0$ por el canal $\rho$. Esto separa la predicción del modelo de la de MMR.

**Proposición 3 (traspaso).** La sensibilidad de la cola $\partial JLoss_\alpha/\partial(\text{shock})$ es **creciente en la concentración**, porque en sistemas más concentrados cada banco tiene $\lambda_i$ mayor (menos entidades, más grandes) ⇒ mayor pérdida por evento.

**Entregable.** Bloque de proposiciones con demostraciones (teorema de la función implícita para signos; condiciones de segundo orden) y un cuaderno numérico de calibración que confirme la U y el desplazamiento del mínimo.

**Criterio de verificación teórica de la fase.**
- Signos de comparative statics verificados analíticamente **y** replicados numéricamente.
- Existencia/unicidad del equilibrio confirmada en la calibración (barrido de parámetros).
- La aproximación de punto de silla validada contra Monte Carlo en al menos un caso de referencia.

**Dependencia:** requiere Fase II cerrada.

---

## 4. Fase IV — Cierre macro y soberano ($JLoss \rightarrow GaR \rightarrow EMBI$)

**Objetivo.** Conectar la cola bancaria con el cuantil inferior del PIB y con el spread soberano, y derivar la **interacción** que es el corazón empírico de la tesis.

### 4.1 Canal $JLoss \rightarrow GaR$
Modelar un *credit crunch*: la pérdida sistémica contrae la oferta de crédito y desplaza a la baja la densidad condicional del crecimiento. El cuantil $\tau$ (p. ej. $\tau = 0{,}05$):

$$
GaR_\tau \;=\; Q_\tau\big(\Delta y \mid JLoss_\alpha\big),
\qquad \frac{\partial GaR_\tau}{\partial JLoss_\alpha} < 0,
$$

con **traspaso creciente en la concentración** (hereda la Proposición 3).

### 4.2 Canal $GaR \rightarrow EMBI$ y la interacción
El spread soberano incorpora (i) el costo fiscal esperado del rescate del sistema (función de $JLoss$) y (ii) el deterioro de sostenibilidad de deuda por menor crecimiento en la cola ($GaR$). El resultado clave es la **complementariedad** (cross-partial):

$$
EMBI = g\big(JLoss_\alpha,\, GaR_\tau\big),
\qquad \boxed{\ \frac{\partial^2 EMBI}{\partial JLoss_\alpha \, \partial GaR_\tau} > 0\ }
$$

**Proposición 4 (amplificación estructural).** La magnitud de la interacción $\partial^2 EMBI/(\partial JLoss\,\partial GaR)$ es **creciente en la concentración** del sistema bancario. Es decir, en economías con banca más concentrada, la coincidencia de alta fragilidad y crecimiento a la baja amplifica el spread soberano de forma más que proporcional.

**Entregable.** Cierre analítico del modelo + proposición de la interacción, con el mapeo explícito a la ecuación empírica de la tesis (el término $JLoss \times GaR$ y su heterogeneidad por concentración).

**Criterio de verificación teórica de la fase.**
- El signo positivo del cross-partial debe derivarse de supuestos declarados y sobrevivir a un caso límite lineal (donde debe anularse).
- Consistencia con el *doom loop*: apagando el respaldo fiscal, la interacción debe desaparecer.

**Dependencia:** requiere Fase III cerrada.

---

## 5. Fase V — Predicciones testeables y puente empírico

**Objetivo.** Traducir cada proposición en una hipótesis contrastable con los datos que ya se poseen, dejando lista la fase empírica posterior.

| # | Predicción teórica | Proxy(s) empírico(s) | Contraste |
|---|---|---|---|
| H1 | Riesgo individual en U respecto a competencia | Lerner / Boone / HHI vs. PD-Merton | Regresión con término cuadrático |
| H2 | $JLoss$ decrece con competencia por canal $\rho$ (mínimo desplazado) | Índices de competencia vs. $JLoss$ (saddle-point) | U con mínimo distinto al de H1 |
| H3 | Traspaso $JLoss\to GaR$ creciente en concentración | HHI × $JLoss$ en regresión cuantílica de $GaR$ | Interacción significativa (cuantil $\tau$) |
| H4 | Interacción $JLoss\times GaR$ sobre $EMBI$ amplificada por concentración | Triple interacción $JLoss\times GaR\times HHI$ | Panel con efectos fijos bidireccionales |

**Estrategia de identificación (preview, para la fase empírica).** Panel de economías en desarrollo; efectos fijos bidireccionales como base (regla 7: no GMM salvo endogeneidad explícita); instrumentos candidatos para competencia (choques regulatorios de entrada, desregulación) si H2–H4 sufren simultaneidad; heterogeneidad por régimen de concentración.

**Entregable.** Tabla de hipótesis ↔ proxies ↔ especificación econométrica, y checklist de disponibilidad de datos (balances CMF, $JLoss$, $GaR$, $EMBI$, índices de competencia).

**Criterio de verificación teórica de la fase.** Cada hipótesis debe (a) desprenderse de una proposición numerada de las Fases III–IV y (b) ser *falsable* con los datos existentes. Si una predicción no es distinguible empíricamente de la de MMR, se marca y se refina el modelo.

**Dependencia:** requiere Fase IV cerrada.

---

## 6. Fase VI — Verificación teórica integral y robustez

**Objetivo.** Someter el modelo al escrutinio del estándar exigido antes de invocar los datos.

**Batería de verificación:**
- **Casos límite y anidamiento:** competencia perfecta, monopolio, $\rho$ constante (⇒ MMR), respaldo fiscal nulo (⇒ sin doom loop).
- **Robustez del setup de competencia:** re-derivar las proposiciones clave bajo Salop; confirmar que los signos se preservan.
- **Estática comparativa numérica:** barrido de parámetros para confirmar U, desplazamiento del mínimo y signo del cross-partial.
- **Validación de la aproximación de punto de silla:** contra Monte Carlo.
- **Coherencia con hechos estilizados:** contrastar cualitativamente contra la evidencia de concentración-estabilidad reportada en la literatura.

**Entregable.** Sección de robustez teórica + apéndice matemático listo para comité.

**Criterio de verificación (revisión adversarial recomendada).** Ejecutar una revisión crítica independiente de las demostraciones y supuestos (idealmente con un subagente/segundo revisor) buscando: supuestos ocultos que garanticen el resultado, no unicidad del equilibrio, y predicciones no distinguibles de las existentes.

**Dependencia:** requiere Fase V cerrada.

---

## 7. Cronograma e hitos

Alineado al esquema de entregas incrementales (hitos de revisión en semanas 5, 10 y 15).

| Semana | Fase(s) | Entregable de checkpoint |
|---|---|---|
| 1–2 | I | Nota de posicionamiento + tabla del gap |
| 3–4 | II | Especificación del modelo (primitivos, equilibrio) verificada en casos límite |
| **5** | **Hito 1** | **Modelo especificado y anidado a MMR; gap validado como proposición abierta** |
| 6–8 | III | Proposiciones 1–3 demostradas + calibración numérica |
| 9 | IV (inicio) | Canal $JLoss\to GaR$ derivado |
| **10** | **Hito 2** | **Cadena completa $JLoss\to GaR\to EMBI$ con Proposición 4 (cross-partial)** |
| 11–12 | V | Tabla de predicciones testeables + checklist de datos |
| 13–14 | VI | Robustez teórica + revisión adversarial de demostraciones |
| **15** | **Hito 3** | **Marco teórico cerrado y falsable, listo para la fase empírica** |

---

## 8. Decisiones abiertas (a resolver antes o durante la Fase II)

1. **Micro-fundar $\rho(n)$ o postularla.** ¿La correlación endógena surge de una elección explícita de diferenciación de cartera (endógena) o se postula una forma reducida $\rho'(n)<0$? La primera es más rigurosa; la segunda, más tratable. Recomendación: postular en la versión base, endogeneizar en extensión.
2. **Estática vs. dinámica.** Modelo de un período para las proposiciones núcleo; discutir si el *doom loop* requiere dos períodos para ser genuino (retroalimentación soberano→banca).
3. **Rol del seguro de depósitos.** Explícito (prima, cobertura) o reducido a un parámetro de risk-shifting.
4. **Traspaso de tasas.** Si el canal $EMBI$ exige modelar el pass-through, incorporar el bloque Monti-Klein auxiliar.
5. **Definición operativa de $JLoss_\alpha$.** ES vs. VaR vs. probabilidad de default conjunta; alinear con la medida que ya se computa vía saddle-point para asegurar el puente empírico.

---

### Nota de método (CLAUDE.md)
Cada fase se cierra solo si su **criterio de verificación teórica** se cumple; no se avanza a la fase siguiente con un eslabón sin validar. Las demostraciones se revisan mentalmente (signos, condiciones de segundo orden) y numéricamente antes de declararlas terminadas. La fase empírica no se inicia hasta cerrar el Hito 3.

*Referencias citadas requieren verificación bibliográfica final antes de la entrega al comité.*
