# Envíos a revista — dos manuscritos separados

Los dos capítulos de la tesis se preparan como **envíos independientes** a revistas
hispanas. El documento de tesis (`../tesis/main.tex`) se mantiene aparte para la defensa
de magíster.

## Estado

| | Archivo | Compila | Extensión |
|---|---|---|---|
| **Paper empírico** | `paper_empirico/main.tex` | ✅ limpio | 38 pp (doble espacio) |
| **Paper teórico** | `paper_teorico/main.tex` | ✅ limpio | 26 pp (doble espacio) |

Cada `main.tex` es un envoltorio `article` \emph{standalone} que reutiliza el cuerpo del
capítulo de la tesis vía `\input` (`../../tesis/paper2_empirico.tex` /
`paper1_oi.tex` + `anexoA_matematico.tex`), con:
- remapeo `\chapter`→`\section`;
- entornos teoremáticos redefinidos sin contador `[chapter]`;
- macros de `umemoria.cls` reproducidas (`\E`, `\1`, `\R`…);
- las referencias cruzadas al otro capítulo neutralizadas (`\definelabel`).

Compilar: `cd paper_empirico && pdflatex main && pdflatex main` (ídem teórico).

## Revistas objetivo (español)

**Empírico** — *Latin American Journal of Central Banking* (CEMLA/Elsevier; encaja por
el marco GaR-CEMLA), *Economía Chilena* (Banco Central de Chile), *Estudios de Economía*
(U. de Chile, bilingüe), *El Trimestre Económico* (FCE, México).

**Teórico** — *El Trimestre Económico*, *Estudios de Economía*, *Revista de Análisis
Económico* (ILADES).

## Adaptación pendiente por paper (trabajo manual, deliberado)

### Ambos
1. **Resumen corto**: cada `main.tex` ya trae un `abstract` de ~180 palabras; el
   `\section*{Resumen del capítulo}` del cuerpo queda como duplicado — eliminarlo del
   `\input` o comentarlo al extraer el cuerpo definitivo.
2. **Bibliografía**: hoy cada cuerpo trae su `\begin{thebibliography}` embebida. Para el
   envío conviene un `refs.bib` único por paper + `\bibliography`. Deduplicar
   `Chari2024`/`Chari2024b`, `ABG2019`/`ABG2019b`, `AcharyaEtAl2017`/`…b`.
3. **Plantilla de la revista**: sustituir el preámbulo genérico por la clase/estilo que
   pida la revista elegida.
4. **Numeración de cuadros**: el cuerpo usa "Cuadro 1/2/3" a mano; pasar a
   `\begin{table}`+`\caption`+`\label`+`\ref`.

### Paper empírico
5. **Recortar §2 (Marco Teórico)**: los tres pilares están desarrollados con detalle de
   tesis; para el artículo, ~1,5 pp bastan (el modelo estructural completo vive en el
   paper teórico).
6. **Afilar el posicionamiento vs. \citet{Chari2024}** (co-autoría del profesor guía):
   dejar explícito en la intro qué aporta la interacción con una cola \emph{doméstica y
   endógena} del crecimiento frente a la interacción con el ciclo financiero global.
7. Las referencias a "el trabajo teórico complementario" pueden citarse como
   *working paper* (`../modelo OI/working_paper.pdf`) o dejarse como "en preparación".

### Paper teórico
8. La Sección 5.4 (H4a/H4b con datos reales) se mantiene como *puesta a prueba parcial*;
   el resultado central deductivo es la **Proposición 3** (mínimo desplazado de $\JLoss$)
   — reordenar la introducción para venderlo como tal.
9. Figuras `fase3..6` y `fig_h4b`, `fig_jloss_paises` copiadas en `figuras/`.

## Cartas de presentación

`paper_empirico/cover_letter.md`, `paper_teorico/cover_letter.md` (borradores).

## Reproducibilidad

Pipeline y números canónicos: `../../1_Codigo/Panel/bbg/` y
`../../1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`. Batería de robustez de árbitro:
`bbg/p5_robustez_arbitro.py`.
