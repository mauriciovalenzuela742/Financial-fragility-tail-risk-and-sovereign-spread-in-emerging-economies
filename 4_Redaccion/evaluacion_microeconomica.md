---
title: "Evaluación microeconómica de la tesis"
subtitle: "Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano — misma rúbrica, lente de un microeconomista (organización industrial bancaria, finanzas bancarias, información, microeconometría), 21 de octubre de 2026"
---

*Evaluación de la versión del commit `73970c2` (tesis de 144 pp.). Usa la misma rúbrica de 8 criterios y
pesos de `evaluacion_experta.md` (escala de 1,0 a 7,0). La econométrica se preguntaba si la inferencia es
correcta, y la macro, si la tesis dice algo creíble sobre el riesgo soberano. Esta pregunta **si la
medida de fragilidad y el mecanismo bancario tienen microfundamentos sólidos, y si la evidencia
aprovecha la información a nivel de banco que la tesis ya tiene**. Las métricas no son del autor
(JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA). Todo son
asociaciones, no causalidad. Este documento no modifica la tesis ni el código.*

---

# 1. Plan de evaluación

Qué revisaría un microeconomista, en orden, y cómo:

| # | Pregunta | Cómo se revisa | Dónde |
|---|---|---|---|
| 1 | ¿Los supuestos del motor de JLoss son defendibles banco por banco? | Leer el motor. Contrastar la LGD fija, la ρ uniforme, el punto de incumplimiento KMV, el horizonte de un año y la tasa libre de riesgo constante con la literatura de riesgo de crédito bancario | `jloss_engine.py:44–54`, `:238–275`, `:306–308`; `03_metodologia.tex` (§3.2) |
| 2 | ¿La agregación banco → país conserva la información? | Ver cuántos bancos tiene cada sistema, el peso del mayor banco y qué hace la saturación de la malla | `03_metodologia.tex:147`; `Bloomberg_extraction/output/*/mktcap_*.csv` |
| 3 | ¿El canal bancario está microfundado? | Buscar el canal concreto por el que un banco frágil encarece la deuda soberana: tenencia de bonos soberanos (*home bias*), garantía implícita de rescate (*too-big-to-fail*), dilución (Acharya–Drechsler–Schnabl) | `02_marco_teorico.tex:18–24` |
| 4 | ¿Hay heterogeneidad entre bancos que la tesis ignore? | Estatales frente a privados, grandes frente a chicos, bancos con más o menos bonos soberanos | No se trata en la tesis |
| 5 | ¿La estructura de mercado importa? | La concentración (H4b), el modelo de Cournot que la tesis eliminó y su predicción distintiva | `07_trabajos_futuros.tex:17`; commit `af71bbf` |
| 6 | ¿Incentivos y riesgo moral? | Si la garantía implícita reduce la disciplina de mercado del precio de las acciones bancarias, lo que contamina la DD de Merton | No se trata |
| 7 | ¿Quién fija el precio? | El inversionista marginal del EMBI frente al de las acciones bancarias; la prueba de participación extranjera | `04_resultados.tex` (§ participación extranjera) |
| 8 | ¿Se usa la variación a nivel de banco para identificar? | Hay 113 bancos con balances y capitalización diaria; la estimación se hace solo con el agregado país. El instrumento granular fue débil | `04_resultados.tex:899`; `p36_giv_granular.py` |

---

# 2. Nota

| # | Criterio | Peso | Nota | Aporte | Econométrica | Macro |
|---|---|---|---|---|---|---|
| 1 | Pregunta, relevancia y contribución | 15 % | 6,0 | 0,900 | 6,3 | 6,3 |
| 2 | Marco teórico y literatura | 10 % | 5,6 | 0,560 | 6,2 | 6,0 |
| 3 | Datos y construcción de las métricas | 15 % | 5,7 | 0,855 | 6,2 | 6,0 |
| 4 | Estrategia empírica e identificación | 20 % | 5,5 | 1,100 | 5,7 | 5,8 |
| 5 | Inferencia y robustez | 15 % | 6,7 | 1,005 | 6,8 | 6,8 |
| 6 | Interpretación | 15 % | 6,3 | 0,945 | 6,5 | 6,3 |
| 7 | Redacción, estructura y extensión | 5 % | 5,8 | 0,290 | 5,4 | 5,8 |
| 8 | Reproducibilidad y transparencia | 5 % | 6,9 | 0,345 | 6,8 | 6,9 |
| | **Nota ponderada** | | | **6,0** | 6,2 | 6,2 |

**Rango:**
- **5,6:** si la comisión incluye a alguien de banca o finanzas corporativas que objete la medida.
- **6,5:** si se ejecutan las mejoras μ1–μ4 (sección 4).

**En una frase:** la tesis construye una base banco por banco excelente (113 bancos, balances y
capitalización diaria con un protocolo único) y después la colapsa en un índice país saturado. Un
microeconomista vería que la pregunta bancaria se puede responder mejor con los datos que ya están en el
repositorio.

---

# 3. Evaluación por criterio

## 3.1 Pregunta y contribución — 6,0
- La pregunta, fragilidad bancaria × riesgo de cola sobre el spread, es relevante. Pero el **mecanismo
  bancario no se contrasta**: la tesis mide un índice agregado y no el canal por el que un banco frágil
  encarece la deuda soberana.
- La contribución más sólida desde la micro es la base de datos homogénea de 113 bancos, que hoy se usa
  solo como insumo.

## 3.2 Marco teórico — 5,6
- **Faltan los modelos de organización industrial bancaria** que la propia investigación desarrolló:
  - El modelo de Cournot con amplificación por concentración se eliminó en el commit `af71bbf`.
  - `07_trabajos_futuros.tex:17` despacha la concentración en una frase ("la teoría no tiene una
    predicción unívoca"), cuando el trabajo previo sí tenía una predicción distintiva.
- **No hay microfundamento del canal:**
  - Farhi–Tirole y Acharya–Drechsler–Schnabl se citan (`02_marco_teorico.tex:18–24`), pero el *home
    bias* de los bancos no se mide en ninguna parte.
  - Faltan la literatura de garantías implícitas y disciplina de mercado (Gropp, Hakenes y Schnabel;
    Acharya, Anginer y Warburton) y la de bancos estatales (La Porta, López-de-Silanes y Shleifer).
- **Falta la lectura de información:** el precio accionario bancario como señal que incorpora antes la
  información. Es justo la interpretación que la tesis da a la precedencia mensual.

## 3.3 Datos y métricas — 5,7
1. **Supuestos del motor homogéneos para todos los bancos:**
   - LGD = 45 % (`jloss_engine.py:44`);
   - ρ = 0,4 uniforme (`:52`, heredado de `jloss.mat`);
   - punto de incumplimiento = deuda de corto plazo + ½ de la de largo plazo (`:308`), una regla de KMV
     calibrada para empresas no financieras;
   - horizonte de un año y tasa libre de riesgo de 4 % (`:50–51`) iguales para Turquía y Chile.

   Para bancos, el apalancamiento de 10–20× hace que la DD sea muy sensible a la definición de pasivos.
   Los depósitos asegurados no son deuda que precipite el incumplimiento como la de una empresa.
2. **Saturación:** la cota de la malla es activa en el 98 % de las observaciones y el 23,7 % de la
   muestra está en el piso (`03_metodologia.tex:147`). La medida pierde la parte inesperada que la
   justifica (la contribución marginal al percentil 99).
3. **Agregación con pocos bancos:**
   - Colombia y Perú tienen 3 bancos cotizados, y Chile 4. En esos sistemas JLoss es la PD de dos o tres
     instituciones, y los bancos no cotizados (estatales, extranjeros) quedan fuera.
   - El criterio de Bulgaria y Hungría (1–2 bancos) es correcto, pero el umbral de 3 es arbitrario y no
     se prueba.
4. **Sesgo de selección:** los bancos cotizados son los grandes y privados. Las subsidiarias de bancos
   extranjeros (Santander, BBVA, Scotiabank en América Latina) y los estatales (Banco do Brasil cotiza;
   BancoEstado no) tienen garantías distintas, y la tesis no las distingue.
5. **A favor:** la distancia al incumplimiento media (anexo D) corrige parte del problema y funciona
   mejor que JLoss.

## 3.4 Estrategia e identificación — 5,5
- **No se usa la variación banco–trimestre.** Con 113 bancos, un panel a nivel de banco con efectos fijos
  de banco y de país-trimestre permitiría separar la parte idiosincrásica de la fragilidad de la parte
  común, que es la que se confunde con el spread.
- El instrumento granular resultó débil (`04_resultados.tex:899`). En parte es porque se agregó al nivel
  país antes de instrumentar, en lugar de explotar la heterogeneidad de exposiciones entre bancos.
- **No hay moderadores bancarios:** la tenencia de bonos soberanos, la propiedad estatal o el tamaño
  relativo. Esas son las variables que la teoría dice que deberían modular la transmisión.

## 3.5 Inferencia y robustez — 6,7
Excelente. El único descuento micro: las pruebas no consideran la correlación entre bancos del mismo
sistema más allá del agregado. Un panel a nivel de banco exigiría errores agrupados en dos dimensiones
(banco y país-trimestre).

## 3.6 Interpretación — 6,3
- **A favor:** el lenguaje de asociaciones es disciplinado. La lectura de que los precios accionarios
  bancarios "incorporan antes la misma información" es correcta y prudente.
- **En contra:** la tesis interpreta JLoss como "el costo esperado de un rescate". Sin medir la garantía
  implícita ni la tenencia de bonos soberanos, esa lectura no se puede contrastar, y la tesis lo admite
  en la respuesta a los objetivos.

## 3.7 Estructura — 5,8
Mejoró con el anexo D. Desde la micro falta una subsección que describa la base a nivel de banco:
distribución de tamaños, concentración y DD por banco.

## 3.8 Reproducibilidad — 6,9
El motor está reimplementado y validado contra MATLAB, y los insumos están commiteados por banco. Un
punto fuerte que habilita todas las mejoras de abajo sin datos nuevos.

---

# 4. Plan de mejoras desde la microeconomía

Prioridad = impacto en la nota ÷ costo, con la defensa en la primera semana de diciembre de 2026. Cada
prueba nueva se preregistra en un commit propio antes de estimar, como en `preregistro_resiliencia.md`.

| # | Mejora | Impacto | Costo | ¿Antes de diciembre? |
|---|---|---|---|---|
| μ1 | Panel a nivel de banco | Alto | Medio (datos en el repo) | Sí |
| μ2 | Sensibilidad del motor a ρ, LGD y punto de incumplimiento | Alto | Bajo | Sí |
| μ3 | Garantías implícitas: estatales frente a privados, tamaño | Alto | Medio (clasificación a mano) | Sí |
| μ4 | Concentración con los mismos bancos y predicción de OI | Medio-alto | Medio | Sí, parcial |
| μ5 | Exposición soberana de los bancos como moderador | Muy alto | Alto (datos nuevos) | Parcial |
| μ6 | Bancos no cotizados y umbral de bancos mínimos | Medio | Bajo | Sí |
| μ7 | Disciplina de mercado: ¿la garantía distorsiona la DD? | Medio | Medio | No (paper) |

## μ1. Panel a nivel de banco (`p46_panel_bancos.py`)
- **Ataca:** 3.4 (no se usa la variación banco–trimestre) y 3.3 (la agregación).
- **Datos:** ya están. `Bloomberg_extraction/output/<país>/mktcap_*.csv` (diario) y `balance_*.csv`
  (trimestral), 113 bancos; la DD por banco sale de `jloss_engine.merton_pd` (como en `p34`/`p37`).
- **Método:**
  - (a) Sensibilidad de cada banco al spread:
    ΔDD_{b,t} = α_b + δ_{c(b),t} + β·(Δln EMBI_{c,t} × X_{b,t−1}) + γ'X_{b,t−1} + ε, con efectos fijos
    de banco y de país-trimestre. Los efectos de país-trimestre absorben todo choque común del sistema,
    incluido el propio spread, de modo que β se identifica solo por la diferencia entre bancos.
    X = tamaño relativo, apalancamiento, propiedad estatal (μ3) y exposición soberana (μ5).
  - (b) Contribución de cada banco al spread: ln EMBI_{c,t} sobre la DD de cada banco ponderada por su
    peso sistémico, con efectos fijos de país y de tiempo. Prueba si es la fragilidad de los bancos
    grandes la que se asocia con el spread.
  - Errores agrupados en dos dimensiones (banco y país-trimestre); wild bootstrap por país.
- **Hipótesis a preregistrar:**
  - μ1-H1: los bancos más grandes del sistema (los que el soberano rescataría) tienen una DD más
    sensible al spread (β > 0 en la interacción con tamaño relativo).
  - μ1-H2: la asociación del spread con la fragilidad proviene de los bancos sistémicos, no de los
    marginales.
- **Qué podría cambiar:** la conclusión sobre la fragilidad (hoy "réplica sugerente, dependiente de
  Turquía"). Daría un canal bancario identificado dentro del país, no solo entre países.

## μ2. Sensibilidad del motor (`p47_sensibilidad_motor.py`)
- **Ataca:** 3.3 (supuestos homogéneos y saturación).
- **Datos:** ya están (los mismos insumos del motor).
- **Método:** recalcular JLoss y la DD media con:
  - ρ banco por banco, estimada como la correlación del retorno del banco con el índice bursátil del
    país en una ventana de 2 años (el motor ya tiene el factor);
  - LGD = 25 %, 45 % y 65 %, y LGD por tipo de banco;
  - punto de incumplimiento con depósitos excluidos o ponderados (los depósitos asegurados no precipitan
    el incumplimiento);
  - la malla de pérdidas recalibrada para que no sature.

  Reestimar la regresión principal y la prueba preregistrada R-H3 con cada versión.
- **Hipótesis:** μ2-H1: el ordenamiento de la fragilidad (correlación de rangos > 0,8) y el signo de
  β₁ no dependen de ρ ni de la LGD.
- **Qué podría cambiar:** la defensa de la medida frente a la comisión. Si una calibración banco por
  banco elimina la saturación, JLoss vuelve a medir la parte inesperada que lo justifica.

## μ3. Garantías implícitas y propiedad (`p48_garantias.py`)
- **Ataca:** 3.2 (microfundamento del rescate) y 3.6 (interpretación de JLoss como costo de rescate).
- **Datos:**
  - Clasificación manual de los 113 bancos: estatal / privado nacional / subsidiaria extranjera.
    Fuentes: informes anuales y la base de propiedad bancaria del Banco Mundial (Bank Regulation and
    Supervision Survey). Unas horas de trabajo.
  - Tamaño relativo (activos sobre el PIB), ya en el balance.
- **Método:** construir el JLoss y la DD **por subgrupo** (estatales, privados nacionales, subsidiarias
  extranjeras) y estimar la regresión principal con los tres. Interacción del spread con la DD de los
  bancos con garantía implícita.
- **Hipótesis:**
  - μ3-H1: la fragilidad de los bancos estatales y de los grandes privados nacionales se asocia más con
    el spread que la de las subsidiarias extranjeras, cuyas pérdidas absorbería la matriz.
  - μ3-H2: en los sistemas con mayor peso de bancos estatales, la asociación es mayor.
- **Qué podría cambiar:** la interpretación de JLoss como pasivo contingente del soberano pasaría a ser
  contrastable, y no solo una lectura.

## μ4. Concentración con los mismos bancos y el modelo de OI (`p49_concentracion_oi.py`)
- **Ataca:** 3.2 (el modelo de Cournot eliminado) y la hipótesis H4b, que quedó sin identificar.
- **Datos:** ya están. `concentracion_trimestral_bbg.csv` (HHI de pasivos de los mismos bancos, `p6`) y
  el working paper del modelo en `4_Redaccion/modelo OI/`.
- **Método:**
  - Recuperar la predicción distintiva del modelo: la amplificación por concentración, es decir, que la
    fragilidad pesa más en el spread donde el sistema es más concentrado.
  - Contrastarla con un HHI medido con los mismos bancos que JLoss, rezagado y estandarizado.
  - Preregistrar la interacción fragilidad × HHI (y la triple con el riesgo de cola, como prueba
    secundaria). Inferencia por wild bootstrap y exclusión de países.
- **Hipótesis:** μ4-H1: la interacción fragilidad × HHI es positiva.
- **Qué podría cambiar:**
  - Si se confirma, la tesis recupera su arista de organización industrial con una predicción
    contrastada.
  - Si no, se reporta como predicción del modelo no respaldada, que es mejor que una frase en trabajos
    futuros.

## μ5. Exposición soberana de los bancos (`p50_exposicion_soberana.py`)
- **Ataca:** 3.2 y 3.4. Es el canal central de Farhi–Tirole (*home bias*), que la tesis cita y no mide.
- **Datos (nuevos):**
  - Tenencia de títulos del gobierno por banco: Bloomberg (campos de inversiones en valores del
    gobierno), informes de los supervisores (CMF en Chile, CNBV en México, BCB en Brasil) o, por país,
    la participación de los bancos domésticos en la deuda pública de la base de Arslanalp y Tsuda, ya en
    `2_Datos/Database_For_Posting_EM_Frozen.xlsx`.
  - Esta última es una opción inmediata a nivel país.
- **Método:** usar la exposición soberana de los bancos (en % de sus activos o del capital) como
  moderador de la transmisión, a nivel país y, si se consigue el dato, a nivel banco dentro del panel de
  μ1.
- **Hipótesis:** μ5-H1: la fragilidad se asocia más con el spread donde los bancos domésticos tienen más
  deuda soberana (*doom loop*).
- **Qué podría cambiar:** sería la primera prueba directa del canal del *doom loop* en la tesis. Si se
  confirma, sostiene la interpretación del mecanismo.

## μ6. Bancos no cotizados y umbral mínimo (`p51_cobertura_sistema.py`)
- **Ataca:** 3.3 (selección y agregación).
- **Datos:** la cobertura de los bancos cotizados sobre los activos totales del sistema, con los activos
  del sistema del Banco Mundial (GFDD) o de los supervisores.
- **Método:**
  - Reportar por país la participación de los bancos cotizados en los activos del sistema.
  - Reestimar excluyendo las economías con cobertura menor que un 50 %.
  - Variar el umbral de bancos mínimos (3, 4, 5).
- **Qué podría cambiar:** la validez de JLoss como medida del sistema en Colombia, Perú y Chile.

## μ7. Disciplina de mercado (paper)
- **Ataca:** 3.2 y 3.3. Si la garantía implícita es creíble, el precio accionario de los bancos grandes
  subestima su riesgo, y la DD de Merton está sesgada justo en los bancos que importan para el soberano.
- **Método:** comparar la DD con los spreads de los bonos bancarios o del CDS bancario, cuando existan
  en Bloomberg, por tamaño y propiedad.
- **Qué podría cambiar:** la credibilidad de las medidas basadas en el precio accionario para los
  sistemas con garantías fuertes.

---

**Ruta recomendada antes de diciembre:**
1. μ2 (1–2 días, sin datos nuevos).
2. μ1 (3–4 días, sin datos nuevos).
3. μ6 (1 día).
4. μ3 (2–3 días, con la clasificación manual).
5. μ4 con su preregistro (2 días).
6. μ5 a nivel país con Arslanalp–Tsuda (1–2 días); a nivel banco y μ7, para el paper.

**Nota esperada con μ1–μ4:** en torno a 6,5. La tesis pasaría de usar los bancos como insumo de un índice
a usarlos como unidad de análisis del mecanismo.

---

# 5. Registro de aplicación (22 de octubre de 2026)

Preregistro 3: `preregistro_micro.md`, commit `d73245f`, anterior a los datos a nivel de banco, con la
clasificación de propiedad fijada (`2_Datos/propiedad_bancos.csv`). El preregistro menciona 89 bancos; son
87, y se declara. Resultados en `b94c301` (μ1, μ3–μ6) y en el commit de μ2. Cifras en
`NUMEROS_CANONICOS_BBG.md`, §30; texto en la Sección `sec:micro-prereg` de la tesis y del paper.

| # | Estado | Resultado |
|---|---|---|
| μ1 | Hecho (preregistrado) | H1: 1,08, positivo sin cada país, wild p uni 0,21. H2: sistémicos 0,062 frente a 0,022; la diferencia no resiste (0,20). Holm 1,00 |
| μ2 | Hecho (preregistrado) | **Se cumple:** Spearman 0,92–0,97 y β₁ entre 0,087 y 0,150 con las tres variantes; con la malla ancha la interacción desaparece (0,001) |
| μ3 | Hecho (preregistrado) | Filiales = nacionales (−0,007); el peso estatal tiene el signo opuesto (−0,120). Holm 1,00 |
| μ4 | Hecho (preregistrado) | 0,101 con DK p = 0,001, pero wild 0,15 y Holm 0,88; el HHI varía poco dentro del país (14 %) |
| μ5 | Hecho (preregistrado) | −0,038, Holm 1,00; tenencia casi puramente transversal (96 % entre países) |
| μ6 | Hecho (secundaria) | Con ≥ 4 o 5 bancos la fragilidad pierde significancia (DK 0,22 / 0,15); el riesgo de cola la conserva. Cobertura de México, 34 % |
| μ7 | No factible | No hay spreads de bonos ni CDS bancarios en el repositorio; queda como trabajo futuro |

**Nota reestimada (misma rúbrica):**
- Contribución: 6,0 → 6,2. Los bancos pasan de insumo a unidad de análisis, aunque el resultado es nulo.
- Marco: 5,6 → 5,9. Las hipótesis micro (pasivo contingente, garantías, Cournot, *home bias*) quedan explícitas y contrastadas.
- Datos: 5,7 → 6,2. La medida resiste tres calibraciones del motor; se agregan la propiedad y la cobertura.
- Identificación: 5,5 → 5,7. Los efectos fijos de país-trimestre absorben todo choque común, incluido el spread.
- Inferencia: 6,7 → 6,8. La familia está preregistrada y corregida por Holm.
- Interpretación: 6,3 → 6,5. La tesis declara que el canal bancario no se demuestra y que el hallazgo central es macro.
- Estructura: 5,8 → 5,7. Hay más extensión (149 pp.).
- Reproducibilidad: 6,9, sin cambio.

**Nota ponderada: 6,2** (0,93 + 0,59 + 0,93 + 1,14 + 1,02 + 0,975 + 0,285 + 0,345).

La nota queda bajo el 6,5 esperado, que suponía que μ1–μ4 afinarían el mecanismo bancario. Las pruebas
están bien hechas y reportadas, pero no lo afinan. Para un microeconomista, lo que más pesa ahora es que la
medida es robusta (μ2) y que la tesis no sobrevende el canal bancario.
