# Prompt para Prism: pulido general de la presentación

Pegar en el asistente de Prism con `defensa.tex` abierto, **después** de haber agregado las dos
láminas nuevas del prompt anterior. Es una pasada de revisión: integra las láminas nuevas con el
resto y deja el deck parejo, sin cambiar el contenido ni las cifras.

```
Revisa todo defensa.tex y déjalo pulido y coherente, sin cambiar el contenido sustantivo ni
ninguna cifra. Trabaja en este orden y al final dame un resumen de los cambios, lámina por lámina.

1. INTEGRAR LAS DOS LÁMINAS NUEVAS DEL INICIO
   ("Determinantes del spread soberano: fundamentos domésticos y factores globales" y
   "Teoría e implicancias: la brecha del spread soberano").
   - Compáralas con el frame "Motivación" y con "El mecanismo: un doom loop banca--soberano".
     Elimina las repeticiones: si "Motivación" repite lo mismo, redúcelo a lo que no esté en
     las láminas nuevas (por ejemplo, la pregunta de investigación en un block) o fusiónalo.
     No borres la pregunta de investigación ni el diagrama TikZ del mecanismo.
   - Revisa que el orden cuente una historia: pilares y literatura → teoría y brecha →
     mecanismo → pregunta e hipótesis → objetivos.
   - Las láminas nuevas deben usar los mismos tamaños de letra, bloques y márgenes que el resto.

2. QUE NADA SE SALGA DE LA LÁMINA
   - Compila y elimina todo Overfull \vbox y \hbox: reduce a \small o \footnotesize, acorta
     frases, usa adjustbox{max width=\linewidth} en tablas o divide la lámina en dos.
   - Ningún texto puede quedar tapado por el pie de página ni cortado a la derecha.
   - Las figuras deben verse completas y legibles (width y height con keepaspectratio).

3. CONSISTENCIA VISUAL
   - Mismo patrón en todas las láminas: título corto (máximo una línea), viñetas de una o dos
     líneas, como máximo 6 viñetas por lámina.
   - Mismo uso de bloques: block para resultados o definiciones, alertblock para salvedades y
     lo no establecido, exampleblock para implicancias y acciones.
   - Negrita solo para la idea clave de cada viñeta (no frases enteras); cursiva solo para
     términos en inglés (spread, wild bootstrap, backstop, doom loop).
   - Tablas con booktabs (toprule, midrule, bottomrule), sin líneas verticales, cifras alineadas.

4. CONSISTENCIA DE CONTENIDO
   - Notación igual en todo el deck: \JLoss, \GaR, D = -\GaR, \EMBI; rezagos como _{t-1};
     decimales con coma ({,}); "pb" para puntos básicos.
   - Las mismas cifras deben coincidir donde se repitan: elasticidad 0,10 (0,0985), 4,7 pb por
     unidad de JLoss, +3,3 % por punto de D, retroalimentación 0,17, interacción promedio
     -0,011 (p = 0,11), núcleo sin crisis +0,034 y +1,8 pb (wild bootstrap p = 0,015 y 0,002),
     N = 765 con 13 economías (799 y 14 con Argentina). Si encuentras una cifra distinta,
     no la cambies: márcala en el resumen final.
   - Terminología única: "fragilidad bancaria", "riesgo de cola del crecimiento",
     "spread soberano", "amplificación", "evidencia condicional".
   - El mensaje debe ser el mismo en motivación, resultados, síntesis y conclusión: hay
     asociación, no causalidad; la amplificación no aparece en promedio sino en momentos y
     economías específicas, como evidencia condicional y no robusta.

5. ESTRUCTURA Y NAVEGACIÓN
   - La tabla de contenidos debe reflejar las secciones actuales; las láminas nuevas deben
     quedar dentro de "Motivación y pregunta".
   - Las láminas de respaldo siguen después de \appendix y no cuentan en la exposición.
   - El total debe quedar entre 40 y 42 láminas. Si para resolver desbordes divides una lámina,
     compensa fusionando o recortando otra del respaldo.

6. REDACCIÓN
   - Español claro y directo; frases cortas; sin repetir la misma idea en láminas seguidas.
   - Revisa ortografía y tildes, concordancia (el capítulo, la sección), y que no queden
     anglicismos innecesarios fuera de los términos técnicos en cursiva.

Al terminar: compila sin errores ni Overfull, confirma el número total de láminas y entrega la
lista de cambios y de cualquier cifra o afirmación que te haya parecido inconsistente.
```

## Notas

- **Revisar lo que marque.** Si Prism reporta cifras inconsistentes, compáralas con
  `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` (secciones 10–14) antes de corregir.
- **Volver al repositorio.** El `defensa.tex` del repositorio no tiene todavía las láminas hechas
  en Prism: hay que descargar la versión final desde Prism para integrarla, regenerar el zip y
  hacer push.
