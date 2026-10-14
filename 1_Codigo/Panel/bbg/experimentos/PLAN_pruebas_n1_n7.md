# Plan de las pruebas N1–N7 (experimento, 14 de octubre de 2026)

**Estado:** experimento. Nada se integra a la tesis, el paper ni las láminas. Cada prueba corre en un
subagente propio, en paralelo, y guarda avances en disco y en git a medida que avanza.

**Hilo conductor actual** (lo que estas pruebas buscan afirmar o mejorar):
1. Los dos riesgos domésticos coinciden más que por azar (1,2–1,3 veces neto del calendario común), y
   la fragilidad bancaria antecede al riesgo económico (sugerente).
2. Cuando coinciden no hay evidencia de amplificación (no se descarta un extra de hasta 30–40 % de la
   suma).
3. El riesgo económico agrega poco y solo en niveles; en este panel se mueve casi enteramente con el
   crecimiento esperado.
4. Ninguna condición estudiada cambia la transmisión.
Réplica: la fragilidad se asocia con el spread (Chari et al., 2024), pero no es una elasticidad común
y se mueve con el spread dentro del mismo trimestre.

## Reglas comunes a las siete pruebas
- **Declaración previa:** cada script empieza con un bloque fechado "DECLARADO ANTES DE ESTIMAR" con
  la hipótesis, el signo esperado, el contraste único que da el veredicto y la regla de decisión.
  No se agregan pruebas después de ver resultados; si algo extra se hace, se rotula "agregado
  después".
- **Base común:** panel de la principal (`x0_comun.datos()`: N = 765; 0,0985 / 0,0324 / −0,0112),
  efectos fijos de país y tiempo salvo que la prueba diga otra cosa; inferencia con wild bootstrap
  por país (Webb), reportando también Driscoll–Kraay y cluster por país.
- **Se reporta todo**, salga como salga.
- **Guardar avances:** después de cada paso, el subagente actualiza `n<k>_AVANCE.md` (qué está
  hecho, qué falta, cifras obtenidas) y hace commit **solo de sus propios archivos** `n<k>_*`.
- Scripts, salidas y reporte en `1_Codigo/Panel/bbg/experimentos/`, con prefijo `n<k>_`.

---

## N1 · La fragilidad bancaria dentro del Growth-at-Risk
**Pregunta.** ¿La fragilidad bancaria predice la cola baja del crecimiento futuro, más allá del índice
de condiciones financieras? Si sí, los dos riesgos son una cadena (bancos → cola del crecimiento →
spread), no dos riesgos paralelos.
**Diseño.**
1. Reproducir la regresión cuantílica de panel del GaR (insumos: `1_Codigo/GaR/individuals/nlhpc_gar_all18/GaR_panel_all18.xlsx`, crecimiento interanual, FCI, VIX; el código del motor está en `1_Codigo/GaR/`) en su versión en muestra.
2. Agregar ln JLoss(t) como predictor del crecimiento en t+1 y t+4, para los cuantiles 5, 10, 25 y
   50 %, con efectos de país.
3. **Contraste primario:** coeficiente de ln JLoss en el cuantil 5 % a un año, negativo; inferencia
   por bootstrap de bloques por país (B = 499). Secundario: que sea mayor en valor absoluto en la cola
   que en la mediana (asimetría).
4. Pronóstico fuera de muestra (ventana expansiva): pérdida cuantílica del GaR con y sin JLoss.
5. Construir el GaR "con fragilidad" y volver a estimar la regresión del spread: ¿cuánto de la
   asociación de la fragilidad pasa por el riesgo de cola?
**Regla.** Cadena respaldada si el coeficiente al 5 % es negativo con p < 0,05 y mejora el pronóstico.

## N2 · La no linealidad con el precio global del riesgo
**Pregunta.** ¿Los riesgos domésticos pesan más en el spread cuando la aversión global al riesgo es
alta?
**Diseño.** Principal + J×ln VIX(t) + D×ln VIX(t) (el nivel del VIX lo absorben los efectos de
tiempo). **Contraste primario:** D×VIX > 0 (riesgo económico cobrado más caro con aversión alta);
J×VIX se reporta como réplica de Chari et al. Holm sobre los dos. Variantes declaradas: spread de
alto rendimiento en vez del VIX; VIX rezagado; terciles de VIX; puntos básicos; sin Turquía y sin
Polonia; excluir crisis.
**Regla.** Respaldada si D×VIX > 0 con p wild < 0,05 tras Holm y estable al excluir países.

## N3 · El bucle banco–soberano donde la teoría dice que debe estar
**Pregunta.** ¿El spread deteriora más a los bancos donde estos tienen más deuda pública?
**Diseño.** Ecuación inversa: ln JLoss(t) sobre ln EMBI(t−1), su interacción con la participación de
los bancos domésticos en la deuda del gobierno (rezagada 4 trimestres, estandarizada; hoja
"Table 3.2 DomesticBank" de `2_Datos/Database_For_Posting_EM_Frozen.xlsx`), ln JLoss(t−1), D(t−1) y
efectos fijos. **Contraste primario:** interacción > 0. Placebo: la participación del banco central
doméstico. Variantes: en diferencias; con el spread de cierre; sin Turquía y sin Polonia.
**Regla.** Bucle respaldado si la interacción es positiva con p wild < 0,05 y el placebo es nulo.

## N4 · Afirmar la aditividad: prueba de equivalencia y versión bayesiana
**Pregunta.** ¿Se puede afirmar que la amplificación es pequeña, y no solo que no se encontró?
**Diseño.**
1. Prueba de equivalencia (dos pruebas unilaterales) para β3 con márgenes declarados: un extra de la
   amplificación de 10 % y de 20 % de la suma de los dos efectos cuando ambos riesgos están una
   desviación estándar dentro del país sobre su media. Intervalos al 90 % con Driscoll–Kraay, cluster
   y wild bootstrap invertido.
2. Modelo jerárquico normal–normal (meta-análisis bayesiano) de las interacciones por país:
   probabilidad posterior de que la amplificación media supere cada margen; heterogeneidad entre
   países.
3. Lo mismo en puntos básicos y con el spread de cierre.
**Regla.** Aditividad afirmada si los intervalos al 90 % caen dentro del margen de 20 %.

## N5 · Estimador con factores comunes (Pesaran, 2006)
**Pregunta.** ¿Qué queda de cada coeficiente si cada país puede reaccionar distinto a los factores
globales no observados?
**Diseño.** Estimadores CCE agrupado (CCEP) y de grupo medio (CCEMG): cada país aumentado con los
promedios transversales del spread y de los regresores, con cargas propias. Errores del grupo medio
no paramétricos. Prueba CD de Pesaran sobre los residuos. Comparación con efectos fijos de dos vías.
Excluir Turquía y Polonia. Países con menos de 30 trimestres fuera del grupo medio.
**Regla.** Una conclusión se afirma si su signo y orden de magnitud se mantienen con CCE.

## N6 · Dirección dentro del trimestre: heterocedasticidad (Rigobon, 2003) e instrumento granular
**Pregunta.** Fragilidad y spread se mueven juntos en el mismo trimestre: ¿en qué dirección?
**Diseño (datos diarios).**
1. Retorno diario del índice bancario de cada país (capitalización por banco,
   `1_Codigo/Bloomberg_extraction/output/<pais>/mktcap_<pais>.csv`) y cambio diario del spread (EMBI
   diario de `2_Datos/embi.xlsx`; CDS diario donde no hay EMBI).
2. **Rigobon:** regímenes de volatilidad declarados (trimestres de VIX alto frente a bajo, y ventanas
   de crisis); estimar por momentos ambos efectos contemporáneos (banca → spread y spread → banca),
   agrupado y por país, con bootstrap.
3. **Instrumento granular (Gabaix y Koijen):** choques propios de los bancos grandes (retorno
   ponderado por tamaño menos el ponderado igual, neto del factor común) como instrumento del
   retorno bancario en la ecuación del spread; primera etapa F; efectos de país-año.
**Regla.** Dirección banca → soberano respaldada si ambos métodos dan un efecto positivo
significativo de la banca sobre el spread.

## N7 · Spread-en-riesgo: regresión cuantílica del spread
**Pregunta.** ¿Los riesgos mueven la cola alta del spread más que su promedio? ¿Aparece la
amplificación en la cola?
**Diseño.** Regresión cuantílica de panel con efectos fijos (método de momentos de Machado y Santos
Silva, 2019) de ln EMBI sobre J, D y J×D rezagados, cuantiles 10, 25, 50, 75 y 90 %; bootstrap por
bloques de país (B = 499). **Contrastes primarios:** (a) efecto de D y de J en el cuantil 90 % mayor
que en la mediana; (b) interacción en el cuantil 90 %. Variante: puntos básicos; sin Polonia.
**Regla.** "Los riesgos mueven la cola del spread" si la diferencia 90 %–50 % es positiva con
p < 0,05.

---

## Reporte final
`REPORTE_pruebas_n1_n7.md`: una sección por prueba con la tabla principal, el veredicto según su regla
y qué cambiaría en el hilo conductor. Commit local; sin push; nada integrado.
