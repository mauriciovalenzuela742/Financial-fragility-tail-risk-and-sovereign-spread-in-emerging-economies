# Defensa — una página

**Tesis.** *Fragilidad bancaria, riesgo de cola del crecimiento y spread soberano en economías emergentes.*
Magíster en Economía Aplicada, U. de Chile · Mauricio Valenzuela Corvalán

---

## La frase de una línea

> La fragilidad bancaria sistémica y el riesgo de cola del crecimiento son **dos caras del mismo mecanismo de *doom loop***. Su interacción se traslada al spread soberano **específicamente en las economías emergentes más dependientes del financiamiento externo de cartera**; la tesis deriva esa complementariedad de un modelo de competencia bancaria y la mide sobre un panel homogéneo y reproducible, siendo explícita sobre dónde la evidencia es fuerte y dónde no.

## Los cinco aportes (en orden de solidez)

1. **Encuadre.** El nexo banca–soberano y el *growth-at-risk* eran literaturas paralelas. Esta tesis las articula como un solo mecanismo y lo formaliza como el término de interacción no lineal `JLoss × GaR` sobre el spread. *No es agregar un regresor.*

2. **Hallazgo empírico con contenido económico.** La complementariedad es **condicional**: **θ = −0,47 (p = 0,023)** en el núcleo de 11 EM de financiamiento externo; se apaga en Polonia e India (deuda local profunda). La condición es **estructural**: el multiplicador opera sobre el *precio* de la deuda en la medida en que el tenedor marginal —un inversor de cartera extranjero— reprecia el *bailout put* cuando el crecimiento cae. Es una **propiedad de la estructura de financiamiento del soberano**, no un efecto frágil.

3. **Dos hallazgos sobre la medición.**
   - EMBI y CDS dan el **mismo θ** sobre la misma submuestra → la diferencia con la versión anterior fue *composición de muestra* (Polonia truncada, India ausente), no la métrica.
   - La malla de pérdidas del motor de `JLoss` satura el VaR99 en el **98 %** de las observaciones → la métrica, como se calibra en la literatura, mide pérdida esperada + estrés fijo; se interpreta **ordinalmente**.

4. **Microfundamento estructural (Cap. 3).** Modelo Cournot que deriva la complementariedad. **Proposición 3 (nueva vs. Martínez-Miera y Repullo):** el mínimo de fragilidad *sistémica* está en un mercado más competido que el de fragilidad *individual* → una política de competencia calibrada solo sobre salud individual deja al sistema subóptimamente concentrado. **No depende de la econometría.**

5. **Pipeline reproducible.** `JLoss` de 113 bancos, un solo protocolo Bloomberg, versionado, trazable a `NUMEROS_CANONICOS_BBG.md`.

## Números clave (panel EMBI, 13 países, N = 721 / 614)

| Resultado | Valor |
|---|---|
| β₁ (`JLoss → spread`, H1) | **+2,8 (t = 2,7)** — respaldada; proyecciones locales +4,6 pb (t = 2,9) |
| β₂ (`GaR → spread`, H2) | **−4,3 (t = −2,3)** — respaldada |
| θ (`JLoss × GaR`, H3), muestra completa | −0,16 (p = 0,26) — **no significativa** |
| θ, **núcleo 11 EM de financiamiento externo** | **−0,47 (p = 0,023; wild boot 0,015)** |
| Umbral de Hansen (efecto de `JLoss` por régimen) | +5,9 vs +2,0 pb; LR = 27 |
| Temporal | θ base pre-2020 = −1,0 (p = 0,057); ventana 2012–2016 = −0,65 (p = 0,018) |
| β₄ (amplificación por concentración, H4b) | **no identificada** — signo inestable entre 3 proxies de HHI |
| IV *shift-share* del canal de nivel | F ≈ 11, 2ª etapa n.s., Sargan rechaza → **no cierra la causalidad** |

## Lo que NO se debe afirmar

- Un θ < 0 robusto y universal.
- Identificación causal cerrada del canal de nivel.
- Respaldo empírico de la amplificación por concentración (H4b).

## El argumento de cierre (si preguntan "¿y entonces qué queda?")

En un área llena de resultados marginales presentados como robustos, un trabajo que dice **"acá exactamente muerde el mecanismo y por qué, y acá el dato no alcanza"** es un aporte a la **credibilidad** de la literatura, no solo a su contenido. Quedan: los canales de nivel bien identificados; una complementariedad condicional con mecanismo económico; un modelo estructural que la predice y una Proposición 3 con implicancia de política independiente de la evidencia; y un pipeline reproducible. La versión honesta y acotada vale más que la sobrevendida.

## Respuestas rápidas a las tres preguntas más probables

- **"Cambió la variable dependiente y el resultado central se movió."** → EMBI y CDS dan el mismo θ sobre la misma submuestra. Lo que movió el resultado fue la composición de la muestra (Polonia/India, que el CDS truncado ocultaba). Es un hallazgo, no una fragilidad: la complementariedad es una propiedad del tipo de economía.
- **"La heterogeneidad núcleo/no-núcleo es *cherry-picking*."** → La distinción se anuncia en la introducción, tiene mecanismo económico (tenedor marginal de la deuda), y el moderador continuo natural —participación de no residentes— está en la agenda. Con solo 2 países en el grupo de contraste el test formal no puede ser significativo, y lo digo así.
- **"La predicción distintiva del modelo (H4b) falla."** → No falla: no se puede contrastar con potencia (13 clusters, HHI casi invariante). La contribución teórica defendible es la Proposición 3, que es deductiva.
