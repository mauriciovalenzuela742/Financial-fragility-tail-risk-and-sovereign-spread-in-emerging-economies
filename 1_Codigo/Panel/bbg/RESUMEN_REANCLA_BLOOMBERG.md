# Reancla de la investigación en datos Bloomberg — un solo panel

Fecha: 2026-08-31 (v3). Qué se hizo y qué cambió en las conclusiones.

## Pipeline (todo re-ejecutable, `.venv`)

```
1_Codigo/JLoss_reconstruction/jloss_bloomberg/   JLoss v9 (20 países, 2004–2026)
1_Codigo/Panel/bbg/
  p0_controles_all.py   controles domésticos (deuda/fiscal IMF WEO, reservas/CA World Bank,
                        inflación/REER de GaR/individuals) para TODOS los países -> controls_all_bbg.csv
  p1_build_panels.py    CDS 5Y Bloomberg -> trimestral; ensambla EL panel -> Panel_bloomberg.csv
                        + panel_real_bbg.csv (plantilla fase5) + cobertura_panel_bbg.csv
  p2_regresiones.py     Cuadro único (M1/M2/M3 + cluster), robustez (pre-2020 prominente),
                        umbral Hansen, efecto marginal, diagnósticos
  p3_causal_fase5.py    batería causal + H4a/H4b
  p4_figuras.py         7 figuras -> bbg/figuras/*.pdf (copiadas a 4_Redaccion/tesis/imagenes/)
  NUMEROS_CANONICOS_BBG.md   <- fuente de verdad
  DIAGNOSTICO_COREA.md       <- por qué Corea y Bulgaria quedan fuera
```

Orden: `p0 -> p1 -> p2 -> p3 -> p4`.

## Un solo panel

- **Variable dependiente = CDS soberano 5Y de Bloomberg, y solo eso.** Donde no hay CDS,
  la celda queda vacía; no se mezcla con EMBI de bonos ni proxies.
- **Roster: 18 economías** (todas con JLoss, menos Corea y Bulgaria). **Muestra de estimación
  (CDS+JLoss+GaR): 838 obs, 14 países** (11 con CDS continuo + Hungría/Polonia con 14 trim.
  + Pakistán con 1).
- **Exclusiones (2), por JLoss no válido a nivel país:** Corea del Sur (Korea discount ->
  Merton PD ≈ 0,55) y Bulgaria (1 banco cotizado, JLoss mediana 29). Ver DIAGNOSTICO_COREA.md.
- **Controles domésticos para todos los países** (antes solo 5 LatAm) -> una sola
  especificación con controles sobre el panel completo.

## Resultados (panel único)

| | v8 regulatorio (dos bases) | Bloomberg (panel único) |
|---|---|---|
| θ (JLoss×GaR), M2 con controles | −0,34 (p<0,05) | **−0,354** (DK p=0,056; wild boot p=0,035; cluster país p=0,001) |
| θ, sin controles (M1) | — | −0,543 (p=0,028) |
| pre-2020 | (más fuerte) | **−0,39 (t=−1,02): signo se mantiene, no significativo** |
| sin 2020–2021 | — | −1,11 (t=−3,53) |
| Umbral Hansen (severo/benigno) | corrobora | +8,1 / +2,3 pb, LR=80 |
| Efecto marginal p10→p90 GaR | monótono | +4,6 → +1,8 (banda excluye 0 en cola severa) |
| IV shift-share | débil | F≈9,5 (débil-a-límite) |
| **H4b (β4>0, amplificación por concentración)** | **+721 (t=2,98) confirmada** | **−392 (t=−2,34): signo contrario, significativo. RECHAZADA** |

**Lectura honesta:** el panel único respalda el **signo y la forma** de la complementariedad
(θ<0, efecto marginal creciente en severidad de cola, umbral); la **magnitud puntual** es
marginalmente significativa y su **identificación descansa en episodios de estrés recientes**
(pre-2020 no se distingue de cero). H4a débil, H4b rechazada.

## Tesis reescrita (una sola investigación, sin "núcleo/ampliado")

`4_Redaccion/tesis/` — recompilada limpio, **75 páginas**:
- `main.tex` (resumen), `introduccion_general.tex`, `discusion_general.tex`
- `paper2_empirico.tex` — §5 "Un solo panel", §6 un solo Cuadro 3, §6.5 robustez con
  subsección prominente de frontera temporal, limitaciones y conclusión reescritas
- `paper1_oi.tex` — §5.4 (H4a/H4b sobre el panel único; H4b resultado negativo)
- **`anexoB_datos.tex` (NUEVO)** — tabla de procedencia de todas las series, `\input` en
  `main.tex` tras el anexo matemático; aparece en el índice de tablas.

## Pendiente (declarado en la tesis)

- Profundidad temporal: pocos episodios de cola independientes; India vía bono 10Y, cerrar
  GaR de Argentina/Egipto/Rusia.
- Extraer de Bloomberg los componentes reales del FCI para anclar también GaR.
- Serie de concentración bancaria trimestral (GFDD es anual, casi invariante).
