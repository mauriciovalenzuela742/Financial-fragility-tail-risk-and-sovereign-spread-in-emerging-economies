---
title: "Evaluación de la investigación desde un desk de crédito soberano emergente"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, mirada de un quant (estilo JPMorgan), y plan para cada rama de investigación"
---

*Evaluación de la versión del commit `9868ab7`. Usa la misma rúbrica de 8 criterios y pesos de
`evaluacion_experta.md`, en la escala de 1,0 a 7,0.*

*Las rondas anteriores preguntaban:*
- *si la inferencia es correcta (econométrica);*
- *si la tesis dice algo creíble sobre el riesgo soberano (macro);*
- *si el canal bancario tiene microfundamentos (micro);*
- *qué haría un banco central con ella (macroprudencial);*
- *si el documento cuenta una sola historia (comisión).*

*Esta ronda pregunta lo que preguntaría un quant de un desk de crédito soberano emergente: **¿el
pipeline entrega un pronóstico, una razón de cobertura o un número de riesgo que sobreviva fuera de la
muestra, neto de costos y sin sesgo de anticipación?***

*Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019,
con la plataforma de CEMLA). Todo son asociaciones, y una señal rentable tampoco sería un efecto causal.
Este documento no modifica la tesis ni el código.*

---

# 1. Plan de evaluación

| # | Pregunta del desk | Qué se mira | Dónde |
|---|---|---|---|
| 1 | ¿Hay sesgo de anticipación (*look-ahead*)? | Si cada regresor estaba disponible en la fecha en que se usa | GaR en pseudo tiempo real (`03_metodologia.tex`, sección del GaR). Rezago de publicación de los balances de JLoss no verificado (`05_discusion.tex:43`) |
| 2 | ¿Hay capacidad predictiva fuera de la muestra? | Error de pronóstico frente a un paseo aleatorio; AUROC de episodios | `p32_aporte_riesgo_cola.py`: el riesgo de cola empeora el pronóstico (RECM +3 %, Clark–West 0,83). `p53_alerta_temprana.py`: AUROC fuera de la muestra 0,49 |
| 3 | ¿Hay alguna señal de alta frecuencia? | Precedencia mensual, magnitud y estabilidad por país | `p37_mensual_fechado.py`: d(−DD) del mes anterior → d ln EMBI 0,0132 (DK 0,005); suma de tres rezagos 0,027, *wild* < 0,001; 13 de 13 sin cada país; sin dirección inversa (*wild* 0,39) |
| 4 | ¿Qué amplitud (*breadth*) tiene el universo? | Países, episodios y grados de libertad para un *backtest* | 13 economías; 39 episodios de estrés en la prueba de alerta temprana |
| 5 | ¿Cuánto pesa el factor global? | Varianza común y heterogeneidad de las cargas | Componente global ≈ 70 % de la varianza (M5, `evaluacion_macroeconomica.md:150`); CCE con cargas por país (`p43`) |
| 6 | ¿Describe la cola de la distribución del spread? | Cuantiles condicionales | `p35_cuantilica_spread.py`: la fragilidad pesa más en el cuantil alto (con −DD, 0,106 en τ = 0,90, p 0,024) |
| 7 | ¿Se puede implementar? | Retornos totales, duración, costos de transacción | Solo hay spreads (`2_Datos/embi.xlsx`, diario): no hay retornos totales, duraciones ni bid-ask |
| 8 | ¿Es reproducible y disciplinado? | Si la especificación se fija antes de mirar los resultados | Un comando (`reproducir.py`), 104 cifras canónicas, seis preregistros fechados en git |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | Econ. | Macro | Micro | Macroprud. | Comisión |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 5,9 | 0,885 | 6,3 | 6,6 | 6,2 | 6,3 | 6,3 |
| 2 | Marco teórico y literatura | 10 % | 6,0 | 0,600 | 6,2 | 6,4 | 5,9 | 5,8 | 6,5 |
| 3 | Datos y construcción de las métricas | 15 % | 6,4 | 0,960 | 6,2 | 6,2 | 6,2 | 6,3 | 6,3 |
| 4 | Estrategia empírica (aquí: diseño predictivo) | 20 % | 5,6 | 1,120 | 5,7 | 5,9 | 5,7 | 5,7 | 5,8 |
| 5 | Inferencia y robustez | 15 % | 6,9 | 1,035 | 6,8 | 6,8 | 6,8 | 6,9 | 6,9 |
| 6 | Interpretación | 15 % | 6,3 | 0,945 | 6,5 | 6,5 | 6,5 | 6,4 | 6,5 |
| 7 | Redacción, estructura y extensión | 5 % | 6,2 | 0,310 | 5,4 | 5,8 | 5,7 | 5,6 | 5,9 |
| 8 | Reproducibilidad y transparencia | 5 % | 7,0 | 0,350 | 6,8 | 6,9 | 6,9 | 6,9 | 6,9 |
| | **Nota ponderada** | | | **6,2** | 6,2 | 6,4 | 6,2 | 6,2 | 6,35 |

**Rango:**
- **5,9:** si el evaluador exige que la investigación ya entregue una estrategia o una medida de riesgo
  validada.
- **6,7:** si se ejecutan las ramas Q1–Q4 de la sección 5 con preregistro y al menos una pasa su
  criterio.

**En una frase:** el pipeline vale más que sus resultados. Tiene datos difíciles de reunir, construidos
con un protocolo único y auditables, y tiene inferencia honesta y disciplina de preregistro. Es
exactamente la infraestructura con que un desk construye señales, pero todavía no ha respondido ninguna
pregunta de inversión: todo lo firme describe niveles y regresores, no retornos.

---

# 3. Evaluación por criterio

## 3.1 Contribución — 5,9

- **A favor:**
  - La simultaneidad de los dos riesgos (1,2 veces lo esperado con el calendario común) es un hecho útil
    para el riesgo de portafolio: los dos choques no se diversifican entre sí.
  - La precedencia mensual de la DD sobre el spread es la única pieza con forma de señal.
- **En contra:**
  - Ningún resultado está en el espacio de los retornos.
  - La precedencia mensual es pequeña: una desviación estándar de d(−DD) va seguida de un spread ~0,6 %
    mayor el mes siguiente y ~1,2 % a tres meses (NUMEROS §22). Nunca se probó como estrategia, neta de
    costos.
  - El riesgo de cola no mejora el pronóstico del spread (§18.1), y la alerta temprana no supera al azar
    fuera de la muestra (AUROC 0,49, §31).

## 3.2 Marco — 6,0

- Es sólido para el riesgo de incumplimiento (Eaton–Gersovitz, el límite fiscal, el nexo banco–soberano).
- Le falta la teoría de valoración con la que trabaja un desk:
  - la prima de riesgo global y la aversión al riesgo de los inversionistas (Longstaff et al., 2011);
  - los factores de carry, momentum y valor en crédito soberano (Asness, Moskowitz y Pedersen, 2013);
  - la segmentación por flujos a fondos dedicados.
- El modelo de límite fiscal predice que el spread debería responder al riesgo de cola 17 veces más de lo
  que responde. Es una pista directa de que la prima global domina, y el marco no la desarrolla.

## 3.3 Datos — 6,4

- **Activo poco común:**
  - 113 bancos extraídos de Bloomberg con un protocolo único;
  - un motor de Merton que permite construir la DD diaria (precios diarios por país en `bbg/<país>/`);
  - un GaR en pseudo tiempo real;
  - deuda trimestral (QPSD) y choques de términos de intercambio.
- **Lo que falta para un *backtest*:**
  - retornos totales EMBI por país y su duración;
  - bid-ask;
  - fechas de calificación;
  - CDS bancarios.
- **El riesgo más serio:** el rezago de publicación de los balances que entran a JLoss no está
  verificado (`05_discusion.tex:43`). Para trading habría que rezagar los fundamentos un trimestre más.

## 3.4 Diseño predictivo — 5,6

Desde un desk, este criterio pregunta por el diseño fuera de la muestra, no por la identificación causal.
- **A favor:** la ventana recursiva de la alerta temprana y el contraste de Clark–West muestran que el
  autor sabe hacerlo.
- **En contra:**
  - Casi todo es en la muestra.
  - Los pronósticos fuera de la muestra son trimestrales, sin efectos de tiempo y sin reestimar el GaR
    (`05_discusion.tex:50`).
  - El factor global, que explica el 70 % de la varianza, nunca se cubre explícitamente: una señal
    doméstica tiene que medirse neta de él.
  - No hay una prueba en frecuencia mensual con la DD, que es la que tiene información.

## 3.5 Inferencia — 6,9

El wild por país, la permutación, la potencia simulada y la corrección conjunta sobre 14 hipótesis son el
estándar de un *backtest* honesto. Con 13 países, un desk agregaría el bootstrap estacionario por bloques
de tiempo y la prueba de Sharpe de Ledoit y Wolf (2008), que la tesis no necesita pero un *backtest* sí.

## 3.6 Interpretación — 6,3

La interpretación es prudente y nunca exagera, lo que un desk valora. Pero no traduce nada a las unidades
de un desk: ni P&L, ni DV01, ni VaR, ni razón de cobertura. La lectura "la simultaneidad es un hecho,
pero no hay amplificación en el nivel" deja abierta la pregunta que más importa para el riesgo: si la
simultaneidad ensancha la distribución de los cambios del spread.

## 3.7 Estructura — 6,2

La versión corta de la predefensa ayuda. Para un desk sobra extensión: la respuesta útil cabe en tres
láminas (simultaneidad, sin amplificación, la señal mensual).

## 3.8 Reproducibilidad — 7,0

Un comando, 104 cifras congeladas, integración continua y seis preregistros fechados: es la disciplina
que separa la investigación sistemática de la minería de datos. Es lo mejor del proyecto desde esta
mirada.

---

# 4. Lo que un desk señalaría antes de usar nada

1. **Anticipación en JLoss.** Antes de cualquier *backtest*, los balances se rezagan un trimestre más que
   en la tesis, o se usa solo la parte de mercado (la DD con el pasivo del trimestre anterior).
2. **Amplitud.** Con 13 países y pocos episodios de estrés, un Sharpe de 0,5 tiene un intervalo que
   cruza el cero con facilidad. La única protección es fijar la señal, el universo, el horizonte y los
   costos antes de mirar un solo retorno.
3. **Turquía.** Aporta el 70 % del coeficiente de la fragilidad. Toda estrategia debe reportarse sin ella.
4. **Costos.** El bid-ask de los bonos soberanos emergentes va de 10 a 25 pb de spread fuera del grado de
   inversión, y más en estrés. Una señal de ~0,6 % de spread al mes puede no sobrevivir.
5. **Licencias.** Los datos de Bloomberg limitan qué se puede publicar. Las series derivadas (JLoss, DD,
   GaR) sí pueden compartirse si se documenta su construcción.

---

# 5. Plan de investigación por rama

## 5.1 Protocolo común

- **Preregistro.** Se escribe `4_Redaccion/preregistro_quant.md` y se commitea **antes de construir
  cualquier retorno**, como en los seis preregistros anteriores. Fija para cada rama:
  - la hipótesis primaria y las secundarias;
  - el criterio de éxito;
  - la consecuencia de cada resultado.
- **Muestra de evaluación:** ventana expansiva, con estimación hasta t y evaluación desde 2015 en
  adelante.
- **Anticipación:** la parte de balance de JLoss se rezaga un trimestre adicional; la DD mensual usa el
  pasivo del trimestre anterior.
- **Retornos:** el retorno de exceso mensual por país se aproxima como r ≈ −D·Δs + s/12, con una
  duración D fija de 7 años, declarada. Se reemplaza por los índices JPM EMBI GD de retorno total por país
  si se consigue el acceso en Bloomberg.
- **Costos:** 15 pb de spread por rotación completa en el caso base, y 25 pb como sensibilidad.
- **Inferencia:**
  - bootstrap estacionario de Politis y Romano (1994) por bloques de tiempo;
  - prueba de Sharpe de Ledoit y Wolf (2008);
  - wild por país cuando es una regresión de panel;
  - corrección de Holm sobre la familia primaria de todas las ramas que se ejecuten.
- **Reporte:** salga como salga, en la tesis o en el paper como extensión, con NUMEROS y canónicos.

**Infraestructura que se reutiliza:**

| Pieza | Archivo |
|---|---|
| DD mensual y lector del EMBI diario | `p37_mensual_fechado.py` (`fragilidad_mensual_bbg.csv`, `2_Datos/embi.xlsx`) |
| Wild por país | `p32_aporte_riesgo_cola.py` (`wild`) |
| Holm, BH y BY; aleatorización | `p56_inferencia_conjunta.py` |
| Ventanas recursivas, AUROC y pérdida | `p53_alerta_temprana.py` |
| Pronóstico fuera de la muestra y Clark–West | `p32_aporte_riesgo_cola.py` |
| Regresión cuantílica por momentos (MMQR) | `p35_cuantilica_spread.py` |
| CCE y cargas factoriales | `p43_revision_econometrica.py` |
| Estudio de eventos diario y placebos | `p39_eventos_respaldo.py` |
| MES y ΔCoVaR con retornos diarios | `p55_medidas_sistemicas.py` |
| Estrés conjunto | `p23_estres_conjunto.py` |
| Panel base | `p14_arbitro_lnlag.py` (`base`, `shift`) |
| Modelo de límite fiscal | `p59_modelo.py` |

## 5.2 Las ramas

### Q1. Una señal de valor relativo con la fragilidad bancaria (principal)

- **Pregunta.** ¿El cambio mensual de la DD del sistema bancario ordena a los países según su retorno
  del mes siguiente?
- **Hipótesis primaria (Q1-H1).** Un portafolio largo en el tercil de países con mayor ΔDD (bancos que
  mejoran) y corto en el tercil con menor ΔDD, igualmente ponderado y neutral al beta del EMBI agregado,
  tiene un Sharpe neto de costos mayor que cero fuera de la muestra.
- **Secundarias:**
  - ponderación por rango;
  - horizonte de tres meses, con carteras superpuestas;
  - sin Turquía;
  - señal en nivel de DD frente a cambio;
  - regresiones de Fama–MacBeth de r_{i,m+1} sobre ΔDD_{i,m}.
- **Datos:** los existentes, más los retornos aproximados.
- **Código nuevo:** `p60_senal_dd.py`. Reutiliza la serie de p37 y la inferencia de p56.
- **Criterio de éxito:** el intervalo del 90 % del Sharpe neto (Ledoit–Wolf) excluye el cero, y el signo
  se mantiene sin Turquía.
- **Riesgos:**
  - con cuatro países por pata, el ruido es alto;
  - la señal puede ser la de las acciones bancarias, que ya incorporan la información antes que el
    spread (lo dice §22).
- **Esfuerzo:** 1–2 semanas.
- **Efecto sobre la rúbrica:** si pasa, contribución +0,5 y diseño predictivo +0,4.

### Q2. Un modelo de valor razonable y la reversión de su residuo

- **Pregunta.** ¿El spread vuelve a su valor razonable según los fundamentos domésticos, y a qué
  velocidad?
- **Hipótesis primaria (Q2-H1).** El residuo de ln EMBI sobre efectos de tiempo, JLoss, el GaR y la
  deuda, estimado con información hasta t, predice con signo negativo el cambio de ln EMBI a uno y tres
  meses. Mejora el pronóstico de un paseo aleatorio según el contraste de Clark–West.
- **Secundarias:**
  - vida media del residuo, con un AR(1) por país;
  - comparación con carry (el spread mismo) y momentum (el cambio de 3 meses);
  - portafolio largo en el barato y corto en el caro.
- **Por qué es prometedora:** la relación de largo plazo del riesgo de cola (PMG, 0,067, IC [0,010; 0,103],
  NUMEROS §27) es justo lo que necesita un valor razonable, aunque no aparezca en los cambios.
- **Código nuevo:** `p61_valor_razonable.py`, con las ventanas de p53 y el Clark–West de p32.
- **Criterio de éxito:** Clark–West con p < 0,05 a un mes y vida media menor que seis meses.
- **Riesgo:** los fundamentos son trimestrales, así que el residuo mensual depende de interpolar.
- **Esfuerzo:** 1 semana.
- **Efecto:** contribución +0,3, interpretación +0,3.

### Q3. ¿La simultaneidad ensancha la cola de los cambios del spread?

- **Pregunta.** La tesis muestra que la coincidencia de los dos riesgos no sube el nivel del spread más
  que la suma. ¿Sube su volatilidad o su riesgo de salto?
- **Hipótesis primaria (Q3-H1).** En la regresión cuantílica de Δ ln EMBI a uno y tres meses, el
  indicador de estrés conjunto (p23) eleva el cuantil 95 % más que el cuantil 50 %. Es decir, el
  coeficiente de escala del MMQR es mayor que cero.
- **Secundarias:**
  - VaR condicional al 95 % y 99 % con los dos riesgos, con *backtest* de Kupiec (cobertura) y
    Christoffersen (independencia) frente a un VaR histórico y uno EWMA;
  - el *expected shortfall* condicional.
- **Por qué importa:** convierte la conclusión más firme de la tesis en una regla de tamaño de posición.
  Nadie la ha probado, y todas las piezas existen (p23, p35).
- **Código nuevo:** `p62_cola_cambios.py`.
- **Criterio de éxito:**
  - escala del término conjunto > 0 con *wild* p < 0,05;
  - el VaR condicional pasa los dos *backtests* y el EWMA no, o lo supera en la pérdida de cuantil.
- **Riesgo:** los episodios conjuntos se concentran desde 2020 (129 de 168), así que el resultado puede
  ser la pandemia. Se reporta sin 2020–2021.
- **Esfuerzo:** 1–2 semanas.
- **Efecto:** contribución +0,4, interpretación +0,3. Si pasa, es la extensión que mejor encaja en la
  tesis.

### Q4. Una razón de cobertura condicional al factor global

- **Pregunta.** ¿La exposición de cada país al factor global cambia con su fragilidad y su deuda? Si es
  así, una cobertura condicional reduce más riesgo que una fija.
- **Hipótesis primaria (Q4-H1).** En Δ ln EMBI_{i,m} = β_{i,m}·ΔF_m + e, con
  β_{i,m} = b_i + c₁·JLoss_{i,m−1} + c₂·deuda_{i,m−1} y F el spread de alto rendimiento de EE. UU., la
  varianza del residuo cubierto fuera de la muestra es menor que con un beta fijo o uno móvil de 36 meses.
  Se contrasta con la prueba de Diebold y Mariano.
- **Secundarias:** el VIX como factor y las cargas CCE de p43 como punto de partida.
- **Código nuevo:** `p63_cobertura.py`. Los factores globales ya están en el panel, y en `tab:chari-arb`.
- **Criterio de éxito:** reducción de varianza significativa (DM p < 0,05) en al menos la mitad de los
  países.
- **Riesgo:** el factor global es casi colineal con los efectos de tiempo, que hoy lo absorben, así que
  hay que estimar sin ellos.
- **Esfuerzo:** 1 semana.
- **Efecto:** diseño predictivo +0,3, interpretación +0,2.

### Q5. Deuda × riesgo de cola en puntos básicos, a frecuencia mensual

- **Pregunta.** El modelo de límite fiscal predice la interacción en puntos básicos (+91 pb por d.e. de
  deuda), y los datos trimestrales dan +3,1 pb no firme (`p59`). ¿Aparece con datos mensuales, en cambios
  y en las unidades que importan para el DV01?
- **Hipótesis primaria (Q5-H1).** En ΔEMBI (pb) mensual, el producto del GaR mensual (Q6) por la deuda
  del trimestre anterior es mayor que cero.
- **Código nuevo:** `p64_deuda_pb_mensual.py`.
- **Criterio de éxito:** *wild* p < 0,05 y signo positivo en al menos 10 de 13 exclusiones.
- **Dependencia:** necesita Q6, porque con el GaR trimestral interpolado la prueba hereda la baja
  frecuencia.
- **Esfuerzo:** 1 semana después de Q6.
- **Efecto:** marco +0,2 (contrasta el modelo en su propio terreno) y contribución +0,2.

### Q6. Un nowcast mensual del GaR

- **Pregunta.** ¿Se puede tener el riesgo de cola cada mes, en tiempo real, en vez de cada trimestre?
- **Método:**
  - re-estimar la regresión cuantílica del GaR con el FCI promediado al mes, con los insumos diarios del
    FCI de `1_Codigo/GaR/individuals/nlhpc_gar_all18`;
  - mantener el crecimiento trimestral como variable dependiente (MIDAS en el regresor);
  - ventana expansiva en pseudo tiempo real.
- **Código nuevo:** `1_Codigo/GaR/individuals/nlhpc_gar_all18/nowcast_gar_mensual.py`. Si la cuantílica
  es lenta, se ejecuta en el supercomputador con un archivo Slurm, como en las rondas anteriores.
- **Criterio de éxito:** correlación mayor que 0,9 con el GaR trimestral en los meses de fin de trimestre,
  y error absoluto mediano menor que 0,5 pp.
- **Esfuerzo:** 2 semanas.
- **Efecto:** datos +0,3. Habilita Q5 y mejora Q2 y Q3.

### Q7. Contagio del banco al soberano en CDS

- **Pregunta.** ¿La fragilidad bancaria se transmite al CDS soberano propio y al de los vecinos?
- **Método:**
  - CDS de los bancos sistémicos frente al CDS soberano;
  - la base CDS–bono;
  - ΔCoVaR entre países con los retornos diarios de p55: la fragilidad de A, ¿mueve el spread de B?
- **Datos faltantes:** los CDS bancarios en Bloomberg (μ7 de `evaluacion_microeconomica.md`). Si no hay
  acceso, se declara no factible, como iMaPP.
- **Código nuevo:** `p65_contagio.py`.
- **Criterio de éxito:** coeficiente de la fragilidad de A sobre el spread de B > 0 con *wild* p < 0,05,
  más allá del factor común.
- **Esfuerzo:** 2–3 semanas si hay datos.
- **Efecto:** contribución +0,3 y datos +0,2.

### Q8. Estudios de eventos condicionados a la fragilidad

- **Pregunta.** ¿El spread reacciona más a las malas noticias soberanas cuando los bancos están frágiles?
- **Eventos:**
  - bajas de calificación soberana;
  - aprobación de programas del FMI;
  - líneas swap (ya en p39).
- **Hipótesis primaria (Q8-H1).** La reacción anormal [0,+5] a una baja de calificación es mayor cuando
  JLoss está sobre la mediana de su país que bajo ella.
- **Código nuevo:** `p66_eventos_fragilidad.py`, con la maquinaria y los placebos de p39.
- **Datos faltantes:** las fechas de calificación, de Bloomberg o de las agencias. Sin ellas, solo FMI y
  swaps, con muy pocos eventos.
- **Criterio de éxito:** diferencia entre estados con p del placebo < 0,05.
- **Esfuerzo:** 1–2 semanas.
- **Efecto:** contribución +0,2.

---

# 6. Ruta y trayectoria de la nota

| Etapa | Ramas | Por qué en este orden | Tiempo |
|---|---|---|---|
| 0 | Preregistro `preregistro_quant.md` | Antes de construir un solo retorno | 1–2 días |
| 1 | Q1 y Q3 | Reutilizan código existente y tienen un pasa/no pasa claro; Q3 extiende el resultado más firme de la tesis | 2–3 semanas |
| 2 | Q2 y Q4 | Valor razonable y cobertura: el núcleo del trabajo de un desk | 2 semanas |
| 3 | Q6 y luego Q5 | El nowcast habilita la prueba del modelo en puntos básicos | 3 semanas |
| 4 | Q8 y Q7 | Dependen de datos nuevos (calificaciones, CDS bancarios) | 3–5 semanas |

| Criterio | Hoy | Con las etapas 1–2, si al menos una rama pasa | Con todo, si Q1–Q6 pasan |
|---|---|---|---|
| Contribución (15 %) | 5,9 | 6,5 | 6,8 |
| Marco (10 %) | 6,0 | 6,4 | 6,6 |
| Datos (15 %) | 6,4 | 6,5 | 6,8 |
| Diseño predictivo (20 %) | 5,6 | 6,2 | 6,5 |
| Inferencia (15 %) | 6,9 | 7,0 | 7,0 |
| Interpretación (15 %) | 6,3 | 6,7 | 6,9 |
| Estructura (5 %) | 6,2 | 6,2 | 6,2 |
| Reproducibilidad (5 %) | 7,0 | 7,0 | 7,0 |
| **Ponderada** | **6,2** | **6,5** | **6,7** |

**Si ninguna rama pasa,** la nota queda en torno a 6,3: sube por transparencia, como con N1–N3. Una
investigación que preregistra una estrategia y reporta que no funciona neta de costos sigue siendo más
creíble que una que no lo intentó.

**Advertencias finales:**
- Con 13 países, cualquier Sharpe tendrá intervalos muy anchos. Un resultado positivo es evidencia
  sugerente, no una estrategia lista para operar.
- Una señal rentable no vuelve causal la asociación: puede reflejar que las acciones bancarias incorporan
  antes la misma información que el spread.
- La rúbrica de tesis no premia el P&L. Estas ramas encajan mejor como un paper o un trabajo posterior a
  la defensa. La excepción es Q3, que extiende directamente la conclusión más firme y cabría como
  extensión preregistrada.

## Referencias citadas en esta evaluación

- Asness, C., Moskowitz, T. y Pedersen, L. (2013). Value and momentum everywhere. *Journal of Finance*,
  68(3).
- Ledoit, O. y Wolf, M. (2008). Robust performance hypothesis testing with the Sharpe ratio. *Journal of
  Empirical Finance*, 15(5).
- Longstaff, F., Pan, J., Pedersen, L. y Singleton, K. (2011). How sovereign is sovereign credit risk?
  *American Economic Journal: Macroeconomics*, 3(2).
- Politis, D. y Romano, J. (1994). The stationary bootstrap. *Journal of the American Statistical
  Association*, 89(428).
