---
title: "Preregistro 9: ESG y gobernanza como factor doméstico del spread, y peso relativo de los factores externos y domésticos (λ)"
subtitle: "Escrito el 27 de octubre de 2026, antes de descargar los datos ESG y de estimar cualquiera de estas pruebas"
---

*Este documento fija un análisis aparte de la tesis. Tiene su propia familia de Holm y no entra en la
inferencia conjunta de las 23 hipótesis (`p66`): ninguna cifra de la tesis cambia. Se commitea solo y
precede a `p67_datos_esg.py`, `p68_indice_esg.py`, `p69_esg_spread.py` y `p70_lambda.py`. Las métricas
no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA).
Todo son asociaciones, no efectos causales.*

**Motivación.**
- **Antecedente:** Barneche, Grezzi y Panario (2024, Universidad ORT Uruguay) relacionan un índice ESG
  soberano con el EMBI en 19 emergentes entre 2005 y 2020, siguiendo a Capelle-Blancard et al. (2019).
  - El índice es un PCA por dimensión sobre 18 variables del Banco Mundial, ponderado por valor propio.
  - El modelo usa efectos fijos de país y EMBI rezagado, sin efectos de tiempo.
  - Encuentran ESG_{t−1} = −0,0066 (p = 0,078), que deja de ser significativo con errores agrupados por
    país (p = 0,119). Por dimensión, solo la gobernanza es significativa (−0,0044, p = 0,049).
- **Lo que agrega este análisis:**
  1. Si el ESG sobrevive a los efectos de tiempo y a la fragilidad bancaria.
  2. Si la gobernanza modera la transmisión de la fragilidad.
  3. Qué peso tienen los factores externos frente a los domésticos, en el sentido de la distinción
     *push*/*pull* que el marco teórico ya discute (Calvo, Leiderman y Reinhart, 1996; Longstaff et al.,
     2011).

**Lo que ya se vio antes de escribir este documento:**
- La tesis de ORT completa (pp. 46–99).
- **Cobertura de la API del Banco Mundial:** solo el número de observaciones y el primer y último año para
  Brasil, Chile e India, sin mirar valores.
  - Las 12 variables WDI y los 6 WGI existen.
  - Tres series ambientales y sociales terminan en 2021: renovables, agotamiento de recursos y paridad de
    matrícula.
  - La serie de CO₂ per cápita que usó ORT está descontinuada y se reemplaza por `EN.GHG.CO2.PC.CE.AR5`.
- Las columnas de `global_controls_bbg.csv` y `usd_neer_bbg.csv`.
- **Que `1_Codigo/Panel/instituciones.csv` es una plantilla:** valores aproximados del WGI 2018,
  marcados "verificar". Su triple interacción no es significativa (NUMEROS_CANONICOS_BBG).
- Ningún resultado que relacione ESG, WGI o un índice externo con el spread de este panel.

## 1. Bases comunes

**Muestra y especificación base**
- **Muestra:** la de la especificación principal de la tesis (`p14.base()`, 13 economías, N = 765), con
  `p14.check_principal` como control.
- **Especificación base (B):**

  ln EMBI_it = a_i + d_t + b1 J_c + b2 T_c + b3 J_c·T_c + e_it,

  con J_c = ln JLoss_{t−1} centrado y T_c = D_{t−1} centrado (D = −GaR, en pp).

**Inferencia**
- Driscoll–Kraay como error de referencia (`p14.DK`).
- *Wild cluster bootstrap* por país (Webb, 999, `p32.wild`). El p unilateral sigue la convención de
  `p42`: p/2 con el signo predicho y 1 − p/2 con el contrario.

**Moderadores y regresores nuevos**
- Se estandarizan en la muestra de estimación, como `M_s` en `p42.moderacion`.
- Entran con el valor disponible en t − 1 (ver la sección 2).

**Criterio de firmeza** (el de los preregistros anteriores):
- p con Holm < 0,05 sobre la familia primaria;
- **y**, al excluir un país a la vez, el mismo signo con p unilateral < 0,10 en las 13 submuestras.

**Reglas generales**
- Semilla 20261027.
- Se reporta todo, salga como salga, en `4_Redaccion/analisis_esg_lambda.md`.
- Toda desviación se declara con su razón.

## 2. Datos y construcción (`p67`, `p68`)

**Fuente.** API del Banco Mundial por `urllib`, con el patrón de `p0_controles_all.py`. Cubre las 13
economías más Argentina (robustez), de 2000 a 2025. Se guardan:
- el bruto anual en `2_Datos/esg_wb_anual.csv`;
- el trimestral en `bbg/esg_trimestral_bbg.csv`.

**Variables (las 18 de ORT)**

| Dimensión | Variable | Código | Transformación (mayor = mejor) |
|---|---|---|---|
| E | Intensidad energética primaria | `EG.EGY.PRIM.PP.KD` | 1/x |
| E | Energía renovable (% consumo final) | `EG.FEC.RNEW.ZS` | x |
| E | CO₂ per cápita | `EN.GHG.CO2.PC.CE.AR5` | 1/x |
| E | Área forestal (% tierra) | `AG.LND.FRST.ZS` | x |
| E | Agotamiento de recursos naturales (% INB) | `NY.ADJ.DRES.GN.ZS` | 1/x |
| E | Estrés hídrico | `ER.H2O.FWST.ZS` | 1/x |
| S | Matrícula secundaria bruta | `SE.SEC.ENRR` | x |
| S | Gasto público en salud (% gasto en salud) | `SH.XPD.GHED.CH.ZS` | x |
| S | Esperanza de vida | `SP.DYN.LE00.IN` | x |
| S | Paridad de género, matrícula primaria | `SE.ENR.PRIM.FM.ZS` | x |
| S | Empleo vulnerable (% empleo) | `SL.EMP.VULN.ZS` | 100 − x |
| S | Participación laboral mujer/hombre | `SL.TLF.CACT.FM.ZS` | x |
| G | Voz y rendición de cuentas | `GOV_WGI_VA.EST` | x |
| G | Estabilidad política | `GOV_WGI_PV.EST` | x |
| G | Efectividad del gobierno | `GOV_WGI_GE.EST` | x |
| G | Calidad regulatoria | `GOV_WGI_RQ.EST` | x |
| G | Estado de derecho | `GOV_WGI_RL.EST` | x |
| G | Control de la corrupción | `GOV_WGI_CC.EST` | x |

Si un valor de 1/x no está definido (x = 0), queda faltante.

**Variables de Tebaldi, Nguyen y Zuluaga (2018)**, solo para lo exploratorio:
- crecimiento del PIB, `NY.GDP.MKTP.KD.ZG`;
- apertura, `NE.TRD.GNFS.ZS`;
- liberalización política de Freedom House: (8 − (PR + CL)/2), con las calificaciones 1–7 de derechos
  políticos y libertades civiles.

Si la descarga de Freedom House no es posible, se usa el índice de democracia liberal de V-Dem
(`v2x_libdem`). Si tampoco lo es, se declara y se usa WGI VA. El TCRE ya está en el panel (`reer`).

**Tiempo, sin anticipación**
- El valor del año y entra en los cuatro trimestres del año y + 1 (escalón). El WGI del año y se publica
  en el otoño de y + 1, y los WDI tienen un rezago similar.
- En la regresión se usa el valor del trimestre t − 1, alineado con ln JLoss_{t−1} y D_{t−1}.
- *Robustez:* interpolación lineal con `annual_to_quarterly()` de `p0_controles_all.py`, con el mismo
  rezago de un año.
- *Vacíos al final:* se arrastra el último valor hasta tres años, con una marca. Robustez: muestra hasta
  2021Q4.
- *Vacíos intermedios:* interpolación lineal entre años observados.

**Índices**
- **G (principal):** primer componente principal de los seis WGI, estandarizados en el panel país-año
  (2003–2025). Se orienta para que mayor = mejor gobernanza.
- **ESG (réplica de ORT):**
  1. A cada variable transformada se le aplica ln(x + 1 + |mín|) si tiene valores ≤ 0, y ln(x) si no;
     luego se estandariza.
  2. PCA por dimensión, con el conjunto final de ORT. E: renovables, CO₂, agotamiento e intensidad, sin
     bosque ni agua. S: las seis. G: las seis.
  3. Se toma el primer componente de cada dimensión, con signo orientado a mayor = mejor.
  4. ESG = Σ_d (λ_d / Σλ) · C_d, con λ_d el primer valor propio de la dimensión d.
- **Se reporta además:**
  - KMO por variable y global, calculado con numpy;
  - cargas y valores propios, comparados con los de ORT (sus pp. 69–75);
  - la fracción de la varianza de G y ESG que es dentro del país.

## 3. Familia primaria (Holm sobre E1–E5)

**E1. ESG dentro del país.** B + ESG_s. Predicción: coeficiente < 0.

**E2. Gobernanza dentro del país.** B + G_s. Predicción: coeficiente < 0.

**E3. La gobernanza modera la transmisión de la fragilidad.** B + G_s + J_c·G_s. Predicción: el
coeficiente de J_c·G_s es < 0. La fragilidad bancaria se traslada menos al spread donde la gobernanza es
mejor: un Estado con instituciones creíbles convierte el pasivo contingente en una carga más acotada.

**E4. Peso de los factores externos.** Modelo de dos bloques (sección 4). Predicción: λ > 0,5, porque la
literatura encuentra que los factores globales dominan (Longstaff et al., 2011). p unilateral = fracción
de réplicas del *bootstrap* con λ* ≤ 0,5.

**E5. El peso externo sube con la tensión global.** λ_t = logística(θ0 + θ1·z(ln VIX_{t−1})). Predicción:
θ1 > 0. p de la razón de verosimilitud contra λ fijo (χ²₁), unilateral con la convención de la sección 1.

**Firmeza de E4 y E5 al excluir un país:** se reestima sin cada país, con un *bootstrap* de 199 réplicas.
Pasa si λ > 0,5 con p < 0,10 en E4, o θ1 > 0 con p < 0,10 en E5, en las 13 submuestras.

## 4. Modelo de dos bloques (`p70`)

  ln EMBI_it = a_i + β·[ λ·Ĝ_t + (1 − λ)·D̂om_it ] + e_it

**Bloque externo:** G_t = Σ_k w_k z_k, con las variables en t − 1 y orientadas a mayor = más riesgo:
- ln VIX;
- UST10Y (log);
- US HY spread (log);
- USD NEER (log, BIS; dólar más fuerte = más riesgo).

**Bloque doméstico:** Dom_it = Σ_j v_j z_j, con:
- ln JLoss_{t−1} y D_{t−1};
- deuda/PIB_{t−4}, −reservas/PIB_{t−4} e inflación_{t−4} (los controles de la tesis en t − 4);
- −G_{t−1}.

**Restricciones e interpretación**
- w y v son no negativos y suman uno en cada bloque (*softmax*). Una variable con signo contrario al
  esperado recibe peso cercano a cero, y eso se reporta.
- Ĝ y D̂om son los índices divididos por su desviación estándar dentro del país. λ ∈ (0, 1) (logística) y
  β > 0 es la escala.
- **λ es la fracción del efecto combinado que aporta una desviación estándar del bloque externo.**
- Se usan efectos fijos de país, el "fondo" de cada economía, que se concentran restando la media por
  país. No hay efectos de tiempo, porque absorberían G_t.

**Estimación e inferencia**
- Mínimos cuadrados no lineales (`scipy.optimize.least_squares`) desde 20 puntos de partida; se elige el
  de menor SSR.
- *Bootstrap* por bloques móviles de 8 trimestres sobre el eje del tiempo (todos los países de los
  trimestres sorteados), con 499 réplicas.
- *Jackknife* por país.

**Validación (antes de los datos reales)**
- **Simulación:** se generan datos con los regresores reales, λ = 0,6, pesos iguales y ruido con la
  varianza residual del modelo lineal. Son 100 réplicas, y el estimador debe recuperar una media de λ̂
  dentro de ±0,05 de 0,6. Si no la recupera, se declara y E4 y E5 pasan a exploratorias.
- **Descomposición de Shapley** del R² dentro del país del modelo lineal sin restringir con los mismos
  regresores. La participación del bloque externo se reporta junto a λ.

**λ por régimen:** el de E5. Se reporta también el BIC frente al λ fijo.

## 5. Exploratorio (fuera de Holm)

- **"Efecto fijo de fondo":**
  - Mundlak: sin efecto fijo de país, con la media de G (y ESG) por país y la desviación respecto de esa
    media, más efectos de tiempo y errores agrupados por país.
  - Regresión de los efectos fijos de país de B sobre el G medio de cada país (13 puntos, descriptiva).
- **Las dimensiones E y S por separado,** como en ORT.
- **D·G** (¿la gobernanza modera la transmisión del riesgo de cola?).
- **Réplica de la especificación de ORT:** EMBI en tanto por uno, EMBI rezagado, reservas/PIB, deuda/PIB,
  inflación, crecimiento y ESG_{t−1}, con efectos fijos de país y sin efectos de tiempo. Se estima en la
  muestra trimestral y en la anual (promedio por año).
- **Réplica de Tebaldi et al. (2018):**
  - ln EMBI sobre ln EMBI_{t−1}, crecimiento, TCRE, apertura y liberalización política, con efectos fijos
    de país (LSDV, T ≈ 88);
  - versión anual con GMM de sistema e instrumentos colapsados, advirtiendo que con 13 países hay más
    instrumentos que grupos.
  - La liberalización política reemplaza a G en E2 y E3 como comparación.
- **Robustez del índice:** pesos iguales entre dimensiones; PCA ajustado solo con 2003–2012; interpolación
  en lugar de escalón; muestra hasta 2021; Argentina incluida.
- **En el modelo λ:** el TCRE y el crecimiento en el bloque doméstico; el EMBI en puntos básicos.
- **Triple interacción con el WGI real:** se reemplaza la plantilla en el ejercicio de `p3_causal_fase5`,
  sin tocar la tesis. Si el resultado cambia, se informa.

## 6. Qué sería evidencia en contra

- **E1 y E2:** coeficientes ≥ 0 o no distinguibles de cero. Mostraría que, una vez que los efectos de
  tiempo y la fragilidad bancaria entran al modelo, el ESG no agrega información dentro del país. Lo que
  ORT atribuye al ESG sería, en ese caso, diferencias entre países (efecto fijo) o ciclo global.
- **E3:** coeficiente ≥ 0. La gobernanza no atenúa la transmisión de la fragilidad.
- **E4:** λ ≤ 0,5. En este panel, el bloque doméstico pesa tanto o más que el externo.
- **E5:** θ1 ≤ 0. El peso externo no sube con la tensión global.

## 7. Advertencias declaradas de antemano

- La gobernanza y el ESG cambian lento. Se espera que la mayor parte de su varianza sea entre países y la
  absorba el efecto fijo de país, por lo que E1 y E2 tienen poca potencia. En ORT, la significancia ya
  desaparecía con errores agrupados.
- Con 13 países, la parte entre países (Mundlak y el segundo paso) es descriptiva.
- λ depende de la estandarización de los bloques y de qué variables entran en cada uno. Por eso se reporta
  junto a la descomposición de Shapley y no se lee como una cifra estructural.
- El PCA se ajusta con toda la muestra, lo que es una mirada hacia adelante en las cargas. La robustez con
  2003–2012 lo acota.
- **Este análisis no modifica la tesis.** Si algún resultado justifica incorporarlo, se decide aparte.
