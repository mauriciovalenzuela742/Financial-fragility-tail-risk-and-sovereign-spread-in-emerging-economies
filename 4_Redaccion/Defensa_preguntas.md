# Defensa de la tesis — 30 preguntas del profesor y guion de respuesta

*Preparación para el examen de grado. Cada respuesta se apoya en números trazables a
`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` y a los CSV del pipeline. Formato: **P** =
pregunta que probablemente hará la comisión; **R** = respuesta corta con cifras listas para
citar; **Si insiste** = la línea de defensa de segundo nivel.*

Complemento específico para la construcción del GaR:
`1_Codigo/Defensa_GaR_preguntas_respuestas.md`.

> **Aviso (2026-10-21).** Las secciones A a G y las preguntas de cierre son del encuadre del
> 2026-09-02 y quedan como **archivo**. Ese encuadre usaba la especificación en niveles
> contemporánea, θ = −0,47 en el núcleo de 11 como hallazgo central y el capítulo de OI, y nada
> de eso es vigente. Para la defensa vale la sección **V**, que va a continuación. Sus cifras están
> en la tesis vigente y en las secciones 17–19 de `NUMEROS_CANONICOS_BBG.md`.

---

## V. Preguntas vigentes (tesis del 2026-10-21)

**V1. Si H3 no se sostiene y los coeficientes de nivel no se distinguen del sesgo de
retroalimentación, ¿qué aprendemos en positivo?**
**R.** Hay tres cosas.
- Los dos riesgos coinciden más que por azar, también descontado el calendario común: 168
  observaciones frente a 140,9 esperadas, 1,2 veces (p = 0,0002).
- La fragilidad antecede al riesgo de cola (0,405; wild p = 0,024). Lo hace sin depender de un
  país (0,32–0,47) y también con el GaR sin bloque bursátil (0,388; wild p = 0,002).
- Una prueba de equivalencia descarta una amplificación de más de un 35 % de la suma de las dos
  asociaciones.

**Si insiste:** el aporte metodológico es separar la aditividad en logaritmos (que equivale a
proporcionalidad en pb) de la amplificación, y medir con qué inferencia se puede leer un panel
de 13 países.

**V2. ¿La simultaneidad no es solo 2020?**
**R.** No. En 2020–22 lo observado iguala a lo esperado por el calendario (razón 1,01). El exceso
viene de 2015–19 (2,9 veces; p = 0,0002) y de 2023–26 (1,3 veces; p = 0,0002).

**V3. ¿Por qué antes decía "1,9 veces" y ahora "1,2"?**
**R.** Porque la nula importa. El 1,9 se compara con la independencia pura, que ignora que
todas las economías se estresan a la vez. El 1,2 conserva cuántas economías tienen el riesgo de
cola alto en cada trimestre. Las dos nulas se rechazan, y la cifra que se usa es la exigente.

**V4. ¿La precedencia fragilidad → riesgo de cola no es mecánica? El FCI y JLoss usan precios
accionarios.**
**R.** Con el GaR reconstruido sin el bloque bursátil, el coeficiente sube (0,388 frente a
0,301 con el bloque, ambos dentro de la muestra). La dirección inversa nunca es significativa.
**Si insiste:** quedan dos límites. Con tres o cuatro rezagos el wild bootstrap ya no rechaza
(p = 0,11 y 0,15), y no se puede fechar dentro del trimestre porque el GaR es trimestral.

**V5. Si JLoss satura la malla en el 98 % de los casos, ¿por qué no usar directamente la PD media
de Merton?**
**R.** La variación de JLoss la gobierna la pérdida esperada, es decir, las PD de Merton
ponderadas, de modo que en la práctica es eso. La métrica se lee como ordinal, el logaritmo es
invariante a su escala, y con la malla ancha la correlación es de aproximadamente 0,9.
*(Pendiente: la mejora B6 de `evaluacion_experta.md` lo estima directamente.)*

**V6. ¿Por qué cambió de CDS a EMBI, de niveles a logaritmos y de contemporáneo a rezago? ¿Qué
se decidió antes de ver qué resultado?**
**R.** El EMBI y el rezago siguen a Chari et al. (2024). Los logaritmos los prefiere la prueba
PE. La agrupación de 11 economías se declaró exploratoria porque nació de ver los datos. La
prueba de participación extranjera se escribió el 13-oct, antes de estimar, con su consecuencia
fijada. La tesis reporta las cuatro combinaciones de forma funcional y rezago.

**V7. Turquía aporta el 70 % de β₁ y Polonia el signo de β₃. ¿Hay un resultado común?**
**R.** No para la fragilidad: las pendientes por país van de −0,84 a +0,97, y la homogeneidad se
rechaza. Por eso la tesis no la presenta como una elasticidad común. El riesgo de cola es
positivo en 10 de las 13 economías.

**V8. ¿Qué diferencia hay entre su "aditividad" y la proporcionalidad mecánica del logaritmo?**
**R.** Con una intensidad de incumplimiento λ = λ₀·JLoss^β₁·e^(β₂D), el spread es
multiplicativo. En pb la complementariedad sale sola, sin ningún término de interacción. La
amplificación exige β₃ > 0 en log-log, y eso es lo que se contrasta.

**V9. El pronóstico fuera de muestra no usa el GaR recursivo ni efectos fijos de tiempo. ¿Para
qué incluirlo?**
**R.** Se declara como evidencia débil en cualquier dirección. Lo que muestra es que ningún
modelo le gana al spread rezagado, tampoco el que agrega la fragilidad.

**V10. ¿Cómo se relaciona con Debt-at-Risk del FMI (Fiscal Monitor, oct. 2024)?**
**R.** Debt-at-Risk lleva la lógica de riesgo de cola a la trayectoria de la deuda. Esta tesis
la lleva al precio de la deuda y la cruza con la fragilidad bancaria, de modo que son
complementarios.

**V11. La prueba preespecificada está en el encabezado del código y no en un registro externo.
¿Cómo lo acredita?**
**R.** No se puede acreditar con un registro externo, y el historial de git tampoco ayuda:
`p26_participacion_extranjera.py` se commiteó por primera vez el 21-oct, junto con sus
resultados. La tesis lo declara como limitación. Lo que sí hay es la consecuencia escrita de
antemano, y la tesis la acató aunque le era desfavorable: el núcleo de 11 pasó a exploratorio.
**Si insiste:** reconocerlo sin rodeos y presentar la prueba como "declarada antes de estimar
por el autor, sin registro verificable".

**V12. Si la causalidad no está identificada, ¿para qué sirve la tesis a un banco central?**
**R.** Para vigilar los dos riesgos juntos, porque coinciden y la fragilidad antecede al
deterioro de la cola del crecimiento. No justifica una prima regulatoria adicional por la
simultaneidad, porque una amplificación grande queda descartada.

**V13. Su tesis dice que la fragilidad no antecede al spread. ¿Y a frecuencia mensual?**
**R.** A frecuencia mensual sí lo antecede. Con la distancia al incumplimiento de Merton mensual (los
mismos bancos y el mismo motor) y el EMBI diario, un aumento de la fragilidad en un mes va seguido de
un spread mayor el mes siguiente (0,013; DK p = 0,005; wild del Wald p < 0,001). Se mantiene sin cada
uno de los 13 países, y la dirección inversa no existe (wild p = 0,39). La magnitud es pequeña: una
d.e. lleva a +0,6 % el mes siguiente.
**Si insiste:** es precedencia, no causalidad. Las acciones bancarias pueden incorporar antes la misma
información que después recoge el spread.

**V14. ¿Probó un instrumento propiamente bancario?**
**R.** Sí, el granular de Gabaix y Koijen: el retorno de los bancos grandes ponderado por tamaño menos
el de igual peso. Es débil (F de 1,8 a 3,2) y su exclusión es dudosa (responde al spread del mismo
trimestre, p = 0,04). Con 3 a 10 bancos por país no alcanza. Se reporta.

**V15. ¿Y el estudio de eventos del respaldo?**
**R.** Se estudiaron nueve anuncios. Las swap de la Fed de marzo de 2020 bajaron el spread de Brasil y
México entre 20 y 22 pp en una semana, frente a los demás países. Las FCL no lo movieron. La relación
diaria banca–spread se acerca a cero después de los eventos, pero igual en los países sin línea: no
hay desacople atribuible al respaldo.

**V16. ¿Qué aprendió de la deuda, las reservas y los controles?**
**R.** Con una prueba preregistrada (commit `c492ca3`, anterior a los datos) y datos trimestrales hay
un resultado firme y dos nulos. Donde hay más deuda pública, el riesgo de cola pesa más en el spread:
una d.e. más de deuda eleva la semielasticidad de 0,032 a 0,043 (Holm p = 0,029; 13 de 13 sin cada
país). La adecuación de reservas no atenúa la transmisión de la fragilidad (Holm 0,29). Y el efecto
directo de la fragilidad, neto del canal fiscal, es ≈ 0.
**Si insiste:** R-H3 no es significativa con Driscoll–Kraay (p = 0,17), y se debilita con la deuda en
t−8. El criterio preregistrado era el wild bootstrap, que la simulación de la tesis muestra mejor
calibrado.

**V17. ¿No dependía el riesgo de cola de Polonia?**
**R.** En la regresión con efectos fijos de tiempo, sí. Pero si cada país responde distinto a los
factores comunes (CCE de Pesaran), resiste el wild bootstrap y la exclusión de cada país. La media de
efectos aleatorios es 0,022 sin Polonia (p = 0,011), y el PMG da una relación de largo plazo de 0,067.
Es un fundamento de nivel, no una señal de corto plazo.

**V18. ¿Cuál es el hallazgo principal de la tesis?**
**R.** Que los dos riesgos domésticos tienden a darse juntos, pero cuando coinciden no hay evidencia de que
se amplifiquen: se descarta una amplificación mayor que un 35 % de la suma. Es la respuesta a la pregunta
de la tesis, y es lo más firme. La pregunta que más pruebas recibió, la de si la deuda amplifica el riesgo de
cola, deja una regularidad de la muestra (+0,033 por d.e. de deuda con el riesgo de cola a un año;
permutación p = 0,009) que ni la réplica externa, ni el instrumento, ni el modelo confirman.
**Si insiste en el doom loop:** la deuda no amplifica la transmisión de la fragilidad bancaria (−0,053) ni
el efecto se concentra en la deuda en moneda extranjera.

**V19. Si el GaR pronostica el crecimiento del trimestre siguiente, ¿no debería entrar con dos rezagos?**
**R.** No hace falta. Lo que importa es con qué información se calcula: GaR_{t−1} usa solo datos de t−1 y
es anterior al spread de t. Igual se probó: con GaR_{t−2} el coeficiente es 0,034 frente a 0,031, y nada
más cambia (p45b). Con los dos rezagos se reparten el coeficiente, porque correlacionan 0,64.

**V20. Tiene 87 bancos. ¿Por qué no usa los bancos para identificar el canal bancario?**
**R.** Lo hice, con un tercer preregistro anterior a los datos (p46–p51). La fragilidad de los bancos
grandes responde más al spread y la asociación se concentra en los dos bancos sistémicos (0,062 frente a
0,022), como predice el pasivo contingente, pero ninguna de las seis hipótesis pasa Holm. Las filiales
extranjeras pesan igual que los nacionales y más banca estatal va con *menos* transmisión.
**Si insiste en la calibración del motor:** con ρ por banco, otro punto de incumplimiento o la malla
ancha, JLoss correlaciona 0,92–0,97 con la base y β₁ sigue positivo (p47). Lo frágil es el número de
bancos: con al menos cuatro por economía la fragilidad pierde significancia; el riesgo de cola no.

**V21. ¿Qué umbral le recomendaría a un banco central?**
**R.** Ninguno, y lo probé con un preregistro (p52–p53). No hay un nivel de tensión financiera ni de deuda
desde el cual la transmisión cambie (Holm 0,38 y 0,52), y estimados país por país los umbrales de deuda y
de riesgo de cola son distintos entre economías: no son transferibles. La regla que respaldan los datos es
continua: el riesgo de cola debe vigilarse con más atención cuanto mayor es la deuda.
**Si insiste en la potencia:** para un umbral que duplique la pendiente, la potencia es de 68 % con la
tensión financiera, pero de 13 % con la deuda; ahí la ausencia de umbral es poco informativa.
**Si pregunta por alerta temprana:** fuera de la muestra el AUROC es 0,49; dentro, 0,71. Con más
tensión los riesgos domésticos pesan menos: en una crisis manda el ciclo global.

**V22. Hizo cuatro preregistros con catorce hipótesis. ¿Sobrevive algo a todas juntas?**
**R.** Lo probé (p56). Con Holm sobre las catorce, ninguna queda bajo 0,05; la más cercana es el riesgo de
cola a un año (0,08). Y al asignar a cada economía la deuda de otra, la amplificación con el riesgo de cola
del trimestre siguiente no se distingue del azar (p = 0,17): por eso la tesis la trata como sugerente. Con el
riesgo de cola del año siguiente sí resiste (p = 0,009), y esa es la versión del hallazgo central que sostengo.
**Si insiste en que era secundaria:** es cierto, y lo declaro; por eso la presento como la versión que resiste
la prueba más exigente, no como la hipótesis preregistrada primaria.

**V23. ¿Replicó el hallazgo central fuera de la muestra?**
**R.** Lo intenté, con un preregistro (p57). En Hungría y Corea el signo se repite, pero la interacción es
siete veces la original y la diferencia se rechaza, así que según el criterio que fijé no replica. En
Hungría, la única con EMBI, el coeficiente es casi igual al original (0,025 frente a 0,033), pero no
significativo, y la réplica tenía una potencia de 5 %: con dos economías no se puede precisar.
**Si pregunta por causalidad:** el instrumento de términos de intercambio (p58) mueve bien el riesgo de cola
(F = 20), pero es débil para la interacción con la deuda (F = 9,7) y la estima nula. Por eso digo que el
hallazgo es de la muestra original.

**V24. ¿Tiene un modelo que explique el hallazgo central?**
**R.** Sí, y no lo explica (p59, preregistro 6). Un modelo de límite fiscal calibrado con el panel predice
que, con más deuda, el riesgo de cola pesa más en puntos básicos, pero menos en logaritmos: la cola
izquierda normal hace que la sensibilidad proporcional caiga cuando el incumplimiento ya es probable. La tesis
estima lo contrario en logaritmos. En puntos básicos los datos dan el signo del modelo (+3,1 pb), pero no es
firme y es muy menor que lo que predice el modelo (10 a 203 pb).
**Si pregunta por qué el modelo exagera tanto:** el GaR mide la cola con error, una parte grande del spread
es prima global y el modelo no tiene aversión al riesgo. Ninguna de esas explicaciones se contrastó.

**V25. Si casi nada se confirma, ¿cuál es su contribución?**
**R.** Tres cosas. Primera, la pregunta de la tesis tiene respuesta: los riesgos coinciden y no hay
amplificación grande, algo que nadie había contrastado porque nadie había cruzado las dos métricas.
Segunda, las series son homogéneas, reproducibles con un comando y quedan disponibles. Tercera, la tesis
muestra con seis preregistros qué resiste y qué no con trece países, y el modelo de límite fiscal muestra
que la predicción teórica sobre deuda y riesgo de cola es en puntos básicos, no en logaritmos.

**V26. ¿Por qué cambió tanto el hallazgo central entre versiones?**
**R.** Porque lo sometí a pruebas cada vez más exigentes y reporté cada una: primero dos preregistros,
después la corrección conjunta, la réplica externa, el instrumento y el modelo. Los datos no cambiaron;
cambió cuánta confianza merece el resultado. Cada cambio está fechado en el historial del repositorio.

**V27. ¿Seis preregistros no son otra forma de buscar hasta encontrar algo?**
**R.** Al revés: cada uno se fijó antes de sus datos y la corrección conjunta trata los cuatro primeros como
una sola familia (p56). Con esa corrección ninguna hipótesis queda bajo 0,05. Si buscara resultados, no los
habría reportado así.
**Si insiste:** las pruebas posteriores (réplica, instrumento, modelo) solo podían confirmar o debilitar el
resultado, y lo debilitaron.

**V28. ¿Qué haría con un año más de investigación?**
**R.** Tres cosas:
- ampliar la muestra a 20–25 economías con Refinitiv o Bloomberg, para que la réplica tenga potencia (con
  dos economías era de 5 %);
- buscar variación exógena en la deuda, como reestructuraciones o cambios de reglas fiscales, en vez de en
  el riesgo de cola;
- extender el modelo con inversionistas aversos al riesgo y una recuperación que caiga con la deuda, que son
  las candidatas para explicar la interacción en logaritmos.

---

> **Encuadre de archivo (2026-09-02).** La variable dependiente es el **EMBI Global Diversified**
> (como en Chari et al. 2024); el CDS 5A es robustez. Panel de **13 países** (Hungría excluida
> por bancos mínimos). El hallazgo central: los canales de **nivel** (H1 `JLoss→spread`, H2
> `GaR→spread`) están bien identificados; la **complementariedad** (H3, θ) es **condicional** —
> θ = −0,16 (n.s.) sobre la muestra completa, pero **θ = −0,47 (p = 0,023)** sobre el núcleo
> de 11 economías emergentes de financiamiento externo, diluyéndose al añadir Polonia e India.
> EMBI y CDS dan el mismo θ sobre la misma submuestra: **la métrica no cambia el resultado; la
> composición de la muestra sí.**

---

## A. Pregunta de investigación, contribución y posicionamiento

**P1. ¿Qué añade esta tesis a Chari et al. (2024), que ya introdujo `JLoss` en el spread
soberano de emergentes? ¿No es solo cambiar un regresor?**
R. Chari et al. interactúan `JLoss` con el **ciclo financiero global exógeno** (VIX, tasa
del Tesoro, HY): dicen *cuándo un choque de fuera golpea más fuerte a los países con banca
frágil*. Esta tesis interactúa `JLoss` con una vulnerabilidad **doméstica y endógena** —el
riesgo de cola del propio crecimiento del país, que la fragilidad bancaria ayuda a generar
por el canal de *credit crunch* y que retroalimenta el costo fiscal del rescate. Cierra el
triángulo banca–crecimiento–soberano que la literatura solo había analizado por pares.
Además: el Capítulo 3 deriva esa complementariedad de un modelo estructural de organización
industrial, algo que Chari et al. no hacen.
Si insiste: la contribución de método es el *pipeline* homogéneo (JLoss de 113 bancos con un
solo protocolo Bloomberg) y la delimitación honesta de fronteras, no la magnitud del
coeficiente.

**P2. El antecedente más próximo lo coescribe su profesor guía. ¿Cómo se distingue su
aporte del de ese grupo?**
R. Comparto las métricas (`JLoss`, marco GaR-CEMLA) pero el objeto es distinto: la
interacción con la cola doméstica, el modelo de OI que la microfundamenta, y la prueba —de
resultado no concluyente— de la amplificación por concentración. El *pipeline* y todos los
números son reproducibles y están versionados.

**P3. Si tuviera que resumir el aporte en una frase, ¿cuál es?**
R. La fragilidad bancaria sistémica y el riesgo de cola del crecimiento elevan cada uno el
spread soberano de las economías emergentes, y su coincidencia lo amplifica de forma
**complementaria** —pero solo en las economías más expuestas al financiamiento externo de
cartera. Se caracteriza *dónde* y *cuándo* esa complementariedad aparece en los precios
soberanos, se la deriva de un modelo estructural de organización industrial bancaria, y se
delimita con precisión qué parte está respaldada y qué parte no.

**P4. ¿Por qué dos capítulos-paper y no un solo artículo integrado?**
R. Son dos objetos de conocimiento que se validan con estándares distintos: el empírico con
significancia/robustez/identificación; el teórico con existencia, unicidad y signos de
estática comparativa deducidos de supuestos explícitos. Separarlos deja que cada uno cumpla
su estándar. La introducción y la discusión general muestran por qué juntos son más que la
suma.

---

## B. Medición de la fragilidad — `JLoss`

**P5. `JLoss` medio es 4,8 y la cota superior de la malla de pérdidas del motor es 4,8 %.
¿No está la métrica pegada al techo?**
R. Verificado (`_diag_censura.py`): la cota **satura el VaR99 en el 98 % de los
país-trimestre**. `JLoss` mide, en la práctica, la pérdida esperada (probabilidades de
Merton) más una contribución de cola evaluada a un **nivel de estrés fijo**, no en el
percentil 99 verdadero. Consecuencia: la variación de `JLoss` la gobierna la pérdida
esperada, no la forma de la cola.
Si insiste: recalculé el motor con una malla más ancha. `JLoss` escala por un factor de
varias veces (heterogéneo entre países) pero preserva en lo esencial el ordenamiento
(correlación ≈ 0,9 con la base). Por eso `JLoss` se interpreta **ordinalmente** —como un
ranking de fragilidad relativa entre países y en el tiempo— y no en niveles, y así lo dice
el §4.1.

**P6. ¿Por qué excluye a Corea del Sur, Bulgaria y Hungría y deja a China?**
R. El criterio es único: que `JLoss` no sea una medida sistémica a nivel de país por número
de bancos cotizados insuficiente. Corea: el valor de mercado de la banca es ≈4 % del punto de
incumplimiento (frente a 15–34 % en el resto), reflejo del *Korea discount*, no de la
solvencia; Merton lo lee como incumplimiento inminente y devuelve `JLoss` 25–47. Bulgaria: un
solo banco cotiza (FIBank), 76/76 trimestres bajo el mínimo. **Hungría: dos bancos cotizados
(OTP dominante), `below_min_banks` en 89/89 trimestres** —mismo criterio que Bulgaria. (En la
versión previa con CDS, Hungría no era candidata porque solo tenía 14 trimestres de CDS; al
pasar la DV al EMBI —que le da 89— la exclusión debe hacerse explícita.) China: `JLoss`
mediano 3,8, máximo 29 —elevado pero no implausible, con 9 bancos cotizados. Es una exclusión
por **insumo no válido**, no por dato faltante.
Si insiste: China es la exclusión que más condicionaría el resultado —lo digo en las
limitaciones (§7). Por eso reporto la robustez sin China de forma prominente (sin China, θ
cae a −0,05 sobre la muestra completa).

**P7. `JLoss` es un regresor estimado, no observado. ¿No invalida eso la inferencia sobre
θ?**
R. Es una limitación real (§7). Dos cosas la acotan: (i) el error de medición
clásico en un regresor **atenúa** el coeficiente hacia cero, así que el θ reportado es un
límite conservador; (ii) perturbando `GaR` con ruido creciente, θ es estable hasta el 25 %
de su desviación (θ ≈ −0,16) y solo baja a −0,15 con el 50 %, sin cambiar de signo. Un
*bootstrap* que re-estime la regresión cuantílica de `GaR` en cada réplica queda como
refinamiento pendiente (es ~45.000 solves del programa lineal).

**P8. El `JLoss` de Bloomberg está mucho más comprimido que el regulatorio (sd ≈ 4,6 vs 8,3).
¿No debería preocuparle que la métrica "buena" dé menos señal?**
R. Es el precio de la homogeneidad: un solo protocolo elimina la heterogeneidad de
definiciones contables entre supervisores, pero también comprime la dispersión —en la
versión regulatoria, Brasil solo concentraba `JLoss` ≈ 16. Esa compresión es la razón más
probable de que la prueba de amplificación por concentración (H4b) quede sin potencia, y
contribuye a que la interacción de primer orden (θ) solo se identifique en el subconjunto de
economías con variación real de fragilidad.

**P9. ¿Por qué ρ = 0,4 y LGD = 0,45 y no otros valores?**
R. Son los parámetros de Chari et al. (2024), a su vez estándar (LGD 45 % es Basilea II para
exposiciones no garantizadas). El objetivo era comparabilidad con esa reconstrucción, no
recalibrar. La sensibilidad del método a ρ se examina en la validación Monte Carlo del
Capítulo 3.

---

## C. Medición del riesgo de cola — `GaR`

**P10. `GaR` no viene de Bloomberg —rompe el principio de homogeneidad de fuente.**
R. Correcto y explícito (Anexo B): los insumos reales del FCI (PIB, IPC, índice accionario,
REER, rendimiento 10Y) son estadísticas nacionales porque Bloomberg no es fuente primaria de
cuentas nacionales. Lo que sí es homogéneo es la métrica de fragilidad —`JLoss`, con
balances y capitalización de los 113 bancos de un solo protocolo Bloomberg—; el spread es el
EMBI Global de J.P. Morgan (el índice de referencia de la literatura, como en Chari et al.).
En la agenda está extraer de Bloomberg los componentes de mercado del FCI (índice accionario,
REER, 10Y) para cerrar más el círculo.

**P11. La media de `GaR` (q05) es +1,6 pp. ¿Un percentil 5 del crecimiento positivo?**
R. Es el cuantil 5 % del crecimiento interanual condicional un trimestre adelante, promediado
sobre las ~720 observaciones-país que incluyen muchos trimestres de expansión en emergentes.
El rango es [−19; +14] pp: en los episodios de estrés `GaR` es marcadamente negativo, que es
donde el mecanismo se identifica. La convención: más negativo = más riesgo a la baja.

**P12. ¿Por qué el cuantil directo y no la skew-t de Adrian et al.?**
R. El cuantil condicional es el objeto primitivo del estimador de Koenker; la skew-t es una
elección de suavizado. Uso el cuantil directo (con reordenamiento de Chernozhukov et al.
2010) y conservo la skew-t como robustez: la correlación entre ambas series de `GaR` es
0,9996, y θ con `GaR` skew-t es −0,16 (n.s.), idéntico al del cuantil directo —la (no)
significancia sobre la muestra completa no depende de la especificación de la cola.
(Detalle en `Defensa_GaR_preguntas_respuestas.md`.)

---

## D. Spread soberano, controles y concentración

**P13. ¿Por qué EMBI y no CDS?**
R. El EMBI Global Diversified es el índice de referencia de la literatura de spreads
soberanos de economías emergentes y la variable dependiente del trabajo más próximo (Chari
et al. 2024). El CDS a cinco años aísla mejor el componente puro de riesgo de crédito, y por
eso se conserva como **serie de robustez**. Lo decisivo: en la submuestra donde ambas series
coexisten (606 observaciones, correlación 0,86) arrojan **el mismo coeficiente de
interacción** (θ ≈ −0,7, p ≈ 0,05). La elección de la métrica no cambia el resultado.
Si insiste: una versión previa de este panel usaba el CDS y daba θ = −0,35 (p = 0,056). La
diferencia con el θ actual (−0,16 sobre la muestra completa) **no es la métrica**, es que el
CDS de Bloomberg estaba truncado para Polonia (14 trimestres) y ausente para India, mientras
el EMBI les da 89 y 54 —y esas economías diluyen la interacción (ver P18).

**P14. Los controles domésticos son anuales interpolados a trimestral. La variación
trimestral es un artefacto.**
R. Cierto para deuda/PIB, balance fiscal, reservas y cuenta corriente (§7). Son variables
lento-móviles y la interpolación lineal es estándar para ellas. Bajo efectos fijos
bidireccionales su variación intra-anual identificable es escasa, de modo que sus
coeficientes **no tienen un signo económico fiable** (la deuda/PIB, por ejemplo, sale con
signo negativo, y la correlación *within* entre EMBI y deuda/PIB es de apenas +0,10). Se
incluyen como controles, no se interpretan; lo relevante es que θ **conserva el signo** y la
(no) significancia con y sin ese bloque.

**P15. El HHI del GFDD es casi invariante en el tiempo. ¿Cómo puede identificar β4?**
R. No puede bien —es exactamente el problema de H4b. Por eso construí una serie de
concentración **trimestral** (`p6_concentracion_trimestral.py`) a partir de los mismos
balances Bloomberg que `JLoss`: CR3/HHI de los bancos cotizados, por país y trimestre.
Correlación ≈ 0,5 con el GFDD anual. Con esa variación temporal real, β4 sigue sin
identificarse (ver P30).
Si insiste: la limitación de la serie trimestral es que mide la concentración del *segmento
cotizado*, no del sistema completo —igual que `JLoss`, no observa bancos no listados.

---

## E. Identificación econométrica de θ (H3)

**P16. θ no es significativo sobre la muestra completa (p = 0,26). ¿Qué queda del hallazgo
central?**
R. Dos cosas quedan sólidas. Primero, los **canales de nivel**: β₁ (`JLoss → spread`) = +2,8
(t = 2,7) y β₂ (`GaR → spread`) = −4,3 (t = −2,3) —cada dimensión eleva el spread. Segundo,
la complementariedad **sí es significativa condicionalmente**: sobre el núcleo de 11
economías emergentes de financiamiento externo, θ = −0,47 (t = −2,29, **p = 0,023**; wild
cluster bootstrap p = 0,015), y el modelo de umbral de Hansen corrobora la no linealidad
(+5,9 vs +2,0 pb por régimen). Lo que la tesis reporta como resultado principal es esa
**heterogeneidad** —dónde y cuándo la complementariedad aparece en los precios—, no un
coeficiente único sobre un panel promedio.

**P17. ¿Y esa heterogeneidad no es *cherry-picking* de países?**
R. El grupo del núcleo son las 11 economías del complejo tradicional de deuda soberana de
alto rendimiento, con alta participación extranjera en la deuda pública. Polonia e India
—las dos que diluyen la interacción— son economías grandes con mercados de deuda local
profundos y baja dependencia de flujos de cartera externos: exactamente donde el canal de
repreciación del *doom loop* debería ser más tenue. El test de interacción de grupo pone
número: la diferencia entre grupos es +0,36, del signo que diluye la interacción, aunque **no
es significativa** (p = 0,23) —con solo dos países en el grupo de contraste no puede serlo, y
lo digo así. El jackknife de dos países confirma que el signo de θ es negativo en el 99 % de
los pares excluidos, y que su significancia depende de qué economías se dejen fuera. La
partición no es *ex post*: es la distinción, anunciada en la introducción, entre economías de
financiamiento externo y de deuda local —el moderador natural, cuando haya datos, es la
participación de no residentes en la deuda soberana (agenda, PC2).

**P18. El resultado cambia según qué países entran. ¿No es un resultado de composición?**
R. Sí, y es el hallazgo, no un defecto: la complementariedad **es** una propiedad del tipo de
economía. Sobre la muestra completa θ = −0,16; sin Polonia sube a −0,29; sobre el núcleo de
11 llega a −0,47 (p = 0,023). Sin China, en cambio, cae a −0,05 —porque 9 de 13 países tienen
`JLoss` mediano 2,2–2,6 y China, Turquía, India y Brasil aportan casi toda la variación de
fragilidad. La agenda (§7) es ampliar el grupo de contraste con más economías de deuda local
profunda para poder contrastar la heterogeneidad formalmente.

**P19. La complementariedad es un fenómeno pre-pandemia. ¿No es entonces algo que ya pasó?**
R. Al interactuar `JLoss×GaR` con una dummy post-2020, el coeficiente base (hasta 2019) es
θ = −1,0 (p = 0,057) y el término post-2020 es +1,0 (p = 0,12): el período post-COVID
compensa casi por completo. En las ventanas móviles de 5 años, la señal es negativa y
significativa en 2012–2016 (θ = −0,65, t = −2,4) y se atenúa después. No es que "ya pasó" —es
que el multiplicador se hace visible en los precios cuando el riesgo soberano de las
economías emergentes está en el centro de la atención de los mercados (crisis de deuda
europea, estrés EM 2015–16), y se diluye en el período de tasas de política extraordinariamente
bajas y normalización abrupta que le sigue.

**P20. ¿Por qué el mecanismo estaría "apagado" en los años de tasas bajas?**
R. Interpretación económica: el multiplicador de *doom loop* opera cuando el precio del
riesgo soberano es sensible a la cola del crecimiento. En el período de compresión
generalizada de spreads y búsqueda de rendimiento posterior a 2016, esa sensibilidad baja;
en los episodios de estrés EM se activa. Es coherente con que la interacción sea, por
construcción, un fenómeno de cola.

**P21. Simultaneidad del *doom loop*: el spread también afecta a `JLoss`. ¿Cómo la resuelve?**
R. Efectos fijos de país y de tiempo (absorben heterogeneidad estructural y choques globales
comunes), regresores centrados, y —para el canal de **nivel** (H1)— proyecciones locales:
la respuesta del spread a un choque de fragilidad alcanza un pico de +4,6 pb (t = 2,9) un
trimestre después, del signo esperado. Una estrategia de variables instrumentales
*shift-share* complementa, pero sobre este panel reducido no cierra la identificación (ver P22).

**P22. ¿Y el IV? ¿No instrumenta el nivel de `JLoss`?**
R. Lo intenta, con un choque global de liquidez de fondeo bancario (*on/off-run* del Tesoro)
interactuado con la exposición pre-2012 de cada país. Sobre el panel de 13 países la primera
etapa es apenas aceptable (F ≈ 11) y la segunda etapa, aunque del signo esperado, no alcanza
significancia (p = 0,34) —bastante más débil que en la versión con más economías y CDS. Un
segundo instrumento (tipo de cambio efectivo amplio del dólar, BIS) da signo opuesto, y la
especificación sobre-identificada **rechaza el test de Sargan** (p < 0,001). La lectura
honesta (§6.8 y limitaciones): la estrategia de variables instrumentales **no cierra la
identificación causal** del canal de nivel sobre esta muestra; la evidencia de H1 descansa en
el MCO con efectos fijos y en las proyecciones locales. No lo escondo.

**P23. ¿Por qué `pre_year = 2012` para estimar la exposición del IV?**
R. 2012 es un quiebre de régimen que aparece de forma independiente en el análisis temporal
de θ (las ventanas móviles). Uso datos de **antes** de ese quiebre para estimar la exposición
estructural, y el instrumento sobre el período posterior. En cualquier caso, sobre el panel
de 13 países el IV es débil (ver P22), de modo que este punto es menos determinante que en
la versión previa del panel.

---

## F. Robustez, diagnósticos y modelo dinámico

**P24. ¿Por qué no un estimador GMM dinámico (Arellano-Bond) para el sesgo de Nickell y la
dinámica del *doom loop*?**
R. Porque la forma del panel es la contraria a la que ese estimador supone: T ≈ 88, N = 13.
El sesgo de Nickell es del orden de 1/T ≈ 1 %, despreciable. Corrí igual un system-GMM: el
signo de la interacción se mantiene negativo, pero el test de Hansen da p = 1,00 —diagnóstico
no informativo por proliferación de instrumentos, exactamente lo que se espera con T ≫ N.
El estimador estático de efectos fijos bidireccionales es el apropiado aquí.

**P25. Dependencia transversal de los residuos —países emergentes se mueven juntos.**
R. Prueba de Pesaran (2021): CD = −1,1, p = 0,28 —no se rechaza la independencia una vez
incluidos los efectos fijos de tiempo. Se mantienen igual los errores de Driscoll-Kraay por
la autocorrelación serial (correlación de primer orden de residuos ≈ 0,9). Hausman rechaza
efectos aleatorios.

**P26. El efecto marginal en el percentil 90 (benigno) incluye el cero. ¿Entonces el
mecanismo no opera en tiempos buenos?**
R. Sobre la muestra completa, el efecto de una unidad de `JLoss` sobre el EMBI es +3,4 pb en
el percentil 10 de `GaR` (cola severa) y +2,1 pb en el percentil 90 —monótonamente decreciente
en `GaR`, la firma de la super-aditividad, aunque de pendiente modesta. En el núcleo de 11
economías, donde θ es tres veces mayor en valor absoluto, esa pendiente es correspondientemente
más pronunciada y el modelo de umbral la corrobora (+5,9 vs +2,0 pb por régimen). Es un
multiplicador de cola: opera cuando el crecimiento ya está en su escenario adverso.

---

## G. El modelo teórico (Capítulo 3)

**P27. La relación en U de la fragilidad individual es poco profunda —un problema conocido
de Martínez-Miera y Repullo (2010). ¿No hereda esa debilidad?**
R. La U poco profunda afecta al canal de fragilidad *individual*, no al aporte del modelo. La
contribución es el canal de **correlación endógena** ρ(n): al hacer la correlación de
activos función de la estructura de mercado, el mínimo de la fragilidad *sistémica* (`JLoss`)
se desplaza hacia más competencia respecto del mínimo individual (Proposición 3). Ese
resultado no depende de la profundidad de la U —depende del signo de ρ'(n).

**P28. ¿Y si ρ'(n) > 0? El canal de *herding* de Acharya-Yorulmazer diría que más bancos
implican más imitación y más correlación.**
R. El modelo entrega la **condición de dominancia** entre el canal de diferenciación
(ρ'(n) < 0, microfundamentado con competencia à la Salop) y el de *herding* (ρ'(n) > 0), y
traslada el signo al dato. La versión base postula ρ'(n) < 0; el microfundamento completo
más allá de Salop es agenda declarada. Es una limitación honesta, no un supuesto oculto.

**P29. El bloque soberano es de equilibrio parcial. El *doom loop* completo necesita
dinámica.**
R. Correcto. El cierre es de un período: `JLoss → GaR` (credit crunch) y `GaR, JLoss →
EMBI` (límite fiscal à la Ghosh et al.). El cross-partial ∂²EMBI/∂JLoss∂GaR < 0 es un
resultado **local** que satura cuando PD_sov → 1. La extensión de dos períodos del bloque
soberano —el lazo con retroalimentación— es la agenda pendiente principal del capítulo.

**P30. La predicción que distingue a su modelo de la OI estándar —la amplificación por
concentración— es justamente la que no se puede contrastar. ¿Para qué sirve el modelo
entonces?**
R. Primero, la franqueza: H4b **no se puede contrastar con potencia**. En la parametrización
$D\equiv-GaR$ (predicción: β4 > 0), el punto estimado no tiene signo estable entre proxies de
concentración —+122 (t = 0,37) con el HHI estructural, +152 (t = 0,73) con la serie anual,
≈ 0 (t = −0,41) con la concentración trimestral— y el bootstrap de bloques por país deja el
IC90 cruzando el cero holgadamente con los tres. La serie trimestral **descarta** que sea
solo falta de variación temporal del proxy; con 13 clusters y un HHI casi invariante, el
coeficiente simplemente no está identificado.
Segundo, para qué sirve el modelo: (i) deriva la complementariedad de primer orden (H4a,
que se sostiene condicionalmente —en el núcleo de economías de financiamiento externo)
desde primeros principios —no es una regularidad sin anclaje; (ii) la Proposición 3 (el
mínimo desplazado de `JLoss`) es puramente deductiva, no
depende de la evidencia, y tiene una implicancia de política directa: una política de
competencia bancaria calibrada solo sobre la salud individual de los bancos deja al sistema
subóptimamente concentrado desde la óptica del riesgo sistémico y su costo fiscal
contingente. Ese resultado se sostiene con independencia de H4b.
Si insiste: la tesis lo reporta como convergencia **parcial** teoría–evidencia y lo dice en
el título de la sección de discusión. Es un resultado no concluyente reportado como tal, no
un fracaso oculto.

---

## Preguntas "grandes" de cierre (probables)

**PC1. Si la complementariedad no es significativa sobre el panel completo, la identificación
descansa en pocos países y en un período, y el canal distintivo del modelo no se puede
contrastar —¿qué queda?**
R. Quedan los **canales de nivel** —fragilidad bancaria y riesgo de cola del crecimiento
elevan cada uno el spread soberano— bien identificados. Queda una **complementariedad
condicional**: significativa (θ = −0,47, p = 0,023) en el núcleo de economías emergentes de
financiamiento externo, con una lectura económica coherente de por qué se diluye en las
economías de deuda local profunda. Queda un modelo estructural que predice y microfundamenta
esa complementariedad. Y queda un *pipeline* reproducible. La contribución es la
caracterización honesta de **dónde y cuándo** el multiplicador de *doom loop* aparece en los
precios soberanos —y eso, en un área donde abundan los resultados frágiles presentados como
universales, es en sí mismo un aporte.

**PC2. ¿Qué haría distinto si empezara de nuevo?**
R. (i) Construir una medida directa de participación extranjera en la deuda soberana para
usarla como moderador continuo de la interacción, en lugar de la dicotomía por tipo de
economía. (ii) Extraer los componentes de mercado del FCI de Bloomberg desde el inicio.
(iii) Buscar instrumentos con mejor argumento de exclusión para el canal de nivel. (iv)
Cerrar el hueco de GaR para las economías que hoy quedan fuera, para ampliar el grupo de
contraste de la heterogeneidad.

**PC3. ¿Cuál es el siguiente paper?**
R. El panel ampliado con más corte transversal, un moderador continuo de exposición externa
para contrastar formalmente la heterogeneidad, y el cierre dinámico de dos períodos del
bloque soberano del modelo. Cada una refuerza directamente a la otra arista.
