import os
D = os.path.dirname(os.path.abspath(__file__)) + "/"
s = open(D + "defensa.tex", encoding="utf-8", newline="").read().replace("\r\n", "\n")


def frame(titulo):
    a = s.index("\\begin{frame}" + titulo)
    b = s.index("\\end{frame}", a) + len("\\end{frame}")
    return s[a:b]


preambulo = s[:s.index("\\begin{document}")]
preambulo = preambulo.replace("\\date{\\today}", "\\date{Predefensa (versión corta) · \\today}")
portada = s[s.index("\\begin{document}") + len("\\begin{document}"):s.index("\\begin{frame}{Tabla de contenidos}")]

PRINCIPALES = [
    "{Dos pilares del \\textit{spread} soberano emergente}",
    "{Pregunta e hipótesis}",
    "{Especificación principal y batería}",
    "{Lectura de la batería: réplica y validación del panel}",
    "{Qué agrega el riesgo económico a lo que explica la fragilidad}",
    "{Los dos riesgos coinciden más de lo que explicaría el azar}",
    "{Cuando coinciden, no hay evidencia de que se amplifiquen}",
    "{Deuda y riesgo de cola: lo que resiste y lo que no}",
    "{Hallazgos y su grado de evidencia}",
    "{Implicancias}",
    "{Conclusión}",
]
RESPALDO = [
    "{Qué aporta esta tesis}",
    "{Construcción de $\\JLoss$: fragilidad bancaria sistémica}",
    "{Construcción del $\\GaR$: riesgo de cola del crecimiento}",
    "{Inferencia: cómo mido la incertidumbre}",
    "{Las bandas: cuánta amplificación se descarta y cuánta no}",
    "{Un modelo de límite fiscal: logaritmos frente a puntos básicos}",
    "{Preguntas de portafolio y corrección global (preregistros 7 y 8)}",
    "{¿Efecto o persistencia? La retroalimentación}",
    "{Limitaciones y trabajo futuro}",
    "{Respaldo: Panel A con errores estándar}",
    "{Hallazgos y su grado de evidencia}",
]

HALLAZGOS = r"""\begin{frame}{Hallazgos y su grado de evidencia}
\centering
\renewcommand{\arraystretch}{1.4}
\begin{adjustbox}{width=\textwidth, max totalheight=0.84\textheight}
\begin{tabular}{lll}
\toprule
\textbf{Hallazgo} & \textbf{Cifra} & \textbf{Evidencia} \\
\midrule
Los dos riesgos coinciden & 1,2 veces lo esperado ($p=0{,}0002$) & \textbf{Firme} \\
La fragilidad antecede a la cola & $0{,}405$ (\textit{wild} $0{,}024$) & \textbf{Firme} (1 trim.) \\
Amplificación (H3) & $-0{,}011$; se descarta $>35\%$ & \textbf{No hay evidencia} \\
El riesgo de cola agrega (H2) & $0{,}032$; CCE \textit{wild} $0{,}016$ & Firme como nivel \\
Fragilidad y \textit{spread} (H1) & $0{,}099$; 70\% es Turquía & Sugerente \\
Deuda $\times$ cola, en la muestra & $+0{,}033$ (permutación $0{,}009$) & Firme en la muestra \\
Deuda $\times$ cola, fuera de ella & réplica, instrumento y modelo & \textbf{No se confirma} \\
Otros moderadores y umbrales & Holm $\geq0{,}29$ & \textbf{No hay evidencia} \\
Corrección global (23 hipótesis) & riesgo de cola a un año $0{,}13$; deuda $\times$ cola $0{,}31$ & \textbf{No sobreviven} \\
\bottomrule
\end{tabular}
\end{adjustbox}
\end{frame}"""

partes = [preambulo, "\\begin{document}\n", portada.strip("\n"), "\n\n"]
for t in PRINCIPALES:
    # la tabla completa de hallazgos se lee muy pequeña: en la principal va una versión condensada
    partes += [HALLAZGOS if t == "{Hallazgos y su grado de evidencia}" else frame(t), "\n\n"]
partes += [frame("\n\\vfill\n\\centering\n{\\Huge\\bfseries\\color{tesisblue} Gracias}"), "\n\n"]
partes += ["% =====================================================================\n\\appendix\n\n"]
for t in RESPALDO:
    f = frame(t)
    if not t.startswith("{Respaldo"):
        f = f.replace("\\begin{frame}{", "\\begin{frame}{Respaldo: ", 1)
    partes += [f, "\n\n"]
partes += [frame("[allowframebreaks]{Referencias principales}"), "\n\n\\end{document}\n"]

cab = ("% Versión corta de defensa.tex para la predefensa: once láminas principales con los resultados\n"
       "% más importantes y el resto como respaldo. Se genera con armar_corta.py a partir de defensa.tex.\n")
open(D + "predefensa_corta.tex", "w", encoding="utf-8", newline="").write(cab + "".join(partes))
print("ok")
