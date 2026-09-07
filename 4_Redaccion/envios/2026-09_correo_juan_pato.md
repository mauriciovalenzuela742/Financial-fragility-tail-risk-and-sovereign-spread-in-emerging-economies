# Correo a Juan y Pato — resultados con datos Bloomberg y valor agregado del GaR

*Borrador. Fecha: septiembre 2026. Adjuntos sugeridos: las 7 figuras de*
*`1_Codigo/Panel/bbg/figuras/eda_*.pdf` + la tabla comparativa de `Regresiones_panel_extended_v3`.*

---

**Asunto:** Avances tesis — panel Bloomberg listo, resultado principal y qué agrega el GaR

Estimados Juan y Pato:

Buenas noticias: ya tengo el panel armado con datos Bloomberg y reproducible de punta a
punta. Puedo re-descargar y re-correr todo cuando haga falta. Abajo va el resumen ordenado,
con la interpretación simple primero y el detalle técnico después.

## 1. La muestra

- **13 economías emergentes** entran a la estimación del mecanismo (EMBI Global Diversified
  de J.P. Morgan + JLoss + GaR disponibles a la vez): Brasil, Chile, China, Colombia, India,
  Indonesia, Malasia, México, Perú, Filipinas, Polonia, Sudáfrica y Turquía.
- Quedan fuera de la estimación —no por falta de dato, sino porque el índice EMBI Global
  Diversified no las cubre— Argentina, Egipto, Pakistán y Rusia.
- **Rusia ya entró** al panel cuantílico que estima el GaR (re-ejecución en el clúster,
  6 de septiembre) y aporta 10 trimestres a la muestra de robustez con CDS (2013–2015).
- **Argentina**: como conversamos, uso el bono a 5 años vía IES. Es lo único que falta bajar;
  lo dejo listo en la próxima sesión de Bloomberg.

## 2. Resultado principal (interpretación simple)

**El efecto cruzado fragilidad-bancaria × riesgo-de-cola amplifica el spread soberano, pero
solo fuera de los trimestres de crisis.**

En la crisis financiera global y en la pandemia, el soberano suele estar respaldado —líneas
de swap de la Fed, financiamiento del FMI, compras del banco central local—, y ese respaldo
desacopla el mecanismo. Cuando se sacan esos trimestres, la complementariedad aparece nítida:
una mala perspectiva de crecimiento hace que la fragilidad bancaria pese mucho más sobre el
spread, precisamente donde no hay una red supranacional que amortigüe.

En números (especificación de referencia, efectos fijos de país y tiempo):

| Muestra | Coef. de la interacción (JLoss × D) | Significancia |
|---|---|---|
| Completa | ≈ +0,14 | no significativo |
| Sin crisis (GFC + COVID) | ≈ +1,2 | p < 0,001 |
| Sin crisis **y** núcleo de 11 EM de financiamiento externo | ≈ +0,9 | p ≈ 0,003 |

## 3. Orientación del GaR corregida

Tenían razón: el GaR venía de la cola izquierda (cuantil 5 %), así que "más negativo = peor"
y el coeficiente de la interacción salía negativo, incómodo de leer. Ahora reporto todo sobre

  **D = −GaR**  ("riesgo de cola": D más alto = peor),

de modo que el coeficiente de interés, **β₃ = coef(JLoss × D)**, es **positivo cuando hay
amplificación** y se lee directo: *"más riesgo de cola ⇒ mayor efecto de la fragilidad sobre
el spread"*. La equivalencia con la parametrización anterior es exacta, β₃ = −θ, así que
ningún número cambia, solo el signo con que se presenta. (Uso D = −GaR y no |GaR| porque
cerca de la mitad de las observaciones tienen GaR > 0; en la cola izquierda, que es la
región relevante, D coincide con |GaR|.)

## 4. Qué agrega el GaR respecto al paper original (Chari et al. 2024)

- El **canal de nivel** del paper se replica: el coeficiente de JLoss sobre el spread es
  positivo, significativo y de una magnitud comparable a la publicada — y **no se mueve**
  cuando agrego el GaR y la interacción (β₁(JLoss) ≈ +2,8 pb por unidad, estable de "JLoss
  solo" a la especificación completa).
- Lo que este trabajo **añade** es β₃: la condicionalidad del efecto de la fragilidad según
  el riesgo de cola del crecimiento. Es el término nuevo, no un cambio en el canal ya
  conocido.
- *(Para cerrar esta tabla necesito el coeficiente exacto de JLoss de la tabla de nivel de
  ustedes — ¿me pasan el número / la tabla?)*

## 5. Figuras adjuntas

1. **Superficie de complementariedad con dimensión temporal** — las iso-curvas del spread
   predicho se doblan hacia la esquina "alta fragilidad + cola severa"; los puntos están
   coloreados por año (recientes oscuros, antiguos claros), como sugirió Juan.
2. **Efecto marginal ∂EMBI/∂JLoss según D**, completa vs. sin crisis — la pendiente sube con
   el riesgo de cola solo fuera de crisis.
3. Binscatter de la pendiente JLoss→EMBI por tercil de D.
4. Prima de amplificación por país.
5. Leave-one-country-out de β₃ (el signo no lo arrastra un solo país).
6. Cobertura del panel.

## 6. Pendientes

- Bajar el bono argentino a 5 años (IES) e incorporar Argentina.
- Reestructurar el Capítulo 2 a la convención D = −GaR (β₃ > 0), hoy escrito con θ < 0.
- Cerrar la comparación de nivel con la cifra de Chari et al. (2024).

Quedo atento a comentarios.

Saludos,
Mauricio

---

### Trazabilidad de los números citados

| Cifra | Fuente |
|---|---|
| β₃ completa ≈ +0,14 (n.s.) / sin crisis ≈ +1,2 (p<0,001) | `bbg/NUMEROS_CANONICOS_BBG.md` §"Batería", M4/PT (θ = −0,136 / −1,190) |
| β₃ núcleo 11 EM y sin crisis ≈ +0,9 (p≈0,003) | `bbg/NUMEROS_CANONICOS_BBG.md` (θ = −0,938, N=405) |
| β₁(JLoss) ≈ +2,8 pb, t ≈ 2,7 | `bbg/NUMEROS_CANONICOS_BBG.md` §"Resultado central" |
| Rusia en el pool GaR (6-sep) | `bbg/NUMEROS_CANONICOS_BBG.md` §"RE-EJECUCIÓN 2026-09-06" |
| Figuras | `1_Codigo/Panel/bbg/EDA_Panel_Final_bbg.ipynb` → `bbg/figuras/eda_*.pdf` |
