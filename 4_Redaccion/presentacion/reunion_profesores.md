# Diapositivas de identificación ("¿efecto o persistencia?") — explicación en palabras simples

*Preparación para responder preguntas de los profesores sobre las diapositivas 15–17 de
`defensa.tex` ("Resultado 2: ¿efecto o persistencia?", "Las proyecciones locales son planas" e
"Inferencia, instrumentos y regresores generados"). El desarrollo completo con todas las cifras
está en el capítulo empírico (`envios/paper_empirico/cuerpo.tex`, Sección "¿Efecto o
persistencia? Las pruebas de identificación", `sec:identificacion`); las cifras vienen de
`1_Codigo/Panel/bbg/paper_arbitro_numeros.csv` (`NUMEROS_CANONICOS_BBG.md`, sección 12).*

## La idea central

Hasta ese punto de la presentación se muestra que `JLoss` y `D = -GaR`, medidos un trimestre
antes, se **asocian** con un spread soberano más alto (elasticidad 0,10 y semielasticidad 0,03),
y que la asociación de la fragilidad replica la de Chari et al. (2024). Estas diapositivas
responden a la pregunta obvia: *"¿pero eso es causal?"*. La respuesta honesta es **no con estos
datos**: el spread también mueve a la fragilidad, ambos son muy persistentes, y con 13 países la
inferencia robusta no rechaza la ausencia de efectos. Decirlo explícitamente juega a favor: un
tribunal valora más una tesis que delimita lo que puede afirmar que una que lo exagera.

## Las pruebas, una por una

**1. Retroalimentación (canal inverso).** Se da vuelta la regresión: ¿el spread de ayer predice
la fragilidad de hoy? Sí, con elasticidad **0,17 (p = 0,009)**, mayor que la del efecto que la
tesis busca medir. Es el *doom loop* de Farhi–Tirole visto desde el otro lado: un spread más alto
deprecia los bonos soberanos que tienen los bancos y sube sus probabilidades de incumplimiento.

**2. Dinámica.** El spread es muy persistente (coeficiente autorregresivo trimestral **0,94**).
Al incluir el spread rezagado como regresor, el efecto de corto plazo de la fragilidad cae a
**0,005 (p = 0,76)** y el de largo plazo (0,078) tiene un error tan grande que p = 0,72. Si en vez
de eso se agrega la fragilidad *adelantada* (t+1), pesa casi lo mismo que la rezagada (0,051 vs.
0,058, ninguna significativa): la regresión principal captura un componente persistente común,
no una respuesta del spread a la fragilidad pasada. (Con ~88 trimestres, el sesgo de Nickell es
del orden de 1/T, así que no es un artefacto del estimador.)

**3. Proyecciones locales.** Miran la trayectoria del spread en los trimestres siguientes a un
cambio en la fragilidad, controlando por el spread previo. **Son planas en todos los horizontes
(0 a 6 trimestres)**. El "+4,6 pb" que aparecía en la versión anterior (en niveles, regresores
contemporáneos) **no se reproduce** en la especificación vigente — si alguien lo recuerda del
Informe, esta es la respuesta.

**4. Wild cluster bootstrap (13 clusters).** Con tan pocos países, los errores de Driscoll–Kraay
son optimistas. Con *wild cluster bootstrap* (pesos de Webb), **ni la fragilidad (p = 0,33) ni el
riesgo de cola (p = 0,20) son significativos**, y la interacción está lejos (p = 0,89).

**5. Variables instrumentales (shift-share).** Tres instrumentos para la fragilidad: liquidez
del Tesoro (on/off-the-run), dólar amplio y términos de intercambio por exposición a
commodities, todos ponderados por exposiciones pre-muestra. Las primeras etapas son razonables
(**F entre 9 y 11**), pero las segundas dan **+0,35, −2,18 y +0,15**, ninguna significativa y con
signo inestable, y **Sargan rechaza (p < 0,001)**: los instrumentos no identifican el mismo
parámetro.

**6. Regresores generados (bootstrap del GaR, 500 réplicas).** `GaR` es una estimación, no un
dato. Re-estimando todo sobre 500 réplicas de su primera etapa, los p-valores combinados son
**0,003 / 0,049 / 0,12**: la medición del riesgo de cola **no** es la fuente del problema.

## El mensaje final

En una frase: **"El panel documenta asociaciones compatibles con el mecanismo y replica la
literatura, pero no permite separarlas de la persistencia del spread ni de su efecto sobre la
propia fragilidad; la debilidad viene de la dinámica y del número de países, no de la medición."**

## Si preguntan...

- **"¿Entonces todo es solo correlación?"** → Es una asociación condicional robusta (efectos
  fijos, controles de Chari, Argentina, distintas medidas de cola), pero no un efecto causal
  identificado. La tesis lo dice así, y la conclusión se formula en esos términos.
- **"¿Por qué no funcionaron los instrumentos?"** → Con 13 países es muy difícil encontrar una
  fuente de variación que mueva la fragilidad bancaria sin otro canal hacia el spread. Los tres
  probados son macro-agregados; haría falta uno específicamente bancario (cambios regulatorios,
  choques de fondeo a bancos grandes).
- **"¿Agregar Argentina ayuda?"** → Pasa a 14 países y 799 observaciones; los coeficientes casi no
  cambian (0,0964 vs. 0,0985) y ninguna conclusión cambia. No resuelve la inferencia: 14
  clusters siguen siendo pocos. Su GaR se estimó sin el bloque de tasas, por eso es robustez.
- **"¿Y la interacción por régimen de crisis?"** → Backstop negativo y EMstress positivo tienen el
  signo del mecanismo, pero no resisten errores agrupados por país (p = 0,40 y 0,11) ni la
  permutación (2015–16 queda 20 de 51 ventanas, p = 0,39).
- **"¿Por qué mostrar esto si debilita la tesis?"** → Porque ocultarlo sería peor: delimitar qué
  permite afirmar el diseño es el aporte metodológico de la tesis.
