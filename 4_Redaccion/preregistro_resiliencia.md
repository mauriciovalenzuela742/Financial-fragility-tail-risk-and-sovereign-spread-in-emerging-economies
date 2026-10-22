---
title: "Preregistro: resiliencia, controles y transmisión de los riesgos al spread"
subtitle: "Escrito el 21 de octubre de 2026, antes de descargar los datos trimestrales y antes de estimar"
---

*Este documento fija las hipótesis, las especificaciones, las reglas de datos y la consecuencia de las
pruebas de resiliencia **antes** de bajar los datos trimestrales y de estimar. El commit que lo
contiene precede en el historial de git a los de `p41_datos_resiliencia.py` y
`p42_resiliencia_preregistrada.py`; esa es la acreditación de la fecha (corrige el problema de `p26`,
cuyo primer commit fue posterior a sus resultados). Todo lo que sigue son asociaciones, no efectos
causales.*

**Declaración de lo que ya se vio.** El autor conoce los resultados previos con controles anuales
interpolados:
- el término de reservas/PIB × fragilidad fue −0,247, exploratorio (depende de Polonia y no pasa Holm);
- con los seis controles, la elasticidad de la fragilidad cae a −0,008.

Por eso las hipótesis no son ciegas. Lo nuevo y no visto son los datos trimestrales, las medidas
(adecuación de reservas en lugar de reservas/PIB; deuda trimestral) y el método (efecto directo
controlado).

---

## 1. Base

La especificación principal de la tesis, con la variable dependiente ln EMBI_{i,t} y los regresores
ln JLoss_{i,t−1}, D_{i,t−1} = −GaR_{i,t−1} y su producto. Los regresores van centrados, con efectos fijos
de país y de tiempo, y la muestra es la de la regresión principal restringida a las observaciones con
el moderador disponible. Inferencia:
- wild cluster bootstrap por país, con pesos de Webb y 999 réplicas;
- Driscoll–Kraay como referencia.

## 2. Datos (reglas fijadas antes de mirarlos)

| Variable | Fuente primaria | Regla si falta |
|---|---|---|
| Deuda del gobierno general, % del PIB, trimestral (DEBT) | Banco Mundial, Quarterly Public Sector Debt (QPSD) | Si falta, gobierno central de la misma base; si tampoco existe, la serie anual interpolada actual, con una marca. Se reporta la cobertura |
| Reservas internacionales sin oro, USD, mensual | FMI IFS/IRFCL (`api.imf.org`) | Banco Mundial GEM; si tampoco existe, la serie anual |
| Deuda externa de corto plazo, todos los sectores, USD, trimestral | Banco Mundial QEDS | Sin sustituto: la economía queda fuera de R-H2 y se declara |
| Adecuación de reservas, RA = ln(reservas / deuda externa de corto plazo) (Greenspan–Guidotti) | Construida | — |

Los moderadores entran rezagados cuatro trimestres (t−4) y estandarizados sobre la muestra de
estimación.

## 3. Hipótesis

**R-H1 (efecto directo controlado).** El efecto de la fragilidad sobre el spread **neto del canal
fiscal** es positivo. Se estima por g-estimación secuencial (Acharya, Blackwell y Sen, 2016):
1. ln EMBI_t sobre ln JLoss_{t−1}, D_{t−1}, los mediadores M_t = (balance fiscal/PIB_t, DEBT_t) y los
   confusores intermedios (inflación_t, tipo de cambio real_t), con efectos fijos de país y de tiempo.
2. Se resta el aporte de los mediadores: Ỹ = ln EMBI_t − M_t'γ̂_M.
3. Ỹ sobre ln JLoss_{t−1}, D_{t−1} y los controles previos (los seis controles en t−4), con efectos fijos
   de país y de tiempo.

El coeficiente de ln JLoss_{t−1} en el paso 3 es el efecto directo controlado (EDC). La inferencia es un
bootstrap de bloques por país sobre las dos etapas (999 réplicas). Contraste unilateral: EDC > 0. Se
reportan además el efecto total (la principal sin interacción) y la fracción mediada.

**R-H2 (adecuación de reservas, familia primaria).** Se agregan RA_{t−4} y ln JLoss_{t−1} × RA_{t−4} a
la base. Predicción: el coeficiente λ de la interacción es **negativo**, es decir, más reservas frente
a la deuda de corto plazo implican menos transmisión de la fragilidad.

**R-H3 (espacio fiscal, familia primaria).** Se agregan DEBT_{t−4} y D_{t−1} × DEBT_{t−4} a la base.
Predicción: el coeficiente ψ es **positivo**, es decir, más deuda implica más transmisión del riesgo de
cola.

## 4. Inferencia y criterio

- **Familia primaria:** {λ, ψ}, con p unilateral del wild bootstrap y corrección de Holm sobre las dos.
- **Veredicto "firme":** p de Holm < 0,05 y, sin cada país, el mismo signo con p unilateral < 0,10 en
  las 13 exclusiones.
- **Veredicto "sugerente":** p de Holm < 0,05 sin pasar la exclusión de países, o p < 0,05 solo con
  Driscoll–Kraay.
- **R-H1** se evalúa sola, con el bootstrap de bloques (α = 0,05, unilateral).

## 5. Pruebas secundarias (se reportan todas; no cambian el veredicto)

- R-H2 con reservas/PIB en lugar de RA.
- R-H2 y R-H3 con los moderadores en t−8.
- R-H2 y R-H3 en la especificación en niveles (pb).
- **Proyecciones locales mensuales dependientes del estado.** Con la serie mensual de `p37`, la
  respuesta acumulada de ln EMBI_{m+h} − ln EMBI_{m−1} a Δ(−DD_w)_m, h = 0…6, se estima por separado
  según el estado de reservas:
  - "alto" si el RA del último trimestre conocido supera la mediana de su país;
  - predicción: una respuesta menor en el estado alto.
  - La diferencia entre estados se contrasta con Driscoll–Kraay y con el wild bootstrap.

## 6. Consecuencia fijada de antemano

- **Si R-H2 no pasa Holm:** el término de reservas de la tesis queda definitivamente como exploratorio
  y la conclusión 4 ("ninguna condición modifica la transmisión de forma demostrable") se mantiene.
- **Si R-H2 es firme:** la conclusión 4 se reescribe y dice que la adecuación de reservas atenúa la
  transmisión de la fragilidad. Ese resultado se reporta en el resumen, en la introducción y en las
  conclusiones.
- **Si R-H1 rechaza la nula:** la tesis dirá que la fragilidad conserva una asociación directa neta del
  canal fiscal, lo que resuelve la ambigüedad del "mal control" (−0,008 con los seis controles).
- **Si R-H1 no la rechaza:** la tesis dirá que no se puede separar la asociación de la fragilidad de su
  paso por las cuentas fiscales.
- **R-H3** se reporta con su veredicto en la sección de resiliencia, cualquiera sea.
