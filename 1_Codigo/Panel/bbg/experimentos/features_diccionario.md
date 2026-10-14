# Diccionario de variables construidas (experimento, no integrado)

Todas a nivel país-trimestre en t; el rezago de un trimestre se aplica al evaluar.

| Variable | Familia | Definición | Fuente |
|---|---|---|---|
| `ln_tamano` | F1 | log de pasivos del sistema bancario / PIB nominal (PIB real por recursión del crecimiento interanual x IPC); definido hasta una constante por país | Panel_JLoss_v9_bloomberg.csv; gGDP_*.csv; CPI_*.csv |
| `ln_costo_pib` | F1 | PRIMARIA. log de JLoss x pasivos del sistema / PIB: pérdida conjunta frente al tamaño de la economía | ídem |
| `ln_costo_reservas` | F1 | pérdida conjunta frente a las reservas (reservas/PIB anual interpolado) | ídem + panel |
| `ln_costo_deuda` | F1 | pérdida conjunta frente a la deuda pública | ídem + panel |
| `ln_nbancos` | F1 | log del número de bancos con probabilidad válida (control: el tamaño salta cuando entra o sale un banco) | panel |
| `lnJ_ancha` | F2 | PRIMARIA. log del JLoss recalculado con malla de pérdidas ancha [0,01; 0,20] (sin India) | Panel_JLoss_wide.csv |
| `J_exceso` | F2 | log del exceso sobre el piso: ln(max(JLoss; 2,16)/2,16); cero en el piso | panel |
| `J_enpiso` | F2 | indicador de JLoss a menos de 2 % del piso | panel |
| `J_z` | F2 | ln JLoss estandarizado dentro de cada país | panel |
| `J_pct` | F2 | percentil de ln JLoss dentro de cada país | panel |
| `J_racha_fuera` | F2 | log(1 + trimestres consecutivos fuera del piso) | panel |
| `frac_estres` | F3 | PRIMARIA. fracción de los pasivos del sistema en bancos con distancia al incumplimiento ingenua < 1,5 | balance_*.csv, mktcap_*.csv (jloss_engine.quarterly_inputs) |
| `frac_estres_1 / frac_estres_2` | F3 | ídem con umbral 1,0 y 2,0 | ídem |
| `ln_apalanc` | F3 | log del apalancamiento a valor de mercado (pasivos / capitalización), ponderado por pasivos | ídem |
| `ln_vol_banca` | F3 | log de la volatilidad accionaria anualizada de los bancos, ponderada por pasivos | ídem |
| `dd_medio / dd_min / dd_disp` | F3 | distancia al incumplimiento ingenua (Bharath y Shumway, 2008): media ponderada, peor banco y dispersión entre bancos | ídem |
| `pd_ing_pond` | F3 | probabilidad de incumplimiento ingenua ponderada por pasivos | ídem |
| `ln_banca_vol_esp` | F4 | PRIMARIA. log de la volatilidad trimestral del retorno de la banca en exceso de la bolsa local (beta de los cuatro trimestres previos) | mktcap_*.csv, STX_*.csv |
| `banca_ret_esp` | F4 | retorno trimestral de la banca en exceso de la bolsa | ídem |
| `ln_bolsa_vol / bolsa_ret` | F4 | volatilidad y retorno trimestral del índice bursátil del país (componente de mercado) | STX_*.csv |
| `ln_banca_vol / banca_ret` | F4 | volatilidad y retorno trimestral de la banca, sin depurar | mktcap_*.csv |
| `D_baja` | F5 | PRIMARIA. distancia a la baja: media condicional menos cuantil 5 % (pp). D = D_media + D_baja | panel (gar_mean, GaR) |
| `D_media` | F5 | menos la media condicional del crecimiento (pp) | panel |
| `D_alza` | F5 | PLACEBO de simetría. distancia al alza: cuantil 95 % menos media (pp) | panel (GaR + iqr_05_95) |
| `D_disp / D_asim / D_prof` | F5 | desviación estándar, asimetría y profundidad de la cola (cuantil 5 % menos pérdida esperada) | panel |
| `D_ins_sintasa` | F6 | PRIMARIA. riesgo de cola (en muestra) con el índice financiero sin el diferencial de tasas reales local-EE.UU. | gar_insample_noCDIFF.csv |
| `D_ins / D_ins_sinbolsa` | F6 | riesgo de cola en muestra, base y sin el bloque bursátil (comparación igual a igual) | gar_insample_*.csv |
| `fci / fci_bolsa / fci_tasa / fci_cambio` | F6 | índice de condiciones financieras y sus tres bloques, promedio trimestral, regenerados con fci_engine.compute_fci | STX/Ryr/CPI/rEER por país |
| `D_mm4` | F7 | PRIMARIA. media móvil de un solo lado de 4 trimestres del riesgo de cola | panel |
| `D_pct` | F7 | percentil del riesgo de cola dentro de cada país | panel |
| `D_propio / J_propio` | F7 | riesgo menos el promedio de los 13 países en el trimestre (componente propio del país) | panel |
| `sorpresa_crec` | F7 | crecimiento interanual realizado menos la media condicional del trimestre anterior (pp); la alineación de fechas es un supuesto | gGDP_*.csv, panel |
| `cola_materializada` | F7 | indicador: el crecimiento realizado cayó bajo el cuantil 5 % previo | ídem |
| `D_ee_replicas` | F7 | desviación estándar del riesgo de cola entre las 500 réplicas (error de estimación, pp) | gar_replicas_nlhpc.csv |
| `J_max4` | F10 | PRIMARIA. máximo de ln JLoss en los últimos 4 trimestres | panel |
| `J_d4 / J_brecha8 / J_vol4 (y D_*)` | F10 | cambio a 4 trimestres, brecha frente a la media móvil de 8 y desviación estándar de 4 trimestres | panel |
| `reer_z / reer_max4` | placebo | tipo de cambio real transformado igual que la fragilidad (no debería explicar el spread) | panel |

## Cobertura (fracción de país-trimestres con dato, 13 países)

| Variable | Cobertura | Países |
|---|---|---|
| `JLoss` | 1.00 | 13 |
| `n_banks` | 1.00 | 13 |
| `below_min_banks` | 1.00 | 13 |
| `GaR` | 0.85 | 13 |
| `ES` | 0.85 | 13 |
| `prob_neg` | 0.85 | 13 |
| `skew` | 0.85 | 13 |
| `std` | 0.85 | 13 |
| `GaR_st` | 0.85 | 13 |
| `n_train` | 0.85 | 13 |
| `gar_mean` | 0.85 | 13 |
| `iqr_05_95` | 0.85 | 13 |
| `scale_st` | 0.85 | 13 |
| `skew_st` | 0.85 | 13 |
| `nu_st` | 0.85 | 13 |
| `EMBI_bps` | 0.81 | 13 |
| `CDS_bps` | 0.86 | 12 |
| `VIX` | 1.00 | 13 |
| `UST10Y` | 1.00 | 13 |
| `US_HY_spread` | 1.00 | 13 |
| `UST10Y_log` | 1.00 | 13 |
| `US_HY_spread_log` | 1.00 | 13 |
| `OnOffRun_spread` | 1.00 | 13 |
| `OnOffRun_spread_log` | 1.00 | 13 |
| `debt_gdp` | 0.86 | 13 |
| `fisc_bal` | 0.86 | 13 |
| `res_gdp` | 0.84 | 13 |
| `ca_gdp` | 0.83 | 13 |
| `infl_yoy` | 0.82 | 13 |
| `reer` | 0.85 | 13 |
| `HHI_struct` | 1.00 | 13 |
| `GaR_pp` | 0.85 | 13 |
| `JLoss_x_GaR` | 0.85 | 13 |
| `lnJ` | 1.00 | 13 |
| `D` | 0.85 | 13 |
| `sys_liab` | 1.00 | 13 |
| `ln_pib_real` | 0.94 | 13 |
| `g_real` | 0.94 | 13 |
| `ln_cpi` | 0.92 | 13 |
| `ln_tamano` | 0.92 | 13 |
| `ln_costo_pib` | 0.92 | 13 |
| `ln_costo_reservas` | 0.78 | 13 |
| `ln_costo_deuda` | 0.78 | 13 |
| `ln_nbancos` | 1.00 | 13 |
| `JLoss_ancha` | 0.93 | 12 |
| `lnJ_ancha` | 0.93 | 12 |
| `J_exceso` | 1.00 | 13 |
| `J_enpiso` | 1.00 | 13 |
| `J_z` | 1.00 | 13 |
| `J_pct` | 1.00 | 13 |
| `J_racha_fuera` | 1.00 | 13 |
| `ln_apalanc` | 1.00 | 13 |
| `ln_vol_banca` | 1.00 | 13 |
| `dd_medio` | 1.00 | 13 |
| `dd_min` | 1.00 | 13 |
| `dd_disp` | 0.97 | 13 |
| `frac_estres` | 1.00 | 13 |
| `frac_estres_1` | 1.00 | 13 |
| `frac_estres_2` | 1.00 | 13 |
| `pd_ing_pond` | 1.00 | 13 |
| `n_bancos_f3` | 1.00 | 13 |
| `banca_ret` | 0.92 | 13 |
| `bolsa_ret` | 0.92 | 13 |
| `banca_ret_esp` | 0.92 | 13 |
| `ln_banca_vol` | 0.92 | 13 |
| `ln_bolsa_vol` | 0.92 | 13 |
| `ln_banca_vol_esp` | 0.92 | 13 |
| `beta_banca` | 0.92 | 13 |
| `media_pp` | 0.85 | 13 |
| `D_media` | 0.85 | 13 |
| `D_baja` | 0.85 | 13 |
| `D_alza` | 0.85 | 13 |
| `D_disp` | 0.85 | 13 |
| `D_asim` | 0.85 | 13 |
| `D_prof` | 0.85 | 13 |
| `fci` | 0.91 | 13 |
| `fci_bolsa` | 0.91 | 13 |
| `fci_tasa` | 0.91 | 13 |
| `fci_cambio` | 0.91 | 13 |
| `D_ins` | 0.85 | 13 |
| `D_ins_sintasa` | 0.85 | 13 |
| `D_ins_sinbolsa` | 0.85 | 13 |
| `D_mm4` | 0.81 | 13 |
| `D_pct` | 0.85 | 13 |
| `D_propio` | 0.85 | 13 |
| `J_propio` | 1.00 | 13 |
| `sorpresa_crec` | 0.83 | 13 |
| `cola_materializada` | 0.83 | 13 |
| `D_ee_replicas` | 0.85 | 13 |
| `J_d4` | 0.96 | 13 |
| `J_brecha8` | 0.92 | 13 |
| `J_max4` | 0.97 | 13 |
| `J_vol4` | 0.97 | 13 |
| `D_d4` | 0.80 | 13 |
| `D_brecha8` | 0.77 | 13 |
| `D_max4` | 0.81 | 13 |
| `D_vol4` | 0.81 | 13 |
| `reer_ln` | 0.85 | 13 |
| `reer_z` | 0.85 | 13 |
| `reer_max4` | 0.82 | 13 |
