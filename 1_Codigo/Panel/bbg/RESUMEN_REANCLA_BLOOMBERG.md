# Reancla de la investigación en datos Bloomberg — resumen

Fecha: 2026-08-31. Qué se hizo, en qué orden, y qué cambió en las conclusiones.

## Pipeline (todo re-ejecutable)

```
1_Codigo/JLoss_reconstruction/jloss_bloomberg/   JLoss v9 (20 países, 2004–2026) + README + QA
1_Codigo/Panel/bbg/
  p1_build_panels.py    CDS 5Y Bloomberg → EMBI trimestral; ensambla Panel_principal_bbg / Panel_ampliado_bbg
  p2_regresiones.py     θ (M2/M3), cluster, robustez, umbral Hansen, efecto marginal, diagnósticos
  p3_causal_fase5.py    batería causal (wild boot, LP, IV shift-share, triple institucional) + H4a/H4b
  p4_figuras.py         7 figuras → bbg/figuras/*.pdf (copiadas a 4_Redaccion/tesis/imagenes/)
  NUMEROS_CANONICOS_BBG.md   ← fuente de verdad para la prosa
  DIAGNOSTICO_COREA.md       ← por qué Corea queda fuera
```

Orden: `p1 → p2 → p3 → p4`. Requiere `.venv` (pandas 2.3, linearmodels 7.0).

## Qué es Bloomberg y qué no

| Insumo | Fuente |
|---|---|
| JLoss (balances + capitalización bursátil, 113 bancos) | **Bloomberg** |
| Spread soberano (CDS 5Y) | **Bloomberg** |
| VIX, UST10Y, US HY spread | **Bloomberg** |
| GaR (FCI: IPC, PIB, bolsa, REER, 10Y) | estadísticas nacionales (Bloomberg no publica cuentas nacionales) — sin cambios |
| HHI concentración | GFDD World Bank |
| Controles domésticos (deuda, fiscal, reservas, CA, inflación, REER) | sin cambios |

## Decisiones tomadas

1. **Corea del Sur excluida** del panel ampliado (11 países, no 12): su E/D de mercado ≈ 0,04
   (Korea discount estructural) hace que el Merton devuelva PD ~0,55 y JLoss 25–47, no creíble.
2. **CDS 5Y como variable dependiente** en vez del EMBI de bonos: homogéneo entre países.
   Cobertura continua 2004–2026 para 11 países; Egipto/Pakistán parciales, Polonia/Hungría/
   Rusia/Bulgaria sin precios de mercado utilizables (quedan para agenda futura).
3. **Panel ampliado** = brazil, chile, china, colombia, indonesia, malaysia, mexico, peru,
   philippines, southafrica, turkey.

## Qué cambió en las conclusiones de la tesis

| | v8 (regulatorio) | Bloomberg | Efecto en la tesis |
|---|---|---|---|
| θ (JLoss×GaR), principal M3 | −0,338 (p=0,028) | **−0,47 (p=0,033)** | se mantiene, pero ahora **depende de los controles** (M2 sin controles n.s.) |
| θ, base ampliada M2 | −0,212 (p=0,069) | **−0,56 (p=0,025)** | más significativo, pero **solo post-2020** |
| Umbral Hansen | corrobora | corrobora (severo +7,0 vs benigno +3,0) | sin cambio de fondo |
| IV shift-share | F débil | **F=51 en panel ampliado** | mejor evidencia del canal de nivel |
| **H4b (β4>0, amplificación por concentración)** | **+721 (t=2,98), confirmada** | **−418 (t=−2,11), RECHAZADA** | **cambio mayor: la predicción distintiva del modelo OI no se sostiene** |

## Archivos de la tesis reescritos

- `4_Redaccion/tesis/main.tex` — resumen
- `4_Redaccion/tesis/introduccion_general.tex` — contribución (iii)
- `4_Redaccion/tesis/paper2_empirico.tex` — resumen, §4.1, §5 (Datos), §6 (Resultados completo), Cuadros 2–3, limitaciones, agenda, conclusión; 4 figuras nuevas embebidas
- `4_Redaccion/tesis/paper1_oi.tex` — resumen, §5.4 (H4a/H4b, resultado negativo de H4b + interpretación), conclusión; 1 figura nueva
- `4_Redaccion/tesis/discusion_general.tex` — síntesis, implicancias, limitaciones, agenda, conclusión
- `4_Redaccion/CONTROL_DE_VERSIONES.md` §5 y `1_Codigo/Panel/NUMEROS_CANONICOS.md` (marcado SUPERADO)

Compila limpio: `4_Redaccion/tesis/main.pdf`, 71 páginas, sin referencias indefinidas.

## Pendiente (declarado en la tesis)

- Extraer de Bloomberg los componentes reales del FCI para anclar también GaR.
- Serie de concentración bancaria trimestral (el GFDD es anual y casi invariante) — es la
  única forma de dirimir si H4b falla por medición o porque el canal es débil.
- Controles domésticos para los 6 países no-LatAm de la base ampliada.
- Incorporar Egipto/Pakistán/Polonia/Hungría/Rusia/Bulgaria con spread de bono 10Y.
