# Carta de presentación — paper empírico (borrador)

Estimado/a Editor/a:

Adjunto para su consideración el manuscrito **"Fragilidad bancaria sistémica, riesgo de
cola del crecimiento y *spread* soberano en economías emergentes"**, para su eventual
publicación en *[revista]*.

El trabajo articula dos literaturas que han evolucionado por separado —el nexo
banca–soberano y el programa de *Growth-at-Risk*— y parte de un resultado conocido: la
fragilidad bancaria se asocia con el *spread* soberano (Chari et al., 2024). La pregunta
es qué agrega el riesgo de cola del crecimiento *doméstico* ($D\equiv-GaR$) y qué ocurre
cuando los dos riesgos se dan a la vez. Sobre un panel de trece economías emergentes
construido con datos de mercado de Bloomberg (2004–2026, $N=765$) y el EMBI Global
Diversified de J.P. Morgan, el resultado de Chari et al. se replica con una construcción
de datos independiente (elasticidad $0{,}099$; $0{,}107$–$0{,}164$ con sus controles),
aunque no como una elasticidad común a los países ni con evidencia de que la fragilidad
anteceda al *spread*: ambos se mueven dentro del mismo trimestre.

El hallazgo central es que los dos riesgos **tienden a darse juntos, sin evidencia de que se
amplifiquen**. (i) Coinciden en su tercil alto $1{,}9$ veces lo esperado bajo
independencia (168 observaciones frente a 87), en los trece países y también fuera de
las crisis globales (permutación por bloques, $p=0{,}001$), y hay evidencia sugerente de que la fragilidad bancaria
antecede al deterioro de la cola del crecimiento. (ii) Cuando coinciden,
no se rechaza que sus asociaciones con el *spread* se sumen: la interacción es $\hat\beta_3=-0{,}011$ (wild
bootstrap $p=0{,}89$) y los datos no permiten descartar una amplificación de hasta un
30–40 % de la suma. (iii) El riesgo de cola agrega información modesta, y solo en
niveles, a lo que explica la fragilidad ($0{,}037$; wild $p=0{,}066$); no mejora el
pronóstico fuera de muestra. (iv) Ninguna condición estudiada —resiliencia de la
política económica, respaldo externo medido por país, participación extranjera en la
deuda con hipótesis escritas antes de estimar— modifica la transmisión de forma
demostrable.

La contribución tiene cuatro partes. Primero, sustancial: es —hasta donde sabemos— el primer
cruce sistemático de una métrica estructural de fragilidad bancaria con una medida de
riesgo de cola del crecimiento *doméstico* en el riesgo soberano de economías
emergentes, frente a la interacción con factores financieros *globales* de la
literatura más próxima (Chari et al., 2024). Las dos métricas son de otros autores (el
$GaR$, de Adrian, Boyarchenko y Giannone, 2019); lo propio es la construcción homogénea
de sus series y su cruce. Segundo, de inferencia: una simulación con dependencia entre
países muestra que los errores de Driscoll–Kraay rechazan una hipótesis nula cierta
entre el 20 % y el 30 % de las veces en niveles, por lo que el criterio es el wild
cluster bootstrap por país; se agregan permutaciones, corrección de Holm, exclusión de
cada país y moderadores placebo. Tercero, de transparencia: el trabajo reporta cada
prueba salga como salga, incluidos los resultados nulos, y declara lo que no se puede
afirmar con trece países, entre ello que las asociaciones no son causales y que un
sesgo de retroalimentación puede explicar parte de los coeficientes de nivel. Cuarto, una batería de pruebas que delimita qué no puede afirmarse con trece países.

Todo el código de construcción de las series y de estimación es reproducible y se pone
a disposición.

El manuscrito es original, no ha sido publicado y no está bajo consideración en otra
revista. Agradezco de antemano el tiempo del equipo editorial y de los evaluadores.

Atentamente,
Mauricio Valenzuela Corvalán
