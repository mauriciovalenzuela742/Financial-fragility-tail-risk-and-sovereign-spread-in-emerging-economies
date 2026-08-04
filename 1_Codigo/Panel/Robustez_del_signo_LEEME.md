# Defender el signo negativo de θ como regularidad empírica

*Acompaña a `Robustez_del_signo.ipynb` (usa `causal_core.py` + `sign_core.py`). Objetivo
acotado: **θ<0 es una característica estable de los datos**, sin afirmar causalidad.*

## La afirmación defendible (una frase)

> El coeficiente de interacción JLoss×GaR es negativo de forma **pervasiva y sistemática**:
> aparece en (casi) todas las especificaciones, sobrevive un test de permutación
> *distribution-free* a niveles convencionales, y se **invierte de manera predecible** cuando
> la medida de cola se orienta al revés (placebo). Su magnitud es incierta, pero el signo es
> una regularidad robusta del panel.

## La evidencia (cuatro ángulos, ambos paneles)

| Ángulo | all17 (5 países) | extendido (11 países) |
|---|---|---|
| **A. Menú de especificaciones** (θ<0 en …) | **14/14** | **10/12** (las 2 positivas ≈ 0) |
| **B. Placebo `prob_neg`** (cola invertida ⇒ debe voltearse) | **+1.81 (positivo, ok)** | **+1.84 (positivo, ok)** |
| **B. Placebos no-cola** (reer, inflación ⇒ ≈0) | −0.01 / +0.15 | ≈0 |
| **C. Bootstrap de bloques**, P(θ<0) | **91%** | **71%** |
| **D. Permutación**, *p* 1-cola | **0.005** | **0.010** |

Lectura conjunta:

- **A (menú):** el signo no depende de la especificación —pooled, FE país, FE tiempo, FE
  dobles, con/ sin controles, primeras diferencias, winsorizado, sin COVID, sin 2020–21, con
  ES o con GaR skew-t. Es negativo en casi todas.
- **B (placebos):** cuando se usa `prob_neg` (mayor = peor cola, orientación opuesta al GaR)
  la interacción **se vuelve positiva**, exactamente como debe si el signo captura severidad
  de cola. Con variables **no-cola** (REER, inflación) la interacción es ≈0. Esto descarta que
  θ<0 sea un artefacto mecánico.
- **C (bootstrap de países):** frente a la incertidumbre de tener pocos países, el signo
  negativo se sostiene en el **71–91%** de los remuestreos. Honesto: no es 100% —con 5–11
  países la magnitud varía y el IC incluye valores pequeños positivos.
- **D (permutación):** si JLoss y la cola no se relacionaran, un θ tan negativo aparecería
  solo **0.5%–1.0%** de las veces. El signo **no es casualidad**.

## Cómo redactarlo (sin sobre-afirmar)

- Afirmar: "θ es **robustamente negativo** a través de especificaciones, submuestras y medidas
  de cola; un test de permutación rechaza la ausencia de asociación (*p*≈0.005–0.010); y el
  signo se invierte con la métrica de cola espejada (`prob_neg`), como predice el mecanismo."
- No afirmar: que θ sea causal, ni que su magnitud esté identificada con precisión, ni que la
  amplificación varíe con instituciones (eso el dato no lo respalda —ver documento causal).
- Frase puente: "La complementariedad negativa es un **hecho estilizado** del panel; su
  cuantificación causal precisa queda para trabajo con más países e instrumentos más fuertes."

## Qué más se podría agregar (extras opcionales)

1. **Regresión cuantílica del EMBI**: mostrar θ<0 sobre todo en los **cuantiles altos** del
   spread (donde vive el riesgo) —refuerza que el signo importa donde más pesa.
2. **Estimación agrupando ambos paneles** (unión de países) → un θ<0 sobre ~13 economías.
3. **θ rodante en el tiempo** (ventanas móviles): mostrar que el signo persiste por décadas.
4. **Combinación meta-analítica** de los θ de las dos bases (efectos aleatorios) → un signo
   negativo agregado con su intervalo.
5. **Más medidas de cola**: expected shortfall al 1%, asimetría de Bowley, `scale_st` del
   skew-t —todas alineadas deberían dar θ<0.

Dime si quieres que agregue alguno; los tres primeros son rápidos sobre lo ya construido.
