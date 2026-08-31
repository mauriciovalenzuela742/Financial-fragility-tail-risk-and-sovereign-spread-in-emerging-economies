# JLoss recomputado con datos Bloomberg (2004Q1–2026Q3)

`Panel_JLoss_v9_bloomberg.csv` — JLoss país-trimestre, ρ=0.4 plano, PD de mercado
(Merton/KMV multi-arranque), motor saddle-point v8 sin cambios.
`qa_jloss.csv` — cobertura y bancos-por-trimestre por país.

## Reproducir

```bash
cd 1_Codigo/JLoss_reconstruction
mkdir -p _stage && for d in ../Bloomberg_extraction/output/*/; do c=$(basename "$d"); \
  cp "$d/balance_$c.csv" "$d/mktcap_$c.csv" _stage/; done
JLoss-pipeline/venv/Scripts/python.exe jloss_engine.py --indir _stage \
  --out jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv
rm -rf _stage
```

## Notas de cobertura (de ESTADO_SESION.md de la extracción Bloomberg)

- **bulgaria, egypt, hungary, russia**: todos los trimestres con <3 bancos cotizados
  (`below_min_banks=True`). JLoss poco representativo — estructural del universo.
- **russia**: serie de mercado termina 2024Q2 (Bloomberg dejó de precificar SBER/VTBR
  por sanciones).
- **southafrica**: bancos reportan balance semestral; el motor arrastra 1 trimestre.
- **southkorea**: empieza 2011 (balance Bloomberg solo desde 2009; holdings formados después).
- **china, india, pakistan**: empiezan 2006–2007 (profundidad de mktcap).
- 376 de 1718 filas con `below_min_banks=True` — filtrar antes de interpretar.

## Diferencias vs Panel_JLoss_v8.csv

Fuente distinta (Bloomberg vs reguladores), universo de bancos distinto, arranque 2004
(no 1999). No es directamente comparable fila a fila; usar v9 como serie nueva homogénea.
