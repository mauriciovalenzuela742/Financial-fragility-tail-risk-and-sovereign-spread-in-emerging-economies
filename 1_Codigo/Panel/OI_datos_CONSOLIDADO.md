# Arista de Organización Industrial × evidencia empírica — síntesis consolidada

*Documento integrador para comité. Une el modelo de OI (competencia bancaria → JLoss → GaR →
EMBI) con los paneles empíricos. Reúne las dos hipótesis firmadas del modelo (Prop. 4): la
complementariedad (H4a) y su amplificación por concentración (H4b), con toda su robustez y sus
límites declarados. Reproducibilidad al final.*

---

## 1. Resumen ejecutivo

El modelo de OI predice que el spread soberano es **multiplicativo** en fragilidad bancaria y
riesgo de cola, y que esa complementariedad **se intensifica con la concentración** del sistema
bancario. Ambas predicciones firmadas tienen respaldo empírico:

- **H4a — complementariedad (β₃>0, equivalente a θ<0 en JLoss×GaR):** es una **regularidad
  robusta** de los datos. El signo aparece en (casi) todas las especificaciones (14/14 en el
  panel LatAm-5; 10/12 en el extendido), sobrevive un test de permutación (*p*≈0,005–0,011) y
  se invierte de forma predecible con la métrica de cola espejada (placebo `prob_neg`).
- **H4b — amplificación por concentración (β₄>0):** se testeó incorporando la concentración
  bancaria (GFDD) y resulta **positiva y robusta a la métrica** — se sostiene en 4 de 5
  proxies (CR3, CR5, índice compuesto y Lerner), con leave-one-country-out positivo en todos.

La honestidad de poder está incorporada: con 5–11 países la magnitud es imprecisa (β₄ no se
identifica con 5 países; con 11 el bootstrap da 74–96 % de probabilidad de signo). La
contribución es la **cadena teoría→medición→evidencia**, no un *p*<0,05 a prueba de balas.

---

## 2. Del modelo a los datos

El cierre del modelo entrega un spread multiplicativo, $S=\lambda\,\eta(g)\,L$, donde $L$ es la
pérdida sistémica (fragilidad) y $\eta(g)$ un multiplicador que crece con la severidad
macro-financiera. De ahí:

$$\frac{\partial S}{\partial L}=\lambda\,\eta(g)\ \Rightarrow\ \frac{\partial EMBI}{\partial JLoss}=\beta_1+\beta_3\,D,\qquad D\equiv -GaR\ge 0.$$

Como $\eta(g)$ crece con la severidad (cola peor = $D$ mayor), el efecto marginal de la
fragilidad **aumenta cuando el riesgo de cola empeora**: eso es exactamente **β₃>0** (o, en
la parametrización con GaR, **θ<0**). La Proposición 4 añade que esta complementariedad es
**mayor donde la banca está más concentrada**, lo que en forma reducida es la triple
interacción con la concentración:

$$EMBI_{i,t}=\alpha_i+\delta_t+\beta_1 JLoss+\beta_2 D+\beta_3\,(JLoss\times D)+\beta_4\,(JLoss\times D\times HHI)+\text{(interac. de orden inferior)}+\gamma'X+\varepsilon_{i,t}.$$

Predicciones firmadas: **β₃>0** (H4a) y **β₄>0** (H4b). Convención de signos: como $D=-GaR$,
el hallazgo previo θ<0 en JLoss×GaR es **idéntico** a β₃>0 en JLoss×D.

*Salvedad conceptual:* JLoss mide la fragilidad **realizada** ($L$), no la *elección* de
riesgo del modelo; el puente empírico vive en la ecuación del spread, que sí es testeable.

---

## 3. H4a — complementariedad (β₃>0 / θ<0): una regularidad empírica

Establecida sin afirmar causalidad, atacando el **signo** desde cuatro ángulos, en las dos
bases (LatAm-5 con controles; extendida de 11 países):

| Ángulo | LatAm-5 (all17) | Extendido (11) |
|---|---|---|
| Menú de especificaciones (θ<0 en…) | **14/14** | **10/12** |
| Placebo `prob_neg` (cola invertida ⇒ debe voltearse) | +1,81 (positivo, ok) | +1,84 (positivo, ok) |
| Placebos no-cola (REER, inflación ⇒ ≈0) | −0,01 / +0,15 | ≈0 |
| Bootstrap de bloques, P(θ<0) | 91 % | 71 % |
| Permutación, *p* 1-cola | **0,005** | **0,011** |

Lectura: el signo no depende de la especificación (pooled, FE país/tiempo/dobles, controles,
primeras diferencias, winsorización, sin-COVID, sin-crisis, cola = ES o skew-t); un test de
permutación rechaza la ausencia de asociación; y el placebo espejado confirma que capta
severidad de cola, no un artefacto mecánico.

*Inferencia con pocos clusters (honestidad):* el *wild cluster bootstrap* muestra que la
significancia bilateral de la magnitud de θ es **frágil** con 5–11 países (p.ej. θ=−0,34 en
all17-M3 pasa de *p* normal 0,006 a *p* wild-boot 0,19). Por eso la afirmación defendible es
sobre el **signo/regularidad**, no sobre una magnitud precisa.

---

## 4. H4b — amplificación por concentración (β₄>0): el test con GFDD

Se incorporó la concentración bancaria de World Bank GFDD y se estimó la triple interacción
(TWFE país+tiempo, SE agrupados por país), en el panel de 11 países (el de 5 no identifica una
triple transversal). La complementariedad **cambia de régimen con la concentración**:
∂²EMBI/∂JLoss∂D pasa de **−119** en baja concentración a **+94** en alta (proxy CR3).

### Robustez a la métrica — cinco proxies

Todos orientados como *"mayor = menos competencia / más concentración"* (⇒ β₄>0 esperado).
Concentración (CR3, CR5) de la API del World Bank; Lerner y Boone de FRED (el WB los
discontinuó en 2014).

| Métrica | Tipo | β₄ | P(β₄>0) | LOO todos>0 |
|---|---|---|---|---|
| CR3 (ratio 3 bancos) | concentración | +721 | 87 % | sí |
| **CR5 (ratio 5 bancos)** | concentración | **+1032** | **96 %** | sí |
| Compuesto (z de CR3+CR5) | concentración | +110 | 93 % | sí |
| Lerner (poder de mercado) | competencia | +746 | 74 % | sí |
| Boone (competencia) | competencia | −171 | 48 % | **no** |

**4 de 5 proxies confirman β₄>0** — y no solo ratios de concentración: también el índice de
**Lerner** (poder de mercado). La más fuerte es **CR5** (P=96 %). El resultado es robusto a
excluir cualquier país (leave-one-country-out) en los cuatro proxies que confirman.

**La excepción — Boone (reportada, no ocultada).** No apoya β₄ (P=48 %) porque su ranking de
países *contradice* al de concentración —Indonesia es "poco competitiva" por Boone pero la
**menos** concentrada por CR3/CR5— y es la medida más ruidosa (elasticidad profit-costo,
discontinuada en 2014). Que el único disidente sea el proxy más problemático es informativo.

---

## 5. Identificación e inferencia

- **Base:** efectos fijos bidireccionales (país y tiempo); regresores clave en la ecuación
  con las interacciones de orden inferior (JLoss×HHI, D×HHI) para que β₄ sea una triple
  genuina.
- **Inferencia:** SE agrupados por país; **wild cluster bootstrap** y **bootstrap de bloques**
  por país (pocos clusters); **permutación** para el signo; **leave-one-country-out**.
- **Por qué β₄ es más creíble que los niveles:** la simultaneidad del *doom loop* sesga sobre
  todo β₁, β₂ (niveles); la **heterogeneidad del efecto según la concentración** —predeterminada
  a nivel país— está mucho menos contaminada. Por eso la inferencia se centra en β₃, β₄.
- **Concentración estructural (no anual):** GFDD tiene quiebres de fuente (Chile −45 pp en
  2015, China ±47/59, Colombia 100→faltantes) por el cambio Bankscope→Orbis. Se usa la
  **mediana por país** (nivel estructural, robusto); β₄>0 se sostiene también con la serie
  anual como robustez.

---

## 6. Limitaciones a declarar ante el comité

1. **Poder muestral.** Con 5 países β₄ no se identifica; con 11 la probabilidad de signo es
   74–96 % (IC amplios). Coincide con el Monte Carlo del diseño (60–70 % de potencia a N=25).
2. **Concentración de nivel (cross-country).** Al usar la mediana por país, β₄ se identifica
   entre países (11 clusters) → poder moderado. HHI es el ratio de 3/5 bancos (CR3/CR5), proxy
   estándar, no el Herfindahl literal.
3. **Lerner/Boone son pre-2014** (discontinuados) y se usan como nivel estructural; México no
   tiene Lerner en FRED (esa columna corre con 10 países).
4. **Descriptivo, no causal.** La cadena se apoya en asociaciones condicionales robustas y en
   la coherencia teoría-datos, no en una identificación causal cerrada.
5. **Ampliar países** exige EMBI/CDS soberano **propietario** (JP Morgan/Bloomberg/Markit); es
   el camino natural para ganar clusters y potencia.

---

## 7. Redacción sugerida (pegar/adaptar)

> "El modelo predice una complementariedad multiplicativa entre fragilidad bancaria y riesgo
> de cola del crecimiento sobre el spread soberano (β₃>0), amplificada por la concentración
> bancaria (β₄>0). La complementariedad es una **regularidad empírica robusta**: aparece en
> (casi) todas las especificaciones y submuestras, sobrevive un test de permutación
> (*p*≈0,005–0,011) y se invierte con la métrica de cola espejada. La amplificación por
> concentración se confirma en un panel de once economías emergentes y es **robusta a la
> medida** —CR3, CR5, un índice compuesto y el índice de Lerner—, con la salvedad honesta de
> que el indicador de Boone, la métrica más ruidosa y de ranking discordante, no la respalda.
> La magnitud es imprecisa por el tamaño muestral, consistente con el análisis de poder del
> diseño; el aporte es la coherencia entre el mecanismo estructural y su huella en los datos."

---

## 8. Reproducibilidad

| Componente | Archivo |
|---|---|
| Núcleo de estimación (real) — β₃, β₄, efecto marginal | `fase5_estimacion_real.py` |
| Robustez multi-métrica de β₄ (5 proxies) | `fase5_robustez_concentracion.py` |
| Robustez del signo de θ / β₃ (menú, placebos, permutación) | `Robustez_del_signo.ipynb`, `sign_core.py` |
| Paneles reales en formato plantilla | `panel_real_final17.csv`, `panel_real_ext11.csv` |
| Concentración/competencia por país (5 proxies) | `concentracion_metrics.csv` |
| Concentración GFDD (serie anual y nivel) | `hhi_gfdd.csv`, `hhi_nivel.csv` |
| Salidas | `fase5_real_resultados.csv`, `fase5_real_amplificacion.png`, `fase5_robustez_concentracion.csv` |

Fuentes: EMBI y GaR/JLoss (cálculo propio del proyecto); concentración CR3/CR5 (World Bank
GFDD, API); Lerner/Boone (FRED, series GFDD discontinuadas, `DDOI04{ISO2}A066NWDB` /
`DDOI05{ISO2}A156NWDB`).
