# Defensa del GaR — preguntas probables del profesor y respuestas

Guion de anticipación para justificar que la construcción y validación del GaR tienen
sentido. Cada respuesta se apoya en evidencia concreta ya verificada (porteo, validaciones
internas y comparación externa). Números listos para citar.

---

## A. Fidelidad de la construcción

**1. ¿Por qué el marco CEMLA C-GARP y no directamente la skew-t de Adrian et al. (2019)?**
El cuantil condicional al 5% es el objeto primitivo del estimador de Koenker; la skew-t es
una *elección de suavizado*, no el dato. Se usa el cuantil directo (con reordenamiento de
Chernozhukov–Fernández-Val–Galichon 2010) y se conserva la skew-t como control de robustez
(`GaR_st`). La correlación entre ambos es **0.9996** (RMSE 0.0011): el resultado no depende
del suavizado.

**2. ¿El porteo de R a Python es fiel? ¿No introdujeron errores?**
Sí, es fiel y verificado por etapas contra la referencia CEMLA (`GaR_test.xlsx`):
- Preprocesamiento (lead, ortogonalización, z-score): `max|diff| ≈ 1e-15` (exacto).
- Estimador de panel `pfe`: el programa lineal (HiGHS) alcanza el **óptimo global**; su
  objetivo es estrictamente menor que el de `rqpd` (2.40614 vs 2.40654, que se detiene por
  tolerancia). Los coeficientes caen dentro de ~1e-3 de la referencia.
- El FCI reproduce la referencia oficial de México con **corr = 0.9995** (RMSE 0.016,
  212/212 meses).

**3. ¿Por qué el percentil 5% directo, sin KDE ni ancho de banda?**
Porque es la lectura del estimador en su propio nivel; evita un ancho de banda arbitrario.
La malla de cuantiles (`n_tau = 39`) hace que el 0.05 caiga exacto, sin interpolar. La
skew-t confirma que no es un artefacto.

**4. ¿Por qué horizonte h = 1 trimestre?**
Para alinear el GaR con la frecuencia trimestral del JLoss y el *merge* por (país,
trimestre): mide el riesgo de cola contemporáneo con `JLoss_{i,t}`. La estimación es en
**ventana expansiva** (pseudo real-time), sin *look-ahead*: los coeficientes se re-estiman
solo con datos hasta cada corte.

---

## B. Identificación y endogeneidad (la preocupación planteada)

**5. El modelo de un factor tiene endogeneidad: el FCI depende de inflación y tasas, que se
determinan junto con el PIB. ¿Cómo lo abordan?**
En tres niveles. (i) En la construcción, el factor financiero se **ortogonaliza respecto del
VIX** (se usan los residuos de FCI~VIX), separando las condiciones financieras domésticas del
factor global y evitando el sesgo por conflación. (ii) El GaR es **reduced-form por diseño**:
la propia metodología CEMLA advierte que la relación crecimiento–condiciones financieras no
debe leerse como causal; el GaR condiciona la cola, no la explica causalmente. (iii) La
pretensión **causal** recae en la etapa de panel del spread, no en el GaR.

**6. ¿Por qué ortogonalizar contra el VIX y no contra inflación y PIB, que es de donde viene
la circularidad?**
Porque la ortogonalización FCI⟂VIX ataca la conflación doméstico/global que es específica del
diseño de un factor. La circularidad estructural inflación–PIB (regla de Taylor) se aborda en
la regresión de spread mediante **efectos fijos de tiempo**, que absorben el ciclo global
común de inflación y política monetaria —confirmado en el código (`fetch_controls.py`)—,
dejando la identificación en la fragilidad financiera **relativa** entre países.

**7. Es que "siempre va a dar algo", por construcción. ¿No es un resultado mecánico?**
Precisamente por eso no interpretamos el GaR como causal: es un condicionamiento de la cola.
La hipótesis contrastable no es "el GaR causa", sino que la **interacción** JLoss×GaR en el
spread es negativa y significativa condicional a controles y efectos fijos —eso no es
mecánico y es lo que se prueba (θ = −0.338 en la base principal, con Driscoll–Kraay).

---

## C. Validación: ¿el GaR es razonable en escala y movimiento?

**8. ¿Cómo saben que la escala del GaR es correcta?**
Porque el pipeline reproduce el marco CEMLA a nivel numérico (preprocesamiento a 1e-15; FCI
vs. México 0.9995). Las magnitudes son plausibles: en el shock COVID (2020Q2) el GaR cae a
≈ **−18%** con `prob_neg = 1.0` en todas las economías, coherente con la contracción observada.

**9. ¿Y que el movimiento temporal tiene sentido?**
Tres evidencias: (i) el *timing* de crisis —COVID 2020Q2 y el *tightening* de 2022Q3, con
colas que se ensanchan (dispersión 0.077 → 0.100)—; (ii) el mecanismo de *vulnerable growth*
de Adrian et al.: `corr(GaR, dispersión) = −0.235`, o sea, peor cola coincide con colas más
anchas; (iii) la comparación externa (pregunta 11).

**10. ¿Por qué no compararon directamente con el GaR del FMI?**
El FMI no publica una serie de GaR por país limpia y descargable (aparece en el GFSR de forma
cualitativa). Por eso el ancla es la referencia del **mismo marco** (CEMLA, coincidencia
exacta) y, para triangular, métricas de riesgo **independientes** (abajo).

**11. ¿Con qué métrica externa validaron que el GaR captura riesgo real?**
Con dos series públicas, en las 17 economías, trimestral:
- **VIX**: correlación negativa en las 17 (pooled within ≈ **−0.50**).
- **SRISK mundial (NYU V-Lab)**: correlación negativa en las 17 (pooled within ≈ **−0.47**).
El signo esperado es negativo (GaR alto = piso más alto = menos riesgo). El co-movimiento es
consistente y del signo correcto.

**12. Pero el VIX está dentro del GaR: ¿no es circular usarlo como validación?**
Correcto, y por eso el benchmark **clave es el SRISK de V-Lab**, que es **externo** a la
construcción del GaR (riesgo sistémico basado en déficit de capital del sistema financiero).
Que un riesgo sistémico ajeno co-mueva negativamente con el GaR en las 17 economías es la
evidencia externa fuerte. El VIX solo confirma consistencia interna.

---

## D. Muestra y cobertura

**13. ¿Por qué el GaR está para 17 economías pero la regresión usa 5 (all17) u 11
(extended)?**
El GaR se entrena con 17 economías para una distribución condicional más rica; la regresión
del spread usa los países con **EMBI disponible**: 5 en la base principal (con controles
domésticos) y 11 en la extendida (robustez, sin controles domésticos). Son dos bases
reportadas por separado, no un cruce.

**14. ¿Qué pasa con Argentina y sus defaults?**
Entra al panel de GaR con **VIX en lugar de FCI**, por su historial de default y mercados de
bonos discontinuos. Se documenta como limitación de datos, no se fuerza un FCI poco fiable.

---

## E. Decisiones que podrían cuestionarse

**15. ¿Por qué excluir el crecimiento observado (g_GDP) de la regresión?**
Porque `corr(g_GDP, GaR) ≈ 0.84`: incluir ambos genera coeficientes explosivos e inestables
en signo. El objeto de interés es la **cola** (GaR), no la media (g_GDP).

**16. ¿La no linealidad no debería probarse con un modelo de umbrales (Hansen)?**
La no linealidad ya reside en las colas: el loss-at-risk y el JLoss se anclan a un percentil,
y estadísticamente la acción está en el extremo, no en la media. El atajo estándar y robusto
es el **término multiplicativo** JLoss×GaR; Hansen se reporta a lo más como robustez, no como
método principal, para no sobrecomplicar la teoría.

**17. ¿La ventana expansiva no contamina con datos futuros?**
No: en cada corte t los coeficientes se re-estiman solo con datos hasta t, y las
observaciones dentro del horizonte del borde salen de la estimación. No hay *look-ahead*.

---

## G. El objeto central: robustez del término de interacción (JLoss × GaR)

> Lo que investigamos es la **multiplicación** JLoss × GaR: la derivada cruzada
> ∂²EMBI/∂JLoss∂GaR = θ < 0 (complementariedad del *doom loop*). Las preguntas de
> robustez deben apuntar a **θ**, no al nivel de JLoss.

**18. ¿Sobrevive el término de interacción θ al controlar por otras métricas de riesgo, o se
lo come el riesgo global?**
Sobrevive y es estable. Base `all17`, N = 253, EMBI, variables centradas, errores
Driscoll–Kraay:

| Modelo | θ (JLoss × GaR) |
|---|---|
| FE país + tiempo | −0.313** (0.143) |
| FE país (base robustez) | −0.293*** (0.110) |
| + VIX | −0.283** (0.116) |
| + SRISK (V-Lab) | −0.344*** (0.114) |
| + VIX y VIX × GaR | −0.271** (0.124) |
| + SRISK y SRISK × GaR | −0.338*** (0.126) |

θ se mantiene negativo y significativo (≈ −0.27 a −0.34) al añadir el riesgo global (VIX), el
sistémico **externo** (SRISK) e incluso sus **propias interacciones** con el GaR. La
amplificación no es un artefacto del riesgo agregado. (Las columnas con OFR FSI, EM Corporate
OAS y US HY completo se agregan con `--download`; se espera el mismo patrón.)

**19. ¿No daría lo mismo cualquier medida de riesgo multiplicada por el GaR? ¿Por qué JLoss?**
No: la complementariedad es **específica de la fragilidad bancaria**. Sustituyendo JLoss por
otra medida en la interacción con el GaR (misma base, mismos controles y FE):

| Interacción alternativa | Coeficiente |
|---|---|
| VIX × GaR (sin JLoss) | −0.916 (0.886), **no significativo** |
| SRISK × GaR (sin JLoss) | −0.002 (0.001), **no significativo** |

El signo es el correcto, pero ni la volatilidad global ni el riesgo sistémico agregado
reproducen la interacción **significativa** que sí tiene JLoss × GaR. Esto **identifica el
canal**: es la fragilidad bancaria —pasivo contingente fiscal— la que amplifica el riesgo
soberano cuando la cola del crecimiento se deteriora, tal como predice el nexo
soberano-bancario (Farhi–Tirole 2018). La especificidad es evidencia **a favor** del
mecanismo, no en contra.

**20. ¿Y JLoss amplifica solo con el GaR, o con cualquier métrica de riesgo? (respuesta
honesta)**
JLoss también interactúa con el VIX, no solo con el GaR; con el SRISK agregado, no. Base
`all17`, N = 253:

| Interacción | Individual | Horse-race (juntas) |
|---|---|---|
| JLoss × GaR | −0.294*** (0.110) | −0.544*** (0.095) |
| JLoss × VIX | −0.999** (0.436) | −1.437*** (0.498) |
| JLoss × SRISK | −0.0003 (n.s.) | −0.0001 (n.s.) |

No lo sobrevendemos como "solo el GaR". Dos matices decisivos: (i) el **VIX está dentro de la
construcción del GaR**, así que JLoss×VIX se solapa parcialmente con JLoss×GaR; (ii) en el
*horse-race*, **JLoss×GaR sobrevive** (−0.54***) junto a JLoss×VIX, aportando amplificación
**propia** más allá de la volatilidad global. Sumado al Panel B (solo JLoss×GaR entre las
interacciones-con-GaR es significativa), el canal robusto y teóricamente motivado es
**fragilidad bancaria × cola del crecimiento real (GaR)**: inestabilidad financiera ×
inestabilidad económica, distinta de la interacción con el riesgo puramente financiero.

*(Como robustez adicional, el nivel de JLoss rezagado también sobrevive a cada métrica —2.5 a
3.0 pb, siempre significativo—, pero el resultado que sostiene la tesis es θ.)*
Errores estándar entre paréntesis; *** p$<$0.01, ** p$<$0.05, * p$<$0.1.

## F. Cierre defensivo (una frase)

El GaR no se ofrece como una relación causal, sino como una **medida reducida de riesgo de
cola del crecimiento**, construida con un marco estándar (CEMLA), reproducida con precisión
numérica, robusta al método (skew-t 0.9996) y **validada externamente** contra un riesgo
sistémico independiente (SRISK) en las 17 economías. La inferencia causal de la tesis vive en
la interacción JLoss×GaR bajo efectos fijos, no en el GaR mismo.
