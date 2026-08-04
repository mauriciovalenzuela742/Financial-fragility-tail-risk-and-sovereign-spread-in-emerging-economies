# Plan — Tablas de riesgo (estilo del paper del profesor), centradas en la interacción

El objeto de la tesis es la **multiplicación** JLoss × GaR: la derivada cruzada
∂²EMBI/∂JLoss∂GaR = **θ < 0** (complementariedad del *doom loop*). Las tablas se organizan
alrededor de **θ**, no del nivel de JLoss.

## Bases de datos (dos, como en el análisis v3)

- **`Panel_final_all17.csv`** — base principal. 5 países LatAm con EMBI, GaR entrenado con 17
  economías, 2007Q4–2022Q2. Con controles domésticos. Modelo M3 (+controles); θ ≈ −0.31/−0.34.
- **`Panel_extended_15paises.csv`** — robustez. 11 países con EMBI, **sin** controles
  domésticos, `VIX_cboe`. Modelo M2 (FE país+tiempo); θ ≈ −0.21.

Cada tabla se corre **por separado** en las dos bases.

---

## Tabla 1 — Robustez y especificidad del término de interacción θ (estilo *Table 8*)

**Modelo central** (variables centradas; FE país; Driscoll–Kraay):

```
EMBI_{i,t} = α + β·JLoss_c + γ·GaR_c + θ·(JLoss×GaR)_c + Θ'·Controles + μ_i (+λ_t) + ε
```

Sin FE de tiempo en las columnas con métricas globales (VIX, SRISK, OFR, EM_OAS), para que
tengan variación (igual que el profe: Time FE = No).

> **Nota de bases:** el resultado robusto vive en la **base principal (all17, con controles)**.
> La **extendida** (11 países, sin controles domésticos, `VIX_cboe`) corrobora el **signo**
> pero es más ruidosa: θ solo es marginal. Se reportan ambas.

### Panel A — ¿Sobrevive θ al controlar por cada métrica de riesgo?

| Modelo | θ — all17 (N=253) | θ — extendida (N=374) |
|---|---|---|
| FE país + tiempo | −0.313** (0.143) | −0.212* (0.116) |
| FE país | −0.293*** (0.110) | −0.232 (0.166) |
| + VIX | −0.283** (0.116) | −0.173 (0.166) |
| + SRISK (V-Lab) | −0.344*** (0.114) | −0.247 (0.156) |
| + VIX y VIX × GaR | −0.271** (0.124) | −0.134 (0.188) |
| + SRISK y SRISK × GaR | −0.338*** (0.126) | −0.244* (0.141) |

En **all17**, θ se mantiene negativo y significativo (≈ −0.27 a −0.34) frente a todo. En la
**extendida**, θ es **marginal**: −0.212* bajo FE país+tiempo (la spec M2, coincide con el
`LEEME`) y pierde significancia sin FE de tiempo. El signo es siempre negativo.
*(Pendiente: columnas con OFR FSI, EM Corporate OAS y US HY tras `--download`.)*

### Panel B — ¿El rol amplificador del GaR es específico de JLoss?

Se sustituye JLoss por cada métrica en la interacción **con el GaR**:

| Interacción | all17 (N=253) | extendida (N=374) |
|---|---|---|
| **JLoss × GaR** | **−0.293*** (0.110)** | −0.232 (0.166) |
| VIX × GaR (sin JLoss) | −0.916 (0.886), n.s. | −0.148 (0.201), n.s. |
| SRISK × GaR (sin JLoss) | −0.002 (0.001), n.s. | +0.003* (0.002), signo + |

En **all17**, solo JLoss × GaR es significativa: el rol amplificador del GaR es específico de
su emparejamiento con la fragilidad bancaria. En la extendida ninguna interacción-con-GaR es
significativa (JLoss×GaR marginal), y SRISK×GaR sale con signo positivo (no interpretable).

### Panel C — ¿JLoss amplifica solo con el GaR, o con cualquier riesgo?

| Interacción | all17 individual | all17 horse-race | extendida individual | extendida horse-race |
|---|---|---|---|---|
| **JLoss × GaR** | −0.294*** (0.110) | −0.544*** (0.095) | −0.232 (0.166) | −0.186 (0.141) |
| JLoss × VIX | −0.999** (0.436) | −1.437*** (0.498) | −0.025 (0.085), n.s. | +0.073 (0.056), n.s. |
| JLoss × SRISK | −0.0003 (0.0007), n.s. | −0.0001, n.s. | +0.0003, n.s. | −0.0009, n.s. |

**Lectura honesta.** En **all17**, JLoss también interactúa con el **VIX** (no solo con el
GaR), pero con dos matices: el VIX **está dentro del GaR** (solapamiento), y **JLoss×GaR
sobrevive el horse-race** aportando amplificación propia. En la **extendida**, JLoss×VIX
**no** es significativa y nada sobrevive el horse-race (base más ruidosa, sin controles). El
canal robusto y teóricamente motivado —presente en la base principal— es **fragilidad
bancaria × cola del crecimiento real (GaR)**: inestabilidad financiera × inestabilidad
económica.

*Significancia: *** p<0.01, ** p<0.05, * p<0.1. Errores Driscoll–Kraay entre paréntesis.*
*Los coeficientes de interacción no son comparables en magnitud entre métricas (unidades
distintas); importa el signo y la significancia.*

---

## Tabla 2 — Métricas de comparación (estilo *Table A.3*)

| Variable | Fuente | Descripción |
|---|---|---|
| **VIX** | CBOE (`VIX_History.csv`) | Volatilidad implícita del S&P 500 a 30 días. Proxy de aversión al riesgo e incertidumbre financiera global. Nota: entra en la construcción del GaR. |
| **US HY OAS** (`US_HY_spread`) | ICE BofA — FRED `BAMLH0A0HYM2` | Option-adjusted spread del índice US High Yield. Prima de riesgo de crédito corporativo de EE.UU. (familia *credit spread* de la Tabla A.3). |
| **EM Corporate OAS** | ICE BofA — FRED `BAMLEMCBPIOAS` | OAS del índice EM Corporate Plus. Prima de crédito de la deuda corporativa de mercados emergentes. |
| **SRISK** (World Financials) | NYU Stern V-Lab | Déficit de capital esperado del sistema financiero condicional a un evento sistémico. Agregado mundial; riesgo sistémico (familia MES/leverage de la Tabla A.3). |
| **OFR FSI** | Office of Financial Research (US Treasury) | Índice diario de estrés financiero sistémico con 30+ variables en cinco categorías: crédito, valuación de acciones, financiamiento, activos seguros y volatilidad. |
| **OFR FSI — Emerging markets** | Office of Financial Research | Contribución del bloque de mercados emergentes al OFR FSI global. |

**Signo esperado vs GaR:** negativo (GaR alto = menos riesgo). Verificado: VIX y SRISK
negativos en las 17 economías (`comparacion_gar_publicas.csv`).

---

## Cómo descargar lo que falta (terminal en `1_Codigo`)

```
python comparar_gar_publicas.py --panel Panel --vlab vlab-srisk-all-20260728.csv --download --out .
```

`--download` baja el OFR FSI (total + Emerging Markets) y el EM Corporate OAS de FRED. El US
HY completo está en `SOURCES`; se añade al bloque de descarga si se quiere en la Tabla 1.

## Pendiente

- Correr los Paneles A–C en la **base extendida** (11 países) y añadir las columnas con las
  métricas descargables (OFR, EM_OAS, US HY).
- Volcar las tablas a Markdown/CSV con un script de regresión (sin LaTeX) para pegarlas al
  working paper.
