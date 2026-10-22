---
title: "Plan de investigación para llevar la evaluación a 7,0"
subtitle: "Qué falta, criterio por criterio, en las cuatro evaluaciones con la misma rúbrica, y qué investigación lo cerraría"
---

*Escrito el 22 de octubre de 2026, sobre la versión del commit posterior a `9d1bf28`, con las
extensiones ya movidas al Anexo E. Usa la rúbrica de 8 criterios y pesos de `evaluacion_experta.md`.
Las métricas no son del autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019,
con CEMLA). Todo lo que se propone sigue la regla del proyecto: preregistro antes de los datos y
reporte salga como salga.*

---

# 1. Dónde está la tesis

Notas vigentes de las cuatro evaluaciones, ya reestimadas:

| # | Criterio | Peso | Econométrica | Macro | Micro | Macroprudencial | Brecha a 7 (peor nota) |
|---|---|---|---|---|---|---|---|
| 1 | Contribución | 15 % | 6,3 | 6,6 | 6,2 | 6,3 | 0,8 |
| 2 | Marco | 10 % | 6,2 | 6,4 | 5,9 | 5,8 | 1,2 |
| 3 | Datos | 15 % | 6,2 | 6,2 | 6,2 | 6,3 | 0,8 |
| 4 | Identificación | 20 % | 5,7 | 5,9 | 5,7 | 5,7 | **1,3** |
| 5 | Inferencia | 15 % | 6,8 | 6,8 | 6,8 | 6,9 | 0,2 |
| 6 | Interpretación | 15 % | 6,5 | 6,5 | 6,5 | 6,4 | 0,6 |
| 7 | Estructura | 5 % | 5,4 | 5,8 | 5,7 | 5,6 | 1,6 |
| 8 | Reproducibilidad | 5 % | 6,8 | 6,9 | 6,9 | 6,9 | 0,2 |
| | **Ponderada** | | 6,2 | 6,4 | 6,2 | 6,2 | |

**Diagnóstico.** La brecha no está en la inferencia ni en la reproducibilidad: ahí la tesis ya está
cerca del máximo, y otra prueba de robustez no mueve la nota. La brecha está en cuatro criterios, que
pesan el 50 %:
- **Identificación (1,3 puntos; 20 %).** Es la brecha más cara. Todo son asociaciones con trece
  economías, y el sesgo de retroalimentación por sí solo produciría coeficientes del orden de los
  observados.
- **Marco (1,2).** El hallazgo central (deuda × riesgo de cola) se motiva con modelos de incumplimiento,
  pero la tesis no tiene un modelo propio que lo derive ni que prediga su magnitud.
- **Estructura (1,6; solo 5 %).** Sigue siendo una tesis de 150 páginas con veinte pruebas, cuando el
  hallazgo central cabe en un capítulo.
- **Contribución y datos (0,8 cada uno).** El hallazgo central se estableció con 10–13 economías de una
  misma muestra, sin replicarse fuera de ella.

**Qué significa un 7,0.** En la escala de la Universidad de Chile, un 7,0 es una tesis excepcional,
publicable sin cambios de fondo. Para un comité, eso exige tres cosas que hoy faltan:
1. un resultado central con una fuente de variación creíble, no solo asociaciones;
2. un modelo que lo prediga cuantitativamente;
3. su réplica fuera de la muestra original.

Con 13 economías el techo realista es de 6,7 a 6,8. Al 7,0 se llega si además la réplica externa sale
bien, cosa que no se puede garantizar de antemano.

---

# 2. El programa de investigación

Todo gira en torno al hallazgo central, que es lo más sólido que tiene la tesis: **la deuda pública
amplifica la transmisión del riesgo de cola del crecimiento al spread**. Hoy es firme en dos
preregistros, pero como asociación y dentro de la muestra. El programa busca cerrar sus tres flancos:
causalidad, teoría y validez externa. Lo demás ---la fragilidad bancaria, la amplificación entre los dos
riesgos, los umbrales--- queda como contexto, ya resuelto.

## N1. Choques exógenos al riesgo de cola: proyecciones locales con instrumento (identificación)

- **Idea.** El riesgo de cola de cada economía se mueve, en parte, por choques que no vienen del spread:
  cambios en los términos de intercambio de las materias primas que exporta y cambios en la demanda
  externa. Si la deuda amplifica la respuesta del spread a esos choques exógenos, la amplificación deja
  de ser una asociación cualquiera.
- **Instrumentos:**
  - el choque de términos de intercambio de materias primas por país (`CTOT_shock`, ya en el panel),
    ponderado por la canasta exportadora predeterminada;
  - el crecimiento de los socios comerciales ponderado por las exportaciones de un año base;
  - como variante, los choques de política monetaria de EE. UU. de alta frecuencia (Jarociński y
    Karadi, 2020), que mueven el riesgo de cola por la vía financiera.
- **Método:** proyecciones locales con instrumento (Jordà, 2005; Stock y Watson, 2018) del spread a h =
  0–8 trimestres, con el riesgo de cola instrumentado y su interacción con la deuda predeterminada (t−4).
  Inferencia robusta a instrumentos débiles (Anderson–Rubin; Montiel Olea y Pflueger, 2013) y wild por
  país.
- **Riesgo declarado.** El instrumento *shift-share* para la fragilidad ya falló (signos opuestos,
  Sargan rechaza). Para el riesgo de cola, el primer paso es medir la fuerza del instrumento con el F
  efectivo antes de mirar el spread, con ese umbral fijado en el preregistro.
- **Impacto si funciona:** identificación de 5,7–5,9 a 6,6–6,8; contribución +0,3.
- **Esfuerzo:** 2–3 semanas. Datos: `CTOT_shock` ya está; el crecimiento de los socios sale de DOTS del
  FMI o de WITS; los choques de política monetaria se publican.

## N2. Validez externa: réplica fuera de la muestra (contribución, datos, inferencia)

- **Idea.** Replicar el hallazgo central en economías que no se usaron para descubrirlo, con un
  preregistro que fije la especificación exacta del panel original.
- **Muestra nueva:**
  - **Hungría, Bulgaria y Corea del Sur**, que ya tienen FCI y GaR (`GaR_panel_all18.xlsx`) y bancos
    extraídos de Bloomberg; falta su CDS soberano como variable dependiente.
  - **Las economías del panel sin EMBI suficiente:** Indonesia, Filipinas y Sudáfrica, con su CDS.
  - **Si se consigue acceso a Bloomberg o Refinitiv,** cinco a diez emergentes más (Tailandia, Arabia
    Saudita, Rumania, Chequia, Vietnam), con el GaR de la plataforma de CEMLA.
- **Prueba:** el coeficiente deuda × riesgo de cola en la muestra nueva, con el signo y un tamaño dentro
  del intervalo del original, y una prueba conjunta de igualdad entre ambas muestras.
- **Por qué pesa tanto.** Es la única prueba que responde de raíz la objeción de los trece países y de
  la búsqueda de especificación. Si replica, la contribución y los datos suben a 6,8–7,0. Si no, la tesis
  lo dice, y la nota baja en contribución pero sube en transparencia.
- **Esfuerzo:** 2 semanas con los datos que ya hay (Hungría, Bulgaria y Corea); 1–2 meses con datos
  nuevos.

## N3. Un modelo que prediga la magnitud (marco)

- **Idea.** Un modelo de incumplimiento soberano de dos períodos, en la línea de Eaton y Gersovitz
  (1981) y Arellano (2008), con una distribución del crecimiento asimétrica cuyo cuantil 5 % es el GaR.
  Su predicción cualitativa es que ∂²spread/∂(riesgo de cola)∂(deuda) > 0, porque con más deuda la
  frontera de incumplimiento se acerca a la cola del crecimiento.
- **Prueba cuantitativa:**
  - calibrar con la deuda, la volatilidad y la asimetría del crecimiento de las trece economías;
  - comparar la semielasticidad implícita del modelo, y cómo crece con la deuda, con las estimadas:
    0,032 en la media y 0,011 más por desviación estándar de deuda;
  - reportar si la estimación cae dentro del rango que el modelo genera con parámetros razonables.
- **Por qué suma.** Convierte una interacción que "predicen los modelos" en una predicción derivada y
  contrastada en magnitud. Además, reemplaza con algo útil el modelo de Cournot que se eliminó.
- **Impacto:** marco de 5,8–6,4 a 6,8; interpretación +0,3, porque la magnitud se puede leer en
  términos del modelo.
- **Esfuerzo:** 2–3 semanas; es un capítulo corto con un apéndice.

## N4. La tesis en torno al hallazgo central (estructura)

- **Reorganizar el cuerpo en 80–90 páginas:**
  1. introducción;
  2. marco con el modelo de N3;
  3. datos y métodos;
  4. **el hallazgo central:** deuda × riesgo de cola, con los dos preregistros, N1 y N2;
  5. **la pregunta original:** simultaneidad sin amplificación;
  6. discusión e implicancias (la regla continua);
  7. conclusiones.
- **Lo que sale del cuerpo:** la réplica de Chari et al., la resiliencia, las crisis, la micro y los
  umbrales se resumen en una tabla de veredictos y van a los anexos.
- **Escala de evidencia:** un solo cuadro al inicio, en vez de repetirla en cada sección.
- **Impacto:** estructura de 5,4–5,8 a 6,8; interpretación +0,2, porque el lector ve el argumento sin
  buscarlo.
- **Esfuerzo:** 1–2 semanas de redacción, sin estimación nueva.

## N5. Datos sin piso y controles trimestrales (datos, identificación)

- **JLoss sin saturación.** La versión con la malla ancha (μ2: Spearman 0,96 con la original) pasa a
  ser la medida principal, y la saturada queda como réplica de Chari et al. La DD de Merton queda como
  medida continua de alta frecuencia.
- **Calificación soberana histórica** (S&P, Moody's o Fitch, desde Bloomberg o las agencias) como
  control y como canal: hoy es el control omitido que más señalan las evaluaciones.
- **Controles fiscales y externos trimestrales** (QPSD y QEDS, ya descargados para la deuda) en lugar de
  los anuales interpolados.
- **Impacto:** datos +0,3; identificación +0,1.
- **Esfuerzo:** 1–2 semanas, según el acceso a las calificaciones.

## N6. Inferencia conjunta sobre todos los preregistros (inferencia)

- **Corrección conjunta:** Romano–Wolf o una tasa de falsos descubrimientos sobre las cuatro familias
  preregistradas a la vez, para responder si algo sobrevive a todas las pruebas que se hicieron.
- **Inferencia por aleatorización:** permutar las asignaciones de deuda entre países para el hallazgo
  central.
- **Impacto:** inferencia de 6,8–6,9 a 7,0.
- **Esfuerzo:** 3–4 días.

## N7. Reproducibilidad completa (reproducibilidad)

- Un solo comando (`make all` o un contenedor) que regenere desde los CSV de datos todas las cifras de la
  tesis.
- Una prueba automática que compare las cifras con `NUMEROS_CANONICOS_BBG.md`.
- Un depósito en Zenodo con DOI y una declaración de disponibilidad de los datos de Bloomberg.
- **Impacto:** reproducibilidad de 6,9 a 7,0.
- **Esfuerzo:** 3–5 días.

---

# 3. Trayectoria de la nota

| Criterio | Hoy (peor) | Con N4 + N6 + N7 (sin datos nuevos) | + N3 y N5 | + N1 y N2 si salen bien |
|---|---|---|---|---|
| Contribución (15 %) | 6,2 | 6,3 | 6,5 | 7,0 |
| Marco (10 %) | 5,8 | 5,9 | 6,8 | 6,9 |
| Datos (15 %) | 6,2 | 6,2 | 6,5 | 6,9 |
| Identificación (20 %) | 5,7 | 5,7 | 5,8 | 6,8 |
| Inferencia (15 %) | 6,8 | 7,0 | 7,0 | 7,0 |
| Interpretación (15 %) | 6,4 | 6,6 | 6,9 | 7,0 |
| Estructura (5 %) | 5,4 | 6,8 | 6,8 | 7,0 |
| Reproducibilidad (5 %) | 6,8 | 7,0 | 7,0 | 7,0 |
| **Ponderada** | **6,2** | **6,3** | **6,6** | **6,9–7,0** |

**Si N1 o N2 no salen,** porque el instrumento es débil o la réplica falla, la nota se queda en torno a
6,6. Una tesis que reporta una réplica fallida con preregistro sigue siendo mejor que una que no la
intentó, pero no es un 7.

---

# 4. Orden recomendado

**Antes de la defensa** (lo que no depende de datos nuevos ni de que algo resulte):
1. N4, reorganizar en torno al hallazgo central (1–2 semanas).
2. N6 y N7, inferencia conjunta y reproducibilidad (1 semana).
3. N3, el modelo (2–3 semanas).

**En paralelo, con preregistro antes de los datos:**

4. N2 con Hungría, Bulgaria y Corea, que ya tienen GaR y bancos (2 semanas).
5. N1 con `CTOT_shock` y el crecimiento de los socios (2–3 semanas).

**Para el paper o después de la defensa:**

6. N5, con calificaciones históricas.
7. N2 ampliado con datos nuevos.

---

# 5. Lo que no mueve la nota

- **Más pruebas de robustez sobre la misma muestra:** la inferencia ya está en 6,8–6,9 y el comité ya
  vio veinte.
- **Más moderadores o umbrales:** ya se probaron tres preregistros de ese tipo, con resultados nulos o
  firmes, y otro más agrega búsqueda, no evidencia.
- **Volver a la amplificación entre fragilidad y riesgo de cola:** está resuelta. Se descarta una
  amplificación de más de un 35 % y no hay potencia para descartar una menor.

**Lo que falta no es otra prueba, sino tres cosas que la tesis no tiene:** variación exógena, un modelo
cuantitativo y una réplica externa del hallazgo central.

---

# 6. Registro de aplicación (22 de octubre de 2026)

| # | Estado | Resultado |
|---|---|---|
| N4 | Hecho | El capítulo de resultados abre con el hallazgo central (Sección 4.1, con los dos preregistros y la inferencia conjunta). La resiliencia y las crisis pasan al Anexo E y quedan resumidas en una sección; las extensiones, al Anexo F. Capítulos 1 a 7: ~78 páginas |
| N6 | Hecho | Con Holm sobre las 14 hipótesis primarias, ninguna bajo 0,05 (R2-H3 0,08; R-H3 0,19). Aleatorización de la deuda: con el riesgo de cola a un año, p = 0,009; a un trimestre, p = 0,17. La interacción preregistrada a un trimestre pasa de firme a sugerente, corregido en la tesis, el paper y las láminas |
| N7 | Hecho | `reproducir.py` (un comando), `verificar_canonicos.py` (67 cifras), integración continua, `CITATION.cff` y `.zenodo.json`. Falta que el autor active Zenodo y publique una *release* para el DOI |

**Efecto sobre la trayectoria de la nota.** N6 sube la inferencia a 7,0, pero baja la contribución, porque
el hallazgo central queda circunscrito al horizonte de un año y a una prueba que era secundaria. Con N4 y N7,
la estructura sube a ~6,7 y la reproducibilidad a 7,0. Nota estimada: **6,3**, igual que la prevista sin
datos nuevos. El peso de N1 y N2 aumenta: son las que pueden devolver al hallazgo central la fuerza que la
inferencia conjunta le quitó, y la réplica externa debería preregistrar como primaria la versión a un año.
