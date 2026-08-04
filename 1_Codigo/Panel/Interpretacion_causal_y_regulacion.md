# Identificación causal y el argumento por la regulación

*Complemento a `Causalidad_Final_17.ipynb` y `Causalidad_Extended_11.ipynb`. Resume qué
podemos y qué no podemos afirmar causalmente, y encuadra el hallazgo como argumento a favor
del control macroprudencial —no como elogio del laissez-faire.*

## 1. La tesis normativa: por qué el signo negativo es un argumento PARA regular

El coeficiente de interacción θ<0 significa que la fragilidad bancaria eleva más el spread
soberano cuando el riesgo de cola del crecimiento es severo: fragilidad y cola son
**complementos**, no sumandos. Ese es el *doom loop* banco-soberano.

La lectura de mercado libre (Hayek/Mises) diría que no hace falta intervenir: el precio
—el spread— ya agrega la información local dispersa y disciplina al banco imprudente. Aquí
usamos a Hayek como **contrapunto, no como respaldo**, por una razón económica precisa: el
mercado sí tarifa la fragilidad, pero lo hace **ex-post, tarde y de forma supra-aditiva**,
justo en la cola severa, cuando la corrección es más destructiva y auto-reforzante. Que la
disciplina llegue así es exactamente la firma de una **externalidad no internalizada**: cada
banco elige su fragilidad mirando su propio riesgo, sin internalizar que, en el mal estado,
su fragilidad se convierte en riesgo soberano para todos. El signo negativo no invita a
"dejar hacer": revela por qué conviene exigir prudencia **ex-ante** —que los bancos
demuestren que pueden sostener el valor de la moneda sin inflar crédito— en vez de esperar
la disciplina ex-post a costo sistémico.

Formalmente, es el argumento pigouviano de la literatura macroprudencial moderna:

- **Stiglitz & Greenwald (1986)** y **Geanakoplos-Polemarchakis**: con información y mercados
  incompletos, el equilibrio competitivo **no** es Pareto-eficiente; hay espacio para mejoras
  con intervención.
- **Lorenzoni (2008)**, **Bianchi (2011)**, **Bianchi & Mendoza**, **Korinek**, **Jeanne &
  Korinek**: los auges de crédito son **ineficientes** por externalidades pecuniarias y de
  fire-sale; el óptimo social pide impuestos/límites al crédito (macroprudencial) —justo
  "no inflar crédito".
- **Farhi & Tirole**: rescates y **riesgo moral colectivo** —los bancos se fragilizan en
  manada porque anticipan el respaldo público.
- **Diamond & Dybvig**, **Diamond & Rajan**: la fragilidad bancaria y las corridas justifican
  seguro de depósitos y regulación.
- **Brunnermeier et al.** (*diabolic loop*), **Acharya, Drechsler & Schnabl**, **Gennaioli,
  Martin & Rossi**: el nexo banco-soberano —tus papers de Marco teórico— formaliza por qué la
  fragilidad se transmite al soberano.

Y la capa que da sentido "sociocultural" al signo:

- **Minsky** (Hipótesis de Inestabilidad Financiera): la estabilidad engendra toma de riesgo
  (hedge→especulativo→Ponzi); la fragilidad es endógena y solo se cobra al girar el ciclo.
  Es casi tu resultado —pero implica **Big Bank/Big Government**, o sea intervención.
- **Keynes** (incertidumbre fundamental, preferencia por liquidez) y **Knight** (riesgo vs.
  incertidumbre): en la cola severa colapsan confianza y liquidez, y la fragilidad se traduce
  en riesgo soberano. **Bagehot**: el soberano es el prestamista de última instancia cuya
  capacidad se duda justo en el mal estado.
- **North**, **La Porta et al.**, **Guiso-Sapienza-Zingales**, **Putnam/Fukuyama**: en
  economías con instituciones y confianza más delgadas, la garantía soberana es menos
  creíble, y el colchón que amortigua el *doom loop* es menor. **Calvo**: *sudden stops* en
  emergentes.

La conclusión normativa no exige que θ sea causal a prueba de balas: descansa en la **teoría
de externalidades** (los bancos no internalizan el costo soberano-sistémico) reforzada por la
evidencia descriptiva del mecanismo. Que Hayek tenga razón en que el mercado *contiene* la
información no implica que el resultado *descentralizado* sea eficiente: precisamente porque
la señal llega tarde y amplificada, la prudencia ex-ante mejora el bienestar.

## 2. Qué muestran las cuatro estrategias (y qué NO)

Números con SE honestos, ambas bases. Interpretar con sobriedad.

| Estrategia | all17 (5 países) | extendido (11 países) | Lectura |
|---|---|---|---|
| **A. Wild cluster bootstrap** (θ) | M3: θ=−0.34, *p* normal 0.006 → **_p_ wild-boot 0.19** | M2: θ=−0.21, *p* normal 0.20 → **_p_ wild-boot 0.40** | Con pocos clusters la significancia aparente **se desvanece**. θ no es estadísticamente robusto. |
| **B. Proyecciones locales** (IRF) | pico régimen severo h=4: +1.6 pb (se 1.1); benigno hasta +2.0 | severo h=4: +1.1 (se 0.6); benigno hasta +3.5 | Respuestas ruidosas y **dependientes del panel**; no confirman limpiamente la amplificación dinámica. |
| **C. Triple institucional** (JxG_I) | −0.08 (t=−0.11) | −0.45 (t=−0.81) | **No significativo**; el punto no apoya (incluso contradice) que instituciones débiles amplifiquen. Datos WGI son **plantilla**. |
| **D. IV shift-share** (β_JLoss nivel) | UST10Y, F=5.1 (débil), β=+12 (p=0.10) | VIX, F=10.4 (límite), β=+4.5 (p=0.12) | Efecto **causal de nivel positivo** (fragilidad→spread, dirección banco→soberano), pero instrumentos débiles-a-límite: sugestivo, no concluyente. |

### Lo defendible
1. **El mecanismo** (complementariedad / no-linealidad de umbral) es teóricamente sólido y
   **visible en la descripción** (sección 14 de los EDA).
2. **La dirección causal banco→soberano en el nivel** es plausible: un aumento de fragilidad
   inducido por un shock global externo eleva el spread (β_JLoss_IV>0 en ambas bases).

### Lo que NO podemos afirmar (todavía)
1. Que θ (la amplificación) sea **estadísticamente significativa** bajo inferencia honesta.
2. Que la amplificación sea **mayor donde las instituciones son más débiles** (el test no lo
   respalda; además los datos institucionales son provisionales).
3. Una **magnitud causal precisa** de la interacción: los instrumentos disponibles son débiles.

Esto no debilita la tesis: la reencuadra. La contribución es el **mecanismo bien motivado +
evidencia descriptiva robusta + una hoja de ruta de identificación honesta**, con la muestra
de emergentes-con-EMBI como cuello de botella. Un comité valora más esa honestidad que un
*p*<0.05 frágil.

## 3. Cómo fortalecerlo (siguiente iteración)

1. **Datos institucionales reales.** Reemplazar `instituciones.csv` (plantilla) por WGI
   oficiales (Rule of Law, Government Effectiveness) y CBI de Garriga; re-correr la sección C.
2. **Instrumentos más fuertes** que el shift-share con series disponibles: shocks de política
   monetaria de EE.UU. identificados (**Bu-Rogers-Wu**, **Bruno-Shin** con flujos bancarios),
   términos de intercambio × exposición sectorial. Elevar la F de primera etapa por encima de
   10–20.
3. **Más clusters / más países.** Conseguir EMBI (o CDS soberano) para más de las 17 economías
   con GaR estimado; con ~17 clusters, la inferencia y el **GMM de sistema** (Blundell-Bond)
   se vuelven creíbles para la reversa.
4. **Corregir el regresor generado.** GaR es estimado: *bootstrap* que re-muestree la primera
   etapa (o función de control) para propagar esa incertidumbre a θ.
5. **LP más limpias.** Definir el *shock* de fragilidad como innovación ortogonalizada
   (residuo de JLoss sobre su historia y globales) y usar transición suave (STAR) en vez de
   umbral duro.

## 4. Cómo llevarlo al texto de la tesis

Enmarca el capítulo empírico como **evidencia del mecanismo + límites de identificación**, y
el capítulo normativo sobre la **economía del bienestar de la regulación**: aunque el mercado
—como diría Hayek— tarife la fragilidad, lo hace tarde y de forma supra-aditiva; esa es la
externalidad que la regulación macroprudencial internaliza ex-ante. El signo negativo es, así
leído, la mejor prueba de por qué el control es necesario: la responsabilidad de los bancos de
sostener el valor de la moneda sin inflar crédito no puede delegarse a una disciplina de
mercado que solo actúa cuando el daño ya es sistémico.

---
*Reproducibilidad: `causal_core.py` (funciones), `Causalidad_*_v*.ipynb` (ejecución),
`causal_output_*/` (tablas y figura IRF). El IV usa auto-selección del shock global con
primera etapa más fuerte; los p-valores del bootstrap usan 999 repeticiones.*
