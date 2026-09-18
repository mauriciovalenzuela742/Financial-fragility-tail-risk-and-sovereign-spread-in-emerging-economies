# Carta de presentación — paper empírico (borrador)

Estimado/a Editor/a:

Adjunto para su consideración el manuscrito **"Fragilidad bancaria sistémica, riesgo de
cola del crecimiento y *spread* soberano en economías emergentes"**, para su eventual
publicación en *[revista]*.

El trabajo articula dos literaturas que han evolucionado por separado —el nexo
banca–soberano y el programa de *Growth-at-Risk*— y contrasta si la fragilidad bancaria
sistémica y el riesgo a la baja del crecimiento determinan el *spread* soberano de forma
**complementaria** y no aditiva. Sobre un panel único de trece economías emergentes
construido íntegramente con datos de mercado de Bloomberg (2004–2026, $N=721$), el
coeficiente de interacción $JLoss\times D$ ($D\equiv-GaR$) sobre el EMBI Global
Diversified de J.P. Morgan tiene el signo que predice el multiplicador de *doom loop*,
pero **no es significativo sobre la muestra completa** ($\hat\beta_3=+0{,}16$,
$p=0{,}26$); los canales de nivel —fragilidad bancaria y riesgo de cola del
crecimiento por separado— sí están bien identificados.

El hallazgo central es la caracterización de **dónde y cuándo** aparece esa
complementariedad, no un coeficiente único. Es significativa en dos dimensiones: (i)
**transversal**, en el núcleo de once economías emergentes de financiamiento externo
($\hat\beta_3=+0{,}47$, $p=0{,}023$), diluyéndose al añadir economías con mercados de
deuda local profundos; y (ii) **temporal**, mediante un test de falsación directo —se
interactúa la complementariedad con un vector de crisis sin excluir observaciones, y se
muestra que se **anula** bajo respaldo oficial masivo (crisis financiera global 2008–09,
pandemia 2020–21) y **sobrevive** en el estrés emergente de 2015–2016, que no tuvo ese
respaldo ($p<0{,}001$). Un modelo de umbral de panel corrobora la no linealidad.

La contribución es triple. Primero, sustancial: es —hasta donde sabemos— la primera
evidencia sistemática de la interacción entre una métrica estructural de fragilidad
bancaria y una medida de riesgo de cola del crecimiento *doméstico y endógeno* en la
determinación del riesgo soberano de economías emergentes, frente a la interacción con
factores financieros *globales y exógenos* de la literatura más próxima (Chari et al.,
2024). Segundo, de identificación: el resultado se somete a una batería exigente —wild
cluster bootstrap, un bootstrap de bloques que re-estima la regresión cuantílica de
$GaR$ completa en cada réplica para propagar la incertidumbre del regresor generado, y
tres intentos de instrumentación del canal de nivel (liquidez de fondeo *on/off-run*,
dólar amplio BIS, choque de términos de intercambio por *commodities*)— sin que ninguna
conclusión cambie de categoría, aunque la identificación causal del canal de nivel no
queda cerrada por variables instrumentales sobre esta muestra. Tercero, de
transparencia: el trabajo declara explícitamente los límites de la inferencia con un
número reducido de países y episodios de cola, y reporta la heterogeneidad como
resultado principal en vez de un coeficiente promedio que la oculta.

Todo el código de construcción de las métricas y de estimación es reproducible y se pone
a disposición.

El manuscrito es original, no ha sido publicado y no está bajo consideración en otra
revista. Agradezco de antemano el tiempo del equipo editorial y de los evaluadores.

Atentamente,
Mauricio Valenzuela Corvalán
