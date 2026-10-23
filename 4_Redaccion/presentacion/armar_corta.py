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
    "{¿Efecto o persistencia? La retroalimentación}",
    "{Limitaciones y trabajo futuro}",
    "{Respaldo: Panel A con errores estándar}",
]

partes = [preambulo, "\\begin{document}\n", portada.strip("\n"), "\n\n"]
for t in PRINCIPALES:
    partes += [frame(t), "\n\n"]
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
