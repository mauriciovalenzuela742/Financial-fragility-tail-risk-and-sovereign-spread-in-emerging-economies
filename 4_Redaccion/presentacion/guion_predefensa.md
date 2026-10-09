---
title: "Predefensa con el profesor guía"
subtitle: "Guion lámina por lámina, preguntas probables y decisiones a pedir — 10 de octubre de 2026"
---

*Mañana presento la defensa completa al profesor guía como si fuera la predefensa. A diferencia de
la reunión de escritura, aquí importa el contenido: él va a interrumpir, probar la econometría y
decidir si la tesis está lista. Objetivo: exponer en unos **25 minutos** y salir con decisiones
claras.*

**Antes de entrar**

- [ ] Llevar la presentación nueva (la del zip optimizado, abierta en Prism) en PDF, en el
      computador y en un pendrive.
- [ ] La tesis en PDF abierta (para mostrar una tabla si la pide) y esta guía impresa.
- [ ] Reloj o cronómetro visible. Ensayar una vez en voz alta midiendo el tiempo.
- [ ] Saber de memoria la página 2 (historia, cifras y salvedades).

*La presentación tiene 40 láminas: 22 de exposición, 16 de respaldo y 2 de referencias. Los números
de este guion corresponden a esa versión.*

\newpage

# 1. Lo que tengo que saber de memoria

**La historia en tres frases**

1. Estudio si la **fragilidad bancaria** y el **riesgo de cola del crecimiento** encarecen juntos la
   deuda soberana de 13 economías emergentes.
2. Ambos se **asocian** con un spread mayor, pero no se puede leer como **causal**: el spread
   también deteriora la fragilidad y ambos son muy persistentes.
3. La **amplificación** no aparece en promedio, sino **fuera de crisis con rescate internacional y
   en economías de financiamiento externo**: evidencia **condicional**, no robusta.

**Las cifras**

| Qué | Cifra |
|---|---|
| Muestra | 13 economías, 2004Q2–2026Q2, N = 765 (14 y 799 con Argentina) |
| Fragilidad → spread | elasticidad 0,0985 (duplicar JLoss ≈ +7 %); 4,7 pb por unidad en niveles |
| Riesgo de cola → spread | 0,0324: +1 pp de D ≈ +3,3 % de spread |
| Retroalimentación spread → JLoss | 0,17 (p = 0,009) |
| Persistencia del spread | ρ = 0,94 trimestral |
| Wild bootstrap (β1 / β2 / β3) | p = 0,33 / 0,20 / 0,89 |
| Interacción promedio | −0,011 (p = 0,11); complementariedad implícita +0,19 pb |
| Permutación EMstress | lugar 20 de 51, p = 0,39 |
| Núcleo de 11, sin crisis | +0,034 (wild p = 0,015) y +1,8 pb (wild p = 0,002) |

**Las tres salvedades del resultado condicional:** grupo definido *ex post*; en logaritmos los
controles lo absorben; 11 *clusters* son pocos.

\newpage

# 2. Guion lámina por lámina (≈ 25 min)

*Frases cortas en la lámina; el detalle lo dices tú. Si te interrumpe, responde y vuelve al hilo.*

## Motivación y pregunta (≈ 6 min)

**1. Portada (15 s).** "Buenos días. Presento *Fragilidad bancaria sistémica y riesgo de cola del
crecimiento*, sobre los determinantes del spread soberano en economías emergentes."

**2. Índice (15 s).** "Cinco partes: motivación, medición, datos, resultados y conclusiones."

**3. Dos pilares del spread (1 min 30 s).** "La literatura explica el spread soberano con dos
pilares: fundamentos domésticos y factores globales. Mido lo doméstico con dos proxies propias,
JLoss para la fragilidad bancaria y GaR para la cola del crecimiento, y absorbo lo global con
efectos fijos de tiempo. Chari et al. (2024) cruzan la fragilidad con factores globales; nadie la
ha cruzado con el riesgo de cola doméstico. Esa es la brecha."

**4. El mecanismo y el balance de fuerzas (1 min 30 s).** "Una cola adversa encarece el rescate
bancario esperado, que es lo que mide JLoss, y el mercado lo cobra en el spread. Abren la brecha
los bancos frágiles, la cola adversa y la deuda en manos extranjeras; la contienen el respaldo
oficial y un mercado local profundo. La flecha punteada es clave: el spread también daña a los
bancos. Esa causalidad inversa es mi principal problema de identificación."

**5. Pregunta e hipótesis (1 min).** "La pregunta es si el mercado penaliza de forma no lineal esa
coincidencia. H1 y H2 son los canales de nivel; H3, la amplificación. Un matiz: si ambos riesgos
escalan la misma probabilidad de incumplimiento, en puntos básicos ya se potencian. La versión
exigente de H3 es una amplificación adicional."

**6. Qué aporta esta tesis (1 min 30 s).** "Adelanto el aporte. Conceptual: un solo mecanismo
para dos literaturas. Empírico: las métricas para 13 países, una réplica independiente de Chari y
la delimitación de cuándo y dónde aparece la amplificación. Metodológico: un pipeline
reproducible. Y el límite, desde ya: son asociaciones y la amplificación es condicional."

## Medición y estrategia (≈ 3 min)

**7. Dos métricas (1 min 30 s).** "JLoss es la pérdida conjunta esperada del sistema bancario:
probabilidades de incumplimiento tipo Merton agregadas por punto de silla, 113 bancos, validada
contra el código original. Es ordinal, por eso va en logaritmos. GaR es el cuantil 5 % del
crecimiento futuro, por regresión cuantílica en pseudo–tiempo real, y verifiqué que no es circular
con el EMBI."

**8. La especificación (1 min 30 s).** "Log del EMBI sobre log de JLoss y el riesgo de cola,
rezagados un trimestre, y su producto, con efectos fijos de país y tiempo. Rezago por la
causalidad inversa; logs por la asimetría. Errores Driscoll–Kraay y, como son 13 países, wild
cluster bootstrap. Todo lo repito en puntos básicos."

## Datos (≈ 1 min)

**9. El panel (1 min).** "13 economías, 2004 a 2026, 765 observaciones. Argentina entra como
robustez. Corea, Bulgaria y Hungría quedan fuera porque su JLoss no es válido a nivel país."

## Resultados (≈ 11 min)

**10. Ambos riesgos se asocian con el spread (1 min 30 s).** "Primer acto, lo que se asocia.
Elasticidad de 0,10 a la fragilidad: duplicar JLoss se asocia con un spread 7 % mayor. Cada punto
de riesgo de cola, 3,3 % más. Replico a Chari et al. Con controles fiscales y cambiarios la
fragilidad se diluye, porque probablemente son los canales por los que opera."

**11. Pero no es causal (1 min 30 s).** "Segundo acto, lo que no puedo afirmar. El spread de ayer
predice la fragilidad de hoy con 0,17; con dinámica, el efecto cae a cero; las proyecciones
locales son planas; con wild bootstrap nada es significativo; y los instrumentos no cierran."

**12. En promedio, sin amplificación adicional (1 min 30 s).** "El efecto de la fragilidad no
crece con el riesgo de cola: la interacción es −0,011, no significativa. En puntos básicos sí se
potencian, pero solo por la forma proporcional."

**13. Las crisis (1 min).** "Al pie de la letra, el patrón del mecanismo: negativa con respaldo
oficial, positiva en 2015–16. Pero 2015–16 queda 20 de 51 ventanas al azar: no es especial."

**14. Dónde sí aparece (2 min).** "Tercer acto. Si separo las 11 economías de financiamiento
externo y miro fuera de las crisis con respaldo, la amplificación aparece: +0,034 en logs, +1,8
puntos básicos en niveles. En Polonia e India, con deuda local profunda, va al revés. Es lo que
predice el mecanismo."

**15. Cómo leer este hallazgo (1 min 30 s).** "Lo digo explícitamente: es condicional. Lo
respalda que resiste el wild bootstrap, aparece en ambas formas y sobrevive a excluir cada país. Lo
limita que el grupo lo definí después de ver la versión anterior, que en logs los controles lo
absorben y que son 11 países. Es una hipótesis bien delimitada, no un hallazgo robusto."

**16. Robustez (1 min).** "Argentina, otra medida de cola, sin el EMBI empalmado, excluyendo
países: las conclusiones no cambian."

## Conclusiones (≈ 4 min)

**17. Respuesta a la pregunta (1 min).** "Objetivo por objetivo: métricas construidas; fragilidad
y riesgo de cola asociados, no causales; complementariedad proporcional en promedio. ¿Penaliza el
mercado la coincidencia de forma no lineal? No en general; sí, condicionalmente."

**18. El aporte (1 min).** "Un mecanismo, dos métricas propias con una réplica independiente, una
delimitación precisa de qué se puede afirmar y dónde buscar la amplificación, y una
infraestructura reproducible. Lo que no afirma: ni causalidad ni amplificación universal."

**19. Implicancias (45 s).** "Respaldado: monitorear JLoss y GaR juntos. Si lo condicional se
confirma: focalizar en economías de financiamiento externo sin respaldo, en vez de regular igual a
todos."

**20. Trabajo futuro (30 s).** "Más países, un moderador medido ex ante, variación exógena bancaria
y mayor frecuencia."

**21. Conclusión (30 s).** Leer las tres frases y la última línea.

**22. Gracias.** "Quedo atento a sus comentarios."

*Respaldo (23–40): no se presenta; se usa para responder. Taller I (23), JLoss (24), GaR (25),
descriptivos (26), batería y controles (27), identificación e IV (28), logs vs. niveles (29),
niveles prueba por prueba (30), vector de crisis (31), heterogeneidad completa (32), Argentina
(33), Hansen (34), leave-one-out (35), medición de JLoss y GaR (36), COVID (37), limitaciones (38).*

\newpage

# 3. Preguntas probables del profesor guía

*Responder en una o dos frases y, si insiste, ir a la lámina de respaldo. Es probable que conozca
JLoss y Chari et al. (2024) en detalle: espera preguntas finas sobre la métrica.*

**¿Por qué log-log y no niveles, como en el Informe de Taller?** Porque las series son muy
asimétricas y JLoss es ordinal; la prueba PE prefiere logs. Reporto todo también en niveles
(láminas 29 y 30): ahí la evidencia es más favorable, pero tampoco resiste el wild bootstrap.

**¿Por qué no hay controles en la regresión principal?** Porque balance fiscal, inflación y tipo de
cambio son plausiblemente canales del mecanismo: la fragilidad rezagada los predice. Con
controles medidos cuatro trimestres antes la elasticidad es 0,062 (n.s.).

**¿El rezago resuelve la endogeneidad?** No del todo: elimina la causalidad inversa más directa,
pero el spread es persistente (ρ = 0,94) y se retroalimenta (0,17). Por eso no hablo de efectos
causales.

**¿No es un problema el sesgo de Nickell con el spread rezagado?** Con T ≈ 88 trimestres el sesgo es
del orden de 1/T; el colapso del coeficiente no es un artefacto.

**¿Por qué Driscoll–Kraay y además wild bootstrap?** DK es robusto a autocorrelación y
dependencia transversal, pero con 13 clusters es optimista. El wild bootstrap con pesos de Webb es
la corrección estándar con pocos clusters.

**¿Por qué fallaron los instrumentos?** Son choques macro-agregados (Tesoro, dólar, términos de
intercambio); mueven más cosas que la fragilidad bancaria. Haría falta un instrumento
específicamente bancario (lámina 28).

**El núcleo de 11 economías, ¿no es una búsqueda de especificación?** Sí, en parte, y lo digo en la
lámina 15: el
grupo viene de la versión anterior. Por eso es evidencia condicional y la agenda propone un
moderador continuo medido ex ante: la participación extranjera en la deuda.

**¿Por qué JLoss es "ordinal"?** La cota superior de la malla de pérdidas (4,8 %) está activa en el
98 % de los casos, así que la variación viene de las PD. En percentiles la asociación se mantiene;
con malla ancha cae (lámina 36).

**¿El GaR no está contaminado por el spread?** El EMBI no entra al cálculo; el único componente
tipo spread aporta 0,07 al FCI y sin él el GaR correlaciona 0,985 con el oficial.

**¿Por qué Argentina no está en la muestra principal?** Su GaR se estimó sin el bloque de tasas y
con una ventana más corta. Como robustez no cambia nada (lámina 33).

**Si nada es causal, ¿cuál es el aporte?** Construir las métricas para 13 países, replicar Chari
et al. con datos independientes, delimitar dónde aparece la amplificación y mostrar por qué este
diseño no basta para más. Es evidencia creíble, no un resultado inflado.

**¿Qué haría con más tiempo?** Más economías, la participación extranjera como moderador, datos de
mayor frecuencia y un choque bancario exógeno.

# 4. Decisiones que debo pedirle

1. **¿La tesis está lista para defender?** Si no, qué falta y con qué plazo.
2. **Encuadre del resultado:** ¿está de acuerdo con "asociación, no causalidad; amplificación
   condicional", o prefiere otro énfasis?
3. **Heterogeneidad por economía:** ¿la dejo en Resultados (4.6) o la bajo a robustez por ser
   *ex post*?
4. **Argentina:** ¿se queda como robustez o vale la pena homologar su GaR y meterla en la muestra
   principal?
5. **Forma funcional:** ¿de acuerdo con logs como principal y niveles en paralelo?
6. **Presentación:** ¿cuánto tiempo tendré en la defensa? ¿Sobran láminas? ¿Qué sacaría?
7. **Paper:** ¿vale la pena enviarlo? ¿A qué revista?
8. **Calendario:** fecha de entrega final, comisión y fecha de defensa.

# 5. Para cerrar la reunión

- [ ] Veredicto: lista / lista con cambios / falta trabajo.
- [ ] Lista de cambios pedidos, con prioridad.
- [ ] Decisiones 2 a 5 tomadas.
- [ ] Duración de la defensa y láminas a recortar.
- [ ] Fechas: entrega, comisión, defensa.

**Notas:**

\vspace{5cm}
