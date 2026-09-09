# Plan — DAG + solidificación de la línea teórica (Cap. 3, modelo OI)

> Copia versionada en el repo: `4_Redaccion/modelo OI/Plan_Revision_Linea_Teorica_2026-09.md`
> (committeada 2026-09-09). Este archivo en `~/.claude/plans/` es la copia de trabajo;
> al avanzar, mantener ambas en sync o volcar aquí → repo antes de commitear.
>
> Agentes de exploración completados: empírico/pipeline ✔, calibración/borradores ✔,
> literatura ✔.

## Progreso — Bloque A + V9 standalones (2026-09-09) — HECHO Y PUSHEADO

Commits en `master` (subidos a `origin/main`, fast-forward):
`14d9982` (recap + salidas EDA bbg) · `1bcfc20` (Cap. 3: DAG, convención D, estimandos).
Upstream configurado: `master` → `origin/main`.

- **Deliverable 0 — HECHO.** Artifact: https://claude.ai/code/artifact/274b9c7c-56da-440e-8063-c9a314e298ed
  — incluye la revisión (V1–V10 + banco de preguntas) **y el DAG como SVG inline de tres capas**
  (estructural / causas comunes / retroalimentación), leyenda y pie con el argumento de V3.
- **Deliverable 1 — HECHO.** Figura TikZ `fig:dag` (Fig. 3.3) + subsección
  3.5.4 "El DAG del mecanismo" en `paper1_oi.tex`; SVG equivalente en el artifact.
  Requirió `\usepackage{tikz}` en `main.tex` y en `envios/paper_teorico/main.tex`,
  y `\shorthandoff{<>}` alrededor de la figura (babel-spanish hace activos `< >`).
- **V9 — box HECHO.** `\begin{mdframed}` "Convención de signos" al inicio del Cap. 3
  (tras "Relación con el Capítulo 2"). Auditoría del cuerpo de pruebas de los
  standalones = ver `## PENDIENTE` §B.
- **V7 — HECHO.** Subsección 3.5.3 "Qué estima cada coeficiente" + Cuadro `tab:estimandos`
  (Tabla 3.1) en `paper1_oi.tex`.
- **V10 — HECHO.** Subsección 2.6 "n como instrumento de política" (`sec:npolitica`) al final
  de §El modelo; enlazada desde §Identificación.
- **V3-A — HECHO.** Observación `rem:decouple` (Obs. 3.3) tras la Prop. 5: la derivada
  cruzada no depende del Canal I.
- **V5 — HECHO.** Párrafo de MDE + "predicción registrada del modelo" en §5.4 (H4b).
- **V9 standalones — HECHO (2026-09-09).** `modelo OI/working_paper.tex` y
  `modelo OI/apendice_matematico.tex` pasados a convención D≡−GaR
  (β₁,β₂ᴰ,β₃,β₄ > 0):
  - `working_paper.tex`: abstract, box "Convención de signos" (nuevo, `\usepackage{mdframed}`),
    Prop. 5 con el iff en D + Obs. `rem:decouple`, `eq:emp` a `multline` con `D`, captions
    `fase4_embi`/`fase5_montecarlo`, §MC (β₃=+0,80, β₄=+3,0), **§5.4 H4a/H4b reescrita a
    resultados Bloomberg** (θ=−0,16 full / β₃=+0,47 núcleo-11; **H4b NO identificado** —
    ya no dice "+721 confirma"), conclusión, y §Contribución/§Relación (JLoss×D).
  - `apendice_matematico.tex`: título, abstract, box con los 4 signos D + tabla D/GaR +
    nota de numeración (Prop. aquí 1–5 = 2–6 en la tesis), Prop. 4/5 con el iff en D,
    remarks reformulados, §Mapeo a D-primario.
  - Numeración de proposiciones: `apendice_matematico` conserva su contador propio
    (U = Prop 1), con nota explícita del offset frente a la tesis. Renumbrado completo
    (añadir prop. de existencia) queda como refinamiento menor.
- **Compila limpio (todo, 2026-09-09):** `tesis/main.tex` 89 pp · `working_paper.tex` 15 pp ·
  `apendice_matematico.tex` 7 pp · `envios/paper_teorico` 31 pp · `envios/paper_empirico` 44 pp.
  0 refs/citas indefinidas en todos.

**Lo que queda: ver "## PENDIENTE" más abajo (reemplaza a "Deliverable 5 — Secuenciación").**

## Context

El **Capítulo 3** de la tesis (`4_Redaccion/tesis/paper1_oi.tex` + Anexo A
`anexoA_matematico.tex`; standalones en `4_Redaccion/modelo OI/`) es un modelo
Cournot de competencia bancaria cuya cadena `n → JLoss → GaR → spread` produce la
interacción `JLoss × D` (D ≡ −GaR) que el Capítulo 2 estima sobre un panel
Bloomberg de 13 economías. En una revisión de esta sesión se identificaron 10
vulnerabilidades (V1–V10) y se preparó un banco de preguntas de comité. El
profesor revisa mañana la **línea teórica** y **espera ver avances escritos**.

Este plan: (0) deja la revisión previa en un artifact; (1) arma el DAG de la
investigación (narrativa + figura TikZ); (2) da un plan por vulnerabilidad;
(3) especifica la extensión de modelo E1 (depositantes activos + margen extensivo
de crédito + función de bienestar) que **entra en la tesis**; (4) detalla el
arreglo de convención de signos y las inconsistencias código/texto encontradas.

**Convención canónica de todo el plan:** `D ≡ −GaR`; signos predichos
`β₁>0, β₂ᴰ>0, β₃>0, β₄>0` (equivale a `θ = β₃ᴳᵃᴿ < 0`).

### Estado real encontrado (relevante para el plan)

- **`corr(JLoss, GaR q05) = −0,208`** (⇒ `corr(JLoss, D) ≈ +0,21`): moderada, no
  alta. Fuente: `1_Codigo/Panel/eda_output_bbg/matriz_correlaciones.csv`.
- **El vínculo `JLoss → GaR` NO se prueba en ninguna parte.** El motor de GaR
  (`1_Codigo/GaR/individuals/nlhpc_gar_all18/gar_engine.py`) condiciona en
  `g_GDP` rezagado, VIX y FCI⊥VIX — **no** en JLoss. JLoss y GaR se construyen
  independientes y se fusionan por país-trimestre.
- **`ρ` (correlación activo-factor) está FIJADA en 0,4** en el motor JLoss
  (`jloss_engine.py:52`, `RHO_FLAT`), no estimada ⇒ el dato NO tiene variación de
  `ρ`; la endogeneidad `ρ(n)` del modelo no tiene contraparte empírica hoy.
- **El placebo "design B"** (permutar GaR dentro de país) **filtra** (θ medio
  −0,27) porque "la posición transversal de GaR está correlacionada con la de
  JLoss y los EF bidireccionales no la absorben del todo → parte de la
  identificación proviene de covariación ENTRE países"
  (`NUMEROS_CANONICOS_BBG.md:520-523`). **Esto valida la preocupación de V3.**
- **Sin diagnóstico VIF** en el panel bbg canónico (histórico: máx 2,35).
- `1_Codigo/Plan_tablas_riesgo.md` ya tiene el análisis de canales distintos
  (Paneles A/B/C: `JLoss×GaR` sobrevive un horse-race vs `VIX×GaR`, `SRISK×GaR`)
  pero **sobre el panel viejo all17**, no el bbg.
- **Dos convenciones de signo vivas:** `tesis/paper1_oi.tex`, `anexoA`,
  `paper2_empirico.tex`, `main.tex`, `envios/*` → D (β₃>0). `modelo OI/
  working_paper.tex` y `apendice_matematico.tex` → GaR (β₃<0), y `working_paper`
  §5.4 **aún reporta H4b confirmada (+721)**. Los CSV canónicos
  (`bateria_bbg.csv`, `NUMEROS_CANONICOS_BBG.md`) siguen en `θ`.
- **Numeración de proposiciones divergente:** `apendice_matematico.tex` (U =
  Prop 1, amplificación = Prop 5 separada, sin prop de existencia) vs. tesis
  (existencia = Prop 1, U = Prop 2, amplificación dentro de Prop 5). Label
  `prop:gran` vs `prop:granular`.
- **`fase3_calibracion.py:14`** codea `x̄ = (R_L − r_D + k)/LGD` — NO la forma
  cerrada de Merton `x̄ = 1 − (1+r_D−e)/(1+R_L)` de `paper1_oi.tex:137`.
- **No hay código** para `fase4_embi.png`, `fase6_robustez.png`, ni para
  `Λ(JLoss)`, `B(JLoss;H)`, `F_η`, ni el bloque soberano — sólo prosa en los
  `Fase_IV/VI_*.md`. `B(JLoss;H) = b₀·JLoss·(1+b₁·H)`, `b₀=0,32`, `b₁=1,2`.
- **`mc_gar.py`** está commiteado con `R=1500`; los papers citan `R=3000`.
- Discrepancias texto/código adicionales: JLoss engine usa ρ=0,4 plano (texto
  dice ρ_i estimada); GaR ortogonaliza FCI⊥VIX (texto dice VIX⊥local).
- **No existe ningún DAG** en la tesis. Hay que construirlo de cero.
- `~/.claude/plans/adaptive-discovering-tarjan.md` = plan de árbitro senior
  (ya ejecutado en gran parte): H4b → "no identificado", batería de robustez,
  censura de JLoss corregida, series trimestrales de HHI, IV. Alinear con él.

---

## Deliverable 0 — Artifact con la revisión previa

Publicar como artifact (HTML de una columna, es-CL, reusar el sistema visual del
artifact `c7ccbe10`): resumen de la línea teórica, fortalezas, V1–V10, y el banco
de ~30 preguntas del profesor con respuestas. Archivo nuevo en scratchpad.
Cruzar con `4_Redaccion/Defensa_preguntas.md` (2026-09-01, 30 preguntas de
comité) para no duplicar y añadir las que falten.

---

## Deliverable 1 — El DAG de la investigación

Tres capas. Va como **figura TikZ nueva en el Cap. 3** (subsección "El DAG del
mecanismo y la estrategia de identificación", después de §Estrategia empírica) y
como **narrativa en el artifact**.

### 1a. Capa estructural (modelo)

```
POLÍTICA DE ENTRADA / COMPETENCIA (F: licencias, fusiones)        [V10]
      |
      v
      n ──────────────────────────────────────► rho(n)   [V1: rho'(n)<0 SUPUESTO;
      |  \                                         |       sin contraparte empírica]
      |   \--► R_L* --(risk-shift, Lema)--► p      |
      |         |                          |       |
      |         └--► x̄(R_L) (margen Keeley) |       |
      |                    \               v       |
      |                     └──► PD ──────► JLoss ◄─┴──── H = Σ λ_i²   [V8: ≠ 1/n
      └──► H ──────────────────────────────► JLoss        si asimetría; Prop. granular]
                                              |
                                    Canal I:  Λ(JLoss; H)   [V3/V4: hoy forma reducida;
                                              |              E1 lo endogeniza vía θ*(R_L)]
                                              v
                                    GaR   (D ≡ −GaR)
   JLoss ──► B(JLoss; H) ───┐                 |
                            v                 v   (g = GaR entra en d')
                   d' = (1+r)/(1+g)·d + B/Y ──┴──► DFL = d̄ − d'
                                                      |
        η ; κ (base inversora) ; b (backstop) ────────┤   [V2: κ, b = moderadores nuevos]
                                                      v
                            Spread = κ · LGD · (1 − F_η(DFL))
```

Derivadas firmadas: `β₁=∂S/∂JLoss`, `β₂ᴰ=∂S/∂D`, `β₃=∂²S/∂JLoss∂D`,
`β₄=∂³S/∂JLoss∂D∂H` (+ nuevas `∂²S/∂JLoss∂D` creciente en κ, decreciente en b).

### 1b. Capa de confusores / causas comunes (identificación Cap. 2)

- **Factores globales** (tasas EE.UU., VIX, apetito de riesgo) → {JLoss, GaR,
  Spread}: se absorben con `γ_t` (EF de tiempo). Chari et al. (2024) los pone al
  centro; aquí son ruido a controlar.
- **`Z` / condiciones financieras comunes** → {JLoss, GaR}: **origen de la
  correlación** `corr(JLoss,D)≈+0,21` y del "leak" del placebo B. Nodo clave para
  V3.
- **Fundamentos domésticos `X`** (deuda/PIB, balance fiscal, reservas, CA, infl,
  REER) → {JLoss, GaR, Spread}: omitidos en la batería tipo Chari; presentes en
  M2 (+6 controles). Confusor.
- **`α_i`** (heterogeneidad de país, incl. base inversora, régimen cambiario) →
  EF de país.

### 1c. Capa de retroalimentación NO modelada (el "loop" — V3)

`Spread → GaR` (costo de fondeo deprime crecimiento); `Spread → JLoss` (pérdidas
soberanas golpean bancos tenedores de deuda); `GaR → JLoss` (mal panorama
deteriora activos — inverso de Canal I); `Spread/crisis → n` (consolidación).
El modelo es una cadena unidireccional; el lazo dinámico es E1 (bloque soberano
de dos períodos, futuro) — declararlo explícito.

### 1d. Uso del DAG en el texto

- Justifica qué absorbe cada conjunto de EF y qué queda sin controlar.
- Muestra que `JLoss → Spread` tiene un camino que **no pasa por GaR**
  (`JLoss → B → DFL → Spread`) y `GaR → Spread` uno que no pasa por JLoss
  (`GaR → d' → DFL → Spread`) ⇒ **son canales distintos aunque `JLoss → GaR`
  exista** (núcleo del argumento de V3).
- Marca los caminos "back-door" abiertos (vía `Z`, vía `X`) y cómo se cierran.

---

## Deliverable 2 — Plan por vulnerabilidad

### V1 — `ρ'(n)<0` es supuesto, y no tiene contraparte empírica

1. Elevar Salop de "robustez" a **microfundamento del caso base** (o sección
   propia): más bancos ⇒ más diferenciación de nicho ⇒ `ρ'(n)<0` derivado.
2. Enunciar como **proposición** la condición de dominancia frente al canal de
   *herding* (Acharya–Yorulmazer 2007; Farhi–Tirole 2012): `ρ'(n)<0 ⟺
   [diferenciación] > [herding]`.
3. **Respaldo de literatura (nuevo):** la tensión está publicada y sin cerrar —
   Wagner (2010, *JFI*) deriva el trade-off diversificación individual ↑ vs.
   riesgo de cola conjunta ↑ (mecanismo idéntico al de `ρ(n)`); Anginer,
   Demirgüç-Kunt & Zhu (2014) hallan empíricamente **más competencia ⇒ menor
   co-dependencia / riesgo sistémico** (= evidencia de signo a favor de
   `ρ'(n)<0`); Allen–Babus–Carletti (2012) endogeniza la estructura de
   *commonality*. Ninguno lo deriva de conducta Cournot ⇒ ése es el aporte.
4. Texto honesto: el modelo colapsa a MMR si `ρ'=0` — ya está, reforzarlo.
5. **Agenda empírica de `ρ(n)`** (nueva subsección "qué mediría `ρ(n)`"):
   correlación de retornos de equity bancario dentro de país vs. nº de bancos
   cotizados / HHI, por país-año, con los datos Bloomberg que ya se tienen
   (`1_Codigo/Bloomberg_extraction/`; misma métrica que Anginer et al.).
   Regresión pequeña, factible ahora.
6. Nota de medición: el motor empírico usa `ρ=0,4` plano ⇒ decir explícitamente
   que la interacción `ρ(n)` es una predicción teórica sin test directo (a
   diferencia de la U y del mínimo desplazado, que sí se calibran).

### V2 — Moderador teórico (H) vs. empírico (financiamiento externo, crisis)

**Extensión del bloque soberano — la de mayor retorno.** Endogenizar los dos
moderadores que el dato SÍ identifica (`corr` documentada en
`p5_robustez_arbitro.py`, resultados en `NUMEROS_CANONICOS_BBG.md:166-189`).

1. **Base de inversores `κ`.** `Spread = κ·LGD·(1 − F_η(DFL))`, `κ∈(0,1]` =
   sensibilidad al riesgo del tenedor marginal de la deuda. `κ` alto = inversor
   de cartera extranjero (núcleo de 11 EM); `κ` bajo = mercado de deuda local
   profundo (Polonia, India). ⇒ `∂²Spread/∂JLoss∂D` escala con `κ`.
   **Nueva Proposición (5b):** la complementariedad es creciente en `κ`.
   Contraparte empírica: share de deuda pública en manos de no residentes
   (proxy disponible: IIF/BIS, o el criterio binario `CONV` ya usado).
2. **Respaldo oficial `b`.** Parámetro de backstop (swap lines Fed, RFI FMI, QE
   doméstico) que agrega masa a `F_η` / reduce `LGD` efectiva ⇒ en crisis con
   `b` alto, `f_η'(DFL) → 0` y la complementariedad se atenúa.
   **Nueva Proposición (5c):** decreciente en `b`. Contraparte: dummy de
   trimestres con línea swap activa / programa FMI (construible por país-trim).
3. `H` (concentración) queda como **tercer** moderador (β₄), no el único.
4. Formalizar el carácter **local** de la Prop. 5 (`DFL*>0`, `f_η'<0`; satura si
   `PD_sov→1`): la interacción sólo aparece en países en zona de riesgo
   intermedio → conecta con "se apaga en Chile (seguro) y en distress extremo".
5. **5b y 5c son testeables con el panel actual** ⇒ convierten el mismatch en
   "el modelo predice exactamente la heterogeneidad hallada". Nueva subsección
   empírica en el Cap. 3 (o fila en `p5_robustez_arbitro.py`).

### V3 — Causalidad de la cadena; `JLoss` y `GaR` como canales DISTINTOS

Objetivo del usuario: no asumir `JLoss → GaR`; mostrar que `GaR` no es un
re-etiquetado de `JLoss` sino un canal causal distinto.

**A. Desacoplar la Prop. 5 del Canal I (edición, `paper1_oi.tex` §Cierre).**
La derivada cruzada `∂²Spread/∂JLoss∂D` se obtiene con `JLoss` y `D` como
argumentos **separados** de `Spread` (vía `B` y vía `d'`) — **no requiere
`JLoss→GaR`**. Reescribir para que Prop. 5 no invoque el Canal I; presentar
Canal I como afirmación auxiliar respaldada por literatura (V4), no como eslabón
necesario. Rebaja el riesgo de "asumir esa causalidad".

**B. Batería de validez discriminante (nuevo `bbg/p9_discriminante.py`, o
extender `p5`).** Todo sobre el panel bbg canónico:
- Reportar `corr(JLoss, D) = +0,21` y la matriz de correlaciones completa de
  regresores (ya en `eda_output_bbg/matriz_correlaciones.csv` — llevar a tabla).
- **VIF y número de condición** de la matriz de diseño M3/M4 (hoy ausente).
- **Incremento anidado** M1→M3→M4: `JLoss` sobrevive a añadir `GaR` y viceversa
  (ya está en `bateria_bbg.csv` — hacerlo explícito como prueba de canales
  distintos, con ΔR²).
- **Ortogonalización:** `GaR = a + c·JLoss + GaR⊥`; re-estimar con `GaR⊥`.
  Si el coeficiente se mantiene, `GaR` aporta señal independiente de `JLoss`.
- **Horse-race** (portar Paneles B y C de `Plan_tablas_riesgo.md` al panel bbg):
  entre `{JLoss×D, VIX×D, SRISK×D}` sólo `JLoss×D` significativa; `JLoss×D`
  sobrevive junto a `JLoss×VIX`.
- **Determinantes de primera etapa distintos** (tabla lado a lado): `JLoss` ←
  balances bancarios Merton/KMV; `GaR` ← `g_GDP` rezagado + VIX + FCI⊥VIX.
  Por construcción no comparten insumos salvo VIX.
- **Placebo B — enfrentarlo, no esconderlo.** Documentar que parte de la
  identificación de `β₃` es transversal (covariación entre países de las
  posiciones de `JLoss` y `GaR`), reportar el estimador *within*-estricto
  (primeras diferencias o transformación de dos vías más agresiva) y mostrar que
  el resultado del **núcleo de 11** sobrevive.

**C. Dirección `JLoss → GaR` (opcional, evidencia sugestiva).** LP / Granger de
`GaR` ante innovaciones rezagadas de `ΔJLoss` con EF país+tiempo (nuevo bloque
pequeño en `p3_causal_fase5.py`, análogo a `local_projections` pero con DV=GaR).
Enmarcar como sugestivo, no identificación. Alternativa: **no** afirmar la
dirección y dejar Canal I como co-movimiento respaldado por literatura.

**D. Texto.** En `paper1_oi.tex` y `discusion_general.tex`: Canal I baja de
"mecanismo estructural" a "eslabón con respaldo en la literatura"; la
contribución firmada queda en la derivada cruzada.

### V4 — Anclar los eslabones en literatura publicada

Nueva subsección "Relación con la literatura, eslabón por eslabón" en el Cap. 3
+ tabla "Respaldo de cada eslabón". **Eslabones CITABLES (no derivar, sólo
citar):**

| Eslabón | Estatus | Citas |
|---|---|---|
| Condiciones financieras/crédito → GaR (predictivo) | muy establecido | Adrian–Boyarchenko–Giannone (2019, *AER*); IMF GFSR (2017); Figueres–Jarociński (2020); Brownlees–Souza (2021) como *caveat* |
| Condiciones financieras → GaR (**causal**) | establecido (1 paper limpio) | Adrian–Grinberg–Liang–Malik–Yu (2022, *AEJ:Macro*, GIV); Aikman et al. (2019) — capital bancario **mitiga** el GaR |
| Contracción de crédito bancario → producto (causal) | muy establecido | Chodorow-Reich (2014); Amiti–Weinstein (2018); Peek–Rosengren (2000); Huber (2018); **Baron–Verner–Xiong (2021)** — caída de *equity* bancario (≈ objeto tipo JLoss) → contracción de crédito y output persistente |
| Crisis bancaria → pérdida de producto persistente | muy establecido | Cerra–Saxena (2008); Reinhart–Rogoff (2009); Laeven–Valencia (2013/2020) |
| Menor crecimiento / menos espacio fiscal → mayor spread/PD | establecido (teoría+empírico) | **Ghosh et al. (2013)**; **Bi (2012)** — *spread* **convexo** cerca del límite fiscal (= el carácter local + saturación de la Prop. 5); Collard–Habib–Rochet (2015); Arellano (2008); Hilscher–Nosbusch (2010) |
| Rescate de pérdidas del sistema → mayor spread soberano | establecido | **Acharya–Drechsler–Schnabl (2014)** (el más cercano a `B(JLoss;H)→spread`); Bova et al. (2016) para magnitudes (rescates financieros hasta ~40% PIB) |
| Factores globales dominan el spread EM; sensibilidad moderada por fortaleza del país | establecido | Longstaff et al. (2011); **Csontó–Ivaschenko (2013)** (fundamentos moderan la sensibilidad al riesgo global = paralelo estructural de κ y H); Chari et al. (2024) |
| Diversificación → menor PD individual pero **mayor cola conjunta** | mecanismo establecido | **Wagner (2010, *JFI*)**; Ibragimov–Jaffee–Walden (2011); Allen–Babus–Carletti (2012); Cai et al. (2018) |
| Λ no lineal (crunch con umbral de capital de intermediario) | respaldo teórico | He–Krishnamurthy (2013); Adrian–Boyarchenko–Giannone (2021, multimodalidad) |

**Eslabones NOVEDOSOS (el aporte de la tesis — usar los "primos" para
argumentar que cada paso es plausible y disciplinado, no arbitrario):**
(a) `ρ(n)` derivada de conducta Cournot; (b) el mapa `Λ: JLoss → GaR` con un
objeto Merton/Vasicek como condicionante del cuantil de crecimiento;
(c) meter `JLoss(n,H)` en un *schedule* de límite fiscal `DFL → spread`;
(d) la derivada cruzada `∂²spread/∂JLoss∂D` amplificada por `H`. **Ningún paper
estima una interacción fragilidad × GaR moderada por concentración** ⇒ el objeto
empírico es nuevo.

Acciones: (1) poblar `refs.bib` del Cap. 3 con estas citas; (2) reescribir
§Literatura relacionada distinguiendo "citable" vs. "aporte"; (3) para Canal I
citar Adrian et al. (2022) + Baron–Verner–Xiong (2021) en vez de derivarlo.

### V5 — La predicción distintiva (β₄) no es testeable con potencia

Alinear con `adaptive-discovering-tarjan.md` (que ya movió H4b a "no
identificado").
1. **Reencuadre de la venta** (`paper1_oi.tex` resumen, §5.4, conclusión;
   `envios/README.md:58` ya lo pide): el resultado central del Cap. 3 es
   **Prop. 3** (deductiva) + signo/forma de H4a + **Prop. 5b/5c** (κ, backstop —
   testeables). β₄ = "predicción registrada, requiere corte transversal mayor".
2. **MDE formal** de β₄ dado N=13, T, nº de clusters — decir qué muestra haría
   falta (la barrida MC de `mc_gar.py` sugiere ~6000 obs). Añadir al Cap. 3.
3. **Identificación transversal alternativa:** colapsar a medias de país,
   regresionar la pendiente país-específica `JLoss×D` sobre la concentración de
   país (13 puntos, scatter / between-estimator). Nuevo, transparente.
4. **Ampliar el panel** (Argentina/Rusia): implementar la vía **IES** de
   Bloomberg (bono soberano 5A como sustituto del 10Y ausente) para cerrar el
   hueco de GaR — acción pendiente ya acordada con Juan
   (`correo_juan_pato.md:25,87`). Rusia ya está en el pool cuantílico de GaR
   (`gar_panel_all18.csv`). Más varianza transversal de HHI para β₄.
5. Proxy de concentración con más dispersión: nº de bancos cotizados por país,
   o el `n` implícito del modelo calibrado por país (numbers-equivalent HHI).

### V6 — Sin función de bienestar  →  cubierto por E1 (Deliverable 3)

La función de bienestar es un producto de la extensión E1. Ver Deliverable 3.
Independiente de E1, añadir ya: la implicancia de política de la Prop. 3
("sistema subóptimamente concentrado") se enuncia hoy sin planificador — marcar
en el texto que es una comparación de minimizadores (`n_J` vs `n_PD`), no un
óptimo de bienestar, hasta que E1 lo cierre.

### V7 — Definir explícitamente qué objeto es cada β

Nueva subsección + tabla en el Cap. 3 (`paper1_oi.tex` §Estrategia empírica),
para cada `β_k`: (a) derivada estructural; (b) estimando empírico (qué cantidad
poblacional, qué se mantiene fijo); (c) supuestos de identificación; (d) caveat.

Contenido:
- `β₁` = efecto **directo** de `JLoss` sobre el spread, **neto del canal de
  credit crunch** (porque `GaR` está en la ecuación). Efecto **total** =
  `β₁ + β₂ᴰ·(∂D/∂JLoss)`. Añadir descomposición de mediación (pequeña, usa el
  `−0,8·HHI·JL` de la forma reducida del MC como referencia de `∂D/∂JLoss`).
- `β₂ᴰ` = efecto de `D` manteniendo `JLoss` fijo (canal límite fiscal puro).
- `β₃` = cambio en el efecto marginal de `JLoss` por punto de `D`
  (complementariedad); estimando = `E[∂²Spread/∂JLoss∂D | α_i, γ_t]`.
- `β₄` = cambio de `β₃` con la concentración; identificado de la varianza
  transversal de HHI (por eso no se identifica con 13 países).
- Notación potential-outcomes / `do(·)`; enlazar con el DAG (Deliverable 1).
- Nombrar que `JLoss` y `GaR` son **regresores generados** (Merton+saddlepoint;
  regresión cuantílica) ⇒ SE subestimados; remitir a la robustez de regresor
  generado ya hecha (`p5_robustez_arbitro.py:249`).

### V8 — `n` simétrico (modelo) vs. `HHI` (dato)

1. **Relajar simetría** en el modelo: tamaños `λ_i` heterogéneos ⇒
   `H = Σλ_i²` objeto genuino ≠ `1/n`. El Anexo A ya escribe
   `Var(L_sys|Z) = Σλ_i² q(1−q) = H·q(1−q)` (`anexoA_matematico.tex:88`) —
   completar la Prop. granular con `λ_i` heterogéneos y mostrar que la Prop. 3
   (shift) sobrevive a un *mean-preserving spread* de tamaños.
2. **Mapeo explícito modelo↔dato:** `n_efectivo = 1/HHI` (numbers-equivalent).
   Usarlo como contraparte empírica de `n`. Documentar en el §Estrategia
   empírica del Cap. 3.
3. Lerner/Boone = **conducta, no estructura** ⇒ sólo robustez (ya así en
   `fase5_robustez_concentracion.py`; hacerlo explícito en texto).
4. **Check transversal modelo↔dato:** resolver el modelo al `n_efectivo` de cada
   país (calibración por país) y comparar el ranking de `JLoss` predicho con el
   estimado (`diag_por_pais_bbg.csv`). Nuevo, pequeño, muy visual.
5. Nota: el motor empírico usa `ρ=0,4` plano ⇒ el canal "granularidad" y el
   canal "correlación" no se separan ni en el modelo simétrico ni en el dato;
   declarar la limitación.

### V9 — Arreglar el signo según la convención D  (detalle en Deliverable 4)

### V10 — Definir qué mueve `n`

1. Adoptar **Salop con entrada libre** como base de las comparativas estáticas:
   `n* = √(t/F)`, `F` = costo de entrada / barrera de licenciamiento. Ya está en
   robustez (`paper1_oi.tex:304`); subirlo a sección propia.
2. Instrumento de política = `F` (régimen de licencias, capital mínimo para
   operar, restricciones a sucursales, entrada de banca extranjera) **o** un
   regulador de competencia que elige `n` s.a. beneficio ≥ 0 (bloqueo de
   fusiones, topes de concentración).
3. **Nueva subsección "n como instrumento de política":** las comparativas
   estáticas en `n` trazan el efecto de una política de entrada/competencia.
4. **Puente con identificación:** episodios de entrada/desregulación por política
   = el "instrumento de competencia" que el Cap. 3 menciona y nunca implementa
   (`paper1_oi.tex:272,321`). Listar episodios candidatos para los 13 países
   (liberalización de banca extranjera, olas de fusiones, nuevas licencias).
5. E1 cierra esto del todo: con mercado de depósitos completo, `n*` sale de
   beneficio cero y `F` / los parámetros del seguro de depósitos son la palanca.

---

## Deliverable 3 — Extensión E1: depositantes activos + margen extensivo + bienestar

**Confirmado en alcance por el usuario.** Nunca existió un bloque de depositantes
ni análisis de bienestar en ningún borrador (`modelo OI/*`, archive). Es
genuinamente nuevo. Cubre V6, ayuda V3/V4 (endogeniza Canal I), ayuda V10, y
da un segundo microfundamento para V1.

### E1.1 Nueva secuencia (5 etapas)

| # | Etapa | Cambio |
|---|---|---|
| 0 | **Depositantes** reparten riqueza `W` entre activo seguro (`r_f`) y depósitos en el banco `i` según `r_D^i` y el riesgo percibido del banco. Seguro de depósitos cubre fracción `κ_I` de las pérdidas (`κ_I=1` ⇒ modelo actual; `κ_I<1` ⇒ prima de riesgo). Oferta de depósitos `S_i(r_D^i, PD_i, {r_D^j})`. | **NUEVO** |
| i | `n` fijado por política de entrada (`F`). | igual (V10) |
| ii | Bancos compiten Cournot en `l_i` **y** fijan `r_D^i`; se vacían el mercado de crédito (`R_L`) y el de depósitos. La hoja de balance liga: depósitos financian `(1−e)·l_i`. | **EXTENDIDO: `r_D` endógeno, creciente en `L`** |
| iii | Proyectistas heterogéneos en calidad `θ ∼ G(θ)`; toma crédito quien `E[pago] ≥` opción externa ⇒ **proyectista marginal `θ*(R_L)`** y demanda `L^d(R_L)=1−G(θ*)`. | **NUEVO: margen extensivo** |
| iv | `Z`, defaults, quiebras bancarias, pago del seguro, costo fiscal `B`. | igual |
| v | Cierre macro-soberano (GaR, límite fiscal, spread). | igual |

### E1.2 Qué resuelve

- **V6 — función de bienestar:**
  `W(n) = ∫ ExcedenteProyectista(θ) dG + U_dep(r_D, riesgo) − ψ·E[B(JLoss;H)]`.
  Planificador elige `n` (vía `F`) para maximizar `W`.
  **Nueva Proposición (E1-1):** orden de `n_W` vs. `n_J` (min `JLoss`) vs. `n_PD`
  (min fragilidad individual). Hipótesis: `n_W ≥ n_J` porque el bienestar valora
  también acceso al crédito, que crece en `n`.
- **V3/V4 — Canal I endógeno:** tras la pérdida sistémica `L_sys`, cae el capital
  bancario ⇒ contrae capacidad de préstamo ⇒ sube `R_L` ⇒ sube `θ*` ⇒ menos
  proyectos financiados. Eso **ES** `Λ`:
  `GaR = μ − φ·[L^d(R_L^{normal}) − L^d(R_L^{post-loss})]`, ahora derivado, no
  postulado. `∂Λ/∂H > 0` sale de que en sistemas concentrados la pérdida de
  capital por evento es mayor (hereda Prop. granular).
- **V10 — `n*` bien definido:** entrada libre por beneficio cero con mercado de
  depósitos completo ⇒ `F` y los parámetros del seguro de depósitos mueven `n`.
- **V1 — segundo microfundamento:** si `κ_I<1`, depositantes huyen de bancos con
  carteras correlacionadas ⇒ disciplina de mercado que puede reforzar o
  contrarrestar `ρ(n)`; el modelo da la condición.

### E1.3 Cierre tratable (caso base para forma cerrada)

- Depositante **media-varianza** (o CRRA log); `G(θ)` **uniforme** ⇒ `L^d(R_L)`
  lineal. Todo lo demás (Cournot en préstamos, Vasicek, `JLoss`, bloque
  soberano) **intacto**.
- Verificar: casos límite (`κ_I=1`, `G` degenerada ⇒ colapsa al modelo actual);
  existencia/unicidad del equilibrio de dos mercados (condición de diagonal
  dominante en el jacobiano de mejores respuestas).
- Calibración numérica nueva (script `modelo OI/fase7_deposito_bienestar.py`):
  `S_i`, `L^d`, `W(n)`, `n_W` vs `n_J` vs `n_PD`.

### E1.4 Literatura

Etapa de depositante como decisión activa (todo establecido):
**Hellmann–Murdock–Stiglitz (2000, *AER*)** — competencia por tasa de depósito
erosiona *franchise value* e induce *gambling* (núcleo teórico); **Matutes–Vives
(2000, *EER*)** — competencia por depósitos ⇒ tasas excesivas ⇒ mayor riesgo de
quiebra; **Egan–Hortaçsu–Matvos (2017, *AER*)** — depositantes no asegurados
retiran cuando sube el *distress* del banco (contraparte empírica, modelo de
demanda estructural, equilibrios múltiples con corridas); Diamond–Dybvig (1983);
Calomiris–Kahn (1991); Diamond–Rajan (2001); Allen–Carletti–Marquez (2011)
para disciplina por el lado del activo. **Ninguno cierra la cadena hasta el
spread soberano** ⇒ ése es el aporte de meter el bloque de depositantes en E1.

### E1.5 Alcance / riesgo

Es el mayor aumento de scope. Fallback si el equilibrio de dos mercados se vuelve
intratable: **versión intermedia** — sólo `r_D(p)` endógeno (ya señalado en
`rem:riskfunding`) + `L^d(R_L)` con `G` uniforme + bienestar estático, sin
elección de cartera del depositante. Decidir en la marcha; llevar ambas a la
reunión.

---

## Deliverable 4 — Convención de signos (V9) + inconsistencias código/texto

### 4a. Convención de signos — `D ≡ −GaR` en todo

| Archivo | Estado hoy | Acción |
|---|---|---|
| `tesis/paper1_oi.tex` | álgebra en GaR, mapa empírico en D (β₃>0) | auditar cada enunciado de signo; Prop. 5 en D; captions `fase4_embi` en D |
| `tesis/anexoA_matematico.tex` | headline D, derivación GaR + tabla D/GaR | mantener; los resultados "boxed" finales todos en D |
| `tesis/paper2_empirico.tex` | ya en β₃=−θ (D) | verificar consistencia; nota al pie ya explica el ×(−1) |
| `tesis/main.tex`, `introduccion_general.tex`, `discusion_general.tex` | D | verificar |
| `modelo OI/working_paper.tex` | **GaR (β₃<0); §5.4 aún con H4b +721** | reescribir a D + resultados actuales (H4b no identificado). Sincronizar con `paper1_oi.tex` |
| `modelo OI/apendice_matematico.tex` | **GaR primitivo, sin tabla D** | reescribir headline a D; añadir tabla D/GaR como en `anexoA`. Unificar numeración de proposiciones con la tesis (existencia = Prop 1; amplificación dentro de Prop 5; `prop:granular`) |
| `NUMEROS_CANONICOS_BBG.md`, `bateria_bbg.csv` | `θ` (GaR) | **no reconvertir el CSV**; añadir columna/README de convención y `β₃ = −θ`. La prosa cita en D |
| figuras `fase4_embi`, `fase5_montecarlo` | generadas en GaR | regenerar ejes y valores β en D (requiere reconstruir el código faltante — ver 4c) |

Un solo box **"Convención de signos"** al inicio del Cap. 3, referenciado en
todo. `grep` de `\GaR` en contexto de signo ⇒ 0 inconsistencias.

### 4b. Sincronización tesis ↔ standalones

`CONTROL_DE_VERSIONES.md:152` obliga: toda corrección de fondo en
`modelo OI/working_paper.tex` / `apendice_matematico.tex` se replica en
`tesis/paper1_oi.tex` / `anexoA_matematico.tex` (y viceversa). El usuario pide
mantenerlos sincronizados. `envios/paper_teorico/main.tex` ya hace `\input` de
las fuentes de tesis ⇒ se actualiza solo.

### 4c. Inconsistencias código/texto a resolver (bonus)

1. **`x̄` (umbral de quiebra):** `fase3_calibracion.py:14` usa
   `x̄=(R_L−r_D+k)/LGD`; el texto usa la forma cerrada de Merton
   `x̄=1−(1+r_D−e)/(1+R_L)`. Decidir cuál es canónico, alinear código y texto.
2. **Código faltante:** escribir `modelo OI/fase4_soberano.py` (genera
   `fase4_embi.png` con `Λ`, `B(JLoss;H)=b₀·JLoss·(1+b₁·H)`, `F_η`) y
   `fase6_robustez.py`. Hoy sólo existen en prosa de los `Fase_*.md`.
3. **`mc_gar.py`:** subir `R` de 1500 a 3000 (lo que citan los papers) y
   re-generar, o corregir el texto a 1500. Añadir la variante en convención D.
4. **`ρ` en `jloss_engine.py`:** texto dice "ρ_i estimada", código usa `ρ=0,4`
   plano. Corregir el texto del Cap. 2 (fuera de la línea teórica, pero
   relevante para V1/V8).
5. **GaR ortogonalización:** texto dice "VIX⊥local", código hace "FCI⊥VIX".
   Corregir el texto del Cap. 2.
6. Proposición 1 (existencia) falta en `apendice_matematico.tex` — añadir.

---

## PENDIENTE

> Bloque A + V9 (tesis y standalones) están HECHOS y pusheados (ver "## Progreso").
> La prioridad exacta puede cambiar según lo que diga el profesor en la reunión.
> El "cómo" de cada ítem está en el "Deliverable 2 — Plan por vulnerabilidad" y en
> los "Deliverable 3/4" de este mismo documento.

### B — Edición de texto (sin cómputo nuevo)

- [ ] **V1 — Salop a caso base.** Subir la extensión Salop de §Robustez a
  microfundamento del caso base (o sección propia); enunciar como proposición la
  condición de dominancia diferenciación vs. *herding* (Acharya–Yorulmazer 2007,
  Farhi–Tirole 2012); citar Wagner (2010, *JFI*), Anginer–Demirgüç-Kunt–Zhu (2014),
  Allen–Babus–Carletti (2012). `paper1_oi.tex` §Robustez + §sistémico.
- [ ] **V4 — literatura eslabón por eslabón.** Nueva subsección + tabla "Respaldo
  de cada eslabón" (contenido ya redactado en el Deliverable 2 · V4). Poblar el
  `\begin{thebibliography}` del Cap. 3 con: Adrian-Boyarchenko-Giannone 2019,
  Adrian-Grinberg-Liang-Malik-Yu 2022, Aikman et al. 2019, Chodorow-Reich 2014,
  Amiti-Weinstein 2018, Baron-Verner-Xiong 2021, Cerra-Saxena 2008, Bi 2012,
  Collard-Habib-Rochet 2015, Bova et al. 2016, Csontó-Ivaschenko 2013,
  Wagner 2010, He-Krishnamurthy 2013. Bajar el Canal I a "eslabón con respaldo
  en literatura".
- [ ] **V6 — nota de planificador.** Marcar en el texto de la Prop. 3 y en la
  §implicancias de política que "subóptimamente concentrado" hoy es una comparación
  de minimizadores (`n_J` vs `n_PD`), no un óptimo de bienestar — hasta que E1 lo cierre.
- [ ] **V8 — mapeo `n ↔ HHI`.** Añadir en §Estrategia empírica: `n_efectivo = 1/HHI`
  (numbers-equivalent) como contraparte empírica de `n`; declarar explícitamente que
  Lerner/Boone son conducta (solo robustez) y que con `ρ` empírica plana (0,4) los
  canales granularidad y correlación no se separan.
- [ ] **Portar a `modelo OI/working_paper.tex`** lo que ya está en la tesis pero
  falta en el standalone: figura DAG (§3.5.4), Cuadro de estimandos (§3.5.3),
  subsección "n como instrumento de política" (§2.6). Requiere `\usepackage{tikz}`
  + `\usetikzlibrary{arrows.meta,positioning}` (sin babel ⇒ sin `\shorthandoff`).
- [ ] **`apendice_matematico.tex` — renumbrado completo** (opcional): añadir la
  proposición de existencia como Prop. 1 y unificar con la tesis. La nota de
  numeración ya evita la confusión; es refinamiento menor.
- [ ] **Sincronía inversa:** cuando se editen `working_paper.tex` /
  `apendice_matematico.tex`, reaplicar en `paper1_oi.tex` / `anexoA_matematico.tex`
  (regla `CONTROL_DE_VERSIONES.md:152`). `envios/paper_teorico` hereda vía `\input`.

### C — Trabajo analítico nuevo (derivaciones + cómputo)

- [ ] **V2 — Prop. 5b (κ) y 5c (backstop).** Derivar en el bloque soberano:
  `Spread = κ·LGD·(1−F_η(DFL))`, κ = sensibilidad del tenedor marginal (Prop. 5b:
  complementariedad creciente en κ); parámetro de backstop `b` que aplana `f_η`
  (Prop. 5c: decreciente en b). + Formalizar el carácter LOCAL de la Prop. 5.
  Anexo A: demostraciones. Contrapartes empíricas: share de deuda en no residentes
  (o el binario `CONV`), dummy trimestre-país de swap line / programa FMI.
- [ ] **V2 — test empírico de 5b/5c** (extender `bbg/p5_robustez_arbitro.py` o
  `p9` nuevo): interacción `JLoss×D` moderada por κ y por `b`. Ambas testeables
  con el panel actual.
- [ ] **V3-B — batería de validez discriminante** (`bbg/p9_discriminante.py`):
  matriz de correlaciones a tabla · VIF y nº de condición de M3/M4 · incremento
  anidado M1→M3→M4 con ΔR² · ortogonalización `GaR = a + c·JLoss + GaR⊥` y
  re-estimación con `GaR⊥` · horse-race (portar Paneles B/C de
  `1_Codigo/Plan_tablas_riesgo.md` al panel bbg: `JLoss×D` vs `VIX×D`, `SRISK×D`) ·
  tabla de determinantes de 1ª etapa lado a lado · **enfrentar el leak del
  placebo-B** (identificación parcialmente transversal) con un estimador
  *within*-estricto y mostrando que el núcleo-11 sobrevive.
- [ ] **V3-C — dirección `JLoss → GaR`** (opcional): LP/Granger de `GaR` ante
  `ΔJLoss` rezagado con EF país+tiempo (bloque nuevo en `p3_causal_fase5.py`,
  análogo a `local_projections` con DV=GaR). Enmarcar como sugestivo, no
  identificación. Alternativa: no afirmar la dirección.
- [ ] **V5 — β₄.** MDE formal dado N=13/T/nº clusters (añadir al Cap. 3) ·
  identificación transversal alternativa (colapsar a medias de país, regresionar
  la pendiente `JLoss×D` país-específica sobre HHI de país — 13 puntos /
  between-estimator) · proxy de concentración con más dispersión (nº bancos
  cotizados; `n` calibrado por país).
- [ ] **V5 / datos — IES para Argentina y Rusia.** Bajar de Bloomberg el bono
  soberano a 5A vía IES como sustituto del 10Y ausente para cerrar el hueco de
  GaR (acordado con Juan, `correo_juan_pato.md:25,87`). Rusia ya está en
  `gar_panel_all18.csv`. Da varianza transversal a β₄.
- [ ] **V8 — re-derivación con `λ_i` heterogéneos.** Completar la Prop. granular
  con tamaños asimétricos (`Var(L_sys|Z)=Σλ_i²·q(1−q)`, ya escrito a medias en
  `anexoA_matematico.tex:88`); mostrar que la Prop. 3 (shift) sobrevive a un
  *mean-preserving spread* de tamaños. + check transversal: resolver el modelo al
  `n_efectivo` de cada país y comparar el ranking de `JLoss` con
  `diag_por_pais_bbg.csv`.
- [ ] **V1 — regresión `ρ(n)`.** Correlación de retornos de equity bancario
  dentro de país vs. nº de bancos cotizados / HHI, por país-año, con los datos
  de `1_Codigo/Bloomberg_extraction/` (misma métrica que Anginer et al.).
- [ ] **4c — código faltante y discrepancias código/texto:**
  - `fase3_calibracion.py:14` usa `x̄=(R_L−r_D+k)/LGD`; el texto usa la forma
    cerrada de Merton `x̄=1−(1+r_D−e)/(1+R_L)`. Decidir cuál es canónica y alinear.
  - Escribir `modelo OI/fase4_soberano.py` (genera `fase4_embi.png` con `Λ`,
    `B(JLoss;H)=b₀·JLoss·(1+b₁·H)`, `b₀=0,32`, `b₁=1,2`, `F_η`) y
    `fase6_robustez.py` — hoy solo existen en prosa de los `Fase_*.md`.
  - `mc_gar.py`: subir `R` de 1500 a 3000 (lo que citan los papers) + variante
    en convención D; regenerar `fase5_montecarlo.png` con ejes/valores en D.
  - Regenerar `fase4_embi.png` con ejes y valores β en convención D.
  - Texto del Cap. 2 (fuera de la línea teórica): `jloss_engine.py` usa `ρ=0,4`
    plano, no "ρ_i estimada"; el motor GaR ortogonaliza `FCI⊥VIX`, no "VIX⊥local".

### D — Extensión E1 (entra en la tesis; el bloque más grande)

Depositantes activos (etapa 0) + margen extensivo de crédito (etapa iii) +
`r_D` endógeno + función de bienestar. Detalle en "Deliverable 3".

- [ ] Reescribir la secuencia/*timing* del modelo (§El modelo) a 5 etapas.
- [ ] Derivar el bloque de depositantes (media-varianza o CRRA log; seguro `κ_I`;
  oferta `S_i`) y el margen extensivo (`θ ∼ G` uniforme ⇒ `L^d(R_L)` lineal).
- [ ] Endogeneizar `r_D` vía vaciado del mercado de depósitos.
- [ ] Función de bienestar `W(n) = ∫ Exc.Proyectista dG + U_dep − ψ·E[B]` +
  **Prop. E1-1** (orden `n_W` vs `n_J` vs `n_PD`).
- [ ] Verificar casos límite: `κ_I=1` y `G` degenerada ⇒ colapsa al modelo actual;
  existencia/unicidad del equilibrio de dos mercados (diagonal dominante del
  jacobiano de mejores respuestas).
- [ ] `modelo OI/fase7_deposito_bienestar.py` (calibración: `S_i`, `L^d`, `W(n)`,
  `n_W`).
- [ ] Cerrar el Canal I: derivar `Λ` del colapso de capital → `R_L` ↑ → `θ*` ↑ →
  menos proyectos (endogeniza la forma reducida de V3/V4).
- [ ] Literatura E1 en `refs.bib`: Hellmann-Murdock-Stiglitz 2000, Matutes-Vives
  2000, Egan-Hortaçsu-Matvos 2017, Diamond-Rajan 2001, Calomiris-Kahn 1991,
  Allen-Carletti-Marquez 2011.
- [ ] **Fallback** si el equilibrio de dos mercados se vuelve intratable: solo
  `r_D(p)` endógeno + `L^d(R_L)` con `G` uniforme + bienestar estático, sin
  elección de cartera del depositante.

### E — Mantenimiento

- [ ] Si E1 cambia la estructura (nueva etapa de depositante / margen extensivo),
  actualizar el DAG en `paper1_oi.tex` **y** en el artifact.
- [ ] Registrar cada avance en `CONTROL_DE_VERSIONES.md` §5 y trazar todo número
  nuevo a `NUMEROS_CANONICOS_BBG.md`.
- [ ] Recompilar los 5 documentos y verificar 0 refs/citas indefinidas antes de
  cada commit.

---

## Archivos críticos

**Prosa teórica:**
`4_Redaccion/tesis/paper1_oi.tex`, `.../anexoA_matematico.tex`,
`.../discusion_general.tex`, `.../introduccion_general.tex`, `.../main.tex`;
`4_Redaccion/modelo OI/working_paper.tex`, `.../apendice_matematico.tex`.

**Código teórico / calibración:**
`4_Redaccion/modelo OI/fase3_calibracion.py`, `mc_gar.py`; nuevos
`fase4_soberano.py`, `fase6_robustez.py`, `fase7_deposito_bienestar.py`.

**Pipeline empírico (para V3/V5/V2):**
`1_Codigo/Panel/bbg/{p2_regresiones,p3_causal_fase5,p5_robustez_arbitro,
p8_bateria_regresiones}.py`, nuevo `p9_discriminante.py`;
`1_Codigo/Panel/causal_core.py`; `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`.
Reutilizar: `linearmodels.PanelOLS` + Driscoll–Kraay, `wild_boot()`,
`umbral_hansen()`, `local_projections` (ya montados).

**Docs de gobierno (leer antes de editar):**
`4_Redaccion/CONTROL_DE_VERSIONES.md` §5 (números oficiales),
`4_Redaccion/modelo OI/Plan_Arista_OI_Competencia_Fragilidad.md`,
`~/.claude/plans/adaptive-discovering-tarjan.md`,
`4_Redaccion/Defensa_preguntas.md`,
`1_Codigo/Panel/Plan_tablas_riesgo.md` (Paneles A/B/C a portar).

**Números:** ninguno entra a la prosa sin trazarse a `NUMEROS_CANONICOS_BBG.md`
(regla de `CONTROL_DE_VERSIONES.md`). Registrar esta revisión en su §5.

---

## Verificación

**Ya cumplido (Bloque A + V9):**
- [x] `latexmk` de los 5 documentos → exit 0, 0 refs/citas indefinidas,
  0 overfull >10pt (`tesis` 89 pp · `working_paper` 15 · `apendice_matematico` 7 ·
  `paper_teorico` 31 · `paper_empirico` 44).
- [x] `working_paper.tex` §5.4 ya no dice "H4b confirmada"; coincide con
  `paper1_oi.tex` §5.4 y con `NUMEROS_CANONICOS_BBG.md` (H4b no identificado).
- [x] Cada `β_k` tiene derivada estructural + estimando + supuestos + caveat (Cuadro 3.1, V7).
- [x] Prop. 5 acompañada de la Obs. 3.3: la derivada cruzada no depende del Canal I (V3-A).
- [x] DAG: figura TikZ en el Cap. 3 (Fig. 3.3) + SVG en el artifact; artifact publicado.
- [x] Registro en `CONTROL_DE_VERSIONES.md` §5. Commits pusheados a `origin/main`.

**Pendiente (criterios de aceptación de lo que queda):**
- [ ] `grep` de `\GaR`/`θ` en contexto de signo → todo en D; standalones ↔ tesis
  mismos signos (parcial: hecho el headline; falta auditar cuerpo de pruebas).
- [ ] Numeración de proposiciones unificada `anexoA` ↔ `apendice_matematico`
  (hoy: nota de offset; falta el renumbrado real — opcional).
- [ ] `p9_discriminante.py` corre; `corr(JLoss,D)`, VIF, ortogonalización,
  horse-race; filas nuevas en `NUMEROS_CANONICOS_BBG.md`.
- [ ] Prop. 5b, 5c enunciadas y demostradas; su test empírico corre.
- [ ] `fase4_soberano.py` reproduce `fase4_embi` en D; `mc_gar.py` a R=3000.
- [ ] E1: el modelo colapsa al actual con `κ_I=1` y `G` degenerada; `W(n)`, `n_W`
  calculados; Prop. E1-1 enunciada.
- [ ] `working_paper.tex` con DAG + Cuadro de estimandos + §"n como política".

## Decisiones del usuario (aplicadas)

1. Reunión espera **avances escritos** ⇒ Bloque A front-load.
2. **E1 entra en la tesis** (derivación completa; fallback intermedio disponible).
3. DAG en **ambos** (TikZ en Cap. 3 + narrativa en artifact).
4. Standalones `modelo OI/*` se **mantienen sincronizados** (convención D +
   resultados actuales).

## Cierre de posicionamiento (del barrido de literatura)

Links 1–3 de la cadena y los bloques de *doom loop* y de depositante son
**citables, no supuestos**. Los cuatro objetos núcleo del modelo — `ρ(n)` de
conducta Cournot, el mapa `Λ`, `JLoss(n,H)` en el `DFL`, y la derivada cruzada
amplificada por `H` — tienen "primos" en la literatura (Wagner 2010; Adrian et
al. 2019/2022; Bi 2012; Acharya–Drechsler–Schnabl 2014; Chari et al. 2024) pero
**no son resultados establecidos** ⇒ son la contribución de la tesis. La tensión
Wagner (2010) vs. Anginer et al. (2014) sobre el signo de competencia→riesgo
sistémico es exactamente el espacio que ocupa la derivación de `ρ(n)`.
