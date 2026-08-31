# Organización de la carpeta — Tesis JLoss × GaR

> **Nota (2026-08-31):** este archivo describe la reorganización de carpetas del 2026-07-25 y
> sigue siendo válido para la **estructura**, pero está **superado en materia de resultados y
> versiones vigentes**. Para el estado actual de la investigación ver [`README.md`](README.md);
> para vigencia archivo por archivo, [`4_Redaccion/CONTROL_DE_VERSIONES.md`](4_Redaccion/CONTROL_DE_VERSIONES.md).

*Reordenada el 2026-07-25.* Todo el material vigente quedó consolidado por tipo dentro de esta carpeta.

## Estructura

```
Jloss/
├── 1_Codigo/                  Pipelines y scripts (cada uno autocontenido)
│   ├── GaR/                   Growth-at-Risk (motor, FCI, insumos por país)
│   ├── JLoss_reconstruction/  Reconstrucción JLoss (v8 vigente + MATLAB)
│   ├── Panel/                 Construcción del panel + EDA + regresiones (v2)
│   ├── Stata_Sov_Risk/        Do-files y bases .dta de Stata
│   └── v0/                    Prototipo original + simulación del modelo
├── 2_Datos/                   Datos sueltos y compartidos
│   ├── embi.xlsx
│   ├── EMBI_real_8countries_2006_2014.csv   (incorporado desde tus subidos)
│   └── growth-at-risk-with-a-pr.xls
├── 3_Marco_teorico/           14 papers de referencia (PDF)
├── 4_Redaccion/               Escritura de la tesis (Boceto v2 = vigente)
└── _RESPALDO_eliminados_2026-07-25.zip   (respaldo de lo borrado)
```

**Nota:** los datos propios de cada pipeline (p. ej. `GaR_panel.xlsx`, los CSV `all17`)
se dejaron **dentro** de su pipeline en `1_Codigo/`, no en `2_Datos/`, para no romper
las rutas relativas de los scripts y notebooks. `2_Datos/` guarda solo los archivos
sueltos y compartidos.

## Qué se conservó como versión vigente

- **JLoss:** `v8` (notebook, figura, `Panel_JLoss_v8.csv`).
- **Panel:** serie `all17` (`Panel_final_all17.csv`, `gar_panel_all17.csv`) y `Regresiones_panel_v2`.
- **Redacción:** `Boceto_1_v2.tex` + `Boceto_1_v2.pdf`.

## Qué se eliminó

- Versiones superadas de JLoss (`v1`–`v5` notebooks y figuras; `Panel_JLoss_Final/v2`).
- Regresiones v1 (`Regresiones_panel.Rmd/.html/.tex`).
- Temporales de LaTeX (`.aux/.log/.out/.spl`), logs de R, checkpoint `_ckpt_latam.csv`,
  autosaves de MATLAB (`.asv`), `__pycache__` y `_tmp_downloads`.

## CORRECCIÓN (restaurado)

Se **restauraron** 7 CSV del Panel que en un inicio marqué como obsoletos pero que el
código vigente sí usa como insumos/intermedios (el EDA `v2` y `Regresiones_panel_v2.Rmd`):
`Panel_final.csv`, `Panel_final_prebackup.csv`, `Panel_final_prebackup_all17.csv`,
`Panel_partial_EMBI_GaR.csv`, `Panel_extended_15paises.csv`, `gar_panel_all15.csv`,
`gar_panel_latam.csv`. Están de vuelta en `1_Codigo/Panel/`.

## Pendientes manuales (2 cosas rápidas)

1. **Borra las carpetas vacías `Jloss/` y `Panel/`** en la raíz. Su contenido ya se movió,
   pero el sistema las dejó bloqueadas (estaban abiertas/indexándose) y no pude eliminarlas.
2. **`matlab_JLOSS.zip` (512 MB)** en `1_Codigo/JLoss_reconstruction/` es un archivo comprimido
   redundante con la carpeta `matlab/` ya descomprimida. No lo borré por seguridad; si no lo
   necesitas, eliminarlo libera ~512 MB.
