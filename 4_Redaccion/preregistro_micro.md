---
title: "Preregistro 3: mejoras microeconómicas (bancos como unidad de análisis)"
subtitle: "Escrito el 22 de octubre de 2026, antes de construir los datos a nivel de banco y antes de estimar"
---

*Este documento fija las hipótesis de las mejoras μ1–μ6 de `4_Redaccion/evaluacion_microeconomica.md`. El
commit que lo contiene incluye la clasificación de propiedad de los 89 bancos del panel de 13 economías
(`2_Datos/propiedad_bancos.csv`, hecha por el autor con información pública y con los cambios de dueño
dentro de la muestra fechados), y precede a los scripts `p46`–`p51`. Antes de escribirlo solo se verificó
que existen los datos:
- la lista de bancos;
- la hoja "Table 3.2 DomesticBank" de Arslanalp y Tsuda;
- el HHI trimestral de `p6`.

No se estimó nada a nivel de banco. Todo son asociaciones, no causalidad.*

**Lo que ya se vio:**
- la fragilidad agregada (JLoss o −DD_w) se asocia con el spread de forma sugerente y depende de Turquía;
- la concentración (H4b) no se identificó con tres proxies, en niveles y en otra especificación;
- la deuda no amplifica la transmisión de la fragilidad (R2-H1).

## 1. Datos

- **DD por banco y trimestre:** con `jloss_engine.quarterly_inputs` y `merton_pd`, los mismos que en
  `p34`. F_b = −DD_b; un valor mayor indica más fragilidad.
- **Peso sistémico:** S_{b,t} es la participación del banco en los pasivos de los bancos cotizados de su
  país.
- **Apalancamiento:** pasivos sobre activos.
- **Propiedad:** estatal, privada nacional o filial extranjera, según `propiedad_bancos.csv`.
- **HHI trimestral** de los mismos bancos (`concentracion_trimestral_bbg.csv`).
- **Tenencia de los bancos domésticos:** su participación en la deuda del gobierno, de Arslanalp y Tsuda
  ("Table 3.2 DomesticBank", % del total).

## 2. Hipótesis de la familia primaria

La inferencia es el wild cluster bootstrap por país (Webb, 999), con p unilateral en la dirección
predicha. Se aplica Holm sobre las seis hipótesis. Una hipótesis es "firme" si su p de Holm es < 0,05 y
además, sin cada país, mantiene el signo con p unilateral < 0,10 en todas las exclusiones.

- **μ1-H1 (sensibilidad de los bancos sistémicos).** Panel banco-trimestre:
  ΔF_{b,t} = α_b + δ_{c,t} + β·(Δln EMBI_{c,t} × S_{b,t−1}) + γ S_{b,t−1} + λ Apalancamiento_{b,t−1} + ε.
  Tiene efectos fijos de banco y de país-trimestre, que absorben todo choque común del país, incluido el
  spread. Predicción: β > 0. Los bancos grandes se vuelven más frágiles cuando sube el spread.
- **μ1-H2 (la asociación viene de los bancos sistémicos).** Se usa la regresión principal y se reemplaza
  ln JLoss por F_sist (−DD ponderado de los dos bancos con más pasivos en t−1) y F_marg (el resto).
  Requiere economías-trimestre con al menos tres bancos. Predicción: b_sist − b_marg > 0, estimado como
  el coeficiente de F_sist en la regresión sobre F_sist y (F_sist + F_marg).
- **μ3-H1 (garantías implícitas).** Igual que μ1-H2, con F_nacional (estatales y privados nacionales) y
  F_extranjero (filiales). La muestra son las economías-trimestre con ambos grupos. Predicción:
  b_nacional − b_extranjero > 0. Las pérdidas de una filial las absorbería su matriz, no el soberano.
- **μ3-H2 (peso estatal).** Se agregan a la principal la participación estatal en los pasivos (t−4,
  estandarizada) y su producto con ln JLoss_{t−1}. Predicción: un coeficiente positivo.
- **μ4-H1 (concentración, predicción del modelo de Cournot).** Se agregan a la principal HHI_{t−4} y
  ln JLoss_{t−1} × HHI_{t−4}. Predicción: un coeficiente positivo.
- **μ5-H1 (exposición soberana, *doom loop*).** Se agregan a la principal la tenencia de los bancos
  domésticos (t−4) y ln JLoss_{t−1} × tenencia. Predicción: un coeficiente positivo.

## 3. Sensibilidad del motor (μ2; criterio propio)

Se recalcula JLoss en tres variantes:
- (i) ρ por banco: la correlación de sus retornos diarios con el índice de capitalización de los demás
  bancos del país, en los ocho trimestres previos, acotada a [0,05; 0,95];
- (ii) un punto de incumplimiento con la deuda de corto plazo (que incluye depósitos) ponderada a la
  mitad, 0,5·CP + 0,5·LP;
- (iii) la malla de pérdidas ancha [0,01; 0,20], incluyendo India.

**μ2-H1:** con cada variante, la correlación de rangos con la base es > 0,8 y β₁ en la principal sigue
positivo. La LGD homogénea no se prueba: JLoss es proporcional a la LGD, de modo que su logaritmo solo
se desplaza en una constante y los coeficientes en logaritmos no cambian. Se demuestra en el texto.

## 4. Secundarias y descriptivas

- **μ6:**
  - la principal exigiendo al menos 3, 4 y 5 bancos por economía-trimestre;
  - la cobertura aproximada de los bancos cotizados (sus activos sobre el crédito de los bancos al sector
    privado, GFDD.DI.02 por el PIB), que es una cota y se reporta como descriptiva.
- μ1-H1 con la propiedad estatal en lugar del tamaño.
- μ3-H1 con DD en lugar de JLoss por grupo.
- **μ7 no se hace:** el repositorio no tiene spreads de bonos ni CDS bancarios. Se declara.

## 5. Consecuencia fijada de antemano

- **μ1-H1 o μ1-H2 firme:** la tesis agrega un canal bancario identificado dentro del país.
- **μ3 firme:** la lectura de JLoss como pasivo contingente del soberano pasa a estar contrastada.
- **μ4-H1 firme:** la predicción del modelo de organización industrial queda respaldada y se reincorpora.
  Si no, se reporta como predicción no respaldada.
- **μ5-H1 firme:** es la primera prueba directa del *doom loop* por la tenencia de deuda.
- **μ2-H1 no se cumple:** la tesis declara que la asociación depende de la calibración del motor.
