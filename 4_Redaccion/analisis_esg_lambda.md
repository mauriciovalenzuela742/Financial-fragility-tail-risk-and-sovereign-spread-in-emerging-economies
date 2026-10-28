---
title: "ESG, gobernanza y el peso de los factores externos y domésticos en el spread"
subtitle: "Resultados del preregistro 9 (análisis aparte de la tesis), 28 de octubre de 2026"
---

*Este informe reporta el preregistro 9 (`4_Redaccion/preregistro_esg.md`, commit `81c2d9c`), escrito antes
de descargar los datos. Es un análisis aparte, con su propia familia de Holm: no entra en las 23 hipótesis
de la tesis ni cambia ninguna cifra canónica (`verificar_canonicos.py`: 140 de 140). Las métricas no son del
autor (JLoss: Chari et al., 2024; GaR: Adrian, Boyarchenko y Giannone, 2019, con CEMLA). Todo son
asociaciones.*

# 1. En una tabla

| | Pregunta | Resultado | Veredicto |
|---|---|---|---|
| E1 | ¿Un mejor ESG se asocia con un spread menor, dentro del país? | −0,43 por d.e.; p unilateral 0,036; Holm 0,11; 12 de 13 sin cada país | Sugerente |
| E2 | ¿Y una mejor gobernanza (WGI)? | −0,33 por d.e.; p unilateral 0,016; Holm 0,063; 13 de 13 | Sugerente (no pasa Holm por poco) |
| E3 | ¿La gobernanza atenúa la transmisión de la fragilidad bancaria? | −0,15; p unilateral 0,013; Holm 0,063; 11 de 13 (cae sin Chile y sin Polonia) | Sugerente y frágil |
| E4 | ¿Dominan los factores externos (λ > 0,5)? | λ = 0,48 [0,25; 0,57]; p 0,79; Shapley 0,44 | No |
| E5 | ¿Pesa más lo externo cuando el VIX sube? | θ1 = −0,09; p 0,83 | No |

**Ninguna hipótesis es firme.** El resultado más sólido es la gobernanza dentro del país (E2):
- pasa el *wild bootstrap*;
- mantiene el signo sin cualquiera de los 13 países;
- resiste todas las variantes del índice;
- se queda en Holm 0,063.

Lo que ORT atribuye al ESG en conjunto es, en este panel, gobernanza: las dimensiones ambiental y social no
se asocian con el spread.

Sobre la combinación λ·externo + (1−λ)·doméstico, el panel no respalda que lo global domine:
- **λ fijo:** una vez que entran los efectos fijos de país, el bloque doméstico pesa tanto o más que el
  externo.
- **λ por régimen:** el peso externo no sube en los episodios de tensión.

# 2. Datos e índices (`p67`, `p68`)

**Fuentes.** Las 18 variables de Barneche, Grezzi y Panario (2024) vienen de la API del Banco Mundial:
- 12 de WDI (`source=2`);
- los 6 WGI (`source=3`, `GOV_WGI_*.EST`).

Se usaron las 13 economías del panel más Argentina, de 2000 a 2025. El CO₂ per cápita usa
`EN.GHG.CO2.PC.CE.AR5`, porque la serie de ORT está descontinuada. Para Tebaldi et al. (2018) se agregaron
el crecimiento, la apertura y Freedom House (calificaciones 1973–2024).

**Tiempo.** El valor del año y entra en los trimestres de y + 1, y en la regresión se usa el de t − 1. Esto
evita usar información que el mercado aún no tenía.

**Índices**

| | Valor propio | Varianza explicada | KMO | Referencia en ORT |
|---|---|---|---|---|
| G (seis WGI, sin logaritmo) | 4,46 | 74 % | 0,83 | 4,22; 70 %; 0,83 |
| ESG-E (renovables, CO₂, agotamiento, intensidad) | 2,14 | 54 % | 0,54 | 2,50; 63 %; 0,69 |
| ESG-S (seis variables) | 3,00 | 50 % | 0,76 | 2,06; 34 %; 0,54 |
| ESG-G (seis WGI, con logaritmo) | 4,11 | 69 % | 0,78 | 4,22; 70 %; 0,83 |

Las cargas de G son parecidas a las de ORT. En la dimensión ambiental, el agotamiento de recursos casi no
carga (0,01).

**Pesos de las dimensiones en el ESG:** E 0,23, S 0,32 y G 0,44. La correlación entre G y ESG es 0,86.

**Lo que ya se esperaba.** Solo un 9 % de la varianza de G en la muestra de estimación es dentro del país;
en el ESG, un 6 %. Por eso un coeficiente por desviación estándar total se traduce en efectos chicos por
movimiento típico dentro del país: E2 equivale a −0,10 log-puntos, cerca de un 10 % del spread, por una
desviación estándar dentro del país.

**Cobertura.** G cubre los 765 trimestres de la muestra. El ESG cubre 652, porque la paridad de matrícula
termina en 2020–2021 y el índice queda sin dato desde 2025.

# 3. Familia primaria (`p69`, `p70`)

Base: la especificación principal de la tesis, ln EMBI sobre ln JLoss_{t−1}, D_{t−1} y su producto, con
efectos fijos de país y de tiempo.

| | Coeficiente | p DK | p cluster país | p wild (unilateral) | Holm | Sin cada país | N |
|---|---|---|---|---|---|---|---|
| E1 ESG_{t−1} | −0,430 | <0,001 | 0,015 | 0,036 | 0,108 | 12/13 (India: 0,11) | 652 |
| E2 G_{t−1} | −0,327 | <0,001 | 0,013 | 0,016 | 0,063 | 13/13 | 765 |
| E3 ln JLoss × G | −0,155 | 0,035 | 0,020 | 0,013 | 0,063 | 11/13 (Chile: 0,23; Polonia: 0,34) | 765 |
| E4 λ > 0,5 | 0,481 | | | 0,794 | 1,000 | 0/13 | 678 |
| E5 θ1 > 0 | −0,088 | | | 0,827 | 1,000 | 0/13 | 678 |

**Lectura**
- **E2.** Una gobernanza mejor que la habitual del mismo país se asocia con un spread menor, aun con la
  fragilidad bancaria y el ciclo global (efectos de tiempo) en el modelo.
  - *Por qué no es firme:* no pasa la corrección de Holm sobre las cinco hipótesis (0,063).
  - *Por qué es lo más sólido del análisis:* el signo no depende de ningún país y el coeficiente va de
    −0,41 a −0,25 al excluir cada uno.
  - *Advertencia:* los WGI se construyen en parte con evaluaciones de riesgo comerciales, como EIU, PRS o
    Global Insight. Esas evaluaciones pueden incorporar el mismo deterioro financiero que mueve el spread.
    El rezago de publicación ordena el tiempo, pero no elimina ese contenido común. Es una asociación.
- **E3.** La fragilidad se traslada menos al spread donde la gobernanza es mejor.
  - Pasa el *wild bootstrap*, pero depende de Chile y de Polonia: sin cualquiera de los dos deja de ser
    significativa.
  - Va en la misma dirección que el resultado de reservas de la tesis: la transmisión de la fragilidad es
    menor donde el Estado tiene más respaldo. Igual que ese resultado, queda como sugerente.
- **E1.** El ESG funciona solo porque contiene la gobernanza. Por separado, las dimensiones ambiental
  (−0,21; p 0,41) y social (−0,09; p 0,35) no se asocian con el spread. Esto coincide con ORT (solo la
  gobernanza era significativa) y con Capelle-Blancard et al. (2019) en lo ambiental.

# 4. El modelo λ (`p70`)

  ln EMBI_it = a_i + β·[ λ·Ĝ_t + (1 − λ)·D̂om_it ] + e_it

**Validación previa.** Con los regresores reales, λ = 0,6 y pesos iguales, el estimador recupera en
promedio 0,581 (d.e. 0,081; 100 réplicas). Está dentro de la tolerancia preregistrada (±0,05), con un
sesgo leve hacia abajo.

**Estimación**

| | Valor |
|---|---|
| λ fijo | 0,481, IC 95 % del *bootstrap* por bloques [0,252; 0,570] |
| Shapley, participación del bloque externo en el R² dentro del país | 0,44 (R² externo 0,09; doméstico 0,11; ambos 0,20) |
| λ sin cada país | entre 0,285 y 0,532 |
| Pesos del bloque externo | US HY spread 1,00; VIX, UST10Y y USD NEER 0 |
| Pesos del bloque doméstico | −G 0,65; ln JLoss 0,22; D 0,10; deuda 0,03; −reservas e inflación 0 |
| λ por régimen | θ1 = −0,088; razón de verosimilitud 0,89 (p 0,35); BIC favorece λ fijo (−1398,8 frente a −1393,2) |
| λ_t entre los percentiles 10 y 90 del VIX | 0,46 a 0,52 |

**Lectura**
- **λ.** Los factores externos y domésticos pesan parecido, y los domésticos algo más.
  - Esto difiere de Longstaff et al. (2011), que encuentran que los CDS soberanos responden sobre todo a
    factores globales. Pero ellos miran la variación común entre países, que aquí absorben en parte los
    efectos fijos y que, en la tesis, absorben los efectos de tiempo.
  - λ no es una cifra estructural: compara una desviación estándar de cada bloque y depende de qué
    variables entran.
  - *Variantes exploratorias:* con el TCRE y el crecimiento en el bloque doméstico, λ = 0,45. Con el EMBI
    en puntos básicos, λ = 0,27.
- **Pesos externos.** Todo el peso va al *spread high yield* de Estados Unidos: el apetito por riesgo de
  crédito resume a los otros tres. En el modelo lineal sin restringir, el VIX, la tasa del Tesoro y el dólar
  tienen signo negativo una vez que el *high yield* está presente. Por eso la restricción de pesos no
  negativos los deja en cero.
- **Pesos domésticos.** La gobernanza tiene el peso más alto. Le siguen la fragilidad bancaria y el riesgo
  de cola. Es coherente con E2.
- **λ por régimen.** No se encontró que lo global gane peso cuando el VIX sube.

# 5. Exploratorio

**"Efecto fijo de fondo"**
- **Mundlak:** sin efecto fijo de país, con efectos de tiempo y errores agrupados por país.
  - La parte *entre* países de G es −0,24 (p 0,011): los países con mejor gobernanza promedio tienen
    spreads más bajos.
  - La parte *dentro* del país es −0,41 (p 0,001).
  - Con el ESG, −0,20 (p 0,035) y −0,54 (p 0,019).
- **Segundo paso:** los efectos fijos de país de la especificación principal sobre el G medio de cada país
  (13 puntos). Correlación −0,34, pendiente −0,14 por d.e. (p 0,19), R² 0,11.
  - El efecto fijo de cada país recoge mucho más que la gobernanza. Con 13 puntos es descriptivo.

**D × G (la gobernanza y el riesgo de cola).** −0,019, con p unilateral 0,015 (DK 0,021; cluster 0,004).
Va en la misma dirección que E3.

**Libertad política (Freedom House).**
- No reemplaza a G: +0,13 (p unilateral 0,64), y su moderación es nula (p 0,34).
- Su correlación con G es 0,55, y solo un 9 % de su varianza es dentro del país.
- Lo que el mercado parece valorar es la calidad del gobierno y del estado de derecho, no la democracia en
  sí.

**Réplica de la especificación de ORT:** EMBI en tanto por uno, EMBI rezagado, reservas, deuda, inflación,
crecimiento, ESG del año anterior y efectos fijos de país.

| Versión | ESG | p | N |
|---|---|---|---|
| Trimestral | −0,0006 | 0,39 | 656 |
| Anual | −0,0025 | 0,15 | 157 |
| Anual, con efectos de tiempo | −0,0012 | 0,49 | 157 |

- *Contra lo publicado:* ORT obtuvo −0,0066 (p 0,078), y con errores agrupados por país p 0,119. Su
  especificación tampoco da significancia en esta muestra.
- *La diferencia:* la especificación de la tesis usa el logaritmo del spread, no lo rezaga e incluye la
  fragilidad y el riesgo de cola. Con el EMBI rezagado, el coeficiente es un efecto de corto plazo, y la
  persistencia del spread (0,88 en esta muestra) absorbe casi toda la variación lenta del índice.

**Réplica de Tebaldi, Nguyen y Zuluaga (2018)**

| Variable | Trimestral (LSDV, efectos de país, N = 740) | Anual (GMM de sistema, instrumentos colapsados, N = 163) |
|---|---|---|
| Spread rezagado | 0,88 | 0,82 |
| Crecimiento | n.s. | −0,027 (p < 0,001) |
| ln TCRE | −0,15 (p 0,015) | n.s. |
| Apertura | +0,0008 (p 0,07) | n.s. |
| Libertad política | +0,037 (p 0,019), con el signo contrario al de Tebaldi | −0,033 (p 0,06), con el signo de Tebaldi |

- *Pruebas del GMM:* 8 instrumentos, Hansen p 0,15, AR(2) p 0,07.
- *Advertencia preregistrada:* con 13 países, el GMM es frágil.
- *Conclusión:* la libertad política cambia de signo según la frecuencia y el estimador, así que no es un
  resultado.

**Robustez de E1 a E3** (coeficiente y p unilateral):

| Variante | E2 (G) | E1 (ESG) | E3 (J × G) |
|---|---|---|---|
| Principal | −0,33 (0,016) | −0,43 (0,036) | −0,15 (0,013) |
| Interpolación en lugar de escalón | −0,34 (0,015) | −0,46 (0,036) | |
| Cargas ajustadas con 2003–2012 | −0,33 (0,016) | −0,44 (0,038) | |
| Pesos iguales entre dimensiones | | −0,47 (0,028) | |
| Hasta 2021Q4 | −0,23 (0,12) | −0,49 (0,007) | −0,14 (0,027) |
| Sin valores arrastrados | −0,23 (0,10) | −0,52 (0,009) | −0,14 (0,026) |
| Con Argentina | −0,33 (0,012) | −0,46 (0,019) | −0,16 (0,020) |

E2 pierde fuerza al cortar en 2021 o al sacar los años con valores arrastrados. Parte de su señal está en
2022–2025, cuando el WGI de varios países se movió:
- cayó en Colombia, Perú y México;
- se recuperó en Polonia;
- cayó en Indonesia en 2024.

**Triple interacción con el WGI real.** La tesis (`anexoB_datos.tex`, fila WGI) usa una plantilla
provisional (`instituciones.csv`) en la triple interacción JLoss × GaR × institución de `p3_causal_fase5`.
Con el estado de derecho real del WGI:

| Versión | Coeficiente | t | N |
|---|---|---|---|
| Plantilla | +0,23 | 0,75 | 614 |
| WGI real de 2018 | −0,45 | −0,55 | 647 |
| Media 2003–2025 | +1,44 | 1,21 | 647 |

La conclusión de la tesis ("no significativo") no cambia con datos reales. La muestra crece porque la
plantilla no cubría a todos los países del panel de esa prueba.

# 6. Qué hacer con esto

1. **En la tesis, nada obligatorio.** Ningún resultado es firme, y la conclusión sobre los moderadores
   ("ninguna otra condición modifica la transmisión de forma demostrable") sigue siendo correcta.
2. **Opcional, en una línea:** reemplazar la nota "plantilla provisional" del Anexo B por el WGI real. Es
   una mejora de datos que no cambia el veredicto.
3. **Trabajos futuros:** la gobernanza es candidata a moderador para un preregistro con más países, porque
   es la señal más estable del análisis. En el mismo preregistro convendría separar el contenido de las
   fuentes comerciales del WGI, por la posible causalidad inversa.
4. **Para la defensa:** si la comisión pregunta por las instituciones, hay respuesta.
   - La gobernanza se asocia con spreads menores dentro del país y parece atenuar la transmisión de la
     fragilidad, pero no pasa la corrección conjunta.
   - El ESG ambiental y social no se asocia con el spread.
   - Los factores externos no dominan una vez que se controla por las diferencias entre países.

# 7. Tebaldi et al. (2018): cómo conseguir el paper y sus datos

- **Paper:** *Research in International Business and Finance* 45: 82–93, doi:10.1016/j.ribaf.2017.07.135.
  - No está en acceso abierto.
  - *Vías:* ScienceDirect con el acceso de la Universidad de Chile (SISIB, VPN o proxy), o pedirlo al
    primer autor (E. Tebaldi, Bryant University).
  - El resumen no nombra las fuentes de la liberalización política, del TCRE ni del spread. Hay que
    confirmarlas en el texto antes de citarlas.
- **Datos (usados aquí):**
  - Freedom House, *Country and Territory Ratings and Statuses 1973–2024*: descarga abierta en
    freedomhouse.org, guardada en `2_Datos/freedomhouse/`. La edición con 2024 aún no está publicada como
    archivo; se puede pedir por correo ("FIW Data Request").
  - Crecimiento (`NY.GDP.MKTP.KD.ZG`) y apertura (`NE.TRD.GNFS.ZS`) del WDI.
  - TCRE del panel.
  - V-Dem (`v2x_libdem`) queda como alternativa abierta si se quiere otra medida de democracia.

# 8. Archivos y reproducción

| Paso | Archivo | Commit |
|---|---|---|
| Preregistro | `4_Redaccion/preregistro_esg.md` | `81c2d9c` |
| Datos | `1_Codigo/Panel/bbg/p67_datos_esg.py` → `2_Datos/esg_wb_anual.csv` | `7647c2c` |
| Índices | `bbg/p68_indice_esg.py` → `esg_indice_anual_bbg.csv`, `esg_trimestral_bbg.csv`, `paper_p68_numeros.csv` | `b843ea1` |
| E1–E3 y exploratorio | `bbg/p69_esg_spread.py` → `paper_p69_numeros.csv` | este commit |
| λ, E4–E5 y Holm | `bbg/p70_lambda.py` → `paper_p70_numeros.csv` | este commit |

- **Desviaciones del plan:**
  - El paso a trimestres principal es en escalón y no la interpolación de `annual_to_quarterly()`, porque
    interpolar entre y e y + 1 usaría en los trimestres de y + 1 un dato que aún no se publica. Así quedó
    escrito en el preregistro; la interpolación va como robustez.
  - La simulación usa β = 0,5 · d.e.(ln EMBI dentro del país), porque el preregistro no fijaba β.
- **Semillas fijas:** 20261027, y 7 en el *wild* de `p32`. Una segunda corrida completa de `p68` a `p70`
  reproduce los tres archivos de cifras byte por byte.

**Referencias nuevas**
- Barneche, C., Grezzi, J. y Panario, B. (2024). *Spread soberano y rating ESG: un análisis de países
  emergentes para el período 2005–2020*. Tesis de Máster en Dirección Financiera, Universidad ORT Uruguay.
- Capelle-Blancard, G., Crifo, P., Diaye, M.-A., Oueghlissi, R. y Scholtens, B. (2019). Sovereign bond
  yield spreads and sustainability: An empirical analysis of OECD countries. *Journal of Banking & Finance*
  98: 156–169.
- Crifo, P., Diaye, M.-A. y Oueghlissi, R. (2017). Measuring the effect of government ESG performance on
  sovereign borrowing cost. *Quarterly Review of Economics and Finance* (volumen y páginas por verificar en
  ScienceDirect).
- Kaufmann, D. y Kraay, A. (2024). The Worldwide Governance Indicators: Methodology and 2024 Update.
  *Policy Research Working Paper* 10952, Banco Mundial.
- Longstaff, F., Pan, J., Pedersen, L. y Singleton, K. (2011). How sovereign is sovereign credit risk?
  *American Economic Journal: Macroeconomics* 3(2): 75–103.
- Margaretic, P. y Pouget, S. (2018). Sovereign bond spreads and extra-financial performance: An empirical
  analysis of emerging markets. *International Review of Economics & Finance* 58: 340–355.
- Tebaldi, E., Nguyen, H. y Zuluaga, J. (2018). Determinants of emerging markets' financial health: A panel
  data study of sovereign bond spreads. *Research in International Business and Finance* 45: 82–93.
