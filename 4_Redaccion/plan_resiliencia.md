---
title: "Plan: una conclusión mejor sobre deuda, reservas, balance fiscal y resiliencia"
subtitle: "Diagnóstico, lo ejecutado (preregistrado) y los pasos siguientes — 21 de octubre de 2026"
---

*Todo lo que sigue son asociaciones, no efectos causales. Las cifras están en
`1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`, §26. El preregistro es
`4_Redaccion/preregistro_resiliencia.md` (commit `c492ca3`, anterior a los datos y a la estimación).*

# 1. Diagnóstico: por qué la evidencia anterior era débil

1. **Frecuencia.** Deuda/PIB, balance fiscal/PIB y reservas/PIB eran series anuales interpoladas a
   trimestres. Bajo efectos fijos de país y de tiempo les queda poca variación propia y su
   coeficiente no tiene signo económico fiable.
2. **Mal control.** Los mismos controles son plausiblemente canales del mecanismo: el costo esperado del
   rescate deteriora las cuentas fiscales. Condicionar en ellos mide la fragilidad neta de su propio
   canal (de 0,099 se pasa a −0,008).
3. **Moderadores no preespecificados.** El índice de resiliencia y sus componentes se eligieron sin
   registro previo. El término reservas × fragilidad (−0,247) no pasaba Holm y dependía de Polonia.
4. **Medida equivocada.** Reservas/PIB no es la medida macroprudencial habitual de adecuación. La regla
   de Greenspan–Guidotti compara las reservas con la deuda externa de corto plazo.
5. **Potencia.** Con trece economías, un moderador que varía sobre todo entre países compara en lo
   esencial trece observaciones.

# 2. Lo ejecutado

| Paso | Qué ataca | Resultado |
|---|---|---|
| Preregistro (commit `c492ca3`) | 3 | Hipótesis, inferencia y consecuencia fijadas antes de los datos |
| Datos trimestrales (QPSD, QEDS, GEM; `p41`) | 1, 4 | Deuda trimestral en 10 de 13 economías; adecuación de reservas en las 13 |
| R-H1: efecto directo por g-estimación secuencial | 2 | Efecto directo ≈ 0 (0,002; IC [−0,19; 0,16]) frente a 0,101 total: la asociación pasa por el canal fiscal o comparte su fundamento |
| R-H2: fragilidad × adecuación de reservas | 3, 4 | −0,063, wild p uni 0,29, Holm 0,29: no se sostiene; el término de reservas queda exploratorio |
| R-H3: riesgo de cola × deuda pública | 3 | **+0,011 por d.e. de deuda; wild p uni 0,015; Holm 0,029; 13 de 13 sin cada país: firme** |
| LP mensual por estado de reservas | 5 | Sin diferencia entre estados en ningún horizonte |

**Conclusión vigente.** La deuda pública amplifica la transmisión del riesgo de cola del crecimiento al
spread: una desviación estándar más de deuda (≈ 20 pp del PIB) la eleva en una cuarta parte, de 0,043 a 0,054.
La adecuación de reservas no atenúa la transmisión de la fragilidad bancaria. Y la asociación de la
fragilidad con el spread no se puede separar de su paso por las cuentas fiscales.

# 3. Pasos siguientes (cada uno, con un preregistro nuevo antes de estimar)

1. **Composición de la deuda.** Pecado original: la participación de la deuda en moneda extranjera y
   en manos de no residentes (QPSD la desagrega). Un mismo nivel de deuda debería pesar más si está en
   dólares. Hipótesis: el término deuda × riesgo de cola crece con la participación en moneda
   extranjera.
2. **Espacio fiscal propiamente tal.** La distancia al límite de deuda (Ghosh et al., 2013) o la base
   de espacio fiscal del Banco Mundial (Kose et al.), en lugar de deuda/PIB. Esa medida captura la
   capacidad de pago y no solo el endeudamiento.
3. **Balance fiscal trimestral.** El de IMF GFS o el de los ministerios de finanzas, para que el
   mediador de R-H1 no sea anual. La prueba de efecto directo gana precisión.
4. **El *doom loop* completo.** La interacción deuda × fragilidad: la teoría (Farhi–Tirole) predice que
   el pasivo contingente bancario pesa más con un soberano más endeudado. Es la contraparte bancaria de
   R-H3.
5. **Calificación soberana histórica.** Es el control que usan Chari et al. y que falta. Permite separar
   si la deuda amplifica el riesgo de cola por encima de lo que ya incorpora la calificación.
6. **Variación dentro del país.** Reestimar R-H3 con la deuda en desviaciones de su tendencia por país,
   para que la identificación descanse en episodios de endeudamiento y no en diferencias entre
   economías.
7. **Más economías.** Las de la base QPSD con EMBI y GaR fuera del panel, para que el moderador no
   compare trece observaciones.

**Orden recomendado antes de la defensa:** 1 y 6 (los datos ya están en las fuentes descargadas), luego 4.
Los demás requieren datos nuevos y quedan para el paper.
