# Correo a Juan y Pato — resultados con datos Bloomberg, interacción de crisis y robustez

*Borrador. Fecha: septiembre 2026. Adjuntos sugeridos: las 8 figuras de*
*`1_Codigo/Panel/bbg/figuras/eda_*.pdf` (incluye la nueva `eda_08_efecto_marginal_regimen`).*

---

**Asunto:** Avances tesis — interacción de crisis sin botar trimestres, endogeneidad del `Ryr`
revisada, y robustez adicional (bootstrap + IV)

Estimados Juan y Pato:

Va el resumen de lo que hicimos tras la reunión, más lo que quedó pendiente del árbitro. Las
dos indicaciones concretas —revisar la endogeneidad del `Ryr` en el `GaR` y reemplazar el
corte por submuestra por un vector de crisis— están resueltas y con números; abajo el
resultado principal primero, el detalle técnico después.

## 1. La muestra

- **13 economías emergentes** entran a la estimación del mecanismo (EMBI Global Diversified
  de J.P. Morgan + JLoss + GaR disponibles a la vez): Brasil, Chile, China, Colombia, India,
  Indonesia, Malasia, México, Perú, Filipinas, Polonia, Sudáfrica y Turquía.
- Quedan fuera de la estimación —no por falta de dato, sino porque el índice EMBI Global
  Diversified no las cubre— Argentina, Egipto, Pakistán y Rusia.
- **Rusia** ya está en el panel que estima el `GaR` (18 países en el *pool* de la regresión
  cuantílica desde la re-ejecución de septiembre) y aporta 10 trimestres a la muestra de
  robustez con CDS (2013–2015); lo único que le falta es el EMBI, no el `GaR`.
- **Argentina**: sigue pendiente el bono a 5 años vía IES. Es lo único que falta bajar de
  Bloomberg antes de poder incorporarla.

## 2. Resultado principal — la interacción de crisis, sin botar trimestres

**Como pidieron, dejamos de botar los trimestres de crisis y en su lugar interactuamos la
complementariedad con un vector de crisis, manteniendo toda la muestra.**

Especificación: `EMBI = FE_país + FE_tiempo + β₁·JLoss + β₂·D + β₃·(JLoss×D) +
β₄·(JLoss×D×Crisis) + β₅·(JLoss×Crisis) + β₆·(D×Crisis) + controles`, con `D ≡ −GaR`.
`β₃` = complementariedad fuera de crisis; `β₃+β₄` = en crisis (la predicción, si el
mecanismo es real, es que se cancelen bajo respaldo oficial).

Fuimos un paso más allá de un solo vector: separamos **Backstop** (crisis financiera global
2008–09 + pandemia 2020–21, con líneas de swap de la Fed, financiamiento del FMI, compras del
banco central local) de **EMstress** (estrés emergente 2015–16, sin ese respaldo). Es un test
de falsación más nítido que un corte temporal simple.

| Spec (efectos fijos país+tiempo, +6 controles) | Coef. | Significancia |
|---|---|---|
| β₃ — complementariedad fuera de crisis | **+0,81** | p = 0,051 |
| β₃+β₄ — bajo **Backstop** (GFC+COVID) | **≈ 0** (−0,03) | Wald no rechaza (p = 0,77) → **se anula** |
| β₃+β₄ — bajo **EMstress** (2015–16) | **≈ +1,0** | Wald rechaza (p < 0,001) → **sobrevive** |

Lectura: la complementariedad es real y significativa fuera de crisis —el nulo de la muestra
completa (β₃ ≈ +0,16–0,19 según la versión del `GaR`, no significativo) es un promedio de
regímenes—, se apaga exactamente donde hay un respaldo oficial que desacopla el canal, y
sobrevive donde no lo hay. Reemplaza al corte por submuestra como resultado principal de la
dimensión temporal; el corte por submuestra (que daba β₃ ≈ +1,2 excluyendo GFC+COVID) queda
como robustez secundaria, y da la misma lectura cualitativa.

Corrido y verificado **idéntico** en Python (`linearmodels`, errores Driscoll–Kraay) y en R
(`plm` + `vcovSCC` + `car::linearHypothesis`), y replicado tanto en el notebook Jupyter como
en el `.Rmd`, como pidió el coguía.

## 3. Endogeneidad del `Ryr` respecto del EMBI — la otra indicación de la reunión

Preocupación: el `Ryr` (rendimiento soberano 10Y) alimenta el FCI que alimenta el `GaR`, y la
variable dependiente es un spread soberano (EMBI) — ¿hay circularidad mecánica?

En vez de solo argumentarlo, lo comprobamos **reconstruyendo el `GaR` sin el único componente
del FCI con forma de *spread*** (`CDIFF`, el diferencial de yields reales vs. EE. UU.) y
re-corriendo todo:

- Diagnóstico por etapas: la correlación con el EMBI se **atenúa de 0,68** (spread crudo
  `Ryr − Ryr_US`) **a 0,07** (la contribución de `CDIFF` al FCI) por la propia transformación
  (diferenciación + piso móvil + estandarización expansiva).
- Reconstrucción real (no solo el diagnóstico): `corr(GaR_sin_CDIFF, GaR_con_CDIFF) = 0,985`.
  Re-estimando todo con el `GaR` sin `CDIFF`, β₃ pasa de +0,19 a +0,23 en la muestra completa
  y de +0,84 a +0,86 fuera de crisis; la cancelación bajo Backstop y la supervivencia bajo
  EMstress se mantienen intactas.
- El EMBI y el CDS **nunca** entran al cómputo del FCI ni del `GaR` (verificado en el código
  del motor).

Conclusión: la preocupación es conceptualmente legítima pero cuantitativamente inmaterial.

## 4. Robustez adicional (pendientes del árbitro senior)

- **Bootstrap de regresor generado.** Corrida en el clúster (NLHPC, 500 réplicas, fidelidad
  completa): re-estima la regresión cuantílica del `GaR` completa en cada réplica —no solo
  perturba el número— y propaga esa incertidumbre a β₃. El error estándar combinado (segunda
  etapa + primera etapa, en cuadratura) crece apenas 2–15 % según la fila, y **ningún
  resultado de la Sección 2 cambia de categoría**. La inferencia que ya reportábamos no
  subestimaba de forma material la incertidumbre de tratar al `GaR` como dato.
- **IV reforzado.** Intentamos un tercer instrumento más exógeno que los dos que ya
  teníamos (liquidez *on/off-run*, dólar amplio BIS): un choque de términos de intercambio
  por *commodities*, con participaciones de exportación **pre-muestra** (1998–2003, Banco
  Mundial) — la exposición no se estima regresando `JLoss` contra el choque, viene de datos
  comerciales externos. Resultado: primera etapa prácticamente nula para `JLoss` (aunque sí
  co-mueve con el EMBI directamente) — el ciclo de *commodities* mueve el riesgo soberano
  agregado, no la fragilidad *bancaria* específica. No cierra la identificación; lo dejamos
  documentado como intento honesto y mantenemos el peso en MCO + proyecciones locales.
- **Posicionamiento vs. Chari et al. (2024).** Revisado: la distinción ya está afilada en la
  introducción y en la sección de brecha de literatura —ellos interactúan `JLoss` con
  factores **globales y exógenos** (VIX, Tesoro, HY); este capítulo lo hace con una
  vulnerabilidad **doméstica y endógena** (`GaR`) que la propia fragilidad bancaria
  contribuye a generar (Canal I del modelo teórico) y que retroalimenta el costo fiscal del
  rescate.

## 5. Orientación del GaR (sin cambios desde el correo anterior)

Seguimos reportando todo sobre **D = −GaR** ("riesgo de cola": D más alto = peor), de modo
que **β₃ = coef(JLoss × D)** es positivo cuando hay amplificación. Equivalencia exacta con
θ (β₃ = −θ): ningún número cambia, solo el signo con que se presenta.

## 6. Qué agrega el GaR respecto al paper original (Chari et al. 2024)

- El **canal de nivel** del paper se replica: JLoss sobre el spread sale positivo,
  significativo y estable de "JLoss solo" a la especificación completa (β₁ ≈ +2,8 pb por
  unidad, t ≈ 2,7).
- Lo que este trabajo **añade** es β₃: la condicionalidad del efecto de la fragilidad según
  el riesgo de cola del crecimiento, y ahora también *cuándo* aparece (fuera de episodios con
  respaldo oficial).
- *(Sigue pendiente para cerrar esta comparación: el coeficiente exacto de JLoss de la tabla
  de nivel de ustedes — ¿me pasan el número / la tabla?)*

## 7. Figuras adjuntas

1. Superficie de complementariedad con dimensión temporal.
2. Efecto marginal ∂EMBI/∂JLoss según D, completa vs. sin crisis.
3. Binscatter de la pendiente JLoss→EMBI por tercil de D.
4. Prima de amplificación por país.
5. Leave-one-country-out de β₃.
6. Cobertura del panel.
7. **Nueva:** efecto marginal por régimen (fuera de crisis / Backstop / EMstress) —
   `eda_08_efecto_marginal_regimen`, la versión gráfica de la Sección 2 de arriba.

## 8. Pendientes

- Bajar el bono argentino a 5 años (IES) e incorporar Argentina — junto con Rusia (que ya
  tiene `GaR`), se actualizará el panel en una sola pasada cuando esté lista.
- Cerrar la comparación de nivel con la cifra de Chari et al. (2024) — necesito el número.
- El resto de lo pedido en la reunión y por el árbitro (interacción de crisis, `Ryr`,
  bootstrap, IV, posicionamiento) ya está resuelto y trazado en el repositorio.

Quedo atento a comentarios.

Saludos,
Mauricio

---

### Trazabilidad de los números citados

| Cifra | Fuente |
|---|---|
| β₃ fuera de crisis +0,81 (p=0,051); Backstop ≈0 (p=0,77); EMstress ≈+1,0 (p<0,001) | `bbg/NUMEROS_CANONICOS_BBG.md` §"Interacción de crisis — SIN botar trimestres" |
| Endogeneidad `Ryr`: corr. 0,68→0,07; β₃ +0,19→+0,23 / +0,84→+0,86 | `bbg/NUMEROS_CANONICOS_BBG.md` §"Endogeneidad `Ryr` ↔ EMBI" |
| Bootstrap C1 (500 réplicas NLHPC, SE combinado) | `bbg/NUMEROS_CANONICOS_BBG.md` §"Bootstrap de regresor generado (C1)" |
| IV reforzado (commodity ToT, F≈0,03) | `bbg/NUMEROS_CANONICOS_BBG.md` §"IV reforzado — commodity ToT shift-share (C2)" |
| β₁(JLoss) ≈ +2,8 pb, t ≈ 2,7 | `bbg/NUMEROS_CANONICOS_BBG.md` §"Resultado central" |
| Rusia en el pool GaR | `bbg/NUMEROS_CANONICOS_BBG.md` §"RE-EJECUCIÓN 2026-09-06" |
| Figuras | `1_Codigo/Panel/bbg/EDA_Panel_Final_bbg.ipynb` → `bbg/figuras/eda_*.pdf` |
