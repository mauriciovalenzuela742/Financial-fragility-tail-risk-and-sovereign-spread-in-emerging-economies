# Defensa de la tesis — 30 preguntas del profesor y guion de respuesta

*Preparación para el examen de grado. Cada respuesta se apoya en números trazables a
`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` y a los CSV del pipeline. Formato: **P** =
pregunta que probablemente hará la comisión; **R** = respuesta corta con cifras listas para
citar; **Si insiste** = la línea de defensa de segundo nivel.*

Complemento específico para la construcción del GaR:
`1_Codigo/Defensa_GaR_preguntas_respuestas.md`.

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
resultado negativo— de la amplificación por concentración. El *pipeline* y todos los números
son reproducibles y están versionados.

**P3. Si tuviera que resumir el aporte en una frase, ¿cuál es?**
R. La fragilidad bancaria sistémica y el riesgo de cola del crecimiento no determinan el
spread soberano de forma aditiva, sino **complementaria**: su coincidencia lo amplifica. Se
establece el **signo y la forma** de esa complementariedad sobre un panel homogéneo, se la
deriva de un modelo estructural, y se delimita con precisión qué parte está respaldada y
qué parte no.

**P4. ¿Por qué dos capítulos-paper y no un solo artículo integrado?**
R. Son dos objetos de conocimiento que se validan con estándares distintos: el empírico con
significancia/robustez/identificación; el teórico con existencia, unicidad y signos de
estática comparativa deducidos de supuestos explícitos. Separarlos deja que cada uno cumpla
su estándar. La introducción y la discusión general muestran por qué juntos son más que la
suma.

---

## B. Medición de la fragilidad — `JLoss`

**P5. `JLoss` medio es 4,1 y la cota superior de la malla de pérdidas del motor es 4,8 %.
¿No está la métrica pegada al techo?**
R. Verificado (`_diag_censura.py`, 6 países): la cota **satura el VaR99 en el 98 % de los
país-trimestre**. `JLoss` mide, en la práctica, la pérdida esperada (probabilidades de
Merton) más una contribución de cola evaluada a un **nivel de estrés fijo**, no en el
percentil 99 verdadero. Consecuencia: la variación de `JLoss` la gobierna la pérdida
esperada, no la forma de la cola.
Si insiste: recalculé el motor con malla `[0,01; 0,20]` para los 14 países de estimación.
`JLoss` escala **×2,8** (heterogéneo entre países), correlación 0,92 con la base. Re-estimando
θ con esa serie corregida: **M2 θ = −0,330 (p = 0,032)** vs base −0,354 (p = 0,056); M1 θ =
−0,572 (p = 0,010). La censura, de sesgar algo, **sesgaba en contra** del hallazgo. `JLoss`
se interpreta ordinalmente, no en niveles — y así lo dice el §4.1.

**P6. ¿Por qué excluye a Corea del Sur y a Bulgaria y deja a China, que también tiene un
`JLoss` elevado?**
R. Corea: el valor de mercado de la banca es ≈4 % del punto de incumplimiento (frente a
15–34 % en el resto), reflejo del *Korea discount*, no de la solvencia; Merton lo lee como
incumplimiento inminente y devuelve `JLoss` 25–47. Bulgaria: un solo banco cotiza (FIBank),
76/76 trimestres bajo el mínimo. China: `JLoss` mediano 3,8, máximo 29 —elevado pero no
implausible; su descuento de valoración es mucho menos extremo. Es una exclusión por
**insumo no válido**, no por dato faltante, y coincide con la reconstrucción regulatoria
previa.
Si insiste: reconozco que China es la exclusión que más condicionaría el resultado —lo digo
en las limitaciones (§7, punto cuarto). Por eso reporto la robustez sin China de forma
prominente.

**P7. `JLoss` es un regresor estimado, no observado. ¿No invalida eso la inferencia sobre
θ?**
R. Es una limitación real (§7, punto quinto). Dos cosas la acotan: (i) el error de medición
clásico en un regresor **atenúa** el coeficiente hacia cero, así que el θ reportado es un
límite conservador; (ii) perturbando `GaR` con ruido creciente, θ es estable hasta el 25 %
de su desviación (θ = −0,34) y solo baja a −0,29 con el 50 %, sin cambiar de signo. Un
*bootstrap* que re-estime la regresión cuantílica de `GaR` en cada réplica queda como
refinamiento pendiente (es ~45.000 solves del programa lineal).

**P8. El `JLoss` de Bloomberg está mucho más comprimido que el regulatorio (sd ≈ 4 vs 8,3).
¿No debería preocuparle que la métrica "buena" dé menos señal?**
R. Es el precio de la homogeneidad: un solo protocolo elimina la heterogeneidad de
definiciones contables entre supervisores, pero también comprime la dispersión —en la
versión regulatoria, Brasil solo concentraba `JLoss` ≈ 16. Esa compresión es la razón más
probable de que la prueba de amplificación por concentración (H4b) quede sin potencia. Para
la interacción de primer orden (θ) la señal alcanza, aunque marginalmente.

**P9. ¿Por qué ρ = 0,4 y LGD = 0,45 y no otros valores?**
R. Son los parámetros de Chari et al. (2024), a su vez estándar (LGD 45 % es Basilea II para
exposiciones no garantizadas). El objetivo era comparabilidad con esa reconstrucción, no
recalibrar. La sensibilidad a ρ está en la validación Monte Carlo del método (Cap. 3, §5.2).

---

## C. Medición del riesgo de cola — `GaR`

**P10. `GaR` no viene de Bloomberg —rompe el principio de homogeneidad de fuente.**
R. Correcto y explícito (Anexo B): los insumos reales del FCI (PIB, IPC, índice accionario,
REER, rendimiento 10Y) son estadísticas nacionales porque Bloomberg no es fuente primaria de
cuentas nacionales. Lo que sí es homogéneo es todo el insumo **de mercado** (balances,
capitalización, CDS, factores globales). En la agenda está extraer de Bloomberg los
componentes de mercado del FCI (índice accionario, REER, 10Y) para cerrar más el círculo.

**P11. La media de `GaR` (q05) es +1,4 pp. ¿Un percentil 5 del crecimiento positivo?**
R. Es el cuantil 5 % del crecimiento interanual condicional un trimestre adelante, promediado
sobre 838 observaciones-país que incluyen muchos trimestres de expansión en emergentes. El
rango es [−22,8; +14,0] pp: en los episodios de estrés `GaR` es marcadamente negativo, que
es donde el mecanismo se identifica. La convención: más negativo = más riesgo a la baja.

**P12. ¿Por qué el cuantil directo y no la skew-t de Adrian et al.?**
R. El cuantil condicional es el objeto primitivo del estimador de Koenker; la skew-t es una
elección de suavizado. Uso el cuantil directo (con reordenamiento de Chernozhukov et al.
2010) y conservo la skew-t como robustez: la correlación entre ambas series de `GaR` es
0,9996, y θ con `GaR` skew-t es −0,354 (p = 0,051), idéntico al del cuantil directo.
(Detalle en `Defensa_GaR_preguntas_respuestas.md`.)

---

## D. CDS, controles y concentración

**P13. ¿Por qué CDS y no EMBI? Pierde observaciones.**
R. El CDS a cinco años aísla el componente puro de riesgo de crédito y es homogéneo entre
países; el EMBI mezcla vencimiento, cupón y liquidez de bonos heterogéneos. Decisión
metodológica: donde no hay CDS, la celda queda vacía —no se sustituye por proxies, para no
ensuciar la variable dependiente. Cuesta cobertura pero gana comparabilidad.

**P14. Los controles domésticos son anuales interpolados a trimestral. La variación
trimestral es un artefacto.**
R. Cierto para deuda/PIB, balance fiscal, reservas y cuenta corriente (§7). Son variables
lento-móviles y la interpolación lineal es estándar para ellas. La inflación y el REER sí
son de frecuencia nativa mensual. El coeficiente de deuda/PIB (+2,32; t = 4,5) se identifica
sobre todo de la variación entre países y de baja frecuencia; lo relevante para la tesis es
que θ **conserva el signo** una vez condicionado por ese bloque, no la magnitud de los
controles.

**P15. El HHI del GFDD es casi invariante en el tiempo. ¿Cómo puede identificar β4?**
R. No puede bien —es exactamente el problema de H4b. Por eso construí una serie de
concentración **trimestral** (`p6_concentracion_trimestral.py`) a partir de los mismos
balances Bloomberg que `JLoss`: CR3/HHI de los bancos cotizados, por país y trimestre.
Correlación 0,62 con el GFDD anual en la muestra de estimación. Con esa variación temporal
real, β4 sigue sin identificarse (ver P24).
Si insiste: la limitación de la serie trimestral es que mide la concentración del *segmento
cotizado*, no del sistema completo —igual que `JLoss`, no observa bancos no listados.

---

## E. Identificación econométrica de θ (H3)

**P16. θ es significativo a p = 0,056. Eso no es significativo. ¿Por qué debería creerle?**
R. Porque lo que la tesis afirma es el **signo y la forma**, no la magnitud puntual —y eso
sí está sólido: θ < 0 en las 5 especificaciones del Cuadro 3, en las 14 submuestras
*leave-one-out*, en las 91 que excluyen dos países, con tres medidas de cola distintas
(GaR q05, skew-t, ES), y el modelo de umbral de Hansen lo corrobora sin imponer la forma
(efecto +8,1 vs +2,3 pb por régimen, LR = 80). La significancia puntual: p = 0,056 (DK),
0,035 (*wild bootstrap*), 0,001 (*cluster* país), 0,051 (GaR skew-t), y un placebo de
reasignación deja θ en el percentil 5 de la nula (p ≈ 0,05). Es marginal, y lo digo así.

**P17. Con 13 países, ¿tiene sentido siquiera hacer inferencia asintótica agrupada?**
R. No del todo —por eso reporto *wild cluster bootstrap* (Cameron-Gelbach-Miller, restringido,
Rademacher, 999 réplicas): p = 0,035. Y el placebo de reasignación de `GaR`, que genera la
distribución nula exacta sin supuestos asintóticos: p ≈ 0,05. Las tres formas de inferencia
convergen en "marginal".

**P18. El resultado desaparece si quita a China. ¿No es un resultado de un país?**
R. El **signo** es negativo en las 91 submuestras de dos países (100 %). La **significancia**
sí descansa en China: sin China θ = −0,17 (t = −1,33); sin China + Turquía θ ≈ 0. El
diagnóstico por país lo explica: 9 de 13 países tienen `JLoss` mediano 2,2–2,6 y casi no
varía; China, Turquía y Brasil aportan la variación de fragilidad. Lo reconozco
explícitamente: "catorce países" sobreestima el corte transversal efectivo. La agenda es
ampliar el panel con economías que aporten variación de `JLoss` (§7 agenda).

**P19. "sin 2020–2021" da θ = −1,11 (t = −3,5) y pre-2020 da θ = −0,39 (t = −1,0). El
resultado se multiplica por tres según qué años entran. ¿No es puro *cherry-picking* de la
ventana?**
R. Es la pregunta correcta, y la respuesta la dan las **ventanas móviles de 5 años**
(`fig_ventanas_theta`): θ es positivo/nulo en 2006–2011 (GFC) y **negativo y significativo
en TODAS las ventanas que empiezan en 2012** (−1,2 en 2012–16; −0,4 en 2015–19; −0,2 en
2018–22; −0,3 en 2021–25). No es un artefacto de COVID: es una **regularidad post-crisis
financiera global**. El pre-2020 sale n.s. solo porque promedia la señal post-2012 con el
período nulo 2004–2011. Y al interactuar `JLoss×GaR` con una dummy post-2020, el término
extra es +0,46 (t = 0,8, n.s.): no hay quiebre discreto en 2020.

**P20. ¿Por qué el mecanismo estaría "apagado" en 2004–2011?**
R. Interpretación económica: el multiplicador de *doom loop* opera cuando el precio del
riesgo soberano es sensible a la cola del crecimiento. En la fase de expansión y baja
percepción de riesgo global previa a la GFC, esa sensibilidad era baja; desde 2012, con el
ciclo de tasas, la crisis del euro y los episodios de estrés EM, se activa. Es coherente con
que la interacción sea, por construcción, un fenómeno de cola.

**P21. Simultaneidad del *doom loop*: el spread también afecta a `JLoss` vía el valor de la
deuda soberana en los balances bancarios. ¿Cómo la resuelve?**
R. Efectos fijos de país y de tiempo (absorben heterogeneidad estructural y choques globales
comunes), regresores centrados, y una estrategia de variables instrumentales *shift-share*
para el canal de **nivel** (`JLoss → spread`): choque global de liquidez de fondeo bancario
(*on/off-run* del Tesoro) interactuado con la exposición pre-2012 de cada país. Primera
etapa fuerte (F = 21,6), β = +17,5 pb (p = 0,001), dirección banco→soberano. Pero —ver P22—
no está cerrado.

**P22. Ese IV: ¿la restricción de exclusión se sostiene? El diferencial de liquidez del
Tesoro puede afectar al spread soberano por muchos canales.**
R. No puedo verificarla directamente, y lo digo (§6.7 y §7, punto séptimo). Añadí un segundo
instrumento igualmente fuerte —el tipo de cambio efectivo amplio del dólar (BIS, 64
economías; F = 23,7)— y el resultado es **honesto y desfavorable**: usado solo da un efecto
pequeño y no significativo (p = 0,46), y la especificación sobre-identificada con ambos
**rechaza el test de Sargan (p = 0,003)**. Los dos instrumentos no identifican el mismo
parámetro. Reporto el de mejor argumento de exclusión (opera sobre el costo de fondeo
bancario, no sobre el soberano directamente) como el más creíble, pero **el efecto de nivel
no está causalmente cerrado**. No lo escondo.

**P23. ¿Por qué `pre_year = 2012` para estimar la exposición del IV? ¿No lo eligió para
maximizar el F?**
R. 2012 es el mismo quiebre de régimen post-GFC que ya establecí de forma independiente en
θ (las ventanas móviles). Uso datos de **antes** de ese quiebre para estimar la exposición
estructural y el instrumento sobre el período donde vive la variación identificadora. No es
*ad hoc* para el F: en la vecindad (2010, 2014) el instrumento también es fuerte (F entre 9
y 20); en 2016 —el corte original, arbitrario— daba F ≈ 9,5, que es lo que antes se
reportaba como "débil-a-límite".

---

## F. Robustez, diagnósticos y modelo dinámico

**P24. ¿Por qué no un estimador GMM dinámico (Arellano-Bond) para el sesgo de Nickell y la
dinámica del *doom loop*?**
R. Porque la forma del panel es la contraria a la que ese estimador supone: T ≈ 88, N = 13.
El sesgo de Nickell es del orden de 1/T ≈ 1 %, despreciable. Corrí igual un system-GMM: el
signo de la interacción se mantiene (−0,25), pero el test de Hansen da p = 1,00 —diagnóstico
no informativo por proliferación de instrumentos, exactamente lo que se espera con T ≫ N.
El estimador estático de efectos fijos bidireccionales es el apropiado aquí.

**P25. Dependencia transversal de los residuos —países emergentes se mueven juntos.**
R. Prueba de Pesaran (2021): CD = −1,2, p = 0,23 —no se rechaza la independencia una vez
incluidos los efectos fijos de tiempo. Se mantienen igual los errores de Driscoll-Kraay por
la autocorrelación serial (correlación de primer orden de residuos ≈ 0,8). Hausman rechaza
efectos aleatorios; los VIF son uniformemente bajos.

**P26. El efecto marginal en el percentil 90 (benigno) incluye el cero. ¿Entonces el
mecanismo no opera en tiempos buenos?**
R. Exacto, y es coherente con la teoría: es un multiplicador de cola. El efecto de una
unidad de `JLoss` sobre el CDS es +4,6 pb en el percentil 10 de `GaR` (cola severa) —la
banda al 90 % excluye el cero— y +1,8 pb en el percentil 90 —la banda incluye el cero. La
firma empírica de la super-aditividad es justamente que el efecto **crece monótonamente** a
medida que empeora el riesgo de cola.

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
concentración— es justamente la que falla empíricamente. ¿Para qué sirve el modelo
entonces?**
R. Primero, la franqueza: sí, H4b no encuentra respaldo (β4 = −392, t agrupado = −2,34, pero
el IC robusto cruza el cero; con la concentración trimestral, β4 = −0,114, IC (−0,144;
+0,013) —sigue cruzando el cero por un margen mínimo). La serie trimestral **descarta** que
sea solo falta de variación temporal del proxy; el peso se inclina hacia un canal
genuinamente más débil que la calibración, o de signo distinto.
Segundo, para qué sirve el modelo: (i) deriva la complementariedad de primer orden (H4a,
que sí se sostiene en signo y forma) desde primeros principios —no es una regularidad sin
anclaje; (ii) la Proposición 3 (el mínimo desplazado de `JLoss`) es puramente deductiva, no
depende de la evidencia, y tiene una implicancia de política directa: una política de
competencia bancaria calibrada solo sobre la salud individual de los bancos deja al sistema
subóptimamente concentrado desde la óptica del riesgo sistémico y su costo fiscal
contingente. Ese resultado se sostiene con independencia de H4b.
Si insiste: la tesis lo reporta como convergencia **parcial** teoría–evidencia y lo dice en
el título de la sección de discusión. Es un resultado negativo genuino, no un fracaso
oculto.

---

## Preguntas "grandes" de cierre (probables)

**PC1. Si el resultado central es marginal, la identificación descansa en pocos países y en
un período, y el canal distintivo del modelo no se confirma —¿qué queda?**
R. Queda el **signo y la forma** de una complementariedad que la literatura no había
articulado, robustos a un conjunto exigente de pruebas; un modelo estructural que la
predice y la extiende; una prueba —de resultado negativo— de su predicción distintiva sobre
datos homogéneos; y un *pipeline* reproducible. La contribución es delimitar con precisión
qué puede afirmarse y qué no —y eso, en un área donde abundan los resultados frágiles
presentados como sólidos, es en sí mismo un aporte.

**PC2. ¿Qué haría distinto si empezara de nuevo?**
R. (i) Extraer los componentes de mercado del FCI de Bloomberg desde el inicio. (ii)
Construir la serie de concentración trimestral antes, no como respuesta a una revisión.
(iii) Buscar instrumentos con mejor argumento de exclusión para el canal de nivel —choques
de política monetaria identificados, términos de intercambio por exposición sectorial. (iv)
Ampliar la extracción de CDS y de GaR a las economías que hoy quedan fuera, para que la
identificación no descanse en 3–4 países.

**PC3. ¿Cuál es el siguiente paper?**
R. El panel ampliado con más corte transversal de `JLoss`, la serie de concentración
trimestral sobre un universo mayor de países, y el cierre dinámico de dos períodos del
bloque soberano del modelo. Cada una refuerza directamente a la otra arista.
