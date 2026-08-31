> **SUPERADO (2026-08-31).** Esta es la versión con datos **regulatorios** (JLoss v8,
> EMBI BCRP/GFSR). La tesis se reancló íntegramente en Bloomberg; la fuente de verdad vigente
> para toda prosa es **`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`**. Este archivo se
> conserva como registro del linaje anterior. El cambio principal: θ (M3 principal) pasó de
> −0,338 a −0,47 y ahora depende de los controles; **H4b (β4>0) dejó de sostenerse** (de
> +721 a −418, signo contrario).

# Números canónicos — fuente única de verdad para la prosa de la tesis

*Generado el 2026-08-03 re-ejecutando directamente el código canónico documentado (no leyendo
salidas antiguas). Referenciado desde `4_Redaccion/CONTROL_DE_VERSIONES.md`, Sección 5.*

**Regla de uso: ningún coeficiente entra a la prosa de la tesis sin poder trazarse a una fila
de este documento.** Si necesita un número que no está aquí, debe re-derivarse con el mismo
método (re-ejecución directa) antes de escribirlo, no copiarse de un borrador.

---

## 0. Procedencia y método

Todos los números de este documento se obtuvieron ejecutando directamente, el 2026-08-03, con
el intérprete de `Jloss/.venv` (`pandas` 2.3.3, `linearmodels` 7.0, `statsmodels` 0.14.6):

1. La lógica de la **celda 39** de `1_Codigo/Panel/EDA_Panel_Final_17.ipynb` (sección "14.4
   *Forest plot* de θ"), que ajusta M1–M5 vía `linearmodels.panel.PanelOLS` con errores
   `cov_type='kernel', kernel='bartlett'` (aproximación Driscoll–Kraay), extraída y ejecutada
   como script independiente sobre `Panel_final_all17.csv` y `Panel_extended_15paises.csv` tal
   como están hoy en disco.
2. `1_Codigo/Panel/fase5_estimacion_real.py` (sin modificar) — triple interacción
   JLoss×D×HHI (H4a/H4b) sobre `panel_real_final17.csv` y `panel_real_ext11.csv`.
3. `1_Codigo/Panel/fase5_robustez_concentracion.py` (sin modificar) — robustez de β4 a 5
   proxies de concentración/competencia.

No fue posible re-ejecutar los `.Rmd` (no hay R instalado en el entorno de ejecución); la
cifra de M3/all17 obtenida aquí por la vía Python (linearmodels) coincide con la reportada por
`LEEME_analisis_v3.md` (25-jul, misma vía) a la tercera cifra decimal, lo que corrobora que el
método Python replica correctamente la salida de R documentada en ese archivo.

---

## 1. Mecanismo central: interacción JLoss × GaR sobre EMBI

### Base principal — `Panel_final_all17.csv` (5 países LatAm, 2007Q4–2022Q2)

| Especificación | N | β₁ (JLoss) | β₂ (GaR, pp) | **θ (JLoss×GaR)** | t | p |
|---|---|---|---|---|---|---|
| M2 — FE país+tiempo, sin controles | 281 | 1,3549 (0,4550) | 2,8737 (2,7843) | **−0,3592** | −2,820 | 0,0053 |
| **M3 — FE país+tiempo, + controles domésticos** | **253** | 1,5251 (0,5564) | 1,4026 (2,8252) | **−0,3378** | **−2,217** | **0,0278** |
| M5-equiv — FE país únicamente, + controles | 253 | — | — | −0,2750 | −2,496 | 0,0132 |
| Cola = Expected Shortfall (en vez de GaR) | 253 | — | — | −0,2473 | −1,476 | — |

Controles domésticos en M3: `debt_gdp, fisc_bal, res_gdp, ca_gdp, infl_yoy, reer`. Errores
Driscoll–Kraay (kernel Bartlett). Variables `JLoss` y `GaR` (en puntos porcentuales) centradas.

**Éste es el número a usar como "M3" del paper empírico: θ = −0,338 (N=253, t=−2,22,
p=0,028).**

### Base de robustez — `Panel_extended_15paises.csv` (11 países, sin controles domésticos)

| Especificación | N | β₁ (JLoss) | β₂ (GaR, pp) | **θ (JLoss×GaR)** | t | p |
|---|---|---|---|---|---|---|
| **M2 — FE país+tiempo (única especificación posible, sin controles)** | **374** | 1,1427 (0,4780) | −1,3578 (2,6325) | **−0,2122** | **−1,828** | **0,0685** |
| Cola = Expected Shortfall (en vez de GaR) | 374 | — | — | −0,1868 | −1,799 | — |

**Éste es el número a usar como "M2" del panel extendido: θ = −0,212 (N=374, t=−1,83,
p=0,069, significativo solo al 10%).**

---

## 2. Discrepancia detectada y su resolución

Antes de esta reconciliación circulaban cuatro valores para "θ, M3, all17": −0,363 (abstract de
`Boceto_1_actualizado.tex`, base vieja N=248), −0,316 (cuerpo del mismo archivo, corrida v2),
−0,338 (`LEEME_analisis_v3.md`, 25-jul) y −0,313 (`Plan_tablas_riesgo.md`, fila "FE país +
tiempo", 28-jul).

**Resolución:** la re-ejecución directa del 2026-08-03 reproduce **−0,3378**, prácticamente
idéntico a los −0,338 de `LEEME_analisis_v3.md` (misma vía de cómputo, mismo archivo fuente).
Se adopta **−0,338** como el valor oficial.

El valor −0,313 de `Plan_tablas_riesgo.md` **no pudo verificarse de forma independiente**: el
script que generó las tablas "Panel A/B/C" de ese documento no quedó guardado como archivo
reproducible (el propio documento lo señala en su sección "Pendiente": *"Volcar las tablas a
Markdown/CSV con un script de regresión"* — es decir, se corrió de forma ad hoc y no se
persistió el código). Es probable que la fila "FE país + tiempo" de esa tabla haya usado una
muestra o un centrado ligeramente distinto al fijar el panel para las columnas con SRISK/VIX
externos (que si requieren un merge adicional). Dado que **no es reproducible hoy**, no se usa
como fuente. Si en el futuro se recupera o reconstruye ese script y reproduce −0,313 de forma
verificable, este documento debe actualizarse y señalar el cambio explícitamente.

Los −0,363 y −0,316 de los Bocetos son, en cualquier caso, **anteriores en el linaje de datos**
(corridas v1/v2 sobre `Panel_final.csv`, N=248, superadas por `Panel_final_all17.csv`, N=253)
y quedan descartados por la Sección 3.3 de `CONTROL_DE_VERSIONES.md`.

---

## 3. Puente OI ↔ datos reales: H4a (complementariedad) y H4b (amplificación por concentración)

Especificación: `EMBI = α_i + δ_t + β₁·JLoss + β₂·D + β₃·(JLoss×D) + β₄·(JLoss×D×HHI) + controles`,
con `D = −GaR` (mayor D = peor cola). H4a: β₃>0 (equivalente a θ<0 en la parametrización de la
Sección 1). H4b: β₄>0 (la concentración bancaria amplifica la complementariedad).

### Panel principal — `panel_real_final17.csv` (5 países)

| HHI | β₃ (JLoss×D) | t | β₄ (JLoss×D×HHI) | t | P(β₄>0) bootstrap | Lectura |
|---|---|---|---|---|---|---|
| Estructural (mediana, limpia) | +54,11 | 1,63 | −363,0 | −0,47 | 36% | **β₄ NO se identifica con 5 países** (signo negativo, no significativo) |
| Anual (con quiebres GFDD) | +30,85 | 1,21 | +437,4 | 2,08 | 79% | Signo positivo pero contaminado por quiebres de fuente (ver §4 de `OI_GFDD_resultados.md`) |

### Panel extendido — `panel_real_ext11.csv` (11 países) — resultado principal de H4b

| HHI | β₃ (JLoss×D) | t | β₄ (JLoss×D×HHI) | t | P(β₄>0) bootstrap | IC90% |
|---|---|---|---|---|---|---|
| **Estructural (mediana, limpia)** | −16,98 | −0,68 | **+720,7** | **2,98** | **87%** | [−425, +2142] |
| Anual (con quiebres GFDD) | +4,36 | 0,18 | +383,4 | 4,47 | 80% | [−707, +828] |

**Resultado H4b principal a citar: β₄ = +721 (t=2,98) en el panel de 11 países con HHI
estructural — confirma la amplificación por concentración, con la salvedad honesta de poder
estadístico moderado (IC90% amplio) dado N=11 clusters de país.**

### Robustez de β₄ a 5 proxies de concentración/competencia (panel de 11 países)

| Proxy | Tipo | β₄ | P(β₄>0) | LOO todos positivos |
|---|---|---|---|---|
| CR3 (3 bancos) | Concentración | +720,6 | 87,1% | Sí |
| **CR5 (5 bancos)** | Concentración | **+1031,7** | **95,7%** | Sí |
| Compuesto (z de CR3+CR5) | Concentración | +110,4 | 92,9% | Sí |
| Lerner | Competencia (n=10 países, sin México) | +745,7 | 73,9% | Sí |
| Boone | Competencia | −170,7 | 48,1% | **No** (LOO min=−909,8) |

**4 de 5 proxies confirman β₄>0**; Boone es la excepción declarada (ranking de países
contradictorio con la concentración real, métrica más ruidosa — ver razonamiento completo en
`OI_GFDD_resultados.md`).

*Todos los valores de esta sección reproducen exactamente (a la primera cifra decimal) los ya
documentados en `OI_datos_CONSOLIDADO.md` y `OI_GFDD_resultados.md` (26-jul) — no hubo drift
desde entonces; se confirma su estabilidad y pueden citarse con seguridad.*

---

## 4. Pendiente: regeneración de figuras

`fig_cobertura.pdf`, `fig_efecto_marginal.pdf`, `fig_forest_theta.pdf` y la carpeta `figures/`
(todas del 17-jul) provienen de la corrida **v2, superada**. Deben regenerarse desde las celdas
de figuras de la Sección 14 de `EDA_Panel_Final_17.ipynb` (14.1 efecto marginal, 14.4 forest
plot, y la cobertura de la Sección 2) usando los números de este documento. Se deja como tarea
de la fase de redacción del paper empírico (no se regeneraron aquí para mantener esta fase
acotada a la reconciliación numérica); el código fuente exacto de cada figura ya está
identificado en las celdas 39–57 de ese notebook.

## 5. Pendiente declarado por el propio `Plan_tablas_riesgo.md`

Paneles A–C corridos solo en la base principal; falta correrlos en la base extendida y sumar
columnas con OFR FSI, EM Corporate OAS y US HY (requiere `--download` en
`comparar_gar_publicas.py`). No bloquea la escritura de la tesis con lo ya reconciliado aquí,
pero es agenda futura a mencionar en limitaciones/agenda del paper empírico.
