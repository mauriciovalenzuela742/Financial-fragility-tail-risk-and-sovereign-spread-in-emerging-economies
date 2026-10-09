pre# Prompt para Prism: dos diapositivas nuevas después del índice

Pegar el bloque de abajo en el asistente de Prism, con el proyecto `defensa.tex` abierto
(subido desde `defensa_latex.zip`). Agrega dos diapositivas justo después de "Tabla de
contenidos" sin tocar las demás: el deck pasa de 40 a 42. Todas las cifras vienen del deck y de
la tesis vigentes.

```
Edita defensa.tex. Agrega DOS frames nuevos inmediatamente después del frame
"Tabla de contenidos": colócalos justo después de \section{Motivación y pregunta}, como las
dos primeras diapositivas de esa sección (antes del frame "Motivación"). No borres ni
modifiques ningún otro frame. Respeta el estilo del archivo: beamer 16:9, tema tesis_beamer,
macros \JLoss, \GaR, \EMBI, \Spread ya definidas, decimales con coma ({,}), texto en español,
\small o \footnotesize si hace falta para que nada se salga de la diapositiva (sin Overfull),
columnas con \begin{columns} y bloques block / alertblock / exampleblock como en el resto del
archivo. Cita autores en texto (Autor, año), sin \cite. No inventes cifras: usa solo las que
aparecen abajo.

FRAME 1 — título: "Determinantes del spread soberano: fundamentos domésticos y factores globales"
Estructura sugerida: dos columnas arriba (los dos pilares) y dos bloques breves abajo.
- Columna izquierda, "Fundamentos macroeconómicos domésticos":
  literatura: Edwards (1984); Hilscher y Nosbusch (2010) — deuda/PIB, crecimiento, términos de
  intercambio, reservas; Uribe y Yue (2006) — ciclo doméstico y spread.
  Nuestras proxies: \JLoss (fragilidad bancaria sistémica, pasivo contingente del fisco; 113
  bancos, Bloomberg) y \GaR (cola del 5% del crecimiento; D = -\GaR), más controles: deuda/PIB,
  balance fiscal, reservas, cuenta corriente, inflación y tipo de cambio real.
- Columna derecha, "Factores globales (push)":
  literatura: Calvo, Leiderman y Reinhart (1996); González-Rozada y Levy Yeyati (2008);
  Longstaff et al. (2011); Remolona, Scatigna y Wu (2008); Miranda-Agrippino y Rey (2022) —
  ciclo financiero global.
  Nuestra proxy: efectos fijos de tiempo, que absorben todo choque común (VIX, tasa del Tesoro
  a 10 años, spread high yield de EE.UU., on/off-the-run); en la réplica de Chari et al. (2024)
  se incluyen explícitamente.
- Bloque "Por qué creer en el mecanismo y en esta especificación":
  el doom loop banca–soberano (Farhi y Tirole, 2018) y el bailout put (Acharya, Drechsler y
  Schnabl, 2014) hacen de la fragilidad bancaria un pasivo contingente que el mercado debe
  incorporar ex ante; el riesgo de cola del crecimiento (Adrian, Boyarchenko y Giannone, 2019)
  es el estado que activa ese multiplicador. Un modelo de intensidad de incumplimiento (Duffie y
  Singleton, 1999) da la forma log-log: ln EMBI sobre ln \JLoss_{t-1}, D_{t-1} y su producto,
  con efectos fijos de país y tiempo; los rezagos hacen predeterminados los regresores frente a
  la retroalimentación spread → fragilidad.
- Bloque "Trabajo reciente relacionado":
  Chari, Garcés, Martínez y Valenzuela (2024, JFS) — JLoss y spread soberano emergente,
  interactuado con factores globales (el más próximo); Farhi y Tirole (2018); Bocola (2016);
  Gennaioli, Martin y Rossi (2014); Adrian, Boyarchenko y Giannone (2019); Ossandón Busch et
  al. (2022, CEMLA). Brecha: nadie interactúa la fragilidad bancaria con el riesgo de cola
  doméstico del crecimiento.

FRAME 2 — título: "Teoría e implicancias: la brecha del spread soberano"
Estructura sugerida: arriba la teoría en una línea; al centro dos columnas con el balance de
fuerzas; abajo un bloque con las acciones.
- Teoría (una o dos líneas): spread ≈ λL con λ = λ0·\JLoss_{t-1}^{β1}·e^{β2 D_{t-1}}; ambos
  riesgos escalan la misma intensidad de incumplimiento, por lo que en puntos básicos se
  potencian (complementariedad proporcional); una amplificación adicional exige β3 > 0.
- Columna "Fuerzas que abren la brecha" (alertblock):
  fragilidad bancaria (pasivo contingente: elasticidad 0,10; ≈4,7 pb por unidad de JLoss);
  cola adversa del crecimiento (+1 pp de D ≈ +3,3% de spread); multiplicador del doom loop
  (el spread retroalimenta a la fragilidad: elasticidad 0,17); deuda en manos de inversionistas
  extranjeros de cartera.
- Columna "Fuerzas que la contienen" (block):
  respaldo oficial (swaps de la Fed, FMI, compras de activos: bajo Backstop la interacción es
  nula o negativa); mercados de deuda local profundos (Polonia e India: interacción negativa);
  fundamentos fiscales sólidos.
- Implicancia (una línea): la amplificación aparece cuando faltan los contrapesos — fuera de
  crisis con respaldo y en el núcleo de 11 economías de financiamiento externo (+0,034 en
  elasticidades, +1,8 pb; resiste wild bootstrap) — evidencia condicional, no robusta.
- Bloque "Acciones para cerrar la brecha" (exampleblock):
  monitoreo macroprudencial conjunto de \JLoss y \GaR como indicadores adelantados;
  profundizar el mercado de deuda en moneda local y la base de inversionistas domésticos;
  acceso a respaldos (líneas swap, FMI) en episodios de estrés; regulación focalizada en
  economías de financiamiento externo y en episodios de doble vulnerabilidad, en lugar de una
  exigencia uniforme (condicional a confirmarse con más datos).

Al terminar: compila, verifica que no haya errores ni cajas desbordadas en los dos frames
nuevos, y que el total de diapositivas pase de 40 a 42.
```

## Notas

- **Solapamiento con "Motivación".** El frame "Motivación" actual se solapa en parte con el nuevo
  frame 1. Si después de verlo resulta redundante, pídele a Prism que lo elimine y el deck queda
  en 41.
- **Diapositivas densas.** Si Prism reporta desbordes o el texto queda apretado, pídele que divida
  un bloque o que quite los años de la lista de literatura.
- **Volver al repositorio.** Lo que se edite en Prism no llega solo a GitHub: hay que descargar el
  `defensa.tex` editado para integrarlo, regenerar el zip y hacer push.
