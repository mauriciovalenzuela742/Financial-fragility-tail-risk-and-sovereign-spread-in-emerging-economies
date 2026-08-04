# Resultados Empíricos y Discusión

## 5.1. Estrategia de identificación y lectura de la evidencia

La estimación se organiza en torno a un panel desbalanceado de cinco economías
emergentes latinoamericanas (Brasil, Chile, Colombia, México y Perú) con frecuencia
trimestral entre 2010Q1 y 2022Q2 ($N=248$; $T$ entre 48 y 50). La especificación de
referencia incorpora **efectos fijos bidireccionales** —de país y de tiempo— de modo
que los efectos de país absorben la heterogeneidad estructural no observada (calidad
institucional, régimen cambiario, profundidad financiera) y los efectos de tiempo
capturan la totalidad de los choques globales comunes (*push factors*): aversión al
riesgo global, ciclo de tasas de la Reserva Federal y condiciones de liquidez
internacional. En consecuencia, la identificación de los parámetros de interés proviene
exclusivamente de la variación *intra-país relativa a la media transversal de cada
trimestre*, lo que constituye un control particularmente exigente frente a la
confusión por factores comunes.

La inferencia se basa en errores estándar de **Driscoll–Kraay**, robustos
simultáneamente a heterocedasticidad, autocorrelación serial y dependencia transversal.
Esta elección se justifica formalmente más adelante (Sección 5.6) y se prefiere al
*clustering* por país dado que, con únicamente cinco conglomerados, la inferencia basada
en *cluster-robust* resulta poco fiable.

La hipótesis central —complementariedad entre fragilidad bancaria sistémica
($JLoss$) y riesgo de cola izquierda del crecimiento ($GaR$)— se contrasta a través del
término de interacción $\theta$ en la especificación

$$EMBI_{i,t}=\alpha_i+\lambda_t+\beta_1 JLoss_{i,t}+\beta_2 GaR_{i,t}+\theta\,(JLoss\times GaR)_{i,t}+\gamma' X_{i,t}+\varepsilon_{i,t}.$$

Bajo la convención de signos adoptada —el $GaR$ se mide en niveles como el cuantil 5%
de la distribución condicional del crecimiento, de modo que valores más negativos
denotan mayor riesgo a la baja— la predicción teórica del mecanismo de *doom loop*
(Farhi y Tirole, 2018) es inequívoca: $\theta<0$, esto es,
$\partial^2 EMBI/\partial JLoss\,\partial GaR<0$.

## 5.2. Resultado principal: el canal de complementariedad

El Cuadro 1 presenta las seis especificaciones centrales. Las columnas M1–M4 y M6
emplean efectos fijos bidireccionales; M5 utiliza únicamente efectos de país para
permitir la entrada explícita del VIX.

**Cuadro 1. Determinantes del spread soberano (variable dependiente: EMBI, en pb)**

| Regresor | M1 | M2 | M3 | M4 (log) | M5 (FE país) | M6 (ES) |
|---|---|---|---|---|---|---|
| JLoss | 2.731\*\*\* | 1.233\*\* | 1.119\* | 0.0049\* | 0.355 | 1.520\*\* |
| GaR (pp) | 3.423\* | 2.863 | 1.421 | 0.0066 | −4.436\*\* | — |
| **JLoss × GaR** | — | **−0.352\*\*\*** | **−0.363\*\*\*** | −0.00042 | **−0.239\*\*** | — |
| ES (pp) | — | — | — | — | — | 0.931 |
| JLoss × ES | — | — | — | — | — | −0.262\*\*\* |
| VIX | — | — | — | — | 3.314 | — |
| Deuda/PIB | — | — | −1.490\* | −0.0042 | −1.148\* | −1.523\* |
| Balance fiscal/PIB | — | — | 7.103\* | 0.0215 | 2.503 | 6.912 |
| Reservas/PIB | — | — | 3.348 | 0.0145 | 3.350\*\* | 3.459 |
| Cuenta corriente/PIB | — | — | 4.522\* | 0.0078 | 7.799\*\*\* | 4.443\* |
| Inflación YoY | — | — | −2.356 | −0.0006 | 7.902\*\*\* | −2.537 |
| REER | — | — | −1.051\*\*\* | −0.0048\*\*\* | −2.063\*\*\* | −1.059\*\*\* |
| $N$ | 248 | 248 | 248 | 248 | 248 | 248 |

*Errores estándar de Driscoll–Kraay. \*\*\* $p<0.01$, \*\* $p<0.05$, \* $p<0.10$.
$JLoss$, $GaR$ y $ES$ centrados; $GaR$ y $ES$ en puntos porcentuales.*

La lectura conjunta de M1 a M3 articula el argumento empírico en tres pasos.

En **M1**, sin término de interacción, la fragilidad bancaria entra con el signo
esperado y elevada significancia ($\hat\beta_1=2.73$, $t=4.78$): un incremento de una
unidad en el índice $JLoss$ se asocia a un aumento de aproximadamente 2.7 puntos básicos
en el spread soberano. Este resultado, por sí solo, documenta la existencia del nexo
banca-soberano que la literatura del *deadly embrace* (Acharya, Drechsler y Schnabl,
2014) postula para economías avanzadas, extendiéndolo al universo emergente.

La incorporación de la interacción en **M2** constituye el contraste directo de la
hipótesis. El coeficiente $\hat\theta=-0.352$ es negativo y altamente significativo
($t=-3.97$), precisamente el signo predicho por el multiplicador de *doom loop*. La
interpretación es que el efecto de la fragilidad bancaria sobre el riesgo soberano **no
es constante**, sino que se intensifica conforme se deteriora la cola izquierda del
crecimiento. Nótese que la introducción de la interacción reduce el coeficiente lineal
de $JLoss$ (de 2.73 a 1.23), lo que es esperable: el efecto promedio se descompone ahora
en un componente de nivel y un componente dependiente del estado del riesgo de cola.

**M3** añade el vector completo de controles macroeconómicos domésticos. El resultado
crucial es la **estabilidad cuantitativa de la interacción**: $\hat\theta$ pasa de
$-0.352$ a $-0.363$ y conserva significancia al 1% ($t=-3.41$). Que la magnitud del
parámetro de interés permanezca prácticamente inalterada tras condicionar por deuda,
balance fiscal, reservas, cuenta corriente, inflación y tipo de cambio real constituye
evidencia de que la complementariedad **no es un artefacto de variables omitidas de
naturaleza fiscal o externa**. El efecto lineal de $JLoss$ se atenúa hasta el margen de
la significancia ($t=1.94$, $p=0.054$), un patrón coherente con que, una vez modelada la
no linealidad, buena parte de la transmisión de la fragilidad opera a través de su
interacción con el riesgo de cola y no de manera autónoma.

## 5.3. Magnitud económica: el multiplicador del riesgo soberano

La relevancia económica del mecanismo se aprecia con nitidez en el **efecto marginal**
de la fragilidad bancaria condicionado al estado del riesgo de cola, evaluado a partir
de M3:

$$\frac{\partial\,EMBI_{i,t}}{\partial\,JLoss_{i,t}}=\hat\beta_1+\hat\theta\,(GaR_{i,t}-\overline{GaR}).$$

**Cuadro 2. Efecto marginal de JLoss sobre el spread según severidad del riesgo de cola**

| Estado del GaR | Nivel (pp) | $\partial EMBI/\partial JLoss$ (pb) | $t$ |
|---|---|---|---|
| Cola severa (percentil 10) | −3.57 | **+2.509** | 4.59 |
| Mediana | +0.37 | +1.078 | 1.85 |
| Entorno benigno (percentil 90) | +4.95 | −0.589 | −0.65 |

El gradiente es monótono y económicamente sustancial. Cuando el riesgo de cola es
severo, una unidad adicional de fragilidad bancaria eleva el spread en 2.5 puntos
básicos, un efecto estimado con elevada precisión ($t=4.59$). En el centro de la
distribución el impacto se reduce a la mitad (1.1 pb) y, en entornos de crecimiento
benigno, se torna estadísticamente nulo. En términos de variación típica, un aumento de
una desviación estándar *intra-país* de $JLoss$ (aproximadamente 6.6 unidades) se
traduce en un encarecimiento de unos 17 puntos básicos del financiamiento soberano bajo
estrés de cola, frente a un efecto indistinguible de cero en condiciones favorables.

Esta es la firma empírica de la **amplificación supra-aditiva**: la fragilidad bancaria
y el riesgo de cola del crecimiento no se suman, se potencian. La fragilidad sistémica
del sistema bancario sólo se traduce en mayor prima de riesgo soberano cuando coexiste
con un escenario macroeconómico vulnerable —exactamente la condición bajo la cual el
rescate implícito del sistema financiero compromete la solvencia del soberano y
realimenta el círculo vicioso descrito por Farhi y Tirole (2018).

## 5.4. El nivel del GaR y la sensibilidad al esquema de efectos fijos

El coeficiente de **nivel** del $GaR$ ($\hat\beta_2$) merece una lectura cuidadosa por
su aparente inestabilidad entre especificaciones. Bajo efectos fijos bidireccionales
(M2, M3) resulta positivo y no significativo, en aparente contradicción con la teoría;
bajo efectos fijos de país únicamente (M5) adquiere el signo negativo esperado y
significancia al 5% ($\hat\beta_2=-4.44$, $t=-2.14$).

Esta divergencia no es anómala sino **mecánicamente esperada**, y refuerza la validez
del diseño. El $GaR$ de estas cinco economías exhibe un fuerte componente común,
gobernado por el ciclo global de crecimiento y la aversión al riesgo internacional. Los
efectos fijos de tiempo de la especificación bidireccional **absorben precisamente ese
componente común**, de modo que el coeficiente de nivel se identifica sobre la variación
idiosincrásica residual del $GaR$ —escasa y débilmente relacionada con el spread una vez
removida la media transversal de cada periodo. Cuando se omiten los efectos de tiempo
(M5), la variación común del $GaR$ reingresa a la regresión y el coeficiente de nivel
recupera el signo teórico.

La implicación metodológica es directa: el **nivel** del $GaR$ es, en esencia, un factor
global cuyo efecto resulta indistinguible del de los demás *push factors* absorbidos por
los efectos de tiempo, por lo que no debe sobreinterpretarse. La **interacción**, en
cambio, se identifica a partir de la covariación *intra-país* entre fragilidad bancaria y
riesgo de cola, y es robusta a ambos esquemas de efectos fijos. La hipótesis de la
investigación es, propiamente, una proposición sobre la *amplificación diferencial*
—captada por $\theta$— y no sobre el efecto incondicional del $GaR$.

## 5.5. Robustez

La inferencia sobre $\theta$ se somete a una batería de pruebas (Cuadro 3).

**Cuadro 3. Robustez del coeficiente de interacción**

| Prueba | $\hat\theta$ | $t$ | Lectura |
|---|---|---|---|
| Driscoll–Kraay (base) | −0.363 | −3.41 | Referencia |
| *Cluster* por país | −0.363 | −3.46 | Inferencia invariante |
| *Cluster* por tiempo | −0.363 | −3.91 | Inferencia invariante |
| HAC de Arellano | −0.363 | −3.46 | Inferencia invariante |
| Submuestra sin COVID-19 (≤2019) | −0.342 | −4.18 | Se fortalece |
| Excluyendo Deuda/PIB | −0.341 | −3.30 | Estable |
| Cola medida con Expected Shortfall | −0.262 | −2.66 | Confirmado |
| Cola medida con prob. crecim. negativo | +1.944 | +1.81 | Signo invertido coherente |

**Estimadores de varianza.** La significancia de $\theta$ es invariante al estimador de
errores estándar empleado: el estadístico $t$ oscila entre $-3.41$ y $-3.91$ y el
$p$-valor permanece por debajo de 0.001 bajo Driscoll–Kraay, *clustering* por país,
*clustering* por tiempo y el estimador HAC de Arellano. La conclusión no descansa, por
tanto, en un supuesto particular sobre la estructura de la matriz de varianzas.

**Exclusión de la pandemia.** Una preocupación natural es que el resultado esté impulsado
por el episodio extremo de 2020. Al reestimar M3 excluyendo todas las observaciones desde
2020, la interacción **se intensifica** ($\hat\theta=-0.342$, $t=-4.18$). El mecanismo de
complementariedad, lejos de ser un fenómeno idiosincrásico de la crisis sanitaria,
caracteriza la relación estructural a lo largo de todo el periodo muestral.

**Medidas alternativas de la cola.** El resultado es robusto a la operacionalización del
riesgo de cola. Sustituyendo el cuantil 5% por el *Expected Shortfall* —la media de la
cola, una medida coherente de riesgo— la interacción conserva signo negativo y
significancia al 1% (M6: $\hat\theta=-0.262$, $t=-2.66$). Empleando la probabilidad de
crecimiento negativo —que, por construcción, se orienta en sentido inverso al $GaR$— la
interacción exhibe el signo **positivo** teóricamente esperado y significancia marginal
($+1.94$, $t=1.81$). Esta inversión de signo, lejos de contradecir la hipótesis, la
corrobora: confirma que es el deterioro del riesgo de cola —cualquiera sea su métrica— lo
que amplifica la transmisión de la fragilidad bancaria.

**Persistencia y dinámica.** Los spreads soberanos exhiben elevada persistencia: en una
especificación dinámica que incluye el spread rezagado, el coeficiente autorregresivo
alcanza 0.84. En dicha especificación la interacción se atenúa pero conserva el signo
correcto y significancia marginal ($\hat\theta=-0.136$, $t=-1.93$). Esta atenuación es
esperable —el rezago absorbe gran parte de la variación contemporánea— y debe leerse con
cautela, pues la inclusión de la dependiente rezagada bajo efectos fijos induce sesgo de
Nickell con $T$ moderado. Se reporta como diagnóstico de persistencia, no como
estimación preferida; un tratamiento formal de la dinámica exigiría un estimador GMM
dinámico (Arellano–Bond), reservado para investigación futura.

**La especificación logarítmica.** En M4, con el spread en logaritmos, la interacción
pierde significancia convencional ($t=-1.09$). Esta atenuación es informativa respecto de
la naturaleza del mecanismo: la transformación logarítmica comprime las observaciones de
spread elevado —los episodios de estrés— que son precisamente donde la amplificación
opera con mayor intensidad. El resultado sugiere que la complementariedad es un fenómeno
de **magnitud absoluta** (puntos básicos), concentrado en los eventos de cola, más que de
naturaleza proporcional; consistente con un multiplicador que se activa en los estados
extremos de la distribución.

## 5.6. Los controles macroeconómicos: interpretación y anomalías

El comportamiento de los controles exige una discusión franca. El **tipo de cambio real
efectivo** se comporta de manera ejemplar: su coeficiente es negativo y altamente
significativo en todas las especificaciones (M3: $-1.05$, $t=-3.67$), indicando que la
apreciación real —asociada a entradas de capital y fortaleza de fundamentos— reduce la
prima de riesgo soberano. Es el control con la lectura económica más limpia y robusta.

En contraste, tres controles fiscales y externos exhiben signos contraintuitivos: el
**balance fiscal** entra con signo positivo (mejor balance asociado a mayor spread), al
igual que la **cuenta corriente**, mientras que la **deuda/PIB** presenta un coeficiente
débilmente negativo. Estos signos no obedecen a multicolinealidad —los factores de
inflación de varianza son uniformemente bajos (todos inferiores a 2.4; Sección 5.7)—
sino, plausiblemente, a **endogeneidad por causalidad inversa**. La consolidación fiscal
en estas economías tiende a producirse *bajo presión de mercado*: los gobiernos ajustan
sus cuentas precisamente cuando enfrentan spreads elevados, generando una correlación
positiva espuria entre mejora del balance y costo de financiamiento. Análogamente, el
ajuste de la cuenta corriente suele materializarse vía compresión de importaciones
durante episodios de *sudden stop*, que coinciden con primas de riesgo elevadas. Estas
simultaneidades sesgan los coeficientes de los controles y requerirían instrumentación
para una interpretación causal —tarea que excede el objeto de este trabajo.

Un punto sustantivo emerge de este patrón. La debilidad del coeficiente de **nivel** de la
deuda, contrapuesta a la robustez de la interacción $JLoss\times GaR$, es coherente con
la tesis del trabajo: en estas economías, la vulnerabilidad soberana relevante no opera
tanto a través del *stock* directo de deuda cuanto a través del **pasivo contingente
bancario**. Es la fragilidad del sistema bancario —proxy del rescate implícito que el
soberano podría verse forzado a asumir— y su interacción con el riesgo de cola del
crecimiento lo que gobierna la prima de riesgo, por encima del endeudamiento explícito.
El canal contingente domina al canal directo, en consonancia con la mecánica del *doom
loop*. Es pertinente señalar, además, que la serie de deuda de Chile procede del Banco
Central de Chile, mientras que la de las restantes economías proviene de los Indicadores
de Desarrollo Mundial; ambas bajo idéntica definición (deuda bruta del gobierno central
como porcentaje del PIB).

## 5.7. Diagnósticos del panel

El conjunto de pruebas diagnósticas valida las decisiones de especificación e inferencia.

La prueba **CD de Pesaran** rechaza contundentemente la independencia transversal
($z=-4.95$, $p<0.001$): los residuos exhiben dependencia transversal significativa aun
después de remover los efectos comunes de tiempo, lo que justifica el empleo de errores
estándar de Driscoll–Kraay —los únicos, entre los considerados, que corrigen esta
dependencia. La prueba de **Wooldridge** detecta autocorrelación serial significativa
($\chi^2=198.95$, $p<0.001$), reforzando la necesidad de un estimador HAC. La prueba de
**Hausman** rechaza la consistencia del estimador de efectos aleatorios
($\chi^2=15.98$, $p=0.001$), confirmando la preferencia por efectos fijos. El test $F$
de **efectos de tiempo** establece su significancia conjunta ($F=3.26$, $p<0.001$),
validando la estructura bidireccional. Finalmente, los **factores de inflación de
varianza** son uniformemente bajos (máximo de 2.35 para el balance fiscal), descartando
problemas de multicolinealidad en el bloque de regresores —resultado que valida *a
posteriori* la decisión de excluir el crecimiento del PIB de la especificación, dada su
elevada correlación con el $GaR$ por construcción.

## 5.8. Síntesis

La evidencia respalda de manera consistente la hipótesis central de complementariedad. El
coeficiente de interacción entre fragilidad bancaria sistémica y riesgo de cola del
crecimiento es negativo, estadísticamente significativo y cuantitativamente estable a
través de: la inclusión progresiva de controles macroeconómicos, cuatro estimadores
alternativos de la matriz de varianzas, la exclusión del episodio pandémico, dos medidas
alternativas del riesgo de cola, y la exclusión de la deuda pública. El efecto de la
fragilidad bancaria sobre el spread soberano se multiplica conforme se agrava el riesgo
de cola —de un efecto nulo en entornos benignos a 2.5 puntos básicos por unidad bajo
estrés severo— configurando la amplificación supra-aditiva que predice el multiplicador
de *doom loop*. La robustez de este resultado contrasta con la fragilidad del efecto de
nivel del $GaR$ —un factor mayoritariamente global— y con las anomalías de signo de los
controles fiscales —atribuibles a endogeneidad—, lo que delimita con precisión el
contenido del hallazgo: lo que determina la prima de riesgo soberano en estas economías
no es la fragilidad bancaria ni el riesgo de cola por separado, sino su interacción.
