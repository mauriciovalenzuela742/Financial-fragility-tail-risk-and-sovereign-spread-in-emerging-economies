---
title: "Predefensa en 10 láminas"
subtitle: "Guion, respuesta a las observaciones del profesor guía y pruebas a revisar — octubre de 2026"
---

*Versión corta que pidió el profesor Martínez en la reunión del 9 de octubre: máximo 9–10 láminas
con pregunta, hipótesis, metodología, resultado e implicancia. Archivo: `predefensa.tex` (10 láminas
+ 17 de anexo). La presentación larga (`defensa.tex`, 53 láminas) tiene los mismos cambios, con más detalle. Tiempo: unos 15
minutos de exposición.*

**Vocabulario que debo cuidar** (lo corrigió el profesor):

- **Amplificación** (o simultaneidad), nunca "multiplicidad".
- Efectos **aditivos** cuando cada riesgo sube el spread por separado y la suma no se potencia.
- **Riesgo financiero** = fragilidad bancaria (JLoss). **Riesgo económico** = cola del crecimiento (GaR).
- Son **correlaciones**; la causalidad no se exige en esta evaluación.

# 1. Guion lámina por lámina

### 1. Portada (15 s)
"Presento la tesis *Fragilidad bancaria sistémica y riesgo de cola del crecimiento: determinantes
del spread soberano en economías emergentes*."

### 2. La pregunta (1 min 30 s)
**Qué digo:** "El spread soberano es la prima que exige el mercado por el riesgo de que un gobierno
no pague. Estudio dos riesgos domésticos de cola: uno **financiero**, la fragilidad del sistema
bancario, que mido con JLoss; y uno **económico**, la cola adversa del crecimiento, que mido con el
Growth-at-Risk. La brecha: no se han cruzado simultáneamente los dos riesgos de cola domésticos, el
financiero y el económico. La pregunta es si cada uno encarece la deuda soberana y si su
coincidencia la amplifica."

**Si me pregunta** por qué digo "económico": porque JLoss también es un riesgo de cola; lo que
distingue al GaR es que es de la actividad económica, no del sistema financiero.

### 3. El mecanismo (1 min 30 s)
**Cómo leer:** el triángulo: primero la línea de arriba, después las dos flechas azules.

**Qué digo:** "El mecanismo es un triángulo, no una secuencia. Los dos riesgos se relacionan entre
sí: un sistema bancario frágil da menos crédito y eso deprime el crecimiento ---el acelerador
financiero de Bernanke, Gertler y Gilchrist---, y un crecimiento débil deteriora a los bancos. Y
ambos se trasladan al spread: la fragilidad, como rescate esperado; la cola del crecimiento, por la
capacidad fiscal. Lo que contiene esa transmisión es el respaldo oficial ---el banco central--- y un
mercado local de deuda profundo; ninguno entra como regresor, los absorben los efectos fijos. Y
como las tres cosas ocurren a la vez, hablo de correlaciones, no de causalidad."

### 4. Hipótesis de trabajo (1 min)
**Qué digo:** "Cuatro hipótesis. Una: cada riesgo importa, y el económico sobrevive a las variables
financieras. Dos: su coincidencia amplifica el spread; si no, los efectos son aditivos. Tres: con
más resiliencia de la política económica ---menos deuda, mejor balance fiscal, más reservas--- ambos
efectos son menores. Cuatro: en una crisis que afecta a todos, ese resguardo puede no bastar."

### 5. Las dos variables en el tiempo (1 min 30 s)
**Cómo leer:** la línea es la mediana entre países; la banda, el rango entre el 25 % y el 75 %; lo
sombreado, las crisis.

**Qué digo:** "Antes de las regresiones, las series. A la izquierda JLoss, la pérdida conjunta
esperada del sistema bancario, calculada con 113 bancos de Bloomberg. A la derecha el riesgo de
cola, que es el cuantil 5 % del crecimiento con el signo invertido. Las dos tienen sentido económico:
son bajas y estables en tiempos normales y saltan en la crisis financiera global y en la pandemia."

**Si me pregunta** por un país: en el anexo están la construcción de cada una y, en la tesis, las
series por país.

### 6. Metodología (1 min 30 s)
**Qué digo:** "Regreso el logaritmo del EMBI sobre el logaritmo de JLoss y el riesgo de cola, ambos
rezagados un trimestre, y su producto, con efectos fijos de país y de tiempo. Beta tres es la
interacción: positiva es amplificación; cero, efectos aditivos. El rezago es por la
retroalimentación del spread; los efectos fijos de tiempo absorben los factores financieros
globales. Mido la incertidumbre con Driscoll–Kraay, con errores agrupados por país y con wild
cluster bootstrap, porque son 13 países."

**Si me pregunta** por el solapamiento del FCI con las variables financieras: ver la sección 2.

### 7. Resultado 1: cada riesgo importa, y son aditivos (2 min 30 s)
**Cómo leer:** la columna del riesgo de cola de arriba abajo: siempre positiva y significativa.
Después la columna de la interacción: nunca positiva y significativa.

**Qué digo:** "Primer resultado. El riesgo económico se asocia con el spread en todas las
especificaciones: un punto más de riesgo de cola, 3,3 % más de spread. Y no es un reflejo de las
variables financieras: si limpio el riesgo de cola de los factores financieros globales, el
coeficiente queda igual, 0,033; y si reconstruyo el GaR sin el bloque bursátil del índice
financiero, que es el que comparte información con JLoss, sigue en 0,045. La fragilidad bancaria
también se asocia, con una elasticidad de 0,10, pero los controles la absorben. Y la interacción no
es positiva en ninguna: no hay amplificación, los efectos son aditivos."

**Conclusión directa:** el riesgo económico importa por sí mismo; los dos riesgos suman, no se
potencian.

**Si me pregunta** por la significancia: con wild bootstrap sobre 13 países ninguno es
significativo; por eso hablo de asociación.

### 8. Resultado 2: la resiliencia como un seguro (2 min)
**Cómo leer:** la fila "fuera de crisis" contra la fila "en crisis".

**Qué digo:** "Segundo resultado. Construí un índice de resiliencia con deuda, balance fiscal y
reservas. Más resiliencia, menor spread. Y fuera de las crisis la resiliencia atenúa el efecto del
riesgo de cola: −0,024 por desviación estándar. Pero en la crisis financiera global y en la pandemia
esa atenuación desaparece. Es como un seguro: en tiempos normales el que está mejor resguardado paga
menos prima, pero cuando el choque les pega a todos las primas suben para todos. Para la fragilidad
bancaria no se cumple: su efecto no es menor en los países más resilientes."

**Conclusión directa:** el resguardo propio protege en tiempos normales, no en crisis sistémicas.

**Si me pregunta** por qué la fragilidad no se atenúa: una lectura posible es que el rescate es más
creíble donde el soberano puede pagarlo, y esa credibilidad traslada el riesgo bancario a la deuda;
no lo puedo contrastar con este diseño.

### 9. Resultado 3: la amplificación aparece sin respaldo externo (2 min)
**Cómo leer:** el punto azul de más abajo (núcleo, sin crisis) es el único cuyo intervalo no toca el
cero.

**Qué digo:** "Tercer resultado, sobre las crisis. Con respaldo externo ---la crisis global y la
pandemia--- la interacción es negativa. En 2015–16, sin respaldo, cuando responde solo el banco
central de cada país, es positiva. Y en las once economías que se financian con inversionistas
extranjeros, fuera de crisis, la amplificación es +0,034. Pero es condicional: el grupo lo definí
después de mirar los datos, los controles la absorben en logaritmos y 2015–16 no se distingue de
otras ventanas."

**Conclusión directa:** la amplificación no es general; aparece donde falta un respaldo externo.

### 10. Conclusiones e implicancias (1 min 30 s)
**Qué digo:** "Cuatro conclusiones: el riesgo económico doméstico se asocia con el spread más allá
de lo financiero; los dos riesgos son aditivos; la resiliencia baja el spread y protege en tiempos
normales, no en crisis sistémicas; y la amplificación aparece sin respaldo externo, como evidencia
condicional. La implicancia: monitorear juntos ambos riesgos; el resguardo propio protege en
tiempos normales y, en una crisis sistémica, lo que protege es el respaldo externo."

\newpage

# 2. Cómo se atendió cada observación del profesor

| Observación (9 de octubre) | Qué se hizo |
|---|---|
| Máximo 9–10 láminas; el resto, anexo | `predefensa.tex`: 10 láminas + anexo |
| Riesgo financiero vs. riesgo económico | Lámina 2; tesis y paper, mecanismo y marco conceptual |
| La brecha: "no se han cruzado simultáneamente…" | Lámina 2; tesis sección 1.3 |
| Triángulo en vez de secuencia; acelerador financiero | Lámina 3; figura nueva en tesis y paper; referencia BGG (1996) |
| El respaldo es el banco central; no está en las regresiones | Lámina 3; tesis sección 1.3 |
| Gráficos de GaR y JLoss antes de las regresiones | Lámina 5 (figura nueva, 2004–2026) |
| "Amplificación", no "multiplicidad"; efectos aditivos | Todo el guion; tesis 2.1.4 fija el vocabulario |
| Solapamiento / endogeneidad del FCI; dos etapas | Estimación nueva: tesis 3.3 y 4.6, Tabla de solapamiento |
| Resiliencia (deuda, balance fiscal, reservas) | Estimación nueva: tesis 3.3 y 4.6, Tabla de resiliencia; lámina 8 |
| Crisis vs. no crisis: ¿sigue funcionando el resguardo? | Lámina 8 y 9; tesis 4.6 y 5.1 (analogía del seguro) |
| La tabla del vector único "está enredada" | Pasa al anexo |
| Correlación, no causalidad | Lámina 3 ("Alcance") y lámina 10 |

# 3. Las dos estimaciones nuevas, en simple

**Solapamiento (¿el GaR cuenta dos veces lo financiero?).** No.

- Los factores globales explican el 34 % de la variación del riesgo de cola dentro de cada país, pero
  los efectos fijos de tiempo ya los absorben: limpiarlo de ellos deja el coeficiente igual (0,033
  frente a 0,032).
- El riesgo de cola y la fragilidad comparten poca variación: correlación parcial 0,26, factor de
  inflación de varianza 1,07.
- El GaR sin el bloque bursátil del índice financiero correlaciona 0,98 con el original y su
  coeficiente es 0,045 frente a 0,039.
- **Matiz que debo decir:** sin efectos fijos de tiempo, el riesgo de cola limpio de factores
  globales deja de ser significativo (0,013, p = 0,17). Parte de su asociación es global; por eso la
  especificación principal lleva efectos fijos de tiempo.

**Resiliencia.** Se cumple a medias.

- Más resiliencia, menor spread (−0,153 por desviación estándar).
- Atenúa el efecto del riesgo de cola fuera de crisis (−0,024, p = 0,007) y no en crisis (−0,001).
- No atenúa el efecto de la fragilidad (+0,053, no significativo; en niveles incluso es mayor).
- **Límite:** ningún término de moderación resiste el wild bootstrap (p = 0,42 y 0,46).

# 4. Pruebas para revisar con el profesor de econometría

1. **Errores estándar:** Driscoll–Kraay como referencia, cluster por país y wild cluster bootstrap con
   pesos de Webb (13 clusters). ¿Es la combinación correcta para N = 13, T ≈ 88?
2. **Dinámica:** spread rezagado como regresor (sesgo de Nickell del orden de 1/T). ¿Hace falta un
   estimador de panel dinámico?
3. **Regresión en dos etapas del GaR:** ¿está bien planteada? ¿Corrige los errores de la segunda
   etapa por usar un residuo estimado?
4. **Regresor generado:** bootstrap de 500 réplicas de la primera etapa del GaR. ¿Suficiente?
5. **Variables instrumentales shift-share** con exposiciones pre-muestra: primeras etapas F ≈ 9–11 y
   Sargan rechaza. ¿Vale la pena insistir o basta con declararlo?
6. **Índice de resiliencia:** promedio de z-scores de tres variables anuales interpoladas. ¿Conviene
   otra agregación (componente principal) o usar las variables por separado?
7. **Heterogeneidad por tipo de economía:** el grupo se definió ex post. ¿Cómo reportarlo sin
   sobrevender?
8. **Prueba de permutación** del episodio de 2015–16: ¿es adecuada con 51 ventanas?

# 5. Pendientes para el seguimiento del viernes 16

- [ ] Confirmar con el programa quién figura como guía y quién como coguía (por ahora: guía J. F.
      Martínez, coguía R. Fischer).
- [ ] Reunión con el profesor de econometría (sección 4).
- [ ] Llevar la tesis con los cambios y la presentación de 10 láminas.
- [ ] Planificar los seguimientos; meta de defensa: primera semana de diciembre.
