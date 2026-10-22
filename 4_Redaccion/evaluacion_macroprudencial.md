---
title: "Evaluación de la tesis desde los mercados financieros y la política macroprudencial"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lente de un economista de estabilidad financiera"
---

*Evaluación de la versión del commit `1560a4b` (tesis de 149 pp.). Usa la misma rúbrica de 8 criterios y
pesos de `evaluacion_experta.md` (escala de 1,0 a 7,0). Las rondas anteriores preguntaban si la inferencia
es correcta (econométrica), si la tesis dice algo creíble sobre el riesgo soberano (macro) y si el canal
bancario tiene microfundamentos (micro). Esta pregunta **qué haría con la tesis un banco central o un
comité de estabilidad financiera: qué indicador vigilar, desde qué nivel preocuparse y con qué
instrumento responder**. Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian,
Boyarchenko y Giannone, 2019, con la plataforma de CEMLA). Todo son asociaciones, no causalidad. Este
documento no modifica la tesis ni el código.*

---

# 1. Plan de evaluación

Qué revisaría un economista de mercados financieros y política macroprudencial, en orden, y cómo:

| # | Pregunta | Cómo se revisa | Dónde |
|---|---|---|---|
| 1 | ¿El EMBI mide riesgo doméstico o el ciclo financiero global? | Peso del componente común (VIX, tasas de EE. UU., flujos) en la varianza del spread y qué queda para los riesgos domésticos | M5 de la ronda macro (`evaluacion_macroeconomica.md:150`); efectos fijos de tiempo |
| 2 | ¿JLoss se compara con las medidas de riesgo sistémico que usan los bancos centrales? | Buscar SRISK, ΔCoVaR o MES calculados sobre los mismos bancos | `02_marco_teorico.tex:65` (solo se citan) |
| 3 | ¿El GaR se usa como herramienta macroprudencial? | Contrastar con el uso del GaR en los informes de estabilidad (FMI, GFSR 2017) y en el diseño de política (Suarez, 2022; Brandão-Marques et al., 2020) | `02_marco_teorico.tex:73`; `05_discusion.tex:19-31` |
| 4 | ¿Hay un umbral operativo? | Buscar un nivel del indicador desde el cual cambia la transmisión, al estilo de la brecha crédito/PIB del colchón contracíclico o de los regímenes de tensión de un CISS | `04_resultados.tex:351`; Anexo D (`fig:umbral`) |
| 5 | ¿Sirve como alerta temprana? | AUROC, ratio ruido/señal y pérdida del regulador para episodios de estrés soberano, en pseudo tiempo real | `04_resultados.tex:142-170` (solo pronóstico del nivel del spread) |
| 6 | ¿Se consideran las políticas macroprudenciales aplicadas? | Buscar un índice de medidas (iMaPP del FMI) como moderador o control | No se trata |
| 7 | ¿La microestructura del mercado de deuda contamina la variable dependiente? | Base CDS–bono, liquidez, composición del índice | Anexo del CDS |
| 8 | ¿Las implicancias son accionables? | Qué indicador, qué umbral, qué instrumento, con qué costo de falsas alarmas | `05_discusion.tex:19-31` |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | Econométrica | Macro | Micro |
|---|---|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,2 | 0,930 | 6,3 | 6,6 | 6,2 |
| 2 | Marco teórico y literatura | 10 % | 5,7 | 0,570 | 6,2 | 6,4 | 5,9 |
| 3 | Datos y construcción de las métricas | 15 % | 6,2 | 0,930 | 6,2 | 6,2 | 6,2 |
| 4 | Estrategia empírica e identificación | 20 % | 5,6 | 1,120 | 5,7 | 5,9 | 5,7 |
| 5 | Inferencia y robustez | 15 % | 6,8 | 1,020 | 6,8 | 6,8 | 6,8 |
| 6 | Interpretación | 15 % | 6,0 | 0,900 | 6,5 | 6,5 | 6,5 |
| 7 | Redacción, estructura y extensión | 5 % | 5,7 | 0,285 | 5,4 | 5,8 | 5,7 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,9 | 0,345 | 6,8 | 6,9 | 6,9 |
| | **Nota ponderada** | | | **6,1** | 6,2 | 6,4 | 6,2 |

(Las columnas de comparación usan las notas reestimadas de cada ronda.)

**Rango:**
- **5,8:** si la comisión lee la tesis como un aporte a la política y pide la regla que la discusión no da.
- **6,6:** si se ejecuta el plan de umbrales U1–U4 y U7 (sección 4) y el semáforo se valida fuera de la
  muestra.

**En una frase:** la tesis establece, con preregistro, una asociación útil para la política ---la deuda
pública amplifica la transmisión del riesgo de cola al spread---, pero se detiene antes de traducirla en lo
que un comité de estabilidad financiera necesita: un indicador, un umbral y una tasa de falsas alarmas.

---

# 3. Evaluación por criterio

## 3.1 Pregunta y contribución — 6,2

**A favor.** La pregunta conecta dos herramientas que los bancos centrales ya usan por separado: medidas
de fragilidad bancaria derivadas de precios de mercado y el GaR de los informes de estabilidad. El
hallazgo central es directamente relevante para la política: el mismo deterioro de la cola del crecimiento
cuesta más en spread a una economía más endeudada (`05_discusion.tex:27`). La simultaneidad de los dos
riesgos y la precedencia de la fragilidad sobre el riesgo de cola justifican vigilarlos juntos
(`05_discusion.tex:23`).

**En contra.** La contribución para la política queda en el plano cualitativo. "Vigilar" no dice desde qué
nivel de deuda o de tensión el riesgo de cola empieza a pesar, ni cuántas falsas alarmas cuesta reaccionar.
La literatura macroprudencial que la tesis podría alimentar ---el colchón contracíclico basado en la brecha
crédito/PIB (Borio y Drehmann, 2009; Drehmann y Juselius, 2014), los regímenes de tensión de los índices
tipo CISS (Holló, Kremer y Lo Duca, 2012) y el GaR como objetivo de política (Suarez, 2022)--- trabaja con
umbrales. La tesis tiene los insumos para proponerlos y no lo hace.

## 3.2 Marco teórico y literatura — 5,7

El marco cubre bien el nexo soberano–bancario, el incumplimiento soberano y la construcción de las dos
métricas, y cita las medidas de mercado (`02_marco_teorico.tex:65`) y el CISS. Faltan tres bloques para este
evaluador:
1. **Política macroprudencial y GaR:** Adrian et al. (2022) sobre la estructura temporal del GaR;
   Brandão-Marques, Gelos, Narita y Nier (2020) y Galán (2020) sobre el efecto de las medidas
   macroprudenciales en la cola del crecimiento; Suarez (2022) sobre el diseño de política con el GaR.
2. **Alerta temprana:** Kaminsky, Lizondo y Reinhart (1998), Alessi y Detken (2011) y Drehmann y Juselius
   (2014), que dan el lenguaje de umbrales, ratio ruido/señal y AUROC.
3. **No linealidades por tensión financiera:** Hubrich y Tetlow (2015) y los modelos de regímenes con un
   CISS, que motivan que la transmisión cambie con el estado del sistema.

## 3.3 Datos y construcción de las métricas — 6,2

La construcción es sólida y ahora robusta a la calibración del motor (μ2: Spearman 0,92–0,97). Para el uso
como señal hay dos límites:
- JLoss satura: el 23,7 % de las observaciones está en el piso (`05_discusion.tex:38`). Un umbral sobre
  JLoss tendría poca resolución justo en la zona tranquila; la DD de Merton (`p34`, `p37`) no satura y es la
  candidata natural para un indicador.
- El FCI que alimenta el GaR (`03_metodologia.tex:156`) es, de hecho, un índice de tensión financiera
  doméstica con bloques accionario, de tasas y cambiario, ortogonalizado respecto del VIX. La tesis lo usa
  solo como insumo del GaR, cuando también es la variable de estado que un regulador miraría.

## 3.4 Estrategia empírica e identificación — 5,6

Dos problemas desde los mercados:
- **El ciclo global domina.** El componente común explica el 70 % de la varianza del spread (M5). Los
  efectos fijos de tiempo lo absorben en promedio, pero un regulador doméstico necesita saber cuánto del
  movimiento le corresponde, y si los riesgos domésticos pesan más cuando la tensión global es alta. La
  tesis no lo condiciona.
- **No hay variación de política.** Ninguna especificación usa medidas macroprudenciales efectivas. Sin
  ellas, la tesis no puede decir si los países que endurecieron sus políticas transmiten menos, ni siquiera
  como asociación. La base iMaPP del FMI (Alam et al., 2019) es pública y cubre las trece economías.

El modelo de umbral existe, pero está subutilizado. Con el GaR como variable de umbral estima γ en
$D = 0{,}12$ y una elasticidad de la fragilidad de 0,141 frente a 0,079 en la cola severa (diferencia
p = 0,08), con un perfil plano y LR = 6,0 bajo el valor crítico (`04_resultados.tex:351`). En niveles el
contraste es mucho más fuerte (LR = 26,0; diferencia de 4,4 pb, p = 0,028; `paper_nivlag_numeros.csv`).
No tiene bootstrap de linealidad por país y no se prueba ninguna otra variable de umbral.

## 3.5 Inferencia y robustez — 6,8

Sin cambio respecto de las demás rondas: wild bootstrap por país, Holm, exclusión de cada país, tres
preregistros con commit previo. Un umbral estimado con 13 países heredaría el mismo problema de potencia,
y la tesis tiene la infraestructura para declararlo (`p32.wild`, simulación de potencia).

## 3.6 Interpretación — 6,0

La interpretación es honesta y prudente: la sección "Lo que el panel no permite" (`05_discusion.tex:31`)
es exactamente lo que un evaluador de política quiere leer. Pero las implicancias son negativas o vagas:
- "No hay base para una prima adicional" (`:25`) y "no hay base para recomendar reservas" (`:29`) son
  conclusiones útiles, pero no proponen nada a cambio.
- "El riesgo de crecimiento debería vigilarse junto con la deuda" (`:27`) es la conclusión más fuerte, y
  no dice desde qué nivel de deuda ni con qué regla.
- La precedencia de la fragilidad sobre el riesgo de cola (firme a un trimestre) y sobre el spread a
  frecuencia mensual sugiere un uso como señal adelantada que la tesis no evalúa: el ejercicio fuera de la
  muestra mide el error de pronóstico del nivel del spread, no la capacidad de anticipar episodios.

## 3.7 Estructura — 5,7

149 pp. Una subsección de umbrales tendría que reemplazar texto, no sumarse, por ejemplo desplazando al
anexo parte de las extensiones.

## 3.8 Reproducibilidad — 6,9

Sin cambio. Todo lo que propone el plan se puede construir con datos que ya están en el repositorio,
salvo la base iMaPP.

---

# 4. Plan de mejoras: umbrales para proponer una política

**Idea central.** Llevar el hallazgo de la tesis a la forma en que trabajan los comités de estabilidad
financiera: **un indicador, un umbral y una tasa de falsas alarmas**. El umbral de tensión financiera que
sugiere el autor es el eje: el FCI doméstico ya existe por país y trimestre en los paneles del GaR
(`1_Codigo/GaR/individuals/nlhpc_gar_all18/GaR_panel_all18.xlsx`, columnas `Country`, `Date`, `FCI`), y hay
una versión sin el bloque de tasas (`build_fci_no_ryr.py`) que evita la circularidad con el spread.

**Disciplina.** Como en las rondas anteriores, todo se fija antes en un preregistro
(`4_Redaccion/preregistro_umbrales.md`, commiteado solo): variables de umbral, malla, rezagos, familia
primaria, corrección de Holm, bootstrap por país, exclusión de cada país y consecuencias de cada
resultado. Se reporta salga como salga. Los umbrales se presentan como **umbrales de vigilancia** (dónde
cambia la asociación), no como umbrales de política óptima ni como efectos causales.

Infraestructura que se reutiliza: `p2_regresiones.py::umbral_hansen()` (malla y LR), `p13::fig_umbral()`
(figura), `p14.base`/`p14.shift` (panel y rezagos), `p42.fit`/`p42.centrar`/`p42.moderacion`,
`p32.wild` (wild por país, Webb), `p51.holm`, `p30` (pseudo tiempo real).

## U1. Umbral de tensión financiera (principal)

- **Pregunta:** ¿existe un nivel de tensión financiera doméstica por sobre el cual la fragilidad bancaria y
  el riesgo de cola se transmiten más al spread?
- **Especificación:** regresión principal con pendientes por régimen,
  $\ln EMBI_{it} = \sum_{r} \mathbb{1}[FCI_{i,t-1} \lessgtr \gamma]\,(\beta_1^r \ln JLoss_{i,t-1} + \beta_2^r D_{i,t-1}) + \alpha_i + \lambda_t + \varepsilon_{it}$,
  con γ por mínimos cuadrados concentrados tras la transformación within, en una malla entre los
  percentiles 15 y 85 del FCI.
- **Inferencia:**
  - linealidad con el bootstrap de Hansen (1999), remuestreando países (999 réplicas);
  - intervalo de γ por inversión del LR;
  - diferencia de pendientes con wild por país;
  - exclusión de cada país.
- **Variantes:**
  - FCI sin el bloque de tasas;
  - FCI en percentil propio de cada país, para que el umbral sea transferible entre economías;
  - con la DD en lugar de JLoss, para evitar el piso.
- **Producto:** una "zona de tensión" con su semielasticidad y la fracción de trimestres de cada país en
  ella.
- **Código:** `1_Codigo/Panel/bbg/p52_umbral_tension.py`, que generaliza `umbral_hansen` a cualquier
  variable de umbral y a pendientes por régimen de más de un regresor.
- **Qué podría cambiar:** si el umbral existe, la conclusión 2 (no hay amplificación en promedio) se
  matiza con una no linealidad de estado, distinta de la interacción multiplicativa ya rechazada.
- **Criterio de éxito (primaria):** LR de linealidad con p bootstrap < 0,05 tras Holm y diferencia de
  pendientes con el signo predicho sin cada país.

## U2. Umbral de deuda para la transmisión del riesgo de cola

- **Pregunta:** ¿desde qué nivel de deuda/PIB el riesgo de cola empieza a pesar en el spread? Es la versión
  con umbral del hallazgo central y de la "intolerancia a la deuda" de Reinhart, Rogoff y Savastano (2003).
- **Especificación:** el mismo modelo, con la deuda trimestral en t−4 (`resiliencia_trimestral_bbg.csv`)
  como variable de umbral y el riesgo de cola a uno y a cuatro trimestres con pendiente por régimen.
- **Producto:** un umbral de deuda con su intervalo. Si el intervalo es amplio, se declara y se reporta la
  curva de la semielasticidad a lo largo de la deuda como alternativa.
- **Qué podría cambiar:** la implicancia `05_discusion.tex:27` pasaría de "vigilar con la deuda" a
  "vigilar especialmente sobre γ_D".
- **Criterio de éxito (primaria):** igual que U1.

## U3. El umbral del GaR, completado

- Repetir el modelo existente (`04_resultados.tex:351`) con el bootstrap de linealidad por país que le
  falta, en logaritmos y en niveles, donde hoy da LR = 26,0.
- Reportar el resultado en el cuerpo, junto a U1 y U2, en una sola tabla de umbrales, y actualizar
  NUMEROS: la sección "Modelo de umbral de Hansen" todavía trae las cifras de la especificación anterior
  (γ = −0,18 sobre el CDS).
- **Secundaria:** no entra en la familia de Holm porque ya fue estimado.

## U1–U3 por país: ¿el umbral agrupado es común o un promedio de umbrales distintos?

- **Pregunta:** el umbral agrupado impone el mismo γ a las trece economías. Si cada una tiene un umbral
  propio, el agrupado puede ser un promedio que no describe a ninguna, y no serviría como regla común.
- **Método:** el mismo modelo de umbral, estimado con la serie de tiempo de cada economía. El componente
  global se descuenta con los efectos de tiempo de la regresión agrupada lineal y, como variante, con
  controles globales. Cada umbral lleva su intervalo por inversión del LR (Hansen, 2000) y un intervalo de
  bootstrap por bloques.
- **Muestra:** solo las economías con al menos 50 trimestres con la variable de umbral, que son nueve.
  Filipinas, Indonesia, Sudáfrica y Malasia no alcanzan.
- **Comparación:**
  1. cuántas economías contienen el umbral agrupado en su intervalo;
  2. una prueba de umbral común frente a umbrales por país;
  3. los umbrales expresados en el percentil propio de cada economía, para ver si lo común es el
     percentil y no el nivel.
- **Advertencia:** con 50 a 90 trimestres por país los intervalos serán aún más amplios que los
  agrupados, y la deuda varía tan lento dentro de un país que su umbral se confunde con un quiebre en el
  tiempo. Por eso se compara con un modelo de quiebre en una fecha.
- **Qué podría cambiar:** si el umbral agrupado cae fuera de la mayoría de los intervalos por país, la
  regla de U7 se expresa en percentiles propios de cada economía y no en un nivel común.

## U4. Alerta temprana: umbrales de señal y semáforo

- **Evento (fijado ex ante):** episodio de estrés soberano = el alza del EMBI en los cuatro trimestres
  siguientes supera el percentil 90 propio del país. Se excluyen los trimestres dentro de un episodio
  para evitar el sesgo post-crisis (Bussière y Fratzscher, 2006).
- **Señales:** DD (o JLoss), GaR, deuda, FCI y la combinación en un logit con efectos fijos de país.
- **Métricas:**
  - AUROC con intervalo bootstrap por país;
  - umbral que minimiza la pérdida del regulador $L(\mu) = \mu\,T_1 + (1-\mu)\,T_2$, con μ = 0,5 y 0,7, donde
    T1 es la fracción de eventos no anticipados y T2 la de falsas alarmas;
  - utilidad relativa de Alessi y Detken (2011);
  - ratio ruido/señal de Kaminsky, Lizondo y Reinhart (1998).
- **Validación:** pseudo tiempo real con ventana recursiva desde 2012, usando la serie del GaR estimada en
  pseudo tiempo real que la tesis ya tiene; con la DD mensual como versión de alta frecuencia.
- **Producto:** un **semáforo** por indicador:
  - verde, bajo el umbral de pérdida mínima;
  - ámbar, entre ese umbral y el de μ = 0,7;
  - rojo, sobre ambos.
  Cada color con sus tasas de aciertos y de falsas alarmas.
- **Código:** `1_Codigo/Panel/bbg/p53_alerta_temprana.py`.
- **Qué podría cambiar:** la conclusión "ninguno de los dos riesgos pronostica el spread" se refiere al
  nivel. Si el AUROC es alto para los episodios, la fragilidad o el GaR sirven como señal aunque no mejoren
  el error cuadrático.
- **Criterio de éxito (primaria):** AUROC fuera de la muestra con su intervalo sobre 0,5, en la
  combinación y en al menos una señal individual.

## U5. Política macroprudencial efectiva (iMaPP)

- **Pregunta:** ¿los endurecimientos macroprudenciales acumulados, con el índice en t−4, se asocian con una
  transmisión menor de la fragilidad o del riesgo de cola?
- **Datos:** base iMaPP del FMI (Alam et al., 2019), pública, cacheada en `2_Datos/imapp/`. Si no es
  accesible, se declara.
- **Método:** moderación con `p42.moderacion`; se separan las medidas sobre el capital bancario (que
  deberían atenuar la fragilidad) y sobre el crédito a hogares (que deberían atenuar el riesgo de cola).
- **Código:** `1_Codigo/Panel/bbg/p54_imapp.py`.
- **Advertencia:** las medidas responden al riesgo, de modo que el signo puede ir en contra de la
  atenuación sin que la política fracase. Es una asociación, como todo lo demás.

## U6. Comparación con las medidas sistémicas de mercado (secundaria)

- Calcular el MES y el ΔCoVaR de cada sistema con los retornos diarios de los mismos bancos (los insumos de
  `p47`) y el índice accionario del país.
- Ver si ordenan las economías y los trimestres como JLoss y si dan el mismo umbral de U1.
- Responde a la pregunta obvia de un banco central: por qué JLoss y no el SRISK que ya publica, por
  ejemplo, el V-Lab.

## U7. Traducción a política (redacción)

- Subsección **"Umbrales de vigilancia"** en la discusión de la tesis y del paper, con:
  - una tabla de umbrales (U1–U3);
  - el semáforo (U4);
  - una regla del tipo *vigilar el riesgo de cola con prioridad cuando la deuda supera γ_D y la tensión
    financiera supera γ_FCI*, con sus tasas de error.
- Situarla respecto del colchón contracíclico (brecha crédito/PIB de Basilea III) y del uso del GaR en los
  informes de estabilidad financiera, y declarar qué no es: ni un umbral óptimo ni un efecto causal.
- Reescribir las implicancias `05_discusion.tex:23-27` con la regla. Mover a un anexo texto equivalente
  de las extensiones para no alargar la tesis.
- Actualizar láminas (una lámina "Umbrales de vigilancia"), Defensa V21, NUMEROS §31, REPRODUCIBILIDAD y
  README.

## Riesgos que se declaran de antemano

- **Potencia:** un umbral de panel con 13 países tiene poca potencia, y el intervalo de γ puede abarcar
  casi toda la malla. Se reporta igual, y se acompaña con la curva continua de la pendiente.
- **Pocos episodios:** se concentran en 2008, 2013, 2015–16, 2018 y 2020. El AUROC tendrá intervalos
  amplios y la validación fuera de la muestra arranca con pocos eventos.
- **Circularidad:** el FCI contiene el rendimiento soberano local; por eso la variante sin el bloque de
  tasas es obligatoria y se reporta en paralelo.
- **Búsqueda de especificación:** varias variables de umbral multiplican las pruebas; por eso la familia
  primaria (U1, U2 y U4 combinado) se fija antes y se corrige por Holm.

---

**Ruta recomendada:**
1. Preregistro de umbrales (½ día, commit solo).
2. U3 (½ día): valida la nueva rutina de bootstrap contra el umbral ya publicado.
3. U1 (2 días).
4. U2 (1 día).
5. U4 (2–3 días).
6. U7 (1–2 días).
7. U5 y U6 si el tiempo alcanza, o para el paper.

**Nota esperada con U1–U4 y U7:** en torno a 6,5–6,6, y depende menos de que los umbrales sean
significativos que de que la tesis entregue un indicador evaluado con el lenguaje de la política
(umbral, aciertos, falsas alarmas). Si los umbrales no aparecen, la nota sube igual, pero menos (≈ 6,3):
la tesis podría afirmar con evidencia que la transmisión no cambia de régimen con la tensión financiera,
que también es una conclusión de política.
