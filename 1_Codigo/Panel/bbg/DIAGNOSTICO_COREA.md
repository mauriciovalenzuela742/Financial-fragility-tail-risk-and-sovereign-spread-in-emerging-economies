# Diagnóstico — por qué se excluye Corea del Sur del panel Bloomberg

**Fecha:** 2026-08-31. Insumo directo de la sección de datos/limitaciones de la tesis.

## Síntoma

El JLoss de Corea del Sur calculado con datos Bloomberg (motor v8, Merton/KMV) tiene
mediana **24,7** y crece de forma monótona de 4 (2011) a **47 (2023)** — un sistema
bancario esencialmente insolvente según la métrica. Ningún otro país supera una mediana
de 10 (Turquía 4,9; China 3,9; India 6,5; Brasil 3,7).

## Causa

La razón **valor de mercado del patrimonio / punto de incumplimiento** ($E/D^{*}$) de los
bancos coreanos es, en mediana, **0,038**, frente a un rango de **0,13–0,34** en el resto
del panel (el siguiente más bajo es China, 0,070):

| País | $E/D^{*}$ mediana | $\sigma_E$ anual. | PD Merton mediana |
|---|---:|---:|---:|
| **southkorea** | **0,038** | 0,26 | **0,55** |
| china | 0,070 | 0,20 | 0,030 |
| turkey | 0,135 | 0,39 | 0,041 |
| brazil | 0,155 | 0,33 | 0,020 |
| philippines | 0,192 | 0,27 | 0,002 |
| peru | 0,281 | 0,22 | 0,000 |

Por banco (mediana): Woori $E/D^{*}=0{,}026$ (PD 0,97), JB Financial 0,029 (PD 0,87),
DGB 0,030 (PD 0,85), Hana 0,033, BNK 0,034; solo Shinhan (0,055) y KB (0,052) y el recién
listado KakaoBank quedan por debajo de PD 0,25.

No es un error de unidades: el P/B implícito (mktcap / patrimonio contable) es 0,3–0,6,
coherente con el **"Korea discount"** ampliamente documentado — los holdings bancarios
coreanos cotizan de forma persistente muy por debajo del valor libro por razones de
gobernanza corporativa, baja distribución de dividendos y participaciones cruzadas de los
*chaebol*, no por riesgo de solvencia.

## Por qué invalida el JLoss de Corea

El modelo estructural de Merton/KMV supone que un valor de mercado del patrimonio muy
inferior al valor de los activos implícito en la deuda señala incumplimiento inminente.
Cuando el descuento de valoración es **estructural y permanente** —y refleja el retorno
esperado del negocio, no su probabilidad de quiebra— el modelo confunde "el mercado
valora poco esta franquicia" con "el mercado espera que esta franquicia incumpla". Es una
falla conocida de los modelos estructurales de crédito aplicados a franquicias
persistentemente subvaloradas.

## Bulgaria — misma decisión, otra causa

Bulgaria también queda fuera, por una razón distinta: **solo un banco búlgaro cotiza**
(FIBank), de modo que el `JLoss` se construye sobre una única institución (**76/76**
trimestres `below_min_banks`) y arroja una **mediana de 29**, incoherente con un sistema
bancario solvente. No es un artefacto del modelo de Merton como en Corea, sino que la métrica
no es una medida a nivel de país cuando el universo cotizado es un solo banco pequeño. Hungría
(2 bancos, OTP dominante) queda al límite pero su `JLoss` mediano (≈3) es plausible, así que
se conserva con nota de cobertura.

## Decisión

**Corea del Sur y Bulgaria quedan fuera del panel de estimación** (exclusión por insumo no
válido, no por dato faltante). Corea es coherente con la reconstrucción regulatoria previa
(v8), que tampoco la incluía. China ($E/D^{*}=0{,}070$, PD 0,030) queda **dentro** pero se
señala en nota: su PD está algo elevada por el mismo fenómeno en menor grado, sin distorsionar
el JLoss agregado.
