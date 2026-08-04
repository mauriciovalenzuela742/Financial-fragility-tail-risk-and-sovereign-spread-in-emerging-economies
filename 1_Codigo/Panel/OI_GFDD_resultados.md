# Unir la arista OI con los datos: test de la amplificación por concentración (GFDD)

*Acompaña a `fase5_estimacion_real.py`, `panel_real_final17.csv`, `panel_real_ext11.csv`,
`hhi_gfdd.csv` y `fase5_real_amplificacion.png`. Pregunta: ¿sirve GFDD para testear la
Proposición 4 / H4b (β₄>0, la concentración amplifica la complementariedad)?*

## Veredicto: sí sirve, con matices honestos

Se bajó de **World Bank GFDD** la concentración bancaria (GFDD.OI.01, ratio de los 3 bancos
mayores) 2006–2021 para los 11 países, y se estimó la ecuación de la Fase V con la triple
interacción sobre los **paneles reales** (no simulados).

**Resultado central (panel extendido, 11 países, HHI estructural limpio):**

| Objeto | Valor | Lectura |
|---|---|---|
| β₄ (JLoss×D×HHI) | **+721, t=2.98** | H4b **confirmada**: la concentración amplifica la complementariedad |
| Leave-one-country-out | **+294 a +993 (los 11 positivos)** | no lo arrastra ningún país |
| Bootstrap de bloques | **P(β₄>0)=87%**, IC90 [−425, +2142] | signo probable; IC amplio = poder moderado con 11 países |
| ∂²EMBI/∂JLoss∂D | baja conc **−119** → alta conc **+94** | la complementariedad *cambia de régimen* con la concentración |

Es decir: en bancos poco concentrados la coincidencia de fragilidad y cola apenas mueve el
spread; en bancos muy concentrados la amplifica fuertemente — exactamente la predicción del
modelo de OI. Se sostiene con la HHI estructural (limpia, t=2.98) y con la anual (t=4.47).

## Matices que hay que declarar

1. **En el panel de 5 países β₄ NO se identifica.** Con solo 5 economías no hay variación
   transversal suficiente para una triple interacción: la HHI estructural da signo negativo
   no significativo (P=36%) y la anual da un positivo espurio (contaminado por quiebres). La
   arista OI **necesita el panel amplio**; H4b es un resultado del extendido, no del núcleo.
2. **GFDD tiene quiebres de fuente.** La serie anual salta artificialmente (Chile −45pp en
   2015, China ±47/59, Colombia 100→faltantes) por el cambio de base subyacente. Por eso el
   resultado principal usa la **concentración estructural por país (mediana, robusta)**, no la
   variación anual. Que β₄ sea positivo con *ambas* versiones es tranquilizador.
3. **HHI es de nivel (cross-country).** Al usar la concentración estructural, β₄ se identifica
   entre países (11 clusters) → **poder moderado** e IC amplio, justo lo que anticipaba tu
   Monte Carlo de la Fase V (60–70% de potencia con N=25; menos aquí). No es un *p*<0.05 a
   prueba de balas: es evidencia **de apoyo con poder limitado**.
4. **GFDD.OI.01 es el ratio de 3 bancos (CR3), no el Herfindahl literal.** Es un proxy estándar
   de concentración; conviene nombrarlo así en la tesis.

## Cómo encaja con lo ya hecho (las dos aristas unidas)

- **H4a (complementariedad, β₃>0 ⇔ nuestro θ<0):** ya establecida de forma robusta en el
  trabajo previo (14/14 y 10/12 especificaciones; permutación p≈0.005–0.010).
- **H4b (amplificación por concentración, β₄>0):** ahora **testeada y apoyada** con GFDD en el
  panel de 11 países. Es la predicción que distingue tu modelo de OI de MMR.

Juntas, las dos hipótesis firmadas del modelo tienen respaldo empírico en los datos que ya
teníamos + GFDD, con la honestidad de poder que el propio plan pide reportar.

## Robustez a la métrica — CINCO proxies (concentración + competencia)

Para no depender de un solo proxy, se re-estimó β₄ en el panel de 11 países con **cinco
medidas estructurales** (mediana por país), todas orientadas como *"mayor = menos competencia
/ más concentración"* (⇒ β₄>0 esperado). Concentración (CR3, CR5) de la API del World Bank;
Lerner y Boone de **FRED** (el WB los discontinuó en 2014 y los quitó de la API/Excel;
`DDOI04{ISO2}A066NWDB` y `DDOI05{ISO2}A156NWDB`).

| Métrica | Tipo | β₄ | P(β₄>0) | LOO todos>0 |
|---|---|---|---|---|
| CR3 (3 bancos) | concentración | +721 | 87% | sí |
| **CR5 (5 bancos)** | concentración | **+1032** | **96%** | sí |
| Compuesto (z de CR3+CR5) | concentración | +110 | 93% | sí |
| Lerner (poder de mercado) | competencia | +746 | 74% | sí |
| Boone | competencia | −171 | 48% | **no** |

**4 de 5 proxies confirman la amplificación** (β₄>0), incluyendo el índice de **Lerner**
(poder de mercado) — no solo ratios de concentración. La más fuerte sigue siendo **CR5**
(P=96%). El resultado no es artefacto de una medida particular.

**La excepción, con honestidad — Boone.** El indicador de Boone **no** apoya β₄ (P=48%). La
razón es transparente: su ranking de países *contradice* al de concentración —por ejemplo,
Indonesia aparece como la "menos competitiva" por Boone pero es la **menos** concentrada por
CR3/CR5— y Boone es la medida más ruidosa (elasticidad profit-costo, discontinuada en 2014).
Que 4/5 proxies coincidan y el disidente sea el más problemático es, en sí, informativo; hay
que reportarlo, no ocultarlo.

**Sobre "más países":** ampliar la muestra exige EMBI/CDS soberano **propietario** (JP
Morgan/Bloomberg/Markit), no bajable por API abierta. Ese sigue siendo el camino para ganar
clusters; la robustez que sí pudimos sumar es la de **múltiples proxies** (CR3, CR5,
compuesto, Lerner), consistente.

## Recomendación

Reportar β₄ como **evidencia de apoyo a la Prop. 4 con poder moderado**, sobre el panel de 11
países, con la concentración estructural GFDD (y la anual como robustez). Para fortalecerlo:
(i) conseguir EMBI/CDS para más de las 17 economías con GaR estimado (más clusters); (ii)
sumar Lerner/Boone de GFDD como proxies alternativos de competencia; (iii) si se quiere
variación temporal creíble de HHI, buscar concentración de bancos centrales nacionales (sin
los quiebres de GFDD).

## Reproducir

```
python fase5_estimacion_real.py
```
Genera `fase5_real_resultados.csv` (β₃, β₄, efecto marginal, P(β₄>0) por panel y versión de
HHI) y `fase5_real_amplificacion.png` (la complementariedad creciente en la concentración).
Los paneles `panel_real_*.csv` están en el formato de `panel_template.csv`, listos también
para `fase5_estimacion.py` original.
