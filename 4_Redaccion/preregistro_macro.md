---
title: "Preregistro 2: mejoras macroeconómicas (deuda, moneda de la deuda, horizonte del riesgo de cola)"
subtitle: "Escrito el 21 de octubre de 2026, antes de descargar los datos nuevos y antes de estimar"
---

*Este documento fija las hipótesis de las mejoras M3, M4 y M6 de `4_Redaccion/evaluacion_macroeconomica.md`.
El commit que lo contiene precede en el historial a los de `p44_datos_macro.py`, `gar_insample_horizonte.py` y
`p45_macro_preregistrada.py`. Antes de escribirlo solo se verificó que existen los indicadores (QPSD:
deuda del gobierno general en moneda extranjera y local, en % del PIB) y que el sitio de la clasificación
de regímenes cambiarios responde; no se miró ningún valor. Todo son asociaciones, no causalidad.*

**Declaración de lo que ya se vio:**
- R-H3 del preregistro 1 (deuda × riesgo de cola: +0,011, firme);
- el GaR a un trimestre no aparece en los cambios ni mejora el pronóstico;
- el efecto directo de la fragilidad neto del canal fiscal es ≈ 0.

## 1. Base

La misma del preregistro 1: la especificación principal (ln EMBI_t sobre ln JLoss_{t−1}, D_{t−1} y su
producto, centrados), con efectos fijos de país y de tiempo. Inferencia con wild cluster bootstrap por
país (Webb, 999) y Driscoll–Kraay como referencia. Moderadores en t−4, estandarizados.

## 2. Datos

| Variable | Fuente | Regla |
|---|---|---|
| DEBT: deuda del gobierno general, % del PIB | QPSD (ya descargada, `p41`) | Igual que en el preregistro 1 |
| FXDEBT y LCDEBT: deuda del gobierno general en moneda extranjera y en moneda local, % del PIB | QPSD (DP.DOD.DECF.CR.GG.Z1 y DP.DOD.DECN.CR.GG.Z1) | Sin sustituto: la economía queda fuera de R2-H2 y se declara |
| GaR4: cuantil 5 % del crecimiento **promedio de los cuatro trimestres siguientes** | Motor de GaR existente, versión dentro de la muestra (la misma del preregistro 1), con esa variable dependiente | D4 = −GaR4, en pp |
| Régimen cambiario (secundaria) | Clasificación gruesa de Ilzetzki, Reinhart y Rogoff; "flexible" = categorías 3 y 4 | Si no se puede descargar, la prueba no se hace y se declara |

## 3. Hipótesis (familia primaria)

- **R2-H1 (doom loop, M6).** Se agregan DEBT_{t−4} y ln JLoss_{t−1} × DEBT_{t−4}. Predicción: un
  coeficiente **positivo**. El pasivo contingente bancario pesa más con un soberano más endeudado.
- **R2-H2 (pecado original, M4).** Se agregan FXDEBT_{t−4} y D_{t−1} × FXDEBT_{t−4}. Predicción: un
  coeficiente **positivo**. El riesgo de cola pesa más cuanto más deuda en moneda extranjera.
- **R2-H3 (horizonte del riesgo de cola, M3).** Se reemplaza D_{t−1} por D4_{t−1} en la especificación
  principal. Predicción: la semielasticidad del riesgo de cola de mediano plazo es **positiva**.

Inferencia: p unilateral del wild bootstrap en la dirección predicha (con el signo predicho, p
bilateral / 2) y Holm sobre las tres. Veredicto "firme": Holm < 0,05 y, sin cada país, el mismo signo con
p unilateral < 0,10 en todas las exclusiones. "Sugerente": Holm < 0,05 sin pasar la exclusión, o
p < 0,05 solo con Driscoll–Kraay.

## 4. Secundarias (se reportan todas)

- R2-H2 con FXDEBT y LCDEBT a la vez: ¿es mayor el término en moneda extranjera que el de moneda local?
- R2-H3 con el GaR a ocho trimestres (D8).
- R-H3 (deuda × riesgo de cola) con D4 en lugar de D.
- R2-H3 en cambios a cuatro trimestres: ¿aparece el riesgo de cola de mediano plazo en los cambios,
  cosa que el de un trimestre no hacía?
- **Descomposición del spread (M5):** el componente idiosincrásico es el residuo de ln EMBI sobre el
  promedio transversal del trimestre, con una carga por país. Se estima la especificación principal sobre
  ese componente, con efectos fijos de país.
- **Régimen cambiario (M8):** los productos de la fragilidad y del riesgo de cola con la indicadora de
  régimen flexible.

## 5. Consecuencia fijada de antemano

- **R2-H1 firme:** la tesis dirá que la deuda pública amplifica también la transmisión de la fragilidad
  bancaria, el *doom loop* completo. **Si no:** solo el canal del crecimiento depende de la deuda.
- **R2-H2 firme:** la amplificación por la deuda se atribuye a la deuda en moneda extranjera (pecado
  original). **Si no:** se reporta como no confirmada.
- **R2-H3 firme:** la tesis dirá que el riesgo de cola de mediano plazo también se asocia con el spread.
  **Si no:** la asociación queda en el horizonte de un trimestre.
- Si R2-H3 aparece además en los cambios, la conclusión 3 se reescribe y deja de decir que el riesgo de
  cola "no aparece en los cambios".
