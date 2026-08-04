# Fase II — Planteamiento formal del modelo

## Competencia bancaria à la Cournot, risk-shifting y cola conjunta de pérdidas ($JLoss$)

**Alcance de esta fase.** Se especifica el modelo de un período: primitivos, elección de riesgo del prestatario, competencia à la Cournot entre bancos, estructura de factor común tipo Merton/Vasicek (la misma que sostiene el cálculo de $JLoss$ por punto de silla), la correlación $\rho(n)$ en **forma reducida**, la definición formal de equilibrio y las condiciones de existencia y unicidad. Se enuncia y demuestra la **Proposición 1** (relación en U del riesgo individual) y se deja formalmente planteado el objeto $JLoss_\alpha$ cuya estática comparativa (**Proposición 2**) se derivará en la Fase III. El cierre macro-soberano ($GaR$, $EMBI$) corresponde a la Fase IV.

---

## 1. Entorno

### 1.1 Agentes y timing
Economía de un período con cuatro tipos de agentes: un continuo de **prestatarios** (empresarios) sin riqueza propia; $n$ **bancos** idénticos con responsabilidad limitada; **depositantes** con seguro de depósitos; y un **asegurador/fisco** (relevante para la Fase IV). La secuencia de decisiones es:

1. La estructura de mercado queda fijada por el número de bancos $n$ (tratado como parámetro en la versión base; endogenizable por libre entrada, §5.3).
2. Los bancos compiten à la **Cournot** eligiendo cantidades de crédito $l_i$; el mercado determina la tasa de préstamo $R_L$.
3. Cada prestatario, tomando $R_L$ como dada, elige el **riesgo** $p$ de su proyecto (canal risk-shifting).
4. Se realiza el **factor macro-financiero común** $Z$; ocurren los defaults; se materializan las pérdidas individuales y la pérdida sistémica.

### 1.2 Prestatarios y microfundamento del risk-shifting
Cada prestatario financia con 1 unidad un proyecto y elige su probabilidad de default $p\in[0,1]$. Con probabilidad $1-p$ el proyecto tiene éxito y rinde $R(p)$; con probabilidad $p$ fracasa y rinde $0$. Se supone

$$
R'(p) > 0, \qquad \frac{d}{dp}\big[(1-p)R(p)\big] \lessgtr 0 \ \text{(retorno esperado cóncavo, con máximo interior)},
$$

es decir, proyectos más riesgosos ofrecen mayor pago condicional al éxito pero menor valor esperado en el margen. Por responsabilidad limitada, el prestatario repaga $1+R_L$ solo en éxito y resuelve

$$
\max_{p\in[0,1]} \ (1-p)\big[R(p) - (1+R_L)\big].
$$

La condición de primer orden (CPO) es

$$
\Psi(p,R_L)\equiv (1-p)R'(p) - \big[R(p) - (1+R_L)\big] = 0,
$$

con condición de segundo orden (CSO) $\Psi_p = (1-p)R''(p) - 2R'(p) < 0$. Por el teorema de la función implícita,

$$
\frac{dp}{dR_L} = -\frac{\Psi_{R_L}}{\Psi_p} = -\frac{1}{(1-p)R''(p)-2R'(p)} > 0.
\tag{1}
$$

**Lema 1 (risk-shifting).** La probabilidad de default elegida por el prestatario es estrictamente creciente en la tasa de préstamo: $p'(R_L)>0$. *(Canal Boyd–De Nicoló: tasas más altas inducen selección de proyectos más riesgosos.)*

### 1.3 Demanda de crédito
La masa de proyectos financiados genera una **demanda inversa de crédito** $R_L=R_L(L)$, con $L=\sum_{i=1}^n l_i$ el crédito agregado, decreciente y (débilmente) cóncava:

$$
R_L'(L) < 0, \qquad 2R_L'(L) + L\,R_L''(L) < 0.
\tag{2}
$$

La segunda desigualdad es la condición estándar que garantiza ingreso marginal decreciente y sustenta la unicidad del equilibrio de Cournot.

---

## 2. Bancos, factor común y probabilidad de quiebra

### 2.1 Estructura de factor único (Merton/Vasicek)
El default de cada préstamo se rige por un modelo de umbral con un **factor común** $Z\sim N(0,1)$ (estado macro-financiero) y un componente idiosincrásico $\varepsilon_j\sim N(0,1)$ independiente. El préstamo $j$ hace default si

$$
\sqrt{\rho}\,Z + \sqrt{1-\rho}\,\varepsilon_j \ < \ \Phi^{-1}(p),
$$

donde $\rho\in(0,1)$ es la **correlación de activos** y $\Phi$ la normal estándar. Por la ley de grandes números, la **fracción de default realizada** en la cartera de un banco, condicional a $Z$, es la función de Vasicek:

$$
x(Z;p,\rho) \;=\; \Phi\!\left(\frac{\Phi^{-1}(p) - \sqrt{\rho}\,Z}{\sqrt{1-\rho}}\right),
\qquad \frac{\partial x}{\partial Z}<0.
\tag{3}
$$

Este es exactamente el núcleo que sostiene el cálculo de $JLoss$ por aproximación de **punto de silla**: con $n$ bancos y exposiciones heterogéneas $\lambda_i$ la distribución de pérdidas conjuntas no tiene forma cerrada y se aproxima por saddle-point; el caso Vasicek de cartera grande (abajo) es el *benchmark* analítico.

### 2.2 Beneficio bancario y umbral de quiebra
Cada banco se fondea con depósitos asegurados al costo bruto $1+r_D$ y mantiene capital $e$ por unidad de crédito. Por unidad prestada, el ingreso neto en el estado $Z$ es $(1-x(Z))(1+R_L) - (1+r_D)$. El banco **quiebra** cuando las pérdidas agotan el capital, esto es cuando la fracción de default supera el umbral

$$
\bar{x}(R_L) \;=\; 1 - \frac{1+r_D-e}{1+R_L}, \qquad \bar{x}'(R_L) > 0.
\tag{4}
$$

El margen $R_L - r_D$ (y el *charter value* asociado a las rentas futuras) constituye el colchón: **más competencia comprime el margen, baja $\bar x$ y acerca al banco a la quiebra** (canal Keeley / franchise value). Como $x(Z)$ es decreciente en $Z$, la quiebra ocurre para $Z$ suficientemente bajo, $Z<\bar z$, con $x(\bar z)=\bar x$. Invirtiendo (3):

$$
\bar z(R_L,p,\rho) \;=\; \frac{\Phi^{-1}(p) - \sqrt{1-\rho}\,\Phi^{-1}\!\big(\bar x(R_L)\big)}{\sqrt{\rho}}.
$$

La **probabilidad de quiebra individual** es

$$
\boxed{\,PD(R_L,p,\rho) \;=\; \Phi\big(\bar z\big) \;=\; \Phi\!\left(\frac{\Phi^{-1}(p) - \sqrt{1-\rho}\,\Phi^{-1}\!\big(\bar x(R_L)\big)}{\sqrt{\rho}}\right).}
\tag{5}
$$

Los dos canales quedan explícitos en (5): vía $p$ (creciente en $R_L$, Lema 1) y vía $\bar x$ (creciente en $R_L$, ec. 4), con **signos opuestos** sobre $\bar z$.

---

## 3. Competencia à la Cournot y equilibrio

### 3.1 Problema del banco
Con responsabilidad limitada y seguro de depósitos, el patrimonio residual se percibe solo en los estados de supervivencia ($Z\ge \bar z$). El banco $i$ elige $l_i$ para maximizar el beneficio esperado:

$$
\Pi_i(l_i,l_{-i}) \;=\; l_i \cdot \mathbb{E}\!\left[\max\big\{(1-x(Z))(1+R_L(L)) - (1+r_D),\,0\big\}\right] \;-\; C(l_i),
\tag{6}
$$

con $L=l_i+\sum_{k\ne i}l_k$, $R_L(L)$ la demanda inversa (2), y $C(\cdot)$ un costo de intermediación convexo (posiblemente lineal). El prestatario responde a $R_L$ según el Lema 1, de modo que $p=p(R_L(L))$: **la elección de riesgo es indirecta**, gobernada por la tasa de equilibrio. *(En la versión base los bancos no eligen riesgo directamente; el monitoreo/screening explícito $r_i$ queda como extensión, por parsimonia — regla 7 del CLAUDE.md.)*

### 3.2 Condición de primer orden y equilibrio simétrico
La CPO de Cournot del banco $i$ es

$$
\frac{\partial \Pi_i}{\partial l_i} \;=\; \pi(R_L) \;+\; l_i\,\pi'(R_L)\,R_L'(L) \;-\; C'(l_i) \;=\; 0,
\tag{7}
$$

donde $\pi(R_L)\equiv \mathbb{E}\big[\max\{(1-x(Z))(1+R_L)-(1+r_D),0\}\big]$ es el margen esperado unitario. En el **equilibrio simétrico** $l_i=l^*$, $L^*=n\,l^*$, y (7) define implícitamente $l^*(n)$ y por tanto la tasa de equilibrio $R_L^*(n)=R_L(n\,l^*(n))$.

**Lema 2 (efecto pro-competitivo).** Bajo (2), la tasa de préstamo de equilibrio es decreciente en el número de bancos: $R_L^{*\prime}(n)<0$, con $\lim_{n\to\infty}R_L^*(n)=R_L^{c}$ (nivel competitivo, margen $\to 0$) y $R_L^*(1)=R_L^{m}$ (nivel de monopolio). *(Resultado estándar de Cournot; el término estratégico $l_i\pi'R_L'$ se diluye a tasa $1/n$.)*

### 3.3 Definición formal de equilibrio

> **Definición (Equilibrio simétrico).** Un equilibrio de este juego es un vector $(l^*,R_L^*,p^*)$ tal que:
> 1. **Prestatarios:** dado $R_L^*$, cada prestatario elige $p^*=p(R_L^*)$ que resuelve $\Psi(p^*,R_L^*)=0$ con $\Psi_p<0$ (Lema 1).
> 2. **Vaciado de mercado:** $R_L^* = R_L(n\,l^*)$ según la demanda inversa (2).
> 3. **Bancos (Nash-Cournot):** $l^*$ satisface la CPO (7) tomando $l_{-i}=l^*$ como dadas, con $\partial^2\Pi_i/\partial l_i^2<0$.
> 4. **(Opcional) Libre entrada:** $n^*$ es el mayor entero con $\Pi_i(l^*,l^*)\ge 0$.

### 3.4 Existencia y unicidad

**Proposición 0 (existencia y unicidad).** Si (i) la demanda inversa satisface (2), (ii) el margen esperado $\pi(R_L)$ es continuo y el beneficio (6) es estrictamente cóncavo en $l_i$ ($\partial^2\Pi_i/\partial l_i^2<0$), y (iii) el costo $C$ es convexo, entonces existe un único equilibrio simétrico de Cournot $(l^*,R_L^*,p^*)$. *(La cuasi-concavidad del beneficio y la pendiente negativa acotada del ingreso marginal garantizan una función de mejor respuesta contractiva; la simetría se sigue de la identidad de los bancos.)*

Estas condiciones se verifican numéricamente en la Fase III (barrido de parámetros) para el cierre paramétrico de §6.

---

## 4. Proposición 1: relación en U del riesgo individual

**Proposición 1 (U-shape).** Sea $PD(n)\equiv PD\big(R_L^*(n),\,p^*(n),\,\rho\big)$ con $\rho$ constante. Entonces la probabilidad de quiebra individual es, en general, **no monótona y con forma de U** en la competencia: existe $\hat n$ tal que $PD'(n)<0$ para $n<\hat n$ y $PD'(n)>0$ para $n>\hat n$.

*Demostración (esquema).* Diferenciando (5) vía la regla de la cadena, con $R_L^{*\prime}(n)<0$ (Lema 2):

$$
PD'(n) \;=\; \varphi(\bar z)\,\frac{d\bar z}{dn}, \qquad
\frac{d\bar z}{dn} \;=\; \frac{R_L^{*\prime}(n)}{\sqrt{\rho}}\Big[\underbrace{\Phi^{-1\prime}(p)\,p'(R_L)}_{>0\ (\text{risk-shifting})} \;-\; \underbrace{\sqrt{1-\rho}\,\Phi^{-1\prime}(\bar x)\,\bar x'(R_L)}_{>0\ (\text{margen})}\Big].
$$

El primer término (canal risk-shifting) contribuye con signo negativo a $\bar z$ —más competencia reduce el riesgo del prestatario y **estabiliza**—; el segundo (canal margen/charter) contribuye con signo positivo —más competencia comprime el colchón y **fragiliza**. Su importancia relativa varía con $n$: en mercados concentrados domina el risk-shifting ($PD$ cae con la entrada), y en mercados competidos domina el efecto margen ($PD$ sube). Por continuidad existe $\hat n$ interior donde $PD'(\hat n)=0$. $\qquad\blacksquare$

Esto reproduce Martínez-Miera y Repullo (2010) como caso particular y fija el *benchmark* que la arista OI debe superar.

---

## 5. De lo individual a lo sistémico: $\rho(n)$ reducida y $JLoss$

### 5.1 Correlación en forma reducida
Acordado para la versión base: la correlación de activos se postula como función decreciente de la competencia,

$$
\rho = \rho(n), \qquad \rho'(n) \le 0,
\tag{8}
$$

capturando que sistemas más competidos exhiben carteras más diferenciadas (menor exposición común). **Interpretación:** (8) es una forma reducida; su microfundamento —elección endógena de diferenciación/especialización de cartera— se desarrollará en la extensión (Fase III/VI). El caso $\rho'(n)=0$ (correlación constante) recupera exactamente el modelo individual de §4.

### 5.2 El objeto $JLoss_\alpha$
Todos los $n$ bancos comparten el factor común $Z$. La **pérdida sistémica** agregada por unidad de crédito, condicional a $Z$, es $L_{\text{sys}}(Z)=\sum_i \lambda_i\,x_i(Z)$; bajo simetría ($\lambda_i=1/n$, $x_i=x$) se reduce a $L_{\text{sys}}(Z)=x(Z;p,\rho)$. Definimos $JLoss$ como el *expected shortfall* al nivel $\alpha$ de la pérdida conjunta. Como $x(Z)$ es decreciente en $Z$, las peores pérdidas corresponden a la cola inferior de $Z$ ($Z\le \Phi^{-1}(\alpha)$):

$$
\boxed{\,JLoss_\alpha(p,\rho) \;=\; \frac{1}{\alpha}\,\mathbb{E}\!\big[x(Z)\,\mathbf{1}\{Z\le \Phi^{-1}(\alpha)\}\big] \;=\; \frac{1}{\alpha}\,\Phi_2\!\big(\Phi^{-1}(p),\,\Phi^{-1}(\alpha);\,\sqrt{\rho}\big),}
\tag{9}
$$

donde $\Phi_2(\cdot,\cdot;\varrho)$ es la CDF normal bivariada con correlación $\varrho$. La expresión cerrada (9) es el ES de Vasicek; para $n$ finito con exposiciones heterogéneas $\lambda_i$, $JLoss_\alpha$ se computa por **punto de silla** (el método ya implementado), siendo (9) el límite de cartera grande.

### 5.3 Propiedades y puente a la Fase III
Dos propiedades conocidas de (9) organizan la derivación siguiente:

$$
\frac{\partial JLoss_\alpha}{\partial p} > 0, \qquad \frac{\partial JLoss_\alpha}{\partial \rho} > 0
$$

(mayor problema de default y mayor correlación engrosan la cola conjunta). En equilibrio, $p=p^*(n)$ y $\rho=\rho(n)$, de modo que

$$
\frac{dJLoss_\alpha}{dn} \;=\; \underbrace{\frac{\partial JLoss_\alpha}{\partial p}\,p^{*\prime}(n)}_{\text{canal individual (U)}} \;+\; \underbrace{\frac{\partial JLoss_\alpha}{\partial \rho}\,\rho'(n)}_{\le\,0\ \text{(canal estructural, nuevo)}}.
\tag{10}
$$

> **Objetivo de la Fase III (Proposición 2).** Demostrar que, bajo (8) con $\rho'(n)<0$, el segundo término de (10) es no positivo y **desplaza el mínimo de $JLoss_\alpha$ hacia mayor competencia** respecto al mínimo $\hat n$ del riesgo individual (Prop. 1): existe un rango donde $PD'(n)\ge 0$ pero $JLoss_\alpha'(n)<0$. Esta cuña entre riesgo individual y riesgo sistémico es la predicción distinguible de MMR.

---

## 6. Cierre paramétrico ilustrativo (para calibración en Fase III)

Para la verificación numérica se propone la siguiente parametrización tratable:

- **Demanda inversa (lineal):** $R_L(L)=A-B\,L$, con $A>1+r_D$, $B>0$ (satisface 2).
- **Risk-shifting (forma reducida lineal):** $p(R_L)=\gamma\,R_L$, $\gamma>0$, en el rango $R_L\in[0,1/\gamma]$ (consistente con el Lema 1).
- **Costo:** $C(l)=c\,l$ (marginal constante $c\ge 0$).
- **Correlación reducida:** $\rho(n)=\rho_0\,e^{-\delta(n-1)}$, con $\rho_0\in(0,1)$, $\delta\ge 0$ (base: $\delta=0$; extensión: $\delta>0$).
- **Capital y depósitos:** $e,\,r_D$ exógenos.

Bajo esta parametrización, el equilibrio de Cournot admite $l^*(n)$ semi-cerrado, $R_L^*(n)=A-B\,n\,l^*(n)$, y $PD(n)$, $JLoss_\alpha(n)$ se evalúan con (5) y (9). El barrido sobre $(\gamma,\delta,\rho_0,e)$ permitirá exhibir simultáneamente la U de $PD$ y el mínimo desplazado de $JLoss_\alpha$.

---

## 7. Verificación teórica de la Fase II (casos límite y anidamiento)

| Verificación | Condición | Resultado esperado |
|---|---|---|
| Competencia perfecta | $n\to\infty$ | $R_L^*\to R_L^c$, margen $\to 0$, $\bar x\to$ mínimo, $PD$ dominada por canal margen (creciente) |
| Monopolio | $n=1$ | $R_L^*=R_L^m$ máximo, $p^*$ máximo, $PD$ dominada por risk-shifting |
| **Anidamiento MMR** | $\rho'(n)=0$ (i.e. $\delta=0$) | (10) colapsa al canal individual; $JLoss$ hereda la U de $PD$ ⇒ **modelo se reduce a MMR** |
| Sin factor común | $\rho\to 0$ | $x(Z)\to p$ (sin riesgo sistémico), $JLoss_\alpha\to p$, quiebra idiosincrásica desaparece |
| Consistencia ES | $\alpha\to 0$ | $JLoss_\alpha\to$ cola extrema; monotonía en $\rho$ preservada |

El anidamiento a MMR (fila 3) es el criterio de cierre de la fase: si al fijar $\delta=0$ el modelo **no** reproduce la U de MMR, hay un error de especificación que debe corregirse antes de avanzar.

---

## 8. Notación

| Símbolo | Significado |
|---|---|
| $n$ | Número de bancos (inverso de la concentración) |
| $l_i,\,L$ | Crédito del banco $i$; crédito agregado $L=\sum l_i$ |
| $R_L,\,r_D$ | Tasa de préstamo; costo bruto de depósitos |
| $p$ | Probabilidad de default del prestatario (riesgo elegido) |
| $R(p)$ | Retorno del proyecto en éxito |
| $Z,\,\varepsilon_j$ | Factor común macro-financiero; shock idiosincrásico |
| $\rho,\,\rho(n)$ | Correlación de activos; forma reducida decreciente en $n$ |
| $x(Z;p,\rho)$ | Fracción de default condicional (Vasicek) |
| $\bar x,\,\bar z$ | Umbral de default de quiebra; umbral en $Z$ |
| $e$ | Capital por unidad de crédito |
| $PD(n)$ | Probabilidad de quiebra individual, ec. (5) |
| $JLoss_\alpha$ | Expected shortfall de la pérdida sistémica, ec. (9) |
| $\Phi,\varphi,\Phi_2$ | CDF/pdf normal estándar; CDF normal bivariada |

---

## 9. Puente a la Fase III

Con el modelo especificado y anidado, la Fase III procede a: (i) demostrar la **Proposición 2** (mínimo desplazado de $JLoss$ vía el canal $\rho(n)$) usando (10); (ii) la **Proposición 3** (traspaso de la cola creciente en concentración, con $\lambda_i$ heterogéneas y saddle-point); y (iii) la calibración numérica del cierre paramétrico de §6, verificando existencia/unicidad (Prop. 0) y la separación entre $PD$ y $JLoss_\alpha$.

*Decisión abierta pendiente para la reunión:* forma funcional definitiva de $R(p)$ (la lineal $p=\gamma R_L$ es reducida; una $R(p)$ estructural cóncava da comparative statics más ricas pero menos tratables). Se recomienda cerrar §6 con la versión lineal para la primera calibración y contrastar robustez con la estructural en la Fase VI.
