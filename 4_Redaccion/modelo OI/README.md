# Modelo OI — Organización Industrial bancaria, JLoss, GaR y EMBI

## 1. Qué contiene esta carpeta y su rol en la tesis

Esta carpeta es la **arista de Organización Industrial (OI)** de la tesis: el desarrollo
completo de un modelo teórico formal de organización industrial bancaria que conecta la
**estructura de mercado bancario** (intensidad de competencia) con la **fragilidad sistémica**
($JLoss$), el **riesgo a la baja del crecimiento** ($GaR$) y el **spread soberano** ($EMBI$) en
economías en desarrollo.

Contiene tanto el **paper teórico completo** (`working_paper.tex`, con su apéndice de
demostraciones `apendice_matematico.tex`) como la **bitácora íntegra de investigación** que
documenta, fase a fase, cómo se construyó, se calibró y se sometió a crítica ese modelo. Es la
pieza que microfunda —desde primeros principios de competencia bancaria à la Cournot, con
responsabilidad limitada y seguro de depósitos— la cadena teórica que el resto de la tesis
contrasta empíricamente.

La carpeta se mueve **como unidad**: `working_paper.tex` referencia sus cuatro figuras
(`fase3_calibracion.png`, `fase4_embi.png`, `fase5_montecarlo.png`, `fase6_robustez.png`) por
nombre relativo a esta misma carpeta.

---

## 2. La cadena teórica del modelo (resumen)

El parámetro profundo del modelo es la estructura de mercado bancario, $n$ (número de bancos,
inverso de la concentración). El modelo se construye en un mercado de crédito con $n$ bancos
idénticos, responsabilidad limitada y seguro de depósitos, que compiten à la Cournot en
cantidad de crédito; los prestatarios, tomando la tasa de equilibrio como dada, eligen el
riesgo de su proyecto (canal *risk-shifting*, Boyd–De Nicoló); un factor macro-financiero común
correlaciona los defaults entre bancos (estructura tipo Merton/Vasicek). La cadena resultante es:

$$
n\ (\text{estructura de mercado}) \;\longrightarrow\; JLoss \;\longrightarrow\; GaR \;\longrightarrow\; EMBI
$$

**Proposiciones principales** (demostradas en `working_paper.tex` y con detalle paso a paso en
`apendice_matematico.tex`):

- **Proposición 1 (existencia y unicidad + forma en U de la fragilidad individual).** El
  equilibrio de Cournot simétrico existe y es único. La probabilidad de quiebra individual
  ($PD$) es no monótona en la competencia: forma de U, por la tensión entre el efecto margen
  /*charter value* (Keeley, 1990) y el efecto *risk-shifting* (Boyd–De Nicoló, 2005). Esta
  proposición **anida exactamente** a Martínez-Miera y Repullo (2010, MMR) como caso particular
  cuando la correlación de activos es constante.

- **Proposición 2 (desplazamiento del mínimo de $JLoss$ — la contribución marginal frente a
  MMR).** Al endogenizar la correlación de activos $\rho(n)$ como decreciente en la
  competencia (carteras más diferenciadas con más bancos), el mínimo de la fragilidad
  **sistémica** ($JLoss$, la cola conjunta de pérdidas) se desplaza hacia un mercado **más
  competido** que el mínimo de la fragilidad **individual** ($PD$). Es la predicción
  distinguible de MMR: una política de competencia calibrada solo sobre la salud individual de
  los bancos deja al sistema subóptimamente concentrado desde la óptica del riesgo de cola.

- **Proposición 3 (traspaso de cola creciente en la concentración).** La sensibilidad de la
  cola sistémica ante un shock es creciente en la concentración (índice de Herfindahl), por un
  canal de granularidad (menos bancos, cada uno con mayor exposición $\lambda_i$) y por el canal
  de correlación $\rho(n)$.

- **Proposición 4 (complementariedad $JLoss \times GaR$ sobre $EMBI$, amplificada por
  concentración).** Cerrando el lazo macro-soberano (*credit crunch* $JLoss \to GaR$; límite
  fiscal / *doom loop* $GaR, JLoss \to EMBI$), la fragilidad sistémica y el riesgo a la baja son
  complementarios en la determinación del spread soberano (derivada cruzada de signo
  determinado), y esa complementariedad es **creciente en la concentración** bancaria.

El modelo se somete además a robustez: se re-deriva bajo una estructura de competencia
alternativa (Salop), se microfundamenta el signo de $\rho(n)$ (canal de diferenciación vs. canal
de *herding*), se valida numéricamente el método de cálculo de $JLoss$ por punto de silla
(contra Monte Carlo y convolución exacta), y se somete a una revisión adversarial explícita
(objeciones de referee con respuestas honestas, incluyendo límites reconocidos).

*Nota de convención de signo:* los documentos de bitácora (`Plan_...md`, `Fase_IV`, `Fase_V`)
trabajan con $D \equiv -GaR$ (magnitud del riesgo a la baja, $\beta_3,\beta_4>0$). La versión
vigente de `apendice_matematico.tex` reescribe el bloque soberano usando $GaR$ directamente
como variable primitiva (cuantil bajo del crecimiento, negativo en la cola), de modo que los
signos coinciden directamente con los de las regresiones: $\beta_1>0$, $\beta_2<0$, $\beta_3<0$,
$\beta_4<0$. Es el mismo resultado económico (complementariedad y amplificación); solo cambia la
convención de signo de la variable de riesgo a la baja.

---

## 3. Inventario de archivos

### Bitácora de investigación (orden cronológico, 22-jul)
No obsoleta: documenta el razonamiento y las decisiones detrás de cada proposición.

| Archivo | Rol |
|---|---|
| `Plan_Arista_OI_Competencia_Fragilidad.md` | Plan de investigación: pregunta, hipótesis central, contribución marginal frente a la literatura, arquitectura de fases, cronograma. |
| `Fase_II_Modelo_Cournot.md` | Especificación formal del modelo: primitivos, timing, equilibrio de Cournot, Proposición 0 (existencia/unicidad) y Proposición 1 (U de $PD$). |
| `Fase_III_Proposiciones_y_Calibracion.md` | Demuestra la Proposición 2 (mínimo de $JLoss$ desplazado) y la Proposición 3 (traspaso creciente en concentración); calibración numérica. |
| `Fase_IV_Cierre_Macro_Soberano.md` | Cierra la cadena macro-soberana ($JLoss\to GaR\to EMBI$); demuestra la Proposición 4 (complementariedad y amplificación estructural). |
| `Fase_V_Diseno_Empirico.md` | Traduce las proposiciones en hipótesis testeables (H1–H4b), especificaciones econométricas y validación del diseño por Monte Carlo. |
| `Fase_VI_Robustez_y_Revision_Adversarial.md` | Robustez bajo Salop, microfundamento de $\rho(n)$, validación del método de punto de silla, revisión adversarial (objeciones de referee) y *scorecard* final. |

### Paper teórico vigente (27-jul / 26-jul)

| Archivo | Rol |
|---|---|
| `working_paper.tex` (+ `.pdf`, `.aux`, `.log`, `.out`) | **Paper teórico vigente.** Consolida las Fases II–VI en un documento autocontenido: modelo, Proposiciones 1–4, calibración, cierre macro-soberano, estrategia empírica y robustez. Referencia las 4 figuras PNG de esta carpeta por nombre. |
| `apendice_matematico.tex` (+ `.pdf`, `.aux`, `.log`, `.out`, `.toc`) | **Apéndice matemático vigente.** Demostraciones formales completas, paso a paso, de cada proposición, verificadas numéricamente. Compila de forma independiente (`\documentclass` propio, sin `\input` cruzado con `working_paper.tex`). Usa $GaR$ (no $D=-GaR$) como variable primitiva. |

### Figuras (referenciadas por `working_paper.tex`)

| Archivo | Contenido |
|---|---|
| `fase3_calibracion.png` | $PD(n)$ en U, descomposición en canales, $JLoss_\alpha(n)$ con mínimo desplazado (Prop. 2), $ES_\alpha$ decreciente en $n$ (Prop. 3). |
| `fase4_embi.png` | $EMBI$ vs. riesgo a la baja para distintos niveles de $JLoss$ (complementariedad) y cross-partial creciente en la concentración (Prop. 4). |
| `fase5_montecarlo.png` | Distribución muestral de $\hat\beta_3$, $\hat\beta_4$ en la validación Monte Carlo del diseño empírico. |
| `fase6_robustez.png` | Validación de la cola de pérdidas (exacto vs. Monte Carlo vs. punto de silla) y estática de entrada de Salop. |

### Código y datos de soporte

| Archivo | Rol |
|---|---|
| `fase3_calibracion.py` | Reproduce la calibración de la Fase III: $PD(n)$, $JLoss_\alpha(n)$ bajo $\delta=0$ (anida MMR) y $\delta=0{,}04$ (mínimo desplazado), y el $ES$ finito-$n$. Genera `fase3_calibracion.png`. |
| `mc_gar.py` | Motor de simulación Monte Carlo (panel balanceado $N,T$) para evaluar sesgo y potencia de $\hat\beta_3$, $\hat\beta_4$ bajo la convención $GaR$ (signos verdaderos negativos), con estimador TWFE y errores agrupados por país. |
| `fase5_estimacion.py` | **Ver advertencia en la sección 4.** Pipeline de estimación (TWFE, especificación de la ecuación principal $EMBI \sim JLoss, GaR$ y sus interacciones con $HHI$) diseñado para validar que la especificación econométrica recupera los signos firmados por el modelo. |
| `panel_template.csv` | **Ver advertencia en la sección 4.** Panel de entrada que consume `fase5_estimacion.py` (columnas: `country, time, EMBI, JLoss, GaR, HHI, debt, growth, gfac`). |

---

## 4. Advertencia importante: `fase5_estimacion.py` usa datos simulados, NO reales

`fase5_estimacion.py` y `panel_template.csv` (27-jul) usan un **panel simulado de juguete**: es
un Monte Carlo de validación del diseño econométrico —confirma que la especificación (TWFE con
efectos fijos bidireccionales, interacción triple $JLoss\times GaR\times HHI$) es capaz de
recuperar los signos que el modelo teórico predice—, **no son datos reales**.

**No confundir** con `1_Codigo/Panel/fase5_estimacion_real.py`, que sí usa datos reales del
panel EMBI/JLoss/GaR y testea las hipótesis H4a (complementariedad) y H4b (amplificación por
concentración bancaria) con evidencia empírica real. Ese es el resultado más avanzado de toda
la investigación.

---

## 5. Estado

El `working_paper.tex` compilado (27-jul) **todavía no incorpora en su prosa** los resultados
empíricos reales de H4a/H4b obtenidos en `1_Codigo/Panel/fase5_estimacion_real.py`. Lo que
`working_paper.tex` presenta en su sección empírica es la validación Monte Carlo del diseño
(sobre panel simulado), no el contraste con los datos reales. Integrar esos resultados reales
como nueva sección empírica del working paper es trabajo pendiente de una fase posterior de
reescritura.

---

## 6. Fuente de verdad

La vigencia de todo el proyecto —qué archivo es el vigente por hilo de investigación, en toda
la tesis, no solo en esta carpeta— se determina en
`4_Redaccion/CONTROL_DE_VERSIONES.md`. Ante cualquier discrepancia entre este README y ese
documento, manda `CONTROL_DE_VERSIONES.md`.
